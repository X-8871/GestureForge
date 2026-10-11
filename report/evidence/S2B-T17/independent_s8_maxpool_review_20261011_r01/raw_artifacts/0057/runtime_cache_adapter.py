"""只改变现有回归的缓存父目录；生成器、冻结oracle与公开刺激保持原字节。"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import types

ROOT = Path.cwd()
SOURCE = ROOT/"verification/test_s2b_backend_coordinates_rtl.py"
RUN_ID = "maxpool_address_guard_trace_20261011_r01"
sys.path.insert(0,str(SOURCE.parent))
raw = SOURCE.read_bytes()
before = 'work=ROOT/"tmp/2B/S2B-T17"/args.run_id; evidence=ROOT/"report/evidence/S2B-T17"/args.run_id'
after = 'work=ROOT/"tmp/2B/S2B-T17/s8_pool_g1_20261011_r01"/args.run_id; evidence=ROOT/"report/evidence/S2B-T17"/args.run_id'
assert raw.decode("utf-8").count(before)==1
transformed = raw.decode("utf-8").replace(before,after)
module = types.ModuleType("s8_backend_runtime")
module.__file__ = str(SOURCE)
exec(compile(transformed,str(SOURCE),"exec"),module.__dict__)
sys.argv = [str(SOURCE),"--run-id",RUN_ID]
rc = module.main()
evidence = ROOT/"report/evidence/S2B-T17"/RUN_ID
shutil.copyfile(Path(__file__),evidence/"runtime_cache_adapter.py")
capture = dict(command=[sys.executable,"-X","utf8","-B",str(Path(__file__))],native_exit_code=rc,
               source_path=SOURCE.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(raw).hexdigest(),
               transformed_sha256=hashlib.sha256(transformed.encode()).hexdigest(),before=before,after=after,
               reason="仅将缓存根限定在总控授权的独占S8父目录；oracle/源码清单/刺激/检查保持原内容。")
(evidence/"runtime_cache_capture.json").write_text(json.dumps(capture,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
raise SystemExit(rc)
