"""S5-T01 注入计划离线校验器（无硬件）：把“脚本化注入的检测结果”按 S5-A 契约校验并预演几何。

只读：读计划 JSON 与冻结参考实现，不连接板卡、不写寄存器。
校验：契约必需字段、state 合法性、零框语义、≤15 框、类别顺序/名称一致、分数区间、正面积、
      并经 `original_norm_to_display_px` + `border_pixel_sets` 预演显示像素（不绘制）。

退出码：0=全部合法；1=存在不合法记录；2=输入/环境错误。
用法：`python -B scripts/stage5_t01/validate_injection_plan.py --plan docs/stage5/s5t01_injection_plan_example.json`
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
import verification.s5_display_geometry_reference as R  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="S5-T01 注入计划离线校验（无硬件）")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = parser.parse_args()

    path = pathlib.Path(args.plan)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.exists():
        print(f"[plan] 计划文件不存在：{path}")
        return 2
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[plan] JSON 解析失败：{exc}")
        return 2

    records = plan.get("records")
    if not isinstance(records, list) or not records:
        print("[plan] 计划必须含非空 records 数组")
        return 2

    results, failures = [], 0
    for index, record in enumerate(records):
        problems = R.validate_result_record(record)
        detail = {"index": index, "frame_id": record.get("frame_id") if isinstance(record, dict) else None,
                  "problems": problems}
        geometry = record.get("geometry") if isinstance(record, dict) else None
        if not problems and isinstance(geometry, dict):
            width, height = int(geometry["width"]), int(geometry["height"])
            geom = R.letterbox_geometry(width, height)
            detail["letterbox"] = {k: geom[k] for k in ("new_width", "new_height", "offset_x", "offset_y")}
            if geom["new_width"] <= 1 or geom["new_height"] <= 1 or width <= 1 or height <= 1:
                problems.append("退化几何：逆映射不适用，必须直接使用阶段4 原图坐标字段（本计划走契约 xyxy 路径，故仅提示）")
                detail["problems"] = problems
            drawn = []
            for det in record.get("detections", []):
                clipped = R.clip_unit_box(det["xyxy"])
                if clipped["zero_area"]:
                    drawn.append({"class_id": det["class_id"], "zero_area": True, "pixels": 0})
                    continue
                px = R.original_norm_to_display_px(clipped["xyxy"], width, height)
                pixels = R.border_pixel_sets(px["x1"], px["y1"], px["x2"], px["y2"],
                                             R.DISPLAY_LINE_WIDTH_PX, width, height)
                drawn.append({"class_id": det["class_id"], "zero_area": False,
                              "px": px, "border_pixels": len(pixels)})
            detail["display_preview"] = drawn
        if problems:
            failures += 1
        results.append(detail)

    summary = {
        "plan": str(path),
        "display_semantics": plan.get("display_semantics"),
        "records": len(records),
        "failed_records": failures,
        "total_boxes": sum(len(r.get("detections", [])) for r in records if isinstance(r, dict)),
        "status": "PASS" if failures == 0 else "FAIL",
    }
    if args.json:
        print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2))
    else:
        print(f"[plan] {summary['status']} records={summary['records']} boxes={summary['total_boxes']} "
              f"failed={failures} semantics={summary['display_semantics']!r}")
        for item in results:
            mark = "OK " if not item["problems"] else "FAIL"
            print(f"  {mark} #{item['index']} frame_id={item['frame_id']} "
                  f"boxes={len(item.get('display_preview', []))} problems={item['problems']}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())