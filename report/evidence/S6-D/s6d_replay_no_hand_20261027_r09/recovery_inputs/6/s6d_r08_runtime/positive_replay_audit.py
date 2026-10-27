#!/usr/bin/env python3
"""只读绑定最新阶段4/5阳性回放，并保守判定阶段6输入资格。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

W4_POSITIVE_DIR = "report/evidence/S4-CTRL/s4t27_replay_positive_20261027_r01"
W4_GATE_RESULT = "report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r04/replay_forward_bridge_result.json"
W4_CONTRACT = "docs/stage4/s4b_shared_input_result_contract.json"
W5_POSITIVE_DIR = "report/evidence/S5-T03/s5t03_stage4_positive_replay_20261027_r01"
W4_CONTRACT_COMMIT = "4400bb89cba5a860d6baa9e976bb08f25606cf15"
W4_CONTRACT_SHA256 = "7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145"
W5_SOURCE_COMMIT = "869b869b9ba559d145f6bb28831667de07b093f8"
W4_FILES = {
    "freeze_index.json": ("a193fca16550b0ac2c2355cdac3c95dfaad3fce654c8d52390a685060719ccc6", 1144),
    "manifest.json": ("c3f5ceb0d0910f0dbc81c1d7f140bc703b2e39ac6809f1f3ae94117a9bc84e53", 680),
    "task27_replay_result_package_positive.json": ("988f2cae79cc4bfb306ccf4ef2601fcb52f6f3c34cfd906ddb6589e686d89986", 4897),
}
W5_MANIFEST_SHA256 = "0a1d05689ed659ff83aad1b6f7203d1d82446630e1216a549f2d52ae227e9884"
W5_FILES = {
    "console/positive_bridge_payload.json": "14e1571b91246c417d6973ad43892c38987799c64db48021c7e3d7fad6d77f0d",
    "console/positive_integrity.json": "4240df395f10e4af76f27416a5af6dd22565001dec7681c9b39399a70aa50730",
    "console/positive_report.json": "1fcc3a936da452691cd7e8d4dd756dd2bc0b82a9a496c01a12f691bc552fc497",
    "five_tuples.jsonl": "12c0937b2f1a1a9eb3997b3e756eb35b342f449e70aeb3eff58f792a8187e670",
    "frames.jsonl": "e3c99504de983f0d614232b9e4745fbf74e8f54b11c3492914cf3cb2fc4eba70",
    "summary.md": "b09f48234f69776bc1723a5b3317413898b63645a069e7c77df24027a3e476b3",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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
        raise RuntimeError(f"Git blob 不可读：{revision}:{rel_path}")
    return sha256_bytes(result.stdout)


def is_ancestor(root: Path, ancestor: str, revision: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, revision],
        capture_output=True, check=False,
    )
    return result.returncode == 0


def worktree_matches_head(root: Path, rel_path: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", rel_path],
        capture_output=True, check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"git diff HEAD -- {rel_path} 失败：退出码 {result.returncode}")
    return result.returncode == 0


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层必须是对象：{path}")
    return value


def verify_file(root: Path, rel_path: str, expected_sha: str,
                expected_bytes: int | None, source_head: str) -> dict[str, Any]:
    path = root / rel_path
    actual_sha = sha256_file(path)
    actual_bytes = path.stat().st_size
    blob_sha = git_blob_sha256(root, source_head, rel_path)
    matches_head = worktree_matches_head(root, rel_path)
    passed = (actual_sha == expected_sha and matches_head
              and (expected_bytes is None or actual_bytes == expected_bytes))
    return {
        "path": rel_path,
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "source_head_blob_sha256": blob_sha,
        "worktree_matches_head_after_git_filters": matches_head,
        "hash_note": "冻结清单按工作树原始字节 SHA-256；HEAD raw blob 单独记录，CRLF 由 Git clean filter 归一化后以 diff HEAD 核验。",
        "expected_bytes": expected_bytes,
        "actual_bytes": actual_bytes,
        "status": "PASS" if passed else "FAIL",
    }


def audit(w4_root: Path, w5_root: Path) -> dict[str, Any]:
    w4_head = git_output(w4_root, "rev-parse", "HEAD")
    w5_head = git_output(w5_root, "rev-parse", "HEAD")
    if not is_ancestor(w4_root, W4_CONTRACT_COMMIT, w4_head):
        raise ValueError("阶段4 r07 契约字节提交不是当前 HEAD 祖先")
    if not is_ancestor(w5_root, W5_SOURCE_COMMIT, w5_head):
        raise ValueError("阶段5阳性消费源码提交不是当前 HEAD 祖先")

    contract_sha = git_blob_sha256(w4_root, W4_CONTRACT_COMMIT, W4_CONTRACT)
    if contract_sha != W4_CONTRACT_SHA256:
        raise ValueError(f"阶段4冻结契约 blob SHA 不符：{contract_sha}")
    contract = json.loads(subprocess.run(
        ["git", "-C", str(w4_root), "cat-file", "blob",
         f"{W4_CONTRACT_COMMIT}:{W4_CONTRACT}"],
        capture_output=True, check=True,
    ).stdout.decode("utf-8"))
    if (contract.get("status") != "FROZEN_OFFLINE_ONLY"
            or contract.get("revision") != "r07"
            or contract.get("contract_version") != "1.3.0"):
        raise ValueError("阶段4契约不是所批准的 r07 / 1.3.0 离线冻结版本")

    w4_manifest_path = f"{W4_POSITIVE_DIR}/manifest.json"
    w4_index_path = f"{W4_POSITIVE_DIR}/freeze_index.json"
    w4_package_path = f"{W4_POSITIVE_DIR}/task27_replay_result_package_positive.json"
    w4_checks = [
        verify_file(w4_root, f"{W4_POSITIVE_DIR}/{name}", expected_sha,
                    expected_bytes, w4_head)
        for name, (expected_sha, expected_bytes) in W4_FILES.items()
    ]
    if any(item["status"] != "PASS" for item in w4_checks):
        raise ValueError("阶段4阳性冻结目录字节、清单或 HEAD blob 不一致")
    w4_manifest = load_json(w4_root / w4_manifest_path)
    w4_index = load_json(w4_root / w4_index_path)
    w4_package = load_json(w4_root / w4_package_path)
    package_sha = next(item["actual_sha256"] for item in w4_checks
                       if item["path"].endswith("task27_replay_result_package_positive.json"))
    if (w4_manifest.get("run_id") != "s4t27_replay_positive_20261027_r01"
            or w4_manifest.get("verdict") != "FROZEN_REPLAY_ONLY_WITH_DETECTIONS"
            or w4_manifest.get("exit_code") != 0
            or w4_index.get("run_id") != w4_manifest.get("run_id")
            or w4_index.get("package_sha256") != package_sha
            or w4_index.get("contract_binding", {}).get("revision") != "r07"
            or w4_index.get("contract_binding", {}).get("json_sha256") != contract_sha
            or w4_package.get("contract_binding", {}).get("revision") != "r07"
            or w4_package.get("contract_binding", {}).get("json_sha256") != contract_sha
            or w4_package.get("marking", {}).get("replay_only") is not True
            or w4_package.get("marking", {}).get("evidence_kind") != "offline_replay"
            or w4_package.get("marking", {}).get("buffer_scope") != "offline_host"):
        raise ValueError("阶段4阳性回放冻结标记或 r07 契约绑定不一致")
    gate_sha_expected = w4_index.get("gate_result_sha256")
    gate_sha_actual = sha256_file(w4_root / W4_GATE_RESULT)
    if (gate_sha_expected != gate_sha_actual
            or gate_sha_expected != w4_package.get("source_bindings", {}).get("gate_result_sha256")):
        raise ValueError("阶段4阳性包所绑定的冻结 gate result 字节不一致")

    w5_manifest_path = f"{W5_POSITIVE_DIR}/manifest.json"
    if sha256_file(w5_root / w5_manifest_path) != W5_MANIFEST_SHA256:
        raise ValueError("阶段5阳性消费清单 SHA-256 漂移")
    w5_manifest = load_json(w5_root / w5_manifest_path)
    if (w5_manifest.get("run_id") != "s5t03_stage4_positive_replay_20261027_r01"
            or w5_manifest.get("task_id") != "S5-T03"
            or w5_manifest.get("source_commit") != W5_SOURCE_COMMIT
            or w5_manifest.get("upstream", {}).get("run_id") != w4_manifest.get("run_id")
            or w5_manifest.get("upstream", {}).get("verdict") != w4_manifest.get("verdict")
            or w5_manifest.get("goal_reached") != "STAGE4_BOXED_FROZEN_REPLAY_CONSUMED_OFFLINE__CROSSCHECK_PASS"
            or w5_manifest.get("integrity", {}).get("all_pass") is not True):
        raise ValueError("阶段5阳性消费清单身份、来源或完整性结论不一致")
    declared = {row.get("path"): row for row in w5_manifest.get("files", [])}
    if set(declared) != set(W5_FILES):
        raise ValueError("阶段5阳性清单文件集合与预期六文件不一致")
    w5_checks = []
    for name, expected_sha in W5_FILES.items():
        row = declared[name]
        actual_sha = sha256_file(w5_root / W5_POSITIVE_DIR / name)
        actual_bytes = (w5_root / W5_POSITIVE_DIR / name).stat().st_size
        passed = actual_sha == expected_sha == row.get("sha256") and actual_bytes == row.get("bytes")
        w5_checks.append({
            "path": f"{W5_POSITIVE_DIR}/{name}",
            "expected_sha256": expected_sha,
            "manifest_sha256": row.get("sha256"),
            "actual_sha256": actual_sha,
            "manifest_bytes": row.get("bytes"),
            "actual_bytes": actual_bytes,
            "status": "PASS" if passed else "FAIL",
        })
    if any(item["status"] != "PASS" for item in w5_checks):
        raise ValueError("阶段5阳性消费文件 SHA/bytes 与清单不一致")

    frame_path = w5_root / W5_POSITIVE_DIR / "frames.jsonl"
    frame_lines = [line for line in frame_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(frame_lines) != 1:
        raise ValueError(f"阶段5阳性回放帧数不是 1：{len(frame_lines)}")
    frame = json.loads(frame_lines[0])
    key = w4_package.get("contract_result_key", {})
    box = (w4_package.get("detections", {}).get("boxes") or [{}])[0]
    frame_detections = frame.get("detections")
    if (frame.get("session_id") != key.get("session_id")
            or frame.get("frame_id") != key.get("frame_id")
            or frame.get("result_seq") != key.get("result_seq")
            or frame.get("state") != "PRESENT"
            or frame.get("detection_count") != 1
            or not isinstance(frame_detections, list) or len(frame_detections) != 1
            or frame_detections[0].get("class_id") != box.get("class_id")
            or frame_detections[0].get("class_name") != box.get("class_name")
            or frame_detections[0].get("score") != box.get("score")
            or frame_detections[0].get("xyxy") != box.get("xyxy")):
        raise ValueError("阶段5阳性帧主键/检测结果未与阶段4冻结包对应")
    marking = frame.get("marking", {})
    if (frame.get("input_kind") != "stage4_frozen_replay"
            or frame.get("consumption_mode") != "replay_only"
            or frame.get("evidence_kind") != "offline_replay"
            or marking.get("replay_only") is not True
            or marking.get("evidence_kind") != "offline_replay"
            or marking.get("buffer_scope") != "offline_host"):
        raise ValueError("阶段5阳性帧缺少 replay_only 范围标记")

    timing = frame.get("timing_basis", {})
    reasons = []
    capture = frame.get("capture_time_ns")
    if capture == 0 and timing.get("capture_time_ns", {}).get("defined") is not True:
        reasons.append("capture_time_ns=0 是 FILE_INJECTION 哨兵，不是测量采集时刻")
    result_time = frame.get("result_time_ns")
    if (result_time is None
            or timing.get("result_time_ns", {}).get("defined") is not True):
        reasons.append("result_time_ns 不可用，缺少阶段4契约同域发布时刻")
    if type(frame.get("stale")) is not bool:
        reasons.append("stale=null，阶段6不得默认解释为 fresh")
    if not reasons:
        reasons.append("阶段6适配语义未通过本次只读审计所需的保守时间字段闸门")
    w5_manifest_declared_sources = w5_manifest.get("sources")

    return {
        "schema_version": 1,
        "audit_kind": "S6-D latest positive replay readonly binding",
        "status": "PASS_BYTES_BLOCKED_INPUT",
        "consumption_eligibility": "BLOCKED",
        "stage4": {
            "current_head": w4_head,
            "contract_commit": W4_CONTRACT_COMMIT,
            "contract_path": W4_CONTRACT,
            "contract_sha256": contract_sha,
            "contract_revision": "r07",
            "freeze_run_id": w4_manifest.get("run_id"),
            "verdict": w4_manifest.get("verdict"),
            "manifest_path": w4_manifest_path,
            "freeze_index_path": w4_index_path,
            "package_path": w4_package_path,
            "gate_result_path": W4_GATE_RESULT,
            "gate_result_sha256": gate_sha_actual,
            "files": w4_checks,
        },
        "stage5": {
            "current_head": w5_head,
            "source_commit": W5_SOURCE_COMMIT,
            "source_commit_is_ancestor": True,
            "manifest_path": w5_manifest_path,
            "manifest_sha256": W5_MANIFEST_SHA256,
            "manifest_declares_sources_array": isinstance(w5_manifest_declared_sources, list),
            "source_binding_limit": (
                "manifest 未声明逐脚本 sources[] 哈希；仅绑定清单中的 source_commit 及其祖先关系，"
                "不声称阶段5阳性产物生成脚本已逐文件绑定。"
                if not isinstance(w5_manifest_declared_sources, list) else None
            ),
            "files": w5_checks,
        },
        "actual_positive_frame": frame,
        "eligibility_reasons": reasons,
        "core_execution": {
            "status": "NOT_RUN",
            "reason": "阳性帧时间字段不满足安全消费条件；未构造事件，未调用阶段6核心。",
        },
        "scope": "offline replay_only; no real-time, hardware, G3, T6-A03/P, 6-E or G4/G5 claim",
    }


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="阶段6阳性回放只读绑定审计")
    parser.add_argument("--w4-root", required=True)
    parser.add_argument("--w5-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    output = Path(args.output).resolve()
    try:
        result = audit(Path(args.w4_root).resolve(), Path(args.w5_root).resolve())
        result["output_path"] = str(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"阳性回放只读绑定审计失败：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": result["status"], "eligibility": result["consumption_eligibility"],
                      "output_path": str(output), "w4_files": len(result["stage4"]["files"]),
                      "w5_files": len(result["stage5"]["files"]),
                      "reasons": result["eligibility_reasons"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
