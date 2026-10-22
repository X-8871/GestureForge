#!/usr/bin/env python3
"""自证工具换行逻辑的单元反例：只做换行选择，内容不同必须登记而不改写。"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"D:\FPGA_Competition\tmp\review\S6A_r07_20261023_r01\repo3")
spec = importlib.util.spec_from_file_location("esp", REPO / "verification/export_selfproof.py")
esp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(esp)

work = Path(r"D:\FPGA_Competition\tmp\review\S6A_r07_20261023_r01\unit")
shutil.rmtree(work, ignore_errors=True)
tree = work / "tree"
tree.mkdir(parents=True)
orig_c = b"line1\r\nline2\r\nline3\r\n"
bad_c = b"line1\r\nlineX\r\nline3\r\n"
declared = {
    "a.txt": hashlib.sha256(b"a1\r\na2\r\n").hexdigest(),       # 声明 CRLF
    "b.txt": hashlib.sha256(b"b1\nb2\n").hexdigest(),           # 声明 LF
    "c.txt": hashlib.sha256(orig_c).hexdigest(),                # 内容将被改一字节
}
manifest = {"files": [{"path": k, "sha256": v} for k, v in declared.items()]}
(tree / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
(tree / "a.txt").write_bytes(b"a1\na2\n")        # 与声明仅换行不同
(tree / "b.txt").write_bytes(b"b1\r\nb2\r\n")    # 与声明仅换行不同
(tree / "c.txt").write_bytes(bad_c)              # 内容真的不同（非换行）
before = {p.name: p.read_bytes() for p in tree.iterdir() if p.suffix == ".txt"}

res = esp.align_by_manifest_hashes(tree, "manifest.json")
after = {p.name: p.read_bytes() for p in tree.iterdir() if p.suffix == ".txt"}
print("[unit-A align_by_manifest_hashes]", json.dumps(res, ensure_ascii=False))
print("  a.txt ->", after["a.txt"], "suffix", after["a.txt"][-4:])
print("  b.txt ->", after["b.txt"], "suffix", after["b.txt"][-4:])
print("  c.txt 未被改写:", after["c.txt"] == before["c.txt"], "| 内容:", after["c.txt"])
print("  c.txt 是否被登记为 unresolved:", "c.txt" in res["unresolved"])
assert after["a.txt"] == b"a1\r\na2\r\n", "a.txt 应被选为 CRLF"
assert after["b.txt"] == b"b1\nb2\n", "b.txt 应被选为 LF"
assert after["c.txt"] == bad_c, "内容不同的文件不得被改写"
assert res["aligned"] == 2 and res["unresolved"] == ["c.txt"]

# normalize_line_endings：源树只差换行 → 采用源字节；内容不同 → 登记不改写
src = work / "source"
src.mkdir(parents=True)
shutil.copytree(tree, src / "tree", dirs_exist_ok=True)
t2 = src / "tree"
(t2 / "d.txt").write_bytes(b"d1\nd2\n")
(src / "d.txt").write_bytes(b"d1\r\nd2\r\n")          # 仅换行不同
(t2 / "e.txt").write_bytes(b"e1\ne2\n")
(src / "e.txt").write_bytes(b"e1\neX\n")              # 内容不同
res2 = esp.normalize_line_endings(t2, src)
print("[unit-B normalize_line_endings]", json.dumps(res2, ensure_ascii=False))
print("  d.txt ->", (t2 / "d.txt").read_bytes())
print("  e.txt 未被改写:", (t2 / "e.txt").read_bytes() == b"e1\ne2\n")
print("  e.txt 已登记 content_differs:", "e.txt" in res2["content_differs"])
assert (t2 / "d.txt").read_bytes() == b"d1\r\nd2\r\n"
assert (t2 / "e.txt").read_bytes() == b"e1\ne2\n"
assert "e.txt" in res2["content_differs"]
print("UNIT_OK：只做换行选择；内容不同的文件一律登记、绝不改写")