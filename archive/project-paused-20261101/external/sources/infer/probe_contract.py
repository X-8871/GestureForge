r"""只读探针：打印 S4-B 共享输入/结果契约与地址图的 region/result 结构（ASCII 输出）。"""
from __future__ import annotations

import json
from pathlib import Path

DOCS = Path(r"D:\codex-worktrees\w4\docs\stage4")
W = Path(r"D:\codex-worktrees\w4")


def dump(path: Path, keys_filter=None, max_chars=4000) -> None:
    print("=" * 20, path.name, f"({path.stat().st_size} B)")
    d = json.loads(path.read_text(encoding="utf-8"))
    print("top keys:", list(d.keys()))
    for k, v in d.items():
        if keys_filter and not any(f in k for f in keys_filter):
            continue
        s = json.dumps(v, ensure_ascii=True, indent=1)
        print(f"--- {k} (len={len(s)})")
        print(s[:max_chars])


for name in ("s4b_shared_input_result_contract.json", "S4B_stage4_address_map.json"):
    dump(DOCS / name, keys_filter=("region", "result", "buffer", "box", "detect", "owner", "interface"))
    print()

# 2B frozen app 的 response 结构（结构定义源码片段）
src = Path(r"D:\FPGA_Competition\w2b\vitis\s2b_inference_app.c")
print("=" * 20, "2B app response/meta struct snippets")
lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
for i, ln in enumerate(lines, 1):
    if any(t in ln for t in ("typedef struct", "META_BYTES", "put32", "put_double", "send_response",
                             "response[", "box->", "classes", "class_id")):
        lo = max(1, i - 2)
        print(f"L{i}: {ln.strip()}")