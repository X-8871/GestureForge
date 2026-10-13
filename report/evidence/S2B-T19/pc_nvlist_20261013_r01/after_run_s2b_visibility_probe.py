"""T19候选visibility0入口；导入/--help不加载SDK或串口，run(config)才执行。

实际入口为Vitis2026.1 vitis.bat -s本文件，显式设置S2B_VISIBILITY_PROBE_CONFIG。
config的compat_review必须由总控固定独立Reviewer真实原件；role/PASS字符串
本身不能证明独立来源。本工具保存原始观察，不发布visibility或冷生命周期PASS。
"""
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import ast
import hashlib
import importlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).absolute().parents[1]
TZ=timezone(timedelta(hours=8))
SDK_INIT=Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\__init__.py")
# 固定T16 EOS→生成postconfig→冷CSR候选；此绑定不替代独立G2及实板兼容批准。
JTAG_SHA="4f69f848f71acb4b2ff7709a4ab40bbb892f0b205137d434f7a5f302805e1f85"
CONFIG_KEYS={"schema_version","source_commit","run_dir","build_details","bindings","compat_review","cold_basis",
             "owned_hw_server_identity","uart_identity","cpu_seed","dap_seed","response_timeout_seconds","pyserial_files","sdk_files"}
ARTIFACT_KEYS={"compiled_xsa","implemented_xsa","init_elf","app_elf","bit","build_details","platform_manifest"}
COMPAT_CHECKS={"same_ps7_config","same_ps_init_bytes","same_bsp_mmu_macros","same_uart_ddr_csr_clocks","full_model_core_present","postroute_timing_pass"}

class VisibilityProbeError(RuntimeError):
    """门禁、真实操作或清理失败，运行证据仍保留。"""

def require(condition,message):
    """不能被python -O移除的门禁。"""
    if not condition:raise VisibilityProbeError(message)

def strict_json(raw):
    """全部对象包括嵌套对象拒重复键；非标准常量不能被静默消费。"""
    def pairs(items):
        result={}
        for key,value in items:
            require(key not in result,"JSON重复键："+key)
            if key=="schema_version":require(type(value) is int,"schema_version必须为整数，bool拒绝")
            result[key]=value
        return result
    def constant(value):
        raise VisibilityProbeError("JSON非标准常量："+value)
    try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
    except (ValueError,UnicodeError,RecursionError) as error:raise VisibilityProbeError("JSON原字节无效") from error

