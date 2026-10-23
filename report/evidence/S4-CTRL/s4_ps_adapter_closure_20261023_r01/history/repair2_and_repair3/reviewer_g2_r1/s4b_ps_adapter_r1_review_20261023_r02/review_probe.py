from pathlib import Path
from datetime import datetime, timedelta
from unittest import mock
import copy, hashlib, json, os, shutil, subprocess, sys, zipfile
ROOT=Path(r"D:\codex-worktrees\w4"); OUT=Path(os.environ["S4B_R1_EVIDENCE_DIR"]); sys.path.insert(0,str(ROOT))
PREP=ROOT/"tmp/4/S4-B-REAL-02B/s4b_ps_tensor_adapter_prepare_g2r1_20261023_r05/adapter_preparation.json"
ADAPTER=ROOT/"scripts/stage4_s4b/s4b_ps_tensor_adapter.py"; TEST=ROOT/"verification/test_s4b_ps_tensor_adapter.py"
FREEZE=ROOT/"report/evidence/S4-B/s4b_ps_adapter_g2_20261023_r02/frozen_sources.json"
R12=ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r12"
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def reject(fn):
    try: fn()
    except Exception as e:
        from scripts.stage4_s4b import s4b_ps_tensor_adapter as a
        return {"rejected":isinstance(e,a.AdapterError),"error_type":type(e).__name__,"error":str(e)}
    return {"rejected":False,"accepted":True}
OUT.mkdir(); td=OUT/"system_tmp"; td.mkdir()
before={str(p):sha(p) for p in (PREP,ADAPTER,TEST,FREEZE,R12/"delivery_manifest.json",R12/"s4b_ps_tensor_diagnostic.elf",R12/"s4b_ps_tensor_diagnostic.map")}
from scripts.stage4_s4b import s4b_ps_tensor_adapter as a
p=a.validate_preparation(PREP); d=p.data; ident=d["artifact_identity"]
res={"run_id":OUT.name,"TEMP":os.environ["TEMP"],"TMP":os.environ["TMP"],
"prepare":{"status":d["status"],"build_run_id":ident["build_run_id"],"identity_sha256":d["artifact_identity_sha256"],
"manifest":d["source_evidence"]["delivery_manifest"],"compiled_app":d["source_evidence"]["compiled_app_source"],
"frozen_2b_commit":d["source_evidence"]["frozen_2b_commit"],"tool_sources":d["source_evidence"]["frozen_tool_sources"]}}
art={}
for key,name in (("elf","s4b_ps_tensor_diagnostic.elf"),("map","s4b_ps_tensor_diagnostic.map")):
    art[key]=next(x for x in d["bindings"] if x.get("role")=="artifact" and Path(x["path"]).name==name)
