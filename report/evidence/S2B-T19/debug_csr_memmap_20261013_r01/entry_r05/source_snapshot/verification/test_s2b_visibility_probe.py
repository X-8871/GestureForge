"""T19离线mock生命周期和固定绑定反例；不导入XSDB/serial、不操作实物。"""
from pathlib import Path
import copy
import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import types
from types import SimpleNamespace
import unittest
import zipfile
from unittest.mock import patch

from . import test_s2b_board_jtag as fixture
from . import s2b_board_jtag as j

REAL_ROOT=Path(__file__).absolute().parents[1]
spec=importlib.util.spec_from_file_location("s2b_visibility_entry",REAL_ROOT/"vitis/run_s2b_visibility_probe.py")
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

def bind(path):
    """固定单元fixture或真实只读来源的原字节。"""
    return {"path":str(path.absolute()),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}

def write(path,data):
    """创建UTF8单元fixture，不伪造正式独审审批。"""
    with path.open("x",encoding="utf-8",newline="\n") as out:json.dump(data,out,ensure_ascii=False);out.write("\n")

class Port(fixture.FakeSerial):
    """真实协议编解码所消费的mock字节；没有串口设备。"""
    def __init__(self,session,build,scenario,**kwargs):
        self.session,self.scenario,self.is_open,self.dtr,self.rts,self.port=session,scenario,False,None,None,None
        self.parameters=kwargs
        def answer(request,payload):
            phase,cpu,dap=fixture.struct.unpack("<III",payload)
            if phase==0:
                for i,v in enumerate(j.pattern(cpu)):session.memory[j.PROBE_ADDRESS+4*i]=v
            words=[session.memory.get(j.PROBE_ADDRESS+4*i,0) for i in range(64)]
            raw=fixture.response(request,probe=fixture.struct.pack("<64I",*words))
            return raw[:-1]+bytes([raw[-1]^1]) if scenario=="cache" else raw
        super().__init__(answer)
        banner=f"S2B-INFERENCE/1 READY SOURCE={build['source_sha256']['vitis/s2b_inference_app.c']} XSA={build['xsa_sha256']} MODEL={j.transport.MODEL_SHA}\r\n".encode()
        self.rx.extend(banner if scenario!="banner" else b"BAD\r\n")
    def open(self):
        if self.scenario=="serial_open":raise RuntimeError("mock serial open failure")
        if self.dtr is not False or self.rts is not False:raise RuntimeError("DTR/RTS必须在open前关闭")
        self.is_open=True;self.session.operations.append(("serial.open",))
    def close(self):
        self.is_open=False
        if self.scenario=="serial_close":raise RuntimeError("mock serial close failure")

