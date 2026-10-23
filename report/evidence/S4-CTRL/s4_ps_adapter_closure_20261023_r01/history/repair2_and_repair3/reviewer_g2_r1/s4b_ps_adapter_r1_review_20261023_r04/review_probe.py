from pathlib import Path
from datetime import datetime, timedelta
from unittest import mock
import copy, hashlib, json, os, subprocess, sys
ROOT=Path(r"D:\codex-worktrees\w4"); OUT=Path(os.environ["S4B_R1_EVIDENCE_DIR"]); sys.path.insert(0,str(ROOT))
PREP=ROOT/"tmp/4/S4-B-REAL-02B/s4b_ps_tensor_adapter_prepare_g2r1_20261023_r05/adapter_preparation.json"
ADAPTER=ROOT/"scripts/stage4_s4b/s4b_ps_tensor_adapter.py"; TEST=ROOT/"verification/test_s4b_ps_tensor_adapter.py"
FREEZE=ROOT/"report/evidence/S4-B/s4b_ps_adapter_g2_20261023_r02/frozen_sources.json"
R12=ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r12"
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()
def expect_reject(fn):
    try: fn()
    except Exception as exc:
        from scripts.stage4_s4b import s4b_ps_tensor_adapter as mod
        return {"rejected":isinstance(exc,mod.AdapterError),"type":type(exc).__name__,"error":str(exc)}
    return {"rejected":False,"accepted":True}
temp=OUT/"system_tmp"; temp.mkdir()
tracked=(PREP,ADAPTER,TEST,FREEZE,R12/"delivery_manifest.json",R12/"s4b_ps_tensor_diagnostic.elf",R12/"s4b_ps_tensor_diagnostic.map")
before={str(path):sha(path) for path in tracked}
from scripts.stage4_s4b import s4b_ps_tensor_adapter as a
prepared=a.validate_preparation(PREP); data=prepared.data; identity=data["artifact_identity"]
result={"run_id":OUT.name,"TEMP":os.environ["TEMP"],"TMP":os.environ["TMP"],
"prepare_status":data["status"],"build_run_id":identity["build_run_id"],
"identity_sha256":data["artifact_identity_sha256"],"source_evidence":data["source_evidence"]}
artifacts={}
for key,name in (("elf","s4b_ps_tensor_diagnostic.elf"),("map","s4b_ps_tensor_diagnostic.map")):
    artifacts[key]=next(row for row in data["bindings"] if row.get("role")=="artifact" and Path(row["path"]).name==name)