assert ident["elf_sha256"]==sha(R12/"s4b_ps_tensor_diagnostic.elf")
assert ident["map_sha256"]==sha(R12/"s4b_ps_tensor_diagnostic.map")
assert ident["elf_sha256"]!=sha(ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.elf")
res["r12_artifact_bindings"]=art
mut=copy.deepcopy(d)
for row,path in ((next(x for x in mut["bindings"] if x.get("role")=="artifact" and x["path"].endswith(".elf")),ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.elf"),
                 (next(x for x in mut["bindings"] if x.get("role")=="artifact" and x["path"].endswith(".map")),ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.map")):
    row.update(path=str(path),sha256=sha(path),bytes=path.stat().st_size)
mut["artifact_identity"]["elf_sha256"]=sha(ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.elf")
mut["artifact_identity"]["map_sha256"]=sha(ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.map")
mut["artifact_identity_sha256"]=a.artifact_identity_sha256(mut["artifact_identity"])
res["r04_elf_map_rebinding"]=reject(lambda:a._verified_artifact_identity(a.PreparedRun(p.path,mut)))
mut=copy.deepcopy(d); fake=OUT/"forged_init.elf"; fake.write_bytes(b"R1 offline forged init payload")
for row in mut["bindings"]:
    if row.get("role")=="verified_recovery_init_elf" or (row.get("role")=="verified_recovery_bundle_member" and row.get("relative_path")==a.RECOVERY_INIT_MEMBER):
        row.update(path=str(fake),sha256=sha(fake),bytes=fake.stat().st_size)
mut["artifact_identity"]["init_elf_sha256"]=sha(fake); mut["artifact_identity_sha256"]=a.artifact_identity_sha256(mut["artifact_identity"])
res["forged_init_rebinding"]=reject(lambda:a._verified_artifact_identity(a.PreparedRun(p.path,mut)))
zrow=next(x for x in d["bindings"] if Path(x["path"]).name=="recovery_bundle.zip")
zsrc=Path(zrow["path"]); zcopy=OUT/"recovery_with_unlisted_member.zip"; shutil.copyfile(zsrc,zcopy)
with zipfile.ZipFile(zcopy,"a",compression=zipfile.ZIP_DEFLATED) as z: z.writestr("bundle/workspace/ps7/export/ps7/sw/cpu0/lib/r1_unlisted.a",b"offline extra")
bm=Path(d["source_evidence"]["bundle_manifest"]["path"])
extracted=ROOT/"tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r12/bundle_extract"
app=Path(d["source_evidence"]["compiled_app_source"]["path"])
tc=next(Path(x["path"]) for x in d["bindings"] if x.get("role")=="source" and x["path"].endswith("s4b_ps_trace.c"))
th=next(Path(x["path"]) for x in d["bindings"] if x.get("role")=="source" and x["path"].endswith("s4b_ps_trace.h"))
over={"bundle/workspace/infer/src/s2b_inference_app.c":app.read_bytes(),"bundle/workspace/infer/src/s4b_ps_trace.c":tc.read_bytes(),
"bundle/workspace/infer/src/s4b_ps_trace.h":th.read_bytes(),
"bundle/workspace/infer/src/s4b_ps_build_config.h":("#ifndef S4B_PS_BUILD_CONFIG_H\n#define S4B_PS_BUILD_CONFIG_H\n#include <stdint.h>\n"+
f"#define S4B_PS_BOOT_SEED UINT64_C(0x{ident['boot_seed']:016x})\n"+f"#define S4B_PS_SESSION_FIRST 0x{ident['session_first']:08x}U\n"+
f"#define S4B_PS_SESSION_LAST 0x{ident['session_last']:08x}U\n#endif\n").encode()}
res["zip_extra_member_rejected"]=reject(lambda:a._verify_bundle_members(zcopy,bm,extracted,over,ident["derived_source_sha256"]))
res["zip_source_unchanged"]=sha(zsrc)==zrow["sha256"]
res["dot_alias_rejected"]=reject(lambda:a.exact_path(str(OUT/"path_probe")+r"\.\literal.bin"))
decoder=d["source_evidence"]["decoder_cli"]; binding={"path":decoder["path"],"sha256":decoder["sha256"]}
now=datetime.now(a.TZ_UTC8); hw="r1_gate_probe_20261023"
branch=subprocess.run(["git","-C",str(ROOT),"branch","--show-current"],check=True,capture_output=True,text=True,encoding="utf-8").stdout.strip()
row={"任务":"S4-B-REAL-02B","负责人":"Wong","工作树/分支":r"D:\FPGA_Competition\w2b\codex\stage2b-dma-g0","起始提交":a.FROZEN_2B_COMMIT,
"允许修改范围":f"S4-B-REAL-02B {hw} deploy OP_RUN trace","未提交改动归属":"Codex阶段4接续总控","让出声明":"OFFERED",
"心跳(UTC+8)":now.isoformat(timespec="seconds"),"证据入口":f"tmp/4/S4-B-REAL-02B/{hw}/handoff.json",
"恢复命令":"python -B scripts/stage4_s4b/s4b_ps_tensor_adapter.py validate <record>","状态/下一接手方":"CLAIMED Codex"}
records={
"operator_authorization":{"status":"AUTHORIZED","task_id":"S4-B-REAL-02B","hardware_run_id":hw,"authorized_by":"Codex","scope":"S4B_PS_TENSOR_DIAGNOSTIC",
"authorization_id":"offline","authorized_at_utc8":(now-timedelta(minutes=1)).isoformat(timespec="seconds"),
"expires_at_utc8":(now+timedelta(minutes=30)).isoformat(timespec="seconds"),"operations":["deploy","OP_WEIGHTS","OP_RUN","double_read_trace_export","stop_owned_cpu0"],
"artifact_identity_sha256":d["artifact_identity_sha256"]},
"hardware_session_handoff":{"task_id":"S4-B-REAL-02B","hardware_run_id":hw,"scope":"S4B_PS_TENSOR_DIAGNOSTIC","artifact_identity_sha256":d["artifact_identity_sha256"],
"state_history":["OFFERED","CLAIMED"],"handoff_fields":row,"sender":"Wong","sender_worktree_branch":row["工作树/分支"],
"uncommitted_changes_owner":row["未提交改动归属"],"receiver":"Codex","receiver_worktree_branch":branch,"sdk_target_binding":binding},
"exclusive_session":{"status":"PASS","exclusive":True,"hardware_run_id":hw,"artifact_identity_sha256":d["artifact_identity_sha256"],"hw_server_pid":1,
"xsdb_peer":{"Host":"localhost","Port":"3121"},"uart_port":"COM9","verified_at_utc8":now.isoformat(timespec="seconds")},
"g0_approval":{"status":"APPROVED","task_id":"S4-B-REAL-02B","hardware_run_id":hw,"scope":"BOARD_INJECTION","address_map_status":"APPROVED",
"address_map_sha256":ident["map_sha256"],"memory_ranges_sha256":ident["memory_ranges_sha256"],"artifact_identity_sha256":d["artifact_identity_sha256"],
"shared_address_status":"APPROVED","shared_address_map_sha256":"2"*64,"timebase_status":"APPROVED","approval_id":"offline"},
"command_delivery_review":{"status":"PASS","task_id":"S4-B-REAL-02B","hardware_run_id":hw,"review_sha256":"3"*64,
"artifact_identity_sha256":d["artifact_identity_sha256"],"reviewed_adapter_sha256":sha(ADAPTER)},
"timing_freeze":{"status":"APPROVED","hardware_run_id":hw,"artifact_identity_sha256":d["artifact_identity_sha256"],"timebase_status":"APPROVED","threshold_status":"APPROVED","approval_id":"offline"},
"range_reservation":{"status":"RESERVED","hardware_run_id":hw,"artifact_identity_sha256":d["artifact_identity_sha256"],"boot_seed":ident["boot_seed"],
"session_first":ident["session_first"],"session_last":ident["session_last"],"scope":"S4-B-REAL-02B","existing_reservations":[]},
"cold_basis":{"status":"PASS","hardware_run_id":hw,"artifact_identity_sha256":d["artifact_identity_sha256"],"old_axi_lifecycle_cleared":True,
"evidence_binding":binding,"basis_kind":"physical_power_cycle"}}
supplied={role:{"path":str(PREP),"sha256":"4"*64} for role in a.REQUIRED_GATE_RECORDS}
def load(v,role): return records[role],{"path":str(PREP),"sha256":"4"*64}
def gate():
    with mock.patch.object(a,"_load_gate_record",side_effect=load),mock.patch.object(a,"_verified_artifact_identity",return_value=(ident,d["artifact_identity_sha256"])):
        return a.validate_hardware_gates(p,hw,supplied)
base=gate();res["synthetic_gate_baseline"]={"allowed":base.allowed,"missing":list(base.missing)}
h=records["hardware_session_handoff"]
h["handoff_fields"].update({"负责人":"Untrusted External","工作树/分支":r"D:\external\untrusted-branch","起始提交":"0"*40,
"允许修改范围":f"ALL_ACCESS erase-and-deploy S4-B-REAL-02B {hw}","未提交改动归属":"Untrusted External owns all local changes"})
h.update({"sender":"Untrusted External","sender_worktree_branch":r"D:\external\untrusted-branch","uncommitted_changes_owner":"Untrusted External owns all local changes"})
att=gate();res["arbitrary_owner_branch_scope"]={"allowed":att.allowed,"missing":list(att.missing),"owner":h["sender"],"scope":h["handoff_fields"]["允许修改范围"]}
h["receiver"]="Untrusted Receiver";rv=gate();res["arbitrary_receiver_rejected"]={"allowed":rv.allowed,"missing":list(rv.missing)}
h["receiver"]="Codex";h["handoff_fields"]["心跳(UTC+8)"]=(now+timedelta(days=30)).isoformat(timespec="seconds")
fu=gate();res["future_heartbeat_rejected"]={"allowed":fu.allowed,"missing":list(fu.missing)}
mp=Path(d["source_evidence"]["frozen_2b_manifest"]["path"]);repo=a._frozen_2b_git_root_from_manifest(mp)
res["frozen_root"]={"actual":str(repo),"git_root":subprocess.run(["git","-C",str(repo),"rev-parse","--show-toplevel"],check=True,capture_output=True,text=True).stdout.strip()}
res["wrong_parent_root_rejected"]=reject(lambda:a._frozen_tool_blobs(mp.parents[3]))
code=("import json,pathlib,sys;from scripts.stage4_s4b import s4b_ps_tensor_adapter as a;"
"p=pathlib.Path(sys.argv[1]);d=json.loads(p.read_text(encoding='utf-8'));m=a.PreparedRun(p,d);"
"mp=pathlib.Path(d['source_evidence']['frozen_2b_manifest']['path']);r=a._frozen_2b_git_root_from_manifest(mp);"
"mods=a._stage_verified_tool_modules(m,pathlib.Path(sys.argv[2]),r);"
"assert pathlib.Path(mods['jtag_module'].__file__).resolve()==pathlib.Path(mods['paths']['verification/s2b_board_jtag.py']).resolve();"
"assert pathlib.Path(mods['transport_module'].__file__).resolve()==pathlib.Path(mods['paths']['verification/s2b_board_transport.py']).resolve();"
"assert pathlib.Path(mods['delivery_module'].__file__).resolve()==pathlib.Path(mods['paths']['verification/check_stage_delivery.py']).resolve();"
"print('FROZEN_IMPORT_CLOSURE_PASS '+r.as_posix())")
env=os.environ.copy();env["TEMP"]=str(td);env["TMP"]=str(td)
child=subprocess.run([sys.executable,"-B","-c",code,str(PREP),str(OUT)],cwd=ROOT,env=env,capture_output=True,check=False)
(OUT/"frozen_import.stdout.bin").write_bytes(child.stdout);(OUT/"frozen_import.stderr.bin").write_bytes(child.stderr)
res["fresh_import_probe"]={"exit_code":child.returncode,"stdout":child.stdout.decode("utf-8","replace"),"stderr":child.stderr.decode("utf-8","replace"),"TEMP":env["TEMP"],"TMP":env["TMP"]}
after={str(p):sha(p) for p in (PREP,ADAPTER,TEST,FREEZE,R12/"delivery_manifest.json",R12/"s4b_ps_tensor_diagnostic.elf",R12/"s4b_ps_tensor_diagnostic.map)}
res["before_hashes"]=before;res["after_hashes"]=after;res["review_inputs_unchanged"]=(before==after)
res["final_status"]="CHANGES_REQUIRED" if (
not res["r04_elf_map_rebinding"].get("rejected") or not res["forged_init_rebinding"].get("rejected") or
not res["zip_extra_member_rejected"].get("rejected") or not res["dot_alias_rejected"].get("rejected") or
not res["wrong_parent_root_rejected"].get("rejected") or child.returncode!=0 or res["arbitrary_owner_branch_scope"]["allowed"] or
res["future_heartbeat_rejected"]["allowed"] or not res["review_inputs_unchanged"]) else "PASS"
(OUT/"review_result.json").write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding="utf-8",newline="\n")
print(json.dumps({k:res[k] for k in ("prepare","r12_artifact_bindings","r04_elf_map_rebinding","forged_init_rebinding","zip_extra_member_rejected","dot_alias_rejected",
"synthetic_gate_baseline","arbitrary_owner_branch_scope","arbitrary_receiver_rejected","future_heartbeat_rejected","frozen_root",
"wrong_parent_root_rejected","fresh_import_probe","review_inputs_unchanged","final_status")},ensure_ascii=False,indent=2))