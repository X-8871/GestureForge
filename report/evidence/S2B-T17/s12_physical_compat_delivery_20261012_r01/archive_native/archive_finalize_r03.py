"""追加正确文件角色的封存清单；所有先前失败字节保留。"""
import json
import sys
import archive_delivery as a

def copy_closed():
    for p in sorted(a.HERE.iterdir()):
        if p.is_file() and not p.name.startswith(("prepare_r03.", "seal_r03.", "final_evidence.", "final_inputs.")):
            a.copy_raw(p, a.OUT / "archive_native" / p.name)

def build(name, seal=False):
    copy_closed()
    if seal:
        for suffix in (".stdout.bin", ".stderr.bin", ".native.json"):
            a.copy_raw(a.HERE / ("prepare_r03" + suffix), a.OUT / "archive_native" / ("prepare_r03" + suffix))
    data = json.loads((a.OUT / "delivery_manifest_precheck.json").read_text(encoding="utf-8"))
    for label in ("precheck_evidence", "precheck_inputs", "precheck_r02_evidence", "precheck_r02_inputs"):
        path = a.HERE / (label + ".native.json")
        if path.exists():
            r = json.loads(path.read_text(encoding="utf-8"))
            code = r["native_exit_code"]
            assert type(code) is int
            data["checks"].append({"name": label, "status": "PASS" if code == 0 else "FAIL",
                "command": " ".join(r["command"]), "exit_code": code,
                "reason": "首evidence2因缺source/result角色，修正清单未改旧字节；inputs2是保留失败/未就绪/未执行导致，不代表工具逻辑或恢复字节失败"})
    if seal:
        evidence = json.loads((a.HERE / "precheck_r02_evidence.native.json").read_text(encoding="utf-8"))
        inputs = json.loads((a.HERE / "precheck_r02_inputs.native.json").read_text(encoding="utf-8"))
        assert evidence["native_exit_code"] == 0 and type(evidence["native_exit_code"]) is int
        assert inputs["native_exit_code"] == 2 and type(inputs["native_exit_code"]) is int
        native = [json.loads(p.read_text(encoding="utf-8")) for p in a.HERE.glob("*.native.json")]
        a.write_json(a.OUT / "archive_receipt.json", {
            "status": "STOP_ARCHIVE_BYTES_VERIFIED_COMPAT_LOGIC_G2_ONLY",
            "raw_manifest_rows": 6404, "zip_count": 4,
            "native_records": native,
            "max_sampled_owned_tree_peak_bytes": max(r["sampled_owned_tree_peak_bytes"] for r in native),
            "absolute_tree_peak_bytes": None,
            "source_restore_index_sha256": a.digest(a.OUT / "source_restore_index.json")[0],
            "zip_entry_index_sha256": a.digest(a.OUT / "zip_entry_index.jsonl")[0],
            "recovery_supplement_sha256": a.digest(a.OUT / "recovery_supplement.json")[0],
            "packaging_precheck_native": {"evidence": 0, "inputs": 2},
            "packaging_first_native": {"evidence": 2, "inputs": 2},
            "archive_first_native": 1, "archive_retry_native": 0,
            "source_commit_role": "实际precommit891观察；非最终生产候选tree", "pins": "None/PENDING",
            "original_fixed_targets_restored": False, "physical_g0": "BLOCKED", "new_budget_sta_g3_g5": "NOT_RUN",
            "old_s11_budget": "BLOCKED", "no_production_old_files_or_git_writes": True,
            "final_manifest_recheck": "最后只读再核验输出留在隔离tmp，不修改本封存包；不自哈希追认尚未发生结果"})
    files = []
    for path in sorted(a.OUT.rglob("*")):
        if path.is_file():
            a.exact(path)
            if path.suffix == ".py":
                role = "source"
            elif path.name.endswith((".stdout.bin", ".stderr.bin")):
                role = "log"
            elif path.name.endswith(".native.json") or path.name == "archive_receipt.json":
                role = "result"
            elif "frozen_records" in path.parts or "guard_recovery_reference" in path.parts:
                role = "input"
            else:
                role = "artifact"
            files.append({"path": path.relative_to(a.ROOT).as_posix(), "sha256": a.digest(path)[0], "role": role,
                "keep_reason": "可恢复原工具/逐项ZIP映射、真实成功失败native或冻结包装清单；不删除首失败"})
    data["files"] = files
    a.write_json(a.OUT / name, data)
    print(json.dumps({"manifest": str(a.OUT / name), "sha256": a.digest(a.OUT / name)[0], "files": len(files),
        "source_restore_index_sha256": a.digest(a.OUT / "source_restore_index.json")[0],
        "zip_entry_index_sha256": a.digest(a.OUT / "zip_entry_index.jsonl")[0]}, ensure_ascii=False))

if __name__ == "__main__":
    if sys.argv[1] == "prepare":
        build("delivery_manifest_precheck_r02.json")
    else:
        assert sys.argv[1] == "seal"
        build("delivery_manifest.json", True)
