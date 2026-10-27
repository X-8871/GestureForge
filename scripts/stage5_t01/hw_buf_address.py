#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从板上 UART 日志解析**当前**显示缓冲地址（取代脚本里的硬编码常量）。

背景（2026-10-27 像素级叠加"未确认"的根因）：`jtag_dump_rows.tcl` / `jtag_read_overlay_buf.tcl`
硬编码 `buf0=0x00114C00`，而该地址是 **10-22 旧版应用** 的 BUF0（旧 UART 实证）。本轮应用上报
`S5_P1_BUF0=00138C00`（BUF1=00727800、BUF2=00D16400）⇒ 回读读到的是**别的内存**，
"缓冲里没有叠加框"是**测量缺陷**而非绘制缺陷。

用法：
    python -B scripts/stage5_t01/hw_buf_address.py --uart <uart.log> [--index 0] [--json out.json]
退出码：0=解析成功；1=未找到；2=输入错误。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

PATTERN = re.compile(r"S5_P1_BUF(\d+)\s*=\s*([0-9A-Fa-f]{1,16})")


class InputError(RuntimeError):
    """输入不合法。"""


def parse_buffer_addresses(uart_log: pathlib.Path) -> dict[int, int]:
    """解析 `S5_P1_BUF<n>=<hex>`；同一序号多次出现取**最后一次**（应用启动后会重印）。"""
    if not uart_log.is_file():
        raise InputError(f"UART 日志不存在：{uart_log}")
    text = uart_log.read_text(encoding="utf-8", errors="replace")
    found: dict[int, int] = {}
    for match in PATTERN.finditer(text):
        found[int(match.group(1))] = int(match.group(2), 16)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="解析板上显示缓冲地址（取代硬编码）")
    parser.add_argument("--uart", required=True, help="板上 UART 日志路径")
    parser.add_argument("--index", type=int, default=0, help="要取哪个缓冲（默认 0）")
    parser.add_argument("--json", dest="json_out", default=None)
    args = parser.parse_args(argv)
    try:
        addresses = parse_buffer_addresses(pathlib.Path(args.uart))
    except InputError as exc:
        print(f"[buf-addr] 输入错误：{exc}")
        return 2
    if args.index not in addresses:
        print(f"[buf-addr] 未在日志中找到 S5_P1_BUF{args.index}")
        return 1
    payload = {"uart_log": str(args.uart), "buffers": {str(k): f"0x{v:08X}" for k, v in sorted(addresses.items())},
               "selected_index": args.index, "selected_hex": f"0x{addresses[args.index]:08X}"}
    if args.json_out:
        pathlib.Path(args.json_out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")
    print(f"[buf-addr] S5_P1_BUF{args.index}={payload['selected_hex']} "
          f"（共解析 {len(addresses)} 个缓冲）")
    return 0


if __name__ == "__main__":
    sys.exit(main())