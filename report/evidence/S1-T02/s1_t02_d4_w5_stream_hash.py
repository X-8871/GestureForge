#!/usr/bin/env python3
"""以安全边界流式核验官方 YOLOv4 conv.137 完整对象的 SHA-256。"""

from __future__ import annotations

import hashlib
import http.client
import json
import base64
import queue
import socket
import stat
import ssl
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence
from urllib.parse import urljoin, urlsplit


TASK_ID = "S1-T02-D4-W5"
INITIAL_URL = (
    "https://github.com/AlexeyAB/darknet/releases/download/"
    "darknet_yolo_v3_optimal/yolov4.conv.137"
)
LOCAL_WEIGHT_PATH = Path(r"D:\FPGA_Data\darknet\weights\yolov4.conv.137")
EXPECTED_BYTES = 170_038_676
EXPECTED_SHA256 = "11c5286cfbffabc9a3059927401ab3480e9483ceafd3265779a0dc26c769bed0"
MAX_REDIRECTS = 5
CHUNK_SIZE = 1024 * 1024
MAX_TOTAL_SECONDS = 3600.0
MAX_IDLE_SECONDS = 300.0
MAX_SOCKET_TIMEOUT_SECONDS = 60.0
ALLOWED_HOSTS = frozenset(
    {
        "github.com",
        "release-assets.githubusercontent.com",
        "github-releases.githubusercontent.com",
        "objects.githubusercontent.com",
    }
)
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
INITIAL_PATH = (
    "/AlexeyAB/darknet/releases/download/"
    "darknet_yolo_v3_optimal/yolov4.conv.137"
)
UTC8 = timezone(timedelta(hours=8))


@dataclass(frozen=True)
class Dependency:
    """记录运行前必须保持不变的只读依赖。"""

    path: str
    size: int
    sha256: str


@dataclass(frozen=True)
class MissingDependency:
    """记录在冻结基线中不存在的历史脚本路径。"""

    path: str


DEPENDENCIES = (
    Dependency(
        "report/evidence/S1-T02/20260917_s1_t02_d4_full_weight_provenance_r1.json",
        6397,
        "d32c7fdd274200c1042fc676f0ebe1e7065eab84875bb793bce6b5f76252930e",
    ),
    Dependency(
        "report/evidence/S1-T02/20260917_s1_t02_d4_full_weight_provenance_r1_summary.md",
        2804,
        "285f97bbc192527b7a743c4a1fc4b78cba1b0ac1b3b97681c24b00c4ea817561",
    ),
    Dependency(
        "report/evidence/S1-T02/20260917_s1_t02_d4_full_weight_provenance_r2.json",
        5120,
        "8d81f4b5cdd9835d23f254d47797e80c424b84593aeeb3ae079f8678a4805b4d",
    ),
    Dependency(
        "report/evidence/S1-T02/20260917_s1_t02_d4_full_weight_provenance_r2_summary.md",
        2535,
        "37f5b0d49e0001fd51a6136a22895fb8718d59b19f5ff9974763019f20216053",
    ),
    Dependency(
        "report/evidence/S1-T02/20260917_s1_t02_d4_full_weight_provenance_r3.json",
        7583,
        "e8a525cbc4eac5404bd2ba1cfd3375fbc92af22ba3654c1c1202fd7307a437b2",
    ),
    Dependency(
        "report/evidence/S1-T02/20260917_s1_t02_d4_full_weight_provenance_r3_summary.md",
        3287,
        "b9071bfac9652a2c0d1fbaaf79b8c6fbdf6be76a62cfec9e278ba59e4d75d2dd",
    ),
    Dependency(
        "report/evidence/S1-T02/20260917_s1_t02_d4_full_weight_provenance_r4.json",
        9685,
        "f487a89170ca0321981d4ef44001ce74df9dc7ebca96273ab57e2686e6f2cae6",
    ),
    Dependency(
        "report/evidence/S1-T02/20260917_s1_t02_d4_full_weight_provenance_r4_summary.md",
        2355,
        "111eefb1b1018333f9962ed4ee8e8d7cdc4f9697726002973f0109a673314529",
    ),
    Dependency(
        "report/evidence/S1-T02/s1_t02_d4_w3_safe_capture.ps1",
        14942,
        "9c0e4a546b51aa6b474023fda591b1d52475c1ee5c13c48e84227a24b954e5d3",
    ),
    Dependency(
        "report/evidence/S1-T02/s1_t02_d4_w4_safe_range_capture.py",
        29161,
        "ea831f1f143e12856f7678d1a2596f574db2702cfc07448bdec380e8a963e029",
    ),
    Dependency(
        "docs/obsidian-project/04-提交材料/阶段验收/"
        "S1-T02-D4_官方Darknet浮点基线与可复现执行.md",
        6010,
        "c926e56eb0a3b9510ee60dfb76bdf22a8e9258727531bfe7a1ed4590cf1ca03a",
    ),
)
MISSING_BASELINE_SCRIPTS = (
    MissingDependency("report/evidence/S1-T02/s1_t02_d4_w1_safe_capture.py"),
    MissingDependency("report/evidence/S1-T02/s1_t02_d4_w1_safe_capture.ps1"),
    MissingDependency("report/evidence/S1-T02/s1_t02_d4_w2_safe_capture.py"),
    MissingDependency("report/evidence/S1-T02/s1_t02_d4_w2_safe_capture.ps1"),
)


class SafeFailure(Exception):
    """只携带内部固定错误类别，不包含远端文本。"""

    def __init__(self, category: str):
        super().__init__(category)
        self.category = category


def _timestamp_utc8() -> str:
    """返回不依赖系统区域设置的东八区时间。"""

    return datetime.now(UTC8).isoformat(timespec="seconds")


def _repository_root() -> Path:
    """从本文件的固定仓库相对位置解析根目录。"""

    return Path(__file__).resolve().parents[3]


def _hash_file(path: Path) -> tuple[int, str]:
    """以有界缓冲区计算文件长度与 SHA-256。"""

    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(CHUNK_SIZE)
            if not block:
                break
            size += len(block)
            digest.update(block)
    return size, digest.hexdigest()


def _snapshot_local_weight(path: Path) -> dict[str, int | str]:
    """对本地权重做只读、有界缓冲的稳定快照。"""

    try:
        if path.is_symlink():
            raise SafeFailure("LocalWeightUnavailable")
        before = path.stat()
        if not stat.S_ISREG(before.st_mode):
            raise SafeFailure("LocalWeightUnavailable")
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            while True:
                block = stream.read(CHUNK_SIZE)
                if not block:
                    break
                size += len(block)
                digest.update(block)
        after = path.stat()
    except SafeFailure:
        raise
    except OSError:
        raise SafeFailure("LocalWeightUnavailable") from None

    before_identity = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    after_identity = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if before_identity != after_identity or size != after.st_size:
        raise SafeFailure("LocalWeightChangedError")
    return {
        "bytes": size,
        "sha256": digest.hexdigest(),
        "mtime_ns": after.st_mtime_ns,
    }


