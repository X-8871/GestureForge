"""记录完整 API 审计与产物对象负例，不启动 Vivado。"""
from pathlib import Path
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

root = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
spec = importlib.util.spec_from_file_location("platform_check", root / "verification/check_s2b_inference_platform.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
run_id = "platform_api_audit_20261011_r08"
owned = ["src/s2b_inference_top.sv", "vivado/s2b_inference_platform.tcl", "board/s2b_inference_platform.json", "board/s2b_inference_platform.md", "verification/check_s2b_inference_platform.py"]

def new_dir(parent, name):
    """逐组件核对父目录原名及类型，拒绝链接与已有运行。"""
    current = Path(parent.anchor)
    for part in parent.parts[1:]:
        if part not in [p.name for p in current.iterdir()]:
            raise ValueError("精确父目录不存在：" + str(current / part))
        current = current / part
        if not current.is_dir() or current.is_symlink() or getattr(current.lstat(), "st_file_attributes", 0) & 0x400:
            raise ValueError("父目录类型或链接非法：" + str(current))
    if name in [p.name for p in current.iterdir()] or (current / name).exists():
        raise ValueError("不覆盖既有 Run：" + name)
    target = current / name
    target.mkdir()
    return target

work = new_dir(root / "tmp/2B/S2B-T13", run_id)
evidence = new_dir(root / "report/evidence/S2B-T13", run_id)
snapshot = new_dir(evidence, "source_snapshot")
sources = module.check_static(root)
before = {p: module.sha256(module.exact_file(root / p)) for p in owned}
for source in owned:
    with (snapshot / Path(source).name).open("xb") as out:
        out.write((root / source).read_bytes())
tcl = (root / "vivado/s2b_inference_platform.tcl").read_text(encoding="utf-8")
pin_loop = re.search(r"foreach pin \[get_bd_intf_pins -of_objects \[get_bd_cells\]\]", tcl)
if pin_loop is None:
    raise ValueError("审计必须从所有 cell 枚举接口 pin")
driver = module.exact_file(root / "tmp/2B/s2b_t13_api_probe.tcl").read_text(encoding="utf-8")
api_names = """add_files assign_bd_address connect_bd_intf_net connect_bd_net create_bd_cell create_bd_design create_project current_fileset current_project generate_target get_bd_addr_segs get_bd_addr_spaces get_bd_cells get_bd_intf_nets get_bd_intf_pins get_bd_intf_ports get_bd_nets get_bd_pins get_bd_ports get_files get_parts get_property list_property make_bd_intf_pins_external make_wrapper save_bd_design set_property update_compile_order validate_bd_design version write_bd_tcl write_hw_platform""".split()
pattern = r"\b(?:get_[a-z_]+|current_project|current_fileset|add_files|assign_bd_address|connect_bd_[a-z_]+|create_bd_[a-z_]+|create_project|generate_target|list_propert[a-z_]*|make_[a-z_]+|save_bd_design|set_property|update_compile_order|validate_bd_design|write_bd_tcl|write_hw_platform|version)\b"
found = set(re.findall(pattern, tcl))
if found != set(api_names):
    raise ValueError("全脚本 API 盘点不一致：" + str(found ^ set(api_names)))
inventory = {"status": "OFFICIAL_API_NAMES_AND_RETURN_USAGE_REVIEWED",
    "method": "全脚本命令词盘点与 UG835 官方目录核对；对象查询返回集合，创建/连接/写出只消费副作用",
    "root_failure": "report/evidence/S2B-T13/ipi_full_20261011_r04/audit.tcldict",
    "observed_root_log": "report/evidence/S2B-T13/ipi_full_20261011_r04/root_mcp_calls.json",
    "commands": [{"command": name, "official_reference": "https://docs.amd.com/r/2025.2-English/ug835-vivado-tcl-commands/" + name} for name in api_names],
    "products": {"get_files": "要求BD与导入wrapper对象各唯一", "generate_target": "副作用，无返回值假设", "make_wrapper": "官方-import副作用；返回任意创建信息或空均不作文件", "write_bd_tcl": "副作用，TCL_OK/TCL_ERROR", "write_hw_platform": "副作用；忽略XSA名称返回", "file_copy": "Tcl标准命令，用get_property NAME取真实BD文件路径，无force"},
    "run": "current_project必须空；get_parts要求唯一；create_project/create_bd_design/add_files/set_property/update_compile_order/save_bd_design均不消费创建对象返回；capture使用自有封装的明确receipt契约",
    "limits": "命名盘点与桩不代替本机Vivado实际help/执行；实际i4已通过construct/validate/audit前半段，后半段与products仍由root实测；未操作MCP"}
(evidence / "api_inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
driver_path = evidence / "api_probe.tcl"
driver_path.write_text(driver, encoding="utf-8")
tclsh = module.exact_file(Path(r"C:\Program Files\Git\ucrt64\bin\tclsh.exe"))
checks = []
runs = []
env = os.environ.copy()
env["PYTHONUTF8"] = "1"
for name, command in [("api_probe", [str(tclsh), str(driver_path), str(work)]), ("static", [sys.executable, "-B", str(root / "verification/check_s2b_inference_platform.py")])]:
    start = time.monotonic()
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, timeout=90)
    with (evidence / (name + ".log")).open("xb") as log:
        log.write(result.stdout + result.stderr)
    runs.append({"command": command, "exit_code": result.returncode, "seconds": round(time.monotonic() - start, 3)})
    checks.append({"name": name, "status": "PASS" if result.returncode == 0 else "FAIL", "command": subprocess.list2cmdline(command), "exit_code": result.returncode, "reason": "只运行隔离桩和静态检查"})
    print(name, "rc", result.returncode)
after = {p: module.sha256(root / p) for p in owned}
snap = {p: module.sha256(snapshot / Path(p).name) for p in owned}
stable = before == after == snap and sources == module.check_static(root)
checks.append({"name": "raw_snapshots_and_source_stability", "status": "PASS" if stable else "FAIL", "command": "五文件运行前原字节快照与运行后哈希比较", "exit_code": 0 if stable else 1, "reason": "本Run快照确实在桩与静态检查前复制"})
old = module.read_json(root / "report/evidence/S2B-T13/platform_external_ports_20261011_r05/source_bindings.json")["source_sha256"]
profile = module.read_json(root / "board/s2b_inference_platform.json")
reuse = all(old[p] == sources[p] for p in profile["rtl_sources"])
checks.append({"name": "unchanged_18rtl_binding", "status": "PASS" if reuse else "FAIL", "command": "比对r05完整18RTL source_bindings与本Run", "exit_code": 0 if reuse else 1, "reason": "本轮仅Tcl API和静态checker修复，未重跑无影响的18RTL编译；r05原日志及源码绑定仍保留"})
checks.append({"name": "actual_ipi", "status": "NOT_RUN", "command": "总控独占实际clean IPI", "exit_code": None, "reason": "桩不是实际Vivado审计；需总控新Run与独立R3"})
binding = {"source_sha256": sources, "owned_before": before, "owned_after": after, "raw_snapshots": snap, "stable": stable, "rtl18_unchanged_from_r05": reuse, "runs": runs, "tool_calls": 2, "heavy_runs": 0, "peak_memory": "未测"}
(evidence / "source_bindings.json").write_text(json.dumps(binding, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
with (evidence / "record_driver.py").open("xb") as stream:
    stream.write(Path(__file__).read_bytes())
interface = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
files = [{"path": p, "sha256": value, "role": "source"} for p, value in sources.items()]
files.append({"path": "board/s2b_inference_platform.md", "sha256": before["board/s2b_inference_platform.md"], "role": "source"})
files.append({"path": interface, "sha256": module.sha256(root / interface), "role": "input"})
for reused in ["source_bindings.json", "verilator_lint.log"]:
    path = root / "report/evidence/S2B-T13/platform_external_ports_20261011_r05" / reused
    files.append({"path": path.relative_to(root).as_posix(), "sha256": module.sha256(path), "role": "input"})
for raw in ["audit.tcldict", "root_mcp_calls.json"]:
    path = root / "report/evidence/S2B-T13/ipi_full_20261011_r04" / raw
    files.append({"path": path.relative_to(root).as_posix(), "sha256": module.sha256(module.exact_file(path)), "role": "input"})
for path in sorted(evidence.rglob("*")):
    if path.is_file():
        files.append({"path": path.relative_to(root).as_posix(), "sha256": module.sha256(path), "role": "log" if path.suffix == ".log" else "result"})
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T13", "run_id": run_id, "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(), "evidence_dir": evidence.relative_to(root).as_posix(), "interfaces": [{"name": "s2b-physical-candidate", "version": "0.1.1", "frozen": False, "path": interface, "sha256": module.sha256(root / interface)}], "files": files, "checks": checks, "tool_versions": {"python": sys.version.split()[0], "tclsh_file_sha256": module.sha256(tclsh)}, "limitations": ["实际IPI r02失败保留，尚未对修复执行实际IPI。", "桩覆盖完整audit三处官方属性枚举与products空返回/任意信息/四项对象负例，不冒称实际Vivado。", "路径/binding已审实现、PS-only profile、工业型号后缀均未变化。", "未触碰MCP、GUI、硬件、业务RTL与其他写者文件；未提交。"]}
(evidence / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(before, indent=2))
raise SystemExit(0 if all(item["status"] != "FAIL" for item in checks) else 1)