def bound_json(item,j,label,record):
    """解析前保存原字节，重复前置核查不能覆盖已有输入快照。"""
    path=j.exact_path(item["path"]);require(path.stat().st_size<=1048576,"JSON输入超过1MiB："+label)
    raw=j.bound_bytes(item)
    row={"binding":item,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
    if "raw_input_dir" in record:
        target=Path(record["raw_input_dir"])/("bound_"+label+".json.raw")
        if target.exists():require(target.is_file() and target.read_bytes()==raw,"重复核查输入漂移："+label)
        else:
            with target.open("xb") as out:out.write(raw)
        row["saved_path"]=str(target)
    else:row["raw_hex"]=raw.hex()
    record.setdefault("raw_json_inputs",{})[label]=row
    return strict_json(raw.decode("utf-8-sig"))

def sdk_source_closure():
    """只读AST闭包；包含导入链及TCF官方动态服务工厂可能加载的代理。"""
    cli=SDK_INIT.parent.parent;product=cli.parent
    roots=[cli,cli/"python-packages/site-packages",cli/"python-packages/win64",product/"scripts/python_pkg"]
    native={name:product/"lib/win64.o"/(name+".pyd") for name in ("xv_pycommontasks","xv_hsmpytasks")}
    def resolve(name):
        if name in native:return native[name] if native[name].is_file() else None
        for root in roots:
            file=root.joinpath(*name.split("."))
            for candidate in (file.with_suffix(".py"),file/"__init__.py"):
                if candidate.is_file() and any(row.name==candidate.name for row in candidate.parent.iterdir()):return candidate.absolute()
        return None
    pending=["xsdb","xsdb.xsdb_debug_session","xsdb.session","xsdb.target","xsdb._tcf_reset","hsi",*native]
    remote=cli/"tcf/services/remote";require(remote.is_dir(),"TCF服务代理工厂目录缺失")
    pending.append("tcf.services.remote")
    for file in remote.glob("*Proxy.py"):
        pending.append("tcf.services.remote."+file.stem)
    result={}
    while pending:
        name=pending.pop()
        if name in result:continue
        file=resolve(name)
        if file is None:continue
        require(len(result)<512 and file.stat().st_size<=8*1024*1024,"SDK源码闭包超过轻量预算："+name)
        result[name]=file
        parts=name.split(".")
        pending.extend(".".join(parts[:i]) for i in range(1,len(parts)))
        if file.suffix!=".py":continue
        package=name if file.name=="__init__.py" else name.rpartition(".")[0]
        for node in ast.walk(ast.parse(file.read_text(encoding="utf-8-sig"),filename=str(file))):
            if isinstance(node,ast.Import):pending.extend(alias.name for alias in node.names)
            elif isinstance(node,ast.ImportFrom):
                if node.level:
                    base=importlib.util.resolve_name("."*node.level+(node.module or ""),package)
                else:base=node.module or ""
                if base:pending.append(base)
                pending.extend(base+"."+alias.name for alias in node.names if base and alias.name!="*")
    require(all(name in result for name in ("xsdb","xsdb.xsdb_debug_session","xsdb.session","xsdb.target","xsdb._tcf_reset",*native)),"关键SDK实现缺失")
    require(sum(file.stat().st_size for file in result.values())<=32*1024*1024,"SDK源码总量超过轻量预算")
    return dict(sorted(result.items()))

def _loaded_native_images(names):
    """只读本进程已加载映像；不加载DLL，不创建SDK会话。"""
    require(os.name=="nt","官方原生模块映像核验要求Windows")
    import ctypes
    kernel=ctypes.WinDLL("kernel32",use_last_error=True)
    kernel.GetModuleHandleW.argtypes=[ctypes.c_wchar_p];kernel.GetModuleHandleW.restype=ctypes.c_void_p
    kernel.GetModuleFileNameW.argtypes=[ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_ulong]
    kernel.GetModuleFileNameW.restype=ctypes.c_ulong
    rows={}
    for name in names:
        handle=kernel.GetModuleHandleW(name+".pyd")
        require(bool(handle),"本进程未加载必需原生映像："+name)
        buffer=ctypes.create_unicode_buffer(32768)
        length=kernel.GetModuleFileNameW(handle,buffer,len(buffer))
        require(0<length<len(buffer),"原生映像路径查询失败或截断："+name)
        rows[name]={"handle":handle,"path":buffer.value}
    require(len({row["handle"] for row in rows.values()})==len(rows),"两个官方原生文件必须为不同已加载映像")
    return rows

def verify_sdk_files(config):
    """配置文件声明的SDK闭包在真实导入前完整核验；共用于preflight与runtime。"""
    j,_=helpers();sdk_files=config["sdk_files"];closure=sdk_source_closure();paths=[]
    require(type(sdk_files) is dict and set(sdk_files)==set(closure),"SDK源码闭包缺项/多项")
    for name,path in closure.items():
        item=sdk_files[name]
        require(type(item) is dict and set(item)=={"path","sha256"},"SDK源码绑定格式错误")
        require(j.exact_path(item["path"])==j.exact_path(path),"SDK源码路径或接收器漂移："+name)
        j.bound_bytes(item);paths.append(item["path"])
    require(len(paths)==len(set(paths)),"SDK源码路径重复")
    require(sdk_files["xsdb"]==config["bindings"]["sdk_init"] and sdk_files["xsdb.target"]==config["bindings"]["sdk_target"],"SDK入口绑定不一致")
    return sdk_files

def verify_serial_files(config):
    """已绑定pyserial纯Python包逐文件核验，导入前不能只检查入口。"""
    j,_=helpers();package=j.exact_path(config["bindings"]["pyserial_init"]["path"])
    require(package.name=="__init__.py" and package.parent.name=="serial","pyserial入口路径错误")
    j.bound_bytes(config["bindings"]["pyserial_init"])
    serial_files=config["pyserial_files"]
    require(type(serial_files) is list and serial_files and len(serial_files)<=100,"pyserial闭包清单错误")
    actual_files=set()
    for file in package.parent.rglob("*.py"):
        require(len(actual_files)<100,"pyserial目录超过声明规模")
        actual_files.add(str(j.exact_path(file)))
    listed=[]
    for item in serial_files:
        j.bound_bytes(item);listed.append(str(j.exact_path(item["path"])))
    require(len(listed)==len(set(listed)) and set(listed)==actual_files,"pyserial purePython包闭包不完整/重复")
    return serial_files

def verify_native_alias(expected):
    """精确绑定官方2026.1共享vivado对象及两个不同物理映像。"""
    j,_=helpers();names=("xv_pycommontasks","xv_hsmpytasks")
    require(all(name in expected and name in sys.modules for name in names),"官方原生模块声明或加载缺失")
    module=sys.modules[names[0]]
    require(module is sys.modules[names[1]] and module.__name__=="vivado","官方原生共享对象/名称不同")
    final=j.exact_path(SDK_INIT.parent.parent.parent/"lib/win64.o/xv_hsmpytasks.pyd")
    spec=getattr(module,"__spec__",None);loader=getattr(spec,"loader",None)
    require(spec is not None and spec.name==names[1] and type(loader) is importlib.machinery.ExtensionFileLoader,"官方原生模块规格/加载器不同")
    require(loader.name==names[1] and all(j.exact_path(path)==final for path in (module.__file__,spec.origin,loader.path)),"官方原生模块元数据来源不同")
    images=_loaded_native_images(names);observed={}
    for name in names:
        fixed=j.exact_path(SDK_INIT.parent.parent.parent/"lib/win64.o"/(name+".pyd"))
        require(j.exact_path(expected[name]["path"])==fixed and j.exact_path(images[name]["path"])==fixed,"实际原生映像物理来源不同："+name)
        j.bound_bytes(expected[name])
        observed[name]={"path":str(fixed),"sha256":expected[name]["sha256"],"handle":images[name]["handle"],
                        "module_name":module.__name__,"metadata_path":str(final),"spec_name":spec.name,"shared_object":True}
    return observed

def verify_runtime_sources(config,session=None,target=None):
    """在建立会话前核验实际模块与方法实现；调用阶段检查新增动态模块。"""
    j,_=helpers();expected=config["sdk_files"]
    required={"xsdb","xsdb.xsdb_debug_session","xsdb.session","xsdb.target","xsdb._tcf_reset"}
    require(required<=set(sys.modules),"实际SDK关键模块未加载")
    roots=[SDK_INIT.parent.parent,SDK_INIT.parent.parent.parent/"scripts/python_pkg",SDK_INIT.parent.parent.parent/"lib/win64.o"]
    observed=verify_native_alias(expected)
    for name,module in list(sys.modules.items()):
        file=getattr(module,"__file__",None)
        if not file:continue
        actual=Path(file).absolute()
        controlled=name.startswith(("xsdb.","tcf.")) or name in expected or any(actual.is_relative_to(root) for root in roots)
        if not controlled:continue
        if name in ("xv_pycommontasks","xv_hsmpytasks"):continue
        require(name in expected,"运行SDK模块未声明："+name)
        require(j.exact_path(file)==j.exact_path(expected[name]["path"]),"实际SDK模块来源漂移："+name)
        j.bound_bytes(expected[name]);observed[name]={"path":str(j.exact_path(file)),"sha256":expected[name]["sha256"]}
    implementations={"xsdb":("start_debug_session","dispose"),"xsdb.xsdb_debug_session":("xsdb_start_debug_session","dispose_session"),
                     "xsdb.session":("Session.__init__","Session.connect","Session.disconnect","Session.targets"),
                     "xsdb.target":("Target.__init__","Target.state","Target.stop","Target.con","Target.dow","Target.bpadd","Target.mrd","Target.mwr","Target.rst","Target.fpga","Target.rrd","Target.loadhw","Target.unloadhw"),
                     "xsdb._tcf_reset":("TcfReset.rst_cmd","TcfReset.rst_capabilities"),"xsdb._breakpoint":("Breakpoint.remove","Breakpoint.status")}
    require(set(implementations)<=set(sys.modules),"实际调用实现模块未加载")
    def code_by_name(code,name):
        if code.co_qualname==name:return code
        for child in code.co_consts:
            if hasattr(child,"co_code"):
                found=code_by_name(child,name)
                if found is not None:return found
    for module,names in implementations.items():
        source=j.exact_path(expected[module]["path"])
        canonical=compile(source.read_text(encoding="utf-8-sig"),str(source),"exec",dont_inherit=True)
        for name in names:
            value=sys.modules[module]
            for part in name.split("."):value=getattr(value,part)
            require(getattr(value,"__module__",None)==module and hasattr(value,"__code__") and j.exact_path(value.__code__.co_filename)==j.exact_path(expected[module]["path"]),"实际SDK调用实现未绑定："+module+"."+name)
            require(value.__code__==code_by_name(canonical,name),"SDK内存中方法实现与已绑定原源码不同："+module+"."+name)
    sdk=sys.modules["xsdb"];dispatch=sys.modules["xsdb.xsdb_debug_session"]
    for name in ("Session","Target"):
        module="xsdb."+name.lower();cls=getattr(sys.modules[module],name)
        require(isinstance(cls,type) and cls.__module__==module and cls.__name__==name and cls.__qualname__==name,"官方SDK类定义来源不同："+name)
    require(dispatch.Session is sys.modules["xsdb.session"].Session,"官方dispatch.Session别名不同")
    require(sys.modules["xsdb.session"].Target is sys.modules["xsdb.target"].Target,"官方session.Target别名不同")
    require("debug_session" in vars(sdk) and "debug_session_int_obj" in vars(dispatch),"官方SDK会话所有权字段缺失")
    if session is None:
        require(sdk.debug_session is None and dispatch.debug_session_int_obj is None,"禁止复用或清理调用方已有SDK会话")
    else:
        cls=sys.modules["xsdb.session"].Session
        require(type(session) is cls and sdk.debug_session is session and dispatch.debug_session_int_obj is session,"实际session类型/模块/自有对象不符")
        for name in ("connect","disconnect","targets"):
            require(getattr(getattr(session,name),"__func__",None) is getattr(cls,name),"实际session方法接收器被替换："+name)
    if target is not None:
        cls=sys.modules["xsdb.target"].Target
        require(type(target) is cls,"实际target接收器类型或定义模块不符")
        for name in ("state","stop","con","dow","bpadd","mrd","mwr","rst","fpga","loadhw","unloadhw"):
            require(getattr(getattr(target,name),"__func__",None) is getattr(cls,name),"实际target方法接收器被替换："+name)
    return observed

def helpers():
    """仅加载无硬件副作用的已审项目工具。"""
    if str(ROOT/"verification") not in sys.path:sys.path.insert(0,str(ROOT/"verification"))
    jtag=importlib.import_module("s2b_board_jtag")
    return jtag,jtag.transport

def digest(path):
    """流式SHA绑定，不复制位流或大型资产。"""
    h=hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""):h.update(block)
    return h.hexdigest()

