"""只读补审总控集成，所有输出和私有Git对象均隔离在本目录。"""

from datetime import datetime, timezone, timedelta
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
import traceback

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
INTEGRATION = ROOT / "report/evidence/S2B-T06/ps_smoke_integration_20261009_r01"
FREEZE = ROOT / "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01"
DEVELOPER = ROOT / "report/evidence/S2B-T06/ps_smoke_20261008_r01"
SCOPE = INTEGRATION / "review_scope.json"
SCOPE_SHA = "574b268724b37126ae5aa95e47f6f4a7eb774d4cc3608cf460b91dfd4a56d533"
BASELINE = "00f51b664fefdaf0c63e605af2427333579fa5f3"
COMMANDS = []
CHECKS = []
PYTHON = r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe"
sys.stdout.reconfigure(encoding="utf-8")


def sha(data):
    """计算原始字节摘要。"""
    return hashlib.sha256(data).hexdigest()


def ordinary(path):
    """拒绝输入文件及其项目内父目录上的重解析。"""
    assert path.is_file(), str(path)
    item = path
    while True:
        properties = item.lstat()
        assert not item.is_symlink() and not (getattr(properties, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT), str(item)
        if item == ROOT or ROOT not in item.parents:
            break
        item = item.parent
    return path


def digest(path):
    """核查实际文件原字节。"""
    return sha(ordinary(path).read_bytes())


def read(path):
    """仅按UTF-8读取项目JSON。"""
    return json.loads(ordinary(path).read_text(encoding="utf-8"))


def create_json(name, value):
    """拒绝覆盖审查原件。"""
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")


def check(name, detail):
    """只在实际断言通过后记录检查结果。"""
    CHECKS.append({"name": name, "status": "PASS", "detail": detail})


def preserve_bytes(name, data):
    """大stdout无损压缩保全，避免重复保存整份冻结文件字节。"""
    compressed = len(data) > 65536
    path = OUT / (name + (".gz" if compressed else ".log"))
    stored = gzip.compress(data, mtime=0) if compressed else data
    with path.open("xb") as output:
        output.write(stored)
    assert (gzip.decompress(path.read_bytes()) if compressed else path.read_bytes()) == data
    return {"path": str(path), "sha256": sha(stored), "raw_sha256": sha(data), "raw_bytes": len(data), "encoding": "gzip_unmodified_stdout" if compressed else "raw_bytes"}


def run(name, arguments, expected=0, environment=None, data=None):
    """真实轻量命令，保存精确argv/cwd/env差异及原stdout/stderr。"""
    start = time.monotonic()
    proc = subprocess.run(arguments, cwd=ROOT, env=environment, input=data, capture_output=True, check=False)
    row = {"name": name, "argv": arguments, "cwd": str(ROOT), "exit_code": proc.returncode, "expected_exit_code": expected,
           "elapsed_seconds": time.monotonic() - start,
           "stdout": preserve_bytes(name + ".stdout", proc.stdout), "stderr": preserve_bytes(name + ".stderr", proc.stderr)}
    if environment:
        row["environment_overrides"] = {key: environment[key] for key in ["GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"] if key in environment}
    if data is not None:
        row["stdin"] = preserve_bytes(name + ".stdin", data)
    COMMANDS.append(row)
    assert proc.returncode == expected, row
    return proc.stdout


def verify_manifest(path, count):
    """独立逐项实际绑定，不用原核验脚本作为唯一依据。"""
    manifest = read(path)
    assert len(manifest["files"]) == count
    rows = []
    for item in manifest["files"] + manifest["interfaces"]:
        actual = digest(ROOT / item["path"])
        assert actual == item["sha256"], item["path"]
        rows.append({"path": item["path"], "sha256": actual})
    check(path.parent.name + "实际绑定", {"files": count, "interfaces": len(manifest["interfaces"]), "differences": 0})
    return manifest, rows


def parse_batch(raw, paths):
    """独立按Git批量协议解析blob原字节并计算SHA256。"""
    cursor = 0
    hashes = {}
    for path in paths:
        end = raw.index(b"\n", cursor)
        header = raw[cursor:end].split()
        assert len(header) == 3 and header[1] == b"blob", (path, header)
        size = int(header[2])
        body = raw[end + 1:end + 1 + size]
        assert len(body) == size and raw[end + 1 + size:end + 2 + size] == b"\n"
        hashes[path] = sha(body)
        cursor = end + 2 + size
    assert cursor == len(raw)
    return hashes


def audit():
    """全程禁止任何板卡API，仅运行文件与隔离Git核验。"""
    assert OUT == ROOT / "tmp/2B/S2B-T06/rv1/review/i01" and digest(SCOPE) == SCOPE_SHA
    scope = read(SCOPE)
    assert len(scope["files"]) == 31 and scope["baseline_commit"] == BASELINE
    initial_head = run("shared_head_before", ["git", "rev-parse", "HEAD"])
    initial_index = run("shared_index_before", ["git", "diff", "--cached", "--binary"])
    initial_status = run("shared_status_before", ["git", "status", "--porcelain=v1", "-z"])
    assert initial_head.decode("ascii").strip() == BASELINE and not initial_index
    for item in scope["files"]:
        assert digest(ROOT / item["path"]) == item["sha256"], item["path"]
    for item in scope["controls"]:
        assert digest(ROOT / item["path"]) == digest(ROOT / item["snapshot"]) == item["sha256"]
        assert (ROOT / item["path"]).read_bytes() == (ROOT / item["snapshot"]).read_bytes()
    assert all(digest(ROOT / path) == value for path, value in scope["source_sha256"].items())
    check("31固定文件和2控制快照及4源码", {"scope_sha256": SCOPE_SHA, "differences": 0})
    approval = read(FREEZE / "acceptance.json")
    expected_gates = {"G1": "PASS_OFFLINE", "G2": "PASS", "G3": "NOT_RUN", "G4": "NOT_PASSED", "stage_2B_G5": "NOT_PASSED", "stage_2B_G0": "NOT_PASSED"}
    assert approval["decision"] == "APPROVED_OFFLINE_PRECHECK_CANDIDATE_ONLY" and approval["gate_status"] == expected_gates
    assert approval["source_sha256"] == scope["source_sha256"] and approval["baseline_commit"] == BASELINE
    assert approval["hardware_execution"] == "NOT_RUN" and approval["fixed_upstream_commit"] == "90652b45ef31e763bd3e6f7527e2fd080ece61a8"
    formal = (ROOT / approval["formal_record"]["path"]).read_text(encoding="utf-8")
    state = (ROOT / ".codex/STATE.md").read_text(encoding="utf-8")
    assert len(state.splitlines()) <= 80
    for text, terms in [(formal, ["仅接受已完成的G1/G2离线结果", "NOT_RUN", "模型部署", "均未执行", "待Wong选择", "不能把它们称为已包含在旧基线提交中", "xc7z020clg400-2"]), (state, ["未通过阶段2B G0", "物理PS/PL恢复接口待Wong决定", "阶段2B仍未通过", "inputs检查2", "NOT_RUN阻断依赖"])]:
        assert all(term in text for term in terms)
    check("批准/正式冻结/STATE语义", {"gate_status": expected_gates, "STATE_lines": len(state.splitlines()), "source_commit_basis": "旧基线提交+新源码SHA，未把新源码声称已存在于旧提交", "physical_recovery": "S2B-T05未选择/未冻结"})
    developer, developer_rows = verify_manifest(DEVELOPER / "delivery_manifest.json", 284)
    freeze, freeze_rows = verify_manifest(FREEZE / "delivery_manifest.json", 141)
    assert freeze["source_commit"] == BASELINE and freeze["checks"][1]["status"] == "NOT_RUN"
    create_json("actual_manifest_hashes.json", {"developer": developer_rows, "freeze": freeze_rows})
    bindings = read(ROOT / approval["reviewer_bindings"]["path"])
    mapping = read(FREEZE / "reviewer_copy_mapping.json")
    assert bindings["file_count"] == len(bindings["files"]) == 110 and mapping["copied_files"] == len(mapping["files"]) == 111
    assert len({row["source"] for row in mapping["files"]}) == len({row["destination"] for row in mapping["files"]}) == 111
    by_source = {row["source"]: row for row in mapping["files"]}
    for item in bindings["files"]:
        row = by_source[item["path"]]
        assert item["sha256"] == row["sha256"] and item["bytes"] == row["bytes"]
    for row in mapping["files"]:
        source, destination = Path(row["source"]), ROOT / row["destination"]
        assert source.stat().st_size == destination.stat().st_size == row["bytes"]
        assert source.read_bytes() == destination.read_bytes() and digest(source) == digest(destination) == row["sha256"]
    assert sum(row["bytes"] for row in mapping["files"]) == mapping["copied_bytes"] == 4339999
    extra = set(by_source) - {row["path"] for row in bindings["files"]}
    assert len(extra) == 1 and digest(Path(next(iter(extra)))) == "6bf5e032f670f563d2fa532aa5e66ebf7ecfbf0c83516043ece975c342e79c48"
    check("G2最小110绑定及清单自身实际复制", {"files": 111, "bytes": 4339999, "byte_differences": 0})
    collection = read(INTEGRATION / "collection_receipt.json")
    assert len(collection["mapping"]) == 11 and collection["initial_outer_exit_code"] == 1 and collection["initial_checker_exit_code"] == "NOT_RECORDED_ORIGINALLY"
    for item in collection["mapping"]:
        source, destination = Path(item["source"]), ROOT / item["destination"]
        assert source.read_bytes() == destination.read_bytes() and digest(source) == digest(destination) == item["sha256"]
    tool_names = ["root_initial_assumption_tool_result.json", "root_physical_block_tool_result.json", "private_index_p01_tool_result.json", "private_index_p02_tool_result.json"]
    tool_results = {name: read(INTEGRATION / name) for name in tool_names}
    assert tool_results[tool_names[0]]["exit_code"] == 1 and "AssertionError" in tool_results[tool_names[0]]["output"]
    assert all(tool_results[name]["exit_code"] == 0 for name in tool_names[1:])
    repeat = read(INTEGRATION / "diagnostics/root_freeze_packaging_checks_02.json")
    assert [x["exit_code"] for x in repeat] == [2, 0]
    assert repeat[0]["result"]["errors"] == ["checks[1] 依赖检查状态为 NOT_RUN，阻断 inputs 核验"]
    check("总控失败/修正原件保全", {"collection_files": 11, "native_tool_results": 4, "initial_wrapper_exit": 1, "initial_underlying_checker_exit": "NOT_RECORDED_ORIGINALLY", "actual_repeat_exit_codes": [2, 0]})
    sdk_paths = read(INTEGRATION / "original_sdk_whitespace_paths.json")
    p01 = read(INTEGRATION / "diagnostics/candidate_index_p01_receipt.json")
    p02 = read(INTEGRATION / "diagnostics/candidate_index_p02_receipt.json")
    p01_text = (INTEGRATION / "diagnostics/candidate_index_p01_whitespace.log").read_text(encoding="utf-8")
    failures = set(re.findall(r"^(report/evidence/S2B-T06/.+?):\d+:", p01_text, re.MULTILINE))
    assert len(sdk_paths) == len(set(sdk_paths)) == 42 and failures == set(sdk_paths)
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    added = run("attributes_diff", ["git", "diff", "--", ".gitattributes"]).decode("utf-8")
    exception_lines = [line[1:] for line in added.splitlines() if line.startswith("+report/evidence/S2B-T06/") and "whitespace=-" in line and "*" not in line]
    assert len(exception_lines) == 42 and {line.split()[0] for line in exception_lines} == set(sdk_paths)
    for path in scope["source_sha256"]:
        assert path + " -text" in attributes and not re.search(r"^" + re.escape(path) + r"\s+.*whitespace=-", attributes, re.MULTILINE)
    assert p01["status"] == "CHECKS_REQUIRED" and p01["whitespace_exit_code"] == 2
    assert p02["status"] == "PASS_PRIVATE_INDEX" and p02["whitespace_exit_code"] == 0 and p02["bound_files"] == 417 and p02["raw_and_restored_differences"] == []
    check("42空白例外精确作用域", {"p01_failures": 42, "new_exact_attribute_paths": 42, "sets_equal": True, "new_project_source_broad_exemption": False})
    checker = ROOT / "verification/check_stage_delivery.py"
    for name, mode, manifest, expected in [("developer_inputs", "inputs", DEVELOPER / "inputs_manifest_r03.json", 0), ("developer_evidence", "evidence", DEVELOPER / "delivery_manifest.json", 0), ("freeze_inputs", "inputs", FREEZE / "delivery_manifest.json", 2), ("freeze_evidence", "evidence", FREEZE / "delivery_manifest.json", 0)]:
        result = json.loads(run(name, [PYTHON, "-B", "-X", "utf8", str(checker), "--mode", mode, "--manifest", str(manifest)], expected))
        if name == "freeze_inputs":
            assert result["status"] == "CHECKS_FAILED" and result["errors"] == ["checks[1] 依赖检查状态为 NOT_RUN，阻断 inputs 核验"]
        else:
            assert result["status"] == "CHECKS_OK" and result["errors"] == []
    assert json.loads(run("original_verify_freeze", [PYTHON, "-B", "-X", "utf8", str(FREEZE / "verify_freeze.py")]))["status"] == "PASS_ROOT_OFFLINE_FREEZE_BINDINGS"
    check("真实轻量交付与批准脚本重测", {"developer_inputs": 0, "developer_evidence": 0, "freeze_inputs": 2, "freeze_evidence": 0, "verify_freeze": 0, "freeze_inputs_only_reason": "checks[1] NOT_RUN"})
    object_directory = OUT / "private_objects"
    assert not object_directory.exists() and not (OUT / "private_index").exists()
    object_directory.mkdir()
    shared_objects = Path(run("shared_object_path", ["git", "rev-parse", "--path-format=absolute", "--git-path", "objects"]).decode("utf-8").strip())
    assert shared_objects.is_dir()
    environment = dict(os.environ, GIT_INDEX_FILE=str(OUT / "private_index"), GIT_OBJECT_DIRECTORY=str(object_directory), GIT_ALTERNATE_OBJECT_DIRECTORIES=str(shared_objects))
    run("private_read_tree", ["git", "read-tree", "HEAD"], environment=environment)
    allow = p02["allowlist"]
    assert len(allow) == len(set(allow)) == 413
    inputs = b"".join(path.encode("utf-8") + b"\0" for path in allow)
    # 强制模式仅作用于经固定p02清单允许的文件，绝不全量暂存。
    run("private_git_add", ["git", "add", "-f", "--pathspec-from-file=-", "--pathspec-file-nul"], environment=environment, data=inputs)
    staged = run("private_staged_paths", ["git", "diff", "--cached", "--name-only", "-z"], environment=environment).decode("utf-8").rstrip("\0").split("\0")
    assert set(staged) == set(allow)
    binding = {}
    for manifest_path, manifest in [(DEVELOPER / "delivery_manifest.json", developer), (FREEZE / "delivery_manifest.json", freeze)]:
        binding[manifest_path.relative_to(ROOT).as_posix()] = digest(manifest_path)
        for item in manifest["files"] + manifest["interfaces"]:
            assert item["path"] not in binding or binding[item["path"]] == item["sha256"]
            binding[item["path"]] = item["sha256"]
    assert len(binding) == 417 and ".codex/STATE.md" not in binding and ".gitattributes" not in binding
    paths = sorted(binding)
    raw_data = run("private_raw_batch", ["git", "cat-file", "--batch"], environment=environment, data=("\n".join(":" + p for p in paths) + "\n").encode("utf-8"))
    checkout_data = run("private_checkout_batch", ["git", "cat-file", "--batch", "--filters"], environment=environment, data=("\n".join(":" + p + " " + p for p in paths) + "\n").encode("utf-8"))
    raw_hashes, checkout_hashes = parse_batch(raw_data, paths), parse_batch(checkout_data, paths)
    differences = [p for p in paths if raw_hashes[p] != binding[p] or checkout_hashes[p] != binding[p]]
    assert not differences
    attr_paths = [".codex/STATE.md", ".gitattributes", *scope["source_sha256"]]
    attr_raw = run("private_selected_attributes", ["git", "check-attr", "--cached", "-z", "text", "whitespace", "--", *attr_paths], environment=environment)
    triples = attr_raw.decode("utf-8").rstrip("\0").split("\0")
    attr_values = {(triples[i], triples[i+1]): triples[i+2] for i in range(0, len(triples), 3)}
    for path in scope["source_sha256"]:
        assert attr_values[path, "text"] == "unset" and attr_values[path, "whitespace"] == "unspecified"
    assert attr_values[".codex/STATE.md", "text"] == attr_values[".gitattributes", "text"] == "unspecified"
    run("private_whitespace_check", ["git", "diff", "--cached", "--check"], environment=environment)
    create_json("private_restore_hashes.json", {"bound_files": len(paths), "differences": differences,
        "files": [{"path": p, "expected_sha256": binding[p], "index_raw_sha256": raw_hashes[p], "checkout_filtered_sha256": checkout_hashes[p]} for p in paths],
        "controls_excluded_from_417": [".codex/STATE.md", ".gitattributes"], "controls_preservation": "独立scope快照绑定；保留既有text unspecified换行处理", "attributes": [{"path": p, "attribute": a, "value": v} for (p, a), v in attr_values.items()]})
    check("独立私有index与对象恢复", {"staged_files": 413, "raw_checkout_bound_files": 417, "differences": 0, "whitespace_exit_code": 0, "writes": "仅i01/private_index和private_objects；共享Git对象仅只读借用", "new_four_sources": "text unset，whitespace unspecified，无空白豁免", "controls": "text unspecified，不纳入417的字节绑定"})
    assert run("shared_head_after", ["git", "rev-parse", "HEAD"]) == initial_head
    assert run("shared_index_after", ["git", "diff", "--cached", "--binary"]) == initial_index
    assert run("shared_status_after", ["git", "status", "--porcelain=v1", "-z"]) == initial_status
    assert digest(SCOPE) == SCOPE_SHA
    for item in scope["files"] + [{"path": x["path"], "sha256": x["sha256"]} for x in scope["controls"]]:
        assert digest(ROOT / item["path"]) == item["sha256"]
    check("补审期间共享版本/内容保持", {"HEAD": BASELINE, "index": "empty", "status_representation": "本次集成前后均NUL，未要求等于历史5项状态", "fixed_files": 31, "control_files": 2})
    create_json("audit_result.json", {"decision": "PASS", "task": "S2B-T06-INTEGRATION-R01", "checked_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "scope_sha256": SCOPE_SHA,
        "baseline_commit": BASELINE, "checks": CHECKS, "commands": COMMANDS, "blocking_findings": [], "gate_status": expected_gates,
        "hardware_execution": "NOT_RUN", "heavy_build_repeated": False, "full_process_tree_peak_memory": "NOT_MEASURED",
        "control_line_endings": "原始工作区控制文件与scope快照一致，既有Git换行处理保留；提交前UTF-8文本/完整差异由总控再次核对",
        "semantic_review": "正式文档、批准和STATE仅接受PS前置候选离线G1/G2；未通过实板/2B G0/G5，T05未选择，无模型部署就绪声明。CHECKS_OK只表示包装。",
        "source_inputs": "新4源码由固定SHA绑定；旧HEAD作为审查基线，upstream 90652b45固定。原G2源码/ELF候选未变，不重复重型Vitis。"})
    print(json.dumps({"decision": "PASS", "checks": len(CHECKS), "commands": len(COMMANDS), "result_sha256": digest(OUT / "audit_result.json"), "hardware_execution": "NOT_RUN"}, ensure_ascii=False))


def bind_evidence():
    """实际驱动退出0后生成不含自哈希循环的最小可复制清单。"""
    result = read(OUT / "audit_result.json")
    assert result["decision"] == "PASS" and (OUT / "audit.exit_code.txt").read_text(encoding="ascii").strip() == "0"
    files = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name not in {"private_index", "private_index.lock", "review_evidence_bindings.json"}:
            files.append({"path": str(path), "relative_to_i01": path.relative_to(OUT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size})
    create_json("review_evidence_bindings.json", {"task": "S2B-T06-INTEGRATION-R01", "decision": "PASS", "hardware_execution": "NOT_RUN", "scope_path": str(SCOPE), "scope_sha256": SCOPE_SHA,
        "result_path": str(OUT / "audit_result.json"), "result_sha256": digest(OUT / "audit_result.json"), "driver_native_exit_code": 0,
        "script_sha256": digest(Path(__file__)), "files": files, "file_count": len(files), "bytes": sum(x["bytes"] for x in files),
        "excluded": ["private_index二进制", "private_objects缓存"], "self_binding": "本清单不纳入自身；总控另计算清单SHA并按清单逐字节复制。大stdout为无损gzip，记录raw SHA/长度并已解压逐字节复核。"})
    print(json.dumps({"decision": "PASS", "result_sha256": digest(OUT / "audit_result.json"), "bindings_sha256": digest(OUT / "review_evidence_bindings.json"), "file_count": len(files), "bytes": sum(x["bytes"] for x in files)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        bind_evidence() if sys.argv[1:] == ["--bind-evidence"] else audit()
    except Exception:
        create_json("failed_audit.json", {"decision": "AUDIT_TOOL_FAILURE", "commands": COMMANDS, "checks_completed": CHECKS, "traceback": traceback.format_exc(), "hardware_execution": "NOT_RUN"})
        raise
