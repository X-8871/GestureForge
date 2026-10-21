#!/usr/bin/env python3
"""S4-A 阶段4 G0 草案只读自检（r02）。

检查内容（退出码 0 = 全部通过，1 = 存在 FAIL，2 = 输入/环境错误）：
  1. 契约 JSON 可解析且必需键齐全；
  2. 上游带 SHA-256 的绑定在本机复算一致；
  3. T25 分片计数与字节数同上游分片恢复清单一致，并可逐片校验 SHA-256；
  4. md §3.2 / §3.3 表格与 JSON 字段集合**双向相等**，且逐字段 `必填`/`2A 冻结` 标注一致；
  5. md §3.4 状态表与 JSON `state_enum` 的状态集合一致；
  6. 2A 冻结常量与**上游文件**（manifest `detection_postprocess`、`address_map.heads`、T29 `head_tensors`）一致，
     而不是只与脚本内副本比对；
  7. 未冻结值在文档与契约中显式标注（DRAFT_PROPOSED / 未冻结）。

修复来源：rev-spec 独立审查 CHANGES_REQUIRED 的 F1（子串检查假通过）、F3（冻结常量自证）、
F13（证据未绑定命令/退出码/版本/被审哈希）。本脚本只读，不写任何上游文件。
本检查通过不代表阶段4 G0 冻结或任何实物验收。
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
        if first in ("字段", "值") or set(first) <= set("-: ") or not first:
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


def main() -> int:
    """执行全部检查并返回退出码。"""
    parser = argparse.ArgumentParser(description="S4-A 草案只读自检")
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
        print(f"[FAIL] 人读草案不存在：{HUMAN_DOC}")
        return 2
    doc_text = HUMAN_DOC.read_text(encoding="utf-8")

    # 1. 必需键
    missing = [key for key in REQUIRED_KEYS if key not in contract]
    if missing:
        failures.append(f"契约缺少必需键：{missing}")
    else:
        passes.append("契约 JSON 可解析且必需键齐全")

    # 2. 上游 SHA 复算
    sha_results: list[dict[str, object]] = []
    for binding in contract.get("upstream_bindings", []):
        expected = binding.get("sha256")
        if not expected:
            continue
        path = resolve(binding["path"])
        entry: dict[str, object] = {"id": binding.get("id"), "path": str(path), "expected": expected}
        if not path.is_file():
            entry["status"] = "MISSING"
            failures.append(f"上游绑定文件缺失：{binding.get('id')} -> {path}")
        else:
            actual = sha256_of(path)
            entry["actual"] = actual
            entry["status"] = "MATCH" if actual == expected else "MISMATCH"
            if actual != expected:
                failures.append(f"上游绑定 SHA 不一致：{binding.get('id')}")
        sha_results.append(entry)
    details["upstream_sha"] = sha_results
    if sha_results and all(item["status"] == "MATCH" for item in sha_results):
        passes.append(f"上游带 SHA 的 {len(sha_results)} 项绑定全部复算一致")

    # 3. T25 分片计数（上游依据 = 分片恢复清单）与逐片 SHA
    shard_binding = next((b for b in contract["upstream_bindings"] if b.get("id") == "s2a_t25_tensor_shards"), None)
    recovery = next((b for b in contract["upstream_bindings"] if b.get("id") == "s2a_t25_shard_recovery_manifest"), None)
    if shard_binding and recovery:
        shard_dir = Path(shard_binding["path"])
        shards = sorted(shard_dir.glob("*.zlib")) if shard_dir.is_dir() else []
        total = sum(item.stat().st_size for item in shards)
        recovery_doc = json.loads(Path(recovery["path"]).read_text(encoding="utf-8"))
        authority = {"sample_count": recovery_doc.get("sample_count"), "total_bytes": recovery_doc.get("total_bytes")}
        entry = {
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
        # 逐片 SHA（默认执行，可用 --no-shard-sha 跳过）
        if not args.no_shard_sha:
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

    # 4. md↔JSON 双向字段对照（修复 F1：解析表格而非子串匹配）
    try:
        result_rows = table_rows(doc_text, "### 3.2 结果字段", "### 3.3 检测框记录")
        detection_rows = table_rows(doc_text, "### 3.3 检测框记录", "### 3.4 状态枚举")
    except ValueError as exc:
        failures.append(f"无法解析人读草案表格：{exc}")
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

    # 6. 2A 冻结常量：从上游文件读取比对（修复 F3）
    frozen = contract["frozen_2a_constants"]
    try:
        manifest_path = resolve(next(b for b in contract["upstream_bindings"] if b["id"] == "s2a_t01_model_manifest")["path"])
        t29_path = resolve(next(b for b in contract["upstream_bindings"] if b["id"] == "s2a_t29_cpu_decode_nms_reference")["path"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        t29 = json.loads(t29_path.read_text(encoding="utf-8"))
    except (StopIteration, KeyError, json.JSONDecodeError, OSError) as exc:
        failures.append(f"无法读取上游冻结依据：{exc}")
    else:
        post = manifest["detection_postprocess"]
        upstream_checks = [
            ("score_threshold", post["score_threshold"], frozen["score_threshold"]),
            ("nms_iou", post["nms_iou"], frozen["nms_iou"]),
            ("max_outputs_per_image", post["max_outputs"], frozen["max_outputs_per_image"]),
            ("classes", post["class_order"], frozen["classes"]),
        ]
        head_checks = []
        for head in manifest["address_map"]["heads"]:
            name = head["name"]
            head_checks.append((f"{name}.length_bytes", head["length_bytes"], frozen[name]["byte_length"]))
            head_checks.append((f"{name}.int8_scale", head["int8_scale"], frozen[name]["int8_scale"]))
            head_checks.append((f"{name}.shape_nchw", head["shape_nchw"], frozen[name]["shape_nchw"]))
        for head_name in ("head13", "head26"):
            ref = t29["samples"][0]["head_tensors"][head_name]
            head_checks.append((f"T29.{head_name}.byte_length", ref["byte_length"], frozen[head_name]["byte_length"]))
            head_checks.append((f"T29.{head_name}.int8_scale", ref["int8_scale"], frozen[head_name]["int8_scale"]))
        # 候选理论上界：manifest 两头几何乘积与 2B 参考实现宏（N3 关闭）
        candidate_checks: list[tuple[str, object, object]] = []
        products = [head["shape_nchw"][2] * head["shape_nchw"][3] for head in manifest["address_map"]["heads"]]
        computed_max = sum(products) * 3 * len(post["class_order"])
        candidate_checks.append(("candidate_theoretical_max(manifest 两头几何×3 anchors×classes)", computed_max, frozen["candidate_theoretical_max"]))
        ref_binding = next((b for b in contract["upstream_bindings"] if b.get("id") == "s2b_ps_decode_reference_impl"), None)
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
                candidate_checks.append(("S2A_T62_MAX_CANDIDATES(2B C 参考)", declared_max, frozen["candidate_theoretical_max"]))
                details["s2b_max_candidates_observed"] = declared_max
            else:
                failures.append(f"2B 参考实现文件不可读：{ref_path}")
        all_checks = upstream_checks + head_checks + candidate_checks
        mismatches = [
            {"item": name, "upstream": upstream, "contract": declared}
            for name, upstream, declared in all_checks
            if upstream != declared
        ]
        details["frozen_constant_checks"] = {
            "checked": len(all_checks),
            "mismatches": mismatches,
        }
        if mismatches:
            failures.append(f"2A 冻结常量与上游文件不一致：{mismatches}")
        else:
            passes.append(
                f"2A 冻结常量与上游文件一致（{len(all_checks)} 项：manifest detection_postprocess/address_map.heads、"
                "T29 head_tensors、候选理论上界与 2B 参考实现宏）"
            )

    # 7. 未冻结标注
    for probe in ("DRAFT_PROPOSED", "未冻结"):
        if probe not in doc_text:
            failures.append(f"人读草案缺少未冻结标注：{probe}")
    if "WARNING" not in contract["draft_proposed_thresholds"]:
        failures.append("draft_proposed_thresholds 缺少 WARNING 声明")
    if "DRAFT_PROPOSED" in doc_text and "未冻结" in doc_text and "WARNING" in contract["draft_proposed_thresholds"]:
        passes.append("草案未冻结值显式标注（DRAFT_PROPOSED / 未冻结 / WARNING）")

    status = "PASS" if not failures else "FAIL"
    evidence_files = [
        {"path": str(CONTRACT), "sha256": sha256_of(CONTRACT), "purpose": "被审契约"},
        {"path": str(HUMAN_DOC), "sha256": sha256_of(HUMAN_DOC), "purpose": "被审人读草案"},
        {"path": str(Path(__file__).resolve()), "sha256": sha256_of(Path(__file__).resolve()), "purpose": "本自检脚本"},
    ]
    report = {
        "task_id": "S4-A",
        "checker_version": "r05",
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
        print(f"[INFO] 证据已写入 {out_dir / 'verify_s4a_draft_result.json'}")

    for line in passes:
        print(f"[PASS] {line}")
    for line in failures:
        print(f"[FAIL] {line}")
    print(f"[{status}] S4-A 草案自检：{len(passes)} 项通过、{len(failures)} 项失败")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())