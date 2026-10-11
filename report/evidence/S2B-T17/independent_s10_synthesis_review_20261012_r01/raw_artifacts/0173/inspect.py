import json
from pathlib import Path

# 只显示当前冻结入口的简短结构，避免展开674副本或全量history正文。
root = Path.cwd()
base = root / "report/evidence/S2B-T17/s10_platform_20261012_r01"
for name in ["s10_delivery_manifest_r03.json", "resource_monitoring/resource_index.json", "s10_mcp_binding.json", "s10_native_mapping.json", "s10_xsa_comparison.json"]:
    value = json.loads((base / name).read_text(encoding="utf-8"))
    print(name)
    for key, entry in value.items():
        if isinstance(entry, list) and len(entry) > 10:
            print(key, "count", len(entry), "first", str(entry[0])[:450])
        elif key == "paired_calls":
            print(key, [{k: x.get(k) for k in ("label", "client_timeout", "client_exit_code")} for x in entry])
        else:
            print(key, json.dumps(entry, ensure_ascii=False)[:6500])
print("root native", [x.name for x in (base / "root_native_closed").iterdir()])
print("resource top", [x.name for x in (base / "resource_monitoring").iterdir()])
index = json.loads((base / "resource_monitoring/resource_index.json").read_text(encoding="utf-8"))
for entry in index["files"]:
    if "s10_guard_actual" in entry["path"] or "s10_supervisor_actual" in entry["path"] or ("s10_root_run_20261012_r01/" in entry["path"] and ("Resource" in entry["path"] or "resource" in entry["path"] or "closed" in entry["path"])):
        print("selected_resource", entry["path"], entry["saved_path"])
