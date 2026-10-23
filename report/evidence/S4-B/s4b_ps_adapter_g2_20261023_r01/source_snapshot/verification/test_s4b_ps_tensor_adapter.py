# -*- coding: utf-8 -*-
"""S4-B adapter离线来源绑定、安全门禁及快照封装回归。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
import unittest
from unittest import mock
import zlib
import zipfile

from scripts.stage4_s4b import s4b_ps_tensor_adapter as adapter


def _valid_trace_header(source_sha: str, seed: int, first: int = 0x100, last: int = 0x1FF) -> bytes:
    """构造只含合法空日志头的离线测试向量。"""
    words = [0] * 36
    words[0] = adapter.TRACE_MAGIC
    words[1] = adapter.TRACE_SCHEMA_VERSION
    words[2] = adapter.TRACE_HEADER_BYTES
    words[3] = adapter.TRACE_RECORD_BYTES
    words[4] = adapter.TRACE_CAPACITY
    words[6] = seed & 0xFFFFFFFF
    words[7] = seed >> 32
    words[8] = first
    words[9] = last
    words[10] = first
    words[25] = 1
    words[26] = 1
    words[27:35] = [int(source_sha[offset:offset + 8], 16) for offset in range(0, 64, 8)]
    header = bytearray(struct.pack("<36I", *words))
    words[35] = zlib.crc32(header[:140]) & 0xFFFFFFFF
    return struct.pack("<36I", *words)


def _valid_preparation(root: Path, run_id: str = "adapter_test_r01") -> adapter.PreparedRun:
    """在临时目录建立最小、但满足validator身份契约的prepare记录。"""
    output_dir = root / "tmp" / "4" / "S4-B-REAL-02B" / run_id
    output_dir.mkdir(parents=True)
    bound_file = output_dir / "bound.bin"
    bound_file.write_bytes(b"frozen-input")
    bound_sha = hashlib.sha256(b"frozen-input").hexdigest()
    xsa = adapter.EXPECTED_XSA_SHA256
    model = adapter.EXPECTED_MODEL_SHA256
    source = adapter.EXPECTED_DERIVED_SOURCE_SHA256
    derived = {
        "derived_s4b_ps_app_sha256": source,
        "embedded_ready_banner": (
            f"S2B-INFERENCE/1 READY SOURCE={source} XSA={xsa} MODEL={model} "
            "DIAG=s4b-ps-tensor/1 TRACE_ABI=1\\r\\n"
        ),
    }
    banner = adapter.build_expected_ready_banner(derived, xsa, model)
    record = {
        "schema_version": 1,
        "status": "OFFLINE_PREPARATION_VALID",
        "task_id": "S4-B-REAL-02B",
        "run_id": run_id,
        "source_build_run_id": adapter.DEFAULT_BUILD_RUN_ID,
        "project_root": str(root),
        "output_run_dir": str(output_dir),
        "bindings": [{"path": str(bound_file), "sha256": bound_sha,
                      "bytes": len(b"frozen-input"), "role": "test_binding"}],
        "artifact_identity": {
            "build_run_id": adapter.DEFAULT_BUILD_RUN_ID,
            "derived_source_sha256": source,
            "elf_sha256": adapter.EXPECTED_APP_ELF_SHA256,
            "map_sha256": adapter.EXPECTED_APP_MAP_SHA256,
            "reservation_status": "BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE",
        },
        "ready_banner": {"text": banner.decode("ascii"), "hex": banner.hex(),
                         "sha256": hashlib.sha256(banner).hexdigest()},
    }
    record["artifact_identity_sha256"] = adapter.artifact_identity_sha256(record["artifact_identity"])
    path = output_dir / "adapter_preparation.json"
    path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8", newline="\n")
    return adapter.PreparedRun(path, record)


class _Spy:
    """遇到任意属性访问即记录，便于证明门禁前没有碰硬件对象。"""

    def __init__(self) -> None:
        object.__setattr__(self, "calls", [])

    def __getattribute__(self, name: str):
        if name == "calls":
            return object.__getattribute__(self, name)
        object.__getattribute__(self, "calls").append(name)
        raise AssertionError(f"门禁前不应访问属性：{name}")


class AdapterBindingTests(unittest.TestCase):
    """检查文件绑定、门禁和来源导入顺序。"""

    def test_manifest_role_and_sha_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact = root / "build" / "app.elf"
            artifact.parent.mkdir()
            artifact.write_bytes(b"selected artifact")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            entries = {"build/app.elf": {"path": "build/app.elf", "sha256": digest, "role": "artifact"}}
            bound = adapter._bound_manifest_file(root, entries, "build/app.elf", ("artifact",))
            self.assertEqual(bound["sha256"], digest)
            with self.assertRaises(adapter.AdapterError):
                adapter._bound_manifest_file(root, entries, "build/app.elf", ("source",))
            altered = {"build/app.elf": {"path": "build/app.elf", "sha256": "0" * 64, "role": "artifact"}}
            with self.assertRaises(adapter.AdapterError):
                adapter._bound_manifest_file(root, altered, "build/app.elf", ("artifact",))

    def test_manifest_rejects_missing_role_duplicate_and_path_alias(self) -> None:
        with self.assertRaises(adapter.AdapterError):
            adapter.safe_relative_path("a/../b")
        with self.assertRaises(adapter.AdapterError):
            adapter.safe_relative_path("a\\b")
        with self.assertRaises(adapter.AdapterError):
            adapter._manifest_entries({"files": [
                {"path": "a.bin", "sha256": "a" * 64, "role": "artifact"},
                {"path": "a.bin", "sha256": "b" * 64, "role": "artifact"},
            ]})

    def test_inventory_accepts_measured_sha_without_expected_sha(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "measured-tool.exe"
            path.write_bytes(b"measured-only")
            row = {"label": "measured tool", "path": str(path), "exists": True,
                   "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                   "expected_sha256": None, "status": "PASS"}
            inventory = {"external_inputs": [row], "external_inputs_before_build": [dict(row)],
                         "external_inputs_after_build": [dict(row)]}
            rows = adapter._inventory_rows(inventory)
            self.assertEqual(adapter._inventory_binding(rows["measured tool"], "measured tool")["sha256"],
                             row["sha256"])
            path.write_bytes(b"changed")
            with self.assertRaises(adapter.AdapterError):
                adapter._inventory_binding(rows["measured tool"], "measured tool")

    def test_historical_source_commit_is_distinct_from_current_head(self) -> None:
        historical = "1" * 40
        current_head = "2" * 40
        with tempfile.TemporaryDirectory() as temporary, \
                mock.patch.object(adapter, "_git_output", side_effect=[
                    (historical + "\n").encode("ascii"), (current_head + "\n").encode("ascii")]):
            recorded, current = adapter._resolve_historical_source_commit(Path(temporary), historical)
        self.assertEqual(recorded, historical)
        self.assertEqual(current, current_head)

    def test_bundle_overlay_is_exact_and_unlisted_files_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "recovery.zip"
            manifest_path = root / "bundle_manifest.json"
            extracted_root = root / "bundle_extract"
            extracted_root.mkdir()
            source_sha = "1" * 64
            base_platform = ('#define S2B_C_SOURCE_SHA256 "' + "0" * 64 + '"\n').encode("utf-8")
            raw_members = {
                adapter.RECOVERY_INIT_MEMBER: b"init elf bytes",
                "bundle/workspace/infer/src/s2b_inference_app.c": b"frozen app bytes",
                "bundle/workspace/infer/src/s2b_inference_platform.h": base_platform,
            }
            overlays = {
                "bundle/workspace/infer/src/s2b_inference_app.c": b"derived app bytes",
                "bundle/workspace/infer/src/s4b_ps_trace.c": b"trace source",
                "bundle/workspace/infer/src/s4b_ps_trace.h": b"trace header",
                "bundle/workspace/infer/src/s4b_ps_build_config.h": b"seed/session config",
            }
            rows = [{"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                    for name, raw in raw_members.items()]
            manifest_path.write_text(json.dumps({
                "source_commit": "03faa2d47a6e49d7475e387cf6b33edda4962c68",
                "xsa_sha256": adapter.EXPECTED_XSA_SHA256,
                "files": rows,
            }), encoding="utf-8")
            with zipfile.ZipFile(archive_path, "w") as archive:
                for name, raw in raw_members.items():
                    archive.writestr(name, raw)
            expected_platform = re.sub(
                rb'(?m)(#define S2B_C_SOURCE_SHA256 ")[0-9a-f]{64}("\s*)',
                lambda match: match.group(1) + source_sha.encode("ascii") + match.group(2),
                base_platform,
                count=1,
            )
            actual_members = {**raw_members, **overlays,
                              "bundle/workspace/infer/src/s2b_inference_platform.h": expected_platform}
            for name, raw in actual_members.items():
                path = extracted_root.joinpath(*name.split("/"))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            test_member_names = set(raw_members)
            test_pathset_sha = hashlib.sha256("\n".join(sorted(test_member_names)).encode("utf-8")).hexdigest()
            with mock.patch.object(adapter, "RECOVERY_BUNDLE_MEMBER_COUNT", len(test_member_names)), \
                    mock.patch.object(adapter, "RECOVERY_BUNDLE_MEMBER_PATHSET_SHA256", test_pathset_sha):
                _, bindings = adapter._verify_bundle_members(
                    archive_path, manifest_path, extracted_root, overlays, source_sha)
            self.assertEqual(len(bindings), len(actual_members))
            rogue = extracted_root / "bundle" / "workspace" / "infer" / "src" / "rogue.c"
            rogue.write_bytes(b"unlisted source")
            with mock.patch.object(adapter, "RECOVERY_BUNDLE_MEMBER_COUNT", len(test_member_names)), \
                    mock.patch.object(adapter, "RECOVERY_BUNDLE_MEMBER_PATHSET_SHA256", test_pathset_sha):
                with self.assertRaises(adapter.AdapterError):
                    adapter._verify_bundle_members(archive_path, manifest_path, extracted_root, overlays, source_sha)

    def test_unknown_source_or_library_path_is_rejected(self) -> None:
        allowed = {"bundle/workspace/infer/src/s2b_inference_app.c",
                   "bundle/workspace/ps7/export/ps7/sw/cpu0/lib/libxil.a"}
        expected_sha = hashlib.sha256("\n".join(sorted(allowed)).encode("utf-8")).hexdigest()
        with mock.patch.object(adapter, "RECOVERY_BUNDLE_MEMBER_COUNT", len(allowed)), \
                mock.patch.object(adapter, "RECOVERY_BUNDLE_MEMBER_PATHSET_SHA256", expected_sha):
            adapter._verify_bundle_member_pathset(set(allowed))
            for extra in ("bundle/workspace/infer/src/rogue.c",
                          "bundle/workspace/ps7/export/ps7/sw/cpu0/lib/librogue.a"):
                with self.subTest(extra=extra), self.assertRaises(adapter.AdapterError):
                    adapter._verify_bundle_member_pathset(set(allowed) | {extra})

    def test_valid_preparation_rehashes_bound_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "tmp" / "4" / "S4-B-REAL-02B").mkdir(parents=True)
            prepared = _valid_preparation(root)
            with mock.patch.object(adapter, "_reconstruct_artifact_identity",
                                   return_value=prepared.data["artifact_identity"]):
                actual = adapter.validate_preparation(prepared.path)
            self.assertEqual(actual.data["status"], "OFFLINE_PREPARATION_VALID")
            tampered = dict(prepared.data)
            tampered["artifact_identity"] = dict(prepared.data["artifact_identity"])
            tampered["artifact_identity"]["derived_source_sha256"] = "0" * 64
            tampered_path = prepared.path.parent / "tampered_preparation.json"
            tampered_path.write_text(json.dumps(tampered, ensure_ascii=False), encoding="utf-8")
            with mock.patch.object(adapter, "_reconstruct_artifact_identity",
                                   return_value=prepared.data["artifact_identity"]):
                with self.assertRaises(adapter.AdapterError):
                    adapter.validate_preparation(tampered_path)
            actual.data["bindings"][0]["path"] and Path(actual.data["bindings"][0]["path"]).write_bytes(b"mutated")
            with mock.patch.object(adapter, "_reconstruct_artifact_identity",
                                   return_value=prepared.data["artifact_identity"]):
                with self.assertRaises(adapter.AdapterError):
                    adapter.validate_preparation(prepared.path)

    def test_missing_hardware_gates_return_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "tmp" / "4" / "S4-B-REAL-02B").mkdir(parents=True)
            prepared = _valid_preparation(root)
            check = adapter.validate_hardware_gates(prepared, "hardware_run_r01", {})
            self.assertFalse(check.allowed)
            self.assertEqual(len(check.missing), len(adapter.REQUIRED_GATE_RECORDS))
            self.assertTrue(all(name in " ".join(check.missing) for name in adapter.REQUIRED_GATE_RECORDS))

    def test_execute_missing_gate_does_not_touch_session_or_uart(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "tmp" / "4" / "S4-B-REAL-02B").mkdir(parents=True)
            prepared = _valid_preparation(root)
            session = _Spy()
            stream = _Spy()
            with mock.patch.object(adapter, "_reconstruct_artifact_identity",
                                   return_value=prepared.data["artifact_identity"]):
                result = adapter.execute_prepared(
                    prepared.path,
                    hardware_run_id="hardware_run_r01",
                    gate_files={},
                    xsdb_session=session,
                    uart_stream=stream,
                    weight_path=Path("must-not-be-read.gf8"),
                    tensor_path=Path("must-not-be-read.bin"),
                    tensor_binding_path=Path("must-not-be-read.json"),
                    rx_record_path=Path("unused"),
                    tx_header_record_path=Path("unused"),
                    frame_id=0,
                    width=1,
                    height=1,
                    repeat=1,
                    core_timeout=1,
                    drain_timeout=1,
                )
        self.assertEqual(result["status"], "BLOCKED_BEFORE_HARDWARE")
        self.assertEqual(result["sdk_calls"], 0)
        self.assertEqual(result["uart_calls"], 0)
        self.assertEqual(session.calls, [])
        self.assertEqual(stream.calls, [])

    def test_frozen_import_rejects_preloaded_name_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            evidence = Path(temporary)
            sentinel = object()
            sys.modules["s2b_board_jtag"] = sentinel
            try:
                with self.assertRaises(adapter.AdapterError):
                    adapter._stage_verified_tool_modules(adapter.PreparedRun(Path("unused"), {}),
                                                         evidence, Path(temporary))
                self.assertEqual(list(evidence.iterdir()), [])
            finally:
                sys.modules.pop("s2b_board_jtag", None)


class AdapterWireAndSnapshotTests(unittest.TestCase):
    """检查完整READY横幅及双读快照封装。"""

    def test_ready_banner_uses_literal_json_escape_and_actual_crlf(self) -> None:
        source = adapter.EXPECTED_DERIVED_SOURCE_SHA256
        derived = {
            "derived_s4b_ps_app_sha256": source,
            "embedded_ready_banner": (
                f"S2B-INFERENCE/1 READY SOURCE={source} XSA={adapter.EXPECTED_XSA_SHA256} "
                f"MODEL={adapter.EXPECTED_MODEL_SHA256} DIAG=s4b-ps-tensor/1 TRACE_ABI=1\\r\\n"
            ),
        }
        expected = adapter.build_expected_ready_banner(
            derived, adapter.EXPECTED_XSA_SHA256, adapter.EXPECTED_MODEL_SHA256)
        self.assertTrue(expected.endswith(b"\r\n"))
        self.assertFalse(expected.endswith(b"\\r\\n"))

        class Wire:
            def __init__(self, raw: bytes) -> None:
                self.raw = raw
                self.read_count = 0

            def read_exact(self, length: int, deadline: float) -> bytes:
                self.read_count += 1
                result, self.raw = self.raw[:length], self.raw[length:]
                return result

        wire = Wire(expected)
        self.assertEqual(adapter._read_ready_banner(wire, expected), expected)
        self.assertEqual(wire.raw, b"")
        self.assertEqual(wire.read_count, len(expected))
        with self.assertRaises(adapter.AdapterError):
            adapter.build_expected_ready_banner(
                {**derived, "embedded_ready_banner": derived["embedded_ready_banner"][:-4] + "x"},
                adapter.EXPECTED_XSA_SHA256,
                adapter.EXPECTED_MODEL_SHA256,
            )

    def test_double_snapshot_pack_checks_identity_crc_layout_and_stability(self) -> None:
        source = adapter.EXPECTED_DERIVED_SOURCE_SHA256
        seed = 0x5342424F4F543132
        header = _valid_trace_header(source, seed)
        records = bytes(adapter.TRACE_RECORDS_BYTES)
        packed = adapter.pack_double_snapshot(
            header, records, header, records,
            expected_source_sha256=source,
            expected_boot_seed=seed,
            expected_session_first=0x100,
            expected_session_last=0x1FF,
        )
        self.assertEqual(len(packed), adapter.DUMP_HEADER.size + 2 * adapter.TRACE_SNAPSHOT_BYTES)
        magic, version, header_size, record_size, capacity, snapshot_size = adapter.DUMP_HEADER.unpack_from(packed)
        self.assertEqual((magic, version, header_size, record_size, capacity, snapshot_size),
                         (b"S4BPSDMP", 1, 144, 184, 1000, 184144))
        with self.assertRaises(adapter.AdapterError):
            adapter.pack_double_snapshot(
                header, records, header, records[:-1] + b"\x01",
                expected_source_sha256=source, expected_boot_seed=seed)
        bad_crc = bytearray(header)
        bad_crc[12] ^= 1
        with self.assertRaises(adapter.AdapterError):
            adapter.pack_double_snapshot(
                bytes(bad_crc), records, bytes(bad_crc), records,
                expected_source_sha256=source, expected_boot_seed=seed)
        with self.assertRaises(adapter.AdapterError):
            adapter.pack_double_snapshot(
                header, records, header, records,
                expected_source_sha256="0" * 64, expected_boot_seed=seed)
        with self.assertRaises(adapter.AdapterError):
            adapter.pack_double_snapshot(
                header, records, header, records,
                expected_source_sha256=source, expected_boot_seed=seed + 1)


if __name__ == "__main__":
    unittest.main()