def verify_dependency_bindings(root: Path | None = None) -> tuple[bool, list[dict[str, object]]]:
    """核验冻结的 W1-W4 证据、脚本和正式 D4 文档。"""

    base = (root or _repository_root()).resolve()
    results: list[dict[str, object]] = []
    all_match = True
    for dependency in DEPENDENCIES:
        relative = Path(dependency.path)
        candidate = (base / relative).resolve()
        try:
            candidate.relative_to(base)
        except ValueError:
            all_match = False
            results.append(
                {
                    "path": dependency.path,
                    "expected_bytes": dependency.size,
                    "expected_sha256": dependency.sha256,
                    "observed_bytes": None,
                    "observed_sha256": None,
                    "matches": False,
                    "error_type": "PathBoundaryError",
                }
            )
            continue
        try:
            observed_size, observed_sha256 = _hash_file(candidate)
            matches = (
                observed_size == dependency.size
                and observed_sha256 == dependency.sha256
            )
            result: dict[str, object] = {
                "path": dependency.path,
                "expected_bytes": dependency.size,
                "expected_sha256": dependency.sha256,
                "observed_bytes": observed_size,
                "observed_sha256": observed_sha256,
                "matches": matches,
            }
            if not matches:
                result["error_type"] = "DependencyMismatch"
            all_match = all_match and matches
            results.append(result)
        except OSError:
            all_match = False
            results.append(
                {
                    "path": dependency.path,
                    "expected_bytes": dependency.size,
                    "expected_sha256": dependency.sha256,
                    "observed_bytes": None,
                    "observed_sha256": None,
                    "matches": False,
                    "error_type": "DependencyUnavailable",
                }
            )

    for dependency in MISSING_BASELINE_SCRIPTS:
        candidate = (base / dependency.path).resolve()
        try:
            candidate.relative_to(base)
            absent = not candidate.exists()
        except ValueError:
            absent = False
        results.append(
            {
                "path": dependency.path,
                "expected_state": "absent_at_frozen_baseline",
                "observed_state": "absent" if absent else "present_or_outside_root",
                "matches": absent,
            }
        )
        all_match = all_match and absent

    results.append(
        {
            "path": "D:/FPGA_Data/darknet/weights/yolov4.conv.137",
            "expected_bytes": EXPECTED_BYTES,
            "expected_sha256": EXPECTED_SHA256,
            "verification_basis": "previous_read_only_measurement",
            "read_this_run": False,
            "verified_this_run": False,
        }
    )
    return all_match, results


def _validate_url(url: str, *, initial: bool) -> tuple[str, str, str, str]:
    """验证 HTTPS、允许主机和安全请求目标，不暴露 URL 内容。"""

    if not isinstance(url, str) or any(
        ord(char) <= 0x20 or ord(char) >= 0x7F for char in url
    ):
        raise SafeFailure("RedirectRejected")
    if "\\" in url:
        raise SafeFailure("RedirectRejected")
    if initial and url != INITIAL_URL:
        raise SafeFailure("InitialUrlRejected")
    try:
        parsed = urlsplit(url)
        scheme = parsed.scheme.lower()
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        raise SafeFailure("RedirectRejected") from None
    if (
        scheme != "https"
        or host not in ALLOWED_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or port not in (None, 443)
        or not parsed.path.startswith("/")
    ):
        raise SafeFailure("RedirectRejected")
    if initial and (host != "github.com" or parsed.path != INITIAL_PATH or parsed.query):
        raise SafeFailure("InitialUrlRejected")
    if any(char in parsed.path for char in ("\r", "\n", "\x00")):
        raise SafeFailure("RedirectRejected")
    target = parsed.path or "/"
    if parsed.query:
        target += "?" + parsed.query
    if any(char in target for char in ("\r", "\n", "\x00")):
        raise SafeFailure("RedirectRejected")
    return scheme, host, parsed.path or "/", target


def _safe_endpoint(url: str, *, initial: bool) -> dict[str, str]:
    """生成不含查询参数和签名路径的端点摘要。"""

    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        if initial and url == INITIAL_URL:
            path = INITIAL_PATH
        else:
            path = "/<redacted>"
        return {"scheme": "https", "host": host, "path": path}
    except (TypeError, ValueError):
        return {"scheme": "unknown", "host": "unknown", "path": "/<redacted>"}


def _header_values(headers: Iterable[tuple[str, str]], name: str) -> list[str]:
    """从响应头中取指定项；调用者不记录原始头文本。"""

    target = name.lower()
    return [value for key, value in headers if key.lower() == target]


def _parse_content_length(headers: Iterable[tuple[str, str]]) -> int:
    """只接受单个纯十进制 Content-Length。"""

    values = _header_values(headers, "Content-Length")
    if len(values) != 1:
        raise SafeFailure("ContentLengthError")
    value = values[0].strip()
    if not value or not value.isascii() or not value.isdecimal():
        raise SafeFailure("ContentLengthError")
    try:
        return int(value, 10)
    except ValueError:
        raise SafeFailure("ContentLengthError") from None


def _content_encoding(headers: Iterable[tuple[str, str]]) -> str:
    """将编码压缩到不携带远端任意文本的有限枚举。"""

    values = _header_values(headers, "Content-Encoding")
    if not values:
        return "identity"
    if len(values) != 1:
        return "invalid"
    value = values[0].strip().lower()
    if value in {"", "identity"}:
        return "identity"
    if value in {"gzip", "deflate", "br"}:
        return value
    return "other"


def _request_timeout(
    started: float,
    last_progress: float,
    now: float,
    total_limit: float,
    idle_limit: float,
    socket_limit: float,
) -> float:
    """计算受总时限、无进度时限和 socket 上限约束的等待时间。"""

    _check_deadlines(now, started, last_progress, total_limit, idle_limit)
    total_left = total_limit - (now - started)
    idle_left = idle_limit - (now - last_progress)
    remaining = min(total_left, idle_left, socket_limit, MAX_SOCKET_TIMEOUT_SECONDS)
    if remaining <= 0:
        if total_left <= 0:
            raise SafeFailure("TotalTimeoutError")
        raise SafeFailure("IdleTimeoutError")
    return max(0.001, remaining)


def _check_deadlines(
    now: float,
    started: float,
    last_progress: float,
    total_limit: float,
    idle_limit: float,
) -> None:
    """在接受网络阶段结果或正文块前检查总时限和无正文进度时限。"""

    if now - started > total_limit:
        raise SafeFailure("TotalTimeoutError")
    if now - last_progress > idle_limit:
        raise SafeFailure("IdleTimeoutError")


def _make_https_connection(host: str, timeout: float) -> http.client.HTTPSConnection:
    """创建启用证书校验的 HTTPS 连接；关闭自动代理与调试输出。"""

    return http.client.HTTPSConnection(
        host,
        timeout=timeout,
        context=ssl.create_default_context(),
    )


def _anonymous_error(exc: BaseException) -> str:
    """把异常映射到固定类别，绝不保留异常文本或 repr。"""

    if isinstance(exc, SafeFailure):
        return exc.category
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "TimeoutError"
    if isinstance(exc, ssl.SSLError):
        return "TlsError"
    if isinstance(exc, http.client.HTTPException):
        return "HttpProtocolError"
    if isinstance(exc, OSError):
        return "ConnectionError"
    return "NetworkError"


