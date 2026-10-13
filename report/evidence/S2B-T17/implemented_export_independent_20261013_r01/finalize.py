"""基于独立实际核查及冻结清单生成限定范围的真实兼容收据。"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from audit import ROOT, OUT, RUN, bind, exact, raw, read_json, require, sha


def save(name, value):
    """在独立目录排他创建UTF8结果。"""
    destination = OUT / name
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return bind(destination)


def main():
    """批准visibility0缓存探针的离线平台兼容性，不调用实物入口。"""
    facts = read_json(OUT / "independent_facts_r01.json")
    supplement = read_json(OUT / "supplement_facts_r01.json")
    platform = RUN / "delivery_manifest.json"
    package = ROOT / "report/evidence/S2B-T17/implemented_export_20261013_r01/delivery_manifest.json"
    require(bind(platform)["sha256"] == "bc6626dcd721a08bd0368b8f46d7960f0be79e5a76e139cb0b100ea75a6376b1", "r05平台清单不是冻结版本")
    require(bind(package)["sha256"] == "046e3547d955f4194ad267fd63b975503d1de89d519974da7b484e18ddc45346", "历史包装清单不是冻结版本")
    checks = read_json(platform)["checks"]
    require(len(checks) == 4 and all(row["status"] == "PASS" for row in checks), "r05平台声明未全部通过")
    executions = []
    parser = ROOT / "verification/check_stage_delivery.py"
    for label, mode, manifest in (("r05_inputs", "inputs", platform), ("r05_evidence", "evidence", platform),
                                  ("historical_package_evidence", "evidence", package)):
        command = [sys.executable, "-X", "utf8", "-B", str(parser), "--mode", mode, "--manifest", str(manifest)]
        began = time.monotonic()
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=60)
        for stream_name, data in (("stdout", completed.stdout), ("stderr", completed.stderr)):
            with (OUT / (label + "." + stream_name + ".log")).open("xb") as stream:
                stream.write(data)
        executions.append({"command": command, "native_exit_code": completed.returncode,
                           "elapsed_seconds": time.monotonic() - began,
                           "stdout": bind(OUT / (label + ".stdout.log")), "stderr": bind(OUT / (label + ".stderr.log"))})
        require(completed.returncode == 0, "独立包装检查失败：" + label)
    calls_binding = save("checker_calls_r01.json", executions)
    sys.path.insert(0, str(ROOT / "verification"))
    import check_s2b_inference_platform as checker
    sources = checker.check_static(ROOT)
    require(sources == facts["source_sha256"] and not facts["pnr"]["current_source_drift"], "当前静态源码闭包漂移")
    for item in facts["bindings"].values():
        require(bind(Path(item["path"])) == item, "独审输入在冻结后发生变化")
    bit = supplement["official_xsa_embedded_bit_extraction"]
    require(bind(Path(bit["path"])) == bit and supplement["same_xsa_embedded_bit_bytes"], "部署位流绑定不成立")
    for name, digest in {"verification/s15_direct_vivado_bitgen.py": "eb11cbd7285b6b647444c265be805c47d7ef3e2f18334a9c7ff9756f7f634441",
                         "verification/s15_bitgen_export.tcl": "bb1307e5b2d49a926213dd65c0d00767f345c23f6b42debb2bea015798d28e8d",
                         "tmp/2B/S2B-T17/basic_license_isolation_20261013_r01/run_isolated_basic.py": "dc8a42def578346b0b6aedcd974540e26b7c092afcb811afafefa8136db8b29d"}.items():
        require(bind(ROOT / name)["sha256"] == digest, "被审工具漂移")
    require(facts["bit_comparison"]["payload_bytes_equal"] and not facts["bit_comparison"]["full_bytes_equal"]
            and facts["bit_comparison"]["differing_bytes"] == 3, "位流差异事实错误")
    approvals = {"same_ps7_config": True, "same_ps_init_bytes": True, "same_bsp_mmu_macros": True,
                 "same_uart_ddr_csr_clocks": True, "full_model_core_present": True, "postroute_timing_pass": True}
    artifacts = {key: {field: facts["bindings"][key][field] for field in ("path", "sha256")}
                 for key in ("compiled_xsa", "implemented_xsa", "init_elf", "app_elf", "build_details")}
    artifacts["bit"] = {field: bit[field] for field in ("path", "sha256")}
    artifacts["platform_manifest"] = {field: bind(platform)[field] for field in ("path", "sha256")}
    receipt = {"schema_version": 1, "kind": "s2b-runtime-platform-compatibility/1.0.0",
               "role": "INDEPENDENT_REVIEWER", "status": "PASS", "scope": "visibility0_cache_probe_only",
               "visibility_parameter": 0, "source_sha256": sources, "artifacts": artifacts, "checks": approvals}
    require(set(receipt) == {"schema_version", "kind", "role", "status", "scope", "visibility_parameter", "source_sha256", "artifacts", "checks"}, "收据字段不符合生产契约")
    require(set(artifacts) == {"compiled_xsa", "implemented_xsa", "init_elf", "app_elf", "bit", "build_details", "platform_manifest"}, "收据产物字段不符合生产契约")
    for item in artifacts.values():
        require(bind(Path(item["path"]))["sha256"] == item["sha256"] and exact(Path(item["path"])).stat().st_size <= 32 * 1024 * 1024, "收据产物超预算或SHA漂移")
    state = bind(ROOT / ".codex/STATE.md")
    attributes = bind(ROOT / ".gitattributes")
    report = {
        "result": "PASS_OFFICIAL_EXPORT_AND_VISIBILITY0_OFFLINE_COMPATIBILITY_ONLY",
        "reviewer": "/root/basic_license_isolation_review",
        "reviewed_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "baseline_commit": "ddd4fbe9d981e8365440c0018c40a4aa3c87e210",
        "facts": bind(OUT / "independent_facts_r01.json"), "supplement": bind(OUT / "supplement_facts_r01.json"),
        "checker_calls": calls_binding, "platform_manifest": bind(platform), "historical_package": bind(package),
        "gitattributes": attributes, "state": state,
        "approval_basis": {
            "same_ps7_config": "独立解析C0/S15/DCP内hwdef/实际官方XSA，937个PS参数逐值一致。",
            "same_ps_init_bytes": "四方六份PS初始化原始字节一致；实际编译和初始ELF由原verify_build校验。",
            "same_bsp_mmu_macros": "六份BSP/MMU/编译文件实际SHA匹配T15；读取实际ELF MMUTable，DDR0x10000000项0x10015de6，CSR初始0x43c00c02；绑定应用将CSR改为Device0xc06并执行flush/invalidate。",
            "same_uart_ddr_csr_clocks": "实际BSP UART1地址0xe0001000/100MHz，CPU666666687Hz，DDR0x00100000..0x3fffffff及CSR0x43c00000..0x43c0ffff；编译与实现HWH地址范围相同，937PS参数相同，PNR50MHz且源码闭包一致。",
            "full_model_core_present": "实际官方HWH存在唯一s2b_inference_top且visibility0；原PNR固定DCP及当前33项check_static源码与独审46项来源闭包一致，非仅依赖HWH模块名。",
            "postroute_timing_pass": "核真既有独立PASS_PNR_STA_ONLY的固定DCP与原始时序报告；Physopt postRoute WNS0.007ns、WHS0.087ns、50MHz、12类check_timing均零。"
        },
        "bit_provenance": "同一官方Vivado会话导出时内部再次write_bitstream -force。外部bit与XSA内部bit仅三个d时间字节不同；4045564B载荷逐字节一致。审批bit精确绑定XSA原始成员提取文件，不把两完整文件称为相等。",
        "monitor": {"actual_samples": 313, "sampling_target_seconds": 0.5, "max_sample_gap_seconds": facts["process"]["max_sample_gap"],
                    "native_cmd_exit": 0, "native_vivado_exit": [0], "two_native_members_closed_zero_exit": True,
                    "all_stop_thresholds_preserved": True},
        "source_document_review": "新增Tcl仅在原bitgen后追加官方XSA导出；原控制器及原bitgen Tcl未改。.gitattributes仅新增精确-text规则；STATE日期与新增当前事实条目相符，并明确兼容和实物仍待核查，未追认r03/r04失败为通过。",
        "config_generator_review": {"sha256": "df86d4b6437a29dce84fb2a707021ea7953e578e61b9c18f4683e4d7bcc273f8", "result": "PASS_OFFLINE_CONFIG_GENERATOR_ONLY",
                                    "scope": "只读静态审查；生成必须有真实收据及SHA/HEAD/产物/currentidentity格式/排他输出。未调用设备入口、SDK或串口，仅git与evidence checker子进程。"},
        "original_failures": "r01/r03/r04失败保持；r03/r04的all-member closure为null，不声称身份完全闭合。汇总包的CHECKS_OK仅证明包装完整。",
        "audit_environment": "首轮check_static因沙箱拒绝祖先目录枚举而native1；受控提升后保持原检查器门禁运行native0，未读取许可或访问硬件。",
        "limitations": ["仅批准visibility0_cache_probe_only的离线平台兼容性。", "不代表缓存探针、冷恢复、PS/PL运行、109样本/1000压力、visibility1、G3/G4/G5通过。", "批准不关闭历史PNR连续预算受阻；本次bitgen/export监护独立判定。"]
    }
    report_binding = save("independent_review_receipt_r01.json", report)
    receipt_binding = save("runtime_compatibility_receipt_r01.json", receipt)
    print(json.dumps({"review": report_binding, "compatibility": receipt_binding, "scope": receipt["scope"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
