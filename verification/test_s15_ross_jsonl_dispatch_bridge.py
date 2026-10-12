"""离线验证S15外层ROSS派发JSONL桥的严格permit与MCP结果绑定。"""
from __future__ import annotations

import hashlib
import json
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import s15_ross_jsonl_dispatch_bridge as bridge_module
import s15_ross_job_guard as ross_guard


class FakeExchange:
    """用纯内存响应替代真实外层MCP，供协议拒绝用例使用。"""

    def __init__(self, make_response):
        self.make_response = make_response
        self.calls = 0

    def exchange(self, request_line: bytes, timeout_seconds: float) -> bytes:
        self.calls += 1
        request = bridge_module._parse_jsonl_frame(request_line, "测试permit")
        return self.make_response(request)

    def finish(self, request_id: str, accepted: bool) -> None:
        return None

    def abort(self) -> None:
        return None


def make_receipt(sequence: int = 0) -> dict:
    """生成与guard callback结构相同的纯本地receipt。"""
    now = time.monotonic()
    command = "open_checkpoint {C:/fixture/candidate.dcp}" if sequence == 0 else "write_bitstream -force {C:/fixture/out.bit}"
    return {
        "kind": "ROSS_DISPATCH_PERMIT",
        "controller_id": bytes(range(32)),
        "permit_nonce": bytes((index + sequence) % 256 for index in range(32)),
        "session_id": "vivado-offline-fixture-session",
        "sequence": sequence,
        "command": command,
        "command_sha256": hashlib.sha256(command.encode("utf-8")).hexdigest(),
        "dcp_sha256": ross_guard.DCP_SHA256 if sequence == 0 else None,
        "output_path": None if sequence == 0 else r"C:\fixture\out.bit",
        "issued_monotonic": now - 0.01,
        "claimed_monotonic": now,
        "mcp_call_required_by_outer_controller": True,
    }


def make_owner(receipt: dict):
    """构造只用于离线fixture的guard实例状态，不启动Job或Vivado。"""
    owner = object.__new__(ross_guard.RossJobGuardController)
    owner._controller_id = receipt["controller_id"]
    owner.expected_session_id = receipt["session_id"]
    owner._pending_ack_nonce = receipt["permit_nonce"]
    owner._dispatch_lease_active = True
    owner.state = "WAIT_COMMAND"
    owner.command_index = receipt["sequence"]
    owner.pending_command = {
        "sequence": receipt["sequence"],
        "command": receipt["command"],
        "sha256": receipt["command_sha256"],
        "claimed_monotonic": receipt["claimed_monotonic"],
        "active_seen": False,
    }
    owner._command_texts = ["open_checkpoint {C:/fixture/candidate.dcp}"]
    owner._output_path = None if receipt["sequence"] == 0 else Path(receipt["output_path"])
    return owner


def make_result(is_error: bool = False) -> dict:
    """构造含完整content与结构化内容的纯本地CallToolResult。"""
    return {
        "content": [{"type": "text", "text": "MCP执行结果fixture"}],
        "structuredContent": {"accepted": True, "nested": [1, None, "完整"]},
        "isError": is_error,
        "_meta": {"capture": "fixture"},
    }


