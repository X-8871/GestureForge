"""只读核对归档纠错与p05控制文本，证据只写本次隔离目录。"""

from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
ARCHIVE = ROOT / "report/evidence/S2B-T06/ps_smoke_integration_20261009_r02"
SUBMISSION = ROOT / "report/evidence/S2B-T06/ps_smoke_submission_20261009_r01"
FREEZE = ROOT / "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01"
OLD = ROOT / "report/evidence/S2B-T06/ps_smoke_integration_20261009_r01"
INDEX = ROOT / "tmp/2B/S2B-T06/final_index_p05"
PYTHON = r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe"
BASELINE = "00f51b664fefdaf0c63e605af2427333579fa5f3"
ARCHIVE_SHA = "59de15380b9c75025c0c4666001e799c272d9ae967d03ee12ef15f746160f1b9"
ASSEMBLY_SHA = "9d0463737b12161a2633ba696a95a2325a298b24edc1a82e23ffa13d2f99029e"
COMMANDS = []
CHECKS = []
sys.stdout.reconfigure(encoding="utf-8")


def sha(data):
    """原始字节SHA256。"""
    return hashlib.sha256(data).hexdigest()


def digest(path):
    """只读精确普通文件。"""
    assert path.is_file() and not path.is_symlink(), str(path)
    return sha(path.read_bytes())


