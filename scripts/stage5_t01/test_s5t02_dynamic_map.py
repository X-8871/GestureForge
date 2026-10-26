#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T02（离线部分）测试：隔离构建 + 合成流 + 与冻结参考对拍 + **变异判别力**。

覆盖
====
1. 端到端：构建（宿主 gcc，`-Wall -Wextra -Werror`）→ 生成用例/长流 → C 执行 → 对拍 `exit 0`，
   129 帧全部 `pixel_exact`、0 失败；
2. **变异判别力**（证明这组门真的能挡住错误实现，而不是"永远通过"）：
   - 取整少一步（`v·span` 而非 `v·(span−1)`）⇒ 对拍必须失败；
   - 线宽 2→1 ⇒ 对拍必须失败；
   - 过期判定 `>` 改成 `>=` ⇒ `age==limit` 用例必须失败；
3. 异常语义：16 框（>15）与非正面积框必须让 C 以非零退出，且**不**画出任何框；
4. 诚实标注：对拍报告必须含 NOT_RUN（板上项/真实回放/摄像头）与"合成流非阶段4 输出"限制；
5. 无板卡/Xilinx 依赖：可移植核心不含 Xilinx 头、无串口/网络调用。
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

P1_APP = REPO_ROOT / "scripts/stage5_t01/p1_app"
BUILD_SCRIPT = REPO_ROOT / "scripts/stage5_t01/build_dynamic_map.sh"
GEN = REPO_ROOT / "scripts/stage5_t01/gen_dynamic_map_cases.py"
VERIFY = REPO_ROOT / "scripts/stage5_t01/verify_dynamic_map.py"
CFLAGS = ["-std=c11", "-Wall", "-Wextra", "-Werror", "-O2"]
# 必须用 Git Bash：从原生 Python 调 `bash` 会命中 WSL bash（execvpe 失败）
GIT_BASH = next((p for p in (r"C:\Program Files\Git\bin\bash.exe",
                             r"C:\Program Files\Git\usr\bin\bash.exe")
                 if pathlib.Path(p).is_file()), shutil.which("bash") or "bash")


