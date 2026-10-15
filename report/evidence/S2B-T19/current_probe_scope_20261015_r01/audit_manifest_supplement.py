"""追加修正清单的三个不适用键；保留首次清单及失败，不重算或覆盖原采集。"""

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[4]
RUN = "report/evidence/S2B-T19/current_probe_scope_20261015_r01"
ORIGINALS = {
    "audit_current_probe.py": "cb96b52a00f1aab9b403aa6fde077e62b1cfb916d4481028ff10023e537d0b89",
    "summary.json": "a71a57f88bf7e7cbe6fea99d6077a71f97c43b7e0f24d9745a0b12220516fdcc",
    "delivery_manifest.json": "2c64fa4f3a7d391b5603cfd678ee1753c864fb54c590b055b2e4ea8ef0bd046a",
}
TARGET = "platform_delivery_manifest.json"


def need(condition, message):
    """明确拒绝漂移和覆盖。"""
    if not condition:
        raise ValueError(message)


def sha(data):
    """返回原字节摘要。"""
    return hashlib.sha256(data).hexdigest()


def encode(value):
    """输出UTF-8、末尾换行。"""
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def invoke(arguments):
    """仅执行只读复核入口，记录真实原始stdout/stderr和退出码。"""
    command = [sys.executable, "-X", "utf8", "-B", *arguments]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
    return {"command": command, "native_exit_code": result.returncode,
            "stdout_hex": result.stdout.hex(), "stderr_hex": result.stderr.hex()}


def main():
    """采集追加补充；verify完全只读，沿用原脚本的祖先基线门禁。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    need(args.collect != args.verify, "必须且仅指定--collect或--verify")
    directory = ROOT / RUN
    for name, expected in ORIGINALS.items():
        path = directory / name
        need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == expected, "原三文件SHA漂移：" + name)
    current = invoke([RUN + "/audit_current_probe.py", "--verify"])
    need(current["native_exit_code"] == 0, "原静态准入只读复核失败")
    checker_args = ["verification/check_stage_delivery.py", "--mode", "evidence", "--manifest"]
    if args.verify:
        checked = invoke(checker_args + [RUN + "/" + TARGET])
        need(checked["native_exit_code"] == 0, "最终限定清单包装核验失败")
        print("CURRENT_PROBE_SUPPLEMENT_VERIFIED; original_failure_preserved; hardware_not_run")
        return
    need(sorted(p.name for p in directory.iterdir()) == sorted([*ORIGINALS, "audit_manifest_supplement.py"]), "Run已有额外文件，禁止覆盖补充")
    original = json.loads((directory / "delivery_manifest.json").read_text(encoding="utf-8"))
    candidate = copy.deepcopy(original)
    changes = []
    for item in candidate["checks"]:
        if item["status"] == "NOT_APPLICABLE":
            need("command" not in item and "exit_code" not in item, "原清单待修正键不符")
            item.update(command=None, exit_code=None)
            changes.append(item["name"])
    need(len(changes) == 3, "只允许三项NA包装键修正")
    spec = importlib.util.spec_from_file_location("current_probe_delivery_schema", ROOT / "verification/check_stage_delivery.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    errors, statuses = [], []
    for index, item in enumerate(candidate["checks"]):
        checker.validate_check(item, index, "evidence", errors, statuses)
    need(not errors, "内存checks schema核验失败：" + repr(errors))
    failed = invoke(checker_args + [RUN + "/delivery_manifest.json"])
    need(failed["native_exit_code"] == 2, "原失败未重现")
    failed_json = json.loads(bytes.fromhex(failed["stdout_hex"]))
    required_errors = [f"checks[{i}]缺少字段：{key}" for i in (8, 9, 10) for key in ("command", "exit_code")]
    need(all(error in failed_json["errors"] for error in required_errors), "原NA缺键失败未完整重现")
    record = {"schema_version": 1, "kind": "s2b-current-probe-packaging-supplement/1.0.0",
        "role": "DEVELOPER_EVIDENCE", "originals_sha256": ORIGINALS,
        "first_observed_packaging_shell_wrapper_exit_code": 1,
        "first_observed_packaging_native_exit_code": "首次外层工具只报告PowerShell包装退出1；实际子进程退出码以本补充直接捕获的2为准。",
        "first_observed_packaging_errors": required_errors,
        "supplement_collection_attempts": [
            {"native_exit_code": 1, "stderr": "{\"status\": \"BLOCKED\", \"error\": \"原失败未重现\"}\n",
             "reason": "初次补充把外层PowerShell退出1误当原生退出码，门禁在输出前拒绝；现按subprocess原生捕获2校正。"},
            {"native_exit_code": 0, "reason": "完整捕获包装失败并追加正确NA键。"}],
        "original_static_verify": current, "original_packaging_failure_reproduced": failed,
        "changes": {"NA_check_names": changes, "added_keys": {"command": None, "exit_code": None}},
        "reason": "仅补齐三个NA检查的强制包装键；状态/理由/原六facts、新build/GP0结果及限制均保持原语义。原清单和全部失败原件保留。",
        "final_platform_manifest": RUN + "/" + TARGET, "independent_review_asserted": False, "hardware_execution": "NOT_RUN"}
    record_bytes = encode(record)
    # 记录先独占落盘，使最终清单能够在内存执行完整实际schema和目录核验。
    with (directory / "packaging_supplement.json").open("xb") as stream:
        stream.write(record_bytes)
    files = {item["path"]: item for item in candidate["files"]}
    for name, role in (("delivery_manifest.json", "diagnostic"), ("audit_manifest_supplement.py", "source"), ("packaging_supplement.json", "diagnostic")):
        relative = RUN + "/" + name
        files[relative] = {"path": relative, "sha256": sha((directory / name).read_bytes()), "role": role,
                           "keep_reason": "保留原包装失败、真实复现stdout/stderr/退出码及追加修正脚本。"}
    candidate["files"] = [files[path] for path in sorted(files)]
    candidate["limitations"].append("首次delivery_manifest.json缺少三个NA项的command/exit_code键而包装失败；本追加清单仅补为null，原件及失败捕获保持。")
    errors, warnings, statuses = checker.validate_manifest(candidate, "evidence", ROOT, directory / TARGET)
    need(not errors and not warnings, "最终清单内存完整schema/绑定/目录核验失败：" + repr(errors + warnings))
    need(all(item["status"] in ("PASS", "NOT_APPLICABLE") for item in candidate["checks"]), "最终清单不满足限定入口状态门禁")
    with (directory / TARGET).open("xb") as stream:
        stream.write(encode(candidate))
    print("CURRENT_PROBE_MANIFEST_SUPPLEMENT_COLLECTED; native_exit_code=0; original_failure_preserved")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "BLOCKED", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
