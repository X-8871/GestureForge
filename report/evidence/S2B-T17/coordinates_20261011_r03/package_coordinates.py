#!/usr/bin/env python3
"""绑定实际S2来源、差异、既有不变引擎回归与本次真实RTL证据。"""
from pathlib import Path
from collections import Counter
import difflib
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent


def sha(path):
    """保存原始字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """只写本次证据，不改变工程文件或旧失败原件。"""
    validation=json.loads((EVIDENCE/"validation.json").read_text(encoding="utf-8"))
    if validation["status"]!="PASS_BACKEND_COORDINATES_G1": raise ValueError("实际RTL未通过")
    spec=importlib.util.spec_from_file_location("coordinates_checker",ROOT/"verification/check_s2b_inference_platform.py")
    checker=importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
    bindings=checker.check_static(ROOT)
    for relative,digest in validation["source_sha256_post"].items():
        if sha(ROOT/relative)!=digest: raise ValueError("待包装源变化")
    snapshot=EVIDENCE/"source_snapshot"
    if snapshot.exists(): raise ValueError("快照已存在，不覆盖")
    for relative in validation["source_sha256_post"]:
        target=snapshot/relative; target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/relative,target)
    s1=ROOT/"report/evidence/S2B-T17/s1_platform_20261011_r01/source_snapshot/src/s2b_network_backend.sv"
    original=EVIDENCE/"s1_network_backend.sv"
    if s1.read_bytes()!=original.read_bytes(): raise ValueError("旧RTL与真实S1综合raw快照不符")
    provenance={"status":"PASS_SOURCE_PROVENANCE","task_baseline_commit":validation["task_baseline_commit"],
        "s1_synthesis_raw_snapshot":{"path":s1.relative_to(ROOT).as_posix(),"sha256":sha(s1),"matches_compared_raw":True},
        "frozen14":{},"derived_diffs":[],"s1_to_s2_diffs":[],"unchanged_engine_regression":{},"warnings":{}}
    freeze="671f9cf494b92ce182b3f1542fefd0cfd4b209f5"
    for relative,expected in checker.FROZEN_CORE_SHA256.items():
        raw=(ROOT/relative).read_bytes(); blob=subprocess.check_output(["git","show",freeze+":"+relative],cwd=ROOT)
        if raw.replace(b"\r\n",b"\n")!=blob.replace(b"\r\n",b"\n"): raise ValueError("冻结Git来源变化")
        if not sha(ROOT/relative)==expected==validation["frozen14_sha256_pre"][relative]==validation["frozen14_sha256_post"][relative]:
            raise ValueError("原14源pre/post变化")
        provenance["frozen14"][relative]={"raw_sha256":expected,"freeze_git_blob_sha256":hashlib.sha256(blob).hexdigest(),"pre_post_unchanged":True}
    for source,(relative,replacements) in checker.DERIVATION_RULES.items():
        before=(ROOT/source).read_text(encoding="utf-8").replace("\r\n","\n"); after=(ROOT/relative).read_text(encoding="utf-8")
        provenance["derived_diffs"].append({"source":source,"path":relative,"sha256":sha(ROOT/relative),"allowed_replacements":replacements,
            "diff":"".join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),source,relative))})
    changed=("src/s2b_network_backend.sv","board/s2b_inference_platform.json","board/s2b_inference_platform.md",
        "vivado/s2b_inference_platform.tcl","verification/check_s2b_inference_platform.py")
    for relative in changed:
        before=subprocess.check_output(["git","show",validation["task_baseline_commit"]+":"+relative],cwd=ROOT).decode("utf-8")
        after=(ROOT/relative).read_text(encoding="utf-8")
        provenance["s1_to_s2_diffs"].append({"path":relative,"sha256":sha(ROOT/relative),
            "diff":"".join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),"S1/"+relative,"S2/"+relative))})
    # 原直接engine参数/长度/地址优先、raw0x80、错误及各状态abort回归可复用，实际源必须逐字一致。
    s1_validation=ROOT/"report/evidence/S2B-T17/specialization_20261011_r04/validation.json"
    prior=json.loads(s1_validation.read_text(encoding="utf-8"))
    engines=("src/s2b_maxpool_engine.sv","src/s2a_route_engine.sv","src/s2b_upsample_engine.sv",
        "src/int8_maxpool_geometry.sv","src/int8_maxpool_window.sv","src/int8_route_query.sv","src/int8_upsample_query.sv")
    unchanged={p:sha(ROOT/p) for p in engines}
    for relative,digest in unchanged.items():
        if prior["source_sha256_post"][relative]!=digest: raise ValueError("engine回归来源变化")
    if prior["status"]!="PASS_GEOMETRY_SPECIALIZATION_G1": raise ValueError("旧直接engine回归未通过")
    provenance["unchanged_engine_regression"]={"validation_path":s1_validation.relative_to(ROOT).as_posix(),"sha256":sha(s1_validation),
        "source_sha256":unchanged,"pool_vectors":prior["simulation_counts"]["pool"],"upsample_vectors":prior["simulation_counts"]["upsample"],
        "coverage":prior["coverage"],"scope":"未重新运行；复用已审S1真实source相同的直接engine异常协议证据。S2真实backend控制与全部非conv请求由本次RTL验证。"}
    warnings=[line for line in (EVIDENCE/"compile.log").read_text(encoding="utf-8").splitlines() if line.startswith("%Warning-")]
    provenance["warnings"]={"count":len(warnings),"classes":dict(Counter(line.split(":",1)[0] for line in warnings)),
        "tb_lines":[line for line in warnings if "tb_s2b_backend_coordinates.sv" in line],
        "stub_lines":[line for line in warnings if "convolution_stub.sv" in line],"all_lines":warnings,
        "policy":"全部Wall诊断原件保留。Wno-fatal不抑制分类警告；2条TB cast上下文WIDTHEXPAND及stub未使用pin如实披露，实际golden使用显式64位非负值，未声明零warning。"}
    (EVIDENCE/"provenance.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    records=[]; env=os.environ.copy(); env["PYTHONUTF8"]="1"
    for name,command in (("static_checker",[sys.executable,"-X","utf8","-B","verification/check_s2b_inference_platform.py"]),
                         ("diff_check",["git","diff","--check"])):
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (EVIDENCE/(name+".log")).write_bytes(result.stdout)
        records.append({"name":name,"command":command,"exit_code":result.returncode})
        if result.returncode: raise ValueError(name+"失败")
    (EVIDENCE/"packaging_checks.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    g0="docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
    physical="docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
    manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":EVIDENCE.name,
        "source_commit":validation["source_commit"],"evidence_dir":EVIDENCE.relative_to(ROOT).as_posix(),
        "interfaces":[{"name":"tiny416冻结模型数值及逻辑接口","version":"S2A-T01/G0","frozen":True,"path":g0,"sha256":sha(ROOT/g0)},
            {"name":"阶段2B物理接口候选","version":"s2b-physical-candidate/0.1.1","frozen":False,"path":physical,"sha256":sha(ROOT/physical)}],
        "files":[],"checks":[],"tool_versions":validation["tool_versions"],"limitations":validation["limitations"]+[
            "本轮S2仅Developer G1；G2待独立Reviewer，G3/新综合/STA/完整整网均NOT_RUN。",
            "prepare_r01原检查器漏physical版本断言、r01 SV实例名关键字、r02未定宽Q31 golden夹具停止均保留，不宣称设计失败或最终通过。",
            "r02授权清理仅可重建obj_dir；全部49文件hash/原命令/失败源和日志保留，正确r03干净重建。",
            "inputs包装预期2，不能借此降低物理候选未冻结或实际部署门槛。"]}
    for item in validation["runs"]+records:
        manifest["checks"].append({"name":item["name"],"status":"PASS","command":subprocess.list2cmdline(item["command"]),
                                  "exit_code":item["exit_code"],"reason":"真实原生退出码与原日志来源绑定。"})
    manifest["checks"].append({"name":"全坐标数学及真实RTL差分","status":"PASS",
        "command":"python -X utf8 -B verification/test_s2b_backend_coordinates_rtl.py --run-id "+EVIDENCE.name,"exit_code":0,
        "reason":"11,407,500原含%C坐标；4,980,736实际FF边界；15层5,234,944输出/12,286,976请求全部逐笔独立golden。"})
    for name,reason in (("G2独立审查","停止写入后总控安排固定源码证据独审。"),("50MHz综合及实现","需新独立项目，不能沿用S1失败STA。"),
        ("完整整网golden","本任务隔离卷积，未跑完整实际CONV计算整网。"),("G3实物验证","本任务不使用MCP或硬件。")):
        manifest["checks"].append({"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":reason})
    manifest_path=EVIDENCE/"delivery_manifest.json"
    def bind_files():
        manifest["files"]=[{"path":p,"sha256":digest,"role":"source"} for p,digest in validation["source_sha256_post"].items()]
        manifest["files"] += [{"path":p,"sha256":sha(ROOT/p),"role":"input"} for p in ("report/evidence/S2A-T01/tiny416_model_manifest.json",physical,s1_validation.relative_to(ROOT).as_posix(),s1.relative_to(ROOT).as_posix())]
        for path in sorted(EVIDENCE.rglob("*")):
            if path.is_file() and path!=manifest_path:
                role="source" if path.suffix in (".sv",".py") or snapshot in path.parents else "log" if path.suffix==".log" else "result"
                manifest["files"].append({"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path),"role":role})
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    bind_files(); codes=[]
    for mode,expected in (("evidence",0),("inputs",2)):
        command=[sys.executable,"-X","utf8","-B","verification/check_stage_delivery.py","--mode",mode,"--manifest",manifest_path.relative_to(ROOT).as_posix()]
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (EVIDENCE/("delivery_"+mode+".log")).write_bytes(result.stdout)
        codes.append({"command":command,"mode":mode,"native_exit_code":result.returncode,"expected_code":expected})
        if result.returncode!=expected: raise ValueError("包装退出码不同："+mode)
    (EVIDENCE/"delivery_native_codes.json").write_text(json.dumps(codes,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    bind_files()
    final=subprocess.run(codes[0]["command"],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if final.returncode!=0 or final.stdout!=(EVIDENCE/"delivery_evidence.log").read_bytes(): raise ValueError("最终包装不同")
    print(json.dumps({"status":provenance["status"],"manifest_sha256":sha(manifest_path),"source_files":len(bindings),"frozen14":len(provenance["frozen14"])},ensure_ascii=False))


if __name__=="__main__":
    main()