def save(path,data):
    """UTF8/LF独占创建结果文件。"""
    require(path.parent.is_dir() and not path.exists(),"结果目标已存在或父目录无效")
    with path.open("x",encoding="utf-8",newline="\n") as out:json.dump(data,out,ensure_ascii=False,indent=2,default=repr);out.write("\n")

class Recorder:
    """逐调用即时落盘原输出、异常和返回类型，失败不能抹去。"""
    def __init__(self,path,record):
        self.stream=path.open("x",encoding="utf-8",newline="\n");self.record=record
    def call(self,name,function,*args,**kwargs):
        row={"time_utc8":datetime.now(TZ).isoformat(),"api":name,"args":repr(args),"kwargs":repr(kwargs)}
        self.record["calls"].append(row);out,err=io.StringIO(),io.StringIO();start=time.monotonic()
        try:
            with redirect_stdout(out),redirect_stderr(err):value=function(*args,**kwargs)
            row.update(status="RETURNED",return_type=type(value).__name__,return_repr=repr(value));return value
        except BaseException as error:
            row.update(status="RAISED",error=repr(error),traceback=traceback.format_exc());raise
        finally:
            row.update(stdout=out.getvalue(),stderr=err.getvalue(),elapsed_seconds=time.monotonic()-start)
            self.stream.write(json.dumps(row,ensure_ascii=False,default=repr)+"\n");self.stream.flush()

