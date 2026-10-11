"""追加归档补充与两阶段封存，不覆盖已写证据字节。"""
import json
import pathlib
import sys
import archive_delivery as a

HERE, ROOT, OUT = a.HERE, a.ROOT, a.OUT

def prepare():
    assert (HERE / "head.stdout.bin").read_text(encoding="utf-8").strip() == a.HEAD
    assert json.loads((HERE / "archive_retry.native.json").read_text(encoding="utf-8"))["native_exit_code"] == 0
    extra = []
    for label, dirname, _, _, _, _ in a.SOURCES:
        base = a.exact(ROOT / "tmp/2B/S2B-T17" / dirname, True)
        for source in sorted(base.iterdir()):
            if source.is_file():
                extra.append(a.copy_raw(source, OUT / "additional_originals" / label / source.name))
    old_binding = json.loads((OUT / "frozen_records/author_r01/final_draft_binding.json").read_text(encoding="utf-8"))
    helper = [f for f in old_binding["files"] if f["path"] == "compat_pins.py"]
    assert len(helper) == 1 and "diff" not in helper[0]
    assert not (ROOT / "tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01/compat_pins.py.diff").exists()
    a.write_json(OUT / "recovery_supplement.json", {
        "status": "ARCHIVE_BYTES_VERIFIED_COMPAT_LOGIC_G2_ONLY",
        "additional_originals": extra,
        "missing_auxiliary": {"path": "tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01/compat_pins.py.diff",
            "status": "MISSING_AUXILIARY_DIFF_NOT_DECLARED_BY_BINDING", "binding_declares_diff": False,
            "declared_missing_classification": "若原binding存在diff声明才适用MISSING_DECLARED_AUXILIARY_DIFF；实际原binding未声明diff，不能捏造",
            "explanation": "首归档器误预期r01第六diff导致实际native1；原helper新增文件字节完整绑定，r01五份真实diff与r02六份diff可恢复"},
        "restore_original_tool_targets": False, "restore_note": "未恢复原固定工具目标；只逐项ZIP读取验证6404 RAW。",
        "source_restore_index_sha256": a.digest(OUT / "source_restore_index.json")[0],
        "zip_entry_index_sha256": a.digest(OUT / "zip_entry_index.jsonl")[0],
        "first_failure_native": json.loads((HERE / "archive.native.json").read_text(encoding="utf-8")),
        "success_native": json.loads((HERE / "archive_retry.native.json").read_text(encoding="utf-8")),
        "source_commit_observation": a.HEAD, "source_commit_role": "precommit891观察；最终生产候选freeze未知",
        "physical_g0": "BLOCKED", "new_budget_sta_g3_g5": "NOT_RUN", "old_s11_budget": "BLOCKED"})
    copy_captures()
    make_manifest("delivery_manifest_precheck.json")

def copy_captures():
    for source in sorted(HERE.iterdir()):
        if source.is_file() and not source.name.startswith(("prepare.", "seal.", "final_evidence.", "final_inputs.")):
            a.copy_raw(source, OUT / "archive_native" / source.name)

def make_manifest(name):
    retry = json.loads((HERE / "archive_retry.native.json").read_text(encoding="utf-8"))
    transcription = json.loads((OUT / "additional_originals/review_r02/native_command_transcription.json").read_text(encoding="utf-8"))
    assert type(transcription["native_exit_code"]) is int and transcription["native_exit_code"] == 0
    files = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            a.exact(p)
            role = "input" if "frozen_records" in p.parts or "guard_recovery_reference" in p.parts else "artifact"
            files.append({"path": p.relative_to(ROOT).as_posix(), "sha256": a.digest(p)[0], "role": role,
                          "keep_reason": "可恢复冻结工具原件、真实成功失败native、ZIP逐项字节索引或包装检查原件"})
    checks = [
        {"name": "archive_first_attempt", "status": "FAIL", "command": " ".join(json.loads((HERE / "archive.native.json").read_text(encoding="utf-8"))["command"]), "exit_code": 1, "reason": "首归档器错误预期不存在的r01第六diff；失败原脚本和stderr保留，后续只新增或核验复用"},
        {"name": "archive_zip_byte_readback", "status": "PASS", "command": " ".join(retry["command"]), "exit_code": 0},
        {"name": "compat_logic_g2_only", "status": "PASS", "command": " ".join(transcription["actual_command"]), "exit_code": 0, "reason": "111独审逻辑检查；native来源为工具输出转录，非原stdout流，原转录字节保留"},
        {"name": "physical_g0", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "最终commit、43实际sourcefreeze、RunIds、functionalG2及helper共同版本未给出，pins仍None/PENDING"},
        {"name": "actual_physical_budget_sta_g3_g5", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本轮仅轻量归档，未执行综合PNR/新budget/STA/板卡/阶段验收"},
        {"name": "old_s11_budget", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "旧S11预算不能由此次逻辑PASS追认"}]
    for label in ("precheck_evidence", "precheck_inputs"):
        record = HERE / (label + ".native.json")
        if record.exists():
            native = json.loads(record.read_text(encoding="utf-8"))
            code = native["native_exit_code"]
            assert type(code) is int and code == (0 if label.endswith("evidence") else 2)
            checks.append({"name": label, "status": "PASS" if code == 0 else "FAIL", "command": " ".join(native["command"]), "exit_code": code,
                           "reason": "evidence仅包装闭合；inputs真实2：首归档失败保留、physical pins未就绪及实际物理未执行"})
    value = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T17", "run_id": OUT.name,
        "source_commit": a.HEAD, "evidence_dir": OUT.relative_to(ROOT).as_posix(), "interfaces": [],
        "interfaces_not_applicable_reason": "离线collector兼容逻辑G2工具与审查原件归档不形成业务接口freeze，无适用上游模型/总线接口；适用输入是冻结工具、原native记录与独审回执。",
        "files": files, "checks": checks, "tool_versions": {"python": sys.version, "zip": "Python stdlib zipfile deflate6", "psutil": "7.2.2"},
        "limitations": ["PASS_COMPAT_LOGIC_G2_ONLY；非physicalG0或重型派发批准", "source_commit为precommit891观察而非最终生产候选tree", "所有实际pins仍None/PENDING，helper未改", "未恢复原固定工具目标；逐项ZIP读取核验", "native独审转录与本轮真实原stdout/stderr分列", "连续OS原子树峰未测null，真实离散自有峰见native记录", "r01两个P2、first_generation及首次归档native1完整保留", "不改生产/Git/旧原件，不执行heavy/ROSS/hardware"]}
    a.write_json(OUT / name, value)
    print(json.dumps({"manifest": str(OUT / name), "sha256": a.digest(OUT / name)[0], "files": len(files)}, ensure_ascii=False))

def seal():
    for label in ("prepare", "precheck_evidence", "precheck_inputs"):
        for suffix in (".stdout.bin", ".stderr.bin", ".native.json"):
            a.copy_raw(HERE / (label + suffix), OUT / "archive_native" / (label + suffix))
    copy_captures()
    make_manifest("delivery_manifest.json")

if __name__ == "__main__":
    {"prepare": prepare, "seal": seal}[sys.argv[1]]()
