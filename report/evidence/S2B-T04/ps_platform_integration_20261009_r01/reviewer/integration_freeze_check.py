"""独立增量核对离线冻结记录、原字节复制链与保留失败，不批准实物操作。"""

import ast
import hashlib
import json
import subprocess
from pathlib import Path


REVIEW = Path(__file__).resolve().parent
ROOT = REVIEW.parents[3]
RUN = ROOT / "report/evidence/S2B-T04/ps_platform_freeze_20261009_r01"
HEAD = "5b9122e425c1499b36b09e80cffda7bf50ca2ef0"
EXPECTED = {
    "docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_platform_offline_freeze_20261009.md":
        "89512d94859abf083e958a2e53139d8f4ab0c0a61989c76eb8794eba9c9db6c1",
    ".codex/STATE.md": "a4c1a621d307bcbf4158826d00b4e7225720761d80b994be3a45868dda8ec3be",
    ".gitattributes": "b7dbcdbe5540cb2b068d2c098cad006f44b6c7d144701f3c714a112c1cbbeb7c",
    "report/evidence/S2B-T04/ps_platform_freeze_20261009_r01/delivery_manifest.json":
        "f07c16f6b3ede117f300707dfffee6615af12a08517a165f9d0fd9f80dd81eb3",
    "report/evidence/S2B-T04/ps_platform_freeze_20261009_r01/acceptance.json":
        "49abdb359951a4af64c9fd08c7a0942154c66a8025789ad9c2ef3d6bdbac8927",
    "report/evidence/S2B-T04/ps_platform_freeze_20261009_r01/copy_mapping.json":
        "45cb9575ff2b8d25d6d9b2211ead13c08a03ccafecff6d235f00feddd6f8dcdd",
}


