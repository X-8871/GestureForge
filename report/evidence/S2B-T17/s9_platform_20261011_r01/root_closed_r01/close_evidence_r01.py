"""闭合S9实际失败时序、资源警报及工具退出证据，不批准部署。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).parents[4]
CACHE = Path(__file__).parent
REPORT = ROOT / "report/evidence/S2B-T17/s9_platform_20261011_r01"
PRE = ROOT / "report/evidence/S2B-T17/s9_source_preflight_20261011_r01"


def sha(path):
    """核对完整普通文件及原字节。"""
    assert path.is_file() and not path.is_symlink(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """只创建新UTF-8原件，禁止覆盖。"""
    assert path.parent.is_dir() and not path.exists(), path
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """先完成所有目录写入，再执行包装检查并保留原生码。"""
    original = REPORT / "s9_delivery_manifest.json"
    manifest = json.loads(original.read_text(encoding="utf-8"))
    assert manifest["source_commit"] == "38c5bc02f42920d4203aa6752530d09c80fc4c57"
    closed = REPORT / "root_closed_r01"
    assert REPORT.is_dir() and not closed.exists()
    closed.mkdir()
    process = json.loads((CACHE / "owned_process_closed.json").read_text(encoding="utf-8"))
    assert process["result"]["exit_code"] == 0
    assert json.loads(process["result"]["output"])["present"] is False
    stop = json.loads((CACHE / "mcp_stop.json").read_text(encoding="utf-8"))
    message = json.loads(stop["result"]["content"][0]["text"])
    assert message["status"] == "success" and message["message"] == "Vivado closed"
    seal = json.loads((CACHE / "s9_seal_r01.native.json").read_text(encoding="utf-8"))
    assert seal["native_exit_code"] == 0
    paths = [Path(__file__), CACHE / "root_closed_gate.json", CACHE / "mcp_stop.json", CACHE / "owned_process_closed.json"]
    paths += list(sorted(CACHE.glob("s9_seal_r01.*")))
    for path in paths:
        target = closed / path.name
        assert not target.exists()
        shutil.copyfile(path, target)
        assert sha(path) == sha(target)

    def add(path, role):
        """已有绑定必须一致，新绑定严格使用三字段。"""
        name = path.relative_to(ROOT).as_posix()
        rows = [r for r in manifest["files"] if r["path"] == name]
        if rows:
            assert len(rows) == 1 and rows[0]["sha256"] == sha(path), name
        else:
            manifest["files"].append(dict(path=name, sha256=sha(path), role=role))

    for path in sorted(REPORT.rglob("*")):
        if path.is_file():
            add(path, "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result")
    for name in ("source_before.json", "source_after.json"):
        add(PRE / name, "input")
    manifest["checks"].append(dict(name="本轮owned Vivado已停止且PID缺失", status="PASS",
        command=process["input"]["cmd"], exit_code=process["result"]["exit_code"],
        reason="真实停止工具返回及独立只读PID核验；不是设计时序或实板通过。"))
    manifest["checks"].append(dict(name="本轮进程树RSS预算", status="FAIL", command=None, exit_code=None,
        reason="23:23:04实际离散样本4,900,474,880B超过4GiB；收到警报后核验时综合已完成，未停止或重跑，23:28:17回落。不提高预算，原件完整绑定。"))
    manifest["limitations"].append("本轮有真实wait客户端300s超时，服务器history/native日志336.601s成功；接口错误未改为0。进程树RSS越4GiB警报及恢复单列，两个child归属历史证据有限；五官方job串行。所有适用时序、实现及实板门禁仍未通过。")
    inputs = REPORT / "s9_delivery_manifest_closure_inputs_r01.json"
    save(inputs, manifest)
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
                   "--mode", mode, "--manifest", str(inputs), "--project-root", str(ROOT)]
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
        paths = []
        for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
            path = CACHE / ("closure_r01_" + mode + "." + suffix)
            with path.open("xb") as stream:
                stream.write(data)
            paths.append(path)
        native = CACHE / ("closure_r01_" + mode + ".native.json")
        save(native, dict(command=command, windows_command=subprocess.list2cmdline(command),
            native_exit_code=result.returncode, elapsed_seconds=time.monotonic()-started, peak_tree_rss_bytes=None))
        paths.append(native)
        assert result.returncode == expected, (mode, result.returncode, result.stdout.decode("utf-8"))
        for path in paths:
            shutil.copyfile(path, closed / path.name)
            assert sha(path) == sha(closed / path.name)
            add(closed / path.name, "log" if path.suffix == ".log" else "result")
        manifest["checks"].append(dict(name="ROOT闭合机器包装："+mode,
            status="PASS" if expected == 0 else "FAIL", command=subprocess.list2cmdline(command),
            exit_code=result.returncode, reason="包装核验；STA仍失败、候选未冻结且实板未运行。"))
    add(inputs, "artifact")
    final = REPORT / "s9_delivery_manifest_r02.json"
    save(final, manifest)
    command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
               "--mode", "evidence", "--manifest", str(final), "--project-root", str(ROOT)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
    for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
        with (CACHE / ("closure_final_r02." + suffix)).open("xb") as stream:
            stream.write(data)
    save(CACHE / "closure_final_r02.native.json", dict(command=command, native_exit_code=result.returncode))
    assert result.returncode == 0, result.stdout.decode("utf-8")
    print(json.dumps(dict(status="CLOSED_FAILED_STA_ONLY", manifest_sha256=sha(final),
        bindings=len(manifest["files"]), evidence_native_exit_code=0, inputs_native_exit_code=2), ensure_ascii=False))


if __name__ == "__main__":
    main()