assert identity["elf_sha256"]==sha(R12/"s4b_ps_tensor_diagnostic.elf")
assert identity["map_sha256"]==sha(R12/"s4b_ps_tensor_diagnostic.map")
assert identity["elf_sha256"]!=sha(ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.elf")
result["r12_artifacts"]=artifacts
mutated=copy.deepcopy(data)
for row,path in (
    (next(x for x in mutated["bindings"] if x.get("role")=="artifact" and x["path"].endswith(".elf")),ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.elf"),
    (next(x for x in mutated["bindings"] if x.get("role")=="artifact" and x["path"].endswith(".map")),ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.map"),
):
    row.update(path=str(path),sha256=sha(path),bytes=path.stat().st_size)
mutated["artifact_identity"]["elf_sha256"]=sha(ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.elf")
mutated["artifact_identity"]["map_sha256"]=sha(ROOT/"report/evidence/S4-B/s4b_ps_tensor_20261023_r04/s4b_ps_tensor_diagnostic.map")
mutated["artifact_identity_sha256"]=a.artifact_identity_sha256(mutated["artifact_identity"])
result["r04_rebinding"]=expect_reject(lambda:a._verified_artifact_identity(a.PreparedRun(prepared.path,mutated)))
mutated=copy.deepcopy(data); fake=OUT/"forged_init.elf"; fake.write_bytes(b"offline forged init")
for row in mutated["bindings"]:
    if row.get("role")=="verified_recovery_init_elf" or (row.get("role")=="verified_recovery_bundle_member" and row.get("relative_path")==a.RECOVERY_INIT_MEMBER):
        row.update(path=str(fake),sha256=sha(fake),bytes=fake.stat().st_size)
mutated["artifact_identity"]["init_elf_sha256"]=sha(fake)
mutated["artifact_identity_sha256"]=a.artifact_identity_sha256(mutated["artifact_identity"])
result["forged_init_rebinding"]=expect_reject(lambda:a._verified_artifact_identity(a.PreparedRun(prepared.path,mutated)))
from verification.test_s4b_ps_tensor_adapter import AdapterBindingTests
binding_tests=AdapterBindingTests()
binding_tests.test_exact_path_rejects_raw_windows_aliases_before_path_normalization()
binding_tests.test_bundle_overlay_is_exact_and_unlisted_files_are_rejected()
result["source_path_and_zip_unit_probes"]="PASS"
binding_tests.test_frozen_import_closure_and_git_root_api_in_fresh_process()
result["frozen_import_probe_exit_code"]=int((OUT/"frozen_import_probe.exit_code.txt").read_text(encoding="ascii"))
result["frozen_import_probe_stdout"]=(OUT/"frozen_import_probe.stdout.bin").read_bytes().decode("utf-8","replace")
result["frozen_import_probe_stderr"]=(OUT/"frozen_import_probe.stderr.bin").read_bytes().decode("utf-8","replace")
decoder=data["source_evidence"]["decoder_cli"]; valid_binding={"path":decoder["path"],"sha256":decoder["sha256"]}
now=datetime.now(a.TZ_UTC8); hw="r1_gate_probe_20261023"
branch=subprocess.run(["git","-C",str(ROOT),"branch","--show-current"],check=True,capture_output=True,text=True,encoding="utf-8").stdout.strip()
handoff_row={"任务":"S4-B-REAL-02B","负责人":"Wong","工作树/分支":r"D:\FPGA_Competition\w2b\codex\stage2b-dma-g0","起始提交":a.FROZEN_2B_COMMIT,
"允许修改范围":f"S4-B-REAL-02B {hw} deploy OP_RUN trace","未提交改动归属":"Codex阶段4接续总控","让出声明":"OFFERED","心跳(UTC+8)":now.isoformat(timespec="seconds"),
"证据入口":f"tmp/4/S4-B-REAL-02B/{hw}/handoff.json","恢复命令":"python -B adapter.py validate","状态/下一接手方":"CLAIMED Codex"}
records={
"operator_authorization":{"status":"AUTHORIZED","task_id":"S4-B-REAL-02B","hardware_run_id":hw,"authorized_by":"Codex","scope":"S4B_PS_TENSOR_DIAGNOSTIC","authorization_id":"offline",
"authorized_at_utc8":(now-timedelta(minutes=1)).isoformat(timespec="seconds"),"expires_at_utc8":(now+timedelta(minutes=30)).isoformat(timespec="seconds"),
"operations":["deploy","OP_WEIGHTS","OP_RUN","double_read_trace_export","stop_owned_cpu0"],"artifact_identity_sha256":data["artifact_identity_sha256"]},
"hardware_session_handoff":{"task_id":"S4-B-REAL-02B","hardware_run_id":hw,"scope":"S4B_PS_TENSOR_DIAGNOSTIC","artifact_identity_sha256":data["artifact_identity_sha256"],
"state_history":["OFFERED","CLAIMED"],"handoff_fields":handoff_row,"sender":"Wong","sender_worktree_branch":handoff_row["工作树/分支"],
"uncommitted_changes_owner":handoff_row["未提交改动归属"],"receiver":"Codex","receiver_worktree_branch":branch,"sdk_target_binding":valid_binding},
"exclusive_session":{"status":"PASS","exclusive":True,"hardware_run_id":hw,"artifact_identity_sha256":data["artifact_identity_sha256"],"hw_server_pid":1,"xsdb_peer":{"Host":"localhost","Port":"3121"},
"uart_port":"COM9","verified_at_utc8":now.isoformat(timespec="seconds")},
"g0_approval":{"status":"APPROVED","task_id":"S4-B-REAL-02B","hardware_run_id":hw,"scope":"BOARD_INJECTION","address_map_status":"APPROVED",
"address_map_sha256":identity["map_sha256"],"memory_ranges_sha256":identity["memory_ranges_sha256"],"artifact_identity_sha256":data["artifact_identity_sha256"],
"shared_address_status":"APPROVED","shared_address_map_sha256":"2"*64,"timebase_status":"APPROVED","approval_id":"offline"},
"command_delivery_review":{"status":"PASS","task_id":"S4-B-REAL-02B","hardware_run_id":hw,"review_sha256":"3"*64,
"artifact_identity_sha256":data["artifact_identity_sha256"],"reviewed_adapter_sha256":sha(ADAPTER)},
"timing_freeze":{"status":"APPROVED","hardware_run_id":hw,"artifact_identity_sha256":data["artifact_identity_sha256"],"timebase_status":"APPROVED","threshold_status":"APPROVED","approval_id":"offline"},
"range_reservation":{"status":"RESERVED","hardware_run_id":hw,"artifact_identity_sha256":data["artifact_identity_sha256"],"boot_seed":identity["boot_seed"],
"session_first":identity["session_first"],"session_last":identity["session_last"],"scope":"S4-B-REAL-02B","existing_reservations":[]},
"cold_basis":{"status":"PASS","hardware_run_id":hw,"artifact_identity_sha256":data["artifact_identity_sha256"],"old_axi_lifecycle_cleared":True,
"evidence_binding":valid_binding,"basis_kind":"physical_power_cycle"}}
supplied={role:{"path":str(PREP),"sha256":"4"*64} for role in a.REQUIRED_GATE_RECORDS}
def load_record(value,role): return records[role],{"path":str(PREP),"sha256":"4"*64}
def check_gate():
    with mock.patch.object(a,"_load_gate_record",side_effect=load_record),mock.patch.object(a,"_verified_artifact_identity",return_value=(identity,data["artifact_identity_sha256"])):
        return a.validate_hardware_gates(prepared,hw,supplied)
base=check_gate();result["synthetic_gate_baseline"]={"allowed":base.allowed,"missing":list(base.missing)}
handoff=records["hardware_session_handoff"]
handoff_row.update({"负责人":"Untrusted External","工作树/分支":r"D:\external\untrusted-branch","起始提交":"0"*40,
"允许修改范围":f"ALL_ACCESS erase-and-deploy S4-B-REAL-02B {hw}","未提交改动归属":"Untrusted External owns all local changes"})
handoff.update({"sender":"Untrusted External","sender_worktree_branch":r"D:\external\untrusted-branch","uncommitted_changes_owner":"Untrusted External owns all local changes"})
attacker=check_gate();result["arbitrary_owner_scope_gate"]={"allowed":attacker.allowed,"missing":list(attacker.missing),"sender":handoff["sender"],"scope":handoff_row["允许修改范围"]}
handoff["receiver"]="Untrusted Receiver";receiver=check_gate();result["arbitrary_receiver_gate"]={"allowed":receiver.allowed,"missing":list(receiver.missing)}
handoff["receiver"]="Codex";handoff_row["心跳(UTC+8)"]=(now+timedelta(days=30)).isoformat(timespec="seconds")
future=check_gate();result["future_heartbeat_gate"]={"allowed":future.allowed,"missing":list(future.missing)}
after={str(path):sha(path) for path in tracked}
result["before_hashes"]=before;result["after_hashes"]=after;result["review_inputs_unchanged"]=before==after
result["final_status"]="CHANGES_REQUIRED" if (not result["r04_rebinding"]["rejected"] or not result["forged_init_rebinding"]["rejected"] or
result["frozen_import_probe_exit_code"]!=0 or result["arbitrary_owner_scope_gate"]["allowed"] or result["future_heartbeat_gate"]["allowed"] or not result["review_inputs_unchanged"]) else "PASS"
(OUT/"review_result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8",newline="\n")
print(json.dumps({k:result[k] for k in ("prepare_status","build_run_id","identity_sha256","r12_artifacts","r04_rebinding","forged_init_rebinding","source_path_and_zip_unit_probes",
"frozen_import_probe_exit_code","frozen_import_probe_stdout","frozen_import_probe_stderr","synthetic_gate_baseline","arbitrary_owner_scope_gate","arbitrary_receiver_gate",
"future_heartbeat_gate","review_inputs_unchanged","final_status")},ensure_ascii=False,indent=2))