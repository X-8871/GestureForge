"""只读采样现有Vivado进程及子进程，区别空闲会话与运行中的重型任务。"""
from pathlib import Path
import json,time,psutil
p=psutil.Process(23188); tree=[p]+p.children(recursive=True)
before={x.pid:sum(x.cpu_times()[:2]) for x in tree}
time.sleep(2)
rows=[{'pid':x.pid,'name':x.name(),'command':x.cmdline(),'rss_bytes':x.memory_info().rss,'cpu_seconds_delta_2s':sum(x.cpu_times()[:2])-before[x.pid]} for x in tree if x.is_running()]
out=Path(__file__).parent/'process_preflight.json'; out.write_text(json.dumps({'rows':rows,'sample_seconds':2},ensure_ascii=False,indent=2),encoding='utf-8'); print(out.read_text(encoding='utf-8'))
