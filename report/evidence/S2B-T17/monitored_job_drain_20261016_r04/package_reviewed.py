"""绑定独立审查原件与冻结源码，不改原始开发运行清单。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent


def sha(path):
    """按原字节计算哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(RUN / "delivery_manifest.json") == "5a5c0aef1c5b356efab807128aa335a00b49261ae8dd634dd57b10aa460fe533"
manifest = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
for entry in manifest["files"]:
    actual = ROOT / entry["path"]
    assert actual.is_file() and sha(actual) == entry["sha256"], entry["path"]
for name in ("unittest", "review_attacks"):
    assert (RUN / "independent_review" / (name + ".exit_code.txt")).read_text(encoding="utf-8-sig").strip() == "0"
paths = [path for path in RUN.rglob("*") if path.is_file() and path != RUN / "delivery_manifest_reviewed.json"]
manifest["files"] = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
                      "role": "source" if path.suffix == ".py" else "log" if path.suffix in (".log", ".txt") else "result",
                      "keep_reason": "保留实际微型回归、独立审查输出、攻击脚本及冻结源码；不作为硬件证据。"}
                     for path in sorted(paths)]
manifest["checks"] = [check for check in manifest["checks"] if check["name"] != "independent_review"]
manifest["checks"].extend([
    {"name": "independent_supervisor_21_tests", "status": "PASS", "exit_code": 0,
     "command": r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -m unittest verification.test_s2b_process_supervisor -v",
     "reason": "独立Reviewer复跑21项退出0；原始stdout/stderr与退出码已保存。"},
    {"name": "independent_resource_boundary_attacks", "status": "PASS", "exit_code": 0,
     "command": r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\FPGA_Competition\w2b\tmp\2B\S2B-T17\review_abe095e_r02\review_attacks.py",
     "reason": "独立配置越界/精确边界与慢终态wall deadline夹具检查退出0。"}])
manifest["limitations"].append("本补充清单只用冻结快照绑定历史源码；原始Developer清单中等待审查为当时状态，最终独审见回执。")
(RUN / "delivery_manifest_reviewed.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
