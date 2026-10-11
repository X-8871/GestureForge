"""封存只读JTAG原件；原生日志编码区别于UTF8业务输出，首轮失败保留。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
FORMAL = ROOT / "report/evidence/S2B-T14/jtag_readonly_20261011_r02"
COMMIT = "5ea54b441bd885e10eac4794cbad5ad48c510a49"


def sha(path):
    """绑定真实普通文件字节。"""
    assert path.is_file() and not path.is_symlink(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """UTF-8写入新目标，绝不覆盖本次原件。"""
    assert path.parent.is_dir() and not path.exists(), path
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """核对真实查询身份、原生返回码、无写操作及完整清理。"""
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head == COMMIT
    probe = RUN / "jtag_targets_probe.py"
    assert sha(probe) == "201dc67de8427662fdf1852309c270eda24f2a9bf70cc2670802b152208c3dc6"
    result = json.loads((RUN / "jtag_targets_result.json").read_text(encoding="utf-8"))
    native = json.loads((RUN / "vitis_probe.native.json").read_text(encoding="utf-8"))
    identity = json.loads((RUN / "hw_server_identity.json").read_text(encoding="utf-8"))
    close = json.loads((RUN / "server_close.json").read_text(encoding="utf-8"))
    assert result["status"] == "TARGETS_ENUMERATED" and not result["cleanup_errors"]
    assert native["native_exit_code"] == 0 and result["expected_hw_server_pid"] == identity["native"]["ProcessId"] == close["native_pid"]
    assert close["status"] == "OWNED_SERVER_CLOSED" and close["identity_checked"] is True
    assert close["native_absent"] is True and close["listeners"] == [] and close["launcher_current"] is None
    assert close["native_exit_code"] == -1
    targets = list(result["targets"].values())
    assert len(targets) == 4 and {r["name"] for r in targets} == {"APU", "ARM Cortex-A9 MPCore #0", "ARM Cortex-A9 MPCore #1", "xc7z020"}
    assert {r["jtag_cable_serial"] for r in targets} == {"210512180081"}
    apu = next(r for r in targets if r["name"] == "APU")
    cpu = [r for r in targets if r["name"].startswith("ARM Cortex-A9")]
    assert all(r["parent_ctx"] == apu["target_ctx"] and r["state_reason"] == "Running" for r in cpu)
    forbidden = (".stop(", ".rst(", ".dow(", ".con(", ".mrd(", ".mwr(", ".fpga(")
    assert not any(token in probe.read_text(encoding="utf-8") for token in forbidden)
    host = json.loads((RUN / "host_resource_preflight.json").read_text(encoding="utf-8"))["value"]
    ports = json.loads(host["output"])["serial"]
    assert len(ports) == 1 and ports[0]["DeviceID"] == "COM4" and ports[0]["ConfigManagerErrorCode"] == 0
    assert ports[0]["PNPDeviceID"] == "USB\\VID_10C4&PID_EA60\\D02E61162787ED11A536569F9D1CC348"
    for path in RUN.iterdir():
        if path.is_file() and path.suffix in (".py", ".ps1", ".json", ".log"):
            if path.name != "vitis_probe.stdout.log":
                path.read_bytes().decode("utf-8")
    assert FORMAL.parent.is_dir() and not FORMAL.exists()
    FORMAL.mkdir()
    files = []
    for path in sorted(RUN.iterdir()):
        if not path.is_file():
            continue
        assert path.suffix in (".py", ".ps1", ".json", ".log"), path
        target = FORMAL / path.name
        shutil.copyfile(path, target)
        assert sha(path) == sha(target)
        files.append(dict(path=target.relative_to(ROOT).as_posix(), sha256=sha(target),
            role="source" if target.suffix in (".py", ".ps1") else "log" if target.suffix == ".log" else "result"))
    scope = FORMAL / "authorization_and_scope.json"
    save(scope, dict(source_commit=COMMIT, authorization="Wong已授权阶段2B工具链与实板调试；本次仅连接和枚举。",
        result="PASS_READONLY_CONNECTION_AND_CLEANUP_ONLY", target_count=4, serial_port="COM4", cable_serial="210512180081",
        cpu_states={r["name"]:r["state_reason"] for r in cpu}, api_scope="start_debug_session/connect/targets/disconnect/dispose",
        closed_native_service_exit_code=-1, close_host_exit_code=0, hardware_program_execution="NOT_RUN",
        limitations=["本次CPU状态仅瞬时枚举快照，不持续监视。","未读取BOOT_MODE/EOS/CSR/时钟或DDR，不继承任何部署准入。","JTAG器件名称不证明XC/XA或速度/温度等级。","硬件服务由本任务Stop-Process释放，真实服务退出码-1；清理命令0，二者不混同。","峰内存未测；不计为PS初始化、UART/DDR、模型、109/1000或G3–G5。"] ))
    files.append(dict(path=scope.relative_to(ROOT).as_posix(), sha256=sha(scope), role="result"))
    checks = [dict(name="已审只读目标枚举",status="PASS",command=subprocess.list2cmdline(native["command"]),exit_code=0,
        reason="本次原生Vitis0，业务TARGETS_ENUMERATED，disconnect/dispose无错误。")]
    for name, script in (("本任务独占服务启动", "start_owned_server.ps1"), ("本任务服务身份核对与闭合", "close_owned_server.ps1")):
        checks.append(dict(name=name,status="PASS",command=subprocess.list2cmdline(["powershell.exe","-NoProfile","-File",str(RUN/script)]),
            exit_code=0,reason="对应真实host返回码为0，完整身份与监听字段见本次原件；服务原生退出码-1另列。"))
    checks.append(dict(name="部署与2B功能验收",status="NOT_RUN",command=None,exit_code=None,reason="本Run只做连接枚举。"))
    manifest = dict(schema_version=1,stage="2B",task_id="S2B-T14",run_id=FORMAL.name,source_commit=COMMIT,
        evidence_dir=FORMAL.relative_to(ROOT).as_posix(),interfaces=[],
        interfaces_not_applicable_reason="只读目标枚举与服务生命周期，不消费CSR/AXI/memory业务接口。",
        files=files,checks=checks,tool_versions=dict(Vitis="2026.1",XSDB="Vitis2026.1公共Python SDK",python=sys.version),
        limitations=json.loads(scope.read_text(encoding="utf-8"))["limitations"])
    initial = FORMAL / "delivery_manifest.json"
    save(initial,manifest)
    command = [sys.executable,"-X","utf8","-B",str(ROOT/"verification/check_stage_delivery.py"),
        "--mode","evidence","--manifest",str(initial),"--project-root",str(ROOT)]
    started=time.monotonic()
    checked=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=55)
    paths=[]
    for suffix,data in (("stdout.log",checked.stdout),("stderr.log",checked.stderr)):
        path=RUN/("package_check."+suffix)
        with path.open("xb") as stream:
            stream.write(data)
        paths.append(path)
    path=RUN/"package_check.native.json"
    save(path,dict(command=command,native_exit_code=checked.returncode,elapsed_seconds=time.monotonic()-started))
    paths.append(path)
    assert checked.returncode==0,checked.stdout.decode("utf-8")
    for path in paths:
        target=FORMAL/path.name
        shutil.copyfile(path,target)
        assert sha(path)==sha(target)
        files.append(dict(path=target.relative_to(ROOT).as_posix(),sha256=sha(target),role="log" if target.suffix==".log" else "result"))
    files.append(dict(path=initial.relative_to(ROOT).as_posix(),sha256=sha(initial),role="artifact"))
    checks.append(dict(name="本Run证据包装",status="PASS",command=subprocess.list2cmdline(command),exit_code=0,reason="只检查清单与文件绑定，不代表任何功能验收。"))
    final=FORMAL/"delivery_manifest_r02.json"
    save(final,manifest)
    print(json.dumps(dict(status="PACKAGED_READONLY_CONNECTION_ONLY",manifest_sha256=sha(final),files=len(files)),ensure_ascii=False))


if __name__ == "__main__":
    main()
