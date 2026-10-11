"""R2证据封包：按真实命令结果记录PASS/FAIL，不覆盖旧Run或伪造实板批准。"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
TEMP = ROOT / "tmp/2B/S2B-T16" / RUN.name
INTERFACE = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"


def sha(path):
    """计算原字节SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    """新建UTF-8原件，不重写已有结果。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def command_text(argv):
    """生成Windows精确参数展示；执行始终使用参数数组。"""
    return subprocess.list2cmdline(argv)


def execute(mode, manifest, output_parent, prefix):
    """保存真实原生输出；不将预期拒绝伪称通过。"""
    argv = [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"),
            "--mode", mode, "--manifest", str(manifest)]
    started = time.monotonic()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True)
    for label, raw in (("stdout", result.stdout), ("stderr", result.stderr)):
        with (output_parent / (prefix + "_" + label + ".log")).open("xb") as stream:
            stream.write(raw)
    return {"command_argv": argv, "native_exit_code": result.returncode,
            "elapsed_seconds": time.monotonic() - started, "manifest_sha256": sha(manifest),
            "status": "PASS" if result.returncode == 0 else "FAIL"}


validation = json.loads((RUN / "validation_result.json").read_text(encoding="utf-8"))
outcomes = json.loads((RUN / "test_case_outcomes.json").read_text(encoding="utf-8"))
assert validation["status"] == "PASS" and outcomes["tests_run"] == 125
for name, expected in validation["source_sha256_before"].items():
    assert sha(ROOT / name) == expected, "封包前源码漂移：" + name
old_manifest = "report/evidence/S2B-T16/cold_observation_20261011_r01/delivery_manifest.json"
assert sha(ROOT / old_manifest) == "b6122a97f7a3594b9524e1e45cdeb9a0afe25c67034aa51d441e30bac997d827"
checks = [
    {"name": "T16原56方法加cold17方法、T19全部19方法和T20全部33方法",
     "status": "PASS", "command": command_text(validation["command_argv"]), "exit_code": 0},
    {"name": "本轮五个代码文件差异空白检查", "status": "PASS",
     "command": command_text(validation["diff_command_argv"]), "exit_code": validation["diff_native_exit_code"]},
    {"name": "R2独立G2", "status": "NOT_RUN", "command": None, "exit_code": None,
     "reason": "Developer候选已完成离线回归，尚待root固定五源并派独立Reviewer。"},
    {"name": "实际runtime兼容与cache", "status": "BLOCKED", "command": None, "exit_code": None,
     "reason": "完整实际平台兼容及独立批准尚未就绪；本轮19项T19均是明确MOCK，不能生成实板批准。"},
    {"name": "BOARD/G3", "status": "NOT_RUN", "command": None, "exit_code": None,
     "reason": "本轮未导入真实SDK或串口，硬件调用数为0。"}]
write(RUN / "repair_basis.json", {
    "source_baseline": validation["source_baseline"], "observed_head": validation["observed_head_after"],
    "r1_manifest": {"path": old_manifest, "sha256": sha(ROOT / old_manifest)},
    "r1_review_receipt_sha256": sha(RUN / "r1_review_receipt.json"),
    "r1_finding": "P1：EOS-only和缺bit3字段被接受；R2增加occupied==set(range(32))。",
    "old_source_sha256": {"verification/s2b_board_jtag.py": "b48533d9ea42eb779e7db55816539efc2a15a9249595b754f67d28394bcf59cf",
                          "verification/test_s2b_board_jtag.py": "35af463f87c1d1323bb10672b4e913bef940162b1de8ac10a40a10c9e9d8eeba",
                          "verification/test_s2b_cold_observation.py": "f892158d264f926589389ce2465a7e00f4e7cd49b8a05d2df15792bb59aca786"},
    "coverage": ["完整0..31、无重叠、每个字段值与32位原字一致，EOS名称精确且唯一位4。",
                 "允许非EOS未知字段名称；覆盖全部32位的独立手算边界0/0xFFFFFFFF/0x80000008。",
                 "EOS-only两态、缺bit3、缺bit31、重叠和矛盾拒绝；reset前/bit后缺位均阻断后续下载并保存raw。",
                 "T19固定新SHA，旧Git源码91bb及改字节明确拒绝；原假类/alias/code/SDK门禁回归保留。",
                 "DDRC低3位1、OCM ready/result2/rc0、CPU0自有清理、CPU1Stopped及failure锁仍由原回归覆盖。"],
    "facts": {"mock_methods": outcomes["methods_by_group"], "hardware_calls": 0,
              "cold_lifecycle_proven": False, "r2_g2": "NOT_RUN", "g3": "NOT_RUN"},
    "temporary_redirection": "T16标准TemporaryDirectory、T20 TEST_PARENT及T19两个parent表达式仅重定向到本轮tmp；未修改断言/门禁。",
    "sdk_source_inventory": "sdk_source_inventory.json",
    "platform_checker": validation["platform_checker"],
    "limitations": validation["limitations"]})


def build_manifest(path, check_rows):
    """清单条目仅含path/sha256/role；体积另记inventory。"""
    files = []
    for item in sorted(RUN.rglob("*")):
        if item.is_file() and item != path:
            role = "source" if item.suffix == ".py" or "source_snapshot" in item.parts else "log" if item.suffix == ".log" else "result"
            files.append({"path": item.relative_to(ROOT).as_posix(), "sha256": sha(item), "role": role})
    files += [{"path": name, "sha256": expected, "role": "input" if name == INTERFACE else "source"}
              for name, expected in validation["source_sha256_before"].items()]
    files.append({"path": old_manifest, "sha256": sha(ROOT / old_manifest), "role": "input"})
    write(path, {"schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN.name,
          "source_commit": validation["source_baseline"], "evidence_dir": RUN.relative_to(ROOT).as_posix(),
          "files": files, "interfaces": [{"name": "PS/PL候选CSR与缓存所有权接口",
             "version": "s2b-physical-candidate/0.1.1", "frozen": False,
             "path": INTERFACE, "sha256": validation["source_sha256_before"][INTERFACE]}],
          "tool_versions": validation["tool_versions"], "checks": check_rows,
          "limitations": ["仅离线G1候选，独立G2待审；未提交，由root统一核对和Git提交。",
                          "实际runtime兼容、cache及BOARD/G3未执行；不能批准visibility1或统一冷生命周期。",
                          "平台checker由S4维护，只保存本轮实际快照和SHA；没有改动该文件。",
                          "evidence包装通过仅证明文件绑定；inputs原生2仍阻断。"]})


precheck = RUN / "delivery_manifest_before_final_checks.json"
build_manifest(precheck, checks)
# 核验期间输出落到tmp，防止校验目录边读边增加未入清单文件。
first = execute("evidence", precheck, TEMP, "evidence_precheck")
inputs = execute("inputs", precheck, TEMP, "inputs")
for prefix in ("evidence_precheck", "inputs"):
    for suffix in ("stdout", "stderr"):
        name = prefix + "_" + suffix + ".log"
        with (RUN / name).open("xb") as stream:
            stream.write((TEMP / name).read_bytes())
write(RUN / "packaging_checks.json", {"evidence": first, "inputs": inputs,
      "interpretation": "evidence只做包装；inputs原生2表示候选未冻结、runtime受阻及G2/G3未执行。"})
assert first["native_exit_code"] == 0 and inputs["native_exit_code"] == 2
for name, row in (("stage_delivery evidence初检", first), ("stage_delivery inputs", inputs)):
    checks.append({"name": name, "status": row["status"], "command": command_text(row["command_argv"]),
                   "exit_code": row["native_exit_code"], "reason": "包装通过" if row["status"] == "PASS" else "候选未冻结、runtime受阻及G2/G3未执行导致原生2。"})
inventory = [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}
             for path in sorted(RUN.rglob("*")) if path.is_file()]
write(RUN / "artifact_inventory.json", {"scope": "最终清单和本inventory自身创建前的文件体积快照", "files": inventory})
final = RUN / "delivery_manifest.json"
build_manifest(final, checks)
last = execute("evidence", final, TEMP, "final_evidence")
last["final_source_sha256"] = {name: sha(ROOT / name) for name in list(validation["source_sha256_before"])[:5]}
last["observed_head_final"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
write(TEMP / "final_packaging_receipt.json", last)
print(json.dumps(last, ensure_ascii=False))
raise SystemExit(last["native_exit_code"])
