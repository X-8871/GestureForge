#!/usr/bin/env python3
"""阶段4↔阶段5 共享输入/结果契约与注入运行书只读自检（r05）。

退出码：0 = 全部 PASS，1 = 存在 FAIL，2 = 输入/环境错误。

检查项：
  1. JSON 可解析、必需顶层键齐全；
  2. upstream_bindings 现场复算 SHA-256（漂移即 FAIL）——修复 T1 的“权威无绑定”；
  3. 输入帧契约字段齐全、capture_time 语义与 S4-A 一致（0 哨兵 + 注解；禁止“不是 0/用注入起点冒充”）；
  4. measurement_scope 键与取值域、source_kind 取值域与 S4-A 一致（不得自造枚举）；
  5. 事件顺序 8 步齐全且声明“不得用超时推断完成”；帧序列（重复/回退）规则存在；
  6. 人读 md 覆盖全部输入字段名；
  7. 结果字段/检测字段与 S4-A 权威**逐一相同**（修复 Z9 盲区）；
  8. 显示五元组齐全，`display_semantics` 取值等于阶段5 G0 的已决值（修复 T3）；
  9. `hud_field_sources` 键集合**恰等于** 13 个 HUD 字段（说明文字不得混入，修复 T4）；
 10. PS 侧日志唯一映射键 = (session_id, frame_id, result_seq)；
 11. stale 规则：**已批准**状态必须给出批准记录绑定、常量=200000000 ns、与阶段5 同源，并声明“已批准≠实现已同步”；
 12. 三范围冻结齐全（allowed/forbidden）；
 13. 消费边界（阶段5 只读/版本化/变更流程）；
 14. 运行书摘要、缓存说明和板上模板的输入/输出 invalidate 顺序一致，并拒绝反序变异；
 15. 真实彩色输入改绑（r04）：范围标签、阶段3 部署绑定、RGB565/B-G-R/RGB888 不混同、宽高/stride/原图坐标、采集时钟 PENDING、逐帧源帧哈希、回放标注规则。

本脚本只读；`--evidence-dir` 把结果清单（含命令、退出码、版本、时间戳、脚本自身 SHA）写入证据目录。
通过不代表契约已冻结、接口语义已独立复审或任何实物验收。
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CONTRACT = WORKTREE / "docs" / "stage4" / "s4b_shared_input_result_contract.json"
HUMAN_DOC = WORKTREE / "docs" / "stage4" / "S4B_shared_input_result_contract.md"
ADDRESS_MAP = WORKTREE / "docs" / "stage4" / "S4B_stage4_address_map.json"
S4A_MD = WORKTREE / "docs" / "stage4" / "S4A_stage4_g0_tracking_and_timing_draft.md"
RUNBOOK = WORKTREE / "docs" / "stage4" / "S4B_injection_path_runbook.md"
CN = timezone(timedelta(hours=8))

REQUIRED_TOP_KEYS = (
    "schema_version",
    "contract_version",
    "status",
    "upstream_bindings",
    "authority_rules",
    "binding_byte_basis",
    "input_source_profiles",
    "input_frame_contract",
    "result_contract",
    "scope_freeze",
    "consumption_boundary",
    "limits",
)

# r04 真实彩色改绑的硬绑定值（阶段3 无补偿部署身份；不得被静默改写）。
STAGE3_SOF_SHA256 = "7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710"
STAGE3_ELF_SHA256 = "1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073"
STAGE3_COLOUR_LABELS = ("camera_live_colour", "camera_capture_replay_colour")
APPROVED_STALE_NS = 200000000
CDX_015_PREVIOUS_SHA256 = "a3ce50d20f2f3b1d573831c18d6d0c347966b9a16699b8cb48cdcee89ee170a7"

REQUIRED_INPUT_FIELDS = (
    "contract_version", "source_kind", "session_id", "frame_id", "width", "height",
    "pixel_format", "byte_order", "stride_bytes", "buffer", "frame_integrity",
    "capture_time_available", "injection_start_ns", "capture_time_ns",
    "timestamp_source", "clock_domain", "measurement_scope",
)

EVENT_ORDER = (
    "producer_write_start", "producer_write_complete", "cache_flush_by_producer",
    "ownership_publish_to_consumer", "consumer_invalidate", "consumer_start",
    "consumer_done", "buffer_release_to_producer",
)

HUD_FIELDS = (
    "capture_fps", "inference_fps", "display_fps", "inference_time_ns", "age_result_ns",
    "age_frame_ns", "frame_id", "boxes", "stale_cleared", "dropped_frames",
    "timeouts", "warmup_state", "display_semantics",
)

DISPLAY_LINKAGE = ("displayed_frame_id", "result_frame_id", "age_result_ns", "age_frame_ns", "display_semantics")
SCOPES = ("offline_regression", "board_injection", "camera")


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(path_text: str) -> Path:
    """相对路径按工作树解析，绝对路径原样使用。"""
    p = Path(path_text)
    return p if p.is_absolute() else WORKTREE / path_text


def find_git_root(path: Path) -> Path | None:
    """向上查找包含 `.git` 的目录（worktree 中 `.git` 可能是文件）。"""
    for parent in [path.parent, *path.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def blob_content_bytes(path: Path, revision: str = "HEAD") -> tuple[bytes | None, str | None]:
    """读取指定修订的原始 blob 字节；失败时禁止回退磁盘。"""
    root = find_git_root(path)
    if root is None:
        return None, f"未找到 git 根：{path}"
    rel = path.relative_to(root).as_posix()
    proc = subprocess.run(["git", "-C", str(root), "cat-file", "blob", f"{revision}:{rel}"], capture_output=True)
    if proc.returncode != 0:
        return None, f"cat-file blob {revision}:{rel} 退出 {proc.returncode}（修订或路径不存在）"
    return proc.stdout, None


def blob_content_sha256(path: Path, revision: str = "HEAD") -> tuple[str | None, str | None]:
    """按指定修订的原始 blob 字节计算 SHA-256。"""
    raw, error = blob_content_bytes(path, revision)
    return (hashlib.sha256(raw).hexdigest() if raw is not None else None), error


def read_binding_bytes(binding: dict) -> tuple[str, bytes | None, str | None]:
    """按声明口径只读取一次原始字节；供哈希与语义解析共同使用。

    status: MATCH / MISMATCH / MISSING / BLOB_UNAVAILABLE / BAD_BYTE_BASIS
    byte_basis：
      - worktree_disk_bytes：工作树磁盘原始字节（默认）
      - git_blob_content：`HEAD:<path>` 的 blob 内容（随 HEAD 移动）
      - git_blob_fixed_revision：`<fixed_revision>:<path>` 的 blob 内容（**固定修订，不随 HEAD 移动**）
    """
    path = resolve(binding["path"])
    basis = binding.get("byte_basis", "worktree_disk_bytes")
    if basis == "worktree_disk_bytes":
        if not path.is_file():
            return "MISSING", None, f"文件不存在：{path}"
        try:
            raw = path.read_bytes()
        except OSError as exc:
            return "MISSING", None, f"文件不可读：{path}：{exc}"
    elif basis == "git_blob_content":
        raw, error = blob_content_bytes(path)
        if raw is None:
            return "BLOB_UNAVAILABLE", None, error
    elif basis == "git_blob_fixed_revision":
        revision = binding.get("fixed_revision")
        if not revision:
            return "BAD_BYTE_BASIS", None, "git_blob_fixed_revision 必须给出 fixed_revision"
        raw, error = blob_content_bytes(path, revision)
        if raw is None:
            return "BLOB_UNAVAILABLE", None, error
    else:
        return "BAD_BYTE_BASIS", None, f"未知 byte_basis：{basis}"
    actual = hashlib.sha256(raw).hexdigest()
    return ("MATCH" if actual == binding.get("sha256") else "MISMATCH"), raw, None


def verify_binding_entry(binding: dict) -> tuple[str, str | None, str | None]:
    """兼容现有调用，按统一读取口径返回状态、实际 SHA 与错误。"""
    status, raw, error = read_binding_bytes(binding)
    return status, (hashlib.sha256(raw).hexdigest() if raw is not None else None), error


def find_key(obj: object, key: str):
    """在嵌套 dict/list 中递归查找第一个匹配键的值。"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                return v
            found = find_key(v, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_key(item, key)
            if found is not None:
                return found
    return None


def contains_in_order(text: str, tokens: tuple[str, ...]) -> bool:
    """按给定顺序查找运行书中的缓存可见性步骤。"""
    positions = [text.find(token) for token in tokens]
    return all(position >= 0 for position in positions) and positions == sorted(positions)


def validate_runbook_cache_order(runbook: str) -> list[str]:
    """检查摘要、实现依据和板上模板分别描述正确的读前维护顺序。"""
    errors: list[str] = []
    summary = next((line for line in runbook.splitlines() if line.startswith("- 覆盖：")), "")
    if "输入帧在 `consumer_start` 前执行 invalidate + DSB" not in summary:
        errors.append("运行书摘要未明确输入帧在 consumer_start 前 invalidate + DSB")
    pl_done_index = summary.find("PL done")
    output_summary = summary[pl_done_index:] if pl_done_index >= 0 else ""
    if not contains_in_order(output_summary, ("PL done", "输出 heads", "invalidate + DSB", "再读取")):
        errors.append("运行书摘要未明确 PL done 后 heads invalidate + DSB 再读取")

    output_rule = next((line for line in runbook.splitlines() if "PL 输出 heads：" in line), "")
    if not contains_in_order(output_rule, ("PL done", "invalidate", "DSB", "再读取 heads")):
        errors.append("运行书实现依据未按 PL done→heads invalidate+DSB→读 heads 描述")

    template = next((line for line in runbook.splitlines() if line.startswith("# 4) 单帧注入")), "")
    if not contains_in_order(
        template,
        ("等 PL done", "输出 heads invalidate + DSB", "读 heads", "确认消费者停止/复位", "释放"),
    ):
        errors.append("运行书板上模板的 done/invalidate/读 heads/停止确认/释放顺序错误")
    return errors


def validate_r03_semantics(contract: dict, doc: str, address_map: dict, s4a: dict) -> list[str]:
    """检查 r03 新增的接口和缓存语义约束。"""
    errors: list[str] = []
    fields = {field.get("name"): field for field in contract["input_frame_contract"]["fields"]}
    if fields.get("session_id", {}).get("type") != "uint32":
        errors.append("session_id 必须与 S4-A 一致使用 uint32")
    if "u32" not in fields.get("session_id", {}).get("semantics", ""):
        errors.append("session_id 缺 S4-A u32 分配/重置语义")

    source_map = contract["input_frame_contract"]["vocabulary_mapping"].get("source_kind", {}).get("map")
    expected_map = {
        "file_injection": "BOARD_INJECTION",
        "synthetic": "OFFLINE_REGRESSION",
        "camera": "CAMERA",
    }
    if source_map != expected_map:
        errors.append("source_kind 必须严格一一映射到三个 S4-A source_kind")

    truth = contract["input_frame_contract"]["vocabulary_mapping"].get("capture_time_truth_table")
    expected_truth = {
        "file_injection": {
            "capture_time_available": False,
            "capture_time_ns": 0,
            "unavailable_fields_contains_capture_time_ns": True,
        },
        "synthetic": {
            "capture_time_available": False,
            "capture_time_ns": 0,
            "unavailable_fields_contains_capture_time_ns": True,
        },
        "camera": {
            "capture_time_available": True,
            "capture_time_ns": "nonzero",
            "unavailable_fields_contains_capture_time_ns": False,
        },
    }
    if truth != expected_truth:
        errors.append("capture_time 真值表必须完整覆盖三种来源")
    capture_available = fields.get("capture_time_available", {}).get("semantics", "")
    capture_ns = fields.get("capture_time_ns", {}).get("semantics", "")
    if not all(token in capture_available for token in ("synthetic", "camera", "false", "true")):
        errors.append("capture_time_available 语义缺 synthetic/camera 完整约束")
    if not all(token in capture_ns for token in ("synthetic", "camera", "0 哨兵", "非零")):
        errors.append("capture_time_ns 语义缺 synthetic/camera 哨兵与真值约束")

    order = contract["input_frame_contract"]["events"].get("order")
    if tuple(order or ()) != EVENT_ORDER:
        errors.append("消费者必须在 start 前完成 input invalidate")

    roles = contract["result_contract"]["ps_side_log"].get("mapping_key_roles", {})
    bypass = s4a.get("uart_plan_b_freeze", {}).get("result_bypass_log_mapping", {})
    expected_roles = {
        "stage4a_join_key": bypass.get("join_key"),
        "ps_log_primary_key": bypass.get("ps_log_primary_key"),
        "uart_observable_key": bypass.get("uart_observable_key"),
    }
    if any(roles.get(name, {}).get("fields") != value for name, value in expected_roles.items()):
        errors.append("S4-A join_key/PS 主键/UART 可观测键未逐项保持原用途")
    if not all(name in roles.get("bridge_log_fields", []) for name in
               ("session_id", "frame_id", "repeat_index", "result_seq", "sequence")):
        errors.append("桥接日志字段未同时保留 S4-A 键字段")

    if address_map.get("status") != "DRAFT_PENDING_REVIEW":
        errors.append("地址图 status 必须保持 DRAFT_PENDING_REVIEW")
    address_space = address_map.get("address_space", {})
    if address_space.get("hardware_cache_line_bytes") != 32:
        errors.append("地址图硬件缓存行必须为冻结 2B BSP 的 32 B")
    if address_space.get("maintenance_alignment_bytes") != 64:
        errors.append("地址图维护对齐策略必须独立声明为 64 B")
    facts = {fact.get("id"): fact for fact in address_map.get("factsources", [])}
    app_fact = facts.get("W2B-APP", {})
    if app_fact.get("sha256") != "9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39":
        errors.append("32 B 缓存行事实未绑定冻结 2B BSP 源码 SHA")

    cdc = contract["input_frame_contract"].get("cache_and_dma_rules", {})
    if cdc.get("hardware_cache_line_bytes") != 32 or cdc.get("maintenance_alignment_bytes") != 64:
        errors.append("共享契约未区分 2B BSP 缓存行参数与维护对齐策略")
    if "PL 输出" not in cdc.get("pl_output_visibility", ""):
        errors.append("PL 输出 done 后 invalidate 未与输入帧事件分开说明")
    if "DRAFT_PENDING_REVIEW" not in doc or "由 4-B 任务冻结" in doc:
        errors.append("人读契约错误声称地址图已冻结")
    if "75278f8dcad0fdacbec9946f59e1841061698c0237a090b1410b293be0460f84" not in doc:
        errors.append("人读契约未绑定当前 S4-A r06 镜像 SHA")
    return errors


def validate_approved_stale_core(contract: dict) -> list[str]:
    """检查 11 核心：已批准 stale 常量必须附批准记录、同源、且不当成已实现。"""
    errors: list[str] = []
    stale = contract.get("result_contract", {}).get("stale_rule", {})
    value = stale.get("stale_limit_ns")
    status = stale.get("stale_limit_status")
    ref = stale.get("approval_reference") or {}
    if status != "APPROVED_BY_WONG":
        errors.append(f"stale_limit_status 必须为 APPROVED_BY_WONG（已批准后不得保留 DRAFT），实际 {status}")
    if value != APPROVED_STALE_NS:
        errors.append(f"stale_limit_ns 必须为已批准值 {APPROVED_STALE_NS}，实际 {value}")
    if not ref.get("receipt_path") or not ref.get("receipt_sha256"):
        errors.append("已批准状态必须给出 approval_reference.receipt_path 与 receipt_sha256")
    else:
        receipt = resolve(str(ref["receipt_path"]))
        if not receipt.is_file():
            errors.append(f"批准记录不存在：{receipt}")
        elif sha256_of(receipt) != ref["receipt_sha256"]:
            errors.append(f"批准记录 SHA 漂移：绑定 {ref['receipt_sha256']} 实际 {sha256_of(receipt)}")
    if not ref.get("approved_means_not_implemented"):
        errors.append("已批准状态必须显式声明『已批准不等于实现已同步』")
    if not stale.get("s4a_r06_supersession_note"):
        errors.append("已批准状态必须写明 S4-A r06 内 DRAFT 标签的取代关系")
    return errors


def validate_colour_profiles(contract: dict) -> list[str]:
    """检查 15：真实彩色输入改绑（r04）的结构与硬绑定值。"""
    errors: list[str] = []
    prof = contract.get("input_source_profiles")
    if not isinstance(prof, dict):
        return ["缺少 input_source_profiles（真实彩色输入改绑未落实）"]
    if "描述性" not in str(prof.get("label_rule", "")):
        errors.append("必须声明范围标签是描述性标签而非新枚举值")
    labels = {entry.get("label"): entry for entry in prof.get("descriptive_labels", [])}
    for name in STAGE3_COLOUR_LABELS:
        if name not in labels:
            errors.append(f"缺范围标签 {name}")
    for name, entry in labels.items():
        if entry.get("maps_to_source_kind") != "camera":
            errors.append(f"{name} 必须映射到 source_kind=camera（不得新增 S4-A 未定义枚举）")
    live = labels.get("camera_live_colour", {})
    replay = labels.get("camera_capture_replay_colour", {})
    if live.get("timing_claim_scope") != "real_live":
        errors.append("camera_live_colour 必须声明 real_live 计时口径")
    if replay.get("timing_claim_scope") != "replay_only":
        errors.append("camera_capture_replay_colour 必须声明 replay_only 计时口径")
    if not any("回放计时" in str(item) for item in replay.get("forbidden_claims", [])):
        errors.append("回放标签必须禁止把回放计时当实时端到端证据")
    if "replay" not in str(prof.get("replay_labeling_rule", "")).lower():
        errors.append("必须声明回放必须标注为回放的规则")

    fmt = prof.get("sensor_and_ddr_format", {})
    for token, field in (("RGB565", "sensor_output"), ("B/G/R", "ddr_dump_byte_order"), ("RGB888", "model_semantics")):
        if token not in str(fmt.get(field, "")):
            errors.append(f"sensor_and_ddr_format.{field} 必须写明 {token}")
    if "不得直接混同" not in str(fmt.get("rule", "")):
        errors.append("必须声明传感器 RGB565 / DDR B-G-R / 模型 RGB888 三层语义不得直接混同")

    dep = prof.get("stage3_deployment_bindings", {})
    if dep.get("uncompensated_sof_bit_sha256") != STAGE3_SOF_SHA256:
        errors.append("必须绑定阶段3 无补偿 SOF 位流 SHA-256")
    if dep.get("runtime_elf_sha256") != STAGE3_ELF_SHA256:
        errors.append("必须绑定阶段3 运行 ELF SHA-256")

    geo = prof.get("frame_geometry", {})
    if (geo.get("width"), geo.get("height"), geo.get("stride_bytes_per_row")) != (1280, 720, 3840):
        errors.append("必须绑定 1280×720 与 stride 3840 B/行")
    if "原图" not in str(geo.get("source_frame_coordinate_basis", "")):
        errors.append("必须声明检测框以原图坐标为准、416 张量坐标不得直接充当原图坐标")
    if prof.get("capture_clock", {}).get("status") != "PENDING_MEASUREMENT":
        errors.append("采集时钟必须保持 PENDING_MEASUREMENT（未实测不得填造频率）")
    if not prof.get("source_frame_hash_rule", {}).get("rule"):
        errors.append("必须给出逐帧源帧哈希绑定规则")
    return errors


def main() -> int:
    """执行全部检查。"""
    parser = argparse.ArgumentParser(description="共享输入/结果契约只读自检")
    parser.add_argument("--evidence-dir", default="")
    args = parser.parse_args()

    failures: list[str] = []
    passes: list[str] = []
    details: dict[str, object] = {}

    if (not CONTRACT.is_file() or not HUMAN_DOC.is_file() or not ADDRESS_MAP.is_file()
            or not S4A_MD.is_file() or not RUNBOOK.is_file()):
        print(f"[FAIL] 契约/地址图/S4-A 镜像/注入运行书缺失：{CONTRACT} / {HUMAN_DOC} / {ADDRESS_MAP} / {S4A_MD} / {RUNBOOK}")
        return 2
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[FAIL] 契约 JSON 无法解析：{exc}")
        return 2
    doc = HUMAN_DOC.read_text(encoding="utf-8")
    address_map = json.loads(ADDRESS_MAP.read_text(encoding="utf-8"))
    runbook = RUNBOOK.read_text(encoding="utf-8")

    runbook_errors = validate_runbook_cache_order(runbook)
    details["runbook_cache_order_errors"] = runbook_errors
    if runbook_errors:
        failures.extend(runbook_errors)
    else:
        passes.append("运行书摘要/缓存说明/板上模板的输入与 heads 输出维护顺序一致")
    mutated_runbook = runbook.replace(
        "等 PL done → 输出 heads invalidate + DSB",
        "输出 heads invalidate + DSB → 等 PL done",
        1,
    )
    mutation_errors = validate_runbook_cache_order(mutated_runbook)
    mutation_detected = mutated_runbook != runbook and bool(mutation_errors)
    details["runbook_negative_controls"] = {
        "output_invalidate_before_pl_done": {
            "mutated": mutated_runbook != runbook,
            "detected": mutation_detected,
            "errors": mutation_errors,
        }
    }
    if mutation_detected:
        passes.append("运行书 PL done/输出 invalidate 反序变异 1/1 被拒绝")
    else:
        failures.append("运行书 PL done/输出 invalidate 反序变异未检出")

    # 1. 顶层键
    missing = [k for k in REQUIRED_TOP_KEYS if k not in contract]
    if missing:
        failures.append(f"缺少必需顶层键：{missing}")
    else:
        passes.append("契约 JSON 可解析且必需顶层键齐全")

    # 2. 权威绑定现场复算（T1）
    bindings = {b["id"]: b for b in contract.get("upstream_bindings", [])}
    bound_bytes: dict[str, bytes] = {}
    if not bindings:
        failures.append("缺少 upstream_bindings（权威无版本绑定）")
    else:
        bad: list[dict[str, object]] = []
        checked = 0
        for bid, b in bindings.items():
            path = resolve(b["path"])
            entry: dict[str, object] = {
                "id": bid, "path": str(path), "expected": b.get("sha256"),
                "byte_basis": b.get("byte_basis", "worktree_disk_bytes"),
            }
            status, raw, error = read_binding_bytes(b)
            actual = hashlib.sha256(raw).hexdigest() if raw is not None else None
            entry["status"] = status
            if error:
                entry["error"] = error
            if actual is not None:
                entry["actual"] = actual
            if status != "MATCH":
                bad.append(entry)
            else:
                checked += 1
                bound_bytes[bid] = raw
        details["upstream_binding_checks"] = {"checked": checked, "total": len(bindings), "bad": bad}
        if bad:
            failures.append(f"权威绑定漂移（必须显式更新绑定并重新审查）：{bad}")
        else:
            passes.append(f"upstream_bindings 现场复算一致（{checked}/{len(bindings)} 项）")
        superseded = bindings.get("cdx_015_execution_index_r02", {}).get("replaces", {})
        if superseded.get("sha256") != CDX_015_PREVIOUS_SHA256:
            failures.append("cdx_015 绑定被更新但未登记 replaces 取代关系（禁止静默改绑定）")
        else:
            passes.append("cdx_015 r02→r03 绑定取代关系已登记")

        # 2b. 绑定字节口径声明（N-1）
        bbb = contract.get("binding_byte_basis")
        basis_errors: list[str] = []
        blob_ids = [bid for bid, b in bindings.items() if b.get("byte_basis") == "git_blob_content"]
        if not isinstance(bbb, dict):
            basis_errors.append("缺少 binding_byte_basis（绑定字节口径未声明）")
        else:
            if bbb.get("default_basis") != "worktree_disk_bytes":
                basis_errors.append("binding_byte_basis.default_basis 必须为 worktree_disk_bytes")
            if "core.autocrlf=false" not in str(bbb.get("cross_newline_requirement", "")):
                basis_errors.append("binding_byte_basis 必须声明 `-c core.autocrlf=false` 跨换行复算前提")
            if not bbb.get("explicit_blob_basis"):
                basis_errors.append("binding_byte_basis 必须声明 git_blob_content 口径语义")
            if not bbb.get("negative_control_expectation"):
                basis_errors.append("binding_byte_basis 必须声明负向对照预期")
        if not blob_ids:
            basis_errors.append("至少应有一个 git_blob_content 绑定（dbdf 两项彩色证据）")
        # 负向对照：把 blob 口径条目改回其磁盘 SHA，必须被同一条口径规则判 MISMATCH
        basis_controls: dict[str, bool] = {}
        if blob_ids:
            target = copy.deepcopy(bindings[blob_ids[0]])
            original = target["sha256"]
            target["sha256"] = ("0" if original[0] != "0" else "1") + original[1:]
            basis_controls["wrong_sha_under_blob_basis"] = verify_binding_entry(target)[0] == "MISMATCH"
            wrong = copy.deepcopy(bindings[blob_ids[0]])
            wrong["byte_basis"] = "not_a_basis"
            basis_controls["unknown_byte_basis"] = verify_binding_entry(wrong)[0] == "BAD_BYTE_BASIS"
            disk_entry = copy.deepcopy(bindings[blob_ids[0]])
            disk_sha = sha256_of(resolve(disk_entry["path"]))
            if disk_sha != original:
                disk_entry["sha256"] = disk_sha
                basis_controls["disk_sha_under_blob_basis"] = verify_binding_entry(disk_entry)[0] == "MISMATCH"

        # 2c. 固定修订口径（不随 HEAD 移动）负向对照
        fixed_ids = [bid for bid, b in bindings.items() if b.get("byte_basis") == "git_blob_fixed_revision"]
        if fixed_ids:
            fixed = copy.deepcopy(bindings[fixed_ids[0]])
            basis_controls["fixed_revision_binds_pinned"] = verify_binding_entry(fixed)[0] == "MATCH"
            no_rev = copy.deepcopy(bindings[fixed_ids[0]])
            no_rev.pop("fixed_revision", None)
            basis_controls["fixed_revision_missing_revision"] = verify_binding_entry(no_rev)[0] == "BAD_BYTE_BASIS"
            head_sha, _ = blob_content_sha256(resolve(fixed["path"]), "HEAD")
            if head_sha and head_sha != fixed["sha256"]:
                drift_head = copy.deepcopy(bindings[fixed_ids[0]])
                drift_head["sha256"] = head_sha
                basis_controls["fixed_revision_rejects_head_content"] = \
                    verify_binding_entry(drift_head)[0] == "MISMATCH"
            details["binding_byte_basis_fixed_revision"] = {
                "entries": fixed_ids, "fixed_revision": fixed.get("fixed_revision"),
                "head_content_differs_from_pinned": bool(head_sha and head_sha != fixed["sha256"]),
            }
        details["binding_byte_basis"] = {"blob_entries": blob_ids, "negative_controls": basis_controls}
        if basis_errors:
            failures.extend(basis_errors)
        elif not all(basis_controls.values()):
            failures.append(f"绑定字节口径负向对照未全部检出：{basis_controls}")
        else:
            passes.append(f"绑定字节口径声明齐全（默认磁盘字节；blob 口径 {len(blob_ids)} 项）+ 2/2 负向对照被拒绝")

    # 只解析本轮哈希已通过的同一份字节，禁止再次读取磁盘或移动后的 HEAD。
    authority_json = {}
    for bid in ("s4a_g0_contract", "stage5_display_g0_fields"):
        authority_json[bid] = None
        if bid in bound_bytes:
            try:
                parsed = json.loads(bound_bytes[bid].decode("utf-8"))
                if not isinstance(parsed, dict):
                    raise ValueError("权威 JSON 顶层必须为对象")
                authority_json[bid] = parsed
            except (UnicodeDecodeError, ValueError) as exc:
                failures.append(f"已绑定权威 JSON 无法解析：{bid}：{exc}")
    s4a = authority_json["s4a_g0_contract"]
    w5 = authority_json["stage5_display_g0_fields"]
    if s4a is None:
        failures.append("无法读取 S4-A 权威以检查 r03 接口语义")
    else:
        semantic_errors = validate_r03_semantics(contract, doc, address_map, s4a)
        if semantic_errors:
            failures.extend(semantic_errors)
        else:
            passes.append("r03 session/source/time/key/cache 语义与 S4-A、地址图一致")
        current_s4a_md_sha = sha256_of(S4A_MD)
        if current_s4a_md_sha not in doc:
            failures.append(f"S4-A 人读镜像 SHA 漂移：契约文档未绑定 {current_s4a_md_sha}")
        else:
            passes.append("S4-A 人读镜像 SHA 与当前 r06 文件一致")

        mutations: list[tuple[str, dict, dict]] = []
        changed = copy.deepcopy(contract)
        next(field for field in changed["input_frame_contract"]["fields"]
             if field["name"] == "session_id")["type"] = "string"
        mutations.append(("session_id_type", changed, address_map))
        changed = copy.deepcopy(contract)
        changed["input_frame_contract"]["vocabulary_mapping"]["source_kind"]["map"]["synthetic"] = "synthetic"
        mutations.append(("extra_source_mapping", changed, address_map))
        changed = copy.deepcopy(contract)
        changed["input_frame_contract"]["vocabulary_mapping"]["capture_time_truth_table"]["synthetic"]["capture_time_available"] = True
        mutations.append(("synthetic_capture_truth", changed, address_map))
        changed = copy.deepcopy(contract)
        changed["input_frame_contract"]["events"]["order"][4:7] = [
            "consumer_start", "consumer_done", "consumer_invalidate"
        ]
        mutations.append(("invalidate_after_read", changed, address_map))
        changed_map = copy.deepcopy(address_map)
        changed_map["status"] = "FROZEN"
        mutations.append(("address_map_frozen", copy.deepcopy(contract), changed_map))
        mutation_results = {
            name: bool(validate_r03_semantics(candidate, doc, mutated_map, s4a))
            for name, candidate, mutated_map in mutations
        }
        details["r03_negative_controls"] = mutation_results
        if all(mutation_results.values()):
            passes.append("r03 检查器变异反例 5/5 均被拒绝")
        else:
            failures.append(f"r03 检查器变异反例未全部检出：{mutation_results}")

    # 3. 输入字段与 capture_time 语义
    inputs = contract["input_frame_contract"]["fields"]
    names = [f["name"] for f in inputs]
    missing_fields = [n for n in REQUIRED_INPUT_FIELDS if n not in names]
    details["input_field_count"] = len(names)
    if missing_fields:
        failures.append(f"输入帧契约缺字段：{missing_fields}")
    else:
        passes.append(f"输入帧契约字段齐全（{len(names)} 项）")
    inj = next((f for f in inputs if f["name"] == "injection_start_ns"), None)
    cap = next((f for f in inputs if f["name"] == "capture_time_ns"), None)
    inj_sem = (inj or {}).get("semantics", "")
    cap_sem = (cap or {}).get("semantics", "")
    if "不是采集时间" not in inj_sem:
        failures.append("injection_start_ns 未声明“不是采集时间”")
    if "0 哨兵" not in cap_sem:
        failures.append("capture_time_ns 未声明 S4-A 的 0 哨兵 + 注解判别口径")
    if "不是 0" in cap_sem:
        failures.append("capture_time_ns 出现“不是 0”的冲突写法（与 S4-A 的 0 哨兵约定冲突）")
    if not failures or "capture_time_ns" not in " ".join(failures):
        passes.append("capture_time 语义与 S4-A 一致（0 哨兵 + 注解；注入起点不得冒充）")

    # 4. 词表与 S4-A 一致（T2）
    vm = contract["input_frame_contract"]["vocabulary_mapping"]
    if s4a is None:
        failures.append("无法读取 S4-A 权威以核对词表")
    else:
        ms_keys = s4a["evidence_annotation"]["measurement_scope"]["keys"]
        expected_keys = sorted(ms_keys.keys())
        if sorted(vm["measurement_scope_keys"]) != expected_keys:
            failures.append(f"measurement_scope 键集合与 S4-A 不一致：契约 {sorted(vm['measurement_scope_keys'])} vs S4-A {expected_keys}")
        else:
            passes.append(f"measurement_scope 键集合与 S4-A 一致（{len(expected_keys)} 个）")
        for key in ("pl_timing", "uart_transport", "board_pl"):
            expected_vals = ms_keys.get(key, {}).get("allowed_values")
            contract_vals = vm.get(f"{key}_allowed")
            if expected_vals is not None and contract_vals != expected_vals:
                failures.append(f"{key} 取值域与 S4-A 不一致：契约 {contract_vals} vs S4-A {expected_vals}")
        if not any("取值域与 S4-A 不一致" in f for f in failures):
            passes.append("pl_timing/uart_transport/board_pl 取值域与 S4-A 一致（无自造枚举）")
        sk = ms_keys.get("source_kind", {}).get("allowed_values")
        if sk is not None:
            mapped = set((vm.get("source_kind", {}).get("map") or {}).keys())
            declared = set(vm.get("source_kind", {}).get("s4a") or [])
            if declared != set(sk):
                failures.append(f"source_kind 声明与 S4-A 不一致：{sorted(declared)} vs {sorted(sk)}")
            else:
                passes.append("source_kind 取值域声明与 S4-A 一致（含跨命名映射）")
            details["source_kind_map_entries"] = sorted(mapped)
        else:
            details["source_kind_check"] = "S4-A 未提供 allowed_values，跳过（如实记录）"

    # 5. 事件与帧序列规则
    events = contract["input_frame_contract"]["events"]
    if tuple(events.get("order", [])) != EVENT_ORDER:
        failures.append(f"事件顺序不完整：{events.get('order')}")
    else:
        passes.append("事件顺序 8 步齐全且次序正确")
    if "不得用超时推断完成" not in events.get("rule", ""):
        failures.append("事件规则未声明不得用超时推断完成")
    seq = contract["input_frame_contract"].get("frame_sequence_rules", {})
    if not all(k in seq for k in ("duplicate_frame_id", "regressed_frame_id", "out_of_order_result")):
        failures.append("帧序列规则缺重复/回退/乱序声明（N5）")
    else:
        passes.append("帧序列规则含重复/回退/乱序处理（N5）")

    # 6. md 覆盖
    uncovered = [n for n in names if n not in doc]
    details["md_uncovered_input_fields"] = uncovered
    if uncovered:
        failures.append(f"人读契约未覆盖输入字段：{uncovered}")
    else:
        passes.append("人读契约覆盖全部输入字段名")

    # 7. 结果字段与 S4-A 逐一相同（Z9）
    if s4a is not None:
        rc = contract["result_contract"]["result_record"]
        s4a_res = {f["name"] for f in s4a["result_record"]["fields"]}
        s4a_det = {f["name"] for f in s4a["detection_record"]["fields"]}
        if set(rc["fields"]) != s4a_res:
            failures.append(f"结果字段与 S4-A 不一致：only-contract={sorted(set(rc['fields'])-s4a_res)} only-s4a={sorted(s4a_res-set(rc['fields']))}")
        elif set(rc["detection_fields"]) != s4a_det:
            failures.append(f"检测字段与 S4-A 不一致：only-contract={sorted(set(rc['detection_fields'])-s4a_det)} only-s4a={sorted(s4a_det-set(rc['detection_fields']))}")
        else:
            passes.append(f"结果字段 {len(s4a_res)} 项与检测字段 {len(s4a_det)} 项与 S4-A 逐一相同")

    # 8. 五元组与 display_semantics 取值（T3）
    linkage = contract["result_contract"]["display_linkage"]["fields"]
    lmap = {f["name"]: f for f in linkage}
    missing_linkage = [n for n in DISPLAY_LINKAGE if n not in lmap]
    if missing_linkage:
        failures.append(f"显示五元组缺字段：{missing_linkage}")
    else:
        passes.append("显示关联五元组齐全（5 项）")
    ds_values = lmap.get("display_semantics", {}).get("values")
    if w5 is not None:
        w5_ds = find_key(w5, "display_semantics")
        w5_value = w5_ds.get("value") if isinstance(w5_ds, dict) else None
        details["stage5_display_semantics_value"] = w5_value
        if w5_value and ds_values != [w5_value]:
            failures.append(f"display_semantics 取值与阶段5 G0 不一致：契约 {ds_values} vs w5 {w5_value}")
        elif w5_value:
            passes.append(f"display_semantics 取值等于阶段5 G0 已决值（{w5_value}）")

    # 9. HUD 键集合恰等于 13（T4）
    hud = contract["result_contract"]["hud_field_sources"]
    if sorted(hud.keys()) != sorted(HUD_FIELDS):
        failures.append(f"hud_field_sources 键不恰为 13 字段：extra={sorted(set(hud)-set(HUD_FIELDS))} missing={sorted(set(HUD_FIELDS)-set(hud))}")
    else:
        passes.append("hud_field_sources 键集合恰等于 13 个 HUD 字段")

    # 10. 唯一映射键
    key = contract["result_contract"]["ps_side_log"]["unique_mapping_key"]
    if key != ["session_id", "frame_id", "result_seq"]:
        failures.append(f"PS 侧唯一映射键不符：{key}")
    else:
        passes.append("PS 侧日志唯一映射键 = (session_id, frame_id, result_seq)")

    # 11. stale 规则（N6）+ 已批准项应用（r04）
    stale = contract["result_contract"]["stale_rule"]
    stale_errors = validate_approved_stale_core(contract)
    if not stale.get("expression") or not stale.get("stage4_stale_definition"):
        stale_errors.append("stale 规则缺 expression 或 stage4_stale_definition")
    if not stale.get("single_source_of_truth"):
        stale_errors.append("stale 未声明唯一常量来源（N6）")
    if w5 is not None:
        w5_stale = find_key(w5, "stale_age_limit_ns")
        details["stage5_stale_age_limit_ns"] = w5_stale
        if w5_stale != stale.get("stale_limit_ns"):
            stale_errors.append(f"跨阶段 stale 常量不同源：契约 {stale.get('stale_limit_ns')} vs 阶段5 {w5_stale}")
    else:
        stale_errors.append("无法读取阶段5 G0 以核对 stale 常量是否同源")

    stale_controls: dict[str, bool] = {}
    mutated = copy.deepcopy(contract)
    mutated["result_contract"]["stale_rule"]["stale_limit_status"] = "DRAFT_PENDING_APPROVAL"
    stale_controls["reverted_to_draft_status"] = bool(validate_approved_stale_core(mutated))
    mutated = copy.deepcopy(contract)
    mutated["result_contract"]["stale_rule"]["stale_limit_ns"] = 100000000
    stale_controls["wrong_limit_value"] = bool(validate_approved_stale_core(mutated))
    mutated = copy.deepcopy(contract)
    mutated["result_contract"]["stale_rule"]["approval_reference"]["receipt_sha256"] = "0" * 64
    stale_controls["forged_receipt_sha256"] = bool(validate_approved_stale_core(mutated))
    mutated = copy.deepcopy(contract)
    mutated["result_contract"]["stale_rule"].pop("approval_reference", None)
    stale_controls["missing_approval_reference"] = bool(validate_approved_stale_core(mutated))
    details["stale_negative_controls"] = stale_controls

    if stale_errors:
        failures.extend(stale_errors)
    elif not all(stale_controls.values()):
        failures.append(f"stale 已批准态负向对照未全部检出：{stale_controls}")
    else:
        passes.append("stale 已批准态：批准记录绑定 + 200000000 ns 与阶段5 同源 + 4/4 负向对照被拒绝")

    # 15. 真实彩色输入改绑（r04）
    colour_errors = validate_colour_profiles(contract)
    colour_controls: dict[str, bool] = {}
    if not colour_errors:
        mutated = copy.deepcopy(contract)
        mutated["input_source_profiles"]["descriptive_labels"][1]["timing_claim_scope"] = "real_live"
        colour_controls["replay_claimed_as_live"] = bool(validate_colour_profiles(mutated))
        mutated = copy.deepcopy(contract)
        mutated["input_source_profiles"]["sensor_and_ddr_format"]["ddr_dump_byte_order"] = "R/G/B"
        colour_controls["wrong_ddr_byte_order"] = bool(validate_colour_profiles(mutated))
        mutated = copy.deepcopy(contract)
        mutated["input_source_profiles"]["capture_clock"]["status"] = "MEASURED"
        colour_controls["fabricated_capture_clock"] = bool(validate_colour_profiles(mutated))
        mutated = copy.deepcopy(contract)
        mutated["input_source_profiles"]["stage3_deployment_bindings"]["runtime_elf_sha256"] = "0" * 64
        colour_controls["forged_elf_binding"] = bool(validate_colour_profiles(mutated))
    details["colour_profile_negative_controls"] = colour_controls
    if colour_errors:
        failures.extend(colour_errors)
    elif not all(colour_controls.values()):
        failures.append(f"彩色改绑负向对照未全部检出：{colour_controls}")
    else:
        passes.append("真实彩色改绑齐全（标签/部署绑定/三层语义/几何/采集时钟/源帧哈希）+ 4/4 负向对照被拒绝")

    # 12. 三范围
    sf = contract["scope_freeze"]
    missing_scopes = [s for s in SCOPES if s not in sf]
    if missing_scopes:
        failures.append(f"范围冻结缺范围：{missing_scopes}")
    else:
        bad_scopes = [s for s in SCOPES if not sf[s].get("allowed_claims") or not sf[s].get("forbidden_claims")]
        if bad_scopes:
            failures.append(f"范围缺 allowed/forbidden：{bad_scopes}")
        else:
            passes.append("三种范围均有 allowed 与 forbidden")

    # 13. 消费边界
    cb = contract["consumption_boundary"]
    if not all(k in cb for k in ("stage5_access", "versioning", "change_process")):
        failures.append("消费边界缺 stage5_access/versioning/change_process")
    elif "只读" not in cb["stage5_access"]:
        failures.append("消费边界未声明阶段5 只读")
    else:
        passes.append("消费边界声明阶段5 只读 + 版本化 + 变更流程")

    status = "PASS" if not failures else "FAIL"
    script_path = Path(__file__).resolve()
    report = {
        "task_id": "S4-CTRL/S4B-contract",
        "checker": "verify_shared_io_contract",
        "checker_version": "r07",
        "status": status,
        "generated_at_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "command": " ".join([sys.executable, *sys.argv]),
        "exit_code": 0 if status == "PASS" else 1,
        "cwd": str(Path.cwd()),
        "python_version": sys.version,
        "platform": platform.platform(),
        "artifact_sha256": {
            "contract_json": sha256_of(CONTRACT),
            "contract_md": sha256_of(HUMAN_DOC),
            "address_map": sha256_of(ADDRESS_MAP),
            "s4a_md_mirror": sha256_of(S4A_MD),
            "injection_runbook": sha256_of(RUNBOOK),
            "checker_script": sha256_of(script_path),
        },
        "passes": passes,
        "failures": failures,
        "details": details,
    }
    if args.evidence_dir:
        out = Path(args.evidence_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "verify_shared_io_contract_result.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[INFO] 证据已写入 {out / 'verify_shared_io_contract_result.json'}")
    for line in passes:
        print(f"[PASS] {line}")
    for line in failures:
        print(f"[FAIL] {line}")
    print(f"[{status}] 共享契约自检：{len(passes)} 项通过、{len(failures)} 项失败")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
