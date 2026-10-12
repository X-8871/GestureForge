"""捕获独立只读审查实际直接wait和两原生流。"""
from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_tile_origin_rtl as previous
record=dict(runs=[])
previous.execute('review_driver_r03',[sys.executable,'-X','utf8','-B',str(HERE/'review.py')],HERE,HERE,dict(os.environ),record,300)
