"""运行真实批准绑定核验并生成离线冻结证据清单，拒绝覆盖。"""

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")


def main():
    root = Path.cwd()
    base = root / "report/evidence/S2B-T06/ps_smoke_offline_freeze_20261009_r01"
    destination = base / "delivery_manifest.json"
    if destination.exists():
        raise RuntimeError("冻结清单目标已存在")
    command = [sys.executable, "-X", "utf8", "-B", str(base / "verify_freeze.py")]
    started = time.perf_counter()
    result = subprocess.run(command, cwd=root, capture_output=True)
    log = base / "root_binding_check.log"
    with log.open("xb") as output:
        output.write(result.stdout + result.stderr)
    execution = {"command": command, "cwd": str(root), "exit_code": result.returncode,
                 "elapsed_seconds": time.perf_counter()-started,
                 "log": log.relative_to(root).as_posix(), "log_sha256": sha(log),
                 "hardware_execution": "NOT_RUN"}
    new_json(base / "root_binding_execution.json", execution)
    if result.returncode:
        raise RuntimeError(f"冻结核验失败：{result.returncode}")
    approval = json.loads((base / "acceptance.json").read_text(encoding="utf-8"))
    old = json.loads((root / approval["developer_manifest"]["path"]).read_text(encoding="utf-8"))
    upstream = json.loads((root / "report/evidence/S2B-T06/ps_smoke_20261008_r01/inputs_manifest_r03.json").read_text(encoding="utf-8"))
    rows = {}
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        role = "log" if path.suffix == ".log" else "artifact" if path.suffix in (".elf", ".map") else "diagnostic"
        row = {"path": relative, "sha256": sha(path), "role": role}
        if path.suffix == ".elf":
            row["keep_reason"] = "独立真实重建或实际ELF反例的原始证据；人工下载只使用Developer固定build_08产物。"
        rows[relative] = row
    for relative in approval["source_sha256"]:
        rows[relative] = {"path": relative, "sha256": sha(root / relative), "role": "source"}
    inputs = [approval["developer_manifest"]["path"],
              "report/evidence/S2B-T06/ps_smoke_20261008_r01/inputs_manifest_r03.json",
              "verification/check_stage_delivery.py", approval["formal_record"]["path"]]
    inputs += [item["path"] for item in upstream["files"]]
    for relative in inputs:
        rows[relative] = {"path": relative, "sha256": sha(root / relative), "role": "input"}
    own_interface = {"name": "PS前置检查软件及人工步骤的离线候选", "version": "s2b-ps-smoke/1.0.0",
                     "frozen": True, **approval["formal_record"]}
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T06",
                "run_id": base.name, "source_commit": approval["baseline_commit"],
                "evidence_dir": base.relative_to(root).as_posix(),
                "interfaces": upstream["interfaces"] + [own_interface],
                "files": [rows[key] for key in sorted(rows)],
                "checks": [{"name": "总控离线批准与源产物审查复制绑定核验", "status": "PASS",
                            "command": subprocess.list2cmdline(command), "exit_code": result.returncode,
                            "reason": "实际机器命令只核对绑定与批准范围；独立G2人工结论另由原收据和正式记录绑定。"},
                           {"name": "实板PS初始化UART和DDR前置检查", "status": "NOT_RUN",
                            "command": None, "exit_code": None,
                            "reason": "本轮仅准备离线候选；板卡实际独占及运行结果尚未取得。"}],
                "tool_versions": {**old["tool_versions"], "Root Python": sys.version.split()[0]},
                "limitations": approval["limits"]}
    new_json(destination, manifest)
    print(json.dumps({"status": "SEALED_OFFLINE_BINDING_MANIFEST", "files": len(rows),
                      "manifest_sha256": sha(destination), "acceptance_sha256": sha(base/"acceptance.json"),
                      "formal_record_sha256": approval["formal_record"]["sha256"],
                      "root_binding_exit_code": result.returncode, "hardware_execution": "NOT_RUN"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
