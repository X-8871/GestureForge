# -*- coding: utf-8 -*-
"""S4-B adapter离线来源绑定、安全门禁及快照封装回归。"""

from __future__ import annotations

import hashlib
import copy
import io
import json
import os
from pathlib import Path
import re
import subprocess
import struct
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta
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


def _completed_trace_header(identity: dict[str, object], uart_sequence: int,
                            frame_id: int, repeat: int) -> bytes:
    """构造一条已完成RUN的合法trace header测试向量。"""
    words = list(struct.unpack("<36I", _valid_trace_header(
        str(identity["derived_source_sha256"]), int(identity["boot_seed"]),
        int(identity["session_first"]), int(identity["session_last"]))))
    session = int(identity["session_first"])
    words[5] = repeat
    words[10] = session + 1
    words[18] = 1
    words[19] = session
    words[20] = uart_sequence
    words[21] = frame_id
    words[22] = repeat
    words[23] = repeat
    words[24] = session
    raw = bytearray(struct.pack("<36I", *words))
    words[35] = zlib.crc32(raw[:140]) & 0xFFFFFFFF
    return struct.pack("<36I", *words)


def _successful_trace_record(session_id: int, frame_id: int, result_seq: int,
                             repeat_index: int, uart_sequence: int,
                             input_crc32: int, epoch: int, terminal_status: int) -> bytes:
    """构造decoder可验的成功推理记录，所有事件时戳按序递增。"""
    words = [0] * 46
    words[0:12] = [0x53345243, 1, 184, 0, session_id, frame_id,
                   result_seq, repeat_index, uart_sequence, input_crc32,
                   adapter.INPUT_BYTES, 1]
    words[12:15] = [0, 0, 3]
    words[15:31] = [10, 0, 20, 0, 30, 0, 40, 0, 50, 0, 60, 0, 70, 0, 80, 0]
    words[31] = epoch & 0xFFFFFFFF
    words[32] = epoch >> 32
    words[33] = frame_id
    words[34] = terminal_status
    words[37] = 1
    words[38] = 0
    words[39] = 0
    words[40] = 0
    words[41] = 0
    words[42] = 2
    words[43] = 1
    words[44] = (1 << 10) - 1
    raw = bytearray(struct.pack("<46I", *words))
    words[45] = zlib.crc32(raw[:180]) & 0xFFFFFFFF
    return struct.pack("<46I", *words)


