#!/usr/bin/env python3
"""轻量复跑25个既有平台反例，并补旧S8版本拒绝；不编译RTL。"""
import copy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"verification"))
import test_s2b_backend_coordinates_rtl as support


def main():
    """保持原反例函数及判据，新增旧0.1.8输入只用于版本兼容回归。"""
    checker=support.load_checker();bindings=checker.check_static(ROOT)
    work=WORK/"platform_negative_probe";work.mkdir()
    records=support.checker_negatives(checker,work,bindings)
    assert len(records)==25
    path=work/"checker_fixture/board/s2b_inference_platform.json"
    profile=json.loads((ROOT/"board/s2b_inference_platform.json").read_text(encoding="utf-8"))
    profile=copy.deepcopy(profile);profile["version"]="s2b-inference-platform/0.1.8"
    path.write_text(json.dumps(profile,ensure_ascii=False),encoding="utf-8")
    try:checker.check_static(work/"checker_fixture")
    except ValueError as exc:records.append({"name":"旧S8 profile0.1.8","status":"REJECTED","reason":str(exc)})
    else:raise ValueError("旧S8 profile被错误接受")
    report={"status":"PASS_PLATFORM_NEGATIVES_ONLY","existing_count":25,"added_old_s8_profile":1,"total":26,
            "records":records,"source_sha256":bindings,"helper_sha256":support.sha(Path(__file__))}
    print(json.dumps(report,ensure_ascii=False))
    return 0


if __name__=="__main__":raise SystemExit(main())
