import json
from pathlib import Path

# 只显示本次实际资源窗口的结构，不展开历史自测副本。
e = Path.cwd() / "report/evidence/S2B-T17/s10_platform_20261012_r01"
index = json.loads((e / "resource_monitoring/resource_index.json").read_text(encoding="utf-8"))
for row in index["files"]:
    if "/raw/065" in row["saved_path"] or "/raw/066" in row["saved_path"] or "/raw/067" in row["saved_path"]:
        print(row["path"], row["saved_path"])
        if row["path"].endswith("guard_receipt.json") or row["path"].endswith("supervisor_receipt.json") or row["path"].endswith("tool.json"):
            value = json.loads((Path.cwd() / row["saved_path"]).read_text(encoding="utf-8"))
            for key, x in value.items():
                if isinstance(x, list) and len(x) > 8:
                    print(key, "COUNT", len(x))
                else:
                    print(key, json.dumps(x, ensure_ascii=False)[:3500])
for name in ["owned_process_closed_r01.tool.json", "s10_launchResource_actual.tool.json", "s10_guard_failure_readback_closed.tool.json", "s10_probes_actual.tool.json", "s10_wait_actual.tool.json"]:
    path = e / "mcp_closed" / name
    if path.is_file():
        print(name, path.read_text(encoding="utf-8")[:3800])
