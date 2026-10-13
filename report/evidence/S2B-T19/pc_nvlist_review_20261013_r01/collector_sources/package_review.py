"""归档独立审查当前脚本和原件，包装检查日志放在隔离临时目录。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
HERE = Path(__file__).absolute().parent
OUT = ROOT / "report/evidence/S2B-T19/pc_nvlist_review_20261013_r01"
CHECK = HERE / "package_check_r01"
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
read = lambda path: json.loads(Path(path).read_text(encoding="utf-8"))
assert ROOT.is_dir() and HERE.is_dir() and OUT.is_dir()
assert not CHECK.exists() and not (OUT / "delivery_manifest.json").exists()
receipt_path = OUT / "review_receipt.json"
receipt_sha = sha(receipt_path)
assert receipt_sha == "ee6cf6fe55daf89225b9746ba4d595fdd26042cc5e1513c9159b1e40edc6bf21"
receipt = read(receipt_path)
assert receipt["status"] == "PASS" and receipt["baseline"] == "6019ed956f0008c4a97b42dc9e0aebb74f31f5c5"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip() == receipt["baseline"]
for path, expected in receipt["source_sha256"].items():
    assert sha(ROOT / path) == expected

snapshots = OUT / "collector_sources"
assert not snapshots.exists()
snapshots.mkdir()
for name in ("independent_review.py", "close_review.py", "package_review.py"):
    source = HERE / name
    assert source.is_file()
    shutil.copyfile(source, snapshots / name)
    assert sha(source) == sha(snapshots / name)

files = []
for path in sorted(OUT.rglob("*")):
    if path.is_file():
        role = "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result"
        files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role,
                      "keep_reason": "独立审查原件、当前脚本快照或原生日志；保留历史环境失败及最终离线PASS，不代表板上验收。"})

g1 = ROOT / "report/evidence/S2B-T19/pc_nvlist_20261013_r01"
actual = read(g1 / "final_r03/actual_cpu1_rrd_r02.json")
inputs = [g1 / "delivery_manifest_r02.json", g1 / "delivery_manifest.json",
          g1 / "final_r03/actual_cpu1_rrd_r02.json", Path(actual["source"]),
          g1 / "final_r03/run_result.json", g1 / "consumers_dependencies_r05/run_result.json"]
assert sha(inputs[0]) == receipt["g1_manifest"]["sha256"]
assert sha(Path(actual["source"])) == actual["source_sha256"]
for path in inputs:
    assert path.is_file() and path.is_relative_to(ROOT)
    files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": "input",
                  "keep_reason": "已核验的真实故障、G1软件验证或历史原清单，只读依赖引用，不复制历史证据树。"})
for path, expected in receipt["source_sha256"].items():
    files.append({"path": path, "sha256": expected, "role": "source", "keep_reason": "本次独立审查固定的实际生产或测试源码，哈希未改。"})
files.append({"path": "verification/check_stage_delivery.py", "sha256": sha(ROOT / "verification/check_stage_delivery.py"),
              "role": "source", "keep_reason": "绑定本次只读机器包装核验实现。"})

historical = read(OUT / "run_result.json")
final = read(OUT / "rerun_r02/run_result.json")
assert historical["exit_code"] == 1 and final["exit_code"] == 0 and final["tests_run"] == 92
assert final["status"] == "PASS" and final["source_sha256"] == receipt["source_sha256"]
checks = [{"name": "initial_r01_ENVIRONMENT_FAILURE", "status": "FAIL",
           "command": subprocess.list2cmdline(historical["command"]), "exit_code": 1,
           "reason": "沙箱拒绝父路径枚举及既有pyserial源码读取，共123个权限ERROR；原始结果与日志保留。"},
          {"name": "rerun_r02_92_methods", "status": "PASS",
           "command": subprocess.list2cmdline(final["command"]), "exit_code": 0},
          {"name": "independent_review_receipt_closure", "status": "PASS",
           "command": subprocess.list2cmdline(receipt["command"]), "exit_code": receipt["native_exit_code"]}]
for check in receipt["packaging_checks"]:
    checks.append({"name": "independent_G1_" + check["mode"],
                   "status": "PASS" if check["exit_code"] == 0 else "BLOCKED",
                   "command": subprocess.list2cmdline(check["command"]), "exit_code": check["exit_code"],
                   **({"reason": "G1历史FAIL及实板NOT_RUN仍严格阻断inputs；不是最终92项软件回归失败。"} if check["exit_code"] else {})})
checks.append({"name": "hardware_G3_G4_G5", "status": "NOT_RUN", "command": None, "exit_code": None,
               "reason": "当前仅独立软件G2审查，不操作真实SDK、会话、板卡或串口；硬件及阶段验收仍待总控完成。"})
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T19", "run_id": OUT.name,
    "source_commit": receipt["baseline"], "evidence_dir": OUT.relative_to(ROOT).as_posix(),
    "interfaces": [], "interfaces_not_applicable_reason": "独立审查既有visibility0 PC读取修复及证据绑定；无新上游接口，不修改总线、UART、模型或平台语义，也不批准接口冻结。",
    "tool_versions": {"python": final["python_version"], "vitis_sdk_source": "2026.1官方target.py，仅AST提取函数，无实际SDK模块或硬件调用。"},
    "files": files, "checks": checks,
    "limitations": ["最终92项为离线独审：89项回归和3项官方AST补充检查；不代表G3/G4/G5。",
        "79消费者仅核查真实原件和哈希，未复跑；SDK及其哈希绑定见原始review_receipt.json。",
        "collector_sources保存归档时当前脚本，不冒充初次失败运行时的即时脚本快照。",
        "初次环境失败的run_result.status保留原CHANGES_REQUIRED字段，按123个权限ERROR明确分类为ENVIRONMENT_FAILURE。",
        "峰值内存未测；不批准visibility1或完整模型验收。",
        "自身evidence包装检查结果保存在独立tmp/package_check_r01，避免清单递归；可依据固定命令再次只读核验。"]}
manifest_path = OUT / "delivery_manifest.json"
with manifest_path.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
CHECK.mkdir()
command = [sys.executable, "-X", "utf8", "-B", "verification/check_stage_delivery.py", "--mode", "evidence",
           "--manifest", manifest_path.relative_to(ROOT).as_posix()]
started = time.monotonic()
result = subprocess.run(command, cwd=ROOT, capture_output=True)
for name, raw in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
    with (CHECK / name).open("xb") as stream:
        stream.write(raw)
execution = {"command": command, "exit_code": result.returncode, "elapsed_seconds": time.monotonic() - started,
             "manifest_path": str(manifest_path), "manifest_sha256": sha(manifest_path),
             "receipt_before_sha256": receipt_sha, "receipt_after_sha256": sha(receipt_path),
             "source_sha256": {path: sha(ROOT / path) for path in receipt["source_sha256"]},
             "stdout_sha256": sha(CHECK / "stdout.log"), "stderr_sha256": sha(CHECK / "stderr.log"),
             "actual_hardware_calls": 0, "repeated_tests": 0}
with (CHECK / "execution.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(execution, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
assert execution["source_sha256"] == receipt["source_sha256"]
assert execution["receipt_before_sha256"] == execution["receipt_after_sha256"]
print(json.dumps({"exit_code": result.returncode, "manifest_sha256": execution["manifest_sha256"],
                  "files_bound": len(files), "check_execution": str(CHECK / "execution.json")}, ensure_ascii=False))
sys.exit(result.returncode)
