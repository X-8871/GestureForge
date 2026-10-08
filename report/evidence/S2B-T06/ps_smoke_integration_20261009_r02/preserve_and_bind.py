"""保全初次包装失败原件，按项目已有清单格式保存集成实验。"""

from pathlib import Path
import hashlib
import json
import platform
import subprocess
import time


def sha(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")


def main():
    root = Path.cwd()
    run = Path(__file__).parent
    old = root / "report/evidence/S2B-T06/ps_smoke_integration_20261009_r01"
    assert run == root / "report/evidence/S2B-T06/ps_smoke_integration_20261009_r02"
    assert run.is_dir() and not run.is_symlink() and old.is_dir()
    assert sha(old / "delivery_manifest.json") == "1562641aba6afc413c444477f5a652e2ee5babd17bdb9dd78b87d65867699034"
    original = json.loads((old / "delivery_manifest.json").read_text(encoding="utf-8"))
    for item in original["files"]:
        assert sha(root / item["path"]) == item["sha256"], item["path"]
    pairs = [(path, "historical_r01/" + path.relative_to(old).as_posix())
             for path in sorted(old.rglob("*")) if path.is_file()]
    for name in ["integration_packaging_r01.json", "integration_packaging_inputs_r01.log",
                 "integration_packaging_evidence_r01.log", "verify_final_index.py"]:
        pairs.append((root / "tmp/2B/S2B-T06" / name, "packaging_failure/" + name))
    for source, _ in pairs:
        assert source.is_file() and not source.is_symlink()
    mapping = []
    started = time.perf_counter()
    for source, relative in pairs:
        target = run / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists() and not target.parent.is_symlink()
        content = source.read_bytes()
        with target.open("xb") as output:
            output.write(content)
        assert target.read_bytes() == content
        mapping.append({"source": str(source), "destination": target.relative_to(root).as_posix(),
                        "bytes": len(content), "sha256": sha(target)})
    failed = json.loads((run / "packaging_failure/integration_packaging_r01.json").read_text(encoding="utf-8"))
    assert [item["exit_code"] for item in failed] == [2, 2]
    assert all(item["result"]["status"] == "CHECKS_FAILED" for item in failed)
    assert len(failed[0]["result"]["errors"]) == 76
    assert all("role 必须是" in error for error in failed[0]["result"]["errors"])
    assert len(failed[1]["result"]["errors"]) == 77
    origins = {}
    for name in ["ps_smoke_20261008_r01", "ps_smoke_offline_freeze_20261009_r01", old.name]:
        path = old.parent / name / "delivery_manifest.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        origins[name] = {"source_commit": value["source_commit"], "manifest_sha256": sha(path)}
    assert origins["ps_smoke_20261008_r01"]["source_commit"] == "90652b45ef31e763bd3e6f7527e2fd080ece61a8"
    assert original["source_commit"] == subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()
    save(run / "copy_mapping.json", {"files": mapping, "copied_files": len(mapping),
        "copied_bytes": sum(item["bytes"] for item in mapping), "elapsed_seconds": time.perf_counter() - started})
    save(run / "correction.json", {
        "previous_archive_manifest_sha256": sha(old / "delivery_manifest.json"),
        "original_packaging_exit_codes": [2, 2], "original_outer_exit_code": 1,
        "original_index_outer_exit_code": 1, "manifest_origins": origins,
        "correction": "r01的76个文件角色evidence不属于既有schema。新包使用已支持角色，旧manifest及两份完整失败日志均逐字节保留。私有index原脚本错误要求三个独立运行均用同一source_commit；改为核对各固定清单的真实来源及源码SHA，不改旧清单。",
        "original_outer_output": "包装外层tool返回曾被输出预算截断，保存实际可见tool返回；underlying两份完整JSON日志和退出码在原结果JSON保留，未补造未采集stderr。",
        "business_candidate_unchanged": True, "candidate_inputs_exit_code": 2,
        "hardware_execution": "NOT_RUN", "G3_G4_stage2B_G5": "NOT_PASSED",
    })
    files = []
    for path in sorted(run.rglob("*")):
        if not path.is_file():
            continue
        role = "log" if path.name.endswith(".log") else "result" if path.suffix == ".json" else "artifact"
        item = {"path": path.relative_to(root).as_posix(), "sha256": sha(path), "role": role}
        if path.suffix == ".gz":
            item["role"] = "diagnostic"
            item["keep_reason"] = "无损保存独立命令的完整原stdout，复核原始恢复字节与日志口径。"
        if path == Path(__file__):
            item["role"] = "source"
        files.append(item)
    for item in original["files"]:
        if not item["path"].startswith(old.relative_to(root).as_posix() + "/"):
            files.append(dict(item))
    files.append({"path": (old / "delivery_manifest.json").relative_to(root).as_posix(),
                  "sha256": sha(old / "delivery_manifest.json"), "role": "input"})
    manifest = {key: value for key, value in original.items() if key != "files"}
    manifest.update({"run_id": run.name, "evidence_dir": run.relative_to(root).as_posix(), "files": files,
                     "tool_versions": {"Python": platform.python_version(), "Git": subprocess.check_output(["git", "--version"], cwd=root).decode().strip()}})
    manifest["limitations"].append("r01清单schema失败，不具有通过包装的效力；r02只修复实验保存格式，软件离线G2及原实板输入阻断保持原结论。")
    save(run / "delivery_manifest.json", manifest)
    print(json.dumps({"status": "PRESERVED_AND_BOUND", "copied_files": len(mapping), "files": len(files),
                      "manifest_sha256": sha(run / "delivery_manifest.json"), "candidate_inputs_exit_code": 2,
                      "hardware_execution": "NOT_RUN"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
