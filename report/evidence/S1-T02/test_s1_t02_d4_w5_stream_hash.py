"""W5 流式校验客户端的纯内存离线测试。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import socket
import subprocess
import sys
import tempfile
import threading
import textwrap
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).with_name("s1_t02_d4_w5_stream_hash.py")
SPEC = importlib.util.spec_from_file_location("w5_stream_hash", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
w5 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = w5
SPEC.loader.exec_module(w5)


class FakeClock:
    """可控单调时钟，用于不等待地覆盖超时分支。"""

    def __init__(self) -> None:
        self.value = 100.0

    def __call__(self) -> float:
        return self.value


class FakeResponse:
    """内存 HTTP 响应，不创建 socket。"""

    def __init__(
        self,
        status: int,
        headers: list[tuple[str, str]],
        body: bytes = b"",
        *,
        read_error: BaseException | None = None,
        clock: FakeClock | None = None,
        clock_advance: float = 0.0,
        on_read: Callable[[], None] | None = None,
        on_headers: Callable[[], None] | None = None,
    ) -> None:
        self.status = status
        self._headers = headers
        self._body = body
        self._read_error = read_error
        self._clock = clock
        self._clock_advance = clock_advance
        self._on_read = on_read
        self._on_headers = on_headers
        self._on_read_called = False
        self.read_sizes: list[int] = []
        self.closed = False

    def getheaders(self) -> list[tuple[str, str]]:
        if self._on_headers is not None:
            self._on_headers()
        return list(self._headers)

    def read1(self, size: int) -> bytes:
        self.read_sizes.append(size)
        if self._on_read is not None and not self._on_read_called:
            self._on_read_called = True
            self._on_read()
        if self._clock is not None and self._clock_advance:
            self._clock.value += self._clock_advance
        if self._read_error is not None:
            raise self._read_error
        block = self._body[:size]
        self._body = self._body[len(block) :]
        return block

    def read(self, size: int) -> bytes:
        raise AssertionError("完整 read() 会话式读取不允许用于网络响应")

    def close(self) -> None:
        self.closed = True


class FakeConnection:
    """保存请求元数据并返回预设响应，不进行网络访问。"""

    def __init__(
        self,
        response: FakeResponse,
        *,
        clock: FakeClock | None = None,
        request_advance: float = 0.0,
        getresponse_advance: float = 0.0,
        request_error: BaseException | None = None,
        getresponse_error: BaseException | None = None,
    ) -> None:
        self.response = response
        self.calls: list[tuple[str, str, dict[str, str]]] = []
        self.sock = None
        self.closed = False
        self._clock = clock
        self._request_advance = request_advance
        self._getresponse_advance = getresponse_advance
        self._request_error = request_error
        self._getresponse_error = getresponse_error

    def request(self, method: str, target: str, headers: dict[str, str]) -> None:
        self.calls.append((method, target, dict(headers)))
        if self._clock is not None:
            self._clock.value += self._request_advance
        if self._request_error is not None:
            raise self._request_error

    def getresponse(self) -> FakeResponse:
        if self._clock is not None:
            self._clock.value += self._getresponse_advance
        if self._getresponse_error is not None:
            raise self._getresponse_error
        return self.response

    def close(self) -> None:
        self.closed = True


class FakeTransport:
    """按顺序提供假响应并记录连接主机。"""

    def __init__(
        self,
        responses: list[FakeResponse],
        *,
        clock: FakeClock | None = None,
        connect_advance: float = 0.0,
        request_advance: float = 0.0,
        getresponse_advance: float = 0.0,
        request_error: BaseException | None = None,
        getresponse_error: BaseException | None = None,
    ) -> None:
        self.responses = list(responses)
        self.connections: list[FakeConnection] = []
        self.hosts: list[str] = []
        self.timeouts: list[float] = []
        self.clock = clock
        self.connect_advance = connect_advance
        self.request_advance = request_advance
        self.getresponse_advance = getresponse_advance
        self.request_error = request_error
        self.getresponse_error = getresponse_error

    def __call__(self, host: str, timeout: float) -> FakeConnection:
        if self.clock is not None:
            self.clock.value += self.connect_advance
        self.hosts.append(host)
        self.timeouts.append(timeout)
        response = self.responses[len(self.connections)]
        connection = FakeConnection(
            response,
            clock=self.clock,
            request_advance=self.request_advance,
            getresponse_advance=self.getresponse_advance,
            request_error=self.request_error,
            getresponse_error=self.getresponse_error,
        )
        self.connections.append(connection)
        return connection


class FlushTrackingStream(StringIO):
    """记录 JSONL 写入是否及时 flush。"""

    def __init__(self) -> None:
        super().__init__()
        self.flush_count = 0

    def flush(self) -> None:
        self.flush_count += 1
        super().flush()


def dependency_ok() -> tuple[bool, list[dict[str, object]]]:
    """用内存替身隔离静态文件依赖检查。"""

    return True, valid_dependency_bindings()


def valid_dependency_bindings() -> list[dict[str, object]]:
    """构造完整固定依赖集与独立权重测量元数据行。"""

    results: list[dict[str, object]] = [
        {
            "path": dependency.path,
            "expected_bytes": dependency.size,
            "expected_sha256": dependency.sha256,
            "observed_bytes": dependency.size,
            "observed_sha256": dependency.sha256,
            "matches": True,
        }
        for dependency in w5.DEPENDENCIES
    ]
    results.extend(
        {
            "path": dependency.path,
            "expected_state": "absent_at_frozen_baseline",
            "observed_state": "absent",
            "matches": True,
        }
        for dependency in w5.MISSING_BASELINE_SCRIPTS
    )
    results.append(
        {
            "path": "D:/FPGA_Data/darknet/weights/yolov4.conv.137",
            "expected_bytes": w5.EXPECTED_BYTES,
            "expected_sha256": w5.EXPECTED_SHA256,
            "verification_basis": "previous_read_only_measurement",
            "read_this_run": False,
            "verified_this_run": False,
        }
    )
    return results


def response_with_body(body: bytes, *, status: int = 200) -> FakeResponse:
    """创建含固定长度头的内存响应。"""

    return FakeResponse(status, [("Content-Length", str(len(body)))], body)


class W5StreamHashTests(unittest.TestCase):
    """验证 URL 边界、HTTP 语义、完整哈希与离线默认行为。"""

    @staticmethod
    def valid_worker_report() -> dict[str, object]:
        """构造与成功响应及本地绑定一致的合成 worker 报告。"""

        digest = hashlib.sha256(b"abc").hexdigest()
        report = w5._emergency_failure_report("unused")
        report.update(
            {
                "error_type": None,
                "exit_code": 0,
                "request_attempt_count": 1,
                "confirmed_get_count": 1,
                "http_response_count": 1,
                "actual_get_count": 1,
                "http_statuses": [200],
                "final_status": 200,
                "content_length": 3,
                "content_encoding": "identity",
                "bytes_read": 3,
                "sha256": digest,
                "expected_local_sha256": digest,
                "hash_matches": True,
                "dependency_bindings": valid_dependency_bindings(),
                "local_weight_binding": {
                    "expected_bytes": 3,
                    "expected_sha256": digest,
                    "matches_expected": True,
                    "stable": True,
                    "matches_remote": True,
                },
            }
        )
        return report

    @staticmethod
    def write_worker_result(path: Path, report: dict[str, object], *, exit_code: int = 0) -> None:
        """写入仅向 stdout 发合成结果的离线 worker。"""

        serialized_report = json.dumps(report, ensure_ascii=True, separators=(",", ":"))
        path.write_text(
            "import json, sys\n"
            "print(json.dumps({'kind':'result','report':json.loads("
            f"{serialized_report!r})}}), flush=True)\n"
            f"sys.exit({exit_code})\n",
            encoding="utf-8",
        )

    def run_fake(
        self,
        responses: list[FakeResponse],
        *,
        expected: bytes = b"abc",
        transport: FakeTransport | None = None,
        **options: object,
    ) -> tuple[dict[str, object], FakeTransport]:
        fake_transport = transport or FakeTransport(responses)
        with tempfile.TemporaryDirectory(prefix="w5-local-weight-") as temp_dir:
            local_path = Path(temp_dir) / "yolov4.conv.137"
            local_path.write_bytes(expected)
            local_weight_path = options.pop("local_weight_path", local_path)
            dependency_check = options.pop("dependency_check", dependency_ok)
            report = w5._verify_remote_asset_impl(
                connection_factory=fake_transport,
                dependency_check=dependency_check,
                local_weight_path=local_weight_path,
                expected_bytes=len(expected),
                expected_sha256=hashlib.sha256(expected).hexdigest(),
                chunk_size=options.pop("chunk_size", 8),
                **options,
            )
        return report, fake_transport

    def test_redirect_then_full_stream_matches_independent_hash(self) -> None:
        """302 到正式资产主机后完整流哈希与独立 hashlib 对照一致。"""

        body = b"synthetic-full-object-0123456789"
        redirect = FakeResponse(
            302,
            [
                (
                    "Location",
                    "https://release-assets.githubusercontent.com/file.bin?token=PRIVATE_SENTINEL",
                )
            ],
        )
        report, transport = self.run_fake(
            [redirect, response_with_body(body)], expected=body
        )
        independent = hashlib.sha256(body).hexdigest()
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["http_statuses"], [302, 200])
        self.assertEqual(report["request_attempt_count"], 2)
        self.assertEqual(report["http_response_count"], 2)
        self.assertEqual(report["confirmed_get_count"], 2)
        self.assertEqual(report["actual_get_count"], 2)
        self.assertEqual(report["redirect_count"], 1)
        self.assertEqual(report["bytes_read"], len(body))
        self.assertEqual(report["sha256"], independent)
        self.assertEqual(report["hash_matches"], True)
        self.assertEqual(
            transport.hosts,
            ["github.com", "release-assets.githubusercontent.com"],
        )
        self.assertTrue(
            all(timeout <= w5.MAX_SOCKET_TIMEOUT_SECONDS for timeout in transport.timeouts)
        )
        self.assertEqual(transport.connections[0].calls[0][0], "GET")
        self.assertNotIn("Range", transport.connections[0].calls[0][2])
        encoded = json.dumps(report, sort_keys=True)
        self.assertNotIn("PRIVATE_SENTINEL", encoded)
        self.assertNotIn("token=", encoded)
        self.assertEqual(redirect.closed, True)

    def test_default_and_help_modes_never_open_socket(self) -> None:
        """无参数与帮助模式不得构造连接或调用 socket。"""

        output = StringIO()
        with patch.object(w5, "_make_https_connection", side_effect=AssertionError):
            with patch.object(socket, "create_connection", side_effect=AssertionError):
                with redirect_stdout(output):
                    self.assertEqual(w5.main([]), 0)
                    self.assertEqual(w5.main(["--help"]), 0)
        self.assertIn("默认只显示帮助", output.getvalue())

    def test_direct_api_call_without_factory_is_not_authorized(self) -> None:
        """直接调用纯 API 默认拒绝网络且不读取本地权重或创建 socket。"""

        with patch.object(w5, "_make_https_connection", side_effect=AssertionError):
            with patch.object(socket, "create_connection", side_effect=AssertionError):
                with patch.object(w5, "_snapshot_local_weight", side_effect=AssertionError):
                    report = w5.verify_remote_asset()
        self.assertEqual(report["error_type"], "NetworkExecutionNotAuthorized")
        self.assertEqual(report["request_attempt_count"], 0)
        self.assertEqual(report["http_response_count"], 0)
        self.assertEqual(report["confirmed_get_count"], 0)
        self.assertEqual(report["actual_get_count"], 0)
        self.assertEqual(report["exit_code"], 1)

    def test_public_api_rejects_unisolated_custom_transport(self) -> None:
        """公共 API 不允许自定义同步 transport 绕过硬期限 worker。"""

        called = False

        def custom_transport(_host: str, _timeout: float) -> object:
            nonlocal called
            called = True
            raise AssertionError("不可调用自定义 transport")

        report = w5.verify_remote_asset(connection_factory=custom_transport)
        self.assertEqual(report["error_type"], "CustomTransportRejected")
        self.assertEqual(report["request_attempt_count"], 0)
        self.assertFalse(called)

    def test_explicit_https_api_routes_through_supervisor_without_network(self) -> None:
        """显式 HTTPS factory 只构造 worker 命令，由父级监督网络执行。"""

        captured: dict[str, object] = {}
        expected = w5._emergency_failure_report("TotalTimeoutError")

        def fake_supervisor(
            command: list[str],
            *,
            total_timeout: float,
            progress_callback: object,
            start_gate: bool,
        ) -> tuple[dict[str, object], dict[str, object]]:
            captured["command"] = command
            captured["total_timeout"] = total_timeout
            captured["progress_callback"] = progress_callback
            captured["start_gate"] = start_gate
            return expected, {"worker_terminated": True}

        callback = lambda _record: None
        with patch.object(w5, "_run_supervised_process", side_effect=fake_supervisor):
            report = w5.verify_remote_asset(
                connection_factory=w5._make_https_connection,
                total_timeout=0.25,
                progress_callback=callback,
            )

        self.assertIs(report, expected)
        command = captured["command"]
        self.assertEqual(command[1], "-c")
        self.assertEqual(command[3], str(SCRIPT_PATH.resolve()))
        self.assertNotIn("--internal-worker", command)
        self.assertEqual(captured["total_timeout"], 0.25)
        self.assertIs(captured["progress_callback"], callback)
        self.assertTrue(captured["start_gate"])

    def test_public_cli_rejects_internal_worker_arguments(self) -> None:
        """公开 CLI 拒绝内部 worker 参数，不能绕过父级监督器。"""

        output = StringIO()
        error = StringIO()
        with patch.object(w5, "_worker_process_main", side_effect=AssertionError):
            with redirect_stdout(output), redirect_stderr(error):
                code = w5.main(
                    ["--execute-network-request", "--internal-worker", "opaque-payload"]
                )

        self.assertEqual(code, 2)
        self.assertNotIn("opaque-payload", output.getvalue() + error.getvalue())
        self.assertIn("参数不受支持", error.getvalue())

    def test_private_bootstrap_runs_guards_before_any_network_request(self) -> None:
        """监督器的私有 bootstrap 可启动 worker，缺失本地权重时仍不联网。"""

        with tempfile.TemporaryDirectory(prefix="w5-private-bootstrap-") as temp_dir:
            missing_weight = Path(temp_dir) / "missing-weight.bin"
            report = w5.verify_remote_asset(
                connection_factory=w5._make_https_connection,
                local_weight_path=missing_weight,
                total_timeout=10.0,
            )

        self.assertIn(
            report["error_type"],
            {"DependencyBindingError", "LocalWeightUnavailable"},
        )
        self.assertEqual(report["request_attempt_count"], 0)
        self.assertEqual(report["http_response_count"], 0)
        self.assertEqual(report["exit_code"], 1)

    def test_unknown_arguments_are_not_echoed(self) -> None:
        """不支持的参数只显示固定错误，不回显可能含签名的参数。"""

        output = StringIO()
        error = StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            code = w5.main(["--url", "https://host.invalid/a?token=PRIVATE_SENTINEL"])
        self.assertEqual(code, 2)
        self.assertNotIn("PRIVATE_SENTINEL", output.getvalue() + error.getvalue())

    def test_only_exact_initial_official_release_url_is_accepted(self) -> None:
        """初始地址必须绑定官方 tag 与精确资产路径。"""

        expected_url = (
            "https://github.com/AlexeyAB/darknet/releases/download/"
            "darknet_yolo_v3_optimal/yolov4.conv.137"
        )
        self.assertEqual(w5.INITIAL_URL, expected_url)
        self.assertEqual(
            str(w5.LOCAL_WEIGHT_PATH),
            r"D:\FPGA_Data\darknet\weights\yolov4.conv.137",
        )
        self.assertEqual(
            w5.INITIAL_PATH,
            "/AlexeyAB/darknet/releases/download/"
            "darknet_yolo_v3_optimal/yolov4.conv.137",
        )
        parsed = w5.urlsplit(w5.INITIAL_URL)
        self.assertEqual(parsed.hostname, "github.com")
        self.assertEqual(
            parsed.path,
            "/AlexeyAB/darknet/releases/download/"
            "darknet_yolo_v3_optimal/yolov4.conv.137",
        )
        self.assertEqual(
            parsed.path.split("/")[5], "darknet_yolo_v3_optimal"
        )
        self.assertEqual(w5._validate_url(expected_url, initial=True)[2], parsed.path)

        for url in (
            "https://github.com/AlexeyAB/darknet/releases/download/"
            "yolov4/yolov4.conv.137?x=1",
            "https://github.com.evil.invalid/AlexeyAB/darknet/releases/download/"
            "darknet_yolo_v3_optimal/yolov4.conv.137",
            "http://github.com/AlexeyAB/darknet/releases/download/"
            "darknet_yolo_v3_optimal/yolov4.conv.137",
        ):
            transport = FakeTransport([])
            report = w5._verify_remote_asset_impl(
                initial_url=url,
                connection_factory=transport,
                dependency_check=dependency_ok,
                expected_bytes=3,
                expected_sha256=hashlib.sha256(b"abc").hexdigest(),
            )
            self.assertEqual(report["error_type"], "InitialUrlRejected")
            self.assertEqual(report["request_attempt_count"], 0)
            self.assertEqual(report["http_response_count"], 0)
            self.assertEqual(transport.connections, [])

    def test_rejects_non_success_status(self) -> None:
        """非 200 响应失败且不读取正文。"""

        response = FakeResponse(403, [("Content-Length", "0")])
        report, _ = self.run_fake([response])
        self.assertEqual(report["error_type"], "HttpStatusError")
        self.assertEqual(report["final_status"], 403)
        self.assertEqual(report["bytes_read"], 0)

    def test_rejects_wrong_content_length_and_duplicate_length(self) -> None:
        """缺失、重复或不符的 Content-Length 均失败。"""

        cases = (
            [("Content-Length", "4")],
            [("Content-Length", "3"), ("Content-Length", "3")],
            [("Content-Length", "three")],
        )
        for headers in cases:
            with self.subTest(headers=headers):
                report, _ = self.run_fake([FakeResponse(200, headers, b"abc")])
                self.assertEqual(report["error_type"], "ContentLengthError")
                self.assertEqual(report["bytes_read"], 0)

    def test_rejects_compressed_or_transfer_encoded_response(self) -> None:
        """只接收 identity 编码且没有 Transfer-Encoding 的实体。"""

        cases = (
            [("Content-Length", "3"), ("Content-Encoding", "gzip")],
            [("Content-Length", "3"), ("Transfer-Encoding", "chunked")],
        )
        expected_errors = ("ContentEncodingError", "TransferEncodingError")
        for headers, expected_error in zip(cases, expected_errors):
            with self.subTest(expected_error=expected_error):
                report, _ = self.run_fake([FakeResponse(200, headers, b"abc")])
                self.assertEqual(report["error_type"], expected_error)
                self.assertEqual(report["bytes_read"], 0)

    def test_rejects_short_body(self) -> None:
        """声明长度正确但响应提前 EOF 时按短读失败。"""

        report, _ = self.run_fake(
            [FakeResponse(200, [("Content-Length", "3")], b"ab")]
        )
        self.assertEqual(report["error_type"], "ShortReadError")
        self.assertEqual(report["bytes_read"], 2)
        self.assertEqual(report["hash_matches"], None)

    def test_rejects_body_over_expected_size(self) -> None:
        """超出目标字节数即停止，并对已收到字节形成摘要。"""

        report, _ = self.run_fake(
            [FakeResponse(200, [("Content-Length", "3")], b"abcd")]
        )
        self.assertEqual(report["error_type"], "SizeLimitError")
        self.assertEqual(report["bytes_read"], 4)
        self.assertEqual(report["sha256"], hashlib.sha256(b"abcd").hexdigest())

    def test_rejects_full_length_wrong_digest(self) -> None:
        """完整传输但摘要不匹配时不能返回成功。"""

        report, _ = self.run_fake([response_with_body(b"bad")], expected=b"abc")
        self.assertEqual(report["error_type"], "HashMismatchError")
        self.assertEqual(report["bytes_read"], 3)
        self.assertEqual(report["hash_matches"], False)

    def test_rejects_cross_domain_and_non_https_redirects(self) -> None:
        """拒绝非白名单主机及降级到 HTTP 的跳转。"""

        locations = (
            "https://evil.invalid/asset?token=PRIVATE_SENTINEL",
            "http://release-assets.githubusercontent.com/asset?token=PRIVATE_SENTINEL",
        )
        for location in locations:
            with self.subTest(location_scheme=location.split(":", 1)[0]):
                response = FakeResponse(302, [("Location", location)])
                transport = FakeTransport([response])
                report, _ = self.run_fake(
                    [response],
                    transport=transport,
                    expected=b"abc",
                )
                self.assertEqual(report["error_type"], "RedirectRejected")
                self.assertEqual(report["request_attempt_count"], 1)
                self.assertEqual(report["http_response_count"], 1)
                self.assertEqual(report["actual_get_count"], 1)
                self.assertEqual(len(transport.connections), 1)
                self.assertNotIn("PRIVATE_SENTINEL", json.dumps(report))

    def test_redirect_limit_is_five_hops(self) -> None:
        """至多跟随 5 次安全跳转，不发第 6 个目标请求。"""

        responses = [
            FakeResponse(
                302,
                [
                    (
                        "Location",
                        f"https://github.com/redirect/{index}?token=PRIVATE_SENTINEL",
                    )
                ],
            )
            for index in range(6)
        ]
        transport = FakeTransport(responses)
        report, _ = self.run_fake(
            responses, transport=transport, expected=b"abc"
        )
        self.assertEqual(report["error_type"], "RedirectLimitError")
        self.assertEqual(report["request_attempt_count"], 6)
        self.assertEqual(report["http_response_count"], 6)
        self.assertEqual(report["confirmed_get_count"], 6)
        self.assertEqual(report["actual_get_count"], 6)
        self.assertEqual(report["redirect_count"], 5)
        self.assertEqual(len(transport.connections), 6)
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(report))

    def test_timeout_and_arbitrary_transport_errors_are_redacted(self) -> None:
        """超时及任意异常仅以固定错误类别输出。"""

        clock = FakeClock()
        timed_response = FakeResponse(
            200,
            [("Content-Length", "3")],
            read_error=socket.timeout("secret query token=PRIVATE_SENTINEL"),
            clock=clock,
            clock_advance=301.0,
        )
        transport = FakeTransport([timed_response])
        report, _ = self.run_fake(
            [timed_response],
            transport=transport,
            expected=b"abc",
            monotonic=clock,
        )
        self.assertEqual(report["error_type"], "IdleTimeoutError")
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(report))

        def failing_transport(_host: str, _timeout: float) -> object:
            raise RuntimeError("signed-query=PRIVATE_SENTINEL")

        with tempfile.TemporaryDirectory(prefix="w5-local-weight-") as temp_dir:
            local_path = Path(temp_dir) / "yolov4.conv.137"
            local_path.write_bytes(b"abc")
            error_report = w5._verify_remote_asset_impl(
                connection_factory=failing_transport,
                dependency_check=dependency_ok,
                local_weight_path=local_path,
                expected_bytes=3,
                expected_sha256=hashlib.sha256(b"abc").hexdigest(),
            )
        self.assertEqual(error_report["error_type"], "NetworkError")
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(error_report))

    def test_request_exception_reports_unknown_actual_get_count(self) -> None:
        """request() 抛错时仅确认调用尝试，实际 GET 数保持未知。"""

        response = response_with_body(b"abc")
        transport = FakeTransport(
            [response], request_error=RuntimeError("signed-query=PRIVATE_SENTINEL")
        )
        report, _ = self.run_fake([response], transport=transport, expected=b"abc")
        self.assertEqual(report["request_attempt_count"], 1)
        self.assertEqual(report["http_response_count"], 0)
        self.assertEqual(report["confirmed_get_count"], 0)
        self.assertIsNone(report["actual_get_count"])
        self.assertEqual(report["error_type"], "NetworkError")
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(report))

    def test_getresponse_timeout_confirms_get_was_sent(self) -> None:
        """request() 返回成功后 getresponse() 超时，发送数为 1、响应数为 0。"""

        response = response_with_body(b"abc")
        transport = FakeTransport(
            [response],
            getresponse_error=socket.timeout("PRIVATE_SENTINEL"),
        )
        report, _ = self.run_fake([response], transport=transport, expected=b"abc")
        self.assertEqual(report["request_attempt_count"], 1)
        self.assertEqual(report["confirmed_get_count"], 1)
        self.assertEqual(report["http_response_count"], 0)
        self.assertEqual(report["actual_get_count"], 1)
        self.assertEqual(report["error_type"], "TimeoutError")
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(report))

    def test_parent_hard_deadline_kills_blocked_network_worker(self) -> None:
        """连接、request、响应、响应头或正文卡住时由父级杀死 worker。"""

        stage_expectations = {
            "connect": (0, 0, 0, 0, []),
            "request": (1, 0, 0, None, []),
            "response": (1, 1, 0, 1, []),
            "headers": (1, 1, 1, 1, [200]),
            "body": (1, 1, 1, 1, [200]),
        }
        with tempfile.TemporaryDirectory(prefix="w5-hard-deadline-") as temp_dir:
            root = Path(temp_dir)
            worker_path = root / "hung_worker.py"
            weight_path = root / "local-weight.bin"
            weight_path.write_bytes(b"abc")
            worker_path.write_text(
                textwrap.dedent(
                    """
                    import hashlib
                    import importlib.util
                    import json
                    import sys
                    import time
                    from pathlib import Path

                    script_path, local_path, stage = sys.argv[1:]
                    spec = importlib.util.spec_from_file_location("w5_child_fixture", script_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    spec.loader.exec_module(module)

                    def block_if(target):
                        if stage == target:
                            time.sleep(30)

                    class Response:
                        status = 200

                        def getheaders(self):
                            block_if("headers")
                            return [("Content-Length", "3")]

                        def read1(self, _size):
                            block_if("body")
                            return b"abc"

                        def close(self):
                            pass

                    class Connection:
                        sock = None

                        def request(self, *_args, **_kwargs):
                            block_if("request")

                        def getresponse(self):
                            block_if("response")
                            return Response()

                        def close(self):
                            pass

                    def factory(_host, _timeout):
                        block_if("connect")
                        return Connection()

                    module._verify_remote_asset_impl(
                        connection_factory=factory,
                        dependency_check=lambda: (True, [{"matches": True}]),
                        local_weight_path=Path(local_path),
                        expected_bytes=3,
                        expected_sha256=hashlib.sha256(b"abc").hexdigest(),
                        total_timeout=20,
                        idle_timeout=20,
                        socket_timeout=1,
                        stage_callback=lambda state: print(
                            json.dumps({"kind": "state", "state": state}), flush=True
                        ),
                    )
                    """
                ),
                encoding="utf-8",
            )
            for stage, expected in stage_expectations.items():
                with self.subTest(stage=stage):
                    started = time.monotonic()
                    report, worker = w5._run_supervised_process(
                        [
                            sys.executable,
                            str(worker_path),
                            str(SCRIPT_PATH.resolve()),
                            str(weight_path),
                            stage,
                        ],
                        total_timeout=0.5,
                    )
                    elapsed = time.monotonic() - started
                    attempts, confirmed, responses, actual, statuses = expected
                    self.assertLess(elapsed, 3.0)
                    self.assertTrue(worker["timed_out"])
                    self.assertTrue(worker["worker_terminated"])
                    self.assertTrue(worker["reader_stopped"])
                    self.assertIsNotNone(worker["worker_exit_code"])
                    self.assertEqual(report["error_type"], "TotalTimeoutError")
                    self.assertEqual(report["exit_code"], 1)
                    self.assertEqual(report["request_attempt_count"], attempts)
                    self.assertEqual(report["confirmed_get_count"], confirmed)
                    self.assertEqual(report["http_response_count"], responses)
                    self.assertEqual(report["actual_get_count"], actual)
                    self.assertEqual(report["http_statuses"], statuses)
                    self.assertEqual(report["bytes_read"], 0)
                    self.assertIsNone(report["sha256"])
                    self.assertIsNone(report["hash_matches"])

    def test_00_reader_start_failure_reaps_worker_without_dispatcher_residue(self) -> None:
        """reader 启动失败时终止 worker，且不遗留本次 dispatcher。"""

        with tempfile.TemporaryDirectory(prefix="w5-reader-start-failure-") as temp_dir:
            worker_path = Path(temp_dir) / "hung_worker.py"
            network_marker = Path(temp_dir) / "network-started.marker"
            worker_path.write_text(
                "import sys, time\n"
                "from pathlib import Path\n"
                "if sys.stdin.readline() == 'start\\n':\n"
                "    Path(sys.argv[1]).write_text('released', encoding='utf-8')\n"
                "time.sleep(30)\n",
                encoding="utf-8",
            )
            started_processes: list[subprocess.Popen[str]] = []
            attempted_threads: list[str] = []
            dispatcher_ids_before = {
                id(thread)
                for thread in threading.enumerate()
                if thread.name == "w5-progress-callback"
            }
            reader_ids_before = {
                id(thread)
                for thread in threading.enumerate()
                if thread.name == "w5-worker-reader"
            }
            real_popen = subprocess.Popen
            real_thread_start = threading.Thread.start

            def capture_popen(*args: Any, **kwargs: Any) -> subprocess.Popen[str]:
                process = real_popen(*args, **kwargs)
                started_processes.append(process)
                return process

            def fail_reader_start(thread: threading.Thread) -> None:
                attempted_threads.append(thread.name)
                if thread.name == "w5-worker-reader":
                    raise RuntimeError("injected reader start failure")
                real_thread_start(thread)

            with patch.object(w5.subprocess, "Popen", side_effect=capture_popen):
                with patch.object(threading.Thread, "start", new=fail_reader_start):
                    report, worker = w5._run_supervised_process(
                        [sys.executable, str(worker_path), str(network_marker)],
                        total_timeout=2.0,
                        progress_callback=lambda _record: None,
                        start_gate=True,
                    )

        self.assertEqual(report["error_type"], "WorkerSetupError")
        self.assertEqual(report["exit_code"], 1)
        self.assertEqual(len(started_processes), 1)
        self.assertIsNotNone(started_processes[0].poll())
        self.assertIsNotNone(started_processes[0].stdout)
        self.assertTrue(started_processes[0].stdout.closed)
        self.assertTrue(started_processes[0].stdin.closed)
        self.assertFalse(network_marker.exists())
        self.assertTrue(worker["worker_terminated"])
        self.assertTrue(worker["reader_stopped"])
        self.assertFalse(worker["callback_dispatcher_started"])
        self.assertIn("w5-worker-reader", attempted_threads)
        self.assertNotIn("w5-progress-callback", attempted_threads)
        self.assertEqual(
            {
                id(thread)
                for thread in threading.enumerate()
                if thread.name == "w5-progress-callback"
            },
            dispatcher_ids_before,
        )
        self.assertEqual(
            {
                id(thread)
                for thread in threading.enumerate()
                if thread.name == "w5-worker-reader"
            },
            reader_ids_before,
        )
        self.assertNotIn("injected reader start failure", json.dumps(report))

    def test_01_dispatcher_start_failure_reaps_worker_and_reader(self) -> None:
        """dispatcher 启动失败时回收 worker 与已启动的 reader。"""

        with tempfile.TemporaryDirectory(prefix="w5-dispatcher-start-failure-") as temp_dir:
            worker_path = Path(temp_dir) / "hung_worker.py"
            network_marker = Path(temp_dir) / "network-started.marker"
            worker_path.write_text(
                "import sys, time\n"
                "from pathlib import Path\n"
                "if sys.stdin.readline() == 'start\\n':\n"
                "    Path(sys.argv[1]).write_text('released', encoding='utf-8')\n"
                "time.sleep(30)\n",
                encoding="utf-8",
            )
            started_processes: list[subprocess.Popen[str]] = []
            attempted_threads: list[str] = []
            callback_ids_before = {
                id(thread)
                for thread in threading.enumerate()
                if thread.name == "w5-progress-callback"
            }
            real_popen = subprocess.Popen
            real_thread_start = threading.Thread.start

            def capture_popen(*args: Any, **kwargs: Any) -> subprocess.Popen[str]:
                process = real_popen(*args, **kwargs)
                started_processes.append(process)
                return process

            def fail_dispatcher_start(thread: threading.Thread) -> None:
                attempted_threads.append(thread.name)
                if thread.name == "w5-progress-callback":
                    raise RuntimeError("injected dispatcher start failure")
                real_thread_start(thread)

            with patch.object(w5.subprocess, "Popen", side_effect=capture_popen):
                with patch.object(threading.Thread, "start", new=fail_dispatcher_start):
                    with patch.object(w5, "_PROGRESS_DISPATCH_THREAD", None):
                        with patch.object(w5, "_PROGRESS_DISPATCH_QUEUE", None):
                            report, worker = w5._run_supervised_process(
                                [sys.executable, str(worker_path), str(network_marker)],
                                total_timeout=2.0,
                                progress_callback=lambda _record: None,
                                start_gate=True,
                            )

        self.assertEqual(report["error_type"], "WorkerSetupError")
        self.assertEqual(len(started_processes), 1)
        self.assertIsNotNone(started_processes[0].poll())
        self.assertIsNotNone(started_processes[0].stdout)
        self.assertTrue(started_processes[0].stdout.closed)
        self.assertIsNotNone(started_processes[0].stdin)
        self.assertTrue(started_processes[0].stdin.closed)
        self.assertFalse(network_marker.exists())
        self.assertTrue(worker["worker_terminated"])
        self.assertTrue(worker["reader_stopped"])
        self.assertFalse(worker["callback_dispatcher_started"])
        self.assertIn("w5-worker-reader", attempted_threads)
        self.assertIn("w5-progress-callback", attempted_threads)
        self.assertEqual(
            {
                id(thread)
                for thread in threading.enumerate()
                if thread.name == "w5-progress-callback"
            },
            callback_ids_before,
        )
        self.assertFalse(
            any(thread.name == "w5-worker-reader" for thread in threading.enumerate())
        )
        self.assertNotIn("injected dispatcher start failure", json.dumps(report))

    def test_02_gate_released_only_after_dispatcher_is_ready(self) -> None:
        """成功路径仅在 dispatcher ready 后释放 worker gate。"""

        with tempfile.TemporaryDirectory(prefix="w5-gate-after-dispatcher-") as temp_dir:
            root = Path(temp_dir)
            worker_path = root / "gated_worker.py"
            dispatcher_marker = root / "dispatcher-ready.marker"
            worker_marker = root / "network-started.marker"
            serialized_report = json.dumps(
                self.valid_worker_report(), ensure_ascii=True, separators=(",", ":")
            )
            worker_path.write_text(
                "import json, sys\n"
                "from pathlib import Path\n"
                "if sys.stdin.readline() != 'start\\n':\n"
                "    sys.exit(2)\n"
                "ready = Path(sys.argv[1]).exists()\n"
                "Path(sys.argv[2]).write_text('ready' if ready else 'released-too-early', encoding='utf-8')\n"
                "report = json.loads(sys.argv[3])\n"
                "print(json.dumps({'kind':'result','report':report}), flush=True)\n",
                encoding="utf-8",
            )
            start_dispatcher = w5._start_progress_dispatcher

            def record_dispatcher_ready(
                callback: Callable[[dict[str, object]], None] | None,
                *,
                deadline: float,
            ) -> tuple[Callable[[dict[str, object]], None], bool]:
                enqueue, ready = start_dispatcher(callback, deadline=deadline)
                if ready:
                    dispatcher_marker.write_text("ready", encoding="utf-8")
                return enqueue, ready

            with patch.object(
                w5, "_start_progress_dispatcher", side_effect=record_dispatcher_ready
            ):
                report, worker = w5._run_supervised_process(
                    [
                        sys.executable,
                        str(worker_path),
                        str(dispatcher_marker),
                        str(worker_marker),
                        serialized_report,
                    ],
                    total_timeout=2.0,
                    progress_callback=lambda _record: None,
                    start_gate=True,
                )
            marker_value = worker_marker.read_text(encoding="utf-8")

        self.assertEqual(marker_value, "ready")
        self.assertEqual(report["exit_code"], 0)
        self.assertTrue(worker["worker_terminated"])
        self.assertTrue(worker["reader_stopped"])
        self.assertTrue(worker["callback_dispatcher_started"])

    def test_parent_interrupt_reaps_worker(self) -> None:
        """父级监督等待被中断时强制回收 worker。"""

        class InterruptingQueue:
            """在父级第一次等待消息时模拟键盘中断。"""

            def put(self, _item: object) -> None:
                return

            def get(self, timeout: float | None = None) -> object:
                raise KeyboardInterrupt

        with tempfile.TemporaryDirectory(prefix="w5-parent-interrupt-") as temp_dir:
            worker_path = Path(temp_dir) / "hung_worker.py"
            worker_path.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
            with patch.object(w5.queue, "Queue", return_value=InterruptingQueue()):
                report, worker = w5._run_supervised_process(
                    [sys.executable, str(worker_path)], total_timeout=2.0
                )

        self.assertEqual(report["error_type"], "InterruptedError")
        self.assertEqual(report["exit_code"], 1)
        self.assertTrue(worker["worker_terminated"])
        self.assertTrue(worker["reader_stopped"])
        self.assertIsNotNone(worker["worker_exit_code"])

    def test_worker_return_code_and_report_must_match(self) -> None:
        """worker 非零退出或报告 exit_code 不一致时拒绝其哈希。"""

        valid = self.valid_worker_report()
        cases = (("worker-nonzero", valid, 17),)
        mismatched = self.valid_worker_report()
        mismatched["exit_code"] = 1
        mismatched["error_type"] = "SyntheticFailure"
        cases += (("report-mismatch", mismatched, 0),)
        malformed = self.valid_worker_report()
        malformed["hash_matches"] = 1
        cases += (("field-type-mismatch", malformed, 0),)
        dependency_mismatch = self.valid_worker_report()
        dependency_mismatch["dependency_bindings"] = [{"matches": False}]
        cases += (("dependency-mismatch", dependency_mismatch, 0),)
        for label, report_data, process_exit in cases:
            with self.subTest(case=label), tempfile.TemporaryDirectory(prefix="w5-exit-code-") as temp_dir:
                worker_path = Path(temp_dir) / "result_worker.py"
                self.write_worker_result(worker_path, report_data, exit_code=process_exit)
                received, lifecycle = w5._run_supervised_process(
                    [sys.executable, str(worker_path)], total_timeout=2.0
                )
            self.assertEqual(received["error_type"], "WorkerExitError")
            self.assertEqual(received["exit_code"], 1)
            self.assertIsNone(received["sha256"])
            self.assertTrue(lifecycle["worker_terminated"])
            self.assertTrue(lifecycle["reader_stopped"])
        self.assertEqual(cases[0][2], 17)

    def test_successful_worker_report_requires_exact_frozen_dependency_set(self) -> None:
        """成功报告必须含齐固定 15 项，且不得靠替换或额外记录伪造通过。"""

        valid = self.valid_worker_report()
        self.assertTrue(w5._worker_report_is_consistent(valid))

        cases: list[tuple[str, dict[str, object]]] = []

        missing = self.valid_worker_report()
        missing["dependency_bindings"] = missing["dependency_bindings"][:-2]
        cases.append(("missing-fixed-bindings", missing))

        duplicate = self.valid_worker_report()
        duplicate_bindings = list(duplicate["dependency_bindings"])
        duplicate_bindings[1] = dict(duplicate_bindings[0])
        duplicate["dependency_bindings"] = duplicate_bindings
        cases.append(("duplicate-fixed-path", duplicate))

        substituted = self.valid_worker_report()
        substituted_bindings = list(substituted["dependency_bindings"])
        substituted_bindings[0] = {
            **substituted_bindings[0],
            "path": "report/evidence/S1-T02/fabricated.json",
        }
        substituted["dependency_bindings"] = substituted_bindings
        cases.append(("substituted-fixed-path", substituted))

        forged_expected_size = self.valid_worker_report()
        forged_size_bindings = list(forged_expected_size["dependency_bindings"])
        forged_size_bindings[0] = {
            **forged_size_bindings[0],
            "expected_bytes": forged_size_bindings[0]["expected_bytes"] + 1,
        }
        forged_expected_size["dependency_bindings"] = forged_size_bindings
        cases.append(("forged-expected-size", forged_expected_size))

        forged_expected_sha = self.valid_worker_report()
        forged_sha_bindings = list(forged_expected_sha["dependency_bindings"])
        forged_sha_bindings[0] = {
            **forged_sha_bindings[0],
            "expected_sha256": "0" * 64,
        }
        forged_expected_sha["dependency_bindings"] = forged_sha_bindings
        cases.append(("forged-expected-sha", forged_expected_sha))

        mismatched_observed_size = self.valid_worker_report()
        observed_size_bindings = list(mismatched_observed_size["dependency_bindings"])
        observed_size_bindings[0] = {
            **observed_size_bindings[0],
            "observed_bytes": observed_size_bindings[0]["observed_bytes"] + 1,
        }
        mismatched_observed_size["dependency_bindings"] = observed_size_bindings
        cases.append(("mismatched-observed-size", mismatched_observed_size))

        mismatched_observed_sha = self.valid_worker_report()
        observed_sha_bindings = list(mismatched_observed_sha["dependency_bindings"])
        observed_sha_bindings[0] = {
            **observed_sha_bindings[0],
            "observed_sha256": "0" * 64,
        }
        mismatched_observed_sha["dependency_bindings"] = observed_sha_bindings
        cases.append(("mismatched-observed-sha", mismatched_observed_sha))

        wrong_missing_state = self.valid_worker_report()
        missing_state_bindings = list(wrong_missing_state["dependency_bindings"])
        missing_state_bindings[len(w5.DEPENDENCIES)] = {
            **missing_state_bindings[len(w5.DEPENDENCIES)],
            "expected_state": "present_at_frozen_baseline",
        }
        wrong_missing_state["dependency_bindings"] = missing_state_bindings
        cases.append(("wrong-missing-state", wrong_missing_state))

        wrong_observed_state = self.valid_worker_report()
        observed_state_bindings = list(wrong_observed_state["dependency_bindings"])
        observed_state_bindings[len(w5.DEPENDENCIES)] = {
            **observed_state_bindings[len(w5.DEPENDENCIES)],
            "observed_state": "present_or_outside_root",
        }
        wrong_observed_state["dependency_bindings"] = observed_state_bindings
        cases.append(("wrong-observed-state", wrong_observed_state))

        extra_match = self.valid_worker_report()
        extra_match_bindings = list(extra_match["dependency_bindings"])
        extra_match_bindings.append(
            {"path": "report/evidence/S1-T02/fake-sixteenth.json", "matches": True}
        )
        extra_match["dependency_bindings"] = extra_match_bindings
        cases.append(("extra-match-record", extra_match))

        for label, report in cases:
            with self.subTest(case=label):
                self.assertFalse(w5._worker_report_is_consistent(report))

        failed = self.valid_worker_report()
        failed.update(
            {
                "exit_code": 1,
                "error_type": "DependencyMismatch",
                "dependency_bindings": [],
            }
        )
        self.assertTrue(w5._worker_report_is_consistent(failed))

    def test_reader_delayed_eof_cannot_extend_deadline_or_accept_result(self) -> None:
        """EOF 延迟 0.1 秒并越过 deadline 时不返回成功。"""

        report_data = self.valid_worker_report()
        with tempfile.TemporaryDirectory(prefix="w5-delayed-eof-") as temp_dir:
            worker_path = Path(temp_dir) / "result_worker.py"
            serialized_report = json.dumps(
                report_data, ensure_ascii=True, separators=(",", ":")
            )
            worker_path.write_text(
                "import json, sys, time\n"
                "time.sleep(0.47)\n"
                f"print(json.dumps({{'kind':'result','report':json.loads({serialized_report!r})}}), flush=True)\n"
                "sys.exit(0)\n",
                encoding="utf-8",
            )
            real_popen = subprocess.Popen

            class DelayedEOF:
                """在底层管道 EOF 后模拟缓慢的 reader 收尾。"""

                def __init__(self, stream: Any) -> None:
                    self.stream = stream
                    self.iterator = iter(stream)
                    self.delayed = False

                def __iter__(self) -> "DelayedEOF":
                    return self

                def __next__(self) -> str:
                    try:
                        return next(self.iterator)
                    except StopIteration:
                        if not self.delayed:
                            self.delayed = True
                            time.sleep(0.1)
                        raise

                def close(self) -> None:
                    self.stream.close()

            def delayed_popen(*args: Any, **kwargs: Any) -> subprocess.Popen[str]:
                process: Any = real_popen(*args, **kwargs)
                assert process.stdout is not None
                process.stdout = DelayedEOF(process.stdout)
                return process

            started = time.monotonic()
            with patch.object(w5.subprocess, "Popen", side_effect=delayed_popen):
                received, lifecycle = w5._run_supervised_process(
                    [sys.executable, str(worker_path)], total_timeout=0.6
                )
            elapsed = time.monotonic() - started

        self.assertLess(elapsed, 0.8)
        self.assertEqual(received["exit_code"], 1)
        self.assertIn(
            received["error_type"],
            {"TotalTimeoutError", "WorkerCleanupTimeoutError", "WorkerTerminationError"},
        )
        self.assertTrue(lifecycle["worker_terminated"])
        self.assertIsNone(received["sha256"])
        reader_deadline = time.monotonic() + 0.5
        while (
            any(thread.name == "w5-worker-reader" for thread in threading.enumerate())
            and time.monotonic() < reader_deadline
        ):
            time.sleep(0.005)
        self.assertFalse(
            any(thread.name == "w5-worker-reader" for thread in threading.enumerate())
        )

    def test_blocking_callback_cannot_delay_timeout_or_accept_late_result(self) -> None:
        """阻塞回调不延迟父级超时，worker 迟到的成功结果不被接纳。"""

        callback_started = threading.Event()
        callback_finished = threading.Event()
        report_data = self.valid_worker_report()
        serialized_report = json.dumps(report_data, ensure_ascii=True, separators=(",", ":"))
        with tempfile.TemporaryDirectory(prefix="w5-blocking-callback-timeout-") as temp_dir:
            worker_path = Path(temp_dir) / "late_result_worker.py"
            worker_path.write_text(
                "import json, time\n"
                "print(json.dumps({'kind':'progress','record':{'event':'progress'}}), flush=True)\n"
                "time.sleep(0.45)\n"
                f"print(json.dumps({{'kind':'result','report':json.loads({serialized_report!r})}}), flush=True)\n",
                encoding="utf-8",
            )

            def slow_callback(_record: dict[str, object]) -> None:
                callback_started.set()
                time.sleep(0.7)
                callback_finished.set()

            started = time.monotonic()
            received, lifecycle = w5._run_supervised_process(
                [sys.executable, str(worker_path)],
                total_timeout=0.3,
                progress_callback=slow_callback,
            )
            elapsed = time.monotonic() - started

        self.assertTrue(callback_started.wait(timeout=0.25))
        self.assertLess(elapsed, 0.5)
        self.assertTrue(lifecycle["timed_out"])
        self.assertTrue(lifecycle["worker_terminated"])
        self.assertTrue(lifecycle["reader_stopped"])
        self.assertIsNotNone(lifecycle["worker_exit_code"])
        self.assertEqual(received["error_type"], "TotalTimeoutError")
        self.assertEqual(received["exit_code"], 1)
        self.assertIsNone(received["sha256"])
        self.assertTrue(callback_finished.wait(timeout=1.0))

    def test_blocking_progress_callback_is_best_effort_and_reused(self) -> None:
        """阻塞和抛错的进度回调不延长期限、不改变结果且只复用一个线程。"""

        callback_started = threading.Event()
        callback_finished = threading.Event()
        records: list[dict[str, object]] = []
        with tempfile.TemporaryDirectory(prefix="w5-blocking-callback-") as temp_dir:
            worker_path = Path(temp_dir) / "result_worker.py"
            report_data = self.valid_worker_report()
            serialized_report = json.dumps(report_data, ensure_ascii=True, separators=(",", ":"))
            worker_path.write_text(
                "import json, time\n"
                "print(json.dumps({'kind':'progress','record':{'event':'progress'}}), flush=True)\n"
                f"print(json.dumps({{'kind':'result','report':json.loads({serialized_report!r})}}), flush=True)\n",
                encoding="utf-8",
            )

            def slow_callback(record: dict[str, object]) -> None:
                callback_started.set()
                time.sleep(0.6)
                records.append(record)
                callback_finished.set()
                raise KeyboardInterrupt

            started = time.monotonic()
            received, lifecycle = w5._run_supervised_process(
                [sys.executable, str(worker_path)],
                total_timeout=0.2,
                progress_callback=slow_callback,
            )
            elapsed = time.monotonic() - started
            for _ in range(3):
                repeated, _ = w5._run_supervised_process(
                    [sys.executable, str(worker_path)],
                    total_timeout=1.0,
                    progress_callback=lambda _record: None,
                )
                self.assertEqual(repeated["exit_code"], 0)
            dispatcher_ids = {
                thread.ident
                for thread in threading.enumerate()
                if thread.name == "w5-progress-callback"
            }

        self.assertTrue(callback_started.wait(timeout=0.2))
        self.assertLess(elapsed, 0.45)
        self.assertTrue(lifecycle["worker_terminated"])
        self.assertTrue(lifecycle["reader_stopped"])
        self.assertEqual(received["exit_code"], 0)
        self.assertEqual(received["sha256"], report_data["sha256"])
        self.assertTrue(callback_finished.wait(timeout=1.0))
        self.assertEqual(len(records), 1)
        self.assertLessEqual(len(dispatcher_ids), 1)

    def test_connect_request_response_and_header_stages_obey_idle_deadline(self) -> None:
        """連線、request、response 與 header 階段超過無進度期限都失敗。"""

        cases = (
            ("connect", 0, 0, 0),
            ("request", 301, 0, 1),
            ("response", 0, 1, 1),
            ("headers", 0, 1, 1),
        )
        for stage, request_advance, expected_responses, expected_actual in cases:
            with self.subTest(stage=stage):
                clock = FakeClock()
                response = FakeResponse(
                    200,
                    [("Content-Length", "3")],
                    b"abc",
                    clock=clock if stage == "headers" else None,
                    on_headers=(
                        (lambda: setattr(clock, "value", clock.value + 301.0))
                        if stage == "headers"
                        else None
                    ),
                )
                transport = FakeTransport(
                    [response],
                    clock=clock,
                    connect_advance=301.0 if stage == "connect" else 0.0,
                    request_advance=301.0 if stage == "request" else request_advance,
                    getresponse_advance=301.0 if stage == "response" else 0.0,
                )
                report, _ = self.run_fake(
                    [response], transport=transport, expected=b"abc", monotonic=clock
                )
                self.assertEqual(report["error_type"], "IdleTimeoutError")
                self.assertEqual(report["request_attempt_count"], 0 if stage == "connect" else 1)
                self.assertEqual(report["http_response_count"], expected_responses)
                self.assertEqual(report["actual_get_count"], expected_actual)

    def test_slow_single_read_and_total_deadline_are_rejected(self) -> None:
        """单次 read1 慢 301 秒或总耗时 3601 秒均不得接受数据。"""

        for delay, expected_error in (
            (301.0, "IdleTimeoutError"),
            (3601.0, "TotalTimeoutError"),
        ):
            with self.subTest(delay=delay):
                clock = FakeClock()
                response = FakeResponse(
                    200,
                    [("Content-Length", "3")],
                    b"abc",
                    clock=clock,
                    clock_advance=delay,
                )
                report, _ = self.run_fake(
                    [response], expected=b"abc", monotonic=clock
                )
                self.assertEqual(report["error_type"], expected_error)
                self.assertEqual(report["bytes_read"], 0)
                self.assertIsNone(report["sha256"])
                self.assertEqual(report["exit_code"], 1)

    def test_total_deadline_applies_to_request_stage(self) -> None:
        """request() 返回后发现超时仍记录已经确认发送的 GET。"""

        clock = FakeClock()
        response = response_with_body(b"abc")
        transport = FakeTransport(
            [response], clock=clock, request_advance=3601.0
        )
        report, _ = self.run_fake(
            [response], transport=transport, expected=b"abc", monotonic=clock
        )
        self.assertEqual(report["error_type"], "TotalTimeoutError")
        self.assertEqual(report["request_attempt_count"], 1)
        self.assertEqual(report["http_response_count"], 0)
        self.assertEqual(report["confirmed_get_count"], 1)
        self.assertEqual(report["actual_get_count"], 1)
        self.assertEqual(report["exit_code"], 1)

    def test_chunk_reads_are_bounded_and_counted(self) -> None:
        """流式读取遵守 chunk 上限且准确累计字节数。"""

        body = b"abcdefghijk"
        response = response_with_body(body)
        report, transport = self.run_fake(
            [response], expected=body, chunk_size=4
        )
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["bytes_read"], len(body))
        self.assertTrue(all(size <= 4 for size in response.read_sizes))
        self.assertEqual(transport.timeouts[0], w5.MAX_SOCKET_TIMEOUT_SECONDS)

    def test_dependency_mismatch_blocks_before_connection(self) -> None:
        """静态绑定不符时不创建任何连接。"""

        transport = FakeTransport([response_with_body(b"abc")])
        report, _ = self.run_fake(
            [response_with_body(b"abc")],
            transport=transport,
            expected=b"abc",
            dependency_check=lambda: (False, [{"matches": False}]),
        )
        self.assertEqual(report["error_type"], "DependencyBindingError")
        self.assertEqual(report["request_attempt_count"], 0)
        self.assertEqual(transport.connections, [])

    def test_local_weight_binding_is_checked_even_with_dependency_seam(self) -> None:
        """缺失或错误本地权重即使静态 seam 返回通过也不得请求网络。"""

        expected_hash = hashlib.sha256(b"abc").hexdigest()
        for write_wrong_file in (False, True):
            with self.subTest(write_wrong_file=write_wrong_file):
                transport = FakeTransport([response_with_body(b"abc")])
                dependency_called = False

                def approved_dependencies() -> tuple[bool, list[dict[str, object]]]:
                    nonlocal dependency_called
                    dependency_called = True
                    return True, [{"matches": True}]

                with tempfile.TemporaryDirectory(prefix="w5-local-weight-") as temp_dir:
                    local_path = Path(temp_dir) / "yolov4.conv.137"
                    if write_wrong_file:
                        local_path.write_bytes(b"xyz")
                    report = w5._verify_remote_asset_impl(
                        connection_factory=transport,
                        dependency_check=approved_dependencies,
                        local_weight_path=local_path,
                        expected_bytes=3,
                        expected_sha256=expected_hash,
                    )

                expected_error = (
                    "LocalWeightMismatchError"
                    if write_wrong_file
                    else "LocalWeightUnavailable"
                )
                self.assertEqual(report["error_type"], expected_error)
                self.assertEqual(report["request_attempt_count"], 0)
                self.assertEqual(transport.connections, [])
                self.assertTrue(dependency_called)
                local_binding = report["local_weight_binding"]
                self.assertFalse(local_binding["matches_expected"])
                self.assertFalse(local_binding["matches_remote"])

    def test_local_weight_change_during_fake_network_fails_postcheck(self) -> None:
        """fake 网络读取期间本地权重变化会使任务失败。"""

        expected = b"abc"
        with tempfile.TemporaryDirectory(prefix="w5-local-weight-") as temp_dir:
            local_path = Path(temp_dir) / "yolov4.conv.137"
            local_path.write_bytes(expected)

            def mutate_local_weight() -> None:
                local_path.write_bytes(b"xyz")

            response = FakeResponse(
                200,
                [("Content-Length", "3")],
                expected,
                on_read=mutate_local_weight,
            )
            transport = FakeTransport([response])
            report = w5._verify_remote_asset_impl(
                connection_factory=transport,
                dependency_check=dependency_ok,
                local_weight_path=local_path,
                expected_bytes=3,
                expected_sha256=hashlib.sha256(expected).hexdigest(),
            )

        self.assertEqual(report["http_statuses"], [200])
        self.assertEqual(report["request_attempt_count"], 1)
        self.assertEqual(report["http_response_count"], 1)
        self.assertEqual(report["sha256"], hashlib.sha256(expected).hexdigest())
        self.assertTrue(report["hash_matches"])
        self.assertEqual(report["error_type"], "LocalWeightChangedError")
        self.assertEqual(report["exit_code"], 1)
        local_binding = report["local_weight_binding"]
        self.assertTrue(local_binding["matches_expected"])
        self.assertFalse(local_binding["stable"])
        self.assertFalse(local_binding["matches_remote"])
        self.assertNotEqual(
            local_binding["before"]["sha256"],
            local_binding["after"]["sha256"],
        )

    def test_success_report_binds_local_pre_and_post_snapshots(self) -> None:
        """成功结果同时绑定远端、运行前和运行后本地文件。"""

        report, _ = self.run_fake([response_with_body(b"abc")], expected=b"abc")
        local_binding = report["local_weight_binding"]
        self.assertEqual(report["exit_code"], 0)
        self.assertTrue(local_binding["matches_expected"])
        self.assertTrue(local_binding["stable"])
        self.assertTrue(local_binding["matches_remote"])
        self.assertEqual(local_binding["before"]["bytes"], 3)
        self.assertEqual(local_binding["after"]["bytes"], 3)
        self.assertEqual(
            local_binding["before"]["sha256"],
            local_binding["after"]["sha256"],
        )

    def test_progress_callback_contains_only_safe_fields(self) -> None:
        """进度回调仅收到白名单字段，不含签名 URL 或哈希中间态。"""

        clock = FakeClock()
        records: list[dict[str, object]] = []

        def advance_clock() -> None:
            clock.value += 61.0

        redirect = FakeResponse(
            302,
            [
                (
                    "Location",
                    "https://release-assets.githubusercontent.com/object?token=PRIVATE_SENTINEL",
                )
            ],
        )
        body = FakeResponse(
            200,
            [("Content-Length", "3"), ("Content-Encoding", "identity")],
            b"abc",
            on_read=advance_clock,
        )
        report, _ = self.run_fake(
            [redirect, body],
            expected=b"abc",
            monotonic=clock,
            progress_interval=60.0,
            progress_callback=records.append,
        )

        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(
            set(record),
            {
                "event",
                "timestamp_utc8",
                "bytes_read",
                "elapsed_seconds",
                "request_attempt_count",
                "http_response_count",
                "confirmed_get_count",
                "actual_get_count",
                "redirect_count",
                "status_count",
                "http_statuses",
            },
        )
        self.assertEqual(record["event"], "progress")
        self.assertEqual(record["bytes_read"], 3)
        self.assertEqual(record["request_attempt_count"], 2)
        self.assertEqual(record["http_response_count"], 2)
        self.assertEqual(record["confirmed_get_count"], 2)
        self.assertEqual(record["actual_get_count"], 2)
        self.assertEqual(record["redirect_count"], 1)
        self.assertEqual(record["status_count"], 2)
        self.assertEqual(record["http_statuses"], [302, 200])
        serialized = json.dumps(record, sort_keys=True).lower()
        for forbidden in ("private_sentinel", "sha256", "url", "location", "headers", "error"):
            self.assertNotIn(forbidden, serialized)

    def test_progress_is_emitted_during_continuous_small_chunk_reads(self) -> None:
        """连续小块传输按 60 秒节奏输出安全进度，无需真实等待。"""

        clock = FakeClock()
        records: list[dict[str, object]] = []
        body = b"abcdef"
        response = FakeResponse(
            200,
            [("Content-Length", str(len(body)))],
            body,
            clock=clock,
            clock_advance=20.0,
        )
        report, _ = self.run_fake(
            [response],
            expected=body,
            chunk_size=1,
            monotonic=clock,
            progress_interval=60.0,
            progress_callback=records.append,
        )
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual([row["elapsed_seconds"] for row in records], [60.0, 120.0])
        self.assertEqual([row["bytes_read"] for row in records], [3, 6])
        for row in records:
            serialized = json.dumps(row, sort_keys=True).lower()
            for forbidden in ("sha256", "url", "location", "headers", "error"):
                self.assertNotIn(forbidden, serialized)

    def test_progress_callback_failure_returns_redacted_failure(self) -> None:
        """回调异常转成固定失败类别，报告不带异常文本。"""

        clock = FakeClock()

        def advance_clock() -> None:
            clock.value += 2.0

        def fail_callback(_record: dict[str, object]) -> None:
            raise RuntimeError("PRIVATE_SENTINEL signed query")

        response = FakeResponse(
            200,
            [("Content-Length", "3")],
            b"abc",
            on_read=advance_clock,
        )
        report, _ = self.run_fake(
            [response],
            expected=b"abc",
            monotonic=clock,
            progress_interval=1.0,
            progress_callback=fail_callback,
        )
        self.assertEqual(report["error_type"], "ProgressCallbackError")
        self.assertEqual(report["exit_code"], 1)
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(report))

    def test_cli_flushes_jsonl_then_final_json(self) -> None:
        """显式执行模式将每条进度 flush，最后另写最终 JSON。"""

        stream = FlushTrackingStream()
        progress = {
            "event": "progress",
            "timestamp_utc8": "2026-09-17T12:00:00+08:00",
            "bytes_read": 3,
            "elapsed_seconds": 1.0,
            "request_attempt_count": 1,
            "http_response_count": 1,
            "confirmed_get_count": 1,
            "actual_get_count": 1,
            "redirect_count": 0,
            "status_count": 1,
            "http_statuses": [200],
        }

        def fake_run(
            *,
            connection_factory: Callable[[str, float], object],
            progress_callback: Callable[[dict[str, object]], None],
        ) -> dict[str, object]:
            self.assertIs(connection_factory, w5._make_https_connection)
            progress_callback(progress)
            return {"task_id": w5.TASK_ID, "exit_code": 0}

        with patch.object(w5, "verify_remote_asset", side_effect=fake_run):
            with patch.object(w5.sys, "stdout", stream):
                code = w5.main(["--execute-network-request"])

        lines = stream.getvalue().splitlines()
        self.assertEqual(code, 0)
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["event"], "progress")
        final_record = json.loads(lines[1])
        self.assertNotIn("event", final_record)
        self.assertEqual(final_record["exit_code"], 0)
        self.assertEqual(stream.flush_count, 2)

    def test_cli_unexpected_failure_emits_redacted_final_json(self) -> None:
        """主流程意外异常仍输出脱敏失败 JSON，不暴露异常文本。"""

        stream = FlushTrackingStream()
        with patch.object(
            w5,
            "verify_remote_asset",
            side_effect=RuntimeError("PRIVATE_SENTINEL signed query"),
        ):
            with patch.object(w5.sys, "stdout", stream):
                code = w5.main(["--execute-network-request"])

        self.assertEqual(code, 1)
        self.assertEqual(stream.flush_count, 1)
        report = json.loads(stream.getvalue())
        self.assertEqual(report["error_type"], "InternalError")
        self.assertNotIn("PRIVATE_SENTINEL", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
