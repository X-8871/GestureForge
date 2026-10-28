#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为固定的阶段4/5回放输入建立阶段6资格证据，不调用状态机。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

RUN_ID = "s6d_replay_qualification_20261029_r03"
RUN_REL = f"report/evidence/S6-D/{RUN_ID}"
W6_HEAD = "56004d3a766e99dd8aef4203bba418865556eef0"
W4_HEAD = "d7af1b7c1a479185e7a8b62774cd8ee1441d127e"
W5_HEAD = "2decd0dc2e2204ee60dceead4c30f091d039081d"
W4_CONTRACT_COMMIT = "4400bb89cba5a860d6baa9e976bb08f25606cf15"
W4_ROOT = Path(r"D:\codex-worktrees\w4")
W5_ROOT = Path(r"D:\codex-worktrees\w5")
W6_ROOT = Path(r"D:\codex-worktrees\w6")
MAIN_ROOT = Path(r"D:\FPGA_Competition")
W4_PACKAGE = "report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r04"
W4_FREEZE = "report/evidence/S4-CTRL/s4t27_replay_package_freeze_20261027_r01"
W5_FREEZE = "report/evidence/S5-T04/s5_freeze_20261027_r07"
W5_NO_HAND = "report/evidence/S5-T03/s5t03_stage4_frozen_replay_20261027_r04"
W5_POSITIVE = "report/evidence/S5-T03/s5t03_stage4_positive_replay_20261027_r01"
W4_FREEZE_SHA = "012f5ea4b6d21cf54b806ec46799bbff967ff41da24a47a52e09a4e9f019dfbd"
W4_CONTRACT_SHA = "7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return digest(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层不是对象：{path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(root: Path, *args: str) -> bytes:
    proc = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args],
                          capture_output=True, check=False)
    if proc.returncode:
        raise RuntimeError(f"git {args!r} 失败：{proc.stderr.decode('utf-8', 'replace')}")
    return proc.stdout


def git_text(root: Path, *args: str) -> str:
    return git(root, *args).decode("utf-8", "strict").strip()


def is_ancestor(root: Path, ancestor: str, revision: str) -> bool:
    proc = subprocess.run(["git", "--no-optional-locks", "-C", str(root), "merge-base",
                           "--is-ancestor", ancestor, revision], capture_output=True, check=False)
    if proc.returncode not in (0, 1):
        raise RuntimeError("无法只读复算冻结契约提交的祖先关系")
    return proc.returncode == 0


def run(command: list[str], cwd: Path, output: Path) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False)
    output.write_text(proc.stdout + proc.stderr, encoding="utf-8")
    return {"command": command, "cwd": str(cwd), "exit_code": proc.returncode,
            "output": f"{RUN_REL}/{output.name}", "output_sha256": file_sha(output)}


def check_record(name: str, result: dict[str, Any]) -> dict[str, Any]:
    exit_code = result["exit_code"]
    status = "PASS" if exit_code == 0 else "FAIL"
    command = subprocess.list2cmdline(result["command"])
    item = {"name": name, "status": status, "command": command, "exit_code": exit_code}
    if status == "FAIL":
        item["reason"] = f"命令真实退出码为{exit_code}；完整诊断见{result['output']}。"
    return item


def rows(path: Path) -> list[dict[str, Any]]:
    result = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not result or any(not isinstance(item, dict) for item in result):
        raise ValueError(f"JSONL 缺少有效对象记录：{path}")
    return result


def frozen_member(frozen_set: dict[str, Any], path: str) -> dict[str, Any]:
    matches = [item for item in frozen_set.get("members", [])
               if isinstance(item, dict) and item.get("path") == path]
    if len(matches) != 1:
        raise ValueError(f"冻结集成员不存在或不唯一：{path}")
    member = matches[0]
    data = (W5_ROOT / path).read_bytes()
    if digest(data) != member.get("sha256") or len(data) != member.get("bytes"):
        raise ValueError(f"阶段5冻结字节不匹配：{path}")
    return {"path": path, "sha256": digest(data), "bytes": len(data), "status": "PASS"}


