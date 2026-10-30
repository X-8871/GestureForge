"""离线复算旧M4-b零差异字段的有效性，不修改上游或运行硬件。"""

import hashlib
import json
import re
import subprocess
from pathlib import Path


def main():
    """固定三个成功样本与一份失败原始日志，保留源码和ELF反汇编依据。"""
    worktree = Path(r"D:\codex-worktrees\w4").resolve(strict=True)
    parent = Path(__file__).resolve().parents[2] / "report/evidence/R03-M3"
    run = parent / "m4b_rootcause_20261031_r02"
    if not parent.is_dir() or run.exists():
        raise FileExistsError("需要现有精确父目录及全新RunId")
    source_commit = "6c09df12c585568b2737da2116fe43913e0062cb"
    source_rel = "vitis/stage4/ps/s4d_ps_app.c"
    source = subprocess.run(["git", "--no-optional-locks", "-C", str(worktree), "cat-file", "blob", source_commit + ":" + source_rel], capture_output=True, check=True).stdout
    text = source.decode("utf-8")
    function = text[text.index("int s4d_m4b_selfcheck(void)"):]
    if not re.search(r"uint32_t d13 = 0, d26 = 0", function):
        raise ValueError("历史源码初值前提变化")
    guard = function[function.index("/* PL→PS"):function.index("/* ACK 收尾")]
    if "if (done == 1)" not in guard or "d13 = s4d_count_diff" not in guard:
        raise ValueError("历史源码比较门控前提变化")
    base = worktree / "report/evidence/S4-T34"
    failures = base / "s4d_m4b_baseline_2b_20261029_r01"
    identity_path = failures / "IDENT.json"
    ident = json.loads(identity_path.read_text(encoding="utf-8"))
    elf_item = next(item for item in ident["checks"] if item["tag"] == "m4b_elf")
    elf = Path(elf_item["path"]).resolve(strict=True)
    if hashlib.sha256(elf.read_bytes()).hexdigest() != elf_item["sha256"]:
        raise ValueError("旧ELF不匹配原窗口身份")
    paths = [failures / "m4b_uart.log",
             base / "s4d_m4b_close_20261029_r01/m4b_uart.log",
             base / "s4d_freeze_r2_m4b_2b_20261029_r01/m4b_uart.log",
             base / "s4d_freeze_r5_m4b_p2d_20261029_r02/m4b_uart.log"]
    samples = []
    run.mkdir()
    (run / "historical_app_source.c").write_bytes(source)
    for index, path in enumerate(paths):
        path = path.resolve(strict=True)
        raw = path.read_bytes()
        log = raw.decode("utf-8", "replace")
        matches = re.findall(r"M4B RESULT=(\{[^\r\n]+\})", log)
        if len(matches) != 1:
            raise ValueError(f"原始日志必须恰有一个结果：{path}")
        result = json.loads(matches[0])
        row = {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
               "result": result, "actual_heads_compare_line": bool(re.search(r"M4B HEADS diff13=", log))}
        (run / f"sample_{index}_uart.log").write_bytes(raw)
        samples.append(row)
    old = samples[0]
    if old["result"]["done"] != 2 or old["result"]["error"] != 5 or old["actual_heads_compare_line"]:
        raise ValueError("失败窗口门控证据与假设不一致")
    for sample in samples[1:]:
        result = sample["result"]
        if not (result["pass"] == result["done"] == 1 and result["error"] == 0
                and result["diff13"] == result["diff26"] == 0 and sample["actual_heads_compare_line"]
                and result["tail13_before"] == 0x5A5A5A5A and result["tail13_after"] == 0x5A5A0506
                and result["lane01_ok"] == result["lane23_ok"] == 1):
            raise ValueError("成功样本未满足真实比较与尾字证据")
    objdump = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-objdump.exe").resolve(strict=True)
    command = [str(objdump), "-d", "--disassemble=s4d_m4b_selfcheck", str(elf)]
    asm = subprocess.run(command, capture_output=True)
    (run / "old_elf_disassembly.txt").write_bytes(asm.stdout)
    (run / "objdump_stderr.txt").write_bytes(asm.stderr)
    assembly = asm.stdout.decode("utf-8", "replace")
    timeout_match = re.search(r"mov\s+r2, #(\d+)[^\r\n]*\r?\n[^\r\n]*str\s+r2, \[r4, #40\]", assembly)
    if not timeout_match:
        raise ValueError("未能从旧ELF识别写core_timeout寄存器的立即数，不能猜测")
    timeout_cycles = int(timeout_match.group(1))
    registration = base / "ps_decode_link_20261028_r01/app_elf_registration_r3.json"
    registration_bytes = registration.read_bytes()
    (run / "historical_registration_r3.json").write_bytes(registration_bytes)
    if "400 周期" not in registration_bytes.decode("utf-8") or timeout_cycles != 400:
        raise ValueError("历史登记与真实ELF超时常量不一致，停止诊断")
    result = {"status": "PASS_OFFLINE_DIAGNOSIS", "source_commit": source_commit,
              "source_path": source_rel, "source_sha256": hashlib.sha256(source).hexdigest(),
              "source_hash_basis": "commit_blob", "old_elf": elf_item,
              "samples": samples, "successful_sample_count": 3,
              "old_diff_zero_meaning": "done=2时跳过比较，d13/d26保留初始化0；不是相等实测",
              "old_timeout_cycles_from_exact_elf": timeout_cycles,
              "old_timeout_seconds_at_50MHz": timeout_cycles / 50000000,
              "timeout_correction": "本次失败ELF ada4b30d实际为400周期，不是其他陈旧ELF的0x40000000；r01粗略时间字段已被本r02更正，旧包保留",
              "new_timeout_seconds_at_50MHz": 0xFFFFFFFF / 50000000,
              "objdump_command": command, "objdump_exit_code": asm.returncode,
              "limitations": ["历史源码快照与旧ELF相关比较门控控制流另须结合反汇编复核，不能仅凭当前源码断言旧ELF",
                              "三个成功样本是历史窗口复算，不是本轮新增板上多次采样",
                              "本轮M3初始CPU Running导致未执行；历史6bit变化根因未由只读保持测试排除",
                              "未改冻结应用；建议后续非冻结修订加compare_performed或null差异字段"], "exit_code": asm.returncode}
    (run / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "successful_samples": 3, "old_comparison_performed": False,
                      "objdump_exit_code": asm.returncode, "run": str(run)}, ensure_ascii=False))
    return asm.returncode


if __name__ == "__main__":
    raise SystemExit(main())
