"""只复制完整、有效的 BASIC 签名块到用户私有临时目录。"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path


original = Path(r"C:\Users\22061\Downloads\Xilinx.lic")
private_parent = Path(r"C:\Users\22061\AppData\Local\Temp")
private_dir = private_parent / "fpga_s2a_basic_20261008_r03"
private_file = private_dir / "Xilinx_Basic.lic"
if not original.is_file() or not private_parent.is_dir():
    raise RuntimeError("已确认的许可文件或私有临时父目录不存在")
if private_dir.exists():
    raise RuntimeError("本次私有临时目录已存在，拒绝覆盖")

raw = original.read_bytes()
original_hash = hashlib.sha256(raw).digest()
lines = raw.splitlines(keepends=True)
allowed = {b"Vivado_Basic_Package", b"Vivado_Synthesis", b"Vivado_Implementation", b"Vivado_Simulation"}
blocks: list[bytes] = []
metadata: list[dict[str, str]] = []
index = 0
while index < len(lines):
    first = lines[index]
    tokens = first.split()
    if tokens and tokens[0] in {b"SERVER", b"USE_SERVER"}:
        raise RuntimeError("发现服务器许可指令，本次仅处理用户提供的本机 BASIC 许可")
    if not tokens or tokens[0] not in {b"INCREMENT", b"FEATURE"}:
        index += 1
        continue
    block_lines = [first]
    index += 1
    while block_lines[-1].rstrip(b"\r\n").rstrip().endswith(b"\\"):
        if index >= len(lines):
            raise RuntimeError("许可签名块续行不完整")
        block_lines.append(lines[index])
        index += 1
    if len(tokens) < 5 or tokens[1] not in allowed:
        continue
    expiry = tokens[4].decode("ascii")
    if expiry != "permanent" and datetime.strptime(expiry, "%d-%b-%Y").date() < date.today():
        continue
    block = b"".join(block_lines)
    # 不解释厂商加密字段，只复制完整原始条目；真正有效性由 Vivado 检出确认。
    blocks.append(block)
    metadata.append({"feature": tokens[1].decode("ascii"), "expiry": expiry})

selected = {item["feature"] for item in metadata}
required = {"Vivado_Basic_Package", "Vivado_Synthesis", "Vivado_Implementation"}
if not required.issubset(selected) or len(selected) != len(metadata):
    raise RuntimeError("完整有效 BASIC 条目不唯一，停止创建私有副本")
result = b"".join(blocks)
private_dir.mkdir()
with private_file.open("xb") as stream:
    stream.write(result)
if private_file.read_bytes() != result or hashlib.sha256(original.read_bytes()).digest() != original_hash:
    raise RuntimeError("原件或副本字节校验失败")
print(json.dumps({"status": "BASIC_SIGNED_BLOCK_COPY_CREATED", "original_unchanged": True,
                  "private_file": str(private_file), "features": metadata,
                  "license_keys_printed_or_stored_in_repository": False}, ensure_ascii=False))