class LifecycleTests(unittest.TestCase):
    """生产编排和真实T16/T15解析器运行于mock SDK，所有部分证据保留。"""
    def setUp(self):
        parent=REAL_ROOT/"tmp/2B/S2B-T19"
        parent.mkdir(exist_ok=True)
        self.directory=Path(tempfile.mkdtemp(prefix="unit_lifecycle_",dir=parent))
        (self.directory/"report/evidence/S2B-T19").mkdir(parents=True)
        self.session=fixture.FakeSession();self.scenario="normal";self.runtime_calls=0;self.ports=[]
        for key in (11,12):self.session.objects[key].running=True
        self.bindings={}
        for name in ("init_elf","app_elf","xsa","bit","csr_source","interface","sdk_target"):
            file=self.directory/name;file.write_bytes(fixture.elf_bytes(app=name=="app_elf") if name.endswith("elf") else fixture.xsa_bytes() if name=="xsa" else name.encode());self.bindings[name]=bind(file)
        for key,file in [("tool_source",Path(j.__file__)),("transport_source",Path(j.transport.__file__)),("elf_parser",REAL_ROOT/"verification/check_s2b_ps_smoke_layout.py"),("delivery_parser",REAL_ROOT/"verification/check_stage_delivery.py")]:self.bindings[key]=bind(file)
        self.build={"source_sha256":{"vitis/s2b_inference_app.c":"a"*64},"xsa_sha256":"b"*64}
        self.expected={"native":{"ProcessId":123,"ExecutablePath":"D:\\root-owned\\hw_server.exe","CreationTimeFileTimeUtc":"123456"}}
        self.uart={"port":"COM4","name":"CP210x (COM4)","pnp_device_id":"USB\\UNIT_FIXTURE","config_manager_error_code":0}
        self.actual={"snapshot":{"servers":[copy.deepcopy(self.expected["native"])],"listeners":[{"LocalPort":3121,"OwningProcess":123}],"ports":[{"Name":self.uart["name"],"PNPDeviceID":self.uart["pnp_device_id"],"ConfigManagerErrorCode":0}]}}
        self.config={"run_dir":str(self.directory/"report/evidence/S2B-T19/run"),"bindings":self.bindings,"cold_basis":self.bindings["interface"],"uart_identity":self.uart,"cpu_seed":0x12345678,"dap_seed":0x76543210,"response_timeout_seconds":0.02}
        def connect(**kwargs):
            if self.scenario=="connect":raise RuntimeError("mock connect failure")
            self.session.operations.append(("connect",kwargs));return "unit-channel"
        def disconnect(**kwargs):
            self.session.operations.append(("disconnect",kwargs))
            if self.scenario=="disconnect":raise RuntimeError("mock disconnect failure")
        self.session.connect=connect;self.session.disconnect=disconnect
        def runtime(config):
            self.runtime_calls+=1
            def dispose():
                if self.scenario=="dispose":raise RuntimeError("mock dispose failure")
            def construct(**kwargs):
                port=Port(self.session,self.build,self.scenario,**kwargs);self.ports.append(port);return port
            def start():
                if self.scenario=="start_session":raise RuntimeError("mock start session failure")
                return self.session
            return SimpleNamespace(start_debug_session=start,dispose=dispose,__file__="UNIT_FAKE_SDK"),SimpleNamespace(Serial=construct,__file__="UNIT_FAKE_SERIAL",__version__="3.5")
        self.runtime=runtime
    def execute(self,scenario="normal",identity=None,map_setup=None,map_clear=None):
        self.scenario=scenario
        if scenario=="init":self.session.fail_init=True
        if scenario=="init_download":self.session.fail_dow=True
        if scenario=="app":
            original=self.session.objects[11].dow
            def fail_app(**kwargs):
                if Path(kwargs["file"]).name=="app_elf":raise RuntimeError("mock app download failure")
                return original(**kwargs)
            self.session.objects[11].dow=fail_app
        if scenario=="fpga":self.session.objects[13].fpga=lambda **kwargs:(_ for _ in ()).throw(RuntimeError("mock FPGA failure"))
        if scenario=="boot":self.session.memory[0xF800025C]=1
        if scenario=="postconfig_lock":self.session.memory[0xF800000C]=0
        if scenario=="postconfig_clock":self.session.memory[0xF8000170]=0
        if scenario=="postconfig_csr":self.session.memory[0x43C00074]=1
        if scenario=="chain":self.session.rows["cpu1"]["jtag_cable_serial"]="wrong"
        if scenario=="cpu0_stop":self.session.objects[11].stop=lambda **kwargs:(_ for _ in ()).throw(RuntimeError("mock CPU0 stop failure"))
        if scenario=="breakpoint_cleanup":
            original=self.session.objects[11].bpadd
            def fail_remove(**kwargs):
                bp=original(**kwargs);bp.remove=lambda:(_ for _ in ()).throw(RuntimeError("mock breakpoint cleanup failure"));return bp
            self.session.objects[11].bpadd=fail_remove
        file=self.directory/"unit_config.json";write(file,self.config)
        with patch.object(p,"ROOT",self.directory),patch.object(p,"_preflight",return_value=(j,j.transport,self.build,self.expected)),patch.object(p,"_runtime",side_effect=self.runtime),patch.object(p,"verify_runtime_sources",return_value={"scope":"UNIT_MOCK"}),patch.object(p,"register_csr_debug_map",side_effect=map_setup),patch.object(p,"clear_csr_debug_map",side_effect=map_clear),patch.object(p,"_identity_snapshot",return_value=self.actual if identity is None else identity):
            if scenario=="normal":result=p.run(file)
            else:
                with self.assertRaises(p.VisibilityProbeError):p.run(file)
                result=json.loads((Path(self.config["run_dir"])/"visibility_probe_result.json").read_text(encoding="utf-8"))
        self.assertFalse(result["cold_lifecycle_proven"])
        self.assertFalse(result["owned_hw_server_released"])
        if scenario=="cpu0_stop":
            self.assertTrue(self.session.objects[11].running)
            self.assertTrue(any(x["action"]=="failure_cpu0" for x in result["cleanup_errors"]))
        elif scenario not in ("chain","start_session","connect"):self.assertFalse(self.session.objects[11].running)
        else:self.assertFalse(any(x[0]=="stop" for x in self.session.operations))
        self.assertEqual(set(self.session._bptable)&{1},{1})
        return result
    def test_full_mock_lifecycle_actual_wire_and_owned_cleanup(self):
        result=self.execute();self.assertEqual(result["native_exit_code"],0)
        self.assertEqual(result["initial_cpu_states"],{j.NAMES[1]:"Running",j.NAMES[2]:"Running"})
        self.assertEqual(result["final_csr"][0x50],0)
        self.assertEqual(result["final_csr"][0x0C],0x400)
        open_index=self.session.operations.index(("serial.open",));con_app=next(i for i,x in enumerate(self.session.operations) if x[0]=="con" and not x[2])
        self.assertLess(open_index,con_app)
        self.assertFalse(self.ports[0].is_open)
        self.assertEqual(result["postconfiguration"]["status"],"PASS")
        self.assertEqual(result["postconfiguration"]["cold_reset_defaults"]["actual"][0x01C],519168)
        self.assertIn(("connect",{"url":"TCP:localhost:3121","server":"hw_server"}),self.session.operations)
        self.assertEqual(result["cache_probe"]["phase0_raw_hex"][:8],"78563412")
        self.assertEqual(len(Path(self.config["run_dir"]).joinpath("uart_rx_raw.bin").read_bytes()),result["banner"]["bytes"]+2*(40+40+256))
    def test_sdk_uart_and_cleanup_failures_preserve_originals(self):
        for scenario in ["start_session","connect","boot","chain","cpu0_stop","init_download","init","fpga","app","banner","cache","serial_open","serial_close","disconnect","dispose","breakpoint_cleanup"]:
            with self.subTest(scenario=scenario):
                self.setUp();result=self.execute(scenario);self.assertEqual(result["native_exit_code"],2)
                self.assertTrue((Path(self.config["run_dir"])/"entry_calls.jsonl").is_file())
                if scenario=="connect":self.assertIn(("disconnect",{}),self.session.operations)
                if scenario in ("serial_close","disconnect","dispose","breakpoint_cleanup"):self.assertTrue(result["cleanup_errors"] or json.loads((Path(self.config["run_dir"])/"jtag_result.json").read_text(encoding="utf-8"))["cleanup_errors"])
    def test_postconfig_failure_locks_wire_before_app_load_or_uart_request(self):
        for scenario in ("postconfig_lock","postconfig_clock","postconfig_csr"):
            with self.subTest(scenario=scenario):
                self.setUp();result=self.execute(scenario)
                self.assertEqual(result["native_exit_code"],2)
                self.assertTrue(result["uart_failed"])
                self.assertFalse(result["uart_events"])
                self.assertFalse(any(row[0]=="con" and not row[2] for row in self.session.operations))
                self.assertFalse(any(row[0]=="dow" and Path(row[2]).name=="app_elf" for row in self.session.operations))
                raw=json.loads((Path(self.config["run_dir"])/"jtag_result.json").read_text(encoding="utf-8"))
                self.assertEqual(raw["postconfiguration"]["status"],"FAILED")
    def test_identity_failure_prevents_sdk_import(self):
        for field,value in [("ProcessId",124),("CreationTimeFileTimeUtc","999"),("ExecutablePath","wrong")]:
            with self.subTest(field=field):
                self.setUp();actual=copy.deepcopy(self.actual);actual["snapshot"]["servers"][0][field]=value
                self.session.objects[11].running=False
                result=self.execute("identity",actual);self.assertEqual(self.runtime_calls,0)
                self.assertFalse(self.session.operations)
        for kind in ("extra","listener","uart"):
            with self.subTest(kind=kind):
                self.setUp();actual=copy.deepcopy(self.actual)
                if kind=="extra":actual["snapshot"]["servers"].append(copy.deepcopy(actual["snapshot"]["servers"][0]))
                if kind=="listener":actual["snapshot"]["listeners"][0]["OwningProcess"]=999
                if kind=="uart":actual["snapshot"]["ports"][0]["PNPDeviceID"]="wrong"
                self.session.objects[11].running=False;self.execute("identity",actual);self.assertEqual(self.runtime_calls,0)
    def test_existing_run_rejected_without_overwrite(self):
        self.execute();before=(Path(self.config["run_dir"])/"visibility_probe_result.json").read_bytes()
        with patch.object(p,"ROOT",self.directory),self.assertRaises(p.VisibilityProbeError):p.run(self.directory/"unit_config.json")
        self.assertEqual(before,(Path(self.config["run_dir"])/"visibility_probe_result.json").read_bytes())
    def test_controller_close_exception_retains_partial_record(self):
        def fail_close(controller):
            raise RuntimeError("mock controller close failure")
        with patch.object(j.JtagController,"close",fail_close):
            result=self.execute("controller_close")
        folder=Path(self.config["run_dir"])
        self.assertEqual(result["native_exit_code"],2)
        self.assertTrue((folder/"jtag_close_failure_snapshot.json").is_file())
        self.assertTrue((folder/"jtag_calls.jsonl").read_bytes())
        self.assertTrue(any(x["action"]=="controller.close" for x in result["cleanup_errors"]))
    def test_mock_partial_map_failure_prevents_uart_and_deploy_and_keeps_original(self):
        """映射故障注入仅核验生产编排，不声明真实SDK映射通过。"""
        events=[]
        def setup(config,record,log,session,controller,owner):
            events.append("register");owner["attempted"]=True
            raise RuntimeError("UNIT_ORIGINAL_MAP_FAILURE")
        def clear(**kwargs):
            self.assertTrue(kwargs["owner"]["attempted"])
            events.append("clear")
            raise RuntimeError("UNIT_MAP_CLEANUP_FAILURE")
        result=self.execute("map_failure",map_setup=setup,map_clear=clear)
        self.assertEqual(events,["register","clear"])
        self.assertIn("UNIT_ORIGINAL_MAP_FAILURE",result["error"])
        self.assertTrue(any(x["action"]=="owned_csr_debug_map.clear" and "UNIT_MAP_CLEANUP_FAILURE" in x["error"] for x in result["cleanup_errors"]))
        self.assertFalse(self.ports)
        self.assertFalse(any(x[0] in ("dow","fpga") or (x[0]=="con" and not x[2]) for x in self.session.operations))
        self.assertIn(("disconnect",{"chan":"unit-channel"}),self.session.operations)
    def test_mock_map_cleanup_failure_overrides_success_and_stops_cpu(self):
        """成功路径的清理故障必须返回失败，不能吞掉映射清理异常。"""
        events=[]
        def setup(config,record,log,session,controller,owner):
            self.assertFalse(self.ports);owner["attempted"]=True;events.append("register")
        def clear(**kwargs):
            self.assertTrue(kwargs["owner"]["attempted"])
            self.assertFalse(self.ports[0].is_open);events.append("clear")
            raise RuntimeError("UNIT_MAP_CLEANUP_FAILURE_AFTER_CACHE")
        result=self.execute("map_cleanup",map_setup=setup,map_clear=clear)
        self.assertEqual(events,["register","clear"])
        self.assertEqual(result["native_exit_code"],2)
        self.assertIn("cache_probe",result)
        self.assertTrue(any(x["action"]=="owned_csr_debug_map.clear" for x in result["cleanup_errors"]))
        self.assertFalse(self.session.objects[11].running)
        self.assertIn(("disconnect",{"chan":"unit-channel"}),self.session.operations)

