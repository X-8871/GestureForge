"""封存已结束的S8原生收集、资源释放与机器包装检查。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CACHE = Path(__file__).resolve().parent
REPORT = ROOT / "report/evidence/S2B-T17/s8_platform_20261011_r01"
PRE = ROOT / "report/evidence/S2B-T17/s8_source_preflight_20261011_r01"


def sha(path):
    """绑定普通文件原字节。"""
    assert path.is_file() and not path.is_symlink(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """拒绝覆盖已保存的真实运行。"""
    assert path.parent.is_dir() and not path.exists(), path
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """仅新增闭合记录，保留原始失败状态与清单。"""
    original = REPORT / "s8_delivery_manifest.json"
    manifest = json.loads(original.read_text(encoding="utf-8"))
    assert manifest["source_commit"] == "c9f423cddc74ea45071fdbb6a68e4505316babb1"
    closed = REPORT / "root_closed"
    assert not closed.exists()
    closed.mkdir()

    def add(path, role):
        """标准files字段保持精确三列且无重复路径。"""
        name = path.relative_to(ROOT).as_posix()
        assert name not in {r["path"] for r in manifest["files"]}, name
        manifest["files"].append(dict(path=name, sha256=sha(path), role=role))

    sources = [CACHE / name for name in (
        "root_closed_gate.json", "s8_seal_r01.native.json", "s8_seal_r01.stdout.log",
        "s8_seal_r01.stderr.log", "mcp_stop.json", "owned_process_closed.json")]
    sources.append(Path(__file__).resolve())
    for source in sources:
        target = closed / source.name
        assert not target.exists()
        shutil.copyfile(source, target)
        assert sha(source) == sha(target)
        add(target, "source" if target.suffix == ".py" else "log" if target.suffix == ".log" else "result")
    process = json.loads((closed / "owned_process_closed.json").read_text(encoding="utf-8"))
    assert process["exit_code"] == 0
    assert json.loads(process["output"])["owned_process_absent"] is True
    for name in ("source_before.json", "source_after.json"):
        add(PRE / name, "input")
    add(original, "artifact")
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
                   "--mode", mode, "--manifest", str(original), "--project-root", str(ROOT)]
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
        for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
            path = closed / (mode + "." + suffix)
            with path.open("xb") as stream:
                stream.write(data)
            add(path, "log")
        path = closed / (mode + ".native.json")
        save(path, dict(command=command, windows_command=subprocess.list2cmdline(command),
                        native_exit_code=result.returncode, elapsed_seconds=time.monotonic()-started,
                        peak_tree_rss_bytes=None))
        add(path, "result")
        assert result.returncode == expected, (mode, result.returncode, result.stdout)
        manifest["checks"].append(dict(name="ROOT闭合机器包装："+mode,
            status="PASS" if expected == 0 else "FAIL", command=subprocess.list2cmdline(command),
            exit_code=result.returncode, reason="包装核验；STA仍失败、候选未冻结且实板未运行。"))
    manifest["limitations"].append("ROOT已保存seal真实原生0和自有会话关闭/进程退出；本清单仍未获得独立证据准确性批准。")
    final = REPORT / "s8_delivery_manifest_r02.json"
    save(final, manifest)
    command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
               "--mode", "evidence", "--manifest", str(final), "--project-root", str(ROOT)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
    for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
        with (CACHE / ("final_manifest_check." + suffix)).open("xb") as stream:
            stream.write(data)
    save(CACHE / "final_manifest_check.native.json", dict(command=command, native_exit_code=result.returncode))
    assert result.returncode == 0, result.stdout
    print(json.dumps(dict(status="CLOSED_FAILED_STA_ONLY", manifest_sha256=sha(final),
        bindings=len(manifest["files"]), evidence_native_exit_code=0, inputs_native_exit_code=2), ensure_ascii=False))


if __name__ == "__main__":
    main()
