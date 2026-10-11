"""只创建审查者自有轻量Python父子对象，均自然退出或经身份复核清理。"""
from pathlib import Path
import subprocess,sys,time,json
mode,marker=sys.argv[1:3]
if mode=='race':
    child=subprocess.Popen([sys.executable,'-X','utf8','-B','-c','import time;time.sleep(0.8)'],cwd=Path.cwd())
elif mode=='orphan':
    child=subprocess.Popen([sys.executable,'-X','utf8','-B','-c','import time;time.sleep(12)'],cwd=Path.cwd())
elif mode=='ancestor':
    nested=str(Path(marker).with_name('nested.json'))
    code='import subprocess,sys,time,json;from pathlib import Path;p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(12)"]);Path(sys.argv[1]).write_text(json.dumps({"pid":p.pid}),encoding="utf-8");time.sleep(.8)'
    child=subprocess.Popen([sys.executable,'-X','utf8','-B','-c',code,nested],cwd=Path.cwd())
    while not Path(nested).exists():time.sleep(.01)
    Path(marker).write_text(json.dumps({'root_pid':__import__('os').getpid(),'child_pid':json.loads(Path(nested).read_text(encoding='utf-8'))['pid'],'parent_pid':child.pid}),encoding='utf-8')
else:child=None
if mode!='ancestor':Path(marker).write_text(json.dumps({'root_pid':__import__('os').getpid(),'child_pid':child.pid if child else None}),encoding='utf-8')
time.sleep(2.4 if mode=='orphan' else 12)
