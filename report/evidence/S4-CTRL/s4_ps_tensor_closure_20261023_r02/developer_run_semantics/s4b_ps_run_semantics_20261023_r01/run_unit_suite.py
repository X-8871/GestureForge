#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""运行并保存S4-B PS旁路解码器单测证据。"""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path


run_dir = Path(__file__).resolve().parent
repo = run_dir.parents[3]
command = [sys.executable, "-B", "-m", "unittest", "-v",
           "verification.test_s4b_ps_tensor"]
result = subprocess.run(
    command, cwd=repo, capture_output=True, text=True,
    encoding="utf-8", errors="replace",
)
(run_dir / "command.txt").write_text(shlex.join(command) + "\n", encoding="utf-8")
(run_dir / "stdout.txt").write_text(result.stdout, encoding="utf-8")
(run_dir / "stderr.txt").write_text(result.stderr, encoding="utf-8")
(run_dir / "exit_code.txt").write_text(f"{result.returncode}\n", encoding="utf-8")
(run_dir / "semantics.md").write_text(
    "# S4-B PS运行结束语义\n\n"
    "依据r12唯一锚点派生源码：`tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r12/"
    "bundle_extract/bundle/workspace/infer/src/s2b_inference_app.c`，SHA-256为"
    " `1be7a551e26f61be1327cdb56672b08d86d17d16433ac405ebd263d5f35bf436`。"
    " `infer_one`仅在`RESPONSE_OK`、UART发送成功且ACK成功时返回成功；其余已记录失败路径"
    "会令`service_request`返回0，主服务循环随即结束。因此status 1要求末次session的每条"
    "记录均为上述成功组合；派生app也不可能在一条失败attempt之后继续写入记录或新session。"
    " `end_run(0)`写status 2并保留已提交记录；未提交attempt可造成无失败记录的partial。\n\n"
    "原始单测命令、退出码和stdout/stderr见同目录文件。\n",
    encoding="utf-8",
)
print(f"run_dir={run_dir}")
print(f"exit_code={result.returncode}")
print(result.stdout, end="")
print(result.stderr, end="", file=sys.stderr)
sys.exit(result.returncode)
