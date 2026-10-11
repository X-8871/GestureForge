"""T19离线mock生命周期和固定绑定反例；不导入XSDB/serial、不操作实物。"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
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
            file=self.directory/name;file.write_bytes(fixture.elf_bytes(app=name=="app_elf") if name.endswith("elf") else name.encode());self.bindings[name]=bind(file)
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
    def execute(self,scenario="normal",identity=None):
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
        if scenario=="chain":self.session.rows["cpu1"]["jtag_cable_serial"]="wrong"
        if scenario=="cpu0_stop":self.session.objects[11].stop=lambda **kwargs:(_ for _ in ()).throw(RuntimeError("mock CPU0 stop failure"))
        if scenario=="breakpoint_cleanup":
            original=self.session.objects[11].bpadd
            def fail_remove(**kwargs):
                bp=original(**kwargs);bp.remove=lambda:(_ for _ in ()).throw(RuntimeError("mock breakpoint cleanup failure"));return bp
            self.session.objects[11].bpadd=fail_remove
        file=self.directory/"unit_config.json";write(file,self.config)
        with patch.object(p,"ROOT",self.directory),patch.object(p,"_preflight",return_value=(j,j.transport,self.build,self.expected)),patch.object(p,"_runtime",side_effect=self.runtime),patch.object(p,"_identity_snapshot",return_value=self.actual if identity is None else identity):
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
        self.assertEqual(result["cache_probe"]["phase0_raw_hex"][:8],"78563412")
        self.assertEqual(len(Path(self.config["run_dir"]).joinpath("uart_rx_raw.bin").read_bytes()),result["banner"]["bytes"]+2*(40+40+256))
    def test_sdk_uart_and_cleanup_failures_preserve_originals(self):
        for scenario in ["start_session","connect","boot","chain","cpu0_stop","init_download","init","fpga","app","banner","cache","serial_open","serial_close","disconnect","dispose","breakpoint_cleanup"]:
            with self.subTest(scenario=scenario):
                self.setUp();result=self.execute(scenario);self.assertEqual(result["native_exit_code"],2)
                self.assertTrue((Path(self.config["run_dir"])/"entry_calls.jsonl").is_file())
                if scenario=="connect":self.assertIn(("disconnect",{}),self.session.operations)
                if scenario in ("serial_close","disconnect","dispose","breakpoint_cleanup"):self.assertTrue(result["cleanup_errors"] or json.loads((Path(self.config["run_dir"])/"jtag_result.json").read_text(encoding="utf-8"))["cleanup_errors"])
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

class PreflightTests(unittest.TestCase):
    """仅对未授权UNIT fixture核验schema/bindings；不创建正式compat receipt。"""
    def setUp(self):
        parent=REAL_ROOT/"tmp/2B/S2B-T19";parent.mkdir(exist_ok=True)
        self.directory=Path(tempfile.mkdtemp(prefix="unit_preflight_",dir=parent))
        self.bindings={}
        for name in ("init_elf","app_elf","xsa","bit","csr_source","interface"):
            file=self.directory/name;file.write_bytes(fixture.elf_bytes(app=name=="app_elf") if name.endswith("elf") else name.encode());self.bindings[name]=bind(file)
        paths={"entry_source":Path(p.__file__),"tool_source":Path(j.__file__),"transport_source":Path(j.transport.__file__),"platform_checker":REAL_ROOT/"verification/check_s2b_inference_platform.py","elf_parser":REAL_ROOT/"verification/check_s2b_ps_smoke_layout.py","delivery_parser":REAL_ROOT/"verification/check_stage_delivery.py","sdk_init":p.SDK_INIT,"sdk_target":p.SDK_INIT.parent/"target.py",
               "csr_source":REAL_ROOT/"src/s2b_control_csr.sv","interface":REAL_ROOT/"docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"}
        serial=Path(sys.executable).parent/"Lib/site-packages/serial/__init__.py"
        paths["pyserial_init"]=serial
        for key,file in paths.items():self.bindings[key]=bind(file)
        self.sources={"unit-fixture-only":"c"*64}
        platform=self.directory/"unit_platform_manifest.json";write(platform,{"checks":[{"status":"PASS"}]})
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
                  "pyserial_files":[bind(f) for f in sorted(serial.parent.rglob("*.py"))]}
        self.record={"calls":[]};self.log=p.Recorder(self.directory/"preflight_calls.jsonl",self.record)
    def tearDown(self):self.log.stream.close()
    def check(self):
        import check_s2b_inference_platform as platform
        original=subprocess.run
        def checked(command,**kwargs):
            if "--mode" in command:return subprocess.CompletedProcess(command,0,b"UNIT_CHECKER_MOCK",b"")
            return original(command,**kwargs)
        with patch.object(platform,"check_static",return_value=self.sources),patch.object(p.subprocess,"run",side_effect=checked):return p._preflight(self.cfg,self.record,self.log)
    def test_bound_schema_fixture_positive_without_runtime(self):
        self.check();self.assertEqual(self.record["verified_inputs"]["compiled_build_status"],"PASS_OFFLINE_FULL_XSA_BUILD")
        self.assertNotIn("xsdb",sys.modules)
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
    def test_platform_manifest_and_native_check_fail_closed(self):
        for status,reason in [("FAIL","native failed"),("NOT_RUN","pending"),("NOT_APPLICABLE","")]:
            with self.subTest(status=status):
                row=copy.deepcopy(self.receipt)
                file=self.directory/("platform_"+status+".json")
                write(file,{"checks":[{"status":status,"reason":reason}]})
                row["artifacts"]["platform_manifest"]=bind(file)
                receipt=self.directory/("receipt_"+status+".json");write(receipt,row)
                self.cfg["compat_review"]=bind(receipt)
                with self.assertRaises(p.VisibilityProbeError):self.check()
        self.cfg["compat_review"]=bind(self.receipt_path)
        import check_s2b_inference_platform as platform
        original=subprocess.run
        def failed_checker(command,**kwargs):
            if "--mode" in command:return subprocess.CompletedProcess(command,2,b"UNIT_CHECKER_NATIVE_FAIL",b"raw error")
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

if __name__=="__main__":unittest.main()