class PreflightTests(unittest.TestCase):
    """仅对未授权UNIT fixture核验schema/bindings；不创建正式compat receipt。"""
    def setUp(self):
        parent=REAL_ROOT/"tmp/2B/S2B-T19";parent.mkdir(exist_ok=True)
        self.directory=Path(tempfile.mkdtemp(prefix="unit_preflight_",dir=parent))
        self.bindings={}
        for name in ("init_elf","app_elf","xsa","bit","csr_source","interface"):
            file=self.directory/name;file.write_bytes(fixture.elf_bytes(app=name=="app_elf") if name.endswith("elf") else fixture.xsa_bytes() if name=="xsa" else name.encode());self.bindings[name]=bind(file)
        paths={"entry_source":Path(p.__file__),"tool_source":Path(j.__file__),"transport_source":Path(j.transport.__file__),"platform_checker":REAL_ROOT/"verification/check_s2b_inference_platform.py","elf_parser":REAL_ROOT/"verification/check_s2b_ps_smoke_layout.py","delivery_parser":REAL_ROOT/"verification/check_stage_delivery.py","sdk_init":p.SDK_INIT,"sdk_target":p.SDK_INIT.parent/"target.py",
               "csr_source":REAL_ROOT/"src/s2b_control_csr.sv","interface":REAL_ROOT/"docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"}
        # 测试采用实板入口已核验的pyserial原件，不要求当前验证解释器安装串口包。
        original=json.loads((REAL_ROOT/"report/evidence/S2B-T19/offline_probe_entry_20261011_r01/offline_result.json").read_text(encoding="utf-8"))
        serial_rows=[row for row in original["pyserial_files"] if Path(row["path"]).name=="__init__.py" and Path(row["path"]).parent.name=="serial"]
        self.assertEqual(len(serial_rows),1)
        serial=Path(serial_rows[0]["path"])
        self.assertEqual(bind(serial)["sha256"],serial_rows[0]["sha256"])
        paths["pyserial_init"]=serial
        for key,file in paths.items():self.bindings[key]=bind(file)
        self.sources={"unit-fixture-only":"c"*64}
        platform=self.directory/"unit_platform_manifest.json";write(platform,{"schema_version":1,"checks":[{"status":"PASS"}]})
        build={"status":"PASS_OFFLINE_FULL_XSA_BUILD","hardware_mode":"FULL_PLATFORM_BOUND","xsa_sha256":self.bindings["xsa"]["sha256"],"elf":self.bindings["app_elf"],"initializer_elf":self.bindings["init_elf"],
               "config":{"xsa":self.bindings["xsa"]["path"],"xsa_sha256":self.bindings["xsa"]["sha256"],"platform_manifest":str(platform),"platform_manifest_sha256":bind(platform)["sha256"]},
               "source_sha256":{name:bind(REAL_ROOT/name)["sha256"] for name in ("vitis/s2b_inference_app.c","verification/s2b_board_transport.py")}}
        self.build_path=self.directory/"unit_build_details.json";write(self.build_path,build)
        implemented=self.directory/"unit_implemented_xsa";implemented.write_bytes(b"UNIT IMPLEMENTED XSA NOT HARDWARE")
        self.receipt={"schema_version":1,"kind":"s2b-runtime-platform-compatibility/1.0.0","role":"INDEPENDENT_REVIEWER","status":"PASS","scope":"visibility0_cache_probe_only","visibility_parameter":0,
                      "source_sha256":self.sources,"artifacts":{"compiled_xsa":self.bindings["xsa"],"implemented_xsa":bind(implemented),"init_elf":self.bindings["init_elf"],"app_elf":self.bindings["app_elf"],"bit":self.bindings["bit"],"build_details":bind(self.build_path),"platform_manifest":bind(platform)},"checks":dict.fromkeys(p.COMPAT_CHECKS,True)}
        self.receipt_path=self.directory/"unit_fixture_receipt_not_approval.json";write(self.receipt_path,self.receipt)
        exe=Path(r"D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe")
        server=self.directory/"unit_server_identity.json";write(server,{"status":"OWNED_SERVER_READY","native":{"ProcessId":123,"ExecutablePath":str(exe),"CreationTimeFileTimeUtc":"123"},"native_sha256":bind(exe)["sha256"]})
        self.cfg={"schema_version":1,"source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REAL_ROOT).decode().strip(),"run_dir":"UNIT_UNUSED","build_details":bind(self.build_path),"bindings":self.bindings,"compat_review":bind(self.receipt_path),"cold_basis":self.bindings["interface"],"owned_hw_server_identity":bind(server),"uart_identity":{"port":"COM4","name":"CP210x (COM4)","pnp_device_id":"UNIT","config_manager_error_code":0},"cpu_seed":1,"dap_seed":2,"response_timeout_seconds":1,
                  "pyserial_files":[bind(f) for f in sorted(serial.parent.rglob("*.py"))],"sdk_files":{name:bind(file) for name,file in p.sdk_source_closure().items()}}
        self.observed_head=self.cfg["source_commit"]
        self.record={"calls":[]};self.log=p.Recorder(self.directory/"preflight_calls.jsonl",self.record)
    def tearDown(self):self.log.stream.close()
    def check(self):
        import check_s2b_inference_platform as platform
        original=subprocess.run
        def checked(command,**kwargs):
            if "--mode" in command:return subprocess.CompletedProcess(command,0,b"UNIT_CHECKER_MOCK",b"")
            if command==["git","rev-parse","HEAD"]:return subprocess.CompletedProcess(command,0,(self.observed_head+"\n").encode(),b"")
            return original(command,**kwargs)
        with patch.object(platform,"check_static",return_value=self.sources),patch.object(p.subprocess,"run",side_effect=checked):return p._preflight(self.cfg,self.record,self.log)
    def test_bound_schema_fixture_positive_without_runtime(self):
        self.check();self.assertEqual(self.record["verified_inputs"]["compiled_build_status"],"PASS_OFFLINE_FULL_XSA_BUILD")
        self.assertNotIn("xsdb",sys.modules)
    def test_prior_jtag_source_and_changed_bytes_rejected(self):
        # 真实历史Git原字节用于反例，临时文件不冒充当前已批准实现。
        prior=subprocess.check_output(["git","show","6d3fd8567b579a51d4042667d47af7d94f2f5a97:verification/s2b_board_jtag.py"],cwd=REAL_ROOT)
        self.assertEqual(hashlib.sha256(prior).hexdigest(),"91bbf5bc8ac5ef9bee37ce6491627a6ac8f38a53b7bba113d1b83447b2ecddf0")
        current=Path(j.__file__).read_bytes()
        self.assertEqual(hashlib.sha256(current).hexdigest(),p.JTAG_SHA)
        for label,raw in (("prior_frozen",prior),("changed_bytes",current+"\n# MOCK字节漂移\n".encode("utf-8"))):
            with self.subTest(label=label):
                file=self.directory/("mock_"+label+".py");file.write_bytes(raw)
                self.cfg["bindings"]["tool_source"]=bind(file)
                with self.assertRaisesRegex(p.VisibilityProbeError,"固定T16候选精确版本"):self.check()
                self.assertNotIn("xsdb",sys.modules)
                self.assertNotIn("serial",sys.modules)
    def test_source_head_drift_rejected_before_sdk_inputs(self):
        self.cfg["source_commit"]="6d00ff2d05e92fa6cff05243fb620f8a0232b9f1"
        self.observed_head="1f2f9b964135ae6b92ccf557fd3f1de9639c3f46"
        with self.assertRaisesRegex(p.VisibilityProbeError,"实际HEAD不同"):self.check()
    def test_artifact_sha_drift_rejected(self):
        for key in ("bit","app_elf","init_elf","xsa"):
            with self.subTest(key=key):
                saved=self.cfg["bindings"][key]["sha256"];self.cfg["bindings"][key]["sha256"]="0"*64
                with self.assertRaises(p.helpers()[0].JtagError):self.check()
                self.cfg["bindings"][key]["sha256"]=saved
        for key in ("compat_review","build_details"):
            saved=self.cfg[key]["sha256"];self.cfg[key]["sha256"]="0"*64
            with self.assertRaises(p.helpers()[0].JtagError):self.check()
            self.cfg[key]["sha256"]=saved
    def test_unit_build_and_unapproved_receipt_rejected(self):
        for field,value in [("role","MOCK_REVIEWER"),("status","FAIL"),("scope","model_run"),("visibility_parameter",1),("source_sha256",{})]:
            with self.subTest(field=field):
                row=copy.deepcopy(self.receipt);row[field]=value;file=self.directory/("bad_"+field+".json");write(file,row);self.cfg["compat_review"]=bind(file)
                with self.assertRaises(p.VisibilityProbeError):self.check()
        self.cfg["compat_review"]=bind(self.receipt_path)
        build=json.loads(self.build_path.read_text(encoding="utf-8"));build["status"]="PASS_UNIT_ONLY_PS_XSA_BUILD";file=self.directory/"unit_bad_build.json";write(file,build);self.cfg["build_details"]=bind(file)
        with self.assertRaises(p.helpers()[1].TransportError):self.check()
    def test_checks_and_pyserial_closure_required(self):
        for name in p.COMPAT_CHECKS:
            row=copy.deepcopy(self.receipt);row["checks"][name]=False;file=self.directory/(name+".json");write(file,row);self.cfg["compat_review"]=bind(file)
            with self.assertRaises(p.VisibilityProbeError):self.check()
        self.cfg["compat_review"]=bind(self.receipt_path);self.cfg["pyserial_files"].pop()
        with self.assertRaises(p.VisibilityProbeError):self.check()
    def test_sdk_source_missing_duplicate_drift_path_rejected(self):
        original=copy.deepcopy(self.cfg["sdk_files"])
        for kind in ("missing","extra","hash","path"):
            with self.subTest(kind=kind):
                self.cfg["sdk_files"]=copy.deepcopy(original)
                if kind=="missing":del self.cfg["sdk_files"]["xsdb.session"]
                if kind=="extra":self.cfg["sdk_files"]["duplicate_session"]=original["xsdb.session"]
                if kind=="hash":self.cfg["sdk_files"]["xsdb.session"]["sha256"]="0"*64
                if kind=="path":self.cfg["sdk_files"]["xsdb.session"]=original["xsdb.target"]
                with self.assertRaises((p.VisibilityProbeError,p.helpers()[0].JtagError)):self.check()
        self.cfg["sdk_files"]=original
    def test_strict_json_bound_inputs_and_schema_rejected(self):
        cases=[("compat_review",self.receipt_path),("build_details",self.build_path),("owned_hw_server_identity",Path(self.cfg["owned_hw_server_identity"]["path"]))]
        for label,path in cases:
            for raw in ('{"status":"FAIL","status":"PASS"}','{"nested":{"path":"bad","path":"good"}}','{"x":NaN}','{"x":Infinity}','{"schema_version":true}'):
                with self.subTest(label=label,raw=raw):
                    file=self.directory/(label+"_bad_"+hashlib.sha256(raw.encode()).hexdigest()+".json");file.write_text(raw,encoding="utf-8")
                    self.cfg[label]=bind(file)
                    with self.assertRaises(p.VisibilityProbeError):self.check()
            self.cfg[label]=bind(path)
        self.cfg["schema_version"]=True
        with self.assertRaises(p.VisibilityProbeError):self.check()
        self.cfg["schema_version"]=1
        for raw in ('{"schema_version":true}','{"schema_version":1,"checks":[{"status":"FAIL","status":"PASS"}]}'):
            row=copy.deepcopy(self.receipt);file=self.directory/("manifest_bad_"+hashlib.sha256(raw.encode()).hexdigest()+".json");file.write_text(raw,encoding="utf-8")
            row["artifacts"]["platform_manifest"]=bind(file)
            receipt=self.directory/("receipt_manifest_"+hashlib.sha256(raw.encode()).hexdigest()+".json");write(receipt,row)
            self.cfg["compat_review"]=bind(receipt)
            with self.assertRaises(p.VisibilityProbeError):self.check()
    def test_platform_manifest_and_native_check_fail_closed(self):
        for status,reason in [("FAIL","native failed"),("NOT_RUN","pending"),("NOT_APPLICABLE","")]:
            with self.subTest(status=status):
                row=copy.deepcopy(self.receipt)
                file=self.directory/("platform_"+status+".json")
                write(file,{"schema_version":1,"checks":[{"status":status,"reason":reason}]})
                row["artifacts"]["platform_manifest"]=bind(file)
                receipt=self.directory/("receipt_"+status+".json");write(receipt,row)
                self.cfg["compat_review"]=bind(receipt)
                with self.assertRaises(p.VisibilityProbeError):self.check()
        self.cfg["compat_review"]=bind(self.receipt_path)
        import check_s2b_inference_platform as platform
        original=subprocess.run
        def failed_checker(command,**kwargs):
            if "--mode" in command:return subprocess.CompletedProcess(command,2,b"UNIT_CHECKER_NATIVE_FAIL",b"raw error")
            if command==["git","rev-parse","HEAD"]:return subprocess.CompletedProcess(command,0,(self.observed_head+"\n").encode(),b"")
            return original(command,**kwargs)
        with patch.object(platform,"check_static",return_value=self.sources),patch.object(p.subprocess,"run",side_effect=failed_checker),self.assertRaises(p.VisibilityProbeError):
            p._preflight(self.cfg,self.record,self.log)
        self.assertEqual(self.record["platform_evidence_check"]["native_exit_code"],2)

