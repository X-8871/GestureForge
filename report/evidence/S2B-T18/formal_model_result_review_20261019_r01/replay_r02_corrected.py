#!/usr/bin/env python3
"""只读重放T18 R02 UART/黄金结果；不连接任何硬件。"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import zlib

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from verification import s2b_board_transport as transport
from verification import s2b_fixed_capture_check as checker

RUN = ROOT / "report/evidence/S2B-T18/formal_stress1000_then109_20261018_r02"
DEPLOY = ROOT / "report/evidence/S2B-T18/formal_stress1000_then109_20261018_r02_deployment"
PREP_PATH = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/preparation_stress_first.json"
AUDIT = ROOT / "report/evidence/S2B-T18/formal_model_evidence_audit_20261019_r01"

errors: list[str] = []
warnings: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            size += len(block)
            digest.update(block)
    return digest.hexdigest(), size


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def exact_file(raw_path: str | Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    return transport.exact_path(path)


def same(left, right, message: str) -> None:
    check(left == right, message)


def verify_manifest_files(manifest: dict, expected_drift: set[str]) -> dict:
    rows = manifest["files"]
    seen: set[str] = set()
    mismatches = []
    missing = []
    total_bytes = 0
    for row in rows:
        relative = row["path"]
        check(relative not in seen, f"delivery manifest重复路径: {relative}")
        seen.add(relative)
        try:
            path = exact_file(relative)
            actual, size = sha_file(path)
            total_bytes += size
            if actual != row["sha256"]:
                mismatches.append({"path": relative, "expected": row["sha256"], "actual": actual})
        except Exception as exc:  # 保留每个缺失项，继续审计其余清单文件
            missing.append({"path": relative, "error": repr(exc)})
    mismatch_paths = {row["path"] for row in mismatches}
    check(not missing, f"delivery manifest存在{len(missing)}个缺失/无法读取文件")
    check(mismatch_paths == expected_drift,
          f"manifest漂移集合不符: expected={sorted(expected_drift)} actual={sorted(mismatch_paths)}")
    return {"listed_files": len(rows), "unique_paths": len(seen), "current_bytes_hashed": total_bytes,
            "mismatches": mismatches, "missing": missing}


def verify_source_snapshots(manifest: dict, config: dict, original_binding: dict,
                            blob_lookup: dict) -> list[dict]:
    result = []
    files = manifest["files"]
    lookup_by_path = {item["original_path"]: item for item in blob_lookup["matches"]}
    binding_names = {
        "verification/s2b_board_acceptance.py": "acceptance_source",
        "verification/s2b_board_jtag.py": "tool_source",
        "vitis/run_s2b_model_acceptance.py": "runner_source"
    }
    for item in original_binding["mapping"]:
        path = item["original_path"]
        manifest_row = files[item["original_files_index"]]
        same(manifest_row["path"], path, f"manifest源索引路径不一致: {path}")
        same(manifest_row["sha256"], item["original_sha256"], f"manifest源索引SHA不一致: {path}")
        snapshot_path = exact_file(item["replacement_path"])
        snapshot_sha, snapshot_size = sha_file(snapshot_path)
        same(snapshot_sha, item["original_sha256"], f"归档源快照SHA不一致: {path}")
        lookup = lookup_by_path.get(path)
        check(lookup is not None, f"缺少Git blob映射: {path}")
        if lookup is not None:
            same(lookup["original_sha256"], item["original_sha256"], f"blob映射原始SHA不一致: {path}")
            same(lookup["snapshot_sha256"], snapshot_sha, f"blob映射快照SHA不一致: {path}")
            rev = subprocess.run(["git", "rev-parse", f"{lookup['matching_commit']}:{path}"],
                                 cwd=ROOT, capture_output=True, check=True, text=True).stdout.strip()
            same(rev, lookup["git_blob"], f"历史commit Git blob ID不一致: {path}")
            blob = subprocess.run(["git", "cat-file", "blob", rev], cwd=ROOT,
                                  capture_output=True, check=True).stdout
            same(sha_bytes(blob), snapshot_sha, f"历史Git blob字节与归档快照不同: {path}")
            same(blob, snapshot_path.read_bytes(), f"历史Git blob逐字节与归档快照不同: {path}")
        binding_name = binding_names.get(path)
        check(binding_name is not None and binding_name in config["bindings"],
              f"实际input_config未绑定源文件: {path}")
        if binding_name in config["bindings"]:
            binding = config["bindings"][binding_name]
            same(binding["path"], str(ROOT / Path(path)), f"input_config源文件路径不是精确原路径: {path}")
            same(binding["sha256"], snapshot_sha, f"input_config与源快照SHA不一致: {path}")
        result.append({"path": path, "input_config_binding": binding_name,
                       "manifest_sha256": item["original_sha256"], "snapshot_sha256": snapshot_sha,
                       "snapshot_bytes": snapshot_size,
                       "historical_commit": item["historical_commit"], "git_blob": item["git_blob"],
                       "git_blob_reverified": lookup is not None})
    return result


def main() -> dict:
    run_result = load_json(RUN / "orchestrator_result.json")
    acceptance = run_result["acceptance"]
    deployment_config = load_json(DEPLOY / "input_config.json")
    orchestrator_config = load_json(RUN / "orchestrator/input_config.json")
    check(deployment_config == orchestrator_config, "deployment与orchestrator input_config内容不同")

    manifest_path = RUN / "delivery_manifest.json"
    manifest = load_json(manifest_path)
    original_binding = load_json(AUDIT / "original_binding.json")
    blob_lookup = load_json(AUDIT / "source_blob_lookup.json")
    manifest_sha, manifest_bytes = sha_file(manifest_path)
    same(manifest_sha, original_binding["original_manifest_sha256"], "原delivery manifest SHA与审计索引不同")
    same(original_binding["original_manifest_path"], "report/evidence/S2B-T18/formal_stress1000_then109_20261018_r02/delivery_manifest.json",
         "原manifest精确路径不同")

    drift = {item["original_path"] for item in original_binding["mapping"]}
    all_manifest = verify_manifest_files(manifest, drift)
    snapshot_results = verify_source_snapshots(manifest, deployment_config, original_binding, blob_lookup)

    bound_files = []
    config_binding_drift = []
    for name, binding in deployment_config["bindings"].items():
        path = exact_file(binding["path"])
        actual, size = sha_file(path)
        matches = actual == binding["sha256"]
        if not matches:
            config_binding_drift.append({"name": name, "path": binding["path"],
                                         "expected": binding["sha256"], "actual": actual})
        bound_files.append({"name": name, "path": binding["path"], "expected_sha256": binding["sha256"],
                            "actual_sha256": actual, "bytes": size, "matches_current_file": matches})
    allowed_config_drift = {item["original_path"] for item in original_binding["mapping"]}
    drift_names = {
        "verification/s2b_board_acceptance.py": "acceptance_source",
        "verification/s2b_board_jtag.py": "tool_source",
        "vitis/run_s2b_model_acceptance.py": "runner_source"
    }
    allowed_config_drift = {deployment_config["bindings"][drift_names[path]]["path"]
                            for path in allowed_config_drift}
    actual_config_drift_paths = {row["path"] for row in config_binding_drift}
    check(actual_config_drift_paths == allowed_config_drift,
          f"input_config当前文件漂移集合不符: {sorted(actual_config_drift_paths)}")

    prep_binding = deployment_config["preparation"]
    prep_path = exact_file(prep_binding["path"])
    prep_sha, _ = sha_file(prep_path)
    same(prep_sha, prep_binding["sha256"], "input_config preparation SHA不匹配")
    prep = load_json(prep_path)
    same(prep["status"], "NOT_RUN", "准备文件状态不是NOT_RUN")
    same(prep["preparation"], "PASS_OFFLINE_ASSET_BINDINGS", "离线资产绑定准备未通过")
    same(len(prep["rows"]), 109, "冻结准备行数不是109")
    same(prep["source_sha256"]["path"],
         deployment_config["bindings"]["acceptance_source"]["path"],
         "preparation与input_config acceptance源码路径不同")
    same(prep["source_sha256"]["sha256"],
         deployment_config["bindings"]["acceptance_source"]["sha256"],
         "preparation与input_config acceptance源码SHA不同")

    first_input = exact_file(prep["rows"][0]["input"]["path"])
    asset_root = first_input.parents[2]
    weight_path, weight, asset_rows = transport.load_assets(asset_root, list(range(109)))
    same(len(asset_rows), 109, "从冻结输入加载的样本数不为109")
    same(sha_bytes(weight), prep["weights"]["sha256"], "实际GF8权重与preparation绑定不同")
    same(str(weight_path), prep["weights"]["path"], "权重实际路径与preparation不同")

    frozen_files = []
    d9_config = checker._frozen_config(ROOT, frozen_files)
    ref0_path = exact_file(prep["rows"][0]["reference"]["path"])
    ref0_doc = load_json(ref0_path)
    golden_source_desc = ref0_doc["golden_source"]
    golden_source_file, frozen_rows, _ = checker._golden_source(golden_source_desc, ROOT, frozen_files)
    same(golden_source_desc["kind"], "frozen_cpu_d9", "引用黄金不是冻结CPU D9来源")
    same(golden_source_desc["sha256"], transport.CPU_D9_SHA, "冻结CPU D9黄金SHA不匹配transport常量")
    source_by_id = {row["sample_id"]: row for row in frozen_rows}
    same(len(source_by_id), 109, "冻结D9来源样本数不是109或sample_id重复")

    refs = []
    golden_heads = []
    d9_detections = []
    ref_files = []
    for index, row in enumerate(prep["rows"]):
        same(row["index"], index, f"preparation行索引不连续: {index}")
        input_path = exact_file(row["input"]["path"])
        input_sha, input_size = sha_file(input_path)
        same(input_sha, row["input"]["sha256"], f"preparation输入SHA错误: {index}")
        same(input_size, transport.INPUT_BYTES, f"输入长度错误: {index}")
        same(row["input"]["sha256"], asset_rows[index]["input_sha256"], f"冻结模型输入SHA不同: {index}")
        same(row["sample_id"], asset_rows[index]["sample"]["sample_id"], f"冻结样本ID不同: {index}")

        ref_path = exact_file(row["reference"]["path"])
        ref_sha, _ = sha_file(ref_path)
        same(ref_sha, row["reference"]["sha256"], f"reference文件SHA错误: {index}")
        ref_doc = load_json(ref_path)
        same(ref_doc["golden_source"], golden_source_desc, f"reference黄金来源变化: {index}")
        ref_rows = checker._document(ref_doc, "s2b_fixed_reference")
        same(len(ref_rows), 1, f"reference样本数不为1: {index}")
        ref = ref_rows[0]
        source_row = source_by_id.get(row["sample_id"])
        check(source_row is not None, f"reference样本缺少冻结D9 source: {row['sample_id']}")
        same(ref["sample_id"], row["sample_id"], f"reference sample_id与preparation不同: {index}")
        same(ref["input"]["pl_input_sha256"], input_sha, f"reference输入SHA与实际input不同: {index}")
        same(ref["input"]["geometry_wh"], asset_rows[index]["golden"]["input"]["geometry_wh"],
             f"reference geometry与冻结黄金不同: {index}")
        check(ref["head_tensors"] is not None, f"reference缺少双头: {index}")
        if source_row is not None:
            same(checker._identity(ref), checker._identity(source_row), f"reference identity与CPU D9来源不同: {index}")
            same(ref["detections"], source_row["detections"], f"reference boxes与CPU D9来源不同: {index}")
            same(ref["nms_output_box_count"], source_row["nms_output_box_count"], f"reference box count不同: {index}")
            for name in transport.HEAD_LENGTHS:
                for field in ("tensor_sha256", "byte_length"):
                    same(ref["head_tensors"][name][field], source_row["head_tensors"][name][field],
                         f"reference {name}.{field}与CPU D9来源不同: {index}")
        heads = checker._read_heads(ref, ROOT, f"frozen_golden[{index}]", frozen_files)
        decoded = checker._decode(heads, ref, d9_config)
        if source_row is not None:
            gold_cmp = checker.compare_detections(source_row["detections"], decoded,
                                                  checker.GOLDEN_RECORD_TOLERANCE)
            check(gold_cmp["match"], f"冻结gold头D9复算与CPU D9记录不符: {index} {gold_cmp['errors'][:2]}")
        golden_heads.append({name: heads[name].payload for name in transport.HEAD_LENGTHS})
        d9_detections.append(decoded)
        refs.append(ref)
        ref_files.append({"path": str(ref_path), "sha256": ref_sha,
                          "head_sha256": {name: sha_bytes(heads[name].payload) for name in transport.HEAD_LENGTHS}})

    core = deployment_config["core_timeout"]
    drain = deployment_config["drain_timeout"]
    tx_events = [row for row in acceptance["events"] if row.get("direction") == "TX"]
    rx_events = [row for row in acceptance["events"] if row.get("direction") == "RX"]
    same(len(tx_events), 111, "TX事件数不等于1 WEIGHTS + 1 STRESS + 109 CORPUS")
    same(len(rx_events), 1110, "RX事件数不等于1 WEIGHTS + 1000 STRESS + 109 CORPUS")

    requests = []
    requests.append({"phase": "weights", "sequence": 1, "frame": 0, "index": 0,
                     "source": prep["weights"], "width": 0, "height": 0, "repeat": 1,
                     "sample_index": None})
    for index, row in enumerate(prep["rows"]):
        if index == 0:
            requests.append({"phase": "stress", "sequence": 2, "frame": 0, "index": 0,
                             "source": row["input"],
                             "width": refs[0]["input"]["geometry_wh"][0],
                             "height": refs[0]["input"]["geometry_wh"][1], "repeat": 1000,
                             "sample_index": 0})
        requests.append({"phase": "corpus", "sequence": 3 + index, "frame": 1000 + index,
                         "index": index, "source": row["input"],
                         "width": refs[index]["input"]["geometry_wh"][0],
                         "height": refs[index]["input"]["geometry_wh"][1], "repeat": 1,
                         "sample_index": index})
    same(len(requests), 111, "重建的request总数不为111")

    tx_path = DEPLOY / "uart_tx_raw.bin"
    tx_raw = tx_path.read_bytes()
    same(len(tx_raw), 111 * transport.HEADER.size, "uart_tx_raw不是111个完整request header")
    reconstructed_requests = []
    for index, spec in enumerate(requests):
        if spec["phase"] == "weights":
            payload = weight
        else:
            payload = struct.pack("<II", core, drain) + exact_file(spec["source"]["path"]).read_bytes()
        request, header = transport.make_request(
            transport.OP_WEIGHTS if spec["phase"] == "weights" else transport.OP_RUN,
            spec["sequence"], spec["frame"], payload, width=spec["width"],
            height=spec["height"], repeat=spec["repeat"])
        raw_header = tx_raw[index * transport.HEADER.size:(index + 1) * transport.HEADER.size]
        same(transport.Header.unpack(raw_header), request, f"TX header字段/CRC与source payload不同: seq={spec['sequence']}")
        same(raw_header, header, f"原TX header字节与重建header不同: seq={spec['sequence']}")
        event = tx_events[index]
        source = spec["source"]
        same((event["sequence"], event["frame"], event["op"]),
             (spec["sequence"], spec["frame"], request.op), f"TX调用日志身份不同: seq={spec['sequence']}")
        same(event["header_sha256"], sha_bytes(raw_header), f"TX调用日志header SHA不同: seq={spec['sequence']}")
        same(event["payload_sha256"], sha_bytes(payload), f"TX payload source SHA不同: seq={spec['sequence']}")
        same(event["payload_crc32"], request.payload_crc, f"TX调用日志payload CRC不同: seq={spec['sequence']}")
        same(event["sent_bytes"], transport.HEADER.size + len(payload), f"TX调用日志长度不同: seq={spec['sequence']}")
        same(event["sent_sha256"], sha_bytes(raw_header + payload), f"TX调用日志完整header+payload SHA不同: seq={spec['sequence']}")
        binding = event["source_binding"]
        same(binding["path"], source["path"], f"TX调用日志源路径不同: seq={spec['sequence']}")
        same(binding["sha256"], source["sha256"], f"TX调用日志源SHA不同: seq={spec['sequence']}")
        same(binding["bytes"], source["bytes"], f"TX调用日志源长度不同: seq={spec['sequence']}")
        reconstructed_requests.append(request)
        del payload

    rx_path = DEPLOY / "uart_rx_raw.bin"
    rx_sha, rx_size = sha_file(rx_path)
    same(acceptance["uart_rx"]["sha256"], rx_sha, "acceptance result原UART SHA不同")
    same(acceptance["uart_rx"]["path"], str(rx_path), "acceptance result原UART路径不同")
    banner = acceptance["startup_banner"]["returned"]
    prefix = acceptance["startup_banner"]["rx_prefix"]
    same(prefix["path"], str(rx_path), "banner prefix路径不同")
    same(prefix["offset"], 0, "banner prefix offset不是0")
    same(prefix["bytes"], banner["bytes"], "banner prefix长度与返回banner不同")
    same(prefix["sha256"], banner["sha256"], "banner prefix摘要与返回banner不同")
    expected_banner = banner["text"].encode("ascii")
    with rx_path.open("rb") as stream:
        actual_banner = stream.read(len(expected_banner))
    same(actual_banner, expected_banner, "真实UART前缀字节与banner原始文本不同")
    same(sha_bytes(actual_banner), banner["sha256"], "真实UART banner SHA不同")
    same(transport.HEADER.size, 40, "S2BU header ABI不是40字节")

    frame_records = acceptance["frames"]
    same(len(frame_records), 1110, "acceptance frame receipt记录数不为1110")
    frame_map = {(row["phase"], row["frame"]): row for row in frame_records}
    same(len(frame_map), len(frame_records), "acceptance frame记录存在重复phase/frame")
    prev_epoch = 0
    response_index = 0
    response_count = 0
    run_response_count = 0
    stress_response_count = 0
    corpus_response_count = 0
    compared_head_bytes = 0
    compared_box_rows = 0
    total_boxes = 0
    response_status_counts: dict[str, int] = {}
    epoch_values = []
    offsets = []
    rx_run_frame_successors = 0

    rx_consumed = 0
    with rx_path.open("rb") as stream:
        stream.seek(len(expected_banner))
        for req_index, (spec, request) in enumerate(zip(requests, reconstructed_requests)):
            count = request.repeat if request.op == transport.OP_RUN else 1
            for index in range(count):
                response_offset = stream.tell()
                response_header = stream.read(transport.HEADER.size)
                check(len(response_header) == transport.HEADER.size,
                      f"响应header截断: seq={request.sequence} index={index}")
                if len(response_header) != transport.HEADER.size:
                    break
                parsed_header = transport.Header.unpack(response_header)
                check(parsed_header.length <= transport.MAX_RESPONSE,
                      f"响应长度超过协议上限: seq={request.sequence} index={index}")
                payload = stream.read(parsed_header.length)
                check(len(payload) == parsed_header.length,
                      f"响应payload截断: seq={request.sequence} index={index}")
                if len(payload) != parsed_header.length:
                    break
                raw_response = response_header + payload
                response_event = rx_events[response_index]
                same(response_event["header"], parsed_header.__dict__,
                     f"RX日志response header字段不同: seq={request.sequence} index={index}")
                same(response_event["header_sha256"], sha_bytes(response_header),
                     f"RX日志header SHA不同: seq={request.sequence} index={index}")
                same(response_event["payload_sha256"], sha_bytes(payload),
                     f"RX日志payload SHA不同: seq={request.sequence} index={index}")
                same(response_event["bytes"], len(raw_response),
                     f"RX日志接收长度不同: seq={request.sequence} index={index}")
                same(response_event["raw_meta"], list(transport.META.unpack_from(payload)),
                     f"RX日志meta不同: seq={request.sequence} index={index}")
                meta, heads, detections = transport.decode_response(
                    response_header, payload, request, index, prev_epoch)
                prev_epoch = meta["epoch"]
                epoch_values.append(prev_epoch)
                response_count += 1
                response_index += 1
                offsets.append({"offset": response_offset, "bytes": len(raw_response)})
                response_status_counts[str(meta["phys_status"])] = response_status_counts.get(str(meta["phys_status"]), 0) + 1

                frame = request.frame + index if request.op == transport.OP_RUN else 0
                phase = spec["phase"]
                directory_name = f"{phase}_{frame:08d}"
                frame_dir = RUN / "frames" / directory_name
                rec = frame_map.get((phase, frame))
                check(rec is not None, f"缺少acceptance frame记录: {phase}/{frame}")
                if rec is not None:
                    same(Path(rec["directory"]).name, directory_name,
                         f"acceptance frame目录名不符: {phase}/{frame}")
                    same(rec["sequence"], request.sequence, f"acceptance frame sequence不同: {phase}/{frame}")
                    same(rec["epoch"], meta["epoch"], f"acceptance frame epoch不同: {phase}/{frame}")
                per_frame = frame_dir / "result.json"
                result_doc = load_json(per_frame)
                span = result_doc["raw_uart"]
                same(span["offset"], response_offset, f"frame原UART offset不同: {phase}/{frame}")
                same(span["bytes"], len(raw_response), f"frame原UART长度不同: {phase}/{frame}")
                same(span["sha256"], sha_bytes(raw_response), f"frame原UART SHA不同: {phase}/{frame}")
                same((result_doc["sequence"], result_doc["frame"], result_doc["repeat_index"],
                      result_doc["repeat_total"]),
                     (request.sequence, frame, index, request.repeat), f"frame结果身份不同: {phase}/{frame}")
                same(result_doc["meta"], meta, f"frame结果meta不同: {phase}/{frame}")
                same((frame_dir / "uart_response_raw.bin").read_bytes(), raw_response,
                     f"frame原始UART副本不同: {phase}/{frame}")
                same((frame_dir / "uart_response_raw.bin").stat().st_size, len(raw_response),
                     f"frame原始UART副本长度不同: {phase}/{frame}")

                if request.op == transport.OP_RUN:
                    run_response_count += 1
                    row_index = 0 if phase == "stress" else spec["sample_index"]
                    expected_heads = golden_heads[row_index]
                    for name, expected in expected_heads.items():
                        actual = heads[name]
                        same(actual, expected, f"UART {phase} {frame} {name}逐字节不等于冻结黄金")
                        same(len(actual), transport.HEAD_LENGTHS[name], f"UART head长度错误: {phase}/{frame}/{name}")
                        head_file = frame_dir / f"{name}.bin"
                        same(head_file.read_bytes(), actual, f"保存head副本不等于从原UART重放的字节: {phase}/{frame}/{name}")
                        compared_head_bytes += len(actual)
                    comparison = checker.compare_detections(d9_detections[row_index], detections,
                                                            checker.ABS_TOLERANCE)
                    check(comparison["match"], f"UART框与冻结D9不同: {phase}/{frame} {comparison['errors'][:3]}")
                    total_boxes += len(detections)
                    compared_box_rows += 1
                    if phase == "stress":
                        stress_response_count += 1
                    else:
                        corpus_response_count += 1
                    capture_doc = load_json(frame_dir / "capture.json")
                    capture = capture_doc["samples"][0]
                    same(capture["sample_id"], refs[row_index]["sample_id"], f"capture sample_id不同: {phase}/{frame}")
                    same(capture["input"], refs[row_index]["input"], f"capture输入身份不同: {phase}/{frame}")
                    same(capture["detections"], detections, f"capture boxes不是原UART解码结果: {phase}/{frame}")
                else:
                    same(meta["phys_status"] & 7, 0, "WEIGHTS响应非IDLE")
                    same(meta["error_code"], 0, "WEIGHTS响应error_code非0")
                    same(meta["response_code"], 0, "WEIGHTS响应code非0")
        rx_consumed = stream.tell()

    same(rx_consumed, rx_size, "UART RX尾部存在未消费字节或末端截断")
    same(response_index, len(rx_events), "原始UART消费响应数与RX事件数不同")
    same(response_count, 1110, "独立解码响应总数不为1110")
    same(run_response_count, 1109, "独立解码RUN响应总数不为1109")
    same(stress_response_count, 1000, "压力响应数不为1000")
    same(corpus_response_count, 109, "corpus响应数不为109")
    same(compared_box_rows, 1109, "未逐帧比对全部1109组D9检测框")
    same(compared_head_bytes, 1109 * sum(transport.HEAD_LENGTHS.values()),
         "逐字节双头比对字节总数不等于1109帧")
    same(prev_epoch, 1109, "最终独立响应epoch不为1109")
    same(acceptance["final_epoch"], prev_epoch, "acceptance摘要final_epoch不同")
    same(acceptance["final_sequence"], 111, "acceptance摘要final_sequence不同")
    same(acceptance["completed_stress"], 1000, "acceptance摘要stress数不同")
    same(acceptance["completed_corpus"], 109, "acceptance摘要corpus数不同")
    same(acceptance["execution_order"], ["weights", "stress", "corpus"], "执行顺序不同")
    same(run_result["native_exit_code"], 0, "orchestrator native exit code非0")
    same(run_result["status"], "PASS_MODEL_CORPUS_AND_STRESS_ONLY", "orchestrator状态不同")

    # 正常RUN的CPU端ACK由已绑定固件在完整UART发送排空后提交；后继RUN/response证明其先前终态已被ACK。
    # 最后一帧没有后继请求，结果包未保存运行后的CSR IDLE快照，故单独标为未动态观察。
    ack_followed = run_response_count - 1
    check(ack_followed == 1108, "后继RUN对前序终态ACK的动态佐证数不是1108")
    app_path = exact_file("vitis/s2b_inference_app.c")
    app_sha, _ = sha_file(app_path)
    source_token = banner["text"].split("SOURCE=", 1)[1].split(" ", 1)[0]
    same(source_token, app_sha, "启动banner SOURCE与固件C源码实际SHA不同")
    build_binding = acceptance["admission"]["build_details"]
    build_details = load_json(exact_file(build_binding["path"]))
    same(sha_file(exact_file(build_binding["path"]))[0], build_binding["sha256"], "build_details文件SHA不同")
    same(build_details["source_sha256"].get("vitis/s2b_inference_app.c"), app_sha,
         "build_details未绑定当前banner所标识的app源码")
    same(acceptance["status"], "PASS_MODEL_CORPUS_AND_STRESS_ONLY", "model acceptance内部状态不同")

    ack_text = app_path.read_text(encoding="utf-8")
    ack_static = ("while (!uart_drain_done())" in ack_text and
                  "return acknowledge(&snap);" in ack_text and
                  "csr_write(0x008U, 4U);" in ack_text)
    check(ack_static, "绑定app源码中未找到UART排空后matching terminal ACK路径")

    source_commits = {"manifest": manifest.get("source_commit"),
                      "input_config": deployment_config.get("source_commit"),
                      "orchestrator_result": run_result.get("source_commit")}
    clean_tree_claim = len(set(source_commits.values())) == 1
    if not clean_tree_claim:
        warnings.append("manifest source_commit与orchestrator/input_config source_commit不同；仅能声称经input_config/call log和归档快照逐文件绑定，不能声称单一clean tree来源。")
    warnings.append("uart_tx_raw.bin仅保存111个40-byte request header；payload由绑定输入字节、source_binding、CRC和调用日志SHA重建校验，并非独立TX线级原字节采集。")
    warnings.append("最后一个corpus RUN的终态ACK无后继RUN可佐证，deployment没有保存运行后CSR IDLE/ACK读回；app源代码可证明ACK调用路径但不能替代该次动态读回。")

    return {
        "schema_version": 1,
        "run_id": run_result["run_id"],
        "replay_status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "source_provenance": {
            "source_commits": source_commits,
            "single_clean_tree_proven": clean_tree_claim,
            "per_file_input_config_bindings": bound_files,
            "input_config_binding_current_file_drift": config_binding_drift,
            "historical_source_snapshots": snapshot_results,
            "original_manifest_sha256": manifest_sha,
            "original_manifest_bytes": manifest_bytes,
            "manifest_inventory": all_manifest
        },
        "frozen_assets": {
            "preparation_path": str(prep_path), "preparation_sha256": prep_sha,
            "rows": len(prep["rows"]), "weight_path": str(weight_path),
            "weight_bytes": len(weight), "weight_sha256": sha_bytes(weight),
            "frozen_cpu_d9_path": str(golden_source_file.path),
            "frozen_cpu_d9_sha256": golden_source_desc["sha256"],
            "frozen_d9_samples": len(frozen_rows), "d9_samples_redecoded": len(d9_detections),
            "references": ref_files,
            "decoder_tool_sha256": sha_file(exact_file("verification/s2b_fixed_capture_check.py"))[0],
            "transport_tool_sha256": sha_file(exact_file("verification/s2b_board_transport.py"))[0],
            "decoder_source_sha256": sha_file(exact_file("verification/s1_t02_d9_yolo_decode.py"))[0]
        },
        "uart_replay": {
            "rx_path": str(rx_path), "rx_bytes": rx_size, "rx_sha256": rx_sha,
            "tx_header_path": str(tx_path), "tx_header_bytes": len(tx_raw), "tx_header_sha256": sha_bytes(tx_raw),
            "tx_requests": len(requests), "rx_responses": response_count,
            "weights_responses": 1, "stress_responses": stress_response_count,
            "corpus_responses": corpus_response_count, "run_responses": run_response_count,
            "response_status_counts": response_status_counts,
            "final_epoch": prev_epoch, "final_sequence": acceptance["final_sequence"],
            "banner_bytes": len(expected_banner), "banner_sha256": sha_bytes(actual_banner),
            "all_response_offsets_and_lengths": offsets
        },
        "golden_comparison": {
            "corpus_samples": len(prep["rows"]), "stress_repeats": stress_response_count,
            "run_frames_compared": compared_box_rows, "head_bytes_compared": compared_head_bytes,
            "detections_total": total_boxes,
            "all_two_head_bytes_equal": not any("逐字节不等" in error for error in errors),
            "all_frame_boxes_match_frozen_d9": not any("冻结D9不同" in error for error in errors),
            "d9_tolerance": checker.ABS_TOLERANCE,
            "gold_record_tolerance": checker.GOLDEN_RECORD_TOLERANCE
        },
        "terminal_ack": {
            "firmware_source_path": str(app_path), "firmware_source_sha256": app_sha,
            "source_hash_matches_banner": source_token == app_sha,
            "source_hash_matches_build_details": build_details["source_sha256"].get("vitis/s2b_inference_app.c") == app_sha,
            "ack_path_in_source": ack_static,
            "prior_terminal_acks_with_successor_response": ack_followed,
            "successful_run_terminals": run_response_count,
            "final_corpus_terminal_ack_dynamically_observed": False,
            "reason": "最终corpus响应之后没有下一RUN，且原deployment未保存运行后CSR IDLE/ACK快照。"
        },
        "execution": {
            "python": sys.version.split()[0], "process_model": "单Python进程；UART按stream读取；文件SHA逐块流式计算。",
            "hardware_access": False, "sdk_jtag_serial_actions": False,
            "peak_memory_measured": False
        }
    }


if __name__ == "__main__":
    try:
        result = main()
    except BaseException as exc:
        result = {"schema_version": 1, "replay_status": "FAIL", "errors": errors + [repr(exc)],
                  "warnings": warnings, "hardware_access": False}
    out = OUT / "replay_r02_corrected_result.json"
    with out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    summary = {key: result.get(key) for key in ("run_id", "replay_status", "errors", "warnings")}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("replay_status") == "PASS" else 1)