def _identity_snapshot():
    """仅枚举进程/监听和Ports PNP；静态PowerShell不插入外部代码。"""
    command="""$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false);
$servers=@(Get-CimInstance Win32_Process -Filter "Name='hw_server.exe'" | Select-Object ProcessId,ParentProcessId,ExecutablePath,@{Name='CreationTimeFileTimeUtc';Expression={[string]$_.CreationDate.ToFileTimeUtc()}});
$listeners=@(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess);
$ports=@(Get-CimInstance Win32_PnPEntity -Filter "PNPClass='Ports'" | Select-Object Name,PNPDeviceID,ConfigManagerErrorCode);
[pscustomobject]@{servers=$servers;listeners=$listeners;ports=$ports}|ConvertTo-Json -Depth 5"""
    native=subprocess.run(["powershell.exe","-NoProfile","-Command",command],capture_output=True,timeout=30)
    require(native.returncode==0,"系统身份查询失败："+repr(native.stderr))
    return {"command":command,"native_exit_code":native.returncode,"stdout_hex":native.stdout.hex(),"stderr_hex":native.stderr.hex(),
            "snapshot":strict_json(native.stdout.decode("utf-8-sig"))}

def validate_identity(actual,expected_server,uart):
    """PID、创建时刻、路径和全部server归属必须一致；不能凭端口存在。"""
    data=actual["snapshot"];servers=data.get("servers");listeners=data.get("listeners");ports=data.get("ports")
    require(type(servers) is list and len(servers)==1,"必须唯一root-owned hw_server")
    server=servers[0];native=expected_server["native"]
    for key in ("ProcessId","ExecutablePath","CreationTimeFileTimeUtc"):
        require(server.get(key)==native[key],"hw_server身份不匹配："+key)
    require(type(listeners) is list and listeners and all(x.get("LocalPort")==3121 and x.get("OwningProcess")==native["ProcessId"] for x in listeners),"3121监听不属于指定进程")
    require(type(ports) is list,"PNP查询类型错误")
    matches=[x for x in ports if x.get("Name")==uart["name"] and x.get("PNPDeviceID")==uart["pnp_device_id"]]
    require(len(matches)==1 and matches[0].get("ConfigManagerErrorCode")==0 and uart["name"].endswith("(COM4)"),"串口PNP身份或状态错误")
    require(len([x for x in ports if str(x.get("Name","")).endswith("(COM4)")])==1,"COM4身份歧义")
    return data

