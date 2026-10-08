"""只读取安装的HSI初始化生成API说明，不打开XSA或访问目标。"""

import hashlib
import inspect
import json
from pathlib import Path

import hsi
import hsiutils
from hsi import HwManager


methods = []
for name in dir(HwManager):
    if any(part in name.lower() for part in ("init", "generate", "open_hw", "close_hw")):
        method = getattr(HwManager, name)
        try:
            signature = str(inspect.signature(method))
        except (ValueError, TypeError):
            signature = None
        methods.append({"name": name, "signature": signature, "doc": inspect.getdoc(method)})
sources = {}
for module in (hsi, hsiutils):
    source = Path(module.__file__)
    sources[module.__name__] = {"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                "init_members": [name for name in dir(module) if "init" in name.lower()]}
target = Path(__file__).parent / "hsi_init_probe.json"
with target.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump({"schema_version": 1, "status": "READ_ONLY_API_METADATA",
               "hardware_execution": "NOT_RUN", "xsa_opened": False,
               "methods": methods, "sources": sources}, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps(methods, ensure_ascii=False, indent=2))
print("HSI_METADATA_ONLY_OK xsa_opened=False hardware_execution=NOT_RUN")
