"""修复T14 r01至r07包装角色，并归档r02失败核心的诊断缓存。"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[4]
PARENT = ROOT / "report/evidence/S2B-T14"
INTERFACE = ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
R02 = PARENT / "csr_fixed_visibility0_20261016_r02"
XIL_SOURCE = R02 / "raw_failed_core/s2b_inference_infer_0_synth_1/.Xil"
XIL_TARGET = ROOT / "tmp/2B/S2B-T14/csr_fixed_visibility0_20261016_r02/failed_core_diagnostic_cache"
XIL_ZIP = R02 / "raw_failed_core_xil.zip"
XIL_MAPPING = R02 / "diagnostic_cache_mapping.json"
OLD_MANIFEST_NAME = "delivery_manifest_initial.json"
REPAIR_MAPPING_NAME = "manifest_reconciliation.json"


def sha256_file(path: Path) -> str:
    """按文件原始字节计算SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """按字节计算SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: dict) -> None:
    """以UTF-8创建JSON记录，不覆盖既有原件。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def verify_no_vivado() -> list[dict]:
    """确认包装前无Vivado活动进程。"""
    command = (
        "$processes=@(Get-Process -Name vivado,vivado_lab -ErrorAction SilentlyContinue | "
        "Select-Object Id,ProcessName); ConvertTo-Json -InputObject $processes -Compress"
    )
    completed = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                               capture_output=True, text=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"检测到Vivado进程或无法核验进程状态：{completed.stdout}{completed.stderr}")
    try:
        active = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Vivado进程检查输出无法解析：{completed.stdout!r}") from error
    if active:
        raise RuntimeError(f"检测到Vivado进程，停止归档与包装：{active}")
    return active


def archive_and_move_xil() -> dict:
    """归档.Xil成员并逐项验证后移动原目录到指定临时目录。"""
    if not XIL_SOURCE.is_dir():
        raise RuntimeError(f"精确.Xil源目录不存在：{XIL_SOURCE}")
    if XIL_TARGET.exists():
        raise RuntimeError(f"临时归档目标已存在，拒绝覆盖：{XIL_TARGET}")
    if not XIL_TARGET.parent.is_dir():
        raise RuntimeError(f"临时归档目标父目录不存在：{XIL_TARGET.parent}")
    if XIL_ZIP.exists() or XIL_MAPPING.exists():
        raise RuntimeError("R02诊断归档输出已存在，拒绝覆盖")
    members = sorted(path for path in XIL_SOURCE.rglob("*") if path.is_file())
    if len(members) != 57:
        raise RuntimeError(f".Xil文件数与已核实值57不符：{len(members)}")
    member_rows = []
    with zipfile.ZipFile(XIL_ZIP, "x", compression=zipfile.ZIP_STORED) as archive:
        for source in members:
            relative = source.relative_to(XIL_SOURCE).as_posix()
            content = source.read_bytes()
            archive.writestr(relative, content)
            member_rows.append({"member": relative, "sha256": sha256_bytes(content),
                                "size_bytes": len(content)})
    with zipfile.ZipFile(XIL_ZIP, "r") as archive:
        names = sorted(name for name in archive.namelist() if not name.endswith("/"))
        if names != sorted(row["member"] for row in member_rows):
            raise RuntimeError(".Xil ZIP成员清单与源目录不匹配")
        for row in member_rows:
            archived = archive.read(row["member"])
            source = XIL_SOURCE / Path(row["member"])
            if (sha256_bytes(archived) != row["sha256"] or
                    sha256_file(source) != row["sha256"] or len(archived) != row["size_bytes"]):
                raise RuntimeError(f".Xil ZIP成员SHA或长度不匹配：{row['member']}")
    if XIL_TARGET.exists():
        raise RuntimeError(f"移动前目标已出现，停止：{XIL_TARGET}")
    shutil.move(os.fspath(XIL_SOURCE), os.fspath(XIL_TARGET))
    moved = sorted(path for path in XIL_TARGET.rglob("*") if path.is_file())
    if len(moved) != len(member_rows):
        raise RuntimeError("移动后的.Xil文件数变化")
    for row in member_rows:
        moved_file = XIL_TARGET / Path(row["member"])
        if not moved_file.is_file() or sha256_file(moved_file) != row["sha256"]:
            raise RuntimeError(f"移动后.Xil原字节不符：{row['member']}")
    mapping = {
        "schema_version": 1,
        "archive_type": "raw_failed_vivado_diagnostic_cache",
        "source_evidence_path": str(XIL_SOURCE),
        "moved_original_path": str(XIL_TARGET),
        "archive_path": str(XIL_ZIP),
        "archive_sha256": sha256_file(XIL_ZIP),
        "archive_size_bytes": XIL_ZIP.stat().st_size,
        "source_file_count": len(member_rows),
        "source_file_bytes": sum(row["size_bytes"] for row in member_rows),
        "members": member_rows,
        "verification": "ZIP逐成员、移动后原目录逐成员SHA-256与长度均相等；R02原运行结果未改写。",
    }
    write_json(XIL_MAPPING, mapping)
    return mapping


