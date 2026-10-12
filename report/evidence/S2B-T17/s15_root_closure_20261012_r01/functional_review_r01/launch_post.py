"""记录补充审查直接子进程的原生返回码。"""
from pathlib import Path
import sys, os
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_tile_origin_rtl as previous
record=dict(runs=[])
previous.execute('post_audit',[sys.executable,'-X','utf8','-B',str(HERE/'post_audit.py')],HERE,HERE,dict(os.environ),record,180)
