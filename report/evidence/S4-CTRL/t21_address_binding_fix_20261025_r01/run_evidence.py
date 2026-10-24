"""仅一次采集 RAW 重复事实修复证据；禁止覆盖已有结果。"""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
REL = OUT.relative_to(ROOT).as_posix()
BASE = "06c9ab83e4215b6ea5ec9fd827b59549e425a285"
SOURCES = ["docs/stage4/S4B_raw_system_g0_gap_registry.json",
           "scripts/stage4_s4b/audit_raw_system_g0_gaps.py", "verification/test_s4_raw_g0_registry.py"]


def sha(data):
    """计算原始字节哈希。"""
    return hashlib.sha256(data).hexdigest()


def save(name, data):
    """创建新证据文件。"""
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def git(*args, tree=ROOT):
    """只读获取 Git 对象。"""
    return subprocess.check_output(["git", "-C", str(tree), *args])


def main():
    """记录回归、实际复算及跨树窗口失效。"""
    assert {p.name for p in OUT.iterdir()} == {"run_evidence.py"}, "RunId 已有产物，禁止重跑"
    assert git("rev-parse", "HEAD").decode().strip() == BASE
    facts = []
    for tree, rel in [(Path("D:/codex-worktrees/dbdf"), "report/evidence/S3-T05/t05_stage3_window_20261024_r01/address_facts.md"),
                      (Path("D:/codex-worktrees/w5"), "report/evidence/S5-T01/s5t01_board_overlay_20261022_r01/run_manifest.json")]:
        assert (tree / rel).is_file()
        head = git("rev-parse", "HEAD", tree=tree).decode().strip()
        blob = git("cat-file", "blob", f"{head}:{rel}", tree=tree)
        fact = {"tree": str(tree), "head_at_read": head, "path": rel, "byte_basis": "git_blob_content", "sha256": sha(blob)}
        if tree.name == "w5":
            data = json.loads(blob)["board_evidence"]
            fact.update(uart_markers=data["uart_markers"], frame_size=data["mm2s"]["frame_size"])
        facts.append(fact)
    save("source_binding.json", {"source_commit": BASE,
         "actual_source_files": [{"path": p, "sha256": sha((ROOT / p).read_bytes())} for p in SOURCES],
         "authoritative_committed_facts": facts, "decimal_corrections": {"0x00114C00": 1133568, "0x00F95400": 16339968},
         "run_started_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")})
    steps = [
        ("regression", [sys.executable, "-B", "-m", "unittest", "verification.test_s4_raw_g0_registry", "-v"], 0),
        ("registry_audit", [sys.executable, "-B", "scripts/stage4_s4b/audit_raw_system_g0_gaps.py", "--evidence-dir", f"{REL}/audit"], 0),
        ("bound_heads", [sys.executable, "-B", "scripts/stage4_s4ctrl/check_bound_tree_heads.py", "--manifest",
                         "report/evidence/S4-CTRL/t21_optionA_landing_20261024_r02/bound_trees.json", "--evidence-dir", f"{REL}/bound_heads"], 1),
        ("diff_check", ["git", "diff", "--check"], 0)]
    checks = []
    for name, command, expected in steps:
        start = time.perf_counter()
        process = subprocess.run(command, cwd=ROOT, capture_output=True,
                                 env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        (OUT / f"{name}.log").write_text((process.stdout + process.stderr).decode("utf-8"),
                                        encoding="utf-8", newline="\n")
        checks.append({"name": name, "command": subprocess.list2cmdline(command), "exit_code": process.returncode,
                       "expected_exit_code": expected, "elapsed_seconds": round(time.perf_counter() - start, 6), "execution_count": 1})
        assert process.returncode == expected, checks[-1]
    save("execution_results.json", {"checks": checks, "peak_memory": "未测", "initial_test_execution_count": 1,
         "scope": "8 项主入口回归及真实登记表复算；无硬件/Vivado；跨树漂移为真实 FAIL，未刷新旧绑定。"})
    files = [{"path": p, "sha256": sha((ROOT / p).read_bytes()), "role": "source"} for p in SOURCES]
    files += [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p.read_bytes()),
               "role": "diagnostic" if p.suffix == ".py" else "log" if p.suffix == ".log" else "result"}
              for p in sorted(OUT.rglob("*")) if p.is_file()]
    save("delivery_manifest.json", {
        "schema_version": 1, "stage": "4", "task_id": "S4-CTRL", "run_id": OUT.name, "source_commit": BASE,
        "evidence_dir": REL, "interfaces": [{"name": "阶段4地址映射", "version": "r03", "frozen": False,
            "path": "docs/stage4/S4B_stage4_address_map.json", "sha256": sha((ROOT / "docs/stage4/S4B_stage4_address_map.json").read_bytes())}],
        "files": files, "checks": [{"name": c["name"], "command": c["command"], "exit_code": c["exit_code"],
            "status": "FAIL" if c["name"] == "bound_heads" else "PASS",
            "reason": "旧跨树窗口失效；如实保留 FAIL_STABLE_DRIFT，未重绑。" if c["name"] == "bound_heads" else "轻量定向检查通过。"} for c in checks],
        "tool_versions": {"python": sys.version, "git": git("--version").decode().strip(), "platform": platform.platform()},
        "limitations": ["跨树有效窗口失效，当前复算不代表系统 G0。", "等待独立复审，region 未 FROZEN，ENABLE=0。",
                        "硬件窗口未授权，板级验证、帧周期 P、阶段4 G5 尚未完成。", "峰值内存未测；未执行推理或 Vivado。"]})
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
