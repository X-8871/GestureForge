"""封存S7独审归档的原生检查及配置，不覆盖已关闭清单。"""

import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FORMAL = ROOT / "report/evidence/S2B-T17/independent_route_address_guard_review_20261011_r01"
OLD_SHA = "5d5b761dd62ea8e6507f9b7927671887ccf25a6c05c8f7650ea959039db4f566"


def digest(raw):
    """返回原字节SHA。"""
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    """只创建新文件，原失败及清单不得覆盖。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """先关闭实际检查输出，再生成有完整绑定的新清单。"""
    original = FORMAL / "delivery_manifest.json"
    assert FORMAL.is_dir() and digest(original.read_bytes()) == OLD_SHA
    new_path = FORMAL / "delivery_manifest_r02.json"
    run_dir = Path(__file__).parent / "archive_route_checks_r01"
    assert not run_dir.exists() and not new_path.exists()
    run_dir.mkdir()
    manifest = json.loads(original.read_text(encoding="utf-8"))
    records, copies = [], []
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        command = [sys.executable, "-X", "utf8", "-B", str(ROOT / "verification/check_stage_delivery.py"),
                   "--mode", mode, "--manifest", str(original), "--project-root", str(ROOT)]
        start = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = run_dir / f"{mode}.stdout.log", run_dir / f"{mode}.stderr.log"
        out.write_bytes(result.stdout)
        err.write_bytes(result.stderr)
        native_path = run_dir / f"{mode}.native.json"
        native = {"command": command, "native_exit_code": result.returncode,
                  "elapsed_seconds": time.perf_counter() - start,
                  "closed_logs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p.read_bytes())}
                                  for p in (out, err)],
                  "peak_memory_bytes": None, "peak_reason": "本轻量归档检查未测峰值。"}
        save(native_path, native)
        assert result.returncode == expected, f"{mode}:原生{result.returncode}，期待{expected}"
        records.append({"name": "root归档首清单" + mode + "原生检查",
                        "status": "PASS" if result.returncode == 0 else "FAIL",
                        "command": subprocess.list2cmdline(command), "exit_code": result.returncode,
                        "reason": "绑定检查；inputs2仍因物理未冻结、原失败及STA/实物未执行，不改变G2批准范围。"})
        copies.extend((out, err, native_path))
    for source in copies:
        target = FORMAL / ("root_archive_" + source.name)
        assert source.is_file() and not target.exists()
        shutil.copyfile(source, target)
        assert source.read_bytes() == target.read_bytes()
        manifest["files"].append({"path": target.relative_to(ROOT).as_posix(),
                                  "sha256": digest(target.read_bytes()),
                                  "role": "log" if target.suffix == ".log" else "result"})
    for source, name, role in ((Path(__file__).parent / "archive_route_config.json", "input_config.json", "input"),
                               (Path(__file__), "seal_route_archive.py", "source"),
                               (Path(__file__).parent / "archive_route.native.json", "archive_route.native.json", "result"),
                               (Path(__file__).parent / "archive_route.stdout.log", "archive_route.stdout.log", "log"),
                               (Path(__file__).parent / "archive_route.stderr.log", "archive_route.stderr.log", "log")):
        target = FORMAL / name
        assert source.is_file() and not target.exists()
        shutil.copyfile(source, target)
        assert source.read_bytes() == target.read_bytes()
        manifest["files"].append({"path": target.relative_to(ROOT).as_posix(),
                                  "sha256": digest(target.read_bytes()), "role": role})
    manifest["files"].append({"path": original.relative_to(ROOT).as_posix(), "sha256": OLD_SHA, "role": "artifact"})
    manifest["checks"].extend(records)
    manifest["limitations"].append("首归档清单不覆盖；r02绑定配置、脚本及已关闭检查；最终动态核验输出留在隔离缓存，避免自引用。")
    save(new_path, manifest)
    print(json.dumps({"status": "SEALED_ARCHIVE_WRAPPER_ONLY", "bindings": len(manifest["files"]),
                      "manifest_sha256": digest(new_path.read_bytes()),
                      "checks_native": [record["exit_code"] for record in records]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
