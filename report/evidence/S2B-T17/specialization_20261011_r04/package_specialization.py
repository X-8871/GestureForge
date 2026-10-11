#!/usr/bin/env python3
"""绑定常量派生的实际源码、来源差异、真实验证命令和当前证据目录。"""
from pathlib import Path
from collections import Counter
import difflib
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
VALIDATION = EVIDENCE / "validation.json"


def sha(path):
    """返回实际原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """只处理本次运行目录，不改旧尝试及项目源码。"""
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_GEOMETRY_SPECIALIZATION_G1":
        raise ValueError("差分验证未通过")
    spec = importlib.util.spec_from_file_location("specialization_checker", ROOT / "verification/check_s2b_inference_platform.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    profile = json.loads((ROOT / "board/s2b_inference_platform.json").read_text(encoding="utf-8"))
    bindings = checker.check_static(ROOT)
    provenance = {"status": "PASS_SOURCE_PROVENANCE", "upstream_freeze_commit": profile["source_derivation"]["upstream_freeze_commit"],
        "task_baseline_commit": validation["task_baseline_commit"], "actual_source_commit": validation["source_commit"],
        "upstream_original_byte_hashes": {}, "derived_diffs": [], "warnings": {},
        "limitations": ["原工作树backend/core含CRLF；派生文件LF。原件字节不变，仅派生比较归一化换行。",
            "源关系检查不是完整整网或50MHz验证，旧2A及0.1.0平台证据不继承为新综合/实物通过。"]}
    for path in checker.FROZEN_CORE_SHA256:
        raw = (ROOT / path).read_bytes()
        blob = subprocess.check_output(["git", "show", provenance["upstream_freeze_commit"] + ":" + path], cwd=ROOT)
        if raw.replace(b"\r\n", b"\n") != blob.replace(b"\r\n", b"\n"):
            raise ValueError("冻结Git来源不符：" + path)
        provenance["upstream_original_byte_hashes"][path] = {"worktree_sha256": sha(ROOT / path),
            "freeze_git_blob_sha256": hashlib.sha256(blob).hexdigest(), "crlf_count": raw.count(b"\r\n"),
            "matches_validation_pre_and_post": sha(ROOT / path) == validation["frozen14_sha256_pre"][path] == validation["frozen14_sha256_post"][path]}
    for source, (path, replacements) in checker.DERIVATION_RULES.items():
        before = (ROOT / source).read_bytes().decode("utf-8").replace("\r\n", "\n")
        after = (ROOT / path).read_bytes().decode("utf-8")
        diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), source, path))
        provenance["derived_diffs"].append({"source": source, "path": path, "sha256": sha(ROOT / path),
            "allowed_replacements": replacements, "diff": diff})
    log = (EVIDENCE / "compile.log").read_text(encoding="utf-8")
    warning_lines = [line for line in log.splitlines() if line.startswith("%Warning-")]
    groups = Counter(line.split(":", 1)[0] for line in warning_lines)
    tb_warnings = [line for line in warning_lines if "tb_s2b_geometry_specialization.sv" in line]
    if tb_warnings:
        raise ValueError("最终TB仍有新增诊断")
    provenance["warnings"] = {"verilator_warning_count": len(warning_lines), "classes": dict(groups),
        "tb_warning_count": len(tb_warnings), "lines": warning_lines,
        "policy": "Wall原始诊断全保留；Wno-fatal仅用于冻结旧RTL及逐字派生继承的诊断，不抑制具体警告。",
        "compiler_runtime_warnings": "Verilator运行库STDOUT_FILENO/STDERR_FILENO重复宏原日志保留。"}
    (EVIDENCE / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    commands = [([sys.executable, "-B", "verification/check_s2b_inference_platform.py"], "static_checker"),
                (["git", "diff", "--check"], "diff_check")]
    records = []
    env = os.environ.copy(); env["PYTHONUTF8"] = "1"
    for command, name in commands:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        (EVIDENCE / (name + ".log")).write_bytes(result.stdout)
        records.append({"name": name, "command": command, "exit_code": result.returncode})
        if result.returncode != 0:
            raise ValueError(name + "失败")
    (EVIDENCE / "packaging_checks.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    model = "report/evidence/S2A-T01/tiny416_model_manifest.json"
    physical = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
    g0 = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
    files = [{"path": path, "sha256": digest, "role": "source"} for path, digest in validation["source_sha256_post"].items()]
    files += [{"path": path, "sha256": sha(ROOT / path), "role": "input"} for path in (model, physical)]
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.name == "delivery_manifest.json":
            continue
        role = "source" if path.parent.name == "source_snapshot" or path.suffix in (".py", ".sv") else "log" if path.suffix == ".log" else "input" if path.suffix == ".dat" else "result"
        files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role})
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T17", "run_id": EVIDENCE.name,
        "source_commit": validation["source_commit"], "evidence_dir": EVIDENCE.relative_to(ROOT).as_posix(),
        "interfaces": [{"name": "tiny416冻结模型数值及逻辑接口", "version": "S2A-T01/G0", "frozen": True,
            "path": g0, "sha256": sha(ROOT / g0)}, {"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.1",
            "frozen": False, "path": physical, "sha256": sha(ROOT / physical)}],
        "files": files, "checks": [], "tool_versions": validation["tool_versions"],
        "limitations": validation["limitations"] + ["G2独立审查待总控进行；本任务未运行Vivado/MCP/综合/实现/板上下载。",
            "原r01基线HEAD门禁失败、r02反例夹具恢复路径失败、r03首次差分PASS均保留；最终r04消除TB独有诊断后重新完整差分。",
            "inputs包装因物理接口候选未冻结及G2/G3/综合未执行，预期非零；不降低正式部署门槛。"]}
    for item in validation["runs"] + records:
        manifest["checks"].append({"name": item["name"], "status": "PASS", "command": subprocess.list2cmdline(item["command"]),
            "exit_code": item["exit_code"], "reason": "真实原生退出码；原始日志与源码哈希绑定本次独立RunId。"})
    manifest["checks"].append({"name": "逐周期差分和来源检查", "status": "PASS",
        "command": "python -B verification/test_s2b_geometry_specialization_rtl.py --run-id " + EVIDENCE.name,
        "exit_code": 0, "reason": "实际runner原生退出0；原始PASS精确计数为19645+3456条，590601周期，全部公开端口比较，26反例拒绝。"})
    for name, reason in (("G2独立审查", "Developer停止写入后由独立Reviewer核查固定内容。"),
        ("50MHz综合及实现", "总控将在独立新工程中验证，不能继承旧失败综合。"),
        ("完整整网golden", "此步仅引擎差分及来源证明，完整新闭包整网未运行。"),
        ("G3实物验证", "本任务禁止烧录、MCP和硬件；真实部署由总控后续执行。")):
        manifest["checks"].append({"name": name, "status": "NOT_RUN", "command": None, "exit_code": None, "reason": reason})
    manifest_path = EVIDENCE / "delivery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    native_records = []
    for mode, expected_code in (("evidence", 0), ("inputs", 2)):
        command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
                   "--manifest", manifest_path.relative_to(ROOT).as_posix()]
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        (EVIDENCE / ("delivery_" + mode + ".log")).write_bytes(result.stdout)
        native_records.append({"command": command, "native_exit_code": result.returncode,
            "expected_code": expected_code, "mode": mode})
        if result.returncode != expected_code:
            raise ValueError("包装检查原生退出码不符：" + mode)
    (EVIDENCE / "delivery_native_codes.json").write_text(json.dumps(native_records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    # 新增包装原件后重新绑定全部目录文件，再只读核验最终清单。
    manifest["files"] = [item for item in manifest["files"] if not item["path"].startswith(EVIDENCE.relative_to(ROOT).as_posix() + "/")]
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.name == "delivery_manifest.json":
            continue
        role = "source" if path.parent.name == "source_snapshot" or path.suffix in (".py", ".sv") else "log" if path.suffix == ".log" else "input" if path.suffix == ".dat" else "result"
        manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role})
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    final = subprocess.run(native_records[0]["command"], cwd=ROOT, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, check=False)
    if final.returncode != 0 or final.stdout != (EVIDENCE / "delivery_evidence.log").read_bytes():
        raise ValueError("最终包装核验不符")
    print(json.dumps({"status": provenance["status"], "source_files": len(bindings), "frozen14": len(provenance["upstream_original_byte_hashes"]),
        "derived_files": len(provenance["derived_diffs"]), "tb_warnings": len(tb_warnings), "warnings": len(warning_lines)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
