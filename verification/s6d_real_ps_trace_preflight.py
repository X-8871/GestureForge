#!/usr/bin/env python3
"""核验阶段4已提交PS诊断轨迹与UART关联，并判定阶段6消费资格。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


W4_COMMIT = "4e0b03dd7090c7dc5615a4cd1e40bd193715faff"
W4_RUN = "report/evidence/S4-B/s4b_ps_tensor_hw_20261027_r01"
RUN_ID = "report/evidence/S6-D/s6d_real_ps_diag_20261027_r01"
W4_FILES = {
    f"{W4_RUN}/adapter_hardware_result.json": "688c945eac6a24e1085eed6aa36fd5fc562e5b85a404d0292b9edb4b41541b30",
    f"{W4_RUN}/adapter_hardware_events.jsonl": "45f8f37cc4e30e998caf0de55e44e132223bcabd875fe53ada415545b14fcdc8",
    f"{W4_RUN}/trace_double_read.bin": "88f104f8b342a8a180632bf1fb2627b372ea013018c401b3e16679e1d6e1a0da",
    "docs/stage4/s4b_shared_input_result_contract.json": "2848ba031a6411e2920f7f8edbd58a3199d3404a2558a867d6c0f245c0796a94",
    "docs/stage4/S4B_shared_input_result_contract.md": "e839f7a0d30f83816b63aedf14047420091dcb84ac75b3d168e87831718b11fd",
    "docs/stage4/S4B_ps_tensor_injection_runbook.md": "b5e2b6686eaaba5486132d8f8e690f1b3b29b0d954add790fd27ecadc40dd6bd",
    "docs/stage4/s4a_stage4_g0_fields.json": "657ea2fbd2587873c4b8161e50390bc4139d373b4496dbfe6d8611081d6930d5",
    "scripts/stage4_s4b/decode_s4b_ps_trace.py": "015adb2a64d70ec9cc2dcfd0856f88e770314351edb51f034056e72523cdecdf",
}
TRACE_PATH = f"{W4_RUN}/trace_double_read.bin"
ADAPTER_PATH = f"{W4_RUN}/adapter_hardware_result.json"
EVENTS_PATH = f"{W4_RUN}/adapter_hardware_events.jsonl"
CONTRACT_JSON = "docs/stage4/s4b_shared_input_result_contract.json"
CONTRACT_MD = "docs/stage4/S4B_shared_input_result_contract.md"
RUNBOOK = "docs/stage4/S4B_ps_tensor_injection_runbook.md"
DECODER = "scripts/stage4_s4b/decode_s4b_ps_trace.py"


class PreflightError(ValueError):
    """表示提交绑定、契约或诊断轨迹不一致。"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def command_result(command: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, cwd=str(cwd), capture_output=True, check=False)


def git_text(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True,
        encoding="utf-8", errors="replace", text=True, check=False,
    )
    if result.returncode != 0:
        raise PreflightError(f"git {' '.join(args)} 失败：{result.stderr.strip()}")
    return result.stdout.strip()


def git_blob(root: Path, revision: str, relative_path: str) -> bytes:
    result = command_result(["git", "-C", str(root), "cat-file", "blob",
                             f"{revision}:{relative_path}"], root)
    if result.returncode != 0:
        raise PreflightError(f"Git blob 不存在：{revision}:{relative_path}")
    return result.stdout


