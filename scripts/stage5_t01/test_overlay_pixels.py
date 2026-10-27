#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""像素级叠加对拍链路的离线测试（含**判别力**：篡改/空框/地址错必须被抓）。

覆盖：
  1. `hw_buf_address.parse_buffer_addresses`：多版本地址取当前值、缺失报错；
  2. 合成转储（期望边框像素来自冻结参考）→ `verify_overlay_pixels` **exit 0**；
  3. 篡改一个边框像素颜色 → **exit 1**（判别力）；
  4. "只有背景、没有边框"的转储（= 本轮板上读错地址时的真实症状）→ **exit 1**；
  5. 字节序为 R,G,B 的转储 → 仍 **exit 0**（自动判定）；
  6. 用例不在表内 / 转储为空 → exit 2 / 1。
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts/stage5_t01"))
sys.path.insert(0, str(REPO_ROOT / "verification"))
import hw_buf_address as ADDR  # noqa: E402
import s5_display_geometry_reference as R  # noqa: E402

sys.path.insert(0, str(REPO_ROOT / "scripts/stage5_t01"))
import verify_overlay_pixels as VP  # noqa: E402

HEADER_GEN = REPO_ROOT / "scripts/stage5_t01/gen_overlay_cases.py"
SOURCE = REPO_ROOT / "scripts/stage5_t01/p1_app/s5_overlay.c"
CASE_ID = 5
CANVAS_W, CANVAS_H = 1280, 720


def _dump_for(cases: dict[int, list[dict]], colors: list[tuple[int, int, int]],
              case_id: int, *, order: str = "BGR", tamper: bool = False,
              background: bool = False) -> str:
    """按 tcl 转储格式合成一段 dump（仅含各框边框所在行）。"""
    boxes = cases[case_id]
    rows: dict[int, dict[int, tuple[int, int, int]]] = {}
    for box in boxes:
        x1, y1, x2, y2 = box["rect"]
        bgr = colors[box["cls"] % 5]
        color = bgr if order == "BGR" else (bgr[2], bgr[1], bgr[0])
        if tamper:
            color = (7, 7, 7)
        if background:
            continue
        for (x, y) in R.border_pixel_sets(x1, y1, x2, y2, R.DISPLAY_LINE_WIDTH_PX, CANVAS_W, CANVAS_H):
            rows.setdefault(y, {})[x] = color
    lines = []
    for y in sorted(rows):
        xs = sorted(rows[y])
        x0 = xs[0] // 4 * 4 if xs else 0           # 字对齐起点（下对齐自第一个像素）
        stream = bytearray()
        for x in range(x0, xs[-1] + 1):
            stream += bytes(rows[y].get(x, (169, 169, 169)))
        while len(stream) % 4:
            stream.append(0)
        words = " ".join(stream[i:i + 4].hex().upper() for i in range(0, len(stream), 4))
        lines.append(f"S5_ROW_BEGIN row={y} x={x0}")
        lines.append(f"  {0x100000 + y * 0x100:06X}:   {words}")
    return "\n".join(lines) + "\n"


class T_AddressParser(unittest.TestCase):
    def test_prefers_current_revision_address(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = pathlib.Path(tmp) / "uart.log"
            log.write_text("S5_P1_BUF0=00114C00\nnoise\nS5_P1_BUF0=00138C00\n"
                           "S5_P1_BUF1=00727800\nS5_P1_BUF2=00D16400\n", encoding="utf-8")
            got = ADDR.parse_buffer_addresses(log)
            self.assertEqual(got[0], 0x00138C00)      # 取最后一次（当前应用）
            self.assertEqual(got[1], 0x00727800)
            self.assertEqual(len(got), 3)

    def test_missing_file_is_input_error(self) -> None:
        with self.assertRaises(ADDR.InputError):
            ADDR.parse_buffer_addresses(pathlib.Path("no_such_uart.log"))

    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = pathlib.Path(tmp) / "uart.log"
            log.write_text("S5_P1_BUF0=00138C00\n", encoding="utf-8")
            self.assertEqual(ADDR.main(["--uart", str(log)]), 0)
            self.assertEqual(ADDR.main(["--uart", str(log), "--index", "2"]), 1)
            self.assertEqual(ADDR.main(["--uart", str(pathlib.Path(tmp) / "nope.log")]), 2)


class T_OverlayPixels(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        tmpdir = tempfile.mkdtemp(prefix="s5ovl_hdr_")
        header = pathlib.Path(tmpdir) / "s5_overlay_cases.h"
        subprocess.run([sys.executable, "-B", str(HEADER_GEN), "--emit-c", str(header)],
                       capture_output=True, cwd=str(REPO_ROOT), check=True)
        cls.header = header
        cls.cases = VP.parse_case_table(header)
        cls.colors = VP.parse_class_colors(SOURCE)
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5ovl_")
        cls.dir = pathlib.Path(cls.tmp.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def _write_and_run(self, text: str, name: str) -> tuple[int, dict]:
        dump = self.dir / f"{name}.txt"
        dump.write_text(text, encoding="utf-8", newline="\n")
        out = self.dir / f"{name}.json"
        code = VP.main(["--dump", str(dump), "--case", str(CASE_ID), "--header", str(self.header),
                        "--source", str(SOURCE), "--json", str(out)])
        payload = json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}
        return code, payload

    def test_intact_dump_passes(self) -> None:
        code, payload = self._write_and_run(_dump_for(self.cases, self.colors, CASE_ID), "intact")
        self.assertEqual(code, 0, payload.get("failures"))
        self.assertTrue(payload["passed"])
        self.assertEqual(len(payload["boxes"]), len(self.cases[CASE_ID]))

    def test_rgb_order_also_passes(self) -> None:
        code, payload = self._write_and_run(_dump_for(self.cases, self.colors, CASE_ID, order="RGB"),
                                            "rgb_order")
        self.assertEqual(code, 0, payload.get("failures"))
        self.assertEqual(payload["boxes"][0]["order"], "RGB")

    def test_tampered_pixel_is_caught(self) -> None:
        code, payload = self._write_and_run(_dump_for(self.cases, self.colors, CASE_ID, tamper=True),
                                            "tampered")
        self.assertEqual(code, 1, "篡改边框颜色未被抓住")
        self.assertFalse(payload["passed"])

    def test_background_only_dump_is_caught(self) -> None:
        """即本轮板上读错缓冲时的真实症状：只有背景、没有叠加框 ⇒ 必须判失败。"""
        code, payload = self._write_and_run(_dump_for(self.cases, self.colors, CASE_ID, background=True),
                                            "background_only")
        self.assertEqual(code, 1, "空框转储未被抓住")

    def test_unknown_case_is_input_error(self) -> None:
        dump = self.dir / "intact2.txt"
        dump.write_text(_dump_for(self.cases, self.colors, CASE_ID), encoding="utf-8", newline="\n")
        self.assertEqual(VP.main(["--dump", str(dump), "--case", "99", "--header", str(self.header),
                                  "--source", str(SOURCE)]), 2)

    def test_empty_dump_fails(self) -> None:
        dump = self.dir / "empty.txt"
        dump.write_text("S5_DUMP_BEGIN\nS5_DUMP_DONE=1\n", encoding="utf-8", newline="\n")
        self.assertEqual(VP.main(["--dump", str(dump), "--case", str(CASE_ID), "--header", str(self.header),
                                  "--source", str(SOURCE)]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)