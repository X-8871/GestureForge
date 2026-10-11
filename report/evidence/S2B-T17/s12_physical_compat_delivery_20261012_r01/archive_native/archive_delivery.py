"""逐字节归档兼容逻辑原件；不恢复或修改固定工具目标。"""
import hashlib
import json
import os
import pathlib
import stat
import sys
import zipfile

HERE = pathlib.Path(__file__).absolute().parent
ROOT = HERE.parents[3]
OUT = ROOT / "report/evidence/S2B-T17/s12_physical_compat_delivery_20261012_r01"
HEAD = "891f750045ce141a8152c96025da559ff1d3a321"
SOURCES = [
    ("author_r01", "s12_physical_compat_prepare_20261012_r01", "448666a160722be83767ba53a775695e515f3df918cef490141c6a47545d1166", 1836, "compatibility_delivery_receipt.json", "8985ce7655a95a48faabb273e502aa91131c1985163f6ba98e8aee336ebe779e"),
    ("review_r01", "independent_s12_physical_compat_review_20261012_r01", "5dfd60ebf6c7a37eff2ec2538ac3000e89b3f94abc57e04f2fd12a685bc7d727", 168, "final_review_receipt.json", "ab56b991d4f9eb6563c7d06444ac35f9de57d07b8f26051b7f32af8dd9ad7d76"),
    ("author_r02", "s12_physical_compat_prepare_20261012_r02", "0e5cdd71fd3ff35b76fa440147b72613154fb5840269c010e2396e60d9adbec5", 3245, "compatibility_delivery_receipt.json", "8fe0346124032ec99bc637d9402901df2a9c462098634984f6838242f5da3c78"),
    ("review_r02", "independent_s12_physical_compat_review_20261012_r02", "4e57062b894df2c6392798172fcfc1e1f7b149d13015f8ccf248185a4e3ff85c", 1155, "final_review_receipt.json", "018c5773edf8a56c0fc6e2eaf068c164ef7f987244621e2720cc95ca777cc3dc"),
]
TOOLS = ["collector.py", "impl_collector.py", "source_after_check.py", "native_source_after.py", "native.py", "compat_pins.py"]
GUARD_DIR = ROOT / "report/evidence/S2B-T17/s12_resource_guard_delivery_20261012_r01"
GUARD_INPUTS = {
    "delivery_manifest_r02.json": "139d5b72f9faa0bb58943b0dcff0d5e70ebcd8d189246e061a4df6013f8c3dce",
    "archive_mapping.json": "52c8fcb9e6a829eafb3e6de2394b543d01feaa055eb34a2d507cf1ab2ba71103",
    "recovery_entry.json": "28bff3069ccecb4a8d801f3e6e8feddd1473119f542dabf50152493b2cc82568",
}
VERIFIED_DIRS = set()

def exact(path, directory=False):
    """核对精确组件名称、目标类型并拒绝链接或重解析点。"""
    path = pathlib.Path(path)
    assert path.is_absolute()
    relative = path.relative_to(ROOT)
    assert all(p not in ("", ".", "..") for p in relative.parts)
    current = ROOT
    for component in relative.parts:
        if current not in VERIFIED_DIRS:
            st = current.lstat()
            assert stat.S_ISDIR(st.st_mode) and not current.is_symlink()
            assert not getattr(st, "st_file_attributes", 0) & 0x400
            VERIFIED_DIRS.add(current)
        matches = [item for item in current.iterdir() if item.name == component]
        assert len(matches) == 1, str(path)
        current = matches[0]
    st = current.lstat()
    assert not current.is_symlink() and not getattr(st, "st_file_attributes", 0) & 0x400
    assert stat.S_ISDIR(st.st_mode) if directory else stat.S_ISREG(st.st_mode)
    return current

def digest(path):
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as src:
        while block := src.read(65536):
            h.update(block)
            size += len(block)
    return h.hexdigest(), size

def checked(path, sha, size=None):
    path = exact(path)
    actual_sha, actual_size = digest(path)
    assert actual_sha == sha and (size is None or actual_size == size), str(path)
    return path

def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")

