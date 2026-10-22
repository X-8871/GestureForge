import subprocess, json, sys
sys.stdout.reconfigure(encoding="utf-8")
b = subprocess.run(["git", "-C", r"D:\codex-worktrees\w4", "show",
                    "73c3dad:docs/stage4/s4a_stage4_g0_fields.json"], capture_output=True).stdout
d = json.loads(b)
found = []
def walk(o, p=""):
    if isinstance(o, dict):
        if o.get("name") == "source_order":
            found.append((p, o))
        for k, v in o.items():
            walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, p + f"/{i}")
walk(d)
for path, v in found:
    print("PATH", path)
    print(json.dumps(v, ensure_ascii=False, indent=2))
