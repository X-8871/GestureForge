#!/usr/bin/env python3
"""死常量检查（S6-B claim S6B-C3 的真实可执行命令）：定义后从未使用的常量必须为 0。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ("src/stage6/s6_actions.py", "src/stage6/s6_core.py")


def main() -> int:
    bad: list[str] = []
    for rel in TARGETS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for name in sorted(set(re.findall(r"^([A-Z][A-Z0-9_]{2,})\s*=", text, flags=re.MULTILINE))):
            if len(re.findall(rf"\b{name}\b", text)) <= 1:
                bad.append(f"{rel}:{name}")
    print(f"unused={bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())