"""只读区分原ROOT缓存目录口径和单独obj口径。"""
from pathlib import Path
import json
root=Path.cwd()
cache=root/"tmp/2B/S2B-T17/maxpool_geometry_factor_20261012_r02/rtl_run"
print(json.dumps({"whole_rtl_run":sum(x.stat().st_size for x in cache.rglob("*") if x.is_file()),"obj_only":sum(x.stat().st_size for d in (cache/"obj_geometry",cache/"obj_engine") for x in d.rglob("*") if x.is_file())}))
