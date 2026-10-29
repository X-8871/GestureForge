# -*- coding: utf-8 -*-
"""只读取证脚本：head13 尾 word（byte 5,068/5,069）差异归因。

用途（2026-10-29，S4-T34 / task-2）：
  1) 打印参考 head13 尾部字节，确认 byte 5,068/5,069 是**有效数据**（0x06/0x05）；
  2) 复核宿主预置的字数算术：mwr 按 32-bit 字计数 ⇒ 5,070//4 = 1,267 字 = 5,068 B，
     尾 2 字节不被写入；
  3) 从基线 run 的候选区 dump 中读出 0x12000000+5,068 处的实际内容，证明它就是
     未更新的旧值（0xFF 0x8F），从而解释 diff13=2 first13=5068。
只读，不写任何证据目录以外的文件。
"""
import hashlib
import os

RAW = r"D:\codex-worktrees\w4\report\evidence\S4-B\20261021_r01\test_fist_000_head13.raw"
RAW26 = r"D:\codex-worktrees\w4\report\evidence\S4-B\20261021_r01\test_fist_000_head26.raw"
PAD = r"D:\codex-worktrees\w4\report\evidence\S4-T34\bringup_window6_20261028_r03\W2_pre_head13_padded.bin"
RUN = r"D:\codex-worktrees\w4\report\evidence\S4-T34\s4d_m4b_baseline_2b_20261029_r03"
HEAD13_OFF = 0x01A46100
ARENA = 0x10000000
RAW_BASE = 0x12000000
BYTES = 5070


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def word_le(b, off):
    return int.from_bytes(b[off:off + 4], "little")


d = open(RAW, "rb").read()
print("=== 参考 head13 ===")
print(f"path={RAW}\nsize={len(d)} sha256={sha(RAW)}")
print("bytes 5056..5069:", " ".join(f"{i}:{d[i]:02x}" for i in range(5056, 5070)))
print("最后完整 word 偏移 5,064:", " ".join(f"{b:02x}" for b in d[5064:5068]),
      f"⇒ LE=0x{word_le(d, 5064):08x}")
print("尾 word 偏移 5,068 仅有 2 字节:", " ".join(f"{b:02x}" for b in d[5068:5070]),
      "⇒ 期望 lane0/lane1 = 0x06/0x05")
print()

print("=== 参考 head26（对照：长度 20,280 B，%4 == 0，无尾部半字） ===")
d26 = open(RAW26, "rb").read()
print(f"size={len(d26)} sha256={sha(RAW26)}  len%4={len(d26) % 4}")
print()

print("=== 宿主预置字数算术（xsdb mwr 的 count 是 32-bit 字数） ===")
print(f"head13: {BYTES} B ⇒ {BYTES // 4} 字 = {BYTES // 4 * 4} B；"
      f"覆盖 byte 0..{BYTES // 4 * 4 - 1}，**tail 2 B 漏写**")
print(f"head26: {len(d26)} B ⇒ {len(d26) // 4} 字 = {len(d26) // 4 * 4} B；完整覆盖")
print(f"补齐后 head13: 5,072 B（+2 pad 0x00）⇒ {(BYTES + 3) // 4} 字 = {(BYTES + 3) // 4 * 4} B")
print()

print("=== window #6 r03 的补齐参考（唯一一次带 pad 的成功路径） ===")
pd = open(PAD, "rb").read()
print(f"padded size={len(pd)} sha256={sha(PAD)}")
print("padded[0:5070]==head13.raw:", pd[:BYTES] == d, " pad bytes:", pd[BYTES:].hex())
print(f"尾部 8 字节: {' '.join(f'{b:02x}' for b in pd[-8:])} ⇒ 尾 word LE=0x{word_le(pd, 5068):08x}")
print()

print("=== 基线 run r03 的候选区 dump：0x12000000+5,068 的实际内容 ===")
for name, base in (("W0_dump.bin", "运行前（预置之后、M4-b 之前）"),
                   ("W4_dump.bin", "运行后")):
    p = os.path.join(RUN, name)
    b = open(p, "rb").read()
    print(f"{name} ({base}) size={len(b)} sha256={sha(p)}")
    print("  bytes 5064..5071:", " ".join(f"{o}:{b[o]:02x}" for o in range(5064, 5072)))
    print(f"  尾 word(5,068) LE=0x{word_le(b, 5068):08x}  期望(补齐参考)=0x{word_le(pd, 5068):08x}"
          f"  ⇒ {'相等' if word_le(b, 5068) == word_le(pd, 5068) else '不等（漏写证据）'}")
print()

print("=== 板上取证地址（供 board-runner 使用） ===")
tail_addr = ARENA + HEAD13_OFF + BYTES // 4 * 4
print(f"arena 尾 word   = 0x{tail_addr:08x}  ({'0x10000000+0x%X+%d' % (HEAD13_OFF, BYTES // 4 * 4)})")
print(f"ref   尾 word   = 0x{RAW_BASE + BYTES // 4 * 4:08x}")
print("期望：arena 尾 word 低 16 位 = 0x0506（lane0=0x06, lane1=0x05）；"
      "高 16 位 = 运行前值（PL 不得越过逻辑张量尾部）")