class ImportTests(unittest.TestCase):
    """fresh subprocess证明导入/--help零SDK与串口导入。"""
    def test_help_and_import_without_hardware_modules(self):
        completed=subprocess.run([sys.executable,str(Path(p.__file__)),"--help"],capture_output=True)
        self.assertEqual(completed.returncode,0)
        code="import importlib.util,sys; s=importlib.util.spec_from_file_location('probe',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); assert 'xsdb' not in sys.modules and 'serial' not in sys.modules"
        completed=subprocess.run([sys.executable,"-c",code,str(Path(p.__file__))],capture_output=True)
        self.assertEqual(completed.returncode,0,completed.stderr)

class SdkBoundaryTests(unittest.TestCase):
    """真实官方方法AST复用与运行来源门禁，禁止TCF连接或SDK实际导入。"""
    def test_official_connect_server_disappears_never_autolaunch(self):
        source=p.SDK_INIT.parent/"session.py"
        tree=ast.parse(source.read_text(encoding="utf-8"))
        cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=="Session")
        connect=copy.deepcopy(next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=="connect"));connect.decorator_list=[]
        stub=ast.parse('class Session:\n def __init__(self):\n  self.__channel_map={}\n  self.launches=[]\n def __launch_server(self,server,url):\n  self.launches.append((server,url))\n  raise RuntimeError("UNIT_AUTOSTART_REACHED")\n').body[0]
        stub.body.append(connect);namespace={"argparse":argparse,"check_int":int,"tcf":SimpleNamespace(connect=lambda url:(_ for _ in ()).throw(RuntimeError("UNIT_SERVER_DISAPPEARED")))}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[stub],type_ignores=[])),str(source),"exec"),namespace)
        unsafe=namespace["Session"]()
        with self.assertRaises(Exception):unsafe.connect(url="TCP:127.0.0.1:3121",server="hw_server")
        self.assertEqual(unsafe.launches,[("hw_server","TCP:127.0.0.1:3121")])
        safe=namespace["Session"]()
        with self.assertRaises(Exception):safe.connect(url="TCP:localhost:3121",server="hw_server")
        self.assertEqual(safe.launches,[])
        fixture=LifecycleTests();fixture.setUp()
        launches=[]
        def connect(**kwargs):
            with self.assertRaises(Exception):safe.connect(**kwargs)
            launches.extend(safe.launches);raise RuntimeError("UNIT_SERVER_EXITED_AFTER_IDENTITY")
        fixture.session.connect=connect
        result=fixture.execute("connect")
        self.assertEqual(launches,[]);self.assertEqual(result["native_exit_code"],2)
        self.assertFalse(any(x[0]=="stop" for x in fixture.session.operations))
    def test_bad_config_preserves_raw_before_any_runtime(self):
        fixture=LifecycleTests();fixture.setUp()
        for index,raw in enumerate((b'{"run_dir":"bad","run_dir":"later"}',b'{"schema_version":true,"run_dir":"bad"}',b'{"value":NaN}',b'{"nested":{"path":"a","path":"b"}}')):
            file=fixture.directory/("malformed_%d.json"%index);file.write_bytes(raw)
            with patch.object(p,"ROOT",fixture.directory),patch.object(p,"_runtime",side_effect=AssertionError("不能导入SDK")),self.assertRaises(p.VisibilityProbeError):p.run(file)
            matches=list((fixture.directory/"report/evidence/S2B-T19").glob("config_rejection_*/input_config.json.raw"))
            self.assertTrue(any(x.read_bytes()==raw for x in matches))
        self.assertFalse(fixture.session.operations)
    def test_actual_module_and_method_source_gate(self):
        files={name:bind(file) for name,file in p.sdk_source_closure().items()}
        required=("xsdb","xsdb.xsdb_debug_session","xsdb.session","xsdb.target","xsdb._tcf_reset","xsdb._breakpoint")
        modules={name:types.ModuleType(name) for name in required}
        methods={"xsdb":("start_debug_session","dispose"),"xsdb.xsdb_debug_session":("xsdb_start_debug_session","dispose_session"),"xsdb.session":("Session.__init__","Session.connect","Session.disconnect","Session.targets"),"xsdb.target":("Target.__init__","Target.state","Target.stop","Target.con","Target.dow","Target.bpadd","Target.mrd","Target.mwr","Target.rst","Target.fpga","Target.rrd","Target.loadhw","Target.unloadhw"),"xsdb._tcf_reset":("TcfReset.rst_cmd","TcfReset.rst_capabilities"),"xsdb._breakpoint":("Breakpoint.remove","Breakpoint.status")}
        def find(code,name):
            if code.co_qualname==name:return code
            for value in code.co_consts:
                if isinstance(value,types.CodeType):
                    result=find(value,name)
                    if result is not None:return result
        for name,module in modules.items():
            module.__file__=files[name]["path"]
            if name not in methods:continue
            compiled=compile(Path(module.__file__).read_text(encoding="utf-8-sig"),module.__file__,"exec",dont_inherit=True)
            for method in methods[name]:
                parts=method.split(".");target=module
                if len(parts)==2:
                    if not hasattr(module,parts[0]):setattr(module,parts[0],type(parts[0],(),{"__module__":name}))
                    target=getattr(module,parts[0])
                function=types.FunctionType(find(compiled,method),{"__name__":name});setattr(target,parts[-1],function)
        modules["xsdb.session"].Target=modules["xsdb.target"].Target
        modules["xsdb.xsdb_debug_session"].Session=modules["xsdb.session"].Session
        modules["xsdb"].debug_session=None;modules["xsdb.xsdb_debug_session"].debug_session_int_obj=None
        config={"sdk_files":files}
        with patch.dict(sys.modules,modules),patch.object(p,"verify_native_alias",return_value={"scope":"NATIVE_TEST_SEPARATE"}):
            p.verify_runtime_sources(config)
            for class_name in ("Session","Target"):
                cls=getattr(modules["xsdb."+class_name.lower()],class_name)
                for attribute in ("__module__","__name__","__qualname__"):
                    with self.subTest(class_name=class_name,attribute=attribute):
                        old=getattr(cls,attribute);setattr(cls,attribute,"FOREIGN_CLASS")
                        with self.assertRaisesRegex(p.VisibilityProbeError,"类定义来源不同"):p.verify_runtime_sources(config)
                        setattr(cls,attribute,old)
            for module_name,attribute in (("xsdb.xsdb_debug_session","Session"),("xsdb.session","Target")):
                with self.subTest(alias=module_name+"."+attribute):
                    old=getattr(modules[module_name],attribute);setattr(modules[module_name],attribute,type(attribute,(),{}))
                    with self.assertRaisesRegex(p.VisibilityProbeError,"别名不同"):p.verify_runtime_sources(config)
                    setattr(modules[module_name],attribute,old)
            modules["xsdb"].debug_session=SimpleNamespace()
            with self.assertRaises(p.VisibilityProbeError):p.verify_runtime_sources(config)
            modules["xsdb"].debug_session=None
            with self.assertRaises(p.VisibilityProbeError):p.verify_runtime_sources(config,SimpleNamespace())
            original=modules["xsdb.session"].__file__;modules["xsdb.session"].__file__=files["xsdb.target"]["path"]
            with self.assertRaises(p.VisibilityProbeError):p.verify_runtime_sources(config)
            modules["xsdb.session"].__file__=original
            modules["xsdb.session"].Session.connect=lambda **kwargs:None
            with self.assertRaises(p.VisibilityProbeError):p.verify_runtime_sources(config)

    def test_native_shared_metadata_and_physical_images_exact(self):
        names=("xv_pycommontasks","xv_hsmpytasks")
        files={name:bind(file) for name,file in p.sdk_source_closure().items()}
        final=files[names[1]]["path"]
        def fixture_native():
            module=types.ModuleType("vivado");module.__file__=final
            loader=importlib.machinery.ExtensionFileLoader(names[1],final)
            module.__spec__=importlib.util.spec_from_loader(names[1],loader)
            return module,{name:{"handle":i+1,"path":files[name]["path"]} for i,name in enumerate(names)}
        module,images=fixture_native()
        with patch.dict(sys.modules,dict.fromkeys(names,module)),patch.object(p,"_loaded_native_images",return_value=images):
            observed=p.verify_native_alias(files)
            self.assertNotEqual(observed[names[0]]["path"],observed[names[1]]["path"])
        for kind in ("unshared","name","spec_name","spec_origin","loader_type","loader_name","loader_path","file","image_path","binding_path","binary_hash","query_failure"):
            with self.subTest(native_fault=kind):
                module,images=fixture_native();declared=copy.deepcopy(files);modules=dict.fromkeys(names,module)
                if kind=="unshared":modules[names[0]]=types.ModuleType("vivado")
                if kind=="name":module.__name__="foreign"
                if kind=="spec_name":module.__spec__.name=names[0]
                if kind=="spec_origin":module.__spec__.origin=files[names[0]]["path"]
                if kind=="loader_type":module.__spec__.loader=SimpleNamespace(name=names[1],path=final)
                if kind=="loader_name":module.__spec__.loader.name=names[0]
                if kind=="loader_path":module.__spec__.loader.path=files[names[0]]["path"]
                if kind=="file":module.__file__=files[names[0]]["path"]
                if kind=="image_path":images[names[0]]["path"]=final
                if kind=="binding_path":declared[names[0]]=declared[names[1]]
                if kind=="binary_hash":declared[names[0]]["sha256"]="0"*64
                error=p.VisibilityProbeError("UNIT_DLL_QUERY_FAILURE") if kind=="query_failure" else None
                with patch.dict(sys.modules,modules),patch.object(p,"_loaded_native_images",return_value=images,side_effect=error):
                    with self.assertRaises((p.VisibilityProbeError,p.helpers()[0].JtagError)):p.verify_native_alias(declared)

