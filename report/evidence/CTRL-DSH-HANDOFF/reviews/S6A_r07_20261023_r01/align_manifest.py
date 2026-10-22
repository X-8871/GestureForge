"""把工作树的清单声明文件对齐到声明哈希（仅换行口径选择）；内容不同即登记不改写。

用法：python align_manifest.py <repo> <manifest-rel-path>
"""
import hashlib
import json
import os
import sys

repo = sys.argv[1]
manifest_rel = sys.argv[2]
path = os.path.join(repo, manifest_rel)
if not os.path.isfile(path):
    print(json.dumps({"error": "manifest missing", "path": path}, ensure_ascii=False))
    raise SystemExit(2)
manifest = json.load(open(path, encoding="utf-8"))
ok = 0
aligned = []
unresolved = []
missing = []
for item in manifest.get("files", []):
    rel = str(item["path"]).replace("\\", "/")
    want = str(item["sha256"]).lower()
    target = os.path.join(repo, rel)
    if not os.path.isfile(target):
        missing.append(rel)
        continue
    data = open(target, "rb").read()
    if hashlib.sha256(data).hexdigest() == want:
        ok += 1
        continue
    normalized = data.replace(b"\r\n", b"\n")
    for candidate in (normalized, normalized.replace(b"\n", b"\r\n")):
        if hashlib.sha256(candidate).hexdigest() == want:
            open(target, "wb").write(candidate)
            aligned.append(rel)
            break
    else:
        unresolved.append(rel)
print(json.dumps({"already_ok": ok, "aligned": aligned, "unresolved": unresolved,
                  "missing": missing}, ensure_ascii=False, indent=2))