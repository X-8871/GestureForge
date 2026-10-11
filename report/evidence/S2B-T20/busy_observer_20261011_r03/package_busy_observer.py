"""打包独占T20离线证据，保留失败原件并记录原生检查退出码。"""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[3]
PARENT = ROOT / "report/evidence/S2B-T20"
BASELINE = "6d3fd8567b579a51d4042667d47af7d94f2f5a97"
NAMES = ("s2b_csr_busy_observer.py", "test_s2b_csr_busy_observer.py")
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def save(path, value):
    """内部清单构建阶段仅更新本包自有元数据，原实验文件绝不覆盖。"""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError("源快照重建补丁定位不唯一")
    return source.replace(old, new)


r01 = PARENT / "busy_observer_20261011_r01"
r02 = PARENT / "busy_observer_20261011_r02"
r03 = PARENT / "busy_observer_20261011_r03"
for run in (r01, r02, r03):
    if not run.is_dir() or not (run / "unittest.log").is_file() or (run / "delivery_manifest.json").exists():
        raise RuntimeError("运行目录缺失、日志缺失或已冻结，禁止覆盖RunId")

# 首轮没有当场复制源码；按唯一的已应用编辑反向还原，明确记录重建来源，不冒充当场采集。
source = (r02 / "source_snapshot" / NAMES[0]).read_text(encoding="utf-8")
source = replace_once(source, '        csr.require(not c.failed and not self.wire.failed, "失败会话禁止继续观测或提交命令")\n', "")
source = replace_once(source, '''            self.wire.rx_file.flush()
            with transport.exact_path(self.wire.rx_file.name).open("rb") as stream:
                stream.seek(start)
                actual = stream.read(self.wire.rx_file.tell() - start)
            csr.require(actual == raw, "同RUN receipt与实际UART磁盘字节不同")
''', "")
source = replace_once(source, '''                try:
                    self.controller.fail_stop()
                except BaseException as cleanup_error:
                    self.controller.record.setdefault("cleanup_errors", []).append(repr(cleanup_error))
''', '''                self.controller.fail_stop()
''')
test = (r02 / "source_snapshot" / NAMES[1]).read_text(encoding="utf-8")
test = replace_once(test, 'self.raw.extend(reply(request, self.session.memory[j.CSR_BASE + 0x050], self.heads, self.boxes))',
                    'self.raw.extend(reply(request, 0, self.heads, self.boxes))')
test = replace_once(test, '''                    epoch = self.session.memory[j.CSR_BASE + 0x050] + 1
                    self.raw.extend(reply(request, epoch, self.heads, self.boxes))
                    self.session.memory[j.CSR_BASE + 0x050] = epoch
                    self.session.memory[j.CSR_BASE + 0x05C] = epoch
''', '''                    self.raw.extend(reply(request, 1, self.heads, self.boxes))
                    self.session.memory[j.CSR_BASE + 0x050] = 1
                    self.session.memory[j.CSR_BASE + 0x05C] = 1
''')
test = replace_once(test, 'transport.make_request(1, 3, 0, b"W" * 5903100)', 'transport.make_request(1, 3, b"W" * 5903100)')
begin = test.index('            archived = target / "fixture_originals"; archived.mkdir()\n')
end = test.index('        self.temp.cleanup()\n', begin)
test = test[:begin] + test[end:]
(r01 / "source_snapshot").mkdir()
for name, raw in zip(NAMES, (source, test)):
    ast.parse(raw)
    (r01 / "source_snapshot" / name).write_text(raw, encoding="utf-8", newline="\n")
save(r01 / "execution.json", {"hardware_execution": "NOT_RUN", "source_commit": BASELINE,
    "source_commit_scope": "任务初始只读git核对的开发基线；首轮执行时HEAD未另行采集，不能宣称为当时HEAD。",
    "command": ["python", "-B", "-m", "unittest", "verification.test_s2b_csr_busy_observer", "-v"],
    "exit_code": 1, "test_count": 32, "errors": 2, "unittest_elapsed_seconds": 12.828,
    "peak_rss_bytes": None, "source_snapshot_provenance": "由r02快照及本会话精确编辑反向重建，未冒充执行前采集。",
    "source_sha256": {"verification/" + name: digest(r01 / "source_snapshot" / name) for name in NAMES},
    "failure_reason": "后续LOAD夹具响应错误地使用epoch0；未消费LOAD反例漏传frame参数。",
    "raw_log_encoding": "原生Windows默认输出原字节保留，不改写为伪UTF-8原件。"})