def _valid_preparation(root: Path | None = None, run_id: str | None = None) -> adapter.PreparedRun:
    """读取本轮实际r13离线prepare产物，不使用自造身份fixture。"""
    del root, run_id
    value = os.environ.get("S4B_ADAPTER_TEST_PREPARATION")
    if not value:
        raise RuntimeError("单测必须设置S4B_ADAPTER_TEST_PREPARATION为本轮r13准备记录")
    return adapter.validate_preparation(Path(value))


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

    def test_exact_path_rejects_raw_windows_aliases_before_path_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            exact = Path(temporary).resolve()
            with self.assertRaises(adapter.AdapterError):
                adapter.exact_path(str(exact) + "\\.\\missing")
            with self.assertRaises(adapter.AdapterError):
                adapter.exact_path(str(exact) + "\\..\\missing")
            with self.assertRaises(adapter.AdapterError):
                adapter.exact_path(str(exact) + "\\\\missing")
            with self.assertRaises(adapter.AdapterError):
                adapter.exact_path(str(exact) + "\\alias. ")

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
            manifest_raw = json.dumps({
                "source_commit": "03faa2d47a6e49d7475e387cf6b33edda4962c68",
                "xsa_sha256": adapter.EXPECTED_XSA_SHA256,
                "files": rows,
            }, separators=(",", ":"), sort_keys=True).encode("utf-8")
            manifest_path.write_bytes(manifest_raw)
            with zipfile.ZipFile(archive_path, "w") as archive:
                for name, raw in raw_members.items():
                    archive.writestr(name, raw)
                archive.writestr("bundle/workspace/manifest.json", manifest_raw)
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
            rogue_name = "bundle/workspace/infer/src/librogue.a"
            with zipfile.ZipFile(archive_path, "a") as archive:
                archive.writestr(rogue_name, b"unlisted library")
            with mock.patch.object(adapter, "RECOVERY_BUNDLE_MEMBER_COUNT", len(test_member_names)), \
                    mock.patch.object(adapter, "RECOVERY_BUNDLE_MEMBER_PATHSET_SHA256", test_pathset_sha):
                with self.assertRaises(adapter.AdapterError):
                    adapter._verify_bundle_members(
                        archive_path, manifest_path, extracted_root, overlays, source_sha)
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
        prepared = _valid_preparation()
        actual = adapter.validate_preparation(prepared.path)
        self.assertEqual(actual.data["status"], "OFFLINE_PREPARATION_VALID")
        output_dir = prepared.path.parent

        wrong_elf = copy.deepcopy(prepared.data)
        elf_r04 = Path(prepared.data["project_root"]) / "report" / "evidence" / "S4-B" / \
            "s4b_ps_tensor_20261023_r04" / "s4b_ps_tensor_diagnostic.elf"
        elf_row = next(row for row in wrong_elf["bindings"] if row["role"] == "artifact" and
                       Path(row["path"]).name == "s4b_ps_tensor_diagnostic.elf")
        elf_row.update(path=str(elf_r04), sha256=hashlib.sha256(elf_r04.read_bytes()).hexdigest(),
                       bytes=elf_r04.stat().st_size)
        elf_row["path"] = str(elf_r04)
        wrong_elf["artifact_identity"]["elf_sha256"] = elf_row["sha256"]
        wrong_elf["artifact_identity_sha256"] = adapter.artifact_identity_sha256(
            wrong_elf["artifact_identity"])
        wrong_elf_path = output_dir / "probe_r04_elf_rebound.json"
        wrong_elf_path.write_text(json.dumps(wrong_elf, ensure_ascii=False), encoding="utf-8", newline="\n")
        with self.assertRaises(adapter.AdapterError):
            adapter.validate_preparation(wrong_elf_path)

        wrong_init = copy.deepcopy(prepared.data)
        fake_init = output_dir / "verified_payload" / "forged_init.elf"
        fake_init.write_bytes(b"not from frozen recovery ZIP")
        init_row = next(row for row in wrong_init["bindings"] if row["role"] == "verified_recovery_init_elf")
        init_row.update(path=str(fake_init), sha256=hashlib.sha256(fake_init.read_bytes()).hexdigest(),
                        bytes=fake_init.stat().st_size)
        bundle_init_row = next(row for row in wrong_init["bindings"]
                               if row["role"] == "verified_recovery_bundle_member" and
                               row.get("relative_path") == adapter.RECOVERY_INIT_MEMBER)
        bundle_init_row.update(path=str(fake_init), sha256=init_row["sha256"],
                               bytes=init_row["bytes"])
        wrong_init["artifact_identity"]["init_elf_sha256"] = init_row["sha256"]
        wrong_init["artifact_identity_sha256"] = adapter.artifact_identity_sha256(wrong_init["artifact_identity"])
        wrong_init_path = output_dir / "probe_forged_init_rebound.json"
        wrong_init_path.write_text(json.dumps(wrong_init, ensure_ascii=False), encoding="utf-8", newline="\n")
        with self.assertRaises(adapter.AdapterError):
            adapter.validate_preparation(wrong_init_path)


    def test_missing_hardware_gates_return_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "tmp" / "4" / "S4-B-REAL-02B").mkdir(parents=True)
            prepared = _valid_preparation(root)
            check = adapter.validate_hardware_gates(prepared, "hardware_run_r01", {})
            self.assertFalse(check.allowed)
            self.assertEqual(len(check.missing), len(adapter.REQUIRED_GATE_RECORDS))
            self.assertTrue(all(name in " ".join(check.missing) for name in adapter.REQUIRED_GATE_RECORDS))

    def test_real_project_handoff_source_fails_closed_against_self_signed_row(self) -> None:
        prepared = _valid_preparation()
        hardware_run_id = f"hardware_run_attack_{time.time_ns()}"
        identity_sha = prepared.data["artifact_identity_sha256"]
        source_context = adapter._hardware_authority_snapshot()
        source_pointer = {key: source_context[key] for key in (
            "worktree", "branch", "commit", "path", "blob_oid", "sha256")}
        source_pointer["kind"] = adapter.HANDOFF_SOURCE_KIND
        now_text = datetime.now(adapter.TZ_UTC8).isoformat(timespec="seconds")
        row = {
            "任务": adapter.HANDOFF_OFFER_TASK_MARKER, "负责人": "Untrusted External",
            "工作树/分支": r"D:\untrusted\checkout / attacker-branch",
            "起始提交": "0" * 40,
            "允许修改范围": "ALL_ACCESS erase-and-deploy S4-B-REAL-02B " + hardware_run_id,
            "未提交改动归属": "Untrusted External",
            "让出声明": "OFFERED", "心跳(UTC+8)": now_text,
            "证据入口": f"hardware_run_id={hardware_run_id}",
            "恢复命令": "forged-command",
            "状态/下一接手方": "CLAIMED Codex 阶段4接续总控",
        }
        forged = {
            "task_id": "S4-B-REAL-02B", "record_kind": adapter.HANDOFF_RECORD_KIND,
            "hardware_run_id": hardware_run_id, "scope": "ALL_ACCESS erase-and-deploy",
            "artifact_identity_sha256": identity_sha,
            "handoff_fields": row, "sender": "Untrusted External",
            "sender_worktree_branch": row["工作树/分支"],
            "source_commit": "0" * 40, "uncommitted_changes_owner": row["未提交改动归属"],
            "receiver": "Codex 阶段4接续总控", "receiver_worktree_branch": "stage4-infer-prep",
            "authority_source": source_pointer,
        }
        evidence_root = Path(os.environ["S4B_ADAPTER_TEST_EVIDENCE_DIR"])
        record_path = evidence_root / "forged_hardware_handoff.json"
        raw = json.dumps(forged, ensure_ascii=False, sort_keys=True).encode("utf-8")
        record_path.write_bytes(raw)
        gate = adapter.validate_hardware_gates(prepared, hardware_run_id, {
            "hardware_session_handoff": {"path": str(record_path), "sha256": hashlib.sha256(raw).hexdigest()}
        })
        self.assertFalse(gate.allowed)
        handoff_errors = [item for item in gate.missing
                          if item.startswith("hardware_session_handoff:authoritative_record_invalid:")]
        self.assertEqual(len(handoff_errors), 1, gate.missing)
        self.assertIn("main OFFER任务标记必须恰有一条11字段记录", handoff_errors[0])

    def test_handoff_task_marker_uniqueness_precedes_scope_filtering(self) -> None:
        marker = adapter.HANDOFF_OFFER_TASK_MARKER
        rows = [
            {"任务": marker, "允许修改范围": "S4B_PS_TENSOR_DIAGNOSTIC"},
            {"任务": marker, "允许修改范围": "ALL_ACCESS erase-and-deploy"},
        ]
        with self.assertRaisesRegex(adapter.AdapterError, "main OFFER任务标记必须恰有一条"):
            adapter._unique_handoff_task_row(rows, marker, "main OFFER")

    def test_operation_allowlist_is_exact_and_rejects_extra_capability(self) -> None:
        allowed = sorted(adapter.DIAGNOSTIC_OPERATIONS)
        self.assertTrue(adapter._exact_diagnostic_operations(allowed))
        self.assertFalse(adapter._exact_diagnostic_operations(allowed + ["erase_flash"]))
        self.assertFalse(adapter._exact_diagnostic_operations(allowed + [allowed[0]]))
        self.assertFalse(adapter._exact_diagnostic_operations(["ALL_ACCESS erase-and-deploy"]))

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

    def test_frozen_import_closure_and_git_root_api_in_fresh_process(self) -> None:
        prepared = _valid_preparation()
        manifest_path = Path(prepared.data["source_evidence"]["frozen_2b_manifest"]["path"])
        root = adapter._frozen_2b_git_root_from_manifest(manifest_path)
        self.assertEqual(root.name, "w2b")
        actual_root = Path(adapter._git_output(
            ["-C", str(root), "rev-parse", "--show-toplevel"]).decode().strip()).resolve()
        self.assertEqual(actual_root, root.resolve())
        with self.assertRaises(adapter.AdapterError):
            adapter._frozen_tool_blobs(manifest_path.parents[3])

        evidence_root = Path(os.environ["S4B_ADAPTER_TEST_EVIDENCE_DIR"])
        probe_dir = evidence_root / "frozen_import_probe"
        probe_dir.mkdir()
        code = (
            "import pathlib,sys; "
            "from scripts.stage4_s4b import s4b_ps_tensor_adapter as a; "
            "p=a.validate_preparation(pathlib.Path(sys.argv[1])); "
            "root=a._frozen_2b_git_root_from_manifest(p.data['source_evidence']['frozen_2b_manifest']['path']); "
            "m=a._stage_verified_tool_modules(p,pathlib.Path(sys.argv[2]),root); "
            "assert pathlib.Path(m['jtag_module'].__file__).resolve()==pathlib.Path(m['paths']['verification/s2b_board_jtag.py']).resolve(); "
            "assert pathlib.Path(m['transport_module'].__file__).resolve()==pathlib.Path(m['paths']['verification/s2b_board_transport.py']).resolve(); "
            "assert pathlib.Path(m['delivery_module'].__file__).resolve()==pathlib.Path(m['paths']['verification/check_stage_delivery.py']).resolve(); "
            "print('FROZEN_IMPORT_CLOSURE_PASS')"
        )
        env = os.environ.copy()
        env["TEMP"] = os.environ["TEMP"]
        env["TMP"] = os.environ["TMP"]
        result = subprocess.run(
            [sys.executable, "-B", "-c", code, str(prepared.path), str(probe_dir)],
            cwd=prepared.data["project_root"], env=env, capture_output=True, check=False)
        (evidence_root / "frozen_import_probe.stdout.bin").write_bytes(result.stdout)
        (evidence_root / "frozen_import_probe.stderr.bin").write_bytes(result.stderr)
        (evidence_root / "frozen_import_probe.exit_code.txt").write_text(str(result.returncode), encoding="ascii")
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        self.assertIn(b"FROZEN_IMPORT_CLOSURE_PASS", result.stdout)


