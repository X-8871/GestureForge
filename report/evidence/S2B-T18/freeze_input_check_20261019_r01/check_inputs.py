"""只读重核对当前正式运行的固定输入；不接触设备或改写活动证据。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess
import sys
import zipfile
import argparse

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CONFIG = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/model_config_r04.json"
PREP = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/preparation_stress_first.json"


def digest(path):
    """按块读取固定文件，避免占用验收进程的内存。"""
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            value.update(block)
    return value.hexdigest()


def refs(value, label):
    """只检查原清单明确列出的路径和哈希，不猜测路径或递归读取历史清单。"""
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            yield label, value
        for key, item in value.items():
            yield from refs(item, label + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from refs(item, label + "[" + str(index) + "]")


def main():
    """生成本次离线检查结果，不把输入完整性当作板上通过。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output = OUT
    if args.output_dir is not None:
        output = args.output_dir.absolute()
        if output.parent.resolve(strict=True) != OUT.parent or output.exists():
            raise RuntimeError("追加运行必须使用同任务下尚不存在的独立目录")
        output.mkdir()
    if (output / "result.json").exists():
        raise RuntimeError("本RunId已有结果，不覆盖重跑")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    records = []
    checked = {}
    failures = []
    documents = [("config", CONFIG), ("preparation", PREP)]
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    build = Path(config["build_details"]["path"]).resolve(strict=True)
    documents.append(("build", build))
    for label, document in documents:
        data = json.loads(document.read_text(encoding="utf-8"))
        for location, item in refs(data, label):
            candidate = Path(item["path"])
            path = candidate if candidate.is_absolute() else ROOT / candidate
            record = {"location": location, "path": str(path), "expected": item["sha256"]}
            try:
                path = path.resolve(strict=True)
                if not path.is_file():
                    raise RuntimeError("绑定目标不是文件")
                key = str(path)
                if key not in checked:
                    checked[key] = {"sha256": digest(path), "bytes": path.stat().st_size}
                record.update(checked[key])
                record["status"] = "PASS" if record["sha256"] == item["sha256"] else "FAIL_HASH"
            except (OSError, RuntimeError) as error:
                record.update(status="FAIL_PATH", error=repr(error))
            records.append(record)
            if record["status"] != "PASS":
                failures.append(record)
    bit = Path(config["bindings"]["bit"]["path"]).resolve(strict=True)
    xsa = Path(config["bindings"]["xsa"]["path"]).resolve(strict=True)
    with zipfile.ZipFile(xsa) as archive:
        names = [name for name in archive.namelist() if name.endswith(".bit")]
        embedded = [{"name": name, "sha256": hashlib.sha256(archive.read(name)).hexdigest()} for name in names]
    embedded_match = len(embedded) == 1 and embedded[0]["sha256"] == digest(bit)
    if not embedded_match:
        failures.append({"status": "FAIL_XSA_EMBEDDED_BIT"})
    result = {"schema_version": 1, "captured_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "source_commit": head, "scope": "FIXED_INPUT_BINDINGS_ONLY_NO_DEVICE_ACCESS",
              "status": "PASS_BOUND_INPUTS_ONLY" if not failures else "FAIL_BOUND_INPUTS",
              "checker": {"path": str(Path(__file__).resolve()), "sha256": digest(Path(__file__))},
              "documents": [{"path": str(path), "sha256": digest(path)} for _, path in documents],
              "checked_bindings": len(records), "unique_files": len(checked),
              "unique_bytes": sum(row["bytes"] for row in checked.values()),
              "bindings": records, "xsa_embedded_bits": embedded,
              "xsa_embedded_bit_matches_deployed_bit": embedded_match, "failures": failures,
              "limitations": ["不读取或固定正在追加的UART和进度文件。", "不代表109、1000、CSR恢复或G4/G5通过。",
                              "仅核对原清单显式路径和SHA，不证明干净重建及语义正确性。"]}
    with (output / "result.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in ("status", "checked_bindings", "unique_files", "unique_bytes", "failures")}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
