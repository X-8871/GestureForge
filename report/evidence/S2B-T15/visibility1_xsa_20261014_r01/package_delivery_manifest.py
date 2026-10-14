#!/usr/bin/env python3
"""为固定的 T15 visibility=1 XSA 离线构建生成可复核证据清单。"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


RUN_ID = "visibility1_xsa_20261014_r01"
RUN_REL = Path("report/evidence/S2B-T15") / RUN_ID
EXPECTED_HEAD = "8bbdcf821020dcb8f0909e8b5e6089ee51d120dc"
EXPECTED_XSA_SHA256 = "90f8d0b9e857f8beb9d99a6264b96441f9ba9b4b0af0568dbbcc064aecba6065"
EXPECTED_PLATFORM_MANIFEST_SHA256 = "0f32ff262d24dc49ff66e65d38653c27b0aaf53fffb263def51cf927412ca1ad"
EXPECTED_CONFIG_SHA256 = "15999265056f0b2ec110318e205d014f6ee4811e78b1dbb68d641f42acd415c8"
EXPECTED_MODEL_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
EXPECTED_FIXED_SAMPLES_SHA256 = "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed"
EXPECTED_SOURCE_COMMIT = EXPECTED_HEAD
EXPECTED_XSA_SOURCE_COMMIT = "f92823f0bd577a49db543868f44c4f63b670d8e0"

INPUT_HASHES = {
    "report/evidence/S2A-T01/tiny416_model_manifest.json": EXPECTED_MODEL_MANIFEST_SHA256,
    "report/evidence/S2A-T01/fixed_test_samples.json": EXPECTED_FIXED_SAMPLES_SHA256,
    "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    "docs/obsidian-project/02-方案设计/系统设计.md": "7aea2ed8a47423f80cda74aea98064f971b7da290509931387b33a2d28b8c33a",
    "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md": "5866547c88b60fbfa977d68c037fa117f7bbfda4e1c2ad0aaf15df200bc3d03c",
    "docs/obsidian-project/02-方案设计/s2b_board_transport.md": "8239191df5938e1d8c02c55a55bbf23ebe20c40fc53c9ae6b46641fc6254d1e5",
    "board/s2b_inference_platform.md": "5068a611fafffe49602f3fdffd6debb97cf6f3c9777ac945ed5b075b7a0d7133",
    "board/s2b_inference_platform.json": "c0b46d89b0ce063bd033586e1ba044bee4088c1bb91a2ea7b33bd285e24bc863",
    "tmp/2B/S2B-T15/t19_visibility1_config_20261014_r01.json": EXPECTED_CONFIG_SHA256,
    "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/artifacts/s2b_inference_wrapper_current.xsa": EXPECTED_XSA_SHA256,
    "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/delivery_manifest.json": EXPECTED_PLATFORM_MANIFEST_SHA256,
}

SOURCE_HASHES = {
    "vitis/s2b_inference_app.c": "9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39",
    "vitis/build_s2b_inference.py": "0259af39128d003c5548ca04c8c51c1652e27c546b5ae2bb709bc92efd879b97",
    "vitis/build_s2b_ps_smoke.py": "addff3a419609ac8203c8838edfd6fd56fb53baccf40efc403fca4eb36b50d76",
    "verification/s2a_ps_decode_nms_reference.c": "cf1904da1b6f9110a957ea788cdb7f9c6b7773d2fd8b7b61779063e5f995d845",
    "verification/s2a_ps_decode_nms_reference.h": "edd61d7f47e2681ebd3b21f599c9637d41b257f5e0fc7b9b909f7962d758ce47",
    "verification/s2b_board_transport.py": "355721403848a4e28afffa06c1dc442b6d52c94859a6ee167d58db10fcdd26c8",
    "verification/check_s2b_ps_smoke_layout.py": "6c12023cc9660d392a0f3e393df2ebaf425af8a4cbb51886a35749d0c6fa0f77",
}

LOG_COPIES = {
    "vitis_bsp_build.log": Path("tmp/2B/S2B-T15/t19_visibility1_20261014_r01/ps7/logs/cpu0_build.log"),
    "vitis_infer_build.log": Path("tmp/2B/S2B-T15/t19_visibility1_20261014_r01/infer/build/build.log"),
    "vitis_init_build.log": Path("tmp/2B/S2B-T15/t19_visibility1_20261014_r01/init/build/build.log"),
}


def sha256(path: Path) -> str:
    """逐块计算文件 SHA-256，避免将大型模型清单整体载入内存。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """以 UTF-8 严格读取 JSON 对象。"""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层不是对象：{path}")
    return value


