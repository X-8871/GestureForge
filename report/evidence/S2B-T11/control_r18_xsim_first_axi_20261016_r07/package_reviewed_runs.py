"""封存完整CSR矩阵及真实独立复跑；不改原始执行结果。"""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
PARENT = Path(__file__).resolve().parent.parent
RUN_NAMES = ["control_r18_xsim_first_axi_20261016_r07", "control_r18_independent_20261016_r08"]


def sha(path):
    """计算原字节摘要。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


for name in RUN_NAMES:
    run = PARENT / name
    work = ROOT / "tmp/2B/S2B-T11" / name
    result_path = run / "result.json"
    original_path = run / "delivery_manifest.json"
    result_hash, original_hash = sha(result_path), sha(original_path)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == "PASS_RTL_SIMULATION_ONLY"
    for source in result["sources"]:
        path = (run / "preflight/source_snapshot" / Path(source["path"]).name
                if source["path"].startswith(("src/", "sim/")) else
                run / "source_snapshot" / Path(source["path"]).name
                if source["path"].startswith("verification/") else ROOT / source["path"])
        assert path.is_file() and sha(path) == source["sha256"]
    for source_name, target_name in [("tb_s2b_control_csr_behav.wdb", "matrix_waveform.wdb"),
                                     ("xsim.jou", "xsim_native.jou")]:
        source, target = work / source_name, run / target_name
        assert source.is_file() and not target.exists()
        shutil.copy2(source, target)
        assert sha(source) == sha(target)
    receipt = {
        "kind": "controller_record_of_independent_review", "status": "PASS",
        "reviewer_task": "/root/csr_final_review", "model_requested": "gpt-6-luna",
        "reasoning_effort_requested": "high", "recorded_by": "/root",
        "scope": "CSR/TB接口语义及r08独立完整XSim复跑；附加board/README手册输入决定表述",
        "source_sha256": {"src/s2b_control_csr.sv": "4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1",
                          "sim/tb_s2b_control_csr.sv": "04afb9a9d3a154c415b40effb2bf47c955c858d0cf203da20b3a0f170f88112a"},
        "independent_run": RUN_NAMES[1], "driver_exit_code": 0,
        "observed_counts": {"directed": 146, "random": 128, "integration": 25, "cycles": 6362},
        "limitations": ["来自本任务子代理实际返回，由总控转录；不是密码学签名。",
                        "G2及RTL仿真通过不代表硬件G3或阶段2B冻结。"]}
    with (run / "independent_review_receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    manifest = json.loads(original_path.read_text(encoding="utf-8"))
    paths = {row["path"]: ROOT / row["path"] for row in manifest["files"]
             if not row["path"].startswith(("src/", "sim/", "verification/"))}
    target_manifest = run / "delivery_manifest_historical.json"
    assert not target_manifest.exists()
    for path in run.rglob("*"):
        if path.is_file():
            paths[path.relative_to(ROOT).as_posix()] = path
    manifest["files"] = [{"path": key, "sha256": sha(path),
        "role": "input" if run not in path.parents else "source" if path.suffix in {".py", ".sv", ".cmd", ".prj", ".tcl", ".ini"}
        else "artifact" if path.suffix == ".wdb" else "log" if path.suffix in {".log", ".jou", ".raw"} else "result",
        "keep_reason": "保留完整矩阵波形供恢复争议复核。" if path.suffix == ".wdb" else "绑定真实源码快照、运行结果和独立审查来源。"}
        for key, path in sorted(paths.items())]
    manifest["limitations"].append("原清单原字节保留；本补充绑定冻结快照与独审转录，不继承为板上通过。")
    target_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert sha(result_path) == result_hash and sha(original_path) == original_hash
    print(name, sha(target_manifest))
