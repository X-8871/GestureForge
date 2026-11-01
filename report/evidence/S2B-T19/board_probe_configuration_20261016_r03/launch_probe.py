"""用已有专属Job监督器执行已授权缓存探针并保存真实退出结果。"""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "verification"))
from s2b_process_supervisor import supervise_process


def main():
    """只启动一次探针，不创建或关闭外部硬件服务。"""
    config = HERE / "input_config.json"
    cli = Path(r"D:\Xilinx\2026.1\Vitis\bin\vitis.bat")
    entry = ROOT / "vitis/run_s2b_visibility_probe.py"
    work = ROOT / "tmp/2B/S2B-T19/cache_probe_supervisor_20261016_r04"
    if not config.is_file() or not cli.is_file() or not entry.is_file() or work.exists():
        raise RuntimeError("输入缺失或执行目录已存在，拒绝覆盖")
    work.mkdir()
    env = dict(os.environ)
    env["S2B_VISIBILITY_PROBE_CONFIG"] = str(config)
    env["PYTHONUTF8"] = "1"
    command = [str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"),
               "/d", "/c", str(HERE / "probe.cmd")]
    record = {"command": command, "cwd": str(work),
              "config_sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
              "scope": "visibility0_cache_probe_only"}
    with (HERE / "probe_r04.stdout.log").open("xb") as output:
        record["job"] = supervise_process(
            name="s2b_current_visibility0_cache_probe_r03", command=command,
            cwd=str(work), environment=env, output_stream=output,
            timeout_seconds=600, start_floor_bytes=int(4.5 * 1024**3),
            stop_floor_bytes=2 * 1024**3)
    with (HERE / "probe_r04_job_result.json").open("x", encoding="utf-8") as output:
        json.dump(record, output, ensure_ascii=False, indent=2)
    print(json.dumps(record["job"], ensure_ascii=False))
    return 0 if record["job"].get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
