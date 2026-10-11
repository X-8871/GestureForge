#!/usr/bin/env python3
"""只在新r08证据中纠正r01原生退出码口径；继承原绑定，不复制模型。"""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
PREVIOUS=ROOT/"report/evidence/S2B-T17/length_guard_20261011_r07"
EVIDENCE=ROOT/"report/evidence/S2B-T17/length_guard_20261011_r08"
def digest(path):
    """原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    """明确UTF-8读取JSON。"""
    return json.loads(path.read_text(encoding="utf-8"))
def write(path,data):
    """仅创建新文件，不覆盖任何原件。"""
    if path.exists():raise ValueError("禁止覆盖："+str(path))
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
def binding(path):
    """只返回已有文件绑定，不复制文件。"""
    if not path.is_file() or path.is_symlink():raise ValueError("精确来源文件缺失")
    return {"path":path.relative_to(ROOT).as_posix(),"sha256":digest(path)}

original_manifest=PREVIOUS/"delivery_manifest_r02.json"
original_freeze=PREVIOUS/"source_freeze.json"
if digest(original_manifest)!="9a672647c2c4dbb7171e27372ff295a326f1cae835545fb4d947add2d22c2746":raise ValueError("原r07清单漂移")
if digest(original_freeze)!="57a0f293e800802b00367ec4b2d8a131310a803825598f773ea19da4ff5be6b4":raise ValueError("原38源冻结漂移")
freeze=read(original_freeze);old_manifest=read(original_manifest)
for path,sha in freeze["source_sha256"].items():
    if digest(ROOT/path)!=sha:raise ValueError("STOP源码漂移："+path)
for row in old_manifest["files"]:
    if digest(ROOT/row["path"])!=row["sha256"]:raise ValueError("旧绑定漂移："+row["path"])

r01=ROOT/"report/evidence/S2B-T17/length_guard_20261011_r01/validation.json"
r01_source=ROOT/"report/evidence/S2B-T17/length_guard_20261011_r01/source_snapshot/verification/test_s2b_conv_validation_rtl.py"
boundary_capture=ROOT/"report/evidence/S2B-T17/length_guard_20261011_r02/boundary_native.json"
r04_capture=ROOT/"report/evidence/S2B-T17/length_guard_20261011_r02/layer0_native.json"
record=read(r01);boundary=read(boundary_capture);r04=read(r04_capture)
if record["status"]!="FAIL" or record["runs"] or record["error"]!="ValueError('可用内存不足')":raise ValueError("r01失败事实不符")
if "length_guard_20261011_r03" not in boundary["command"] or boundary["native_exit_code"]!=0:raise ValueError("boundary捕获实际未绑定r03")
if "length_guard_20261011_r04" not in r04["command"] or r04["native_exit_code"]!=2:raise ValueError("r04捕获来源不符")
source_text=r01_source.read_text(encoding="utf-8")
expected_return='return 0 if report["status"] in ("PASS","PREPARED_NOT_RUN") else 2'
if source_text.count(expected_return)!=1:raise ValueError("r01源码推断路径不符")
write(EVIDENCE/"r01_native_exit_correction.json",{
    "schema_version":1,"task_id":"S2B-T17-S6","scope":"只纠正证据口径，不改变实现、G1结果或原始失败事实",
    "r01":{"business_status":"FAIL_RESOURCE_PREFLIGHT","validation_binding":binding(r01),
        "observed_error":record["error"],"compile_or_simulation_runs":[],"replayed":False,
        "native_exit_code":None,"native_exit_capture_status":"NOT_CAPTURED",
        "host_exit_code":1,"host_exit_source":{"kind":"本会话exec_command返回元数据的明确转录，不是原生capture",
            "chunk_id":"4acff6","exit_code":1,"wall_time_seconds":3.3090612},
        "expected_or_inferred_native_exit_code":2,"inference_source":{"snapshot":binding(r01_source),"return_expression":expected_return,
            "basis":"已保存status=FAIL，源码末尾对应return2；未直接捕获原生退出，不能升级为实测native2"}},
    "separate_captures":{"boundary_native":{**binding(boundary_capture),"actual_run_id":"length_guard_20261011_r03","native_exit_code":0,
        "relation":"此捕获属于r03，不属于r01"},"layer0_native":{**binding(r04_capture),"actual_run_id":"length_guard_20261011_r04","native_exit_code":2,
        "relation":"r04有直接捕获，不能覆盖r01未知值"}},
    "format_basis":{"checker":binding(ROOT/"verification/check_stage_delivery.py"),"function":"_check_check",
        "rules":"FAIL要求真实非零整数exit_code；NOT_RUN要求exit_code=null。r01原生捕获未执行，因此仅捕获条目用NOT_RUN/null；运行失败事实另行明确保存。"},
    "superseded_claims":[{"file":binding(PREVIOUS/"delivery_manifest_r02.json"),"location":"checks/name=historical_ram_preflight_r01",
        "incorrect":"status=FAIL/exit_code=2及真实脚本返回2误称实际捕获"},
        {"file":binding(PREVIOUS/"g1_summary.json"),"location":"checks/name=historical_ram_preflight_r01","incorrect":"同上"},
        {"file":binding(PREVIOUS/"tools/pack_delivery.py"),"location":"硬编码历史r01 checks条目","incorrect":"把源码推断2写入native退出码字段"}],
    "original_artifacts_unchanged":True,"nine_project_sources_unchanged":True})

reason="r01运行已因可用内存不足失败；原生退出码捕获未执行，故仅捕获条目NOT_RUN/null。宿主exec1与源码推断2来源分别见r01_native_exit_correction.json；两者均不冒充实测native。未重跑r01，r04真实2不覆盖r01。"
def correct_checks(checks):
    """只替换错误的退出捕获条目；其他真实测试原样保留。"""
    result=copy.deepcopy(checks);matches=[i for i,row in enumerate(result) if row["name"]=="historical_ram_preflight_r01"]
    if len(matches)!=1:raise ValueError("旧r01条目不唯一")
    result[matches[0]]={"name":"historical_r01_native_exit_capture","status":"NOT_RUN","command":None,"exit_code":None,"reason":reason}
    return result
summary=read(PREVIOUS/"g1_summary.json");summary["checks"]=correct_checks(summary["checks"])
summary["limitations"]=[row for row in summary["limitations"] if "r01/r04资源门禁失败" not in row]+[reason]
summary["evidence_correction"]={"previous_summary":binding(PREVIOUS/"g1_summary.json"),"g1_status_unchanged":True,"scope":"r01原生退出码未捕获/null；没有新仿真"}
write(EVIDENCE/"g1_summary.json",summary)
freeze["run_id"]="length_guard_20261011_r08"
freeze["evidence_correction"]={"previous_source_freeze":binding(original_freeze),"same_source_sha256":True,"same_source_diff_sha256":True,
    "nine_sources_still_stopped":True,"g1_unchanged":True,"basis":"独审指出r01原生捕获不存在；仅证据口径纠正"}
write(EVIDENCE/"source_freeze.json",freeze)
write(EVIDENCE/"inherited_binding.json",{"previous_manifest":binding(original_manifest),"inherited_entries":len(old_manifest["files"]),
    "rechecked_original_hashes":True,"source_bindings":len(freeze["source_sha256"]),"static_bindings":freeze["static_binding_count"],
    "new_model_copy_bytes":0,"new_source_copy_bytes":0,"original_files_are_referenced_not_copied":True,
    "superseded_semantics":"旧文件保留原字节，仅其r01退出码解释由新correction/g1_summary替代；原始数值、周期与其他原生结果保持。"})
manifest=copy.deepcopy(old_manifest);manifest["run_id"]="length_guard_20261011_r08";manifest["evidence_dir"]=EVIDENCE.relative_to(ROOT).as_posix()
manifest["checks"]=correct_checks(manifest["checks"])
manifest["limitations"]=[row for row in manifest["limitations"] if "r01/r04资源门禁失败" not in row]+[reason]
manifest["files"].append({**binding(original_manifest),"role":"artifact"})
write(EVIDENCE/"manifest_base.json",manifest)
print(json.dumps({"status":"CORRECTED_EVIDENCE_ONLY","g1":summary["status"],"nine_sources_unchanged":True,
    "source_freeze_sha256":digest(EVIDENCE/"source_freeze.json"),"previous_manifest":binding(original_manifest)},ensure_ascii=False))
