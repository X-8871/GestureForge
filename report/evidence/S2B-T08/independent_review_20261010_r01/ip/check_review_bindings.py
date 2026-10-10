"""独立核对当前被审文件与清单绑定，并保存审查输入哈希。"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[4]
manifest_path = root / "report/evidence/S2B-T08/ip_probe_20261009_r01/delivery_manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
actual = []
for item in manifest["files"] + manifest["interfaces"]:
    file_path = root / item["path"]
    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    if digest != item["sha256"]:
        raise RuntimeError(f"文件哈希不符：{item['path']}")
    actual.append({"path": item["path"], "sha256": digest})
output = {
    "status": "PASS",
    "source_commit": manifest["source_commit"],
    "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    "file_count": len(manifest["files"]),
    "interface_count": len(manifest["interfaces"]),
    "bindings": actual,
}
Path(__file__).with_name("reviewed_bindings.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"PASS files={output['file_count']} interfaces={output['interface_count']}")
