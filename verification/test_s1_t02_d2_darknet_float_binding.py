"""S1-T02-D2 Darknet 浮点逐层绑定器的隔离测试。"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from verification.s1_t02_d2_darknet_float_binding import FloatBindingError, parse_dump_index


class DarknetFloatBindingTest(unittest.TestCase):
    """覆盖 dump 索引完整性和长度绑定。"""

    def test_rejects_incomplete_dump_set(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dump = root / "dump"
            dump.mkdir()
            (dump / "sample_0000_layer_00.bin").write_bytes(b"\x00" * 4)
            (dump / "index.csv").write_text(
                "sample_index,layer_index,output_count,file\n"
                f"0,0,1,{dump / 'sample_0000_layer_00.bin'}\n",
                encoding="utf-8",
            )
            with self.assertRaises(FloatBindingError):
                parse_dump_index(dump / "index.csv", dump, {0, 1}, 1)

    def test_accepts_complete_dump_set(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dump = root / "dump"
            dump.mkdir()
            rows = ["sample_index,layer_index,output_count,file"]
            for sample in range(2):
                for layer in (0, 1):
                    path = dump / f"sample_{sample:04d}_layer_{layer:02d}.bin"
                    path.write_bytes(b"\x00" * 8)
                    rows.append(f"{sample},{layer},2,{path}")
            index = dump / "index.csv"
            index.write_text("\n".join(rows) + "\n", encoding="utf-8")
            records = parse_dump_index(index, dump, {0, 1}, 2)
            self.assertEqual(len(records), 4)
