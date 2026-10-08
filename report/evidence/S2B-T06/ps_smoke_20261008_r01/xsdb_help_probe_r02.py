"""只读确认断点、停驻状态和PC检查的实际API，不创建调试会话。"""

import contextlib
import hashlib
import inspect
import io
import json
from pathlib import Path

import xsdb
from xsdb import xsdb_debug_session
from xsdb._breakpoint import Breakpoint
from xsdb.target import Target
from vitis.domain import Domain


assert xsdb.debug_session is None
assert xsdb_debug_session.debug_session_int_obj is None
methods = []
for method in (Target.state, Target.bpadd, Target.bpremove, Target.rrd,
               Target.con, Target.mrd, Breakpoint.remove, Breakpoint.status,
               Domain.set_lib, Domain.get_libs):
    source = Path(inspect.getsourcefile(method))
    methods.append({"name": method.__qualname__, "signature": str(inspect.signature(method)),
                    "doc": inspect.getdoc(method), "source_path": str(source),
                    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "implementation": inspect.getsource(method)})
help_texts = {}
for name in ("state", "bpadd", "bpremove", "rrd", "con", "mrd"):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        xsdb.help(name)
    help_texts[name] = output.getvalue()
assert xsdb.debug_session is None
assert xsdb_debug_session.debug_session_int_obj is None
target = Path(__file__).parent / "xsdb_help_probe_r02.json"
with target.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump({"schema_version": 1, "status": "PASS_READ_ONLY_PYTHON_XSDB_HELP",
               "hardware_execution": "NOT_RUN", "debug_session_created": False,
               "connected": False, "targets_enumerated": False,
               "methods": methods, "actual_help_output": help_texts},
              stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print("PASS_READ_ONLY_PYTHON_XSDB_HELP_R02 debug_session_created=False hardware_execution=NOT_RUN")
