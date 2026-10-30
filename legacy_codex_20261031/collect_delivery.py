"""建立本轮独立证据汇总与精确待提交清单，不操作Git暂存/提交。"""

import hashlib
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


def write_json(path, value):
    """所有新证据使用UTF-8和LF，已存在目标一律拒绝覆盖。"""
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    """只新建本轮RunId，编译输出保存到隔离临时目录，声明尚未提交。"""
    root = Path(__file__).resolve().parent.parent
    evidence = (root / "report/evidence").resolve(strict=True)
    task = evidence / "CTRL-LEGACY"
    run = task / "residuals_20261031_r01"
    if run.exists():
        raise FileExistsError(run)
    task.mkdir(exist_ok=True)
    run.mkdir()
    (task / ".gitattributes").write_text("* -text\n", encoding="utf-8", newline="\n")
    temp_parent = Path(r"D:\tmp").resolve(strict=True)
    build = temp_parent / "codex_c2_arm_20261031_r01"
    build.mkdir(exist_ok=False)
    compiler = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe").resolve(strict=True)
    c2 = root / "legacy_codex_20261031/c2"
    includes = [r"D:\FPGA_Competition\w2b\verification", r"D:\codex-worktrees\w4\report\evidence\S5-T01\s5_p3b_sw_20261030_r01\src"]
    command = [str(compiler), "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic", "-O0", "-mcpu=cortex-a9",
               "-mfpu=vfpv3", "-mfloat-abi=hard", "-S"]
    for include in includes:
        command += ["-I", str(Path(include).resolve(strict=True))]
    assembly = build / "c2_s5_publish_arm.s"
    command += [str(c2 / "c2_s5_publish.c"), "-o", str(assembly)]
    version = subprocess.run([str(compiler), "--version"], capture_output=True, check=True).stdout.decode("utf-8", "replace").splitlines()[0]
    result = subprocess.run(command, capture_output=True)
    (run / "arm_compile_stdout.txt").write_bytes(result.stdout)
    (run / "arm_compile_stderr.txt").write_bytes(result.stderr)
    if result.returncode:
        write_json(run / "arm_compile.json", {"command": command, "exit_code": result.returncode, "compiler_version": version})
        return result.returncode
    data = assembly.read_bytes()
    (run / "c2_s5_publish_arm.s").write_bytes(data)
    text = data.decode("utf-8")
    match = re.search(r"(?ms)^c2_store_seqlock:\s*(.*?)^\s*\.size\s+c2_store_seqlock", text)
    if not match:
        raise ValueError("ARM汇编中未找到独立锁字写函数")
    body = match.group(1)
    if not re.search(r"\bstr\s+r\d+,\s*\[r\d+\]", body) or re.search(r"\bstr[b|h]\b", body):
        raise ValueError("ARM锁字写缺少单次STR或出现字节/半字STR")
    write_json(run / "arm_compile.json", {"command": command, "exit_code": result.returncode, "compiler_version": version,
                "target": "Cortex-A9，AArch32小端", "lock_function_assembly": body,
                "meaning": "只验证目标代码生成使用32位STR；不证明板上DDR/cache可见性或消费者协议"})
    write_json(run / "validation_summary.json", {
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "R08": {"status": "PASS", "scope": "正式OFFER11字段、19项归属已由DSH020 CLAIM关闭", "commit": "892d944f6a1c04a8956fce200f9edc416edce8c6"},
        "R03": {"status": "BLOCKED", "tool_review": "PASS", "mock_tests": 43, "mock_exit_code": 0,
                "hardware_capture": "NOT_RUN", "reason": "初始CPU0 Running与租约不符，约59.453秒安全收窗，新OFFER待提供", "offline_rootcause": "PASS_R02"},
        "C2": {"status": "PASS_OFFLINE_BLOCKED_BOARD", "review": "PASS_R02", "PS51_exit_code": 0, "PS7_exit_code": 0,
               "ARM_compile_exit_code": 0, "profile": "sidecar+0x100/14项，DSH022 rev3", "board": "NOT_RUN"},
        "C3": {"status": "PASS", "review": "PASS_R02", "unit_tests": 11, "exit_code": 0,
               "period_us": 16673.669516, "period_scope": "历史6沿/5间隔的VDMA读帧代理；非相机SOF/非HDMI物理边沿/非推理P"},
        "C4": {"status": "FAIL", "review": "CHANGES_REQUIRED", "meaning": "复审报告已完成，原阶段6证据存在阻断；未修改冻结物"},
        "R02": {"SEC": "原Stage3 task11仍BLOCKED_NOT_RUN；仅当前不含相机wrapper的S5/S6范围可论证N/A，待责任方裁决",
                "no_ILA_alternatives": "已交付分层建议，未伪称实测"},
        "limitations": ["C1既有包已提交，之后本轮新增代码/证据等待DSH按交接约定串行提交",
                        "此汇总不是Git提交或commit_blob交付清单，strict门禁待DSH提交后建立",
                        "独立回归结果引用固定Reviewer报告，未无理由重复全套测试", "未push、ENABLE=0、未改阶段5/6冻结物"]})
    prefixes = [root / "legacy_codex_20261031", evidence / "R03-M3", task]
    files = []
    for prefix in prefixes:
        for path in sorted(prefix.rglob("*")):
            if not path.is_file() or path.suffix == ".pyc" or "__pycache__" in path.parts or path.name == "submission_inventory.json":
                continue
            raw = path.read_bytes()
            files.append({"path": path.relative_to(root).as_posix(), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    write_json(run / "submission_inventory.json", {"status": "PENDING_DSH_SERIAL_COMMIT", "identity_basis": "工作区字节，仅供提交核对；非交付manifest",
               "allowed_prefixes": [p.relative_to(root).as_posix() for p in prefixes], "files": files,
               "exclude": [".codex/STATE.md原历史差异（R08新段如需入库须逐差异处理）", "两份S6-A规格历史差异", "14个旧证据目录", "其他工作树/main业务文件", "编译临时目录D:/tmp/codex_c2_arm_20261031_r01"]})
    print(json.dumps({"run": str(run), "files": len(files), "bytes": sum(x["bytes"] for x in files), "ARM_compile_exit_code": 0,
                      "status": "PENDING_DSH_SERIAL_COMMIT"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
