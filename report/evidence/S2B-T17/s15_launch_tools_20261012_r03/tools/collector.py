"""S15轻量准备、源码核验及关闭后证据收集；不调用Vivado或硬件。"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib

import compat_pins
import native_contract as contract
ROOT=Path(__file__).parents[4]
WORK=Path(__file__).parent
CACHE=compat_pins.SYNTH_CACHE
PROJECT=compat_pins.PROJECT
REPORT=compat_pins.SYNTH_REPORT
PRE=compat_pins.SOURCE_PRE
FREEZE=compat_pins.SOURCE_FREEZE
FREEZE_SHA=compat_pins.SOURCE_FREEZE_SHA
CLASSIFIER=ROOT/"report/evidence/S2B-T17/s7_platform_20261011_r01/collector_code/classify_s7_sta.py"
CLASSIFIER_SHA="7eb8cdc2f3d1584c7952e6cc5106227cc0d84cc42b6529a624426eaf174c0c9a"
LABELS=("source","builder","setup","launch","wait","open_run","reports","query_xdc","close")


def require(condition,message):
    """输入或绑定不符立即停止，不改写已存在证据。"""
    if not condition: raise ValueError(message)


def exact(path,kind="file"):
    """逐组件核验精确大小写、目标类型及reparse，不接受路径别名。"""
    raw=os.fspath(path)
    require(type(raw) is str,"路径不是Unicode字符串")
    require(not any(component in {".",".."} for component in re.split(r"[\\/]",raw)),"原始路径含点路径组件："+raw)
    path=Path(raw); require(path.is_absolute(),"不是完整路径："+str(path))
    require(not path.drive.startswith("\\\\"),"UNC或设备命名空间路径不适用于本机C盘部署")
    current=Path(path.anchor)
    if sys.platform == "win32":
        attributes=None
        for component in path.parts[1:]:
            if attributes is not None: require(attributes&0x10,"父目录类型错误："+str(current))
            actual,attributes=compat_pins.windows_find_info(current/component)
            require(actual==component,"精确大小写名称不存在："+str(path))
            require(not attributes&0x400,"路径含重解析点："+str(current/component))
            current=current/component
        if attributes is None: attributes=0x10 if current.is_dir() else 0
        is_directory=bool(attributes&0x10)
        require(is_directory if kind=="directory" else (not is_directory and not attributes&0x40),"目标类型错误："+str(current))
    else:
        for component in path.parts[1:]:
            require(current.is_dir(),"父目录类型错误："+str(current))
            require(component in {p.name for p in current.iterdir()},"精确名称不存在："+str(path))
            current=current/component
            info=current.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info,"st_file_attributes",0)&getattr(stat,"FILE_ATTRIBUTE_REPARSE_POINT",1024),"路径含链接："+str(current))
        require(current.is_dir() if kind=="directory" else current.is_file(),"目标类型错误："+str(current))
    return current


def rel(path):
    """已有精确目标仅转成仓库标识，文件系统目标不重拼写。"""
    return path.relative_to(ROOT).as_posix()


def sha(path):
    """流式绑定真实原字节。"""
    digest=hashlib.sha256()
    with exact(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""): digest.update(block)
    return digest.hexdigest()


def binding(path):
    """库存单独保存长度，不混入标准files三字段。"""
    path=exact(path)
    return dict(path=rel(path),sha256=sha(path),bytes=path.stat().st_size)


def read(path):
    """JSON采用UTF-8，不执行输入中的命令。"""
    return json.loads(exact(path).read_text(encoding="utf-8"))


def fresh(path,directory=False):
    """只允许本轮固定落点；不覆盖RunId或既有目标。"""
    require(any(path.is_relative_to(p) for p in (WORK,CACHE,REPORT,PRE)),"写入目标越界")
    exact(path.parent,"directory"); require(not path.exists(),"目标已存在："+str(path))
    if directory: path.mkdir()
    return path


def save(path,value):
    """创建新UTF-8 JSON，异常原件保持。"""
    with fresh(path).open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2); stream.write("\n")


def rawcopy(source,target):
    """复制前后逐字节核对来源，正式目录使用安全名称。"""
    before=binding(source)
    shutil.copyfile(source,fresh(target))
    copied=binding(target); require(binding(source)==before and copied["sha256"]==before["sha256"] and copied["bytes"]==before["bytes"],"复制来源漂移")
    return dict(original_path=before["path"],saved_path=copied["path"],sha256=copied["sha256"],bytes=copied["bytes"])


def git(*args):
    """只读精确Git对象并保留原生失败码。"""
    command=["git","-c","core.longpaths=true","-c","maintenance.auto=false",*args]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30)
    require(result.returncode==0,"Git原生失败："+str(result.returncode)+":"+result.stderr.decode("utf-8",errors="replace"))
    return result.stdout,command


def require_pinned_commit(commit):
    """综合实际源码提交必须严格等于本轮ROOT冻结pin，不能仅比较HEAD或RAW。"""
    require(type(commit) is str and re.fullmatch(r"[0-9a-f]{40}",commit) and commit==compat_pins.SOURCE_COMMIT,"源码提交与ROOT冻结SOURCE_COMMIT不同")


def load_freeze():
    """消费本轮G1新schema，不预设历史static/extra/RAW数量。"""
    compat_pins.require_ready()
    require(sha(FREEZE)==FREEZE_SHA,"G1 freeze原字节不同")
    freeze=read(FREEZE); require_pinned_commit(freeze.get("source_commit")); rows=freeze["source_files"]
    require(freeze["profile"]=="s2b-inference-platform/0.1.15" and len(rows)==len({r["path"] for r in rows}),"freeze版本或路径重复")
    hashes={r["path"]:r["sha256"] for r in rows}
    require(bool(hashes) and "verification/test_s2b_conv_tile_origin_rtl.py" in hashes,"本轮冻结集合为空或遗漏S13真实runner")
    require(len(freeze["frozen14"])==14 and set(freeze["frozen14"])<=set(hashes),"原14声明错误")
    spec=importlib.util.spec_from_file_location("s15_platform_checker",exact(ROOT/"verification/check_s2b_inference_platform.py"))
    checker=importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
    static=checker.check_static(ROOT)
    require(bool(static),"本轮实际static闭包为空")
    require(set(static)<=set(hashes),"static闭包不是freeze子集")
    require(freeze["frozen14"]==checker.FROZEN_CORE_SHA256,"原14固定SHA不同")
    for name,expected in hashes.items(): require(sha(ROOT/name)==expected,"已审源漂移："+name)
    profile=read(ROOT/"board/s2b_inference_platform.json")
    require(profile["version"]==freeze["profile"],"实际profile与本轮冻结不同")
    require(profile["rtl_sources"]==freeze["active_rtl_sources"] and len(profile["rtl_sources"])==18,"实际18RTL闭包不同")
    require(len(profile["source_derivation"]["derived_sources"])==8 and profile["clock_hz"]==50000000 and profile["visibility_default"]==0,"8派生/50MHz/visibility0不同")
    return freeze,hashes,static,profile


def prepare(receipt_name):
    """只写tmp准备receipt，不伪造commit或生成source_before。"""
    compat_pins.require_ready()
    exact(WORK,"directory"); exact(CACHE,"directory")
    freeze,hashes,static,profile=load_freeze()
    require(sha(CLASSIFIER)==CLASSIFIER_SHA,"既有STA分类器漂移")
    scripts=[]
    for name in ("collector.py","native.py","native_capture.py","compat_pins.py"):
        path=exact(WORK/name); ast.parse(path.read_text(encoding="utf-8")); scripts.append(binding(path))
    receipt=dict(status="STOP_PREPARED_ONLY",created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),source_freeze=binding(FREEZE),source_count=len(hashes),static_count=len(static),extra_paths=sorted(set(hashes)-set(static)),active_rtl_count=18,derived_count=8,original_active_count=6,outer_count=4,prepared_scripts=scripts,sta_classifier=binding(CLASSIFIER),targets=dict(project=str(PROJECT),rootrun=str(CACHE),evidence=str(REPORT),preflight=str(PRE)),actual_commit="ROOT审查并提交后必须作为--commit传入，准备期不声明新提交。",source_before_written=False,formal_report_written=False,heavy_or_ross_or_hardware_executed=False,tool_versions=dict(python=sys.version),assumptions=["ROOT仅一次products与一次synth；products native0/capture1只保留失败，不重跑。","collect须显式CLOSED_INPUTS_READY/project_closed门禁及已封存history/log/source_after。","五任务OS退出码未捕获时为null；MCP客户端、capture和native码分别记录。","六PSinit/HWH按实际字节比较，不预设相同或兼容。","seal必须在collector原生包装完成之后执行；G1/G2只绑定已有原件，不自报审查0。"])
    receipt["runtime_config"]=compat_pins.runtime_config_binding()
    require(re.fullmatch(r"prepared_receipt(?:_r\d+)?\.json",receipt_name),"准备receipt名称非法")
    save(WORK/receipt_name,receipt)
    print(json.dumps(receipt,ensure_ascii=False))


def source(commit,phase):
    """实际提交/全部源码已校验后才创建本轮前或后快照。"""
    compat_pins.require_ready()
    require_pinned_commit(commit)
    require(re.fullmatch(r"[0-9a-f]{40}",commit),"缺少ROOT提供的完整提交")
    head,_=git("rev-parse","HEAD"); require(head.decode("ascii").strip()==commit,"HEAD与实际提交不同")
    freeze,hashes,static,profile=load_freeze(); files=[]
    for name,expected in hashes.items():
        raw=exact(ROOT/name).read_bytes(); blob,command=git("show",commit+":"+name)
        same=blob==raw; eol=not same and b"\r\n" not in blob and blob.replace(b"\n",b"\r\n")==raw
        require(same or eol,"Git不是RAW或精确全文件LF->RAWCRLF："+name)
        files.append(dict(path=name,sha256=expected,bytes=len(raw),git_blob_sha256=hashlib.sha256(blob).hexdigest(),git_relation="RAW_IDENTICAL" if same else "GIT_LF_TO_RAW_CRLF",git_native_command=command,git_native_exit_code=0))
    if phase=="before":
        require(not PROJECT.exists() and not REPORT.exists() and not PRE.exists(),"before要求新project/evidence/preflight")
        staged,_=git("diff","--cached","--name-only"); require(not staged.strip(),"暂存区未闭合")
        fresh(PRE,directory=True)
        fresh(REPORT,directory=True)
    else:
        exact(PROJECT,"directory"); exact(REPORT,"directory"); before=read(PRE/"source_before.json")
        require(before["source_commit"]==commit and {r["path"]:r["sha256"] for r in before["source_files"]}==hashes,"前后基线/源码不同")
    target=PRE/("source_snapshot" if phase=="before" else "source_snapshot_after"); fresh(target,directory=True)
    for row in files:
        dest=target/row["path"]; dest.parent.mkdir(parents=True,exist_ok=True)
        copied=rawcopy(ROOT/row["path"],dest); row["snapshot"]=copied["saved_path"]
    record=dict(schema_version=1,status="PASS_SOURCE_"+phase.upper()+"_ONLY",created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),source_commit=commit,actual_head_at_check=commit,source_freeze=rel(FREEZE),source_freeze_sha256=FREEZE_SHA,source_files=files,source_count=len(files),platform_static_source_count=len(static),source_sha256=hashes,static_source_sha256=static,frozen14_sha256=freeze["frozen14"],profile_version=profile["version"],clock_hz=50000000,visibility_parameter=0,project_dir=str(PROJECT),evidence_dir=str(REPORT),limitations=["仅源码和Git字节核验，不代表STA或实板通过。"])
    save(PRE/("source_"+phase+".json"),record)
    if phase=="after": save(CACHE/"static_actual_closed.json",dict(source_commit=commit,source_count=len(static),source_sha256=static))
    print(json.dumps(dict(status=record["status"],source_count=len(files),static_count=len(static),git_raw=sum(r["git_relation"]=="RAW_IDENTICAL" for r in files),git_eol=sum(r["git_relation"]!="RAW_IDENTICAL" for r in files),source_record=binding(PRE/("source_"+phase+".json"))),ensure_ascii=False))


def mcp_json(record):
    """保留原始CallToolResult和input/result包；不覆盖client错误。"""
    result=record.get("result",record)
    blocks=[b["text"] for b in result["content"] if b.get("type")=="text"]
    require(len(blocks)==1,"MCP文本不唯一")
    return json.loads(blocks[0])


def client_pair(item,label,call,allow_error=False):
    """client仍running只绑定移交，终态码来自实际关闭history；不补造客户端0。"""
    result=call.get("result",call)
    error=result.get("isError") is True
    if error:
        require(label=="wait" or allow_error,"非wait的MCP错误尚未关闭")
        return dict(client_timeout_or_error=True,client_running_handoff=False,client_exit_code=None)
    payload=mcp_json(call)
    if payload.get("status")=="running":
        require(label=="wait" and payload.get("command")==item["command"],"running移交只能对应同一真实wait")
        require(payload.get("session_id")==call.get("input",{}).get("session_id") and type(payload.get("session_id")) is str,"running移交session不同或未知")
        require(payload.get("exit_code") is None and type(item.get("code")) is int,"running client不得伪造终态；必须存在关闭history码")
        return dict(client_timeout_or_error=False,client_running_handoff=True,client_exit_code=None,client_running_payload=payload)
    code=payload.get("exit_code")
    require(type(code) is int and type(item.get("code")) is int and code==item["code"],"client/native码类型或值不同")
    return dict(client_timeout_or_error=False,client_running_handoff=False,client_exit_code=code)


def manifest_identifier(row):
    """仅转换清单相对标识符；真实文件系统路径仍由exact逐组件核验。"""
    require(type(row) is dict and type(row.get("path")) is str,"清单绑定格式不同")
    name=row["path"]
    require(not name.startswith(("/", "\\")) and ":" not in name,"清单标识符不得为绝对路径")
    parts=re.split(r"[/\\]",name)
    require(all(p not in ("", ".", "..") for p in parts),"清单标识符含空段或相对跳转")
    return dict(row,path="/".join(parts))


def expected_tool_bindings():
    """实际独审receipt冻结完整生产工具闭包，不借当前文件自封批准。"""
    review=read(compat_pins.pinned(compat_pins.TOOLS_G2,compat_pins.TOOLS_G2_SHA))
    require(review.get('status')==compat_pins.TOOLS_G2_EXPECTED_STATUS and review['status'].startswith('PASS'),'工具独审状态不同')
    declared=review.get('reviewed_tools');require(type(declared) is list,'工具独审缺完整reviewed_tools')
    actual=contract.capture_tools(WORK,ROOT)
    for row in actual:
        matches=[item for item in declared if item.get('path')==row['path']]
        require(matches==[row],'完整生产工具闭包未冻结或发生漂移：'+row['path'])
    return actual


def runtime_native_records(gate,commit=None):
    """实际包装逐项核全身份、工具及完整命令；失败原件拒绝伪作PASS。"""
    declarations=gate.get("native_wrappers")
    require(type(declarations) is list and bool(declarations),"关闭门禁缺显式native_wrappers")
    require(len(declarations)==len({r["path"] for r in declarations}),"实际包装声明重复")
    expected_tools=expected_tool_bindings()
    result=[]
    for row in declarations:
        path=exact(ROOT/row["path"])
        require(path.parent==CACHE and re.fullmatch(r"s15_runtime_[A-Za-z0-9_]+\.native\.json",path.name),"实际包装路径或prefix不同")
        require(binding(path)==row,"实际包装原件漂移")
        record=read(path)
        require(type(record) is dict and record.get("mode") in ("prepare","source","collect","seal"),"实际包装缺mode或schema未知")
        require(type(record.get("prefix")) is str and path.name==record["prefix"]+".native.json","实际包装prefix绑定不同")
        require(type(record.get("native_exit_code")) is int and type(record.get("command")) is list,"实际包装原生命令或退出码未知")
        require(record.get("direct_child_wait_returned") is True and type(record.get("closed_logs")) is list and len(record["closed_logs"])==2,"实际包装未直接wait闭合")
        command=record['command'];require(command[:6]==[sys.executable,'-X','utf8','-B',str(WORK/'collector.py'),record['mode']],'实际包装命令与mode/工具不同')
        parsed=contract.collector_arguments(command[5:]);options=parsed['options']
        if record['mode']!='prepare':
            require(options['--commit']==(commit if commit is not None else compat_pins.SOURCE_COMMIT),'实际包装完整argv commit不同')
        prefix=record['prefix']
        possible_wrappers=[
            [sys.executable,'-X','utf8','-B',str(WORK/'native.py'),'--prefix',prefix,'--',*command[5:]],
            [sys.executable,'-X','utf8','-B',str(WORK/'native_capture.py'),prefix,*command],
        ]
        require(record.get('wrapper_command') in possible_wrappers,'实际wrapper完整argv不同')
        logs=[binding(exact(CACHE/(prefix+'.'+suffix))) for suffix in ('stdout.bin','stderr.bin')]
        runtime_config=compat_pins.runtime_config_binding()
        native_python=compat_pins.validate_native_python_pin(compat_pins.NATIVE_PYTHON,compat_pins.NATIVE_PYTHON_SHA256)
        contract.validate_capture(record,command,record['wrapper_command'],str(ROOT),expected_tools,prefix,logs,runtime_config,native_python)
        require(record.get('capture_target_kind')=='COLLECTOR','通用canary不得伪作实际collector')
        if record['mode']=='source' and record['native_exit_code']==0:
            source_row=gate.get('source_'+options['--phase'])
            require(record.get('source_output')==source_row and binding(ROOT/source_row['path'])==source_row,'实际source phase输出与gate不同')
            require(read(ROOT/source_row['path']).get('source_commit')==(commit if commit is not None else compat_pins.SOURCE_COMMIT),'实际source phase输出commit不同')
        if record['mode']=='collect':
            consumed=binding(exact(Path(options['--gate'])))
            require(record.get('consumed_gate')==consumed and record.get('consumed_gate_after')==consumed,'实际collect消费gate字节不同')
            if record['native_exit_code']==0:
                require(record.get('collection_summary')==binding(REPORT/'s15_collection_summary.json'),'实际collect输出summary字节不同')
        result.append((path,record))
    return result


def validate_collect_chain(summary,seal_gate,records,commit):
    """collect消费不可改gate_r01，seal的新gate只扩展原生闭合列表。"""
    successes=[record for _,record in records if record['mode']=='collect' and record['native_exit_code']==0 and record['wrapper_exit_code']==0]
    require(len(successes)==1,'缺唯一成功的真实collect包装')
    record=successes[0];options=contract.collector_arguments(record['command'][5:])['options']
    consumed_path=exact(Path(options['--gate']));consumed_binding=binding(consumed_path)
    require(summary.get('source_commit')==commit and summary.get('root_gate')==consumed_binding,'summary未绑定实际消费的SOURCE/gate字节')
    require(record.get('consumed_gate')==consumed_binding and record.get('consumed_gate_after')==consumed_binding,'原生capture消费gate前后不同')
    consumed_gate=closed_gate(consumed_path,commit)
    require(summary.get('closed_gate_inputs')==consumed_gate,'summary SOURCE/config/MCP九命令/闭合文件来自其他gate')
    original={key:value for key,value in consumed_gate.items() if key!='native_wrappers'}
    extended={key:value for key,value in seal_gate.items() if key!='native_wrappers'}
    require(original==extended,'新seal gate改动SOURCE/config/MCP/已闭合原件或其他字段')
    old=consumed_gate.get('native_wrappers',[]);new=seal_gate.get('native_wrappers',[])
    require(type(old) is list and type(new) is list and all(row in new for row in old),'seal gate仅可显式扩展native列表')
    require(any(row==binding(next(path for path,item in records if item is record)) for row in new),'seal gate缺实际collect包装绑定')
    require(record.get('collection_summary')==binding(REPORT/'s15_collection_summary.json'),'collect输出summary不是当前原字节')
    return dict(consumed_gate=consumed_binding,collection_summary=record['collection_summary'],native_record=binding(next(path for path,item in records if item is record)))


def closed_gate(path,commit):
    """ROOT显式关闭声明与全部被声明原件按字节核验。"""
    compat_pins.require_ready()
    require_pinned_commit(commit)
    gate=read(path)
    require(gate.get("root_explicit_signal")=="CLOSED_INPUTS_READY" and gate.get("project_closed") is True and gate.get("source_commit")==commit,"ROOT关闭门禁不成立")
    require(gate.get("root_declared_products_execution_count")==1 and gate.get("root_declared_synthesis_execution_count")==1,"未确认products/synth只执行一次")
    for key in ("preparation_receipt","source_before","source_after","static_source_closed","immutable_session_log","mcp_history","runtime_config"):
        row=gate[key]; require(binding(ROOT/row["path"])==row,"闭合原件漂移："+key)
    for key in ("design_mcp_records","additional_closed_files","approved_evidence"):
        rows=[manifest_identifier(r) for r in gate.get(key,[])] if key=="approved_evidence" else gate.get(key,[])
        if key=="approved_evidence": gate[key]=rows
        for row in rows:
            actual=binding(ROOT/row["path"])
            require(all(actual[k]==row[k] for k in actual),"声明原件漂移："+row["path"])
    require(sha(FREEZE)==FREEZE_SHA,"freeze漂移")
    require(gate["runtime_config"]==compat_pins.runtime_config_binding(),"ROOT关闭配置与当前原字节不同")
    require_pinned_commit(read(FREEZE).get("source_commit"))
    for key in ("source_before","source_after"):
        require_pinned_commit(read(ROOT/gate[key]["path"]).get("source_commit"))
    require([r["label"] for r in gate["design_mcp_records"]]==list(LABELS),"实际九design命令声明不同")
    return gate


def first(pattern,text):
    """实际报告字段缺失立即停止，不以旧报告补齐。"""
    found=re.findall(pattern,text,re.M); require(bool(found),"报告字段缺失："+pattern)
    return found[0].strip()


def collect(commit,gate_path):
    """关闭后收集本轮实际原件，状态和资源均从本轮读取。"""
    compat_pins.require_ready()
    require_pinned_commit(commit)
    gate=closed_gate(gate_path,commit); exact(REPORT,"directory")
    preparation=read(ROOT/gate["preparation_receipt"]["path"])
    for row in preparation["prepared_scripts"]: require(binding(ROOT/row["path"])==row,"实际收集脚本不是最终准备版本")
    require(sha(FREEZE)==FREEZE_SHA,"freeze漂移")
    before,after=read(ROOT/gate["source_before"]["path"]),read(ROOT/gate["source_after"]["path"])
    static=read(ROOT/gate["static_source_closed"]["path"]); freeze=read(FREEZE)
    require_pinned_commit(freeze.get("source_commit"))
    hashes={r["path"]:r["sha256"] for r in freeze["source_files"]}
    require(before["source_commit"]==after["source_commit"]==static["source_commit"]==commit,"关闭源码提交不同")
    require(before["source_freeze_sha256"]==after["source_freeze_sha256"]==FREEZE_SHA,"前后冻结入口不同")
    require(before["source_sha256"]==after["source_sha256"]==hashes and before["frozen14_sha256"]==after["frozen14_sha256"]==freeze["frozen14"],"源码前后或原14漂移")
    require(static["source_sha256"]==after["static_source_sha256"] and static["source_count"]==len(static["source_sha256"]),"static来源集合不同")
    for record in (before,after):
        require({r["path"]:r["sha256"] for r in record["source_files"]}==hashes,"前后source_files集合不同")
        for row in record["source_files"]: require(sha(ROOT/row["snapshot"])==row["sha256"],"源码快照漂移")
    profile=read(ROOT/next(r["snapshot"] for r in after["source_files"] if r["path"]=="board/s2b_inference_platform.json"))
    require(profile["version"]=="s2b-inference-platform/0.1.15" and profile["clock_hz"]==50000000 and profile["visibility_default"]==0,"实际profile不同")
    initial=[binding(p) for p in sorted(REPORT.rglob("*")) if p.is_file()]
    save(REPORT/"s15_original_inventory.json",dict(files=initial))
    code=fresh(REPORT/"collector_code",directory=True)
    for path in (WORK/"collector.py",WORK/"native.py",WORK/"compat_pins.py",compat_pins.RUNTIME_CONFIG,ROOT/gate["preparation_receipt"]["path"],CLASSIFIER): rawcopy(path,code/path.name)
    for path in sorted(WORK.glob("s15_preparation_r01.*")): rawcopy(path,code/path.name)
    require(sha(CLASSIFIER)==CLASSIFIER_SHA,"classifier原字节漂移")
    closed=fresh(REPORT/"mcp_closed",directory=True); copied={}
    declarations=[gate[k] for k in ("source_before","source_after","static_source_closed","immutable_session_log","mcp_history")]+gate["design_mcp_records"]+gate.get("additional_closed_files",[])
    for row in declarations:
        source=exact(ROOT/row["path"])
        if source.name in copied: require(copied[source.name]["original_path"]==row["path"],"关闭输入同名冲突"); continue
        copied[source.name]=rawcopy(source,closed/source.name)
    history=mcp_json(read(ROOT/gate["mcp_history"]["path"]))["history"]
    require(len(history)==len(LABELS),"设计history数量不同")
    paired=[]
    for item,row in zip(history,gate["design_mcp_records"]):
        call=read(ROOT/row["path"]); result=call.get("result",call)
        if "input" in call: require(call["input"]["command"]==item["command"],"client/history命令不同")
        client=client_pair(item,row["label"],call)
        paired.append(dict(label=row["label"],client_record=row,client_timeout=client["client_timeout_or_error"],native_history=item,client_input_captured="input" in call,**client))
    require(paired[-1]["native_history"]["command"]=="close_project" and paired[-1]["native_history"]["code"]==0,"原生工程尚未关闭")
    by_label={row["label"]:row["native_history"] for row in paired}
    for label in ("source","setup","launch","wait","open_run","reports","query_xdc","close"):
        require(by_label[label]["code"]==0,"原生控制命令失败："+label)
    states=by_label["query_xdc"]["output"]
    require(states.count("status {synth_design Complete!} progress 100%")==5 and states.count("status {Not started} progress 0%")==5 and "clock_period 20.000" in states,"真实run状态/时钟不同")
    native=fresh(REPORT/"native_jobs",directory=True); runroot=exact(PROJECT/"s2b_inference_candidate.runs","directory")
    directories=sorted(p for p in runroot.iterdir() if p.is_dir() and p.name!=".jobs")
    require(len(directories)==5,"实际native任务不是五个")
    mappings=[]; jobs=[]
    allowed=(".tcl",".log",".jou",".vds",".xdc",".rpt",".rst",".js",".sh",".bat",".xml")
    for directory in directories:
        target=fresh(native/("wrapper_native_s15_r01" if directory.name=="synth_1" else directory.name),directory=True)
        log=exact(directory/"runme.log").read_text(encoding="utf-8")
        require("synth_design completed successfully" in log and "0 Critical Warnings and 0 Errors encountered" in log,"native日志不是成功结束")
        require((directory/"__synthesis_is_complete__").is_file() and (directory/".vivado.end.rst").is_file() and not (directory/".vivado.error.rst").exists(),"native结束marker不同")
        for p in sorted(directory.iterdir()):
            if p.is_file() and (p.suffix in allowed or p.name in ("htr.txt","__synthesis_is_complete__")): mappings.append(rawcopy(p,target/p.name))
        process=ET.fromstring(exact(directory/".vivado.begin.rst").read_bytes()).find("Process"); require(process is not None,"launcher记录缺失")
        elapsed=first(r"synth_design:.*?elapsed = (\d+:\d+:\d+)",log)
        peaks=re.findall(r"peak = ([0-9.]+)",log); diag=re.findall(r"(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered",log)
        jobs.append(dict(run=directory.name,status="NATIVE_SYNTH_COMPLETED_LOG_AND_MARKERS",launcher_pid=int(process.attrib["Pid"]),launcher_command=process.attrib["Command"],synth_elapsed_seconds=sum(int(v)*m for v,m in zip(elapsed.split(":"),(3600,60,1))),reported_single_process_peak_mb=max(map(float,peaks)) if peaks else None,process_tree_peak_memory_bytes=None,raw_os_process_exit_code=None,os_exit_code_reason="OS子进程返回码未直接捕获；日志/marker/history分别保留，不补造0。",final_diagnostics=dict(zip(("infos","warnings","critical_warnings","errors"),map(int,diag[-1])))))
    require(sum(Path(r["saved_path"]).suffix==".vds" for r in mappings)==5,"VDS原件不是五个")
    infer=exact(native/"s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl").read_text(encoding="utf-8")
    block=first(r"read_verilog -library xil_defaultlib -sv \{([^}]+)\}",infer)
    compiled=[Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
    require(len(compiled)==len(set(compiled))==18 and set(compiled)==set(profile["rtl_sources"]),"native编译18不同")
    generated=fresh(REPORT/"generated_inputs",directory=True); genroot=exact(PROJECT/"s2b_inference_candidate.gen/sources_1/bd/s2b_inference","directory")
    constraints=sorted(genroot.rglob("*.xdc"))+sorted(runroot.rglob("*_propImpl.xdc"))
    require(constraints and len({p.name for p in constraints})==len(constraints),"生成XDC同名或缺失")
    for p in constraints: mappings.append(rawcopy(p,generated/p.name))
    wrapper=exact(PROJECT/"s2b_inference_candidate.srcs/sources_1/imports/hdl/s2b_inference_wrapper.v")
    require(sha(wrapper)==sha(genroot/"hdl/s2b_inference_wrapper.v"),"唯一wrapper字节不同")
    for p in (wrapper,genroot/"synth/s2b_inference.v",genroot/"ip/s2b_inference_infer_0/synth/s2b_inference_infer_0.sv"): mappings.append(rawcopy(p,generated/p.name))
    require(wrapper.as_posix() in (native/"wrapper_native_s15_r01/s2b_inference_wrapper.tcl").read_text(encoding="utf-8"),"原生wrapper不是已登记唯一import对象")
    require("wrapper "+wrapper.as_posix()+" top s2b_inference_wrapper" in exact(REPORT/"setup_synthesis.tcldict").read_text(encoding="utf-8"),"setup唯一importwrapper记录不同")
    xsa=exact(REPORT/"s2b_inference_no_bit.xsa"); oldxsa=exact(ROOT/"report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa")
    members=[]
    with zipfile.ZipFile(oldxsa) as old,zipfile.ZipFile(xsa) as new:
        require(new.testzip() is None and not any(n.endswith(".bit") for n in new.namelist()),"XSA CRC或无bit范围不同")
        for name in ("ps7_init.c","ps7_init.h","ps7_init.html","ps7_init.tcl","ps7_init_gpl.c","ps7_init_gpl.h","s2b_inference.hwh"):
            a,b=old.read(name),new.read(name)
            row=dict(member=name,old_sha256=hashlib.sha256(a).hexdigest(),new_sha256=hashlib.sha256(b).hexdigest(),raw_equal=a==b,old_bytes=len(a),new_bytes=len(b),crc32=new.getinfo(name).CRC)
            require(zlib.crc32(b)==row["crc32"],"XSA成员CRC不同")
            if name.startswith("ps7_init"):
                original=exact(genroot/"ip/s2b_inference_ps7_0"/name); require(original.read_bytes()==b,"生成PSinit与XSA成员不同")
                row["generated_original"]=binding(original); mappings.append(rawcopy(original,generated/name))
            else:
                with fresh(generated/name).open("xb") as stream: stream.write(b)
            members.append(row)
        for name in ("hwdef.xml","xsa.json","xsa.xml"):
            with fresh(generated/name).open("xb") as stream: stream.write(new.read(name))
    products=exact(REPORT/"products.tcldict").read_text(encoding="utf-8")
    products_native=int(first(r"\bcode (\d+)\b",products)); products_capture=1 if "status FAIL" in products else 0 if "status OK" in products else None
    require(products_capture is not None,"products capture状态缺失")
    save(REPORT/"s15_source_binding.json",dict(source_commit=commit,source_count=len(hashes),static_count=len(static["source_sha256"]),extra_paths=sorted(set(hashes)-set(static["source_sha256"])),before=gate["source_before"],after=gate["source_after"],freeze=binding(FREEZE),frozen14=freeze["frozen14"],compiled_rtl=compiled,git_raw_count=sum(r["git_relation"]=="RAW_IDENTICAL" for r in after["source_files"]),git_exact_eol_count=sum(r["git_relation"]=="GIT_LF_TO_RAW_CRLF" for r in after["source_files"])))
    save(REPORT/"s15_native_mapping.json",dict(files=mappings,jobs=jobs,compiled_rtl=compiled,native_job_count=5,native_vds_count=5,generated_xdc_count=len(constraints),cache_excluded="不复制EXE/obj/DCP/PB/WDF/cache；生成目录改用generated_inputs/native_jobs。"))
    save(REPORT/"s15_mcp_binding.json",dict(paired_calls=paired,design_execute_calls=len(paired),products_native_exit_code=products_native,products_capture_exit_code=products_capture,products_warning_before=re.findall(r"native_counts_before \{WARNING (\d+)",products),products_warning_after=re.findall(r"native_counts_after \{WARNING (\d+)",products),products_repeated=False,all_host_tool_calls=None))
    save(REPORT/"s15_xsa_comparison.json",dict(old_xsa=binding(oldxsa),new_xsa=binding(xsa),members=members,six_psinit_equal=all(r["raw_equal"] for r in members[:6]),hwh_raw_equal=members[6]["raw_equal"],runtime_elf_bsp_compatibility="NOT_APPROVED",hardware="NOT_RUN"))
    command=[sys.executable,"-X","utf8","-B",str(CLASSIFIER),"--report",str(REPORT/"timing_summary_synth.rpt"),"--result",str(REPORT/"s15_sta_result.json")]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=45)
    for suffix,data in (("stdout.log",result.stdout),("stderr.log",result.stderr)):
        with fresh(REPORT/("s15_sta_classifier."+suffix)).open("xb") as stream: stream.write(data)
    save(REPORT/"s15_sta_classifier.native.json",dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=result.returncode,classifier=binding(CLASSIFIER),peak_memory_bytes=None))
    require(result.returncode in (0,2),"STA输入解析失败；原件保留")
    sta=read(REPORT/"s15_sta_result.json"); require(sta["native_exit_code"]==result.returncode,"STA原生码不同")
    xdc=exact(REPORT/"constraints_synth.xdc").read_text(encoding="utf-8")
    require("create_clock -period 20.000 -name clk_fpga_0" in xdc,"实际约束不是50MHz")
    falsepaths=re.findall(r"current_instance ([^\r\n]+)\r?\n(set_false_path[^\r\n]+)",xdc)
    require(len(falsepaths)==2 and all("rst_fclk0/U0/EXT_LPF/" in scope and "syncstages_ff_reg[0]" in command for scope,command in falsepaths),"实际新增或改变时序例外")
    save(REPORT/"s15_constraints_binding.json",dict(clock=sta["clock"],check_timing=sta["check_timing"],exported_false_paths=[dict(scope=s,command=c) for s,c in falsepaths],false_path_count=len(falsepaths),exceptions_report=binding(REPORT/"exceptions_synth.rpt")))
    util=exact(REPORT/"utilization_flat_synth.rpt").read_text(encoding="utf-8")
    resources={key:float(first(r"^\|\s*"+re.escape(label)+r"\s*\|\s*(\d+(?:\.\d+)?)\s*\|",util)) for key,label in (("lut","Slice LUTs*"),("ff","Slice Registers"),("bram","Block RAM Tile"),("dsp","DSPs"),("latch","Register as Latch"))}
    worst=exact(REPORT/"timing_worst_synth.rpt").read_text(encoding="utf-8")
    path=dict(source=first(r"^\s*Source:\s*(\S+)",worst),destination=first(r"^\s*Destination:\s*(\S+)",worst),logic_levels=first(r"^\s*Logic Levels:\s*(.+)",worst),data_path_delay_ns=float(first(r"^\s*Data Path Delay:\s*([\d.]+)ns",worst)),speed_file=first(r"^\| Speed File\s*:\s*(.+)",worst))
    for row in initial: require(binding(ROOT/row["path"])==row,"ROOT原件在收集时漂移")
    save(REPORT/"s15_collection_summary.json",dict(status="COLLECTED_S15_"+sta["status"]+"_PENDING_INDEPENDENT_REVIEW",source_commit=commit,profile=profile["version"],source_count=len(hashes),static_count=len(static["source_sha256"]),active_rtl_count=18,original_raw_inventory=initial,closed_input_mapping=list(copied.values()),timing=sta,resources=resources,worst_path=path,native_jobs=jobs,products_native_exit_code=products_native,products_capture_exit_code=products_capture,sta_native_exit_code=result.returncode,root_gate=binding(gate_path),closed_gate_inputs=gate,independent_review="NOT_RUN",implementation="NOT_RUN",postroute="NOT_RUN",hardware="NOT_RUN",limitations=["仅实际综合态STA，不代表-1/postroute或G3；精确speed_file保留。","products native/capture与客户端/nativewait分开，不重跑products或重复登记wrapper。","原生五任务OS退出码未捕获为null；日志与marker不是OS返回码。","单进程日志峰不是进程树峰，未取得字段为null。","六PSinit与HWH按实际字节关系报告，不继承旧ELF/BSP兼容批准。"] ))
    print(json.dumps(dict(status="COLLECTED_S15",sta=sta["status"],native_classifier_exit_code=result.returncode,source_count=len(hashes),static_count=len(static["source_sha256"])),ensure_ascii=False))


def seal(commit,gate_path):
    """只封包已闭合结果；不伪造当前collector或审查成功码。"""
    compat_pins.require_ready()
    require_pinned_commit(commit)
    gate=closed_gate(gate_path,commit); summary=read(REPORT/"s15_collection_summary.json")
    require(summary["source_commit"]==commit,"封包基线不同")
    profile_version=read(FREEZE)["profile"]
    require(profile_version=="s2b-inference-platform/0.1.15","封包实际冻结profile不同")
    validated_records=runtime_native_records(gate,commit)
    chain=validate_collect_chain(summary,gate,validated_records,commit)
    save(REPORT/'collect_gate_chain.json',chain)
    native_dir=fresh(REPORT/"native_closed",directory=True); native_records=[]
    for path,record in validated_records:
        native_records.append(record); rawcopy(path,native_dir/path.name)
        for row in record.get("closed_logs",[]): rawcopy(ROOT/row["path"],native_dir/Path(row["path"]).name)
    require(any(r.get("mode")=="collect" and r["native_exit_code"]==0 for r in native_records),"collect原生包装尚未闭合或失败")
    for phase in ("before","after"):
        require(any(r.get("mode")=="source" and r["native_exit_code"]==0 and "--phase" in r["command"] and r["command"][r["command"].index("--phase")+1]==phase and "--commit" in r["command"] and r["command"][r["command"].index("--commit")+1]==commit for r in native_records),"缺少本次真实source原生闭合："+phase)
    reference=read(ROOT/"report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_delivery_manifest_r03.json")
    interfaces=reference["interfaces"]
    for row in interfaces: require(sha(ROOT/row["path"])==row["sha256"],"接口文档漂移")
    files=[]
    for p in sorted(REPORT.rglob("*")):
        if not p.is_file(): continue
        role="source" if p.suffix in (".py",".sv",".v",".tcl",".xdc",".c",".h",".sh",".bat",".js") else "log" if p.suffix in (".log",".rpt",".vds",".jou") else "artifact" if p.suffix in (".xsa",".rst") or p.name=="__synthesis_is_complete__" else "result"
        files.append(dict(path=rel(p),sha256=sha(p),role=role))
    for phase in ("source_before","source_after"):
        for row in read(ROOT/gate[phase]["path"])["source_files"]: files.append(dict(path=row["snapshot"],sha256=row["sha256"],role="source"))
    externals=list(dict.fromkeys([FREEZE,CLASSIFIER]+[ROOT/r["path"] for r in gate.get("approved_evidence",[])]))
    files += [dict(path=rel(p),sha256=sha(p),role="input") for p in externals]
    require(len(files)==len({r["path"] for r in files}),"清单路径重复")
    checks=[]
    for record in native_records:
        checks.append(dict(name="实际原生包装："+record["mode"]+":"+record["prefix"],status="PASS" if record["native_exit_code"]==0 and record['wrapper_exit_code']==0 else "FAIL",command=subprocess.list2cmdline(record["command"]),exit_code=record['wrapper_exit_code'],reason=record['capture_status']+"；真实wrapper和child状态均已核，非G2或板上批准。"))
    classifier=read(REPORT/"s15_sta_classifier.native.json")
    checks.append(dict(name="50MHz综合态STA分类",status="PASS" if classifier["native_exit_code"]==0 else "FAIL",command=classifier["windows_command"],exit_code=classifier["native_exit_code"],reason=summary["timing"]["status"]))
    for name in ("独立实际证据审查","实现及postroute","G3板上cache/模型/109/1000任务"):
        checks.append(dict(name=name,status="NOT_RUN",command=None,exit_code=None,reason="collector只归档原件，此项尚未执行。"))
    manifest=dict(schema_version=1,stage="2B",task_id="S2B-T17",run_id=REPORT.name,source_commit=commit,evidence_dir=rel(REPORT),interfaces=interfaces,tool_versions=dict(python=sys.version,Vivado="实际原生日志版本；未运行新版本查询",profile=profile_version),files=files,checks=checks,limitations=summary["limitations"])
    save(REPORT/"s15_delivery_manifest.json",manifest)
    print(json.dumps(dict(status="SEALED_ONLY_NOT_APPROVED",manifest=binding(REPORT/"s15_delivery_manifest.json"),next_command=[sys.executable,"-X","utf8","-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode","evidence","--manifest",str(REPORT/"s15_delivery_manifest.json")]),ensure_ascii=False))


def main():
    """参数区分准备与真实前后/关闭收集，缺失提交或门禁立即拒绝。"""
    parser=argparse.ArgumentParser(); parser.add_argument("mode",choices=("prepare","source","collect","seal"))
    parser.add_argument("--commit"); parser.add_argument("--phase",choices=("before","after")); parser.add_argument("--gate",type=Path)
    parser.add_argument("--receipt",default="prepared_receipt.json")
    args=parser.parse_args()
    if args.mode=="prepare": return prepare(args.receipt)
    require(args.commit and re.fullmatch(r"[0-9a-f]{40}",args.commit),"必须传入ROOT实际提交")
    if args.mode=="source": require(args.phase is not None,"缺少source阶段"); return source(args.commit,args.phase)
    require(args.gate is not None,"缺少ROOT明确关闭门禁")
    return collect(args.commit,args.gate) if args.mode=="collect" else seal(args.commit,args.gate)


if __name__=="__main__":
    main()

