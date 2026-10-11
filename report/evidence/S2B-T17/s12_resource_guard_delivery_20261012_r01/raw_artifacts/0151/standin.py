"""仅导入自测使用的自有轻量替身；生产CLI没有替身选择入口。"""
import json
from pathlib import Path
import sys
import time

binding = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = Path(sys.argv[2]) / "guard"
out.mkdir()
with (out / "samples.jsonl").open("x", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(dict(index=0, members=[binding], alerts=[], uncertain=[]), ensure_ascii=False)+"\n")
time.sleep(10.6)
with (out / "guard_receipt.json").open("x", encoding="utf-8") as f:
    json.dump(dict(status="BLOCKED", reason="OWNED_STANDIN_TERMINAL", fixture=True), f)
raise SystemExit(7)
