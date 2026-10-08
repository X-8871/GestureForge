"""核对最新XC/-2候选及被替代XA/-1I候选的原始绑定。"""
from __future__ import annotations

import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

BASELINE = "3375cb4d0d52854e85142851dda03de05a0291c0"
XPR = "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr"
EXPECTED_PART = "xc7z020clg400-2"
PHOTO_SHA256 = "d062f1268b5f6eaafc78eb0b66cbc21e61d2bece65812068aef6e4a2f7778549"


def main() -> None:
    """仅确认工程目标与证据完整性，不判定实物芯片身份。"""
    here = Path(__file__).resolve().parent
    root = here.parents[3]
    current = (root / XPR).read_bytes()
    baseline = subprocess.run(
        ["git", "show", f"{BASELINE}:{XPR}"],
        cwd=root, capture_output=True, check=True,
    ).stdout
    actual_xml = ET.fromstring(current)
    if ET.tostring(actual_xml) != ET.tostring(ET.fromstring(baseline)):
        raise RuntimeError("最新XC候选XML语义与原始基线不同")
    parts = [n.get("Val") for n in actual_xml.findall("./Configuration/Option[@Name='Part']")]
    parts += [n.get("Part") for n in actual_xml.findall("./Runs/Run") if n.get("Id") in ("synth_1", "impl_1")]
    if parts != [EXPECTED_PART] * 3:
        raise RuntimeError("三个候选目标字段不一致")
    old_run = here.parent / "target_resolution_20261008_r01"
    manifest = json.loads((old_run / "delivery_manifest.json").read_text(encoding="utf-8"))
    replacements = {
        XPR: here / "prior_requested_1I.xpr",
        "board/README.md": here / "prior_board_readme.md",
    }
    replayed = []
    for binding in manifest["files"]:
        path = replacements.get(binding["path"], root / binding["path"])
        if not path.is_file():
            raise RuntimeError(f"历史候选依赖缺失：{binding['path']}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != binding["sha256"]:
            raise RuntimeError(f"历史候选原始哈希不一致：{binding['path']}")
        replayed.append({"declared_path": binding["path"], "actual_path": path.relative_to(root).as_posix(), "sha256": digest})
    if hashlib.sha256((old_run / "chip_identity.jpg").read_bytes()).hexdigest() != PHOTO_SHA256:
        raise RuntimeError("照片原始字节与用户附件不一致")
    old_xml = ET.fromstring((here / "prior_requested_1I.xpr").read_bytes())
    old_parts = [n.get("Val") for n in old_xml.findall("./Configuration/Option[@Name='Part']")]
    old_parts += [n.get("Part") for n in old_xml.findall("./Runs/Run") if n.get("Id") in ("synth_1", "impl_1")]
    if old_parts != ["xa7z020clg400-1I"] * 3:
        raise RuntimeError("旧候选快照不是原来的XA/-1I候选")
    print(json.dumps({
        "status": "PASS_REQUESTED_XC2_XML_AND_HISTORICAL_REPLAY",
        "baseline": BASELINE, "xpr_sha256": hashlib.sha256(current).hexdigest(),
        "part_fields": parts, "changed_semantic_field_count_from_baseline": 0,
        "photo_sha256": PHOTO_SHA256, "historical_replayed_bindings": replayed,
        "limitations": ["历史r01仅通过指定旧源码快照重放，不能直接作为当前交付的inputs。", "照片XA与厂商确认XC冲突仍未解决；此检查不证明实物型号、速度等级或板上功能。"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
