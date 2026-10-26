from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


CN = timezone(timedelta(hours=8))
CHECKER_VERSION = "r13"
WORKTREE = Path(r"D:\codex-worktrees\w4")
DBDF = Path(r"D:\codex-worktrees\dbdf")
EXPECTED_W4_BASELINE_COMMIT = "4c726f17d4a83df9e6fbd8b1a9863c0ac2fb256e"
HISTORIC_R10_EXPECTED_W4_HEAD = "33988ed7e8a97a9d5395b8cfd136a327c37d7dc9"
GOLDEN_RUN_ID = "s4t26_golden_rebind_20261026_r02"
GOLDEN_RUN_DIR = WORKTREE / "report/evidence/S4-CTRL" / GOLDEN_RUN_ID
GOLDEN_MANIFEST = GOLDEN_RUN_DIR / "golden_materialization_manifest.json"
GOLDEN_MANIFEST_SHA256 = "47e4cc362d174f1c8eb451197554e5978cd818032c3461af655f959f9fa108c6"
DECISION_RECORD = WORKTREE / "docs/stage4/s4t26_golden_rebind_decision_20261026_r01.md"
DECISION_RECORD_SHA256 = "819c9054be9bc3232d51666bc9e52e112fc3932b1d3a165d36040f26744356e1"
T25_INDEX_SHA256 = "2d76f9e284130c96374de6ea3525e0c92778b0f701c8894cd4d127234c8d3c72"
T29_REFERENCE_SHA256 = "26392c8d7f5ca8643a26c149411c66d6f2343a544f8c4f03d32584dc4e071d33"
T29_CONTROL_COMPARISON = WORKTREE / "report/evidence/S4-CTRL/s4t26_golden_control_20261026_r04/control_comparison.json"
T29_CONTROL_COMPARISON_SHA256 = "b4200da6e8a0e71fa539639f4114273cbf6aaaa8fcd2447b70c1e4ceb61e2589"
MAIN_T25_SHARDS = Path(r"D:\FPGA_Competition\report\evidence\S2A-T25\tensors")
TASK25_PACKAGE = Path("report/evidence/S3-T05/t05_replay_binding_20261025_r01")
TASK25_MANIFEST_SOURCE_COMMIT = "9dcb0229cdd5fdd968f91dfd200f1df92acaa9cd"
TASK25_PACKAGE_COMMIT = "584b07664e88a18bf786ba9565a138861e136d76"
TASK25_FRAME_COMMIT = "0ad2000cbc4af7b29f299c2277465bba608a8129"
TASK25_FRAME = Path("report/evidence/S3-T05/t05_stage3_window_20261024_r01/frame_full.bin")
TASK25_FRAME_SHA256 = "939fce22b7e86aa6356dc80d977626dcfe34ce8e9def8964ff03122d956752f0"
S4A_CONTRACT = WORKTREE / "docs/stage4/s4a_stage4_g0_fields.json"
S4A_CONTRACT_SHA256 = "657ea2fbd2587873c4b8161e50390bc4139d373b4496dbfe6d8611081d6930d5"
ACTIVATION_REPORT = WORKTREE / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_activation_calibration_r1.json"
ACTIVATION_REPORT_SHA256 = "6d73283c698a94dd30cf00634de59fb76a8e889916eb4d00e50b76c245687216"
REFERENCE_RUN = WORKTREE / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_int8_forward_r2.json"
REFERENCE_RUN_SHA256 = "3d5ccedc9dc25f62353711c75f509706187047dbd70321cefb98e0bc0ade3973"
BRIDGE_SOURCE = WORKTREE / "scripts/stage4_s4ctrl/replay_forward_bridge.py"
S4B_CONTRACT = WORKTREE / "docs/stage4/s4b_shared_input_result_contract.json"
PREEXISTING_PATHS = {
    ".codex/STATE.md",
    *[f"report/evidence/S4-B/s4b_ps_tensor_20261023_{run}/s4b_ps_tensor_diagnostic.{ext}"
      for run in ("r04", "r05", "r09", "r11", "r12", "r13") for ext in ("elf", "map")],
}
TASK_OWNED_UNCOMMITTED_PATHS = {
    "verification/check_s4t26_g0_inputs.py",
    "scripts/stage4_s4ctrl/replay_forward_bridge.py",
}
PREEXISTING_ARTIFACT_SHA256 = {
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.elf": "85dc56c409e2e2d09ba6579086b3475acf5f811f9cdf4d121ccc74ba4dc1a8dd",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.map": "00fcee65c8cebfdf8b7d1b96217d8612cb412ba1d4e68ea56a64a6cf74634c13",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r05/s4b_ps_tensor_diagnostic.elf": "f2280f7a834856f3c89ad5e955a6ed0c80b8d9932617abb9fe82bf8033e48654",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r05/s4b_ps_tensor_diagnostic.map": "ab9d7b8d06d0deb23bf62bc53efb729930ae0be40fddd34d9fd2a4b9adf9c49f",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r09/s4b_ps_tensor_diagnostic.elf": "e63cf0eea1110652d1152801e02dcf57cb06ba77aae096c6767eaf3f5c620d3b",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r09/s4b_ps_tensor_diagnostic.map": "d39f5e0c922602980d4a75b94da255eb555f8c39be90dbd1431ad910d2fe6bc7",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r11/s4b_ps_tensor_diagnostic.elf": "7b8c469c11dcadd30be1150e1cce35c199e02f2119c995aa822b60a0fd1074d8",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r11/s4b_ps_tensor_diagnostic.map": "dbc7ab15ead170b6644c6eb6478b15a0b48659100bea5857f67b859517e85865",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r12/s4b_ps_tensor_diagnostic.elf": "f61300d26dc0b66410b9348b5e96719e7c06061ce807cbc86a8149962471718e",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r12/s4b_ps_tensor_diagnostic.map": "0fbeab6d269a5f31cc50be5c00e8bf4671bfbe99975cfe7e15e190f605d45b00",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r13/s4b_ps_tensor_diagnostic.elf": "bfe88660a7c9b16b4d4360ccf33a7540ee215b7d2ae940408b24bdf83c15ec07",
    "report/evidence/S4-B/s4b_ps_tensor_20261023_r13/s4b_ps_tensor_diagnostic.map": "4a0f9cf8e281482a70459f5e247c9b42863bff058b91c38eb7fcf832fcc1d62d",
}
KNOWN_PYTHONS = [
    Path(r"C:\Users\22061\anaconda3\python.exe"),
    Path(r"C:\Users\22061\anaconda3\envs\dl_env\python.exe"),
    Path(r"C:\Users\22061\anaconda3\pkgs\python-3.11.15-h1044e36_0\python.exe"),
    Path(r"C:\Users\22061\anaconda3\pkgs\python-3.7.0-hea74fb7_0\python.exe"),
    Path(r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe"),
    Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


class MissingInputError(Exception):
    """表示 G0 必需输入缺失或无法只读取得。"""


class IntegrityError(Exception):
    """表示冻结输入存在字节或绑定不一致。"""


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise MissingInputError(f"缺少必需文件：{label}；精确路径={path}")


def optional_sha256_file(path: Path) -> str | None:
    try:
        return sha256_file(path) if path.is_file() else None
    except OSError:
        return None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def git_text(tree: Path, *args: str) -> str:
    result = run(["git", "-C", str(tree), *args])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout.decode("utf-8", errors="replace").strip()


def git_object_sha256(tree: Path, commit: str, relpath: str) -> str:
    result = run(["git", "-C", str(tree), "show", f"{commit}:{relpath}"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return sha256_bytes(result.stdout)


def git_is_ancestor(tree: Path, ancestor: str, descendant: str) -> bool:
    result = run(["git", "-C", str(tree), "merge-base", "--is-ancestor", ancestor, descendant])
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.returncode == 0


def add_check(checks: list[dict[str, Any]], name: str, status: str, detail: Any) -> None:
    checks.append({"name": name, "status": status, "detail": detail})


def probe_cv2() -> list[dict[str, Any]]:
    probes = []
    code = "import cv2; print(cv2.__version__)"
    for interpreter in KNOWN_PYTHONS:
        row: dict[str, Any] = {"interpreter": str(interpreter), "command": [str(interpreter), "-B", "-c", code]}
        if not interpreter.is_file():
            row.update({"status": "MISSING", "exit_code": None, "stdout": "", "stderr": "解释器文件不存在"})
        else:
            result = run([str(interpreter), "-B", "-c", code])
            stdout = result.stdout.decode("utf-8", errors="replace").strip()
            stderr = result.stderr.decode("utf-8", errors="replace").strip()
            row.update({"status": "AVAILABLE" if result.returncode == 0 else "UNAVAILABLE",
                        "exit_code": result.returncode, "stdout": stdout, "stderr": stderr})
        probes.append(row)
    return probes


def verify_contract_assets() -> dict[str, Any]:
    require_file(S4A_CONTRACT, "S4-A 冻结契约")
    contract = load_json(S4A_CONTRACT)
    if sha256_file(S4A_CONTRACT) != S4A_CONTRACT_SHA256:
        raise IntegrityError("S4-A 契约 SHA 与 task-26 固定引用不符")
    by_id = {item.get("id"): item for item in contract.get("upstream_bindings", [])}
    ids = ["s2a_external_cfg", "s2a_external_darknet_weights", "s2a_external_gf8", "s2a_external_calibration_list"]
    assets = {}
    for item_id in ids:
        item = by_id.get(item_id)
        if not item:
            assets[item_id] = {"status": "BLOCKED", "reason": "缺少必需冻结绑定"}
            continue
        if not item.get("path"):
            assets[item_id] = {"status": "BLOCKED", "reason": "冻结绑定缺少 path 字段"}
            continue
        path = Path(item["path"])
        if not path.is_file():
            assets[item_id] = {"path": str(path), "contract_sha256": item.get("sha256"),
                               "actual_sha256": None, "bytes": None, "status": "BLOCKED",
                               "reason": "冻结绑定目标文件缺失"}
            continue
        actual = sha256_file(path) if path.is_file() else None
        assets[item_id] = {"path": str(path), "contract_sha256": item.get("sha256"),
                           "actual_sha256": actual, "bytes": path.stat().st_size if path.is_file() else None,
                           "status": "PASS" if actual == str(item.get("sha256", "")).lower() else "FAIL"}
    calib_item = by_id.get("s2a_external_calibration_list", {})
    calibration_path = Path(calib_item["path"]) if calib_item.get("path") else None
    calibration_lines: list[str] = []
    if calibration_path and calibration_path.is_file():
        calibration_lines = [line.strip() for line in calibration_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    require_file(ACTIVATION_REPORT, "冻结 activation report")
    activation = load_json(ACTIVATION_REPORT)
    source_inputs = activation.get("inputs", {})
    activation_sources = {}
    source_pairs = [(key, key[:-7]) for key in source_inputs if key.endswith("_sha256")]
    for hash_key, path_key in source_pairs:
        source_path = Path(source_inputs.get(path_key, ""))
        expected = str(source_inputs.get(hash_key, "")).lower()
        actual = sha256_file(source_path) if source_path.is_file() else None
        activation_sources[path_key] = {"path": str(source_path), "expected_sha256": expected,
                                        "actual_sha256": actual,
                                        "status": ("BLOCKED" if not source_path.is_file() or not expected
                                                   else "PASS" if actual == expected else "FAIL")}
    activation_sha = sha256_file(ACTIVATION_REPORT)
    parameter_keys = {"cfg", "weights", "calibration_list", "stats_csv"}
    parameter_sources_ok = all(activation_sources.get(key, {}).get("status") == "PASS" for key in parameter_keys)
    producer_sources_ok = all(activation_sources.get(key, {}).get("status") == "PASS"
                              for key in ("darknet_executable", "activation_hook_source"))
    return {
        "s4a_contract": {"path": str(S4A_CONTRACT), "sha256": sha256_file(S4A_CONTRACT),
                          "expected_sha256": S4A_CONTRACT_SHA256, "status": contract.get("status"),
                          "revision": contract.get("revision")},
        "assets": assets,
        "calibration_list": {"path": str(calibration_path) if calibration_path else None,
                             "line_count": len(calibration_lines), "unique_line_count": len(set(calibration_lines)),
                             "first_sample_entry": calibration_lines[0] if calibration_lines else None},
        "activation_report": {"path": str(ACTIVATION_REPORT), "expected_sha256": ACTIVATION_REPORT_SHA256,
                              "actual_sha256": activation_sha,
                              "hash_matches": activation_sha == ACTIVATION_REPORT_SHA256,
                              "parameter_inputs_match": parameter_sources_ok,
                              "producer_sources_match": producer_sources_ok,
                              "inputs": activation_sources, "status": activation.get("status")},
    }


def verify_task25_package() -> dict[str, Any]:
    package_dir = DBDF / TASK25_PACKAGE
    manifest_path = package_dir / "delivery_manifest.json"
    binding_path = package_dir / "replay_input_binding.json"
    require_file(manifest_path, "task-25 delivery_manifest.json")
    require_file(binding_path, "task-25 replay_input_binding.json")
    frame_disk = DBDF / TASK25_FRAME
    require_file(frame_disk, "task-25 固定来源帧")
    manifest = load_json(manifest_path)
    binding = load_json(binding_path)
    if not isinstance(manifest, dict) or not isinstance(binding, dict):
        raise IntegrityError("task-25 manifest/binding 顶层必须是 JSON 对象")
    manifest_source_commit = str(manifest.get("source_commit", ""))
    package_commit = TASK25_PACKAGE_COMMIT
    binding_commit = str(binding.get("source_commit", ""))
    declared_files = []
    files_ok = True
    manifest_files = manifest.get("files")
    manifest_missing_fields = [key for key in ("source_commit", "files") if key not in manifest]
    if not isinstance(manifest_files, list) or not manifest_files:
        manifest_missing_fields.append("files[]")
        manifest_files = []
    for item in manifest_files:
        if not isinstance(item, dict) or not item.get("path") or not item.get("sha256"):
            files_ok = False
            declared_files.append({"entry": item, "status": "BLOCKED", "reason": "清单文件项缺少 path/sha256"})
            continue
        rel = Path(item["path"])
        if rel.is_absolute() or ".." in rel.parts:
            files_ok = False
            declared_files.append({"path": item["path"], "status": "INVALID_PATH"})
            continue
        disk_path = DBDF / rel
        if not disk_path.is_file():
            files_ok = False
            declared_files.append({"path": item["path"], "expected_sha256": str(item["sha256"]).lower(),
                                   "disk_sha256": None, "status": "BLOCKED", "reason": "清单所列输入文件缺失"})
            continue
        disk_sha = sha256_file(disk_path)
        commit_sha = git_object_sha256(DBDF, package_commit, item["path"])
        expected_sha = str(item.get("sha256", "")).lower()
        ok = disk_sha == expected_sha == commit_sha
        files_ok = files_ok and ok
        declared_files.append({"path": item["path"], "expected_sha256": expected_sha,
                               "disk_sha256": disk_sha, "manifest_commit_sha256": commit_sha,
                               "status": "PASS" if ok else "FAIL"})
    frame_disk_sha = sha256_file(frame_disk) if frame_disk.is_file() else None
    frame_commit_sha = git_object_sha256(DBDF, TASK25_FRAME_COMMIT, TASK25_FRAME.as_posix())
    required = ["schema_version", "task_id", "input_id", "source_kind", "mode", "timing_claim_scope",
                "source_worktree", "source_commit", "source_frame_path", "source_frame_sha256",
                "source_frame_size_bytes", "frame_integrity", "source_frame_id", "width", "height",
                "stride_bytes", "pixel_format", "byte_order", "coordinate_origin", "capture_time_available",
                "source_capture_time_text", "source_capture_time_precision", "capture_time_ns", "clock_domain",
                "timestamp_source", "limitations"]
    missing_fields = [key for key in required if key not in binding]
    expected_values = {"task_id": "task-25", "source_kind": "camera", "mode": "offline_replay",
                       "timing_claim_scope": "replay_only", "source_frame_id": 1, "width": 1280,
                       "height": 720, "stride_bytes": 3840, "pixel_format": "BGR888",
                       "byte_order": "BGR", "coordinate_origin": "top_left",
                       "capture_time_available": True, "source_capture_time_precision": "one_second_as_recorded",
                       "clock_domain": "replay_documented_wallclock"}
    semantic_mismatches = {key: {"expected": value, "actual": binding.get(key)}
                           for key, value in expected_values.items() if binding.get(key) != value}
    frame_integrity = binding.get("frame_integrity")
    if not isinstance(frame_integrity, dict):
        frame_integrity = {}
    frame_ok = (frame_disk_sha == TASK25_FRAME_SHA256 == frame_commit_sha
                and binding.get("source_frame_sha256") == TASK25_FRAME_SHA256
                and frame_integrity.get("value") == TASK25_FRAME_SHA256
                and binding.get("source_frame_size_bytes") == 2764800
                and frame_integrity.get("length_bytes") == 2764800
                and not semantic_mismatches)
    current_dbdf_head = git_text(DBDF, "rev-parse", "HEAD")
    index_path_text = git_text(DBDF, "rev-parse", "--git-path", "index")
    index_path = Path(index_path_text)
    if not index_path.is_absolute():
        index_path = DBDF / index_path
    index_sha_before = sha256_file(index_path) if index_path.is_file() else None
    status_result = run(["git", "--no-optional-locks", "-C", str(DBDF), "status", "--short",
                         "--untracked-files=all", "--", TASK25_PACKAGE.as_posix(), TASK25_FRAME.as_posix()])
    if status_result.returncode != 0:
        raise MissingInputError("无法只读核验 task-25 工作树状态：" +
                                 status_result.stderr.decode("utf-8", errors="replace").strip())
    package_worktree_status = status_result.stdout.decode("utf-8", errors="replace").strip()
    index_sha_after = sha256_file(index_path) if index_path.is_file() else None
    package_is_ancestor = git_is_ancestor(DBDF, package_commit, current_dbdf_head)
    frame_is_ancestor = git_is_ancestor(DBDF, TASK25_FRAME_COMMIT, current_dbdf_head)
    commits_ok = (manifest_source_commit == TASK25_MANIFEST_SOURCE_COMMIT
                  and git_text(DBDF, "cat-file", "-e", f"{manifest_source_commit}^{{commit}}") == ""
                  and git_text(DBDF, "cat-file", "-e", f"{package_commit}^{{commit}}") == ""
                  and git_text(DBDF, "cat-file", "-e", f"{TASK25_FRAME_COMMIT}^{{commit}}") == "")
    if manifest_missing_fields or missing_fields or any(item.get("status") == "BLOCKED" for item in declared_files):
        package_status = "BLOCKED"
    elif (not frame_ok or not files_ok or not commits_ok or not package_is_ancestor or not frame_is_ancestor
          or package_worktree_status or index_sha_before != index_sha_after):
        package_status = "FAIL"
    else:
        package_status = "PASS"
    return {
        "package_path": str(package_dir), "package_commit": package_commit,
        "manifest_source_commit": manifest_source_commit,
        "package_commit_is_ancestor_of_observed_dbdf_head": package_is_ancestor,
        "frame_commit_is_ancestor_of_observed_dbdf_head": frame_is_ancestor,
        "package_and_frame_worktree_status": package_worktree_status,
        "dbdf_index_read_only_check": {"git_option": "--no-optional-locks", "index_path": str(index_path),
                                        "sha256_before": index_sha_before, "sha256_after": index_sha_after,
                                        "unchanged": index_sha_before == index_sha_after},
        "package_commit_exists": commits_ok, "package_manifest_sha256": sha256_file(manifest_path),
        "binding_sha256": sha256_file(binding_path), "manifest_files": declared_files,
        "manifest_missing_fields": manifest_missing_fields,
        "all_manifest_files_match_disk_and_commit": files_ok,
        "frame": {"path": str(frame_disk), "source_commit": binding_commit,
                  "required_source_commit": TASK25_FRAME_COMMIT, "expected_sha256": TASK25_FRAME_SHA256,
                  "disk_sha256": frame_disk_sha, "source_commit_sha256": frame_commit_sha,
                  "size_bytes": frame_disk.stat().st_size if frame_disk.is_file() else None,
                  "commit_is_ancestor_of_observed_dbdf_head": frame_is_ancestor,
                  "status": "PASS" if frame_ok and binding_commit == TASK25_FRAME_COMMIT
                  and frame_is_ancestor else "FAIL"},
        "input_interface_fields": {"required": required, "missing": missing_fields,
                                   "source_kind": binding.get("source_kind"), "mode": binding.get("mode"),
                                   "timing_claim_scope": binding.get("timing_claim_scope"),
                                   "dimensions": [binding.get("width"), binding.get("height")],
                                   "stride_bytes": binding.get("stride_bytes"),
                                   "pixel_format": binding.get("pixel_format"),
                                   "byte_order": binding.get("byte_order"),
                                   "capture_time_available": binding.get("capture_time_available"),
                                   "capture_time_ns": binding.get("capture_time_ns"),
                                   "clock_domain": binding.get("clock_domain")},
        "semantic_mismatches": semantic_mismatches,
        "interfaces_declared_by_package": manifest.get("interfaces"),
        "interfaces_not_applicable_reason": manifest.get("interfaces_not_applicable_reason"),
        "current_dbdf_head_observed_only": current_dbdf_head,
        "status": package_status,
    }


def verify_rebound_goldens() -> dict[str, Any]:
    """核验批准的双样本决策与 T25/T29 原始张量材料化结果。"""
    require_file(DECISION_RECORD, "批准的黄金来源与样本改绑决策")
    decision_sha = sha256_file(DECISION_RECORD)
    decision_text = DECISION_RECORD.read_text(encoding="utf-8")
    if decision_sha != DECISION_RECORD_SHA256:
        raise IntegrityError("decision 记录 SHA 与固定批准记录不符")
    required_decision_text = (
        "当前 Darknet/hook 未复现 T29，不作为 task-26 黄金来源",
        "NOT_USED_HISTORICAL",
        "负样本不得替代阳性检测/显示覆盖",
        "raw_head_gate",
        "positive_detection_gate",
    )
    missing_decision_text = [value for value in required_decision_text if value not in decision_text]
    if missing_decision_text:
        raise IntegrityError(f"decision 未明确记录所需裁决：{missing_decision_text}")

    require_file(GOLDEN_MANIFEST, "冻结 head 材料化清单")
    manifest_sha = sha256_file(GOLDEN_MANIFEST)
    if manifest_sha != GOLDEN_MANIFEST_SHA256:
        raise IntegrityError("黄金材料化清单 SHA 与固定 RunId 不符")
    manifest = load_json(GOLDEN_MANIFEST)
    if manifest.get("run_id") != GOLDEN_RUN_ID or manifest.get("status") != "MATERIALIZED_AND_SHA_VERIFIED":
        raise IntegrityError("材料化清单 RunId/status 不匹配")
    if manifest.get("decision_record") != {
        "path": "docs/stage4/s4t26_golden_rebind_decision_20261026_r01.md",
        "sha256": decision_sha,
    }:
        raise IntegrityError("材料化清单未绑定当前 decision SHA")
    if manifest.get("gates") != {
        "raw_head_gate": "approved_no_hand_001",
        "positive_detection_gate": "test_fist_000",
        "negative_gate_cannot_replace_positive_detection_or_display_coverage": True,
    }:
        raise IntegrityError("材料化清单双样本门绑定不匹配")
    if manifest.get("old_calibration", {}).get("status") != "NOT_USED_HISTORICAL":
        raise IntegrityError("旧校准样本未明确标为 NOT_USED_HISTORICAL")
    if (manifest.get("old_calibration", {}).get("sample_id")
            != "98529267-1eda-43a6-8e38-245947ecb312"
            or manifest.get("old_calibration", {}).get("sha256") != "c116ba1d...35ee70b"):
        raise IntegrityError("旧校准样本历史身份/SHA 注记不匹配")

    t25_path = WORKTREE / "report/evidence/S2A-T25/cpu_layer_golden_index.json"
    t29_path = WORKTREE / "report/evidence/S2A-T29/cpu_decode_nms_reference.json"
    require_file(t25_path, "T25 冻结索引")
    require_file(t29_path, "T29 冻结检测/NMS 参考")
    if sha256_file(t25_path) != T25_INDEX_SHA256 or sha256_file(t29_path) != T29_REFERENCE_SHA256:
        raise IntegrityError("T25/T29 冻结索引字节 SHA 不匹配")
    declared_sources = manifest.get("frozen_sources", {})
    if (declared_sources.get("t25_index") != {
            "path": "report/evidence/S2A-T25/cpu_layer_golden_index.json",
            "sha256": T25_INDEX_SHA256,
        }
            or declared_sources.get("t29_reference") != {
                "path": "report/evidence/S2A-T29/cpu_decode_nms_reference.json",
                "sha256": T29_REFERENCE_SHA256,
            }
            or declared_sources.get("source_mutation") != "NONE"):
        raise IntegrityError("材料化清单的 T25/T29 来源绑定不匹配")
    t25 = load_json(t25_path)
    t29 = load_json(t29_path)
    expected_samples = {
        "approved_no_hand_001": {
            "gate": "raw_head_gate", "sample_index": 102,
            "image_path": r"D:\FPGA_Data\HaGRIDv2\user_no_hand\20260915_friend_001.png",
            "image_sha256": "10f1f104343cae97abf817316de3a75bacb646da6c686a2204eedcc2611f34f4",
            "shard_sha256": "50910134351acd1d8ab70ffd7129a13a0553440316efee572f34fceb5e6f79d6",
            "stream_sha256": "7e1e75a903e3c65a3449c9e78295225768e75a90633d5982267ebdddc4b8cd69",
            "heads": {
                "head13": {"sha256": "902bb209b285cf46b5adb17e8051035aae0bcc3cca88ee9a7fe650737330ea6d",
                           "shape": [1, 30, 13, 13], "scale": 0.24267549589862975,
                           "offset": 10772736, "length": 5070},
                "head26": {"sha256": "f96cca6678114df8e997847bfeb244664a9cb583ebf120990774cb680277e1c2",
                           "shape": [1, 30, 26, 26], "scale": 0.30223452951025775,
                           "offset": 11361870, "length": 20280},
            },
        },
        "test_fist_000": {
            "gate": "positive_detection_gate", "sample_index": 0,
            "image_path": r"D:\FPGA_Data\HaGRIDv2\dataset\fist\fist\c39c0301-d0ed-4d34-97a0-84c93dd0f515.jpg",
            "image_sha256": "6dbd72693bc6ad2af6121ffe95e2ee5e9c14597a4c4d16a6db8cdf07d8e43b0e",
            "shard_sha256": "49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e",
            "stream_sha256": "090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80",
            "heads": {
                "head13": {"sha256": "07b59ca389890e8ac2ac704d97364e9717164becbbe90950dc10e9ed28d2cab6",
                           "shape": [1, 30, 13, 13], "scale": 0.24267549589862975,
                           "offset": 10772736, "length": 5070},
                "head26": {"sha256": "7524ce5c60a1a0af3b7275dda1481158f808c1d2354141a66c10de2afe7be14e",
                           "shape": [1, 30, 26, 26], "scale": 0.30223452951025775,
                           "offset": 11361870, "length": 20280},
            },
        },
    }
    if not isinstance(manifest.get("goldens"), list) or len(manifest["goldens"]) != 4:
        raise IntegrityError("材料化清单未包含且仅包含四个 head 文件")
    entries_by_key = {
        (row.get("sample_id"), Path(str(row.get("file", ""))).stem.removeprefix(
            f"{row.get('sample_id', '')}_")): row
        for row in manifest["goldens"] if isinstance(row, dict)
    }
    if len(entries_by_key) != 4:
        raise IntegrityError("材料化清单存在重复或非法 head 项")
    t25_samples = {(row.get("sample_index"), row.get("sample_id")): row
                   for row in t25.get("samples", []) if isinstance(row, dict)}
    t29_samples = {row.get("sample_id"): row
                   for row in t29.get("samples", []) if isinstance(row, dict)}
    verified_samples: dict[str, Any] = {}
    for sample_id, expected in expected_samples.items():
        sample = t25_samples.get((expected["sample_index"], sample_id))
        reference = t29_samples.get(sample_id)
        if not isinstance(sample, dict) or not isinstance(reference, dict):
            raise MissingInputError(f"T25/T29 缺少冻结样本记录：{sample_id}")
        if str(sample.get("original_input", {}).get("sha256", "")).lower() != expected["image_sha256"]:
            raise IntegrityError(f"T25 样本图像 SHA 绑定不匹配：{sample_id}")
        image_path = Path(expected["image_path"])
        require_file(image_path, f"冻结样本图像 {sample_id}")
        image_sha = sha256_file(image_path)
        if image_sha != expected["image_sha256"]:
            raise IntegrityError(f"冻结样本图像 SHA 不匹配：{sample_id}")
        shard_record = sample.get("network", {}).get("compressed_shard", {})
        if shard_record.get("sha256") != expected["shard_sha256"]:
            raise IntegrityError(f"T25 分片记录 SHA 不匹配：{sample_id}")
        shard_path = MAIN_T25_SHARDS / Path(str(shard_record.get("path", ""))).name
        require_file(shard_path, f"T25 冻结压缩分片 {sample_id}")
        compressed = shard_path.read_bytes()
        compressed_sha = sha256_bytes(compressed)
        if compressed_sha != expected["shard_sha256"] or len(compressed) != shard_record.get("compressed_bytes"):
            raise IntegrityError(f"T25 压缩分片字节 SHA/长度不匹配：{sample_id}")
        try:
            raw_stream = zlib.decompress(compressed)
        except zlib.error as exc:
            raise IntegrityError(f"T25 分片无法解压：{sample_id}: {exc}") from exc
        raw_sha = sha256_bytes(raw_stream)
        if (raw_sha != expected["stream_sha256"]
                or raw_sha != shard_record.get("decompressed_sha256")
                or raw_sha != sample.get("network", {}).get("raw_stream_sha256")
                or len(raw_stream) != shard_record.get("decompressed_bytes")):
            raise IntegrityError(f"T25 解压整流 SHA/长度不匹配：{sample_id}")
        verified_heads = {}
        for name, head_expected in expected["heads"].items():
            t25_tensor = next((row for row in sample.get("network", {}).get("tensors", [])
                               if row.get("layer_index") == (29 if name == "head13" else 36)), None)
            t29_tensor = reference.get("head_tensors", {}).get(name)
            if not isinstance(t25_tensor, dict) or not isinstance(t29_tensor, dict):
                raise MissingInputError(f"T25/T29 缺少 {sample_id} {name} 定义")
            if (t25_tensor.get("shape_nchw") != head_expected["shape"]
                    or t25_tensor.get("scale") != head_expected["scale"]
                    or t25_tensor.get("byte_offset") != head_expected["offset"]
                    or t25_tensor.get("byte_length") != head_expected["length"]
                    or t25_tensor.get("tensor_sha256") != head_expected["sha256"]
                    or t29_tensor.get("shape_nchw") != head_expected["shape"]
                    or t29_tensor.get("int8_scale") != head_expected["scale"]
                    or t29_tensor.get("byte_offset") != head_expected["offset"]
                    or t29_tensor.get("byte_length") != head_expected["length"]
                    or t29_tensor.get("tensor_sha256") != head_expected["sha256"]):
                raise IntegrityError(f"T25/T29 张量元数据不匹配：{sample_id} {name}")
            entry = entries_by_key.get((sample_id, name))
            expected_relpath = f"golden/{sample_id}_{name}.bin"
            if (not isinstance(entry, dict) or entry.get("gate") != expected["gate"]
                    or entry.get("sample_index") != expected["sample_index"]
                    or entry.get("name") != name
                    or entry.get("file") != expected_relpath
                    or entry.get("source_image_path") != str(image_path)
                    or entry.get("source_image_sha256") != expected["image_sha256"]
                    or entry.get("sha256") != head_expected["sha256"]
                    or entry.get("shape_nchw") != head_expected["shape"]
                    or entry.get("scale") != head_expected["scale"]
                    or entry.get("byte_offset") != head_expected["offset"]
                    or entry.get("byte_length") != head_expected["length"]
                    or entry.get("t25_shard_path") != shard_record.get("path")
                    or entry.get("t25_shard_sha256") != expected["shard_sha256"]
                    or entry.get("t25_decompressed_stream_sha256") != expected["stream_sha256"]
                    or entry.get("t25_tensor_sha256") != head_expected["sha256"]
                    or entry.get("t29_tensor_sha256") != head_expected["sha256"]):
                raise IntegrityError(f"材料化清单绑定错误：{sample_id} {name}")
            golden_path = GOLDEN_RUN_DIR / expected_relpath
            require_file(golden_path, f"材料化 raw {name} {sample_id}")
            golden_bytes = golden_path.read_bytes()
            start = head_expected["offset"]
            expected_bytes = raw_stream[start:start + head_expected["length"]]
            if (len(golden_bytes) != head_expected["length"]
                    or sha256_bytes(golden_bytes) != head_expected["sha256"]
                    or golden_bytes != expected_bytes):
                raise IntegrityError(f"材料化文件不是 T25 原始切片或 SHA 错误：{sample_id} {name}")
            verified_heads[name] = {"path": str(golden_path), "sha256": sha256_bytes(golden_bytes),
                                    "shape_nchw": head_expected["shape"], "scale": head_expected["scale"],
                                    "byte_offset": start, "byte_length": len(golden_bytes),
                                    "byte_identical_to_t25_slice": True,
                                    "t25_tensor_sha256": t25_tensor["tensor_sha256"],
                                    "t29_tensor_sha256": t29_tensor["tensor_sha256"]}
        verified_samples[sample_id] = {
            "gate": expected["gate"], "sample_index": expected["sample_index"],
            "image_path": str(image_path), "image_sha256": image_sha,
            "compressed_shard_sha256": compressed_sha, "decompressed_stream_sha256": raw_sha,
            "heads": verified_heads,
        }
    return {
        "status": "PASS", "decision_record": {"path": str(DECISION_RECORD), "sha256": decision_sha},
        "materialization_manifest": {"path": str(GOLDEN_MANIFEST), "sha256": manifest_sha},
        "source_indexes": {"t25_index_sha256": sha256_file(t25_path),
                           "t29_reference_sha256": sha256_file(t29_path)},
        "gates": verified_samples,
        "old_calibration_sample": {"sample_id": "98529267-1eda-43a6-8e38-245947ecb312",
                                    "sha256": "c116ba1d...35ee70b", "status": "NOT_USED_HISTORICAL"},
        "source_policy": "当前 Darknet/hook 控制未复现 T29；只消费 T25/T29 冻结张量，不以当前 Darknet 生成黄金",
    }


def verify_darknet_control_not_golden() -> dict[str, Any]:
    """确认历史 r04 Darknet 对拍失败并据此排除其黄金来源资格。"""
    require_file(T29_CONTROL_COMPARISON, "r04 Darknet/T29 控制失败证据")
    actual_sha = sha256_file(T29_CONTROL_COMPARISON)
    if actual_sha != T29_CONTROL_COMPARISON_SHA256:
        raise IntegrityError("r04 Darknet 控制对拍证据 SHA 变化")
    comparison = load_json(T29_CONTROL_COMPARISON)
    layers = comparison.get("layers", {})
    expected = {"29": 2929, "36": 10358}
    observed = {key: layers.get(key, {}).get("mismatch_count") for key in expected}
    valid = (comparison.get("status") == "BLOCKED_MISMATCH"
             and comparison.get("all_control_heads_byte_identical") is False
             and comparison.get("next_step_allowed_only_if_pass") is False
             and observed == expected
             and all(layers.get(key, {}).get("byte_equal") is False for key in expected))
    if not valid:
        raise IntegrityError("r04 控制失败状态/差异数不再匹配")
    return {
        "status": "PASS", "run_id": comparison.get("run_id"),
        "comparison_sha256": actual_sha, "producer_exe_sha256": comparison.get("producer_exe_sha256"),
        "producer_hook_sha256": comparison.get("producer_hook_sha256"),
        "layers": observed, "all_control_heads_byte_identical": False,
        "conclusion": "Darknet 控制未复现 T29，当前 Darknet/hook 不作为黄金来源",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="task-26 G0 冻结输入只读预检")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"s4t26_g0_inputs_20261026_r[0-9]{2}", args.run_id):
        print("[FAIL] run-id 不符合本轮固定命名范围", file=sys.stderr)
        return 1
    run_dir = WORKTREE / "report/evidence/S4-CTRL" / args.run_id
    if run_dir.exists():
        print(f"[FAIL] 目标 RunId 已存在，拒绝覆盖：{run_dir}", file=sys.stderr)
        return 1
    run_dir.mkdir(parents=True)

    checks: list[dict[str, Any]] = []
    w4_head = git_text(WORKTREE, "rev-parse", "HEAD")
    w4_branch = git_text(WORKTREE, "branch", "--show-current")
    baseline_commit_exists = (git_text(WORKTREE, "cat-file", "-e",
                                       f"{EXPECTED_W4_BASELINE_COMMIT}^{{commit}}") == "")
    baseline_is_ancestor = git_is_ancestor(WORKTREE, EXPECTED_W4_BASELINE_COMMIT, w4_head)
    baseline_ok = (w4_branch == "stage4-infer-prep" and baseline_commit_exists
                   and baseline_is_ancestor)
    add_check(checks, "task_baseline", "PASS" if baseline_ok else "FAIL",
              {"head_observed": w4_head,
               "expected_reviewed_baseline_commit": EXPECTED_W4_BASELINE_COMMIT,
               "expected_baseline_commit_exists": baseline_commit_exists,
               "expected_baseline_is_ancestor_of_observed_head": baseline_is_ancestor,
               "historical_r10_expected_head_not_current_baseline": HISTORIC_R10_EXPECTED_W4_HEAD,
               "branch": w4_branch, "required_branch": "stage4-infer-prep",
               "interpretation": "固定审查基线必须存在且为当前观测 HEAD 的祖先；r10 的 33988ed 仅作历史记录"})

    try:
        contract_assets = verify_contract_assets()
    except MissingInputError as exc:
        contract_assets = None
        add_check(checks, "frozen_parameter_sources", "BLOCKED", {"reason": str(exc)})
    except IntegrityError as exc:
        contract_assets = None
        add_check(checks, "frozen_parameter_sources", "FAIL", {"reason": str(exc)})
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        contract_assets = None
        add_check(checks, "frozen_parameter_sources", "BLOCKED",
                  {"reason": f"冻结参数输入无法读取或缺少字段：{type(exc).__name__}: {exc}"})
    if contract_assets is not None:
        assets_blocked = any(item.get("status") == "BLOCKED" for item in contract_assets["assets"].values())
        assets_fail = any(item.get("status") == "FAIL" for item in contract_assets["assets"].values())
        assets_ok = (not assets_blocked and not assets_fail
                     and all(item.get("status") == "PASS" for item in contract_assets["assets"].values())
                     and contract_assets["activation_report"]["hash_matches"]
                     and contract_assets["activation_report"]["parameter_inputs_match"]
                     and contract_assets["calibration_list"]["line_count"] == 512
                     and contract_assets["calibration_list"]["unique_line_count"] == 512)
        parameter_status = "PASS" if assets_ok else "FAIL" if assets_fail else "BLOCKED"
        add_check(checks, "frozen_parameter_sources", parameter_status, contract_assets)
        producer_sources_ok = contract_assets["activation_report"]["producer_sources_match"]
        add_check(checks, "activation_producer_provenance", "PASS" if producer_sources_ok else "BLOCKED",
                  {"reason": "activation report 记录的生成可执行文件或 hook 源码 SHA 与固定路径当前字节不符" if not producer_sources_ok else None,
                   "mismatches": {key: value for key, value in contract_assets["activation_report"]["inputs"].items()
                                  if value["status"] != "PASS"}})

    try:
        task25 = verify_task25_package()
        add_check(checks, "task25_replay_input_package", task25["status"], task25)
    except (MissingInputError, IntegrityError, OSError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
        task25 = None
        add_check(checks, "task25_replay_input_package", "BLOCKED",
                  {"reason": f"task-25 固定输入无法完整核验：{type(exc).__name__}: {exc}"})

    try:
        rebound_goldens = verify_rebound_goldens()
        add_check(checks, "approved_rebound_gate_goldens", "PASS", rebound_goldens)
    except (MissingInputError, IntegrityError, OSError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
        add_check(checks, "approved_rebound_gate_goldens", "BLOCKED",
                  {"reason": f"批准样本或 T25/T29 材料化黄金无法完整核验：{type(exc).__name__}: {exc}",
                   "raw_head_gate": "approved_no_hand_001/sample_102",
                   "positive_detection_gate": "test_fist_000/sample_000",
                   "legacy_calibration_sample_status": "NOT_USED_HISTORICAL"})

    try:
        control = verify_darknet_control_not_golden()
        add_check(checks, "darknet_control_not_golden_source", "PASS", control)
    except (MissingInputError, IntegrityError, OSError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
        add_check(checks, "darknet_control_not_golden_source", "BLOCKED",
                  {"reason": f"r04 控制失败证据无法确认：{type(exc).__name__}: {exc}",
                   "required_interpretation": "Darknet 控制未复现 T29，不作为黄金来源"})

    try:
        probes = probe_cv2()
    except OSError as exc:
        probes = []
        add_check(checks, "existing_cv2_interpreter", "BLOCKED",
                  {"reason": f"无法检查既有解释器：{type(exc).__name__}: {exc}"})
    cv2_available = any(row.get("status") == "AVAILABLE" for row in probes)
    if probes:
        add_check(checks, "existing_cv2_interpreter", "PASS" if cv2_available else "BLOCKED",
                  {"probes": probes, "scope_note": "核验 task-26 已声明的既有解释器候选；未安装或修改依赖"})

    try:
        require_file(BRIDGE_SOURCE, "固定版本回放桥接入口")
        source_text = BRIDGE_SOURCE.read_text(encoding="utf-8")
        bridge_version = re.search(r'^BRIDGE_VERSION\s*=\s*"([^"]+)"', source_text, re.MULTILINE)
        bridge_package = re.search(r'^TASK25_PACKAGE_COMMIT\s*=\s*"([0-9a-f]+)"', source_text, re.MULTILINE)
        bridge_frame = re.search(r'^TASK25_FRAME_COMMIT\s*=\s*"([0-9a-f]+)"', source_text, re.MULTILINE)
        dbdf_head = git_text(DBDF, "rev-parse", "HEAD")
        package_ancestor = git_is_ancestor(DBDF, TASK25_PACKAGE_COMMIT, dbdf_head)
        frame_ancestor = git_is_ancestor(DBDF, TASK25_FRAME_COMMIT, dbdf_head)
        old_head_pins = bool(re.search(r'^(?:BASELINE_COMMIT|EXPECTED_W4_HEAD|EXPECTED_DBDF_HEAD|DBDF_TREE_HEAD)\s*=',
                                       source_text, re.MULTILINE))
        pin_detail = {"bridge_source_sha256": sha256_file(BRIDGE_SOURCE),
                      "bridge_version": bridge_version.group(1) if bridge_version else None,
                      "expected_bridge_version": "r10",
                      "task_w4_head_observed_only": w4_head,
                      "dbdf_head_observed_only": dbdf_head,
                      "task25_package_commit": TASK25_PACKAGE_COMMIT,
                      "task25_frame_source_commit": TASK25_FRAME_COMMIT,
                      "bridge_package_commit": bridge_package.group(1) if bridge_package else None,
                      "bridge_frame_commit": bridge_frame.group(1) if bridge_frame else None,
                      "package_commit_is_ancestor": package_ancestor,
                      "frame_commit_is_ancestor": frame_ancestor,
                      "legacy_head_pins_present": old_head_pins,
                      "interpretation": "w4 与 dbdf HEAD 只记录观察值；task-25 包提交和帧提交固定，并分别要求为当前 dbdf HEAD 的祖先"}
        pin_ok = (pin_detail["bridge_version"] == "r10"
                  and pin_detail["bridge_package_commit"] == TASK25_PACKAGE_COMMIT
                  and pin_detail["bridge_frame_commit"] == TASK25_FRAME_COMMIT
                  and package_ancestor and frame_ancestor and not old_head_pins)
        add_check(checks, "bridge_runner_moving_head_contract", "PASS" if pin_ok else "BLOCKED", pin_detail)
    except (MissingInputError, OSError, RuntimeError) as exc:
        add_check(checks, "bridge_runner_moving_head_contract", "BLOCKED",
                  {"reason": f"固定桥接入口或精确版本无法核验：{type(exc).__name__}: {exc}"})

    try:
        require_file(S4B_CONTRACT, "S4-B 回放结果接口契约")
        s4b = load_json(S4B_CONTRACT)
        stale = s4b.get("result_contract", {}).get("stale_rule", {})
        semantics = {"timing_claim_scope": "replay_only",
                     "result_join_key": ["session_id", "frame_id", "result_seq"],
                     "stale_limit_ns": stale.get("stale_limit_ns"),
                     "stale_limit_status": stale.get("stale_limit_status"),
                     "capture_time_source": "task-25 documented capture_time_ns / replay_documented_wallclock only",
                     "injection_start_ns_as_capture_time": False,
                     "enable": 0,
                     "raw_system_g0": "NOT_CLOSED",
                     "p_4d_g3_g5": "NOT_RUN"}
        semantics_status = ("PASS" if stale.get("stale_limit_ns") == 200000000
                            and stale.get("stale_limit_status") == "APPROVED_BY_WONG" else "BLOCKED")
        add_check(checks, "replay_semantics_and_stage_boundaries", semantics_status, semantics)
    except (MissingInputError, OSError, KeyError, json.JSONDecodeError, AttributeError) as exc:
        semantics = {"timing_claim_scope": "replay_only", "injection_start_ns_as_capture_time": False,
                     "enable": 0, "raw_system_g0": "NOT_CLOSED", "p_4d_g3_g5": "NOT_RUN"}
        add_check(checks, "replay_semantics_and_stage_boundaries", "BLOCKED",
                  {"semantics": semantics, "reason": f"接口语义来源缺失或无效：{type(exc).__name__}: {exc}"})

    status_result = run(["git", "-C", str(WORKTREE), "status", "--short", "--untracked-files=all"])
    if status_result.returncode != 0:
        raise RuntimeError(status_result.stderr.decode("utf-8", errors="replace"))
    status_lines = status_result.stdout.decode("utf-8", errors="replace").splitlines()
    observed_dirty = {line[3:].replace("\\", "/") for line in status_lines if len(line) >= 4}
    own_prefixes = (
        "report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r",
        "report/evidence/S4-CTRL/s4t26_golden_rebind_20261026_r",
    )
    own_paths = {"docs/stage4/s4t26_golden_rebind_decision_20261026_r01.md"}
    observed_preexisting = {path for path in observed_dirty
                            if path not in TASK_OWNED_UNCOMMITTED_PATHS and path not in own_paths
                            and not path.startswith(own_prefixes)}
    artifact_hashes = {}
    for relpath, expected_sha in PREEXISTING_ARTIFACT_SHA256.items():
        path = WORKTREE / relpath
        actual_sha = sha256_file(path) if path.is_file() else None
        artifact_hashes[relpath] = {"expected_sha256": expected_sha, "actual_sha256": actual_sha,
                                    "status": "PASS" if actual_sha == expected_sha else "FAIL"}
    state_diff = run(["git", "-C", str(WORKTREE), "diff", "--", ".codex/STATE.md"])
    state_diff_sha = sha256_bytes(state_diff.stdout) if state_diff.returncode == 0 else None
    preexisting_ok = (observed_preexisting == PREEXISTING_PATHS
                      and all(item["status"] == "PASS" for item in artifact_hashes.values())
                      and state_diff.returncode == 0)
    add_check(checks, "preexisting_changes_preserved", "PASS" if preexisting_ok else "FAIL",
              {"expected_preexisting_paths": sorted(PREEXISTING_PATHS),
               "observed_preexisting_paths_excluding_task_owned_files": sorted(observed_preexisting),
               "task_owned_uncommitted_paths": sorted(TASK_OWNED_UNCOMMITTED_PATHS),
               "elf_map_hashes": artifact_hashes,
               "state_worktree_sha256": sha256_file(WORKTREE / ".codex/STATE.md"),
               "state_existing_diff_sha256": state_diff_sha,
               "attribution": ".codex/STATE.md 保留既有状态差异；12 个 ELF/MAP 为既有本机恢复产物，未修改、删除或暂存"})

    blockers = [f"{item['name']}: {item['detail']}" for item in checks if item["status"] == "BLOCKED"]
    failures = [item["name"] for item in checks if item["status"] == "FAIL"]
    status = "FAIL" if failures else ("BLOCKED" if blockers else "PASS")
    exit_code = 1 if failures else (2 if blockers else 0)
    out = {
        "task_id": "S4-T26-GOLDEN-REBIND", "task_name": "阶段4 task-26 黄金来源改绑 G0",
        "checker_version": CHECKER_VERSION,
        "run_id": args.run_id, "status": status, "exit_code": exit_code,
        "generated_utc8": datetime.now(CN).isoformat(timespec="seconds"),
        "command": [sys.executable, str(Path(__file__).resolve()), "--run-id", args.run_id],
        "worktree": str(WORKTREE), "branch": w4_branch, "head_observed_only": w4_head,
        "environment": {"python": sys.version, "executable": sys.executable,
                        "platform": platform.platform(), "numpy_probe_not_needed": True,
                        "cv2_probe_count": len(probes)},
        "checks": checks, "blocking_reasons": blockers, "failures": failures,
        "execution": {"sample_102_raw_head_forward": "NOT_RUN", "sample_000_positive_detection_forward": "NOT_RUN",
                      "replay_frame_forward": "NOT_RUN",
                      "raw_head13_head26_capture_or_compare": "NOT_RUN", "d9_decode_nms": "NOT_RUN",
                      "negative_controls": "NOT_RUN", "png_imread_unchanged_pixel_identity": "NOT_RUN",
                      "hardware_vivado_jtag_com4": "NOT_RUN"},
        "result_semantics_to_preserve": semantics,
        "limitations": [
            "此 RunId 仅记录 G0 输入核验；未产生真实网络推理、检测或任务-27/28 可消费的冻结推理结果包。",
            "task-25 单帧只作离线回放输入；其秒级文档墙钟时间不是 PS 单调时钟，也不提供实时帧周期。",
            "当前 Darknet/hook 控制未复现 T29；不作为黄金来源，r03/r04 失败证据保持原样。",
            "approved_no_hand_001 仅关闭 raw-head 门；阳性检测/显示覆盖单独由 test_fist_000 承担。",
            "原校准图 98529267-1eda-43a6-8e38-245947ecb312.jpg 标记 NOT_USED_HISTORICAL。",
            "s4-shared-io r06 仍为 DRAFT_PENDING_REVIEW；ENABLE=0，RAW 系统 G0 未闭合。",
            "阶段3、板卡、JTAG、COM4、下载、烧录及硬件会话均未访问。",
            "既有 12 个 ELF/MAP 未修改、未删除、未暂存；本轮开始时 .codex/STATE.md 的既有差异保持原样。",
        ],
    }
    preflight_path = run_dir / "preflight_verification.json"
    preflight_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_path = Path(__file__).resolve()
    manifest = {
        "task_id": out["task_id"], "run_id": args.run_id, "status": status, "exit_code": exit_code,
        "worktree": str(WORKTREE), "head_observed_only": w4_head, "command": out["command"],
        "source": {"path": str(source_path), "version": CHECKER_VERSION,
                   "sha256": sha256_file(source_path)},
        "inputs": {"s4a_contract_sha256": optional_sha256_file(S4A_CONTRACT),
                   "activation_report_sha256": optional_sha256_file(ACTIVATION_REPORT),
                   "reference_run_sha256": optional_sha256_file(REFERENCE_RUN),
                   "golden_materialization_manifest_sha256": optional_sha256_file(GOLDEN_MANIFEST),
                   "decision_record_sha256": optional_sha256_file(DECISION_RECORD),
                   "darknet_control_comparison_sha256": optional_sha256_file(T29_CONTROL_COMPARISON),
                   "task25_package_manifest_sha256": task25.get("package_manifest_sha256") if task25 else None,
                   "task25_binding_sha256": task25.get("binding_sha256") if task25 else None,
                   "task25_frame_sha256": task25.get("frame", {}).get("disk_sha256") if task25 else None,
                   "parameter_sources": contract_assets.get("assets") if contract_assets else None,
                   "availability_note": "缺失或不可读的输入保留为 null；逐项原因见 preflight_verification.json 的 BLOCKED 检查。"},
        "outputs": {"preflight_verification.json": {"sha256": sha256_file(preflight_path),
                                                        "size_bytes": preflight_path.stat().st_size}},
        "blocking_reasons": blockers,
    }
    manifest_path = run_dir / "delivery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "exit_code": exit_code, "run_dir": str(run_dir),
                      "blocking_check_names": [item["name"] for item in checks if item["status"] == "BLOCKED"],
                      "failure_check_names": failures}, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
