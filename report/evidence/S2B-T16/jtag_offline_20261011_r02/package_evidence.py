"""生成本轮证据绑定清单；只读项目源，创建新清单，不操作硬件。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).absolute().parents[4]
RUN = Path(__file__).absolute().parent
result = json.loads((RUN / "validation_result.json").read_text(encoding="utf-8"))
interface_path = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
files = []
for path in sorted(RUN.iterdir()):
    if path.is_file():
        files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "role": "log" if path.suffix == ".log" else ("source" if path.suffix == ".py" else "result")})
for relative, digest in result["source_sha256"].items():
    if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
        raise RuntimeError("源文件自回归后发生漂移：" + relative)
    files.append({"path": relative, "sha256": digest, "role": "source" if relative.startswith("verification/") else "input"})
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN.name,
            "source_commit": result["source_commit"], "evidence_dir": RUN.relative_to(ROOT).as_posix(),
            "interfaces": [{"name": "PS/PL候选CSR与缓存所有权接口", "version": "s2b-physical-candidate/0.1.1",
                            "frozen": False, "path": interface_path, "sha256": result["source_sha256"][interface_path]}],
            "files": files, "tool_versions": {"Python": result["python_version"], "XSDB-source": "Vitis 2026.1 local SDK source inspection"},
            "checks": [{"name": "离线mock SDK回归44项", "status": "PASS", "command": "python -B -m unittest verification.test_s2b_board_jtag -v", "exit_code": result["native_exit_code"]},
                       {"name": "实板部署缓存与CSR验证", "status": "NOT_RUN", "command": None, "exit_code": None,
                        "reason": "本Developer任务禁止操作硬件，由总控固定独立G2后执行。"},
                       {"name": "独立审查", "status": "NOT_RUN", "command": None, "exit_code": None,
                        "reason": "Developer已交付本轮源码与44项证据，独立Reviewer尚未执行。"}],
            "limitations": ["只交付可审查API，不声称G2/G3/G4/G5完成。", "候选接口未冻结，inputs模式仍受阻。",
                            "初次33项失败未保存独立完整原生日志，本轮保留会话工具输出的明确摘要；r01原件保留。",
                            "SDK通用DAP异常无法证明SLVERR；峰值内存未测。"]}
with (RUN / "delivery_manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2); stream.write("\n")
