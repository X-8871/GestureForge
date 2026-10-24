"""主运行结束后追加诊断与只读包装核验；只完成本轮首次封包。"""
import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
REL = OUT.relative_to(ROOT).as_posix()

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    if (OUT / "packaging_checks.json").exists():
        raise SystemExit("已经封包，不得重跑覆盖")
    manifest = json.loads((OUT / "delivery_manifest.json").read_text(encoding="utf-8"))
    for check in manifest["checks"]:
        if check["status"] == "FAIL":
            check["reason"] = "旧 r13 的当前源码复算仍失败；未改写旧包或降低正常声明标准，详见 tool_suite_s6a.json 与 snapshot_diagnostic.json。"
    diagnostic = ROOT / "tmp/6/self_test_snapshot.json"
    shutil.copyfile(diagnostic, OUT / "snapshot_diagnostic.json")
    inputs = copy.deepcopy(manifest)
    inputs["files"] = [dict(f, role="input") for f in inputs["files"] if f["role"] == "source"]
    inputs["checks"] = [{"name": "输入源码运行前后稳定性", "status": "PASS", "exit_code": 0,
                          "command": "python -B " + REL + "/run_validation.py",
                          "reason": "execution.json 的 source_stable 必须为 true。"}]
    assert json.loads((OUT / "execution.json").read_text(encoding="utf-8"))["source_stable"] is True
    save("inputs_manifest.json", inputs)
    initial = ROOT / "report/evidence/S6-E/s6e_gate_fix_20261024_r01"
    manifest["limitations"].append("r01 仅初轮诊断，执行中源码继续修复，不作为最终源码认证；r02 是源码前后哈希一致的最终轮。")
    bound = [f for f in manifest["files"] if f["role"] == "source"]
    bound += [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": "diagnostic",
               "keep_reason": "初轮失败诊断，非最终源码验证"} for p in sorted(initial.iterdir()) if p.is_file()]
    manifest["files"] = bound + [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": "result",
                                  "keep_reason": "最终轮真实命令/结果/日志/诊断"}
                                 for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "delivery_manifest.json"]
    save("delivery_manifest.json", manifest)
    packaging = []
    for mode, filename in (("inputs", "inputs_manifest.json"), ("evidence", "delivery_manifest.json")):
        command = [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"),
                   "--mode", mode, "--manifest", str(OUT / filename), "--project-root", str(ROOT)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        packaging.append({"mode": mode, "command": subprocess.list2cmdline(command),
                          "exit_code": result.returncode, "output": result.stdout + result.stderr})
        print(mode, result.returncode, result.stdout, flush=True)
    save("packaging_checks.json", packaging)
    # 收尾绑定包装核验的输出；不再执行受绑定脚本或改写任何结果。
    manifest["files"].append({"path": REL + "/packaging_checks.json", "sha256": sha(OUT / "packaging_checks.json"),
                              "role": "result", "keep_reason": "只读包装核验的真实命令与退出码；不代表测试通过"})
    save("delivery_manifest.json", manifest)
    return 0 if all(p["exit_code"] == 0 for p in packaging) else 1

if __name__ == "__main__":
    raise SystemExit(main())
