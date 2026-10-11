"""隔离轻量只读审查的真实原生命令和离散内存记录。"""
import json
import pathlib
import subprocess
import sys
import time
import psutil

out = pathlib.Path(__file__).absolute().parent
command = [sys.executable, '-X', 'utf8', '-B', str(out / 'check_pack.py')]
start = time.monotonic()
peak = unknown = samples = 0
with (out / 'supplement.stdout.log').open('xb') as stdout, (out / 'supplement.stderr.log').open('xb') as stderr:
    child = subprocess.Popen(command, cwd=out.parents[3], stdout=stdout, stderr=stderr)
    process = psutil.Process(child.pid)
    while child.poll() is None:
        rss = 0
        try:
            tree = [process] + process.children(recursive=True)
            for member in tree:
                try:
                    rss += member.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    unknown += 1
            samples += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            unknown += 1
        peak = max(peak, rss)
        if peak > 268435456 or time.monotonic() - start > 120:
            child.kill()
            raise RuntimeError('隔离审查越过120秒/256MiB轻量停止门槛')
        time.sleep(0.02)
    code = child.wait()
record = {'command': command, 'cwd': str(out.parents[3]), 'native_exit_code': code,
          'elapsed_seconds': time.monotonic() - start, 'sampled_owned_tree_peak_bytes': peak,
          'sample_interval_seconds': 0.02, 'samples': samples, 'unknown_samples': unknown,
          'absolute_tree_peak_bytes': None, 'limitations': ['离散采样不能证明OS连续绝对树峰；退出短命Git对象可能UNKNOWN。', '只核最终输入与门禁，未调用Vivado或硬件。']}
with (out / 'supplement.native.json').open('x', encoding='utf-8', newline='\n') as f:
    json.dump(record, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps(record, ensure_ascii=False))
sys.exit(code)
