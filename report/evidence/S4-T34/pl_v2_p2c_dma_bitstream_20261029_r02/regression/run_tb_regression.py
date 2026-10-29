r"""P2c 回归：把 V2 冻结的 3 个 TB 跑在 **P2c RTL（SRC_BASE 默认 0）** 上，与 planA2 基线逐项对照。

目的（rev-s5 B2）：证明"加 SRC_BASE 参数"没有改变任何算术/时序/输出——
TB 未改动、RTL 未改动（默认 SRC_BASE=0 与冻结基线一致），只有参数默认值可被 BD 覆盖。

对照基线：D:\tmp\lead\planA2_20261029_r01\tb\results.tsv（P2a/P2b 冻结前的三条等价结果）
判据：pass=1 且 mismatch=0；cycles/ars/beats/tlast/tuser/bp_cycles 与基线逐项相同；FNV 行（若有）dut 与 gold 相同。
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

XV = pathlib.Path(r"D:\Xilinx\2026.1\Vivado\bin")
RTL = pathlib.Path(r"D:\tmp\lead\p2c_20261029_r01\src\rtl")
TBS = pathlib.Path(r"D:\wb-out\task1\tb")
GOLD_SRC = pathlib.Path(r"D:\wb-out-r3\p0_rerun\golden")
WORK = pathlib.Path(r"D:\tmp\lead\p2c_20261029_r01\regression")
BASE_TSV = pathlib.Path(r"D:\tmp\lead\planA2_20261029_r01\tb\results.tsv")

CASES = [
    ("work_engine_v2", "tb_s4d_preproc_engine_v2", ["s4d_preproc_engine_v2.sv"], "tb_s4d_preproc_engine_v2.sv"),
    ("work_v2_axi", "tb_s4d_preproc_v2_axi", ["s4d_preproc_engine_v2.sv", "s4d_axi4_rd_shim.sv"], "tb_s4d_preproc_v2_axi.sv"),
    ("work_v2_axis", "tb_s4d_preproc_v2_axis", ["s4d_preproc_engine_v2.sv", "s4d_preproc_out_axis.sv"], "tb_s4d_preproc_v2_axis.sv"),
]


def run(cmd: list[str], cwd: pathlib.Path, log: pathlib.Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5400)
    txt = (p.stdout or "") + (p.stderr or "")
    log.write_text(txt, encoding="utf-8", newline="\n")
    return p.returncode, txt


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    # TB 用相对路径 ../golden/<file> 读激励 ⇒ golden 必须在各 case 目录的父目录
    (WORK / "golden").mkdir(parents=True, exist_ok=True)
    for g in GOLD_SRC.glob("*.bin"):
        shutil.copy2(g, WORK / "golden" / g.name)
    baseline = {}
    for ln in BASE_TSV.read_text(encoding="utf-8").splitlines():
        parts = ln.split("\t")
        if len(parts) >= 6:
            baseline[parts[0]] = {"verdict": parts[4], "result": parts[5]}
    out_lines = []
    fails = 0
    for work, top, rtls, tb in CASES:
        d = WORK / work
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)

        srcs = [str(RTL / r) for r in rtls] + [str(TBS / tb)]
        c1, _ = run([str(XV / "xvlog.bat"), "-sv", "-i", str(RTL), *srcs], d, d / "xvlog.log")
        c2, _ = run([str(XV / "xelab.bat"), "-debug", "off", top, "-s", "sim"], d, d / "xelab.log")
        c3, tx = run([str(XV / "xsim.bat"), "sim", "-runall"], d, d / "xsim.log")
        res = next((ln for ln in tx.splitlines() if ln.startswith("RESULT")), None)
        fnv = next((ln for ln in tx.splitlines() if "FNV1a64" in ln or ln.startswith("FNV")), None)
        b = baseline.get(work, {})
        same = (res is not None and b.get("result") is not None
                and res.strip() == b["result"].strip() and c1 == 0 and c2 == 0 and c3 == 0)
        if not same:
            fails += 1
        out_lines.append(f"{work}\txvlog={c1}\txelab={c2}\txsim={c3}\t{'EQUIV' if same else 'DIFF'}\t{res}\t{fnv}")
        print(out_lines[-1], flush=True)
        print("  baseline:", b.get("result"), flush=True)
    (WORK / "results.tsv").write_text("\n".join(out_lines) + "\n", encoding="utf-8", newline="\n")
    print(f"P2C_TB_REGRESSION={'PASS' if fails == 0 else 'FAIL'} cases={len(CASES)} fails={fails}", flush=True)
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())