"""记录审查driver直接子进程原生退出码和原始日志。"""
from pathlib import Path
import sys, os, json
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_tile_origin_rtl as previous
record=dict(runs=[])
try:
    text=previous.execute('review_driver_r02',[sys.executable,'-X','utf8','-B',str(HERE/'review.py')],HERE,HERE,dict(os.environ),record,1200)
    print(text,flush=True)
except Exception as error:
    print(json.dumps(dict(error=repr(error)),ensure_ascii=True),flush=True)
    sys.exit(1)
