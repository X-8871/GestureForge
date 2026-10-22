"""S5-A 包装核验：独立审查两轮结论必须与记录一致（真实退出码 0）。

第 1 轮：`s5r01_20261022_r01/independent_review.json` → verdict 必须为 CHANGES_REQUIRED；
第 2 轮：`s5r01_20261022_r02/closure_review.json` → closure verdict 必须为 PASS。
退出码：0=一致；1=不一致或缺文件；2=JSON 不可解析。
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ROUND1 = REPO_ROOT / "report/evidence/S5-CTRL/S5-R01/s5r01_20261022_r01/independent_review.json"
ROUND2 = REPO_ROOT / "report/evidence/S5-CTRL/S5-R01/s5r01_20261022_r02/closure_review.json"

_VERDICT_KEYS = ("verdict", "closure_verdict", "closureVerdict", "overall_verdict", "result")


def _load(path: pathlib.Path) -> dict:
    if not path.exists():
        print(f"[verdicts] 缺失：{path}")
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _extract(record: dict) -> str | None:
    for key in _VERDICT_KEYS:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().upper()
    # 兜底：在嵌套结构里找第一个类似的 verdict 字符串
    for value in record.values():
        if isinstance(value, dict):
            found = _extract(value)
            if found:
                return found
    return None


def main() -> int:
    try:
        round1, round2 = _load(ROUND1), _load(ROUND2)
    except FileNotFoundError:
        return 1
    except json.JSONDecodeError as exc:
        print(f"[verdicts] JSON 解析失败：{exc}")
        return 2

    verdict1, verdict2 = _extract(round1), _extract(round2)
    print(f"[verdicts] round1 verdict={verdict1!r} (期望 CHANGES_REQUIRED)")
    print(f"[verdicts] round2 verdict={verdict2!r} (期望 PASS / CLOSED)")
    ok1 = verdict1 == "CHANGES_REQUIRED"
    ok2 = verdict2 in {"PASS", "CLOSED", "PASS_CLOSED"}
    if not (ok1 and ok2):
        print("[verdicts] 不一致 -> exit 1")
        return 1
    print("[verdicts] 一致 -> exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())