"""保留初始清单schema失败原件，另建修正包装；不重跑主测试或硬件。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).absolute().parents[4]
RUN = Path(__file__).absolute().parent
data = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
# 已执行且返回非零的检查必须记FAIL；BLOCKED的exit_code按schema只能为null。
data["checks"][1]["status"] = "FAIL"
data["limitations"].append("初始delivery_manifest.json把已执行inputs的rc2与BLOCKED并列，包装schema失败；原件保留。本修正版明确FAIL/rc2，仅表示候选依赖检查受阻。")
data["files"] = []
for path in sorted(RUN.iterdir()):
    data["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                          "role": "source" if path.suffix == ".py" else ("log" if path.suffix == ".log" else "result")})
for name in ("report/evidence/S2B-T16/jtag_offline_20261011_r02/delivery_manifest.json", "verification/check_stage_delivery.py"):
    data["files"].append({"path": name, "sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), "role": "input"})
with (RUN / "packaging_delivery_manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(data, stream, ensure_ascii=False, indent=2); stream.write("\n")
