#!/usr/bin/env python3
"""使用已绑定的PS-only XSA离线生成CPU0 UART/DDR检查应用。"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import os
import re
import stat
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).absolute().parent.parent


def exact_path(raw: str | Path, kind: str) -> Path:
    """逐分量核对精确名称和类型，拒绝符号链接及重解析点。"""
    path = Path(raw)
    if not path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise ValueError(f"必须使用不含点分量的绝对路径：{raw}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        with os.scandir(current) as entries:
            if not any(entry.name == part for entry in entries):
                raise ValueError(f"精确路径不存在：{current / part}")
        current = current / part
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or (getattr(info, "st_file_attributes", 0) & 0x400):
            raise ValueError(f"拒绝符号链接或重解析点：{current}")
    info = current.lstat()
    if kind == "file" and not stat.S_ISREG(info.st_mode):
        raise ValueError(f"目标不是普通文件：{current}")
    if kind == "directory" and not stat.S_ISDIR(info.st_mode):
        raise ValueError(f"目标不是目录：{current}")
    return current


def new_file(raw: str | Path) -> Path:
    """检查精确父目录和新名称，现有目标一律拒绝覆盖。"""
    path = Path(raw)
    parent = exact_path(path.parent, "directory")
    if not path.name or path.name in {".", ".."}:
        raise ValueError("新文件名无效")
    with os.scandir(parent) as entries:
        if any(entry.name.casefold() == path.name.casefold() for entry in entries):
            raise FileExistsError(f"输出已存在或存在大小写冲突：{path}")
    return parent / path.name


def sha256(path: Path) -> str:
    """对实际文件字节计算SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, data: object) -> None:
    """仅创建UTF-8/LF JSON，不覆盖失败证据。"""
    with new_file(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def api_probe() -> None:
    """只导入安装的API和描述符，不创建客户端、平台或工作区。"""
    import vitis
    from vitis.cli_client import Embedded
    from vitis.component import HostComponent
    from vitis.domain import Domain
    from vitis.ldfile import Ldfile
    from vitis.platform_component import Platform

    targets = [vitis.create_client, vitis.dispose, Embedded.set_workspace,
               Embedded.create_platform_component, Embedded.create_app_component,
               Platform.get_domain, Platform.build, Domain.get_config, Domain.set_config,
               HostComponent.import_files, HostComponent.set_app_config,
               HostComponent.build, HostComponent.get_ld_script,
               Ldfile.get_memory_regions, Ldfile.update_memory_region,
               Ldfile.add_memory_region, Ldfile.set_stack_size, Ldfile.set_heap_size]
    methods = []
    for target in targets:
        path = exact_path(inspect.getsourcefile(target), "file")
        methods.append({"name": target.__qualname__, "signature": str(inspect.signature(target)),
                        "source_path": str(path), "source_sha256": sha256(path),
                        "doc": inspect.getdoc(target)})
    enums = {}
    status_fields = {}
    for module_name in ("build_pb2", "platform_pb2", "workspace_pb2"):
        module = importlib.import_module(module_name)
        for message in module.DESCRIPTOR.message_types_by_name.values():
            field = message.fields_by_name.get("type")
            if field is not None and field.enum_type is not None:
                enums[f"{module_name}.{message.name}.type"] = {
                    item.name: item.number for item in field.enum_type.values}
            field = message.fields_by_name.get("status")
            if field is not None:
                status_fields[f"{module_name}.{message.name}.status"] = {
                    "protobuf_field_type": field.type,
                    "enum_values": None if field.enum_type is None else {
                        item.name: item.number for item in field.enum_type.values}}
    data = {"mode": "READ_ONLY_API_PROBE", "client_created": False,
            "vitis_version_env": os.environ.get("XILINX_VITIS_VERSION"),
            "python_version": sys.version, "methods": methods, "response_type_enums": enums,
            "response_status_fields": status_fields}
    output = os.environ.get("S2B_PS_SMOKE_PROBE_OUTPUT")
    if output:
        write_json(Path(output), data)
    print(json.dumps({key: value for key, value in data.items() if key != "methods"}, ensure_ascii=False, indent=2))
    print("API_PROBE_OK")


def new_directory(path: Path, allowed_parent: Path) -> Path:
    """工作区和产物目录均要求全新名称，失败运行留在原处。"""
    require_under(path, allowed_parent)
    target = new_file(path)
    target.mkdir()
    return exact_path(target, "directory")


def require_under(path: Path, parent: Path) -> None:
    """限制构建写入范围为本仓库的任务缓存和证据目录。"""
    try:
        relative = path.relative_to(parent)
    except ValueError:
        raise ValueError(f"路径不属于授权目录：{path}") from None
    if not relative.parts:
        raise ValueError(f"目标不能是授权目录本身：{path}")


def copy_exclusive(source: Path, destination: Path) -> Path:
    """复制必要证据的原始字节，拒绝覆盖并检查复制后的哈希。"""
    source = exact_path(source, "file")
    destination = new_file(destination)
    with source.open("rb") as reader, destination.open("xb") as writer:
        for block in iter(lambda: reader.read(1024 * 1024), b""):
            writer.write(block)
    if sha256(source) != sha256(destination):
        raise ValueError(f"证据复制哈希不符：{source}")
    return destination


def unique_file(directory: Path, name: str, required_part: str | None = None) -> Path:
    """枚举实际生成名称；多个同名副本只在字节完全相同的情况下接受。"""
    found = [exact_path(item, "file") for item in directory.rglob(name)
             if required_part is None or required_part in item.parts]
    if not found or len({sha256(item) for item in found}) != 1:
        raise ValueError(f"生成文件缺失或存在不同内容的同名候选：{name}：{found}")
    return sorted(found, key=lambda item: (len(item.parts), str(item)))[0]


def run_checked(command: list[str], cwd: Path, log: Path,
                records: list[dict[str, object]]) -> None:
    """记录精确命令、退出码及耗时；非零立即停止并保留日志。"""
    start = time.monotonic()
    result = subprocess.run(command, cwd=cwd, capture_output=True, check=False)
    with new_file(log).open("xb") as stream:
        stream.write(result.stdout)
        stream.write(result.stderr)
    record = {"command": command, "cwd": str(cwd), "exit_code": result.returncode,
              "elapsed_seconds": time.monotonic() - start, "log": str(log), "log_sha256": sha256(log)}
    records.append(record)
    print(json.dumps(record, ensure_ascii=False), flush=True)
    if result.returncode != 0:
        raise RuntimeError(f"命令失败：{command}；日志：{log}")


def build_from_binding() -> None:
    """先核验固定依赖，再在独占workspace创建平台、BSP和真实ARM ELF。"""
    config_path = exact_path(os.environ["S2B_PS_SMOKE_CONFIG"], "file")
    sys.path.insert(0, str(exact_path(PROJECT_ROOT / "verification", "directory")))
    from check_stage_delivery import load_json_strict
    from check_s2b_ps_smoke_layout import APP_SIZE, BUFFER_SIZE, macro_int, require, verify_cache_contract, xsa_metadata

    config = load_json_strict(config_path)
    expected_keys = {"schema_version", "source_commit", "xsa", "xsa_sha256", "xsa_source_commit",
                     "inputs_manifest", "inputs_manifest_sha256", "workspace", "artifact_dir", "command"}
    require(set(config) == expected_keys and config["schema_version"] == 1, "构建配置字段或版本不符")
    for key in ("source_commit", "xsa_source_commit"):
        require(isinstance(config[key], str) and re.fullmatch(r"[0-9a-f]{40}", config[key]) is not None,
                f"必须填写固定Git提交：{key}")
        found = subprocess.run(["git", "cat-file", "-e", config[key] + "^{commit}"],
                               cwd=PROJECT_ROOT, check=False, capture_output=True)
        require(found.returncode == 0, f"固定提交在本仓库不可读取：{key}")
    xsa = exact_path(config["xsa"], "file")
    inputs = exact_path(config["inputs_manifest"], "file")
    require(sha256(xsa) == config["xsa_sha256"] and sha256(inputs) == config["inputs_manifest_sha256"],
            "固定XSA或inputs清单SHA-256不符")
    input_data = load_json_strict(inputs)
    xsa_relative = xsa.relative_to(PROJECT_ROOT).as_posix()
    require(any(item.get("path") == xsa_relative and item.get("sha256") == config["xsa_sha256"] and
                item.get("role") == "input" for item in input_data["files"]), "inputs未绑定同一XSA")
    require(input_data["source_commit"] == config["source_commit"], "inputs源码基线与构建配置不同")
    workspace = Path(config["workspace"])
    artifact = Path(config["artifact_dir"])
    cache_base = exact_path(PROJECT_ROOT / "tmp" / "2B" / "S2B-T06", "directory")
    evidence_base = exact_path(PROJECT_ROOT / "report" / "evidence" / "S2B-T06", "directory")
    require_under(workspace, cache_base)
    require_under(artifact, evidence_base)
    new_file(workspace)
    new_file(artifact)
    source_paths = [exact_path(PROJECT_ROOT / part, "file") for part in
                    ("vitis/s2b_ps_smoke.c", "vitis/build_s2b_ps_smoke.py",
                     "verification/check_s2b_ps_smoke_layout.py", "verification/check_stage_delivery.py")]
    source_hashes = {str(path): sha256(path) for path in source_paths}
    artifact = new_directory(artifact, evidence_base)
    started = time.monotonic()
    details: dict[str, object] = {"schema_version": 1, "status": "FAIL", "hardware_execution": "NOT_RUN",
                                  "config": config, "config_sha256": sha256(config_path),
                                  "source_sha256": source_hashes, "commands": [], "api_calls": [],
                                  "attempts": 1, "peak_memory_bytes": None,
                                  "peak_memory_reason": "未测量整个Vitis及其子进程树的峰值内存"}
    details["started_at_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    client_created = False
    try:
        snapshot_dir = new_directory(artifact / "source_snapshot", artifact)
        details["source_snapshot"] = {}
        for path in source_paths:
            copied = copy_exclusive(path, snapshot_dir / path.name)
            details["source_snapshot"][str(path)] = {"path": str(copied), "sha256": sha256(copied)}
        run_checked(
            [sys.executable, "-B", str(PROJECT_ROOT / "verification/check_stage_delivery.py"),
             "--mode", "inputs", "--manifest", str(inputs)], PROJECT_ROOT,
            artifact / "inputs_check.log", details["commands"])
        metadata = xsa_metadata(xsa)
        details["xsa_metadata"] = metadata
        # 原样留存固定XSA的初始化成员；构建过程不导入或执行任何初始化代码。
        ps_init_sources = {}
        with zipfile.ZipFile(xsa) as archive:
            for name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl"):
                members = [item for item in archive.namelist() if item.split("/")[-1] == name]
                require(len(members) == 1, f"固定XSA必须唯一包含初始化来源：{name}")
                require(archive.getinfo(members[0]).file_size < 2 * 1024 * 1024, "初始化来源超出读取预算")
                destination = new_file(artifact / name)
                with destination.open("xb") as stream:
                    stream.write(archive.read(members[0]))
                ps_init_sources[name] = destination
            details["ps7_init_sources"] = {name: {"path": str(path), "sha256": sha256(path), "executed": False}
                                           for name, path in ps_init_sources.items()}
        version = os.environ.get("XILINX_VITIS_VERSION", "")
        require("v2026.1" in version, "必须通过本机Vitis 2026.1 CLI运行")
        import vitis
        import build_pb2
        import platform_pb2

        def api_call(label: str, function: object, *args: object, **kwargs: object) -> object:
            call_start = time.monotonic()
            record = {"name": label, "args": [repr(item) for item in args],
                      "kwargs": {key: repr(value) for key, value in kwargs.items()}}
            details["api_calls"].append(record)
            try:
                response = function(*args, **kwargs)
                record.update(return_type=type(response).__name__, return_repr=repr(response))
                return response
            except Exception as error:
                record["error"] = f"{type(error).__name__}: {error}"
                raise
            finally:
                record["elapsed_seconds"] = time.monotonic() - call_start
                print(json.dumps(record, ensure_ascii=False), flush=True)

        def build_status(name: str, function: object, descriptor: object) -> None:
            response = api_call(name, function)
            expected = descriptor.fields_by_name["type"].enum_type.values_by_name["SUCCESS"].number
            require(type(response) is int and response == expected,
                    f"{name}未返回实际protobuf SUCCESS={expected}：{response!r}")

        workspace = new_directory(workspace, cache_base)
        # 新CLI进程使用默认空端口创建自己的server，不连接已有IDE/server。
        client = api_call("vitis.create_client", vitis.create_client, workspace=str(workspace))
        client_created = True
        require(client._serverObj.cp is not None, "未创建本次独占Vitis server")
        details["own_server_pid"] = client._serverObj.cp.pid
        require(api_call("client.set_workspace", client.set_workspace, path=str(workspace)) is True,
                "工作区配置失败")
        # 深层CMake临时文件受Windows工具路径长度限制，组件名称保留简短明确。
        platform_name = "ps7"
        domain_name = "cpu0"
        platform = api_call("client.create_platform_component", client.create_platform_component,
                            name=platform_name, hw_design=str(xsa), cpu="ps7_cortexa9_0", os="standalone",
                            domain_name=domain_name, no_boot_bsp=True, generate_dtb=False)
        domain = api_call("platform.get_domain", platform.get_domain, name=domain_name)
        for param in ("standalone_stdin", "standalone_stdout"):
            require(api_call("domain.set_config:" + param, domain.set_config,
                             "os", param, "ps7_uart_1") is True, f"BSP配置失败：{param}")
            actual = api_call("domain.get_config:" + param, domain.get_config, "os", param)
            require(isinstance(actual, dict) and actual.get("value") == "ps7_uart_1",
                    f"BSP配置回读不符：{param}：{actual!r}")
        # 官方zynq_fsbl模板要求这三项库；仍使用同一CPU0 standalone域。
        libraries = api_call("domain.get_libs", domain.get_libs)
        require(isinstance(libraries, list), "实际BSP库列表类型不符")
        for name in ("xiltimer", "xilffs", "xilrsa"):
            if not any(item.get("name") == name for item in libraries):
                require(api_call("domain.set_lib:" + name, domain.set_lib, lib_name=name) is True,
                        f"官方初始化库配置失败：{name}")
        libraries = api_call("domain.get_libs:readback", domain.get_libs)
        require(all(any(item.get("name") == name for item in libraries)
                    for name in ("xiltimer", "xilffs", "xilrsa")), "官方初始化库配置回读不符")
        details["bsp_libraries"] = libraries
        build_status("platform.build", platform.build, platform_pb2.PlatformResponse.DESCRIPTOR)
        platform_root = exact_path(workspace / platform_name, "directory")
        xpfm = unique_file(platform_root, platform_name + ".xpfm")
        bsp_sources = {}
        bsp_origins = {}
        for name in ("xparameters.h", "xparameters_ps.h", "bspconfig.h", "xuartps.h", "xuartps_sinit.c",
                     "xuartps_g.c", "xil_cache.c", "xdevcfg.c", "xdevcfg_hw.h"):
            origin = unique_file(platform_root, name, "cortexa9" if name == "xil_cache.c" else None)
            bsp_origins[name] = {"path": str(origin), "sha256": sha256(origin)}
            bsp_sources[name] = copy_exclusive(origin, artifact / name)
        details["generated_bsp_sources"] = bsp_origins
        xparams = bsp_sources["xparameters.h"].read_text(encoding="utf-8")
        candidates = re.findall(r"^\s*#define\s+(XPAR_XUARTPS_[0-9]+_BASEADDR)\s+", xparams, re.MULTILINE)
        candidates = [name for name in candidates if macro_int(xparams, name) == metadata["uart1_base"]]
        require(len(candidates) == 1, "实际BSP的UART1 canonical基地址宏不唯一")
        uart_macro = candidates[0]
        ddr_macros = re.findall(r"^\s*#define\s+(XPAR_[A-Z0-9_]*DDR[A-Z0-9_]*_BASEADDRESS)\s+", xparams, re.MULTILINE)
        ddr_macros = [name for name in ddr_macros if macro_int(xparams, name) == metadata["ddr_begin"] and
                      macro_int(xparams, name.removesuffix("BASEADDRESS") + "HIGHADDRESS") == metadata["ddr_end"] - 1]
        require(len(ddr_macros) == 1, "实际BSP与XSA的DDR范围宏不唯一或不符")
        ddr_base_macro = ddr_macros[0]
        ddr_high_macro = ddr_base_macro.removesuffix("BASEADDRESS") + "HIGHADDRESS"
        bspconfig = bsp_sources["bspconfig.h"].read_text(encoding="utf-8")
        require(all(macro_int(bspconfig, name) == metadata["uart1_base"] for name in
                    ("STDIN_BASEADDRESS", "STDOUT_BASEADDRESS")), "实际生成stdin/stdout基地址不符")
        cache_text = bsp_sources["xil_cache.c"].read_text(encoding="utf-8")
        verify_cache_contract(cache_text)
        app = api_call("client.create_app_component", client.create_app_component,
                       name="s2b_ps_smoke", platform=str(xpfm), domain=domain_name, template="empty_application")
        require(api_call("app.import_files", app.import_files, from_loc=str(PROJECT_ROOT / "vitis"),
                         files=["s2b_ps_smoke.c"], dest_dir_in_cmp="src") is True, "应用源码导入失败")
        ld = api_call("app.get_ld_script", app.get_ld_script)
        ld_path = exact_path(ld.file_path, "file")
        require_under(ld_path, workspace)
        copy_exclusive(ld_path, artifact / "generated_default_lscript.ld")
        require(api_call("ld.set_stack_size", ld.set_stack_size, "0x4000") is True, "stack配置失败")
        require(api_call("ld.set_heap_size", ld.set_heap_size, "0x4000") is True, "heap配置失败")
        regions = api_call("ld.get_memory_regions", ld.get_memory_regions)
        details["generated_linker_memory_regions"] = regions
        ddr_regions = [item for item in regions if "ddr" in item["name"].lower()]
        require(len(ddr_regions) == 1, "实际linker的DDR区域不唯一")
        region = ddr_regions[0]
        begin = int(region["base_address"], 0)
        size = int(region["size"], 0)
        require(begin == metadata["ddr_begin"] and begin + size == metadata["ddr_end"],
                "实际生成linker DDR区域与固定XSA不符")
        buffer_begin = begin + APP_SIZE
        buffer_end = buffer_begin + BUFFER_SIZE
        require(begin > 0 and buffer_begin % 64 == 0 and buffer_end <= begin + size and buffer_end < 0x100000000,
                "DDR专属分区空间不足或溢出")
        require(api_call("ld.update_memory_region", ld.update_memory_region,
                         name=region["name"], base_address=hex(begin), size=hex(APP_SIZE)) is True,
                "应用DDR分区失败")
        require(api_call("ld.add_memory_region", ld.add_memory_region,
                         name="s2b_smoke_ddr", base_address=hex(buffer_begin), size=hex(BUFFER_SIZE)) is True,
                "buffer DDR分区失败")
        text = ld_path.read_text(encoding="utf-8")
        require(".s2b_smoke_buffer" not in text and "SECTIONS" in text and text.rstrip().endswith("}"),
                "生成链接脚本结构不符")
        closing = text.rfind("}")
        extra = """\n/* 此节只属于PS smoke对象，位于独占DDR分区且不由启动.bss清零。 */
.s2b_smoke_buffer (NOLOAD) : ALIGN(64) {
    __s2b_smoke_buffer_start = .;
    KEEP(*(.s2b_smoke_buffer))
    __s2b_smoke_buffer_end = .;
} > s2b_smoke_ddr
"""
        text = text[:closing] + extra + text[closing:]
        text += '\nASSERT(SIZEOF(.s2b_smoke_buffer) == 0x100000, "S2B buffer size")\n'
        text += 'ASSERT((ADDR(.s2b_smoke_buffer) & 63) == 0, "S2B buffer alignment")\n'
        # 仅覆盖本次新workspace中由本脚本刚生成、已留存原始副本的链接脚本。
        exact_path(ld_path, "file")
        with ld_path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        source_root = exact_path(workspace / "s2b_ps_smoke" / "src", "directory")
        imported_source = exact_path(source_root / "s2b_ps_smoke.c", "file")
        require(sha256(imported_source) == source_hashes[str(source_paths[0])], "实际编译源码副本SHA-256不符")
        header = new_file(source_root / "s2b_smoke_platform.h")
        with header.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write("/* 从实际固定XSA、BSP和链接分区生成，禁止手填物理地址。 */\n")
            stream.write("#ifndef S2B_SMOKE_PLATFORM_H\n#define S2B_SMOKE_PLATFORM_H\n")
            stream.write(f"#define S2B_UART1_BASE {uart_macro}\n#define S2B_BSP_CACHELINE_BYTES 32U\n")
            stream.write(f'#define S2B_C_SOURCE_SHA256 "{source_hashes[str(source_paths[0])]}"\n')
            stream.write(f'#define S2B_XSA_SHA256 "{config["xsa_sha256"]}"\n')
            stream.write(f"#define S2B_BUFFER_BEGIN 0x{buffer_begin:08X}U\n#define S2B_BUFFER_END 0x{buffer_end:08X}U\n#endif\n")
        for key, value in (("USER_COMPILE_OTHER_FLAGS", "-std=gnu11 -Wall -Wextra -Werror"),
                           ("USER_LINK_OTHER_FLAGS", "-Wl,-Map=s2b_ps_smoke.map,--cref")):
            require(api_call("app.set_app_config:" + key, app.set_app_config, key=key, values=value) is True,
                    f"应用构建配置失败：{key}")
        build_status("app.build", app.build, build_pb2.BuildResponse.DESCRIPTOR)
        require(sha256(imported_source) == source_hashes[str(source_paths[0])], "编译期间应用源码副本发生变更")
        elf = copy_exclusive(unique_file(workspace / "s2b_ps_smoke", "s2b_ps_smoke.elf"), artifact / "s2b_ps_smoke.elf")
        link_map = copy_exclusive(unique_file(workspace / "s2b_ps_smoke", "s2b_ps_smoke.map"), artifact / "s2b_ps_smoke.map")
        linker = copy_exclusive(ld_path, artifact / "lscript.ld")
        generated_header = copy_exclusive(header, artifact / "s2b_smoke_platform.h")
        compiled_source = copy_exclusive(imported_source, artifact / "s2b_ps_smoke.c")

        # 无ps7_init.py时按本机官方模板生成OCM初始化ELF；这里只编译，不执行。
        fsbl = api_call("client.create_app_component:fsbl", client.create_app_component,
                        name="s2b_ps_init", platform=str(xpfm), domain=domain_name, template="zynq_fsbl")
        fsbl_root = exact_path(workspace / "s2b_ps_init", "directory")
        sdk_fsbl = exact_path(Path(os.environ["XILINX_VITIS"]) / "data/embeddedsw/lib/sw_apps/zynq_fsbl/src", "directory")
        fsbl_sources = {}
        fsbl_origins = {}
        for name in ("main.c", "fsbl.h", "fsbl_debug.h", "fsbl_hooks.c", "fsbl_hooks.h",
                     "pcap.c", "pcap.h", "fsbl_handoff.S"):
            origin = unique_file(fsbl_root, name)
            sdk_origin = exact_path(sdk_fsbl / name, "file")
            require(sha256(origin) == sha256(sdk_origin), f"实际FSBL源码与官方模板不同：{name}")
            fsbl_origins[name] = {"path": str(origin), "sdk_path": str(sdk_origin), "sha256": sha256(origin)}
            fsbl_sources[name] = copy_exclusive(origin, artifact / ("fsbl_" + name))
        for name in ("ps7_init.c", "ps7_init.h"):
            origin = unique_file(fsbl_root, name)
            require(sha256(origin) == sha256(ps_init_sources[name]), f"FSBL初始化来源与固定XSA不同：{name}")
            fsbl_origins[name] = {"path": str(origin), "sha256": sha256(origin), "same_fixed_xsa": True}
        fsbl_ld = api_call("fsbl.get_ld_script", fsbl.get_ld_script)
        fsbl_ld_path = exact_path(fsbl_ld.file_path, "file")
        require_under(fsbl_ld_path, workspace)
        require(sha256(fsbl_ld_path) == sha256(exact_path(sdk_fsbl / "lscript.ld", "file")),
                "实际FSBL链接脚本必须保持官方OCM模板原字节")
        for key, value in (("USER_COMPILE_OTHER_FLAGS", "-save-temps=obj -UPS7_POST_CONFIG -UJTAG_ENABLE_LEVEL_SHIFTERS"),
                           ("USER_LINK_OTHER_FLAGS", "-Wl,-Map=s2b_ps_init.map,--cref")):
            require(api_call("fsbl.set_app_config:" + key, fsbl.set_app_config, key=key, values=value) is True,
                    f"官方FSBL构建配置失败：{key}")
        build_status("fsbl.build", fsbl.build, build_pb2.BuildResponse.DESCRIPTOR)
        elf_candidates = list(fsbl_root.rglob("*.elf"))
        require(len(elf_candidates) == 1, f"官方初始化ELF必须唯一：{elf_candidates}")
        fsbl_elf = copy_exclusive(elf_candidates[0], artifact / "s2b_ps_init.elf")
        fsbl_map = copy_exclusive(unique_file(fsbl_root, "s2b_ps_init.map"), artifact / "s2b_ps_init.map")
        fsbl_linker = copy_exclusive(fsbl_ld_path, artifact / "fsbl_lscript.ld")
        preprocessed = [item for item in fsbl_root.rglob("*.i") if item.name in ("main.i", "main.c.i")]
        require(len(preprocessed) == 1, f"实际FSBL main预处理结果必须唯一：{preprocessed}")
        fsbl_main_preprocessed = copy_exclusive(preprocessed[0], artifact / "fsbl_main.i")
        fsbl_config = copy_exclusive(unique_file(fsbl_root, "UserConfig.cmake"), artifact / "fsbl_UserConfig.cmake")
        details["generated_fsbl_sources"] = fsbl_origins
        bound = {"xsa": xsa, "elf": elf, "map": link_map, "linker": linker,
                 "xparameters": bsp_sources["xparameters.h"], "bspconfig": bsp_sources["bspconfig.h"],
                 "cache_source": bsp_sources["xil_cache.c"], "uart_header": bsp_sources["xuartps.h"],
                 "uart_lookup_source": bsp_sources["xuartps_sinit.c"], "uart_config": bsp_sources["xuartps_g.c"],
                 "generated_header": generated_header, "c_source": compiled_source,
                 "fsbl_elf": fsbl_elf, "fsbl_map": fsbl_map, "fsbl_linker": fsbl_linker,
                 "default_linker": artifact / "generated_default_lscript.ld",
                 "fsbl_main_preprocessed": fsbl_main_preprocessed, "fsbl_config": fsbl_config,
                 "fsbl_hooks": fsbl_sources["fsbl_hooks.c"], "fsbl_pcap": fsbl_sources["pcap.c"],
                 "fsbl_handoff": fsbl_sources["fsbl_handoff.S"],
                 "devcfg_source": bsp_sources["xdevcfg.c"], "devcfg_hw": bsp_sources["xdevcfg_hw.h"],
                 "ps_parameters": bsp_sources["xparameters_ps.h"],
                 "ps_init_c": ps_init_sources["ps7_init.c"], "ps_init_h": ps_init_sources["ps7_init.h"]}
        policy = {"ddr_begin": begin, "ddr_end": begin + size, "app_begin": begin, "app_size": APP_SIZE,
                  "app_region": region["name"], "buffer_begin": buffer_begin, "buffer_size": BUFFER_SIZE,
                  "uart_base_macro": uart_macro, "ddr_base_macro": ddr_base_macro, "ddr_high_macro": ddr_high_macro}
        layout_binding = {"schema_version": 1, "hardware_execution": "NOT_RUN", "policy": policy,
                          "fsbl_policy": {"platform_memory_regions": regions, "ready_symbol": "FsblHandoffJtagExit"},
                          "source_commit": config["source_commit"], "xsa_source_commit": config["xsa_source_commit"],
                          "files": {name: {"path": str(path), "sha256": sha256(path)} for name, path in bound.items()}}
        layout_manifest = artifact / "layout_binding.json"
        write_json(layout_manifest, layout_binding)
        readelf = exact_path(Path(os.environ["XILINX_VITIS"]) / "gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-readelf.exe", "file")
        gcc = exact_path(readelf.parent / "arm-none-eabi-gcc.exe", "file")
        run_checked([str(gcc), "--version"], workspace, artifact / "gcc_version.log", details["commands"])
        run_checked([str(readelf), "--wide", "--file-header", "--program-headers",
                     "--section-headers", "--symbols", "--arch-specific", str(elf)], workspace,
                    artifact / "readelf.log", details["commands"])
        run_checked([str(readelf), "--wide", "--file-header", "--program-headers",
                     "--section-headers", "--symbols", "--arch-specific", str(fsbl_elf)], workspace,
                    artifact / "fsbl_readelf.log", details["commands"])
        objdump = exact_path(readelf.parent / "arm-none-eabi-objdump.exe", "file")
        run_checked([str(objdump), "-d", str(fsbl_elf)], workspace,
                    artifact / "fsbl_disassembly.log", details["commands"])
        run_checked([sys.executable, "-B", str(PROJECT_ROOT / "verification/check_s2b_ps_smoke_layout.py"),
                     "--manifest", str(layout_manifest), "--self-test"], PROJECT_ROOT,
                    artifact / "layout_check.json", details["commands"])
        require(all(sha256(Path(path)) == digest for path, digest in source_hashes.items()), "构建过程中被审源码发生变化")
        require(sha256(xsa) == config["xsa_sha256"] and sha256(inputs) == config["inputs_manifest_sha256"], "构建期间依赖变更")
        details["status"] = "PASS_OFFLINE_BUILD_AND_LAYOUT"
        details["vitis_version"] = version
        details["files"] = layout_binding["files"]
        details["policy"] = policy
        print("S2B_PS_SMOKE_BUILD_OK hardware_execution=NOT_RUN", flush=True)
    except Exception as error:
        details["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        cleanup_error = None
        try:
            if client_created:
                vitis.dispose()
                details["own_server_cleanup"] = "DISPOSE_CALLED"
        except Exception as error:
            cleanup_error = error
            details["cleanup_error"] = f"{type(error).__name__}: {error}"
            details["status"] = "FAIL"
        finally:
            details["elapsed_seconds"] = time.monotonic() - started
            details["finished_at_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
            details["api_call_count"] = len(details["api_calls"])
            details["command_count"] = len(details["commands"])
            write_json(artifact / "build_details.json", details)
        if cleanup_error is not None:
            raise RuntimeError("本次独占Vitis server清理失败，详见保留的构建记录") from cleanup_error


def main() -> int:
    """构建须显式选择模式；缺少冻结配置时拒绝创建任何平台。"""
    os.environ["PYTHONUTF8"] = "1"
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    mode = os.environ.get("S2B_PS_SMOKE_MODE", "")
    if mode == "probe":
        api_probe()
        return 0
    if mode == "build":
        build_from_binding()
        return 0
    raise ValueError("必须显式选择S2B_PS_SMOKE_MODE=probe或build；build另需已审冻结配置")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"S2B_PS_SMOKE_BUILD_FAIL: {type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
