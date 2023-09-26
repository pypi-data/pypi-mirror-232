#
# SPDX-FileCopyrightText: Copyright (c) 1993-2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
from collections import namedtuple

from polygraphy import mod, util
from polygraphy.logger import G_LOGGER
from polygraphy.tools.args import ModelArgs, OnnxLoadArgs, OnnxSaveArgs
from polygraphy.tools.surgeon.subtool.base import BaseSurgeonSubtool

onnx = mod.lazy_import("onnx")
onnx_numpy_helper = mod.lazy_import("onnx.numpy_helper")
np = mod.lazy_import("numpy")


PruneInfo = namedtuple("PruneInfo", ["name", "axis"])


class GraphPruner:
    def __init__(self, g):
        self.g = g
        # map: initializer name -> object
        self.w_name2obj = {t.name: t for t in g.initializer}
        # map: tensor name -> producer node object
        self.tname2producer = dict()
        for n in g.node:
            for t in n.output:
                self.tname2producer[t] = n

        self.prune_infos = dict()

    # Look back through Q/DQ/Cast nodes
    def __tensor(self, t, axis):
        if t in self.w_name2obj:
            G_LOGGER.verbose(f"Tracking weight: ({t})")
            self.prune_infos[t] = PruneInfo(t, axis)
            return

        axis_insensitive_op_type = [
            "QuantizeLinear",
            "DequantizeLinear",
            "TRT_FP8QuantizeLinear",
            "TRT_FP8DequantizeLinear",
            "Cast",
        ]
        stop_op_type = [
            "LayerNormalization",
            "Reshape",
            "Concat",
            "Slice",
            "Shape",
            "Unsqueeze",
            "Gather",
            "Mul",
            "Add",
        ]
        if t in self.tname2producer:
            producer = self.tname2producer[t]
            if producer.op_type in axis_insensitive_op_type:
                G_LOGGER.verbose(f"({t}) is produced by {producer.op_type}, looking back")
                self.__tensor(producer.input[0], axis)
            elif producer.op_type == "Transpose":
                G_LOGGER.verbose(f"({t}) is produced by {producer.op_type}, checking attributes")
                for attr in producer.attribute:
                    if attr.name == "perm":
                        perm = list(attr.ints)
                        new_axis = perm.index(axis)
                        G_LOGGER.verbose(f"attribute <perm> is {perm}, axis {axis} -> {new_axis}")
                        self.__tensor(producer.input[0], new_axis)
                        return
                G_LOGGER.warning(f"{producer.op_type} doesn't have <perm> attribution!")
            elif producer.op_type in stop_op_type:
                G_LOGGER.verbose(
                    f"({t}) produced by {producer.name} type {producer.op_type}. Stopping backward analysis."
                )
            else:
                G_LOGGER.warning(f"({t}) produced by {producer.name} type {producer.op_type} is unsupported!")

    def __conv(self, node):
        assert node.op_type == "Conv"
        w = node.input[1]
        self.__tensor(w, 1)

    def __matmul(self, node):
        assert node.op_type == "MatMul"
        a = node.input[0]
        b = node.input[1]
        self.__tensor(a, 1)
        self.__tensor(b, 0)

    def __gemm(self, node):
        assert node.op_type == "Gemm"
        a = node.input[0]
        b = node.input[1]

        # get attributes
        trans_a = False
        trans_b = False
        attrs = node.attribute
        for attr in attrs:
            if attr.name == "transA":
                trans_a = attr.i == 1
            elif attr.name == "transB":
                trans_b = attr.i == 1

        # check
        axis = 0 if trans_a else 1
        self.__tensor(a, axis)
        axis = 1 if trans_b else 0
        self.__tensor(b, axis)

    def walk_nodes(self):
        assert len(self.prune_infos) == 0
        count = len(self.g.node)
        for i in range(count):
            n = self.g.node[i]
            G_LOGGER.verbose(f"Processing node {i}/{count} ({n.op_type}): {n.name}")
            if n.op_type == "MatMul":
                self.__matmul(n)
            elif n.op_type == "Gemm":
                self.__gemm(n)
            elif n.op_type == "Conv":
                self.__conv(n)
            else:
                pass
        G_LOGGER.info(f"Collected {len(self.prune_infos)} weights candidates.")

    def drop_na(self):
        G_LOGGER.verbose("Removing the ones that not appliable!")
        prune_infos = list(self.prune_infos.values())
        count = len(prune_infos)
        final_prune_infos = []
        for i in range(count):
            pinfo = prune_infos[i]
            G_LOGGER.verbose(f"Processing PruneInfo {i}/{count}: {pinfo}")
            t = self.w_name2obj[pinfo.name]
            supported_dtypes = [
                onnx.TensorProto.FLOAT,
                onnx.TensorProto.FLOAT16,
                onnx.TensorProto.BFLOAT16,
            ]
            if not t.data_type in supported_dtypes:
                G_LOGGER.warning(f"Skip {t.name} due to unsupported type {t.data_type}")
                continue
            assert pinfo.axis < len(t.dims)
            dim = t.dims[pinfo.axis]
            if dim % 4 != 0:
                G_LOGGER.verbose(f"Skip non-4 prune axis ({dim} in {t.dims})")
                continue
            final_prune_infos.append(pinfo)

        new_count = len(final_prune_infos)
        G_LOGGER.info(f"Removed {count - new_count} ({count} -> {new_count}) pruning N/A tensor(s)")
        return final_prune_infos

    # Walk nodes to collect the tensors (initializers) that need to be pruned and the axis.
    def collect(self):
        self.walk_nodes()
        prune_infos = self.drop_na()
        return prune_infos


