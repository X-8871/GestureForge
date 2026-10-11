"""保存 S7 实际综合后的源码核验、静态映射及关闭日志原件。"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
PREFLIGHT = ROOT / "report/evidence/S2B-T17/s7_source_preflight_20261011_r01"
LOG = Path("C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition\\tmp\\2B\\S2B-T17\\s7_root_run_20261011_r01\\.vivado-ai\\vivado_23400231_91fc2051.log")
BASELINE = "a5caefba952a08f365d57193696b08c0e1aff2a5"

def digest(path):
    """核验精确现存文件并返回原字节哈希。"""
    assert path.is_file() and not path.is_symlink(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_new(path, value):
    """新证据只创建一次，已有原件不得覆盖。"""
    assert path.parent.is_dir() and not path.exists(), path
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

def main():
    """先确认原生项目关闭成功，再捕获核验退出码及不可变快照。"""
    assert ROOT.is_dir() and RUN.is_dir() and PREFLIGHT.is_dir()
    close = json.loads((RUN / "mcp_close.json").read_text(encoding="utf-8"))
    assert close["input"]["command"] == "close_project"
    assert close["input"]["session_id"] == "vivado-20261011-205640-497a6a78"
    close_result = json.loads(close["result"]["content"][0]["text"])
    assert close_result["exit_code"] == 0
    command = [sys.executable, "-B", "-X", "utf8", str(RUN / "source_preflight.py"), "after"]
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
    for name, data in (("source_after.stdout.log", result.stdout), ("source_after.stderr.log", result.stderr)):
        target = RUN / name
        assert not target.exists()
        with target.open("xb") as stream:
            stream.write(data)
    write_new(RUN / "source_after.native.json", {
        "command": command, "cwd": str(ROOT), "native_exit_code": result.returncode,
        "elapsed_seconds": time.monotonic() - started, "peak_memory_bytes": None,
        "host_shell_exit_code": None})
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    after = json.loads((PREFLIGHT / "source_after.json").read_text(encoding="utf-8"))
    assert after["source_commit"] == BASELINE and after["actual_head_at_check"] == BASELINE
    spec = importlib.util.spec_from_file_location("s7_closed_checker", ROOT / "verification/check_s2b_inference_platform.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    mapping = checker.check_static(ROOT)
    frozen = {row["path"]: row["sha256"] for row in after["source_files"]}
    assert len(mapping) == 31 and len(frozen) == 39
    assert all(frozen[name] == value for name, value in mapping.items())
    target = RUN / "static_actual_closed.json"
    write_new(target, {
        "status": "PASS_CLOSED_ACTUAL_STATIC", "profile": "0.1.7",
        "source_commit": BASELINE, "source_count": len(mapping),
        "source_sha256": mapping, "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "limitations": ["仅静态源码绑定；实际 50MHz 综合 STA 失败，实板未执行"]})
    snapshot = RUN / "root_session_snapshot.log"
    assert LOG.is_file() and not LOG.is_symlink() and not snapshot.exists()
    raw = LOG.read_bytes()
    with snapshot.open("xb") as stream:
        stream.write(raw)
    assert snapshot.read_bytes() == raw
    write_new(RUN / "root_session_snapshot_binding.json", {
        "source_path": str(LOG), "snapshot_path": str(snapshot),
        "sha256": digest(snapshot), "bytes": len(raw), "project_closed": True,
        "mcp_close_sha256": digest(RUN / "mcp_close.json"),
        "scope": "S7 报告及项目关闭后的原字节快照，不消费后续日志追加"})
    print(json.dumps({
        "status": "PASS_CLOSED_SOURCE_LOG_ONLY",
        "source_after_sha256": digest(PREFLIGHT / "source_after.json"),
        "static_sha256": digest(target), "snapshot_sha256": digest(snapshot),
        "snapshot_bytes": len(raw), "source_count": len(frozen)}, ensure_ascii=False))

if __name__ == "__main__":
    main()

