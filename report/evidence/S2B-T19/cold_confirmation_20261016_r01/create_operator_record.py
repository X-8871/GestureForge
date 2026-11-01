"""将本轮真实用户确认绑定为人工冷启动依据，不生成硬件通过结论。"""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
source = RUN / "user_message.json"
raw = source.read_bytes()
message = json.loads(raw.decode("utf-8"))
assert message["raw_user_text"] == "已重启，10s"
record = {
    "kind": "external-por-operator-confirmation/1.0.0", "operator": "Wong",
    "time_utc8": message["confirmation_recorded_at_utc8"],
    "statement": "Wong回复“已重启，10s”，作为对板卡断电约10秒后重新上电请求的确认；time_utc8是确认记录时间，未测POR沿或确切上电时刻。",
    "source": {"path": str(source), "sha256": hashlib.sha256(raw).hexdigest()},
}
with (RUN / "operator_confirmation.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(hashlib.sha256((RUN / "operator_confirmation.json").read_bytes()).hexdigest())
