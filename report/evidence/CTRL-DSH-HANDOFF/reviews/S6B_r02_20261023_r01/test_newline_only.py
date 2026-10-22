#!/usr/bin/env python3
"""S6-B r02 复审：export_selfproof 的“只选换行口径、不改内容”反例核验。

直接调用被测函数（只读导入），在隔离临时目录构造三组反例：
  1) 仅换行不同（CRLF vs LF）→ 允许对齐（这就是它做的唯一“修正”）；
  2) 一个非换行字节不同（相对清单哈希）→ 必须登记 unresolved，且**字节不变**；
  3) 一个非换行字节不同（相对工作区源文件）→ 必须登记 content_differs，且**字节不变**。
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

W6 = Path(r"D:\codex-worktrees\w6")
sys.path.insert(0, str(W6 / "verification"))
import export_selfproof as esp  # noqa: E402

TMP = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\selftmp_align")
if TMP.exists():
    import shutil
    shutil.rmtree(TMP)
TMP.mkdir(parents=True)

# ---------------------------------------------------------------- 反例 1/2：清单哈希对齐
tree = TMP / "tree"
(tree / "sub").mkdir(parents=True)
(tree / "sub" / "lf_only.txt").write_bytes(b"alpha\nbeta\n")          # 与清单 LF 哈希一致
(tree / "sub" / "crlf_only.txt").write_bytes(b"alpha\r\nbeta\r\n")    # 仅换行不同
(tree / "sub" / "one_byte_diff.txt").write_bytes(b"alpha\r\nbetA\r\n")  # 非换行差异 1 字节
manifest = {
    "files": [
        {"path": "sub/lf_only.txt", "sha256": hashlib.sha256(b"alpha\nbeta\n").hexdigest()},
        {"path": "sub/crlf_only.txt", "sha256": hashlib.sha256(b"alpha\nbeta\n").hexdigest()},
        {"path": "sub/one_byte_diff.txt", "sha256": hashlib.sha256(b"alpha\nbeta\n").hexdigest()},
    ]
}
(tree / "m.json").write_text(json.dumps(manifest), encoding="utf-8")
before = (tree / "sub" / "one_byte_diff.txt").read_bytes()
result = esp.align_by_manifest_hashes(tree, "m.json")
after = (tree / "sub" / "one_byte_diff.txt").read_bytes()
print("反例1/2 align_by_manifest_hashes ->", result)
print("  crlf_only 是否被按换行对齐:", (tree / "sub" / "crlf_only.txt").read_bytes() == b"alpha\nbeta\n")
print("  非换行差异文件是否被改动:", before != after, "| 仍登记为 unresolved:",
      "sub/one_byte_diff.txt" in result["unresolved"])

# ---------------------------------------------------------------- 反例 3：工作区字节替换
tree2 = TMP / "tree2"
tree2.mkdir()
source = TMP / "source"
source.mkdir()
(tree2 / "a.py").write_bytes(b"line1\r\nline2\r\n")     # 导出（提交）字节
(source / "a.py").write_bytes(b"line1\nline2\n")        # 工作区字节：仅换行不同
(tree2 / "b.py").write_bytes(b"line1\r\nline3\r\n")     # 非换行差异
(source / "b.py").write_bytes(b"line1\r\nline2\r\n")
r2 = esp.normalize_line_endings(tree2, source)
print("反例3 normalize_line_endings ->", r2)
print("  a.py 是否按换行对齐为工作区字节:", (tree2 / "a.py").read_bytes() == b"line1\nline2\n")
print("  b.py 是否保留原字节（未被内容修正）:", (tree2 / "b.py").read_bytes() == b"line1\r\nline3\r\n")