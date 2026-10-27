#!/usr/bin/env python
"""生成现场类硬件门禁记录：exclusive_session / cold_basis（只读观测，不启动任何服务）。

exclusive_session：读取当前 hw_server 进程 PID 与串口枚举，写出 30 分钟窗口的记录。
    本脚本**不启动** hw_server / xsdb，也不打开串口；会话必须由持有者先行建立。
cold_basis：按操作者提供的断电事实与证据文件生成记录（physical_power_cycle）。

用法：
  python -B scripts/stage4_s4b/make_runtime_gate_records.py --role exclusive_session \
      --preparation <prep.json> --hardware-run-id <RunId> --out-dir <dir> --expect-uart COM4

  python -B scripts/stage4_s4b/make_runtime_gate_records.py --role cold_basis \
      --preparation <prep.json> --hardware-run-id <RunId> --out-dir <dir> \
      --power-cycle-at "2026-10-27 14:20" --evidence <断电证据文件> \
      --attestation "Wong 已执行物理断电并重新上电"

退出码：0 = 记录已生成；1 = 现场条件不满足（拒绝生成）；2 = 参数/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType

TZ_UTC8 = timezone(timedelta(hours=8))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_adapter(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("s4b_ps_tensor_adapter", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"无法构造 adapter 规格：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def hw_server_pids() -> list[int]:
    proc = subprocess.run(["tasklist", "/FI", "IMAGENAME eq hw_server.exe", "/FO", "CSV", "/NH"],
                          capture_output=True, text=True, errors="replace")
    pids: list[int] = []
    for line in proc.stdout.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 2 and parts[0].lower().startswith("hw_server"):
            if parts[1].isdigit():
                pids.append(int(parts[1]))
    return pids


def com_ports() -> list[str]:
    try:
        import winreg
    except ImportError:
        return []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
    except OSError:
        return []
    ports: list[str] = []
    try:
        i = 0
        while True:
            try:
                _, value, _ = winreg.EnumValue(key, i)
            except OSError:
                break
            ports.append(str(value))
            i += 1
    finally:
        key.Close()
    return sorted(ports)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="生成现场类硬件门禁记录")
    ap.add_argument("--role", required=True, choices=["exclusive_session", "cold_basis"])
    ap.add_argument("--preparation", required=True)
    ap.add_argument("--hardware-run-id", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--expect-uart", default="COM4")
    ap.add_argument("--xsdb-host", default="localhost")
    ap.add_argument("--xsdb-port", default="3121")
    ap.add_argument("--power-cycle-at", default=None, help="断电→上电时刻（YYYY-MM-DD HH:MM，UTC+8）")
    ap.add_argument("--evidence", default=None, help="断电证据文件路径")
    ap.add_argument("--attestation", default=None, help="操作者确认语句")
    args = ap.parse_args(argv)

    out_dir = Path(args.out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[ERROR] 输出目录已存在且非空：{out_dir}", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    worktree = Path(__file__).resolve().parents[2]
    adapter = load_adapter(worktree / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py")
    prepared = adapter.validate_preparation(Path(args.preparation).resolve())
    _, digest = adapter._verified_artifact_identity(prepared)

    now = datetime.now(TZ_UTC8)

    if args.role == "exclusive_session":
        pids = hw_server_pids()
        ports = com_ports()
        problems = []
        if len(pids) != 1:
            problems.append(f"hw_server 进程数为 {len(pids)}（必须恰好 1）")
        if args.expect_uart not in ports:
            problems.append(f"串口 {args.expect_uart} 不在枚举中：{ports}")
        if args.xsdb_port != "3121":
            problems.append("xsdb 端口必须为 3121")
        if args.xsdb_host not in ("localhost", "127.0.0.1"):
            problems.append("xsdb peer 必须是 localhost 或 127.0.0.1")
        if problems:
            print("[FAIL] 现场条件不满足，拒绝生成 exclusive_session：", file=sys.stderr)
            for p in problems:
                print(f"  - {p}", file=sys.stderr)
            return 1
        record = {
            "status": "PASS",
            "exclusive": True,
            "hardware_run_id": args.hardware_run_id,
            "artifact_identity_sha256": digest,
            "hw_server_pid": pids[0],
            "xsdb_peer": {"Host": args.xsdb_host, "Port": args.xsdb_port},
            "uart_port": args.expect_uart,
            "verified_at_utc8": now.isoformat(timespec="seconds"),
            "validity_seconds": 1800,
            "observed": {"com_ports": ports, "hw_server_pids": pids},
            "boundaries": ["本记录只证独占与环境可见性，不证板上行为", "未启动/未重启任何服务"],
        }
        name = "exclusive_session.json"
    else:
        if not args.power_cycle_at or not args.evidence or not args.attestation:
            print("[ERROR] cold_basis 需要 --power-cycle-at / --evidence / --attestation", file=sys.stderr)
            return 2
        evidence = Path(args.evidence)
        if not evidence.is_file():
            print(f"[FAIL] 断电证据文件不存在：{evidence}", file=sys.stderr)
            return 1
        try:
            cycle_at = datetime.strptime(args.power_cycle_at, "%Y-%m-%d %H:%M").replace(tzinfo=TZ_UTC8)
        except ValueError:
            print("[ERROR] --power-cycle-at 格式必须为 'YYYY-MM-DD HH:MM'", file=sys.stderr)
            return 2
        if cycle_at > now:
            print("[FAIL] 断电时刻晚于当前时间", file=sys.stderr)
            return 1
        record = {
            "status": "PASS",
            "hardware_run_id": args.hardware_run_id,
            "artifact_identity_sha256": digest,
            "old_axi_lifecycle_cleared": True,
            "basis_kind": "physical_power_cycle",
            "power_cycle_at_utc8": cycle_at.isoformat(timespec="seconds"),
            "attestation": args.attestation,
            "evidence_binding": {"path": str(evidence.resolve()), "sha256": sha256_file(evidence)},
            "recorded_at_utc8": now.isoformat(timespec="seconds"),
            "boundaries": ["冷依据只证明旧生命周期已清除，不证明板上功能", "未执行任何 reset/重配置"],
        }
        name = "cold_basis.json"

    (out_dir / name).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out_dir.iterdir()) if p.is_file() and p.name != "manifest.json"]
    (out_dir / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "task_id": "S4-B-REAL-02B", "run_id": args.hardware_run_id,
        "generated_utc8": now.isoformat(timespec="seconds"), "verdict": "GENERATED",
        "exit_code": 0, "files": files, "role": args.role,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[GENERATED] {args.role} → {out_dir / name}")
    print(f"  record_sha256={sha256_file(out_dir / name)[:16]}…")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        print(f"[ERROR] 未预期错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
