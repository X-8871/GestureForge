#!/usr/bin/env python3
"""S4-C 离线回放与对拍工具的单元与轻量集成测试。

运行方式（仓库根目录）：

    python -m unittest verification.test_s4_replay_compare -v

覆盖范围：
  1. 上游绑定 SHA 与 S4-A 契约一致性（含 manifest 两头常量交叉核对）；
  2. 冻结 D9 解码器加载、API 与工具函数；
  3. 两头抽取计划：偏移/长度/scale 来自 T25 索引并与 T29 双向核对；
  4. INT8 → float64 反量化；
  5. 逐框对拍：离散字段全等、score/xyxy 容限边界与 mismatch 定位；
  6. --limit/--seed 随机子集的选择元数据（种子/样本数/id 列表）；
  7. --actual 目录三种格式与长度校验；
  8. 单样本 golden 对拍 PASS + 1 字节篡改必须 FAIL 并定位到样本/字段；
  9. 篡改反例自检（--self-test-tamper 语义）与 CLI 退出码契约。

需要主树 T25 分片/上游文件的用例在缺失时显式 skip，不伪称通过。
测试只写系统临时目录，不写工作树内的业务文件。
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import s4_replay_compare as s4c  # noqa: E402

SAMPLE_ID = "test_fist_000"
_CACHE: dict[str, object] = {}


def upstream() -> dict[str, object]:
    """加载一次上游数据集供多个用例共享。"""

    if "paths" not in _CACHE:
        paths = s4c.resolve_upstream_paths()
        index, reference, catalog = s4c.load_upstream_dataset(paths)
        _CACHE.update(
            {
                "paths": paths,
                "index": index,
                "reference": reference,
                "catalog": catalog,
                "idx": {str(item["sample_id"]): item for item in index["samples"]},
                "ref": {str(item["sample_id"]): item for item in reference["samples"]},
                "cat": {str(item["sample_id"]): item for item in catalog["samples"]},
            }
        )
    return _CACHE


def main_tree_ready() -> bool:
    """主树上游文件与分片目录是否可用。"""

    paths = s4c.resolve_upstream_paths()
    return (
        paths.t25_index.is_file()
        and paths.t29_ref.is_file()
        and paths.catalog.is_file()
        and paths.manifest.is_file()
        and paths.tensors_dir.is_dir()
    )


def decoder_binding() -> s4c.DecoderBinding:
    """按冻结路径加载 D9（带缓存）。"""

    if "decoder" not in _CACHE:
        paths = s4c.resolve_upstream_paths()
        _CACHE["decoder"] = s4c.load_frozen_decoder(paths.decoder_dir)
    return _CACHE["decoder"]  # type: ignore[return-value]


class UpstreamBindingTests(unittest.TestCase):
    """上游冻结绑定与解码器加载。"""

    def test_expected_sha_matches_s4a_contract(self) -> None:
        # 工具内声明的期望 SHA 必须与 S4-A 契约逐项一致，避免口径漂移。
        contract, contract_sha = s4c.load_s4a_contract()
        self.assertIsNotNone(contract, "S4-A 契约缺失")
        self.assertEqual(contract_sha, s4c.sha256_file(s4c.S4A_CONTRACT_PATH))
        bindings = {item["id"]: item for item in contract["upstream_bindings"]}
        for binding_id, expected in s4c.EXPECTED_SHA256.items():
            self.assertIn(binding_id, bindings)
            self.assertEqual(bindings[binding_id]["sha256"], expected, binding_id)

    @unittest.skipUnless(main_tree_ready(), "主树 T25/T29/T01 上游不可用")
    def test_verify_upstream_files_all_match(self) -> None:
        paths = s4c.resolve_upstream_paths()
        records, failures = s4c.verify_upstream_files(paths)
        self.assertEqual(failures, [], f"上游校验失败：{failures}")
        statuses = {item["id"]: item.get("status") for item in records}
        for binding_id in s4c.EXPECTED_SHA256:
            self.assertIn(statuses[binding_id], {"MATCH", "MATCH_AFTER_LF_NORMALIZATION"}, binding_id)
        self.assertEqual(statuses["s2a_t25_tensor_shards"], "MATCH")

    @unittest.skipUnless(s4c.resolve_upstream_paths().manifest.is_file(), "T01 manifest 不可用")
    def test_manifest_head_constants_crosscheck(self) -> None:
        report = s4c.check_manifest_heads(s4c.resolve_upstream_paths().manifest)
        self.assertEqual(report["status"], "PASS", report["failures"])
        by_name = {item["name"]: item for item in report["heads"]}
        self.assertEqual(set(by_name), {"head13", "head26"})
        self.assertEqual(by_name["head13"]["manifest_length_bytes"], 5070)
        self.assertEqual(by_name["head26"]["manifest_length_bytes"], 20280)
        self.assertEqual(by_name["head13"]["layer_output_scale"], 0.24267549589862975)
        self.assertEqual(by_name["head26"]["layer_output_scale"], 0.30223452951025775)

    def test_decoder_loads_with_frozen_api(self) -> None:
        binding = decoder_binding()
        self.assertEqual(binding.sha256, s4c.EXPECTED_SHA256["s1_t02_d9_decoder"])
        self.assertEqual(binding.api, "decode_yolov4_tiny416")
        self.assertEqual(
            binding.dependency_sha256, s4c.EXPECTED_SHA256["s1_t02_d6_metrics"]
        )
        specs = tuple((spec.name, spec.grid_width, spec.anchor_mask) for spec in binding.module.HEAD_SPECS)
        self.assertEqual(specs, (("13x13", 13, (3, 4, 5)), ("26x26", 26, (1, 2, 3))))
        with self.assertRaises(s4c.S4CError):
            s4c.decode_heads(binding, {"head13": [0.0] * 5070, "head26": [0.0] * 20280}, (416, 416), 0.1)

    @unittest.skipUnless(main_tree_ready(), "主树上游不可用")
    def test_dataset_alignment(self) -> None:
        data = upstream()
        self.assertEqual(len(data["idx"]), 109)  # type: ignore[arg-type]
        self.assertEqual(list(data["idx"]), list(data["ref"]))  # type: ignore[arg-type]
        self.assertEqual(list(data["idx"]), list(data["cat"]))  # type: ignore[arg-type]


class HeadPlanTests(unittest.TestCase):
    """两头抽取计划（偏移不硬编码）。"""

    @unittest.skipUnless(main_tree_ready(), "主树上游不可用")
    def test_head_plan_offsets_and_lengths(self) -> None:
        data = upstream()
        plans = s4c.build_head_plans(data["idx"][SAMPLE_ID], data["ref"][SAMPLE_ID])  # type: ignore[index]
        self.assertEqual(set(plans), {"head13", "head26"})
        self.assertEqual(plans["head13"].byte_length, 5070)
        self.assertEqual(plans["head26"].byte_length, 20280)
        self.assertEqual(plans["head13"].byte_offset, 10772736)
        self.assertEqual(plans["head26"].byte_offset, 11361870)
        self.assertEqual(plans["head13"].scale, 0.24267549589862975)
        self.assertEqual(plans["head26"].scale, 0.30223452951025775)
        self.assertEqual(plans["head13"].shape_nchw, (1, 30, 13, 13))
        self.assertEqual(plans["head26"].shape_nchw, (1, 30, 26, 26))
        self.assertIn("t25_index.network.tensors", plans["head13"].offset_source)
        # 偏移来源必须是索引的 yolo 条目，而不是 T29 参考（口径要求）。
        yolo = [t for t in data["idx"][SAMPLE_ID]["network"]["tensors"] if t["op"] == "yolo"]  # type: ignore[index]
        self.assertEqual(
            plans["head13"].byte_offset, next(t for t in yolo if t["layer_index"] == 30)["byte_offset"]
        )

    @unittest.skipUnless(main_tree_ready(), "主树上游不可用")
    def test_head_plan_detects_inconsistent_reference(self) -> None:
        data = upstream()
        index_sample = json.loads(json.dumps(data["idx"][SAMPLE_ID]))  # type: ignore[index]
        t29_sample = json.loads(json.dumps(data["ref"][SAMPLE_ID]))  # type: ignore[index]
        t29_sample["head_tensors"]["head13"]["byte_offset"] += 1
        with self.assertRaises(s4c.UpstreamError):
            s4c.build_head_plans(index_sample, t29_sample)

    def test_head_name_from_shape_rejects_unknown(self) -> None:
        with self.assertRaises(s4c.UpstreamError):
            s4c._head_name_from_shape((1, 30, 7, 7))


class DequantizeTests(unittest.TestCase):
    """INT8 → float64 反量化。"""

    def test_values_and_scale(self) -> None:
        data = bytes([0x80, 0x00, 0x7F, 0xFF])  # -128, 0, 127, -1
        out = s4c.dequantize_int8(data, 0.5)
        self.assertEqual(out, [-64.0, 0.0, 63.5, -0.5])
        self.assertTrue(all(isinstance(item, float) for item in out))

    def test_scale_is_applied_once(self) -> None:
        scale = 0.24267549589862975
        out = s4c.dequantize_int8(bytes([1, 2]), scale)
        self.assertAlmostEqual(out[0], scale, places=18)
        self.assertAlmostEqual(out[1], 2 * scale, places=18)


class CompareHeadBytesTests(unittest.TestCase):
    """两头 INT8 字节逐值比较。"""

    def test_identical_and_single_diff(self) -> None:
        golden = bytes(range(20))
        identical = s4c.compare_head_bytes(golden, golden)
        self.assertTrue(identical["identical"])
        self.assertEqual(identical["diff_byte_count"], 0)
        self.assertIsNone(identical["first_diff_offset"])
        mutated = bytearray(golden)
        mutated[3] = 99
        mutated[9] = 0
        diff = s4c.compare_head_bytes(golden, bytes(mutated))
        self.assertFalse(diff["identical"])
        self.assertEqual(diff["diff_byte_count"], 2)
        self.assertEqual(diff["first_diff_offset"], 3)
        self.assertEqual(diff["expected_byte"], 3)
        self.assertEqual(diff["actual_byte"], 99)
        self.assertEqual(diff["diff_offsets_preview"], [3, 9])

    def test_length_mismatch_is_not_identical(self) -> None:
        diff = s4c.compare_head_bytes(b"\x01\x02\x03", b"\x01\x02")
        self.assertFalse(diff["identical"])
        self.assertFalse(diff["length_match"])
        self.assertEqual(diff["compared_bytes"], 2)


class CompareTests(unittest.TestCase):
    """逐框对拍语义。"""

    @staticmethod
    def _record(class_id: int = 0, score: float = 0.5, box: tuple[float, float, float, float] = (0.1, 0.2, 0.3, 0.4), order: int = 7) -> dict:
        return {
            "class_id": class_id,
            "class_name": s4c.FROZEN_CLASSES[class_id],
            "score": score,
            "xyxy": list(box),
            "source_order": order,
        }

    def test_exact_match_passes(self) -> None:
        result = s4c.compare_detections([self._record()], [self._record()], 1e-6)
        self.assertEqual(result["mismatches"], [])
        self.assertEqual(result["max_score_abs_error"], 0.0)
        self.assertEqual(result["max_xyxy_abs_error"], 0.0)

    def test_tolerance_boundary(self) -> None:
        # 口径：绝对误差 ≤ 1e-6 通过，> 1e-6 判 mismatch（比较的是 float64 计算差值）。
        # 这里取二进制可精确表示的边界值，避免"数学上恰等于 1e-6 但表示误差使其略大"的歧义；
        # 2A 冻结回放是同样的 float64 运算，golden 对拍的实际误差恒为 0.0。
        within = self._record(score=1.0 + 1e-6)
        self.assertEqual(
            s4c.compare_detections([self._record(score=1.0)], [within], 1e-6)["mismatches"], []
        )
        beyond = self._record(score=1.0 + 2e-6)
        mismatches = s4c.compare_detections([self._record(score=1.0)], [beyond], 1e-6)["mismatches"]
        self.assertEqual([item["field"] for item in mismatches], ["score"])
        self.assertAlmostEqual(mismatches[0]["abs_error"], 2e-6, places=12)
        self.assertEqual(mismatches[0]["tolerance"], 1e-6)

    def test_xyxy_component_localization(self) -> None:
        actual = self._record(box=(0.1, 0.2, 0.3, 0.4 + 5e-6))
        mismatches = s4c.compare_detections([self._record()], [actual], 1e-6)["mismatches"]
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0]["field"], "xyxy[3]")
        self.assertEqual(mismatches[0]["component"], 3)
        self.assertEqual(mismatches[0]["index"], 0)

    def test_discrete_fields_and_count(self) -> None:
        expected = [self._record(class_id=0, order=7), self._record(class_id=1, order=9)]
        actual = [self._record(class_id=1, order=7)]
        mismatches = s4c.compare_detections(expected, actual, 1e-6)["mismatches"]
        fields = [item["field"] for item in mismatches]
        self.assertIn("detection_count", fields)
        self.assertIn("class_id", fields)
        self.assertIn("class_name", fields)

    def test_source_order_mismatch_is_discrete(self) -> None:
        mismatches = s4c.compare_detections(
            [self._record(order=7)], [self._record(order=8)], 1e-6
        )["mismatches"]
        self.assertEqual([(item["field"], item["kind"]) for item in mismatches], [("source_order", "discrete")])


class SelectionTests(unittest.TestCase):
    """--limit/--seed 选择元数据。"""

    def setUp(self) -> None:
        self.ids = [f"sample_{index:03d}" for index in range(109)]

    def test_full_selection_default(self) -> None:
        selected, meta = s4c.select_sample_ids(self.ids)
        self.assertEqual(len(selected), 109)
        self.assertEqual(meta["rule"], "full_all_samples")
        self.assertIsNone(meta["seed"])
        self.assertEqual(meta["selected"], 109)

    def test_seeded_subset_is_deterministic_and_recorded(self) -> None:
        first, meta = s4c.select_sample_ids(self.ids, limit=8, seed=20261021)
        second, _ = s4c.select_sample_ids(self.ids, limit=8, seed=20261021)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 8)
        self.assertEqual(meta["rule"], "seeded_random_subset")
        self.assertEqual(meta["seed"], 20261021)
        self.assertEqual(meta["seed_source"], "cli")
        self.assertEqual(meta["sample_ids"], first)
        other, _ = s4c.select_sample_ids(self.ids, limit=8, seed=1)
        self.assertNotEqual(other, first)

    def test_subset_default_seed_is_recorded(self) -> None:
        selected, meta = s4c.select_sample_ids(self.ids, limit=3)
        self.assertEqual(len(selected), 3)
        self.assertEqual(meta["seed"], s4c.DEFAULT_SUBSET_SEED)
        self.assertEqual(meta["seed_source"], "default")
        self.assertEqual(
            selected, s4c.select_sample_ids(self.ids, limit=3, seed=s4c.DEFAULT_SUBSET_SEED)[0]
        )

    def test_explicit_ids_and_unknown_rejected(self) -> None:
        selected, meta = s4c.select_sample_ids(
            self.ids, explicit=["sample_005", "sample_001"]
        )
        self.assertEqual(selected, ["sample_001", "sample_005"])
        self.assertEqual(meta["rule"], "explicit_sample_ids")
        with self.assertRaises(s4c.S4CError):
            s4c.select_sample_ids(self.ids, explicit=["nope"])


class ActualHeadsLoaderTests(unittest.TestCase):
    """--actual 目录格式。"""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="s4c_actual_")
        self.dir = Path(self._tmp.name)
        self.lengths = {"head13": 5070, "head26": 20280}
        self.head13 = bytes((index * 7) % 256 for index in range(5070))
        self.head26 = bytes((index * 11) % 256 for index in range(20280))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_bin_pair(self) -> None:
        (self.dir / f"{SAMPLE_ID}.head13.bin").write_bytes(self.head13)
        (self.dir / f"{SAMPLE_ID}.head26.bin").write_bytes(self.head26)
        loaded = s4c.load_actual_heads(self.dir, SAMPLE_ID, self.lengths)
        self.assertEqual(bytes(loaded["head13"]["bytes"]), self.head13)
        self.assertEqual(bytes(loaded["head26"]["bytes"]), self.head26)

    def test_concat_bin(self) -> None:
        (self.dir / f"{SAMPLE_ID}.heads.bin").write_bytes(self.head13 + self.head26)
        loaded = s4c.load_actual_heads(self.dir, SAMPLE_ID, self.lengths)
        self.assertEqual(bytes(loaded["head13"]["bytes"]), self.head13)
        self.assertEqual(bytes(loaded["head26"]["bytes"]), self.head26)

    def test_json_signed_and_hex_and_base64(self) -> None:
        signed = [value - 256 if value > 127 else value for value in self.head13]
        (self.dir / f"{SAMPLE_ID}.json").write_text(
            json.dumps(
                {
                    "head13": signed,
                    "head26": {"hex": self.head26.hex()},
                }
            ),
            encoding="utf-8",
        )
        loaded = s4c.load_actual_heads(self.dir, SAMPLE_ID, self.lengths)
        self.assertEqual(bytes(loaded["head13"]["bytes"]), self.head13)
        self.assertEqual(bytes(loaded["head26"]["bytes"]), self.head26)
        (self.dir / f"{SAMPLE_ID}.json").write_text(
            json.dumps(
                {
                    "heads": {
                        "head13": {"base64": __import__("base64").b64encode(self.head13).decode("ascii")},
                        "head26": list(self.head26),
                    }
                }
            ),
            encoding="utf-8",
        )
        loaded = s4c.load_actual_heads(self.dir, SAMPLE_ID, self.lengths)
        self.assertEqual(bytes(loaded["head13"]["bytes"]), self.head13)
        self.assertEqual(bytes(loaded["head26"]["bytes"]), self.head26)

    def test_length_and_missing_errors(self) -> None:
        (self.dir / f"{SAMPLE_ID}.head13.bin").write_bytes(self.head13[:-1])
        (self.dir / f"{SAMPLE_ID}.head26.bin").write_bytes(self.head26)
        with self.assertRaises(s4c.ActualInputError):
            s4c.load_actual_heads(self.dir, SAMPLE_ID, self.lengths)
        with self.assertRaises(s4c.ActualInputError):
            s4c.load_actual_heads(self.dir, "unknown_sample", self.lengths)


class ObjectnessByteIndexTests(unittest.TestCase):
    """由 source_order 反解篡改字节下标。"""

    def test_first_pair_maps_to_head13_objectness(self) -> None:
        info = s4c.objectness_byte_index_for_source_order(0, decoder_binding())
        self.assertEqual(info["head"], "head13")
        self.assertEqual(info["byte_index"], 4 * 13 * 13)  # entry=4 的第一平面起点
        self.assertEqual(info["row"], 0)
        self.assertEqual(info["col"], 0)
        self.assertEqual(info["local_anchor"], 0)

    def test_second_head_pair_maps_into_head26(self) -> None:
        info = s4c.objectness_byte_index_for_source_order(6570, decoder_binding())
        self.assertEqual(info["head"], "head26")
        self.assertEqual(info["class_id"], 0)
        self.assertEqual(info["byte_index"], 4 * 26 * 26 + 10 * 26 + 9)


@unittest.skipUnless(main_tree_ready(), "主树 T25 分片不可用")
class GoldenSampleTests(unittest.TestCase):
    """真实分片上的单样本 golden 对拍与篡改定位。"""

    def _index_and_t29(self) -> tuple[dict, dict, dict]:
        data = upstream()
        return (
            data["idx"][SAMPLE_ID],  # type: ignore[index]
            data["ref"][SAMPLE_ID],  # type: ignore[index]
            data["cat"][SAMPLE_ID],  # type: ignore[index]
        )

    def test_single_sample_golden_passes(self) -> None:
        index_sample, t29_sample, catalog_sample = self._index_and_t29()
        record = s4c.evaluate_golden_sample(
            decoder=decoder_binding(),
            index_sample=index_sample,
            t29_sample=t29_sample,
            catalog_sample=catalog_sample,
            tensors_dir=s4c.resolve_upstream_paths().tensors_dir,
        )
        self.assertEqual(record["status"], "PASS", record["mismatches"])
        self.assertEqual(record["mismatch_count"], 0)
        self.assertTrue(record["heads"]["head13"]["byte_match"])
        self.assertTrue(record["heads"]["head26"]["byte_match"])
        self.assertTrue(record["raw_stream"]["raw_stream_byte_match"])
        self.assertEqual(record["raw_stream"]["raw_stream_sha256"], index_sample["network"]["raw_stream_sha256"])
        self.assertEqual(record["heads"]["head13"]["byte_offset"], index_sample["network"]["tensors"][30]["byte_offset"])
        self.assertEqual(len(record["detections_actual"]), len(t29_sample["detections"]))

    def test_one_byte_tamper_fails_and_localizes(self) -> None:
        index_sample, t29_sample, _ = self._index_and_t29()
        paths = s4c.resolve_upstream_paths()
        with tempfile.TemporaryDirectory(prefix="s4c_tamper_") as tmp:
            tmp_dir = Path(tmp)
            s4c.export_golden_heads(
                index_sample=index_sample,
                t29_sample=t29_sample,
                tensors_dir=paths.tensors_dir,
                out_dir=tmp_dir,
            )
            head13 = bytearray((tmp_dir / f"{SAMPLE_ID}.head13.bin").read_bytes())
            golden_heads = {
                "head13": bytes(head13),
                "head26": (tmp_dir / f"{SAMPLE_ID}.head26.bin").read_bytes(),
            }
            head13[0] ^= 0x01
            (tmp_dir / f"{SAMPLE_ID}.head13.bin").write_bytes(bytes(head13))
            record = s4c.evaluate_actual_sample(
                decoder=decoder_binding(),
                t29_sample=t29_sample,
                index_sample=index_sample,
                actual_dir=tmp_dir,
                golden_heads=golden_heads,
                golden_heads_info={"available": True, "source": "unittest"},
            )
            self.assertEqual(record["status"], "FAIL")
            fields = [item["field"] for item in record["mismatches"]]
            self.assertIn("head13.tensor_sha256", fields)
            self.assertEqual(record["sample_id"], SAMPLE_ID)
            self.assertEqual(record["mismatches"][0]["kind"], "byte")
            # 逐值定位：必须在第 0 字节指出期望/实际差异（golden 字节来自 T25 分片）。
            mismatch = record["mismatches"][0]
            self.assertEqual(mismatch["first_diff_offset"], 0)
            self.assertEqual(mismatch["diff_byte_count"], 1)
            self.assertEqual(mismatch["expected_byte"] ^ 1, mismatch["actual_byte"])
            self.assertEqual(mismatch["max_abs_int8_delta"], 1)
            comparison = record["heads"]["head13"]["golden_byte_comparison"]
            self.assertFalse(comparison["identical"])
            self.assertEqual(comparison["first_diff_offset"], 0)
            self.assertTrue(record["golden_byte_reference"]["available"])

    def test_actual_mode_degrades_when_golden_bytes_absent(self) -> None:
        # golden 字节不可用时仍必须只凭 T29 SHA 判定 FAIL，并记录降级事实。
        index_sample, t29_sample, _ = self._index_and_t29()
        with tempfile.TemporaryDirectory(prefix="s4c_nogold_") as tmp:
            tmp_dir = Path(tmp)
            paths = s4c.resolve_upstream_paths()
            s4c.export_golden_heads(
                index_sample=index_sample,
                t29_sample=t29_sample,
                tensors_dir=paths.tensors_dir,
                out_dir=tmp_dir,
            )
            head13 = bytearray((tmp_dir / f"{SAMPLE_ID}.head13.bin").read_bytes())
            head13[5] ^= 0x01
            (tmp_dir / f"{SAMPLE_ID}.head13.bin").write_bytes(bytes(head13))
            record = s4c.evaluate_actual_sample(
                decoder=decoder_binding(),
                t29_sample=t29_sample,
                index_sample=index_sample,
                actual_dir=tmp_dir,
                golden_heads=None,
                golden_heads_info={"available": False, "reason": "unittest 模拟无分片"},
            )
            self.assertEqual(record["status"], "FAIL")
            comparison = record["heads"]["head13"]["golden_byte_comparison"]
            self.assertFalse(comparison["available"])
            self.assertIsNone(
                next(
                    item for item in record["mismatches"] if item["field"] == "head13.tensor_sha256"
                ).get("first_diff_offset")
            )
            self.assertFalse(record["golden_byte_reference"]["available"])

    def test_objectness_bump_changes_score(self) -> None:
        index_sample, t29_sample, _ = self._index_and_t29()
        paths = s4c.resolve_upstream_paths()
        target = t29_sample["detections"][0]
        with tempfile.TemporaryDirectory(prefix="s4c_bump_") as tmp:
            tmp_dir = Path(tmp)
            s4c.export_golden_heads(
                index_sample=index_sample,
                t29_sample=t29_sample,
                tensors_dir=paths.tensors_dir,
                out_dir=tmp_dir,
            )
            info = s4c.objectness_byte_index_for_source_order(
                target["source_order"], decoder_binding()
            )
            head_path = tmp_dir / f"{SAMPLE_ID}.{info['head']}.bin"
            payload = bytearray(head_path.read_bytes())
            payload[info["byte_index"]] = 127
            head_path.write_bytes(bytes(payload))
            record = s4c.evaluate_actual_sample(
                decoder=decoder_binding(),
                t29_sample=t29_sample,
                index_sample=index_sample,
                actual_dir=tmp_dir,
            )
            self.assertEqual(record["status"], "FAIL")
            fields = [item["field"] for item in record["mismatches"]]
            self.assertIn("score", fields)
            self.assertGreater(record["max_score_abs_error"], 1e-6)

    def test_tamper_self_test_reports_all_probes_detected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s4c_selftest_") as tmp:
            data = upstream()
            exit_code, evidence = s4c.run_tamper_self_test(
                paths=data["paths"],  # type: ignore[arg-type]
                decoder=decoder_binding(),
                index_by_id=data["idx"],  # type: ignore[arg-type]
                t29_by_id=data["ref"],  # type: ignore[arg-type]
                catalog_by_id=data["cat"],  # type: ignore[arg-type]
                sample_id=SAMPLE_ID,
                tamper_dir=Path(tmp),
                run_id="unittest",
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue(evidence["all_tamper_probes_detected"])
            self.assertEqual(len(evidence["probes"]), 2)
            for probe in evidence["probes"]:
                self.assertTrue(probe["detected"], probe)
                self.assertTrue(probe["localized_fields"], probe)
            self.assertEqual(evidence["sample_id"], SAMPLE_ID)
            self.assertEqual(evidence["probes"][0]["tamper"]["original_byte"] ^ 1, evidence["probes"][0]["tamper"]["tampered_byte"])


@unittest.skipUnless(main_tree_ready(), "主树 T25 分片不可用")
class CliContractTests(unittest.TestCase):
    """CLI 退出码与报告落盘契约。"""

    def _run(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(HERE / "s4_replay_compare.py"), *args],
            cwd=str(WORKTREE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_pristine_actual_exit_zero_and_tamper_exit_one(self) -> None:
        data = upstream()
        paths = data["paths"]
        index_sample = data["idx"][SAMPLE_ID]  # type: ignore[index]
        t29_sample = data["ref"][SAMPLE_ID]  # type: ignore[index]
        with tempfile.TemporaryDirectory(prefix="s4c_cli_") as tmp:
            tmp_dir = Path(tmp)
            pristine = tmp_dir / "pristine"
            s4c.export_golden_heads(
                index_sample=index_sample,
                t29_sample=t29_sample,
                tensors_dir=paths.tensors_dir,  # type: ignore[attr-defined]
                out_dir=pristine,
            )
            report_path = tmp_dir / "pristine_report.json"
            result = self._run(
                [
                    "--actual",
                    str(pristine),
                    "--sample-id",
                    SAMPLE_ID,
                    "--json-out",
                    str(report_path),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["summary"]["mismatch_total"], 0)
            self.assertEqual(report["selection"]["rule"], "explicit_sample_ids")

            tampered = tmp_dir / "tampered"
            tampered.mkdir()
            head13 = bytearray((pristine / f"{SAMPLE_ID}.head13.bin").read_bytes())
            head13[0] ^= 0x01
            (tampered / f"{SAMPLE_ID}.head13.bin").write_bytes(bytes(head13))
            (tampered / f"{SAMPLE_ID}.head26.bin").write_bytes(
                (pristine / f"{SAMPLE_ID}.head26.bin").read_bytes()
            )
            tamper_report_path = tmp_dir / "tamper_report.json"
            result = self._run(
                [
                    "--actual",
                    str(tampered),
                    "--sample-id",
                    SAMPLE_ID,
                    "--json-out",
                    str(tamper_report_path),
                ]
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            tamper_report = json.loads(tamper_report_path.read_text(encoding="utf-8"))
            self.assertEqual(tamper_report["status"], "FAIL")
            self.assertEqual(tamper_report["summary"]["byte_mismatch_count"], 1)
            fields = [
                item["field"]
                for sample in tamper_report["samples"]
                for item in sample["mismatches"]
            ]
            self.assertIn("head13.tensor_sha256", fields)
            mismatch = next(
                item
                for sample in tamper_report["samples"]
                for item in sample["mismatches"]
                if item["field"] == "head13.tensor_sha256"
            )
            self.assertEqual(mismatch["first_diff_offset"], 0)
            self.assertEqual(mismatch["expected_byte"] ^ 1, mismatch["actual_byte"])

    def test_bad_score_threshold_exits_two(self) -> None:
        result = self._run(["--score-threshold", "0.1", "--json-out", "tmp/4/S4C/should_not_write.json"])
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_upstream_sha_mismatch_rejected(self) -> None:
        # 用一份被篡改的索引副本证明工具不会在字节层放过篡改。
        with tempfile.TemporaryDirectory(prefix="s4c_index_") as tmp:
            fake = Path(tmp) / "index.json"
            payload = bytearray(s4c.resolve_upstream_paths().t25_index.read_bytes())
            payload[0] ^= 0x01
            fake.write_bytes(bytes(payload))
            result = self._run(
                ["--t25-index", str(fake), "--sample-id", SAMPLE_ID, "--json-out", str(Path(tmp) / "r.json")]
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class ReportSchemaTests(unittest.TestCase):
    """报告节必须机器可读且含口径/统计。"""

    REQUIRED_TOP_KEYS = (
        "schema_version",
        "task_id",
        "status",
        "mode",
        "comparison_spec",
        "selection",
        "samples",
        "per_sample_status",
        "summary",
        "timing",
        "memory",
        "upstream_bindings",
        "limitations",
        "not_executed",
    )

    def test_report_keys_present(self) -> None:
        # 用空样本集合构造一份最小报告，避免依赖主树。
        paths = s4c.resolve_upstream_paths()
        decoder = decoder_binding()
        report = s4c.run_compare(
            paths=paths,
            decoder=decoder,
            index_by_id={},
            t29_by_id={},
            catalog_by_id={},
            selection={
                "rule": "explicit_sample_ids",
                "available": 0,
                "selected": 0,
                "limit": None,
                "seed": None,
                "seed_source": "not_used",
                "sample_ids": [],
            },
            mode="golden",
            run_id="unittest_schema",
            contract=s4c.load_s4a_contract()[0],
        )
        for key in self.REQUIRED_TOP_KEYS:
            self.assertIn(key, report, key)
        self.assertEqual(report["status"], "PASS")
        spec = report["comparison_spec"]
        self.assertEqual(spec["score_threshold"], 0.25)
        self.assertEqual(spec["nms_iou"], 0.45)
        self.assertEqual(spec["max_outputs_per_image"], 15)
        self.assertEqual(spec["tolerance"]["score_abs_tolerance"], 1e-6)
        self.assertEqual(spec["tolerance"]["xyxy_abs_tolerance_per_component"], 1e-6)
        self.assertEqual(spec["tolerance"]["relative_tolerance"], 0.0)
        self.assertEqual(spec["head_byte_lengths"], {"head13": 5070, "head26": 20280})


if __name__ == "__main__":
    unittest.main()