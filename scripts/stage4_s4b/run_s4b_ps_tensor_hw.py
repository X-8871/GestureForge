#!/usr/bin/env python
"""受门禁保护的 S4-B PS 张量诊断执行器（唯一入口）。

必须以 Vitis 2026.1 自带 Python 运行（需要 xsdb 包与 TCF）：
  PYTHONPATH="D:/Xilinx/2026.1/Vitis/scripts/xsdb;D:/Xilinx/2026.1/Vitis/cli/python-packages/site-packages;D:/Xilinx/2026.1/Vitis/cli;<repo>/.pylibs"
  D:/Xilinx/2026.1/Vitis/tps/win64/python-3.13.0/python.exe scripts/stage4_s4b/run_s4b_ps_tensor_hw.py ...

职责边界：
  - 建立 hw_server 会话（host/port 由参数给定，必须匹配 exclusive_session 记录）；
  - 打开 COM4 串口流（115200/8N1，无流控）；
  - 调用 adapter.execute_prepared —— 部署、OP_WEIGHTS、OP_RUN、trace 双读、收尾全部由冻结工具链完成；
  - 本脚本不直接调用任何 hw_axi/下载/复位 API，不重试，不吞错。

退出码：0 = RUN 完成；1 = BLOCKED_BEFORE_HARDWARE（门禁拒绝）；2 = 异常。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import traceback
from pathlib import Path

REQUIRED_GATE_ROLES = ("operator_authorization", "hardware_session_handoff", "exclusive_session",
                       "g0_approval", "command_delivery_review", "timing_freeze",
                       "range_reservation", "cold_basis")


def load_adapter(path: Path):
    spec = importlib.util.spec_from_file_location("s4b_ps_tensor_adapter_runner", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    repo = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser(description="S4-B PS 张量诊断受门禁执行器")
    ap.add_argument("--preparation", required=True)
    ap.add_argument("--hardware-run-id", required=True)
    ap.add_argument("--gate-dir", required=True)
    ap.add_argument("--weight-path", required=True)
    ap.add_argument("--tensor-path", required=True)
    ap.add_argument("--tensor-binding-path", required=True)
    ap.add_argument("--uart", default="COM4")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3121)
    ap.add_argument("--frame-id", type=lambda v: int(v, 0), default=0)
    ap.add_argument("--width", type=int, default=416)
    ap.add_argument("--height", type=int, default=416)
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--core-timeout", type=lambda v: int(v, 0), default=0xFFFFFFFF)
    ap.add_argument("--drain-timeout", type=lambda v: int(v, 0), default=0xFFFFFFFF)
    ap.add_argument("--ack-timeout", type=float, default=5.0, help="RUN ACK/IDLE 观察期限，必须在 (0,10] 秒")
    args = ap.parse_args(argv)

    adapter = load_adapter(repo / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py")
    gate_dir = Path(args.gate_dir).resolve()
    gate_files = {}
    for role in REQUIRED_GATE_ROLES:
        candidate = gate_dir / f"{role}.json"
        if not candidate.is_file():
            print(f"[FAIL] 门禁记录缺失：{candidate}", file=sys.stderr)
            return 1
        gate_files[role] = {"path": str(candidate), "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest()}

    evidence_dir = repo / "tmp" / "4" / "S4-B-REAL-02B" / args.hardware_run_id
    if evidence_dir.exists():
        print(f"[FAIL] 硬件 Run 目录已存在（execute_prepared 拒绝覆盖）：{evidence_dir}", file=sys.stderr)
        return 1

    # 现场会话：xsdb 经 TCF 连接 hw_server；peer 属性由冻结工具自校验。
    import xsdb  # noqa: PLC0415 — 只能在 Vitis Python 下导入
    import serial  # noqa: PLC0415 — pyserial 位于 .pylibs（pip --target）
    sdk = xsdb.start_debug_session()
    channel = None
    stream = None
    try:
        print(f"[INFO] 连接 hw_server {args.host}:{args.port} …", flush=True)
        channel = sdk.connect(host=args.host, port=args.port, server="hw_server")
        peer = dict(sdk._curchan_obj.remote_peer.attrs)
        print(f"[INFO] peer={peer}", flush=True)
        print(f"[INFO] 打开 {args.uart}（115200/8N1，无流控）…", flush=True)
        stream = serial.Serial(args.uart, baudrate=115200, bytesize=8, parity="N", stopbits=1,
                               timeout=0.1, write_timeout=1.0, rtscts=False, dsrdtr=False)
        result = adapter.execute_prepared(
            Path(args.preparation),
            hardware_run_id=args.hardware_run_id,
            gate_files=gate_files,
            xsdb_session=sdk,
            uart_stream=stream,
            weight_path=Path(args.weight_path),
            tensor_path=Path(args.tensor_path),
            tensor_binding_path=Path(args.tensor_binding_path),
            rx_record_path=evidence_dir / "uart_rx.raw.bin",
            tx_header_record_path=evidence_dir / "uart_tx_headers.raw.bin",
            frame_id=args.frame_id,
            width=args.width,
            height=args.height,
            repeat=args.repeat,
            core_timeout=args.core_timeout,
            drain_timeout=args.drain_timeout,
            completion_timeout_seconds=args.ack_timeout,
        )
        print(json.dumps({k: v for k, v in result.items() if k not in ("gate_record_sha256",)},
                         ensure_ascii=False, indent=1, default=str)[:4000], flush=True)
        status = result.get("status")
        if status == "BLOCKED_BEFORE_HARDWARE":
            return 1
        return 0 if status in ("PASS", "COMPLETED") else 2
    finally:
        for closer, what in ((lambda: stream.close(), "serial"), (lambda: sdk.disconnect(chan=channel), "xsdb")):
            try:
                closer()
                print(f"[INFO] {what} 已释放", flush=True)
            except BaseException as exc:  # noqa: BLE001
                print(f"[WARN] {what} 释放异常：{exc}", flush=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        print("[FAIL] 未预期异常（硬件状态须人工核对 hw_server/JTAG）", file=sys.stderr)
        raise SystemExit(2) from None
