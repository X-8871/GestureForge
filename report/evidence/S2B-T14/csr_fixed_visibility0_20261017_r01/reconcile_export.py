"""对账Vivado原生XSA内部bit头时间差并生成离线交付包。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
SOURCE = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r07"
SOURCE_RESULT = SOURCE / "result.json"
SOURCE_INPUT = SOURCE / "input_record.json"
EXPECTED = {
    "xsa": "d3f1f14711322df567def1836ff2bbdef0f4c7d986e8e379c9f203dd206ca938",
    "raw_bit": "e3091c3a460adae2f6151ff2f235a798f3c8ba0cc30af1c750c44ddf125f80ea",
    "embedded_bit": "cec64cd0644ba39b8b311fd5bce38c9cfd03b2148052da4c5d2af7c56520145a",
    "sync_payload": "f02e79d53ebeba255b0cfd7a202efff2552404cadcc263aa5bcc90177b2a5281",
}
COPY_ARTIFACTS = (
    "timing_summary.rpt", "actual_timing_setup.rpt", "actual_timing_hold.rpt",
    "pulse_width.rpt", "clock_interaction.rpt", "clocks.rpt", "check_timing.rpt",
    "route_status.rpt", "utilization.rpt", "drc.rpt", "methodology.rpt",
    "methodology.json", "constraints.xdc", "routed.dcp", "s2b_inference.xsa",
    "timing_metrics.tcldict",
)


def sha256_bytes(data: bytes) -> str:
    """计算字节串的SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """计算文件的SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    """拒绝不符合冻结证据的输入。"""
    if not condition:
        raise RuntimeError(message)


def parse_xilinx_bit(data: bytes) -> dict:
    """按Xilinx .bit头部字段a至e读取文件，并返回头和配置payload。"""
    require(len(data) >= 16, "bit文件短于Xilinx头部最小长度")
    cursor = 0

    def take_u16(label: str) -> int:
        nonlocal cursor
        require(cursor + 2 <= len(data), f"{label}长度字段越界")
        value = struct.unpack_from(">H", data, cursor)[0]
        cursor += 2
        return value

    magic_length = take_u16("magic")
    require(magic_length == 9 and cursor + magic_length <= len(data), "Xilinx bit magic长度错误")
    magic = data[cursor:cursor + magic_length]
    cursor += magic_length
    require(take_u16("field marker") == 1, "Xilinx bit字段标记错误")
    fields: dict[str, bytes | int] = {}
    field_ranges: dict[str, tuple[int, int]] = {}
    for expected_tag in "abcd":
        require(cursor < len(data), f"缺少字段{expected_tag}")
        tag = chr(data[cursor])
        cursor += 1
        require(tag == expected_tag, f"字段顺序错误：应为{expected_tag}，实际{tag!r}")
        length = take_u16(f"字段{tag}")
        require(cursor + length <= len(data), f"字段{tag}内容越界")
        field_start = cursor
        value = data[cursor:cursor + length]
        cursor += length
        require(value.endswith(b"\0"), f"字段{tag}缺少NUL终止符")
        fields[tag] = value[:-1]
        field_ranges[tag] = (field_start, cursor)
    require(cursor < len(data) and chr(data[cursor]) == "e", "缺少payload长度字段e")
    cursor += 1
    require(cursor + 4 <= len(data), "字段e长度字段越界")
    payload_length = struct.unpack_from(">I", data, cursor)[0]
    cursor += 4
    require(payload_length == len(data) - cursor, "字段e长度与文件payload长度不符")
    payload = data[cursor:]
    return {"magic": magic, "fields": fields, "payload": payload,
            "field_ranges": field_ranges, "payload_offset": cursor, "payload_length": payload_length}


def main() -> None:
    """保留R07失败原件，生成含canonical XSA bit的离线对账包。"""
    require(SOURCE_RESULT.is_file() and SOURCE_INPUT.is_file(), "R07原始记录缺失")
    result = json.loads(SOURCE_RESULT.read_text(encoding="utf-8"))
    source_input = json.loads(SOURCE_INPUT.read_text(encoding="utf-8"))
    require(result.get("status") == "FAIL", "R07应保留其原始FAIL状态")
    require(result.get("job", {}).get("status") == "PASS" and
            result["job"].get("exit_code") == 0 and result["job"].get("cleanup_confirmed") is True,
            "R07原生Job并未通过或未完成清理")
    require(result.get("native_log_has_failure") is False and
            result.get("timing_slacks_nonnegative") is True and
            result.get("missing_or_empty_artifacts") == [], "R07不是已知的单一XSA内部bit时间头差异")
    require(result.get("xsa_bit_matches_r07_bit") is False, "R07结果已不再是待对账状态")
    xsa_source = SOURCE / "s2b_inference.xsa"
    raw_bit_source = SOURCE / "s2b_inference.bit"
    require(sha256_file(xsa_source) == EXPECTED["xsa"], "R07 XSA SHA与已观察输入不符")
    require(sha256_file(raw_bit_source) == EXPECTED["raw_bit"], "R07 bit SHA与已观察输入不符")

    final_records = (RUN / "input_record.json", RUN / "result.json", RUN / "delivery_manifest.json")
    require(not any(path.exists() for path in final_records), "R08最终记录已存在，拒绝覆盖")
    for name in COPY_ARTIFACTS:
        source = SOURCE / name
        require(source.is_file() and source.stat().st_size > 0, f"R07产物缺失或为空：{name}")
        require(result.get("artifact_sha256", {}).get(name) == sha256_file(source),
                f"R07原件SHA与R07结果记录不符：{name}")
        destination = RUN / name
        if destination.exists():
            require(destination.is_file() and sha256_file(destination) == sha256_file(source),
                    f"R08已有文件与R07原件不符，拒绝覆盖：{name}")
        else:
            shutil.copyfile(source, destination)
        require(sha256_file(RUN / name) == sha256_file(source), f"复制字节变化：{name}")
    require(result.get("artifact_sha256", {}).get("s2b_inference.bit") == sha256_file(raw_bit_source),
            "R07原始bit SHA与R07结果记录不符")
    raw_destination = RUN / "bitgen_raw.bit"
    if raw_destination.exists():
        require(raw_destination.is_file() and sha256_file(raw_destination) == sha256_file(raw_bit_source),
                "R08已有raw bit与R07原件不符，拒绝覆盖")
    else:
        shutil.copyfile(raw_bit_source, raw_destination)
    xsa_bytes = (RUN / "s2b_inference.xsa").read_bytes()
    with zipfile.ZipFile(RUN / "s2b_inference.xsa") as archive:
        bit_entries = [entry for entry in archive.namelist()
                       if entry.lower().endswith(".bit")]
        require(len(bit_entries) == 1 and Path(bit_entries[0]).name == "s2b_inference.bit",
                "原生XSA必须含唯一s2b_inference.bit成员")
        canonical_bit = archive.read(bit_entries[0])
    canonical_destination = RUN / "s2b_inference.bit"
    if canonical_destination.exists():
        require(canonical_destination.is_file() and sha256_file(canonical_destination) == sha256_bytes(canonical_bit),
                "R08已有canonical bit与XSA原件不符，拒绝覆盖")
    else:
        canonical_destination.write_bytes(canonical_bit)
    require(sha256_bytes(xsa_bytes) == EXPECTED["xsa"], "复制后的R07 XSA字节发生变化")
    require(sha256_bytes(canonical_bit) == EXPECTED["embedded_bit"], "XSA内部bit SHA不符")

    raw = parse_xilinx_bit((RUN / "bitgen_raw.bit").read_bytes())
    canonical = parse_xilinx_bit(canonical_bit)
    require(raw["magic"] == canonical["magic"], "bit magic不同")
    require(raw["fields"]["a"] == canonical["fields"]["a"], "bit设计标识字段a不同")
    require(raw["fields"]["b"] == canonical["fields"]["b"], "bit器件字段b不同")
    require(raw["payload"] == canonical["payload"], "Xilinx配置payload逐字节不同")
    sync_marker = bytes.fromhex("aa995566")
    sync_offsets = [offset for offset in range(len(canonical_bit)) if canonical_bit.startswith(sync_marker, offset)]
    require(sync_offsets == [260] and raw["payload"][260 - raw["payload_offset"]:] ==
            canonical["payload"][260 - canonical["payload_offset"]:], "配置sync后payload字节不一致")
    sync_payload = canonical_bit[260:]
    require(sha256_bytes(sync_payload) == EXPECTED["sync_payload"], "sync后配置payload SHA不符")
    changed_offsets = [offset for offset, (left, right) in enumerate(
        zip((RUN / "bitgen_raw.bit").read_bytes(), canonical_bit)) if left != right]
    require(len((RUN / "bitgen_raw.bit").read_bytes()) == len(canonical_bit) == 4045776,
            "两bit文件长度不符")
    require(changed_offsets == [202, 205], f"完整bit差异超出已核实日期/时间字节：{changed_offsets}")
    date_time_ranges = (raw["field_ranges"]["c"], raw["field_ranges"]["d"])
    require(all(any(start <= offset < end for start, end in date_time_ranges)
                for offset in changed_offsets), "bit差异不在日期/时间头字段c/d内")
    require(raw["fields"]["c"] != canonical["fields"]["c"] or
            raw["fields"]["d"] != canonical["fields"]["d"], "bit头日期/时间未见差异")

    source_result_sha = sha256_file(SOURCE_RESULT)
    source_input_sha = sha256_file(SOURCE_INPUT)
    artifact_names = (*COPY_ARTIFACTS, "bitgen_raw.bit", "s2b_inference.bit")
    artifact_sha = {name: sha256_file(RUN / name) for name in artifact_names}
    artifact_sizes = {name: (RUN / name).stat().st_size for name in artifact_names}
    missing = [name for name in artifact_names if artifact_sizes[name] <= 0]
    require(not missing, f"R08产物缺失或为空：{missing}")
    job = dict(result["job"])
    result_out = {
        "schema_version": 1,
        "status": "PASS_ARTIFACTS_PENDING_INDEPENDENT_REVIEW",
        "execution_type": "OFFLINE_ARTIFACT_RECONCILIATION",
        "hardware_execution": "NOT_RUN",
        "hardware_scope": "NOT_APPLICABLE_OFFLINE_PACKAGE_ONLY",
        "source_commit": result["source_commit"],
        "source_run_id": SOURCE.name,
        "source_result_path": str(SOURCE_RESULT),
        "source_result_sha256": source_result_sha,
        "source_input_record_path": str(SOURCE_INPUT),
        "source_input_record_sha256": source_input_sha,
        "source_run_original_status": result["status"],
        "source_run_original_bitgen_sha256": EXPECTED["raw_bit"],
        "source_run_native_xsa_sha256": EXPECTED["xsa"],
        "source_run_native_log_path": str(SOURCE / "vivado.native.log"),
        "source_run_native_log_sha256": result["native_log_sha256"],
        "job": job,
        "job_is_reused_source_evidence": True,
        "job_source_run_id": SOURCE.name,
        "job_source_result_sha256": source_result_sha,
        "native_log_has_failure": False,
        "native_log_provenance": {"path": str(SOURCE / "vivado.native.log"),
                                  "sha256": result["native_log_sha256"],
                                  "scope": "R07原生运行日志；R08未运行Vivado"},
        "timing_slack_values": result["timing_slack_values"],
        "timing_slacks_nonnegative": True,
        "xsa_contains_bit": True,
        "xsa_bit_matches_canonical_bit": True,
        "missing_or_empty_artifacts": missing,
        "artifact_sha256": artifact_sha,
        "artifact_sizes": artifact_sizes,
        "bit_reconciliation": {
            "format": "Xilinx .bit header fields a/b/c/d/e",
            "bitgen_raw_sha256": EXPECTED["raw_bit"],
            "embedded_canonical_sha256": EXPECTED["embedded_bit"],
            "design_field_a_equal": True,
            "part_field_b_equal": True,
            "date_field_c_raw": raw["fields"]["c"].decode("ascii"),
            "date_field_c_xsa": canonical["fields"]["c"].decode("ascii"),
            "time_field_d_raw": raw["fields"]["d"].decode("ascii"),
            "time_field_d_xsa": canonical["fields"]["d"].decode("ascii"),
            "differing_file_offsets": changed_offsets,
            "payload_offset": canonical["payload_offset"],
            "payload_length": canonical["payload_length"],
            "e_payload_sha256": sha256_bytes(canonical["payload"]),
            "payload_sha256_from_sync_word": EXPECTED["sync_payload"],
            "sync_word_offset": 260,
            "payload_byte_equal": raw["payload"] == canonical["payload"] and raw["payload"][48:] == canonical["payload"][48:],
        },
        "qualification": {"expected_samples": 109, "completed_samples": 0,
                          "expected_platform_samples": 1000, "completed_platform_samples": 0,
                          "status": "NOT_RUN"},
    }
    input_out = {
        "schema_version": 1,
        "status": result_out["status"],
        "execution_type": result_out["execution_type"],
        "hardware_execution": result_out["hardware_execution"],
        "source_commit": result_out["source_commit"],
        "source_run_id": SOURCE.name,
        "source_result_sha256": source_result_sha,
        "source_input_record_sha256": source_input_sha,
        "input_source_commit": source_input["source_commit"],
        "r07_status_preserved": result["status"],
        "job_is_reused_source_evidence": True,
        "job_source_run_id": SOURCE.name,
        "artifact_sha256": artifact_sha,
        "bit_reconciliation": result_out["bit_reconciliation"],
        "hardware_qualification_status": "NOT_RUN",
    }
    require(input_out["source_commit"] == input_out["input_source_commit"],
            "R08 input/result source commit不一致")
    manifest = {
        "schema_version": 1,
        "package_kind": "S2B-T14_OFFLINE_NATIVE_XSA_BIT_HEADER_RECONCILIATION",
        "status": result_out["status"],
        "scope": "offline_artifact_reconciliation_only",
        "hardware_execution": "NOT_APPLICABLE_FOR_THIS_PACKAGE",
        "hardware_qualification": result_out["qualification"],
        "source_commit": result["source_commit"],
        "source_run": {"run_id": SOURCE.name, "status": result["status"],
                       "result_sha256": source_result_sha, "input_record_sha256": source_input_sha,
                       "native_log_sha256": result["native_log_sha256"]},
        "bit_reconciliation": result_out["bit_reconciliation"],
        "artifacts": {name: {"path": name, "sha256": artifact_sha[name], "size_bytes": artifact_sizes[name]}
                      for name in artifact_names},
        "statement": "R07原始FAIL记录保持不变。R08仅将R07原生XSA内部bit作为canonical bit，并证明与R07 standalone bit的设计/器件字段相同、日期时间字段外payload逐字节相同。",
    }
    for filename, data in (("result.json", result_out), ("input_record.json", input_out),
                           ("delivery_manifest.json", manifest)):
        with (RUN / filename).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print(json.dumps({"status": result_out["status"], "source_run_status": result["status"],
                      "payload_sha256": EXPECTED["sync_payload"], "changed_offsets": changed_offsets,
                      "artifacts": len(artifact_names)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
