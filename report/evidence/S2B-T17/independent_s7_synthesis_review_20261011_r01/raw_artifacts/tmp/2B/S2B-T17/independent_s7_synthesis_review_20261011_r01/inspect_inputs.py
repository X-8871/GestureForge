import json
import sys
from pathlib import Path

# 限制展示数量，避免完整历史和大型清单占据审查上下文。
def compact(value):
    if isinstance(value, dict):
        if len(value) > 40:
            return {"键数量": len(value), "前四键": list(value)[:4]}
        return {k: compact(v) for k, v in value.items()}
    if isinstance(value, list):
        if len(value) > 8:
            return {"数量": len(value), "前两项": [compact(v) for v in value[:2]]}
        return [compact(v) for v in value]
    return value

for name in sys.argv[1:]:
    path = Path(name)
    print("路径：", name)
    print(json.dumps(compact(json.loads(path.read_text(encoding="utf-8"))), ensure_ascii=False, indent=2))