def prune_bf16_tensor(tensor, outer, pdim, pstride):
    G_LOGGER.verbose("Pruning BF16 tensor")
    assert tensor.data_type == onnx.TensorProto.BFLOAT16
    is_raw_data = len(tensor.int32_data) == 0
    data = bytearray(tensor.raw_data) if is_raw_data else tensor.int32_data
    step = 4 if is_raw_data else 2

    ostride = pdim * pstride
    for o in range(outer):
        for i in range(pstride):
            for piter in range(0, pdim, step):

                def short2long(idx):
                    return o * ostride + (piter + idx) * pstride + i

                if is_raw_data:
                    # data is 8bit array, bf16 is 16bit
                    # the index is doubled, and we need twice change for one bf16 value
                    data[short2long(1) * 2] = 0
                    data[short2long(1) * 2 + 1] = 0
                    data[short2long(2) * 2] = 0
                    data[short2long(2) * 2 + 1] = 0
                else:
                    # data is 32bit array, bf16 is 16bit
                    # We use the index but only need to change one value
                    data[short2long(0)] = 0

    if is_raw_data:
        tensor.raw_data = bytes(data)
    return tensor


def prune_tensor(pinfo, tensor):
    G_LOGGER.verbose(f"Pruning {pinfo.name}")
    axis = pinfo.axis
    dims = tensor.dims
    pdim = tensor.dims[axis]

    # figure out the stride
    outer = 1
    pstride = 1
    for i in range(0, axis, 1):
        outer *= dims[i]
    for i in range(axis + 1, len(tensor.dims), 1):
        pstride *= dims[i]
    G_LOGGER.verbose(f"axis {axis} of dims {dims} has stride {pstride} and outer {outer}")

    # We need hacks since BF16 has not been fully enabled in Numpy or ONNX.
    if tensor.data_type is onnx.TensorProto.BFLOAT16:
        return prune_bf16_tensor(tensor, outer, pdim, pstride)

    # prune alongside the axis
    ostride = pdim * pstride
    data = np.array(onnx_numpy_helper.to_array(tensor)).reshape(util.volume(dims))
    for o in range(outer):
        for i in range(pstride):
            for piter in range(0, pdim, 4):

                def short2long(idx):
                    """Convert the short-index to the location in the buffer"""
                    return o * ostride + (piter + idx) * pstride + i

                short_idx = range(4)
                long_idx = [short2long(si) for si in short_idx]
                vals = [data[li] for li in long_idx]
                vals_abs = [abs(v) for v in vals]
                min0_idx = vals_abs.index(min(vals_abs))
                vals_abs[min0_idx] = sys.float_info.max
                min1_idx = vals_abs.index(min(vals_abs))

                min0_idx = short2long(min0_idx)
                min1_idx = short2long(min1_idx)
                np.put(data, min0_idx, 0)
                np.put(data, min1_idx, 0)

    # pack raw data pack and then push to the model
    data = data.reshape(dims)
    return onnx_numpy_helper.from_array(data, name=tensor.name)


def build_new_model(m, new_w_name2obj):
    if len(new_w_name2obj) == 0:
        G_LOGGER.verbose("No need to build new model object")
        return m

    G_LOGGER.info("Replacing weights to build new model object...")
    g = m.graph
    new_initializer = list()
    n = len(g.initializer)
    for i in range(n):
        t = g.initializer[i]
        G_LOGGER.verbose(f"Processing {i}/{n} {t.name}")
        if t.name in new_w_name2obj:
            new_t = new_w_name2obj[t.name]
            new_initializer.append(new_t)
        else:
            new_initializer.append(t)

    new_g = onnx.helper.make_graph(
        nodes=g.node,
        name=g.name,
        inputs=g.input,
        outputs=g.output,
        initializer=new_initializer,
        doc_string=g.doc_string,
        value_info=g.value_info,
    )

    attrs = {
        "ir_version": m.ir_version,
        "producer_name": "polygraphy surgeon prune",
        "opset_imports": [m.opset_import[0]],
    }
    new_m = onnx.helper.make_model(new_g, **attrs)
    return new_m


class Prune(BaseSurgeonSubtool):
    """
    Prune the weights of a model to be 2:4 structured sparsity pattern without regard for accuracy.
    For every four weight values, two will be set to zero.

    **NOTE:** This tool is meant to help functionally test sparsity. It will almost certainly cause significant accuracy degradation and so should NOT be used outside of functional testing.
    """

    def __init__(self):
        super().__init__("prune")

    def show_start_end_logging_impl(self, args):
        return True

    def get_subscriptions_impl(self):
        return [
            ModelArgs(model_opt_required=True, input_shapes_opt_name=False, required_model_type="onnx"),
            OnnxLoadArgs(allow_shape_inference=False, outputs_opt_prefix=False, allow_from_tf=False),
            OnnxSaveArgs(allow_shape_inference=False, output_opt_required=True),
        ]

    def run_impl(self, args):
        model = super().load_model()

        g = model.graph

        gpruner = GraphPruner(g)
        prune_infos = gpruner.collect()
        count = len(prune_infos)
        G_LOGGER.info(f"Going to prune {count} tensors")
        new_w_name2obj = dict()
        for i in range(count):
            pinfo = prune_infos[i]
            tensor = gpruner.w_name2obj[pinfo.name]
            G_LOGGER.verbose(f"Pruning {i}/{count} {pinfo.name}")
            new_t = prune_tensor(pinfo, tensor)
            new_w_name2obj[new_t.name] = new_t
        G_LOGGER.info("Prune done!")

        m_to_save = build_new_model(model, new_w_name2obj)

        super().save_model(m_to_save)