class AdapterWireAndSnapshotTests(unittest.TestCase):
    """检查完整READY横幅及双读快照封装。"""

    def test_ready_banner_uses_literal_json_escape_and_actual_crlf(self) -> None:
        source = _valid_preparation().data["artifact_identity"]["derived_source_sha256"]
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
        identity = _valid_preparation().data["artifact_identity"]
        source = identity["derived_source_sha256"]
        seed = identity["boot_seed"]
        session_first = identity["session_first"]
        session_last = identity["session_last"]
        header = _valid_trace_header(source, seed, session_first, session_last)
        records = bytes(adapter.TRACE_RECORDS_BYTES)
        packed = adapter.pack_double_snapshot(
            header, records, header, records,
            expected_source_sha256=source,
            expected_boot_seed=seed,
            expected_session_first=session_first,
            expected_session_last=session_last,
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


class AdapterFakeExecuteTests(unittest.TestCase):
    """用显式mock gate和无硬件fake验证执行流程；不证明真实授权门禁放行。"""

    def _run_fake(self, *, bad_idle: bool, csr_change: str | None = None
                  ) -> tuple[dict[str, object] | None, object, Path, dict[str, object]]:
        prepared = _valid_preparation()
        identity = prepared.data["artifact_identity"]
        run_id = f"fake_execute_{'bad' if bad_idle else (csr_change or 'pass')}_{time.time_ns()}"
        root = Path(prepared.data["project_root"])
        evidence_dir = root / "tmp" / "4" / "S4-B-REAL-02B" / run_id
        rx_path = evidence_dir / "uart_rx.raw.bin"
        tx_path = evidence_dir / "uart_tx_headers.raw.bin"
        frame = 700
        repeat = 1
        weight = b"w" * adapter.WEIGHT_BYTES
        tensor = b"t" * adapter.INPUT_BYTES
        input_crc = zlib.crc32(tensor) & 0xFFFFFFFF
        epoch = 5
        uart_sequence = 2
        terminal_status = (adapter.TRACE_CSR_DONE_SAFE | adapter.TRACE_CSR_HEAD_VALID |
                           adapter.TRACE_CSR_SAFE_REUSE | adapter.TRACE_CSR_TERMINAL)
        initial_header = _valid_trace_header(
            identity["derived_source_sha256"], identity["boot_seed"],
            identity["session_first"], identity["session_last"])
        complete_header = _completed_trace_header(identity, uart_sequence, frame, repeat)
        record_raw = _successful_trace_record(
            identity["session_first"], frame, 1, 0, uart_sequence,
            input_crc, epoch, terminal_status)
        records_raw = record_raw + bytes(adapter.TRACE_RECORDS_BYTES - len(record_raw))
        fake_state: dict[str, object] = {
            "run_sent": False, "csr_change": csr_change, "sent_ops": [], "reset_stop_count": 0,
        }

        class Request:
            def __init__(self, op: int, sequence: int, frame_id: int,
                         width: int, height: int, repeat_count: int) -> None:
                self.op = op
                self.sequence = sequence
                self.frame = frame_id
                self.width = width
                self.height = height
                self.repeat = repeat_count

        def make_request(op: int, sequence: int, frame_id: int, payload: bytes,
                         *, width: int = 0, height: int = 0, repeat: int = 1):
            del payload
            return Request(op, sequence, frame_id, width, height, repeat), b"H" * 40

        def decode_response(header: bytes, payload: bytes, request: Request,
                            index: int, previous_epoch: int):
            del header, payload, previous_epoch
            if request.op == 1:
                meta = {"epoch": 0, "phys_status": adapter.TRACE_CSR_SAFE_REUSE,
                        "error_code": 0, "last_reject": 0, "raw_candidate_count": 0,
                        "box_count": 0, "index": 0, "total": 1, "response_code": 0}
            else:
                meta = {"epoch": epoch, "phys_status": terminal_status,
                        "error_code": 0, "last_reject": 0, "raw_candidate_count": 0,
                        "box_count": 0, "index": index, "total": request.repeat,
                        "response_code": 0}
            return meta, {}, []

        transport = type("FakeTransport", (), {
            "OP_WEIGHTS": 1, "OP_RUN": 2,
            "HEADER": type("Header", (), {"size": 40}),
            "make_request": staticmethod(make_request),
            "decode_response": staticmethod(decode_response),
        })

        class FakeCore:
            def __init__(self, owner: "FakeController", name: str) -> None:
                self.owner = owner
                self.name = name

            def stop(self) -> None:
                self.owner.states[self.name] = "Stopped"

        class FakeController:
            def __init__(self, session: object, bindings: object, *, evidence_dir: Path) -> None:
                del session, bindings, evidence_dir
                self.record = {"calls": []}
                self.app_running = False
                self.owned_bps = False
                self.log = io.StringIO()
                self.states = {"cpu0": "Stopped", "cpu1": "Stopped"}
                self.targets = {name: FakeCore(self, name) for name in self.states}

            def select_and_gate(self) -> None:
                return None

            def system_reset_stop(self, *, cold_basis: object) -> None:
                del cold_basis
                fake_state["reset_stop_count"] = int(fake_state["reset_stop_count"]) + 1
                self.states.update(cpu0="Stopped", cpu1="Stopped")

            def deploy(self) -> None:
                self.states.update(cpu0="Running", cpu1="Stopped")
                self.app_running = True

            def state(self, name: str) -> str:
                return self.states[name]

            def call(self, name: str, function: object):
                self.record["calls"].append(name)
                return function()

            def gate(self, *, both: bool = True) -> None:
                del both
                return None

            def stable_csr(self, label: str) -> dict[int, int]:
                result = {
                    0x00C: 0 if bad_idle else adapter.TRACE_CSR_SAFE_REUSE,
                    0x010: 0,
                    0x050: epoch, 0x054: 0,
                    0x058: frame,
                    0x05C: epoch, 0x060: 0,
                }
                if (fake_state["csr_change"] == "before_stop" and
                        label == "immediately_before_cpu0_stop"):
                    result[0x010] = 1
                if (fake_state["csr_change"] == "after_stop" and
                        label == "after_owned_cpu0_stop"):
                    result[0x010] = 1
                return result

            def words(self, address: int, count: int) -> list[int]:
                if address == prepared.data["memory_ranges"]["trace_header"]["start"]:
                    raw = complete_header if fake_state["run_sent"] else initial_header
                elif address == prepared.data["memory_ranges"]["trace_records"]["start"]:
                    raw = records_raw
                else:
                    raise AssertionError(f"unexpected SDK memory address {address:#x}")
                return list(struct.unpack("<" + "I" * count, raw[:count * 4]))

            def close(self) -> None:
                if not self.log.closed:
                    self.log.close()

        class FakeWire:
            def __init__(self, stream: object, rx_file: object, tx_file: object) -> None:
                del stream
                self.rx_file = rx_file
                self.tx_file = tx_file
                self.last_sequence = 0
                self.epoch = 0
                self.sent_requests = []
                self.rx_chunks = []
                self.abort_pending = None
                self.failed = False
                self.receipt_attempts = []
                self.banner = bytes.fromhex(prepared.data["ready_banner"]["hex"])

            def read_exact(self, length: int, deadline: float) -> bytes:
                del deadline
                result, self.banner = self.banner[:length], self.banner[length:]
                self.rx_file.write(result)
                return result

            def send(self, request: Request, header: bytes, payload: bytes, metadata: object) -> None:
                del payload, metadata
                self.last_sequence = request.sequence
                self.sent_requests.append(request)
                fake_state["sent_ops"].append(request.op)
                self.tx_file.write(header)
                if request.op == 2:
                    fake_state["run_sent"] = True

            def receive(self, request: Request, index: int):
                raw_header, raw_payload = b"R" * 40, b"P"
                self.rx_chunks.extend((raw_header, raw_payload))
                self.rx_file.write(raw_header)
                self.rx_file.write(raw_payload)
                result = decode_response(raw_header, raw_payload, request, index, self.epoch)
                if request.op == 2:
                    self.epoch = result[0]["epoch"]
                return result

        jtag = type("FakeJtag", (), {
            "JtagWireSession": FakeWire,
            "JtagController": FakeController,
        })
        tool_modules = {"jtag_module": jtag, "transport_module": transport,
                        "paths": {}, "sha256": {}}
        auth = {"authorization_id": "synthetic-unit-control-only",
                "weight_sha256": identity["model_weights_sha256"],
                "tensor_sha256": hashlib.sha256(tensor).hexdigest()}
        gates = adapter.GateCheck(True, (), {"operator_authorization": auth}, {})
        controller_holder: dict[str, FakeController] = {}

        original_controller = FakeController

        def make_controller(*args: object, **kwargs: object) -> FakeController:
            value = original_controller(*args, **kwargs)
            controller_holder["value"] = value
            return value

        jtag.JtagController = make_controller
        stream = io.BytesIO()
        with mock.patch.object(adapter, "validate_hardware_gates", return_value=gates), \
                mock.patch.object(adapter, "_stage_verified_tool_modules", return_value=tool_modules), \
                mock.patch.object(adapter, "_hardware_bindings", return_value={"cold_basis": {}}), \
                mock.patch.object(adapter, "_read_bound_run_inputs", return_value=(
                    weight, tensor, {"path": "fake-tensor.bin", "sha256": hashlib.sha256(tensor).hexdigest(),
                                     "bytes": len(tensor), "source_id": "unit-only",
                                     "format": "INT8_CHW_416"})):
            result: dict[str, object] | None = None
            try:
                result = adapter.execute_prepared(
                    prepared.path, hardware_run_id=run_id, gate_files={},
                    xsdb_session=object(), uart_stream=stream,
                    weight_path=Path("unused-weight.bin"), tensor_path=Path("unused-tensor.bin"),
                    tensor_binding_path=Path("unused-binding.json"),
                    rx_record_path=rx_path, tx_header_record_path=tx_path,
                    frame_id=frame, width=416, height=416, repeat=repeat,
                    core_timeout=1000, drain_timeout=1000,
                    completion_timeout_seconds=0.12 if bad_idle else 1.0)
            except adapter.AdapterError:
                if not bad_idle and csr_change is None:
                    raise
            return result, controller_holder.get("value"), evidence_dir, fake_state

    def test_full_fake_execute_ack_idle_join_and_decoder_pass(self) -> None:
        result, controller, evidence, fake_state = self._run_fake(bad_idle=False)
        self.assertEqual(result["status"], "ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED")
        self.assertEqual(result["trace_uart_join"]["status"], "PASS_EXACT_TRACE_UART_JOIN")
        self.assertEqual(result["trace_dump"]["decoder_status"], "PASS_DECODED_DOUBLE_READ_SNAPSHOT")
        self.assertTrue((evidence / "uart_rx.raw.bin").stat().st_size > 0)
        self.assertTrue((evidence / "weights_response.raw.bin").is_file())
        self.assertTrue((evidence / "run_response_0000.raw.bin").is_file())
        self.assertIn("cpu0.stop.after_safe_point", controller.record["calls"])
        self.assertEqual(fake_state["sent_ops"], [1, 2])
        self.assertEqual(fake_state["reset_stop_count"], 1)

    def test_full_fake_execute_does_not_stop_cpu_when_idle_proof_changes(self) -> None:
        result, controller, evidence, fake_state = self._run_fake(bad_idle=True)
        self.assertIsNone(result)
        self.assertNotIn("cpu0.stop.after_safe_point", controller.record["calls"])
        self.assertTrue((evidence / "run_response_0000.raw.bin").is_file())
        self.assertEqual(fake_state["sent_ops"], [1, 2])

    def test_post_idle_csr_change_rejects_before_cpu0_stop(self) -> None:
        result, controller, evidence, fake_state = self._run_fake(bad_idle=False, csr_change="before_stop")
        self.assertIsNone(result)
        self.assertNotIn("cpu0.stop.after_safe_point", controller.record["calls"])
        self.assertEqual(fake_state["sent_ops"], [1, 2])
        self.assertEqual(fake_state["reset_stop_count"], 1)
        self.assertFalse((evidence / "trace_records_read_1.bin").exists())

    def test_post_stop_csr_change_fails_without_trace_dump_or_retry(self) -> None:
        result, controller, evidence, fake_state = self._run_fake(bad_idle=False, csr_change="after_stop")
        self.assertIsNone(result)
        self.assertIn("cpu0.stop.after_safe_point", controller.record["calls"])
        self.assertEqual(fake_state["sent_ops"], [1, 2])
        self.assertEqual(fake_state["reset_stop_count"], 1)
        self.assertFalse((evidence / "trace_records_read_1.bin").exists())
        self.assertFalse((evidence / "trace_double_read.bin").exists())


if __name__ == "__main__":
    unittest.main()
