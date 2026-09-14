"""S1-T01 数据检查器的无外部依赖回归测试。"""

from __future__ import annotations

import binascii
import csv
import hashlib
import struct
import tempfile
import unittest
from pathlib import Path

from verification.s1_t01_dataset_check import SEMANTIC_REVIEW_COLUMNS, Thresholds, validate_dataset


class DatasetCheckTest(unittest.TestCase):
    """验证正常清单和非法标签的主要分支。"""

    @staticmethod
    def _write_ppm(path: Path, color: int) -> None:
        """写入最小可解析 PPM 测试图片。"""

        path.write_bytes(b"P6\n4 4\n255\n" + bytes([color, 220, 200]) * 16)

    @staticmethod
    def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
        """构造带正确 CRC 的 PNG 数据块。"""

        crc = binascii.crc32(chunk_type + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", crc)

    @classmethod
    def _write_invalid_png(cls, path: Path) -> None:
        """写入 CRC 正确但 zlib 载荷非法的 PNG。"""

        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        path.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + cls._png_chunk(b"IHDR", ihdr)
            + cls._png_chunk(b"IDAT", b"\x78\x9c\xff\xff")
            + cls._png_chunk(b"IEND", b"")
        )

    @staticmethod
    def _write_empty_jpeg(path: Path, entropy: bytes = b"") -> None:
        """写入含表、含扫描段但熵编码为空或伪造的 JPEG。"""

        def segment(marker: int, payload: bytes) -> bytes:
            return b"\xff" + bytes([marker]) + struct.pack(">H", len(payload) + 2) + payload

        dqt = b"\x00" + bytes(64)
        dht = b"\x00" + bytes(16) + b"\x00"
        sof0 = b"\x08\x00\x01\x00\x01\x01\x01\x11\x00"
        sos = b"\x01\x01\x00\x00\x3f\x00"
        path.write_bytes(
            b"\xff\xd8"
            + segment(0xDB, dqt)
            + segment(0xC4, dht)
            + segment(0xC0, sof0)
            + segment(0xDA, sos)
            + entropy
            + b"\xff\xd9"
        )

    @staticmethod
    def _write_rows(manifest: Path, rows: list[dict[str, str]]) -> None:
        """以 UTF-8 重写测试清单。"""

        with manifest.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _write_semantic_rows(path: Path, rows: list[dict[str, str]]) -> None:
        """以 UTF-8 写入人工语义补充表。"""

        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=SEMANTIC_REVIEW_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    def _make_dataset(self, root: Path) -> Path:
        """建立仅供检查器回归使用的最小清单。"""

        manifest = root / "manifest.csv"
        rows: list[dict[str, str]] = []
        label_index = 0
        for index in range(30):
            split = "train" if index < 16 else "val"
            session = "session_train" if split == "train" else "session_val"
            person = "person_train" if split == "train" else "person_val"
            is_no_hand = index in {0, 1, 16, 17, 18}
            image_dir = root / "images" / split / ("no_gesture" if is_no_hand else "target")
            label_dir = root / "labels" / split / ("no_gesture" if is_no_hand else "target")
            image = image_dir / f"image_{index:02d}.ppm"
            label = label_dir / f"image_{index:02d}.txt"
            image.parent.mkdir(parents=True, exist_ok=True)
            label.parent.mkdir(parents=True, exist_ok=True)
            self._write_ppm(image, 20 + index)
            if is_no_hand:
                label.write_text("", encoding="utf-8")
            else:
                class_id = label_index % 5
                label_index += 1
                label.write_text(f"{class_id} 0.5 0.5 0.4 0.4\n", encoding="utf-8")
            rows.append(
                {
                    "image": image.relative_to(root).as_posix(),
                    "label": label.relative_to(root).as_posix(),
                    "split": split,
                    "session_id": session,
                    "person_id": person,
                    "source": "unit-test-fixture",
                    "license": "internal-test-only",
                    "is_real": "true",
                }
            )
        self._write_rows(manifest, rows)
        return manifest

    def _make_semantic_review(self, root: Path, manifest: Path, roles: dict[int, str] | None = None) -> Path:
        """为测试夹具生成带人工结果和图片哈希的语义表。"""

        roles = roles or {0: "no_hand", 1: "no_hand", 16: "no_hand", 17: "no_hand", 18: "no_hand"}
        with manifest.open("r", encoding="utf-8", newline="") as stream:
            manifest_rows = list(csv.DictReader(stream))
        semantic_rows: list[dict[str, str]] = []
        for index, role in roles.items():
            source = manifest_rows[index]
            image_path = root / source["image"]
            record = dict(source)
            record["image_sha256"] = hashlib.sha256(image_path.read_bytes()).hexdigest()
            record["sample_role"] = role
            record["manual_result"] = {
                "no_hand": "confirmed_no_hand",
                "non_target_gesture": "accepted_non_target",
                "target_gesture": "pass_box",
            }[role]
            record["reviewer"] = "Wong"
            record["reviewed_at_utc8"] = "2026-09-14T12:00:00+08:00"
            semantic_rows.append(record)
        semantic_path = root / "semantic_review.csv"
        self._write_semantic_rows(semantic_path, semantic_rows)
        return semantic_path

    def test_valid_manifest_passes_automated_checks(self) -> None:
        """正常数据应通过自动门槛，但仍保留人工抽查状态。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            semantic_review = self._make_semantic_review(root, manifest)
            report = validate_dataset(root, manifest, Thresholds(), semantic_review=semantic_review)
            self.assertEqual(report["status"], "PASS_AUTOMATED_MANUAL_PENDING")
            self.assertEqual(report["checks"]["AC03"], "通过自动检查")
            self.assertIn("人工抽查", report["checks"]["AC04"])
            self.assertEqual(report["metrics"]["real_images"], 30)
            self.assertEqual(sum(report["metrics"]["no_hand_images_per_split"].values()), 5)
            self.assertEqual(sum(report["metrics"]["non_target_gesture_images_per_split"].values()), 0)

    def test_no_gesture_directory_alone_is_not_no_hand(self) -> None:
        """没有语义记录时，目录名和空标签不能冒充无手样本。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            report = validate_dataset(root, manifest, Thresholds())
            self.assertEqual(sum(report["metrics"]["no_hand_images_per_split"].values()), 0)
            self.assertEqual(sum(report["metrics"]["non_target_gesture_images_per_split"].values()), 0)
            self.assertIn("无手图片 0 < 5", report["checks"]["AC03"])

    def test_semantic_roles_are_counted_separately(self) -> None:
        """非五类目标负样本不能计入 no_hand。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            semantic_review = self._make_semantic_review(root, manifest, {0: "non_target_gesture", 1: "no_hand", 16: "no_hand", 17: "no_hand", 18: "no_hand"})
            report = validate_dataset(root, manifest, Thresholds(), semantic_review=semantic_review)
            self.assertEqual(sum(report["metrics"]["no_hand_images_per_split"].values()), 4)
            self.assertEqual(sum(report["metrics"]["non_target_gesture_images_per_split"].values()), 1)

    def test_semantic_path_alias_duplicate_is_reported(self) -> None:
        """语义表通过大小写和 .. 别名重复绑定同一物理图片时应失败。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            semantic_review = self._make_semantic_review(root, manifest)
            with semantic_review.open("r", encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            duplicate = dict(rows[0])
            duplicate["image"] = "images/train/no_gesture/../no_gesture/IMAGE_00.PPM"
            duplicate["label"] = "labels/train/no_gesture/../no_gesture/IMAGE_00.TXT"
            rows.append(duplicate)
            self._write_semantic_rows(semantic_review, rows)
            report = validate_dataset(root, manifest, Thresholds(), semantic_review=semantic_review)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("重复映射同一物理图片" in error for error in report["errors"]))

    def test_invalid_label_is_reported(self) -> None:
        """非法 class_id 应阻断自动检查。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            bad_label = root / "labels" / "train" / "target" / "image_02.txt"
            bad_label.write_text("9 0.5 0.5 0.4 0.4\n", encoding="utf-8")
            report = validate_dataset(root, manifest, Thresholds())
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("class_id 越界" in error for error in report["errors"]))

    def test_svg_previews_are_generated(self) -> None:
        """正常清单应生成每类两个框和五张无手图的抽查预览。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            preview_dir = root / "previews"
            semantic_review = self._make_semantic_review(root, manifest)
            report = validate_dataset(root, manifest, Thresholds(), preview_dir, semantic_review)
            self.assertEqual(len(report["preview_files"]), 15)
            self.assertTrue(all(Path(path).is_file() for path in report["preview_files"]))

    def test_label_stem_mismatch_is_reported(self) -> None:
        """图片和标签 stem 不一致时应阻断自动检查。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            with manifest.open("r", encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            rows[2]["label"] = rows[3]["label"]
            self._write_rows(manifest, rows)
            report = validate_dataset(root, manifest, Thresholds())
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("stem 不一致" in error for error in report["errors"]))

    def test_physical_path_alias_duplicate_is_reported(self) -> None:
        """大小写和 .. 别名映射同一物理图片/标签时应阻断检查。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            with manifest.open("r", encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            rows[3]["image"] = "images/val/../val/IMAGE_03.PPM"
            rows[3]["label"] = "labels/val/../val/IMAGE_03.TXT"
            rows[4]["image"] = "images/val/../val/IMAGE_03.PPM"
            rows[4]["label"] = "labels/val/../val/IMAGE_03.TXT"
            self._write_rows(manifest, rows)
            report = validate_dataset(root, manifest, Thresholds())
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("规范化物理图片路径" in error for error in report["errors"]))
            self.assertTrue(any("规范化物理标签路径" in error for error in report["errors"]))

    def test_truncated_pnm_is_reported(self) -> None:
        """只有 PNM 头部而缺少像素载荷时应被拒绝。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            truncated = root / "images" / "train" / "target" / "image_02.ppm"
            truncated.write_bytes(b"P6\n4 4\n255\n")
            report = validate_dataset(root, manifest, Thresholds())
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("图片不可解析" in error and "像素载荷长度错误" in error for error in report["errors"]))

    def test_invalid_png_zlib_reports_failure(self) -> None:
        """非法 PNG zlib 载荷应返回可审计报告而不是抛出异常。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            image = root / "images" / "train" / "target" / "image_02.png"
            self._write_invalid_png(image)
            with manifest.open("r", encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            rows[2]["image"] = "images/train/target/image_02.png"
            self._write_rows(manifest, rows)
            report = validate_dataset(root, manifest, Thresholds())
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("PNG zlib 载荷无效" in error for error in report["errors"]))

    def test_empty_and_fake_jpeg_entropy_reports_failure(self) -> None:
        """空或伪造 JPEG 熵编码应被完整解码检查拒绝。"""

        for entropy in (b"", b"\x01\x02"):
            with self.subTest(entropy=entropy):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    manifest = self._make_dataset(root)
                    image = root / "images" / "train" / "target" / "image_02.jpg"
                    self._write_empty_jpeg(image, entropy)
                    with manifest.open("r", encoding="utf-8", newline="") as stream:
                        rows = list(csv.DictReader(stream))
                    rows[2]["image"] = "images/train/target/image_02.jpg"
                    self._write_rows(manifest, rows)
                    report = validate_dataset(root, manifest, Thresholds())
                    self.assertEqual(report["status"], "FAIL")
                    self.assertTrue(any("JPEG" in error and ("熵编码区为空" in error or "解码失败" in error) for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
