"""封存只读软件审查收据；真实板卡验收保持未执行。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).absolute().parents[4]
OUT=ROOT/"report/evidence/S2B-T19/csr_map_review_20261013_r02"
TEMP=Path(__file__).parent
def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def bind(file):return {"path":str(file),"sha256":sha(file),"bytes":file.stat().st_size}
upstream=ROOT/"report/evidence/S2B-T17/implemented_export_independent_20261013_r01/runtime_compatibility_receipt_r01.json"
receipt=json.loads(upstream.read_text(encoding="utf-8"))
xsa=Path(receipt["artifacts"]["implemented_xsa"]["path"])
assert xsa.is_file() and sha(xsa)=="6f2cddd2f8d81d9b8d7ae8987aa446d354cb4b44cd208dfdb336eb24b796c1be"
with zipfile.ZipFile(xsa) as archive:
    names=archive.namelist()
    assert len(names)==len(set(names))
    members=[name for name in names if name.endswith(".hwh")]
    assert len(members)==1
    data=archive.read(members[0]);tree=ET.fromstring(data)
    selected=[row.attrib for row in tree.findall(".//MEMRANGE") if 0x43C00000<=int(row.get("BASEVALUE","-1"),0)<=0x43C0FFFF]
assert len(selected)==1
row=selected[0]
assert int(row["BASEVALUE"],0)==0x43C00000 and int(row["HIGHVALUE"],0)==0x43C0FFFF
assert all(row[key]==value for key,value in {"INSTANCE":"infer","MEMTYPE":"REGISTER","MASTERBUSINTERFACE":"M_AXI_GP0","SLAVEBUSINTERFACE":"S_AXI"}.items())
xsa_check={"status":"PASS_READONLY_HWH","implemented_xsa":bind(xsa),"hwh_member":members[0],"hwh_sha256":hashlib.sha256(data).hexdigest(),"selected_region":row}
(OUT/"actual_xsa_check.json").write_text(json.dumps(xsa_check,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
source_hashes={"vitis/run_s2b_visibility_probe.py":"01e7668a5af91a3f110ae92bcdeecdcf4cb56f12d4dd8f2cc3c45ee6d7ed71ab","verification/test_s2b_visibility_probe.py":"086bfbcdb7e6172a4d51b940e49e0eda3ee0daafc0afc71dfdd2c13e002b161c"}
snapshots={}
for name,digest in source_hashes.items():
    file=ROOT/name;assert sha(file)==digest
    output=OUT/(file.name+".snapshot")
    with output.open("xb") as stream:stream.write(file.read_bytes())
    snapshots[name]=bind(output)
tests=json.loads((OUT/"tests_result.json").read_text(encoding="utf-8"))
assert tests["native_exit_code"]==0 and tests["tests_run"]==28 and tests["source_sha256"]==source_hashes
result={"schema_version":1,"role":"INDEPENDENT_REVIEWER","task_id":"S2B-T19","status":"PASS_G2_SOFTWARE_ONLY","review_scope":"CSR debug mapping fix only; visibility0_cache_probe_only","reviewed_at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"baseline_commit":"dd1ffe44f2cb0d8a99f79e314febf2bdd44d84e2","source_sha256":source_hashes,"source_snapshots":snapshots,"compatibility_receipt":bind(upstream),"sdk_sources":[bind(Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\target.py")),bind(Path(r"D:\Xilinx\2026.1\Vitis\cli\hsiutils\__init__.py"))],"checks":{"full_unit_methods":28,"full_unit_failures":0,"full_unit_errors":0,"full_unit_native_exit_code":0,"full_unit_elapsed_seconds":tests["elapsed_seconds"],"official_ast_full_mapping_and_cleanup":"PASS","official_partial_load_failure":"EXPECTED_CLEANUP_FAILURE_NOT_FALSE_SUCCESS","actual_implemented_xsa_hwh":"PASS","force_mem_accesses_added":False,"blocking_findings":[]},"commands":[{"command":sys.executable+" -X utf8 -B "+str(TEMP/"run_review_tests.py"),"exit_code":0},{"command":sys.executable+" -X utf8 -B "+str(TEMP/"review_sdk_cases.py"),"exit_code":0},{"command":sys.executable+" -X utf8 -B "+str(TEMP/"review_full_sdk.py"),"exit_code":0}],"evidence":[bind(file) for file in OUT.iterdir() if file.is_file()],"independent_drivers":[bind(file) for file in TEMP.iterdir() if file.is_file()],"limitations":["审查未连接hw_server、板卡或串口；未导入SDK真实会话。","官方AST在模拟设计、CPU节点和TCF下发上执行，不代表真实SDK/板上映射成功。","SDK loadhw在创建design后、建立_memmap_ctxs前失败时，unloadhw提前返回；当前生产门禁准确将_designtable残留记为cleanup失败，disconnect/dispose不证明该design已close。","SDK内部表读取用于核验官方下发请求；本轮没有真实远端TCF memorymap读回。","BOARD/G3/G4/G5和cache实板结果仍NOT_RUN，不批准visibility1、LOAD/START或模型计算。","峰值内存与完整工具调用量未测；先前沙箱枚举失败和独立driver两次错误原件保留。"]}
with (OUT/"review_receipt.json").open("x",encoding="utf-8",newline="\n") as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write("\n")
print(json.dumps({"status":result["status"],"receipt":bind(OUT/"review_receipt.json"),"tests":28},ensure_ascii=False))
