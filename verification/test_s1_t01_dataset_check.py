"""S1-T01 数据检查器的无外部依赖回归测试。"""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from verification.s1_t01_dataset_check import Thresholds, validate_dataset


class DatasetCheckTest(unittest.TestCase):
    """验证正常清单和非法标签的主要分支。"""

    @staticmethod
    def _write_ppm(path: Path, color: int) -> None:
        """写入最小可解析 PPM 测试图片。"""

        path.write_bytes(b"P6\n4 4\n255\n" + bytes([color, 220, 200]) * 16)

    def _make_dataset(self, root: Path) -> Path:
        """建立仅供检查器回归使用的最小清单。"""

        manifest = root / "manifest.csv"
        rows: list[dict[str, str]] = []
        label_index = 0
        for index in range(30):
            split = "train" if index < 16 else "val"
            session = "session_train" if split == "train" else "session_val"
            person = "person_train" if split == "train" else "person_val"
            image = root / "images" / split / f"image_{index:02d}.ppm"
            label = root / "labels" / split / f"image_{index:02d}.txt"
            image.parent.mkdir(parents=True, exist_ok=True)
            label.parent.mkdir(parents=True, exist_ok=True)
            self._write_ppm(image, 20 + index)
            if index in {0, 1, 16, 17, 18}:
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
        with manifest.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return manifest

    def test_valid_manifest_passes_automated_checks(self) -> None:
        """正常数据应通过自动门槛，但仍保留人工抽查状态。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            report = validate_dataset(root, manifest, Thresholds())
            self.assertEqual(report["status"], "PASS_AUTOMATED_MANUAL_PENDING")
            self.assertEqual(report["checks"]["AC03"], "通过自动检查")
            self.assertIn("人工抽查", report["checks"]["AC04"])
            self.assertEqual(report["metrics"]["real_images"], 30)

    def test_invalid_label_is_reported(self) -> None:
        """非法 class_id 应阻断自动检查。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._make_dataset(root)
            bad_label = root / "labels" / "train" / "image_02.txt"
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
            report = validate_dataset(root, manifest, Thresholds(), preview_dir)
            self.assertEqual(len(report["preview_files"]), 15)
            self.assertTrue(all(Path(path).is_file() for path in report["preview_files"]))


if __name__ == "__main__":
    unittest.main()
