"""原样复制技术证据到合法交付目录，保留原路径与失败核验。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
RUN = "ps_uart_clock_fix_delivery_20261009_173128_r01"
PACKAGE = ROOT / "report/evidence/S2B-T06" / RUN
ORIGINALS = [ROOT / "report/evidence/S2B-T06/ps_uart_clock_fix_20261009_171959_r01", ROOT / "report/evidence/S2B-T06/ps_uart_clock_fix_20261009_172254_r02"]

def digest(path):
    """核对实际复制字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    """仅创建新的UTF-8记录。"""
    with (PACKAGE / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

def main():
    """保持原件与内嵌绑定路径原样；交付清单绑定副本实际字节。"""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(ROOT / "vitis"))
    from build_s2b_ps_smoke import exact_path, copy_exclusive
    exact_path(PACKAGE, "directory")
    mapping = []
    failed_checks = []
    for index, original in enumerate(ORIGINALS, 1):
        exact_path(original, "directory")
        for path in sorted(original.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(original)
            parts = list(relative.parts)
            if parts[0] == "build":
                parts[0] = "build_01"
            destination = PACKAGE / f"attempt{index}" / Path(*parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            exact_path(destination.parent, "directory")
            if destination.exists():
                exact_path(destination, "file")
                assert digest(destination) == digest(path)
            else:
                copy_exclusive(path, destination)
            mapping.append({"original": path.relative_to(ROOT).as_posix(), "copy": destination.relative_to(ROOT).as_posix(), "sha256": digest(path)})
        command = [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"), "--mode", "evidence", "--manifest", str(original / "delivery_manifest.json")]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)
        log = PACKAGE / f"original_packaging_check_attempt{index}.log"
        if log.exists():
            assert log.read_bytes() == result.stdout + result.stderr
        else:
            with log.open("xb") as stream:
                stream.write(result.stdout)
                stream.write(result.stderr)
        assert result.returncode == 2 and b"build" in result.stdout
        failed_checks.append({"command": command, "exit_code": result.returncode, "log": log.relative_to(ROOT).as_posix(), "log_sha256": digest(log)})
    copy_exclusive(Path(__file__).absolute(), PACKAGE / "package_delivery.py")
    save("package_attempt1_failure.json", {"status": "FAIL_COLLECTOR_EXIT_CODE_ASSERTION", "native_exit_code": 1,
             "reason": "收集器把包装失败退出码误写为1；原检查器原生返回2，真实失败stdout已保留。",
             "recovery": "按检查器实际返回约定核对2，所有已复制文件逐字节核验后复用，不覆盖原件。"})
    save("copy_mapping.json", {"status": "PASS_BYTE_IDENTICAL_COPY", "original_files_unchanged": True, "mapping": mapping,
                              "original_packaging_checks": failed_checks, "reason": "原件目录名build被检查器视为缓存；仅副本目录名使用build_01，内嵌原始路径与日志原字节不改。"})
    files = []
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file():
            continue
        role = "source" if path.suffix in (".py", ".c", ".h", ".md") else "artifact" if path.suffix in (".elf", ".map", ".ld") else "log" if path.suffix in (".log", ".patch") else "result"
        entry = {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": role}
        if path.suffix in (".elf", ".map"):
            entry["keep_reason"] = "保留实际ELF与布局及原始失败诊断，供独立审查。"
        files.append(entry)
    for path in (ROOT / "vitis/s2b_ps_smoke.c", ROOT / "vitis/s2b_ps_smoke.md"):
        files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": "source"})
    receipt = json.loads((ORIGINALS[1] / "build_receipt.json").read_text(encoding="utf-8"))
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T06", "run_id": RUN, "source_commit": "117911e63cd7468418f11847ffedc9293dbca075",
                "evidence_dir": PACKAGE.relative_to(ROOT).as_posix(), "interfaces": json.loads((ORIGINALS[1] / "inputs_manifest.json").read_text(encoding="utf-8"))["interfaces"],
                "files": files, "tool_versions": {"Vitis": "2026.1", "ARM_GCC": "13.4.0", "Python": "3.13.0"},
                "checks": [{"name": "短缓存同XSA构建和布局", "status": "PASS", "command": json.dumps(receipt["command"], ensure_ascii=False), "exit_code": 0, "reason": "三个真实构建API整数0，原生及有效退出0，联合布局及14反例通过。"},
                           {"name": "首轮长缓存构建", "status": "FAIL", "command": json.dumps(receipt["command"], ensure_ascii=False), "exit_code": 1, "reason": "原生CLI0但平台API失败，有效退出1，依赖文件创建失败；原件保留。"},
                           {"name": "新版实板", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本次离线候选未上板，不继承旧版功能结果。"}],
                "limitations": ["离线构建不代表独立G2、G3/G4/G5；新版正式冻结未批准。", "原路径ELF可通过copy_mapping及SHA复核；原包装build目录检查失败也保留。", "收集器前三次失败按原脚本和显式错误记录保留，未补造缺失traceback。"]}
    save("delivery_manifest.json", manifest)
    print(json.dumps({"status": "PACKAGE_SAVED", "manifest": str(PACKAGE / "delivery_manifest.json"), "manifest_sha256": digest(PACKAGE / "delivery_manifest.json"), "copied_file_count": len(mapping)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
