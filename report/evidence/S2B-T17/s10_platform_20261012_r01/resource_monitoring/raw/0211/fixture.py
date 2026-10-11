"""只创建审查者自有轻量Python父子对象，均自然退出或经身份复核清理。"""
from pathlib import Path
import subprocess,sys,time,json
mode,marker=sys.argv[1:3]
if mode=='race':
    child=subprocess.Popen([sys.executable,'-X','utf8','-B','-c','import time;time.sleep(0.8)'],cwd=Path.cwd())
elif mode=='orphan':
    child=subprocess.Popen([sys.executable,'-X','utf8','-B','-c','import time;time.sleep(12)'],cwd=Path.cwd())
else:child=None
Path(marker).write_text(json.dumps({'root_pid':__import__('os').getpid(),'child_pid':child.pid if child else None}),encoding='utf-8')
time.sleep(2.4 if mode=='orphan' else 12)
