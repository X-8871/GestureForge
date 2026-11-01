"""以不可变副本重封装R08平台产物，绑定当前接口文档和完整文件清单。"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\FPGA_Competition\w2b")
SOURCE = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r08"
TARGET = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261017_r03"
OLD_MANIFEST = SOURCE / "platform_delivery_manifest.json"
CURRENT_INTERFACE = ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_dir() or not TARGET.is_dir() or any(
    path.name != Path(__file__).name for path in TARGET.iterdir()
):
    raise SystemExit("源平台目录无效，或目标目录已含内容")

for source_path in sorted(SOURCE.iterdir()):
    if not source_path.is_file() or source_path.name == "delivery_manifest.json":
        continue
    target_name = (
        "prior_platform_delivery_manifest.json"
        if source_path.name == "platform_delivery_manifest.json"
        else source_path.name
    )
    shutil.copy2(source_path, TARGET / target_name)

old = json.loads(OLD_MANIFEST.read_text(encoding="utf-8"))
result = json.loads((TARGET / "result.json").read_text(encoding="utf-8"))
files = []
for path in sorted(TARGET.iterdir()):
    if not path.is_file() or path.name == "platform_delivery_manifest.json":
        continue
    relative = path.relative_to(ROOT).as_posix()
    if path.suffix.lower() in {".bit", ".xsa", ".dcp"} or path.name.startswith("ps7_init."):
        role = "artifact"
    elif path.suffix.lower() in {".rpt", ".log", ".tcldict"}:
        role = "log"
    elif path.name in {"result.json", "input_record.json", "repackage_record.json"}:
        role = "result"
    elif path.name == "prior_platform_delivery_manifest.json":
        role = "input"
    else:
        role = "source"
    row = {"path": relative, "sha256": sha256(path), "role": role}
    if path.suffix.lower() == ".dcp":
        row["keep_reason"] = "保留Vivado route checkpoint，以便复核原始实现产物。"
    if role == "input":
        row["keep_reason"] = "保留原R08平台清单字节，说明新封包没有改写原件。"
    files.append(row)

current_interface_sha = sha256(CURRENT_INTERFACE)
manifest = {
    "schema_version": 1,
    "stage": "2B",
    "task_id": "S2B-T14",
    "run_id": TARGET.name,
    "source_commit": result["source_commit"],
    "evidence_dir": TARGET.relative_to(ROOT).as_posix(),
    "interfaces": [{
        "name": "阶段2B物理接口",
        "version": "s2b-physical/1.0.0",
        "frozen": True,
        "path": CURRENT_INTERFACE.relative_to(ROOT).as_posix(),
        "sha256": current_interface_sha,
    }],
    "files": files,
    "checks": old["checks"],
    "limitations": old["limitations"] + [
        "本目录是R08原始产物的字节级副本及清单补充，不是新综合/实现/bitgen，也未改写R08原Run。",
        "新清单绑定当前s2b-physical/1.0.0接口文本并列全六个ps7_init文件；旧R08清单原件另存为prior_platform_delivery_manifest.json。",
        "该封包核验不证明板卡PCB/实装DDR、G3/G4/G5、109样本、1000任务或异常恢复。",
    ],
    "tool_versions": old.get("tool_versions", {}),
}
record = {
    "schema_version": 1,
    "kind": "s2b-platform-evidence-repackage/1.0.0",
    "status": "BYTE_IDENTICAL_REPACKAGE",
    "source_run": SOURCE.relative_to(ROOT).as_posix(),
    "source_manifest_sha256": sha256(OLD_MANIFEST),
    "source_commit": result["source_commit"],
    "copied_artifacts": {
        name: sha256(TARGET / name)
        for name in ("s2b_inference.xsa", "s2b_inference.bit")
    },
    "current_interface": {
        "path": CURRENT_INTERFACE.relative_to(ROOT).as_posix(),
        "sha256": current_interface_sha,
    },
    "limitations": [
        "只复制现有R08原件，不启动Vivado，不改变任何位流/XSA/源RTL。",
        "原R08目录及其delivery manifest不修改。",
        "Reviewer仍须独立核对本补充清单及当前接口兼容范围。",
    ],
}
(TARGET / "repackage_record.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
manifest["files"] = [
    {"path": row["path"], "sha256": sha256(ROOT / row["path"]), **{k: v for k, v in row.items() if k not in {"path", "sha256"}}}
    for row in files
]
manifest["files"].append({
    "path": (TARGET / "repackage_record.json").relative_to(ROOT).as_posix(),
    "sha256": sha256(TARGET / "repackage_record.json"),
    "role": "result",
})
(TARGET / "platform_delivery_manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({
    "run_id": TARGET.name,
    "source_commit": manifest["source_commit"],
    "file_count": len(manifest["files"]),
    "xsa_sha256": record["copied_artifacts"]["s2b_inference.xsa"],
    "bit_sha256": record["copied_artifacts"]["s2b_inference.bit"],
    "interface_sha256": current_interface_sha,
}, ensure_ascii=False))
