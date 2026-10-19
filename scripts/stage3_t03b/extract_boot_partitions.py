"""从厂商官方 BOOT.BIN 中按 bootgen 头部表声明的偏移/长度提取分区，用于板卡硬件连通性检查。
只读输入官方原件；输出写入本轮隔离目录；不修改厂商文件。
校验：分区数据必须以 ELF magic 开头，且声明的长度必须落在文件内。
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

BOOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
# bootgen -read 的输出（2026-10-20 实测）：
# fsbl.elf          unencrypted_length 0x00007002
# design_1_wrapper.bit unencrypted_length 0x000f6ec0
# vdma_hdmi.elf     unencrypted_length 0x0005c002
PARTITIONS = [
    ("fsbl.elf", 0x7002, True),
    ("design_1_wrapper.bit", 0xF6EC0, False),
    ("vdma_hdmi.elf", 0x5C002, True),
]

data = BOOT.read_bytes()
OUT.mkdir(parents=True, exist_ok=True)
report = {
    "source": str(BOOT),
    "source_size": len(data),
    "source_sha256": hashlib.sha256(data).hexdigest(),
    "extracted": [],
}

# 定位所有 ELF magic
elf_offsets = []
start = 0
while True:
    i = data.find(b"\x7fELF", start)
    if i < 0:
        break
    elf_offsets.append(i)
    start = i + 4

report["elf_magic_offsets"] = [hex(x) for x in elf_offsets]

for name, length, is_elf in PARTITIONS:
    chosen = None
    if is_elf:
        # 选择“偏移 + 声明长度”最自洽的候选：ELF 头内的 e_ehsize/节表必须落在区间内
        for off in elf_offsets:
            if off + length > len(data):
                continue
            blob = data[off:off + length]
            try:
                (_, _, _, _, _, _, _, e_shoff, _, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from(
                    "<16sHHIIIIIHHHHHH", blob, 0)
            except struct.error:
                continue
            if e_shoff + e_shnum * e_shentsize <= len(blob) and e_shstrndx < e_shnum:
                chosen = off
                break
    else:
        # bitstream 不含 ELF magic：用 boot header 中的 fsbl_length 之后的连续区域定位
        magic_idx = data.find(b"\xaa\x99\x55\x66")
        candidates = []
        pos = 0
        while True:
            i = data.find(b"\xff\xff\xff\xff\xaa\x99\x55\x66", pos)
            if i < 0:
                break
            candidates.append(i)
            pos = i + 1
        for off in candidates:
            if off + length <= len(data):
                chosen = off
                break
    if chosen is None:
        report["extracted"].append({"name": name, "status": "NOT_FOUND"})
        continue
    blob = data[chosen:chosen + length]
    dest = OUT / name
    dest.write_bytes(blob)
    report["extracted"].append({
        "name": name,
        "status": "OK",
        "offset": hex(chosen),
        "declared_length": length,
        "written_bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
    })

(OUT / "extract_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))