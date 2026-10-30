"""在已批准窗口内持有唯一hw_server Job，标准输入stop仅结束本轮进程树。"""

import argparse
import json
import socket
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import job_launcher


class OwnedJob(job_launcher.Native):
    """只记录本轮Assign的Job句柄，不按名称或猜测PID结束进程。"""

    def __init__(self):
        super().__init__()
        self.ready = threading.Event()
        self.job = None

    def assign(self, job, process):
        super().assign(job, process)
        self.job = job
        self.ready.set()


def main():
    """仅显式execute-board可开窗；九分钟硬上限独立于主机调用方。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-board", action="store_true", required=True)
    parser.add_argument("--port", type=int, choices=(3121, 3122), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    now = datetime.now(timezone(timedelta(hours=8)))
    if now.date().isoformat() != "2026-10-31" or not (80 <= now.hour * 60 + now.minute < 100):
        parser.error("仅允许2026-10-31 01:20至01:40之间开始，占板最多九分钟")
    lease_end = now.replace(hour=1, minute=45, second=0, microsecond=0)
    budget = min(520, int((lease_end - now).total_seconds()) - 10)
    if budget <= 0:
        parser.error("租期剩余时间不足以安全收窗")
    root = Path(__file__).resolve().parents[2]
    parent = args.out.parent.resolve(strict=True)
    if not parent.is_relative_to(root) or args.out.exists():
        parser.error("输出必须在本次获准w6范围内且不存在")
    for port in (3121, 3122):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                parser.error(f"端口{port}已有监听，不启动、不干扰原会话")
    batch = Path(r"D:\Xilinx\2026.1\Vivado\bin\hw_server.bat").resolve(strict=True)
    cmd = Path(r"C:\Windows\System32\cmd.exe").resolve(strict=True)
    payload = f'""{batch}" -p tcp::{args.port}"'
    line = subprocess.list2cmdline([str(cmd), "/d", "/q", "/v:off", "/s", "/c"]) + " " + payload
    args.out.mkdir()
    api = OwnedJob()
    result = {}

    def worker():
        """超时或父进程退出都会结束本次Job，绝不触碰别的会话。"""
        try:
            result.update(job_launcher.run_job(str(cmd), line, args.out,
                          job_launcher.offline_environment(args.out), args.out / "job", budget, api=api))
        except Exception as exc:
            result.update(status="SERVER_JOB_ERROR", exception=repr(exc), cleanup_confirmed=False)

    thread = threading.Thread(target=worker, daemon=False)
    thread.start()
    input_ready = threading.Event()
    input_value = {}

    def read_stop():
        """输入等待不得阻止主线程处理Job超时或提前退出。"""
        input_value["line"] = sys.stdin.readline().strip()
        input_ready.set()

    normal_stop = False
    try:
        if not api.ready.wait(10):
            raise RuntimeError("hw_server Job未完成Assign")
        for _ in range(50):
            with socket.socket() as probe:
                if probe.connect_ex(("127.0.0.1", args.port)) == 0:
                    print(json.dumps({"status": "OWNED_SERVER_LISTENING", "port": args.port,
                                      "started_utc8": now.isoformat(), "budget_seconds": budget}), flush=True)
                    break
            if not thread.is_alive():
                raise RuntimeError("hw_server启动后提前退出")
            threading.Event().wait(0.1)
        else:
            raise RuntimeError("hw_server未按时监听")
        threading.Thread(target=read_stop, daemon=True).start()
        while not input_ready.wait(0.1) and thread.is_alive():
            pass
        normal_stop = input_ready.is_set() and input_value.get("line") == "stop" and thread.is_alive()
        if not normal_stop:
            result["stop_reason"] = "标准输入关闭或非stop，按失败收窗"
    finally:
        if thread.is_alive() and api.job:
            try:
                api.terminate_job(api.job)
            except OSError as exc:
                result["stop_error"] = repr(exc)
        thread.join(6)
        result["thread_joined"] = not thread.is_alive()
        result["normal_stop_requested"] = normal_stop
        result["finished_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
        passed = normal_stop and result.get("cleanup_confirmed") and not thread.is_alive() and not result.get("timed_out")
        result["close_status"] = "CLOSED_BY_REQUEST" if passed else ("HARD_TIMEOUT" if result.get("timed_out") else "FAILED_CLOSE")
        (args.out / "server_close.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": result["close_status"], "cleanup_confirmed": result.get("cleanup_confirmed"),
                          "thread_joined": not thread.is_alive()}), flush=True)
    return 0 if passed else (124 if result.get("timed_out") else 2)


if __name__ == "__main__":
    raise SystemExit(main())
