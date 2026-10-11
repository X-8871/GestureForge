import json,sys,time
from pathlib import Path
b=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"));o=Path(sys.argv[2]);(o/"guard").mkdir();
(o/"guard"/"samples.jsonl").write_text(json.dumps(dict(index=0,members=[b],alerts=[],uncertain=[]))+"\n",encoding="utf-8");time.sleep(10.2);
(o/"guard"/"guard_receipt.json").write_text(json.dumps(dict(status="SELFTEST_TERMINAL")),encoding="utf-8");sys.exit(7)
