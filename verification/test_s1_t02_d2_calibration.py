import csv
import tempfile
import unittest
from pathlib import Path

try:
    import s1_t02_d2_calibration as calibration
except ModuleNotFoundError:
    from verification import s1_t02_d2_calibration as calibration


class CalibrationTests(unittest.TestCase):
    def test_requires_exact_semantic_negative_counts(self):
        with self.assertRaises(ValueError):
            calibration.validate_semantic_negative_counts(["a", "b", "c"], ["d"] * 4)
        with self.assertRaises(ValueError):
            calibration.validate_semantic_negative_counts(["a", "b"], ["d"] * 5)
        calibration.validate_semantic_negative_counts(["a", "b", "c"], ["d"] * 5)

    def test_select_calibration_rejects_over_quota_semantic_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = []
            train_paths = []
            semantic_rows = []
            for class_id, class_name in enumerate(calibration.CLASS_NAMES):
                for index in range(100):
                    image = root / "dataset" / class_name / f"{index}.jpg"
                    label = root / "labels" / class_name / f"{index}.txt"
                    image.parent.mkdir(parents=True, exist_ok=True)
                    label.parent.mkdir(parents=True, exist_ok=True)
                    image.write_bytes(b"fixture")
                    label.write_text(f"{class_id} 0.5 0.5 0.1 0.1\n", encoding="utf-8")
                    image_value = image.relative_to(root).as_posix()
                    label_value = label.relative_to(root).as_posix()
                    rows.append({"image": image_value, "label": label_value, "split": "train", "session_id": f"s{index}", "person_id": f"p{index}"})
                    train_paths.append(str(image))
            for index in range(9):
                image = root / "dataset" / "negative" / f"{index}.jpg"
                label = root / "labels" / "negative" / f"{index}.txt"
                image.parent.mkdir(parents=True, exist_ok=True)
                label.parent.mkdir(parents=True, exist_ok=True)
                image.write_bytes(b"fixture")
                label.write_text("", encoding="utf-8")
                rows.append({"image": image.relative_to(root).as_posix(), "label": label.relative_to(root).as_posix(), "split": "train", "session_id": f"n{index}", "person_id": f"n{index}"})
                train_paths.append(str(image))
                semantic_rows.append(f"{image.relative_to(root).as_posix()},{'no_hand' if index < 3 else 'non_target_gesture'}")
            manifest = root / "manifest.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["image", "label", "split", "session_id", "person_id"])
                writer.writeheader()
                writer.writerows(rows)
            train = root / "train.list"
            train.write_text("\n".join(train_paths) + "\n", encoding="utf-8")
            semantic = root / "semantic.csv"
            semantic.write_text("image,sample_role\n" + "\n".join(semantic_rows) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non_target_gesture 数量不是 5"):
                calibration.select_calibration(root, manifest, train, semantic)

    def test_select_calibration_rejects_no_hand_over_quota_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = []
            train_paths = []
            semantic_rows = []
            for class_id, class_name in enumerate(calibration.CLASS_NAMES):
                for index in range(100):
                    image = root / "dataset" / class_name / f"{index}.jpg"
                    label = root / "labels" / class_name / f"{index}.txt"
                    image.parent.mkdir(parents=True, exist_ok=True)
                    label.parent.mkdir(parents=True, exist_ok=True)
                    image.write_bytes(b"fixture")
                    label.write_text(f"{class_id} 0.5 0.5 0.1 0.1\n", encoding="utf-8")
                    image_value = image.relative_to(root).as_posix()
                    label_value = label.relative_to(root).as_posix()
                    rows.append({"image": image_value, "label": label_value, "split": "train", "session_id": f"s{index}", "person_id": f"p{index}"})
                    train_paths.append(str(image))
            for index in range(9):
                image = root / "dataset" / "negative" / f"{index}.jpg"
                label = root / "labels" / "negative" / f"{index}.txt"
                image.parent.mkdir(parents=True, exist_ok=True)
                label.parent.mkdir(parents=True, exist_ok=True)
                image.write_bytes(b"fixture")
                label.write_text("", encoding="utf-8")
                rows.append({"image": image.relative_to(root).as_posix(), "label": label.relative_to(root).as_posix(), "split": "train", "session_id": f"n{index}", "person_id": f"n{index}"})
                train_paths.append(str(image))
                semantic_rows.append(f"{image.relative_to(root).as_posix()},{'no_hand' if index < 4 else 'non_target_gesture'}")
            manifest = root / "manifest.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["image", "label", "split", "session_id", "person_id"])
                writer.writeheader()
                writer.writerows(rows)
            train = root / "train.list"
            train.write_text("\n".join(train_paths) + "\n", encoding="utf-8")
            semantic = root / "semantic.csv"
            semantic.write_text("image,sample_role\n" + "\n".join(semantic_rows) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "train no_hand 数量不是 3"):
                calibration.select_calibration(root, manifest, train, semantic)

    def test_rejects_duplicate_train_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "a.jpg"
            label = root / "a.txt"
            image.write_bytes(b"fixture")
            label.write_text("0 0.5 0.5 0.1 0.1\n", encoding="utf-8")
            manifest = root / "manifest.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["image", "label", "split", "session_id", "person_id"])
                writer.writeheader()
                writer.writerow({"image": "a.jpg", "label": "a.txt", "split": "train", "session_id": "s", "person_id": "p"})
            train = root / "train.list"
            train.write_text(f"{image}\n{image}\n", encoding="utf-8")
            semantic = root / "semantic.csv"
            semantic.write_text("image,sample_role\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                calibration.select_calibration(root, manifest, train, semantic)

    def test_canonical_relative_paths_are_resolved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "dataset" / "x.jpg"
            label = root / "labels" / "x.txt"
            image.parent.mkdir()
            label.parent.mkdir()
            image.write_bytes(b"fixture")
            label.write_text("0 0.5 0.5 0.1 0.1\n", encoding="utf-8")
            manifest = root / "manifest.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["image", "label", "split", "session_id", "person_id"])
                writer.writeheader()
                writer.writerow({"image": "dataset/x.jpg", "label": "labels/x.txt", "split": "train", "session_id": "s", "person_id": "p"})
            train = root / "train.list"
            train.write_text(str(image).replace("/", "\\") + "\n", encoding="utf-8")
            semantic = root / "semantic.csv"
            semantic.write_text("image,sample_role\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                calibration.select_calibration(root, manifest, train, semantic)


if __name__ == "__main__":
    unittest.main()
