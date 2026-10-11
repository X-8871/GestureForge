"""修复闭合包装顺序；先绑定现有原件，再在隔离缓存执行检查。"""
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
    """校验普通文件原字节。"""
    assert path.is_file() and not path.is_symlink(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """每次写入新名称，保留所有失败原件。"""
    assert path.parent.is_dir() and not path.exists(), path
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """机器检查仅核对证据包装，不批准失败的时序。"""
    original = REPORT / "s8_delivery_manifest.json"
    manifest = json.loads(original.read_text(encoding="utf-8"))
    assert manifest["source_commit"] == "c9f423cddc74ea45071fdbb6a68e4505316babb1"
    closed = REPORT / "root_closed_r02"
    assert not closed.exists()
    closed.mkdir()
    script = Path(__file__).resolve()
    shutil.copyfile(script, closed / script.name)
    assert sha(script) == sha(closed / script.name)

    def add(path, role):
        """已有绑定只允许相同SHA，新增绑定使用精确三字段。"""
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
    process = json.loads((REPORT / "root_closed/owned_process_closed.json").read_text(encoding="utf-8"))
    assert process["exit_code"] == 0 and json.loads(process["output"])["owned_process_absent"] is True
    prior = json.loads((REPORT / "root_closed/evidence.native.json").read_text(encoding="utf-8"))
    assert prior["native_exit_code"] == 2
    manifest["checks"].append(dict(name="首轮闭合包装顺序失败", status="FAIL", command=prior["windows_command"],
        exit_code=2, reason="首轮在向目录新增文件后检查旧清单，真实未列入files错误保留；本轮重建完整绑定。"))
    inputs = REPORT / "s8_delivery_manifest_closure_inputs_r02.json"
    save(inputs, manifest)
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
                   "--mode", mode, "--manifest", str(inputs), "--project-root", str(ROOT)]
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=55)
        paths = []
        for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
            path = CACHE / ("closure_r02_" + mode + "." + suffix)
            with path.open("xb") as stream:
                stream.write(data)
            paths.append(path)
        native = CACHE / ("closure_r02_" + mode + ".native.json")
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
    manifest["limitations"].append("首轮闭合包装失败完整保留；ROOT已封存seal原生0及自有会话关闭/进程退出，独立证据审查仍待执行。")
    final = REPORT / "s8_delivery_manifest_r02.json"
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
