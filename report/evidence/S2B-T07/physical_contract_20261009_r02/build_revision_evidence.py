import argparse
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone


ROOT = pathlib.Path(__file__).resolve().parents[4]
RUN = pathlib.Path(__file__).resolve().parent
REL = RUN.relative_to(ROOT).as_posix()
OLD = ROOT / "report/evidence/S2B-T07/physical_contract_20261009_r01"
BASELINE = "3f6e327a0ff9adc04ed6c98c1578862b8c2fae64"
DOC = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
DESIGN = "docs/obsidian-project/02-方案设计/系统设计.md"
SPEC = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
MODEL = "report/evidence/S2A-T01/tiny416_model_manifest.json"
RECEIPT = "tmp/2B/S2B-T07/review_r01_20261009/review_receipt.json"
RECEIPT_SHA = "ecc1b9fba11399ebf1b1f23fdd7855d6c44cda21f3378576e9a4ceb602f20878"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    # 本Run所有新生成文本均为UTF-8，不覆盖r01原始结果。
    (RUN / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_exact(source, destination):
    if not source.is_file() or not destination.parent.is_dir():
        raise ValueError("复制源类型或精确目标父目录错误")
    with destination.open("xb") as stream:
        stream.write(source.read_bytes())


def compute():
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() != BASELINE:
        raise ValueError("HEAD已变化，停止绑定旧源码基线")
    if sha(ROOT / RECEIPT) != RECEIPT_SHA:
        raise ValueError("R1收据SHA不匹配")
    receipt = json.loads((ROOT / RECEIPT).read_text(encoding="utf-8"))
    if receipt["decision"] != "CHANGES_REQUIRED":
        raise ValueError("未收到真实R1修订依据")
    copy_exact(ROOT / RECEIPT, RUN / "review_receipt_r01.json")
    prior = json.loads((OLD / "source_snapshot_bindings.json").read_text(encoding="utf-8"))
    snapshots = RUN / "snapshots"
    snapshots.mkdir()
    bindings = []
    for item in prior["files"]:
        source = ROOT / item["original_path"]
        if not source.is_file():
            raise ValueError(f"源码原件不存在：{source}")
        if item["original_path"] not in [DOC, DESIGN] and sha(source) != item["sha256"]:
            raise ValueError(f"非本轮修改的静态输入发生变化：{source}")
        destination = snapshots / source.name
        copy_exact(source, destination)
        bindings.append({"original_path": item["original_path"], "snapshot_path": destination.relative_to(ROOT).as_posix(),
                         "sha256": sha(source), "bytes": source.stat().st_size})
    bsp_bindings = []
    for item in prior["external_official_bsp_sources"]:
        source = ROOT / item["snapshot_path"]
        if sha(source) != item["sha256"]:
            raise ValueError("r01官方BSP源码快照已变化")
        destination = snapshots / source.name
        copy_exact(source, destination)
        bsp_bindings.append({**item, "snapshot_path": destination.relative_to(ROOT).as_posix(),
                            "reuse_from": item["snapshot_path"], "reuse_reason": "官方BSP原字节快照复用，无新的外部数据访问"})
    reused = []
    for name in ["layout_result.json", "manifest_layout_projection.json"]:
        source = OLD / name
        expected = sha(source)
        if name == "layout_result.json" and expected != receipt["fixed_reviewed_hashes"][f"{OLD.relative_to(ROOT).as_posix()}/{name}"]:
            raise ValueError("冻结r01尺寸结果不同于R1审查版本")
        copy_exact(source, RUN / name)
        reused.append({"source": source.relative_to(ROOT).as_posix(), "destination": f"{REL}/{name}",
                       "sha256": expected, "bytes": source.stat().st_size,
                       "reason": "只修物理候选语义，冻结模型和地址尺寸不变；原结果按SHA复用，不重跑历史计算"})
    if sha(ROOT / MODEL) != "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a":
        raise ValueError("冻结model manifest原件SHA变化")
    write("source_snapshot_bindings.json", {"source_commit": BASELINE, "files": bindings,
          "external_official_bsp_sources": bsp_bindings, "reused_results": reused})
    top = (ROOT / "src/s2a_stage2a_core_ooc.sv").read_text(encoding="utf-8")
    csr = (ROOT / "src/s2a_control_csr.sv").read_text(encoding="utf-8")
    shell = (ROOT / "src/s2a_runtime_shell.sv").read_text(encoding="utf-8")
    backend = (ROOT / "src/s2a_network_backend.sv").read_text(encoding="utf-8")
    memory = (ROOT / "src/s2a_memory_master.sv").read_text(encoding="utf-8")
    facts = {
        "core_public_interface": "CSR与memory，busy/done/error/backend_abort为内部私有logic",
        "csr_ready_is_not_hard_reset": "csr_ready = !hard_reset;" in csr,
        "soft_reset_clears_diagnostics_and_registers_abort": "backend_abort <= 1'b1;" in csr and "error_code <= NONE;" in csr,
        "memory_cancel_same_edge": "soft_reset_now = csr_valid && csr_ready && csr_write" in shell and "cancel_master = hard_reset || backend_abort || soft_reset_now;" in shell,
        "backend_consumes_registered_abort_next_edge": "end else if (abort) begin" in backend and "state <= ST_IDLE;" in backend,
        "public_mem_valid_withdraws_on_cancel_or_owner_clear": "mem_valid = pending && buffer_owner_pl && !hard_reset && !cancel;" in memory,
    }
    if not all(v for v in facts.values() if isinstance(v, bool)):
        raise ValueError("源代码语义标记与候选观察路径不一致")
    # 仅枚举拟定仲裁的相位算术，不模拟RTL、CSR行为或AXI事务。
    phase_rows = []
    for phase in range(4):
        status_delta = next(n for n in range(1, 5) if (phase + n) % 4 in [0, 3])
        code_delta = next(n for n in range(status_delta + 1, status_delta + 5) if (phase + n) % 4 == 1)
        phase_rows.append({"producer_edge_phase": phase, "status_sample_E_plus": status_delta,
                           "associated_error_code_sample_E_plus": code_delta,
                           "same_edge_read_is_old": True})
    status_bound = max(row["status_sample_E_plus"] for row in phase_rows)
    error_bound = max(row["associated_error_code_sample_E_plus"] for row in phase_rows)
    arm_components = {"first_idle_status_max_cycles": 3, "one_preaccepted_debug_max_cycles": 4,
                      "seven_control_writes_four_cycle_slots_max_cycles": 7 * 4}
    arm_conservative_sum = sum(arm_components.values())
    doc = (ROOT / DOC).read_text(encoding="utf-8")
    lines = doc.splitlines()
    closure_keys = {
        "R1-F01": "AXI3写B不继承AXI4新增的AW接受依赖",
        "R1-F02": "### 4.1 既有端口、常驻CSR监视与停止确认",
        "R1-F03": "### 4.2 首次观察、同沿优先与终态保持",
        "R1-F04": "single beat是驱动与GP0转换配置的输入前提",
        "R1-F05": "01/EXOKAY",
        "R1-F06": "132页仅为元数据",
    }
    closures = []
    for finding, key in closure_keys.items():
        location = next((i + 1 for i, line in enumerate(lines) if key in line), None)
        if location is None:
            raise ValueError(f"缺失候选修订：{finding}")
        closures.append({"finding_id": finding, "candidate_path": DOC, "line": location,
                         "developer_status": "IMPLEMENTED_IN_CANDIDATE_PENDING_INDEPENDENT_R2", "locating_text": key})
    write("candidate_revision_result.json", {
        "status": "READ_ONLY_SOURCE_AND_FORMULA_ANALYSIS_COMPLETE_NOT_RTL_VERIFICATION",
        "source_commit": BASELINE, "candidate_version": "s2b-physical-candidate/0.1.1",
        "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "review_receipt_sha256": RECEIPT_SHA, "closed_in_candidate_pending_review": closures,
        "source_facts": facts, "csr_phase_formula": {
            "schedule": {"0": "STATUS", "1": "ERROR_CODE", "2": "CONTROL_OR_ONE_DEBUG", "3": "STATUS"},
            "producer_consumer_rows": phase_rows, "status_bound_cycles": status_bound,
            "associated_error_code_bound_cycles": error_bound,
            "first_observed_error_source_reserved_before_code": True,
            "first_error_pending_blocks_terminal_and_safe": True,
            "arming_components": arm_components, "arming_conservative_sum_cycles": arm_conservative_sum,
            "candidate_arming_limit_cycles": 40,
            "arming_sum_within_candidate_limit": arm_conservative_sum <= 40,
            "soft_reset_edge": "S=phase2真实CMD握手；control诊断清零/backend_abort NBA置1",
            "backend_abort_consumption_edge": "S+1=phase3，后端与算子在该沿消费abort，STATUS读虽见CSR零仍不能据此提前确认后端已经停止",
            "earliest_eligible_stop_confirmation_edge": "S+2=phase0：此时后端S+1的NBA已完成，真实CSR STATUS四状态位0且mem_valid0",
            "conservative_reset_to_confirmation_bound_cycles": 5,
            "not_hardware_measurement": True,
        }, "protocol_decisions": {
            "axi3_early_matching_B": "已声明写且W完成、BID匹配即可保存B；AW未完成单独不报错，AW/W/B完整闭合才交付或清账",
            "first_error_same_edge_priority": ["AXI_PROTOCOL", "AXI_SLVERR_OR_DECERR", "EXTERNAL_ABORT", "OBSERVED_CORE_ERROR", "OBSERVED_SUCCESS"],
            "cancel_edge_OKAY": "握手仍入账，只消费丢弃，不mem_ready/done/HEAD_VALID或新子读",
            "new_write_declaration": "初次同沿置AWVALID/WVALID，握手独立；已有VALID不能被取消撤销",
            "GP0_single_beat": "驱动输入前提；Lite没有AxLEN，不能宣称原burst被拒绝或零副作用",
            "nonexclusive_EXOKAY": "协议隔离；保存响应/继续已声明通道，不能误成功或凭空清ledger",
        }, "reused_layout": reused,
        "limitations": ["没有RTL/软件测试、构建、综合或硬件动作", "源标记与相位公式仅证明给定候选可静态实现，不是实现结果", "完整物理G0、独立R2、实际deadline/GP0配置/可见性仍未完成", "保留109冻结样本及正式100/1000板上标准，不降低指标"]})
    print(json.dumps({"read_only_formula_analysis": "COMPLETE", "status_bound_cycles": status_bound,
        "error_code_bound_cycles": error_bound, "arming_sum_cycles": arm_conservative_sum,
        "prior_layout_recalculation_count": 0, "candidate_revision_count": len(closures)}, ensure_ascii=False))


def manifest():
    binding = json.loads((RUN / "source_snapshot_bindings.json").read_text(encoding="utf-8"))
    checks = []
    for name in ["analysis_execution.json", "diff_execution.json", "packaging_execution.json"]:
        if (RUN / name).exists():
            item = json.loads((RUN / name).read_text(encoding="utf-8"))
            checks.append({"name": item["name"], "status": "PASS" if item["exit_code"] == 0 else "FAIL", "command": item["command"], "exit_code": item["exit_code"], "reason": item["scope"]})
    for name, status, reason in [
        ("完整物理G0冻结", "BLOCKED", "GP0实际转换/single-beat输入前提、CSR实现/集成、arena/cache、deadline及可见性仍未完成"),
        ("R2独立复审", "NOT_RUN", "D2停止写入后由总控派独立Reviewer，不能据修订自述关闭G2"),
        ("RTL和软件验证", "NOT_RUN", "本次只读源码与相位公式，不实现或运行功能测试"),
        ("实物100样本与1000连续任务", "NOT_RUN", "本次不操作实物，不将串口枚举当功能验收"),
    ]:
        checks.append({"name": name, "status": status, "command": None, "exit_code": None, "reason": reason})
    files = [{"path": item["original_path"], "sha256": sha(ROOT / item["original_path"]), "role": "source"} for item in binding["files"]]
    files.append({"path": MODEL, "sha256": sha(ROOT / MODEL), "role": "input"})
    for path in sorted(RUN.rglob("*")):
        if path.is_file() and path.name != "delivery_manifest.json":
            role = "source" if path.suffix in [".py", ".sv", ".md", ".c"] else "log" if path.name.endswith("console.txt") else "result"
            files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role})
    write("delivery_manifest.json", {
        "schema_version": 1, "stage": "2B", "task_id": "S2B-T07", "run_id": RUN.name,
        "source_commit": BASELINE, "evidence_dir": REL,
        "interfaces": [
            {"name": "已冻结2A模型/CSR/单word memory", "version": "2026-09-23", "frozen": True, "path": SPEC, "sha256": sha(ROOT / SPEC)},
            {"name": "已批准恢复原则，完整物理接口不在其冻结范围", "version": "s2b-axi-recovery-principles/1.0.0", "frozen": True, "path": DESIGN, "sha256": sha(ROOT / DESIGN)},
            {"name": "R1修订的物理接口候选，尚未冻结", "version": "s2b-physical-candidate/0.1.1", "frozen": False, "path": DOC, "sha256": sha(ROOT / DOC)},
        ], "files": files, "checks": checks,
        "tool_versions": {"python": platform.python_version(), "git": subprocess.check_output(["git", "--version"], text=True).strip()},
        "limitations": ["r01尺寸/投影按SHA原字节复用，历史尺寸计算重跑次数0", "R1 CHANGES_REQUIRED收据绑定六项候选修订，R2尚未执行", "只读源码/公式/包装，不是RTL或软件测试，不改实现不操作硬件", "完整物理G0/G3/G4/G5仍未通过；包装CHECKS_OK不能覆盖", "原r01证据及失败完整保留；0.1.0由0.1.1候选替代不改写旧Run", "提交由总控负责，Developer不提交", "峰值内存和全部工具调用未测"]})


