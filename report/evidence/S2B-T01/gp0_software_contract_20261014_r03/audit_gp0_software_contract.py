#!/usr/bin/env python3
"""核验绑定Vitis ELF的GP0软件单拍输入契约。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[4]
RUN_REL = "report/evidence/S2B-T01/gp0_software_contract_20261014_r03"
R01_REL = "report/evidence/S2B-T01/gp0_software_contract_20261014_r01"
R02_REL = "report/evidence/S2B-T01/gp0_software_contract_20261014_r02"
T15_REL = "report/evidence/S2B-T15/visibility1_xsa_20261014_r01"
T19_REL = "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01"
PREVIOUS_GP0_REL = "report/evidence/S2B-T01/gp0_translation_mode_audit_20261014_r01"
DEVELOPER_START_HEAD = "b02ea83ee3d40d0b940fdaefe30459f47e23a025"
BASELINE_HEAD = "0aaea57de30ee83833244bb2eb6e1caf802e39ce"
ELF_SHA256 = "a7ca427ab06f5f81a650bcb0d2bda3ed0adb716c3c2cb226c34519e695d47869"
ELF_BYTES = 390612
APP_SHA256 = "9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39"
T15_MANIFEST_SHA256 = "9abedb7b0b54363cfc96d40213b32d5ba7bdcad7c88e7f5f676f81ca7ccb4d65"
T15_BUILD_SHA256 = "0a5a80f05f0ccb8a00b737b91d145b704535578a62ab8d575cadfd83424587b0"
T15_XSA_SHA256 = "90f8d0b9e857f8beb9d99a6264b96441f9ba9b4b0af0568dbbcc064aecba6065"
T19_XSA_SHA256 = T15_XSA_SHA256
T19_MANIFEST_SHA256 = "0f32ff262d24dc49ff66e65d38653c27b0aaf53fffb263def51cf927412ca1ad"
OLD_CANDIDATE_SHA256 = "69de8697f2b4d2f49fe5925a8985a71937a28a9b4848c9f793feb91e481816d9"
R01_FINAL_SCRIPT_SHA256 = "dd5aac076d59756ee8d5fa36a7ec7ef66cd27496db1f245ab2764c636f8635d6"
R01_FINAL_JSON_SHA256 = "f15c9ffdf06d43d43c62a1b4dfbf33fb561c5af6ac5d5cf0aff9a0ec7088d1c8"
R01_FINAL_REPORT_SHA256 = "d4dbb9c2e15b249db95b839117434faed135d6f7fa1c3715c7a5702105550bbf"
R01_FINAL_MANIFEST_SHA256 = "f9f00f09744b4f55c92e66125bd1192a1581396ffe5e453f55a0355368c98516"
R01_PRELIMINARY_SCRIPT_SHA256 = "a285412c272387013f3fa932aaaa28a10db5f62b303a5642aba4edb1183e57af"
R01_PRELIMINARY_JSON_SHA256 = "69f2eb66540da92a560471f3d66780bd02da734e5c972796e1f27263a22fdf67"
R01_PRELIMINARY_REPORT_SHA256 = "6d74d5cd95107f11cc4bd70c5b57c7cb8b3e09e7ba2f1d29936822a8cef4b980"
R02_FINAL_SCRIPT_SHA256 = "062da989bc76cc84eeb47c075daffd72eac17eb5b93ee7e81ff3b303ab337d8d"
R02_FINAL_CONTRACT_SHA256 = "30a35fac38590f7bb5eff892ab9453fae748189b311adf83cd9c25e1e26dcdfe"
R02_FINAL_REPORT_SHA256 = "d9077f919cb25a37925c19d6ff747b626e090446347d917c4577ef1278e20ca9"
R02_FINAL_MANIFEST_SHA256 = "9442dbac8d0dc30a324c8301f236ec67537617ac1794412141b7521ab472f8ac"
R02_RAW_GUARD_SHA256 = "9c67fe77fa5846d39ef515be9cfff3eadd6d798616682631f560fd188728a7a3"
R02_UTF8_GUARD_SHA256 = "2ccfb2bb30bc85068966ad1c1a3263fd8688f316a0cc6cac7ef4fafe8b8e7dad"
R02_PREMANIFEST_VERIFY_SHA256 = "2c955e9914abec56dd55be15d02508e447974c8647ea76bbb1a9eb706fbcbd4a"
PYTHON_PATH = (
    r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime"
    r"\dependencies\python\python.exe"
)


def insist(condition: bool, message: str) -> None:
    """遇到不符合绑定基线的输入时立即停止。"""
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def repo_path(relative: str) -> Path:
    """解析经核验的仓库内相对路径，并拒绝逃逸。"""
    path = (ROOT / Path(relative)).resolve(strict=True)
    insist(path.is_relative_to(ROOT), f"仓库相对路径越界：{relative}")
    insist(path.is_file(), f"输入不是常规文件：{relative}")
    return path


def bind_file(relative: str, role: str, reason: str, expected: str | None = None) -> dict:
    path = repo_path(relative)
    digest, size = sha256_file(path)
    if expected is not None:
        insist(digest == expected, f"SHA-256不匹配：{relative}，得到 {digest}")
    return {
        "path": relative,
        "sha256": digest,
        "bytes": size,
        "role": role,
        "reason": reason,
    }


def read_text(relative: str, expected: str | None = None) -> tuple[str, dict]:
    binding = bind_file(relative, "input", "静态核查输入。", expected)
    text = repo_path(relative).read_bytes().decode("utf-8")
    return text, binding


def load_json(relative: str, expected: str | None = None) -> tuple[dict, dict]:
    text, binding = read_text(relative, expected)
    value = json.loads(text)
    insist(isinstance(value, dict), f"JSON顶层不是对象：{relative}")
    return value, binding


def section_name(strings: bytes, offset: int) -> str:
    insist(0 <= offset < len(strings), "ELF节名偏移越界")
    end = strings.find(b"\0", offset)
    insist(end >= 0, "ELF节名未以NUL结尾")
    return strings[offset:end].decode("ascii")


def parse_elf32_arm(path: Path) -> dict:
    """依ELF头及节表从虚拟地址换算文件偏移，不使用硬编码文件偏移。"""
    data = path.read_bytes()
    digest = sha256_bytes(data)
    insist(digest == ELF_SHA256, f"infer.elf完整SHA-256不符：{digest}")
    insist(len(data) == ELF_BYTES, f"infer.elf字节数不符：{len(data)}")
    insist(data[:4] == b"\x7fELF", "ELF魔数错误")
    insist(data[4] == 1 and data[5] == 1, "目标不是小端ELF32")
    insist(data[6] == 1, "ELF版本字段错误")
    (
        e_type,
        e_machine,
        e_version,
        entry,
        phoff,
        shoff,
        flags,
        ehsize,
        phentsize,
        phnum,
        shentsize,
        shnum,
        shstrndx,
    ) = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
    insist(e_type == 2 and e_machine == 40 and e_version == 1, "ELF不是ET_EXEC/ARM")
    insist(ehsize == 52 and shentsize >= 40 and shnum > 0, "ELF头/节表布局不支持")
    insist(shstrndx < shnum, "ELF节名表索引越界")
    insist(shoff + shentsize * shnum <= len(data), "ELF节表超出文件")

    raw_sections = []
    for index in range(shnum):
        item = struct.unpack_from("<IIIIIIIIII", data, shoff + index * shentsize)
        raw_sections.append(item)
    shstr = raw_sections[shstrndx]
    shstr_off, shstr_size = shstr[4], shstr[5]
    insist(shstr_off + shstr_size <= len(data), "ELF节名表超出文件")
    names = data[shstr_off : shstr_off + shstr_size]

    sections: dict[str, dict] = {}
    for index, item in enumerate(raw_sections):
        name_offset, kind, section_flags, address, offset, size, link, info, align, entsize = item
        name = section_name(names, name_offset) if name_offset else ""
        if kind != 8:
            insist(offset + size <= len(data), f"ELF节内容超出文件：{name}")
        if name:
            insist(name not in sections, f"ELF节名重复：{name}")
            sections[name] = {
                "index": index,
                "type": kind,
                "flags": section_flags,
                "address": address,
                "offset": offset,
                "size": size,
                "align": align,
                "entry_size": entsize,
                "link": link,
                "info": info,
            }
    insist(entry == 0x00100000, f"ELF入口地址错误：0x{entry:08x}")
    text = sections.get(".text")
    insist(text is not None, "ELF缺少.text")
    insist(text["type"] == 1 and (text["flags"] & 0x4) != 0, ".text不是可执行PROGBITS")
    insist(text["address"] == 0x00100000 and text["offset"] == 0x1000, ".text节映射不符")
    insist(text["size"] == 0xD6A4, ".text节长度不符")
    for required in (".mmu_tbl", ".s2b_tensor_ddr"):
        insist(required in sections, f"ELF缺少{required}")
    insist(
        sections[".mmu_tbl"]["address"] == 0x00110000
        and sections[".mmu_tbl"]["size"] == 0x4000,
        "ELF MMU表节映射不符",
    )
    arena = sections[".s2b_tensor_ddr"]
    insist(
        arena["type"] == 8
        and arena["address"] == 0x10000000
        and arena["size"] == 0x02000000
        and arena["align"] == 64,
        "ELF专属arena节属性/布局不符",
    )
    return {
        "sha256": digest,
        "bytes": len(data),
        "elf_class": "ELF32",
        "endianness": "little",
        "type": e_type,
        "machine": e_machine,
        "machine_name": "ARM",
        "entry": entry,
        "program_header_offset": phoff,
        "program_header_entry_size": phentsize,
        "program_header_count": phnum,
        "section_header_offset": shoff,
        "section_header_entry_size": shentsize,
        "section_count": shnum,
        "flags": flags,
        "sections": sections,
        "_bytes": data,
    }


SAMPLES = [
    (0x00100000, 0xEA000031, "b 1000cc <_boot>", "入口向量跳到启动代码"),
    (0x00100154, 0xE3C00001, "bic r0, r0, #1", "启动代码先清SCTLR.M"),
    (0x00100224, 0xE59F01E8, "ldr r0, [pc, #488]", "读取TTBR0表基址字面量"),
    (0x0010022C, 0xEE020F10, "mcr 15, 0, r0, cr2, cr0, {0}", "写TTBR0"),
    (0x00100230, 0xE3E00000, "mvn r0, #0", "构造全域访问控制值"),
    (0x00100234, 0xEE030F10, "mcr 15, 0, r0, cr3, cr0, {0}", "写域访问控制寄存器"),
    (0x00100238, 0xE59F01D8, "ldr r0, [pc, #472]", "读取SCTLR配置字面量"),
    (0x0010023C, 0xEE010F10, "mcr 15, 0, r0, cr1, cr0, {0}", "启动路径写SCTLR"),
    (0x00100240, 0xF57FF04F, "dsb sy", "SCTLR写后DSB"),
    (0x00100244, 0xF57FF06F, "isb sy", "SCTLR写后ISB"),
    (0x00100338, 0xEA00005F, "b 1004bc <_start>", "MMU初始化后进入_start"),
    (0x00100414, 0x00110000, ".word 0x00110000", "TTBR0表基址字面量"),
    (0x00100418, 0x00001005, ".word 0x00001005", "SCTLR配置字面量：M/C/I置位"),
    (0x00101220, 0xE7D3001F, "bfc r0, #0, #20", "MMU属性函数清除地址低20位"),
    (0x00101228, 0xE1800001, "orr r0, r0, r1", "合成section描述符属性"),
    (0x00101230, 0xE7830102, "str r0, [r3, r2, lsl #2]", "写MMU页表描述符"),
    (0x00101244, 0xF57FF04F, "dsb sy", "MMU属性更新后DSB"),
    (0x00101248, 0xF57FF06F, "isb sy", "MMU属性更新后ISB"),
    (0x00100FE8, 0xEE014F10, "mcr 15, 0, r4, cr1, cr0, {0}", "实际应用启用DCache"),
    (0x0010BC14, 0xE3A03000, "mov r3, #0", "CSR读取样例设置基址低位"),
    (0x0010BC1C, 0xE34433C0, "movt r3, #17344", "CSR读取样例形成0x43c00000"),
    (0x0010BC28, 0xE593400C, "ldr r4, [r3, #12]", "CSR+0x0c的32-bit load样例"),
    (0x0010BF14, 0xE3A0C000, "mov ip, #0", "CSR写入样例设置基址低位"),
    (0x0010BF1C, 0xE344C3C0, "movt ip, #17344", "CSR写入样例形成0x43c00000"),
    (0x0010BF70, 0xE58C0014, "str r0, [ip, #20]", "CSR+0x14的32-bit store样例"),
    (0x0010BF74, 0xF57FF04F, "dsb sy", "CSR写入后的DSB样例"),
    (0x0010C560, 0xE3A00000, "mov r0, #0", "实际调用前清零CSR_BASE低位"),
    (0x0010C564, 0xE3001C06, "movw r1, #3078", "实际调用DEVICE_MEMORY参数低半字"),
    (0x0010C568, 0xE34403C0, "movt r0, #17344", "实际调用CSR_BASE高半字"),
    (0x0010C56C, 0xEBFFD329, "bl 101218 <xil_settlbattributes>", "实际调用CSR Device属性设置"),
    (0x0010C570, 0xEBFFD296, "bl 100fd0 <xil_dcacheenable>", "实际调用DCache启用函数"),
]


def disassembly_line(text: str, address: int) -> tuple[int, str, str]:
    target = f"{address:06x}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(target):
            match = re.match(r"([0-9a-fA-F]+):\s+([0-9a-fA-F]+)\s+(.+)$", stripped)
            insist(match is not None, f"反汇编行格式错误：{stripped}")
            return int(match.group(1), 16), match.group(2).lower(), " ".join(match.group(3).lower().split())
    raise ValueError(f"反汇编缺少地址0x{address:08x}")


def check_text_sections(elf: dict, layout: dict, readelf: str) -> None:
    for name in (".text", ".mmu_tbl", ".s2b_tensor_ddr"):
        direct = elf["sections"][name]
        recorded = next((item for item in layout["sections"] if item.get("name") == name), None)
        insist(recorded is not None, f"既有elf_layout.json缺少{name}")
        for direct_key, recorded_key in (("type", "type"), ("address", "address"), ("offset", "offset"), ("size", "size"), ("align", "align")):
            insist(direct[direct_key] == recorded[recorded_key], f"ELF原节表与既有布局不符：{name}.{direct_key}")
    entry = re.search(r"Entry point address:\s+0x([0-9a-fA-F]+)", readelf)
    insist(entry is not None and int(entry.group(1), 16) == elf["entry"], "readelf入口与ELF头不符")
    patterns = {
        ".text": r"\[\s*\d+\]\s+\.text\s+PROGBITS\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)",
        ".s2b_tensor_ddr": r"\[\s*\d+\]\s+\.s2b_tensor_ddr\s+NOBITS\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)",
    }
    for name, pattern in patterns.items():
        found = re.search(pattern, readelf)
        insist(found is not None, f"readelf输出缺少{name}")
        address, offset, size = (int(value, 16) for value in found.groups())
        direct = elf["sections"][name]
        insist((address, offset, size) == (direct["address"], direct["offset"], direct["size"]), f"readelf与ELF节表不符：{name}")


def validate_baseline_relationship(repository: Path, baseline: str, strict_current_head: bool) -> None:
    """验证固定审计提交存在；复核时允许其为当前提交的祖先。"""
    current_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repository, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout.strip()
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{baseline}^{{commit}}"],
        cwd=repository,
        capture_output=True,
        check=False,
    )
    insist(exists.returncode == 0, f"固定审计提交不存在：{baseline}")
    if strict_current_head:
        insist(current_head == baseline, f"采集时HEAD不等于固定审计提交：{current_head}")
        return
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline, "HEAD"], cwd=repository, check=False
    )
    insist(ancestor.returncode == 0, f"固定审计提交不是当前HEAD祖先：{baseline} -> {current_head}")


def check_baseline_guard_fixture() -> dict:
    """在隔离临时Git仓库内验证采集严格、提交后复核允许祖先关系。"""
    with tempfile.TemporaryDirectory(prefix="s2b-gp0-baseline-guard-") as temporary:
        repository = Path(temporary)
        subprocess.run(["git", "init", "-q", "-b", "main", str(repository)], check=True, capture_output=True)
        identity = ["git", "-c", "user.name=GP0 fixture", "-c", "user.email=gp0-fixture@example.invalid"]
        subprocess.run(identity + ["commit", "--allow-empty", "-m", "baseline"], cwd=repository, check=True, capture_output=True)
        baseline = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repository, check=True, capture_output=True, text=True).stdout.strip()
        subprocess.run(identity + ["commit", "--allow-empty", "-m", "descendant"], cwd=repository, check=True, capture_output=True)
        validate_baseline_relationship(repository, baseline, strict_current_head=False)
        try:
            validate_baseline_relationship(repository, baseline, strict_current_head=True)
        except ValueError:
            strict_descendant_rejected = True
        else:
            raise AssertionError("严格采集路径接受了已前进的HEAD")
        subprocess.run(["git", "checkout", "-q", "--orphan", "unrelated"], cwd=repository, check=True, capture_output=True)
        subprocess.run(identity + ["commit", "--allow-empty", "-m", "unrelated"], cwd=repository, check=True, capture_output=True)
        try:
            validate_baseline_relationship(repository, baseline, strict_current_head=False)
        except ValueError:
            unrelated_history_rejected = True
        else:
            raise AssertionError("只读复核接受了非祖先审计提交")
    return {
        "status": "PASS_BASELINE_GUARD_FIXTURE",
        "strict_collection_rejects_descendant_head": strict_descendant_rejected,
        "read_only_verification_accepts_descendant_head": True,
        "read_only_verification_rejects_unrelated_head": unrelated_history_rejected,
        "fixed_facts_exclude_observed_head": True,
        "fixture_location": "系统临时目录中的隔离Git仓库，退出时由TemporaryDirectory清理；未触及项目Git数据库。",
    }


def collect_audit(strict_current_head: bool = True) -> dict:
    validate_baseline_relationship(ROOT, BASELINE_HEAD, strict_current_head)
    candidate = bind_file(
        "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
        "input",
        "候选文档当前GP0契约文本；仍未冻结，本审计不把它当作已冻结接口。",
    )
    app_source, app_binding = read_text("vitis/s2b_inference_app.c", APP_SHA256)
    t15 = Path(T15_REL)
    t15_manifest, t15_manifest_binding = load_json(f"{T15_REL}/delivery_manifest.json", T15_MANIFEST_SHA256)
    build, build_binding = load_json(f"{T15_REL}/build_details.json", T15_BUILD_SHA256)
    t19_manifest, t19_binding = load_json(f"{T19_REL}/delivery_manifest.json", T19_MANIFEST_SHA256)
    old_gp0, old_gp0_binding = load_json(f"{PREVIOUS_GP0_REL}/hwh_extract.json")
    r01_contract, r01_contract_binding = load_json(
        f"{R01_REL}/software_contract.json", R01_FINAL_JSON_SHA256
    )
    r01_manifest, r01_manifest_binding = load_json(
        f"{R01_REL}/delivery_manifest.json", R01_FINAL_MANIFEST_SHA256
    )
    r01_preliminary = r01_contract.get("same_run_preliminary_generation", {})
    insist(r01_preliminary.get("audit_script_sha256") == R01_PRELIMINARY_SCRIPT_SHA256, "R01历史初步脚本SHA记录不符")
    insist(r01_preliminary.get("software_contract_sha256") == R01_PRELIMINARY_JSON_SHA256, "R01历史初步JSON SHA记录不符")
    insist(r01_preliminary.get("audit_report_sha256") == R01_PRELIMINARY_REPORT_SHA256, "R01历史初步报告SHA记录不符")
    r02_manifest, r02_manifest_binding = load_json(
        f"{R02_REL}/delivery_manifest.json", R02_FINAL_MANIFEST_SHA256
    )
    insist(r02_manifest.get("run_id") == "gp0_software_contract_20261014_r02", "R02历史manifest RunId不符")
    r02_history_expected = {
        f"{R02_REL}/audit_gp0_software_contract.py": R02_FINAL_SCRIPT_SHA256,
        f"{R02_REL}/software_contract.json": R02_FINAL_CONTRACT_SHA256,
        f"{R02_REL}/audit_report.md": R02_FINAL_REPORT_SHA256,
        f"{R02_REL}/overwrite_guard_check.json": R02_RAW_GUARD_SHA256,
        f"{R02_REL}/overwrite_guard_check_utf8.json": R02_UTF8_GUARD_SHA256,
        f"{R02_REL}/readonly_verify_pre_manifest.json": R02_PREMANIFEST_VERIFY_SHA256,
    }
    r02_history_bindings = [
        bind_file(path, "input", "R02未通过G2的历史原字节输入；本R03不以R02事实推出ELF结论。", expected)
        for path, expected in r02_history_expected.items()
    ]
    r02_raw_guard = repo_path(f"{R02_REL}/overwrite_guard_check.json").read_bytes()
    r02_raw_guard_json = json.loads(r02_raw_guard.decode("cp936"))
    insist(r02_raw_guard_json.get("status") == "PASS_STRICT_OVERWRITE_GUARD", "R02原始stdout没有按CP936解出拒覆盖结果")
    r02_manifest_files = {item["path"]: item["sha256"] for item in r02_manifest.get("files", [])}
    insist(
        all(r02_manifest_files.get(path) == expected for path, expected in r02_history_expected.items()),
        "R02历史manifest未绑定预期现存文件",
    )

    candidate_hash_from_prior = old_gp0["audit"]["candidate_document"]["sha256"]
    insist(candidate_hash_from_prior == OLD_CANDIDATE_SHA256, "既有GP0审计未绑定指定候选文档前版SHA")
    insist(old_gp0["xsa"]["sha256"] == T19_XSA_SHA256, "既有GP0审计XSA SHA不符")
    insist(old_gp0["converter"]["parameters"]["TRANSLATION_MODE"] == "0", "XSA转换器不是mode0")
    insist(old_gp0["converter"]["parameters"]["SI_PROTOCOL"] == "AXI3", "转换器SI不是AXI3")
    insist(old_gp0["converter"]["parameters"]["MI_PROTOCOL"] == "AXI4LITE", "转换器MI不是AXI4-Lite")
    insist(old_gp0["converter"]["parameters"]["DATA_WIDTH"] == "32", "转换器数据宽度不是32 bit")
    xsa_binding = bind_file(
        f"{T19_REL}/artifacts/s2b_inference_wrapper_current.xsa",
        "input",
        "绑定与实际Vitis构建及既有HWH核查相同的visibility=1 XSA；仅静态配置来源。",
        T19_XSA_SHA256,
    )
    insist(t19_manifest["source_commit"] == "f92823f0bd577a49db543868f44c4f63b670d8e0", "T19 XSA来源提交不符")
    insist(build["xsa_sha256"] == T15_XSA_SHA256 and build["config"]["xsa_sha256"] == T15_XSA_SHA256, "T15构建绑定XSA不符")
    insist(build["source_commit"] == "8bbdcf821020dcb8f0909e8b5e6089ee51d120dc", "T15应用构建提交不符")
    insist(build["hardware_execution"] == "NOT_RUN", "T15硬件执行状态非NOT_RUN")
    insist(build["elf"]["sha256"] == ELF_SHA256, "build_details未绑定预期infer.elf")
    expected_inputs = {
        f"{T15_REL}/infer.elf": (ELF_SHA256, "实际推理ELF，按完整SHA和ELF节表读取。"),
        f"{T15_REL}/app_disassembly.log": ("5cdcfad70886a0a4420c1376fa0ae52b1e68ad34882ec767fd63ed2d3e9fa503", "已存GNU反汇编，与ELF选定地址逐条对照。"),
        f"{T15_REL}/app_readelf.log": ("5e4cfcc979947f2608f20283752b8495ff3d5839438e697e524c634579a8b9de", "已存readelf输出，与ELF头和节表交叉核对。"),
        f"{T15_REL}/app_preprocessed.i": ("db3b721814f017f1490b5fd06305cb048929b6f9832d2e6a35844a5bcc79706a", "绑定实际CPU0预处理后的MMIO访问实现。"),
        f"{T15_REL}/app_compile_commands.json": ("57f37cab9a0fb7a29746ab128e896db7f3fc9b10c6ad3748be3c0e53e6cabd58", "绑定实际Vitis编译命令和宏。"),
        f"{T15_REL}/bspconfig.h": ("1ff8617a56f0d6d9bdedfe48c2b25a9e0fe4cca26050053a64a2e35be11932d0", "绑定实际CPU0 BSP CPU标识。"),
        f"{T15_REL}/xparameters.h": ("7361be552faffb0b59b37d157c7fe7e332bea52841a17095e2ff7b8c80f04a36", "绑定实际BSP地址参数。"),
        f"{T15_REL}/xil_mmu.c": ("162ae3aecbf611b2d6bcb8454ff95b11040dcf807aa59b377b4b669b4966b864", "绑定实际BSP的section属性与屏障实现。"),
        f"{T15_REL}/xil_mmu.h": ("72bb377ea9cd805828e2103e47f35bdf3c0a291d4529c422a81391e86fe268ab", "绑定DEVICE_MEMORY常量定义。"),
        f"{T15_REL}/translation_table.S": ("bae655f4d6c39f01a2e0f100196cfbd02722c6ba7197225ba5e6bf237aaa4430", "绑定实际BSP翻译表初始化源快照。"),
        f"{T15_REL}/asm_vectors.S": ("bdc399c68867653fd00fd7707000d6e70162f6bad31f1be6ea3ad5248d5e93c7", "绑定实际BSP异常向量和启动源快照。"),
        f"{T15_REL}/elf_layout.json": ("4e2640a5dffca2af96e7987f084f2316ff3e34fe17c4d6c696dab4ec3060728c", "构建时ELF布局输出，与实际ELF节表交叉核对。"),
        f"{T15_REL}/source_snapshot/s2b_inference_app.c": (APP_SHA256, "T15运行保存的实际应用源码快照，必须与当前源字节一致。"),
        f"{PREVIOUS_GP0_REL}/s2b_inference.hwh": (old_gp0["xsa"]["hwh_member_sha256"], "由绑定XSA提取并被既有HWH审计核验的原字节。"),
    }
    input_bindings = [
        candidate,
        app_binding,
        t15_manifest_binding,
        build_binding,
        t19_binding,
        old_gp0_binding,
        xsa_binding,
        r01_contract_binding,
        r01_manifest_binding,
        r02_manifest_binding,
    ]
    r01_final_bindings = [
        bind_file(f"{R01_REL}/audit_gp0_software_contract.py", "input", "R01现存最终审计脚本原字节；历史输入只读保留。", R01_FINAL_SCRIPT_SHA256),
        r01_contract_binding,
        bind_file(f"{R01_REL}/audit_report.md", "input", "R01现存最终报告原字节；不代表G2通过或冻结。", R01_FINAL_REPORT_SHA256),
        r01_manifest_binding,
    ]
    r01_manifest_files = {item["path"]: item["sha256"] for item in r01_manifest["files"]}
    for item in r01_final_bindings[:3]:
        insist(r01_manifest_files.get(item["path"]) == item["sha256"], f"R01最终清单未绑定其现存文件：{item['path']}")
    input_bindings.extend(r01_final_bindings)
    input_bindings.extend(r02_history_bindings)
    input_bindings.extend(
        bind_file(path, "input", reason, expected)
        for path, (expected, reason) in expected_inputs.items()
    )
    input_bindings = list({item["path"]: item for item in input_bindings}.values())
    manifest_files = {
        item["path"]: item["sha256"] for item in t15_manifest["files"]
    }
    insist(manifest_files.get(f"{T15_REL}/infer.elf") == ELF_SHA256, "T15交付清单未绑定该infer.elf")
    insist(manifest_files.get("vitis/s2b_inference_app.c") == APP_SHA256, "T15交付清单未绑定当前应用源码")
    insist(build["source_sha256"].get("vitis/s2b_inference_app.c") == APP_SHA256, "T15构建回执未绑定实际应用源码")
    insist(
        sha256_file(repo_path(f"{T15_REL}/source_snapshot/s2b_inference_app.c"))[0] == APP_SHA256,
        "T15源快照与当前应用源码不同",
    )
    elf_path = repo_path(f"{T15_REL}/infer.elf")
    elf = parse_elf32_arm(elf_path)
    elf_bytes = elf.pop("_bytes")
    readelf = repo_path(f"{T15_REL}/app_readelf.log").read_bytes().decode("utf-8")
    disassembly = repo_path(f"{T15_REL}/app_disassembly.log").read_bytes().decode("utf-8")
    layout, layout_binding = load_json(f"{T15_REL}/elf_layout.json")
    check_text_sections(elf, layout, readelf)
    selected = []
    text_section = elf["sections"][".text"]
    for address, expected_word, fragment, purpose in SAMPLES:
        insist(text_section["address"] <= address and address + 4 <= text_section["address"] + text_section["size"], f"地址不在.text内：0x{address:08x}")
        file_offset = text_section["offset"] + address - text_section["address"]
        raw = elf_bytes[file_offset : file_offset + 4]
        actual_word = int.from_bytes(raw, "little")
        insist(actual_word == expected_word, f"ELF字节不符：VA 0x{address:08x} 实际0x{actual_word:08x}")
        dis_va, dis_word, disasm = disassembly_line(disassembly, address)
        insist(dis_va == address and int(dis_word, 16) == actual_word, f"反汇编与ELF原字节不符：0x{address:08x}")
        insist(fragment in disasm, f"反汇编助记符/操作数不符：0x{address:08x}，{disasm}")
        selected.append(
            {
                "virtual_address": f"0x{address:08x}",
                "elf_section": ".text",
                "section_address": f"0x{text_section['address']:08x}",
                "section_file_offset": f"0x{text_section['offset']:x}",
                "derived_file_offset": f"0x{file_offset:x}",
                "raw_bytes_little_endian": raw.hex(" "),
                "word": f"0x{actual_word:08x}",
                "disassembly": disasm,
                "purpose": purpose,
                "fact_class": "actual_elf_bytes_cross_checked_with_saved_objdump",
            }
        )

    # 解码两条选定的ARM single data transfer指令，独立核实访问方向/宽度/立即数。
    transfers = []
    for address, expected_load, base_register, base_value, expected_offset in (
        (0x0010BC28, True, 3, 0x43C00000, 0x0C),
        (0x0010BF70, False, 12, 0x43C00000, 0x14),
    ):
        row = next(item for item in selected if int(item["virtual_address"], 16) == address)
        word = int(row["word"], 16)
        insist((word & 0x0C000000) == 0x04000000, f"样例不是ARM data transfer：0x{address:08x}")
        immediate = (word >> 25) & 1 == 0
        upward = (word >> 23) & 1 == 1
        preindexed = (word >> 24) & 1 == 1
        byte_transfer = (word >> 22) & 1 == 1
        writeback = (word >> 21) & 1 == 1
        load = (word >> 20) & 1 == 1
        rn = (word >> 16) & 0xF
        rd = (word >> 12) & 0xF
        offset = word & 0xFFF
        insist(immediate and upward and preindexed and not byte_transfer and not writeback, "CSR样例不是无写回的正向word立即数访问")
        insist(load == expected_load and rn == base_register and offset == expected_offset, "CSR样例方向/基址/偏移不符")
        effective = base_value + offset
        insist(effective % 4 == 0, "CSR样例有效地址未按32-bit对齐")
        transfers.append(
            {
                "virtual_address": row["virtual_address"],
                "operation": "LDR word" if load else "STR word",
                "base_register": f"r{rn}",
                "base_register_setup": "0x43c00000，由同一函数内MOV/MOVT指令建立",
                "offset": f"0x{offset:x}",
                "effective_address": f"0x{effective:08x}",
                "width_bits": 32,
                "aligned_4_bytes": True,
                "preindexed": preindexed,
                "writeback": writeback,
                "instruction_word": row["word"],
                "derived_file_offset": row["derived_file_offset"],
                "raw_bytes_little_endian": row["raw_bytes_little_endian"],
                "fact_class": "decoded_actual_elf_sample_not_whole_program_coverage",
            }
        )
    source_lines = app_source.splitlines()
    insist("#define CSR_BASE 0x43C00000U" in app_source, "应用CSR_BASE不符")
    insist("#ifdef USE_AMP" in app_source and "#error" in app_source, "应用没有显式拒绝USE_AMP")
    insist("static void barrier(void) { __asm__ volatile(\"dsb sy\" ::: \"memory\"); }" in app_source, "源码DSB wrapper不符")
    insist("static uint32_t csr_read(uint32_t offset) { return Xil_In32(CSR_BASE + offset); }" in app_source, "源码csr_read不是Xil_In32包装")
    insist("static void csr_write(uint32_t offset, uint32_t value) { Xil_Out32(CSR_BASE + offset, value); barrier(); }" in app_source, "源码csr_write不是Xil_Out32并DSB包装")
    insist("Xil_SetTlbAttributes((INTPTR)CSR_BASE, DEVICE_MEMORY);" in app_source, "源码未设置CSR Device属性")
    insist("#define ARENA_BYTES 0x02000000U" in app_source, "源码arena容量不符")
    insist('section(".s2b_tensor_ddr")' in app_source and "aligned(64)" in app_source, "源码arena节或对齐声明不符")
    offsets = []
    for match in re.finditer(r"\bcsr_(?:read|write)\(\s*([^,\)]+)", app_source):
        expression = match.group(1).strip()
        if expression == "uint32_t offset":
            continue
        numeric = re.sub(r"[uUlL]+$", "", expression)
        try:
            value = int(numeric, 0)
        except ValueError as exc:
            raise ValueError(f"CSR调用偏移不是可核对常量：{expression}") from exc
        insist(value % 4 == 0, f"源码CSR偏移未4-byte对齐：{expression}")
        offsets.append(value)
    insist(offsets, "未找到CSR调用点")
    insist(len(re.findall(r"\bXil_In32\s*\(", app_source)) == 1, "CSR源码存在包装之外的Xil_In32调用")
    insist(len(re.findall(r"\bXil_Out32\s*\(", app_source)) == 1, "CSR源码存在包装之外的Xil_Out32调用")
    insist("volatile u32 *) Addr" in repo_path(f"{T15_REL}/app_preprocessed.i").read_bytes().decode("utf-8"), "预处理Xil_In32不是volatile u32 load")
    preprocessed = repo_path(f"{T15_REL}/app_preprocessed.i").read_bytes().decode("utf-8")
    insist("volatile u32 *LocalAddr = (volatile u32 *)Addr;" in preprocessed, "预处理Xil_Out32不是volatile u32 store")
    insist("#define DEVICE_MEMORY 0xC06" in repo_path(f"{T15_REL}/xil_mmu.h").read_bytes().decode("utf-8"), "BSP DEVICE_MEMORY常量不符")
    mmu_source = repo_path(f"{T15_REL}/xil_mmu.c").read_bytes().decode("utf-8")
    insist("section = Addr / 0x100000U;" in mmu_source and "*ptr = (Addr & 0xFFF00000U) | attrib;" in mmu_source, "BSP MMU属性函数不是1MiB section描述符路径")
    insist("dsb();" in mmu_source and "isb();" in mmu_source, "BSP MMU更新缺少DSB/ISB")
    bsp = repo_path(f"{T15_REL}/bspconfig.h").read_bytes().decode("utf-8")
    insist(re.search(r"^#define\s+XPAR_CPU_ID\s+0\s*$", bsp, re.MULTILINE) is not None, "BSP不是CPU0配置")
    compile_commands = json.loads(repo_path(f"{T15_REL}/app_compile_commands.json").read_bytes().decode("utf-8"))
    app_commands = [item["command"] for item in compile_commands if "s2b_inference_app.c" in item.get("file", "")]
    insist(len(app_commands) == 1, "Vitis编译命令中未唯一定位s2b_inference_app.c")
    compile_command = app_commands[0]
    insist("-DSDT" in compile_command and "-mcpu=cortex-a9" in compile_command, "编译命令未绑定SDT/Cortex-A9")
    insist("USE_AMP" not in compile_command and "S2B_HOST_MOCK" not in compile_command, "实际编译命令启用了AMP或host mock")
    insist("cpu0" in compile_command.lower(), "编译命令未出现CPU0 BSP路径")
    layout_arena = elf["sections"][".s2b_tensor_ddr"]
    insist(0x43C00000 % 4 == 0 and all(value % 4 == 0 for value in offsets), "CSR基址/偏移未对齐")
    sctlr_value = 0x1005
    facts = {
        "r01_recovery_history": {
            "preserved_final_files": [
                {"path": item["path"], "sha256": item["sha256"], "bytes": item["bytes"]}
                for item in r01_final_bindings
            ],
            "preliminary_generation_sha256_only": {
                "script": R01_PRELIMINARY_SCRIPT_SHA256,
                "software_contract_json": R01_PRELIMINARY_JSON_SHA256,
                "audit_report_md": R01_PRELIMINARY_REPORT_SHA256,
            },
            "preliminary_raw_bytes_recoverable": False,
            "preliminary_raw_bytes_status": "原字节不可恢复；仅有历史记录的SHA-256，不伪造恢复副本。",
            "r01_g2_status": "NOT_PASSED",
            "r01_upstream_frozen": False,
            "r01_status_reason": "R01同Run覆盖导致初稿原字节丢失；独立审查要求修复可恢复性，R01不作为G2通过或冻结上游。本R03保留R01现存最终四文件原字节作为历史输入。",
            "r01_contract_json_binding": r01_contract_binding["sha256"],
            "r01_manifest_binding": r01_manifest_binding["sha256"],
        },
        "r02_historical_run": {
            "run_id": r02_manifest["run_id"],
            "source_commit": r02_manifest["source_commit"],
            "g2_status": "NOT_PASSED",
            "frozen_upstream": False,
            "known_limitation": "R02只读入口要求复核时live HEAD仍等于source_commit；提交后不能回算。R02是原字节保留的历史运行，不作为G2通过或冻结上游。",
            "manifest_sha256": r02_manifest_binding["sha256"],
            "preserved_files": [
                {"path": path, "sha256": expected}
                for path, expected in r02_history_expected.items()
            ],
            "raw_stdout_capture": {
                "path": f"{R02_REL}/overwrite_guard_check.json",
                "sha256": R02_RAW_GUARD_SHA256,
                "role": "R02本地结果原始捕获；cp936/CRLF，JSON按cp936解码得到PASS_STRICT_OVERWRITE_GUARD；未按UTF-8解析。",
                "decoded_status": r02_raw_guard_json["status"],
                "raw_bytes_preserved": True,
            },
            "r02_facts_used_to_infer_elf": False,
        },
        "actual_elf_and_xsa": {
            "t15_build_status": build["status"],
            "hardware_execution": build["hardware_execution"],
            "vitis_version": build["vitis_version"],
            "app_build_commit": build["source_commit"],
            "xsa_sha256": build["xsa_sha256"],
            "xsa_source_commit": build["config"]["xsa_source_commit"],
            "elf": {key: value for key, value in elf.items() if key != "sections"},
            "elf_sections": elf["sections"],
            "t15_manifest_sha256": t15_manifest_binding["sha256"],
            "t19_manifest_sha256": t19_binding["sha256"],
            "xsa_sha256_verified": xsa_binding["sha256"],
        },
        "startup_mmu_path": {
            "actual_binary_facts": [
                "ELF e_entry=0x00100000；该处原始指令分支到_boot。",
                "启动代码把SCTLR.M清零后，读取0x00110000页表基址并写TTBR0、写DACR全域访问，再从ELF字面量0x00001005写SCTLR。",
                "0x00001005的SCTLR M、C、I位分别为bit0、bit2、bit12，值均为1；其后实际指令为DSB SY及ISB SY，随后进入_start。",
                "main实际调用Xil_SetTlbAttributes，调用参数在ELF中为地址0x43c00000及属性0x0c06；已绑定BSP宏DEVICE_MEMORY=0xC06。",
                "BSP实现以1MiB section写入(Addr & 0xFFF00000) | attrib，再执行D-cache flush、TLB/branch predictor失效及DSB/ISB；本结论同时绑定其T15源码哈希。",
            ],
            "static_inference": "如果该infer.elf按此启动路径由CPU0实际执行，MMU把0x43C00000所在1MiB section映射为DEVICE_MEMORY；该范围包含GP0 CSR窗口。",
            "runtime_not_proven": ["当前ELF未在板上下载/执行；MMU寄存器当前运行值未实测。", "板卡实际器件及PL当前配置不由ELF证明。"],
        },
        "csr_scalar_access": {
            "source_contract": {
                "csr_base": "0x43c00000",
                "csr_base_aligned_4_bytes": True,
                "csr_call_site_count": len(offsets),
                "distinct_aligned_offsets": [f"0x{value:03x}" for value in sorted(set(offsets))],
                "all_csr_call_offsets_aligned_4_bytes": True,
                "read_wrapper": "Xil_In32 -> volatile u32 load",
                "write_wrapper": "Xil_Out32 -> volatile u32 store; followed by DSB SY",
                "amp_compile_define_absent_and_source_rejected": True,
                "bsp_xpar_cpu_id": 0,
                "compile_cpu": "cortex-a9",
            },
            "selected_actual_elf_transfers": transfers,
            "selected_actual_elf_words": selected,
            "selected_word_sample_count": len(selected),
            "selected_instruction_note": "仅核对列出的ELF字/指令样例地址；这不是覆盖ELF全部指令/控制流的反汇编证明。",
            "static_inference": "对于受约束应用路径，源级全部CSR调用点使用对齐的32-bit Xil_In32/Xil_Out32；ELF样例实际为word LDR/STR。UG585 Device/Strongly Ordered属性保留ARM访问数量与大小，禁止未对齐和推测访问；这支持把单笔标量软件访问作为master输入契约。",
            "barrier_limit": "DSB SY是ARM内存顺序/完成屏障，不采样或证明GP0 AXI信号、AWLEN/ARLEN或Lite侧副作用。",
        },
        "bsp_cpu_and_arena": {
            "cpu0_bsp_fact": "T15实际生成的bspconfig.h为XPAR_CPU_ID=0，实际编译命令来自cpu0 BSP且未定义USE_AMP/S2B_HOST_MOCK。",
            "not_a_runtime_binding": "构建配置不证明板上当前运行的是该ELF，也不证明CPU1已停核或无中断/重入/其他writer。",
            "arena_elf_section": {
                "name": ".s2b_tensor_ddr",
                "kind": "SHT_NOBITS",
                "address": f"0x{layout_arena['address']:08x}",
                "size_bytes": layout_arena["size"],
                "alignment_bytes": layout_arena["align"],
            },
            "arena_limit": "ELF/linker中的NOLOAD 32MiB窗口不是实板DDR可用性、独占性或其他主机未访问的证明。",
        },
        "static_scope_and_g0_g3": {
            "g0_input_contract": "可核对绑定CPU0驱动、无AMP、标量对齐32-bit Device CSR访问及运行排他前提；可审查mode0的single-beat master输入契约和安全、受控的G3测试计划。",
            "g3_dynamic": ["GP0实际AWLEN/ARLEN值及VALID/READY握手。", "AXI3到Lite转换后的事务、读写响应和背压。", "协议异常与错误响应边界。", "converter/interconnect reset实际断言、释放、重叠及恢复行为。"],
            "not_staticaly_inferred": ["没有实板AWLEN=0或ARLEN=0观测。", "PS互连/GP0/Protocol Converter动态实现的行为、属性传递与异常输入结果。", "单核实际运行绑定、CPU1停核、无中断/无重入、无其他控制或arena writer。", "HP0读写事务、错误排空、cache维护/DDR可见性、完整模型结果与期限。"],
            "mode0_test_limit": "mode0规定SI单拍输入前提；本审计不建议也不执行在mode0下故意发送burst。",
            "overall_g0": "本审计只补充GP0软件输入契约静态证据；不宣布候选整体G0通过或接口冻结。",
            "acceptance": "100样本、1000连续任务及既有模型/实物验收标准保持不变。",
            "board_identity_update": "按Wong于2026-10-14最新确认，AX7020目标为XC7Z020-2CLG400I，照片所示亦为该型号，Vivado part应核实xc7z020clg400-2；此记录来自用户确认，不是本审计的物理测量鉴定。",
        },
        "prior_candidate_binding": {
            "previous_candidate_document_sha256": candidate_hash_from_prior,
            "current_candidate_document_sha256": candidate["sha256"],
            "candidate_version_or_frozen_status_changed": False,
            "hwh_converter_mode": old_gp0["converter"]["parameters"]["TRANSLATION_MODE"],
            "hwh_runtime_len": "not inferable from HWH",
        },
        "input_bindings": list(
            {item["path"]: item for item in input_bindings + [layout_binding]}.values()
        ),
        "source_locations": {
            "app": "vitis/s2b_inference_app.c:21-25,36,100-102,465-469",
            "app_preprocessed": f"{T15_REL}/app_preprocessed.i:5348-5381",
            "bsp_cpu_id": f"{T15_REL}/bspconfig.h:33",
            "mmu_attribute_constant": f"{T15_REL}/xil_mmu.h:56",
            "mmu_descriptor_and_barriers": f"{T15_REL}/xil_mmu.c:86-105",
            "elf_header_and_sections": f"{T15_REL}/app_readelf.log:11,25,39",
            "entry_sctlr_mmu_csr_samples": f"{T15_REL}/app_disassembly.log:8,113-115,165-173,303-305,1127-1135,1287-1301,16140,16356-16357,16741-16746",
            "xsa_hwh_mode0": f"{PREVIOUS_GP0_REL}/hwh_extract.json",
        },
        "sources": {
            "ug585_device_strongly_ordered": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Device-and-Strongly-Ordered",
            "pg059_protocol_conversion_options": "https://docs.amd.com/r/en-US/pg059-axi-interconnect/Protocol-CONVERSION-Options",
        },
        "tool": {
            "python_executable": str(Path(sys.executable).resolve()),
            "python_version": sys.version,
            "implementation": "stdlib only",
            "audit_time_china": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds"),
        },
        "review_boundary": {
            "evidence_is_offline_static_only": True,
            "elf_copied_into_new_run": False,
            "saved_readelf_objdump_and_t15_sources_copied": False,
            "hardware_access_or_run": False,
            "synthesis_or_simulation": False,
        },
    }
    # 记录本脚本字节哈希；原ELF、反汇编和大构建输入只绑定，不复制进新Run。
    script_rel = f"{RUN_REL}/audit_gp0_software_contract.py"
    facts["audit_script"] = bind_file(script_rel, "source", "实际运行的stdlib ELF/输入契约核验脚本。")
    facts["baseline"] = {
        "audit_execution_head": BASELINE_HEAD,
        "developer_start_head": DEVELOPER_START_HEAD,
        "t15_app_source_commit": build["source_commit"],
        "t19_xsa_source_commit": build["config"]["xsa_source_commit"],
        "old_gp0_audit_head": old_gp0["audit"]["worktree_head"],
    }
    return facts


def no_whitespace_errors(path: Path, root: Path) -> None:
    """用Git逐个检查新Run内的已跟踪/未跟踪文本，不把diff退出1误判为空白错误。"""
    if path.suffix.lower() == ".raw" or path.name == "overwrite_guard_check.json":
        return
    proc = subprocess.run(
        ["git", "diff", "--no-index", "--check", "--", "/dev/null", str(path.relative_to(root)).replace("\\", "/")],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    insist(proc.returncode in (0, 1), f"git diff --no-index --check执行失败：{path}: {proc.returncode} {proc.stderr}")
    insist(not proc.stdout and not proc.stderr, f"新Run文件存在空白诊断或Git错误：{path}: {proc.stdout}{proc.stderr}")


def validate_run_text(run_dir: Path) -> list[Path]:
    files = sorted(path for path in run_dir.iterdir() if path.is_file())
    insist(files, "Run目录没有证据文件")
    insist(all(path.suffix.lower() in {".py", ".md", ".json", ".raw"} for path in files), "Run目录出现未批准文件类型")
    for path in files:
        raw = path.read_bytes()
        if path.suffix.lower() == ".raw" or path.name == "overwrite_guard_check.json":
            continue
        raw.decode("utf-8")
        insist(b"\r" not in raw, f"新Run文本必须使用显式LF：{path.name}")
        insist(raw.endswith(b"\n"), f"新Run文本缺少末尾LF：{path.name}")
        no_whitespace_errors(path, ROOT)
    return files


def generation_targets(run_dir: Path) -> list[Path]:
    """返回此Run唯一允许生成的主结果目标。"""
    return [
        run_dir / "software_contract.json",
        run_dir / "audit_report.md",
        run_dir / "delivery_manifest.json",
    ]


def require_generation_targets_absent(targets: list[Path]) -> None:
    """主结果有任一已存在就拒绝写入，包含未完成且无manifest的Run。"""
    existing = [path.name for path in targets if path.exists()]
    if existing:
        raise FileExistsError("Run结果目标已存在，拒绝覆盖或重生：" + ", ".join(existing))


def check_overwrite_guard() -> dict:
    """在系统临时目录用空目标及逐一碰撞夹具核验拒覆盖逻辑。"""
    names = ("software_contract.json", "audit_report.md", "delivery_manifest.json")
    with tempfile.TemporaryDirectory(prefix="s2b-gp0-overwrite-guard-") as temporary:
        fixture_dir = Path(temporary)
        targets = [fixture_dir / name for name in names]
        require_generation_targets_absent(targets)
        cases = []
        for selected in targets:
            marker = ("保留夹具原字节：" + selected.name + "\n").encode("utf-8")
            with selected.open("xb") as stream:
                stream.write(marker)
            try:
                require_generation_targets_absent(targets)
            except FileExistsError as exc:
                insist(selected.read_bytes() == marker, "拒覆盖检查改写了已有夹具字节")
                cases.append({"existing_target": selected.name, "refused": True, "error": str(exc)})
            else:
                raise AssertionError(f"未拒绝已存在目标：{selected.name}")
            finally:
                selected.unlink()
        require_generation_targets_absent(targets)
    return {
        "status": "PASS_STRICT_OVERWRITE_GUARD",
        "tested_targets": list(names),
        "empty_target_set_accepted": True,
        "each_existing_target_refused_without_changing_fixture_bytes": cases,
        "fixture_location": "系统临时目录；退出时由TemporaryDirectory清理，不触及仓库Run输出。",
    }


def verify_read_only() -> dict:
    """从现存证据与原输入重算并比对；本入口不创建、修改或删除文件。"""
    run_dir = ROOT / RUN_REL
    insist(run_dir.is_dir(), "精确R03目录不存在")
    run_files_before = sorted(path for path in run_dir.iterdir() if path.is_file())
    before = {path.name: sha256_file(path)[0] for path in run_files_before}
    manifest_path = run_dir / "delivery_manifest.json"
    manifest = None
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        insist(manifest.get("run_id") == "gp0_software_contract_20261014_r03", "只读复核RunId不符")
        insist(manifest.get("source_commit") == BASELINE_HEAD, "只读复核source_commit不符")
        listed_local = {}
        for item in manifest.get("files", []):
            relative = item["path"]
            if relative.startswith(RUN_REL + "/"):
                listed_local[Path(relative).name] = item["sha256"]
                path = repo_path(relative)
                insist(sha256_file(path)[0] == item["sha256"], f"只读复核本Run文件哈希不符：{relative}")
            else:
                path = repo_path(relative)
                insist(sha256_file(path)[0] == item["sha256"], f"只读复核输入哈希不符：{relative}")
        expected_local = {name: digest for name, digest in listed_local.items()}
        actual_local = {name: digest for name, digest in before.items() if name != "delivery_manifest.json"}
        insist(expected_local == actual_local, "只读复核本Run文件集合与manifest不一致")

    saved = json.loads((run_dir / "software_contract.json").read_text(encoding="utf-8"))
    fresh = collect_audit(strict_current_head=False)
    saved_comparable = json.loads(json.dumps(saved))
    fresh_comparable = json.loads(json.dumps(fresh))
    saved_comparable.get("tool", {}).pop("audit_time_china", None)
    fresh_comparable.get("tool", {}).pop("audit_time_china", None)
    insist(saved_comparable == fresh_comparable, "只读重算facts与保存的software_contract.json不同")
    saved_report = (run_dir / "audit_report.md").read_bytes()
    insist(saved_report == render_report(fresh).encode("utf-8"), "只读重算报告与保存的audit_report.md不同")

    run_files_after = sorted(path for path in run_dir.iterdir() if path.is_file())
    after = {path.name: sha256_file(path)[0] for path in run_files_after}
    insist(before == after, "只读复核期间Run文件字节发生变化")
    return {
        "status": "PASS_READ_ONLY_RECOMPUTE",
        "run_id": manifest["run_id"] if manifest is not None else "gp0_software_contract_20261014_r03",
        "source_commit": manifest["source_commit"] if manifest is not None else BASELINE_HEAD,
        "recomputed_contract_matches": True,
        "recomputed_report_matches": True,
        "manifest_hashes_match": manifest is not None,
        "manifest_checked": manifest is not None,
        "run_file_hashes_unchanged": True,
        "files_checked": len(before),
        "writes_performed": False,
    }


def write_manifest(args: argparse.Namespace) -> None:
    run_dir = repo_path(RUN_REL + "/software_contract.json").parent
    audit_path = run_dir / "software_contract.json"
    report_path = run_dir / "audit_report.md"
    script_path = run_dir / "audit_gp0_software_contract.py"
    manifest_path = run_dir / "delivery_manifest.json"
    if manifest_path.exists():
        raise FileExistsError("delivery_manifest.json已存在，拒绝覆盖或重生")
    insist(audit_path.is_file() and report_path.is_file() and script_path.is_file(), "缺少先行生成的审计输出")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    baseline_result = json.loads((run_dir / "baseline_guard_check.json").read_text(encoding="utf-8"))
    overwrite_result = json.loads((run_dir / "overwrite_guard_check_utf8.json").read_text(encoding="utf-8"))
    readonly_result = json.loads((run_dir / "readonly_verify_pre_manifest.json").read_text(encoding="utf-8"))
    insist(baseline_result.get("status") == "PASS_BASELINE_GUARD_FIXTURE", "基线祖先夹具结果未通过")
    insist(overwrite_result.get("status") == "PASS_STRICT_OVERWRITE_GUARD", "拒覆盖检查结果文件未通过")
    insist(readonly_result.get("status") == "PASS_READ_ONLY_RECOMPUTE", "只读重算结果文件未通过")
    insist(readonly_result.get("writes_performed") is False and readonly_result.get("run_file_hashes_unchanged") is True, "只读重算结果未证明无写入及原字节保持")
    recompute = verify_read_only()
    insist(recompute["status"] == "PASS_READ_ONLY_RECOMPUTE", "生成manifest前只读重算失败")
    insist(args.baseline_guard_exit == 0, "固定提交祖先夹具检查未以exit 0完成")
    insist(args.overwrite_guard_exit == 0, "拒覆盖夹具检查未以exit 0完成")
    insist(args.readonly_check_exit == 0, "只读重算命令未以exit 0完成")
    run_files = validate_run_text(run_dir)
    external = audit["input_bindings"]
    listed = []
    for path in run_files:
        relative = path.relative_to(ROOT).as_posix()
        digest, _size = sha256_file(path)
        if path.name == "delivery_manifest.json":
            continue
        if path.name == "audit_gp0_software_contract.py":
            role = "source"
            reason = "本审计运行的只读ELF解析与证据绑定脚本。"
        elif path.suffix.lower() == ".raw" or path.name == "overwrite_guard_check.json":
            role = "result"
            reason = "首次拒覆盖检查的stdout原始捕获；保留Windows CP936/CRLF字节，不改写或作为UTF-8文本解析。"
        else:
            role = "result"
            reason = "本Run生成的机器可读核验结果或中文审计报告。"
        listed.append({"path": relative, "sha256": digest, "role": role, "keep_reason": reason})
    for item in external:
        listed.append(
            {
                "path": item["path"],
                "sha256": item["sha256"],
                "role": item["role"],
                "keep_reason": item["reason"],
            }
        )
    check_statuses = [
        {
            "name": "ELF与软件契约静态审计脚本",
            "status": "PASS",
            "command": f"{PYTHON_PATH} -B {RUN_REL}/audit_gp0_software_contract.py",
            "exit_code": 0,
            "reason": "实际脚本以绑定ELF、readelf/objdump和BSP证据运行完成。",
        },
        {
            "name": "固定基线严格采集与提交后祖先复核夹具",
            "status": "PASS",
            "command": f"{PYTHON_PATH} -B {RUN_REL}/audit_gp0_software_contract.py --check-baseline-guard",
            "exit_code": args.baseline_guard_exit,
            "reason": "隔离Git仓库证明采集拒绝前进HEAD、只读复核接受固定提交的后代HEAD并拒绝无关历史。",
        },
        {
            "name": "RunId拒覆盖夹具检查",
            "status": "PASS",
            "command": f"{PYTHON_PATH} -B {RUN_REL}/audit_gp0_software_contract.py --check-overwrite-guard",
            "exit_code": args.overwrite_guard_exit,
            "reason": "隔离临时夹具逐一占用JSON、报告和manifest目标；脚本均拒绝且原夹具字节不变。",
        },
        {
            "name": "输出只读重算核验",
            "status": "PASS",
            "command": f"{PYTHON_PATH} -B {RUN_REL}/audit_gp0_software_contract.py --verify-read-only",
            "exit_code": args.readonly_check_exit,
            "reason": "manifest生成前逐字节重算facts/报告并确认Run文件SHA未变化；manifest随后以独占创建方式写入。",
        },
        {
            "name": "UTF-8/LF与git空白诊断",
            "status": "PASS",
            "command": "脚本validate_run_text逐项解码UTF-8、拒绝CR并调用git diff --no-index --check",
            "exit_code": 0,
            "reason": "manifest生成前逐一核验Run目录已有全部文本；manifest自身写入后另行只读检查。",
        },
    ]
    manifest = {
        "schema_version": 1,
        "stage": "2B",
        "task_id": "S2B-T01",
        "run_id": "gp0_software_contract_20261014_r03",
        "source_commit": BASELINE_HEAD,
        "evidence_dir": RUN_REL,
        "interfaces": [],
        "interfaces_not_applicable_reason": "本audit核对既有实际T15软件ELF和绑定T19 XSA/HWH的GP0软件输入契约，没有消费任何已冻结的S2B物理接口；候选文档仍未冻结，本证据不以其替代冻结接口或批准接口冻结。R01与R02均未通过G2且不是冻结上游；本R03重新解析原ELF并绑定两Run现存历史文件。",
        "files": listed,
        "checks": check_statuses,
        "limitations": [
            "离线静态软件/ELF审计；没有下载或执行ELF，没有访问板卡、UART、JTAG或Vivado。",
            "不声称实际GP0 AWLEN/ARLEN为0，不把HWH连线或DSB屏障当作总线事务观测。",
            "mode0的single-beat输入前提不允许本Run故意向转换器发送burst。",
            "CPU0当前运行绑定、CPU1停核、无中断/重入/并发writer、arena独占及板上MMU属性均为运行前提，未由构建证明。",
            "HWH/XSA转换器动态行为、PS interconnect属性/事务形态、响应/READY背压/reset、HP0/cache/DDR可见性需G3及后续验收验证。",
            "不宣布整体G0/G2/G3/G4/G5通过；其他G0阻断与100样本/1000任务指标保持。",
        ],
        "tool_versions": {
            "python": "Python 3.12.14; 标准库",
            "evidence_checker": f"verification/check_stage_delivery.py at audit execution HEAD {BASELINE_HEAD}",
            "ELF_tools": "仅只读复用T15保存的GNU readelf/objdump文本；没有重新运行Vitis/GNU工具。",
        },
    }
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with manifest_path.open("xb") as stream:
        stream.write(encoded)
    insist(b"\r" not in manifest_path.read_bytes(), "manifest未保持LF")
    no_whitespace_errors(manifest_path, ROOT)
    print(json.dumps({"status": "MANIFEST_WRITTEN", "path": manifest_path.relative_to(ROOT).as_posix(), "files": len(listed), "checks": check_statuses}, ensure_ascii=False))


def render_report(facts: dict) -> str:
    elf = facts["actual_elf_and_xsa"]["elf"]
    sections = facts["actual_elf_and_xsa"]["elf_sections"]
    transfers = facts["csr_scalar_access"]["selected_actual_elf_transfers"]
    samples = facts["csr_scalar_access"]["selected_actual_elf_words"]
    rows = [
        "# GP0 软件单拍契约静态审计",
        "",
        "日期：2026-10-14（UTC+8）",
        "",
        "任务：S2B-T01 / RunId `gp0_software_contract_20261014_r03`",
        "",
        "## 结论与边界",
        "",
        "本Run核对了T15实际构建的 `infer.elf` 原字节、ELF32 ARM节表、保存的readelf/objdump、预处理应用、CPU0 BSP/MMU源码，以及与T15同SHA的T19 visibility=1 XSA/HWH静态审计。结果支持一个受限的软件输入契约：该实际应用由CPU0单核执行、无中断重入/并发提交、CPU1停核且没有其他GP0控制writer时，CSR通过32-bit、4-byte对齐、Device映射的标量load/store访问。证据是静态支持，不是板上AXI观测；选定指令是抽样核对，不构成逐条覆盖整个ELF的形式化证明。",
        "",
        "G0可以评审这一软件输入契约、CPU/写入者运行前提、mode0单拍要求及安全受控的G3测试计划。没有必要把G3实物事务波形前置成G0输入。绑定XSA的mode0要求SI所有事务为single-beat，但本审计没有观测 `AWLEN/ARLEN`，也不推断PS互连/转换器动态事务、Lite侧行为、响应/READY背压或reset恢复。mode0下不得故意发送burst。候选整体仍未冻结，其他G0阻断继续有效；本Run不宣布G0通过。",
        "",
        "## 基线与哈希绑定",
        "",
        f"- 固定审计基线：`{facts['baseline']['audit_execution_head']}`。生成时要求HEAD精确相同；只读复核验证该提交仍存在且为当前HEAD祖先，不把复核时HEAD写入固定facts。",
        f"- T15应用构建提交：`{facts['baseline']['t15_app_source_commit']}`；应用源码 SHA-256：`{APP_SHA256}`。当前源码与T15保存的 `source_snapshot/s2b_inference_app.c` 字节相同。",
        f"- 实际 `infer.elf`：SHA-256 `{elf['sha256']}`，{elf['bytes']} bytes；T15 delivery manifest 与 build_details 均绑定此SHA。原ELF未复制到本Run。",
        f"- T15 XSA：SHA-256 `{facts['actual_elf_and_xsa']['xsa_sha256_verified']}`；T19平台源提交 `{facts['baseline']['t19_xsa_source_commit']}`。T15 build_details、T19 XSA及既有HWH审计绑定相同XSA字节。",
        f"- T15 delivery manifest SHA-256：`{facts['actual_elf_and_xsa']['t15_manifest_sha256']}`；T19 delivery manifest SHA-256：`{facts['actual_elf_and_xsa']['t19_manifest_sha256']}`。旧GP0 HWH审计绑定候选前版SHA `{facts['prior_candidate_binding']['previous_candidate_document_sha256']}`；当前候选文档SHA `{facts['prior_candidate_binding']['current_candidate_document_sha256']}`。候选版本/冻结状态未由本Run变更。",
        f"- R01现存最终文件作为历史输入绑定：R01脚本 `{facts['r01_recovery_history']['preserved_final_files'][0]['sha256']}`、JSON `{facts['r01_recovery_history']['preserved_final_files'][1]['sha256']}`、报告 `{facts['r01_recovery_history']['preserved_final_files'][2]['sha256']}`、manifest `{facts['r01_recovery_history']['preserved_final_files'][3]['sha256']}`。",
        f"- R02历史stdout原始捕获：`{R02_REL}/overwrite_guard_check.json`，SHA-256 `{facts['r02_historical_run']['raw_stdout_capture']['sha256']}`；CP936/CRLF原字节保持不动，按CP936解码其JSON状态，不按UTF-8文本解析。R03拒覆盖检查另生成UTF-8/LF结果并纳入本Run manifest。",
        "- 完整输入路径、文件长度和SHA见同目录 `software_contract.json` 的 `input_bindings`。大ELF、反汇编和原构建材料只按路径/SHA绑定，不复制或改写。",
        "",
        "## ELF头和节表核对",
        "",
        f"直接解析ELF头得到：{elf['elf_class']}、{elf['endianness']} endian、ARM machine={elf['machine']}、ET_EXEC、entry=`0x{elf['entry']:08x}`；完整文件SHA先核验后解析。用节名表解析节表，不根据固定文件偏移猜测指令位置。",
        "",
        "| 节 | ELF type | VMA | 文件偏移 | size | align | 静态含义 |",
        "|---|---:|---:|---:|---:|---:|---|",
        f"| `.text` | {sections['.text']['type']} PROGBITS | `0x{sections['.text']['address']:08x}` | `0x{sections['.text']['offset']:x}` | `0x{sections['.text']['size']:x}` | {sections['.text']['align']} | 可执行代码，VA→file offset按节映射计算 |",
        f"| `.mmu_tbl` | {sections['.mmu_tbl']['type']} PROGBITS | `0x{sections['.mmu_tbl']['address']:08x}` | `0x{sections['.mmu_tbl']['offset']:x}` | `0x{sections['.mmu_tbl']['size']:x}` | {sections['.mmu_tbl']['align']} | 启动翻译表 |",
        f"| `.s2b_tensor_ddr` | {sections['.s2b_tensor_ddr']['type']} NOBITS | `0x{sections['.s2b_tensor_ddr']['address']:08x}` | `0x{sections['.s2b_tensor_ddr']['offset']:x}` | `0x{sections['.s2b_tensor_ddr']['size']:x}` | {sections['.s2b_tensor_ddr']['align']} | ELF中的32MiB NOLOAD arena声明 |",
        "",
        "直接ELF解析结果与既有 `elf_layout.json` 及 `app_readelf.log` 的entry、`.text`、arena字段一致。以下文件偏移都是由 `.text` 的 `sh_offset + (VA - sh_addr)`计算得出。",
        "",
        "## R01可恢复性记录",
        "",
        f"R01的三份初步字节仅保留历史SHA：脚本 `{R01_PRELIMINARY_SCRIPT_SHA256}`、JSON `{R01_PRELIMINARY_JSON_SHA256}`、报告 `{R01_PRELIMINARY_REPORT_SHA256}`；这些初稿原字节无法恢复，本Run不生成仿制副本。R01现存最终四个文件与R02七个最终/检查文件均以原字节绑定为历史输入。R01因初稿丢失未通过G2；R02虽有本地检查结果，但只读入口不能跨source_commit复核，也未通过G2。R01/R02都不是冻结上游；本R03从T15实际ELF和外部原输入重新采集静态事实，不用R01/R02结论推导ELF事实。",
        "",
        "## 启动MMU与CSR Device属性",
        "",
        "实际ELF入口 `0x00100000` 的word为 `0xea000031`，objdump解为跳转 `_boot`。启动路径先执行 `bic` 清SCTLR.M，然后加载 `.mmu_tbl` VMA `0x00110000`并写TTBR0，设置DACR，之后从ELF字面量 `0x00001005` 写SCTLR，紧跟 `DSB SY`、`ISB SY`，再分支到 `_start`。`0x1005` 的SCTLR M(bit0)、C(bit2)、I(bit12)均置位。实际应用后续又调用 `Xil_SetTlbAttributes`，传入 `CSR_BASE=0x43c00000` 和 `DEVICE_MEMORY=0xC06`，再调用 `Xil_DCacheEnable`。T15 BSP `xil_mmu.c`以1MiB section表项 `(Addr & 0xFFF00000) | attrib` 更新属性，并刷新D-cache、失效TLB/branch predictor、执行DSB/ISB；其section边界覆盖64KiB CSR窗口。",
        "",
        "下面逐项给出这些ELF样例word的VA、经ELF `.text` 节表映射得到的文件偏移、ELF原字节及保存反汇编。样例只核验列出位置，不覆盖所有控制流或证明整个系统不可能存在其他master。",
        "",
        "| 用途 | VA | 文件偏移 | ELF原字节（little-endian） | word | 已保存objdump |",
        "|---|---:|---:|---|---:|---|",
    ]
    for item in samples:
        rows.append(
            f"| {item['purpose']} | `{item['virtual_address']}` | `0x{int(item['derived_file_offset'], 16):x}` | `{item['raw_bytes_little_endian']}` | `{item['word']}` | `{item['disassembly']}` |"
        )
    rows.extend(
        [
        "",
        "这是链接ELF和绑定BSP源码中的静态路径。它支持‘若此ELF确由目标CPU执行，则该CPU虚拟地址映射被设置成Device’的推理；不证明实板已加载该ELF、MMU寄存器当前值、PS互连属性或真实事务。",
        "",
        "## 标量访问与对齐",
        "",
        "源级 `csr_read` 只调用 `Xil_In32(CSR_BASE + offset)`；预处理后的BSP实现为 `*(volatile u32 *)Addr`。`csr_write` 只调用 `Xil_Out32`（volatile `u32 *`写入）并执行 `DSB SY`。脚本检查了应用全部CSR调用点，偏移均为4的倍数，CSR_BASE本身也按4字节对齐；实际编译配置为Cortex-A9/SDT CPU0 BSP，源码禁止 `USE_AMP`，编译命令不定义 `USE_AMP` 或 `S2B_HOST_MOCK`。BSP `bspconfig.h` 的 `XPAR_CPU_ID=0`。",
        "",
        "| 用途 | VA | 由ELF节表推导的file offset | ELF原字节（little-endian） | 解码/有效地址 |",
        "|---|---:|---:|---|---|",
        ]
    )
    for item in transfers:
        rows.append(
            f"| {item['operation']} | `{item['virtual_address']}` | `{item['derived_file_offset']}` | `{item['raw_bytes_little_endian']}` | `{item['instruction_word']}`，{item['base_register']}={item['base_register_setup']}，offset `{item['offset']}`，EA `{item['effective_address']}`，32-bit对齐 |"
        )
    rows.extend(
        [
            "",
            "ELF的word指令字节与保存的objdump在相同VA逐项相符。Xil_In32的选定样例是 `LDR r4,[r3,#12]`，有效地址 `0x43c0000c`；写入样例是 `STR r0,[ip,#20]`，有效地址 `0x43c00014`，之后紧接实际 `DSB SY`。它们只示例性核对load/store宽度和屏障；源级对调用点的核对覆盖已列应用CSR调用表达式，但没有建立全ELF控制流、异常处理路径或第三方库无其他CSR writer的证明。",
            "",
            "AMD [UG585 v1.15 Device and Strongly Ordered](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Device-and-Strongly-Ordered)说明Device/Strongly Ordered访问保持ARM访问的数量与大小、禁止未对齐及推测访问。结合该ELF的32-bit标量load/store和对齐调用点，这足以支撑受限软件输入契约的静态评审。`DSB SY`不等于GP0事务捕获，也不证明 `AWLEN/ARLEN`。",
            "",
            "## CPU0、AMP与arena约束",
            "",
            "T15编译使用来自 `ps7_cortexa9_0/cpu0` 的实际BSP，`XPAR_CPU_ID=0`；应用源包含 `USE_AMP` 拒绝编译保护，保存的编译命令没有 `USE_AMP`。ELF中 `.s2b_tensor_ddr` 是地址 `0x10000000`、大小 `0x02000000`、64-byte对齐的NOBITS节。这些是构建和链接事实，不是运行绑定：未证明此ELF当前在CPU0执行、CPU1停核、无中断/重入、无DAP/PS DMA/其他PL writer，也未证明arena在板上DDR中运行时独占。",
            "",
            "## G0/G3界线及尚缺静态事实",
            "",
            "G0可核对软件输入契约：CPU0实际应用、非AMP、标量对齐32-bit Device CSR访问，以及无中断重入/其他控制writer、CPU1停核等运行前提；可审查在converter mode0下满足single-beat前提的安全G3测试计划。G0可以确认测试对象、边界和停止条件，不要求预先取得G3波形。候选其他HP/cache/恢复/timeout/数据绑定等G0阻断仍在；本Run不宣布整体G0通过。",
            "",
            "实际 `AWLEN/ARLEN`、AXI3 `VALID/READY`握手、converter输出Lite事务、读写响应和异常边界、READY背压、PS互连行为、reset断言/释放/重叠与恢复必须由G3实物/集成事务证据确认。静态HWH只能说明XSA中的AXI3→AXI4-Lite连接、32-bit宽度和 `TRANSLATION_MODE=0`；其 `AWLEN/ARLEN`连线没有运行值。AMD [PG059 Protocol CONVERSION Options](https://docs.amd.com/r/en-US/pg059-axi-interconnect/Protocol-CONVERSION-Options)对mode0要求SI所有事务为single-beat。本审计不故意对mode0送burst，不推测违规输入的转换器响应，也不把DSB当作总线观察。",
            "",
            "静态材料也不推出CPU实际执行位置、CPU1状态、IRQ/FIQ访问、独立writer/调试访问、实板MMU当前配置、HP0/DDR/cache可见性、whole-model correctness、实物速度和1000连续任务期限。这些依赖运行状态或硬件测量。Wong于2026-10-14确认AX7020目标器件为XC7Z020-2CLG400I、照片所示板卡亦为该型号，Vivado part应核实 `xc7z020clg400-2`；本Run仅记录该用户确认，不把它表述为物理测量鉴定。",
            "",
            "## 限制和执行记录",
            "",
            "- 只读复用已存在的T15/T19证据；新Run不复制390,612-byte ELF、718,896-byte objdump或其他大型输入，只绑定原路径/哈希。",
            "- 没有调用Vitis/GNU重新编译或执行ELF；没有运行仿真、综合、Vivado、JTAG、UART或板卡操作。",
            "- T15 build_details记载 `hardware_execution=NOT_RUN`；T15 BSP CPU0构建配置不证明上板CPU运行绑定。",
            "- 不改converter配置、RTL、驱动源码、候选版本或正式100样本/1000任务验收指标。",
            "- 全部直接输入/结果字节哈希、选定指令字/文件映射、运行工具和机读限制在 `software_contract.json`。证据包装检查只核对清单及文件绑定，不代表G0/G3/G4/G5通过。",
            "",
        ]
    )
    return "\n".join(rows)


def run_audit() -> None:
    run_dir = ROOT / RUN_REL
    insist(run_dir.is_dir(), "精确Run目录不存在")
    audit_path = run_dir / "software_contract.json"
    report_path = run_dir / "audit_report.md"
    require_generation_targets_absent(generation_targets(run_dir))
    facts = collect_audit()
    audit_json = json.dumps(facts, ensure_ascii=False, indent=2) + "\n"
    report = render_report(facts)
    for output, content in ((audit_path, audit_json), (report_path, report)):
        encoded = content.encode("utf-8")
        insist(b"\r" not in encoded and encoded.endswith(b"\n"), f"新文本不是显式LF：{output.name}")
        with output.open("xb") as stream:
            stream.write(encoded)
    print(json.dumps({"status": "PASS_STATIC_SOFTWARE_CONTRACT_ONLY", "elf_sha256": facts["actual_elf_and_xsa"]["elf"]["sha256"], "elf_bytes": facts["actual_elf_and_xsa"]["elf"]["bytes"], "verified_elf_word_samples": facts["csr_scalar_access"]["selected_word_sample_count"], "input_files_bound": len(facts["input_bindings"]), "report": f"{RUN_REL}/audit_report.md"}, ensure_ascii=False))


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="核验绑定Vitis ELF的GP0软件单拍输入契约")
    parser.add_argument("--finalize-manifest", action="store_true", help="只在manifest目标不存在时独占创建一次")
    parser.add_argument("--baseline-guard-exit", type=int, default=-1)
    parser.add_argument("--overwrite-guard-exit", type=int, default=-1)
    parser.add_argument("--readonly-check-exit", type=int, default=-1)
    parser.add_argument("--verify-read-only", action="store_true", help="重算并比较已有证据，不写文件")
    parser.add_argument("--check-baseline-guard", action="store_true", help="在隔离临时Git仓库检查基线祖先校验")
    parser.add_argument("--check-overwrite-guard", action="store_true", help="在隔离临时夹具中检查严格拒绝覆盖逻辑")
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="strict", newline="\n")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="strict", newline="\n")
    args = make_parser().parse_args()
    try:
        if args.finalize_manifest:
            write_manifest(args)
        elif args.verify_read_only:
            print(json.dumps(verify_read_only(), ensure_ascii=False))
        elif args.check_baseline_guard:
            print(json.dumps(check_baseline_guard_fixture(), ensure_ascii=False))
        elif args.check_overwrite_guard:
            print(json.dumps(check_overwrite_guard(), ensure_ascii=False))
        else:
            run_audit()
        return 0
    except Exception as exc:
        print(json.dumps({"status": "FAIL_STATIC_SOFTWARE_CONTRACT_AUDIT", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
