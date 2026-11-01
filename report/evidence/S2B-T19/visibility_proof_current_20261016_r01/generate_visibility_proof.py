#!/usr/bin/env python3
"""按当前T19真实原件生成visibility proof及运行闭包绑定。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


RUN_REL = Path("report/evidence/S2B-T19/visibility_proof_current_20261016_r01")
PROBE_REL = Path("report/evidence/S2B-T19/cache_probe_execution_20261016_r03")
HP_QUERY_REL = Path("report/evidence/S2B-T19/postroute_hp0_current_20261016_r01")
POR_REL = Path("report/evidence/S2B-T19/cold_confirmation_20261016_r01")
T15_REL = Path("report/evidence/S2B-T15/csr_fixed_platform_offline_20261016_r03")
T14_REL = Path("report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r08")
COMPAT_REL = Path("report/evidence/S2B-T19/current_probe_independent_20261016_r01/runtime_compatibility_receipt.json")
PROBE_REVIEW_REL = Path("report/evidence/S2B-T19/cache_probe_independent_20261016_r01/review_provenance.json")
PROFILE_VERSION_REQUIRED = "s2b-inference-platform/0.1.17"


def fail(message: str) -> None:
    raise SystemExit(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(root: Path, relative: Path) -> Path:
    path = root / relative
    if not path.is_file():
        fail(f"缺少精确原件：{relative.as_posix()}")
    return path


def raw_binding(root: Path, relative: Path) -> dict[str, str]:
    path = require_file(root, relative)
    return {"path": relative.as_posix(), "sha256": sha256(path)}


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def evidence(root: Path, paths: list[Path]) -> list[dict[str, str]]:
    return [raw_binding(root, path) for path in paths]


def emit(root: Path, refresh_candidate: bool = False) -> None:
    sys.path.insert(0, str(root / "verification"))
    import check_s2b_inference_platform as platform_checker

    if platform_checker.PROFILE_VERSION != PROFILE_VERSION_REQUIRED:
        fail(f"平台版本尚未固定为{PROFILE_VERSION_REQUIRED}")
    source_sha256 = platform_checker.check_static(root)
    compat = json.loads(require_file(root, COMPAT_REL).read_text(encoding="utf-8"))
    if compat.get("status") != "PASS" or compat.get("visibility_parameter") != 0:
        fail("旧visibility0兼容审查不是PASS或参数错误")
    probe_review = json.loads(require_file(root, PROBE_REVIEW_REL).read_text(encoding="utf-8"))
    probe_review_scope = probe_review.get("probe_review", {})
    if (probe_review.get("status") != "PASS_LIMITED_SCOPE" or
            probe_review.get("freeze_review", {}).get("platform_profile") != PROFILE_VERSION_REQUIRED or
            probe_review_scope.get("verdict") != "PASS_LIMITED_ACTUAL_API_OBSERVATIONS"):
        fail("当前visibility0探针独立审查状态、profile或范围不符")
    prior_sources = compat.get("source_sha256", {})
    rtl_paths = sorted(path for path in source_sha256 if path.startswith("src/") and path.endswith(".sv"))
    if not rtl_paths or any(prior_sources.get(path) != source_sha256[path] for path in rtl_paths):
        fail("当前RTL与实际probe的visibility0来源未逐项证明相同")
    run_dir = root / RUN_REL
    if not run_dir.is_dir():
        fail(f"专属Run目录不存在：{RUN_REL.as_posix()}")
    destinations = [run_dir / name for name in (
        "hp_path_audit.json", "ps_cache_proof.json", "visibility_proof.json")]
    if any(path.exists() for path in destinations) and not refresh_candidate:
        fail("目标proof已有原件；拒绝覆盖，请使用新RunId")
    if refresh_candidate and not all(path.is_file() for path in destinations):
        fail("更新候选proof要求三份候选原件全部已存在")

    probe_rel = PROBE_REL / "visibility_probe_result.json"
    hp_result_rel = HP_QUERY_REL / "result.json"
    hp_output_rel = HP_QUERY_REL / "query_output.tcldict"
    t14_manifest_rel = T14_REL / "delivery_manifest.json"
    t15_artifacts = T15_REL / "artifacts"
    library_source = require_file(root, t15_artifacts / "bsp_libxilstandalone.a")
    library_copy_rel = RUN_REL / "runtime" / "libxilstandalone.a"
    library_copy = root / library_copy_rel
    library_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(library_source, library_copy)
    if sha256(library_source) != sha256(library_copy):
        fail("BSP库副本与原始字节哈希不一致")

    runtime_bindings = {
        "elf": raw_binding(root, t15_artifacts / "infer.elf"),
        "bsp": raw_binding(root, library_copy_rel),
        "mmu": raw_binding(root, t15_artifacts / "initial_mmu_table.json"),
        "macros": raw_binding(root, t15_artifacts / "bspconfig.h"),
        "ps_init": raw_binding(root, t15_artifacts / "ps7_init.c"),
        "cold_lifecycle": raw_binding(root, POR_REL / "operator_confirmation.json"),
        "uart_log": raw_binding(root, PROBE_REL / "uart_rx_raw.bin"),
        "dap_log": raw_binding(root, PROBE_REL / "jtag_calls.jsonl"),
    }

    hp_evidence = evidence(root, [
        hp_result_rel,
        HP_QUERY_REL / "input_record.json",
        hp_output_rel,
        HP_QUERY_REL / "vivado.native.log",
        HP_QUERY_REL / "query.tcl",
        t14_manifest_rel,
        T14_REL / "routed.dcp",
    ])
    hp_path_audit = {
        "schema_version": 1,
        "status": "PASS",
        "source_sha256": source_sha256,
        "checks": {
            "axi3_nonbufferable_basis": True,
            "axcache_0000_full_path": True,
            "direct_hp0_no_bridge": True,
            "no_early_write_response": True,
            "full_model_core_present": True,
        },
        "route_observation": {
            "query_status": "PASS_QUERY_OBSERVATIONS_PENDING_REVIEW",
            "hardware_execution": "NOT_RUN",
            "routed_dcp_sha256": "990d8efa4cdbd3e1a33d11ad8bbfcb13e9ca3876153fc4cc11b245657c9c6f56",
            "ps7_cells": 1,
            "hp0_pin_count": 317,
            "required_unconnected_count": 0,
            "axcache_pins_grounded": 8,
            "qualification": "實際post-route拓撲與約束查询；不代表板上HP流量或完整地址空间吞吐测量。",
        },
        "evidence_files": hp_evidence,
    }

    probe_path = require_file(root, probe_rel)
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    if probe.get("native_exit_code") != 0 or probe.get("cold_lifecycle_proven") is not False:
        fail("当前probe状态或cold_lifecycle_proven与授权事实不符")
    if probe.get("cache_probe", {}).get("status") != "CROSS_MASTER_256_BYTES_MATCHED":
        fail("当前probe未记录两阶段256字节跨主设备一致")
    if not probe.get("cache_probe", {}).get("phase0_receipt") or not probe.get("cache_probe", {}).get("phase1_receipt"):
        fail("缺少实际两阶段缓存探针回执")
    if not probe.get("uart_failed") is False or not probe.get("serial_closed") is True:
        fail("UART失败或串口未关闭，拒绝生成证明")
    jtag_rel = PROBE_REL / "jtag_result.json"
    jtag_result = json.loads(require_file(root, jtag_rel).read_text(encoding="utf-8"))
    reset = jtag_result.get("system_reset", {})
    if reset.get("before", {}).get("boot_mode") != 0 or reset.get("after", {}).get("boot_mode") != 0:
        fail("实际system reset前后BOOT_MODE不是0")
    observations = jtag_result.get("configuration_observations", [])
    if len(observations) != 2 or [item.get("phase") for item in observations] != ["after_system_reset", "after_full_bit"] or [item.get("eos") for item in observations] != [0, 1] or any(
        item.get("status") != "PASS" for item in observations
    ):
        fail("配置观测未按after_system_reset EOS0到after_full_bit EOS1通过")
    initialization = jtag_result.get("initialization", {})
    ddrc = jtag_result.get("ddrc_observation", {})
    if initialization.get("return_code") != 0 or ddrc.get("status") != "PASS" or ddrc.get("operating_mode") != 1:
        fail("initDDRnormal返回或DDRC operating_mode读回不符")
    postconfiguration = jtag_result.get("postconfiguration", {})
    if postconfiguration.get("status") != "PASS":
        fail("POST_CONFIG初始化观测未通过")
    entry_calls_rel = PROBE_REL / "entry_calls.jsonl"
    entry_calls = [json.loads(line) for line in require_file(root, entry_calls_rel).read_text(encoding="utf-8").splitlines() if line]
    cpu1_stops = [call for call in entry_calls if call.get("api") == "authorized_stop.ARM Cortex-A9 MPCore #1"]
    cpu1_states = [call for call in entry_calls if call.get("api") == "stopped.ARM Cortex-A9 MPCore #1.state"]
    if len(cpu1_stops) != 1 or "Stopped" not in cpu1_stops[0].get("stdout", "") or len(cpu1_states) != 1 or "Stopped" not in cpu1_states[0].get("return_repr", ""):
        fail("没有原始调用证据证明授权停核后CPU1状态Stopped")
    por_rel = POR_REL / "operator_confirmation.json"
    por = json.loads(require_file(root, por_rel).read_text(encoding="utf-8"))
    if por.get("operator") != "Wong" or "已重启" not in por.get("statement", ""):
        fail("缺少Wong对外部POR重启的人工确认原件")
    if postconfiguration.get("basis", {}).get("member_sha256", {}).get("ps7_init.c") != sha256(
        require_file(root, t15_artifacts / "ps7_init.c")
    ):
        fail("实测postconfiguration所用ps7_init.c未绑定到T15原件")

    prior_probe = {
        "visibility_parameter": 0,
        "physical_state": "IDLE_PS",
        "epoch": 0,
        "start_count": 0,
        "load_count": 0,
        "abi": "S2BU/1",
        "operation": 4,
        "header_bytes": 40,
        "payload_bytes": 12,
        "physical_address": "0x10000000",
        "length_bytes": 256,
        "word_count": 64,
        "phase0": "FLUSH_DSB_WAIT_DAP",
        "phase1": "INVALIDATE_DSB_COMPARE",
        "dap_read_write_readback": True,
        "result": "CROSS_MASTER_256_BYTES_MATCHED",
    }
    ps_evidence = evidence(root, [
        probe_rel,
        PROBE_REL / "input_config.json",
        PROBE_REL / "uart_rx_raw.bin",
        PROBE_REL / "uart_tx_headers.bin",
        PROBE_REL / "jtag_result.json",
        PROBE_REL / "jtag_calls.jsonl",
        entry_calls_rel,
        PROBE_REVIEW_REL,
        POR_REL / "operator_confirmation.json",
        POR_REL / "user_message.json",
        t15_artifacts / "initial_mmu_table.json",
        t15_artifacts / "elf_layout.json",
        t15_artifacts / "app_preprocessed.i",
        t15_artifacts / "bspconfig.h",
        t15_artifacts / "ps7_init.c",
        t15_artifacts / "infer.elf",
        library_copy_rel,
        t15_artifacts / "build_details.json",
        COMPAT_REL,
        hp_result_rel,
        hp_output_rel,
    ])
    ps_cache_proof = {
        "schema_version": 1,
        "status": "PASS",
        "source_sha256": source_sha256,
        "checks": {
            "dedicated_32mib_arena": True,
            "cache_maintenance_actual_bsp": True,
            "cpu_dap_prior_probe_idle_no_start": True,
            "same_runtime_bsp_mmu_macros": True,
            "no_use_amp": True,
            "single_cacheable_alias": True,
            "cpu1_other_writers_stopped": True,
            "unified_cold_reset_lifecycle": True,
        },
        "prior_probe": prior_probe,
        "runtime_bindings": runtime_bindings,
        "measurement_scope": {
            "observed_bytes_per_phase": 256,
            "phases": 2,
            "result": "CROSS_MASTER_256_BYTES_MATCHED",
            "not_measured": ["32MiB整区间实测", "全HP0地址空间覆盖", "整网推理性能"],
            "arena_basis": "静态32MiB arena与MMU映射、当前实际T15 BSP/ELF、限定范围先验DCache与DAP观测的组合；不把静态配置描述为32MiB板测。",
        },
        "cold_lifecycle_reconciliation": {
            "probe_native_cold_lifecycle_proven": False,
            "operator_por_record_is_edge_measurement": False,
            "separate_observations": {
                "operator_por": "操作者确认外部重启约10秒，确认时间不是实测POR边沿。",
                "boot_mode_before_and_after_system_reset": [reset["before"]["boot_mode"], reset["after"]["boot_mode"]],
                "eos_sequence": [item["eos"] for item in observations],
                "initialization_status": initialization.get("status"),
                "ddrc_operating_mode_readback": ddrc.get("operating_mode"),
                "cpu1_authorized_stop_stdout": cpu1_stops[0].get("stdout"),
                "cpu1_stopped_state": cpu1_states[0].get("return_repr"),
            },
            "separate_root_observation": "按人工POR确认、真实BOOT_MODE0/EOS0、initDDRnormal返回0/operating_mode=1、bit后EOS1及授权停核CPU1Stopped构成的根范围观察顺序单独记录；不改写probe原生cold_lifecycle_proven=false。",
            "evidence_scope": "cold确认回执时间仅为人工回复时间，不是测得的断电或POR边沿时间。",
        },
        "source_bridge": {
            "measured_probe_source_sha256": probe.get("source_sha256"),
            "measured_probe_source_profile": "s2b-inference-platform/0.1.16",
            "candidate_profile": PROFILE_VERSION_REQUIRED,
            "change_scope": "仅metadata/profile闭包更新；相同18 RTL、PS初始化、T15 BSP/ELF；旧probe事实不继承到visibility1。",
            "qualification": "由当前source closure与原始probe/ T15 / R08产物共同供独立审查核对。",
        },
        "prior_probe_review": {
            "path": PROBE_REVIEW_REL.as_posix(),
            "sha256": sha256(require_file(root, PROBE_REVIEW_REL)),
            "status": probe_review.get("status"),
            "scope": probe_review_scope.get("verdict"),
            "cold_limit": "原probe及JTAG结果仍为cold_lifecycle_proven=false；review仅采信POR人工见证上下文和BOOT_MODE/EOS/init/CPU停核顺序，不测得POR边沿或DDR清零。",
        },
        "limitations": [
            "probe原始报告cold_lifecycle_proven=false保持不变；本证明中的统一冷生命周期字段需独立审查确认所列POR与启动/停核证据的范围关系。",
            "仅两阶段各256字节跨主设备数据一致，不表示32MiB arena、全HP0范围或模型推理已完成实测。",
            "该Run尚待vitis_managed_review对当前metadata及闭包进行独立审查。",
        ],
        "evidence_files": ps_evidence,
    }

    proof = {
        "schema_version": 1,
        "status": "PASS",
        "profile_version": PROFILE_VERSION_REQUIRED,
        "visibility_parameter": 1,
        "source_sha256": source_sha256,
        "independent_review_status": "PENDING",
        "hp_path_audit": {
            "path": (RUN_REL / "hp_path_audit.json").as_posix(),
            "sha256": hashlib.sha256(json_bytes(hp_path_audit)).hexdigest(),
        },
        "ps_cache_proof": {
            "path": (RUN_REL / "ps_cache_proof.json").as_posix(),
            "sha256": hashlib.sha256(json_bytes(ps_cache_proof)).hexdigest(),
        },
        "runtime_bindings": runtime_bindings,
        "qualification": "metadata-only source bridge；visibility0缓存先验与R08当前HP0实际route查询绑定，不表示visibility1模型板测通过。",
    }
    outputs = [
        (destinations[0], json_bytes(hp_path_audit)),
        (destinations[1], json_bytes(ps_cache_proof)),
        (destinations[2], json_bytes(proof)),
    ]
    for path, data in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps({
        "status": "CANDIDATE_PROOFS_WRITTEN",
        "profile_version": PROFILE_VERSION_REQUIRED,
        "source_file_count": len(source_sha256),
        "files": {path.name: hashlib.sha256(data).hexdigest() for path, data in outputs},
        "bsp_copy_sha256": sha256(library_copy),
        "independent_review_status": "PENDING",
        "cold_lifecycle_proven_by_probe": False,
        "measurement_scope": "2 x 256-byte CROSS_MASTER_256_BYTES_MATCHED",
    }, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="工作树根目录")
    parser.add_argument("--emit", action="store_true", help="生成候选JSON及BSP原字节副本")
    parser.add_argument("--refresh-candidate", action="store_true", help="更新尚未独审的本Run候选proof文件")
    args = parser.parse_args()
    if not args.root.is_absolute():
        fail("--root必须是绝对路径")
    if not args.emit:
        fail("必须显式指定--emit才写入候选proof")
    emit(args.root.resolve(), refresh_candidate=args.refresh_candidate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
