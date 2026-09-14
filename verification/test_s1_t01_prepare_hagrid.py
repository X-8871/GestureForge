"""S1-T01 HaGRIDv2 标签转换器的无外部依赖回归测试。"""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from verification.s1_t01_prepare_hagrid import prepare_dataset


class PrepareHaGRIDTest(unittest.TestCase):
    """验证五类正样本和 no_gesture 负样本的基本转换。"""

    def test_prepare_target_classes_and_negative_samples(self) -> None:
        """应生成相对路径清单、五类 YOLO 框和空负样本标签。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            annotation_root = root / "dataset" / "annotations" / "annotations"
            image_ids = {
                "fist": "fist-id",
                "palm": "palm-id",
                "one": "one-id",
                "two_up": "two-up-id",
                "three": "three-id",
                "no_gesture": "negative-id",
            }
            for class_name, image_id in image_ids.items():
                image_dir = root / "dataset" / class_name / class_name if class_name != "no_gesture" else root / "dataset" / class_name
                image_dir.mkdir(parents=True, exist_ok=True)
                (image_dir / f"{image_id}.jpg").write_bytes(b"fixture")
            for split in ("train", "val", "test"):
                split_dir = annotation_root / split
                split_dir.mkdir(parents=True, exist_ok=True)
                for class_name, image_id in image_ids.items():
                    record = {
                        "bboxes": [[0.5, 0.5, 0.25, 0.25]],
                        "labels": [class_name],
                        "user_id": f"user-{split}-{class_name}",
                    }
                    if class_name == "no_gesture":
                        record["bboxes"] = []
                        record["labels"] = ["no_gesture"]
                    (split_dir / f"{class_name}.json").write_text(
                        json.dumps({image_id: record}), encoding="utf-8"
                    )

            manifest = root / "manifest.csv"
            labels = root / "labels"
            report = prepare_dataset(root, manifest, labels)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["metrics"]["rows"], 18)
            self.assertEqual(report["metrics"]["boxes"], 15)
            with manifest.open("r", encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 18)
            self.assertEqual(rows[0]["image"].count("\\"), 0)
            self.assertEqual(
                (root / rows[0]["label"]).read_text(encoding="utf-8").strip(),
                "0 0.50000000 0.50000000 0.25000000 0.25000000",
            )
            negative_rows = [row for row in rows if row["image"].endswith("negative-id.jpg")]
            self.assertEqual(len(negative_rows), 3)
            self.assertEqual((root / negative_rows[0]["label"]).read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