def source_files() -> list[tuple[str, Path, str, str]]:
    return [
        ("w4", W4_ROOT / W4_FREEZE / "replay_package_freeze.json", "inputs/w4/replay_package_freeze.json", "阶段4回放冻结声明"),
        ("w4", W4_ROOT / W4_FREEZE / "manifest.json", "inputs/w4/freeze_manifest.json", "阶段4回放冻结清单"),
        ("w4", W4_ROOT / W4_PACKAGE / "task27_replay_result_package.json", "inputs/w4/task27_replay_result_package.json", "阶段4冻结NO_HAND回放结果包"),
        ("w4", W4_ROOT / "docs/stage4/s4b_shared_input_result_contract.json", "inputs/w4/s4b_shared_input_result_contract.json", "阶段4共享契约s4-shared-io/1.3.0 r07"),
        ("w5", W5_ROOT / W5_FREEZE / "frozen_set.json", "inputs/w5/frozen_set.json", "阶段5离线冻结集定义"),
        ("w5", W5_ROOT / W5_FREEZE / "delivery_manifest.json", "inputs/w5/freeze_delivery_manifest.json", "阶段5离线冻结清单"),
        ("w5", W5_ROOT / W5_NO_HAND / "frames.jsonl", "inputs/w5/no_hand_frames.jsonl", "阶段5冻结NO_HAND回放帧"),
        ("w5", W5_ROOT / W5_POSITIVE / "manifest.json", "inputs/w5/positive_manifest.json", "阶段5冻结阳性回放清单"),
        ("w5", W5_ROOT / W5_POSITIVE / "frames.jsonl", "inputs/w5/positive_frames.jsonl", "阶段5冻结阳性fist回放帧"),
    ]


def refresh_delivery(run_dir: Path, delivery: dict[str, Any]) -> None:
    files = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_file() and path.name != "delivery_manifest.json":
            files.append({"path": path.relative_to(W6_ROOT).as_posix(),
                          "sha256": file_sha(path),
                          "role": "source" if path.suffix == ".py" else "log" if path.suffix == ".txt" else "result",
                          "keep_reason": "本次唯一RunId的来源副本、资格判定或真实验证输出",
                          "hash_basis": "worktree_disk"})
    delivery["files"] = files
    write_json(run_dir / "delivery_manifest.json", delivery)