def copy_raw(source, dest):
    source = exact(source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        exact(dest)
        assert digest(source) == digest(dest), "拒绝覆盖已存在且不同的归档原件"
    else:
        with dest.open("xb") as dst, source.open("rb") as src:
            while block := src.read(65536):
                dst.write(block)
    assert digest(source) == digest(dest)
    sha, size = digest(dest)
    return {"original_path": source.relative_to(ROOT).as_posix(), "original_absolute_path": str(source),
            "archived_path": dest.relative_to(ROOT).as_posix(), "sha256": sha, "bytes": size}

def create_archive():
    exact(OUT.parent, True)
    if OUT.exists():
        exact(OUT, True)
        assert (HERE / "archive.native.json").is_file()
        assert json.loads((HERE / "archive.native.json").read_text(encoding="utf-8"))["native_exit_code"] == 1
        assert not (OUT / "source_restore_index.json").exists(), "禁止修改已封存目录"
    else:
        assert not any(p.name == OUT.name for p in OUT.parent.iterdir())
    # 冻结索引与重要回执在创建正式目录前全部核验。
    for _, dirname, sha, _, receipt, receipt_sha in SOURCES:
        base = exact(ROOT / "tmp/2B/S2B-T17" / dirname, True)
        checked(base / "raw_manifest.jsonl", sha)
        checked(base / receipt, receipt_sha)
    for name, sha in GUARD_INPUTS.items():
        checked(GUARD_DIR / name, sha)
    OUT.mkdir(exist_ok=True)
    inventory = []
    plain = []
    counts = []
    for label, dirname, manifest_sha, count, receipt, _ in SOURCES:
        base = exact(ROOT / "tmp/2B/S2B-T17" / dirname, True)
        manifest = checked(base / "raw_manifest.jsonl", manifest_sha)
        rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
        assert len(rows) == count
        members = set()
        archive = OUT / (label + ".zip")
        existing_zip = archive.exists()
        if existing_zip:
            exact(archive)
        with zipfile.ZipFile(archive, "r" if existing_zip else "x", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for line, row in enumerate(rows, 1):
                rel = pathlib.PurePosixPath(row["path"])
                assert not rel.is_absolute() and all(p not in ("", ".", "..") for p in rel.parts)
                source = checked(base.joinpath(*rel.parts), row["sha256"], row["bytes"])
                if "absolute_path" in row:
                    assert str(source) == row["absolute_path"]
                entry = source.relative_to(ROOT).as_posix()
                assert entry not in members and not entry.startswith("/") and ":" not in entry
                members.add(entry)
                if not existing_zip:
                    z.write(source, arcname=entry)
                inventory.append({"group": label, "manifest_original_path": manifest.relative_to(ROOT).as_posix(),
                                  "manifest_sha256": manifest_sha, "manifest_line": line, "original_raw_path": row["path"],
                                  "original_repo_path": entry, "original_absolute_path": str(source),
                                  "zip": archive.name, "entry": entry, "sha256": row["sha256"], "bytes": row["bytes"]})
        # 逐项读取压缩字节，并核对名称、链接属性、哈希和长度。
        expected = [i for i in inventory if i["group"] == label]
        with zipfile.ZipFile(archive) as z:
            assert len(z.infolist()) == len(members) == count and set(z.namelist()) == members
            for item in expected:
                info = z.getinfo(item["entry"])
                assert not info.is_dir() and not stat.S_ISLNK(info.external_attr >> 16)
                h = hashlib.sha256()
                size = 0
                with z.open(info) as f:
                    while block := f.read(65536):
                        h.update(block)
                        size += len(block)
                assert h.hexdigest() == item["sha256"] and size == item["bytes"]
        counts.append({"group": label, "files": count, "raw_bytes": sum(i["bytes"] for i in expected),
                       "zip": archive.name, "zip_sha256": digest(archive)[0], "zip_bytes": archive.stat().st_size,
                       "readback_verified_items": count})
        # 原始顶层记录单独保留，夹具及首轮失败原件仍完整位于 ZIP 内。
        names = ["raw_manifest.jsonl", receipt, "final_draft_binding.json", "pending_pins.json", "preseal_receipt.json"]
        for name in names:
            source = base / name
            if source.exists():
                plain.append(copy_raw(source, OUT / "frozen_records" / label / name))
        if label.startswith("author"):
            for name in TOOLS:
                for suffix in ("", ".diff"):
                    source = base / (name + suffix)
                    if label == "author_r01" and name == "compat_pins.py" and suffix == ".diff":
                        assert not source.exists(), "首轮实有五diff；不捏造第六份"
                        continue
                    plain.append(copy_raw(source, OUT / "tools" / label / (name + suffix)))
    with (OUT / "zip_entry_index.jsonl").open("x", encoding="utf-8", newline="\n") as f:
        for item in inventory:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    fixed_refs = []
    for name, sha in GUARD_INPUTS.items():
        source = checked(GUARD_DIR / name, sha)
        plain.append(copy_raw(source, OUT / "guard_recovery_reference" / name))
        fixed_refs.append({"original_path": source.relative_to(ROOT).as_posix(), "sha256": sha})
    review = json.loads((OUT / "frozen_records/review_r02/final_review_receipt.json").read_text(encoding="utf-8"))
    assert review["status"] == "PASS_COMPAT_LOGIC_G2_ONLY"
    for tool in review["reviewed_files"]:
        checked(OUT / "tools/author_r02" / tool["path"], tool["sha256"], tool["bytes"])
    index = {"schema_version": 1, "status": "ARCHIVE_BYTES_VERIFIED_COMPAT_LOGIC_G2_ONLY", "source_commit_observation": HEAD,
             "source_commit_role": "归档时观察的precommit891基线，不是最终生产候选tree或physical SOURCE_COMMIT",
             "raw_manifest_rows": len(inventory), "zip_count": len(counts), "archives": counts, "plain_raw_copies": plain,
             "entry_index": {"path": "zip_entry_index.jsonl", "sha256": digest(OUT / "zip_entry_index.jsonl")[0]},
             "restore_original_tool_targets": False, "restore_note": "未恢复原固定工具目标；本轮仅逐项ZIP读取验证。恢复须在未来获授权且精确目标不存在时按entry原仓库相对路径执行，禁止自动覆盖。",
             "guard_fixed_recovery_references": fixed_refs,
             "tool_targets": [{"original_absolute_path": str(ROOT / "tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r02" / name),
                               "archive_copy": "tools/author_r02/" + name, "sha256": digest(OUT / "tools/author_r02" / name)[0]} for name in TOOLS],
             "pin_state": "SOURCE_COMMIT/实际freeze/RunIds/functionalG2均None或PENDING；本轮不改pins",
             "r01_review": "CHANGES_REQUIRED：两P2失败与首次generation/native错误记录保留",
             "archive_first_native_failure": "首轮native1：r01不存在compat_pins.py.diff；原脚本及原stderr保留。首轮实有五diff、r02六diff；不伪造缺失文件。已有ZIP只读取逐项校验，已有plain仅允许字节相同且不覆盖。",
             "r02_review": "PASS_COMPAT_LOGIC_G2_ONLY", "physical_g0": "BLOCKED", "actual_sta": "NOT_RUN",
             "actual_new_budget": "NOT_RUN", "old_s11_budget": "BLOCKED", "g3": "NOT_RUN", "g5": "NOT_RUN"}
    write_json(OUT / "source_restore_index.json", index)
    print(json.dumps({"status": index["status"], "raw_manifest_rows": len(inventory), "zip_count": len(counts), "archives": counts}, ensure_ascii=False))

def manifest():
    files = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "delivery_manifest.json":
            exact(path)
            role = "input" if "frozen_records" in path.parts or "guard_recovery_reference" in path.parts else "artifact"
            files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)[0], "role": role,
                          "keep_reason": "冻结原件、逐项恢复映射或真实归档与包装核验记录；保留失败及未执行语义"})
    archive_native = json.loads((HERE / "archive_retry.native.json").read_text(encoding="utf-8"))
    assert type(archive_native["native_exit_code"]) is int and archive_native["native_exit_code"] == 0
    value = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T17", "run_id": OUT.name, "source_commit": HEAD,
             "evidence_dir": OUT.relative_to(ROOT).as_posix(), "interfaces": [],
             "interfaces_not_applicable_reason": "本交付是离线physical collector兼容逻辑工具与审查原件归档，不形成模型、总线或业务接口freeze；依赖为已绑定的工具字节及独审回执。",
             "files": files, "checks": [
                 {"name": "archive_zip_bytes", "status": "PASS", "command": " ".join(archive_native["command"]), "exit_code": 0},
                 {"name": "compat_logic_g2", "status": "PASS", "command": "独审真实原生记录见review_r02.zip及冻结final_review_receipt.json：111 checks native0", "exit_code": 0},
                 {"name": "physical_g0", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "最终源码commit、43实际sourcefreeze、RunIds和functionalG2最终pins尚未给出；不能重型派发"},
                 {"name": "new_physical_budget_sta_g3_g5", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本轮仅归档；未执行综合PNR、STA、真实新budget、板级G3或阶段G5"},
                 {"name": "old_s11_budget", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "旧S11预算未闭合，不能由本轮工具逻辑PASS追认"}],
             "tool_versions": {"python": sys.version, "archive": "stdlib zipfile，四份冻结索引逐项读取校验"},
             "limitations": ["SOURCE为precommit891当前观测，不是最终生产候选冻结", "仅PASS_COMPAT_LOGIC_G2_ONLY，不是physical G0批准", "未恢复原固定工具目标", "离散自有树RSS见native记录，OS原子绝对树峰未测null", "仅本新目录写入；不改生产、旧原件、pins或Git，不运行heavy或hardware"]}
    target = OUT / "delivery_manifest.json"
    if target.exists():
        # 仅本任务尚未封存的清单按新封存集合刷新；历史首次清单单独保留。
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        write_json(target, value)
    print(json.dumps({"manifest": str(target), "sha256": digest(target)[0], "files": len(files)}, ensure_ascii=False))

def finalize():
    formal_logs = OUT / "archive_native"
    formal_logs.mkdir(exist_ok=True)
    for source in sorted(HERE.iterdir()):
        if source.is_file() and source.name not in ("finalize.stdout.bin", "finalize.stderr.bin", "finalize.native.json"):
            dest = formal_logs / source.name
            if not dest.exists():
                copy_raw(source, dest)
    manifest()

if __name__ == "__main__":
    {"archive": create_archive, "manifest": manifest, "finalize": finalize}[sys.argv[1]]()
