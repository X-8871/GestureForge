"""轻量setup已结束后，重新绑定同一自有Vivado；保留r01阻断。"""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import psutil
import capture_owned_run as original

HERE = Path(__file__).parent
KEYS = ("pid", "create_time", "exe", "cwd", "cmdline", "ppid")

def bound(path):
    """绑定真实原始证据字节。"""
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def save(name, data):
    """新文件独占创建，不覆盖历史运行。"""
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2); stream.write("\n")

def main():
    """核实旧监督终态、精确目录别名、当前身份与预算。"""
    old = json.loads((HERE / "owned_binding.json").read_text(encoding="utf-8"))
    sup_path = HERE / "supervision_r01/supervisor_receipt.json"
    sup = json.loads(sup_path.read_text(encoding="utf-8"))
    assert sup["supervisor_exit_code"] == 2 and sup["child_native_exit_code"] == 3
    assert sup["guard_terminal"]["status"] == "BLOCKED"
    consumer_path = HERE / "native_consumer_r01/consumer_receipt.json"
    consumer = json.loads(consumer_path.read_text(encoding="utf-8"))
    assert consumer["native_exit_code"] == 2 and consumer["blocked_latched"] is True
    for previous in (sup["guard_identity"], consumer["consumer_identity"]):
        try:
            live = original.identity(previous["pid"])
        except psutil.NoSuchProcess:
            continue
        assert live["create_time"] != previous["create_time"], "旧监护仍存活，禁止重复启动"
    row = original.identity(old["pid"])
    assert all(row[k] == old[k] for k in KEYS if k != "cwd")
    assert row["cwd"] in old["allowed_run_dirs"] and Path(row["cwd"]).samefile(HERE)
    aliases = []
    for candidate in old["allowed_run_dirs"]:
        item = Path(candidate)
        assert item.is_dir()
        reference = HERE if item.samefile(HERE) else original.WORK
        assert item.samefile(reference)
        assert candidate[1:] == str(reference)[1:]
        aliases.append(dict(path=candidate, samefile=str(reference), character_difference="仅索引0盘符；按原样记录"))
    heavy = [dict(pid=p.pid, name=p.info["name"], birth=p.info["create_time"])
             for p in psutil.process_iter(["name", "create_time"])
             if (p.info["name"] or "").lower() in ("vivado.exe", "verilator_bin.exe", "xsim.exe", "cc1plus.exe")]
    assert len(heavy) == 1 and heavy[0]["pid"] == row["pid"]
    ram, disk = psutil.virtual_memory().available, psutil.disk_usage("C:/").free
    plan = json.loads((HERE / "resource_plan.json").read_text(encoding="utf-8"))
    assert plan["source_commit"] == old["source_commit"] == original.SOURCE
    assert ram >= plan["new_run_available_ram_stop_bytes"] and disk >= plan["minimum_c_disk_free_before_dispatch_bytes"]
    plan.update(actual_pre_start_ram_bytes=ram, actual_pre_start_c_disk_free_bytes=disk,
                recovery="r01终态后同一ROOT重新准入；不追认products期间连续预算")
    binding = dict(old, **row)
    binding["captured_at_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    binding["recovery_number"] = 2
    assert original.identity(row["pid"]) == row
    save("resource_plan_r02.json", plan); save("owned_binding_r02.json", binding)
    save("identity_admission_r02.json", dict(status="READY_DISCRETE_RECOVERY_ONLY", six_field_identity=row,
        parent_identity=original.identity(row["ppid"]), source_commit=original.SOURCE,
        current_heavy=heavy, available_ram_bytes=ram, c_disk_free_bytes=disk,
        previous_supervisor=bound(sup_path), previous_consumer=bound(consumer_path),
        alias_proof=aliases, whole_tree_budget="NOT_YET_MONITORED_R02",
        limitation="必须新SUP READY及当前消费者实际完整首行核验后派发；r01 BLOCKED保留。"))
    print(json.dumps(dict(status="READY_DISCRETE_RECOVERY_ONLY", identity=row, available_ram_bytes=ram,
                         c_disk_free_bytes=disk), ensure_ascii=False))

if __name__ == "__main__":
    main()
