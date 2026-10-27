#!/usr/bin/env python
"""端口闭集正负控制：证明 exclusive_session 的 peer 校验只被放宽到 23121，且仍拒绝任意端口。

做法：以 r05 七类记录为基底，向临时副本注入合成 exclusive_session（5 个变体），
逐一调用 adapter.validate_hardware_gates 的**真实**判定，记录 ok 与 missing。
不启动任何服务、不写被审文件、不改动 r05/r06 原文件。
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ_UTC8 = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[4]
GATE_SRC = ROOT / "report/evidence/S4-B/s4b_hw_gates_20261027_r05"
PREP = ROOT / "tmp/4/S4-B-REAL-02B/s4b_ps_adapter_g3_20261027_r01/adapter_preparation.json"
RUN_ID = "s4b_ps_tensor_hw_20261027_r01"
ROLES = ("operator_authorization", "hardware_session_handoff", "g0_approval",
         "command_delivery_review", "timing_freeze", "range_reservation", "cold_basis")

VARIANTS = [
    ("loopback_23121", {"Host": "127.0.0.1", "Port": "23121"}, True),
    ("localhost_23121", {"Host": "localhost", "Port": "23121"}, True),
    ("arbitrary_9999", {"Host": "127.0.0.1", "Port": "9999"}, False),
    ("remote_host_23121", {"Host": "192.168.1.5", "Port": "23121"}, False),
    ("legacy_3121", {"Host": "127.0.0.1", "Port": "3121"}, True),
]


def load_adapter():
    path = ROOT / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py"
    spec = importlib.util.spec_from_file_location("adapter_port_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    adapter = load_adapter()
    prepared = adapter.validate_preparation(PREP)
    _, digest = adapter._verified_artifact_identity(prepared)
    now = datetime.now(TZ_UTC8).isoformat(timespec="seconds")

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, peer, expect_ok in VARIANTS:
            gate_dir = Path(tmp) / name
            gate_dir.mkdir()
            files = {}
            for role in ROLES:
                dst = gate_dir / f"{role}.json"
                shutil.copy2(GATE_SRC / f"{role}.json", dst)
                files[role] = {"path": str(dst), "sha256": hashlib.sha256(dst.read_bytes()).hexdigest()}
            record = {
                "status": "PASS", "exclusive": True, "hardware_run_id": RUN_ID,
                "artifact_identity_sha256": digest, "hw_server_pid": 4242,
                "xsdb_peer": peer, "uart_port": "COM4",
                "verified_at_utc8": now, "validity_seconds": 1800,
                "observed": {"session_port_listening": True},
            }
            ex = gate_dir / "exclusive_session.json"
            ex.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            files["exclusive_session"] = {"path": str(ex),
                                          "sha256": hashlib.sha256(ex.read_bytes()).hexdigest()}
            gate = adapter.validate_hardware_gates(prepared, RUN_ID, files)
            peer_missing = [m for m in gate.missing if m.startswith("exclusive_session:")]
            results.append({
                "variant": name, "xsdb_peer": peer,
                "expect_ok": expect_ok, "ok": gate.allowed,
                "exclusive_missing": peer_missing,
                "verdict_matches_expectation": (gate.allowed is expect_ok) and
                                               (bool(peer_missing) is (not expect_ok)),
                "all_missing": list(gate.missing),
            })

    payload = {
        "schema_version": "s4b_hw_port_closed_set_probe_v1",
        "generated_utc8": now,
        "adapter_sha256": hashlib.sha256(
            (ROOT / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py").read_bytes()).hexdigest(),
        "allowed_hosts": list(adapter.HW_SESSION_HOSTS),
        "allowed_ports": list(adapter.HW_SESSION_PORTS),
        "base_gate_dir": str(GATE_SRC.relative_to(ROOT)).replace("\\", "/"),
        "results": results,
        "all_match": all(r["verdict_matches_expectation"] for r in results),
    }
    out = Path(__file__).resolve().parent / "port_closed_set_probe.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in results:
        print(f"{r['variant']:<22} ok={r['ok']!s:<5} expect_ok={r['expect_ok']!s:<5} "
              f"match={r['verdict_matches_expectation']} peer_missing={r['exclusive_missing']}")
    print(f"all_match={payload['all_match']} → {out}")
    return 0 if payload["all_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
