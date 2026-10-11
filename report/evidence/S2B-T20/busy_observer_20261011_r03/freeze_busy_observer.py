"""修正command字段后冻结T20证据；保留第一次包装失败的全部原件。"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[3]
PARENT = ROOT / "report/evidence/S2B-T20"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check(name, code, command, reason):
    return {"name": name, "status": "PASS" if code == 0 else "FAIL", "command": subprocess.list2cmdline(command),
            "exit_code": code, "reason": reason}


r01 = PARENT / "busy_observer_20261011_r01"
for name in ("delivery_manifest.json", "inventory.json"):
    original = r01 / name
    archived = r01 / (original.stem + "_first_attempt.json")
    if not original.is_file() or archived.exists():
        raise RuntimeError("原件缺失或备份已存在")
    shutil.copyfile(original, archived)
save(r01 / "packaging_failure.json", {"native_exit_code": 1,
    "command": "python -B tmp/2B/S2B-T20/package_busy_observer.py",
    "reason": "stage checks.command要求字符串，第一次包装写成argv数组，evidence实际返回2。原manifest及inventory逐字备份，原inputs/evidence结果不改写。",
    "exception": "RuntimeError: evidence退出码偏离预期：2"})
r03 = PARENT / "busy_observer_20261011_r03"
shutil.copyfile(Path(__file__), r03 / "freeze_busy_observer.py")
interfaces = []
for title, version, name in (("PS/PL物理候选", "s2b-physical-candidate/0.1.1", "s2b_physical_interface_candidate.md"),
                              ("UART候选", "s2bu-candidate/1.1", "s2b_board_transport.md")):
    path = ROOT / "docs/obsidian-project/02-方案设计" / name
    interfaces.append({"name": title, "version": version, "frozen": False,
                       "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)})

for number in (1, 2, 3):
    run = PARENT / f"busy_observer_20261011_r0{number}"
    execution = json.loads((run / "execution.json").read_text(encoding="utf-8"))
    checks = [check("实际离线回归", execution["exit_code"], execution["command"],
                    "r01为32项中2个夹具错误；r02为65项通过；r03为35新增+33既有共68项通过。"),
        {"name": "独立G2审查", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "Developer停止写入后由总控派独立Reviewer。"},
        {"name": "实板busy拒绝及同RUN黄金", "status": "NOT_RUN", "command": None, "exit_code": None,
         "reason": "BOARD NOT_RUN；只使用内存设备，没有创建SDK或串口会话。"}]
    if number == 1:
        for mode in ("inputs", "evidence"):
            prior = json.loads((run / (mode + "_check.json")).read_text(encoding="utf-8"))
            checks.append(check("首版包装" + mode, prior["native_exit_code"], prior["command"],
                                "原生检查失败：checks.command为数组，schema要求字符串；保留原错误，不改称BLOCKED。"))
    external = [{"path": "src/s2b_control_csr.sv", "sha256": digest(ROOT / "src/s2b_control_csr.sv"), "role": "input"}]
    if number == 3:
        for relative, expected in execution["source_sha256"].items():
            if digest(ROOT / relative) != expected:
                raise RuntimeError("测试后源码变化：" + relative)
            external.append({"path": relative, "sha256": expected, "role": "source"})
    manifest_path = run / "delivery_manifest.json"

    def manifest():
        paths = sorted(path for path in run.rglob("*") if path.is_file() and
                       path.name not in ("delivery_manifest.json", "inventory.json"))
        save(run / "inventory.json", {"hardware_execution": "NOT_RUN",
            "development_baseline": "6d3fd8567b579a51d4042667d47af7d94f2f5a97",
            "files": [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                       "sha256": digest(path)} for path in paths],
            "limitations": ["不包含自身及delivery_manifest，避免循环摘要。",
                "代表夹具临时路径已按fixture_originals/index.json映射为逐字保留原件；原报告不重写。"]})
        paths.append(run / "inventory.json")
        files = external + [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
            "role": "source" if path.parent.name == "source_snapshot" else "log" if path.suffix == ".log" else "result"} for path in paths]
        save(manifest_path, {"schema_version": 1, "stage": "2B", "task_id": "S2B-T20", "run_id": run.name,
            "source_commit": execution["source_commit"], "evidence_dir": run.relative_to(ROOT).as_posix(),
            "interfaces": interfaces, "files": files, "checks": checks,
            "tool_versions": {"python": sys.version, "memory_monitor": "psutil 7.2.2，50ms RSS轮询；r01未测"},
            "limitations": ["G1离线开发证据；独立G2待执行，BOARD NOT_RUN。", "候选接口未冻结，inputs拒绝是实际FAIL/2，包装通过不代表G0。",
                "PASS_BUSY_START_REJECTION_AND_GOLD只发生于MOCK_ONLY夹具，不代表实板通过。",
                "离散DAP不能排除不可观察账本瞬态，不关闭ILA缺口。",
                "r01源码由精确编辑反向重建，执行HEAD未单独采集，清单source_commit是初始开发基线；详见execution.json。"]})

    manifest()
    for mode in ("inputs", "evidence"):
        command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
                   "--manifest", str(manifest_path.relative_to(ROOT))]
        result = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True)
        output = run / (mode + "_check_final.json")
        if output.exists():
            raise RuntimeError("不覆盖检查原件")
        save(output, {"command": command, "native_exit_code": result.returncode,
                      "stdout": result.stdout.decode("utf-8"), "stderr": result.stderr.decode("utf-8")})
        checks.append(check("最终" + mode + "检查", result.returncode, command,
                            "候选物理/UART接口未冻结，实际inputs返回2。" if mode == "inputs" else "仅证明文件与包装，不代表测试或板上通过。"))
        manifest()
        if result.returncode != (2 if mode == "inputs" else 0):
            raise RuntimeError(result.stdout.decode("utf-8") + result.stderr.decode("utf-8"))
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", str(manifest_path)]
    final = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True)
    if final.returncode:
        raise RuntimeError(final.stdout.decode("utf-8") + final.stderr.decode("utf-8"))
    print(json.dumps({"run": run.name, "evidence_native_exit": final.returncode,
                      "manifest_sha256": digest(manifest_path)}, ensure_ascii=False))
