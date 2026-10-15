"""用独立Job保护当前候选XSA的离线Vitis构建，不访问板卡。"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
WORK = ROOT / "tmp/2B/S2B-T15/c16r1"
ARTIFACT = RUN / "artifacts"
sys.path.insert(0, str(ROOT))
from verification.s2b_process_supervisor import supervise_process, GIB

checkpoint_stream = None


def sha(path):
    """绑定实际文件字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save():
    """保留启动和终态，包括失败。"""
    (RUN / "launcher_record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def checkpoint(payload):
    """每15秒保留自有Job进度。"""
    checkpoint_stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
    checkpoint_stream.flush()
    print(json.dumps(payload, ensure_ascii=False), flush=True)


if any(path.exists() for path in (WORK, ARTIFACT, RUN / "config.json", RUN / "launcher_record.json",
                                  RUN / "checkpoints.jsonl", RUN / "vitis.stdout.log")):
    raise RuntimeError("运行目标已存在，禁止覆盖重跑")
record = {"status": "NOT_RUN", "hardware_execution": "NOT_RUN", "g0_effect": "NONE",
          "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
          "sources": [], "attempts": 1, "peak_memory": "未测"}
try:
    xsa = ROOT / "report/evidence/S2B-T13/platform_current_20261016_r02/s2b_inference_no_bit.xsa"
    platform = xsa.parent / "delivery_manifest.json"
    expected_xsa = "481e1a73b5ce731743c61491bb98ab3d640903417c4457ac96a1270f9a1ca783"
    expected_platform = "edefe48721147d6a65fb68414f4122515fc6bbb1d7ee008db07e040e83ce2a31"
    if sha(xsa) != expected_xsa or sha(platform) != expected_platform:
        raise RuntimeError("平台/XSA原字节绑定不符")
    frozen = {"vitis/build_s2b_inference.py": "c60bbb2d7228c35bbb25393b1864e531a939278a6ab7ebff04debb564ee07f94",
              "verification/check_s2b_inference_mmu.py": "d8da6610daa5a321129650cfec072c1549b0328dd382e9f1166481ca8d954178"}
    for name, expected in frozen.items():
        if sha(ROOT / name) != expected:
            raise RuntimeError(f"已审构建输入漂移：{name}")
    snapshots = RUN / "launcher_sources"
    snapshots.mkdir()
    for name in ("verification/s15_job_guard.py", "verification/s2b_process_supervisor.py", *frozen):
        source = ROOT / name
        shutil.copy2(source, snapshots / source.name)
        record["sources"].append({"path": name, "sha256": sha(source)})
    config = {"schema_version": 1, "source_commit": record["source_commit"],
              "xsa": str(xsa), "xsa_sha256": expected_xsa,
              "xsa_source_commit": "c9ce89d08578b690c85966136f7674a79893b59c",
              "hardware_mode": "FULL_PLATFORM_BOUND", "platform_manifest": str(platform),
              "platform_manifest_sha256": expected_platform,
              "workspace": str(WORK), "artifact_dir": str(ARTIFACT)}
    with (RUN / "config.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    executable = Path("D:/Xilinx/2026.1/Vitis/bin/vitis.bat")
    if not executable.is_file():
        raise RuntimeError("精确Vitis路径不存在")
    record["vitis_launcher"] = {"path": str(executable), "sha256": sha(executable)}
    wrapper = RUN / "build.cmd"
    native_exit = RUN / "native_exit_vitis.txt"
    if wrapper.exists() or native_exit.exists():
        raise RuntimeError("阶段包装器或原生退出码文件已存在")
    wrapper.write_text('@echo off\n'
                       + f'call "{executable}" -s "{ROOT / "vitis/build_s2b_inference.py"}"\n'
                       + 'set "VITIS_RC=%errorlevel%"\n'
                       + f'> "{native_exit}" echo %VITIS_RC%\n'
                       + 'exit /b %VITIS_RC%\n', encoding="utf-8", newline="\r\n")
    environment = dict(os.environ)
    environment["S2B_INFERENCE_CONFIG"] = str(RUN / "config.json")
    checkpoint_stream = (RUN / "checkpoints.jsonl").open("x", encoding="utf-8", newline="\n")
    record["status"] = "RUNNING"
    save()
    with (RUN / "vitis.stdout.log").open("xb") as stream:
        job = supervise_process(name="vitis_candidate_build",
            command=[str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"), "/d", "/c", str(wrapper)],
            cwd=str(ROOT), environment=environment, output_stream=stream,
            timeout_seconds=600, start_floor_bytes=int(4.5 * GIB), stop_floor_bytes=2 * GIB,
            checkpoint_callback=checkpoint)
    record["job"] = job
    record["native_exit_code"] = int(native_exit.read_text(encoding="utf-8").strip()) if native_exit.is_file() else None
    if not (job["status"] == "PASS" and job["exit_code"] == 0 and not job["timed_out"]
            and job["cleanup_confirmed"] and record["native_exit_code"] == 0):
        record["status"] = "BLOCKED" if job["status"].startswith("BLOCKED_") else "FAIL"
        raise RuntimeError(f"Vitis原生退出、监控或Job清理未通过：{job['status']}")
    details = json.loads((ARTIFACT / "build_details.json").read_text(encoding="utf-8"))
    if details["status"] != "PASS_OFFLINE_FULL_XSA_BUILD" or details["hardware_execution"] != "NOT_RUN":
        raise RuntimeError("Vitis内层构建未通过或范围不符")
    for entry in record["sources"]:
        if sha(ROOT / entry["path"]) != entry["sha256"]:
            raise RuntimeError("运行期间源码变化")
    record["status"] = "PASS_OFFLINE_CANDIDATE_BUILD_ONLY"
except Exception as error:
    if record["status"] != "BLOCKED":
        record["status"] = "FAIL"
    record["error"] = f"{type(error).__name__}: {error}"
finally:
    if checkpoint_stream is not None:
        try:
            checkpoint_stream.close()
        except Exception as error:
            record["status"] = "FAIL"
            record["checkpoint_close_error"] = f"{type(error).__name__}: {error}"
    save()
print(record["status"], flush=True)
sys.exit(0 if record["status"] == "PASS_OFFLINE_CANDIDATE_BUILD_ONLY" else 1)