def _preflight(config,record,log):
    """全部固定原字节及兼容审批先核验，再允许SDK/串口导入。"""
    j,t=helpers()
    require(type(config) is dict and set(config)==CONFIG_KEYS and type(config["schema_version"]) is int and config["schema_version"]==1,"config字段或版本错误")
    require(re.fullmatch(r"[0-9a-f]{40}",str(config["source_commit"])),"提交必须完整固定")
    subprocess.run(["git","cat-file","-e",config["source_commit"]+"^{commit}"],cwd=ROOT,check=True,capture_output=True)
    observed_commit=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,capture_output=True).stdout.decode("ascii").strip()
    require(observed_commit==config["source_commit"],"root选定源码基线与实际HEAD不同")
    record["source_commit"]=observed_commit
    require(type(config["cpu_seed"]) is int and type(config["dap_seed"]) is int and config["cpu_seed"]!=config["dap_seed"],"两个seed必须不同")
    j.pattern(config["cpu_seed"]);j.pattern(config["dap_seed"])
    require(type(config["response_timeout_seconds"]) in (int,float) and 0<config["response_timeout_seconds"]<=60,"UART观察期限必须0..60秒")
    uart=config["uart_identity"]
    require(type(uart) is dict and set(uart)=={"port","name","pnp_device_id","config_manager_error_code"} and uart["port"]=="COM4" and uart["config_manager_error_code"]==0 and type(uart["name"]) is str and type(uart["pnp_device_id"]) is str and uart["pnp_device_id"],"UART identity格式错误")
    bindings=config["bindings"]
    required={"init_elf","app_elf","xsa","bit","csr_source","interface","sdk_target","tool_source","elf_parser","delivery_parser","transport_source","entry_source","platform_checker","sdk_init","pyserial_init"}
    require(type(bindings) is dict and set(bindings)==required,"T16/入口绑定字段错误")
    for item in bindings.values():
        require(type(item) is dict and set(item)=={"path","sha256"},"绑定格式错误")
        require(j.exact_path(item["path"]).stat().st_size<=32*1024*1024,"绑定文件超出轻量入口预算")
        j.bound_bytes(item)
    require(bindings["tool_source"]["sha256"]==JTAG_SHA,"必须使用固定T16候选精确版本")
    postconfig=j.postconfig_basis(j.bound_bytes(bindings["xsa"]))
    serial_files=verify_serial_files(config)
    for key,path in [("entry_source",Path(__file__).absolute()),("tool_source",Path(j.__file__).absolute()),("transport_source",Path(t.__file__).absolute()),
                     ("platform_checker",ROOT/"verification/check_s2b_inference_platform.py"),("elf_parser",ROOT/"verification/check_s2b_ps_smoke_layout.py"),
                     ("delivery_parser",ROOT/"verification/check_stage_delivery.py"),("csr_source",ROOT/"src/s2b_control_csr.sv"),
                     ("interface",ROOT/"docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"),
                     ("sdk_init",SDK_INIT),("sdk_target",SDK_INIT.parent/"target.py")]:
        require(j.exact_path(bindings[key]["path"])==j.exact_path(path),"实际运行来源未绑定："+key)
    sdk_files=verify_sdk_files(config)
    require(j.exact_path(bindings["bit"]["path"]).stat().st_size<=32*1024*1024,"位流超出入口内存预算")
    bound_json(config["build_details"],j,"build_details",record);build_path,build=t.verify_build(config["build_details"]["path"])
    require(digest(build_path)==config["build_details"]["sha256"],"build_details漂移")
    for key,source in [("app_elf",build["elf"]),("init_elf",build["initializer_elf"]),("xsa",{"path":build["config"]["xsa"],"sha256":build["xsa_sha256"]})]:
        require(bindings[key]=={k:source[k] for k in ("path","sha256")},"编译产物绑定不同："+key)
    receipt=bound_json(config["compat_review"],j,"compat_review",record)
    require(set(receipt)=={"schema_version","kind","role","status","scope","visibility_parameter","source_sha256","artifacts","checks"},"compat receipt字段错误")
    require(type(receipt["schema_version"]) is int and receipt["schema_version"]==1 and receipt["kind"]=="s2b-runtime-platform-compatibility/1.0.0" and receipt["role"]=="INDEPENDENT_REVIEWER" and receipt["status"]=="PASS" and receipt["scope"]=="visibility0_cache_probe_only" and type(receipt["visibility_parameter"]) is int and receipt["visibility_parameter"]==0,"拒绝UNIT/mock或未批准的兼容receipt")
    require(type(receipt["checks"]) is dict and set(receipt["checks"])==COMPAT_CHECKS and all(v is True for v in receipt["checks"].values()),"兼容事实未全部批准")
    checker=importlib.import_module("check_s2b_inference_platform")
    require(j.exact_path(checker.__file__)==j.exact_path(bindings["platform_checker"]["path"]),"平台checker模块来源错误")
    actual_sources=log.call("platform.check_static",checker.check_static,ROOT)
    require(receipt["source_sha256"]==actual_sources,"compat闭包与当前平台不同")
    artifacts=receipt["artifacts"]
    require(type(artifacts) is dict and set(artifacts)==ARTIFACT_KEYS,"compat artifact字段错误")
    for item in artifacts.values():
        require(type(item) is dict and set(item)=={"path","sha256"},"compat artifact绑定格式错误")
        require(j.exact_path(item["path"]).stat().st_size<=32*1024*1024,"compat artifact超出轻量入口预算")
        j.bound_bytes(item)
    for key,expected in [("compiled_xsa",bindings["xsa"]),("init_elf",bindings["init_elf"]),("app_elf",bindings["app_elf"]),("bit",bindings["bit"]),("build_details",config["build_details"])]:require(artifacts[key]==expected,"compat artifact不匹配："+key)
    require(artifacts["implemented_xsa"]["path"]!=artifacts["compiled_xsa"]["path"],"编译XSA与新implemented XSA不得混为同文件")
    manifest=bound_json(artifacts["platform_manifest"],j,"platform_manifest",record)
    require(type(manifest.get("schema_version")) is int and manifest["schema_version"]==1,"平台manifest schema_version类型错误")
    require(type(manifest.get("checks")) is list and manifest["checks"] and all(x.get("status")=="PASS" or (x.get("status")=="NOT_APPLICABLE" and type(x.get("reason")) is str and x["reason"].strip()) for x in manifest["checks"]),"平台manifest仍有失败/受阻/未执行项")
    command=[sys.executable,"-B",bindings["delivery_parser"]["path"],"--mode","evidence","--manifest",artifacts["platform_manifest"]["path"]]
    checked=log.call("platform.evidence_checker",subprocess.run,command,cwd=ROOT,capture_output=True,timeout=30)
    record["platform_evidence_check"]={"command":command,"native_exit_code":checked.returncode,"stdout_hex":checked.stdout.hex(),"stderr_hex":checked.stderr.hex()}
    require(checked.returncode==0,"平台manifest包装核验失败")
    require(j.bound_bytes(config["cold_basis"]),"官方统一冷恢复依据为空")
    server=bound_json(config["owned_hw_server_identity"],j,"owned_server",record)
    require(server.get("status")=="OWNED_SERVER_READY" and type(server.get("native")) is dict,"owned server记录未就绪")
    native=server["native"]
    require(type(native.get("ProcessId")) is int and native["ProcessId"]>0 and re.fullmatch(r"[0-9]+",str(native.get("CreationTimeFileTimeUtc",""))),"服务PID/creation格式错误")
    require(j.exact_path(native["ExecutablePath"]).name=="hw_server.exe" and digest(j.exact_path(native["ExecutablePath"]))==server["native_sha256"],"服务原生可执行文件绑定错误")
    record["verified_inputs"]={"build_details":config["build_details"],"compat_review":config["compat_review"],"compat_artifacts":artifacts,"source_sha256":actual_sources,"cold_basis":config["cold_basis"],"compiled_build_status":build["status"],"pyserial_files":serial_files,"sdk_files":sdk_files,"sdk_init":bindings["sdk_init"],"sdk_target":bindings["sdk_target"],"postconfig_basis":postconfig}
    return j,t,build,server

