"""封存归档首轮原生检查，再生成含配置及关闭日志的新清单。"""

import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FORMAL = ROOT / "report/evidence/S2B-T16/independent_postconfig_review_20261011_r01"
OLD_SHA = "462abe31567bb99b8c5dfa78b166e00f2b861760b155a0ccbc3873268ec05740"


def digest(raw):
    """计算原字节SHA。"""
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    """禁止覆盖关闭的记录。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """原生检查的所有输出先关闭于缓存，再复制到正式证据。"""
    original_path = FORMAL / "delivery_manifest.json"
    assert FORMAL.is_dir() and digest(original_path.read_bytes()) == OLD_SHA
    new_path = FORMAL / "delivery_manifest_r02.json"
    run_dir = Path(__file__).parent / "archive_checks_r01"
    assert not run_dir.exists() and not new_path.exists()
    run_dir.mkdir()
    manifest = json.loads(original_path.read_text(encoding="utf-8"))
    records, copies = [], []
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
                   "--mode", mode, "--manifest", str(original_path), "--project-root", str(ROOT)]
        start = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = run_dir / f"{mode}.stdout.log", run_dir / f"{mode}.stderr.log"
        out.write_bytes(result.stdout)
        err.write_bytes(result.stderr)
        native_path = run_dir / f"{mode}.native.json"
        native = {"command": command, "native_exit_code": result.returncode,
                  "elapsed_seconds": time.perf_counter() - start,
                  "closed_logs": [{"path": p.relative_to(ROOT).as_posix(),
                                   "sha256": digest(p.read_bytes())} for p in (out, err)],
                  "peak_memory_bytes": None, "peak_reason": "本轻量归档检查未测峰值。"}
        save(native_path, native)
        assert result.returncode == expected, f"{mode}:原生{result.returncode}，期待{expected}"
        records.append({"name": "root归档首清单" + mode + "原生检查",
                        "status": "PASS" if result.returncode == 0 else "FAIL",
                        "command": subprocess.list2cmdline(command), "exit_code": result.returncode,
                        "reason": "原件封装绑定；inputs2仍反映未冻结接口及STA/未执行阻断，不改变独审范围。"})
        copies.extend((out, err, native_path))
    for source in copies:
        target = FORMAL / ("root_archive_" + source.name)
        assert source.is_file() and not target.exists()
        shutil.copyfile(source, target)
        assert source.read_bytes() == target.read_bytes()
        manifest["files"].append({"path": target.relative_to(ROOT).as_posix(),
                                  "sha256": digest(target.read_bytes()),
                                  "role": "log" if target.suffix == ".log" else "result"})
    for source, name, role in ((Path(__file__).parent / "archive_postconfig_config.json", "input_config.json", "input"),
                               (Path(__file__), "seal_postconfig_archive.py", "source"),
                               (Path(__file__).parent / "archive.native.json", "archive.native.json", "result"),
                               (Path(__file__).parent / "archive.stdout.log", "archive.stdout.log", "log"),
                               (Path(__file__).parent / "archive.stderr.log", "archive.stderr.log", "log")):
        target = FORMAL / name
        assert source.is_file() and not target.exists()
        shutil.copyfile(source, target)
        assert source.read_bytes() == target.read_bytes()
        manifest["files"].append({"path": target.relative_to(ROOT).as_posix(),
                                  "sha256": digest(target.read_bytes()), "role": role})
    manifest["files"].append({"path": original_path.relative_to(ROOT).as_posix(),
                              "sha256": OLD_SHA, "role": "artifact"})
    manifest["checks"].extend(records)
    manifest["limitations"].append("首归档清单原件不覆盖；本r02绑定归档配置、脚本及已关闭的首轮检查原件。最终动态检查日志仅留隔离缓存，避免清单自引用。")
    save(new_path, manifest)
    print(json.dumps({"status": "SEALED_ARCHIVE_WRAPPER_ONLY", "bindings": len(manifest["files"]),
                      "manifest_sha256": digest(new_path.read_bytes()),
                      "checks_native": [record["exit_code"] for record in records]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
