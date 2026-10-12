"""核验本轮唯一自有布线会话、资源及固定综合依赖，不访问实物。"""
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sys
import psutil

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
WORK = ROOT / "tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02"
sys.path.insert(0, str(WORK))
import compat_pins as pins


def identity(pid):
    """读取六字段并重查出生时间，拒绝读取期间身份复用。"""
    process = psutil.Process(pid)
    birth = process.create_time()
    row = dict(pid=pid, create_time=birth, exe=process.exe(), cwd=process.cwd(),
               cmdline=process.cmdline(), ppid=process.ppid())
    assert process.is_running() and psutil.Process(pid).create_time() == birth
    return row


def save(name, value):
    """只写本次精确目录中的新文件，禁止覆盖。"""
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """按已审综合pin核验准入，保留原运行门槛及启动RAM豁免。"""
    pins.require_ready(pnr=True)
    assert pins.SYNTH_CACHE == WORK and pins.PROJECT.parent == WORK
    start = json.loads((HERE / "vivado_start.tool.json").read_text(encoding="utf-8"))
    payload = json.loads(next(x["text"] for x in start["content"] if x["type"] == "text"))
    assert payload["status"] == "success" and type(payload["process_id"]) is int
    log = pins.exact(payload["log_file"])
    assert log.parent.parent == HERE
    row = identity(payload["process_id"])
    assert row["exe"] == r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe"
    assert row["cmdline"].count("-log") == 1
    command_log = Path(row["cmdline"][row["cmdline"].index("-log") + 1])
    assert (Path(row["cwd"]) / command_log).samefile(log)
    assert Path(row["cwd"]).samefile(HERE)
    allowed, aliases = [], []
    for original in (HERE, WORK):
        pins.exact(original, True)
        allowed.append(str(original))
        alternative = str(original)[0].lower() + str(original)[1:]
        if alternative != str(original):
            assert Path(alternative).is_dir() and Path(alternative).samefile(original)
            aliases.append(dict(original=str(original), observed_drive_alias=alternative,
                                difference="仅索引0盘符C/c，实际samefile核验"))
            allowed.append(alternative)
    assert row["cwd"] in allowed
    heavy = [dict(pid=p.pid, name=p.info["name"], birth=p.info["create_time"])
             for p in psutil.process_iter(["name", "create_time"])
             if (p.info["name"] or "").lower() in
             ("vivado.exe", "verilator_bin.exe", "xsim.exe", "cc1plus.exe")]
    assert len(heavy) == 1 and heavy[0]["pid"] == row["pid"], heavy
    ram, disk = psutil.virtual_memory().available, psutil.disk_usage("C:/").free
    assert ram >= 536870912 and disk >= 8589934592
    freeze = json.loads(pins.SOURCE_FREEZE.read_text(encoding="utf-8"))
    assert freeze["source_commit"] == pins.SOURCE_COMMIT
    plan = dict(schema_version=1, source_commit=pins.SOURCE_COMMIT,
                new_run_tree_rss_limit_bytes=6442450944,
                new_run_available_ram_stop_bytes=536870912,
                minimum_c_disk_free_before_dispatch_bytes=8589934592,
                resource_sample_interval_seconds=1,
                original_startup_ram_minimum_bytes=4831838208,
                startup_ram_minimum_waiver_authorized=True,
                user_authorization="再给你三次机会，一定要完成这个时序任务，继续综合",
                authorization_scope="延续离线时序闭合与启动RAM豁免；运行门槛、身份、时序和验收标准保持。",
                actual_pre_start_ram_bytes=ram, actual_pre_start_c_disk_free_bytes=disk,
                launch_jobs=1, general_maxThreads=1, simultaneous_heavy=1,
                supervisor_live_interval_seconds=5, no_log_progress_stop_seconds=900,
                board_connected=False, hardware_access=False)
    binding = dict(row, source_commit=pins.SOURCE_COMMIT,
                   run_id="s15_postroute_root_20261012_r01", allowed_run_dirs=allowed,
                   progress_logs=[str(log)], no_progress_seconds=900,
                   captured_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat())
    assert identity(row["pid"]) == row
    save("resource_plan.json", plan)
    save("owned_binding.json", binding)
    save("identity_admission.json", dict(status="READY_OFFLINE_PNR_DEPENDENCIES_AND_RESOURCES",
        source_commit=pins.SOURCE_COMMIT, six_field_identity=row,
        parent_identity=identity(row["ppid"]), allowed_alias_proof=aliases,
        current_heavy=heavy, available_ram_bytes=ram, c_disk_free_bytes=disk,
        synthesis_manifest=dict(path=str(pins.SYNTH_MANIFEST), sha256=pins.SYNTH_MANIFEST_SHA),
        synthesis_g2=dict(path=str(pins.SYNTH_G2), sha256=pins.SYNTH_G2_SHA),
        whole_tree_budget="NOT_YET_MONITORED",
        limitations=["仅离散准入；impl派发还须守卫和独立消费器的新鲜准入。"] ))
    print(json.dumps(dict(status="READY_OFFLINE_PNR_DEPENDENCIES_AND_RESOURCES", pid=row["pid"],
        birth=row["create_time"], cwd=row["cwd"], available_ram_bytes=ram,
        c_disk_free_bytes=disk), ensure_ascii=False))


if __name__ == "__main__":
    main()