def _runtime(config):
    """只在显式run中导入官方XSDB与已绑定pyserial；不创建Vitis client/server。"""
    require("v2026.1" in os.environ.get("XILINX_VITIS_VERSION",""),"必须通过Vitis2026.1脚本入口")
    verify_sdk_files(config);verify_serial_files(config)
    package=Path(config["bindings"]["pyserial_init"]["path"])
    require(package.name=="__init__.py" and package.parent.name=="serial","pyserial入口路径错误")
    if str(package.parent.parent) not in sys.path:sys.path.insert(0,str(package.parent.parent))
    xsdb=importlib.import_module("xsdb");serial=importlib.import_module("serial")
    j,_=helpers()
    require(j.exact_path(xsdb.__file__)==j.exact_path(config["bindings"]["sdk_init"]["path"]),"XSDB实际模块漂移")
    require(j.exact_path(serial.__file__)==j.exact_path(package) and serial.__version__=="3.5","pyserial实际模块/版本不匹配")
    verify_runtime_sources(config)
    return xsdb,serial

def register_csr_debug_map(config,record,log,session,controller,owner):
    """仅从已独审的implemented XSA登记CSR调试窗口，不放开其他PL地址。"""
    j,_=helpers()
    binding=record["verified_inputs"]["compat_artifacts"]["implemented_xsa"]
    raw=j.bound_bytes(binding)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names=archive.namelist()
        require(len(names)==len(set(names)),"implemented XSA存在重复成员")
        members=[name for name in names if name.endswith(".hwh")]
        require(len(members)==1 and archive.getinfo(members[0]).file_size<=4*1024*1024,"implemented HWH不唯一或过大")
        tree=ET.fromstring(archive.read(members[0]))
    base,end=0x43C00000,0x43C0FFFF
    regions=[]
    for row in tree.findall(".//MEMRANGE"):
        address=int(row.get("BASEVALUE","-1"),0)
        if base<=address<=end:regions.append(row.attrib)
    require(len(regions)==1,"CSR筛选范围必须只有一个HWH地址块")
    region=regions[0]
    require(int(region["BASEVALUE"],0)==base and int(region["HIGHVALUE"],0)==end
            and region.get("INSTANCE")=="infer" and region.get("MEMTYPE")=="REGISTER"
            and region.get("MASTERBUSINTERFACE")=="M_AXI_GP0" and region.get("SLAVEBUSINTERFACE")=="S_AXI",
            "HWH CSR窗口、器件或总线不符合已批准平台")
    controller.gate()
    reference=controller.targets["apu"]
    apu=log.call("session.select_apu_for_debug_map",session.targets,id=vars(reference)["_id"])
    require(all(vars(apu).get(key)==vars(reference).get(key) for key in ("_ctx","_id","_name"))
            and session._curtarget is apu,"映射接收器与实际选中APU不一致")
    log.call("runtime.verify_debug_map_target",verify_runtime_sources,config,session,apu)
    require(not session._designtable and not session._memmap_ctxs,"新自有会话已存在硬件映射，拒绝复用")
    owner.update(apu=apu,channel=session._curchan,ctx=vars(apu)["_ctx"],attempted=True)
    record["debug_memory_map"]={"status":"ATTEMPTED","implemented_xsa":binding,"hwh_region":region,
                                "apu_id":vars(apu)["_id"],"apu_ctx":owner["ctx"],"range":[base,end],"cleanup":"NOT_RUN"}
    log.call("apu.loadhw.csr_only",apu.loadhw,hw=binding["path"],mem_ranges=[[base,end]])
    log.call("runtime.verify_after_loadhw",verify_runtime_sources,config,session,apu)
    mapped=session._memmap_ctxs.get(owner["channel"],{}).get(owner["ctx"],{})
    values=list(mapped.values())
    require(len(values)==1 and values[0].get("base")==base and values[0].get("size")==0x10000
            and values[0].get("high")==end and values[0].get("type")=="REGISTER" and values[0].get("flags")==3,
            "SDK实际硬件映射缺失、越界或权限不符")
    table=session._memmaptable.get(owner["channel"],{}).get(owner["ctx"],{})
    entries=[row for rows in table.values() for row in rows]
    require(len(entries)==1 and entries[0].get("Addr")==base and entries[0].get("Size")==0x10000
            and entries[0].get("Flags")==3 and "FileName" not in entries[0],"SDK下发映射不是唯一CSR读写窗口")
    record["debug_memory_map"].update(status="REGISTERED_CSR_ONLY",sdk_regions=mapped,sdk_entries=entries)

def clear_csr_debug_map(config,record,log,session,owner):
    """清理本次自有会话登记的硬件映射；部分失败亦保留真实清理结果。"""
    if not owner.get("attempted"):return
    apu=log.call("session.select_apu_for_map_cleanup",session.targets,id=vars(owner["apu"])["_id"])
    require(all(vars(apu).get(key)==vars(owner["apu"]).get(key) for key in ("_ctx","_id","_name"))
            and session._curtarget is apu and session._curchan==owner["channel"],"清理映射APU身份不符")
    log.call("runtime.verify_map_cleanup_target",verify_runtime_sources,config,session,apu)
    log.call("apu.unloadhw.owned_map",apu.unloadhw)
    require(not session._designtable and not session._memmap_ctxs.get(owner["channel"],{}),"本次硬件映射未清理")
    record["debug_memory_map"]["cleanup"]="OWNED_HW_MAP_CLEARED"

