"""独立核验已产生的源码原件；不批准失败身份采集或连续资源预算。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
WORK = ROOT / "tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02"
sys.path.insert(0, str(WORK))
import compat_pins as pins


def bound(path):
    """绑定精确存在的实际原字节。"""
    path = pins.exact(path)
    raw = path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def main():
    pins.require_ready()
    freeze = json.loads(pins.SOURCE_FREEZE.read_text(encoding="utf-8"))
    before_path = pins.SOURCE_PRE / "source_before.json"
    before = json.loads(pins.exact(before_path).read_text(encoding="utf-8"))
    capture_path = WORK / "s15_runtime_source_before_r1.native.json"
    capture = json.loads(pins.exact(capture_path).read_text(encoding="utf-8"))
    assert capture["native_exit_code"] == 0 and capture["direct_child_wait_returned"] is True
    assert before["source_commit"] == freeze["source_commit"] == pins.SOURCE_COMMIT
    assert before["source_freeze_sha256"] == bound(pins.SOURCE_FREEZE)["sha256"]
    commands = []

    def git(*args):
        """记录每条真实Git直接wait，不声明其短生命周期后代身份已采集。"""
        command = ["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", *args]
        child = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
        commands.append(dict(command=command, native_exit_code=child.returncode, direct_wait=True,
                             stdout_sha256=hashlib.sha256(child.stdout).hexdigest(), stderr_sha256=hashlib.sha256(child.stderr).hexdigest()))
        assert child.returncode == 0, child.stderr
        return child.stdout

    assert git("rev-parse", "HEAD").decode("ascii").strip() == pins.SOURCE_COMMIT
    hashes = {}
    for row in freeze["source_files"]:
        actual = bound(ROOT / row["path"])
        assert actual == row
        raw = pins.exact(ROOT / row["path"]).read_bytes()
        blob = git("show", pins.SOURCE_COMMIT + ":" + row["path"])
        assert blob == raw or (b"\r\n" not in blob and blob.replace(b"\n", b"\r\n") == raw)
        snapshot = next(item["snapshot"] for item in before["source_files"] if item["path"] == row["path"])
        assert bound(ROOT / snapshot)["sha256"] == row["sha256"]
        hashes[row["path"]] = row["sha256"]
    assert hashes == before["source_sha256"] and len(hashes) == 46
    assert before["frozen14_sha256"] == freeze["frozen14"]
    assert all(hashes[name] == digest for name, digest in freeze["frozen14"].items())
    review = json.loads(pins.TOOLS_G2.read_text(encoding="utf-8"))
    tools = review["reviewed_tools"]
    assert len(tools) == 13
    assert all(bound(ROOT / row["path"]) == row for row in tools)
    dependencies = freeze["tool_runtime_dependencies"]
    for row in dependencies:
        assert bound(ROOT / row["actual"]["path"]) == row["actual"]
        assert bound(ROOT / row["recovery"]["path"]) == row["recovery"]
        assert row["actual"]["sha256"] == row["recovery"]["sha256"]
    assert git("rev-parse", "HEAD").decode("ascii").strip() == pins.SOURCE_COMMIT
    result = dict(status="READY_SOURCE_BYTES_AND_COMMIT_ONLY", source_commit=pins.SOURCE_COMMIT,
                  source_before=bound(before_path), source_freeze=bound(pins.SOURCE_FREEZE),
                  source_count=46, static_count=33, frozen14=freeze["frozen14"],
                  git_commands=commands, tool_runtime_dependencies=dependencies,
                  failed_capture=bound(capture_path), failed_capture_status=capture["capture_status"],
                  failed_capture_unknown_count=capture["unknown_count"],
                  limitations=["源码collector真实child0；其wrapper2和27短进程未知保留，不批准该采集、预算或整树终态。", "本核查独立核源码及直接Git退出码；Vivado必须由新守卫/消费器另行实际准入。"])
    with (HERE / "source_admission_r01.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(dict(status=result["status"], source_count=46, git_direct_wait_count=len(commands),
                         failed_capture_preserved=True, budget="NOT_APPROVED_BY_SOURCE_CHECK")))


if __name__ == "__main__":
    main()