class DispatchBridgeTests(unittest.TestCase):
    """覆盖许可接受、真实结果哈希及fail-closed边界。"""

    def _response(self, request: dict, **overrides) -> bytes:
        fields = {
            "actual_tool_id": request["tool_id"],
            "actual_arguments": request["arguments"],
            "call_tool_result": make_result(),
        }
        fields.update(overrides)
        return bridge_module.encode_dispatch_result(request, **fields)

    def _bridge_for_response(self, make_response, timeout: float = 0.2, receipt: dict | None = None):
        owner = make_owner(receipt if receipt is not None else make_receipt())
        exchange = FakeExchange(make_response)
        callback = bridge_module.JsonlDispatchBridge(
            owner,
            exchange,
            timeout_seconds=timeout,
        )
        return owner, exchange, callback

    def test_live_broker_accepts_exact_call_and_hashes_complete_result_bytes(self) -> None:
        receipt = make_receipt(0)
        owner = make_owner(receipt)
        broker = bridge_module.JsonlDispatchBroker()
        callback = bridge_module.JsonlDispatchBridge(owner, broker, timeout_seconds=0.5)
        result = make_result()
        calls: list[tuple[str, dict]] = []
        service_error: list[BaseException] = []

        def invoke(tool_id: str, arguments: dict) -> object:
            calls.append((tool_id, arguments))
            return result

        def serve() -> None:
            try:
                broker.serve_one(invoke, timeout_seconds=0.5)
            except BaseException as error:
                service_error.append(error)

        service = threading.Thread(target=serve, daemon=True)
        service.start()
        ack = callback(receipt)
        service.join(timeout=1.0)

        expected_arguments = {"session_id": receipt["session_id"], "command": receipt["command"]}
        result_bytes = json.dumps(result, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        self.assertFalse(service.is_alive())
        self.assertEqual(service_error, [])
        self.assertEqual(calls, [(bridge_module.EXECUTE_TOOL_ID, expected_arguments)])
        self.assertIs(type(ack), ross_guard.DispatchAck)
        self.assertIs(ack.owner, owner)
        self.assertEqual(ack.controller_id, receipt["controller_id"])
        self.assertEqual(ack.permit_nonce, receipt["permit_nonce"])
        self.assertEqual(ack.session_id, receipt["session_id"])
        self.assertEqual(ack.sequence, 0)
        self.assertEqual(ack.command, receipt["command"])
        self.assertEqual(ack.command_sha256, receipt["command_sha256"])
        self.assertEqual(ack.dcp_sha256, receipt["dcp_sha256"])
        self.assertEqual(ack.outcome, "ACCEPTED")
        self.assertEqual(ack.response_sha256, hashlib.sha256(result_bytes).hexdigest())
        self.assertEqual(callback.last_call_tool_result_json.encode("utf-8"), result_bytes)
        self.assertEqual(callback.last_call_tool_result, result)

    def test_broker_supports_only_ordered_unique_two_permit_sequence(self) -> None:
        receipt0 = make_receipt(0)
        owner = make_owner(receipt0)
        broker = bridge_module.JsonlDispatchBroker()
        callback = bridge_module.JsonlDispatchBridge(owner, broker, timeout_seconds=0.5)
        calls: list[tuple[str, dict]] = []
        errors: list[BaseException] = []

        def service_one() -> None:
            try:
                broker.serve_one(lambda tool, args: (calls.append((tool, args)) or make_result()), 0.5)
            except BaseException as error:
                errors.append(error)

        first = threading.Thread(target=service_one, daemon=True)
        first.start()
        ack0 = callback(receipt0)
        first.join(timeout=1.0)
        receipt1 = make_receipt(1)
        owner._controller_id = receipt1["controller_id"]
        owner._pending_ack_nonce = receipt1["permit_nonce"]
        owner.command_index = receipt1["sequence"]
        owner.pending_command = {
            "sequence": receipt1["sequence"],
            "command": receipt1["command"],
            "sha256": receipt1["command_sha256"],
            "claimed_monotonic": receipt1["claimed_monotonic"],
            "active_seen": False,
        }
        owner._output_path = Path(receipt1["output_path"])
        second = threading.Thread(target=service_one, daemon=True)
        second.start()
        ack1 = callback(receipt1)
        second.join(timeout=1.0)
        self.assertEqual(errors, [])
        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual((ack0.sequence, ack1.sequence), (0, 1))
        self.assertEqual([item[0] for item in calls], [bridge_module.EXECUTE_TOOL_ID] * 2)
        with self.assertRaises(bridge_module.DispatchBridgeError):
            callback(make_receipt(1))

    def test_two_bridges_cannot_dispatch_same_owner_nonce_concurrently(self) -> None:
        receipt = make_receipt(0)
        owner = make_owner(receipt)
        brokers = [bridge_module.JsonlDispatchBroker(), bridge_module.JsonlDispatchBroker()]
        callbacks = [
            bridge_module.JsonlDispatchBridge(owner, broker, timeout_seconds=0.5)
            for broker in brokers
        ]
        start = threading.Event()
        calls: list[tuple[str, dict]] = []
        acknowledgements: list[ross_guard.DispatchAck] = []
        callback_errors: list[BaseException] = []
        service_errors: list[BaseException] = []

        def invoke(tool_id: str, arguments: dict) -> object:
            calls.append((tool_id, arguments))
            return make_result()

        def serve(broker: bridge_module.JsonlDispatchBroker) -> None:
            try:
                broker.serve_one(invoke, timeout_seconds=0.75)
            except BaseException as error:
                service_errors.append(error)

        def dispatch(callback: bridge_module.JsonlDispatchBridge) -> None:
            start.wait()
            try:
                acknowledgements.append(callback(receipt))
            except BaseException as error:
                callback_errors.append(error)

        services = [threading.Thread(target=serve, args=(broker,), daemon=True) for broker in brokers]
        clients = [threading.Thread(target=dispatch, args=(callback,), daemon=True) for callback in callbacks]
        for thread in services + clients:
            thread.start()
        start.set()
        for thread in clients + services:
            thread.join(timeout=1.5)

        self.assertTrue(all(not thread.is_alive() for thread in clients + services))
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(acknowledgements), 1)
        self.assertEqual(len(callback_errors), 1)
        self.assertEqual(len(service_errors), 1)
        self.assertEqual(sum(callback._poisoned for callback in callbacks), 1)
        self.assertEqual(sum(broker._poisoned for broker in brokers), 1)

    def test_close_or_abort_before_final_dispatch_claim_blocks_mcp(self) -> None:
        for close_method in ("close", "abort"):
            with self.subTest(close_method=close_method):
                receipt = make_receipt(0)
                owner = make_owner(receipt)
                broker = bridge_module.JsonlDispatchBroker()
                callback = bridge_module.JsonlDispatchBridge(owner, broker, timeout_seconds=2.0)
                claim_entered = threading.Event()
                resume_claim = threading.Event()
                calls: list[tuple[str, dict]] = []
                callback_errors: list[BaseException] = []
                service_errors: list[BaseException] = []
                original_claim = broker._invoke_current_pending

                def delayed_claim(bridge, request, invoke_mcp):
                    claim_entered.set()
                    if not resume_claim.wait(timeout=1.0):
                        raise TimeoutError("测试未恢复最终派发claim")
                    return original_claim(bridge, request, invoke_mcp)

                def invoke(tool_id: str, arguments: dict) -> object:
                    calls.append((tool_id, arguments))
                    return make_result()

                def serve() -> None:
                    try:
                        broker.serve_one(invoke, timeout_seconds=3.0)
                    except BaseException as error:
                        service_errors.append(error)

                def dispatch() -> None:
                    try:
                        callback(receipt)
                    except BaseException as error:
                        callback_errors.append(error)

                with patch.object(broker, "_invoke_current_pending", delayed_claim):
                    server = threading.Thread(target=serve, daemon=True)
                    client = threading.Thread(target=dispatch, daemon=True)
                    server.start()
                    client.start()
                    try:
                        self.assertTrue(claim_entered.wait(timeout=1.0))
                        self.assertIsNotNone(broker._pending)
                        self.assertTrue(broker._pending.served)
                        getattr(broker, close_method)()
                    finally:
                        if not broker._closed and not broker._poisoned:
                            broker.close()
                        resume_claim.set()
                        client.join(timeout=2.5)
                        server.join(timeout=2.5)

                self.assertFalse(client.is_alive())
                self.assertFalse(server.is_alive())
                self.assertEqual(calls, [])
                self.assertEqual(len(callback_errors), 1)
                self.assertEqual(len(service_errors), 1)
                self.assertFalse(broker._pending.dispatch_claimed)
                self.assertTrue(broker._closed or broker._poisoned)

    def test_closed_handler_rejects_legacy_noop_claim_and_never_calls_mcp(self) -> None:
        for close_method in ("close", "abort"):
            with self.subTest(close_method=close_method):
                receipt = make_receipt(0)
                owner = make_owner(receipt)
                broker = bridge_module.JsonlDispatchBroker()
                callback = bridge_module.JsonlDispatchBridge(owner, broker, timeout_seconds=0.5)
                request, request_line = bridge_module.build_dispatch_request(receipt, 0)
                callback._dispatch_active = True
                callback._active_request = request
                calls: list[tuple[str, dict]] = []

                def invoke(tool_id: str, arguments: dict) -> object:
                    calls.append((tool_id, arguments))
                    return make_result()

                getattr(broker, close_method)()

                with self.assertRaises(TypeError):
                    bridge_module.handle_one_jsonl_request(
                        request_line,
                        invoke,
                        bridge=callback,
                        dispatch_claim=lambda _request: None,
                    )
                self.assertEqual(calls, [])

                with self.assertRaises(bridge_module.DispatchBridgeError):
                    bridge_module.handle_one_jsonl_request(
                        request_line,
                        invoke,
                        bridge=callback,
                    )
                self.assertEqual(calls, [])
                self.assertTrue(callback._poisoned)
                self.assertTrue(broker._closed or broker._poisoned)

    def test_direct_handler_rejects_sequence_zero_without_live_bridge(self) -> None:
        receipt = make_receipt(0)
        forged = dict(receipt)
        forged["command"] = "close_project"
        forged["command_sha256"] = hashlib.sha256(b"close_project").hexdigest()
        _, request_line = bridge_module.build_dispatch_request(forged, 0)
        seen: list[tuple[str, dict]] = []

        def invoke(tool_id: str, arguments: dict) -> object:
            seen.append((tool_id, arguments))
            return make_result()

        with self.assertRaises(bridge_module.DispatchBridgeError):
            bridge_module.handle_one_jsonl_request(request_line, invoke)
        self.assertEqual(seen, [])

    def test_direct_broker_rejects_forged_sequence_zero_and_closes_before_mcp(self) -> None:
        approved = make_receipt(0)
        forged = dict(approved)
        forged["command"] = "close_project"
        forged["command_sha256"] = hashlib.sha256(b"close_project").hexdigest()
        _, request_line = bridge_module.build_dispatch_request(forged, 0)
        owner = make_owner(approved)
        broker = bridge_module.JsonlDispatchBroker()
        callback = bridge_module.JsonlDispatchBridge(owner, broker, timeout_seconds=0.5)
        calls: list[tuple[str, dict]] = []
        exchange_errors: list[BaseException] = []
        service_errors: list[BaseException] = []

        def exchange() -> None:
            try:
                broker.exchange(request_line, 0.5)
            except BaseException as error:
                exchange_errors.append(error)

        def invoke(tool_id: str, arguments: dict) -> object:
            calls.append((tool_id, arguments))
            return make_result()

        def serve() -> None:
            try:
                broker.serve_one(invoke, timeout_seconds=0.5)
            except BaseException as error:
                service_errors.append(error)

        client = threading.Thread(target=exchange, daemon=True)
        server = threading.Thread(target=serve, daemon=True)
        client.start()
        server.start()
        client.join(timeout=1.0)
        server.join(timeout=1.0)

        self.assertFalse(client.is_alive())
        self.assertFalse(server.is_alive())
        self.assertEqual(calls, [])
        self.assertEqual(len(exchange_errors), 1)
        self.assertEqual(len(service_errors), 1)
        self.assertTrue(broker._poisoned)
        self.assertTrue(callback._poisoned)

    def test_unbound_broker_service_fails_closed_without_mcp_call(self) -> None:
        broker = bridge_module.JsonlDispatchBroker()
        calls: list[bool] = []
        with self.assertRaises(bridge_module.DispatchBridgeError):
            broker.serve_one(lambda *_: (calls.append(True) or make_result()), timeout_seconds=0.1)
        self.assertEqual(calls, [])
        self.assertTrue(broker._poisoned)

    def test_missing_extra_bad_type_or_out_of_order_receipt_fails_before_exchange(self) -> None:
        invalid_receipts = []
        missing = make_receipt()
        missing.pop("command_sha256")
        invalid_receipts.append(missing)
        extra = make_receipt()
        extra["task_progress"] = "not identity"
        invalid_receipts.append(extra)
        wrong_bool = make_receipt()
        wrong_bool["sequence"] = True
        invalid_receipts.append(wrong_bool)
        wrong_nonce = make_receipt()
        wrong_nonce["permit_nonce"] = b"short"
        invalid_receipts.append(wrong_nonce)
        wrong_command_hash = make_receipt()
        wrong_command_hash["command"] += " "
        invalid_receipts.append(wrong_command_hash)
        bridge = bridge_module.JsonlDispatchBridge(
            make_owner(make_receipt()), FakeExchange(lambda request: b""), timeout_seconds=0.1
        )
        for receipt in invalid_receipts:
            with self.subTest(receipt=receipt):
                new_bridge = bridge_module.JsonlDispatchBridge(
                    make_owner(make_receipt()), FakeExchange(lambda request: b""), timeout_seconds=0.1
                )
                with self.assertRaises(bridge_module.DispatchBridgeError):
                    new_bridge(receipt)
        with self.assertRaises(bridge_module.DispatchBridgeError):
            bridge(make_receipt(1))

    def test_receipt_must_match_live_guard_and_approved_command(self) -> None:
        original = make_receipt(0)
        invalid = []
        wrong_session = dict(original)
        wrong_session["session_id"] = "other-session"
        invalid.append(wrong_session)
        wrong_command = dict(original)
        wrong_command["command"] = "close_project"
        wrong_command["command_sha256"] = hashlib.sha256(b"close_project").hexdigest()
        invalid.append(wrong_command)
        wrong_dcp = dict(original)
        wrong_dcp["dcp_sha256"] = "0" * 64
        invalid.append(wrong_dcp)
        for receipt in invalid:
            with self.subTest(receipt=receipt):
                exchange = FakeExchange(lambda request: b"")
                callback = bridge_module.JsonlDispatchBridge(
                    make_owner(original), exchange, timeout_seconds=0.1
                )
                with self.assertRaises(bridge_module.DispatchBridgeError):
                    callback(receipt)
                self.assertEqual(exchange.calls, 0)

    def test_response_session_command_arguments_and_tool_markers_are_bound(self) -> None:
        receipt = make_receipt(0)
        cases = (
            ("session", {"receipt": {"session_id": "other-session"}}),
            ("command", {"receipt": {"command": "close_project"}}),
            ("tool", {"tool": "vivado_stop"}),
            ("tool-id", {"tool_id": "mcp__vivado_ross__vivado_stop"}),
            ("arguments", {"arguments": {"session_id": receipt["session_id"], "command": "wrong"}}),
        )
        for name, changes in cases:
            with self.subTest(name=name):
                def make_bad(request: dict, changes=changes) -> bytes:
                    response = self._response(request)
                    value = bridge_module._parse_jsonl_frame(response, "fixture")
                    for key, item in changes.items():
                        if key == "receipt":
                            value["receipt"].update(item)
                        else:
                            value[key] = item
                    return bridge_module._jsonl_bytes(value)

                _, exchange, callback = self._bridge_for_response(make_bad, receipt=receipt)
                with self.assertRaises(bridge_module.DispatchBridgeError):
                    callback(receipt)
                self.assertEqual(exchange.calls, 1)

    def test_response_receipt_rejects_bool_integer_sequence_confusion(self) -> None:
        for sequence, confused_value in ((0, False), (1, True)):
            receipt = make_receipt(sequence)

            def make_bad(request: dict, confused_value=confused_value) -> bytes:
                response = self._response(request)
                value = bridge_module._parse_jsonl_frame(response, "fixture")
                value["receipt"]["sequence"] = confused_value
                return bridge_module._jsonl_bytes(value)

            with self.subTest(sequence=sequence, confused_value=confused_value):
                _, exchange, callback = self._bridge_for_response(make_bad, receipt=receipt)
                callback.expected_sequence = sequence
                with self.assertRaises(bridge_module.DispatchBridgeError):
                    callback(receipt)
                self.assertEqual(exchange.calls, 1)
                self.assertTrue(callback._poisoned)

    def test_eof_duplicate_frame_malformed_json_duplicate_keys_and_hash_mismatch_fail(self) -> None:
        receipt = make_receipt(0)
        cases = {
            "eof": lambda request: b"",
            "duplicate-response": lambda request: self._response(request) * 2,
            "malformed-json": lambda request: b"{not-json}\n",
            "duplicate-key": lambda request: b'{"kind":"ROSS_DISPATCH_RESULT","kind":"duplicate"}\n',
            "hash-mismatch": lambda request: self._tampered_hash(self._response(request)),
        }
        for name, make_response in cases.items():
            with self.subTest(name=name):
                _, _, callback = self._bridge_for_response(make_response, receipt=receipt)
                with self.assertRaises(bridge_module.DispatchBridgeError):
                    callback(receipt)

    @staticmethod
    def _tampered_hash(response_line: bytes) -> bytes:
        value = bridge_module._parse_jsonl_frame(response_line, "fixture")
        value["response_sha256"] = "0" * 64
        return bridge_module._jsonl_bytes(value)

    def test_is_error_true_and_invalid_error_marker_fail_closed(self) -> None:
        receipt = make_receipt(0)
        for bad_result in (make_result(is_error=True), {"content": [], "isError": "true"}):
            with self.subTest(result=bad_result):
                _, _, callback = self._bridge_for_response(
                    lambda request, result=bad_result: bridge_module.encode_dispatch_result(
                        request,
                        request["tool_id"],
                        request["arguments"],
                        result,
                    ),
                    receipt=receipt,
                )
                with self.assertRaises(bridge_module.DispatchBridgeError):
                    callback(receipt)

    def test_timeout_is_bounded_and_never_retries(self) -> None:
        receipt = make_receipt(0)
        release = threading.Event()

        def delayed_response(request: dict) -> bytes:
            release.wait(0.5)
            return self._response(request)

        owner, exchange, callback = self._bridge_for_response(delayed_response, timeout=0.03, receipt=receipt)
        started = time.monotonic()
        with self.assertRaises(bridge_module.DispatchTimeout):
            callback(receipt)
        elapsed = time.monotonic() - started
        release.set()
        self.assertLess(elapsed, 0.2)
        self.assertEqual(exchange.calls, 1)
        with self.assertRaises(bridge_module.DispatchBridgeError):
            callback(receipt)

    def test_jsonl_request_rejects_extra_line_wrong_tool_and_wrong_arguments(self) -> None:
        receipt = make_receipt(0)
        request, request_line = bridge_module.build_dispatch_request(receipt, 0)
        with self.assertRaises(bridge_module.DispatchBridgeError):
            bridge_module.handle_one_jsonl_request(request_line + request_line, lambda *_: make_result())
        for field, bad_value in (
            ("tool", "vivado_stop"),
            ("tool_id", "mcp__vivado_ross__vivado_stop"),
            ("arguments", {"session_id": "other", "command": receipt["command"]}),
        ):
            with self.subTest(field=field):
                bad_request = dict(request)
                bad_request[field] = bad_value
                called: list[bool] = []
                with self.assertRaises(bridge_module.DispatchBridgeError):
                    bridge_module.handle_one_jsonl_request(
                        bridge_module._jsonl_bytes(bad_request),
                        lambda *_: (called.append(True) or make_result()),
                    )
                self.assertEqual(called, [])

    def test_broker_eof_before_permit_fails_closed(self) -> None:
        receipt = make_receipt()
        broker = bridge_module.JsonlDispatchBroker()
        callback = bridge_module.JsonlDispatchBridge(make_owner(receipt), broker, timeout_seconds=0.1)
        broker.close()
        with self.assertRaises(bridge_module.DispatchEOF):
            callback(receipt)

    def test_simultaneous_permits_are_rejected_without_second_exchange(self) -> None:
        receipt = make_receipt()
        gate = threading.Event()

        def slow_response(request: dict) -> bytes:
            gate.wait(0.3)
            return self._response(request)

        owner, exchange, callback = self._bridge_for_response(slow_response, timeout=0.08, receipt=receipt)
        first_error: list[BaseException] = []
        first = threading.Thread(
            target=lambda: self._capture(first_error, callback, receipt),
            daemon=True,
        )
        first.start()
        deadline = time.monotonic() + 0.1
        while exchange.calls == 0 and time.monotonic() < deadline:
            time.sleep(0.001)
        with self.assertRaises(bridge_module.DispatchBridgeError):
            callback(receipt)
        gate.set()
        first.join(timeout=0.5)
        self.assertEqual(exchange.calls, 1)
        self.assertFalse(first.is_alive())

    @staticmethod
    def _capture(errors: list[BaseException], callback, receipt: dict) -> None:
        try:
            callback(receipt)
        except BaseException as error:
            errors.append(error)


if __name__ == "__main__":
    unittest.main(verbosity=2)
