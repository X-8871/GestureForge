"""独立补充边界反例，仅使用fake与原字节，不导入SDK或串口。"""
from pathlib import Path
import sys
import tempfile
import json
import hashlib
import copy
import ast
import argparse
import types
import time
from unittest.mock import patch

folder = Path(__file__).parent
root = folder.parents[3]
sys.path.insert(0, str(root))
from verification import test_s2b_visibility_probe as suite
p = suite.p
started = time.monotonic()
rows = []
original_mkdtemp = tempfile.mkdtemp

def isolated_mkdtemp(*args, **kwargs):
    """覆盖既有fixture明确指定的父目录，避免写出审查授权目录。"""
    kwargs["dir"] = folder
    return original_mkdtemp(*args, **kwargs)

with patch.object(tempfile, "mkdtemp", side_effect=isolated_mkdtemp):
    case = suite.PreflightTests()
    case.setUp()
    try:
        for label, original in (("compat_review", case.receipt_path), ("build_details", case.build_path), ("owned_hw_server_identity", Path(case.cfg["owned_hw_server_identity"]["path"]))):
            for index, raw in enumerate((b'{"array":[{"nested":{"status":"FAIL","status":"PASS"}}]}', b'{"array":[{"nested":{"v":-Infinity}}]}', b'{"array":[{"schema_version":1.0}]}')):
                file = case.directory / (label+"_independent_"+str(index)+".json")
                file.write_bytes(raw)
                case.cfg[label] = suite.bind(file)
                try:
                    case.check()
                    raise AssertionError("无效输入被接受")
                except p.VisibilityProbeError as error:
                    rows.append({"label": label, "raw": raw.decode(), "status": "REJECTED", "error": repr(error)})
            case.cfg[label] = suite.bind(original)
        manifest = copy.deepcopy(case.receipt)
        file = case.directory / "manifest_independent_nested.json"
        raw = b'{"schema_version":1,"checks":[{"status":"PASS","metadata":{"k":1,"k":2}}]}'
        file.write_bytes(raw)
        manifest["artifacts"]["platform_manifest"] = suite.bind(file)
        receipt = case.directory / "receipt_independent_nested.json"
        suite.write(receipt, manifest)
        case.cfg["compat_review"] = suite.bind(receipt)
        try:
            case.check()
            raise AssertionError("嵌套manifest重复键被接受")
        except p.VisibilityProbeError as error:
            rows.append({"label": "platform_manifest", "status": "REJECTED", "error": repr(error)})
    finally:
        case.tearDown()
    case = suite.LifecycleTests()
    case.setUp()
    original_runtime = case.runtime
    def early_failure(config):
        """同时制造串口打开与自有session清理失败，保留主错误。"""
        sdk, serial = original_runtime(config)
        sdk.dispose = lambda: (_ for _ in ()).throw(RuntimeError("REVIEW_SECONDARY_DISPOSE"))
        return sdk, serial
    case.runtime = early_failure
    result = case.execute("serial_open")
    assert "mock serial open failure" in result["error"]
    assert any("REVIEW_SECONDARY_DISPOSE" in row["error"] for row in result["cleanup_errors"])
    assert result["serial_closed"] is True
    rows.append({"label": "early_uart_and_cleanup_failure", "status": "PRIMARY_AND_SECONDARY_PRESERVED", "result_path": str(Path(case.config["run_dir"])/"visibility_probe_result.json")})

source = p.SDK_INIT.parent / "session.py"
tree = ast.parse(source.read_text(encoding="utf-8"))
cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == "Session")
connect = copy.deepcopy(next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == "connect"))
connect.decorator_list = []
fake = ast.parse('class Session:\n def __init__(self):\n  self.__channel_map={}\n  self.launches=[]\n def __launch_server(self,server,url):\n  self.launches.append((server,url))\n  raise RuntimeError("REVIEW_FAKE_LAUNCH")\n').body[0]
fake.body.append(connect)
def failed_tcf(url):
    """模拟身份检查之后服务退出，完全禁止真实TCF调用。"""
    raise RuntimeError("REVIEW_SERVER_DISAPPEARED_AFTER_PREIDENTITY")
namespace = {"argparse": argparse, "check_int": int, "tcf": types.SimpleNamespace(connect=failed_tcf)}
exec(compile(ast.fix_missing_locations(ast.Module(body=[fake], type_ignores=[])), str(source), "exec"), namespace)
for url, count in (("TCP:127.0.0.1:3121", 1), ("TCP:localhost:3121", 0)):
    session = namespace["Session"]()
    try:
        session.connect(url=url, server="hw_server")
        raise AssertionError("连接失败未抛出")
    except RuntimeError:
        pass
    except Exception:
        pass
    assert len(session.launches) == count
    rows.append({"label": "official_ast_connect_mock", "url": url, "launch_count": len(session.launches), "expected_count": count})

closure = json.loads((root / "report/evidence/S2B-T19/offline_probe_fix_20261011_r01/sdk_source_closure.json").read_text(encoding="utf-8"))["modules"]
actual = p.sdk_source_closure()
assert set(closure) == set(actual)
for name, file in actual.items():
    assert str(file) == closure[name]["path"]
    assert hashlib.sha256(file.read_bytes()).hexdigest() == closure[name]["sha256"]
remote = p.SDK_INIT.parent.parent / "tcf/services/remote"
proxies = ["tcf.services.remote."+file.stem for file in remote.glob("*Proxy.py")]
assert all(name in closure for name in proxies)
rows.append({"label": "closure_actual_disk_hashes_and_dynamic_proxies", "modules": len(actual), "bytes": sum(f.stat().st_size for f in actual.values()), "proxy_count": len(proxies), "status": "MATCH_DISK_NOT_RUNTIME"})
manifest = json.loads((root / "report/evidence/S2B-T19/offline_probe_fix_20261011_r01/delivery_manifest.json").read_text(encoding="utf-8"))
for item in manifest["files"]:
    file = root/item["path"]
    assert hashlib.sha256(file.read_bytes()).hexdigest() == item["sha256"], item
rows.append({"label": "final_manifest_all_bound_files", "count": len(manifest["files"]), "status": "MATCH"})
assert "xsdb" not in sys.modules and "serial" not in sys.modules
record = {"native_exit_code": 0, "hardware_execution": "NOT_RUN", "rows": rows, "elapsed_seconds": time.monotonic()-started}
with (folder/"adversarial_result.json").open("x", encoding="utf-8") as output:
    json.dump(record, output, ensure_ascii=False, indent=2)
print(json.dumps(record, ensure_ascii=False))
