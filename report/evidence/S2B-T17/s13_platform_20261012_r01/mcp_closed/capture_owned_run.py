"""捕获本轮自有Vivado六字段身份及资源，不访问板卡。"""
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import psutil

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
WORK = ROOT / "tmp/2B/S2B-T17/s13_launch_prepare_20261012_r01"
SOURCE = "701dc55af0c53a959e84dc0c470f136918f5bd50"

def identity(pid):
    """每次读取真实存活、出生时间和完整参数。"""
    process = psutil.Process(pid)
    birth = process.create_time()
    row = dict(pid=pid, create_time=birth, exe=process.exe(), cwd=process.cwd(),
               cmdline=process.cmdline(), ppid=process.ppid())
    assert process.is_running() and psutil.Process(pid).create_time() == birth
    return row

def save(name, value):
    """只在已核验的本轮目录创建新证据，拒绝覆盖。"""
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write("\n")

def main():
    """绑定真实ROSS启动返回；磁盘与运行时门槛保持。"""
    assert HERE.is_dir() and WORK.is_dir()
    tool = json.loads((HERE / "vivado_start.tool.json").read_text(encoding="utf-8"))
    payload = json.loads(next(x["text"] for x in tool["content"] if x["type"] == "text"))
    assert payload["status"] == "success" and payload["process_id"] == 24504
    log = Path(payload["log_file"])
    assert log.is_file() and log.parent.parent == HERE
    row = identity(payload["process_id"])
    assert row["exe"] == r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe"
    assert row["cmdline"][row["cmdline"].index("-log") + 1] == r".vivado-ai\vivado_71658082_43fdea0e.log"
    assert Path(row["cwd"]).samefile(HERE)
    allowed, aliases = [], []
    for original in (HERE, WORK):
        allowed.append(str(original))
        alternative = str(original)[0].lower() + str(original)[1:]
        if alternative != str(original):
            assert Path(alternative).is_dir() and Path(alternative).samefile(original)
            assert str(original)[1:] == alternative[1:]
            aliases.append(dict(original=str(original), observed_drive_alias=alternative,
                                difference="仅索引0盘符C/c；samefile/stat证实同一目录"))
            allowed.append(alternative)
    assert row["cwd"] in allowed
    heavy = [dict(pid=p.pid, name=p.info["name"], birth=p.info["create_time"])
             for p in psutil.process_iter(["name", "create_time"])
             if (p.info["name"] or "").lower() in ("vivado.exe", "verilator_bin.exe", "xsim.exe", "cc1plus.exe")]
    assert len(heavy) == 1 and heavy[0]["pid"] == row["pid"], heavy
    ram, disk = psutil.virtual_memory().available, psutil.disk_usage("C:/").free
    assert ram >= 536870912 and disk >= 8589934592
    before = json.loads((ROOT / "report/evidence/S2B-T17/s13_source_preflight_20261012_r01/source_before.json").read_text(encoding="utf-8"))
    assert before["source_commit"] == SOURCE and before["source_count"] == 44
    plan = dict(schema_version=1, source_commit=SOURCE, new_run_tree_rss_limit_bytes=6442450944,
                new_run_available_ram_stop_bytes=536870912, minimum_c_disk_free_before_dispatch_bytes=8589934592,
                resource_sample_interval_seconds=1, original_startup_ram_minimum_bytes=4831838208,
                startup_ram_minimum_waiver_authorized=True,
                user_authorization="闲置程序已经关闭了，重新检查内存，达不到门槛也进行综合，继续运行到 JTAG 下载前，需要连接板卡时再叫我。",
                authorization_scope="仅启动RAM门槛豁免；原运行阈值、身份、时序及验收标准保持。",
                actual_pre_start_ram_bytes=ram, actual_pre_start_c_disk_free_bytes=disk,
                launch_jobs=1, general_maxThreads=1, simultaneous_heavy=1,
                supervisor_live_interval_seconds=5, no_log_progress_stop_seconds=900,
                board_connected=False, hardware_access=False)
    binding = dict(row, source_commit=SOURCE, run_id="s13_physical_launch_20261012_r01",
                   allowed_run_dirs=allowed, progress_logs=[str(log)], no_progress_seconds=900,
                   captured_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat())
    assert identity(row["pid"]) == row
    save("resource_plan.json", plan); save("owned_binding.json", binding)
    save("identity_admission.json", dict(status="READY_OFFLINE_SOURCE_AND_RUNTIME_RESOURCES",
        source_commit=SOURCE, six_field_identity=row, parent_identity=identity(row["ppid"]),
        allowed_alias_proof=aliases, current_heavy=heavy, available_ram_bytes=ram,
        c_disk_free_bytes=disk, whole_tree_budget="NOT_YET_MONITORED",
        limitations=["离散准入不代表连续预算；必须guard READY及原生consumer首消费后派发。"] ))
    print(json.dumps(dict(status="READY_OFFLINE_SOURCE_AND_RUNTIME_RESOURCES", pid=row["pid"],
        birth=row["create_time"], cwd=row["cwd"], available_ram_bytes=ram,
        c_disk_free_bytes=disk), ensure_ascii=False))

if __name__ == "__main__":
    main()
