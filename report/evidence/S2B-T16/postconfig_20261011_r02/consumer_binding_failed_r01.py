"""补齐跨消费者实际源与SDK文件哈希；只读厂商SDK，不加载其模块。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).absolute().parents[4]
RUN = ROOT / "report/evidence/S2B-T16/postconfig_20261011_r02"
assert RUN.is_dir() and not (RUN / "consumer_binding.json").exists()
paths = ("verification/test_s2b_board_transport.py", "verification/test_s2b_board_acceptance.py",
         "verification/test_s2b_csr_busy_observer.py", "verification/s2b_board_acceptance.py",
         "verification/s2b_csr_busy_observer.py", "vitis/s2b_inference_app.c")
hashes = {}
for name in paths:
    path = ROOT / name
    assert path.is_file()
    target = RUN / "consumer_source_snapshot" / name
    assert not target.exists(); target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert hashlib.sha256(target.read_bytes()).hexdigest() == hashes[name]
spec = importlib.util.spec_from_file_location("s2b_postconfig_entry_readonly", ROOT / "vitis/run_s2b_visibility_probe.py")
entry = importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
sdk = {key: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
       for key, path in entry.sdk_source_closure().items()}
assert len(sdk) == 19
value = {"source_sha256": hashes, "sdk_19_file_closure": sdk, "sdk_module_imported": False,
         "consumer_tests": {"command": "python -B -m unittest verification.test_s2b_board_transport verification.test_s2b_board_acceptance verification.test_s2b_csr_busy_observer -v",
                            "native_exit_code": 0, "test_methods": 81, "elapsed_seconds": 46.729},
         "precheck": {"native_exit_code": 0, "test_methods": 2, "elapsed_seconds": 51.568},
         "previous_full_run": {"run_id": "postconfig_20261011_r01", "native_exit_code": 0, "test_methods": 101, "elapsed_seconds": 533.745,
                               "packaging_native_exit_code": 2, "packaging_status": "FAIL", "reason": "interface.path使用快照而非docs；原件保留，最终r02改正。"},
         "scope": "仅离线消费者mock及现有C native harness；未连接SDK/串口/设备。S5平台源正在变更，非本轮软件消费者闭包。"}
assert not (RUN / Path(__file__).name).exists(); shutil.copyfile(Path(__file__), RUN / Path(__file__).name)
with (RUN / "consumer_binding.json").open("x", encoding="utf-8", newline="\n") as output:
    json.dump(value, output, ensure_ascii=False, indent=2); output.write("\n")
print(json.dumps({"consumer_sources": len(hashes), "sdk_sources": len(sdk), "sdk_module_imported": False}))