def build() -> int:
    run_dir = W6_ROOT / RUN_REL
    if git_text(W6_ROOT, "rev-parse", "HEAD") != W6_HEAD:
        raise ValueError("w6 HEAD 已改变，停止以当前包冒充原固定基线")
    if git_text(W4_ROOT, "rev-parse", "HEAD") != W4_HEAD:
        raise ValueError("w4 HEAD 已改变，需重新核验阶段4冻结输入")
    if git_text(W5_ROOT, "rev-parse", "HEAD") != W5_HEAD:
        raise ValueError("w5 HEAD 已改变，需重新核验阶段5冻结输入")
    existing = [p.name for p in run_dir.iterdir() if p.name != "build_qualification.py"]
    if existing:
        raise ValueError(f"RunId已有输出，拒绝覆盖：{existing}")

    freeze_path = W4_ROOT / W4_FREEZE / "replay_package_freeze.json"
    freeze_manifest_path = W4_ROOT / W4_FREEZE / "manifest.json"
    contract_rel = "docs/stage4/s4b_shared_input_result_contract.json"
    contract_blob = git(W4_ROOT, "cat-file", "blob", f"{W4_CONTRACT_COMMIT}:{contract_rel}")
    freeze = read_json(freeze_path)
    freeze_manifest = read_json(freeze_manifest_path)
    contract = json.loads(contract_blob.decode("utf-8"))
    if file_sha(freeze_path) != W4_FREEZE_SHA or digest(contract_blob) != W4_CONTRACT_SHA:
        raise ValueError("阶段4冻结记录或固定提交中的共享契约字节与冻结版本不符")
    if not is_ancestor(W4_ROOT, W4_CONTRACT_COMMIT, W4_HEAD):
        raise ValueError("阶段4固定共享契约提交不在核验的w4 HEAD历史中")
    freeze_member = next((item for item in freeze_manifest.get("files", [])
                          if item.get("path") == "replay_package_freeze.json"), None)
    if freeze_manifest.get("verdict") != "FROZEN_REPLAY_ONLY" or not freeze_member:
        raise ValueError("阶段4冻结清单未证明 replay-only 冻结")
    if (freeze_member.get("sha256") != W4_FREEZE_SHA
            or freeze_member.get("bytes") != freeze_path.stat().st_size):
        raise ValueError("阶段4冻结记录字节与其清单绑定不符")
    freeze_record = contract.get("freeze_record") or {}
    if (contract.get("contract_version") != "1.3.0" or contract.get("revision") != "r07"
            or contract.get("status") != "FROZEN_OFFLINE_ONLY"
            or freeze_record.get("freeze_scope") != "OFFLINE_ONLY"):
        raise ValueError("阶段4契约冻结版本或范围不符")
    frozen_set_path = W5_ROOT / W5_FREEZE / "frozen_set.json"
    frozen_set = read_json(frozen_set_path)
    if frozen_set.get("freeze_kind") != "OFFLINE_SCOPE_FROZEN":
        raise ValueError("阶段5证据不属于离线范围冻结")
    nohand_rel = f"{W5_NO_HAND}/frames.jsonl"
    positive_rel = f"{W5_POSITIVE}/frames.jsonl"
    nohand_member = frozen_member(frozen_set, nohand_rel)
    positive_member = frozen_member(frozen_set, positive_rel)
    nohand = rows(W5_ROOT / nohand_rel)[0]
    positive = rows(W5_ROOT / positive_rel)[0]
    package = read_json(W4_ROOT / W4_PACKAGE / "task27_replay_result_package.json")
    marking = package.get("marking", {})
    if marking.get("replay_only") is not True or marking.get("evidence_kind") != "offline_replay":
        raise ValueError("阶段4结果包缺少 replay_only/offline_replay 来源标记")
    package_row = next((item for item in freeze.get("files", [])
                        if item.get("path") == "task27_replay_result_package.json"), None)
    package_bytes = (W4_ROOT / W4_PACKAGE / "task27_replay_result_package.json").read_bytes()
    if (package_row is None or digest(package_bytes) != package_row.get("sha256")
            or len(package_bytes) != package_row.get("bytes")):
        raise ValueError("阶段4NO_HAND结果包当前字节不再满足冻结记录")

    sys.path.insert(0, str(W6_ROOT))
    from verification.s6d_replay_preview_preflight import classify_frame

    nohand_gate = classify_frame(nohand, marking)
    positive_gate = classify_frame(positive, positive.get("marking", {}))
    for label, gate in (("NO_HAND", nohand_gate), ("positive", positive_gate)):
        if gate.get("status") != "BLOCKED" or gate.get("core_event_constructed") is not False \
                or gate.get("core_step_called") is not False:
            raise ValueError(f"{label}输入没有保持BLOCKED/核心NOT_RUN")

    core_blob = git(W6_ROOT, "cat-file", "blob", f"{W6_HEAD}:src/stage6/s6_core.py")
    params_blob = git(W6_ROOT, "cat-file", "blob", f"{W6_HEAD}:src/stage6/s6_params.py")
    gate_blob = (W6_ROOT / "verification/s6d_replay_preview_preflight.py").read_bytes()
    for rel, blob in (("src/stage6/s6_core.py", core_blob), ("src/stage6/s6_params.py", params_blob)):
        if (W6_ROOT / rel).read_bytes() != blob:
            raise ValueError(f"待绑定源码工作树字节偏离提交：{rel}")

    source_records = []
    input_files = []
    for owner, source, copy_rel, reason in source_files():
        target = run_dir / copy_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if owner == "w4" and source.as_posix().endswith("s4b_shared_input_result_contract.json"):
            source_bytes = contract_blob
            source_commit = W4_CONTRACT_COMMIT
            basis = "commit_blob"
        else:
            source_bytes = source.read_bytes()
            source_commit = W4_HEAD if owner == "w4" else W5_HEAD
            basis = "worktree_disk"
        target.write_bytes(source_bytes)
        if source_bytes != target.read_bytes():
            raise ValueError(f"上游只读输入副本不一致：{source}")
        row = {"owner": owner, "worktree": str(W4_ROOT if owner == "w4" else W5_ROOT),
               "commit": source_commit, "source_path": str(source),
               "copy_path": f"{RUN_REL}/{copy_rel}", "bytes": len(source_bytes),
               "sha256": digest(source_bytes), "hash_basis": basis, "status": "PASS"}
        source_records.append(row)
        input_files.append({"path": row["copy_path"], "sha256": row["sha256"], "role": "input",
                            "keep_reason": reason, "hash_basis": "worktree_disk"})

    commands: dict[str, Any] = {}
    build_command = [sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve())]
    build_output = run_dir / "build_invocation_output.txt"
    build_output.write_text("", encoding="utf-8")
    commands["build_qualification"] = {
        "command": build_command,
        "cwd": str(W6_ROOT),
        "exit_code": 0,
        "output": f"{RUN_REL}/build_invocation_output.txt",
        "output_sha256": file_sha(build_output),
    }
    commands["stage5_frozen_set"] = run(
        [sys.executable, "-B", "-X", "utf8", str(W5_ROOT / "verification/verify_stage5_frozen_set.py"),
         "--root", str(W5_ROOT), "--frozen-set", str(frozen_set_path)], W5_ROOT,
        run_dir / "stage5_frozen_set_check.txt")
    commands["s6d_eligibility_tests"] = run(
        [sys.executable, "-B", "-X", "utf8", "-m", "unittest", "-v",
         "verification.test_s6d_replay_preview_preflight"], W6_ROOT,
        run_dir / "s6d_eligibility_tests.txt")

    sources_doc = {
        "schema_version": 1, "run_id": RUN_ID, "w6_commit": W6_HEAD,
        "w4": {"worktree": str(W4_ROOT), "head": W4_HEAD,
               "contract_id": "s4-shared-io", "contract_version": "1.3.0", "revision": "r07",
               "contract_status": "FROZEN_OFFLINE_ONLY", "contract_sha256": W4_CONTRACT_SHA,
               "contract_bytes_commit": W4_CONTRACT_COMMIT,
               "freeze_run_id": freeze.get("run_id"), "freeze_scope": freeze.get("freeze_scope"),
               "freeze_sha256": W4_FREEZE_SHA, "package_dir": W4_PACKAGE},
        "w5": {"worktree": str(W5_ROOT), "head": W5_HEAD,
               "freeze_run_id": "s5_freeze_20261027_r07",
               "frozen_set_id": frozen_set.get("frozen_set_id"),
               "selected_members": [nohand_member, positive_member]},
        "files": source_records,
    }
    write_json(run_dir / "input_sources.json", sources_doc)
    result = {
        "schema_version": 1, "task_id": "S6-D", "run_id": RUN_ID,
        "status": "BLOCKED", "scope": "replay_only_qualification",
        "stage6_source_commit": W6_HEAD,
        "stage6_source_bindings": {"core_sha256": digest(core_blob),
                                   "params_sha256": digest(params_blob),
                                   "qualification_gate_sha256": digest(gate_blob)},
        "interfaces": [
            {"id": "s4-shared-io", "version": "1.3.0", "revision": "r07",
             "status": "FROZEN_OFFLINE_ONLY", "scope": "replay_only"},
            {"id": frozen_set.get("frozen_set_id"), "version": "OFFLINE_SCOPE_FROZEN",
             "revision": "s5_freeze_20261027_r07", "scope": "replay_only"},
        ],
        "frames": [
            {"variant": "NO_HAND", "frame_id": nohand.get("frame_id"), "state": nohand.get("state"),
             "capture_time_ns": nohand.get("capture_time_ns"),
             "result_time_ns": nohand.get("result_time_ns"), "stale": nohand.get("stale"),
             "eligibility": nohand_gate},
            {"variant": "positive_with_detections", "frame_id": positive.get("frame_id"),
             "state": positive.get("state"), "detection_count": positive.get("detection_count"),
             "detections": positive.get("detections"), "capture_time_ns": positive.get("capture_time_ns"),
             "result_time_ns": positive.get("result_time_ns"), "stale": positive.get("stale"),
             "eligibility": positive_gate},
        ],
        "core_execution": {"status": "NOT_RUN", "core_event_constructed": False,
                           "core_step_called": False,
                           "reason": "NO_HAND与阳性帧均被当前输入资格门阻断。"},
        "limitations": [
            "NO_HAND只有秒级文档墙钟capture_time；无同域发布时刻、result_time_ns与stale。",
            "阳性帧capture_time_ns=0是FILE_INJECTION哨兵，result_time_ns与stale为空。",
            "阳性state=PRESENT；阶段6核心只接受OK/NO_HAND，当前材料无已冻结映射。",
            "未推导fresh/stale、单调t_input_ns或帧周期；没有构造核心事件或调用状态机。",
            "不代表实时推理、板级行为、P/T6-A03、G3/G4/G5或阶段6整体冻结通过。",
        ],
        "initial_commands": commands,
    }
    write_json(run_dir / "preflight_result.json", result)
    (run_dir / "summary.md").write_text(
        "\n".join(["# S6-D replay-only资格核验", "",
                   "- 判定：**BLOCKED**；阶段6核心：**NOT_RUN**。",
                   f"- 当前阶段6提交：`{W6_HEAD}`；核心SHA-256：`{digest(core_blob)}`。",
                   f"- 阶段4冻结：`s4-shared-io/1.3.0 r07`，仅 `FROZEN_OFFLINE_ONLY`；记录SHA-256：`{W4_FREEZE_SHA}`。",
                   f"- 阶段5冻结集：`{frozen_set.get('frozen_set_id')}`；w5 HEAD：`{W5_HEAD}`。",
                   f"- NO_HAND：result_time_ns={nohand.get('result_time_ns')}、stale={nohand.get('stale')}；资格BLOCKED。",
                   f"- 阳性帧：state={positive.get('state')}、capture_time_ns={positive.get('capture_time_ns')}（FILE_INJECTION哨兵）、stale={positive.get('stale')}；资格BLOCKED。",
                   "- 未构造核心事件、未调用状态机；回放结论不表示实时、板级或G3/G4/G5。", ""]),
        encoding="utf-8")

    input_manifest = {
        "schema_version": 1, "stage": "6", "task_id": "S6-D", "run_id": RUN_ID,
        "source_commit": W6_HEAD, "evidence_dir": RUN_REL,
        "interfaces": [],
        "interfaces_not_applicable_reason": "本包仅绑定阶段4/5离线回放输入并核验当前资格，不声明阶段6跨阶段集成接口已满足。",
        "files": input_files + [
            {"path": rel, "sha256": digest(blob), "role": "source",
             "keep_reason": "当前w6源码字节；资格门的未提交版本按磁盘字节绑定",
             "hash_basis": "worktree_disk" if rel.endswith("s6d_replay_preview_preflight.py") else "commit_blob"}
            for rel, blob in (("src/stage6/s6_core.py", core_blob),
                              ("src/stage6/s6_params.py", params_blob),
                              ("verification/s6d_replay_preview_preflight.py", gate_blob))],
        "hash_basis": "worktree_disk", "hash_basis_commit": W6_HEAD,
        "checks": [
            check_record("阶段5离线冻结集复验", commands["stage5_frozen_set"]),
            check_record("阶段6资格门现有单测", commands["s6d_eligibility_tests"]),
        ],
        "limitations": ["两条输入资格均BLOCKED；缺失字段保持未知。"],
    }
    write_json(run_dir / "inputs_manifest.json", input_manifest)
    commands["inputs_manifest"] = run(
        [sys.executable, "-B", "-X", "utf8", str(MAIN_ROOT / "verification/check_stage_delivery.py"),
         "--mode", "inputs", "--manifest", str(run_dir / "inputs_manifest.json"),
         "--project-root", str(W6_ROOT)], MAIN_ROOT, run_dir / "inputs_check.txt")
    input_manifest["checks"].append(check_record("阶段交付inputs模式", commands["inputs_manifest"]))
    write_json(run_dir / "inputs_manifest.json", input_manifest)
    write_json(run_dir / "qualification_commands.json", commands)
    (run_dir / "evidence_check.txt").write_text("尚未运行。\n", encoding="utf-8")
    (run_dir / "hash_basis_check.txt").write_text("尚未运行。\n", encoding="utf-8")
    delivery = {
        "schema_version": 1, "stage": "6", "task_id": "S6-D", "run_id": RUN_ID,
        "source_commit": W6_HEAD, "evidence_dir": RUN_REL, "interfaces": [],
        "interfaces_not_applicable_reason": input_manifest["interfaces_not_applicable_reason"],
        "hash_basis": "worktree_disk", "hash_basis_note": "证据包按本次工作树字节核验。",
        "files": [], "checks": [
            check_record("阶段5离线冻结集复验", commands["stage5_frozen_set"]),
            check_record("阶段6资格门现有单测", commands["s6d_eligibility_tests"]),
            {"name": "replay-only资格", "status": "BLOCKED", "command": None, "exit_code": None,
             "reason": "NO_HAND缺result_time/stale；阳性帧缺时序且PRESENT状态没有阶段6冻结映射。"},
            check_record("阶段交付inputs模式", commands["inputs_manifest"]),
            {"name": "阶段交付evidence模式", "status": "NOT_RUN", "command": None, "exit_code": None,
             "reason": "生成最终清单后实跑并绑定真实退出码。"},
            {"name": "manifest hash_basis strict", "status": "NOT_RUN", "command": None, "exit_code": None,
             "reason": "证据文件列表稳定后按两个manifest实跑strict模式。"},
            {"name": "R01证据构建命令", "status": "PASS",
             "command": subprocess.list2cmdline(build_command), "exit_code": 0},
        ],
        "limitations": result["limitations"],
        "tool_versions": {"python": sys.version.split()[0], "w6_head": W6_HEAD,
                          "w4_head": W4_HEAD, "w5_head": W5_HEAD},
    }
    write_json(run_dir / "delivery_manifest.json", delivery)

    def evidence_check() -> dict[str, Any]:
        refresh_delivery(run_dir, delivery)
        check = run([sys.executable, "-B", "-X", "utf8",
                     str(MAIN_ROOT / "verification/check_stage_delivery.py"),
                     "--mode", "evidence", "--manifest", str(run_dir / "delivery_manifest.json"),
                     "--project-root", str(W6_ROOT)], MAIN_ROOT, run_dir / "evidence_check.txt")
        commands["evidence_manifest"] = check
        delivery["checks"][4] = check_record("阶段交付evidence模式", check)
        write_json(run_dir / "qualification_commands.json", commands)
        return check

    def hash_check() -> dict[str, Any]:
        refresh_delivery(run_dir, delivery)
        check = run([sys.executable, "-B", "-X", "utf8",
                     str(MAIN_ROOT / "verification/check_manifest_hash_basis.py"),
                     "--repo", str(W6_ROOT), "--paths", f"{RUN_REL}/inputs_manifest.json",
                     "--paths", f"{RUN_REL}/delivery_manifest.json", "--mode", "strict", "--json",
                     "--commit", W6_HEAD], MAIN_ROOT, run_dir / "hash_basis_check.txt")
        commands["manifest_hash_basis"] = check
        delivery["checks"][5] = check_record("manifest hash_basis strict", check)
        write_json(run_dir / "qualification_commands.json", commands)
        return check

    stable = False
    for _ in range(8):
        before = (file_sha(run_dir / "evidence_check.txt"),
                  file_sha(run_dir / "hash_basis_check.txt"),
                  file_sha(run_dir / "qualification_commands.json"))
        ev = evidence_check()
        hb = hash_check()
        after = (file_sha(run_dir / "evidence_check.txt"),
                 file_sha(run_dir / "hash_basis_check.txt"),
                 file_sha(run_dir / "qualification_commands.json"))
        if ev["exit_code"] != 0 or hb["exit_code"] != 0:
            break
        if before == after:
            stable = True
            break
    return 0 if all(commands.get(key, {}).get("exit_code") == 0 for key in (
        "stage5_frozen_set", "s6d_eligibility_tests", "inputs_manifest", "evidence_manifest", "manifest_hash_basis")) and stable else 1


def main() -> int:
    try:
        return build()
    except Exception as exc:  # 失败关闭并保留诊断
        print(f"[FAIL] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
