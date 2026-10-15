"""绑定候选构建产物，同时明确保留外层退出失败。"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent


def sha(path):
    """按原字节计算哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


record = json.loads((RUN / "launcher_record.json").read_text(encoding="utf-8"))
details = json.loads((RUN / "artifacts/build_details.json").read_text(encoding="utf-8"))
assert record["status"] == "FAIL" and record["job"]["status"] == "FAIL_JOB_NOT_EMPTY"
assert record["native_exit_code"] == 0 and record["job"]["cleanup_confirmed"] is True
assert details["status"] == "PASS_OFFLINE_FULL_XSA_BUILD"
assert details["hardware_execution"] == "NOT_RUN"
config = json.loads((RUN / "config.json").read_text(encoding="utf-8"))
sources = RUN / "build_sources"
sources.mkdir(exist_ok=True)
for name, expected in details["source_sha256"].items():
    source = ROOT / name
    assert source.is_file() and sha(source) == expected, name
    destination = sources / source.name
    if destination.exists():
        assert sha(destination) == expected, str(destination)
    else:
        shutil.copy2(source, destination)
for entry in record["sources"]:
    assert sha(RUN / "launcher_sources" / Path(entry["path"]).name) == entry["sha256"]
archive = Path(details["bsp_translation_table"]["archive_path"])
assert archive.is_file() and sha(archive) == details["bsp_translation_table"]["archive_sha256"]
retained_archive = RUN / "artifacts/bsp_libxilstandalone.a"
if retained_archive.exists():
    assert sha(retained_archive) == sha(archive)
else:
    shutil.copy2(archive, retained_archive)
paths = {path.relative_to(ROOT).as_posix(): path for path in RUN.rglob("*")
         if path.is_file() and path.name != "delivery_manifest.json"}
for key, expected_key in (("xsa", "xsa_sha256"), ("platform_manifest", "platform_manifest_sha256")):
    path = Path(config[key])
    assert path.is_file() and sha(path) == config[expected_key]
    paths[path.relative_to(ROOT).as_posix()] = path
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T15", "run_id": RUN.name,
    "source_commit": record["source_commit"], "evidence_dir": RUN.relative_to(ROOT).as_posix(),
    "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.2",
                    "frozen": False, "path": "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
                    "sha256": "1486a7f69e7a2053acfcad05151a9c54cfffab776d4154141741236aa88c401b"}],
    "files": [{"path": name, "sha256": sha(path),
               "role": "input" if RUN not in path.parents else "artifact" if path.suffix in (".a", ".elf")
                       else "source" if path.suffix in (".py", ".c", ".h", ".S", ".cmd", ".ld", ".cmake", ".i")
                       else "log" if path.suffix in (".log", ".jsonl") else "result",
               "keep_reason": "保留实际BSP归档用于独立于临时构建目录核查MMU来源链。" if path == retained_archive
                              else "绑定本Run实际源码、配置、编译产物、原始结果或退出失败证据。"}
              for name, path in sorted(paths.items())],
    "checks": [
        {"name": "supervised_candidate_build", "status": "FAIL", "exit_code": 1,
         "command": "launch_build.py", "reason": "原生退出0，但root退出时Job仍有成员，整体FAIL_JOB_NOT_EMPTY。"},
        {"name": "native_offline_build", "status": "PASS", "exit_code": 0,
         "command": "build.cmd", "reason": "内层BSP/ELF生成并完成初始MMU静态检查；不覆盖外层退出准入。"},
        {"name": "hardware_validation", "status": "NOT_RUN", "exit_code": None,
         "command": None, "reason": "候选visibility=0只离线构建，没有PS/PL下载、DDR或实板执行。"}],
    "limitations": details["limitations"] + [
        "整体FAIL；不能将内层PASS、包装检查或静态MMU检查当作G0/G3/G4/G5。",
        "残留PID9332不同于自建server PID23024，身份未知；请求终止不证明该成员确实被强制杀死。",
        "本Run仅执行一次；峰值进程树内存未测，最低可用RAM和采样间隔见launcher_record。"],
    "tool_versions": {"Python_packager": sys.version, "Vitis": details["vitis_version"]}}
(RUN / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