def run():
    command = [sys.executable, "-B", str(pathlib.Path(__file__).resolve()), "--mode", "compute"]
    start = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, env=ENV)
    (RUN / "analysis_console.txt").write_bytes(result.stdout + result.stderr)
    write("analysis_execution.json", {"name": "源码/四相位时序只读核查与r01原字节复用", "command": f"PYTHONIOENCODING=utf-8 python -B {REL}/build_revision_evidence.py --mode compute", "argv": command,
        "exit_code": result.returncode, "elapsed_seconds": time.perf_counter() - start,
        "scope": "未模拟RTL或AXI；只核对源码标记、相位算术、SHA及文档快照", "historical_layout_recalculation_count": 0})
    if result.returncode:
        print((result.stdout + result.stderr).decode("utf-8"))
        raise SystemExit(result.returncode)
    command = ["git", "diff", "--check", "--", DOC, DESIGN]
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    (RUN / "diff_console.txt").write_bytes(result.stdout + result.stderr)
    write("diff_execution.json", {"name": "两份修订候选差异空白核查", "command": f"git diff --check -- {DOC} {DESIGN}", "argv": command, "exit_code": result.returncode, "scope": "仅核对本轮允许修改的两份候选文档"})
    manifest()
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", f"{REL}/delivery_manifest.json"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, env=ENV)
    (RUN / "packaging_console.txt").write_bytes(result.stdout + result.stderr)
    write("packaging_execution.json", {"name": "R02修订证据包装核查", "command": f"PYTHONIOENCODING=utf-8 python -B verification/check_stage_delivery.py --mode evidence --manifest {REL}/delivery_manifest.json", "argv": command, "exit_code": result.returncode,
        "scope": "仅哈希/目录清单，日志随后加入清单并由总控核查最终版本；不证明接口语义/G0/G2或实物"})
    manifest()
    print((RUN / "analysis_console.txt").read_text(encoding="utf-8"))
    print(json.dumps({"packaging_exit_code": result.returncode}))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["compute", "run", "manifest"], required=True)
    mode = parser.parse_args().mode
    {"compute": compute, "run": run, "manifest": manifest}[mode]()
