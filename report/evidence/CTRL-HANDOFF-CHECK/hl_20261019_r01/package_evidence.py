# -*- coding: utf-8 -*-
"""打包 HL-T01~HL-T06（交接检查器）的 G1/G2 证据：只复制 tmp 下的审查与自测产物。"""
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone, timedelta

REPO = r"D:\FPGA_Competition"
EVID = os.path.join(REPO, "report", "evidence", "CTRL-HANDOFF-CHECK", "hl_20261019_r01")
CST = timezone(timedelta(hours=8))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rec(path):
    if not os.path.isfile(path):
        return {"path": path, "missing": True}
    return {
        "source": path,
        "bytes": os.path.getsize(path),
        "sha256_packaging_time": sha256(path),
        "mtime_utc8": datetime.fromtimestamp(os.path.getmtime(path), CST).isoformat(),
    }


os.makedirs(os.path.join(EVID, "review"), exist_ok=True)
os.makedirs(os.path.join(EVID, "selftest"), exist_ok=True)

# 三轮独立审查的机器可读结论
reviews = {
    "HL-T02_20261019T2115_rev1": r"tmp\HL-T02\20261019T2115_rev1\review_findings.json",
    "HL-T04_20261019T2135_rev2": r"tmp\HL-T04\20261019T2135_rev2\review_findings.json",
    "HL-T06_20261019T2146_rev3": r"tmp\HL-T06\20261019T2146_rev3\review_findings.json",
}
review_records = {}
for name, rel in reviews.items():
    src = os.path.join(REPO, rel)
    dst = os.path.join(EVID, "review", name + ".review_findings.json")
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    review_records[name] = {"copied": rec(dst), "original": rel}

# 冻结交付物（源文件不复制，只登记哈希；它们进入同一次提交）
tool_files = ["verification/handoff_check.py", "verification/test_handoff_check.py"]
tool_records = {}
for rel in tool_files:
    p = os.path.join(REPO, rel.replace("/", os.sep))
    tool_records[rel] = {"bytes": os.path.getsize(p), "sha256_frozen": sha256(p)}

# 自测原始输出（两次 OK 的 run1/run2 + 守护演示）
selftests = {
    "hl05_run1": r"tmp\HL-T01\hl05_run1\out.txt",
    "hl05_run2": r"tmp\HL-T01\hl05_run2\out.txt",
}
selftest_records = {}
for name, rel in selftests.items():
    src = os.path.join(REPO, rel)
    if os.path.isfile(src):
        dst = os.path.join(EVID, "selftest", name + ".txt")
        shutil.copy2(src, dst)
        selftest_records[name] = {"copied": rec(dst), "original": rel}

manifest = {
    "schema_version": 1,
    "task_id": "CTRL-HANDOFF-CHECK",
    "run_id": "hl_20261019_r01",
    "created_utc8": datetime.now(CST).isoformat(),
    "author": "DSH (team lead)",
    "scope": "Codex↔DSH 交接检查器（只读）的 G1 交付与 G2 独立审查证据封包",
    "deliverables": tool_records,
    "review_rounds": review_records,
    "self_test_outputs": selftest_records,
    "verification_commands": [
        {
            "command": "python -B -m unittest verification.test_handoff_check -v",
            "native_exit_code_at_2132_2143_utc8": 1,
            "note": "21:30 后首次复现 BLOCKING-1（35 用例中 test_JSON输出为单行且可解析 失败）",
        },
        {
            "command": "python -B -m unittest verification.test_handoff_check -v",
            "tests": 38,
            "native_exit_code_at_2143_and_after": 0,
            "note": "HL-T05 修复后连跑两次均 OK（退出码 0），证据见 self_test_outputs",
        },
        {
            "command": "python -B verification/handoff_check.py --print-template",
            "native_exit_code": 0,
        },
        {
            "command": "python -B verification/handoff_check.py --worktree D:\\FPGA_Competition",
            "native_exit_code": 1,
            "note": "真实状态：c FAIL（共享工作区未提交且无归属声明）、d FAIL（hw_server.exe PID 10116 真实存活）；e/f/g/h/i SKIP",
        },
        {
            "command": "python -B verification/handoff_check.py --worktree D:\\FPGA_Competition\\w2b",
            "native_exit_code": 1,
            "note": "b PASS 且锁路径由 git 解析为 D:/FPGA_Competition/.git/worktrees/w2b/index.lock（未假定 .git 在根）",
        },
    ],
    "independent_review": {
        "rounds": [
            {"task": "HL-T02", "verdict": "PASS", "counterexamples": 40, "note": "两个非阻断观察项，总控裁定需加固"},
            {"task": "HL-T04", "verdict": "CHANGES_REQUIRED", "counterexamples": 58, "blocking": "BLOCKING-1 测试用固定心跳字面量导致 21:30 后永久失败"},
            {"task": "HL-T06", "verdict": "PASS", "counterexamples": 58, "note": "BLOCKING-1 关闭；回归与 HL-T04 完全一致；只改测试文件，检查器哈希未变"},
        ],
        "reviewer_role": "INDEPENDENT_REVIEWER（只读；未修改被审文件；未提交）",
    },
    "limitations": [
        "d 项对真实 hw_server.exe(PID 10116，2B 会话) 判 FAIL 属预期；检查器只报告、不结束进程。",
        "g 项只校验证据目录存在与 manifest.json 可读，不校验清单 schema（属 check_stage_delivery.py）。",
        "POSIX 进程枚举分支（ps/pgrep）未在 Windows 实跑，仅以注入方式覆盖 SKIP。",
        "两名真实 Agent 的并发接管时序未测；检查器不能阻止他人写入，只能核验契约。",
        "所有 sha256 为打包时计算，不冒充运行时绑定；本封包不含运行时二进制产物。",
        "审查与自测的临时产物仍在 tmp/ 下保留原件，本封包为只读复制。",
    ],
    "known_observations": [
        "OBS-1（HL-T06，可选加固）：正则守护用例可被多种写法绕过（单引号字典式、间接常量、datetime 计算式、setdefault 位置），属形态烟测；真正保障来自两条动态心跳行为用例。关闭条件：改为结构约束（携带 --record 的 run_cli 必须来自 live_record()）。",
        "OBS-2（HL-T06，可选加固）：未来若把 make_record()（NOW 派生）直接用于真实 CLI 用例并断言 e，可能复现同类腐化且正则不命中。关闭条件：加命名/断言约束，限定 make_record() 仅供 now=NOW 注入用例使用。",
        "OBS-3（HL-T04，可选加固）：模板中字段语义与匹配规则为硬编码散文，当前与实现逐条一致；未来改实现需手工同步。",
    ],
    "hardware_execution": "NOT_RUN",
    "notes": "本轮未跑 Vivado/xsim、未动 w2b、未结束任何进程；提交只含交付物与本证据包。",
}

mpath = os.path.join(EVID, "manifest.json")
with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print(json.dumps({"evidence_dir": EVID, "manifest_sha256": sha256(mpath)}, ensure_ascii=False, indent=2))