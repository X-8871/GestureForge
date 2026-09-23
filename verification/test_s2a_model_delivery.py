"""验证阶段 2A 模型交付清单生成器。"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

try:
    from . import s2a_model_delivery as delivery
except ImportError:
    import s2a_model_delivery as delivery


class ModelDeliveryTest(unittest.TestCase):
    """检查 tiny416 模型绑定、层元数据和固定样本清单。"""

    def test_xorshift32_is_repeatable_and_rejects_zero_seed(self) -> None:
        """校验冻结 PRNG 对相同种子生成完全相同的字节序列。"""

        first = delivery.xorshift32(20260922, 64)
        second = delivery.xorshift32(20260922, 64)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        with self.assertRaises(delivery.DeliveryError):
            delivery.xorshift32(0, 1)

    def test_vectorized_preprocess_matches_d2_reference_at_edges(self) -> None:
        """比较向量化预处理与 D2 参考器，覆盖缩放端点和单像素尺寸。"""

        from verification.s1_t02_d2_numeric_reference import preprocess_rgb_uint8_to_chw_int8

        rng = np.random.default_rng(20260922)
        for src_height, src_width, dst_height, dst_width in (
            (3, 5, 8, 8),
            (4, 7, 7, 5),
            (1, 1, 4, 4),
            (5, 5, 5, 5),
            (2, 9, 1, 7),
            (9, 2, 7, 1),
        ):
            with self.subTest(shape=(src_height, src_width, dst_height, dst_width)):
                rgb = rng.integers(0, 256, size=(src_height, src_width, 3), dtype=np.uint8)
                actual = delivery.preprocess_rgb_chw_int8(rgb, dst_width, dst_height)
                expected = preprocess_rgb_uint8_to_chw_int8(rgb.tolist(), dst_width, dst_height)
                self.assertTrue(np.array_equal(actual, np.asarray(expected, dtype=np.int8)))

    def test_full_model_and_fixed_sample_manifest_bindings(self) -> None:
        """生成并核验完整 38 层规格与含多 GT 图片的固定输入。"""

        with tempfile.TemporaryDirectory(prefix="gestureforge_s2a_delivery_") as temporary:
            output_dir = Path(temporary) / "evidence"
            self.assertEqual(delivery.main(["--output-dir", str(output_dir)]), 0)
            model = json.loads((output_dir / "tiny416_model_manifest.json").read_text(encoding="utf-8"))
            samples = json.loads((output_dir / "fixed_test_samples.json").read_text(encoding="utf-8"))
            model_bytes = (output_dir / "tiny416_model_manifest.json").read_bytes()

        self.assertEqual(model["status"], "G0_FROZEN")
        self.assertEqual(len(model["layers"]), 38)
        self.assertEqual(sum(layer["op"] == "convolutional" for layer in model["layers"]), 21)
        self.assertEqual(model["layers"][30]["output_shape_nchw"], [1, 30, 13, 13])
        self.assertEqual(model["layers"][37]["output_shape_nchw"], [1, 30, 26, 26])
        self.assertEqual(model["layers"][30]["tensor_address"], model["layers"][29]["tensor_address"])
        self.assertEqual(model["layers"][37]["tensor_address"], model["layers"][36]["tensor_address"])
        self.assertEqual(
            model["bindings"]["input_preprocess_reference"]["callable"],
            "preprocess_rgb_uint8_to_chw_int8",
        )
        self.assertEqual(samples["sample_count"], 109)
        self.assertEqual([item["frame_id"] for item in samples["samples"]], list(range(109)))
        self.assertTrue(all(item["width"] > 0 and item["height"] > 0 for item in samples["samples"]))
        self.assertEqual(samples["coverage"]["empty_ground_truth"], 3)
        self.assertEqual(samples["coverage"]["full_network_inputs"]["count"], 109)
        self.assertEqual(samples["coverage"]["full_network_inputs"]["official_multi_ground_truth_count"], 2)
        self.assertEqual(samples["coverage"]["full_network_inputs"]["official_additional_multi_ground_truth_samples"], 2)
        self.assertEqual(samples["model_manifest_binding"]["sha256"], hashlib.sha256(model_bytes).hexdigest())
        self.assertEqual(samples["coverage"]["postprocess_fixtures"]["source_commit"], delivery.BASELINE_COMMIT)
        self.assertTrue(all(len(item["pl_input_sha256"]) == 64 for item in samples["samples"]))
        self.assertEqual(
            set(samples["coverage"]["five_classes"]),
            {f"class:{name}" for name in delivery.EXPECTED_CLASSES},
        )
        self.assertEqual(
            model["address_map"]["feature_workspace"]["base_address"],
            delivery.FEATURE_BASE,
        )
        delivery.validate_address_map(model["layers"], model["address_map"])
        self.assertEqual(
            model["control_protocol"]["timeout"],
            "timeout_cycles must be nonzero; count rising edges after the accepted start edge; completion at the Nth edge wins over timeout, otherwise abort at that edge",
        )
        self.assertIn("mem_error_code[2:0]", model["memory_protocol"]["signals"])
        self.assertIn("mem_rstrb[3:0]", model["memory_protocol"]["signals"])
        self.assertEqual(model["memory_protocol"]["error_response_codes"]["1"].split(";")[0], "BAD_ARGUMENT")
        self.assertEqual(model["memory_protocol"]["error_response_codes"]["2"].split(";")[0], "BAD_RANGE")
        self.assertEqual(model["memory_protocol"]["error_response_codes"]["6"].split(";")[0], "INTERNAL")
        self.assertIn("any other nonzero", model["memory_protocol"]["error_code_mapping"])
        self.assertEqual(model["control_protocol"]["error_codes"]["7"], "ACCUMULATOR_OVERFLOW")
        self.assertEqual(
            [item["offset"] for item in model["control_protocol"]["register_map"]],
            ["0x00", "0x04", "0x08", "0x0C", "0x10", "0x14", "0x18", "0x1C", "0x20", "0x24", "0x28", "0x2C", "0x30", "0x34", "0x38", "0x3C"],
        )
        conv = next(layer for layer in model["layers"] if layer["op"] == "convolutional")
        pool = next(layer for layer in model["layers"] if layer["op"] == "maxpool")
        self.assertEqual(conv["padding_value_int8"], 0)
        self.assertEqual(pool["pad_value_int8"], -127)
        self.assertIn("window_origin_yx_at_output_0", pool)
        self.assertIn("padding_lrtb_actual", pool)
        plan = model["operator_test_plan"]
        protocol_vectors = plan["protocol_vectors"]
        self.assertEqual(
            model["control_protocol"]["ready"],
            "csr_ready is high outside hard reset; software must change/deassert valid after each accepted transfer",
        )
        self.assertEqual(protocol_vectors["csr"]["ready_outside_hard_reset"], 1)
        self.assertEqual(protocol_vectors["csr"]["stall_cycles"], [])
        self.assertNotIn("csr_stall_cycles", protocol_vectors)
        self.assertIn("before the next rising edge", protocol_vectors["csr"]["transfer_rule"])
        self.assertEqual(protocol_vectors["memory_stall_cycles"], [0, 1, 2, 7, 3])
        self.assertIn("each memory request class", protocol_vectors["memory_stall_repeat"])
        self.assertNotIn("CSR", protocol_vectors["memory_stall_repeat"])
        operator_event = model["control_protocol"]["operator_completion_event"]
        self.assertEqual(operator_event["signals"], ["operator_result_valid", "operator_error_code[2:0]"])
        self.assertIn("internal PL", operator_event["direction"])
        self.assertIn("one-cycle pulse", operator_event["handshake"])
        self.assertIn("unknown nonzero", operator_event["error"])
        self.assertIn("Nth timeout edge wins", operator_event["timeout_boundary"])
        memory_error_plan = protocol_vectors["memory_error_recovery"]
        self.assertEqual(
            memory_error_plan["response_cases"],
            [
                {"mem_error_code": 6, "expected_csr_error_code": 6},
                {"mem_error_code": 7, "expected_csr_error_code": 6},
            ],
        )
        self.assertEqual(memory_error_plan["expected_status_bits"], {"busy": 0, "done": 0, "error": 1, "pl_owns_buffers": 0})
        self.assertFalse(memory_error_plan["head_output_valid"])
        self.assertIn("ACK bit1", memory_error_plan["recovery"])
        self.assertIn("memory error code 6 and unknown nonzero map to INTERNAL; error ACK then legal recovery", protocol_vectors["required_cases"])
        overflow_plan = protocol_vectors["accumulator_overflow_recovery"]
        overflow_vector = plan["directed_case_vectors"]["int8_mac"][overflow_plan["arithmetic_vector_case_index"]]
        self.assertEqual(overflow_vector["case_index"], 9)
        self.assertIn("not a cfg/GF8 convolution vector", overflow_plan["arithmetic_test_scope"])
        self.assertEqual(overflow_vector["first_int32_overflow_product_index"], overflow_plan["expected_first_int32_overflow_product_index"])
        fault_injection = overflow_plan["controller_fault_injection"]
        self.assertEqual(fault_injection["fixture"], "controller unit test with a behavioral operator backend stub")
        self.assertIn("STATUS.busy=1", fault_injection["after_start"])
        self.assertIn("operator_error_code=7", fault_injection["after_start"])
        self.assertEqual(fault_injection["interface"], "control_protocol.operator_completion_event")
        self.assertEqual(overflow_plan["expected_csr_error_code"], 7)
        self.assertEqual(model["control_protocol"]["error_codes"][str(overflow_plan["expected_csr_error_code"])], "ACCUMULATOR_OVERFLOW")
        self.assertEqual(overflow_plan["expected_status_bits"], {"busy": 0, "done": 0, "error": 1, "pl_owns_buffers": 0})
        self.assertFalse(overflow_plan["head_output_valid"])
        self.assertIn("ACK bit1", overflow_plan["recovery"])
        self.assertIn("INT32 accumulator overflow maps to code 7, invalidates heads and recovers after ACK", protocol_vectors["required_cases"])
        from verification.s1_t02_d2_numeric_reference import checked_int32

        self.assertTrue(all(len(items) == 16 for items in plan["directed_cases_by_operator"].values()))
        vectors = plan["directed_case_vectors"]
        self.assertEqual([item["case_index"] for item in vectors["int8_mac"]], list(range(16)))
        self.assertTrue(all(item["k"] == len(item["activation_int8"]) == len(item["weight_int8"]) for item in vectors["int8_mac"]))
        for vector in vectors["int8_mac"]:
            exact = vector["bias_int32"] + sum(a * w for a, w in zip(vector["activation_int8"], vector["weight_int8"]))
            self.assertEqual(vector["exact_int64_sum"], exact)
            accumulator = vector["bias_int32"]
            checked_accumulator = checked_int32(vector["bias_int32"], "bias")
            overflow_index = None
            for index, (activation, weight) in enumerate(zip(vector["activation_int8"], vector["weight_int8"])):
                accumulator += activation * weight
                if overflow_index is None and not (-(1 << 31) <= accumulator <= (1 << 31) - 1):
                    overflow_index = index
                if overflow_index is None:
                    checked_accumulator = checked_int32(checked_accumulator + activation * weight, f"accumulator[{index}]")
            self.assertEqual(vector["first_int32_overflow_product_index"], overflow_index)
            self.assertEqual(vector["expected_int32_result"], exact if overflow_index is None else None)
            if overflow_index is None:
                self.assertEqual(checked_accumulator, vector["expected_int32_result"])
            else:
                with self.assertRaises(OverflowError):
                    checked_value = checked_int32(vector["bias_int32"], "bias")
                    for index, (activation, weight) in enumerate(zip(vector["activation_int8"], vector["weight_int8"])):
                        checked_value = checked_int32(checked_value + activation * weight, f"accumulator[{index}]")
        self.assertEqual(vectors["int8_mac"][8]["exact_int64_sum"], (1 << 31) - 1)
        self.assertEqual(vectors["int8_mac"][9]["first_int32_overflow_product_index"], 0)
        self.assertEqual(vectors["int8_mac"][10]["exact_int64_sum"], -(1 << 31))
        self.assertEqual(vectors["int8_mac"][11]["first_int32_overflow_product_index"], 0)
        package_path = Path(model["bindings"]["gf8_package"]["path"])
        _, package_layers = delivery.parse_package(package_path)
        conv_layers = {str(layer["layer_index"]): layer for layer in model["layers"] if layer["op"] == "convolutional"}
        conv_target_rules = [
            ("first", "first", "first"), ("first", "first", "first"),
            ("first", "first", "first"), ("first", "first", "first"),
            ("middle", "middle", "middle"), ("middle", "middle", "middle"),
            ("first", "first", "first"), ("last", "last", "last"),
            ("first", "first", "first"), ("last", "last", "last"),
            ("first", "first", "first"), ("last", "last", "last"),
            ("last", "last", "last"), ("first", "first", "first"),
            ("middle", "middle", "middle"), ("middle", "middle", "middle"),
        ]
        self.assertEqual(set(vectors["convolutional"]), set(conv_layers))
        for layer_key, layer_vectors in vectors["convolutional"].items():
            self.assertEqual([item["case_index"] for item in layer_vectors], list(range(16)))
            layer = conv_layers[layer_key]
            package_layer = package_layers[layer["weight_layer_index"]]
            for vector in layer_vectors:
                channel = vector["target_output_nchw"][1]
                expected_weights = package_layer.quantized_weights[channel].reshape(-1).astype(np.int16).tolist()
                self.assertEqual(vector["weight_reduction_int8"], expected_weights)
                self.assertEqual(vector["bias_int32"], layer["bias_accumulator_int32_per_output_channel"][channel])
                self.assertEqual(len(vector["input_reduction_int8"]), len(expected_weights))
                self.assertEqual(len(vector["source_reduction_values_int8"]), len(expected_weights))
                self.assertEqual(len(vector["input_reduction_int8"]), len(vector["weight_reduction_int8"]))
                self.assertEqual(vector["case_name"], plan["directed_cases_by_operator"]["convolutional"][vector["case_index"]])
                target_rules = conv_target_rules[vector["case_index"]]
                expected_target = [
                    0,
                    0 if target_rules[0] == "first" else layer["output_shape_nchw"][1] - 1 if target_rules[0] == "last" else layer["output_shape_nchw"][1] // 2,
                    0 if target_rules[1] == "first" else layer["output_shape_nchw"][2] - 1 if target_rules[1] == "last" else layer["output_shape_nchw"][2] // 2,
                    0 if target_rules[2] == "first" else layer["output_shape_nchw"][3] - 1 if target_rules[2] == "last" else layer["output_shape_nchw"][3] // 2,
                ]
                self.assertEqual(vector["target_output_nchw"], expected_target)
                self.assertLess(channel, layer["output_shape_nchw"][1])
                self.assertLess(vector["target_output_nchw"][2], layer["output_shape_nchw"][2])
                self.assertLess(vector["target_output_nchw"][3], layer["output_shape_nchw"][3])
                self.assertEqual(vector["reduction_order"], "local_input_channel, kernel_y, kernel_x; flattened index=((channel*kernel_h)+kernel_y)*kernel_w+kernel_x")
                kernel_height, kernel_width = layer["kernel_hw"]
                origin_y, origin_x = vector["input_patch_origin_yx"]
                for index, (source_value, effective_value) in enumerate(zip(vector["source_reduction_values_int8"], vector["input_reduction_int8"])):
                    tap_y = (index // kernel_width) % kernel_height
                    tap_x = index % kernel_width
                    input_y, input_x = origin_y + tap_y, origin_x + tap_x
                    in_bounds = 0 <= input_y < layer["input_shape_nchw"][2] and 0 <= input_x < layer["input_shape_nchw"][3]
                    self.assertEqual(source_value is not None, in_bounds)
                    self.assertEqual(effective_value, source_value if in_bounds else vector["padding_value_int8"])
                products = [a * w for a, w in zip(vector["input_reduction_int8"], vector["weight_reduction_int8"])]
                if vector["first_int32_overflow_product_index"] is None:
                    checked_value = checked_int32(vector["bias_int32"], "bias")
                    for index, product in enumerate(products):
                        checked_value = checked_int32(checked_value + product, f"accumulator[{index}]")
                    self.assertEqual(checked_value, vector["expected_int32_result"])
                else:
                    with self.assertRaises(OverflowError):
                        checked_value = checked_int32(vector["bias_int32"], "bias")
                        for index, product in enumerate(products):
                            checked_value = checked_int32(checked_value + product, f"accumulator[{index}]")
                inputs = vector["source_reduction_values_int8"]
                valid_inputs = [value for value in inputs if value is not None]
                case_index = vector["case_index"]
                if case_index in (0, 12):
                    self.assertTrue(all(value == 0 for value in valid_inputs))
                elif case_index == 1:
                    self.assertTrue(all(value == 127 for value in valid_inputs))
                elif case_index == 2:
                    self.assertTrue(all(value == -127 for value in valid_inputs))
                elif case_index == 3:
                    self.assertEqual(inputs, [None if value is None else (-127 if index % 2 == 0 else 127) for index, value in enumerate(inputs)])
                elif case_index == 4:
                    self.assertEqual(inputs[0], 127)
                    self.assertTrue(all(value in (0, None) for value in inputs[1:]))
                elif case_index == 5:
                    self.assertTrue(all(value in (0, None) for value in inputs[:-1]))
                    self.assertEqual(inputs[-1], 127)
                elif case_index in (8, 9):
                    self.assertEqual(inputs.count(127), 1)
                    tap_y = layer["kernel_hw"][0] // 2 if layer["kernel_hw"][0] % 2 else 0
                    tap_x = layer["kernel_hw"][1] // 2 if layer["kernel_hw"][1] % 2 else 0
                    expected_index = tap_y * layer["kernel_hw"][1] + tap_x
                    self.assertEqual(inputs[expected_index], 127)
                elif case_index == 10:
                    self.assertTrue(all(value == 1 for value in valid_inputs))
                elif case_index == 11:
                    self.assertTrue(all(value == -1 for value in valid_inputs))
                elif case_index == 13:
                    self.assertEqual(inputs, [None if value is None else (-1 if index % 2 == 0 else 1) for index, value in enumerate(inputs)])
                elif case_index == 14:
                    self.assertEqual(inputs[0], 1)
                    self.assertTrue(all(value in (0, None) for value in inputs[1:]))
                elif case_index == 15:
                    self.assertTrue(all(value in (0, None) for value in inputs[:-1]))
                    self.assertEqual(inputs[-1], -1)
                if case_index in (6, 7):
                    nonzero = [index for index, value in enumerate(inputs) if value not in (0, None)]
                    self.assertEqual(len(nonzero), 1)
                    reduction_index = nonzero[0]
                    local_channel = reduction_index // (kernel_height * kernel_width)
                    tap_y = (reduction_index // kernel_width) % kernel_height
                    tap_x = reduction_index % kernel_width
                    origin_y, origin_x = vector["input_patch_origin_yx"]
                    input_y, input_x = origin_y + tap_y, origin_x + tap_x
                    expected_channel = 0 if case_index == 6 else layer["input_shape_nchw"][1] - 1
                    self.assertEqual(vector["input_channel_base"] + local_channel, expected_channel)
                    if case_index == 6:
                        self.assertEqual((input_y, input_x), (max(0, origin_y), max(0, origin_x)))
                    else:
                        self.assertEqual((input_y, input_x), (min(layer["input_shape_nchw"][2] - 1, origin_y + kernel_height - 1), min(layer["input_shape_nchw"][3] - 1, origin_x + kernel_width - 1)))
        self.assertEqual(set(vectors["route"]), {str(layer["layer_index"]) for layer in model["layers"] if layer["op"] == "route"})
        for layer_key, layer_vectors in vectors["route"].items():
            layer = model["layers"][int(layer_key)]
            self.assertEqual([item["case_index"] for item in layer_vectors], list(range(16)))
            for vector in layer_vectors:
                self.assertEqual(vector["case_name"], plan["directed_cases_by_operator"]["route"][vector["case_index"]])
                source_scales = [source["input_scale"] for source in vector["source_tensors"]]
                scale_mismatch = any(scale != source_scales[0] for scale in source_scales[1:])
                self.assertEqual(
                    vector["scale_rule_applied"],
                    "unlike_source_scales_requantize" if scale_mismatch else "equal_source_scales_identity",
                )
                if vector["case_index"] == 9:
                    expected_conversion_source = next(
                        (index for index, scale in enumerate(source_scales) if scale != vector["target_scale"]),
                        None,
                    )
                    self.assertEqual(vector["scale_conversion_source_index"], expected_conversion_source)
                    self.assertEqual(scale_mismatch, expected_conversion_source is not None)
                    self.assertEqual(vector["scale_conversion_input_value_int8"], -127 if expected_conversion_source is not None else None)
                    for source_index, source in enumerate(vector["source_tensors"]):
                        if expected_conversion_source is not None:
                            expected_values = [-127] * len(source["source_values_int8"]) if source_index == expected_conversion_source else [0] * len(source["source_values_int8"])
                        else:
                            expected_values = [-1 if index % 2 == 0 else 1 for index in range(len(source["source_values_int8"]))]
                        self.assertEqual(source["source_values_int8"], expected_values)
                        if source_index == expected_conversion_source:
                            self.assertTrue(all(value != -127 for value in source["requantized_values_int8"]))
                            self.assertTrue(any(value != input_value for value, input_value in zip(source["requantized_values_int8"], source["source_values_int8"])))
                output = []
                for source_index, source in enumerate(vector["source_tensors"]):
                    self.assertEqual(source["selected_source_channel_range"], layer["route_source_channel_ranges"][source_index])
                    start, end = source["selected_source_channel_range"]
                    self.assertEqual(source["selected_source_channels"], list(range(start, end)))
                    self.assertEqual(len(source["source_values_int8"]), len(source["selected_source_channels"]))
                    self.assertEqual(len(source["requantized_values_int8"]), len(source["source_values_int8"]))
                    independently_requantized = []
                    for value in source["source_values_int8"]:
                        scaled = value * source["input_scale"] / vector["target_scale"]
                        rounded = int(np.sign(scaled) * np.floor(abs(scaled) + 0.5))
                        independently_requantized.append(min(127, max(-127, rounded)))
                    self.assertEqual(source["requantized_values_int8"], independently_requantized)
                    output.extend(source["requantized_values_int8"])
                self.assertEqual(output, vector["output_channel_values_int8"])
                self.assertEqual(len(output), layer["output_shape_nchw"][1])
        self.assertEqual(model["layers"][3]["route_source_channel_ranges"], [[32, 64]])
        self.assertEqual(model["layers"][11]["route_source_channel_ranges"], [[64, 128]])
        self.assertEqual(model["layers"][3]["output_shape_nchw"][1], 32)
        self.assertEqual(model["layers"][11]["output_shape_nchw"][1], 64)
        for route_layer_index in (3, 11):
            route_vectors = {item["case_index"]: item for item in vectors["route"][str(route_layer_index)]}
            channels = model["layers"][route_layer_index]["output_shape_nchw"][1]
            self.assertEqual(route_vectors[0]["output_channel_values_int8"], [0] * channels)
            self.assertEqual(route_vectors[1]["output_channel_values_int8"], [127] * channels)
            self.assertEqual(route_vectors[2]["output_channel_values_int8"], [-127] * channels)
            self.assertEqual(route_vectors[4]["output_channel_values_int8"], [127] * channels)
            self.assertEqual(route_vectors[5]["output_channel_values_int8"], [127] * channels)
            self.assertEqual(route_vectors[6]["output_channel_values_int8"], [127] + [0] * (channels - 1))
            self.assertEqual(route_vectors[7]["output_channel_values_int8"], [0] * (channels - 1) + [127])
            self.assertEqual(route_vectors[8]["output_channel_values_int8"], [1] * channels)
            self.assertEqual(route_vectors[9]["output_channel_values_int8"], [-1 if index % 2 == 0 else 1 for index in range(channels)])
        pool_layers = {str(layer["layer_index"]): layer for layer in model["layers"] if layer["op"] == "maxpool"}
        self.assertEqual(set(vectors["maxpool"]), set(pool_layers))
        for layer_key, layer_vectors in vectors["maxpool"].items():
            layer = pool_layers[layer_key]
            self.assertEqual([item["case_index"] for item in layer_vectors], list(range(16)))
            for vector in layer_vectors:
                self.assertEqual(vector["case_name"], plan["directed_cases_by_operator"]["maxpool"][vector["case_index"]])
                expected_candidates = [source_value if source_value is not None else vector["pad_value_int8"] for source_value in vector["source_window_values_int8"]]
                self.assertEqual(expected_candidates, vector["candidate_values_int8"])
                self.assertEqual(vector["expected_output_int8"], max(expected_candidates))
                self.assertEqual(vector["window_order"], "kernel_y then kernel_x; row-major tap index=kernel_y*kernel_width+kernel_x")
                self.assertEqual(len(vector["source_window_values_int8"]), 4)
                if vector["case_index"] == 0:
                    self.assertEqual(vector["candidate_values_int8"], [0] * 4)
                elif vector["case_index"] == 1:
                    self.assertEqual(vector["candidate_values_int8"], [127] * 4)
                elif vector["case_index"] == 2:
                    self.assertEqual(vector["candidate_values_int8"], [-127] * 4)
                elif vector["case_index"] == 3:
                    self.assertEqual(vector["candidate_values_int8"], [-127, 127, -127, 127])
                elif 4 <= vector["case_index"] <= 7:
                    expected = [-127] * 4
                    expected[vector["case_index"] - 4] = 127
                    self.assertEqual(vector["candidate_values_int8"], expected)
                elif 8 <= vector["case_index"] <= 11:
                    expected = [127] * 4
                    expected[vector["case_index"] - 8] = -127
                    self.assertEqual(vector["candidate_values_int8"], expected)
                elif vector["case_index"] == 12:
                    self.assertEqual(vector["candidate_values_int8"], [1, 2, 3, 4])
                elif vector["case_index"] == 13:
                    self.assertEqual(vector["candidate_values_int8"], [-1, -2, -3, -4])
                elif vector["case_index"] == 14:
                    self.assertEqual(vector["candidate_values_int8"], [11, 12, 13, 14])
                elif vector["case_index"] == 15:
                    self.assertEqual(vector["candidate_values_int8"], [-11, -12, -13, -14])
                for source_value, candidate, coordinate in zip(vector["source_window_values_int8"], vector["candidate_values_int8"], vector["input_coordinates_cyx"]):
                    if coordinate is None:
                        self.assertIsNone(source_value)
                        self.assertEqual(candidate, -127)
                    else:
                        self.assertEqual(source_value, candidate)
        upsample_layers = {str(layer["layer_index"]): layer for layer in model["layers"] if layer["op"] == "upsample"}
        self.assertEqual(set(vectors["upsample"]), set(upsample_layers))
        for layer_key, layer_vectors in vectors["upsample"].items():
            layer = upsample_layers[layer_key]
            self.assertEqual([item["case_index"] for item in layer_vectors], list(range(16)))
            for vector in layer_vectors:
                self.assertEqual(vector["case_name"], plan["directed_cases_by_operator"]["upsample"][vector["case_index"]])
                expected_values = [1, -1, 2, 3, 4, 5, 6, 7, 0, 127, -127, -127, 17, -17, 23, -23]
                self.assertEqual(vector["queries"][0]["source_value_int8"], expected_values[vector["case_index"]])
                self.assertEqual(vector["source_tensor_default_int8"], 0)
                self.assertTrue(all(query["output_nchw"][1] < layer["output_shape_nchw"][1] for query in vector["queries"]))
                for query in vector["queries"]:
                    _, channel, row, col = query["output_nchw"]
                    self.assertEqual(query["source_cyx"], [channel, row // layer["stride"], col // layer["stride"]])
                    self.assertEqual(query["source_value_int8"], vector["queries"][0]["source_value_int8"])
                    self.assertEqual(query["expected_output_int8"], query["source_value_int8"])
                if vector["case_index"] in (6, 7):
                    self.assertEqual(len(vector["queries"]), 2)
                    self.assertTrue(vector["all_queries_share_source_coordinate"])
        yolo_layers = {str(layer["layer_index"]): layer for layer in model["layers"] if layer["op"] == "yolo"}
        self.assertEqual(set(vectors["yolo"]), set(yolo_layers))
        for layer_key, layer_vectors in vectors["yolo"].items():
            layer = yolo_layers[layer_key]
            source_layer = model["layers"][layer["output_tensor_index"]]
            _, channels, height, width = layer["output_shape_nchw"]
            self.assertEqual([item["case_index"] for item in layer_vectors], list(range(16)))
            self.assertEqual(layer["tensor_address"], source_layer["tensor_address"])
            for vector in layer_vectors:
                self.assertEqual(vector["case_name"], plan["directed_cases_by_operator"]["yolo"][vector["case_index"]])
                self.assertTrue(vector["zero_copy_alias"])
                for query in vector["queries"]:
                    self.assertEqual(query["channel"], query["anchor_local"] * 10 + query["entry"])
                    self.assertEqual(query["tensor_byte_offset"], (query["channel"] * height + query["row"]) * width + query["column"])
                    self.assertEqual(query["tensor_byte_address"], layer["tensor_address"] + query["tensor_byte_offset"])
                    self.assertEqual(query["source_tensor_byte_address"], source_layer["tensor_address"] + query["tensor_byte_offset"])
                if vector["case_index"] == 14:
                    self.assertTrue(vector["contiguous_channel_boundary"])
                if vector["case_index"] == 15:
                    self.assertTrue(vector["tail_byte_query"])
        self.assertTrue(all(not any(pool_layer["padding_lrtb_actual"]) for pool_layer in plan["actual_cfg_edge_facts"]["maxpool_layers"].values()))
        self.assertEqual(len(plan["actual_cfg_edge_facts"]["maxpool_layers"]), 3)
        self.assertTrue(all(pool_layer["kernel_hw"] == [2, 2] and pool_layer["stride_hw"] == [2, 2] and pool_layer["darknet_padding_parameter"] == 1 and pool_layer["window_origin_yx_at_output_0"] == [0, 0] for pool_layer in plan["actual_cfg_edge_facts"]["maxpool_layers"].values()))
        self.assertEqual(plan["actual_cfg_edge_facts"]["conv_1x1_layers"], [7, 15, 23, 27, 29, 32, 36])
        self.assertTrue(all(layer["padding_lrtb"] == [0, 0, 0, 0] for layer in model["layers"] if layer["op"] == "convolutional" and layer["kernel_hw"] == [1, 1]))
        self.assertTrue(plan["actual_cfg_edge_facts"]["configured_activation_is_not_overridden"])
        fixtures = plan["separate_unit_fixtures"]
        self.assertIn("not full cfg layers", fixtures["scope"])
        from verification.s1_t02_d2_int8_forward import (
            make_patches,
            maxpool,
            round_away_array,
            saturate_array,
        )
        conv_fixture = fixtures["conv_zero_padding_3x3"]
        input_tensor = np.asarray(conv_fixture["input_int8_nchw"], dtype=np.int8)[0]
        weight_tensor = np.asarray(conv_fixture["weight_oihw"], dtype=np.int8).reshape(1, -1)
        patches, out_h, out_w = make_patches(input_tensor, 3, 1, 1)
        conv_result = (weight_tensor.astype(np.int64) @ patches.astype(np.int64)).reshape(1, out_h, out_w)
        self.assertEqual(conv_result.reshape(1, 1, out_h, out_w).tolist(), conv_fixture["expected_accumulator_nchw"])
        pool_fixture = fixtures["maxpool_darknet_padding"]
        pool_input = np.asarray(pool_fixture["input_int8_nchw"], dtype=np.int8)[0]
        pool_result = maxpool(pool_input, 3, 1, 2)
        self.assertEqual(pool_result.reshape(1, 1, 4, 4).tolist(), pool_fixture["expected_output_nchw"])
        rounding_fixture = fixtures["requantize_half_away_and_saturate"]
        quantized = saturate_array(round_away_array(np.asarray(rounding_fixture["scaled_values"])))
        self.assertEqual(quantized.tolist(), rounding_fixture["expected_int8"])
        leaky_fixture = fixtures["leaky_relu_0_1"]
        activated = np.asarray(leaky_fixture["scaled_pre_activation"], dtype=np.float64)
        activated = np.where(activated >= 0.0, activated, activated * 0.1)
        self.assertEqual(activated.tolist(), leaky_fixture["expected_scaled_output"])
        self.assertEqual(
            saturate_array(round_away_array(activated)).tolist(),
            leaky_fixture["expected_quantized_int8"],
        )
        route_fixture = fixtures["route_half_away"]
        route_source0 = saturate_array(round_away_array(
            np.asarray(route_fixture["source0_values"]) * route_fixture["source_scales"][0] / route_fixture["target_scale"]
        ))
        self.assertEqual(route_source0.tolist(), route_fixture["source0_expected"])
        upsample_fixture = fixtures["upsample_nearest_repeat"]
        upsample_input = np.asarray(upsample_fixture["input_int8_nchw"], dtype=np.int8)
        upsample_output = np.repeat(np.repeat(upsample_input, 2, axis=2), 2, axis=3)
        self.assertEqual(upsample_output.tolist(), upsample_fixture["expected_output_nchw"])
        bad_map = json.loads(json.dumps(model["address_map"]))
        bad_map["weight_package"]["address"] = bad_map["input"]["address"]
        with self.assertRaisesRegex(delivery.DeliveryError, "范围发生重叠"):
            delivery.validate_address_map(model["layers"], bad_map)


if __name__ == "__main__":
    unittest.main()
