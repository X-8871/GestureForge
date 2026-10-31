"""在租约执行门禁内持有本轮命名Windows Job及其hw_server监听器。"""

import argparse
import ctypes
import json
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1] / "r03"))
import job_launcher
import owner_guard


class NamedKernel:
    """为既有启动器注入本轮唯一Job名称并拒绝打开既有Job。"""

    def __init__(self, kernel, job_name):
        self._kernel = kernel
        self._job_name = job_name

    def __getattr__(self, name):
        return getattr(self._kernel, name)

    def CreateJobObjectW(self, security_attributes, name):
        if name is not None:
            raise owner_guard.GuardError("启动器尝试使用未批准的Job名称")
        ctypes.set_last_error(0)
        handle = self._kernel.CreateJobObjectW(security_attributes, self._job_name)
        error = ctypes.get_last_error()
        if not handle:
            raise OSError(error, "CreateJobObjectW")
        if error == 183:
            if not self._kernel.CloseHandle(handle):
                raise OSError(ctypes.get_last_error(), "CloseHandle(existing named Job)")
            raise FileExistsError(error, "命名Job已经存在，拒绝附着既有Job", self._job_name)
        return handle


class OwnedJob(job_launcher.Native):
    """保存本轮Job句柄；holder内直接用Native.pids核监听归属。"""

    def __init__(self, job_name):
        super().__init__()
        self.job_name = job_name
        self.k = NamedKernel(self.k, job_name)
        self.ready = threading.Event()
        self.job = None

    def assign(self, job, process):
        super().assign(job, process)
        self.job = job
        self.ready.set()