class CsrDebugMapTests(unittest.TestCase):
    """独立最小地址块与SDK状态反例；不导入SDK或操作设备。"""
    def setUp(self):
        parent=REAL_ROOT/"tmp/2B/S2B-T19"
        parent.mkdir(exist_ok=True)
        self.directory=Path(tempfile.mkdtemp(prefix="unit_csr_map_",dir=parent))
        self.binding=self.directory/"implemented.xsa"
        self.region={"BASEVALUE":"0x43C00000","HIGHVALUE":"0x43C0FFFF","INSTANCE":"infer",
                     "MEMTYPE":"REGISTER","MASTERBUSINTERFACE":"M_AXI_GP0","SLAVEBUSINTERFACE":"S_AXI"}
        self.write_hwh([self.region])
        self.calls=[];self.scenario="normal"
        self.session=SimpleNamespace(_curtarget=None,_curchan="owned",_designtable={},_memmap_ctxs={},_memmaptable={})
        self.apu=SimpleNamespace(_ctx="apu",_id=10,_name="APU")
        def select(*,id):
            self.calls.append(("select",id))
            selected=self.apu if self.scenario!="wrong_selection" else SimpleNamespace(_ctx="fpga",_id=13,_name="xc7z020")
            self.session._curtarget=selected
            return selected
        def loadhw(*,hw,mem_ranges):
            self.assertIs(self.session._curtarget,self.apu)
            self.calls.append(("loadhw",hw,mem_ranges))
            self.session._designtable[hw]={"design":"UNIT_FAKE_DESIGN"}
            if self.scenario=="partial_load":raise RuntimeError("UNIT_PARTIAL_LOAD")
            value={"base":0x43C00000,"high":0x43C0FFFF,"size":0x10000,"type":"REGISTER","flags":3}
            entry={"Addr":0x43C00000,"Size":0x10000,"Flags":3}
            if self.scenario=="expanded":value["size"]=0x20000
            if self.scenario=="flags":value["flags"]=7
            if self.scenario=="entry_expanded":entry["Size"]=0x20000
            if self.scenario=="entry_flags":entry["Flags"]=7
            if self.scenario=="file_map":entry["FileName"]="UNOWNED_FILE"
            context="cpu0" if self.scenario=="wrong_context" else "apu"
            self.session._memmap_ctxs={"owned":{context:{"infer_S_AXI":value}}}
            self.session._memmaptable={"owned":{context:{0x43C00000:[entry]}}}
            if self.scenario=="extra":self.session._memmaptable["owned"][context][0x44000000]=[{"Addr":0x44000000,"Size":0x1000,"Flags":3}]
            if self.scenario=="missing":self.session._memmap_ctxs={}
        def unloadhw():
            self.assertIs(self.session._curtarget,self.apu)
            self.calls.append(("unloadhw",))
            if self.scenario=="cleanup_failure":raise RuntimeError("UNIT_UNLOAD_FAILURE")
            self.session._designtable.clear();self.session._memmap_ctxs.clear();self.session._memmaptable.clear()
        self.session.targets=select;self.apu.loadhw=loadhw;self.apu.unloadhw=unloadhw
        def gate():
            self.calls.append(("gate",))
            self.session._curtarget=SimpleNamespace(_ctx="fpga")
        self.controller=SimpleNamespace(targets={"apu":self.apu},gate=gate)
        self.record={"calls":[],"verified_inputs":{"compat_artifacts":{"implemented_xsa":bind(self.binding)}}}
        self.log=p.Recorder(self.directory/"calls.jsonl",self.record);self.owner={}
        self.runtime_patch=patch.object(p,"verify_runtime_sources",return_value={"scope":"UNIT_MOCK"})
        self.runtime_patch.start()
    def tearDown(self):
        self.runtime_patch.stop();self.log.stream.close()
    def write_hwh(self,regions,duplicate=False):
        text="<SYSTEM>"+"".join("<MEMRANGE "+" ".join(f'{k}="{v}"' for k,v in row.items())+"/>" for row in regions)+"</SYSTEM>"
        with zipfile.ZipFile(self.binding,"w") as archive:
            archive.writestr("unit.hwh",text)
            if duplicate:archive.writestr("second.hwh",text)
    def register(self):
        self.record["verified_inputs"]["compat_artifacts"]["implemented_xsa"]=bind(self.binding)
        return p.register_csr_debug_map({},self.record,self.log,self.session,self.controller,self.owner)
    def clear(self):
        return p.clear_csr_debug_map({},self.record,self.log,self.session,self.owner)
    def test_exact_window_selects_apu_and_cleans_owned_map(self):
        self.register()
        self.assertEqual(self.calls[:2],[("gate",),("select",10)])
        self.assertEqual(self.calls[2],("loadhw",str(self.binding.absolute()),[[0x43C00000,0x43C0FFFF]]))
        self.assertEqual(self.record["debug_memory_map"]["status"],"REGISTERED_CSR_ONLY")
        self.clear();self.assertEqual(self.record["debug_memory_map"]["cleanup"],"OWNED_HW_MAP_CLEARED")
    def test_hwh_rejects_missing_duplicate_expanded_and_wrong_interface(self):
        for rows in ([],[self.region,self.region], [{**self.region,"HIGHVALUE":"0x43C1FFFF"}],
                     [{**self.region,"INSTANCE":"other"}],[{**self.region,"MEMTYPE":"MEMORY"}],
                     [{**self.region,"MASTERBUSINTERFACE":"M_AXI_GP1"}]):
            with self.subTest(rows=rows):
                self.write_hwh(rows)
                with self.assertRaises(p.VisibilityProbeError):self.register()
                self.assertFalse(any(row[0]=="loadhw" for row in self.calls))
        self.write_hwh([self.region],duplicate=True)
        with self.assertRaises(p.VisibilityProbeError):self.register()
    def test_actual_sdk_mapping_growth_permissions_context_or_absence_rejected(self):
        for scenario in ("expanded","flags","entry_expanded","entry_flags","file_map","wrong_context","extra","missing"):
            with self.subTest(scenario=scenario):
                self.scenario=scenario
                with self.assertRaises(p.VisibilityProbeError):self.register()
                self.assertTrue(self.owner["attempted"])
                self.clear()
    def test_wrong_selection_or_preexisting_design_rejected(self):
        self.scenario="wrong_selection"
        with self.assertRaises(p.VisibilityProbeError):self.register()
        self.assertFalse(self.owner)
        self.scenario="normal";self.session._designtable["other"]={}
        with self.assertRaises(p.VisibilityProbeError):self.register()
        self.assertFalse(any(row[0]=="loadhw" for row in self.calls))
    def test_partial_load_and_cleanup_errors_remain_errors(self):
        self.scenario="partial_load"
        with self.assertRaisesRegex(RuntimeError,"UNIT_PARTIAL_LOAD"):self.register()
        self.assertTrue(self.owner["attempted"]);self.clear()
        self.scenario="normal";self.register();self.scenario="cleanup_failure"
        with self.assertRaisesRegex(RuntimeError,"UNIT_UNLOAD_FAILURE"):self.clear()
        self.assertEqual(self.record["debug_memory_map"]["cleanup"],"NOT_RUN")
    def test_changed_cleanup_target_or_channel_rejected(self):
        self.register();self.session._curchan="different"
        with self.assertRaises(p.VisibilityProbeError):self.clear()
        self.assertFalse(any(row[0]=="unloadhw" for row in self.calls))

if __name__=="__main__":unittest.main()