def _worker_message(kind: str, payload: dict[str, object]) -> None:
    """向父进程发送一条 UTF-8 JSON 协议消息并立即刷新。"""

    sys.stdout.write(
        json.dumps(
            {"kind": kind, **payload},
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )
    sys.stdout.flush()


def _timeout_report(
    snapshot: dict[str, object], *, elapsed_seconds: float, error_type: str
) -> dict[str, object]:
    """生成不接纳 worker 部分哈希或正文数据的超时报告。"""

    report = _emergency_failure_report(error_type)
    attempts = int(snapshot.get("request_attempt_count", 0))
    confirmed = int(snapshot.get("confirmed_get_count", 0))
    responses = int(snapshot.get("http_response_count", 0))
    statuses = snapshot.get("http_statuses", [])
    report.update(
        {
            "request_attempt_count": attempts,
            "confirmed_get_count": confirmed,
            "http_response_count": responses,
            "actual_get_count": confirmed if attempts == confirmed else None,
            "http_statuses": list(statuses) if isinstance(statuses, list) else [],
            "redirect_count": int(snapshot.get("redirect_count", 0)),
            "final_status": snapshot.get("final_status"),
            "content_length": snapshot.get("content_length"),
            "content_encoding": snapshot.get("content_encoding", "unknown"),
            "bytes_read": 0,
            "sha256": None,
            "hash_matches": None,
            "elapsed_seconds": round(max(0.0, elapsed_seconds), 3),
        }
    )
    return report


_PROGRESS_DISPATCH_LOCK = threading.Lock()
_PROGRESS_DISPATCH_QUEUE: queue.Queue[
    tuple[Callable[[dict[str, object]], None], dict[str, object]] | None
] | None = None
_PROGRESS_DISPATCH_THREAD: threading.Thread | None = None
_PROGRESS_DISPATCH_READY: threading.Event | None = None


def _dispatch_progress_records(
    pending: queue.Queue[
        tuple[Callable[[dict[str, object]], None], dict[str, object]] | None
    ],
    ready: threading.Event,
) -> None:
    """在唯一后台线程中尽力交付记录；用户回调错误不影响网络结果。"""

    ready.set()
    while True:
        item = pending.get()
        if item is None:
            return
        callback, record = item
        try:
            callback(record)
        except BaseException:
            continue


def _start_progress_dispatcher(
    callback: Callable[[dict[str, object]], None] | None,
    *,
    deadline: float,
    on_dispatcher_start: Callable[
        [
            threading.Thread,
            queue.Queue[
                tuple[Callable[[dict[str, object]], None], dict[str, object]] | None
            ],
            threading.Event,
        ],
        None,
    ]
    | None = None,
) -> tuple[Callable[[dict[str, object]], None], bool]:
    """以单个进程级 daemon 和 8 项队列尽力交付进度。

    用户回调异常（包括迟到异常）会被吞掉，不改变网络结果。回调永久阻塞时，
    最多保留这一条进程级线程；队列覆盖旧快照，不为后续任务增建线程。
    """

    if callback is None:
        return lambda _record: None, False

    global _PROGRESS_DISPATCH_QUEUE, _PROGRESS_DISPATCH_THREAD, _PROGRESS_DISPATCH_READY
    remaining = max(0.0, deadline - time.monotonic())
    if not _PROGRESS_DISPATCH_LOCK.acquire(timeout=remaining):
        raise RuntimeError("callback dispatcher lock timed out")
    try:
        if (
            _PROGRESS_DISPATCH_QUEUE is None
            or _PROGRESS_DISPATCH_THREAD is None
            or not _PROGRESS_DISPATCH_THREAD.is_alive()
        ):
            pending: queue.Queue[
                tuple[Callable[[dict[str, object]], None], dict[str, object]] | None
            ] = queue.Queue(maxsize=8)
            ready = threading.Event()
            thread = threading.Thread(
                target=_dispatch_progress_records,
                args=(pending, ready),
                name="w5-progress-callback",
                daemon=True,
            )
            _PROGRESS_DISPATCH_QUEUE = pending
            _PROGRESS_DISPATCH_THREAD = thread
            _PROGRESS_DISPATCH_READY = ready
            if on_dispatcher_start is not None:
                on_dispatcher_start(thread, pending, ready)
            thread.start()
        else:
            assert _PROGRESS_DISPATCH_READY is not None
            thread = _PROGRESS_DISPATCH_THREAD
            pending = _PROGRESS_DISPATCH_QUEUE
            ready = _PROGRESS_DISPATCH_READY
            if on_dispatcher_start is not None:
                on_dispatcher_start(thread, pending, ready)
        if not ready.wait(timeout=max(0.0, deadline - time.monotonic())):
            raise RuntimeError("callback dispatcher not ready")
        dispatcher_queue = _PROGRESS_DISPATCH_QUEUE
    finally:
        _PROGRESS_DISPATCH_LOCK.release()

    def enqueue(record: dict[str, object]) -> None:
        """队列拥塞时丢弃旧快照，保留最新累计状态且不等待用户代码。"""

        assert dispatcher_queue is not None
        item = (callback, record)
        try:
            dispatcher_queue.put_nowait(item)
        except queue.Full:
            try:
                dispatcher_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                dispatcher_queue.put_nowait(item)
            except queue.Full:
                pass

    return enqueue, True


def _stop_starting_progress_dispatcher(
    thread: threading.Thread | None,
    pending: queue.Queue[
        tuple[Callable[[dict[str, object]], None], dict[str, object]] | None
    ]
    | None,
    *,
    deadline: float,
) -> bool | None:
    """停止启动未完成的 dispatcher，并在总期限内等待线程退出。"""

    if thread is None:
        return None
    if thread.ident is None:
        stopped = True
    else:
        if thread.is_alive() and pending is not None:
            try:
                pending.put_nowait(None)
            except queue.Full:
                try:
                    pending.get_nowait()
                except queue.Empty:
                    pass
                try:
                    pending.put_nowait(None)
                except queue.Full:
                    pass
        if thread.is_alive():
            try:
                thread.join(timeout=max(0.0, deadline - time.monotonic()))
            except RuntimeError:
                pass
        stopped = not thread.is_alive()

    if stopped:
        global _PROGRESS_DISPATCH_QUEUE, _PROGRESS_DISPATCH_THREAD, _PROGRESS_DISPATCH_READY
        lock_remaining = max(0.0, deadline - time.monotonic())
        lock_acquired = _PROGRESS_DISPATCH_LOCK.acquire(timeout=lock_remaining)
        if lock_acquired:
            if _PROGRESS_DISPATCH_THREAD is thread:
                _PROGRESS_DISPATCH_QUEUE = None
                _PROGRESS_DISPATCH_THREAD = None
                _PROGRESS_DISPATCH_READY = None
            _PROGRESS_DISPATCH_LOCK.release()
    return stopped


def _worker_report_is_consistent(report: object) -> bool:
    """校验 worker 最终报告的必要字段、计数关系和成功摘要绑定。"""

    if not isinstance(report, dict):
        return False
    required = {
        "task_id",
        "exit_code",
        "error_type",
        "request_attempt_count",
        "confirmed_get_count",
        "http_response_count",
        "actual_get_count",
        "http_statuses",
        "content_length",
        "content_encoding",
        "bytes_read",
        "sha256",
        "expected_local_sha256",
        "hash_matches",
        "dependency_bindings",
        "local_weight_binding",
        "license",
    }
    if not required.issubset(report):
        return False
    if report["task_id"] != TASK_ID or type(report["exit_code"]) is not int:
        return False
    if report["exit_code"] not in (0, 1):
        return False
    if report["license"] != "UNRESOLVED":
        return False

    attempts = report["request_attempt_count"]
    confirmed = report["confirmed_get_count"]
    responses = report["http_response_count"]
    bytes_read = report["bytes_read"]
    if any(type(value) is not int or value < 0 for value in (attempts, confirmed, responses, bytes_read)):
        return False
    if confirmed > attempts or attempts - confirmed > 1:
        return False
    if responses > confirmed or confirmed - responses > 1:
        return False
    expected_actual = confirmed if attempts == confirmed else None
    if report["actual_get_count"] != expected_actual:
        return False

    statuses = report["http_statuses"]
    if (
        not isinstance(statuses, list)
        or len(statuses) > responses
        or any(type(status) is not int or not 100 <= status <= 599 for status in statuses)
    ):
        return False
    final_status = report.get("final_status")
    if statuses and final_status != statuses[-1]:
        return False

    expected_sha = report["expected_local_sha256"]
    actual_sha = report["sha256"]
    valid_hash = lambda value: (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )
    if not valid_hash(expected_sha):
        return False
    if actual_sha is not None and not valid_hash(actual_sha):
        return False
    if report["hash_matches"] is not None and type(report["hash_matches"]) is not bool:
        return False
    dependency_bindings = report["dependency_bindings"]
    if not isinstance(dependency_bindings, list) or any(
        not isinstance(item, dict) for item in dependency_bindings
    ):
        return False
    binding = report["local_weight_binding"]
    if not isinstance(binding, dict):
        return False

    if report["exit_code"] == 1:
        return isinstance(report["error_type"], str) and bool(report["error_type"])

    if not _successful_dependency_bindings_are_complete(dependency_bindings):
        return False

    expected_bytes = binding.get("expected_bytes")
    return (
        report["error_type"] is None
        and attempts == confirmed == responses
        and confirmed > 0
        and len(statuses) == responses
        and report["actual_get_count"] == confirmed
        and final_status == 200
        and report["content_encoding"] == "identity"
        and type(expected_bytes) is int
        and expected_bytes > 0
        and type(report["content_length"]) is int
        and report["content_length"] == expected_bytes
        and bytes_read == expected_bytes
        and report["hash_matches"] is True
        and actual_sha == expected_sha
        and binding.get("expected_sha256") == expected_sha
        and binding.get("matches_expected") is True
        and binding.get("stable") is True
        and binding.get("matches_remote") is True
    )


def _successful_dependency_bindings_are_complete(
    bindings: list[dict[str, object]],
) -> bool:
    """要求成功报告完整绑定固定 W1-W4 集及独立权重元数据行。"""

    expected_paths = {
        dependency.path: dependency for dependency in DEPENDENCIES
    }
    missing_paths = {
        dependency.path for dependency in MISSING_BASELINE_SCRIPTS
    }
    measurement_path = "D:/FPGA_Data/darknet/weights/yolov4.conv.137"
    expected_count = len(expected_paths) + len(missing_paths) + 1
    if len(bindings) != expected_count:
        return False

    seen: set[str] = set()
    measurement_seen = False
    for item in bindings:
        path = item.get("path")
        if not isinstance(path, str) or path in seen:
            return False
        seen.add(path)

        dependency = expected_paths.get(path)
        if dependency is not None:
            if (
                type(item.get("expected_bytes")) is not int
                or item["expected_bytes"] != dependency.size
                or item.get("expected_sha256") != dependency.sha256
                or type(item.get("observed_bytes")) is not int
                or item["observed_bytes"] != dependency.size
                or item.get("observed_sha256") != dependency.sha256
                or item.get("matches") is not True
            ):
                return False
            continue

        if path in missing_paths:
            if (
                item.get("expected_state") != "absent_at_frozen_baseline"
                or item.get("observed_state") != "absent"
                or item.get("matches") is not True
            ):
                return False
            continue

        if path == measurement_path and not measurement_seen:
            if (
                item.get("expected_bytes") != EXPECTED_BYTES
                or item.get("expected_sha256") != EXPECTED_SHA256
                or item.get("verification_basis") != "previous_read_only_measurement"
                or item.get("read_this_run") is not False
                or item.get("verified_this_run") is not False
                or "matches" in item
            ):
                return False
            measurement_seen = True
            continue

        # 未知路径、伪造的额外 matches 行和重复元数据行均不能被忽略。
        return False

    return seen == (set(expected_paths) | missing_paths | {measurement_path}) and measurement_seen


def _run_supervised_process(
    command: Sequence[str],
    *,
    total_timeout: float,
    progress_callback: Callable[[dict[str, object]], None] | None = None,
    start_gate: bool = False,
) -> tuple[dict[str, object], dict[str, object]]:
    """在父级绝对期限内收集子进程消息，超时时终止并等待 worker 退出。"""

    started = time.monotonic()
    deadline = started + total_timeout
    cleanup_reserve = min(2.0, total_timeout * 0.5)
    operation_deadline = deadline - cleanup_reserve
    last_snapshot: dict[str, object] = {}
    messages: queue.Queue[object] = queue.Queue()
    try:
        process = subprocess.Popen(
            list(command),
            stdin=subprocess.PIPE if start_gate else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if sys.platform == "win32"
                else 0
            ),
        )
    except Exception:
        return _emergency_failure_report("WorkerStartError"), {
            "worker_pid": None,
            "worker_exit_code": None,
            "worker_terminated": True,
            "reader_stopped": True,
            "callback_dispatcher_started": False,
            "callback_dispatcher_stopped": None,
            "worker_ready": False,
            "timed_out": False,
        }

    reader_stop_requested = threading.Event()

    def read_messages() -> None:
        """从 worker 管道持续读行，避免父进程阻塞在未完成的 readline。"""

        assert process.stdout is not None
        try:
            for line in process.stdout:
                messages.put(line)
        except (OSError, ValueError):
            if not reader_stop_requested.is_set():
                messages.put({"kind": "reader-error"})
        finally:
            messages.put(None)
            try:
                process.stdout.close()
            except (OSError, ValueError):
                pass

    reader: threading.Thread | None = None
    dispatcher_ready = False
    dispatcher_thread: threading.Thread | None = None
    dispatcher_queue: queue.Queue[
        tuple[Callable[[dict[str, object]], None], dict[str, object]] | None
    ] | None = None
    worker_ready = False
    enqueue_progress: Callable[[dict[str, object]], None] = lambda _record: None

    def track_dispatcher(
        thread: threading.Thread,
        pending: queue.Queue[
            tuple[Callable[[dict[str, object]], None], dict[str, object]] | None
        ],
        _ready: threading.Event,
    ) -> None:
        """保留尚在启动中的共享 dispatcher，供父级超时回收。"""

        nonlocal dispatcher_thread, dispatcher_queue
        dispatcher_thread = thread
        dispatcher_queue = pending

    def cleanup_worker(
        *,
        reason: str,
        stop_reader: bool,
    ) -> tuple[dict[str, object], dict[str, object]]:
        """按绝对期限剩余时间回收 worker/reader，并关闭管道。"""

        if process.poll() is None:
            try:
                process.kill()
            except OSError:
                pass
        exit_code: int | None
        remaining = max(0.0, deadline - time.monotonic())
        try:
            exit_code = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            exit_code = process.poll()
        if process.stdin is not None:
            try:
                process.stdin.close()
            except Exception:
                pass
        if stop_reader:
            reader_stop_requested.set()
        if process.stdout is not None and stop_reader:
            try:
                process.stdout.close()
            except (OSError, ValueError):
                pass
        if reader is not None and reader.is_alive() and stop_reader:
            try:
                reader.join(timeout=max(0.0, deadline - time.monotonic()))
            except RuntimeError:
                pass
        dispatcher_stopped: bool | None = None
        if dispatcher_thread is not None and not dispatcher_ready:
            dispatcher_stopped = _stop_starting_progress_dispatcher(
                dispatcher_thread,
                dispatcher_queue,
                deadline=deadline,
            )
        worker_stopped = process.poll() is not None
        reader_stopped = reader is None or not reader.is_alive()
        if not worker_stopped:
            final_error_type = "WorkerTerminationError"
        elif dispatcher_stopped is False:
            final_error_type = "CallbackDispatcherTerminationError"
        else:
            final_error_type = reason
        report = _timeout_report(
            last_snapshot,
            elapsed_seconds=time.monotonic() - started,
            error_type=final_error_type,
        )
        return report, {
            "worker_pid": process.pid,
            "worker_exit_code": exit_code,
            "worker_terminated": worker_stopped,
            "reader_stopped": reader_stopped,
            "callback_dispatcher_started": dispatcher_ready,
            "callback_dispatcher_stopped": dispatcher_stopped,
            "worker_ready": worker_ready,
            "timed_out": reason == "TotalTimeoutError",
        }

    try:
        reader = threading.Thread(
            target=read_messages,
            name="w5-worker-reader",
            daemon=True,
        )
        reader.start()
        enqueue_progress, dispatcher_ready = _start_progress_dispatcher(
            progress_callback,
            deadline=operation_deadline,
            on_dispatcher_start=track_dispatcher,
        )
    except BaseException as exc:
        if isinstance(exc, KeyboardInterrupt):
            reason = "InterruptedError"
        elif time.monotonic() >= operation_deadline:
            reason = "TotalTimeoutError"
        else:
            reason = "WorkerSetupError"
        return cleanup_worker(reason=reason, stop_reader=True)

    def terminate(error_type: str, *, timed_out: bool) -> tuple[dict[str, object], dict[str, object]]:
        """超时或协议失败时强制结束 worker，不接受其部分结果。"""

        report, lifecycle = cleanup_worker(reason=error_type, stop_reader=True)
        lifecycle["timed_out"] = timed_out
        return report, lifecycle

    if start_gate:
        while True:
            remaining = operation_deadline - time.monotonic()
            if remaining <= 0:
                return terminate("TotalTimeoutError", timed_out=True)
            try:
                line = messages.get(timeout=remaining)
            except KeyboardInterrupt:
                return terminate("InterruptedError", timed_out=False)
            except queue.Empty:
                return terminate("TotalTimeoutError", timed_out=True)
            if time.monotonic() >= operation_deadline:
                return terminate("TotalTimeoutError", timed_out=True)
            if line is None or not isinstance(line, str):
                return terminate("WorkerProtocolError", timed_out=False)
            try:
                ready_message = json.loads(line)
            except Exception:
                return terminate("WorkerProtocolError", timed_out=False)
            if ready_message != {"kind": "ready"}:
                return terminate("WorkerProtocolError", timed_out=False)
            worker_ready = True
            break
        try:
            if process.stdin is None:
                raise RuntimeError("worker gate unavailable")
            process.stdin.write("start\n")
            process.stdin.flush()
            process.stdin.close()
        except BaseException as exc:
            reason = "InterruptedError" if isinstance(exc, KeyboardInterrupt) else "WorkerSetupError"
            return terminate(reason, timed_out=False)

    while True:
        remaining = operation_deadline - time.monotonic()
        if remaining <= 0:
            return terminate("TotalTimeoutError", timed_out=True)
        try:
            line = messages.get(timeout=remaining)
        except KeyboardInterrupt:
            return terminate("InterruptedError", timed_out=False)
        except queue.Empty:
            return terminate("TotalTimeoutError", timed_out=True)
        if time.monotonic() >= operation_deadline:
            return terminate("TotalTimeoutError", timed_out=True)
        if line is None:
            error_type = "WorkerProtocolError" if process.poll() == 0 else "WorkerExitError"
            return terminate(error_type, timed_out=False)
        if not isinstance(line, str):
            return terminate("WorkerProtocolError", timed_out=False)
        try:
            message = json.loads(line)
            kind = message.get("kind")
            if kind == "state" and isinstance(message.get("state"), dict):
                last_snapshot = message["state"]
            elif kind == "progress" and isinstance(message.get("record"), dict):
                enqueue_progress(message["record"])
            elif kind == "result" and isinstance(message.get("report"), dict):
                remaining = operation_deadline - time.monotonic()
                if remaining <= 0:
                    return terminate("TotalTimeoutError", timed_out=True)
                try:
                    exit_code = process.wait(timeout=remaining)
                except KeyboardInterrupt:
                    return terminate("InterruptedError", timed_out=False)
                except subprocess.TimeoutExpired:
                    return terminate("TotalTimeoutError", timed_out=True)
                if time.monotonic() >= operation_deadline:
                    return terminate("TotalTimeoutError", timed_out=True)
                remaining = max(0.0, operation_deadline - time.monotonic())
                reader.join(timeout=remaining)
                if reader.is_alive() or time.monotonic() >= operation_deadline:
                    return terminate("WorkerCleanupTimeoutError", timed_out=True)
                report = message["report"]
                if (
                    type(exit_code) is not int
                    or exit_code not in (0, 1)
                    or not _worker_report_is_consistent(report)
                    or exit_code != report.get("exit_code")
                ):
                    return terminate("WorkerExitError", timed_out=False)
                return message["report"], {
                    "worker_pid": process.pid,
                    "worker_exit_code": exit_code,
                    "worker_terminated": exit_code is not None,
                    "reader_stopped": True,
                    "callback_dispatcher_started": dispatcher_ready,
                    "callback_dispatcher_stopped": None,
                    "worker_ready": worker_ready,
                    "timed_out": False,
                }
            else:
                return terminate("WorkerProtocolError", timed_out=False)
        except Exception:
            return terminate("WorkerProtocolError", timed_out=False)


