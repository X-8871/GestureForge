#!/usr/bin/env python3
"""阶段4↔阶段5 共享输入/结果契约（s4-shared-io）只读自检（r02）。

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
 11. stale 规则存在、状态为 DRAFT_PENDING_APPROVAL、声明唯一常量来源（修复 N6）；
 12. 三范围冻结齐全（allowed/forbidden）；
 13. 消费边界（阶段5 只读/版本化/变更流程）。

本脚本只读；`--evidence-dir` 把结果清单（含命令、退出码、版本、时间戳、脚本自身 SHA）写入证据目录。
通过不代表契约已冻结或任何实物验收。
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
CONTRACT = WORKTREE / "docs" / "stage4" / "s4b_shared_input_result_contract.json"
HUMAN_DOC = WORKTREE / "docs" / "stage4" / "S4B_shared_input_result_contract.md"
CN = timezone(timedelta(hours=8))

REQUIRED_TOP_KEYS = (
    "schema_version",
    "contract_version",
    "status",
    "upstream_bindings",
    "authority_rules",
    "input_frame_contract",
    "result_contract",
    "scope_freeze",
    "consumption_boundary",
    "limits",
)

REQUIRED_INPUT_FIELDS = (
    "contract_version", "source_kind", "session_id", "frame_id", "width", "height",
    "pixel_format", "byte_order", "stride_bytes", "buffer", "frame_integrity",
    "capture_time_available", "injection_start_ns", "capture_time_ns",
    "timestamp_source", "clock_domain", "measurement_scope",
)

EVENT_ORDER = (
    "producer_write_start", "producer_write_complete", "cache_flush_by_producer",
    "ownership_publish_to_consumer", "consumer_start", "consumer_done",
    "consumer_invalidate", "buffer_release_to_producer",
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


def main() -> int:
    """执行全部检查。"""
    parser = argparse.ArgumentParser(description="共享输入/结果契约只读自检")
    parser.add_argument("--evidence-dir", default="")
    args = parser.parse_args()

    failures: list[str] = []
    passes: list[str] = []
    details: dict[str, object] = {}

    if not CONTRACT.is_file() or not HUMAN_DOC.is_file():
        print(f"[FAIL] 契约文件缺失：{CONTRACT} / {HUMAN_DOC}")
        return 2
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[FAIL] 契约 JSON 无法解析：{exc}")
        return 2
    doc = HUMAN_DOC.read_text(encoding="utf-8")

    # 1. 顶层键
    missing = [k for k in REQUIRED_TOP_KEYS if k not in contract]
    if missing:
        failures.append(f"缺少必需顶层键：{missing}")
    else:
        passes.append("契约 JSON 可解析且必需顶层键齐全")

    # 2. 权威绑定现场复算（T1）
    bindings = {b["id"]: b for b in contract.get("upstream_bindings", [])}
    if not bindings:
        failures.append("缺少 upstream_bindings（权威无版本绑定）")
    else:
        bad: list[dict[str, object]] = []
        checked = 0
        for bid, b in bindings.items():
            path = resolve(b["path"])
            entry: dict[str, object] = {"id": bid, "path": str(path), "expected": b.get("sha256")}
            if not path.is_file():
                entry["status"] = "MISSING"
                bad.append(entry)
                continue
            actual = sha256_of(path)
            checked += 1
            entry["actual"] = actual
            entry["status"] = "MATCH" if actual == b.get("sha256") else "MISMATCH"
            if entry["status"] != "MATCH":
                bad.append(entry)
        details["upstream_binding_checks"] = {"checked": checked, "total": len(bindings), "bad": bad}
        if bad:
            failures.append(f"权威绑定漂移（必须显式更新绑定并重新审查）：{bad}")
        else:
            passes.append(f"upstream_bindings 现场复算一致（{checked}/{len(bindings)} 项）")

    s4a_path = resolve(bindings["s4a_g0_contract"]["path"]) if "s4a_g0_contract" in bindings else None
    w5_path = resolve(bindings["stage5_display_g0_fields"]["path"]) if "stage5_display_g0_fields" in bindings else None
    s4a = json.loads(s4a_path.read_text(encoding="utf-8")) if s4a_path and s4a_path.is_file() else None
    w5 = json.loads(w5_path.read_text(encoding="utf-8")) if w5_path and w5_path.is_file() else None

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

    # 11. stale 规则（N6）
    stale = contract["result_contract"]["stale_rule"]
    if not stale.get("expression") or not stale.get("stage4_stale_definition"):
        failures.append("stale 规则缺 expression 或 stage4_stale_definition")
    elif stale.get("stale_limit_status") != "DRAFT_PENDING_APPROVAL":
        failures.append("stale_limit_status 必须为 DRAFT_PENDING_APPROVAL")
    elif not stale.get("single_source_of_truth"):
        failures.append("stale 未声明唯一常量来源（N6）")
    else:
        passes.append("stale 规则含双基准定义、DRAFT 状态与唯一来源声明（N6）")

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
        "checker_version": "r02",
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