"""门禁修复的单次运行器；真实失败仍记录为 FAIL，不认证旧证据包。"""
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
REL = OUT.relative_to(ROOT).as_posix()
SOURCES = ["verification/tool_self_tests.py", "verification/s6e_acceptance_check.py",
           "verification/test_s6_gate_regression.py", "verification/claim_verify.py",
           "verification/s6_g0_selfcheck.py", "verification/s6a_fresh_selfcheck_twice.py",
           "verification/approval_regression.py", "verification/export_selfproof.py",
           "verification/check_stage_delivery.py", "docs/stage6/s6a_stage6_g0_behavior_v1.json",
           "docs/stage6/s6e_stage6_acceptance_cases_v1.json", "docs/stage6/S6E_stage6_acceptance_cases_v1.md"]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    if (OUT / "execution.json").exists():
        raise SystemExit("RunId 已使用；禁止覆盖")
    before = {p: sha(ROOT / p) for p in SOURCES}
    commands = [
        ("directed_regression", ["verification/test_s6_gate_regression.py"]),
        ("acceptance_injections", ["verification/s6e_acceptance_check.py", "--project-root", str(ROOT),
                                  "--inject-self-test", "--out", REL + "/acceptance_injections.json"]),
        ("tool_suite_s6a", ["verification/tool_self_tests.py", "--project-root", str(ROOT), "--package", "s6a",
                            "--run-dir", "report/evidence/S6-A/s6a_g0_20261024_r13",
                            "--s6a-run", "report/evidence/S6-A/s6a_g0_20261024_r13",
                            "--out", REL + "/tool_suite_s6a.json"])]
    checks, timings = [], {}
    for name, args in commands:
        command = [sys.executable, "-B"] + args
        start = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (OUT / (name + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
        checks.append({"name": name, "status": "PASS" if result.returncode == 0 else "FAIL",
                       "command": subprocess.list2cmdline(command), "exit_code": result.returncode})
        timings[name] = round(time.perf_counter() - start, 3)
        print(name, result.returncode, timings[name], flush=True)
    after = {p: sha(ROOT / p) for p in SOURCES}
    save("execution.json", {"schema_version": 1, "source_hashes_before": before, "source_hashes_after": after,
         "source_stable": before == after, "checks": checks, "elapsed_seconds": timings,
         "generated_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
         "peak_memory": "未测", "repeated_final_runs": 1,
         "scope": "两脚本定向修复；旧 r13 只读复算，不认证旧包；S6-B 未重跑"})
    files = [{"path": p, "sha256": before[p], "role": "source", "keep_reason": "实际源码与输入"} for p in SOURCES]
    files += [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": "result",
               "keep_reason": "本轮真实结果/日志及复现命令"} for p in sorted(OUT.iterdir()) if p.is_file()]
    save("delivery_manifest.json", {"schema_version": 1, "stage": "6", "task_id": "S6-E", "run_id": OUT.name,
         "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "evidence_dir": REL, "interfaces": [],
         "interfaces_not_applicable_reason": "验证器修复只消费本树行为表和旧证据，不消费下游冻结接口或硬件接口。",
         "files": files, "checks": checks, "tool_versions": {"python": platform.python_version()},
         "limitations": ["source_commit 为运行基线；待审源码以 files SHA256 绑定。",
                         "旧包不就地重建；工具套件失败不视为关闭，见真实 claim 结果。",
                         "G3/G5 未提升；T6-A03 和 P 为 NOT_RUN；无硬件操作；S6-B 完整包未重建。",
                         "CHECKS_OK 仅证明包装绑定；本包可含真实 FAIL，不能视为全套通过。"]})
    return 0 if before == after and all(c["exit_code"] == 0 for c in checks) else 1

if __name__ == "__main__":
    raise SystemExit(main())
