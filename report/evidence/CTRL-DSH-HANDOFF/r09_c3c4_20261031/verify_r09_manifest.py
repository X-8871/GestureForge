import json, subprocess, sys, pathlib
W6 = r"D:\codex-worktrees\w6"
man = pathlib.Path(sys.argv[1])
m = json.loads(man.read_text(encoding="utf-8"))
bad = 0
for it in m["files"]:
    p, c, blob = it["path"], it["commit"], it["blob"]
    try:
        cur = subprocess.run(["git","-C",W6,"rev-parse",f"{c}:{p}"], capture_output=True, text=True, check=True).stdout.strip()
        size = int(subprocess.run(["git","-C",W6,"cat-file","-s",blob], capture_output=True, text=True, check=True).stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"FAIL(missing) {p} @ {c}"); bad += 1; continue
    if cur != blob or size != it["bytes"]:
        print(f"FAIL(mismatch) {p}: blob {blob[:10]}->{cur[:10]}, bytes {it['bytes']}->{size}"); bad += 1
print(f"checked={len(m['files'])} mismatch={bad}")
sys.exit(0 if bad == 0 else 1)