def _write_json_new(path, value):
    """以UTF-8和独占创建方式写入新记录。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def _utc8_now():
    return datetime.now(owner_guard.UTC8)


def _finish_close(server_dir, result, normal_stop, thread_joined, *, writer=None):
    """分别报告Job清理与收窗证据写入，并以证据写入结果决定退出码。"""
    cleanup_confirmed = bool(
        result.get("cleanup_confirmed") is True
        and result.get("job_handle_closed") is True
        and result.get("root_wait_after_job_close") == 0
        and thread_joined
    )
    result["cleanup_status"] = (
        "CLEANUP_CONFIRMED" if cleanup_confirmed else "CLEANUP_UNCONFIRMED"
    )
    close_status = (
        "CLOSED_BY_REQUEST"
        if owner_guard.close_succeeded(normal_stop, result, thread_joined)
        else ("HARD_TIMEOUT" if result.get("timed_out") else "FAILED_CLOSE")
    )
    result["close_status"] = close_status
    record_status = "NOT_ATTEMPTED"
    record_error = None
    if server_dir is None:
        close_status = "FAILED_CLOSE"
        record_error = "server目录未创建，无法保存收窗记录"
    else:
        try:
            (writer or _write_json_new)(server_dir / "server_close.json", result)
            record_status = "WRITTEN"
        except OSError as exc:
            close_status = "FAILED_CLOSE"
            record_status = "FAILED"
            record_error = f"{type(exc).__name__}: {exc}"
    result["close_status"] = close_status
    result["close_record_write_status"] = record_status
    if record_error is not None:
        result["close_record_write_error"] = record_error
    print(
        json.dumps(
            {
                "status": close_status,
                "cleanup_status": result["cleanup_status"],
                "cleanup_confirmed": result.get("cleanup_confirmed"),
                "thread_joined": thread_joined,
                "close_record_write_status": record_status,
                "close_record_write_error": record_error,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    exit_code = 0 if close_status == "CLOSED_BY_REQUEST" else (
        124 if result.get("timed_out") else 2
    )
    return exit_code, close_status


def _owner_proof(lease_file, root, api, thread):
    """重读租约与配置后验证本轮Job仍持有监听端口。"""
    execution = owner_guard.load_execution(lease_file, root)
    proof = owner_guard.verify_owner(
        execution,
        thread_alive=thread.is_alive,
        job_pids=lambda name: api.pids(api.job) if name == api.job_name and api.job else [],
        listener_pids=owner_guard.query_listener_pids,
        loopback_connected=owner_guard.loopback_connected,
    )
    return execution, proof


def main(argv=None):
    """仅按显式租约启动；租约文件不替代外部板窗授权或就绪核验。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-board", action="store_true", required=True)
    parser.add_argument("--lease-file", type=Path, required=True)
    parser.add_argument("--port", type=int, choices=(3121, 3122), required=True)
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[2]
    server_dir = None
    api = None
    thread = None
    result = {}
    normal_stop = False
    exit_code = 2
    try:
        lease = owner_guard.load_lease(args.lease_file, root)
        configured_port, port_digest = owner_guard.assert_requested_port(
            lease.run_dir, args.port
        )
        owner_guard.assert_port_free(configured_port)
        candidate_server_dir = lease.run_dir / "server"
        if candidate_server_dir.exists() or candidate_server_dir.is_symlink():
            raise owner_guard.GuardError("server目录已存在，本RunId不可重用")
        candidate_server_dir.mkdir()
        server_dir = candidate_server_dir

        now = _utc8_now()
        budget = min(
            520,
            lease.max_seconds,
            int((lease.ends_at - now).total_seconds()) - 10,
        )
        if budget <= 0:
            raise owner_guard.GuardError("租期剩余时间不足以安全收窗")
        job_name = "Local\\M3_OWNER_" + uuid.uuid4().hex
        start_record = {
            "schema": owner_guard.START_SCHEMA,
            "lease_id": lease.lease_id,
            "run_dir": str(lease.run_dir),
            "lease_file_path": str(lease.path),
            "lease_file_sha256": lease.digest,
            "authorization_file_path": str(lease.authorization_file),
            "authorization_file_sha256": lease.authorization_digest,
            "context_file_path": str(lease.context_file),
            "context_file_sha256": lease.context_digest,
            "port": configured_port,
            "port_file_sha256": port_digest,
            "job_name": job_name,
            "started_utc8": now.isoformat(timespec="seconds"),
            "budget_seconds": budget,
            "lease_end_utc8": lease.ends_at.isoformat(timespec="seconds"),
            "execution_gate": owner_guard.LOCAL_GATE_MEANING,
            "initial_readiness": "由总控外部核对；本工具未作声明",
        }
        _write_json_new(server_dir / "server_start.json", start_record)
        api = OwnedJob(job_name)
        cmd = Path(r"C:\Windows\System32\cmd.exe").resolve(strict=True)
        batch = Path(r"D:\Xilinx\2026.1\Vivado\bin\hw_server.bat").resolve(strict=True)
        payload = f'""{batch}" -p tcp::{configured_port}"'
        command_line = subprocess.list2cmdline(
            [str(cmd), "/d", "/q", "/v:off", "/s", "/c"]
        ) + " " + payload

        def worker():
            """超时、异常或停止请求都只清理本轮Job。"""
            try:
                result.update(
                    job_launcher.run_job(
                        str(cmd),
                        command_line,
                        server_dir,
                        job_launcher.offline_environment(server_dir),
                        server_dir / "job",
                        budget,
                        api=api,
                    )
                )
            except Exception as exc:
                result.update(
                    status="SERVER_JOB_ERROR",
                    exception=repr(exc),
                    cleanup_confirmed=False,
                )

        thread = threading.Thread(target=worker, daemon=False)
        thread.start()
        if not api.ready.wait(10):
            raise owner_guard.GuardError("本轮Job未完成Assign")

        initial_proof = None
        for _ in range(50):
            if not thread.is_alive():
                raise owner_guard.GuardError("hw_server启动后Job线程提前退出")
            try:
                _, initial_proof = _owner_proof(args.lease_file, root, api, thread)
                break
            except owner_guard.GuardError:
                threading.Event().wait(0.1)
        if initial_proof is None:
            raise owner_guard.GuardError("未能验证本轮Job拥有目标端口监听")

        print(
            json.dumps(
                {
                    "status": "OWNED_SERVER_LISTENING",
                    "port": configured_port,
                    "job_name": job_name,
                    "owner_proof": initial_proof,
                    "lease_gate": owner_guard.LOCAL_GATE_MEANING,
                    "initial_readiness": "由总控外部核对；本工具未作声明",
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        input_ready = threading.Event()
        input_value = {}

        def read_stop():
            """读取一次stop命令，不阻塞主线程监视Job。"""
            input_value["line"] = sys.stdin.readline().strip()
            input_ready.set()

        threading.Thread(target=read_stop, daemon=True).start()
        while not input_ready.wait(0.1) and thread.is_alive():
            pass
        normal_stop = (
            input_ready.is_set()
            and input_value.get("line") == "stop"
            and thread.is_alive()
        )
        if normal_stop:
            _owner_proof(args.lease_file, root, api, thread)
        else:
            result["stop_reason"] = "标准输入关闭、非stop或本轮Job已退出"
    except Exception as exc:
        normal_stop = False
        result["holder_error"] = f"{type(exc).__name__}: {exc}"
        print(result["holder_error"], file=sys.stderr, flush=True)
    finally:
        if thread is not None and thread.is_alive() and api is not None and api.job:
            try:
                api.terminate_job(api.job)
            except OSError as exc:
                result["stop_error"] = repr(exc)
        if thread is not None:
            thread.join(6)
            thread_joined = not thread.is_alive()
        else:
            thread_joined = True
        result["thread_joined"] = thread_joined
        result["normal_stop_requested"] = normal_stop
        result["finished_utc8"] = _utc8_now().isoformat(timespec="seconds")
        result["cleanup_scope"] = "仅本轮命名Job句柄；未按PID结束任何其他进程"
        exit_code, _ = _finish_close(
            server_dir,
            result,
            normal_stop,
            thread_joined,
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
