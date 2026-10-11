"""自有轻量父链；文件标记使helper自然退出，不查询其它窗口对象。"""
import os
import sys
import time

work = os.getcwd()
mode = sys.argv[1]
child = None
if mode in {"root", "helper"}:
    import subprocess
    child = subprocess.Popen([sys.executable, "-S", "-B", "-X", "utf8", __file__, "helper" if mode == "root" else "leaf"], cwd=work)
with open(os.path.join(work, mode + "_ready.json"), "x", encoding="utf-8") as stream:
    stream.write('{"pid":%d,"child":%s}' % (os.getpid(), str(child.pid) if child else "null"))
print("自有夹具 " + mode, flush=True)
started = time.monotonic()
while time.monotonic() - started < 40:
    if os.path.exists(os.path.join(work, mode + "_exit")):
        break
    if mode == "leaf" and os.path.exists(os.path.join(work, "new_child")) and child is None:
        import subprocess
        child = subprocess.Popen([sys.executable, "-S", "-B", "-X", "utf8", __file__, "newborn"], cwd=work)
    time.sleep(0.02)
