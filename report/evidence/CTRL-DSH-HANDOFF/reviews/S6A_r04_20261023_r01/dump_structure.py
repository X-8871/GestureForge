# -*- coding: utf-8 -*-
"""独立评审：转储被审 JSON 的结构骨架（只读）。"""
import json, sys, hashlib, os

ROOT = r"D:\codex-worktrees\w6"
J = os.path.join(ROOT, "docs", "stage6", "s6a_stage6_g0_behavior_v1.json")

with open(J, "rb") as f:
    raw = f.read()
print("SHA256(json) =", hashlib.sha256(raw).hexdigest())
print("bytes =", len(raw))

d = json.loads(raw.decode("utf-8"))
print("top-level keys =", list(d.keys()))
print()

for k, v in d.items():
    if isinstance(v, dict):
        print(f"[dict] {k}: {len(v)} keys -> {list(v.keys())[:40]}")
    elif isinstance(v, list):
        print(f"[list] {k}: {len(v)} items", end="")
        if v and isinstance(v[0], dict):
            print(f" | item keys: {list(v[0].keys())}")
        else:
            print(f" | first: {v[:6]}")
    else:
        print(f"[scalar] {k} = {v!r}")