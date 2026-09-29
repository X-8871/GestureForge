from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path


ROOT = Path(r"D:\FPGA_Competition")
RUN_ROOT = ROOT / r"report\evidence\S2A-T57\run07"
RUNNER_PATH = ROOT / r"verification\test_s2a_conv_layer35_row21_all_channels_rtl.py"
PREPARE_PATH = RUN_ROOT / "prepare_summary.json"
FIXTURE_MANIFEST_PATH = RUN_ROOT / "fixture" / "fixture_manifest.json"


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 根节点不是对象：{path}")
    return value


def replace_json(path: Path, value: dict[str, object]) -> None:
    temporary = path.with_name(path.name + ".r7tmp")
    if temporary.exists():
        raise FileExistsError(temporary)
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with temporary.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


if RUN_ROOT.resolve() != Path(r"D:\FPGA_Competition\report\evidence\S2A-T57\run07"):
    raise RuntimeError(f"run07 路径不匹配：{RUN_ROOT.resolve()}")
if not RUN_ROOT.is_dir() or not PREPARE_PATH.is_file() or not FIXTURE_MANIFEST_PATH.is_file():
    raise FileNotFoundError("run07 prepare-only 证据不完整")

spec = importlib.util.spec_from_file_location("t57_r7_runner", RUNNER_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"无法加载 runner：{RUNNER_PATH}")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
source_hashes = runner._source_hashes()

prepare = read_json(PREPARE_PATH)
fixture_manifest = read_json(FIXTURE_MANIFEST_PATH)
if prepare.get("baseline_head") != "7b8bad78a456310d2ca797a02e3a5a7f873f9c18":
    raise RuntimeError("prepare summary 的基线提交不匹配")
if fixture_manifest.get("baseline_head") != prepare.get("baseline_head"):
    raise RuntimeError("fixture manifest 的基线提交不匹配")

fixture_records_before = fixture_manifest.get("files")
if not isinstance(fixture_records_before, dict):
    raise TypeError("fixture manifest 的文件记录格式错误")
for name, record in fixture_records_before.items():
    if not isinstance(record, dict):
        raise TypeError(f"fixture 记录格式错误：{name}")
    path = Path(str(record.get("path", "")))
    if not path.is_file() or path.stat().st_size != int(record.get("bytes", -1)):
        raise RuntimeError(f"fixture 路径或字节数不匹配：{name}")
    if sha_file(path) != str(record.get("sha256", "")).lower():
        raise RuntimeError(f"fixture SHA-256 不匹配：{name}")

bindings = prepare.get("bindings")
if not isinstance(bindings, dict):
    raise TypeError("prepare summary 缺少 bindings")
bindings["T57_source_hashes"] = source_hashes
fixture_manifest["T57_source_hashes"] = source_hashes
fixture_manifest["runner_source_sha256"] = source_hashes[runner.T57_RUNNER_RELATIVE]
replace_json(FIXTURE_MANIFEST_PATH, fixture_manifest)

manifest_bytes = FIXTURE_MANIFEST_PATH.stat().st_size
prepare_fixture = prepare.get("fixture")
if not isinstance(prepare_fixture, dict):
    raise TypeError("prepare summary 缺少 fixture")
prepare_fixture["manifest"] = {
    "path": str(FIXTURE_MANIFEST_PATH.resolve()),
    "bytes": manifest_bytes,
    "sha256": sha_file(FIXTURE_MANIFEST_PATH),
}
replace_json(PREPARE_PATH, prepare)

updated_prepare = read_json(PREPARE_PATH)
updated_manifest = read_json(FIXTURE_MANIFEST_PATH)
if updated_prepare["bindings"]["T57_source_hashes"] != source_hashes:
    raise RuntimeError("prepare summary 源码绑定刷新失败")
if updated_manifest["T57_source_hashes"] != source_hashes:
    raise RuntimeError("fixture manifest 源码绑定刷新失败")
if updated_manifest["files"] != fixture_records_before:
    raise RuntimeError("fixture 文件记录在绑定刷新期间发生变化")
print(json.dumps({
    "status": "PASS_SOURCE_BINDINGS_REFRESHED",
    "runner_sha256": source_hashes[runner.T57_RUNNER_RELATIVE],
    "source_file_count": len(source_hashes),
    "fixture_file_count": len(fixture_records_before),
    "fixture_records_unchanged": True,
    "prepare_sha256": sha_file(PREPARE_PATH),
    "fixture_manifest_sha256": sha_file(FIXTURE_MANIFEST_PATH),
}, ensure_ascii=False, indent=2))
