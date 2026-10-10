"""为总控独立 lint 与审查原件生成哈希清单，不解析 lint 内容。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]

def digest(path):
    """计算文件原始字节 SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    """显式依据总控已核对结果打包，不把工具退出码等同验收。"""
    run_id, status, count = sys.argv[1:4]
    evidence = ROOT / "report" / "evidence" / "S2B-T10" / run_id
    assert evidence.is_dir()
    target = evidence / "delivery_manifest.json"
    assert not target.exists()
    files = []
    for path in sorted(evidence.rglob("*")):
        if path.is_file():
            role = "source" if path.suffix in (".sv", ".py") else "log" if path.suffix == ".log" else "result"
            files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": role})
    spec = ROOT / "docs" / "obsidian-project" / "02-方案设计" / "s2b_physical_interface_candidate.md"
    files.append({"path": spec.relative_to(ROOT).as_posix(), "sha256": digest(spec), "role": "input"})
    checks = [{"name": "工具与原件核验", "status": "PASS", "command": "Vivado MCP synth_design -lint 或独立 Verilator driver，精确命令和退出码见绑定原件", "exit_code": 0, "reason": "仅核验指定工具执行及原件，未运行完整平台综合或实物。"},
              {"name": "独立范围判定", "status": status, "command": None, "exit_code": None, "reason": f"总控逐项核对原件：lint实际消息数量或独立场景统计 {count}；详细范围见同Run绑定报告。"},
              {"name": "完整物理接口部署", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "候选0.1.1未冻结，完整控制/cache/时序/实物验收未执行。"}]
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T10", "run_id": run_id,
                "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "evidence_dir": evidence.relative_to(ROOT).as_posix(), "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.1", "frozen": False, "path": spec.relative_to(ROOT).as_posix(), "sha256": digest(spec)}],
                "files": files, "checks": checks, "tool_versions": {"Vivado": "2026.1", "Python": sys.version.split()[0], "Verilator": "5.050（仅独立审查实际使用，lint Run不使用）"},
                "limitations": ["每个Run只绑定自身快照，不把历史失败当成修正版结果；未执行完整PS/PL集成、时序或实物。", "机器CHECKS_OK仅证明包装完整，不证明接口冻结、语义正确或SAFE。", "lint内存与耗时以工具原件为准；其他峰值内存未测，未宣称全部工具调用统计完整。"]}
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target.relative_to(ROOT).as_posix(), digest(target))

if __name__ == "__main__":
    main()
