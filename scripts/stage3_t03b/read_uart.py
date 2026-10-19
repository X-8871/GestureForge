"""读取板块 PS UART（默认 COM4 @115200）指定秒数并写入日志。

用途：阶段3 板测时抓取应用 xil_printf 输出（S3_DIAG_* 诊断行）。
只读串口，不发送任何数据。用法：
    python read_uart.py <port> <seconds> <out_file>
"""
import sys
import time
from pathlib import Path

import serial  # pyserial

port = sys.argv[1] if len(sys.argv) > 1 else "COM4"
seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("uart_capture.txt")

out.parent.mkdir(parents=True, exist_ok=True)
collected = bytearray()
with serial.Serial(port, baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=0.2) as ser:
    deadline = time.time() + seconds
    while time.time() < deadline:
        chunk = ser.read(4096)
        if chunk:
            collected.extend(chunk)
            sys.stdout.write(chunk.decode("utf-8", errors="replace"))
            sys.stdout.flush()

out.write_bytes(bytes(collected))
print(f"\nUART_CAPTURE_BYTES={len(collected)}")
print(f"UART_CAPTURE_FILE={out}")
text = collected.decode("utf-8", errors="replace")
for marker in ("S3_DIAG_APP_ENTER", "S3_DIAG_SENSOR_ID", "S3_DIAG_DISPLAY_START", "S3_DIAG_VDMA_WRITE_STARTED"):
    print(f"UART_MARKER_{marker}={'FOUND' if marker in text else 'MISSING'}")