(r03 / "source_snapshot").mkdir()
for name in NAMES:
    shutil.copyfile(ROOT / "verification" / name, r03 / "source_snapshot" / name)
shutil.copyfile(Path(__file__), r03 / "package_busy_observer.py")
shutil.copyfile(Path(__file__).with_name("busy_observer_offline_runner.py"), r03 / "busy_observer_offline_runner.py")
final = json.loads((r03 / "execution.json").read_text(encoding="utf-8"))
for relative, sha in final["source_sha256"].items():
    if digest(ROOT / relative) != sha:
        raise RuntimeError("测试后相关源码发生变化：" + relative)
for name in NAMES:
    ast.parse((ROOT / "verification" / name).read_text(encoding="utf-8"))
save(r03 / "api_usage.json", {"scope": "尚待独立G2；实板BOARD NOT_RUN",
    "entry": "s2b_csr_busy_observer.execute_busy_start(controller, wire, config_binding, new_run_dir, preparation=preparation_binding, observation_seconds=5.0, poll_seconds=0.01)",
    "caller": "实际持有已审核会话的总控；不打开SDK/串口，不创建回调，不隐式下载或冷复位。",
    "preconditions": ["controller和wire必须分别是实际JtagController/JtagWireSession精确类型。",
        "T20既有UART scene schema：完整真实IDLE快照、wire同epoch、CPU0 Running/CPU1 Stopped。",
        "config.source_commit为调用时HEAD；现有T18 visibility1/同ELF/BSP/最终PL审查和文件绑定门禁全部通过。",
        "preparation_binding为完整109准备JSON的path/sha256；逐项实际validate_plan成功。",
        "实际原UART/TX磁盘、事件及receipt历史最终LOAD和sample000 frame0 RUN成功；不能由布尔或字典替代。"],
    "request": "沿用seed实际core/drain非零32bit期限、冻结sample000输入、640×480、repeat1、seq+1/frame1/epoch+1。",
    "busy_observation": "STATUS→HI/LO/HI→frame/error→完整CSR→STATUS；允许ARMING→RUN及AXI_PROGRESS/AXI_PENDING逐次变化。0x06C/70/74为首故障字段，保持0。",
    "rejection": "真实CPU0 stop及PC留证；前后包围仍忙、严格身份/配置/首错不变量、LAST_REJECT 0→1、原生已审精确SLVERR同时成立。",
    "completion": "只resume本次自有CPU0；消费同一RUN实际receipt，匹配CRC/seq/frame/epoch/reject1并完整保存UART、两个头和全部框；T18独立checker全量通过。",
    "failure": "UNKNOWN/OKAY/DECERR、身份变化、错误黄金均失败锁存与fail_stop；终态/过快为NOT_EXECUTED_IN_BUSY。失败后不resume/清锁/操作CPU1。",
    "limitations": ["不证明读间不可观察账本或状态瞬态，不关闭ILA缺口。", "mock PASS及清单CHECKS_OK均不等于板上G3/G4/G5。"]})

interfaces = []
for name, version, relative in (("PS/PL物理候选", "s2b-physical-candidate/0.1.1", "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"),
                                ("UART候选", "s2bu-candidate/1.1", "docs/obsidian-project/02-方案设计/s2b_board_transport.md")):
    interfaces.append({"name": name, "version": version, "frozen": False, "path": relative, "sha256": digest(ROOT / relative)})


def check_entry(name, code, command, reason):
    return {"name": name, "status": "PASS" if code == 0 else "FAIL", "command": command, "exit_code": code, "reason": reason}