def _compile(src_dir: pathlib.Path, out_bin: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gcc", *CFLAGS, "-I", str(src_dir), "-o", str(out_bin),
         str(src_dir / "s5_dynamic_map_host.c"), str(src_dir / "s5_dynamic_map.c"), "-lm"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")


class T_DynamicMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5t02_")
        cls.run_dir = pathlib.Path(cls.tmp.name) / "run"
        cls.run_dir.mkdir(parents=True)
        # 路径用正斜杠 Windows 形式（Git Bash 原生可读；避免 cygpath 的 /tmp↔D:\tmp 映射歧义）
        cls.run_dir_posix = str(cls.run_dir).replace("\\", "/")
        cls.build = subprocess.run([GIT_BASH, str(BUILD_SCRIPT).replace("\\", "/"), cls.run_dir_posix],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace")
        if cls.build.returncode != 0:
            raise AssertionError(f"隔离构建失败：rc={cls.build.returncode}\nstdout={cls.build.stdout[-400:]}\nstderr={cls.build.stderr[-400:]}")
        candidates = [cls.run_dir / "build" / "s5_dynamic_map_host",
                      cls.run_dir / "build" / "s5_dynamic_map_host.exe"]
        cls.binary = next((p for p in candidates if p.is_file()), candidates[0])
        cls.gen = subprocess.run([sys.executable, "-B", str(GEN), "--out", str(cls.run_dir)],
                                 capture_output=True, text=True, encoding="utf-8", errors="replace")
        combined = cls.run_dir / "all.tsv"
        combined.write_text((cls.run_dir / "cases.tsv").read_text(encoding="utf-8") +
                            (cls.run_dir / "stream_120.tsv").read_text(encoding="utf-8"),
                            encoding="utf-8", newline="\n")
        cls.c_run = subprocess.run([str(cls.binary), str(combined), str(cls.run_dir / "all_c.jsonl")],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace")
        cls.jsonl = cls.run_dir / "all_c.jsonl"
        cls.report_path = cls.run_dir / "verify.json"
        cls.verify = subprocess.run(
            [sys.executable, "-B", str(VERIFY), "--cases", str(cls.run_dir / "cases.tsv"),
             "--stream", str(cls.run_dir / "stream_120.tsv"), "--jsonl", str(cls.jsonl),
             "--json", str(cls.report_path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        cls.report = json.loads(cls.report_path.read_text(encoding="utf-8")) if cls.report_path.is_file() else {}

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    # ── 端到端 ─────────────────────────────────────────────────────────────
    def test_01_build_and_generate_ok(self) -> None:
        self.assertEqual(self.build.returncode, 0, self.build.stderr[-800:])
        self.assertTrue(self.binary.is_file())
        self.assertEqual(self.gen.returncode, 0, self.gen.stderr[-400:])
        meta = json.loads((self.run_dir / "cases_meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["canvas"], [1280, 720])
        self.assertIn("HDMI", meta["canvas_source"])
        # 6 必备用例 + 4 非 OK 带框 + 零面积 + both + placement 组合 + NO_HAND 大 age + 3 过期边界
        self.assertEqual(len(meta["cases"]), 17)
        self.assertGreaterEqual(meta["stream"]["frames"], 100)     # ≥100 帧五元组

    def test_02_c_run_and_cross_check_pass(self) -> None:
        self.assertEqual(self.c_run.returncode, 0, self.c_run.stderr[-400:])
        self.assertEqual(self.verify.returncode, 0, self.verify.stdout[-800:])
        self.assertTrue(self.report["passed"], self.report["failures"][:5])
        self.assertEqual(self.report["frames_compared"], 137)
        self.assertEqual(self.report["verdict_counts"], {"pixel_exact": 137})
        self.assertEqual(self.report["semantics_unique"], ["B_latest_result_overlay"])

    def test_03_five_tuple_and_counters(self) -> None:
        """五元组可按 frame_id 索引、覆盖 0..119；计数与调度模型一致。"""
        self.assertEqual(self.report["displayed_ne_result_frames"], 2)
        counters = self.report["counters_expected"]
        for name in ("frames_committed", "warmup_frames", "dropped_frames", "timeouts",
                     "error_results", "duplicate_results", "out_of_order_results", "stale_cleared",
                     "zero_area_dropped"):
            self.assertGreater(counters[name], 0, f"{name} 未覆盖到故障路径")
        self.assertEqual(self.report["counters_from_c_summary"]["frames_committed"], 137)

    def test_04_hud_na_not_faked(self) -> None:
        self.assertEqual(self.report["hud_field_count"], 13)
        self.assertEqual(self.report["hud_na_required"], ["CAPTURE_FPS", "INFERENCE_FPS"])
        rows = [json.loads(line) for line in self.jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
        frames = [row for row in rows if "summary" not in row]
        for row in frames:
            hud = row["hud"]
            self.assertEqual(hud["CAPTURE_FPS"], "NA")
            self.assertEqual(hud["INFERENCE_FPS"], "NA")
            self.assertNotEqual(hud["CAPTURE_FPS"], 0)
            self.assertNotEqual(hud["INFERENCE_FPS"], 0)

    def test_05_stale_boundaries(self) -> None:
        """三个过期边界：`age==limit` 不过期 / `limit+1` 过期 / 显式 stale_flag 过期。"""
        raw = [json.loads(line) for line in self.jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = [row for row in raw if "summary" not in row]
        # 用例在文件最前面共 9 帧（长流从 0 重新编号，不能用 frame_index 做字典键）
        cases = rows[:17]
        # 实际顺序：0..5 原 6 用例 → 6/7 两个 age 边界 → 8..15 复审新增 → 16 显式 flag
        self.assertFalse(cases[6]["stale_effective"], "age_frame==limit 不应判过期")
        self.assertEqual(cases[6]["boxes_drawn"], 1)
        self.assertTrue(cases[7]["stale_effective"], "age_frame==limit+1 应判过期")
        self.assertEqual(cases[7]["boxes_drawn"], 0)
        self.assertEqual(cases[7]["stale_reason"], "age_frame_exceeds_limit")
        self.assertTrue(cases[16]["stale_effective"])
        self.assertEqual(cases[16]["stale_reason"], "stale_flag")

    def test_05b_review_coverage_is_exercised(self) -> None:
        """复审 B3/B4/B6/B7 的覆盖性：both 原因、placement 组合、零面积、非 OK 带框守恒。"""
        coverage = self.report["coverage_requirements"]
        for name, ok in coverage.items():
            self.assertTrue(ok, f"覆盖性判据未满足：{name}")
        raw = [json.loads(line) for line in self.jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
        cases = [row for row in raw if "summary" not in row][:17]
        # B2：非 OK 状态**带 2 框**仍必须 0 绘制（此前悬挂指针导致误绘 + 计数被隐藏）→ 索引 8..11
        for index, state in zip((8, 9, 10, 11), ("TIMEOUT", "ERROR", "DUPLICATE", "OUT_OF_ORDER")):
            self.assertEqual(cases[index]["boxes"], [], cases[index]["state"])
            self.assertEqual(cases[index]["boxes_drawn"], 0, cases[index]["state"])
            self.assertEqual(cases[index]["state"], state)
        # B3：both 串必须与冻结参考逐字一致 → 索引 13
        self.assertEqual(cases[13]["stale_reason"], "both")
        # B4：placement 组合必须被覆盖 → 索引 14
        placements = {box["label_placement"] for row in cases for box in row.get("boxes", [])}
        self.assertTrue(any("clamped_bottom+clamped_x" in item for item in placements), placements)
        # B6：零面积计数增长且同帧另一框照常绘制 → 索引 12
        self.assertEqual(cases[12]["zero_area_dropped"], 1)
        self.assertEqual(cases[12]["boxes_drawn"], 1)
        # B7：NO_HAND 且 age 越限 ⇒ 如实报非过期 → 索引 15
        self.assertFalse(cases[15]["stale_effective"])
        self.assertEqual(cases[15]["stale_reason"], "none")
        self.assertEqual(cases[15]["boxes_drawn"], 0)

    def test_05c_hud_fields_match_authoritative_table(self) -> None:
        """B5：HUD 字段名必须与 P1 权威表一致（且对拍器已逐项核对 11 项值）。"""
        authoritative = self.report["hud_fields_authoritative"]
        self.assertEqual(len(authoritative), 13)
        rows = [json.loads(line) for line in self.jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
        for row in rows:
            if "summary" in row:
                continue
            self.assertEqual(list(row["hud"]), authoritative)
            break

    def test_06_honest_labels(self) -> None:
        limitations = " ".join(self.report["limitations"])
        not_run = " ".join(self.report["not_run"])
        self.assertIn("合成", limitations)
        self.assertIn("不是", limitations)
        self.assertIn("B1–B10", not_run)
        self.assertIn("真实回放接入", not_run)

    # ── 变异判别力 ─────────────────────────────────────────────────────────
    def _mutated_verify(self, mutate) -> subprocess.CompletedProcess:
        """在隔离副本上注入变异（可同时改 .c 与 .h），再用**未修改的**对拍器检验必须失败。"""
        src = pathlib.Path(self.tmp.name) / "mut_src"
        shutil.rmtree(src, ignore_errors=True)
        shutil.copytree(P1_APP, src)
        changed = 0
        for name in ("s5_dynamic_map.c", "s5_dynamic_map.h", "s5_dynamic_map_host.c"):
            path = src / name
            text = path.read_text(encoding="utf-8")
            mutated = mutate(name, text)
            if mutated != text:
                path.write_text(mutated, encoding="utf-8", newline="\n")
                changed += 1
        self.assertGreater(changed, 0, "变异未生效（锚点不匹配）")
        binary = pathlib.Path(self.tmp.name) / "mut_bin"
        build = _compile(src, binary)
        self.assertEqual(build.returncode, 0, build.stderr[-500:])
        jsonl = pathlib.Path(self.tmp.name) / "mut.jsonl"
        run = subprocess.run([str(binary), str(self.run_dir / "all.tsv"), str(jsonl)],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        if run.returncode != 0:
            return run
        return subprocess.run(
            [sys.executable, "-B", str(VERIFY), "--cases", str(self.run_dir / "cases.tsv"),
             "--stream", str(self.run_dir / "stream_120.tsv"), "--jsonl", str(jsonl),
             "--json", str(pathlib.Path(self.tmp.name) / "mut_verify.json")],
            capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_10_mutation_span_off_by_one_is_caught(self) -> None:
        """取整少一步（用 span 而非 span−1）⇒ 对拍必须失败。"""
        def mutate(name: str, text: str) -> str:
            if name != "s5_dynamic_map.c":
                return text
            return (text.replace("box->x1 * (double)(display_width - 1)", "box->x1 * (double)display_width")
                        .replace("box->y1 * (double)(display_height - 1)", "box->y1 * (double)display_height")
                        .replace("box->x2 * (double)(display_width - 1)", "box->x2 * (double)display_width")
                        .replace("box->y2 * (double)(display_height - 1)", "box->y2 * (double)display_height"))
        result = self._mutated_verify(mutate)
        self.assertNotEqual(result.returncode, 0, "取整错误未被对拍抓住")

    def test_11_mutation_line_width_is_caught(self) -> None:
        """线宽 2→1 ⇒ 边框像素集必然不同，对拍必须失败。"""
        def mutate(name: str, text: str) -> str:
            if name != "s5_dynamic_map.h":
                return text
            return text.replace("#define S5D_DISPLAY_LINE_WIDTH_PX  2",
                                "#define S5D_DISPLAY_LINE_WIDTH_PX  1")
        result = self._mutated_verify(mutate)
        self.assertNotEqual(result.returncode, 0, "线宽错误未被抓住")

    def test_12_mutation_stale_ge_is_caught(self) -> None:
        """过期判定 `>` 改成 `>=` ⇒ `age==limit` 用例必须失败。"""
        def mutate(name: str, text: str) -> str:
            if name != "s5_dynamic_map.c":
                return text
            return text.replace("by_age = age_frame_ns > limit_ns ? 1 : 0;",
                                "by_age = age_frame_ns >= limit_ns ? 1 : 0;")
        result = self._mutated_verify(mutate)
        self.assertNotEqual(result.returncode, 0, "过期判定退化未被抓住")

    # ── 异常语义 ───────────────────────────────────────────────────────────
    def test_20_too_many_boxes_fails(self) -> None:
        path = pathlib.Path(self.tmp.name) / "too_many.tsv"
        lines = ["F 0 0 0 1 1000000000 1000500000 1001500000 0 0 OK 16"]
        lines += [f"B 0 0.5 0.1 0.1 0.2 0.2 30 11" for _ in range(16)]
        lines.append("E")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        result = subprocess.run([str(self.binary), str(path), str(pathlib.Path(self.tmp.name) / "tm.jsonl")],
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(result.returncode, 0, ">15 框必须被拒")

    def test_21_non_positive_area_fails(self) -> None:
        path = pathlib.Path(self.tmp.name) / "bad_box.tsv"
        path.write_text("F 0 0 0 1 1000000000 1000500000 1001500000 0 0 OK 1\n"
                        "B 0 0.5 0.40 0.40 0.30 0.30 30 11\nE\n", encoding="utf-8", newline="\n")
        result = subprocess.run([str(self.binary), str(path), str(pathlib.Path(self.tmp.name) / "bb.jsonl")],
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(result.returncode, 0, "非正面积框必须被拒（不得静默绘制）")

    # ── 无板卡依赖 ─────────────────────────────────────────────────────────
    def test_30_no_board_or_xilinx_dependency(self) -> None:
        core = (P1_APP / "s5_dynamic_map.c").read_text(encoding="utf-8")
        header = (P1_APP / "s5_dynamic_map.h").read_text(encoding="utf-8")
        host = (P1_APP / "s5_dynamic_map_host.c").read_text(encoding="utf-8")
        for forbidden in ("xil_printf.h", "xparameters.h", "xaxivdma.h", "xscugic.h",
                          "sleep.h", "xil_cache.h"):
            for text in (core, header):
                self.assertNotIn(forbidden, text, f"可移植核心不得包含 {forbidden}")
        lowered = (core + header + host).lower()
        for forbidden in ("import serial", "hw_server", "xsdb", "socket(", "curl "):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)