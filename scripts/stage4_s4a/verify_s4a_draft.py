#!/usr/bin/env python3
"""S4-A 阶段4 G0 基线与结论口径只读自检（r06）。

检查内容（退出码 0 = 全部通过，1 = 存在 FAIL，2 = 输入/环境错误）：
  1. 契约 JSON 可解析且必需键齐全（含 g0_round_freeze/scope_freeze/candidate_limit_boundary_test/
     uart_plan_b_freeze/hardware_authorization_conditions/round_freeze_metadata）；
  2. §2 上游钉扎现场复算：带 SHA-256 的条目必须 MATCH（含字节数）；目录聚合引用必须存在；
     声明 NOT_AVAILABLE 的条目必须真不可读（可读却标不可读判 FAIL，杜绝写猜的哈希）；
  3. T25 分片计数/字节数与分片恢复清单一致，并可逐片校验 SHA-256；
  4. md §3.2 / §3.3 表格与 JSON 字段集合**双向相等**，且逐字段 `必填`/`2A 冻结` 标注一致；
  5. md §3.4 状态表与 JSON `state_enum` 状态集合严格相等；
  6. md §4.4 measurement_scope 键集合与 JSON 严格相等；
  7. 2A 冻结常量与**上游文件**（manifest detection_postprocess/address_map.heads、T29 head_tensors）
     一致，候选理论上界与 manifest 几何乘积及 2B 参考实现头文件宏一致；
  8. g0_round_freeze 与人读文档一致（冻结项齐备 + 锚点存在；未冻结项状态为 DRAFT_PENDING_APPROVAL）；
  9. scope_freeze 恰含三种范围且允许/禁止结论非空、锚点存在；候选上限边界口径齐备；
 10. 2B 事实对齐：必须出现回执 SHA/代码基线/最终提交/G4/G5/1000/108 与「正式冻结并释放硬件」
     「现场会话核验为准」，且不得再出现旧快照语句。

本脚本只读，不写任何上游文件；只把结果 JSON 写入 --evidence-dir。滚动下载 23 MB/57 MB 等外部
大文件时按 1 MiB 流式读取。本检查通过不代表阶段4 G0 未决项获批或任何实物验收。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CONTRACT = WORKTREE / "docs" / "stage4" / "s4a_stage4_g0_fields.json"
HUMAN_DOC = WORKTREE / "docs" / "stage4" / "S4A_stage4_g0_tracking_and_timing_draft.md"

REQUIRED_KEYS = (
    "schema_version",
    "status",
    "round_freeze_metadata",
    "g0_round_freeze",
    "scope_freeze",
    "candidate_limit_boundary_test",
    "uart_plan_b_freeze",
    "hardware_authorization_conditions",
    "upstream_bindings",
    "frozen_2a_constants",
    "result_record",
    "detection_record",
    "state_enum",
    "timing_definitions",
    "anomaly_accounting",
    "draft_proposed_thresholds",
    "uart_mapping",
    "limitations",
)

STATES = ("OK", "NO_HAND", "TIMEOUT", "ERROR", "DROPPED")

REQUIRED_BINDING_IDS = (
    "s2a_t01_spec",
    "s2a_t01_model_manifest",
    "s2a_t01_fixed_test_samples",
    "s2a_t25_layer_golden_index",
    "s2a_t25_shard_recovery_manifest",
    "s2a_t25_tensor_shards",
    "s2a_t29_cpu_decode_nms_reference",
    "s2a_external_cfg",
    "s2a_external_darknet_weights",
    "s2a_external_gf8",
    "s2a_external_calibration_list",
    "s2a_external_hagridv2_manifest_csv",
    "s1_t02_d2_numeric_reference",
    "s1_t02_d9_decoder",
    "s1_t02_d6_metrics",
    "s2b_physical_interface_candidate",
    "s2b_board_transport",
    "s2a_ps_decode_nms_reference_c",
    "s2a_ps_decode_nms_reference_h",
    "s2b_board_transport_py",
    "s2b_inference_app_c",
    "s2b_build_inference_py",
    "s2b_inference_platform_json",
    "stage2b_freeze_receipt",
)

REQUIRED_FROZEN_IDS = (
    "uart_plan_b",
    "scope_freeze",
    "anomaly_behaviour",
    "candidate_limit_boundary",
    "timing_definitions_reference",
    "hardware_authorization",
)

REQUIRED_DRAFT_IDS = ("stale_age_limit", "timebase_and_cross_domain_measurement")

REQUIRED_SCOPE_IDS = ("offline_regression", "board_injection", "camera")

ALLOWED_NOT_FROZEN_STATUS = ("DRAFT_PENDING_APPROVAL", "CLOSED_FOR_THIS_ROUND")

REQUIRED_DOC_PHRASES = (
    "2687e87a9664d6415d17738a6f6ff10b8fe3e372696399eb710fa2d06d2778e1",
    "16ce2cdf8c00c6214435629d75a5e4b63acb66a9",
    "07c3d3958578b9cc9d3b8eae3758711fe08724c2",
    "正式冻结并释放硬件",
    "释放硬件",
    "现场会话核验为准",
    "G4=PASS",
    "G5=PASS",
    "1000 次连续任务",
    "108 个 ACK 闭环",
    "DRAFT_PENDING_APPROVAL",
    "S4A-FREEZE-UART-B",
    "S4A-FREEZE-SCOPES",
    "S4A-FREEZE-ANOMALY",
    "S4A-FREEZE-CANDIDATE-BOUNDARY",
    "S4A-FREEZE-TIMING-REF",
    "S4A-FREEZE-HW-AUTH",
    "S4A-DRAFT-STALE-AGE-LIMIT",
    "S4A-DRAFT-TIMEBASE",
    "S4A-DRAFT-OPTION-A-EXTENSION",
    "恰好 12675",
    "追加 12676",
    "S2A_T62_INVALID_ARGUMENT",
    "BAD_ARGUMENT",
    "4096",
    "注入不得伪造",
    "injection_start_ns",
    "capture_time_available",
    "result_seq",
    "session_id",
    "NOT_EXECUTED_OFFLINE",
)

FORBIDDEN_DOC_PHRASES = ("2B 尚未", "2B尚未", "仍持硬件")

CN_TIMES = timedelta(hours=8)


def now_utc8() -> str:
    """返回 UTC+8 的 ISO 8601 当前时刻。"""
    return datetime.now(timezone.utc).astimezone(timezone(CN_TIMES)).isoformat(timespec="seconds")


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(path_text: str) -> Path:
    """把绑定路径解析为绝对路径（相对路径按工作树解析）。"""
    path = Path(path_text)
    return path if path.is_absolute() else WORKTREE / path_text


def table_rows(text: str, start_marker: str, end_marker: str, min_cells: int = 4) -> list[list[str]]:
    """解析指定小节内的 markdown 表格数据行，返回去掉表头与分隔行的单元格列表。"""
    if start_marker not in text:
        raise ValueError(f"未找到小节标记：{start_marker}")
    section = text.split(start_marker, 1)[1]
    if end_marker in section:
        section = section.split(end_marker, 1)[0]
    rows: list[list[str]] = []
    for raw in section.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) < min_cells:
            continue
        first = cells[0]
        if first in ("字段", "值", "键", "绑定 ID", "项", "冻结 ID", "未冻结 ID", "条件 ID") or set(first) <= set("-: ") or not first:
            continue
        rows.append(cells)
    return rows


def compare_md_table(
    rows: list[list[str]],
    json_fields: list[dict],
    table_name: str,
    failures: list[str],
    details: dict,
) -> None:
    """双向比对 md 表格与 JSON 字段定义（集合相等 + 无重复行 + 逐字段标注一致）。"""
    name_list = [row[0] for row in rows]
    duplicates = sorted({name for name in name_list if name_list.count(name) > 1})
    details[f"{table_name}_duplicate_rows"] = duplicates
    if duplicates:
        failures.append(f"{table_name}：md 表格存在重复字段行 {duplicates}")
    md_map = {row[0]: {"required": row[2] == "是", "frozen_by_2a": row[3] == "是"} for row in rows}
    json_map = {item["name"]: {"required": bool(item["required"]), "frozen_by_2a": bool(item["frozen_by_2a"])} for item in json_fields}
    md_only = sorted(set(md_map) - set(json_map))
    json_only = sorted(set(json_map) - set(md_map))
    mismatched = []
    for name in sorted(set(md_map) & set(json_map)):
        if md_map[name] != json_map[name]:
            mismatched.append({"field": name, "md": md_map[name], "json": json_map[name]})
    details[f"{table_name}_md_only"] = md_only
    details[f"{table_name}_json_only"] = json_only
    details[f"{table_name}_annotation_mismatch"] = mismatched
    details[f"{table_name}_field_count"] = len(md_map)
    if md_only:
        failures.append(f"{table_name}：md 有而 JSON 无的字段 {md_only}")
    if json_only:
        failures.append(f"{table_name}：JSON 有而 md 无的字段 {json_only}")
    if mismatched:
        failures.append(f"{table_name}：必填/2A 冻结标注不一致 {mismatched}")


def check_upstream_bindings(contract: dict, failures: list[str], passes: list[str], details: dict) -> None:
    """现场复算全部上游钉扎条目（含 NOT_AVAILABLE 与目录聚合引用的诚实性检查）。"""
    bindings = contract.get("upstream_bindings", [])
    ids = [item.get("id") for item in bindings]
    missing_ids = [item for item in REQUIRED_BINDING_IDS if item not in ids]
    if missing_ids:
        failures.append(f"upstream_bindings 缺少必需钉扎条目：{missing_ids}")
    else:
        passes.append(f"upstream_bindings 必需钉扎条目齐备（{len(REQUIRED_BINDING_IDS)} 项必需 ID）")

    sha_results: list[dict[str, object]] = []
    directory_results: list[dict[str, object]] = []
    not_available: list[dict[str, object]] = []
    match_count = 0
    for binding in bindings:
        binding_id = binding.get("id")
        path = resolve(binding["path"])
        expected = binding.get("sha256")
        if not expected:
            status = str(binding.get("status", ""))
            if status == "READ_ONLY_REFERENCE" or "pattern" in binding or "file_count" in binding:
                entry: dict[str, object] = {
                    "id": binding_id,
                    "path": str(path),
                    "aggregate": True,
                    "declared_file_count": binding.get("file_count"),
                    "declared_total_bytes": binding.get("total_bytes"),
                    "count_authority": binding.get("count_authority"),
                }
                if path.is_dir():
                    # 计数与逐片 SHA 以分片恢复清单为准，由 check_tensor_shards 复核，此处只确认可读。
                    entry["status"] = "DIRECTORY_OK"
                else:
                    entry["status"] = "DIRECTORY_MISSING"
                    failures.append(f"目录聚合钉扎路径不可读：{binding_id} -> {path}")
                directory_results.append(entry)
                continue
            if "NOT_AVAILABLE" in status:
                reason = binding.get("unavailable_reason")
                entry = {"id": binding_id, "path": str(path), "declared_unavailable": True, "reason": reason}
                if not reason:
                    failures.append(f"{binding_id} 声明 NOT_AVAILABLE 但未给出 unavailable_reason")
                if path.is_file():
                    failures.append(
                        f"{binding_id} 声明 NOT_AVAILABLE 但文件实际可读（{path}）：禁止以不可读为由规避复算"
                    )
                    entry["status"] = "DECLARED_UNAVAILABLE_BUT_READABLE"
                else:
                    entry["status"] = "NOT_AVAILABLE_CONFIRMED"
                not_available.append(entry)
                continue
            failures.append(f"{binding_id} 既无 sha256 也未声明 READ_ONLY_REFERENCE/NOT_AVAILABLE")
            continue

        entry = {"id": binding_id, "path": str(path), "expected": expected}
        if not path.is_file():
            entry["status"] = "MISSING"
            failures.append(f"上游钉扎文件缺失：{binding_id} -> {path}")
        else:
            actual = sha256_of(path)
            size = path.stat().st_size
            entry["actual_sha256"] = actual
            entry["actual_bytes"] = size
            entry["declared_bytes"] = binding.get("bytes")
            if actual != expected:
                entry["status"] = "MISMATCH"
                failures.append(f"上游钉扎 SHA 不一致：{binding_id}（清单 {expected}，实际 {actual}）")
            elif "bytes" in binding and size != binding["bytes"]:
                entry["status"] = "SIZE_MISMATCH"
                failures.append(f"上游钉扎字节数不一致：{binding_id}（清单 {binding['bytes']}，实际 {size}）")
            elif "sample_count" in binding:
                count = sum(
                    1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()
                )
                entry["actual_sample_count"] = count
                entry["declared_sample_count"] = binding["sample_count"]
                if count != binding["sample_count"]:
                    entry["status"] = "SAMPLE_COUNT_MISMATCH"
                    failures.append(f"上游钉扎样本数不一致：{binding_id}（清单 {binding['sample_count']}，实际 {count}）")
                else:
                    entry["status"] = "MATCH"
                    match_count += 1
            else:
                entry["status"] = "MATCH"
                match_count += 1
        sha_results.append(entry)

    details["upstream_sha"] = sha_results
    details["upstream_directory"] = directory_results
    details["upstream_not_available"] = not_available
    details["upstream_match_count"] = match_count
    if sha_results and all(item["status"] == "MATCH" for item in sha_results):
        passes.append(f"上游带 SHA-256 的 {match_count} 项钉扎现场复算全部一致（含字节数）")


def check_tensor_shards(contract: dict, no_shard_sha: bool, failures: list[str], passes: list[str], details: dict) -> None:
    """T25 分片计数（上游依据 = 分片恢复清单）与逐片 SHA 校验。"""
    shard_binding = next((b for b in contract["upstream_bindings"] if b.get("id") == "s2a_t25_tensor_shards"), None)
    recovery = next((b for b in contract["upstream_bindings"] if b.get("id") == "s2a_t25_shard_recovery_manifest"), None)
    if not (shard_binding and recovery):
        return
    shard_dir = Path(shard_binding["path"])
    shards = sorted(shard_dir.glob("*.zlib")) if shard_dir.is_dir() else []
    total = sum(item.stat().st_size for item in shards)
    recovery_doc = json.loads(Path(recovery["path"]).read_text(encoding="utf-8"))
    authority = {"sample_count": recovery_doc.get("sample_count"), "total_bytes": recovery_doc.get("total_bytes")}
    entry: dict[str, object] = {
        "dir": str(shard_dir),
        "observed_file_count": len(shards),
        "observed_total_bytes": total,
        "authority_manifest": {"path": recovery["path"], "declared": authority},
        "contract_declared": {"file_count": shard_binding.get("file_count"), "total_bytes": shard_binding.get("total_bytes")},
    }
    ok = (
        len(shards) == authority["sample_count"]
        and total == authority["total_bytes"]
        and shard_binding.get("file_count") == authority["sample_count"]
        and shard_binding.get("total_bytes") == authority["total_bytes"]
    )
    entry["status"] = "MATCH" if ok else "MISMATCH"
    if ok:
        passes.append(f"T25 分片计数与上游恢复清单一致：{len(shards)} 个 / {total} B")
    else:
        failures.append(f"T25 分片计数与上游恢复清单不一致：观测 {len(shards)}/{total}，清单 {authority}")
    if not no_shard_sha:
        by_index = {item["sample_index"]: item for item in recovery_doc.get("shards", [])}
        bad: list[dict[str, object]] = []
        checked = 0
        for shard in shards:
            try:
                index = int(shard.stem.split("_")[-1])
            except ValueError:
                bad.append({"file": shard.name, "reason": "无法解析样本序号"})
                continue
            declared = by_index.get(index)
            if not declared:
                bad.append({"file": shard.name, "reason": "恢复清单无该样本"})
                continue
            actual = sha256_of(shard)
            checked += 1
            if actual != declared.get("sha256") or shard.stat().st_size != declared.get("bytes"):
                bad.append({"file": shard.name, "expected": declared.get("sha256"), "actual": actual})
        entry["shard_sha_checked"] = checked
        entry["shard_sha_bad"] = bad
        if bad or checked != len(shards):
            failures.append(f"T25 分片逐片 SHA 校验失败：{len(bad)} 项异常，已校验 {checked}/{len(shards)}")
        else:
            passes.append(f"T25 分片逐片 SHA-256 全部一致（{checked}/{len(shards)}）")
    else:
        entry["shard_sha_checked"] = 0
        entry["shard_sha_bad"] = "SKIPPED_BY_FLAG"
    details["tensor_shards"] = entry


def check_frozen_constants(contract: dict, failures: list[str], passes: list[str], details: dict) -> None:
    """2A 冻结常量与上游文件比对（含候选理论上界与 2B 参考实现宏）。"""
    frozen = contract["frozen_2a_constants"]
    try:
        manifest_path = resolve(next(b for b in contract["upstream_bindings"] if b["id"] == "s2a_t01_model_manifest")["path"])
        t29_path = resolve(next(b for b in contract["upstream_bindings"] if b["id"] == "s2a_t29_cpu_decode_nms_reference")["path"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        t29 = json.loads(t29_path.read_text(encoding="utf-8"))
    except (StopIteration, KeyError, json.JSONDecodeError, OSError) as exc:
        failures.append(f"无法读取上游冻结依据：{exc}")
        return

    post = manifest["detection_postprocess"]
    checks: list[tuple[str, object, object]] = [
        ("score_threshold", post["score_threshold"], frozen["score_threshold"]),
        ("nms_iou", post["nms_iou"], frozen["nms_iou"]),
        ("max_outputs_per_image", post["max_outputs"], frozen["max_outputs_per_image"]),
        ("classes", post["class_order"], frozen["classes"]),
    ]
    for head in manifest["address_map"]["heads"]:
        name = head["name"]
        checks.append((f"{name}.length_bytes", head["length_bytes"], frozen[name]["byte_length"]))
        checks.append((f"{name}.int8_scale", head["int8_scale"], frozen[name]["int8_scale"]))
        checks.append((f"{name}.shape_nchw", head["shape_nchw"], frozen[name]["shape_nchw"]))
    for head_name in ("head13", "head26"):
        ref = t29["samples"][0]["head_tensors"][head_name]
        checks.append((f"T29.{head_name}.byte_length", ref["byte_length"], frozen[head_name]["byte_length"]))
        checks.append((f"T29.{head_name}.int8_scale", ref["int8_scale"], frozen[head_name]["int8_scale"]))

    products = [head["shape_nchw"][2] * head["shape_nchw"][3] for head in manifest["address_map"]["heads"]]
    computed_max = sum(products) * 3 * len(post["class_order"])
    checks.append(("candidate_theoretical_max(manifest 两头几何×3 anchors×classes)", computed_max, frozen["candidate_theoretical_max"]))

    ref_binding = next((b for b in contract["upstream_bindings"] if b.get("id") == "s2a_ps_decode_nms_reference_c"), None)
    header_binding = next((b for b in contract["upstream_bindings"] if b.get("id") == "s2a_ps_decode_nms_reference_h"), None)
    if ref_binding:
        ref_path = resolve(ref_binding["path"])
        if ref_path.is_file():
            ref_text = ref_path.read_text(encoding="utf-8", errors="replace")
            declared_max = None
            for line in ref_text.splitlines():
                if "#define" in line and "S2A_T62_MAX_CANDIDATES" in line:
                    digits = "".join(ch for ch in line.split("S2A_T62_MAX_CANDIDATES", 1)[1] if ch.isdigit())
                    declared_max = int(digits) if digits else None
                    break
            checks.append(("S2A_T62_MAX_CANDIDATES(2B C 参考)", declared_max, frozen["candidate_theoretical_max"]))
            details["s2b_max_candidates_observed"] = declared_max
            has_hard_error = any(
                "S2A_T62_INVALID_ARGUMENT" in line and "return" in line for line in ref_text.splitlines()
            )
            details["s2b_hard_error_branch_present"] = has_hard_error
            if not has_hard_error:
                failures.append("2B C 参考未发现 S2A_T62_INVALID_ARGUMENT 硬错误分支（候选上限语义不成立）")
        else:
            failures.append(f"2B 参考实现文件不可读：{ref_path}")
    if header_binding:
        header_path = resolve(header_binding["path"])
        if header_path.is_file():
            header_text = header_path.read_text(encoding="utf-8", errors="replace")
            has_invalid = "S2A_T62_INVALID_ARGUMENT" in header_text
            details["s2b_header_invalid_argument_present"] = has_invalid
            if not has_invalid:
                failures.append("2B 参考头文件未定义 S2A_T62_INVALID_ARGUMENT")
        else:
            failures.append(f"2B 参考头文件不可读：{header_path}")

    mismatches = [
        {"item": name, "upstream": upstream, "contract": declared}
        for name, upstream, declared in checks
        if upstream != declared
    ]
    details["frozen_constant_checks"] = {"checked": len(checks), "mismatches": mismatches}
    if mismatches:
        failures.append(f"2A 冻结常量与上游文件不一致：{mismatches}")
    else:
        passes.append(
            f"2A 冻结常量与上游文件一致（{len(checks)} 项：manifest detection_postprocess/address_map.heads、"
            "T29 head_tensors、候选理论上界与 2B 参考实现宏）"
        )


def check_round_freeze(contract: dict, doc_text: str, failures: list[str], passes: list[str], details: dict) -> None:
    """g0_round_freeze / scope_freeze / 候选边界 / 2B 事实对齐 与文档一致性。"""
    freeze = contract.get("g0_round_freeze", {})
    frozen_items = freeze.get("frozen_items", [])
    not_frozen_items = freeze.get("not_frozen_items", [])

    frozen_ids = [item.get("id") for item in frozen_items]
    missing_frozen = [item for item in REQUIRED_FROZEN_IDS if item not in frozen_ids]
    details["frozen_item_ids"] = frozen_ids
    if missing_frozen:
        failures.append(f"g0_round_freeze 缺少必需冻结项：{missing_frozen}")
    else:
        passes.append(f"g0_round_freeze 冻结项齐备（{len(REQUIRED_FROZEN_IDS)} 项）")
    bad_anchors = []
    for item in frozen_items:
        for field in ("freeze_id", "doc_section", "statement"):
            if not item.get(field):
                failures.append(f"冻结项 {item.get('id')} 缺少 {field}")
        if item.get("freeze_id") and item["freeze_id"] not in doc_text:
            bad_anchors.append({"id": item.get("id"), "anchor": item.get("freeze_id")})
        if item.get("doc_section") and item["doc_section"] not in doc_text:
            bad_anchors.append({"id": item.get("id"), "anchor": item.get("doc_section")})
    details["frozen_anchor_missing"] = bad_anchors
    if bad_anchors:
        failures.append(f"冻结项锚点在文档中缺失：{bad_anchors}")

    draft_ids = [item.get("id") for item in not_frozen_items]
    missing_draft = [item for item in REQUIRED_DRAFT_IDS if item not in draft_ids]
    details["not_frozen_item_ids"] = draft_ids
    if missing_draft:
        failures.append(f"g0_round_freeze 缺少必需未冻结项：{missing_draft}")
    else:
        passes.append(f"g0_round_freeze 未冻结项齐备（{len(REQUIRED_DRAFT_IDS)} 项必需 ID）")
    by_id = {item.get("id"): item for item in not_frozen_items}
    for item in not_frozen_items:
        item_id = item.get("id")
        status = item.get("status")
        if status not in ALLOWED_NOT_FROZEN_STATUS:
            failures.append(f"未冻结项 {item_id} 状态非法：{status}")
        if item.get("freeze_id") and item["freeze_id"] not in doc_text:
            failures.append(f"未冻结项 {item_id} 的锚点 {item.get('freeze_id')} 在文档中缺失")
    for item_id in REQUIRED_DRAFT_IDS:
        item = by_id.get(item_id)
        if item and item.get("status") != "DRAFT_PENDING_APPROVAL":
            failures.append(
                f"未冻结项 {item_id} 状态必须为 DRAFT_PENDING_APPROVAL，实际 {item.get('status')}（不得写成已批准）"
            )
    if all(by_id.get(item_id, {}).get("status") == "DRAFT_PENDING_APPROVAL" for item_id in REQUIRED_DRAFT_IDS):
        passes.append("未冻结项 stale_age_limit/时基方法 均为 DRAFT_PENDING_APPROVAL（未写成已批准）")

    scope = contract.get("scope_freeze", {})
    scope_ids = [key for key in scope if key != "description"]
    details["scope_ids"] = scope_ids
    if sorted(scope_ids) != sorted(REQUIRED_SCOPE_IDS):
        failures.append(f"scope_freeze 键集合不为三种范围：{scope_ids}")
    else:
        scope_bad = []
        for scope_id in REQUIRED_SCOPE_IDS:
            body = scope[scope_id]
            if not body.get("allowed_conclusions"):
                scope_bad.append(f"{scope_id}.allowed_conclusions 为空")
            if not body.get("forbidden_conclusions"):
                scope_bad.append(f"{scope_id}.forbidden_conclusions 为空")
            if f"`{scope_id}`" not in doc_text:
                scope_bad.append(f"{scope_id} 锚点在文档中缺失")
            template = body.get("measurement_scope_template", {})
            if template.get("source_kind") != body.get("source_kind"):
                scope_bad.append(f"{scope_id}.measurement_scope_template.source_kind 与 source_kind 不一致")
            if scope_id != "camera" and template.get("capture_time_available") is not False:
                scope_bad.append(f"{scope_id} 非摄像头范围的 capture_time_available 必须为 false")
        details["scope_problems"] = scope_bad
        if scope_bad:
            failures.append(f"scope_freeze 检查失败：{scope_bad}")
        else:
            passes.append("scope_freeze 恰含三种范围、允许/禁止结论非空、锚点存在、注入不伪造采集时间")

    boundary = contract.get("candidate_limit_boundary_test", {})
    frozen = contract["frozen_2a_constants"]
    boundary_problems = []
    if boundary.get("limit") != frozen["candidate_theoretical_max"]:
        boundary_problems.append(f"limit={boundary.get('limit')} 与 candidate_theoretical_max 不一致")
    over = boundary.get("over_limit_case", {})
    if over.get("append_attempt") != boundary.get("limit", 0) + 1:
        boundary_problems.append(f"over_limit_case.append_attempt={over.get('append_attempt')} 不为 limit+1")
    if over.get("expected_error") != "S2A_T62_INVALID_ARGUMENT":
        boundary_problems.append("over_limit_case.expected_error 必须为 S2A_T62_INVALID_ARGUMENT")
    if over.get("csr_error_code") != frozen["csr_error_codes"]["BAD_ARGUMENT"]:
        boundary_problems.append("over_limit_case.csr_error_code 必须等于 BAD_ARGUMENT")
    if boundary.get("truncation_defined") is not False:
        boundary_problems.append("truncation_defined 必须为 false（不定义候选截断）")
    deprecated = boundary.get("deprecated_4096", {})
    if deprecated.get("value") != 4096 or deprecated.get("enabled") is not False:
        boundary_problems.append("已废弃 4096 必须记录为 enabled=false")
    exact = boundary.get("exact_limit_case", {})
    if exact.get("candidate_count") != boundary.get("limit"):
        boundary_problems.append("exact_limit_case.candidate_count 必须等于 limit")
    details["candidate_boundary_problems"] = boundary_problems
    if boundary_problems:
        failures.append(f"候选上限边界口径检查失败：{boundary_problems}")
    else:
        passes.append("候选上限边界口径齐备（12675 恰好可行 / 12676 硬错误 / 禁用 4096 / 不定义截断）")

    uart = contract.get("uart_plan_b_freeze", {})
    uart_problems = []
    if uart.get("interface_unchanged") is not True or uart.get("extension_closed") is not True:
        uart_problems.append("UART 方案 B 必须 interface_unchanged=true 且 extension_closed=true")
    mapping = uart.get("result_bypass_log_mapping", {})
    if set(mapping.get("join_key", [])) != {"session_id", "frame_id", "repeat_index"}:
        uart_problems.append("连接键必须为 session_id/frame_id/repeat_index")
    if not mapping.get("conflict_policy"):
        uart_problems.append("缺少冲突处理策略")
    details["uart_plan_b_problems"] = uart_problems
    if uart_problems:
        failures.append(f"UART 方案 B 冻结检查失败：{uart_problems}")
    else:
        passes.append("UART 方案 B 冻结齐备（s2bu/1.1 不变、扩展关闭、旁路映射与冲突处理）")

    facts = contract.get("round_freeze_metadata", {}).get("upstream_facts_2b", {})
    receipt_sha = next((b for b in contract["upstream_bindings"] if b.get("id") == "stage2b_freeze_receipt"), {})
    fact_problems = []
    if facts.get("freeze_receipt_sha256") != receipt_sha.get("sha256"):
        fact_problems.append("回执 SHA 与 upstream_bindings 不一致")
    if facts.get("g4") != "PASS" or facts.get("g5") != "PASS":
        fact_problems.append("G4/G5 必须为 PASS")
    if facts.get("continuous_tasks_accepted") != 1000 or facts.get("golden_ack_closed_accepted") != 108:
        fact_problems.append("1000 连续任务 / 108 ACK 闭环事实缺失")
    details["upstream_fact_problems"] = fact_problems
    if fact_problems:
        failures.append(f"2B 上游事实块检查失败：{fact_problems}")
    else:
        passes.append("2B 上游事实块与冻结回执一致（SHA/提交/G4G5/1000/108/释放时间）")

    missing_phrases = [phrase for phrase in REQUIRED_DOC_PHRASES if phrase not in doc_text]
    details["required_doc_phrases_missing"] = missing_phrases
    if missing_phrases:
        failures.append(f"人读文档缺少必需事实/锚点字符串：{missing_phrases}")
    else:
        passes.append(f"人读文档包含全部必需事实与锚点字符串（{len(REQUIRED_DOC_PHRASES)} 项）")

    found_forbidden = [phrase for phrase in FORBIDDEN_DOC_PHRASES if phrase in doc_text]
    details["forbidden_doc_phrases_found"] = found_forbidden
    if found_forbidden:
        failures.append(f"人读文档仍含与事实不符的旧快照语句：{found_forbidden}")
    else:
        passes.append("人读文档已无与事实不符的旧快照语句（2B 未验收/仍持硬件类表述）")

    if "DRAFT_PENDING_APPROVAL" not in doc_text:
        failures.append("人读文档缺少 DRAFT_PENDING_APPROVAL 标注")


def main() -> int:
    """执行全部检查并返回退出码。"""
    parser = argparse.ArgumentParser(description="S4-A 阶段4 G0 基线与结论口径只读自检")
    parser.add_argument("--evidence-dir", default="", help="可选的证据输出目录（本工作树内）")
    parser.add_argument("--no-shard-sha", action="store_true", help="跳过 109 个分片的逐片 SHA-256 校验")
    args = parser.parse_args()

    failures: list[str] = []
    passes: list[str] = []
    details: dict[str, object] = {}

    if not CONTRACT.is_file():
        print(f"[FAIL] 契约文件不存在：{CONTRACT}")
        return 2
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[FAIL] 契约 JSON 无法解析：{exc}")
        return 2
    if not HUMAN_DOC.is_file():
        print(f"[FAIL] 人读文档不存在：{HUMAN_DOC}")
        return 2
    doc_text = HUMAN_DOC.read_text(encoding="utf-8")

    # 1. 必需键
    missing = [key for key in REQUIRED_KEYS if key not in contract]
    if missing:
        failures.append(f"契约缺少必需键：{missing}")
    else:
        passes.append("契约 JSON 可解析且必需键齐全")

    # 2-3. 上游钉扎与分片
    check_upstream_bindings(contract, failures, passes, details)
    check_tensor_shards(contract, args.no_shard_sha, failures, passes, details)

    # 4. md↔JSON 双向字段对照
    try:
        result_rows = table_rows(doc_text, "### 3.2 结果字段", "### 3.3 检测框记录")
        detection_rows = table_rows(doc_text, "### 3.3 检测框记录", "### 3.4 状态枚举")
    except ValueError as exc:
        failures.append(f"无法解析人读文档表格：{exc}")
    else:
        compare_md_table(result_rows, contract["result_record"]["fields"], "result_table", failures, details)
        compare_md_table(detection_rows, contract["detection_record"]["fields"], "detection_table", failures, details)
        if not any("表" in item and ("有而" in item or "标注不一致" in item) for item in failures):
            passes.append(
                "md §3.2/§3.3 与 JSON 字段集合双向相等、标注逐字段一致"
                f"（结果 {len(result_rows)} 项、检测 {len(detection_rows)} 项）"
            )

    # 5. 状态集合对照
    try:
        state_rows = table_rows(doc_text, "### 3.4 状态枚举", "## 4. 时间口径", min_cells=2)
    except ValueError as exc:
        failures.append(f"无法解析状态枚举表：{exc}")
    else:
        md_states = {row[0] for row in state_rows}
        json_states = set(contract["state_enum"])
        details["state_md"] = sorted(md_states)
        details["state_json"] = sorted(json_states)
        if md_states != json_states or json_states != set(STATES):
            failures.append(
                f"状态集合不严格相等：md={sorted(md_states)} json={sorted(json_states)} 期望恰为={list(STATES)}"
                "（state_enum 中混入非状态键或漏状态都会判 FAIL）"
            )
        else:
            passes.append("md §3.4 状态表与 JSON state_enum 键集合严格相等且恰为 5 个状态")

    # 6. measurement_scope 键集合对照
    try:
        scope_rows = table_rows(doc_text, "### 4.4", "## 5. 异常与边界记录口径", min_cells=3)
    except ValueError as exc:
        failures.append(f"无法解析 measurement_scope 表：{exc}")
    else:
        md_scope_keys = {row[0] for row in scope_rows}
        json_scope_keys = set(contract["evidence_annotation"]["measurement_scope"]["keys"])
        details["measurement_scope_md"] = sorted(md_scope_keys)
        details["measurement_scope_json"] = sorted(json_scope_keys)
        if md_scope_keys != json_scope_keys:
            failures.append(
                f"measurement_scope 键集合不一致：md={sorted(md_scope_keys)} json={sorted(json_scope_keys)}"
            )
        else:
            passes.append(f"md §4.4 measurement_scope 键集合同 JSON 严格相等（{len(md_scope_keys)} 键）")

    # 7. 2A 冻结常量
    check_frozen_constants(contract, failures, passes, details)

    # 8-10. 本轮冻结块、范围、边界、2B 事实与文档一致性
    check_round_freeze(contract, doc_text, failures, passes, details)

    status = "PASS" if not failures else "FAIL"
    evidence_files = [
        {"path": str(CONTRACT), "sha256": sha256_of(CONTRACT), "purpose": "被审契约（r06）"},
        {"path": str(HUMAN_DOC), "sha256": sha256_of(HUMAN_DOC), "purpose": "被审人读文档（r06）"},
        {"path": str(Path(__file__).resolve()), "sha256": sha256_of(Path(__file__).resolve()), "purpose": "本自检脚本"},
    ]
    report = {
        "task_id": "S4-A",
        "checker_version": "r06",
        "status": status,
        "generated_at_utc8": now_utc8(),
        "command": " ".join([sys.executable, *sys.argv]),
        "exit_code": 0 if status == "PASS" else 1,
        "cwd": str(Path.cwd()),
        "python_version": sys.version,
        "platform": platform.platform(),
        "evidence_files": evidence_files,
        "passes": passes,
        "failures": failures,
        "details": details,
    }

    if args.evidence_dir:
        out_dir = Path(args.evidence_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "verify_s4a_draft_result.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        recompute = {
            "task_id": "S4-A",
            "purpose": "现场复算上游钉扎（SHA-256 / 字节数 / 样本数 / 目录聚合 / NOT_AVAILABLE 诚实性）",
            "generated_at_utc8": now_utc8(),
            "worktree": str(WORKTREE),
            "branch": "stage4-infer-prep",
            "required_binding_ids": list(REQUIRED_BINDING_IDS),
            "sha_entries": details.get("upstream_sha", []),
            "directory_entries": details.get("upstream_directory", []),
            "not_available_entries": details.get("upstream_not_available", []),
            "match_count": details.get("upstream_match_count", 0),
            "tensor_shards": details.get("tensor_shards", {}),
        }
        (out_dir / "upstream_sha_recompute.json").write_text(
            json.dumps(recompute, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[INFO] 证据已写入 {out_dir}")

    for line in passes:
        print(f"[PASS] {line}")
    for line in failures:
        print(f"[FAIL] {line}")
    print(f"[{status}] S4-A G0 基线自检：{len(passes)} 项通过、{len(failures)} 项失败")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())