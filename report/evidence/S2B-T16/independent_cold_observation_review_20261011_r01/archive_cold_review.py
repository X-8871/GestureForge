"""按冻结清单归档独立审查原件；不重跑测试，不操作设备。"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone


ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
RUN = "independent_cold_observation_review_20261011_r01"
OUT = ROOT / "report/evidence/S2B-T16" / RUN
WORK = ROOT / "tmp/2B/S2B-T16/cold_review_archive_20261011_r01"
HEAD = "90c87b773fe06684797f6bb3cca2da078a4d49aa"
BASE = "6d3fd8567b579a51d4042667d47af7d94f2f5a97"
PREFIX = "tmp/2B/S2B-T16/independent_cold_observation_review_20261011_"
RAW = {
    "r1": (PREFIX + "r01/raw_delivery_manifest.json", "1081745f33a56038a821d7a12c5e661387b415a978c0c11851c5bf9b5b67253a", 45),
    "r2": (PREFIX + "r03/raw_delivery_manifest.json", "3810537c791bf4e52d106913591c116c8ec520c05cae38bb6cf5fbd646493758", 117),
}
G1 = {
    "r1": ("report/evidence/S2B-T16/cold_observation_20261011_r01/delivery_manifest.json", "b6122a97f7a3594b9524e1e45cdeb9a0afe25c67034aa51d441e30bac997d827"),
    "r2": ("report/evidence/S2B-T16/cold_observation_20261011_r02/delivery_manifest.json", "f69b69e711259afc6de4fc033a0845a71ba86468b51f99a84a995a6ffb223ce4"),
}
CURRENT = {
    "verification/s2b_board_jtag.py": "1ce01c810715e6c20f2952d3488ebb6ce8f7792861075e1a25bbc1f91db7651b",
    "verification/test_s2b_board_jtag.py": "c35a08dce67c761596d36296c0abb89c08fcb98f9bfde46160f6e6cfa1a30c3f",
    "verification/test_s2b_cold_observation.py": "ce1af9db23fcd6a07c2c31df0b3c1f9186aaf1f756e34af68d2323f5cb0a38f1",
    "vitis/run_s2b_visibility_probe.py": "bc9c94b0d49769ea08941d0cda252038c2b5390f342439d960dcede690c52aa2",
    "verification/test_s2b_visibility_probe.py": "84d04910efc9e4f051c6439550349a21910c0a77d22720f5afed3e2a998b7e4d",
}
OLD = {
    "verification/s2b_board_jtag.py": "b48533d9ea42eb779e7db55816539efc2a15a9249595b754f67d28394bcf59cf",
    "verification/test_s2b_board_jtag.py": "35af463f87c1d1323bb10672b4e913bef940162b1de8ac10a40a10c9e9d8eeba",
    "verification/test_s2b_cold_observation.py": "f892158d264f926589389ce2465a7e00f4e7cd49b8a05d2df15792bb59aca786",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def checked_file(name: str, expected: str | None = None) -> tuple[Path, bytes]:
    """核验完整名称、路径类型、仓库边界与可选哈希。"""
    path = ROOT / name
    assert path.is_file() and not path.is_symlink(), name
    assert path.resolve().is_relative_to(ROOT.resolve()), name
    data = path.read_bytes()
    if expected is not None:
        assert sha(data) == expected, (name, sha(data), expected)
    return path, data


def write_new(path: Path, data: bytes) -> None:
    assert path.is_relative_to(OUT) or path.is_relative_to(WORK), path
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def json_new(path: Path, value: object) -> None:
    write_new(path, json_bytes(value))


def main() -> None:
    started = time.perf_counter()
    assert ROOT.is_dir() and OUT.parent.is_dir() and WORK.is_dir()
    assert not OUT.exists(), "RunId 已存在，禁止覆盖运行。"
    observed_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert observed_head == HEAD, observed_head
    for name, expected in CURRENT.items():
        checked_file(name, expected)
    checker, checker_bytes = checked_file("verification/check_stage_delivery.py", "cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf")
    planned = []
    group_counts = {}
    raw_data = {}
    for group, (name, expected, count) in RAW.items():
        _, data = checked_file(name, expected)
        manifest = json.loads(data)
        raw_data[group] = manifest
        assert len(manifest["files"]) == count
        entries = list(manifest["files"]) + [{"path": name, "sha256": expected, "role": "result"}]
        seen = set()
        total_bytes = 0
        for index, entry in enumerate(entries, 1):
            source = entry["path"]
            allowed_runs = [PREFIX + "r01/"] if group == "r1" else [PREFIX + "r02/", PREFIX + "r03/"]
            assert any(source.startswith(prefix) for prefix in allowed_runs), source
            assert "scratch" not in Path(source).parts and source not in seen, source
            seen.add(source)
            source_path, content = checked_file(source, entry["sha256"])
            basename = source_path.name
            stable_name = basename if basename in {"review_receipt.json", "raw_delivery_manifest.json"} else f"{index:04d}_{basename}"
            dest = OUT / "raw" / group / stable_name
            planned.append((group, entry, source_path, dest, content))
            total_bytes += len(content)
        group_counts[group] = {"listed": count, "including_manifest": len(entries), "bytes": total_bytes}
    assert group_counts["r2"]["bytes"] == 1804218
    for group, expected in [("r1", "e5ea9e4b9c86c0207a103ed0ac6d42270acf1e7351bf0a67fbd3f2705d910d77"), ("r2", "64eb9b5104ec2da4c4e8c212eab2a3ce7805e9fb71cfe6aacff9d7edabc0336a")]:
        receipt = [item for item in planned if item[0] == group and item[2].name == "review_receipt.json"]
        assert len(receipt) == 1 and sha(receipt[0][4]) == expected
    dependencies = []
    external_bindings = {}
    g1_counts = {}
    for group, (name, expected) in G1.items():
        manifest_path, data = checked_file(name, expected)
        manifest = json.loads(data)
        entries = list(manifest["files"]) + [{"path": name, "sha256": expected, "role": "input"}]
        owned = set()
        for entry in entries:
            path, content = checked_file(entry["path"])
            actual = sha(content)
            record = {"group": group, "original_path": entry["path"], "original_role": entry["role"], "declared_sha256": entry["sha256"], "observed_sha256": actual, "observed_bytes": len(content)}
            if group == "r1" and entry["path"] in OLD:
                assert entry["sha256"] == OLD[entry["path"]] and actual == CURRENT[entry["path"]]
                record["status"] = "HISTORICAL_SOURCE_SUPERSEDED"
                record["reason"] = "旧 G1 未保存源码快照；当前 R2 原件不能按历史 SHA 绑定。生产源仅由 Reviewer 事后精确重建；两个旧测试源原件缺失。"
            else:
                assert actual == entry["sha256"], record
                role = "input" if path.is_relative_to(manifest_path.parent) else entry["role"]
                assert role in {"input", "source"}, record
                external_bindings[entry["path"]] = {"path": entry["path"], "sha256": actual, "role": role}
                record["status"] = "HASH_BOUND"
            if path.is_relative_to(manifest_path.parent):
                owned.add(path)
            dependencies.append(record)
        discovered = set()
        for directory, subdirs, filenames in os.walk(manifest_path.parent):
            assert "scratch" not in subdirs
            for filename in filenames:
                discovered.add(Path(directory) / filename)
                assert len(discovered) <= 200, "G1 有界枚举超限。"
        assert discovered == owned, (group, discovered - owned, owned - discovered)
        g1_counts[group] = {"internal_files_including_manifest": len(owned), "listed_total": len(entries) - 1, "historical_superseded_sources": 3 if group == "r1" else 0}
    for name, expected in CURRENT.items():
        external_bindings[name] = {"path": name, "sha256": expected, "role": "source"}
    OUT.mkdir()
    mapping = []
    roles = {}
    for group, entry, source, dest, content in planned:
        write_new(dest, content)
        assert dest.read_bytes() == content
        roles[relative(dest)] = entry["role"]
        mapping.append({"group": group, "original_path": entry["path"], "archived_path": relative(dest), "sha256": entry["sha256"], "bytes": len(content), "original_role": entry["role"], "archive_method": "逐字节复制；原路径仅作为来源，不改写原件内部路径"})
    reconstruction = next(item for item in mapping if item["original_path"].endswith("/reconstructed_r1_s2b_board_jtag.py"))
    assert reconstruction["sha256"] == OLD["verification/s2b_board_jtag.py"]
    script_bytes = Path(__file__).read_bytes()
    write_new(OUT / "archive_cold_review.py", script_bytes)
    roles[relative(OUT / "archive_cold_review.py")] = "source"
    json_new(OUT / "archive_mapping.json", {"schema_version": 1, "scope": "Reviewer 冻结 raw 清单全部文件与清单自身；不枚举 scratch", "groups": group_counts, "files": mapping})
    json_new(OUT / "g1_dependency_bindings.json", {"schema_version": 1, "groups": g1_counts, "bindings": dependencies, "historical_reconstruction": {**reconstruction, "contemporaneous_capture": False, "method": "Reviewer 从 R2 生产源原字节移除唯一新增完整位覆盖断言，恢复 R1 已冻结 SHA。Collector 仅复制该重建文件。", "missing_original_test_sources": list(OLD)[1:]}})
    r2_receipt = json.loads((OUT / "raw/r2/review_receipt.json").read_text(encoding="utf-8"))
    limitations = [
        "仅归档 PASS_SOFTWARE_G2_ONLY；原 R1 CHANGES_REQUIRED 与 R2 bootstrap 失败原件保持不变。",
        "旧 R1 G1 清单的三个历史 live 源 SHA 已被 R2 替代，不声称当前目录仍满足旧源码绑定。",
        "R1 生产源是 Reviewer 事后精确重建，非当时捕获；两个历史测试源原字节副本缺失。",
        "R1 Reviewer 713 个 scratch 文件按任务卡排除，Collector 未扫描或改动；R2 全部 scratch 亦排除。",
        "归档保留原件内的旧路径和历史状态；archive_mapping.json 给出当前永久副本，原 raw 清单不当作新 wrapper。",
        "实际 runtime 兼容、cache、BOARD/G3 未批准；cold_lifecycle_proven 仍未证明，不批准 visibility1 或完整 2B。",
        "hardware_calls=0；Collector 未导入 SDK、连接串口或 JTAG、调用 ROSS、重跑软件测试或修改业务源码。",
        "独立 R2 152 方法、431 subtests、97.593 秒和 235020288 字节峰值均引用冻结 Reviewer 回执，不是 Collector 重测。",
        "Collector 峰值内存与完整工具调用量未测；只记录本归档及包装检查实际耗时。",
        "最终 wrapper 检查只证明包装绑定，inputs 的真实 FAIL/2 保留，不代表 G0/G3/G4/G5。",
    ]
    checks = [
        {"name": "历史 R1 独立软件审查", "status": "FAIL", "command": "python -B " + PREFIX + "r01/run_review.py", "exit_code": 1, "reason": "原 P1 缺失 metadata 接受及 T19 pin 拒绝原件保留；P1 关闭依据是新的 R2 回执。"},
        {"name": "历史 R2 Reviewer bootstrap", "status": "FAIL", "command": "python -B " + PREFIX + "r02/run_review.py", "exit_code": 1, "reason": "历史源码提取失败，git 原生 128；测试未运行，原 bootstrap 原件保留。"},
        {"name": "R2 独立软件 G2", "status": "PASS", "command": "python -B " + PREFIX + "r03/run_review.py", "exit_code": 0, "reason": "冻结回执 PASS_SOFTWARE_G2_ONLY；152 方法与 431 subtests，0 failure/0 error。"},
        {"name": "实际 runtime 与 cache", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "完整实际平台兼容与实板批准尚未取得。"},
        {"name": "BOARD/G3", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本轮只有软件审查及证据归档，硬件调用为零。"},
    ]
    json_new(OUT / "archive_audit.json", {"schema_version": 1, "status": "PASS_ARCHIVE_BYTE_BINDINGS", "source_baseline": BASE, "observed_head": observed_head, "archived_review_result": r2_receipt["status"], "reviewer_groups": group_counts, "g1_groups": g1_counts, "current_source_sha256": CURRENT, "checker_sha256": sha(checker_bytes), "archive_copy_count": len(mapping), "archive_copy_bytes": sum(item["bytes"] for item in mapping), "software_g2": {"tests_run": r2_receipt["test_results"]["tests_run"], "subtests": sum(r2_receipt["test_results"]["subtest_result_groups"].values()), "elapsed_seconds": r2_receipt["elapsed_seconds"], "resource": r2_receipt["resource"]}, "hardware_calls": 0, "copied_originals_revalidated": True, "elapsed_before_packaging_seconds": time.perf_counter() - started, "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "limitations": limitations})

    def manifest() -> dict:
        """包装 files 仅含路径、哈希和角色，字节数留在独立映射中。"""
        items = dict(external_bindings)
        for path in sorted(OUT.rglob("*")):
            if path.is_file() and path != OUT / "delivery_manifest.json":
                name = relative(path)
                items[name] = {"path": name, "sha256": sha(path.read_bytes()), "role": roles.get(name, "log" if path.suffix == ".log" else "result")}
        return {"schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN, "source_commit": HEAD, "evidence_dir": relative(OUT), "interfaces": raw_data["r2"]["interfaces"], "files": sorted(items.values(), key=lambda item: item["path"]), "checks": list(checks), "tool_versions": {"Python": platform.python_version(), "Git": subprocess.check_output(["git", "--version"], cwd=ROOT, text=True).strip(), "archive": "Python 标准库逐字节复制及 SHA-256，未调用 SDK"}, "limitations": limitations}

    manifest_path = OUT / "delivery_manifest.json"
    json_new(manifest_path, manifest())
    preliminary = manifest_path.read_bytes()
    checker_runs = []
    for mode in ["evidence", "inputs"]:
        args = [sys.executable, "-B", str(checker), "--mode", mode, "--manifest", str(manifest_path)]
        run_started = time.perf_counter()
        completed = subprocess.run(args, cwd=ROOT, capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        record = {"mode": mode, "command_argv": args, "native_exit_code": completed.returncode, "status": "PASS" if completed.returncode == 0 else "FAIL", "manifest_sha256_at_execution": sha(preliminary), "elapsed_seconds": time.perf_counter() - run_started}
        checker_runs.append(record)
        # 首次包装日志先保存在工作目录，避免第二项检查看到未列出的新增文件。
        write_new(WORK / f"precheck_{mode}_stdout.log", completed.stdout)
        write_new(WORK / f"precheck_{mode}_stderr.log", completed.stderr)
        assert completed.returncode == (0 if mode == "evidence" else 2), record
    write_new(OUT / "delivery_manifest_before_archive_checks.json", preliminary)
    for record in checker_runs:
        mode = record["mode"]
        for stream in ["stdout", "stderr"]:
            write_new(OUT / f"archive_{mode}_{stream}.log", (WORK / f"precheck_{mode}_{stream}.log").read_bytes())
        checks.append({"name": f"归档初检 {mode}", "status": record["status"], "command": subprocess.list2cmdline(record["command_argv"]), "exit_code": record["native_exit_code"], "reason": "检查时清单原字节保存在 delivery_manifest_before_archive_checks.json；inputs 的真实 FAIL 不转写为 PASS。"})
    json_new(OUT / "packaging_checks.json", {"schema_version": 1, "checks": checker_runs, "hardware_calls": 0})
    assert manifest_path.is_file() and manifest_path.read_bytes() == preliminary
    manifest_path.write_bytes(json_bytes(manifest()))
    final_hash = sha(manifest_path.read_bytes())
    final_runs = []
    for mode in ["evidence", "inputs"]:
        args = [sys.executable, "-B", str(checker), "--mode", mode, "--manifest", str(manifest_path)]
        run_started = time.perf_counter()
        completed = subprocess.run(args, cwd=ROOT, capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        write_new(WORK / f"final_{mode}_stdout.log", completed.stdout)
        write_new(WORK / f"final_{mode}_stderr.log", completed.stderr)
        final_runs.append({"mode": mode, "command_argv": args, "native_exit_code": completed.returncode, "status": "PASS" if completed.returncode == 0 else "FAIL", "manifest_sha256": final_hash, "elapsed_seconds": time.perf_counter() - run_started})
        assert completed.returncode == (0 if mode == "evidence" else 2), final_runs[-1]
    for _, entry, _, dest, content in planned:
        checked_file(entry["path"], entry["sha256"])
        assert dest.read_bytes() == content
    for name, expected in CURRENT.items():
        checked_file(name, expected)
    assert sha(manifest_path.read_bytes()) == final_hash
    final_files = [{"path": relative(path), "sha256": sha(path.read_bytes()), "bytes": path.stat().st_size} for path in sorted(OUT.rglob("*")) if path.is_file()]
    summary = {"status": "PASS_ARCHIVE_ONLY", "delivery_manifest": relative(manifest_path), "delivery_manifest_sha256": final_hash, "formal_file_count": len(final_files), "formal_bytes": sum(item["bytes"] for item in final_files), "reviewer_groups": group_counts, "g1_groups": g1_counts, "final_checks": final_runs, "formal_files": final_files, "elapsed_seconds": time.perf_counter() - started, "hardware_calls": 0, "git_commit": "由 root 统一提交，Collector 未暂存或提交。"}
    json_new(WORK / "collector_receipt.json", summary)
    print(json.dumps({key: value for key, value in summary.items() if key != "formal_files"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