def _worker_process_main(encoded_options: str) -> int:
    """子进程入口：独占执行 DNS、TLS、HTTP 和正文读取。"""

    try:
        _worker_message("ready", {})
        if sys.stdin.readline() != "start\n":
            return 1
    except Exception:
        return 1
    try:
        raw = base64.urlsafe_b64decode(encoded_options.encode("ascii"))
        options = json.loads(raw.decode("utf-8"))
        allowed = {
            "initial_url",
            "local_weight_path",
            "progress_interval",
            "expected_bytes",
            "expected_sha256",
            "max_redirects",
            "chunk_size",
            "total_timeout",
            "idle_timeout",
            "socket_timeout",
        }
        if not isinstance(options, dict) or set(options) != allowed:
            raise ValueError
        options["local_weight_path"] = Path(options["local_weight_path"])
        report = _verify_remote_asset_impl(
            connection_factory=_make_https_connection,
            dependency_check=None,
            progress_callback=lambda record: _worker_message("progress", {"record": record}),
            stage_callback=lambda state: _worker_message("state", {"state": state}),
            **options,
        )
    except BaseException as exc:
        if isinstance(exc, KeyboardInterrupt):
            report = _emergency_failure_report("InterruptedError")
        else:
            report = _emergency_failure_report("WorkerInternalError")
    try:
        _worker_message("result", {"report": report})
    except Exception:
        return 1
    return int(report.get("exit_code", 1))


