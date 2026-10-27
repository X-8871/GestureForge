#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`gen_dump_rows` 的离线测试：边判据 + **陈旧行列表的回归复现**（判别力）。

覆盖：
  1. 当前用例表生成的计划 → 边判据 **通过**（每框 4 条边各 ≥8 像素）；
  2. **负控**：用旧 `jtag_dump_rows.tcl` 的陈旧行/x 列表核算当前表 → 边判据 **必须失败**
     （复现 2026-10-27 "边框颜色对不上"的**假失配**根因：采样没落在当前边框上）；
  3. 生成的 TCL 含既有输出格式（`S5_ROW_BEGIN` + `mrd -force`），可被同一对拍器消费。
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
import gen_dump_rows as G  # noqa: E402
import verify_overlay_pixels as VP  # noqa: E402

# 旧 tcl 里写死的行/x 列表（按旧版矩形；本轮定位的假失配来源）
STALE_SEGMENTS = [(0, 0), (53, 0), (53, 512), (66, 512), (359, 0), (200, 64),
                  (200, 0), (359, 1256)]


def _header(tmp: pathlib.Path) -> pathlib.Path:
    header = tmp / "s5_overlay_cases.h"
    subprocess.run([sys.executable, "-B", str(REPO_ROOT / "scripts/stage5_t01/gen_overlay_cases.py"),
                    "--emit-c", str(header)], capture_output=True, cwd=str(REPO_ROOT), check=True)
    return header


class T_GenDumpRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5gen_")
        cls.dir = pathlib.Path(cls.tmp.name)
        cls.header = _header(cls.dir)
        cls.cases = VP.parse_case_table(cls.header)
        cls.boxes = cls.cases[5]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_01_current_plan_passes_edge_criterion(self) -> None:
        plan = G.build_plan(self.boxes)
        cov = G.coverage(plan, self.boxes)
        self.assertTrue(cov["edge_criterion_passed"],
                        f"边判据未通过：{json.dumps(cov['per_box'], ensure_ascii=False)}")
        self.assertEqual(cov["edges_ok"], cov["edges_total"])
        self.assertGreaterEqual(cov["edges_total"], 8)          # 2 框 × 4 边
        for item in cov["per_box"]:
            for name, edge in item["edges"].items():
                self.assertTrue(edge["ok"], f"{item['label']} 的 {name} 边采样不足：{edge}")

    def test_02_stale_segment_list_fails_for_current_table(self) -> None:
        """负控：陈旧行列表对当前表必须判**失败**（否则判据无判别力）。"""
        stale_plan = [{"row": row, "x": x, "why": "stale"} for row, x in STALE_SEGMENTS]
        # 用与现场相同的窗口宽度核算
        cov = G.coverage(stale_plan, self.boxes)
        self.assertFalse(cov["edge_criterion_passed"],
                         "陈旧行列表竟然通过了边判据 ⇒ 判据无判别力")
        self.assertLess(cov["rate"], 0.2, f"陈旧列表的逐像素覆盖率应很低：{cov['rate']}")

    def test_03_emitted_tcl_matches_existing_format(self) -> None:
        plan = G.build_plan(self.boxes)
        out = self.dir / "gen.tcl"
        G.emit_tcl(plan, 5, out)
        text = out.read_text(encoding="utf-8")
        self.assertIn("S5_ROW_BEGIN row=", text)
        self.assertIn("mrd -force", text)
        self.assertIn("connect -url tcp:localhost:", text)      # 端口可覆盖（默认 23121）

    # ── 地址模式端到端（测量链离线闭环） ────────────────────────────────────
    BUF0 = 0x00138C00

    def _synth_dump(self, *, tamper: bool = False) -> pathlib.Path:
        """按生成计划的**真实地址**合成转储：边框像素用类颜色，其余背景；可选篡改一个边框像素。"""
        rows: dict[int, bytearray] = {}
        colors = VP.parse_class_colors(REPO_ROOT / "scripts/stage5_t01/p1_app/s5_overlay.c")
        for box in self.boxes:
            x1, y1, x2, y2 = box["rect"]
            want = colors[box["cls"] % 5]
            for (x, y) in VP.R.border_pixel_sets(x1, y1, x2, y2, VP.LINE_W, G.CANVAS_W, G.CANVAS_H):
                row = rows.setdefault(y, bytearray([169] * (G.CANVAS_W * 3)))
                row[3 * x:3 * x + 3] = bytes(want)
        if tamper:
            x1, y1 = self.boxes[0]["rect"][0], self.boxes[0]["rect"][1]
            rows[y1][3 * x1:3 * x1 + 3] = bytes((7, 7, 7))
        plan = G.build_plan(self.boxes)
        words_per_seg = G.WINDOW_PX * 3 // G.WORD_ALIGN
        lines = ["S5_DUMP_BEGIN"]
        for item in plan:
            row, x0 = item["row"], item["x"]
            data = rows.get(row, bytearray([169] * (G.CANVAS_W * 3)))
            lines.append(f"S5_ROW_BEGIN row={row} x={x0}")
            for i in range(words_per_seg):
                addr = self.BUF0 + row * G.STRIDE + x0 * 3 + i * G.WORD_ALIGN
                chunk = bytes(data[x0 * 3 + i * G.WORD_ALIGN: x0 * 3 + i * G.WORD_ALIGN + G.WORD_ALIGN])
                if len(chunk) < G.WORD_ALIGN:
                    chunk = chunk + bytes(G.WORD_ALIGN - len(chunk))
                lines.append(f"  {addr:06X}:   {chunk.hex().upper()}")
        path = self.dir / f"synth_{'tamper' if tamper else 'ok'}.txt"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        return path

    def test_05_address_mode_end_to_end_passes(self) -> None:
        dump = self._synth_dump()
        code = VP.main(["--dump", str(dump), "--case", "5", "--header", str(self.header),
                        "--source", str(REPO_ROOT / "scripts/stage5_t01/p1_app/s5_overlay.c"),
                        "--mode", "address", "--buf0", hex(self.BUF0), "--stride", str(G.STRIDE),
                        "--min-coverage", "0.02"])
        self.assertEqual(code, 0, "地址模式端到端应判通过")

    def test_06_address_mode_tamper_is_caught(self) -> None:
        dump = self._synth_dump(tamper=True)
        code = VP.main(["--dump", str(dump), "--case", "5", "--header", str(self.header),
                        "--source", str(REPO_ROOT / "scripts/stage5_t01/p1_app/s5_overlay.c"),
                        "--mode", "address", "--buf0", hex(self.BUF0), "--stride", str(G.STRIDE),
                        "--min-coverage", "0.02"])
        self.assertEqual(code, 1, "篡改边框像素未被抓住 ⇒ 测量链无判别力")

    def test_04_cli_exit_codes(self) -> None:
        header = self.dir / "s5_overlay_cases.h"
        self.assertEqual(G.main(["--case", "5", "--header", str(header)]), 0)
        self.assertEqual(G.main(["--case", "99", "--header", str(header)]), 2)
        self.assertEqual(G.main(["--case", "5", "--header", str(self.dir / "nope.h")]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)