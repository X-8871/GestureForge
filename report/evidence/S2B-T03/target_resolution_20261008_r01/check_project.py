"""核对阶段2B工程仅校正用户确认的三个器件字段。"""
from __future__ import annotations
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

BASELINE = "3375cb4d0d52854e85142851dda03de05a0291c0"
RELATIVE_XPR = "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr"
EXPECTED_PART = "xa7z020clg400-1I"
PHOTO_SHA256 = "d062f1268b5f6eaafc78eb0b66cbc21e61d2bece65812068aef6e4a2f7778549"

def main() -> None:
    """从实际Git基线和工作文件验证XML语义与身份照片绑定。"""
    root = Path(__file__).resolve().parents[4]
    xpr = root / RELATIVE_XPR
    photo = Path(__file__).resolve().parent / "chip_identity.jpg"
    if not xpr.is_file() or not photo.is_file():
        raise RuntimeError("工程或身份照片缺失")
    baseline = subprocess.run(
        ["git", "show", f"{BASELINE}:{RELATIVE_XPR}"],
        cwd=root, check=True, capture_output=True,
    ).stdout
    actual_bytes = xpr.read_bytes()
    expected = ET.fromstring(baseline)
    actual = ET.fromstring(actual_bytes)
    fields = expected.findall("./Configuration/Option[@Name='Part']")
    fields += expected.findall("./Runs/Run")
    part_fields = [node for node in fields if node.get("Name") == "Part" or node.get("Id") in ("synth_1", "impl_1")]
    if len(part_fields) != 3:
        raise RuntimeError("基线未找到预期的三个器件字段")
    for node in part_fields:
        key = "Val" if node.get("Name") == "Part" else "Part"
        if node.get(key) != "xc7z020clg400-2":
            raise RuntimeError("基线器件字段与已审资料不符")
        node.set(key, EXPECTED_PART)
    if ET.tostring(actual) != ET.tostring(expected):
        raise RuntimeError("实际XML含有器件字段以外的语义差异")
    actual_parts = [node.get("Val") for node in actual.findall("./Configuration/Option[@Name='Part']")]
    actual_parts += [node.get("Part") for node in actual.findall("./Runs/Run") if node.get("Id") in ("synth_1", "impl_1")]
    if actual_parts != [EXPECTED_PART] * 3:
        raise RuntimeError("实际器件字段不一致")
    actual_photo_sha = hashlib.sha256(photo.read_bytes()).hexdigest()
    if actual_photo_sha != PHOTO_SHA256:
        raise RuntimeError("身份照片原始字节与用户附件不一致")
    print(json.dumps({
        "status": "PASS_TARGET_ONLY_XML_AND_PHOTO_BINDING",
        "baseline": BASELINE, "xpr": RELATIVE_XPR,
        "xpr_sha256": hashlib.sha256(actual_bytes).hexdigest(),
        "part_fields": actual_parts, "changed_semantic_field_count": 3,
        "photo_sha256": actual_photo_sha,
        "limitations": ["未创建或验证PS平台、整网部署、时序或板上功能。"],
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
