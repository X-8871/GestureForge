"""从已核验XSim导出脚本派生epoch白盒注入对照运行。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
OLD = RUN.parent / "control_r18_xsim_preflight_20261016_r01"
PREFLIGHT = RUN / "preflight"
WORK = ROOT / "tmp/2B/S2B-T11" / RUN.name


def sha(path):
    """按原字节计算输入哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert not PREFLIGHT.exists() and not WORK.exists()
assert sha(OLD / "delivery_manifest.json") == "32ce831d41bb91e753c84b1944547086ec6ed6805de4db72c3a16f39b2f916bc"
original = json.loads((OLD / "delivery_manifest.json").read_text(encoding="utf-8"))
sources = [entry for entry in original["files"] if entry["path"].startswith(("src/", "sim/"))]
assert len(sources) == 7
PREFLIGHT.mkdir()
(PREFLIGHT / "source_snapshot").mkdir()
exported = PREFLIGHT / "exported_scripts"
exported.mkdir()
WORK.mkdir()
bindings = []
for entry in sources:
    source = ROOT / entry["path"]
    expected = ("04afb9a9d3a154c415b40effb2bf47c955c858d0cf203da20b3a0f170f88112a"
                if entry["path"] == "sim/tb_s2b_control_csr.sv" else entry["sha256"])
    assert source.is_file() and sha(source) == expected, str(source)
    snapshot = PREFLIGHT / "source_snapshot" / source.name
    shutil.copy2(source, snapshot)
    bindings.extend([source, snapshot])
for entry in original["files"]:
    source = ROOT / entry["path"]
    if source.parent != OLD / "exported_scripts":
        continue
    assert source.is_file() and sha(source) == entry["sha256"]
    destination = exported / source.name
    if source.name == "tb_s2b_control_csr_vlog.prj":
        data = source.read_bytes()
        before = str(OLD / "source_snapshot").replace("\\", "/").encode("utf-8")
        after = str(PREFLIGHT / "source_snapshot").replace("\\", "/").encode("utf-8")
        assert data.count(before) == 7
        destination.write_bytes(data.replace(before, after))
    else:
        shutil.copy2(source, destination)
    shutil.copy2(destination, WORK / destination.name)
    bindings.append(destination)
version = PREFLIGHT / "native_tool_versions.txt"
shutil.copy2(OLD / version.name, version)
bindings.extend([version, OLD / "delivery_manifest.json", Path(__file__).resolve()])
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T11", "run_id": RUN.name,
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "evidence_dir": PREFLIGHT.relative_to(ROOT).as_posix(), "interfaces": original["interfaces"],
    "files": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
               "role": "source" if path.suffix in (".sv", ".py", ".prj", ".tcl", ".ini") else "input",
               "keep_reason": "绑定严格单线程工具设置、六份原RTL和epoch注入对照TB。"}
              for path in bindings],
    "checks": [{"name": "diagnostic_input_derivation", "status": "PASS", "exit_code": 0,
                "command": "prepare_diag_run.py",
                "reason": "原导出脚本逐字节验证；仅PRJ目录引用、TB诊断和epoch白盒注入时序改变，不改协议断言或验收。"}],
    "limitations": ["复用先前MCP导出设置，没有重新声称MCP预检或动态通过。", "epoch在无时钟沿窗口force/release，CSR及START前检查最大epoch与监视相位保持。"],
    "tool_versions": original["tool_versions"]}
manifest_path = PREFLIGHT / "delivery_manifest.json"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
old_driver = RUN.parent / "control_r18_xsim_execution_20261016_r02/execute_xsim.py"
assert sha(old_driver) == "e118d2394de5c95f146810a3d8985b15e27edf6cc5c8a40377df84c56960f517"
driver = old_driver.read_text(encoding="utf-8")
replacements = {
    'PREFLIGHT = ROOT / "report/evidence/S2B-T11/control_r18_xsim_preflight_20261016_r01"':
        'PREFLIGHT = EVIDENCE / "preflight"',
    '32ce831d41bb91e753c84b1944547086ec6ed6805de4db72c3a16f39b2f916bc': sha(manifest_path),
    '"不更改断言、样本数、覆盖、RTL和testbench。"':
        '"TB仅增加诊断并在无时钟沿窗口注入epoch；原协议断言、计数、覆盖、seed及RTL不改。"',
}
for before, after in replacements.items():
    assert driver.count(before) == 1
    driver = driver.replace(before, after)
(RUN / "execute_xsim.py").write_text(driver, encoding="utf-8", newline="\n")
print(json.dumps({"prepared_only": True, "preflight_sha256": sha(manifest_path),
                  "driver_sha256": sha(RUN / "execute_xsim.py")}, ensure_ascii=False))