def read(path):
    """不导入共享实验脚本，仅读取UTF-8。"""
    digest(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write(name, value):
    """仅创建本次新原件，不覆盖。"""
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def check(name, detail):
    """断言后记录结果。"""
    CHECKS.append({"name": name, "status": "PASS", "detail": detail})


def run(name, argv, expected=0, environment=None, data=None):
    """保存真实只读命令及未改写的stdout/stderr。"""
    started = time.monotonic()
    proc = subprocess.run(argv, cwd=ROOT, env=environment, input=data, capture_output=True, check=False)
    row = {"name": name, "argv": argv, "cwd": str(ROOT), "exit_code": proc.returncode, "expected_exit_code": expected, "elapsed_seconds": time.monotonic() - started}
    for key, content in [("stdout", proc.stdout), ("stderr", proc.stderr)]:
        path = OUT / (name + "." + key + ".log")
        with path.open("xb") as stream:
            stream.write(content)
        row[key] = {"path": str(path), "sha256": sha(content), "bytes": len(content)}
    if data is not None:
        path = OUT / (name + ".stdin.bin")
        with path.open("xb") as stream:
            stream.write(data)
        row["stdin"] = {"path": str(path), "sha256": sha(data), "bytes": len(data)}
    if environment:
        row["environment_overrides"] = {"GIT_INDEX_FILE": environment["GIT_INDEX_FILE"]}
    COMMANDS.append(row)
    assert proc.returncode == expected, row
    return proc.stdout


def audit():
    """只读现有私有index；不运行会创建index/封口的总控脚本。"""
    assert OUT == ROOT / "tmp/2B/S2B-T06/rv1/review/i02"
    assert digest(ARCHIVE / "delivery_manifest.json") == ARCHIVE_SHA and digest(SUBMISSION / "assembly.json") == ASSEMBLY_SHA
    head_before = run("shared_head_before", ["git", "rev-parse", "HEAD"])
    index_before = run("shared_index_before", ["git", "diff", "--cached", "--binary"])
    status_before = run("shared_status_before", ["git", "status", "--porcelain=v1", "-z"])
    assert head_before.decode("ascii").strip() == BASELINE and not index_before
    sources = read(OLD / "review_scope.json")["source_sha256"]
    fixed = dict(sources)
    fixed.update({
        ".codex/STATE.md": "93dd92b9be1e94b9928ff4a44be073a0154162feedb0378f385142b022f1beb1",
        ".gitattributes": "dddc9c5fa6965cd0bdaf30ef00b4553768174f30c3337c6f8f3b8b172031d809",
        "docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_smoke_offline_freeze_20261009.md": "8ad988a011ea93c024df64a55a047b494422839ef8cb2fe886886267bfda032f",
        "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/acceptance.json": "ec2e9ab8743172523052a35f857187faacd2b925d903459c6061172566bddeb8",
        "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01/delivery_manifest.json": "084ea9fecd333db8ef454e09e873b4eddd7858e75fc405e086dec99667db50e5",
    })
    assert all(digest(ROOT / p) == h for p, h in fixed.items())
    submission_inputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in SUBMISSION.iterdir() if p.is_file()}
    assert len(submission_inputs) == 12 and not (SUBMISSION / "delivery_manifest.json").exists()
    write("fixed_inputs.json", {"fixed_source_and_controls": fixed, "submission_12_current_files": submission_inputs, "archive_manifest_sha256": ARCHIVE_SHA, "assembly_sha256": ASSEMBLY_SHA})
    check("核心G2/审批/控制内容未变", {"fixed_files": len(fixed), "submission_files": 12, "submission_sealed": False})
    archive = read(ARCHIVE / "delivery_manifest.json")
    assert archive["source_commit"] == BASELINE and len(archive["files"]) == 100
    roles = {"artifact", "diagnostic", "input", "log", "result", "source"}
    actual_rows = []
    for item in archive["files"]:
        assert item["role"] in roles and digest(ROOT / item["path"]) == item["sha256"], item
        actual_rows.append({"path": item["path"], "sha256": item["sha256"]})
    assert archive["interfaces"] == [] and "实板NOT_RUN阻断未关闭" in archive["interfaces_not_applicable_reason"]
    assert archive["checks"][1]["status"] == "NOT_APPLICABLE" and "业务候选的实板G3仍为NOT_RUN" in archive["checks"][1]["reason"]
    assert read(FREEZE / "delivery_manifest.json")["checks"][1]["status"] == "NOT_RUN"
    write("archive_100_actual_hashes.json", actual_rows)
    mapping = read(ARCHIVE / "copy_mapping.json")
    assert mapping["copied_files"] == len(mapping["files"]) == len({r["destination"] for r in mapping["files"]}) == 81
    historical = []
    for row in mapping["files"]:
        source, destination = Path(row["source"]), ROOT / row["destination"]
        assert digest(source) == digest(destination) == row["sha256"]
        assert source.stat().st_size == destination.stat().st_size == row["bytes"] and source.read_bytes() == destination.read_bytes()
        if source.parent == OLD or OLD in source.parents:
            historical.append(source.relative_to(OLD).as_posix())
    old_inventory = {p.relative_to(OLD).as_posix() for p in OLD.rglob("*") if p.is_file()}
    assert len(historical) == 77 and set(historical) == old_inventory and sum(row["bytes"] for row in mapping["files"]) == mapping["copied_bytes"]
    check("r02实际100绑定/81复制链", {"bindings": 100, "copied_files": 81, "r01_all_files": 77, "original_extra_diagnostics": 4, "byte_differences": 0, "archive_NA": "仅纯归档；业务G3仍NOT_RUN"})
    correction = read(ARCHIVE / "correction.json")
    assert correction["original_packaging_exit_codes"] == [2, 2] and correction["original_outer_exit_code"] == correction["original_index_outer_exit_code"] == 1
    original_package = read(ARCHIVE / "packaging_failure/integration_packaging_r01.json")
    assert [r["exit_code"] for r in original_package] == [2, 2]
    for row in original_package:
        assert row["result"]["status"] == "CHECKS_FAILED" and all(".role " in e or e.startswith("evidence 模式至少") for e in row["result"]["errors"])
    old_manifest = read(OLD / "delivery_manifest.json")
    assert digest(OLD / "delivery_manifest.json") == correction["previous_archive_manifest_sha256"]
    assert sum(item.get("role") == "evidence" for item in old_manifest["files"]) == 76
    original_origin = read(ARCHIVE / "initial_index_tool_result.json")
    assert original_origin["exit_code"] == 1 and 'assert obj["source_commit"] == baseline' in original_origin["output"]
    p04_tool = read(SUBMISSION / "original_index_p04_tool_result.json")
    assert p04_tool["exit_code"] == 1 and "129" in p04_tool["output"] and "fatal: too many arguments" in p04_tool["output"]
    p04 = (SUBMISSION / "original_index_p04.py").read_text(encoding="utf-8")
    current = (SUBMISSION / "verified_index_script.py").read_text(encoding="utf-8")
    assert digest(SUBMISSION / "verified_index_script.py") == digest(ROOT / "tmp/2B/S2B-T06/verify_final_index.py") == "dd8504da95a21feb2ff98341cedd8882ad7e6751370fd0dbd2b60a2914b2c3a7"
    assert '"--filters", ":" + item["path"], item["path"]' in p04 and '"--filters", ":" + item["path"]]' in current
    assert 'expected_origin = "90652b45ef31e763bd3e6f7527e2fd080ece61a8" if name == "ps_smoke_20261008_r01" else baseline' in current
    failure_sources = [ARCHIVE / "initial_packaging_tool_result.json", ARCHIVE / "initial_index_tool_result.json", ARCHIVE / "packaging_failure/integration_packaging_r01.json", ARCHIVE / "packaging_failure/integration_packaging_inputs_r01.log", ARCHIVE / "packaging_failure/integration_packaging_evidence_r01.log", ARCHIVE / "packaging_failure/verify_final_index.py", SUBMISSION / "original_index_p04.py", SUBMISSION / "original_index_p04_tool_result.json"]
    failure_copies = []
    for number, source in enumerate(failure_sources):
        target = OUT / (f"failure_original_{number:02d}_" + source.name)
        with target.open("xb") as stream:
            stream.write(source.read_bytes())
        assert source.read_bytes() == target.read_bytes()
        failure_copies.append({"source": str(source), "destination": str(target), "sha256": digest(target)})
    write("failure_copy_mapping.json", failure_copies)
    check("原失败与纯实验修复", {"role_evidence_wrong_files": 76, "original_packaging_exits": [2, 2], "original_wrappers": [1, 1, 1], "git_cli_exit": 129, "original_tool_output": "原包装tool输出曾截断，完整underlying JSON日志已保留，不补造stderr", "fix_scope": "schema合法角色/各origin提交/Git standalone filters单一对象参数，无软件设计变更"})
    assembly = read(SUBMISSION / "assembly.json")
    assert len(assembly["copies"]) == 7 and assembly["fixed_archive_sha256"] == ARCHIVE_SHA
    for row in assembly["copies"]:
        assert digest(Path(row["source"])) == digest(ROOT / row["destination"]) == row["sha256"]
        assert Path(row["source"]).read_bytes() == (ROOT / row["destination"]).read_bytes()
    p05 = read(SUBMISSION / "pre_submission_index_receipt.json")
    assert p05["status"] == "PASS_FINAL_INDEX" and p05["staged_files"] == 577 and p05["bound_files"] == 581
    assert p05["raw_and_restored_differences"] == [] and p05["whitespace_exit_code"] == 0
    assert read(SUBMISSION / "pre_submission_index_tool_result.json")["exit_code"] == 0
    manifests = ["ps_smoke_20261008_r01", "ps_smoke_offline_freeze_20261009_r01", "ps_smoke_integration_20261009_r01", "ps_smoke_integration_20261009_r02"]
    origins = {}
    binding = {}
    for name in manifests:
        path = ROOT / "report/evidence/S2B-T06" / name / "delivery_manifest.json"
        manifest = read(path)
        expected = "90652b45ef31e763bd3e6f7527e2fd080ece61a8" if name == manifests[0] else BASELINE
        assert manifest["source_commit"] == expected
        origins[name] = expected
        binding[path.relative_to(ROOT).as_posix()] = digest(path)
        for item in manifest["files"] + manifest["interfaces"]:
            assert item["path"] not in binding or binding[item["path"]] == item["sha256"]
            binding[item["path"]] = item["sha256"]
    assert p05["manifest_source_commits"] == origins and len(binding) == 581
    assert all(digest(ROOT / p) == h for p, h in binding.items())
    check("p05真实来源与范围", {"manifest_origins": origins, "actual_bound_files": 581, "actual_raw_file_differences": 0, "p05_reported_raw_checkout_differences": 0, "coverage": "四已封口Run；未覆盖尚未封口submission，最终五Run/提交需总控另核对"})
    checker = ROOT / "verification/check_stage_delivery.py"
    for name, mode, manifest, expected in [("r02_inputs", "inputs", ARCHIVE / "delivery_manifest.json", 0), ("r02_evidence", "evidence", ARCHIVE / "delivery_manifest.json", 0), ("business_freeze_inputs", "inputs", FREEZE / "delivery_manifest.json", 2), ("business_freeze_evidence", "evidence", FREEZE / "delivery_manifest.json", 0)]:
        result = json.loads(run(name, [PYTHON, "-B", "-X", "utf8", str(checker), "--mode", mode, "--manifest", str(manifest)], expected))
        if name == "business_freeze_inputs":
            assert result["errors"] == ["checks[1] 依赖检查状态为 NOT_RUN，阻断 inputs 核验"]
        else:
            assert result["status"] == "CHECKS_OK" and not result["errors"]
    check("真实包装命令", {"r02_inputs": 0, "r02_evidence": 0, "business_inputs": 2, "business_evidence": 0, "business_only_blocker": "checks[1] NOT_RUN"})
    index_hash_before = digest(INDEX)
    environment = dict(os.environ, GIT_INDEX_FILE=str(INDEX))
    staged = run("p05_staged_paths", ["git", "diff", "--cached", "--name-only", "-z"], environment=environment).decode("utf-8").rstrip("\0").split("\0")
    assert len(staged) == 577 and set(staged) == set(p05["allowlist"])
    control_results = []
    scope = read(OLD / "review_scope.json")
    for number, item in enumerate(scope["controls"]):
        path, snapshot = item["path"], ROOT / item["snapshot"]
        content = snapshot.read_bytes()
        assert sha(content) == item["sha256"] and (ROOT / path).read_bytes() == content
        expected_blob = run(f"control_{number}_expected_blob", ["git", "hash-object", "--path=" + path, "--stdin"], environment=environment, data=content).decode("ascii").strip()
        staged_blob = run(f"control_{number}_staged_blob", ["git", "rev-parse", ":" + path], environment=environment).decode("ascii").strip()
        restored = run(f"control_{number}_checkout", ["git", "cat-file", "--filters", ":" + path], environment=environment)
        previous = next(row for row in p05["controls"] if row["path"] == path)
        assert expected_blob == staged_blob == previous["expected_git_blob"] == previous["staged_git_blob"]
        assert sha(restored) == previous["restored_sha256"]
        assert restored.decode("utf-8").replace("\r\n", "\n") == content.decode("utf-8").replace("\r\n", "\n")
        control_results.append({"path": path, "reviewed_sha256": sha(content), "restored_sha256": sha(restored), "expected_blob": expected_blob, "staged_blob": staged_blob, "utf8_text_equal_with_existing_eol_processing": True})
    run("p05_whitespace_readonly", ["git", "diff", "--cached", "--check"], environment=environment)
    assert digest(INDEX) == index_hash_before
    check("p05两个控制blob与恢复只读复验", {"controls": control_results, "private_index_bytes_unchanged": True, "writes_to_index_or_objects": False})
    assert run("shared_head_after", ["git", "rev-parse", "HEAD"]) == head_before
    assert run("shared_index_after", ["git", "diff", "--cached", "--binary"]) == index_before
    assert run("shared_status_after", ["git", "status", "--porcelain=v1", "-z"]) == status_before
    assert all(digest(ROOT / p) == h for p, h in fixed.items())
    assert digest(ARCHIVE / "delivery_manifest.json") == ARCHIVE_SHA and digest(SUBMISSION / "assembly.json") == ASSEMBLY_SHA
    assert {p.relative_to(ROOT).as_posix(): digest(p) for p in SUBMISSION.iterdir() if p.is_file()} == submission_inputs
    write("review_receipt.json", {"task": "S2B-T06-INTEGRATION-R02", "decision": "PASS", "blocking_findings": [], "baseline_commit": BASELINE, "checked_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "archive_manifest_sha256": ARCHIVE_SHA, "assembly_sha256": ASSEMBLY_SHA, "checks": CHECKS, "commands": COMMANDS, "hardware_execution": "NOT_RUN",
        "scope": "归档schema与来源/Git CLI纠错、真实失败保全、核心G2/审批/control保持、p05四Run及两个控制文本只读复验",
        "limits": ["不重复Vitis/主业务/G2；不执行任何实物操作。", "纯归档G3不适用不能绕过业务实板NOT_RUN；G3/G4/2B G0/G5均未通过。", "p05仅覆盖四已封口Run，不宣称未封口submission或最终五Run已提交/已验收。", "本轮仅写i02原件，未修改任何共享Git/index/objects/分支；不执行硬编码总控写入脚本。", "控制文件SHA恢复差异来自既有换行规则，已用被审snapshot的Git blob及UTF-8文本联合核验，不擅自改字节规则。", "i01 PASS继续有效；剩余最终封口/全五Run提交核验属于总控后续责任。"]})
    print(json.dumps({"decision": "PASS", "checks": len(CHECKS), "commands": len(COMMANDS), "receipt_sha256": digest(OUT / "review_receipt.json"), "hardware_execution": "NOT_RUN"}, ensure_ascii=False))


