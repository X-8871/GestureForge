"""真实源码code object搭配错误定义模块的fake接收器反例，不导入SDK。"""
from pathlib import Path
import sys
import types
import json
import hashlib
from unittest.mock import patch

folder = Path(__file__).parent
root = folder.parents[3]
sys.path.insert(0, str(root))
from verification.test_s2b_visibility_probe import p, bind

files = {name: bind(file) for name, file in p.sdk_source_closure().items()}
methods = {"xsdb": ("start_debug_session", "dispose"),
           "xsdb.xsdb_debug_session": ("xsdb_start_debug_session", "dispose_session"),
           "xsdb.session": ("Session.__init__", "Session.connect", "Session.disconnect", "Session.targets"),
           "xsdb.target": ("Target.__init__", "Target.state", "Target.stop", "Target.con", "Target.dow", "Target.bpadd", "Target.mrd", "Target.mwr", "Target.rst", "Target.fpga", "Target.rrd"),
           "xsdb._tcf_reset": ("TcfReset.rst_cmd", "TcfReset.rst_capabilities"),
           "xsdb._breakpoint": ("Breakpoint.remove", "Breakpoint.status")}
modules = {name: types.ModuleType(name) for name in methods}
def find(code, qualname):
    """仅从原源码读取方法code，不执行其函数。"""
    if code.co_qualname == qualname:
        return code
    for child in code.co_consts:
        if isinstance(child, types.CodeType):
            found = find(child, qualname)
            if found is not None:
                return found
for name, module in modules.items():
    module.__file__ = files[name]["path"]
    compiled = compile(Path(module.__file__).read_text(encoding="utf-8-sig"), module.__file__, "exec", dont_inherit=True)
    for method in methods[name]:
        pieces = method.split(".")
        target = module
        if len(pieces) == 2:
            if not hasattr(module, pieces[0]):
                setattr(module, pieces[0], type(pieces[0], (), {"__module__": name}))
            target = getattr(module, pieces[0])
        setattr(target, pieces[-1], types.FunctionType(find(compiled, method), {"__name__": name}))
modules["xsdb"].debug_session = None
modules["xsdb.xsdb_debug_session"].debug_session_int_obj = None
config = {"sdk_files": files}
rows = []
with patch.dict(sys.modules, modules):
    p.verify_runtime_sources(config)
    rows.append({"label": "canonical_method_mock_baseline", "status": "ACCEPTED"})
    session_cls = modules["xsdb.session"].Session
    session_cls.__module__ = "review_wrong_receiver_source"
    modules["xsdb.xsdb_debug_session"].Session = session_cls
    p.verify_runtime_sources(config)
    rows.append({"label": "wrong_class_origin_before_start", "status": "ACCEPTED", "session_class_module": session_cls.__module__})
    session = object.__new__(session_cls)
    modules["xsdb"].debug_session = session
    modules["xsdb.xsdb_debug_session"].debug_session_int_obj = session
    p.verify_runtime_sources(config, session)
    rows.append({"label": "wrong_session_class_origin_with_mock_receiver", "status": "ACCEPTED", "session_class_module": type(session).__module__})
    target_cls = modules["xsdb.target"].Target
    target_cls.__module__ = "review_wrong_target_source"
    target = object.__new__(target_cls)
    p.verify_runtime_sources(config, session, target)
    rows.append({"label": "wrong_target_class_origin_with_mock_receiver", "status": "ACCEPTED", "target_class_module": type(target).__module__})
assert "xsdb" not in sys.modules and "serial" not in sys.modules
record = {"hardware_execution": "NOT_RUN", "scope": "FAKE_CLASSES_WITH_UNEXECUTED_OFFICIAL_METHOD_CODE", "rows": rows, "native_exit_code": 0}
with (folder/"class_origin_counterexample.json").open("x", encoding="utf-8") as output:
    json.dump(record, output, ensure_ascii=False, indent=2)
print(json.dumps(record, ensure_ascii=False))
