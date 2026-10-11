"""逐项归档冻结的 BUSY 软件审查证据，只运行清单包装检查。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
WORK = ROOT / "tmp/2B/S2B-T20/busy_review_archive_20261011_r02"
RUN = "independent_busy_observer_review_20261011_r01"
OUT = ROOT / "report/evidence/S2B-T20" / RUN
PREFIX = "tmp/2B/S2B-T20/"
RAW_NAME = PREFIX + "independent_busy_observer_review_20261011_r04/raw_delivery_manifest.json"
RAW_SHA = "5f54b2fe2ac52e9187adea50c37feb7759726f18eae6480cc428757ce0dc8c5e"
RECEIPT_NAME = PREFIX + "independent_busy_observer_review_20261011_r04/review_receipt.json"
RECEIPT_SHA = "bc982e697b430cb75735668e13efd56bd41da2aff2d52474414a8519d956da3e"
REVIEW_HEAD = "90c87b773fe06684797f6bb3cca2da078a4d49aa"
CHECKER_SHA = "cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf"
G1 = {
    "r01": "8d8a8845a97fa3f45182ed025a63e869b2fcc5c7d673797d459438ed534308eb",
    "r02": "a330765173d78f72d1e0e3e03faa21b2c751777c9472e034b570dc14dc621cbd",
    "r03": "adbfceaebfc2856a9b21afe8fb031184bd245fdb7723d057e7635624247786b4",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_bytes(name: str, expected: str | None = None) -> tuple[Path, bytes]:
    """按原始名称核对完整路径、文件类型、边界和哈希。"""
    path = ROOT / name
    assert path.is_file() and not path.is_symlink(), name
    assert path.resolve().is_relative_to(ROOT.resolve()), name
    data = path.read_bytes()
    if expected is not None:
        assert sha(data) == expected, (name, sha(data), expected)
    return path, data


def write_new(path: Path, data: bytes) -> None:
    """仅创建本轮明确目录内的新文件，拒绝覆盖已有运行。"""
    assert path.is_relative_to(OUT) or path.is_relative_to(WORK), path
    assert not path.exists(), path
    assert path.parent.resolve().is_relative_to(ROOT.resolve()), path
    path.parent.mkdir(parents=True, exist_ok=True)
    assert path.parent.is_dir() and not path.parent.is_symlink(), path
    with path.open("xb") as handle:
        handle.write(data)


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def json_new(path: Path, value: object) -> None:
    write_new(path, encoded(value))


def command_record(checker: Path, manifest: Path, mode: str, prefix: str) -> dict:
    """采集只读检查器的原生退出码及原始标准输出，不修改检查状态。"""
    argv = [sys.executable, "-B", str(checker), "--mode", mode, "--manifest", str(manifest)]
    before = manifest.read_bytes()
    started = time.perf_counter()
    completed = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=30,
                               env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    record = {
        "mode": mode,
        "command_argv": argv,
        "cwd": str(ROOT),
        "native_exit_code": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "manifest_sha256_at_execution": sha(before),
        "elapsed_seconds": time.perf_counter() - started,
        "stdout_path": relative(WORK / f"{prefix}_{mode}_stdout.log"),
        "stderr_path": relative(WORK / f"{prefix}_{mode}_stderr.log"),
        "hardware_calls": 0,
    }
    for stream, content in [("stdout", completed.stdout), ("stderr", completed.stderr)]:
        write_new(WORK / f"{prefix}_{mode}_{stream}.log", content)
        record[f"{stream}_sha256"] = sha(content)
    json_new(WORK / f"{prefix}_{mode}_native.json", record)
    assert manifest.read_bytes() == before, "只读检查不能改变清单。"
    assert completed.returncode == (0 if mode == "evidence" else 2), record
    return record


def main() -> None:
    started = time.perf_counter()
    assert ROOT.is_dir() and WORK.is_dir() and OUT.parent.is_dir()
    assert not OUT.exists(), "正式 RunId 已存在，禁止覆盖。"
    observed_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    checker, checker_data = file_bytes("verification/check_stage_delivery.py", CHECKER_SHA)
    _, raw_data = file_bytes(RAW_NAME, RAW_SHA)
    raw = json.loads(raw_data)
    _, receipt_data = file_bytes(RECEIPT_NAME, RECEIPT_SHA)
    receipt = json.loads(receipt_data)
    assert raw["status"] == receipt["status"] == "PASS_SOFTWARE_G2_ONLY"
    assert raw["source_commit"] == receipt["source_commit"] == REVIEW_HEAD
    assert len(raw["files"]) == 118
    assert receipt["counts"] == {
        "frozen_regression_tests": 68, "independent_native_cases": 50,
        "public_and_plan_checks": 18, "selected_raw_reruns": 6,
        "developer_file_bindings": 99, "dependency_source_bindings": 8,
    }
    allowed = tuple(PREFIX + f"independent_busy_observer_review_20261011_r{n:02d}/" for n in range(1, 5))
    planned = []
    raw_seen = set()
    for entry in raw["files"] + [{"path": RAW_NAME, "sha256": RAW_SHA, "role": "result"}]:
        name = entry["path"]
        assert name.startswith(allowed) and name not in raw_seen, name
        raw_seen.add(name)
        source, content = file_bytes(name, entry["sha256"])
        dest = OUT / "raw" / name[len(PREFIX):]
        planned.append((entry, source, dest, content))
    assert len(planned) == 119 and sum(len(item[3]) for item in planned) == 28749458
    assert RECEIPT_NAME in raw_seen
    sources = receipt["dependency_source_sha256"]
    assert len(sources) == 8
    source_data = {}
    for name, expected in sources.items():
        source_data[name] = file_bytes(name, expected)
    assert sources["verification/s2b_csr_busy_observer.py"] == "de15f04086f025de2786ebdb08d2c913b1a88073dcaadd4a0f3057f39d9dd3f2"
    assert sources["verification/test_s2b_csr_busy_observer.py"] == "13d33dbbe33986ef0e8d1dc90587552b50504fb9734a6b34b95ed12a82fdcc12"
    bindings = []
    external = {}
    g1_counts = {}
    g1_objects = {}
    for group, expected in G1.items():
        name = f"report/evidence/S2B-T20/busy_observer_20261011_{group}/delivery_manifest.json"
        manifest_path, data = file_bytes(name, expected)
        obj = json.loads(data)
        g1_objects[group] = obj
        owned = set()
        for entry in obj["files"] + [{"path": name, "sha256": expected, "role": "input"}]:
            path, content = file_bytes(entry["path"], entry["sha256"])
            bindings.append({"group": group, "path": entry["path"], "sha256": entry["sha256"],
                             "bytes": len(content), "original_role": entry["role"], "status": "HASH_BOUND"})
            inside = path.is_relative_to(manifest_path.parent)
            if inside:
                owned.add(path)
            role = "input" if inside else entry["role"]
            assert role in {"input", "source"}, entry
            prior = external.get(entry["path"])
            normalized = {"path": entry["path"], "sha256": entry["sha256"], "role": role}
            assert prior is None or prior == normalized, entry
            external[entry["path"]] = normalized
        discovered = set()
        for directory, subdirs, filenames in os.walk(manifest_path.parent):
            assert not any((Path(directory) / item).is_symlink() for item in subdirs)
            for filename in filenames:
                discovered.add(Path(directory) / filename)
                assert len(discovered) <= 150, "当前 G1 目录有界枚举超限。"
        assert discovered == owned, (group, discovered - owned, owned - discovered)
        g1_counts[group] = {"listed": len(obj["files"]), "owned_including_manifest": len(owned),
                            "manifest_sha256": expected, "original_source_commit": obj["source_commit"]}
    assert sum(item["listed"] for item in g1_counts.values()) == 99
    assert len(bindings) == 102 and len(external) == 102
    for name, expected in sources.items():
        assert external[name] == {"path": name, "sha256": expected, "role": "source"}
    # 仅归档清单列明原件；排除的五十场景原始目录不枚举、不复制、不删除。
    OUT.mkdir()
    roles = {}
    mapping = []
    for entry, source, dest, content in planned:
        write_new(dest, content)
        assert dest.read_bytes() == content
        roles[relative(dest)] = entry["role"]
        mapping.append({"original_path": entry["path"], "archived_path": relative(dest),
                        "sha256": entry["sha256"], "bytes": len(content), "role": entry["role"],
                        "method": "原字节逐项复制，保留原件内部路径与历史状态。"})
    source_mapping = []
    for name, (path, content) in source_data.items():
        dest = OUT / "actual_source_snapshot" / path.name
        write_new(dest, content)
        roles[relative(dest)] = "source"
        source_mapping.append({"original_path": name, "snapshot_path": relative(dest),
                               "sha256": sha(content), "bytes": len(content),
                               "captured_head": observed_head, "reviewer_head": REVIEW_HEAD})
    script = Path(__file__).read_bytes()
    write_new(OUT / "archive_busy_review.py", script)
    roles[relative(OUT / "archive_busy_review.py")] = "source"
    json_new(OUT / "raw_copy_mapping.json", {"schema_version": 1, "listed_count": 118,
             "copied_including_manifest": 119, "copied_bytes": 28749458, "files": mapping,
             "omitted_retained_local": raw["omitted_retained_local"],
             "scope": "只复制冻结 raw 清单列明的全部文件及清单本身。"})
    json_new(OUT / "g1_dependency_bindings.json", {"schema_version": 1, "groups": g1_counts,
             "developer_listed_file_count": 99, "bindings_including_three_manifests": bindings,
             "historical_r01_source": {"contemporaneous_capture": False,
              "provenance_path": "report/evidence/S2B-T20/busy_observer_20261011_r01/execution.json",
              "method": "Developer 由 r02 快照和精确编辑反向重建；原件说明与 SHA 保留。",
              "live_source_binding": "旧 r01/r02 源只绑定各自 source_snapshot，不错误绑定当前 live 源。"}})
    json_new(OUT / "actual_source_mapping.json", {"schema_version": 1, "files": source_mapping,
             "observed_collection_head": observed_head, "reviewer_original_head": REVIEW_HEAD,
             "dependency_count_including_two_new_sources": 8})
    limitations = list(receipt["limitations"]) + [
        "Collector 仅复制与封装已有软件 G2；不复审、不重跑测试、不操作实物。",
        "归档记录采集时实际 HEAD；原 Reviewer/G1 原件保留当时 source_commit，不改写旧版本。",
        "r01 开发源是明示反向补丁重建件，首轮执行 HEAD 未独立采集，不能冒充执行前快照。",
        "Reviewer r01 的五十场景完整批量 raw 只留原 tmp；本次仅复制冻结的 118 项及清单自身。",
        "公开负向仅重定向输出 ROOT 到隔离 tmp，所有生产 gate 为原实现；真实公开正向批准仍 NOT_RUN。",
        "现有接口 frozen=false；inputs 实际 FAIL/2，不代表 G0/G3/G4/G5。",
        "Collector 峰值内存和全部工具调用量未测；Reviewer 原九次进程耗时与 RSS 仅引用原件。",
        "归档中的原始 Windows 日志保留原编码字节；新增 JSON 与脚本均为 UTF-8。",
    ]
    checks = []
    for index, execution in enumerate(receipt["executions"], 1):
        checks.append({"name": f"冻结 Reviewer 原生命令 {index}：{execution['purpose']}",
                       "status": execution["status"],
                       "command": subprocess.list2cmdline(execution["command"]),
                       "exit_code": execution["exit_code"],
                       "reason": "引用冻结回执与 raw 原件，Collector 未重测。"})
    checks.extend([
        {"name": "公开入口真实正向准入", "status": "NOT_RUN", "command": None,
         "exit_code": None, "reason": receipt["public_positive_hardware_admission"]["reason"]},
        {"name": "BOARD/G3", "status": "NOT_RUN", "command": None, "exit_code": None,
         "reason": "本轮仅软件证据归档，硬件调用为零。"},
        {"name": "G4/G5", "status": "BLOCKED", "command": None, "exit_code": None,
         "reason": "真实板上与冻结接口准入缺失，软件 G2 不能替代。"},
    ])
    json_new(OUT / "archive_audit.json", {"schema_version": 1, "status": "PASS_ARCHIVE_BYTE_BINDINGS",
             "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
             "observed_collection_head": observed_head, "reviewer_original_head": REVIEW_HEAD,
             "raw_manifest_sha256": RAW_SHA, "review_receipt_sha256": RECEIPT_SHA,
             "checker_sha256": sha(checker_data), "archive_copy_count": 119,
             "archive_copy_bytes": 28749458, "g1_groups": g1_counts,
             "current_dependency_sha256": sources, "software_g2": receipt["G2"],
             "coverage_counts": receipt["counts"], "reviewer_resources": receipt["resources"],
             "hardware_calls": 0, "tests_rerun": 0, "ross_calls": 0,
             "elapsed_before_packaging_seconds": time.perf_counter() - started,
             "collector_peak_rss_bytes": None, "limitations": limitations})
    # 字节数只写入独立 inventory，阶段清单 files 保持规定的三个字段。
    initial_inventory = [{"path": relative(path), "sha256": sha(path.read_bytes()),
                          "bytes": path.stat().st_size}
                         for path in sorted(OUT.rglob("*")) if path.is_file()]
    json_new(OUT / "archive_inventory.json", {"schema_version": 1, "files": initial_inventory,
             "scope": "归档副本、源码快照和包装元数据；排除自身及后续包装检查产物，避免循环哈希。"})

    def manifest() -> dict:
        items = dict(external)
        for path in sorted(OUT.rglob("*")):
            if path.is_file() and path.name != "delivery_manifest.json":
                name = relative(path)
                items[name] = {"path": name, "sha256": sha(path.read_bytes()),
                               "role": roles.get(name, "log" if path.suffix == ".log" else "result")}
        return {"schema_version": 1, "stage": "2B", "task_id": "S2B-T20", "run_id": RUN,
                "source_commit": observed_head, "evidence_dir": relative(OUT),
                "interfaces": g1_objects["r03"]["interfaces"],
                "files": sorted(items.values(), key=lambda item: item["path"]),
                "checks": list(checks),
                "tool_versions": {"Python": platform.python_version(),
                 "Git": subprocess.check_output(["git", "--version"], cwd=ROOT, text=True).strip(),
                 "archive": "Python 标准库逐字节复制及 SHA-256；包装检查器只读。"},
                "limitations": limitations}

    manifest_path = OUT / "delivery_manifest.json"
    json_new(manifest_path, manifest())
    preliminary = manifest_path.read_bytes()
    preliminary_records = [command_record(checker, manifest_path, mode, "precheck")
                           for mode in ["evidence", "inputs"]]
    write_new(OUT / "delivery_manifest_before_archive_checks.json", preliminary)
    for record in preliminary_records:
        mode = record["mode"]
        for stream in ["stdout", "stderr"]:
            _, data = file_bytes(record[f"{stream}_path"], record[f"{stream}_sha256"])
            write_new(OUT / f"archive_{mode}_{stream}.log", data)
        checks.append({"name": f"归档初检 {mode}", "status": record["status"],
                       "command": subprocess.list2cmdline(record["command_argv"]),
                       "exit_code": record["native_exit_code"],
                       "reason": "被检查清单原字节保存在 delivery_manifest_before_archive_checks.json；inputs FAIL/2 如实保留。"})
    json_new(OUT / "packaging_checks.json", {"schema_version": 1, "checks": preliminary_records,
             "hardware_calls": 0, "tests_rerun": 0})
    assert manifest_path.is_file() and manifest_path.read_bytes() == preliminary
    manifest_path.write_bytes(encoded(manifest()))
    final_hash = sha(manifest_path.read_bytes())
    final_records = [command_record(checker, manifest_path, mode, "final")
                     for mode in ["evidence", "inputs"]]
    for entry, source, dest, content in planned:
        file_bytes(entry["path"], entry["sha256"])
        assert dest.read_bytes() == content
    for name, expected in sources.items():
        file_bytes(name, expected)
    for name, entry in external.items():
        file_bytes(name, entry["sha256"])
    assert sha(manifest_path.read_bytes()) == final_hash
    final_files = [{"path": relative(path), "sha256": sha(path.read_bytes()),
                    "bytes": path.stat().st_size}
                   for path in sorted(OUT.rglob("*")) if path.is_file()]
    # 最终封闭索引与检查记录留在工作目录，避免清单哈希自引用。
    result = {"schema_version": 1, "status": "PASS_ARCHIVE_ONLY", "formal_dir": relative(OUT),
              "formal_files": final_files, "formal_file_count": len(final_files),
              "formal_bytes": sum(item["bytes"] for item in final_files),
              "manifest_sha256": final_hash, "observed_collection_head": observed_head,
              "reviewer_original_head": REVIEW_HEAD, "final_checks": final_records,
              "elapsed_seconds": time.perf_counter() - started,
              "hardware_calls": 0, "tests_rerun": 0, "git_mutations": 0,
              "collector_peak_rss_bytes": None, "limitations": limitations}
    json_new(WORK / "archive_result.json", result)
    json_new(WORK / "formal_files.json", {"files": final_files})
    print(json.dumps({key: result[key] for key in ["status", "formal_dir", "formal_file_count",
          "formal_bytes", "manifest_sha256", "observed_collection_head", "reviewer_original_head",
          "elapsed_seconds"]}, ensure_ascii=False))
    print(json.dumps({"native_checks": [(r["mode"], r["native_exit_code"], r["status"])
                      for r in final_records]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