def bind():
    """驱动实际退出后冻结最小实验原件，清单不包含自身。"""
    assert (OUT / "audit.exit_code.txt").read_text(encoding="ascii").strip() == "0" and read(OUT / "review_receipt.json")["decision"] == "PASS"
    files = [{"path": str(p), "relative_to_i02": p.relative_to(OUT).as_posix(), "sha256": digest(p), "bytes": p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "review_evidence_bindings.json"]
    write("review_evidence_bindings.json", {"decision": "PASS", "task": "S2B-T06-INTEGRATION-R02", "hardware_execution": "NOT_RUN", "receipt_path": str(OUT / "review_receipt.json"), "receipt_sha256": digest(OUT / "review_receipt.json"), "files": files, "file_count": len(files), "bytes": sum(row["bytes"] for row in files), "excluded": "未创建/复制任何index或Git object/cache；没有自哈希循环", "native_exit_code": 0})
    print(json.dumps({"decision": "PASS", "receipt_sha256": digest(OUT / "review_receipt.json"), "bindings_sha256": digest(OUT / "review_evidence_bindings.json"), "files": len(files), "bytes": sum(row["bytes"] for row in files)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        bind() if sys.argv[1:] == ["--bind-evidence"] else audit()
    except Exception:
        write("audit_failure.json", {"status": "REVIEW_TOOL_FAILED", "traceback": traceback.format_exc(), "commands": COMMANDS, "checks_completed": CHECKS, "hardware_execution": "NOT_RUN"})
        raise
