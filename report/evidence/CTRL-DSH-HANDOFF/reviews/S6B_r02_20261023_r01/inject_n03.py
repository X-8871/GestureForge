#!/usr/bin/env python3
"""S6-B r02 复审：N-03 覆盖映射由实际用例派生 + 断言有效性（隔离副本内注入）。"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso")
WORK = ISO / "tmp/review_inj/builder"
ORIG_SRC = ISO / "report/evidence/S6-B/s6b_core_20261023_r02/cases/build_case_matrix.py"
COMMITTED_MATRIX = ISO / "report/evidence/S6-B/s6b_core_20261023_r02/cases/case_matrix.json"
PY = sys.executable
ENV = {**os.environ, "PYTHONUTF8": "1"}

if WORK.exists():
    shutil.rmtree(WORK)
(WORK / "cases").mkdir(parents=True)

TEXT = ORIG_SRC.read_text(encoding="utf-8")
OLD_RUN = 'RUN = Path(r"D:\\codex-worktrees\\w6\\report\\evidence\\S6-B\\s6b_core_20261023_r02")'
assert OLD_RUN in TEXT, "未找到 RUN 行"
NEW_RUN = f'RUN = Path(r"{WORK}")'


def build(label: str, text: str, expect_zero: bool):
    (WORK / "builder.py").write_text(text, encoding="utf-8")
    proc = subprocess.run([PY, "-B", str(WORK / "builder.py")], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False, env=ENV)
    tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
    print(f"[{label}] exit={proc.returncode} expect_zero={expect_zero} :: {tail[-1][:160] if tail else ''}")
    return proc.returncode


# (i) 未注入：应成功，且产物与提交版一致（builder 可复现）
base = TEXT.replace(OLD_RUN, NEW_RUN)
rc = build("N-03 baseline", base, True)
if rc == 0:
    got = hashlib.sha256((WORK / "cases/case_matrix.json").read_bytes()).hexdigest()
    want = hashlib.sha256(COMMITTED_MATRIX.read_bytes()).hexdigest()
    print(f"  重新生成的 case_matrix.json 与提交版一致: {got == want} ({got[:16]} vs {want[:16]})")

# (ii) 注入 A：把一条用例的 matrix_class 改成未映射值 → 必须失败
inject_a = base.replace('"case_id": "C6b-no-hand-with-detections"',
                        '"case_id": "C6b-no-hand-with-detections"', 1)
inject_a = inject_a.replace('"matrix_class": "NO_HAND / 未知类 / 低分",',
                            '"matrix_class": "复审注入：未映射类别",', 1)
rc_a = build("N-03 injectA 未映射类", inject_a, False)

# (iii) 注入 B：删掉一个 CDX 类别的映射（使该类无用例）→ 必须失败
inject_b = base.replace('    "低 FPS / 窗口完成取较晚": "时间等于阈值、前后 1 个计时单位",\n', "")
rc_b = build("N-03 injectB 某类无用例", inject_b, False)

# (iv) 注入 C：让两条用例映射到同一 CDX 类的重复检查（把 C9c 的 class 改成与 C1 相同）
inject_c = base.replace('"matrix_class": "低 FPS / 窗口完成取较晚",', '"matrix_class": "每类稳定输入",', 1)
rc_c = build("N-03 injectC C9c 改归 C1 类（应仍成功，覆盖数变 6）", inject_c, True)

print("RESULT:", {"baseline_ok": rc == 0, "injectA_fails": rc_a != 0,
                  "injectB_fails": rc_b != 0, "injectC_ok": rc_c == 0})