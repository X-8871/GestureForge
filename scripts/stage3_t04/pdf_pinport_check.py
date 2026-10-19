"""在 AX7020 用户手册 PDF 中定位器件引脚出现在 J10 还是 J11 的针脚表。

用途：验证本工程 AN5642 约束所用 FPGA 封装引脚（T16/V18/.../B20）究竟属于哪个扩展口。
只读 PDF；输出命中页与上下文行。
用法: python pdf_pinport_check.py <pdf> T16 V18 V17 ...
"""
import re
import sys

import fitz  # PyMuPDF

pdf = sys.argv[1]
pins = sys.argv[2:] or ["T16", "V18", "V17", "T15", "T11", "A20", "B19", "B20"]

doc = fitz.open(pdf)
print(f"PDF={pdf} pages={doc.page_count}")
port_re = re.compile(r"J1[01]")

for pno in range(doc.page_count):
    page = doc[pno]
    text = page.get_text("text")
    if "J10" not in text and "J11" not in text:
        continue
    hits = [p for p in pins if re.search(rf"\b{p}\b", text)]
    if not hits:
        continue
    print(f"\n=== page {pno + 1} (1-based): 命中 {sorted(set(hits))} ===")
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if any(re.search(rf"\b{p}\b", s) for p in hits) or port_re.search(s):
            print(f"  {s}")