def verify_remote_asset(**options: object) -> dict[str, object]:
    """纯 API 默认离线；显式 HTTPS factory 的网络路径由硬期限 worker 执行。"""

    factory = options.get("connection_factory")
    if factory is None:
        return _verify_remote_asset_impl(**options)
    if factory is not _make_https_connection:
        return _emergency_failure_report("CustomTransportRejected")
    if options.get("dependency_check") is not None:
        return _emergency_failure_report("ConfigurationError")
    if options.get("monotonic", time.monotonic) is not time.monotonic:
        return _emergency_failure_report("ConfigurationError")

    total_timeout = options.get("total_timeout", MAX_TOTAL_SECONDS)
    if not isinstance(total_timeout, (int, float)) or not 0 < total_timeout <= MAX_TOTAL_SECONDS:
        return _verify_remote_asset_impl(**options)
    defaults: dict[str, object] = {
        "initial_url": INITIAL_URL,
        "local_weight_path": LOCAL_WEIGHT_PATH,
        "progress_interval": 60.0,
        "expected_bytes": EXPECTED_BYTES,
        "expected_sha256": EXPECTED_SHA256,
        "max_redirects": MAX_REDIRECTS,
        "chunk_size": CHUNK_SIZE,
        "total_timeout": MAX_TOTAL_SECONDS,
        "idle_timeout": MAX_IDLE_SECONDS,
        "socket_timeout": MAX_SOCKET_TIMEOUT_SECONDS,
    }
    serializable = {key: options.get(key, value) for key, value in defaults.items()}
    serializable["local_weight_path"] = str(serializable["local_weight_path"])
    try:
        encoded = base64.urlsafe_b64encode(
            json.dumps(serializable, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
        ).decode("ascii")
        bootstrap = (
            "import importlib.util,sys;"
            "spec=importlib.util.spec_from_file_location('_w5_worker',sys.argv[1]);"
            "module=importlib.util.module_from_spec(spec);"
            "sys.modules[spec.name]=module;"
            "spec.loader.exec_module(module);"
            "raise SystemExit(module._worker_process_main(sys.argv[2]))"
        )
        command = [
            sys.executable,
            "-c",
            bootstrap,
            str(Path(__file__).resolve()),
            encoded,
        ]
        report, _worker = _run_supervised_process(
            command,
            total_timeout=float(total_timeout),
            progress_callback=options.get("progress_callback"),
            start_gate=True,
        )
        return report
    except Exception:
        return _emergency_failure_report("WorkerSupervisorError")


def _verify_remote_asset_impl(
    *,
    initial_url: str = INITIAL_URL,
    connection_factory: Callable[[str, float], object] | None = None,
    dependency_check: Callable[[], tuple[bool, list[dict[str, object]]]] | None = None,
    local_weight_path: Path = LOCAL_WEIGHT_PATH,
    progress_callback: Callable[[dict[str, object]], None] | None = None,
    progress_interval: float = 60.0,
    expected_bytes: int = EXPECTED_BYTES,
    expected_sha256: str = EXPECTED_SHA256,
    max_redirects: int = MAX_REDIRECTS,
    chunk_size: int = CHUNK_SIZE,
    total_timeout: float = MAX_TOTAL_SECONDS,
    idle_timeout: float = MAX_IDLE_SECONDS,
    socket_timeout: float = MAX_SOCKET_TIMEOUT_SECONDS,
    monotonic: Callable[[], float] = time.monotonic,
    stage_callback: Callable[[dict[str, object]], None] | None = None,
) -> dict[str, object]:
    """执行流式核验核心；公共 HTTPS 入口在隔离 worker 中调用本函数。"""

    started_wall = _timestamp_utc8()
    started = monotonic()
    last_progress = started
    last_progress_emit = started
    statuses: list[int] = []
    endpoints: list[dict[str, str]] = []
    request_attempt_count = 0
    http_response_count = 0
    confirmed_get_count = 0
    followed_redirects = 0
    content_length: int | None = None
    content_encoding = "unknown"
    bytes_read = 0
    digest = hashlib.sha256()
    actual_sha256: str | None = None
    hash_matches: bool | None = None
    error_type: str | None = None
    dependency_results: list[dict[str, object]] = []
    local_weight_binding: dict[str, object] = {
        "path": str(local_weight_path),
        "expected_bytes": expected_bytes,
        "expected_sha256": expected_sha256,
        "before": None,
        "after": None,
        "matches_expected": False,
        "stable": None,
        "matches_remote": False,
    }
    local_before_snapshot: dict[str, int | str] | None = None
    exit_code = 1
    final_status: int | None = None

    def emit_state(stage: str) -> None:
        """在可能阻塞的网络调用前后发送最小计数快照。"""

        if stage_callback is None:
            return
        state: dict[str, object] = {
            "stage": stage,
            "request_attempt_count": request_attempt_count,
            "confirmed_get_count": confirmed_get_count,
            "http_response_count": http_response_count,
            "http_statuses": list(statuses),
            "redirect_count": followed_redirects,
            "final_status": final_status,
            "content_length": content_length,
            "content_encoding": content_encoding,
        }
        stage_callback(state)

    def emit_progress_if_due(now: float) -> None:
        """仅向回调发送固定字段的安全进度，不含对象摘要或输入文本。"""

        nonlocal last_progress_emit
        if progress_callback is None or now - last_progress_emit < progress_interval:
            return
        record: dict[str, object] = {
            "event": "progress",
            "timestamp_utc8": _timestamp_utc8(),
            "bytes_read": bytes_read,
            "elapsed_seconds": round(max(0.0, now - started), 3),
            "request_attempt_count": request_attempt_count,
            "http_response_count": http_response_count,
            "confirmed_get_count": confirmed_get_count,
            "actual_get_count": confirmed_get_count if request_attempt_count == confirmed_get_count else None,
            "redirect_count": followed_redirects,
            "status_count": len(statuses),
            "http_statuses": list(statuses),
        }
        try:
            progress_callback(record)
        except Exception:
            raise SafeFailure("ProgressCallbackError") from None
        last_progress_emit = now

    def base_report() -> dict[str, object]:
        return {
            "task_id": TASK_ID,
            "started_at_utc8": started_wall,
            "completed_at_utc8": _timestamp_utc8(),
            "endpoints": endpoints,
            "http_statuses": statuses,
            "request_attempt_count": request_attempt_count,
            "http_response_count": http_response_count,
            "confirmed_get_count": confirmed_get_count,
            "actual_get_count": confirmed_get_count if request_attempt_count == confirmed_get_count else None,
            "redirect_count": followed_redirects,
            "final_status": final_status,
            "content_length": content_length,
            "content_encoding": content_encoding,
            "bytes_read": bytes_read,
            "sha256": actual_sha256,
            "expected_local_sha256": expected_sha256,
            "hash_matches": hash_matches,
            "elapsed_seconds": round(max(0.0, monotonic() - started), 3),
            "error_type": error_type,
            "exit_code": exit_code,
            "dependency_bindings": dependency_results,
            "local_weight_binding": local_weight_binding,
            "license": "UNRESOLVED",
        }

    try:
        if connection_factory is None:
            raise SafeFailure("NetworkExecutionNotAuthorized")
        if (
            expected_bytes <= 0
            or len(expected_sha256) != 64
            or any(char not in "0123456789abcdef" for char in expected_sha256.lower())
            or not 0 <= max_redirects <= MAX_REDIRECTS
            or not 0 < chunk_size <= CHUNK_SIZE
            or not 0 < total_timeout <= MAX_TOTAL_SECONDS
            or not 0 < idle_timeout <= MAX_IDLE_SECONDS
            or not 0 < socket_timeout <= MAX_SOCKET_TIMEOUT_SECONDS
            or not 0 < progress_interval <= MAX_SOCKET_TIMEOUT_SECONDS
        ):
            raise SafeFailure("ConfigurationError")

        _validate_url(initial_url, initial=True)
        if dependency_check is None:
            dependencies_ok, dependency_results = verify_dependency_bindings()
        else:
            dependencies_ok, dependency_results = dependency_check()
        if not dependencies_ok:
            raise SafeFailure("DependencyBindingError")

        local_before_snapshot = _snapshot_local_weight(Path(local_weight_path))
        local_weight_binding["before"] = local_before_snapshot
        local_matches_expected = (
            local_before_snapshot["bytes"] == expected_bytes
            and local_before_snapshot["sha256"] == expected_sha256
        )
        local_weight_binding["matches_expected"] = local_matches_expected
        if not local_matches_expected:
            raise SafeFailure("LocalWeightMismatchError")

        current_url = initial_url
        seen_urls = {current_url}
        while True:
            _check_deadlines(
                monotonic(), started, last_progress, total_timeout, idle_timeout
            )
            scheme, host, _path, target = _validate_url(
                current_url, initial=(request_attempt_count == 0)
            )
            del scheme
            endpoints.append(
                _safe_endpoint(current_url, initial=(request_attempt_count == 0))
            )
            timeout = _request_timeout(
                started,
                last_progress,
                monotonic(),
                total_timeout,
                idle_timeout,
                socket_timeout,
            )
            emit_state("connection_start")
            connection = connection_factory(host, timeout)
            emit_state("connection_ready")
            now = monotonic()
            _check_deadlines(now, started, last_progress, total_timeout, idle_timeout)
            response = None
            try:
                timeout = _request_timeout(
                    started,
                    last_progress,
                    monotonic(),
                    total_timeout,
                    idle_timeout,
                    socket_timeout,
                )
                sock = getattr(connection, "sock", None)
                if sock is not None:
                    sock.settimeout(timeout)
                request_attempt_count += 1
                emit_state("request_start")
                connection.request(
                    "GET",
                    target,
                    headers={
                        "Accept-Encoding": "identity",
                        "Connection": "close",
                        "User-Agent": "GestureForge-S1-T02-D4-W5/1.0",
                    },
                )
                confirmed_get_count += 1
                emit_state("request_sent")
                now = monotonic()
                _check_deadlines(now, started, last_progress, total_timeout, idle_timeout)
                emit_progress_if_due(now)
                timeout = _request_timeout(
                    started,
                    last_progress,
                    now,
                    total_timeout,
                    idle_timeout,
                    socket_timeout,
                )
                sock = getattr(connection, "sock", None)
                if sock is not None:
                    sock.settimeout(timeout)
                emit_state("response_start")
                response = connection.getresponse()
                http_response_count += 1
                emit_state("response_received")
                now = monotonic()
                _check_deadlines(now, started, last_progress, total_timeout, idle_timeout)
                final_status = int(response.status)
                statuses.append(final_status)
                emit_progress_if_due(now)
                if final_status in REDIRECT_STATUSES:
                    if followed_redirects >= max_redirects:
                        raise SafeFailure("RedirectLimitError")
                    timeout = _request_timeout(
                        started,
                        last_progress,
                        monotonic(),
                        total_timeout,
                        idle_timeout,
                        socket_timeout,
                    )
                    sock = getattr(connection, "sock", None)
                    if sock is not None:
                        sock.settimeout(timeout)
                    emit_state("headers_start")
                    headers = response.getheaders()
                    now = monotonic()
                    _check_deadlines(
                        now, started, last_progress, total_timeout, idle_timeout
                    )
                    emit_progress_if_due(now)
                    location_values = _header_values(headers, "Location")
                    if len(location_values) != 1:
                        raise SafeFailure("RedirectRejected")
                    next_url = urljoin(current_url, location_values[0])
                    _validate_url(next_url, initial=False)
                    if next_url in seen_urls:
                        raise SafeFailure("RedirectLoopError")
                    followed_redirects += 1
                    seen_urls.add(next_url)
                    current_url = next_url
                    continue

                if final_status != 200:
                    raise SafeFailure("HttpStatusError")
                timeout = _request_timeout(
                    started,
                    last_progress,
                    monotonic(),
                    total_timeout,
                    idle_timeout,
                    socket_timeout,
                )
                sock = getattr(connection, "sock", None)
                if sock is not None:
                    sock.settimeout(timeout)
                emit_state("headers_start")
                headers = response.getheaders()
                now = monotonic()
                _check_deadlines(now, started, last_progress, total_timeout, idle_timeout)
                emit_progress_if_due(now)
                content_length = _parse_content_length(headers)
                content_encoding = _content_encoding(headers)
                if content_encoding != "identity":
                    raise SafeFailure("ContentEncodingError")
                if _header_values(headers, "Transfer-Encoding"):
                    raise SafeFailure("TransferEncodingError")
                if content_length != expected_bytes:
                    raise SafeFailure("ContentLengthError")

                while True:
                    now = monotonic()
                    timeout = _request_timeout(
                        started,
                        last_progress,
                        now,
                        total_timeout,
                        idle_timeout,
                        socket_timeout,
                    )
                    if progress_callback is not None:
                        progress_remaining = progress_interval - (
                            now - last_progress_emit
                        )
                        timeout = min(timeout, max(0.001, progress_remaining))
                    sock = getattr(connection, "sock", None)
                    if sock is not None:
                        sock.settimeout(timeout)
                    read_size = min(chunk_size, expected_bytes - bytes_read + 1)
                    try:
                        read1 = getattr(response, "read1", None)
                        if not callable(read1):
                            raise SafeFailure("HttpProtocolError")
                        emit_state("body_read_start")
                        block = read1(read_size)
                    except (socket.timeout, TimeoutError):
                        now = monotonic()
                        _check_deadlines(
                            now, started, last_progress, total_timeout, idle_timeout
                        )
                        emit_progress_if_due(now)
                        continue
                    now = monotonic()
                    _check_deadlines(
                        now, started, last_progress, total_timeout, idle_timeout
                    )
                    if not isinstance(block, bytes):
                        raise SafeFailure("HttpProtocolError")
                    if not block:
                        emit_progress_if_due(now)
                        break
                    bytes_read += len(block)
                    digest.update(block)
                    if bytes_read > expected_bytes:
                        raise SafeFailure("SizeLimitError")
                    last_progress = now
                    emit_state("body_read_complete")
                    emit_progress_if_due(last_progress)

                actual_sha256 = digest.hexdigest()
                if bytes_read != expected_bytes:
                    raise SafeFailure("ShortReadError")
                hash_matches = actual_sha256 == expected_sha256
                if not hash_matches:
                    raise SafeFailure("HashMismatchError")
                exit_code = 0
                break
            finally:
                if response is not None:
                    try:
                        response.close()
                    except Exception:
                        pass
                try:
                    connection.close()
                except Exception:
                    pass
    except KeyboardInterrupt:
        error_type = "InterruptedError"
        if bytes_read and actual_sha256 is None:
            actual_sha256 = digest.hexdigest()
        if bytes_read != expected_bytes:
            hash_matches = None
    except Exception as exc:
        error_type = _anonymous_error(exc)
        if bytes_read and actual_sha256 is None:
            actual_sha256 = digest.hexdigest()
        if bytes_read != expected_bytes:
            hash_matches = None

    if local_before_snapshot is not None and request_attempt_count > 0:
        try:
            local_after_snapshot = _snapshot_local_weight(Path(local_weight_path))
            local_weight_binding["after"] = local_after_snapshot
            stable = all(
                local_before_snapshot[key] == local_after_snapshot[key]
                for key in ("bytes", "sha256", "mtime_ns")
            )
            local_weight_binding["stable"] = stable
            matches_remote = (
                stable
                and local_before_snapshot["bytes"] == expected_bytes
                and local_after_snapshot["bytes"] == expected_bytes
                and local_before_snapshot["sha256"] == expected_sha256
                and local_after_snapshot["sha256"] == expected_sha256
                and actual_sha256 == local_before_snapshot["sha256"]
                and actual_sha256 == local_after_snapshot["sha256"]
            )
            local_weight_binding["matches_remote"] = matches_remote
            if not stable:
                error_type = "LocalWeightChangedError"
                exit_code = 1
            elif exit_code == 0 and not matches_remote:
                error_type = "LocalWeightMismatchError"
                exit_code = 1
        except SafeFailure as exc:
            local_weight_binding["post_error_type"] = exc.category
            local_weight_binding["stable"] = False
            local_weight_binding["matches_remote"] = False
            error_type = exc.category
            exit_code = 1
        except Exception:
            local_weight_binding["post_error_type"] = "LocalWeightUnavailable"
            local_weight_binding["stable"] = False
            local_weight_binding["matches_remote"] = False
            error_type = "LocalWeightChangedError"
            exit_code = 1

    return base_report()


def _help_text() -> str:
    """返回不含资产 URL 或签名信息的固定帮助文本。"""

    return (
        "用法: py -3 s1_t02_d4_w5_stream_hash.py [--help | "
        "--execute-network-request]\n"
        "默认只显示帮助，不执行 socket/HTTP 操作。\n"
        "--execute-network-request 显式启动一次受限的完整对象 SHA-256 核验。\n"
        "许可状态保持 UNRESOLVED；本工具不下载或保存响应正文。\n"
    )


def _write_progress_jsonl(record: dict[str, object]) -> None:
    """逐行写出进度并立即 flush，便于后台日志持续落盘。"""

    sys.stdout.write(
        json.dumps(record, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    )
    sys.stdout.flush()


def _emergency_failure_report(error_type: str) -> dict[str, object]:
    """为主流程意外异常构造不含异常文本的最终失败 JSON。"""

    now = _timestamp_utc8()
    return {
        "task_id": TASK_ID,
        "started_at_utc8": now,
        "completed_at_utc8": now,
        "endpoints": [],
        "http_statuses": [],
        "request_attempt_count": 0,
        "http_response_count": 0,
        "confirmed_get_count": 0,
        "actual_get_count": 0,
        "redirect_count": 0,
        "final_status": None,
        "content_length": None,
        "content_encoding": "unknown",
        "bytes_read": 0,
        "sha256": None,
        "expected_local_sha256": EXPECTED_SHA256,
        "hash_matches": None,
        "elapsed_seconds": 0.0,
        "error_type": error_type,
        "exit_code": 1,
        "dependency_bindings": [],
        "local_weight_binding": {
            "path": str(LOCAL_WEIGHT_PATH),
            "expected_bytes": EXPECTED_BYTES,
            "expected_sha256": EXPECTED_SHA256,
            "before": None,
            "after": None,
            "matches_expected": False,
            "stable": None,
            "matches_remote": False,
        },
        "license": "UNRESOLVED",
    }


def main(argv: Sequence[str] | None = None) -> int:
    """默认只显示帮助；仅唯一显式开关允许网络执行。"""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments == ["--help"] or arguments == ["-h"]:
        sys.stdout.write(_help_text())
        return 0
    if arguments != ["--execute-network-request"]:
        sys.stderr.write("参数不受支持；未执行网络请求。请使用 --help。\n")
        return 2
    try:
        report = verify_remote_asset(
            connection_factory=_make_https_connection,
            progress_callback=_write_progress_jsonl,
        )
    except KeyboardInterrupt:
        report = _emergency_failure_report("InterruptedError")
    except Exception:
        report = _emergency_failure_report("InternalError")
    try:
        final_line = json.dumps(
            report,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    except Exception:
        report = _emergency_failure_report("ReportSerializationError")
        final_line = json.dumps(
            report,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    try:
        sys.stdout.write(final_line + "\n")
        sys.stdout.flush()
    except Exception:
        return 1
    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