def role_for(path: Path) -> str:
    """按文件用途分配清单角色，DCP与诊断ZIP作为artifact。"""
    suffix = path.suffix.casefold()
    if suffix in {".py", ".tcl", ".sv", ".cmd", ".ps1", ".xdc"}:
        return "source"
    if suffix in {".dcp", ".zip", ".wdb", ".vcd", ".wlf", ".fsdb"}:
        return "artifact"
    if suffix in {".log", ".jou", ".stderr"} or path.name.endswith(".stderr.raw"):
        return "log"
    return "result"


def make_manifest(run: Path, actual: dict, initial_sha: str, xil_mapping: dict | None) -> dict:
    """按当前证据目录重新枚举文件并保留真实运行判定。"""
    old_dcp_rows = []
    initial = json.loads((run / OLD_MANIFEST_NAME).read_text(encoding="utf-8"))
    for item in initial.get("files", []):
        if str(item.get("path", "")).casefold().endswith(".dcp"):
            old_dcp_rows.append({"path": item["path"], "sha256": item["sha256"],
                                 "initial_role": item.get("role")})
    package_script = Path(__file__).resolve()
    mapping = {
        "schema_version": 1,
        "run_id": run.name,
        "initial_manifest_copy": OLD_MANIFEST_NAME,
        "initial_manifest_sha256": initial_sha,
        "dcp_role_repair": {"old_role": "result", "new_role": "artifact",
                            "reason": "DCP为可复核实现/诊断产物，不是运行结果记录；原DCP字节和SHA不变。",
                            "initial_dcp_rows": old_dcp_rows},
        "source_result_status_preserved": actual["status"],
        "source_run_job_status": actual.get("job", {}).get("status"),
        "source_run_exit_code": actual.get("job", {}).get("exit_code"),
        "source_run_cleanup_confirmed": actual.get("job", {}).get("cleanup_confirmed"),
        "xil_archive": xil_mapping,
        "change_reason": "修复新包装清单的DCP角色并规范化R02的Vivado .Xil诊断缓存；不修改result/input/native日志或原始失败产物。",
        "repair_script_sha256": sha256_file(package_script),
    }
    mapping_path = run / REPAIR_MAPPING_NAME
    if not mapping_path.exists():
        write_json(mapping_path, mapping)
    else:
        raise RuntimeError(f"补充mapping已存在，拒绝覆盖：{mapping_path}")
    files = []
    for path in sorted(item for item in run.rglob("*") if item.is_file()):
        if path.name == "delivery_manifest.json":
            continue
        relative = path.relative_to(ROOT).as_posix()
        if ".Xil" in relative:
            raise RuntimeError(f"证据目录中仍有被checker拒绝的.Xil缓存：{relative}")
        if path.suffix.casefold() == ".dcp" and role_for(path) != "artifact":
            raise RuntimeError(f"DCP角色分类错误：{relative}")
        if path.suffix.casefold() == ".zip" and role_for(path) != "artifact":
            raise RuntimeError(f"诊断归档角色分类错误：{relative}")
        reason = "保留原始运行输入、结果、日志或诊断产物；包装修正不改变原运行结论。"
        if path.suffix.casefold() == ".dcp":
            reason = "保留原始实现/综合设计检查点，供离线诊断复核。"
        elif path.suffix.casefold() == ".zip":
            reason = "保留由诊断缓存原文件组成的逐成员SHA核验归档。"
        files.append({"path": relative, "sha256": sha256_file(path),
                      "role": role_for(path), "keep_reason": reason})
    passed = str(actual["status"]).startswith("PASS")
    job = actual.get("job", {})
    job_terminal = job.get("status") != "RUNNING" and job.get("cleanup_confirmed") is True
    if not job_terminal:
        raise RuntimeError(f"Run并非已结束/清理确认：{run.name} {job}")
    data = {
        "schema_version": 1,
        "stage": "2B",
        "task_id": "S2B-T14",
        "run_id": run.name,
        "source_commit": actual.get("source_commit"),
        "evidence_dir": run.relative_to(ROOT).as_posix(),
        "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.2",
                        "frozen": False, "path": INTERFACE.relative_to(ROOT).as_posix(),
                        "sha256": sha256_file(INTERFACE)}],
        "files": files,
        "checks": [
            {"name": "actual_driver_result", "status": "PASS" if passed else "FAIL",
             "exit_code": 0 if passed else 1,
             "command": "launch_infer_ooc.py" if run.name.endswith("r03") else "launch_build.py",
             "reason": f"原始result.json状态为{actual['status']}；未修改原运行结论。"},
            {"name": "hardware_validation", "status": "NOT_APPLICABLE", "exit_code": None,
             "command": None,
             "reason": "本Run为离线综合/实现交付包装；未执行板卡动作，正式2B G3仍未执行。"},
        ],
        "limitations": [
            "此清单仅核对包装；不将失败运行、综合完成、产物生成或checker通过等同独立审查、G0或G3/G4/G5通过。",
            "各Run的FAIL/PASS_CORE_OOC_SYNTH状态按原result.json保留；R07原始bit完整SHA差异仅由独立R08对账包解释，R07仍保持FAIL。",
            "全程未执行板卡；109黄金样本和1000连续任务均未执行。",
        ],
        "tool_versions": {"Vivado": "2026.1", "packager_python": sys.version.split()[0]},
    }
    (run / "delivery_manifest.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return data


def main() -> None:
    """先封存R02缓存，再保存旧清单并重新生成七份包装清单。"""
    verify_no_vivado()
    runs = [PARENT / f"csr_fixed_visibility0_20261016_r{number:02d}" for number in range(1, 8)]
    originals = {}
    for run in runs:
        if not run.is_dir():
            raise RuntimeError(f"Run目录不存在：{run}")
        result_path = run / "result.json"
        manifest_path = run / "delivery_manifest.json"
        if not result_path.is_file() or not manifest_path.is_file():
            raise RuntimeError(f"原始result或首次清单缺失：{run}")
        actual = json.loads(result_path.read_text(encoding="utf-8"))
        job = actual.get("job", {})
        if actual.get("status") == "RUNNING" or job.get("status") == "RUNNING" or job.get("cleanup_confirmed") is not True:
            raise RuntimeError(f"Run尚未终态或Job清理未确认：{run}")
        initial_copy = run / OLD_MANIFEST_NAME
        if initial_copy.exists() or (run / REPAIR_MAPPING_NAME).exists():
            raise RuntimeError(f"检测到既有首次清单副本或补充mapping，拒绝覆盖：{run}")
        originals[run] = {"result": actual, "manifest_sha256": sha256_file(manifest_path)}
        shutil.copyfile(manifest_path, initial_copy)
        if sha256_file(initial_copy) != originals[run]["manifest_sha256"]:
            raise RuntimeError(f"首次清单副本SHA不匹配：{run}")
    xil_mapping = archive_and_move_xil()
    outputs = []
    for run in runs:
        details = originals[run]
        mapping = xil_mapping if run == R02 else None
        outputs.append(make_manifest(run, details["result"], details["manifest_sha256"], mapping))
    print(json.dumps({"runs": [{"run_id": row["run_id"], "check": row["checks"][0]["status"],
                                "files": len(row["files"])} for row in outputs],
                      "xil_archive": str(XIL_ZIP), "xil_sha256": sha256_file(XIL_ZIP),
                      "xil_target": str(XIL_TARGET)}, ensure_ascii=False))


def refresh_wrapper_hashes() -> None:
    """更新包装修正脚本和补充mapping哈希，不触碰原运行记录。"""
    script_hash = sha256_file(Path(__file__).resolve())
    for number in range(1, 8):
        run = PARENT / f"csr_fixed_visibility0_20261016_r{number:02d}"
        mapping_path = run / REPAIR_MAPPING_NAME
        manifest_path = run / "delivery_manifest.json"
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        mapping["repair_script_sha256"] = script_hash
        mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8", newline="\n")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.pop("repair_mapping", None)
        for interface in manifest.get("interfaces", []):
            interface_path = ROOT / interface["path"]
            interface["sha256"] = sha256_file(interface_path)
        for item in manifest["files"]:
            path = ROOT / item["path"]
            item["sha256"] = sha256_file(path)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8", newline="\n")
    print(json.dumps({"status": "WRAPPER_HASHES_REFRESHED", "script_sha256": script_hash}, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1:] == ["--refresh-wrapper-hashes"]:
        refresh_wrapper_hashes()
    else:
        main()