for run in (r01, r02, r03):
    record = json.loads((run / "execution.json").read_text(encoding="utf-8"))
    checks = [check_entry("实际离线回归", record["exit_code"], record["command"],
        "原生退出码原样保存；r01为夹具错误，r02为65项通过，r03为35新增+33既有共68项通过。"),
        {"name": "独立G2审查", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "Developer停止写入后由总控派独立Reviewer。"},
        {"name": "实板busy拒绝及同RUN黄金", "status": "NOT_RUN", "command": None, "exit_code": None,
         "reason": "BOARD NOT_RUN；仅内存原生夹具，没有SDK/串口/实物操作权限。"}]
    source_files = [{"path": str((run / "source_snapshot" / name).relative_to(ROOT).as_posix()),
                     "sha256": digest(run / "source_snapshot" / name), "role": "source"} for name in NAMES]
    if run == r03:
        source_files += [{"path": relative, "sha256": sha, "role": "source"} for relative, sha in record["source_sha256"].items()]
    input_file = "src/s2b_control_csr.sv"
    source_files.append({"path": input_file, "sha256": digest(ROOT / input_file), "role": "input"})
    manifest_path = run / "delivery_manifest.json"

    def manifest():
        paths = sorted(path for path in run.rglob("*") if path.is_file() and path.name not in ("delivery_manifest.json", "inventory.json"))
        save(run / "inventory.json", {"hardware_execution": "NOT_RUN", "source_baseline": BASELINE,
            "files": [{"path": str(path.relative_to(ROOT).as_posix()), "bytes": path.stat().st_size,
                       "sha256": digest(path)} for path in paths],
            "limitations": ["inventory不包含自身及最终delivery_manifest，避免循环摘要。", "原路径位于隔离tmp的代表夹具在fixture_originals/index.json逐字映射，没有改写原实验结果。"]})
        paths.append(run / "inventory.json")
        files = {item["path"]: item for item in source_files}
        for path in paths:
            relative = str(path.relative_to(ROOT).as_posix())
            files.setdefault(relative, {"path": relative, "sha256": digest(path),
                "role": "log" if path.suffix == ".log" else "result"})
        save(manifest_path, {"schema_version": 1, "stage": "2B", "task_id": "S2B-T20", "run_id": run.name,
            "source_commit": record["source_commit"], "evidence_dir": str(run.relative_to(ROOT).as_posix()),
            "interfaces": interfaces, "files": list(files.values()), "checks": checks,
            "tool_versions": {"python": sys.version, "memory_monitor": "psutil 7.2.2；50ms RSS轮询，r01未测"},
            "limitations": ["仅离线G1开发证据；独立G2及实际BOARD NOT_RUN。", "物理/UART接口仍为候选；inputs检查须拒绝冻结准入。",
                "PASS_BUSY_START_REJECTION_AND_GOLD仅在MOCK_ONLY代表夹具发生，不能声称真实硬件通过。",
                "离散DAP不能排除不可观察账本瞬态，不关闭ILA缺口。", "r01源码为精确编辑反向重建且运行HEAD未单独采集，详见execution.json。"]})

    manifest()
    for mode in ("inputs", "evidence"):
        command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
                   "--manifest", str(manifest_path.relative_to(ROOT))]
        result = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True)
        save(run / (mode + "_check.json"), {"command": command, "native_exit_code": result.returncode,
            "stdout": result.stdout.decode("utf-8"), "stderr": result.stderr.decode("utf-8"), "hardware_execution": "NOT_RUN"})
        checks.append(check_entry(mode + "机器包装检查", result.returncode, command,
            "已执行native2必须记FAIL；候选接口未冻结使inputs拒绝属预期。" if mode == "inputs" else "只证明清单包装，不代表测试或板上通过。"))
        manifest()
        if result.returncode != (2 if mode == "inputs" else 0):
            raise RuntimeError(mode + "退出码偏离预期：" + str(result.returncode))
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", str(manifest_path)]
    result = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout.decode("utf-8") + result.stderr.decode("utf-8"))
    print(json.dumps({"run": run.name, "evidence_native_exit": result.returncode,
                      "manifest_sha256": digest(manifest_path)}, ensure_ascii=False))
