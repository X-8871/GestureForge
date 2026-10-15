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
INITIALIZER_C = r'''/* 只调用同一固定XSA的PS初始化；所有对象和模式栈必须属于OCM。 */
#include "ps7_init.h"
#include "xil_cache.h"
#include "xil_types.h"
#include "xpseudo_asm.h"
#ifndef SDT
#error "初始化壳要求实际SDT CPU0 BSP"
#endif
#ifdef USE_AMP
#error "初始化壳不支持AMP"
#endif
_Static_assert(sizeof(u32) == 4, "u32 must be 32 bit");
volatile u32 s2b_ps_init_result __attribute__((aligned(64))) = 0U;
volatile int s2b_ps_init_return __attribute__((aligned(64))) = -1;

__attribute__((used, noinline, noreturn)) void s2b_ps_init_ready(void)
{
    /* 独有成功停止点；不加载启动镜像、不配置PL、不释放CPU1。 */
    for (;;) { __asm__ volatile("wfe" ::: "memory"); }
}

__attribute__((used, noinline, noreturn)) void s2b_ps_init_fail(void)
{
    /* 原ps7_init返回码供调试器读取；失败不进入成功停止点。 */
    for (;;) { __asm__ volatile("wfe" ::: "memory"); }
}

int main(void)
{
    u32 mpidr;
    __asm__ volatile("mrc p15, 0, %0, c0, c0, 5" : "=r"(mpidr));
    /* BSP启动只使用OCM；在调用初始化前把OCM脏数据写回并关闭DCache。 */
    Xil_DCacheFlush();
    Xil_DCacheDisable();
    if ((mpidr & 0xFFU) != 0U) {
        s2b_ps_init_result = 0x81U;
        dsb();
        s2b_ps_init_fail();
    }
    s2b_ps_init_result = 1U;
    dsb();
    s2b_ps_init_return = ps7_init();
    if (s2b_ps_init_return != PS7_INIT_SUCCESS) {
        s2b_ps_init_result = 0x82U;
        dsb();
        s2b_ps_init_fail();
    }
    s2b_ps_init_result = 2U;
    dsb();
    s2b_ps_init_ready();
}
'''


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
        # 最小初始化壳与smoke共用实际CPU0域，不加入启动镜像或PCAP库。
        libraries = api_call("domain.get_libs", domain.get_libs)
        require(isinstance(libraries, list), "实际BSP库列表类型不符")
        details["bsp_libraries"] = libraries
        build_status("platform.build", platform.build, platform_pb2.PlatformResponse.DESCRIPTOR)
        platform_root = exact_path(workspace / platform_name, "directory")
        xpfm = unique_file(platform_root, platform_name + ".xpfm")
        bsp_sources = {}
        bsp_origins = {}
        bsp_root = exact_path(platform_root / "ps7_cortexa9_0" / domain_name / "bsp", "directory")
        source_locations = {"xuartps_sinit.c": "libsrc/uartps/src/xuartps_sinit.c",
                            "xuartps_g.c": "libsrc/uartps/src/xuartps_g.c",
                            "xdevcfg.c": "libsrc/devcfg/src/xdevcfg.c",
                            "xiltimer.c": "libsrc/xiltimer/src/xiltimer.c",
                            "globaltimer_sleep_zynq.c": "libsrc/xiltimer/src/core/default_timer/globaltimer_sleep_zynq.c",
                            "xil_cache.c": "libsrc/standalone/src/arm/cortexa9/xil_cache.c"}
        for name in ("xparameters.h", "xparameters_ps.h", "bspconfig.h", "xuartps.h", "xuartps_sinit.c",
                     "xuartps_g.c", "xil_cache.c", "xdevcfg.c", "xdevcfg_hw.h", "xiltimer.c",
                     "globaltimer_sleep_zynq.c", "xtimer_config.h", "xiltimer.h"):
            # include头是实际生成的编译输入；common/src中的空模板不是该BSP头。
            origin = exact_path(bsp_root / source_locations.get(name, "include/" + name), "file")
            bsp_origins[name] = {"path": str(origin), "sha256": sha256(origin)}
            bsp_sources[name] = copy_exclusive(origin, artifact / name)
        details["generated_bsp_sources"] = bsp_origins
        bsp_compile_commands = copy_exclusive(
            exact_path(bsp_root / "libsrc/build_configs/gen_bsp/compile_commands.json", "file"),
            artifact / "bsp_compile_commands.json")
        bsp_specs = copy_exclusive(exact_path(bsp_root / "Xilinx.spec", "file"), artifact / "Xilinx.spec")
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

        # 使用官方OCM链接脚本和同字节初始化来源，生成没有启动器行为的最小调用壳。
        initializer = api_call("client.create_app_component:initializer", client.create_app_component,
                               name="s2b_ps_init", platform=str(xpfm), domain=domain_name, template="empty_application")
        init_root = exact_path(workspace / "s2b_ps_init", "directory")
        sdk_data_alias = Path(os.environ["XILINX_VITIS"]) / "data"
        # 安装程序已有的只读data链接已核实指向版本公共data；不创建任何链接。
        sdk_data = exact_path(sdk_data_alias.resolve(strict=True), "directory")
        require(sdk_data == Path(os.environ["XILINX_VITIS"]).parent / "data",
                "安装data链接目标与已核验版本公共data不同")
        details["installed_sdk_data"] = {"requested": str(sdk_data_alias), "actual_target": str(sdk_data),
                                         "read_only": True, "created_link": False}
        official_ocm_ld = exact_path(sdk_data / "embeddedsw/lib/sw_apps/zynq_fsbl/src/lscript.ld", "file")
        init_source = new_file(artifact / "s2b_ps_init.c")
        with init_source.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(INITIALIZER_C)
        require(api_call("initializer.import_files", initializer.import_files, from_loc=str(artifact),
                         files=["s2b_ps_init.c", "ps7_init.c", "ps7_init.h"], dest_dir_in_cmp="src") is True,
                "最小初始化源码导入失败")
        for name, source in (("s2b_ps_init.c", init_source), ("ps7_init.c", ps_init_sources["ps7_init.c"]),
                             ("ps7_init.h", ps_init_sources["ps7_init.h"])):
            require(sha256(exact_path(init_root / "src" / name, "file")) == sha256(source),
                    f"实际初始化编译来源不符：{name}")
        init_ld = api_call("initializer.get_ld_script", initializer.get_ld_script)
        init_ld_path = exact_path(init_ld.file_path, "file")
        require_under(init_ld_path, workspace)
        copy_exclusive(init_ld_path, artifact / "initializer_default_lscript.ld")
        # 仅替换本次workspace刚生成、已保存原件的ld；官方OCM脚本原字节不改。
        with init_ld_path.open("wb") as stream:
            stream.write(official_ocm_ld.read_bytes())
        require(sha256(init_ld_path) == sha256(official_ocm_ld), "官方OCM脚本复制SHA不符")
        details["initializer_official_linker"] = {"path": str(official_ocm_ld), "sha256": sha256(official_ocm_ld)}
        for key, value in (("USER_COMPILE_OTHER_FLAGS", "-std=gnu11 -Wall -Wextra -ffunction-sections -fdata-sections -save-temps=obj"),
                           ("USER_LINK_OTHER_FLAGS", "-Wl,-Map=s2b_ps_init.map,--cref,--gc-sections")):
            require(api_call("initializer.set_app_config:" + key, initializer.set_app_config, key=key, values=value) is True,
                    f"初始化壳构建配置失败：{key}")
        build_status("initializer.build", initializer.build, build_pb2.BuildResponse.DESCRIPTOR)
        init_elf = copy_exclusive(unique_file(init_root, "s2b_ps_init.elf"), artifact / "s2b_ps_init.elf")
        init_map = copy_exclusive(unique_file(init_root, "s2b_ps_init.map"), artifact / "s2b_ps_init.map")
        init_linker = copy_exclusive(init_ld_path, artifact / "s2b_ps_init.ld")
        init_config = copy_exclusive(unique_file(init_root, "UserConfig.cmake"), artifact / "init_UserConfig.cmake")
        preprocess_dir = new_directory(artifact / "init_preprocessed", artifact)
        init_preprocessed = {}
        for item in sorted(init_root.rglob("*.i")):
            require(item.name in ("s2b_ps_init.c.i", "ps7_init.c.i"), f"初始化壳出现未声明的C编译单元：{item}")
            require(item.name not in init_preprocessed, "初始化预处理单元重复")
            init_preprocessed[item.name] = copy_exclusive(item, preprocess_dir / item.name)
        require(set(init_preprocessed) == {"s2b_ps_init.c.i", "ps7_init.c.i"}, "初始化预处理单元缺失")
        startup = {}
        for name in ("boot.S", "xil-crt0.S", "asm_vectors.S", "cpu_init.S", "translation_table.S"):
            origin = exact_path(bsp_root / "libsrc/standalone/src/arm/cortexa9/gcc" / name, "file")
            startup[name] = copy_exclusive(origin, artifact / ("init_" + name))
        for name, source in (("s2b_ps_init.c", init_source), ("ps7_init.c", ps_init_sources["ps7_init.c"]),
                             ("ps7_init.h", ps_init_sources["ps7_init.h"])):
            require(sha256(exact_path(init_root / "src" / name, "file")) == sha256(source),
                    f"初始化构建期间源文件变更：{name}")
        bound = {"xsa": xsa, "elf": elf, "map": link_map, "linker": linker,
                 "xparameters": bsp_sources["xparameters.h"], "bspconfig": bsp_sources["bspconfig.h"],
                 "cache_source": bsp_sources["xil_cache.c"], "uart_header": bsp_sources["xuartps.h"],
                 "uart_lookup_source": bsp_sources["xuartps_sinit.c"], "uart_config": bsp_sources["xuartps_g.c"],
                 "generated_header": generated_header, "c_source": compiled_source,
                 "init_elf": init_elf, "init_map": init_map, "init_linker": init_linker,
                 "default_linker": artifact / "generated_default_lscript.ld",
                 "init_source": init_source, "init_config": init_config,
                 "init_preprocessed": init_preprocessed["s2b_ps_init.c.i"],
                 "ps_init_preprocessed": init_preprocessed["ps7_init.c.i"],
                 "init_boot": startup["boot.S"], "init_crt": startup["xil-crt0.S"],
                 "init_vectors": startup["asm_vectors.S"], "init_cpu": startup["cpu_init.S"],
                 "init_translation": startup["translation_table.S"],
                 "timer_source": bsp_sources["xiltimer.c"], "timer_backend": bsp_sources["globaltimer_sleep_zynq.c"],
                 "timer_config": bsp_sources["xtimer_config.h"], "timer_header": bsp_sources["xiltimer.h"],
                 "bsp_compile_commands": bsp_compile_commands, "bsp_specs": bsp_specs,
                 "ps_parameters": bsp_sources["xparameters_ps.h"],
                 "ps_init_c": ps_init_sources["ps7_init.c"], "ps_init_h": ps_init_sources["ps7_init.h"]}
        policy = {"ddr_begin": begin, "ddr_end": begin + size, "app_begin": begin, "app_size": APP_SIZE,
                  "app_region": region["name"], "buffer_begin": buffer_begin, "buffer_size": BUFFER_SIZE,
                  "uart_base_macro": uart_macro, "ddr_base_macro": ddr_base_macro, "ddr_high_macro": ddr_high_macro}
        layout_binding = {"schema_version": 1, "hardware_execution": "NOT_RUN", "policy": policy,
                          "init_policy": {"platform_memory_regions": regions, "ready_symbol": "s2b_ps_init_ready",
                                          "fail_symbol": "s2b_ps_init_fail", "strategy": "MINIMAL_OCM_PS7_INIT"},
                          "source_commit": config["source_commit"], "xsa_source_commit": config["xsa_source_commit"],
                          "files": {name: {"path": str(path), "sha256": sha256(path)} for name, path in bound.items()}}
        layout_manifest = artifact / "layout_binding.json"
        readelf_alias = Path(os.environ["XILINX_VITIS"]) / "gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-readelf.exe"
        # 与data相同，gnu是安装程序已有的版本公共工具链接，仅解析只读工具。
        readelf = exact_path(readelf_alias.resolve(strict=True), "file")
        require(readelf == Path(os.environ["XILINX_VITIS"]).parent / "gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-readelf.exe",
                "安装gnu链接目标与已核验的公共工具路径不同")
        details["installed_readelf"] = {"requested": str(readelf_alias), "actual_target": str(readelf),
                                        "sha256": sha256(readelf), "created_link": False}
        gcc = exact_path(readelf.parent / "arm-none-eabi-gcc.exe", "file")
        run_checked([str(gcc), "--version"], workspace, artifact / "gcc_version.log", details["commands"])
        run_checked([str(readelf), "--wide", "--file-header", "--program-headers",
                     "--section-headers", "--symbols", "--arch-specific", str(elf)], workspace,
                    artifact / "readelf.log", details["commands"])
        run_checked([str(readelf), "--wide", "--file-header", "--program-headers",
                     "--section-headers", "--symbols", "--arch-specific", str(init_elf)], workspace,
                    artifact / "init_readelf.log", details["commands"])
        objdump = exact_path(readelf.parent / "arm-none-eabi-objdump.exe", "file")
        run_checked([str(objdump), "-d", str(init_elf)], workspace,
                    artifact / "init_disassembly.log", details["commands"])
        layout_binding["files"]["init_disassembly"] = {
            "path": str(artifact / "init_disassembly.log"), "sha256": sha256(artifact / "init_disassembly.log")}
        write_json(layout_manifest, layout_binding)
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