def run(config):
    """总控显式传入JSON文件才执行；新Run独占，任何失败留原字节并抛异常。"""
    j,_=helpers();config_path=j.exact_path(config)
    require(config_path.stat().st_size<=1048576,"config超过1MiB限制")
    raw=config_path.read_bytes()
    parent=j.exact_path(ROOT/"report/evidence/S2B-T19",directory=True)
    try:
        cfg=strict_json(raw.decode("utf-8"));require(type(cfg) is dict and "run_dir" in cfg,"config需要run_dir")
    except (VisibilityProbeError,UnicodeError) as error:
        import uuid
        rejected=parent/("config_rejection_"+datetime.now(TZ).strftime("%Y%m%d_%H%M%S")+"_"+uuid.uuid4().hex)
        require(not rejected.exists(),"config拒绝Run已存在");rejected.mkdir()
        with (rejected/"input_config.json.raw").open("xb") as out:out.write(raw)
        save(rejected/"visibility_probe_result.json",{"status":"FAILED_CONFIG_REJECTED","native_exit_code":2,"hardware_execution":"NOT_RUN","config_sha256":hashlib.sha256(raw).hexdigest(),"error":repr(error)})
        raise VisibilityProbeError("config拒绝，原字节："+str(rejected)) from error
    requested=Path(cfg["run_dir"])
    require(requested.is_absolute() and requested.parent==parent and re.fullmatch(r"[A-Za-z0-9_-]+",requested.name) and not requested.exists(),"RunId必须为指定T19父目录下的新精确目录")
    requested.mkdir();folder=j.exact_path(requested,directory=True)
    record={"schema_version":1,"status":"FAILED","hardware_execution":"REQUESTED_BY_ROOT_CALL","cold_lifecycle_proven":False,
            "config_path":str(config_path),"config_sha256":hashlib.sha256(raw).hexdigest(),"source_sha256":digest(Path(__file__)),
            "calls":[],"identity_snapshots":[],"cleanup_errors":[],"raw_input_dir":str(folder),"peak_process_tree_memory_bytes":None,"started_at_utc8":datetime.now(TZ).isoformat(),
            "limitations":["compat role/PASS字符串不创造独立来源，root固定SHA的真实Reviewer来源需独立核查。","system-stop不等于物理POR或旧AXI生命周期结束，cold flag始终false。","本入口只执行visibility0缓存先验，不LOAD、不START、不发布visibility PASS。","核状态为离散观测，进程树峰值内存未测。"]}
    with (folder/"input_config.json").open("xb") as out:out.write(raw)
    log=Recorder(folder/"entry_calls.jsonl",record)
    sdk=session=channel=port=controller=wire=None;cpu0=None;cpu0_touched=False;start=time.monotonic();failure=None;map_owner={}
    def identity(label):
        actual=log.call("identity."+label,_identity_snapshot)
        record["identity_snapshots"].append({"label":label,**actual})
        validate_identity(actual,server,cfg["uart_identity"])
    def stop_cpu0(label):
        if cpu0 is not None and cpu0_touched:
            state=log.call(label+".state",cpu0.state)
            if state=="Running":log.call(label+".stop",cpu0.stop)
            require(log.call(label+".state_after",cpu0.state).startswith("Stopped"),"CPU0未停止")
    try:
        j,t,build,server=_preflight(cfg,record,log)
        identity("before_sdk")
        sdk,serial=log.call("runtime.import_bound_modules",_runtime,cfg)
        record["runtime_sdk_sources"]=log.call("runtime.verify_before_session",verify_runtime_sources,cfg)
        record["runtime_modules"]={"xsdb_file":sdk.__file__,"pyserial_file":serial.__file__,"pyserial_version":serial.__version__,"vitis_environment_version":os.environ.get("XILINX_VITIS_VERSION")}
        session=log.call("xsdb.start_debug_session",sdk.start_debug_session)
        log.call("runtime.verify_session_class",verify_runtime_sources,cfg,session)
        channel=log.call("session.connect",session.connect,url="TCP:localhost:3121",server="hw_server")
        record["runtime_sdk_sources"]=log.call("runtime.verify_after_connect",verify_runtime_sources,cfg,session)
        identity("after_connect")
        rows=log.call("session.initial_targets",session.targets,"--target_properties");selected=j.validate_targets(rows)
        record["initial_targets"]=rows;record["initial_cpu_states"]={}
        cores=[]
        for name in j.NAMES[1:3]:
            row=selected[name];target=log.call("session.initial_cpu",session.targets,id=row["target_id"])
            log.call("runtime.verify_initial_target",verify_runtime_sources,cfg,session,target)
            require(vars(target).get("_ctx")==row["target_ctx"] and vars(target).get("_id")==row["target_id"] and vars(target).get("_name")==name,"初始CPU对象身份错误")
            state=log.call("initial."+name+".state",target.state)
            require(type(state) is str and (state=="Running" or state.startswith("Stopped")),"初始核状态未知")
            record["initial_cpu_states"][name]=state;cores.append((name,target,state))
        cpu0=cores[0][1]
        for name,target,state in cores:
            if name==j.NAMES[1]:cpu0_touched=True
            if state=="Running":log.call("authorized_stop."+name,target.stop)
            require(log.call("stopped."+name+".state",target.state).startswith("Stopped"),"核停住失败")
        controller=j.JtagController(session,cfg["bindings"],folder)
        controller.select_and_gate()
        for target in controller.targets.values():
            log.call("runtime.verify_controller_target",verify_runtime_sources,cfg,session,target)
        controller.system_reset_stop(cfg["cold_basis"])
        log.call("runtime.verify_after_reset",verify_runtime_sources,cfg,session)
        _preflight(cfg,record,log);identity("before_uart_deploy")
        register_csr_debug_map(cfg,record,log,session,controller,map_owner)
        port=log.call("serial.construct_closed",serial.Serial,port=None,baudrate=115200,bytesize=8,parity="N",stopbits=1,timeout=0.1,write_timeout=1.0,rtscts=False,dsrdtr=False)
        port.dtr=False;port.rts=False;port.port="COM4"
        log.call("serial.open",port.open)
        record["serial_config"]={"port":"COM4","baudrate":115200,"bytesize":8,"parity":"N","stopbits":1,"timeout":0.1,"write_timeout":1.0,"rtscts":False,"dsrdtr":False,"dtr":False,"rts":False}
        with (folder/"uart_rx_raw.bin").open("xb") as rx,(folder/"uart_tx_headers.bin").open("xb") as tx:
            wire=j.JtagWireSession(port,rx,tx,response_timeout=cfg["response_timeout_seconds"])
            controller.deploy()
            require(controller.postconfigured and controller.record["postconfiguration"]["status"]=="PASS","T16 postconfig及app前冷CSR未通过")
            record["postconfiguration"]=controller.record["postconfiguration"]
            log.call("runtime.verify_after_deploy",verify_runtime_sources,cfg,session)
            record["banner"]=log.call("wire.banner",wire.banner,build["source_sha256"]["vitis/s2b_inference_app.c"],build["xsa_sha256"])
            identity("before_cache")
            record["cache_probe"]=controller.cache_probe(wire,cfg["cpu_seed"],cfg["dap_seed"])
            record["runtime_sdk_sources"]=log.call("runtime.verify_after_cache",verify_runtime_sources,cfg,session)
            final=controller.cold_idle("entry_final_before_stop")
            record["final_csr"]=final
            require(wire.epoch==0 and wire.last_sequence==2 and wire.abort_pending is None and not wire.failed,"cache后UART状态不符")
            record["uart_events"]=wire.events
            stop_cpu0("completed_probe_cpu0")
        identity("after_probe")
        record["status"]="API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING"
    except BaseException as error:
        failure=error;record.update(status="FAILED",error=repr(error),traceback=traceback.format_exc())
        if wire is not None:wire.failed=True
        if controller is not None:
            controller.failed=True;controller.record["status"]="FAILED";controller.fail_stop()
        try:stop_cpu0("failure_cpu0")
        except BaseException as stop_error:record["cleanup_errors"].append({"action":"failure_cpu0","error":repr(stop_error)})
    finally:
        if wire is not None:
            record["uart_events"]=wire.events;record["uart_failed"]=wire.failed
        def cleanup(name,function,**kwargs):
            nonlocal failure
            try:log.call(name,function,**kwargs)
            except BaseException as error:
                record["cleanup_errors"].append({"action":name,"error":repr(error)})
                failure=failure or error;record["status"]="FAILED"
                if controller is not None:controller.failed=True;controller.record["status"]="FAILED"
                if wire is not None:wire.failed=True
                try:stop_cpu0("cleanup_failure_cpu0")
                except BaseException as stop_error:record["cleanup_errors"].append({"action":"cleanup_failure_cpu0","error":repr(stop_error)})
        if port is not None:
            def close_serial():
                port.close();require(not port.is_open,"串口close返回后仍打开")
            cleanup("serial.close",close_serial);record["serial_closed"]=not port.is_open
        if controller is not None:
            cleanup("controller.close",controller.close)
            if controller.failed or controller.record["cleanup_errors"]:
                failure=failure or VisibilityProbeError("controller清理失败");record["status"]="FAILED"
            if not controller.log.closed:
                cleanup("controller.partial_log.close",controller.log.close)
                save(folder/"jtag_close_failure_snapshot.json",controller.record)
        if session is not None:
            cleanup("owned_csr_debug_map.clear",clear_csr_debug_map,config=cfg,record=record,log=log,session=session,owner=map_owner)
            cleanup("session.disconnect",session.disconnect,**({"chan":channel} if channel is not None else {}))
        if sdk is not None:cleanup("xsdb.dispose",sdk.dispose)
        for name in ("uart_rx_raw.bin","uart_tx_headers.bin","jtag_result.json","jtag_calls.jsonl"):
            path=folder/name
            if path.is_file():record.setdefault("saved_files",{})[name]={"sha256":digest(path),"bytes":path.stat().st_size}
        record.update(finished_at_utc8=datetime.now(TZ).isoformat(),elapsed_seconds=time.monotonic()-start,native_exit_code=2 if failure or record["status"]=="FAILED" else 0,owned_hw_server_released=False)
        log.stream.close();save(folder/"visibility_probe_result.json",record)
    if failure is not None:raise VisibilityProbeError("候选cache先验运行失败，完整证据："+str(folder)) from failure
    return record

def main():
    """仅显式config参数或root设置的环境变量触发真实运行。"""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,help="root固定的精确JSON配置路径；将执行授权的易失部署与cacheprobe")
    args=parser.parse_args()
    config=args.config or os.environ.get("S2B_VISIBILITY_PROBE_CONFIG")
    require(config is not None,"需要显式--config或S2B_VISIBILITY_PROBE_CONFIG")
    result=run(config);print(json.dumps({"status":result["status"],"native_exit_code":result["native_exit_code"]},ensure_ascii=False));return result["native_exit_code"]

if __name__=="__main__":
    try:raise SystemExit(main())
    except VisibilityProbeError as error:
        print(str(error),file=sys.stderr);raise SystemExit(2)
