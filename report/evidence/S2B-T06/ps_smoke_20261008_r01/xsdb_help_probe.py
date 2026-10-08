"""只导入本机Python XSDB并读取帮助，不创建调试会话或访问硬件。"""

import contextlib
import hashlib
import inspect
import io
import json
from pathlib import Path

import xsdb
from xsdb import xsdb_debug_session
from xsdb.session import Session
from xsdb.target import Target


assert xsdb.debug_session is None
assert xsdb_debug_session.debug_session_int_obj is None
methods = []
for method in (xsdb.start_debug_session, xsdb.dispose, xsdb.help,
               Session.connect, Session.disconnect, Session.targets,
               Target.stop, Target.rst, Target.dow, Target.con,
               Target.init_ps, Target.mrd, Target.loadhw):
    source = Path(inspect.getsourcefile(method))
    methods.append({"name": method.__qualname__, "signature": str(inspect.signature(method)),
                    "doc": inspect.getdoc(method), "source_path": str(source),
                    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
help_texts = {}
for name in ("usage", "connect", "disconnect", "targets", "stop", "rst", "dow", "con", "mrd", "init_ps", "loadhw"):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        xsdb.help(name)
    help_texts[name] = output.getvalue()
assert xsdb.debug_session is None
assert xsdb_debug_session.debug_session_int_obj is None
data = {"schema_version": 1, "status": "PASS_READ_ONLY_PYTHON_XSDB_HELP",
        "hardware_execution": "NOT_RUN", "debug_session_created": False,
        "connected": False, "targets_enumerated": False,
        "methods": methods, "actual_help_output": help_texts}
target = Path(__file__).parent / "xsdb_help_probe.json"
assert not target.exists()
with target.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(data, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print("PASS_READ_ONLY_PYTHON_XSDB_HELP debug_session_created=False hardware_execution=NOT_RUN")
