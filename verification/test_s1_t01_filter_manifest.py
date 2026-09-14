"""S1-T01 清单去重器的无外部依赖回归测试。"""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from verification.s1_t01_filter_manifest import filter_manifest


class FilterManifestTest(unittest.TestCase):
    """验证 train 优先的跨 split 去重规则。"""

    def test_filter_keeps_train_and_removes_lower_priority_rows(self) -> None:
        """同一哈希的 val/test 应被移除，未重复行应保留。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "manifest.csv"
            output = root / "manifest_clean.csv"
            duplicate_log = root / "duplicates.log"
            report = {
                "status": "PASS",
                "duplicate_hashes": 1,
                "duplicate_rows": 3,
                "duplicates": {
                    "abc": [
                        {"split": "train", "image": "i-train.jpg", "label": "i-train.txt", "person_id": "p1"},
                        {"split": "val", "image": "i-val.jpg", "label": "i-val.txt", "person_id": "p2"},
                        {"split": "test", "image": "i-test.jpg", "label": "i-test.txt", "person_id": "p3"},
                    ]
                },
            }
            duplicate_log.write_text(json.dumps(report) + "\n", encoding="utf-8")
            fields = ["image", "label", "split", "session_id", "person_id", "source", "license", "is_real"]
            rows = []
            for split, name in (("train", "i-train"), ("val", "i-val"), ("test", "i-test"), ("train", "unique")):
                rows.append(
                    {
                        "image": f"{name}.jpg",
                        "label": f"{name}.txt",
                        "split": split,
                        "session_id": f"s-{split}",
                        "person_id": f"p-{name}",
                        "source": "fixture",
                        "license": "fixture",
                        "is_real": "true",
                    }
                )
            with source.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

            result = filter_manifest(source, output, duplicate_log)

            self.assertEqual(result["input_rows"], 4)
            self.assertEqual(result["output_rows"], 2)
            self.assertEqual(result["dropped_rows"], 2)
            with output.open("r", encoding="utf-8", newline="") as stream:
                self.assertEqual([row["image"] for row in csv.DictReader(stream)], ["i-train.jpg", "unique.jpg"])


if __name__ == "__main__":
    unittest.main()
