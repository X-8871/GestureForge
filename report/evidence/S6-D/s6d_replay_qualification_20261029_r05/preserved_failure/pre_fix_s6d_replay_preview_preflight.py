#!/usr/bin/env python3
"""核验阶段4单帧回放能否安全进入阶段6离线核心。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

EXPECTED_W4_RUN_HEAD = "4f4ae8f6d44f95b81e3cad2c17341611b0695485"
EXPECTED_W4_REVIEW_COMMIT = "5f9a04a045f4aaa7516759513f660f9872cbab61"
EXPECTED_W4_CONTRACT_COMMIT = "4400bb89cba5a860d6baa9e976bb08f25606cf15"
EXPECTED_W5_SOURCE_COMMIT = "869b869b9ba559d145f6bb28831667de07b093f8"
W4_CONTRACT = "docs/stage4/s4b_shared_input_result_contract.json"
W4_FREEZE = "report/evidence/S4-CTRL/s4t27_replay_package_freeze_20261027_r01/replay_package_freeze.json"
W4_FREEZE_MANIFEST = "report/evidence/S4-CTRL/s4t27_replay_package_freeze_20261027_r01/manifest.json"
W4_PACKAGE_DIR = "report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r04"
W5_REPLAY_DIR = "report/evidence/S5-T03/s5t03_stage4_frozen_replay_20261027_r04"
EXPECTED_FREEZE_SHA256 = "012f5ea4b6d21cf54b806ec46799bbff967ff41da24a47a52e09a4e9f019dfbd"
EXPECTED_W4_CONTRACT_SHA256 = "7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145"
EXPECTED_W5_MANIFEST_SHA256 = "3fb5f94c560f92dbcab0deb68afbde3b857b5b6d722364a35dbb5b5a979b472b"
EXPECTED_W5_FILES = {
    "freeze_integrity.json": "fb4f7dc0c3c2133d859b9b25931051c7983169bc2a8c55ef7d80e461a48b55a7",
    "consumer_report.json": "f58d5167d029a5e54623bc69ceb7af92a38985159766eaae417fb3fe2eb573f9",
    "crosscheck_report.json": "24001aefa7af21fdfeb3589cb7f320a5fc23f751ca3f59c227208d48379cc664",
    "frames.json": "6f2320cdfe7f0409719c705cb578a20b2869d88a27058325e6ce6ac16bb19536",
    "frames.jsonl": "1435e5340ecd5e80774eef7183f4d51f8f1b8a08e850e44b8d422d35ef8f6f0d",
    "five_tuples.jsonl": "c65a94af026cdf956e94de4421575461ecad0f10e18e274c7d96b3bc5bc188ae",
    "gate_evidence_projection.json": "ad5659becee5cea00166dd0c2f02f146a480c494840ff018fed113995678f22a",
    "summary.md": "abaf9073b0a59b7404fc2772c6366b427e4ef790b318a43e83123640e42d84bd",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层必须是对象：{path}")
    return value


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{result.stderr.strip()}")
    return result.stdout.strip()


def git_blob_sha256(root: Path, revision: str, rel_path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", f"{revision}:{rel_path}"],
        capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"读取 Git blob 失败：{revision}:{rel_path}")
    return sha256_bytes(result.stdout)


def git_blob(root: Path, revision: str, rel_path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", f"{revision}:{rel_path}"],
        capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"读取 Git blob 失败：{revision}:{rel_path}")
    return result.stdout


def is_ancestor(root: Path, ancestor: str, revision: str) -> bool:
    result = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                             ancestor, revision], capture_output=True, check=False)
    return result.returncode == 0


def bind_stage6_file(root: Path, rel_path: str, revision: str) -> dict[str, Any]:
    path = root / rel_path
    disk_sha = sha256_file(path)
    blob_sha = None
    try:
        blob_sha = git_blob_sha256(root, revision, rel_path)
    except RuntimeError:
        pass
    return {
        "path": rel_path,
        "disk_sha256": disk_sha,
        "bytes": path.stat().st_size,
        "head_blob_sha256": blob_sha,
        "disk_matches_head_blob": None if blob_sha is None else disk_sha == blob_sha,
    }


def hash_entry(root: Path, rel_path: str, role: str, reason: str) -> dict[str, str]:
    return {"path": rel_path, "sha256": sha256_file(root / rel_path),
            "role": role, "keep_reason": reason}


def run_tool(command: list[str], cwd: Path) -> dict[str, Any]:
    result = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=False)
    return {"command": subprocess.list2cmdline(command), "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require_sha(path: Path, expected: str, label: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"{label} SHA-256 不符：期望 {expected}，实际 {actual}")
    return actual


def classify_frame(frame: dict[str, Any], marking: dict[str, Any]) -> dict[str, Any]:
    """只判断回放结果记录是否具备安全输入条件，不补造缺失字段。"""
    reasons: list[str] = []
    if marking.get("replay_only") is not True:
        reasons.append("来源未声明 replay_only=true")
    if marking.get("evidence_kind") != "offline_replay":
        reasons.append("来源 evidence_kind 不是 offline_replay")
    if marking.get("buffer_scope") != "offline_host":
        reasons.append("来源 buffer_scope 不是 offline_host")
    if frame.get("input_kind") != "stage4_frozen_replay":
        reasons.append("输入记录不是 stage4_frozen_replay")
    if frame.get("consumption_mode") != "replay_only":
        reasons.append("输入记录 consumption_mode 不是 replay_only")
    if frame.get("evidence_kind") != "offline_replay":
        reasons.append("输入记录 evidence_kind 不是 offline_replay")
    if frame.get("scope_statement") != "离线主机回放；不代表 PL、实物或实时检测输出":
        reasons.append("输入记录缺少精确离线回放范围声明")
    if frame.get("state") not in {"OK", "NO_HAND"}:
        reasons.append("结果 state 不属于阶段6可消费的 OK/NO_HAND")
    detections = frame.get("detections")
    if not isinstance(detections, list):
        reasons.append("detections 缺失或不是数组")
    elif frame.get("detection_count") != len(detections):
        reasons.append("detection_count 与 detections 数量不一致")
    if frame.get("state") == "NO_HAND" and detections != []:
        reasons.append("NO_HAND 结果必须为零框；不得补入阳性门禁框")
    stale = frame.get("stale")
    if type(stale) is not bool:
        reasons.append("stale 不是布尔值；阶段6不能把未知状态静默当作 fresh")
    else:
        result_time = frame.get("result_time_ns")
        age_result = frame.get("age_result_ns")
        age_frame = frame.get("age_frame_ns")
        if isinstance(result_time, bool) or not isinstance(result_time, int) or result_time < 0:
            reasons.append("缺少契约结果记录要求的有效单调 result_time_ns")
        if (not isinstance(age_result, int) or isinstance(age_result, bool) or age_result < 0
                or not isinstance(age_frame, int) or isinstance(age_frame, bool) or age_frame < 0):
            if stale:
                reasons.append("stale=true 结果缺少契约要求的 age_result_ns 与 age_frame_ns")
            else:
                reasons.append("stale=false 结果缺少可复算的 age_result_ns 与 age_frame_ns")
        # r07 未冻结结果时间、采集时间与 stale 来源的字段依据和时钟域 schema；
        # 帧内自报字符串不能证明这些值来自权威单调时钟，因此两种 stale 标志都阻断。
        reasons.append("阶段4 r07 未冻结可验证的结果时间/stale 来源 schema；回放字段自报值不足以证明时钟权威")
    key = (frame.get("session_id"), frame.get("frame_id"), frame.get("result_seq"))
    if any(type(value) is not int for value in key):
        reasons.append("session_id/frame_id/result_seq 缺少整数主键")
    return {
        "status": "READY_FOR_REPLAY_ONLY_PREVIEW" if not reasons else "BLOCKED",
        "reasons": reasons,
        "core_event_constructed": False,
        "core_step_called": False,
    }


def audit_upstream(w4_root: Path, w5_root: Path) -> dict[str, Any]:
    w4_head = git_output(w4_root, "rev-parse", "HEAD")
    w5_head = git_output(w5_root, "rev-parse", "HEAD")

    freeze_path = w4_root / W4_FREEZE
    freeze_sha = require_sha(freeze_path, EXPECTED_FREEZE_SHA256, "w4 回放冻结记录")
    freeze = load_json(freeze_path)
    freeze_manifest = load_json(w4_root / W4_FREEZE_MANIFEST)
    if freeze_manifest.get("verdict") != "FROZEN_REPLAY_ONLY":
        raise ValueError("w4 回放冻结清单未标记 FROZEN_REPLAY_ONLY")
    freeze_file = (freeze_manifest.get("files") or [{}])[0]
    if (freeze_file.get("path") != "replay_package_freeze.json"
            or freeze_file.get("sha256") != freeze_sha
            or freeze_file.get("bytes") != freeze_path.stat().st_size):
        raise ValueError("w4 冻结记录与其清单绑定不一致")

    w4_run_manifest = load_json(w4_root / W4_PACKAGE_DIR / "delivery_manifest.json")
    w4_run_head = w4_run_manifest.get("baseline", {}).get("head_observed_only")
    if not is_ancestor(w4_root, EXPECTED_W4_CONTRACT_COMMIT, w4_head):
        raise ValueError("w4 固定 r07 契约提交不是当前 w4 HEAD 的祖先")
    contract_blob = git_blob(w4_root, EXPECTED_W4_CONTRACT_COMMIT, W4_CONTRACT)
    contract_sha = sha256_bytes(contract_blob)
    if contract_sha != EXPECTED_W4_CONTRACT_SHA256:
        raise ValueError("w4 固定提交中的 r07 契约字节哈希不符")
    contract = json.loads(contract_blob.decode("utf-8"))
    review_record = contract.get("review_record") or {}
    freeze_record = contract.get("freeze_record") or {}
    review_commit = review_record.get("reviewed_commit")
    if w4_run_head != EXPECTED_W4_RUN_HEAD:
        raise ValueError(f"w4 回放生成提交不符：期望 {EXPECTED_W4_RUN_HEAD}，实际 {w4_run_head}")
    if review_commit != EXPECTED_W4_REVIEW_COMMIT:
        raise ValueError(f"w4 契约复审提交不符：期望 {EXPECTED_W4_REVIEW_COMMIT}，实际 {review_commit}")
    if (review_record.get("verdict") != "PASS"
            or review_record.get("json_sha256") != freeze_record.get("based_on_reviewed_json_sha256")
            or review_record.get("md_sha256") != freeze_record.get("based_on_reviewed_md_sha256")
            or freeze_record.get("reviewed_commit") != review_commit
            or freeze_record.get("frozen_revision") != "r07"
            or freeze_record.get("frozen_contract_version") != "1.3.0"
            or freeze_record.get("freeze_scope") != "OFFLINE_ONLY"):
        raise ValueError("w4 冻结契约未将 PASS 复审字节、复审提交与 r07 离线冻结记录交叉绑定")
    if not is_ancestor(w4_root, w4_run_head, w4_head):
        raise ValueError("w4 回放生成提交不是当前 w4 HEAD 的祖先")
    if not is_ancestor(w4_root, review_commit, w4_head):
        raise ValueError("w4 契约独立复审提交不是当前 w4 HEAD 的祖先")

    if not is_ancestor(w5_root, EXPECTED_W5_SOURCE_COMMIT, w5_head):
        raise ValueError("w5 回放消费者源码提交不是当前 w5 HEAD 的祖先")

    binding = freeze.get("contract_binding") or {}
    if (contract.get("status") != "FROZEN_OFFLINE_ONLY"
            or contract.get("contract_version") != "1.3.0"
            or contract.get("revision") != "r07"
            or binding.get("json_sha256") != contract_sha
            or binding.get("freeze_scope") != "OFFLINE_ONLY"):
        raise ValueError("w4 契约状态、版本或冻结绑定不一致")
    result_record = (contract.get("result_contract") or {}).get("result_record") or {}
    stale_rule = (contract.get("result_contract") or {}).get("stale_rule") or {}
    result_record_fields = result_record.get("fields")
    if (not isinstance(result_record.get("authority"), str)
            or not isinstance(result_record_fields, list)
            or "stale" not in result_record_fields
            or "result_time_ns" not in result_record_fields
            or stale_rule.get("stale_limit_ns") != 200000000
            or stale_rule.get("stale_limit_status") != "APPROVED_BY_WONG"):
        raise ValueError("w4 固定 r07 契约缺少获批 stale 与时间字段定义")

    source_dir = w4_root / W4_PACKAGE_DIR
    file_checks = []
    for record in freeze.get("files", []):
        path = source_dir / record["path"]
        actual = sha256_file(path)
        actual_bytes = path.stat().st_size
        passed = actual == record.get("sha256") and actual_bytes == record.get("bytes")
        file_checks.append({"path": record["path"], "sha256": actual,
                            "bytes": actual_bytes, "status": "PASS" if passed else "FAIL"})
        if not passed:
            raise ValueError(f"w4 冻结包文件不匹配：{record['path']}")
    if len(file_checks) != 10 or freeze.get("missing_files") != []:
        raise ValueError("w4 回放包不是完整的 10 文件冻结集")

    package = load_json(source_dir / "task27_replay_result_package.json")
    if package.get("marking", {}).get("replay_only") is not True:
        raise ValueError("w4 task-27 结果包缺少 replay_only 标记")
    if (package.get("marking", {}).get("evidence_kind") != "offline_replay"
            or package.get("marking", {}).get("buffer_scope") != "offline_host"):
        raise ValueError("w4 task-27 结果包的离线来源标记不完整")
    if package.get("contract_result_key") != freeze.get("package_identity", {}).get("contract_result_key"):
        raise ValueError("w4 结果主键与冻结身份不一致")

    s5_dir = w5_root / W5_REPLAY_DIR
    s5_manifest_path = s5_dir / "manifest.json"
    s5_manifest_sha = require_sha(s5_manifest_path, EXPECTED_W5_MANIFEST_SHA256, "w5 回放消费清单")
    s5_manifest = load_json(s5_manifest_path)
    if (s5_manifest.get("run_id") != "s5t03_stage4_frozen_replay_20261027_r04"
            or s5_manifest.get("consumption_mode") != "replay_only"
            or s5_manifest.get("evidence_kind") != "offline_replay"):
        raise ValueError("w5 消费证据身份或范围标签不一致")
    for source in s5_manifest.get("sources", []):
        source_path = source["path"]
        disk_sha = sha256_file(w5_root / source_path)
        blob_sha = git_blob_sha256(w5_root, EXPECTED_W5_SOURCE_COMMIT, source_path)
        if disk_sha != source.get("sha256") or blob_sha != source.get("sha256"):
            raise ValueError(f"w5 消费脚本与固定源码提交 blob 不匹配：{source_path}")

    evidence_files = {}
    for name, expected_sha in EXPECTED_W5_FILES.items():
        path = s5_dir / name
        actual = require_sha(path, expected_sha, f"w5 消费产物 {name}")
        evidence_files[name] = {"sha256": actual, "bytes": path.stat().st_size}

    integrity = load_json(s5_dir / "freeze_integrity.json")
    consumer = load_json(s5_dir / "consumer_report.json")
    crosscheck = load_json(s5_dir / "crosscheck_report.json")
    frames_doc = load_json(s5_dir / "frames.json")
    projection = load_json(s5_dir / "gate_evidence_projection.json")
    if (integrity.get("consumable") is not True
            or integrity.get("verdict") != "CONSUMABLE_OFFLINE_REPLAY_ONLY"
            or integrity.get("file_integrity", {}).get("checked") != 10
            or integrity.get("file_integrity", {}).get("ok") != 10
            or integrity.get("upstream_binding_drift", {}).get("checked") != 17
            or integrity.get("upstream_binding_drift", {}).get("ok") != 17):
        raise ValueError("w5 冻结完整性记录未通过 10/10 与 17/17")
    if consumer.get("source", {}).get("contract_sha256") != contract_sha:
        raise ValueError("w5 消费报告绑定的 w4 契约 SHA 不匹配")
    if (crosscheck.get("integrity", {}).get("consumable") is not True
            or crosscheck.get("labels", {}).get("verdict") != "PASS"):
        raise ValueError("w5 回放交叉核验不是 PASS")
    projection_records = projection.get("records", [])
    projection_sources = [
        row.get("source_ref", "")
        for record in projection_records
        for row in record.get("detections", [])
    ]
    if (projection.get("display_eligible") is not False
            or not projection_records
            or any(record.get("display_eligible") is not False
                   or record.get("is_replay_frame") is not False
                   or record.get("attribution") != "gate_evidence_sample_not_replay_frame"
                   for record in projection_records)
            or any(not source.startswith((
                "positive_detection_gate.d9_nms.predictions[",
                "positive_detection_gate.d9_nms.t29_reference_predictions[",
            )) for source in projection_sources)):
        raise ValueError("w5 阳性门禁投影未保持 display_eligible=false 或来源标签不符")
    if frames_doc.get("frame_count") != 1 or len(frames_doc.get("frames", [])) != 1:
        raise ValueError("w5 消费结果应为且仅为 1 帧")
    frame = frames_doc["frames"][0]
    expected_key = package["contract_result_key"]
    if (frame.get("session_id") != expected_key.get("session_id")
            or frame.get("frame_id") != expected_key.get("frame_id")
            or frame.get("result_seq") != expected_key.get("result_seq")):
        raise ValueError("w5 帧记录与 w4 回放结果主键不一致")

    evidence_files["manifest.json"] = {"sha256": s5_manifest_sha,
                                        "bytes": s5_manifest_path.stat().st_size}
    return {
        "w4": {"current_head": w4_head, "run_source_commit": w4_run_head,
               "reviewed_contract_commit": review_commit, "contract_path": W4_CONTRACT,
               "contract_commit": EXPECTED_W4_CONTRACT_COMMIT,
               "contract_sha256": contract_sha, "contract_version": "1.3.0",
               "contract_revision": "r07", "freeze_record_path": W4_FREEZE,
               "freeze_record_sha256": freeze_sha, "freeze_scope": "OFFLINE_ONLY",
               "result_record_authority": result_record["authority"],
               "result_record_fields": result_record_fields,
               "stale_rule": stale_rule,
               "package_dir": W4_PACKAGE_DIR, "package_files": file_checks},
        "w5": {"current_head": w5_head, "source_commit": EXPECTED_W5_SOURCE_COMMIT,
               "evidence_dir": W5_REPLAY_DIR,
               "manifest_sha256": s5_manifest_sha, "source_count": len(s5_manifest.get("sources", [])),
               "source_hashes_match_pinned_commit_blobs": True, "evidence_files": evidence_files,
               "freeze_integrity": {"verdict": integrity.get("verdict"),
                                    "file_integrity": "10/10 PASS",
                                    "upstream_binding_drift": "17/17 PASS"}},
        "package_marking": package.get("marking"),
        "frame": frame,
    }


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="阶段6 replay-only 单帧预演输入门")
    parser.add_argument("--upstream-audit", action="store_true",
                        help="只读复算固定阶段4/5提交、冻结字节和消费产物")
    parser.add_argument("--project-root")
    parser.add_argument("--w4-root", default="D:/codex-worktrees/w4")
    parser.add_argument("--w5-root", default="D:/codex-worktrees/w5")
    parser.add_argument("--run-dir")
    args = parser.parse_args(argv)
    if args.upstream_audit:
        try:
            upstream = audit_upstream(Path(args.w4_root).resolve(), Path(args.w5_root).resolve())
        except Exception as exc:  # noqa: BLE001
            print(f"上游绑定核验失败：{type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
        print(json.dumps({"status": "PASS", "upstream_bindings": upstream}, ensure_ascii=False))
        return 0
    if not args.project_root or not args.run_dir:
        parser.error("预演模式必须提供 --project-root 与 --run-dir")
    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    expected_run = "report/evidence/S6-D/s6d_replay_no_hand_20261027_r03"
    if Path(args.run_dir).as_posix() != expected_run:
        print(f"RunId 路径必须精确为 {expected_run}")
        return 2
    if run_dir.exists():
        print(f"RunId 已存在，拒绝覆盖：{run_dir}")
        return 2
    try:
        upstream = audit_upstream(Path(args.w4_root).resolve(), Path(args.w5_root).resolve())
    except Exception as exc:  # noqa: BLE001
        print(f"上游绑定核验失败：{type(exc).__name__}: {exc}")
        return 2

    frame = upstream.pop("frame")
    package_marking = upstream.pop("package_marking")
    decision = classify_frame(frame, package_marking)
    run_dir.mkdir(parents=True)
    w6_head = git_output(root, "rev-parse", "HEAD")
    stage6_paths = [
        "docs/stage6/s6a_stage6_g0_behavior_v1.json",
        "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
        "src/stage6/s6_core.py",
        "src/stage6/s6_params.py",
        "verification/s6d_replay_preview_preflight.py",
        "verification/test_s6d_replay_preview_preflight.py",
        "verification/run_s6d_replay_preview.py",
    ]
    stage6_bindings = [bind_stage6_file(root, rel, w6_head) for rel in stage6_paths]
    result = {
        "schema_version": 1,
        "task_id": "S6-D",
        "run_id": run_dir.name,
        "status": "BLOCKED" if decision["status"] == "BLOCKED" else "PREVIEW_READY_NOT_EXECUTED",
        "generated_scope": "offline_replay_only",
        "stage6_source_commit": w6_head,
        "stage6_source_bindings": stage6_bindings,
        "preserved_initial_attempts": [{
            "attempt": 1,
            "command_exit_code": 1,
            "observed_output": (
                "上游绑定核验失败：ValueError: w4 HEAD 漂移：期望 "
                "40b9a8c431d2b9ac884117208288a999b29e309e，实际 "
                "b46a012dfb04e7c49fa8fd4296485ac148b20b99"),
            "effect": "在 RunId 目录创建前停止；未生成或覆盖任何证据文件。",
            "resolution": "改为验证不变回放冻结字节、生成提交/复审提交身份及其可达性；仅记录当前 HEAD。",
        }, {
            "attempt": 2,
            "command_exit_code": 1,
            "observed_output": (
                "上游绑定核验失败：ValueError: w4 契约复审提交不符：期望 "
                "5f9a04a045f4aaa7516759513f660f9872cbab61，实际 None"),
            "effect": "在 RunId 目录创建前停止；未生成或覆盖任何证据文件。",
            "resolution": "复审提交在冻结契约 review_record 与 freeze_record 中交叉绑定；回放冻结记录自身不含 reviewed_commit。",
        }, {
            "attempt": 3,
            "command_exit_code": 1,
            "observed_output": (
                "上游绑定核验失败：ValueError: w5 阳性门禁投影未保持 "
                "display_eligible=false 或来源标签不符"),
            "effect": "在 RunId 目录创建前停止；未生成或覆盖任何证据文件。",
            "resolution": "验证每条投影记录标记为非回放且不可显示，并按冻结产物中的两个实际源引用前缀识别门禁几何框。",
        }],
        "preserved_preflight_attempts": [{
            "attempt": 1,
            "command": "python -B verification/s6d_replay_preview_preflight.py --upstream-audit --w4-root D:/codex-worktrees/w4 --w5-root D:/codex-worktrees/w5",
            "exit_code": 1,
            "observed_error": "UnicodeEncodeError: console encoding gbk 无法输出 SHA 绑定审计结果中的 U+21D2 字符；在写入 RunId 前停止。",
            "effect": "只读 CLI 自检失败；未修改上游或 w6 文件，未创建任何预演证据。",
            "resolution": "所有审计/检查子进程加入 -X utf8，CLI stdout/stderr 显式使用 UTF-8。",
        }],
        "upstream_bindings": upstream,
        "actual_replay_input": {
            key: frame.get(key) for key in (
                "session_id", "frame_id", "result_seq", "repeat_index", "sequence",
                "source_kind", "state", "detection_count", "detections", "capture_time_ns",
                "result_time_ns", "inference_time_ns", "end_to_end_latency_ns", "stale", "error_code",
                "timing_basis", "field_bases",
                "input_kind", "consumption_mode", "evidence_kind", "buffer_scope", "scope_statement",
            )
        },
        "eligibility": decision,
        "core_execution": {"status": "NOT_RUN",
                           "reason": "输入字段闸门 BLOCKED 时不调用状态机，避免将未知 stale 默认为 fresh。"},
        "not_applicable": [
            "阳性检测门禁框不属于回放帧；本轮未读取、未注入，也未生成任何检测框。",
            "单帧 NO_HAND 不含目标选择、稳定窗口、保持/重获、动作、冷却、去重、未知场景或恢复轨迹。",
            "capture_time_ns 属 documented replay wall-clock；没有单调发布时刻和帧间周期，未据此构造 t_input_ns。",
            "T6-A03/P、实时延迟、板级 G3、6-E 实物验收、G4/G5 均未执行。",
        ],
    }
    output = run_dir / "preflight_result.json"
    write_json(output, result)
    summary = [
        "# S6-D 单帧回放输入预检",
        "",
        f"- 状态：**{result['status']}**",
        "- 适用范围：阶段4/5 固定字节下的离线 replay-only 输入资格检查。",
        "- 状态机：**未调用**；没有构造事件或动作。",
        "- 真实回放帧：1 帧 `NO_HAND`、0 检测框。",
        f"- 阻断原因：{'；'.join(decision['reasons']) if decision['reasons'] else '无'}",
        "- 阳性门禁几何投影明确 `display_eligible=false`，未读作回放检测框。",
        "- `capture_time_ns` 是文档化回放墙钟，不是单调发布计时；`result_time_ns`、年龄和 `stale` 均不可用。",
        "- T6-A03/P、实时延迟、板级 G3、6-E 实物验收及阶段 G4/G5 未执行。",
        "",
    ]
    (run_dir / "summary.md").write_text("\n".join(summary), encoding="utf-8")

    test_command = [sys.executable, "-B", "-X", "utf8", "-m", "unittest", "-v",
                    "verification.test_s6d_replay_preview_preflight"]
    test_run = run_tool(test_command, root)
    (run_dir / "unit_test_output.txt").write_text(
        test_run["stdout"] + test_run["stderr"], encoding="utf-8")

    audit_command = [sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "--upstream-audit",
                     "--w4-root", str(Path(args.w4_root).resolve()),
                     "--w5-root", str(Path(args.w5_root).resolve())]
    audit_run = run_tool(audit_command, root)
    audit_output_path = run_dir / "upstream_audit_output.txt"
    audit_output_path.write_text(audit_run["stdout"] + audit_run["stderr"], encoding="utf-8")
    result["independent_upstream_audit"] = {
        "command": audit_run["command"],
        "exit_code": audit_run["exit_code"],
        "output_path": args.run_dir.replace("\\", "/") + "/upstream_audit_output.txt",
        "output_sha256": sha256_file(audit_output_path),
    }
    if audit_run["exit_code"] != 0 or test_run["exit_code"] != 0:
        result["status"] = "BLOCKED"
    write_json(output, result)

    inputs_manifest_path = run_dir / "inputs_manifest.json"
    input_files = [
        hash_entry(root, "docs/stage6/s6a_stage6_g0_behavior_v1.json", "input",
                   "阶段6 已批准行为表：NO_HAND 与窗口推进语义依据"),
        hash_entry(root, "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", "source",
                   "阶段6 行为说明与范围约束"),
        hash_entry(root, "src/stage6/s6_core.py", "source",
                   "被评估的阶段6 实际状态机核心；本轮未调用"),
        hash_entry(root, "src/stage6/s6_params.py", "source",
                   "被评估的阶段6 参数校验层；本轮未装载参数"),
        hash_entry(root, "verification/s6d_replay_preview_preflight.py", "source",
                   "本轮回放输入门实现"),
        hash_entry(root, "verification/test_s6d_replay_preview_preflight.py", "source",
                   "本轮回放输入门定向测试"),
        hash_entry(root, "verification/run_s6d_replay_preview.py", "source",
                   "负责捕获主预检 runner 实际退出码并固定最终清单的本轮包装器"),
        {"path": args.run_dir.replace("\\", "/") + "/preflight_result.json",
         "sha256": sha256_file(output), "role": "result",
         "keep_reason": "本轮输入资格与上游绑定结果"},
    ]
    inputs_payload = {
        "schema_version": 1, "stage": "6", "task_id": "S6-D", "run_id": run_dir.name,
        "source_commit": w6_head, "evidence_dir": args.run_dir.replace("\\", "/"),
        "interfaces": [],
        "interfaces_not_applicable_reason": (
            "本次只读绑定阶段4/5 的跨树 replay-only 文件；没有把离线范围冻结件申报为阶段6 集成接口。"),
        "files": input_files,
        "checks": [{"name": "阶段4/5 独立只读绑定复算",
                    "status": "PASS" if audit_run["exit_code"] == 0 else "FAIL",
                    "command": audit_run["command"],
                    "exit_code": audit_run["exit_code"]}],
        "limitations": [
            "上游独立复算命令、stdout、stderr 与退出码均收录；逐文件 SHA 和 pinned commit 记录在 preflight_result.json。",
            "输入资格 BLOCKED 属于本次结果，不代表结构/哈希检查失败。",
        ],
    }
    write_json(inputs_manifest_path, inputs_payload)
    checker = root / "verification/check_stage_delivery.py"
    inputs_command = [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "inputs",
                      "--manifest", str(inputs_manifest_path), "--project-root", str(root)]
    inputs_run = run_tool(inputs_command, root)
    (run_dir / "check_inputs_mode_output.txt").write_text(
        inputs_run["stdout"] + inputs_run["stderr"], encoding="utf-8")

    source_commit = w6_head
    evidence_output_path = run_dir / "check_evidence_mode_output.txt"
    evidence_output_path.write_text("evidence checker 尚未执行。\n", encoding="utf-8")
    common_files = []
    for item in input_files:
        common_files.append({**item})
    common_files.extend([
        {"path": args.run_dir.replace("\\", "/") + "/inputs_manifest.json",
         "sha256": sha256_file(inputs_manifest_path), "role": "result",
         "keep_reason": "输入清单与实际哈希"},
        {"path": args.run_dir.replace("\\", "/") + "/summary.md",
         "sha256": sha256_file(run_dir / "summary.md"), "role": "result",
         "keep_reason": "人读范围摘要"},
        {"path": args.run_dir.replace("\\", "/") + "/unit_test_output.txt",
         "sha256": sha256_file(run_dir / "unit_test_output.txt"), "role": "log",
         "keep_reason": "定向单测真实输出"},
        {"path": args.run_dir.replace("\\", "/") + "/check_inputs_mode_output.txt",
         "sha256": sha256_file(run_dir / "check_inputs_mode_output.txt"), "role": "log",
         "keep_reason": "阶段交付输入清单核验真实输出"},
        {"path": args.run_dir.replace("\\", "/") + "/upstream_audit_output.txt",
         "sha256": sha256_file(run_dir / "upstream_audit_output.txt"), "role": "log",
         "keep_reason": "独立只读复算阶段4/5提交、冻结字节和消费产物的真实输出"},
        {"path": args.run_dir.replace("\\", "/") + "/check_evidence_mode_output.txt",
         "sha256": sha256_file(evidence_output_path), "role": "log",
         "keep_reason": "阶段交付 evidence 模式真实 stdout/stderr"},
    ])
    checks = [
        {"name": "replay-only 单帧输入资格", "status": "BLOCKED", "command": None,
         "exit_code": None, "reason": "实际 stale=null 且无契约权威时间依据；不可静默映射为 stale=false。"},
        {"name": "阶段4/5 独立只读绑定复算",
         "status": "PASS" if audit_run["exit_code"] == 0 else "FAIL",
         "command": audit_run["command"], "exit_code": audit_run["exit_code"],
         **({} if audit_run["exit_code"] == 0 else {"reason": "独立上游绑定复算失败"})},
        {"name": "阶段交付 inputs 模式", "status": "PASS" if inputs_run["exit_code"] == 0 else "FAIL",
         "command": inputs_run["command"], "exit_code": inputs_run["exit_code"],
         **({} if inputs_run["exit_code"] == 0 else {"reason": "inputs 模式失败"})},
        {"name": "定向单元测试", "status": "PASS" if test_run["exit_code"] == 0 else "FAIL",
         "command": subprocess.list2cmdline(test_command), "exit_code": test_run["exit_code"],
         **({} if test_run["exit_code"] == 0 else {"reason": "单元测试失败"})},
        {"name": "阶段交付 evidence 模式", "status": "NOT_RUN", "command": None,
         "exit_code": None, "reason": "生成清单后立即实跑并收录真实退出码。"},
    ]
    delivery_manifest = {
        "schema_version": 1, "stage": "6", "task_id": "S6-D", "run_id": run_dir.name,
        "source_commit": source_commit, "evidence_dir": args.run_dir.replace("\\", "/"),
        "interfaces": [], "interfaces_not_applicable_reason": inputs_payload["interfaces_not_applicable_reason"],
        "files": common_files, "checks": checks,
        "limitations": [
            "本包只记录 replay-only 单帧输入预检；状态机未调用，阶段6 回放预演未执行。",
            "阶段4/5 上游 SHA、精确提交及消费范围见 preflight_result.json。",
            "没有实测时间/帧周期；T6-A03/P 仍 NOT_RUN。",
            "阳性门禁几何投影 display_eligible=false，未作为回放框消费。",
        ],
        "tool_versions": {
            "python": sys.version.split()[0],
            "git": git_output(root, "--version"),
        },
    }
    delivery_path = run_dir / "delivery_manifest.json"
    write_json(delivery_path, delivery_manifest)
    evidence_command = [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "evidence",
                        "--manifest", str(delivery_path), "--project-root", str(root)]
    prior_output: str | None = None
    prior_exit: int | None = None
    evidence_exit = 2
    evidence_stable = False
    for _ in range(5):
        evidence_run = run_tool(evidence_command, root)
        evidence_output = evidence_run["stdout"] + evidence_run["stderr"]
        evidence_exit = evidence_run["exit_code"]
        checks[-1] = {
            "name": "阶段交付 evidence 模式",
            "status": "PASS" if evidence_exit == 0 else "FAIL",
            "command": evidence_run["command"],
            "exit_code": evidence_exit,
            **({} if evidence_exit == 0 else {"reason": "evidence 模式失败"}),
        }
        evidence_output_path.write_text(evidence_output, encoding="utf-8")
        next(record for record in common_files
             if record["path"].endswith("/check_evidence_mode_output.txt"))["sha256"] = sha256_file(
                 evidence_output_path)
        delivery_manifest["checks"] = checks
        write_json(delivery_path, delivery_manifest)
        if evidence_output == prior_output and evidence_exit == prior_exit:
            evidence_stable = True
            break
        prior_output = evidence_output
        prior_exit = evidence_exit
    if not evidence_stable:
        checks[-1] = {
            "name": "阶段交付 evidence 模式",
            "status": "FAIL",
            "command": evidence_run["command"],
            "exit_code": evidence_exit,
            "reason": "checker 输出在清单绑定复核中未稳定，不能判为通过",
        }
        delivery_manifest["checks"] = checks
        write_json(delivery_path, delivery_manifest)
    print(json.dumps({"status": result["status"], "run_id": result["run_id"],
                      "unit_test_exit_code": test_run["exit_code"],
                      "upstream_audit_exit_code": audit_run["exit_code"],
                      "inputs_check_exit_code": inputs_run["exit_code"],
                      "evidence_check_exit_code": evidence_exit,
                      "runner_exit_code": 2 if result["status"] == "BLOCKED" else 0,
                      "reasons": decision["reasons"]}, ensure_ascii=False))
    return 2 if result["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