def parse_json(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightError(f"{label} 不是有效 UTF-8 JSON：{exc}") from exc
    if not isinstance(value, dict):
        raise PreflightError(f"{label} 顶层必须是对象")
    return value


def parse_jsonl(data: bytes, label: str) -> list[dict[str, Any]]:
    try:
        lines = data.decode("utf-8").splitlines()
        values = [json.loads(line) for line in lines if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightError(f"{label} 不是有效 UTF-8 JSONL：{exc}") from exc
    if any(not isinstance(value, dict) for value in values):
        raise PreflightError(f"{label} 每行顶层必须是对象")
    return values


def find_mapping_roles(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        roles = value.get("mapping_key_roles")
        if isinstance(roles, dict):
            found.append(roles)
        for child in value.values():
            found.extend(find_mapping_roles(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_mapping_roles(child))
    return found


def verify_contract(contract: dict[str, Any], contract_md: bytes, runbook: bytes) -> dict[str, Any]:
    if (contract.get("status") != "FROZEN_OFFLINE_ONLY"
            or contract.get("contract_version") != "1.3.0"
            or contract.get("revision") != "r07"):
        raise PreflightError("阶段4共享契约不是绑定的 r07 离线冻结契约")
    role_sets = find_mapping_roles(contract)
    if len(role_sets) != 1:
        raise PreflightError("共享契约中 mapping_key_roles 缺失或不唯一")
    roles = role_sets[0]
    expected_roles = {
        "stage4a_join_key": ["session_id", "frame_id", "repeat_index"],
        "ps_log_primary_key": ["session_id", "result_seq"],
        "uart_observable_key": ["frame_id", "repeat_index", "sequence"],
        "contract_result_key": ["session_id", "frame_id", "result_seq"],
    }
    for name, fields in expected_roles.items():
        item = roles.get(name)
        if not isinstance(item, dict) or item.get("fields") != fields:
            raise PreflightError(f"共享契约的 {name} 字段角色与冻结口径不符")
    md_text = contract_md.decode("utf-8")
    runbook_text = runbook.decode("utf-8")
    if "UART 可观测键 `(frame_id, repeat_index, sequence)`" not in md_text:
        raise PreflightError("契约人读镜像缺少 UART 可观测键语义")
    if "PS 日志主键：`(session_id, result_seq)`" not in runbook_text:
        raise PreflightError("PS 诊断 runbook 缺少 PS 本地结果序号语义")
    if "S2BU/1.1 字节协议不携带 `session_id` 或 `result_seq`" not in runbook_text:
        raise PreflightError("PS 诊断 runbook 未声明 UART 不传输 session/result_seq")
    if "等于 `repeat_index + 1`" not in runbook_text:
        raise PreflightError("runbook 未声明 UART 诊断路径的本地 result_seq 关系")
    return {"status": "PASS", "contract_version": "1.3.0", "revision": "r07",
            "key_roles": expected_roles,
            "meaning": "result_seq 为 PS 本地结果序号；UART sequence 为请求/响应配对序号，独立命名空间。"}


def assess_diagnostic(adapter: dict[str, Any], events: list[dict[str, Any]],
                      decoded: dict[str, Any], contract_binding: dict[str, Any]) -> dict[str, Any]:
    """复核精确 join；不把诊断计数伪造成阶段6结果记录。"""
    if adapter.get("status") != "ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED":
        raise PreflightError("adapter 不是实际 PS 张量诊断完成记录")
    if adapter.get("hardware_run_id") != "s4b_ps_tensor_hw_20261027_r01":
        raise PreflightError("adapter hardware_run_id 与固定证据包不符")
    if adapter.get("complete_stage4_or_RGB_preprocess") != "NOT_CLAIMED":
        raise PreflightError("输入包阶段4/RGB 声明与已核验限制不符")

    identity = adapter.get("artifact_identity") or {}
    trace = adapter.get("trace_dump") or {}
    join = adapter.get("trace_uart_join") or {}
    receipts = adapter.get("uart_receipts")
    matches = join.get("matches")
    records = decoded.get("records")
    if decoded.get("status") != "PASS_DECODED_DOUBLE_READ_SNAPSHOT":
        raise PreflightError("双读 trace 解码没有 PASS")
    if decoded.get("snapshot_stability") != "two_full_region_reads_byte_identical":
        raise PreflightError("trace 未证明两次全区读取字节一致")
    if (adapter.get("trace_dump", {}).get("decoder_status")
            != "PASS_DECODED_DOUBLE_READ_SNAPSHOT"):
        raise PreflightError("adapter 未记录双读 trace 解码通过")
    if trace.get("record_count") != 1 or decoded.get("record_count") != 1:
        raise PreflightError("固定单帧诊断应恰有一条 PS trace 记录")
    if join.get("status") != "PASS_EXACT_TRACE_UART_JOIN" or len(matches or []) != 1:
        raise PreflightError("adapter 未提供唯一精确 trace/UART join")
    if not isinstance(records, list) or len(records) != 1:
        raise PreflightError("解码 trace 必须恰有一条结果记录")
    if not isinstance(receipts, list) or len(receipts) != 1:
        raise PreflightError("固定单帧诊断应恰有一条 UART RUN 回执")

    record = records[0]
    match = matches[0]
    receipt = receipts[0]
    run_events = [item for item in events if item.get("event") == "OP_RUN_response"]
    weight_events = [item for item in events if item.get("event") == "OP_WEIGHTS"]
    if len(run_events) != 1 or len(weight_events) != 1:
        raise PreflightError("UART 事件须各有一条 WEIGHTS 和 RUN 响应")
    run_event = run_events[0]
    weight_event = weight_events[0]

    result_key = (record.get("session_id"), record.get("frame_id"), record.get("result_seq"))
    expected_key = (1396845568, 0, 1)
    if result_key != expected_key:
        raise PreflightError(f"PS trace 结果键不符：{result_key!r}")
    if record.get("repeat_index") != 0 or record.get("uart_sequence") != 2:
        raise PreflightError("PS trace 的 repeat_index/UART sequence 不符")
    if (identity.get("session_first") != result_key[0]
            or identity.get("session_last") != 1396846567):
        raise PreflightError("trace session 不在构建身份绑定的 session 范围内")
    header = decoded.get("header") or {}
    if any(header.get(key) != result_key[0] for key in (
            "active_session_id", "last_assigned_session_id")):
        raise PreflightError("trace header 与 PS 结果 session 不一致")
    if header.get("active_uart_sequence") != record["uart_sequence"]:
        raise PreflightError("trace header UART sequence 与记录不一致")
    if header.get("active_base_frame") != record["frame_id"]:
        raise PreflightError("trace header base frame 与记录不一致")

    if (match.get("session_id"), match.get("frame_id"), match.get("result_seq"),
            match.get("repeat_index"), match.get("uart_sequence")) != (
            record["session_id"], record["frame_id"], record["result_seq"],
            record["repeat_index"], record["uart_sequence"]):
        raise PreflightError("adapter trace_uart_join 与独立解码记录不一致")
    if (receipt.get("frame"), receipt.get("index"), receipt.get("sequence")) != (
            record["frame_id"], record["repeat_index"], record["uart_sequence"]):
        raise PreflightError("UART receipt frame/index/sequence 与 PS trace 不一致")
    if (run_event.get("frame"), run_event.get("index"), run_event.get("sequence")) != (
            record["frame_id"], record["repeat_index"], record["uart_sequence"]):
        raise PreflightError("UART OP_RUN 事件与 PS trace 不一致")
    if (weight_event.get("sequence"), run_event.get("sequence")) != (1, 2):
        raise PreflightError("WEIGHTS/RUN 运输 sequence 关系不符合证据包")
    if record.get("result_seq") == record.get("uart_sequence"):
        raise PreflightError("本证据包中本地 result_seq 不应与 UART sequence 混为同一值")
    if record.get("result_seq") != record.get("repeat_index") + 1:
        raise PreflightError("本 UART 诊断路径 result_seq 与 repeat_index 关系不符合 runbook")
    if (record.get("input_crc32") != receipt.get("input_crc32")
            or receipt.get("input_crc32") != match.get("input_crc32")
            or record.get("input_crc32") != 1064075869):
        raise PreflightError("PS trace、UART receipt 与 adapter join 的输入 CRC 不一致")
    if (record.get("detection_count") != 1 or receipt.get("detection_count") != 1
            or (receipt.get("meta") or {}).get("box_count") != 1
            or record.get("raw_candidate_count") != 2
            or (receipt.get("meta") or {}).get("raw_candidate_count") != 2):
        raise PreflightError("检测/候选计数在 PS trace 与 UART 回执间不一致")
    if (record.get("epoch") != 1 or record.get("terminal_status") != 3588
            or receipt.get("epoch") != record.get("epoch")
            or (receipt.get("meta") or {}).get("phys_status") != record.get("terminal_status")):
        raise PreflightError("PS 终态/epoch 与 UART metadata 不一致")
    if (record.get("response_status") != 0 or record.get("uart_send_status") != 2
            or record.get("ack_state") != 1 or record.get("terminal_safe") is not True):
        raise PreflightError("该记录不是完整成功的 PS diagnostic attempt")

    absent = [field for field in (
        "detections", "state", "result_time_ns", "stale", "error_code",
    ) if field not in adapter]
    if record.get("capture_time_available") is not False or record.get("capture_time_ns") != 0:
        raise PreflightError("trace capture 时间字段不符合阶段4注入诊断的不可用标记")
    return {
        "status": "DIAGNOSTIC_ONLY",
        "stage6_core_eligibility": "BLOCKED",
        "contract_binding": contract_binding,
        "observed_keys": {
            "contract_result_key": list(result_key),
            "stage4a_join_key": [record["session_id"], record["frame_id"], record["repeat_index"]],
            "ps_log_primary_key": [record["session_id"], record["result_seq"]],
            "uart_observable_key": [record["frame_id"], record["repeat_index"], record["uart_sequence"]],
        },
        "uart_sequence_namespace_evidence": {
            "weights_sequence": weight_event["sequence"],
            "run_sequence": run_event["sequence"],
            "ps_result_seq": record["result_seq"],
            "ps_result_seq_is_uart_sequence": False,
        },
        "diagnostic_counts": {
            "detection_count": record["detection_count"],
            "box_count": receipt["meta"]["box_count"],
            "raw_candidate_count": record["raw_candidate_count"],
            "head_hashes_only": sorted((receipt.get("heads") or {}).keys()),
            "detections_payload_present": isinstance(adapter.get("detections"), list),
            "box_geometry_present": False,
        },
        "time_fields": {
            "capture_time_available": record["capture_time_available"],
            "capture_time_ns": record["capture_time_ns"],
            "result_time_ns_present": "result_time_ns" in adapter,
            "stale_present": "stale" in adapter,
            "raw_ticks_converted_to_ns": False,
        },
        "missing_stage6_result_fields": absent + ["geometry/score/xyxy detections"],
        "core_event_constructed": False,
        "core_step_called": False,
        "reasons": [
            "adapter/trace 仅提供检测框数量与 heads 哈希，不含阶段6所需 detections[]、class、score 或 xyxy；不得由计数或哈希推造框。",
            "trace capture_time_available=false 且为 0；无契约结果时刻与 stale 权威值，不得将 raw timer ticks 当 ns 或默认 fresh。",
            "该证据是单帧 INT8_CHW_416 PS 诊断；complete_stage4_or_RGB_preprocess=NOT_CLAIMED。",
        ],
    }


def audit_w4(w4_root: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    root_text = git_text(w4_root, "rev-parse", "--show-toplevel")
    root = Path(root_text).resolve()
    if root != w4_root.resolve():
        raise PreflightError(f"w4 根目录不精确：期望 {w4_root.resolve()}，实际 {root}")
    head = git_text(root, "rev-parse", "HEAD")
    if git_text(root, "cat-file", "-t", W4_COMMIT) != "commit":
        raise PreflightError("固定阶段4提交对象不是 commit")
    ancestor = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                               W4_COMMIT, head], capture_output=True, check=False)
    if ancestor.returncode != 0:
        raise PreflightError("固定阶段4诊断提交不是当前 w4 HEAD 的祖先")
    blobs: dict[str, bytes] = {}
    bindings: list[dict[str, Any]] = []
    for relative_path, expected_sha in W4_FILES.items():
        blob = git_blob(root, W4_COMMIT, relative_path)
        actual_sha = sha256_bytes(blob)
        if actual_sha != expected_sha:
            raise PreflightError(f"固定阶段4文件 SHA 不符：{relative_path}：{actual_sha}")
        blob_oid = git_text(root, "rev-parse", f"{W4_COMMIT}:{relative_path}")
        bindings.append({"path": relative_path, "git_blob": blob_oid,
                         "sha256": actual_sha, "bytes": len(blob)})
        blobs[relative_path] = blob

    adapter = parse_json(blobs[ADAPTER_PATH], ADAPTER_PATH)
    events = parse_jsonl(blobs[EVENTS_PATH], EVENTS_PATH)
    contract = parse_json(blobs[CONTRACT_JSON], CONTRACT_JSON)
    contract_binding = verify_contract(contract, blobs[CONTRACT_MD], blobs[RUNBOOK])
    assessment = {
        "pinned_commit": W4_COMMIT,
        "current_w4_head_observed": head,
        "pinned_commit_is_ancestor": True,
        "input_bindings": bindings,
        "contract_review": contract_binding,
    }
    assessment["adapter"] = adapter
    assessment["events"] = events
    return assessment, blobs


def decode_trace(w4_root: Path, trace: bytes,
                 adapter: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str]:
    decoder_path = w4_root / DECODER
    decoder_blob_sha = sha256_bytes(git_blob(w4_root, W4_COMMIT, DECODER))
    if decoder_blob_sha != W4_FILES[DECODER]:
        raise PreflightError("固定提交中的解码器 SHA 与常量不符")
    if sha256_bytes(decoder_path.read_bytes()) != decoder_blob_sha:
        raise PreflightError("w4 工作树 decoder 字节与固定提交 blob 不一致")
    trace_meta = adapter.get("trace_dump") or {}
    if sha256_bytes(trace) != trace_meta.get("sha256") or len(trace) != trace_meta.get("bytes"):
        raise PreflightError("trace bytes/size 与 adapter trace_dump 绑定不一致")
    artifact_identity = adapter.get("artifact_identity") or {}
    with tempfile.TemporaryDirectory(prefix="s6d-real-ps-") as temporary:
        input_path = Path(temporary) / "trace_double_read.bin"
        output_path = Path(temporary) / "trace_decoded.json"
        input_path.write_bytes(trace)
        command = [sys.executable, "-B", "-X", "utf8", str(decoder_path), str(input_path),
                   "--expected-source-sha256", str(artifact_identity.get("derived_source_sha256")),
                   "--expected-boot-seed", hex(artifact_identity.get("boot_seed", 0)),
                   "--output", str(output_path)]
        completed = command_result(command, w4_root)
        if completed.returncode == 0:
            decoded_bytes = output_path.read_bytes()
    process_log = (
        f"命令：{subprocess.list2cmdline(command)}\n"
        f"退出码：{completed.returncode}\n"
        f"stdout UTF-8:\n{completed.stdout.decode('utf-8', errors='replace')}\n"
        f"stderr UTF-8:\n{completed.stderr.decode('utf-8', errors='replace')}\n"
    )
    if completed.returncode != 0:
        raise PreflightError(f"固定阶段4 trace decoder 失败，退出码 {completed.returncode}")
    decoded = parse_json(decoded_bytes, "trace_decoded.json")
    return decoded, {"command": subprocess.list2cmdline(command),
                     "exit_code": completed.returncode}, process_log


def run_audit(w4_root: Path) -> dict[str, Any]:
    upstream, blobs = audit_w4(w4_root)
    adapter = upstream.pop("adapter")
    events = upstream.pop("events")
    decoded, decoder_check, decoder_log = decode_trace(w4_root, blobs[TRACE_PATH], adapter)
    decision = assess_diagnostic(adapter, events, decoded, upstream["contract_review"])
    upstream.update({
        "status": "BLOCKED_FOR_S6_CORE",
        "adapter_sha256": sha256_bytes(blobs[ADAPTER_PATH]),
        "adapter_blob": next(item["git_blob"] for item in upstream["input_bindings"]
                              if item["path"] == ADAPTER_PATH),
        "trace_decoder": decoder_check,
        "trace_decoder_process": decoder_log,
        "trace_decoded": decoded,
        "eligibility": decision,
        "core_execution": {"status": "NOT_RUN", "core_event_constructed": False,
                            "core_step_called": False},
        "limitations": [
            "该包只有诊断计数和heads哈希，没有阶段6 detections[]/框几何。",
            "capture_time不可用；没有权威result_time_ns或stale值，未将raw ticks换算成ns。",
            "不证明完整阶段4/RGB预处理、实时性能、板级G3、6-E实物验收或阶段G4/G5。",
        ],
    })
    return upstream


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--w4-root", type=Path, required=True)
    parser.add_argument("--output", type=Path,
                        help="可选：将只读审计JSON写入调用方指定的新证据文件")
    args = parser.parse_args(argv)
    try:
        result = run_audit(args.w4_root.resolve())
        serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            if args.output.exists():
                raise PreflightError(f"拒绝覆盖已有输出：{args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized, encoding="utf-8")
        else:
            sys.stdout.write(serialized)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"阶段6真实PS诊断预检失败：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