def require_hash(root: Path, relative: str, expected: str) -> None:
    """核对精确路径存在且 SHA-256 与本轮冻结值一致。"""
    path = root / Path(relative)
    if not path.is_file():
        raise FileNotFoundError(f"缺少输入文件：{relative}")
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"SHA-256 不匹配：{relative}，预期 {expected}，实际 {actual}")


def verify_source_blobs(root: Path, details: dict[str, Any]) -> None:
    """同时核对本地源码、构建回执、快照和绑定提交中的 Git blob。"""
    details_hashes = details.get("source_sha256")
    if not isinstance(details_hashes, dict) or set(details_hashes) != set(SOURCE_HASHES):
        raise ValueError("build_details 的源码集合与本轮七份实际输入不一致")
    for relative, expected in SOURCE_HASHES.items():
        require_hash(root, relative, expected)
        if details_hashes.get(relative) != expected:
            raise ValueError(f"build_details 源码散列不匹配：{relative}")
        snapshot = root / RUN_REL / "source_snapshot" / Path(relative).name
        require_hash(root, snapshot.relative_to(root).as_posix(), expected)
        blob = subprocess.run(
            ["git", "cat-file", "blob", f"{EXPECTED_HEAD}:{relative}"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError(f"Git HEAD 源码 blob 与构建散列不匹配：{relative}")


def copy_logs(root: Path, run_dir: Path) -> None:
    """复制三份构建器原生日志；若目标已存在，只接受字节完全相同的副本。"""
    for name, source_rel in LOG_COPIES.items():
        source = root / source_rel
        target = run_dir / name
        if not source.is_file():
            raise FileNotFoundError(f"缺少构建原生日志：{source_rel.as_posix()}")
        if target.exists():
            if not target.is_file() or sha256(target) != sha256(source):
                raise FileExistsError(f"拒绝覆盖不匹配的日志副本：{target}")
        else:
            shutil.copy2(source, target)
        if sha256(target) != sha256(source):
            raise ValueError(f"日志复制后散列不匹配：{name}")


def verify_build(root: Path, run_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """核验本轮配置、平台输入和两个 ELF 布局证据。"""
    details_path = run_dir / "build_details.json"
    details = load_json(details_path)
    config = load_json(root / "tmp/2B/S2B-T15/t19_visibility1_config_20261014_r01.json")
    platform = load_json(
        root / "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/delivery_manifest.json"
    )
    if details.get("status") != "PASS_OFFLINE_FULL_XSA_BUILD":
        raise ValueError("build_details 状态不等于 PASS_OFFLINE_FULL_XSA_BUILD")
    if details.get("hardware_execution") != "NOT_RUN":
        raise ValueError("本轮硬件执行状态应为 NOT_RUN")
    if details.get("source_commit") != EXPECTED_SOURCE_COMMIT:
        raise ValueError("build_details 源提交不匹配")
    if details.get("xsa_sha256") != EXPECTED_XSA_SHA256:
        raise ValueError("build_details 中的 XSA SHA-256 不匹配")
    if details.get("config_sha256") != EXPECTED_CONFIG_SHA256:
        raise ValueError("build_details 配置 SHA-256 不匹配")
    if config.get("source_commit") != EXPECTED_HEAD:
        raise ValueError("配置文件 source_commit 不匹配")
    if config.get("xsa_source_commit") != EXPECTED_XSA_SOURCE_COMMIT:
        raise ValueError("XSA 源提交与已记录实现版本不匹配")
    if config.get("xsa_sha256") != EXPECTED_XSA_SHA256:
        raise ValueError("配置中的 XSA SHA-256 不匹配")
    if config.get("platform_manifest_sha256") != EXPECTED_PLATFORM_MANIFEST_SHA256:
        raise ValueError("配置中的上游 platform manifest SHA-256 不匹配")
    expected_xsa_path = root / "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/artifacts/s2b_inference_wrapper_current.xsa"
    expected_platform_path = root / "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/delivery_manifest.json"
    if Path(str(config.get("xsa", ""))).resolve() != expected_xsa_path.resolve():
        raise ValueError("配置中的 XSA 精确路径与本轮绑定路径不一致")
    if Path(str(config.get("platform_manifest", ""))).resolve() != expected_platform_path.resolve():
        raise ValueError("配置中的 platform manifest 精确路径与本轮绑定路径不一致")
    if platform.get("source_commit") != EXPECTED_XSA_SOURCE_COMMIT:
        raise ValueError("上游平台清单提交与 XSA 来源提交不匹配")
    if platform.get("tool_versions", {}).get("target_part") != "xc7z020clg400-2":
        raise ValueError("上游 XSA 目标不是任务要求记录的 XC7Z020 -2 候选")
    api_calls = details.get("api_calls", [])
    for required_api in ("platform.build", "app.build", "init.build"):
        if not any(
            item.get("name") == required_api
            and item.get("return_type") == "int"
            and item.get("return_repr") == "0"
            for item in api_calls
        ):
            raise ValueError(f"build_details 缺少成功回执：{required_api}")

    for relative, expected in INPUT_HASHES.items():
        require_hash(root, relative, expected)
    verify_source_blobs(root, details)

    for elf_key, layout_name, expected_entry in (
        ("elf", "elf_layout.json", 0x00100000),
        ("initializer_elf", "init_elf_layout.json", 0x00000000),
    ):
        record = details.get(elf_key)
        if not isinstance(record, dict):
            raise ValueError(f"build_details 缺少 {elf_key} 记录")
        elf_path = run_dir / ("infer.elf" if elf_key == "elf" else "init.elf")
        if Path(str(record.get("path", ""))).resolve() != elf_path.resolve():
            raise ValueError(f"build_details 中 {elf_path.name} 的精确路径不匹配")
        if sha256(elf_path) != record.get("sha256"):
            raise ValueError(f"{elf_path.name} 与 build_details ELF SHA-256 不一致")
        layout = load_json(run_dir / layout_name)
        if layout.get("entry") != expected_entry:
            raise ValueError(f"{layout_name} 入口地址不符合本轮 ELF 布局")
        readelf = run_dir / ("app_readelf.log" if elf_key == "elf" else "init_readelf.log")
        objdump = run_dir / ("app_disassembly.log" if elf_key == "elf" else "init_disassembly.log")
        if not readelf.is_file() or not objdump.is_file():
            raise FileNotFoundError(f"缺少 {elf_path.name} 的 readelf/objdump 输出")
        successful_commands = [
            item
            for item in details.get("commands", [])
            if item.get("exit_code") == 0 and Path(str(item.get("log", ""))).name in {readelf.name, objdump.name}
        ]
        if len(successful_commands) != 2:
            raise ValueError(f"{elf_path.name} 的 readelf/objdump 命令没有两项退出码 0 的回执")

    app_layout = load_json(run_dir / "elf_layout.json")
    arena = next(
        (item for item in app_layout.get("sections", []) if item.get("name") == ".s2b_tensor_ddr"),
        None,
    )
    if not isinstance(arena, dict) or (
        arena.get("address"), arena.get("size"), arena.get("align"), arena.get("type")
    ) != (0x10000000, 0x02000000, 64, 8):
        raise ValueError("infer.elf 的 DDR arena 未匹配 0x10000000/32 MiB/64-byte NOLOAD 布局")
    bsp_log = run_dir / "vitis_bsp_build.log"
    if "[102/102]" not in bsp_log.read_text(encoding="utf-8", errors="replace"):
        raise ValueError("CPU0 BSP 原生日志未记录 102/102 完成")
    init_layout = load_json(run_dir / "init_elf_layout.json")
    for section in init_layout.get("sections", []):
        address = section.get("address")
        size = section.get("size")
        if not isinstance(address, int) or not isinstance(size, int) or not size:
            continue
        end = address + size
        if address >= 0xFFFF0000:
            if end > 0xFFFFFE00:
                raise ValueError("init.elf 高地址节超出 OCM 上部窗口")
        elif address < 0x00030000:
            if end > 0x00030000:
                raise ValueError("init.elf 低地址节超出 OCM 下部窗口")
        elif section.get("flags", 0) & 0x2:
            raise ValueError(f"init.elf 含位于 OCM 外的已分配节：{section.get('name')}")
    return details, config, platform


def file_record(root: Path, path: Path, role: str, reason: str) -> dict[str, str]:
    """生成单个文件的仓库相对路径、角色和散列记录。"""
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256(path),
        "role": role,
        "keep_reason": reason,
    }


def build_manifest(root: Path, run_dir: Path, details: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """根据本轮冻结输入与运行目录实际内容生成标准证据清单。"""
    manifest_rel = RUN_REL / "delivery_manifest.json"
    files: list[dict[str, str]] = []
    for relative, expected in INPUT_HASHES.items():
        role = "input"
        if relative in SOURCE_HASHES:
            role = "source"
        files.append(
            {
                "path": relative,
                "sha256": expected,
                "role": role,
                "keep_reason": "绑定本轮模型、规格、平台 XSA、构建配置或物理/UART候选输入。",
            }
        )
    for relative, expected in SOURCE_HASHES.items():
        files.append(
            {
                "path": relative,
                "sha256": expected,
                "role": "source",
                "keep_reason": "本次 Vitis 实际消费并与绑定 Git HEAD blob 核对的七份源码之一。",
            }
        )

    manifest_path = root / manifest_rel
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix.casefold() == ".log":
            role = "log"
            reason = "保留本轮 Vitis/GNU 原始编译、ELF核验或版本输出。"
        elif path.name in {"build_details.json", "elf_layout.json", "init_elf_layout.json"}:
            role = "result"
            reason = "记录本轮构建回执或由 ELF/readelf 核验得到的布局结果。"
        elif path.name == "package_delivery_manifest.py":
            role = "artifact"
            reason = "本 Run 固定路径的可复核清单生成脚本。"
        elif path.suffix.casefold() in {".elf", ".map"}:
            role = "artifact"
            reason = "保留本轮离线生成的可执行 ELF 或链接映射。"
        elif path.suffix.casefold() == ".json":
            role = "result"
            reason = "保留本轮编译配置、命令或机器可读构建材料。"
        else:
            role = "artifact"
            reason = "保留本轮构建生成物或与输入绑定的源码快照。"
        files.append(file_record(root, path, role, reason))

    if len({record["path"] for record in files}) != len(files):
        raise ValueError("files 清单出现重复路径")

    xsa_check_command = (
        "核对 build config、build_details、上游 T19 platform manifest 及 XSA 的 SHA-256"
    )
    source_check_command = (
        "核对七份源码 SHA-256、source_snapshot 与 git cat-file blob 8bbdcf821020dcb8f0909e8b5e6089ee51d120dc:<path>"
    )
    elf_check_command = (
        "arm-none-eabi-readelf --wide -a；arm-none-eabi-objdump -d；核对两个 ELF 与 JSON 布局证据"
    )
    vitis_check_command = (
        "Vitis 2026.1 API：client.create_platform_component；platform.build；app.build；init.build"
    )
    package_command = (
        "python -B verification/check_stage_delivery.py --mode evidence --manifest "
        f"{manifest_rel.as_posix()}"
    )
    inputs_command = (
        "python -B verification/check_stage_delivery.py --mode inputs --manifest "
        f"{manifest_rel.as_posix()}"
    )
    checks = [
        {
            "name": "源码与 Git 提交绑定",
            "status": "PASS",
            "command": source_check_command,
            "exit_code": 0,
            "reason": "七份实际消费源码的散列同时匹配 build_details、工作树、source_snapshot 和绑定提交的 Git blob。",
        },
        {
            "name": "visibility=1 XSA、平台清单与构建配置绑定",
            "status": "PASS",
            "command": xsa_check_command,
            "exit_code": 0,
            "reason": f"XSA SHA-256={EXPECTED_XSA_SHA256}；平台清单 SHA-256={EXPECTED_PLATFORM_MANIFEST_SHA256}；配置 SHA-256={EXPECTED_CONFIG_SHA256}；目标 xc7z020clg400-2，XSA源提交 {EXPECTED_XSA_SOURCE_COMMIT}。",
        },
        {
            "name": "Vitis 离线完整平台与 CPU0 BSP/应用/初始化构建",
            "status": "PASS",
            "command": vitis_check_command,
            "exit_code": 0,
            "reason": f"Vitis 状态 {details['status']}；Vitis 原生退出码 0；BSP 编译 102/102；infer.elf 与 init.elf 均成功构建；耗时 {details['elapsed_seconds']:.2f} 秒。硬件执行状态为 NOT_RUN。",
        },
        {
            "name": "infer/init ELF、readelf/objdump 与内存布局证据",
            "status": "PASS",
            "command": elf_check_command,
            "exit_code": 0,
            "reason": f"infer.elf SHA-256={details['elf']['sha256']}，入口 0x00100000，32 MiB arena 位于 0x10000000 且 64-byte 对齐；init.elf SHA-256={details['initializer_elf']['sha256']}，入口位于 OCM 0x00000000。readelf/objdump 回执均为退出码 0。",
        },
        {
            "name": "G0 物理接口、UART 与完整器件身份",
            "status": "BLOCKED",
            "command": inputs_command,
            "exit_code": None,
            "reason": "待执行 inputs 模式确认冻结门禁；物理接口候选 s2b-physical-candidate/0.1.1 与 UART 候选 s2bu-candidate/1.1 均未冻结；芯片照片丝印为 XA7Z020/CLG400，用户转述厂商确认为 XC7Z020-2CLG400I，证据冲突未消解。",
        },
        {
            "name": "JTAG 下载、PS 初始化、UART/DDR/cache 与模型板上验收",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "本轮仅为离线构建封装，未连接或操作板卡；100 个黄金样本与 1000 次连续任务仍待实板执行。",
        },
        {
            "name": "标准 evidence 清单核验",
            "status": "NOT_RUN",
            "command": package_command,
            "exit_code": None,
            "reason": "清单写入后运行 verification/check_stage_delivery.py 的 evidence 模式。",
        },
    ]

    interfaces = [
        {
            "name": "S2A 冻结 tiny416 模型与 CSR/存储接口",
            "version": "S2A-T01/G0",
            "frozen": True,
            "path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
            "sha256": INPUT_HASHES["docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"],
        },
        {
            "name": "PS/PL 物理接口候选",
            "version": "s2b-physical-candidate/0.1.1",
            "frozen": False,
            "path": "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
            "sha256": INPUT_HASHES["docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"],
        },
        {
            "name": "CPU0/UART 运输候选",
            "version": "s2bu-candidate/1.1",
            "frozen": False,
            "path": "docs/obsidian-project/02-方案设计/s2b_board_transport.md",
            "sha256": INPUT_HASHES["docs/obsidian-project/02-方案设计/s2b_board_transport.md"],
        },
    ]

    return {
        "schema_version": 1,
        "stage": "2B",
        "task_id": "S2B-T15",
        "run_id": RUN_ID,
        "source_commit": EXPECTED_HEAD,
        "evidence_dir": RUN_REL.as_posix(),
        "interfaces": interfaces,
        "files": sorted(files, key=lambda item: item["path"]),
        "checks": checks,
        "limitations": [
            "本证据仅证明绑定 visibility=1 XSA 的 Vitis 离线 CPU0 BSP、推理应用和 PS 初始化 ELF 构建；不代表模型已部署或 G3/G4/G5 已通过。",
            "XSA 按 XC7Z020 -2 目标生成，器件完整身份尚未核验；照片中的 XA7Z020 与用户转述的 XC7Z020-2CLG400I 相冲突，不能据此认定板卡和 XSA 已匹配。",
            "PS/PL 物理接口候选 s2b-physical-candidate/0.1.1 与 UART 候选 s2bu-candidate/1.1 均未冻结，G0 仍阻断实板部署。",
            "未执行 JTAG 下载、PS 初始化、UART/DDR/cache 实测、100 个黄金样本比对或 1000 次连续任务；上述项目状态均为 NOT_RUN。",
            "Vitis 进程树峰值内存未测；build_details 将该项明确记录为未测。",
        ],
        "tool_versions": {
            "Vivado_XSA_provenance": "2026.1 build 6511674",
            "Vitis": details["vitis_version"],
            "ARM_GNU": "arm-xilinx-eabi-gcc 13.4.0",
            "target_part_candidate": "xc7z020clg400-2",
        },
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    """以 UTF-8 写入稳定缩进的 JSON 文件。"""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def run_evidence_check(root: Path, manifest_rel: Path) -> tuple[int, dict[str, Any]]:
    """调用仓库的只读证据清单检查器并解析其 JSON 回执。"""
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "verification/check_stage_delivery.py",
            "--mode",
            "evidence",
            "--manifest",
            manifest_rel.as_posix(),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"evidence 核验器未返回 JSON：{result.stdout!r} {result.stderr!r}") from exc
    return result.returncode, parsed


def run_inputs_check(root: Path, manifest_rel: Path) -> tuple[int, dict[str, Any]]:
    """运行 inputs 核验，确认 G0 阻塞及其具体未冻结项。"""
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "verification/check_stage_delivery.py",
            "--mode",
            "inputs",
            "--manifest",
            manifest_rel.as_posix(),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"inputs 核验器未返回 JSON：{result.stdout!r} {result.stderr!r}") from exc
    return result.returncode, parsed


def main() -> int:
    """执行固定 Run 的哈希复核、原生日志复制与清单生成。"""
    script_path = Path(__file__).resolve()
    root = script_path.parents[4]
    run_dir = root / RUN_REL
    if script_path.parent != run_dir.resolve():
        raise RuntimeError("脚本所在目录与固定 RunId 不符，拒绝写入")
    if subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip() != EXPECTED_HEAD:
        raise RuntimeError("当前 HEAD 与本轮构建绑定提交不一致")
    if not run_dir.is_dir():
        raise FileNotFoundError(f"本轮 evidence 目录不存在：{RUN_REL.as_posix()}")

    for relative, expected in INPUT_HASHES.items():
        require_hash(root, relative, expected)
    copy_logs(root, run_dir)
    details, config, _platform = verify_build(root, run_dir)
    manifest = build_manifest(root, run_dir, details, config)
    manifest_rel = RUN_REL / "delivery_manifest.json"
    manifest_path = root / manifest_rel
    write_json(manifest_path, manifest)

    first_code, first_result = run_evidence_check(root, manifest_rel)
    evidence_check = next(
        item for item in manifest["checks"] if item["name"] == "标准 evidence 清单核验"
    )
    if first_code != 0 or first_result.get("status") != "CHECKS_OK":
        evidence_check["status"] = "FAIL"
        evidence_check["exit_code"] = first_code if first_code != 0 else 2
        evidence_check["reason"] = "首轮 evidence 清单核验失败；详见生成器标准输出。"
        write_json(manifest_path, manifest)
        print(json.dumps(first_result, ensure_ascii=False))
        return evidence_check["exit_code"]

    evidence_check["status"] = "PASS"
    evidence_check["exit_code"] = 0
    evidence_check["reason"] = "check_stage_delivery.py 返回 CHECKS_OK；此结果仅证明本 Run 文件枚举及 SHA-256 包装完整。"
    write_json(manifest_path, manifest)

    inputs_code, inputs_result = run_inputs_check(root, manifest_rel)
    if (
        inputs_code == 0
        or inputs_result.get("status") != "CHECKS_FAILED"
        or inputs_result.get("mode") != "inputs"
    ):
        raise RuntimeError("inputs 核验结果与当前已知 G0 阻塞不符，停止生成最终清单")
    blocker_check = next(
        item for item in manifest["checks"] if item["name"] == "G0 物理接口、UART 与完整器件身份"
    )
    blocker_check["reason"] = (
        f"inputs 核验实测 CHECKS_FAILED，核验器进程退出码 {inputs_code}；"
        f"诊断：{'；'.join(inputs_result.get('errors', []))}。"
        "物理接口候选 s2b-physical-candidate/0.1.1 与 UART 候选 s2bu-candidate/1.1 均未冻结；"
        "芯片照片丝印为 XA7Z020/CLG400，用户转述厂商确认为 XC7Z020-2CLG400I，证据冲突未消解。"
    )
    write_json(manifest_path, manifest)

    final_code, final_result = run_evidence_check(root, manifest_rel)
    if final_code != 0 or final_result.get("status") != "CHECKS_OK":
        evidence_check["status"] = "FAIL"
        evidence_check["exit_code"] = final_code if final_code != 0 else 2
        evidence_check["reason"] = "最终 evidence 清单复核失败；详见生成器标准输出。"
        write_json(manifest_path, manifest)
        print(json.dumps(final_result, ensure_ascii=False))
        return evidence_check["exit_code"]
    print(json.dumps(final_result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