def digest(path):
    """验证精确文件类型并读取原始字节摘要。"""
    assert path.is_file(), str(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    """只按 UTF-8 读取指定的 JSON 文件。"""
    assert path.is_file(), str(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    """本次只核查已有实验的冻结集成，不重建 Vivado 或改动正式文件。"""
    assert ROOT == Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
    assert ROOT.is_dir() and REVIEW.is_dir() and RUN.is_dir()
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode("utf-8").strip() == HEAD
    for relative, expected in EXPECTED.items():
        assert digest(ROOT / relative) == expected, relative

    manifest = read_json(RUN / "delivery_manifest.json")
    acceptance = read_json(RUN / "acceptance.json")
    mapping = read_json(RUN / "copy_mapping.json")
    review = read_json(RUN / "reviewer/review_evidence_bindings.json")
    assert len(manifest["files"]) == 69
    paths = {item["path"] for item in manifest["files"]}
    assert len(paths) == 69
    for item in manifest["files"]:
        path = ROOT / item["path"]
        assert path.resolve().is_relative_to(ROOT)
        assert digest(path) == item["sha256"], item["path"]
    actual_files = {path.relative_to(ROOT).as_posix() for path in RUN.rglob("*") if path.is_file()}
    assert actual_files == {name for name in paths if name.startswith(RUN.relative_to(ROOT).as_posix() + "/")} | {
        (RUN / "delivery_manifest.json").relative_to(ROOT).as_posix()
    }

    assert mapping["status"] == "EXACT_BYTE_COPY_PASS" and len(mapping["files"]) == 55
    destinations = {item["source"]: item for item in mapping["files"]}
    assert len(destinations) == 55
    assert len({item["destination"] for item in mapping["files"]}) == 55
    for item in mapping["files"]:
        copied = ROOT / item["destination"]
        assert copied.resolve().is_relative_to(RUN.resolve())
        assert digest(copied) == item["sha256"] and copied.stat().st_size == item["bytes"]
        if item["source"] != ".gitattributes":
            original = ROOT / item["source"]
            assert digest(original) == item["sha256"] and original.read_bytes() == copied.read_bytes()
    assert review["status"] == "PASS" and len(review["artifacts"]) == 53
    assert review["issues"]["R1_P1"]["status"] == "CLOSED"
    assert review["issues"]["remaining_blocking_design_issues"] == []
    assert digest(RUN / "reviewer/review_evidence_bindings.json") == "b4290cff78f423e6395203dec267e11c981df77ebc930bb6ff91d9aaa8309d00"
    for item in review["artifacts"]:
        copied = destinations[item["path"]]
        assert copied["sha256"] == item["sha256"] and copied["bytes"] == item["bytes"]
    assert set(destinations) == {item["path"] for item in review["artifacts"]} | {
        "tmp/2B/S2B-T04/platform_review_20261009_r02/review_evidence_bindings.json", ".gitattributes"
    }
    for item in review["source_baseline"]["fixed_files"]:
        path = ROOT / (destinations[item["path"]]["destination"] if item["path"] == ".gitattributes" else item["path"])
        assert digest(path) == item["sha256"]

    old_attributes = (RUN / "source_prior/.gitattributes").read_bytes()
    current_attributes = (ROOT / ".gitattributes").read_bytes()
    assert hashlib.sha256(old_attributes).hexdigest() == "b9065faaf804ee149a01c77e1c64a2465c8518acb5d066d22c5cf21975c22248"
    assert current_attributes.startswith(old_attributes)
    attribute_suffix = current_attributes[len(old_attributes):].decode("utf-8")
    suffix_lines = [line for line in attribute_suffix.splitlines() if line and not line.startswith("#")]
    assert len(suffix_lines) == 7
    for line in suffix_lines:
        assert line.startswith("docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_platform_offline_freeze_20261009.md ") or line.startswith(
            "report/evidence/S2B-T04/ps_platform_freeze_20261009_r01/"
        )
    checked_paths = sorted(paths)
    attr_result = subprocess.run(
        ["git", "check-attr", "--stdin", "-z", "text", "whitespace"],
        input=("\0".join(checked_paths) + "\0").encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT, check=True,
    )
    triples = attr_result.stdout.decode("utf-8").rstrip("\0").split("\0")
    attributes = {}
    for index in range(0, len(triples), 3):
        path, name, value = triples[index:index + 3]
        attributes.setdefault(path, {})[name] = value
    assert len(attributes) == 69
    for path, values in attributes.items():
        assert values["text"] == "unset", (path, values)
        if path.startswith(RUN.relative_to(ROOT).as_posix() + "/"):
            raw = path.endswith((".log", ".tcldict", "/ps7_init.c", "/ps7_init.h", "/ps7_init.tcl"))
            assert values["whitespace"] == (
                "-blank-at-eol,-blank-at-eof,-space-before-tab,cr-at-eol" if raw else
                "blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol"
            ), (path, values)

    assert acceptance["status"] == "ACCEPTED_OFFLINE_BUILD_INPUT"
    assert acceptance["approved_by"] == "阶段总控 /root"
    assert acceptance["approval_scope"] == "仅S2B-T06 standalone CPU0 UART/DDR前置检查软件及必要官方PS初始化产物的离线构建输入"
    assert acceptance["interface_version"] == "s2b-ps-platform/1.0.1"
    assert acceptance["source_baseline"] == HEAD
    for name in ("formal_record", "candidate_xsa", "independent_review", "copy_mapping"):
        item = acceptance[name]
        assert digest(ROOT / item["path"]) == item["sha256"]
    assert acceptance["formal_record"]["path"].startswith("docs/")
    assert acceptance["candidate_xsa"]["sha256"] == review["check_result"]["candidate_xsa_sha256"]
    assert not any("批准" in item["name"] for item in manifest["checks"])
    for item in manifest["checks"]:
        if item["status"] == "PASS":
            assert isinstance(item["command"], str) and item["command"]
            assert type(item["exit_code"]) is int and item["exit_code"] == 0

    original_manifest = read_json(RUN / "delivery_manifest_initial.json")
    failure = read_json(RUN / "pack_checks_initial_receipts.json")
    assert digest(RUN / "delivery_manifest_initial.json") == "990c74299e89a8cc55ac7363b740247054162007f5d9809fdf565c185bb2c6a9"
    original_approval = [item for item in original_manifest["checks"] if item["name"] == "总控离线输入批准"]
    assert len(original_approval) == 1 and original_approval[0]["command"] is None and original_approval[0]["exit_code"] is None
    assert failure["status"] == "INITIAL_PACK_CHECK_FAILED"
    for mode in ("inputs", "evidence"):
        assert failure[mode]["exit_code"] == 1
        output = json.loads(failure[mode]["output"])
        assert output["status"] == "CHECKS_FAILED" and len(output["errors"]) == 2
        assert all("checks[4]" in message for message in output["errors"])

    checker_source = (RUN / "freeze_binding_check.py").read_text(encoding="utf-8")
    tree = ast.parse(checker_source)
    writes = {"write_text", "write_bytes", "mkdir", "unlink", "rename", "replace", "rmdir", "touch", "exec", "eval"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else ""
            assert name not in writes, name
    assert "不判断批准权限或实物适用性" in checker_source
    assert "只核对引用与文件数据，不代表批准权限、实物适用性或阶段2B验收" in checker_source
    assert json.loads((RUN / "freeze_check_r01.stdout.log").read_text(encoding="utf-8"))["status"] == "FREEZE_BINDINGS_OK"
    assert (RUN / "freeze_check_r01.stderr.log").read_bytes() == b""
    state = (ROOT / ".codex/STATE.md").read_text(encoding="utf-8")
    document = (ROOT / acceptance["formal_record"]["path"]).read_text(encoding="utf-8")
    assert len(state.splitlines()) == 47
    assert "未通过阶段2B G0" in state and "仅批准S2B-T06离线构建" in state
    assert "不表示阶段2B G0/G3/G4/G5通过" in document and "实际板卡适用性" in document
    assert "物理异常排空恢复候选仍等待 Wong 选择" in document
    print(json.dumps({
        "status": "INCREMENTAL_FREEZE_INTEGRATION_PASS",
        "source_baseline": HEAD, "manifest_bindings": 69, "copied_files": 55,
        "independent_experiment_files": 53, "original_sources_unchanged": 6,
        "historical_attributes_restored": True, "attribute_paths_checked": 69,
        "original_packaging_failure_exit_codes": {"inputs": 1, "evidence": 1},
        "approval_scope_data_matches_root_freeze": True,
        "checks_do_not_claim_manual_approval_as_process": True,
        "state_lines": 47, "new_vivado_runs": 0,
        "limits": "仅增量核对离线冻结集成；人工批准的权限和实物适用性不由脚本判定。",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
