"""只读迁移当前ELF的visibility0限定准入；采集仅独占创建本Run摘要和清单。"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
RUN = "report/evidence/S2B-T19/current_probe_scope_20261015_r01"
BASELINE = "37c4b840977e727b6504d83b803da3358f89040e"
OLD = "report/evidence/S2B-T19/visibility0_compatibility_20261014_r01"
BSP = "report/evidence/S2B-T15/visibility1_xsa_20261014_r02"
GP0 = "report/evidence/S2B-T01/gp0_software_contract_20261014_r03"
PYTHON = r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
PINS = {
    OLD + "/audit_compatibility.py": "66a869f10f2a206ad0ef3090958d937a919661b7339f00469044a38333c2f16b",
    OLD + "/summary.json": "40f687966b8b71c466d4e9075893a9de2369ac494f16db13f652e177c0b96f33",
    OLD + "/delivery_manifest.json": "78df2c45ed08cb3603a62739c2bebb4f6fa87f97dc9e68c1b938cdaed07d97fe",
    GP0 + "/audit_gp0_software_contract.py": "36f810fa9ddb37f1d9c0739ed27d8a456f15359d9d33b2cd6e9fd184bec3028f",
    GP0 + "/software_contract.json": "a90e21460882793bf82e5a4713618d564d8bebc812a8731221ffb696098dd5cf",
    GP0 + "/delivery_manifest.json": "c5c6c9559c451cd50654735028a328dcc3fc2c37b8839fb3f1612492cdbdaa0e",
    BSP + "/package_offline_build.py": "b86df0fec83c02e36b2696db07c322c674aed7c0361d7cb270d2f8180a715110",
    BSP + "/delivery_manifest.json": "66008ed50e588698e7344e272d587e826073dc943e29aa8fff622939c2a6b243",
    BSP + "/runtime_section_comparison.json": "82d9e1ee16985f14f8352dbe51287b3c8d0e70004b878439bbb7fc2dd287a381",
    BSP + "/infer.elf": "a436634e803cd6990a108e9d00b23a13a4e039149d0e413e450faca1daf67f2d",
    BSP + "/init.elf": "978a0970d49f4afe4341fde7887e7f3d31b1aacb24f3b9e6511d96276a2e1b3a",
}
LIMITS = [
    "本Run仅为visibility=0、CPU/DAP起始256字节探针的离线静态准入迁移；不LOAD、不START、不经过PL/HP0。",
    "不生成INDEPENDENT_REVIEWER receipt或最终运行config；本Developer结果须独立审查后由总控决定消费。",
    "新旧完整ELF不相同；仅在逐节差异完全解释、31个原字样例及实际BSP重新核验后迁移限定GP0静态依据。",
    "实际AxLEN、HP0/cache属性与可见性未测；32MiB arena、整网G0/100黄金/1000连续及异常恢复均未通过本Run。",
    "CPU0单一控制、禁止IRQ重入、CPU1停止是实际硬件入口必须受控观察的前提；本Run未观测或宣称其已满足。",
    "旧构建host drift BLOCKED及上游全平台未冻结/失败原件保留；限定清单PASS不能使原平台G0或旧构建转为PASS。",
    "峰值内存未测；仅标准库静态解析，不启动SDK/Vitis/Vivado/JTAG/串口或硬件。",
]


def need(condition, message):
    """明确失败，优化模式不能消除门禁。"""
    if not condition:
        raise ValueError(message)


def sha(data):
    """返回原字节摘要。"""
    return hashlib.sha256(data).hexdigest()


def raw(relative, inputs, expected=None):
    """复用精确文件名，拒绝符号链接及摘要漂移。"""
    path = ROOT / relative
    need(path.is_file() and not path.is_symlink(), "精确普通文件缺失：" + relative)
    need(any(p.name == path.name for p in path.parent.iterdir()), "实际名称字符不符：" + relative)
    data = path.read_bytes()
    actual = sha(data)
    need(expected is None or actual == expected, "输入SHA不符：" + relative)
    need(relative not in inputs or inputs[relative] == actual, "同轮输入漂移：" + relative)
    inputs[relative] = actual
    return data


def module(relative, name, inputs):
    """只导入封存的离线解析程序，不调用其采集或运行main。"""
    raw(relative, inputs, PINS.get(relative))
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def audit(strict):
    """重新核验平台事实、当前构建闭包和新ELF软件契约，不写文件。"""
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, check=True, text=True).stdout.strip()
    need(not strict or head == BASELINE, "采集HEAD不等于固定基线")
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", BASELINE, "HEAD"], cwd=ROOT, capture_output=True)
    need(ancestor.returncode == 0, "固定基线不是当前HEAD祖先")
    inputs = {}
    for relative, expected in PINS.items():
        raw(relative, inputs, expected)
    previous = json.loads(raw(OLD + "/summary.json", inputs))
    old_facts = previous["audit"]
    for relative, expected in old_facts["input_sha256"].items():
        if relative.endswith("/delivery_manifest.json"):
            raw(relative, inputs, expected)
    # 沿用封存解析逻辑，明确替换BSP目录及两份ELF绑定后重新执行全部六项核验。
    compat = module(OLD + "/audit_compatibility.py", "current_probe_compat", inputs)
    compat.BSP = BSP
    compat.EXPECTED = dict(compat.EXPECTED)
    for key, filename in (("app_elf", "infer.elf"), ("init_elf", "init.elf")):
        compat.EXPECTED[key] = (BSP + "/" + filename, PINS[BSP + "/" + filename])
    current = compat.audit()
    need(set(current["checks"]) == compat.COMPAT and all(current["checks"].values()), "当前平台兼容事实失败：" + json.dumps(current["errors"], ensure_ascii=False))
    need(not current["current_build_source_drift"], "当前构建源码闭包仍有漂移")
    preflight = current.pop("old_build_runtime_preflight")
    need(preflight["status"] == "PASS", "当前transport.verify_build失败")
    for relative, expected in current["input_sha256"].items():
        raw(relative, inputs, expected)
    # 重新读取两份ELF，复算全部运行节/函数及差异分类，再与封存T15对照。
    package = module(BSP + "/package_offline_build.py", "current_probe_package", inputs)
    comparison = json.loads(raw(BSP + "/runtime_section_comparison.json", inputs))
    for label, filename in (("infer", "infer.elf"), ("init", "init.elf")):
        result = package.compare_elf(filename)
        need(result == comparison[label], "T15运行节/函数对照原件与重新计算不同：" + label)
        need(not result["different_function_symbols"], "有长度函数的地址/长度/原字节不同")
        for key in ("old_elf", "new_elf"):
            row = result[key]
            raw(row["path"], inputs, row["sha256"])
    classified = package.classify_infer_differences()
    need(comparison["infer"]["different_runtime_sections"] == [".rodata", ".text"], "infer存在额外运行节差异")
    need(comparison["init"]["different_runtime_sections"] == [".note.gnu.build-id"], "init存在额外运行节差异")
    # 直接从新ELF节表换算31个虚拟地址，核对word、原字节及新反汇编行。
    gp = module(GP0 + "/audit_gp0_software_contract.py", "current_probe_gp0", inputs)
    gp.ELF_SHA256 = PINS[BSP + "/infer.elf"]
    gp.ELF_BYTES = len(raw(BSP + "/infer.elf", inputs))
    elf = gp.parse_elf32_arm(ROOT / BSP / "infer.elf")
    layout = json.loads(raw(BSP + "/elf_layout.json", inputs))
    gp.check_text_sections(elf, layout, raw(BSP + "/app_readelf.log", inputs).decode("utf-8"))
    disassembly = raw(BSP + "/app_disassembly.log", inputs).decode("utf-8")
    samples = []
    need(len(gp.SAMPLES) == 31, "迁移样例不是31项")
    for address, expected, assembly, purpose in gp.SAMPLES:
        sections = [(name, s) for name, s in elf["sections"].items() if s["type"] != 8 and s["address"] <= address and address + 4 <= s["address"] + s["size"]]
        need(len(sections) == 1 and sections[0][0] == ".text", "31word样例未唯一映射到.text")
        name, section = sections[0]
        offset = section["offset"] + address - section["address"]
        payload = elf["_bytes"][offset:offset + 4]
        need(struct.unpack("<I", payload)[0] == expected, "新ELF样例原字不符")
        observed_address, observed_word, observed_assembly = gp.disassembly_line(disassembly, address)
        need(observed_address == address and int(observed_word, 16) == expected and assembly in observed_assembly, "新ELF反汇编样例不符")
        samples.append({"address": address, "section": name, "file_offset": offset, "bytes_hex": payload.hex(), "word": f"0x{expected:08x}", "assembly": observed_assembly, "purpose": purpose})
    mmu = raw(BSP + "/xil_mmu.c", inputs).decode("utf-8")
    need("section = Addr / 0x100000U;" in mmu and "*ptr = (Addr & 0xFFF00000U) | attrib;" in mmu and "dsb();" in mmu and "isb();" in mmu, "当前BSP页表更新/屏障路径不同")
    need("#define DEVICE_MEMORY 0xC06" in raw(BSP + "/xil_mmu.h", inputs).decode("utf-8"), "当前BSP Device常量不同")
    for relative in ("verification/s2b_board_transport.py", "verification/check_s2b_ps_smoke_layout.py", "verification/check_stage_delivery.py", RUN + "/audit_current_probe.py"):
        raw(relative, inputs)
    current["input_sha256"] = dict(sorted(inputs.items()))
    artifacts = dict(current["bound_artifacts"])
    return {
        "scope": "visibility0_cache_probe_only", "source_commit": BASELINE,
        "checks": current["checks"], "facts": current["facts"], "entry_contract": current["entry_contract"],
        "current_build_preflight": preflight, "current_build_source_drift": current["current_build_source_drift"],
        "bound_artifacts_without_platform_manifest": artifacts,
        "new_elf_gp0_static_migration": {"status": "PASS_STATIC_ONLY", "sample_count": len(samples), "samples": samples,
            "elf_sha256": gp.ELF_SHA256, "elf_sections": {k: elf["sections"][k] for k in (".text", ".mmu_tbl", ".s2b_tensor_ddr")},
            "runtime_comparison_recomputed_equal": True, "infer_difference_classification": classified,
            "startup_sctlr_literal": "0x1005", "startup_mmu_c_i_enabled": True, "csr_device_attribute": "0xc06",
            "evidence_reason": "31word覆盖启动MMU/TTBR0/SCTLR、CSR Device重标记、标量LDR/STR及DSB；全.text差异仅20字节GNU build-id，全部有长度函数原字节/地址/长度一致。",
            "dynamic_cpu_preconditions_observed": False, "actual_gp0_axlen_observed": False},
        "historical_blockers_preserved": {"old_build_runtime_preflight": old_facts["old_build_runtime_preflight"],
            "old_build_source_drift": old_facts["current_build_source_drift"],
            "upstream_original_checks": current["original_manifest_checks"]},
        "hardware_observations": current["hardware_observations"], "input_sha256": dict(sorted(inputs.items())),
        "limitations": LIMITS,
    }


def encode(value):
    """固定UTF-8和换行。"""
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main():
    """先完整核验，随后xb独占创建；verify只读且允许基线后代。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    need(args.collect != args.verify, "必须且仅指定--collect或--verify")
    if args.collect:
        need(sorted(p.name for p in (ROOT / RUN).iterdir()) == ["audit_current_probe.py"], "Run已占用，禁止覆盖或重生")
    start = time.monotonic()
    result = audit(args.collect)
    if args.verify:
        saved = json.loads((ROOT / RUN / "summary.json").read_text(encoding="utf-8"))
        need(saved["audit"] == result, "封存摘要与重新计算不符")
        manifest = json.loads((ROOT / RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
        for item in manifest["files"]:
            raw(item["path"], {}, item["sha256"])
        print("CURRENT_PROBE_STATIC_VERIFIED; independent_review_not_asserted; hardware_not_run")
        return
    command = [PYTHON, "-X", "utf8", "-B", RUN + "/audit_current_probe.py", "--collect"]
    summary = {"schema_version": 1, "kind": "s2b-current-probe-static-scope/1.0.0", "role": "DEVELOPER_EVIDENCE",
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "status": "STATIC_SCOPE_PASS_AWAITING_INDEPENDENT_REVIEW",
        "command": command, "native_exit_code": 0, "elapsed_seconds_before_output": time.monotonic() - start,
        "repeat_count": 2, "collection_attempts": [
            {"fixed_baseline": "6e75eca59274444fa66d81465dbc03a8aab6f276", "native_exit_code": 1,
             "stdout": "", "stderr": "{\"status\": \"BLOCKED\", \"error\": \"采集HEAD不等于固定基线\"}\n",
             "reason": "共享HEAD已推进为本Run当前基线；门禁在任何摘要输出前停止。"},
            {"fixed_baseline": BASELINE, "native_exit_code": 0, "reason": "当前基线重新采集，摘要和清单首次独占创建。"}],
        "peak_memory": "未测", "audit": result}
    summary_bytes = encode(summary)
    files = dict(result["input_sha256"])
    files[RUN + "/summary.json"] = sha(summary_bytes)
    checks = [{"name": name, "status": "PASS", "command": " ".join(command), "exit_code": 0, "reason": "当前输入原字节重新核验，详见summary.json。"} for name in sorted(result["checks"])]
    for name in ("current_build_source_closure", "new_elf_gp0_static_migration"):
        checks.append({"name": name, "status": "PASS", "command": " ".join(command), "exit_code": 0, "reason": "只读当前verify_build和新ELF/BSP静态核验通过。"})
    for name, reason in (
        ("full_model_runtime_g0", "本Run不消费模型或运行整网；仅为不LOAD/不START的256B CPU/DAP探针准备离线输入，原平台G0阻断仍保留。"),
        ("hardware_execution", "实际探针须在独立运行Run及独审准入后执行；本静态证据Run未执行硬件，不以此项表示动态通过。"),
        ("golden100_continuous1000_recovery", "正式整网验收由后续完整平台运行完成；本静态探针迁移不覆盖，也未降低100/1000及恢复指标。")):
        checks.append({"name": name, "status": "NOT_APPLICABLE", "reason": reason})
    upstream = json.loads((ROOT / BSP / "delivery_manifest.json").read_text(encoding="utf-8"))
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T19", "run_id": Path(RUN).name,
        "source_commit": BASELINE, "evidence_dir": RUN,
        "interfaces": [x for x in upstream["interfaces"] if x["version"] in ("s2b-physical-candidate/0.1.1", "s2bu-candidate/1.1")],
        "files": [{"path": path, "sha256": digest, "role": "source" if path.endswith(".py") else "result" if path == RUN + "/summary.json" else "input",
            "keep_reason": "绑定本Run静态核验实际读取的源码、原始平台/构建/历史阻断及结果，不改写上游原件。"} for path, digest in sorted(files.items())],
        "checks": checks, "limitations": LIMITS,
        "tool_versions": {"Python": sys.version.split()[0], "Vitis_build_only": "2026.1；本Run未启动Vitis"}}
    # 所有内容定稿后仅独占创建，不覆盖任何已有证据。
    for name, content in (("summary.json", summary_bytes), ("delivery_manifest.json", encode(manifest))):
        with (ROOT / RUN / name).open("xb") as stream:
            stream.write(content)
    print("CURRENT_PROBE_STATIC_COLLECTED; native_exit_code=0; independent_review_not_asserted; hardware_not_run")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "BLOCKED", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
