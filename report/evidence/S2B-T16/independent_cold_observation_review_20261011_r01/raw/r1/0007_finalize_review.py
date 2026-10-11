"""冻结独立审查回执与精确待归档原始文件列表，不写项目证据。"""
import hashlib
import json
from pathlib import Path
import subprocess

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    """使用UTF-8只新建文件，不覆盖原件。"""
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as output:
        json.dump(data, output, ensure_ascii=False, indent=2)
        output.write("\n")


execution = json.loads((RUN / "execution_receipt.json").read_text(encoding="utf-8"))
diff_command = ["git", "diff", "--check", "--", *execution["source_sha256"]]
result = subprocess.run(diff_command, cwd=ROOT, capture_output=True)
(RUN / "diff_stdout.log").write_bytes(result.stdout)
(RUN / "diff_stderr.log").write_bytes(result.stderr)
assert result.returncode == 0
for path, digest in execution["source_sha256"].items():
    assert sha(ROOT / path) == digest
sources = [
    {"title": "UG470 v1.17表5-29（印刷107页）", "url": "https://docs.amd.com/api/khub/documents/FOs3lXmlcWxBhTIFxVKyGA/content", "verified_fact": "EOS位4仅表示Startup序列是否结束，不证明旧AXI、cache、arena生命周期结束。"},
    {"title": "UG585 v1.15 Register (ddrc) mode_sts_reg", "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-ddrc-mode_sts_reg", "verified_fact": "Absolute Address=0xF8006054；真实DAP读取32位原字保存。"},
    {"title": "UG585 v1.15 Register mode_sts_reg Details", "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-mode_sts_reg-Details", "verified_fact": "operating_mode[2:0]中1=Normal，0=Init，2=Powerdown，3=Self-refresh，4以上Deep powerdown。"},
]
write("review_receipt.json", {
    "schema_version": 1, "role": "INDEPENDENT_REVIEWER", "task_id": "S2B-T16-COLD-G2", "status": "CHANGES_REQUIRED",
    "source_commit": execution["source_commit"], "source_sha256": execution["source_sha256"],
    "g1_manifest_sha256": "b6122a97f7a3594b9524e1e45cdeb9a0afe25c67034aa51d441e30bac997d827",
    "execution_receipt_sha256": sha(RUN / "execution_receipt.json"),
    "scope": "仅离线观测门禁软件G2；全部冻结源、G1 RAW绑定、SDK原生输出形状、官方EOS/DDRC依据、正式冷生命周期与cache接口、独立反例及受影响T19/T20",
    "findings": [{"priority": "P1", "file": "verification/s2b_board_jtag.py", "line": 112,
        "title": "截断CONFIG_STATUS metadata被接受", "impact": "只含EOS位4或遗漏位3的输出仍可PASS；system-stop后及full-bit后门禁接受缺失字段证据，无法满足要求的完整native原字/metadata绑定。",
        "countercases": ["CONFIG_STATUS: 0 + EOS[4]:0", "CONFIG_STATUS: 16 + EOS[4]:1", "CONFIG_STATUS: 16 + LOW[2:0]:0 + EOS[4]:1 + UPPER[31:5]:0（缺bit3）"],
        "evidence": "tests_stderr.log：test_truncated_metadata_must_not_be_accepted两subcase及test_hole_in_metadata_must_not_be_accepted共3 FAIL",
        "basis": "root任务卡及2026-10-11澄清：SDK字段必须不重叠且完整覆盖0..31；EOS名称精确唯一bit4；其它字段无需硬白名单，但值/位宽/原字完整一致。",
        "close_when": "在解析返回前验证occupied == set(range(32))；保留现有语法/位宽/重叠/原字/EOS校验；修订所有有效mock为完整metadata，新增缺位/截断负例，并独立复审冻结新SHA。"}],
    "test_results": {"total_methods": 127, "native_exit_code": 1,
        "original_T16": {"methods": 56, "status": "PASS"}, "developer_cold": {"methods": 10, "status": "PASS"},
        "T20_CSR": {"methods": 33, "status": "PASS"},
        "T19_visibility": {"methods": 18, "pass": 14, "error": 4, "status": "FAIL", "explanation": "vitis/run_s2b_visibility_probe.py:27/316固定已审91bb…源码SHA，当前候选被正确拒绝；未调整JTAG_SHA或降低runtimecompat门禁。该项仍BLOCKED，不能作为候选T19兼容通过。"},
        "independent": {"methods": 10, "pass_methods": 8, "failed_methods": 2, "failed_subcases": 3, "status": "FAIL"}},
    "native_checks": execution["stage_checks"] + [{"name": "限定三源diff-check", "command_argv": diff_command, "status": "PASS", "native_exit_code": result.returncode}],
    "verified_behaviors": ["非canonical整数/超大值/符号/位宽/重叠/错EOS位/raw不一致/非None/stderr均拒绝", "DDRC0与2..7均阻止bit/app，已执行init事实保持True", "post-bit失败不下载app；app下载失败保留已确认configured事实", "调用顺序system-stop→EOS0→OCM ready/result2/return0→DDRCmode1→full-bit→EOS1→dow/conCPU0", "失败锁存、仅自有BP移除和CPU0停止、CPU1未resume/reset、cold_lifecycle_proven=False"],
    "official_sources": sources, "resource": execution["resource"], "elapsed_seconds": execution["elapsed_seconds"],
    "limitations": ["G2尚未通过，本Run必须保留FAIL原件；未运行G3。", "未导入真实XSDB/serial或创建Session，hardware_calls=0。", "EOS和DDRC结果不批准官方reset候选、旧AXI生命周期、cache清空、arena重新初始化或visibility1。", "T19真实runtimecompat与actualcache仍BLOCKED。", "T19/T20及T16轻量mock仅临时落点重定向，本轮不提交，由root统一归档和Git。", "新导入子进程峰值未单独测量，其余原生测试子进程峰值低于300MiB。"],
    "stop": "全部命令已结束；本Reviewer停止写入。"})
paths = [path for path in RUN.rglob("*") if path.is_file() and "scratch" not in path.relative_to(RUN).parts and path.name != "raw_delivery_manifest.json"]
files = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": "source" if path.suffix == ".py" else "log" if path.suffix in (".txt", ".log") else "result"} for path in sorted(paths)]
write("raw_delivery_manifest.json", {"schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN.name,
    "source_commit": execution["source_commit"], "evidence_dir": RUN.relative_to(ROOT).as_posix(), "files": files,
    "interfaces": [{"name": "PS/PL候选物理接口", "version": "s2b-physical-candidate/0.1.1", "frozen": False, "path": "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md", "sha256": sha(ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md")}],
    "checks": [{"name": "独立软件G2", "status": "FAIL", "command": "python -B run_review.py", "exit_code": 1}, {"name": "实板G3", "status": "NOT_RUN", "command": None, "exit_code": None}],
    "tool_versions": execution["tool_versions"], "limitations": ["raw manifest为root精确归档输入；scratch是可重建mock缓存，不在待归档范围；不宣称完整tmp目录包装通过。", "CHANGES_REQUIRED；T19兼容与实际cache保持BLOCKED。"]})
print(json.dumps({"receipt_sha256": sha(RUN / "review_receipt.json"), "raw_manifest_sha256": sha(RUN / "raw_delivery_manifest.json"), "archive_files": len(files) + 1, "receipt": str(RUN / "review_receipt.json"), "manifest": str(RUN / "raw_delivery_manifest.json")}, ensure_ascii=False))
