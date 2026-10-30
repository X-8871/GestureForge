"""只准备M3授权副本与ELF加载范围核验，不访问硬件或修改上游。"""

import hashlib
import json
import struct
from pathlib import Path


root = Path(__file__).resolve().parent.parent
run = root / "report/evidence/R03-M3/m3_pair_20261031_r01"
target = run / "authorization.md"
if target.exists():
    raise FileExistsError(target)
mail = Path(r"D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox")
names = ["DSH-20261031-019-m3-paired-sampling-board-lease-offer.md",
         "DSH-20261031-021-sidecar-divergence-m3-lifecycle-ack.md",
         "DSH-20261031-022-sidecar-identity-a-final.md"]
content = []
for name in names:
    path = (mail / name).resolve(strict=True)
    content.append(path.read_text(encoding="utf-8"))
target.write_text("\n\n".join(content), encoding="utf-8", newline="\n")
elf = Path(r"D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_chainA.elf").resolve(strict=True)
data = elf.read_bytes()
if data[:6] != b"\x7fELF\x01\x01":
    raise ValueError("必须是32位小端ELF")
offset = struct.unpack_from("<I", data, 28)[0]
size, count = struct.unpack_from("<HH", data, 42)
segments = []
for i in range(count):
    kind, file_offset, virtual, physical, file_bytes, memory_bytes, flags, alignment = struct.unpack_from("<IIIIIIII", data, offset + i * size)
    if kind == 1:
        if memory_bytes and physical < 0x12C08000 and physical + memory_bytes > 0x12000000:
            raise ValueError("ELF加载范围与M3候选区相交，停止")
        segments.append({"physical_start": hex(physical), "memory_bytes": memory_bytes, "file_bytes": file_bytes})
result = {"elf": str(elf), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
          "load_segments": segments, "candidate_overlap": False, "exit_code": 0,
          "meaning": "仅静态准备，未dow或运行程序；当前POR不重复init，应用只dow不con"}
(run / "elf_load_ranges.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(result, ensure_ascii=False))
