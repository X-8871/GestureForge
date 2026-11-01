"""限定300秒独立Vivado只读查询，采集本次拥有的进程树与内存。"""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from ctypes import wintypes as W
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[4]
SOURCE_DIR = Path(__file__).resolve().parent
TMP = SOURCE_DIR / 'attempt_r03'
OUT = ROOT / 'report/evidence/S2B-T19/postroute_hp0_query_20261013_r01/attempt_r03'
TMP.mkdir(exist_ok=False)
OUT.mkdir(exist_ok=False)
PLAN = ROOT / 'report/evidence/S2B-T19/visibility_remaining_audit_20261013_r01/postroute_query_plan.json'
plan = json.loads(PLAN.read_text(encoding='utf-8'))
dcp = Path(plan['input']['path'])
assert dcp.is_file() and hashlib.sha256(dcp.read_bytes()).hexdigest() == plan['input']['sha256']
vivado = Path(r'D:\Xilinx\2026.1\Vivado\bin\vivado.bat')
assert vivado.is_file() and OUT.is_dir() and TMP.is_dir()

class Entry(ctypes.Structure):
    _fields_ = [('size', W.DWORD), ('cnt', W.DWORD), ('pid', W.DWORD), ('heap', ctypes.c_size_t),
        ('module', W.DWORD), ('threads', W.DWORD), ('parent', W.DWORD), ('priority', W.LONG),
        ('flags', W.DWORD), ('exe', W.WCHAR * 260)]
class Memory(ctypes.Structure):
    _fields_ = [('cb', W.DWORD), ('faults', W.DWORD), ('peak', ctypes.c_size_t), ('rss', ctypes.c_size_t),
        ('quota_peak_paged', ctypes.c_size_t), ('quota_paged', ctypes.c_size_t),
        ('quota_peak_nonpaged', ctypes.c_size_t), ('quota_nonpaged', ctypes.c_size_t),
        ('pagefile', ctypes.c_size_t), ('peak_pagefile', ctypes.c_size_t)]
class GlobalMemory(ctypes.Structure):
    _fields_ = [('length', W.DWORD), ('load', W.DWORD)] + [(n, ctypes.c_ulonglong) for n in
        ['total', 'available', 'page_total', 'page_available', 'virtual_total', 'virtual_available', 'extended']]
k = ctypes.WinDLL('kernel32', use_last_error=True)
p = ctypes.WinDLL('psapi', use_last_error=True)
k.CreateToolhelp32Snapshot.argtypes = [W.DWORD, W.DWORD]
k.CreateToolhelp32Snapshot.restype = W.HANDLE
k.Process32FirstW.argtypes = [W.HANDLE, ctypes.POINTER(Entry)]
k.Process32NextW.argtypes = [W.HANDLE, ctypes.POINTER(Entry)]
k.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
k.OpenProcess.restype = W.HANDLE
k.CloseHandle.argtypes = [W.HANDLE]
k.QueryFullProcessImageNameW.argtypes = [W.HANDLE, W.DWORD, W.LPWSTR, ctypes.POINTER(W.DWORD)]
p.GetProcessMemoryInfo.argtypes = [W.HANDLE, ctypes.POINTER(Memory), W.DWORD]

def snapshot():
    handle = k.CreateToolhelp32Snapshot(2, 0)
    if handle == W.HANDLE(-1).value:
        raise OSError(ctypes.get_last_error(), '进程快照失败')
    e = Entry(); e.size = ctypes.sizeof(e)
    result = {}
    valid = k.Process32FirstW(handle, ctypes.byref(e))
    while valid:
        result[int(e.pid)] = {'pid': int(e.pid), 'parent': int(e.parent), 'exe': e.exe}
        valid = k.Process32NextW(handle, ctypes.byref(e))
    k.CloseHandle(handle)
    return result

def measure(processes, root_pid):
    owned = {root_pid}
    for _ in range(32):
        new = {pid for pid, info in processes.items() if info['parent'] in owned}
        if new <= owned:
            break
        owned |= new
    records = []
    for pid in sorted(owned & processes.keys()):
        info = dict(processes[pid])
        handle = k.OpenProcess(0x1000 | 0x0010, False, pid)
        if handle:
            mem = Memory(); mem.cb = ctypes.sizeof(mem)
            info['rss_bytes'] = int(mem.rss) if p.GetProcessMemoryInfo(handle, ctypes.byref(mem), mem.cb) else None
            info['peak_rss_bytes'] = int(mem.peak) if info['rss_bytes'] is not None else None
            buffer = ctypes.create_unicode_buffer(32768); size = W.DWORD(len(buffer))
            info['path'] = buffer.value if k.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)) else None
            k.CloseHandle(handle)
        else:
            info['memory_error'] = ctypes.get_last_error()
        records.append(info)
    gm = GlobalMemory(); gm.length = ctypes.sizeof(gm)
    k.GlobalMemoryStatusEx(ctypes.byref(gm))
    return records, int(gm.available)

baseline = snapshot()
heavy = [v for v in baseline.values() if v['exe'].lower() in {'vivado.exe', 'xsim.exe', 'xelab.exe', 'xsynth.exe'}]
if heavy:
    raise RuntimeError(f'已有重型进程，停止：{heavy}')
initial_records, initial_available = measure(baseline, os.getpid())
if initial_available < 2 * 1024**3:
    raise RuntimeError('启动前可用内存不足2GiB')
wrapper = TMP / 'run.cmd'
wrapper.write_text('@echo off\nrem 固定只读查询，退出码原样返回\n' +
    f'call "{vivado}" -mode batch -source "{SOURCE_DIR / "query_r03.tcl"}" -log "{OUT / "vivado.log"}" '
    f'-journal "{OUT / "vivado.jou"}" -tclargs "{dcp}" "{OUT}"\nexit /b %errorlevel%\n', encoding='utf-8')
assert ' ' not in str(wrapper), '包装路径含空格，停止而非猜测转义'
command = [os.environ['COMSPEC'], '/d', '/c', str(wrapper)]
# 仅子进程使用本次私有配置/临时目录，防止写入用户现有配置。
child_env = dict(os.environ)
private_profile = TMP / 'profile'
for name, target in {'APPDATA': TMP / 'appdata', 'LOCALAPPDATA': TMP / 'localappdata',
                     'USERPROFILE': private_profile, 'TEMP': TMP / 'temp', 'TMP': TMP / 'temp'}.items():
    target.mkdir(parents=True, exist_ok=True)
    child_env[name] = str(target)
(private_profile / '.Xilinx' / 'Vivado').mkdir(parents=True, exist_ok=True)
started = time.monotonic()
receipt = {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'command': command, 'cwd': str(TMP), 'dcp': plan['input'],
    'started_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'child_private_environment': {name: child_env[name] for name in ['APPDATA','LOCALAPPDATA','USERPROFILE','TEMP','TMP']},
    'initial_available_bytes': initial_available, 'initial_heavy_processes': heavy,
    'budget': {'timeout_seconds': 300, 'minimum_available_bytes': 512 * 1024**2,
        'ps7_pins': 4096, 'ordinary_leaf': 4096, 'shared_gnd_leaf': 65536, 'clock_leaf': 8192, 'cone': 4096, 'backend_cells': 32768},
    'budget_adjustment_basis': 'PS7真实3305 pins；固定PNR有19891 LUT/4371寄存器及4534脉宽endpoint，clock8192；共享常量全芯片扇出按net去重。未使用PS7 ARESETN/FIFO计数OUT另记，不将其当事务口。',
    'hardware_execution': 'NOT_RUN', 'synthesis_implementation': 'NOT_RUN'}
peak = 0
with (OUT / 'cli.stdout.log').open('wb') as stdout, (OUT / 'cli.stderr.log').open('wb') as stderr, (OUT / 'process_samples.jsonl').open('w', encoding='utf-8') as samples:
    process = subprocess.Popen(command, cwd=TMP, env=child_env, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
    receipt['launcher_pid'] = process.pid
    reason = None
    while process.poll() is None:
        records, available = measure(snapshot(), process.pid)
        total = sum(r.get('rss_bytes') or 0 for r in records)
        peak = max(peak, total)
        elapsed = time.monotonic() - started
        samples.write(json.dumps({'elapsed_seconds': elapsed, 'available_bytes': available,
            'rss_sum_bytes': total, 'processes': records}, ensure_ascii=False) + '\n')
        samples.flush()
        if elapsed >= 300 or available < 512 * 1024**2:
            reason = 'TIMEOUT_300S' if elapsed >= 300 else 'AVAILABLE_MEMORY_LT_512MIB'
            # 只终止本次仍存活的Popen根及其子树，绝不匹配关闭他人会话。
            killed = subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
            receipt['owned_stop'] = {'reason': reason, 'native_exit_code': killed.returncode,
                'stdout': killed.stdout.decode('utf-8', errors='replace'), 'stderr': killed.stderr.decode('utf-8', errors='replace')}
            break
        time.sleep(1)
    try:
        receipt['native_exit_code'] = process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        receipt['native_exit_code'] = None
        receipt['stop_error'] = '拥有的launcher未在停止后退出'
receipt.update(elapsed_seconds=time.monotonic()-started, sampled_peak_process_tree_rss_bytes=peak,
    peak_memory_reason='1秒Toolhelp进程树+GetProcessMemoryInfo WorkingSet采样，非连续极值；每进程peak另存样本',
    stop_reason=reason, repeat_count=1,
    final_dcp_sha256=hashlib.sha256(dcp.read_bytes()).hexdigest())
assert receipt['final_dcp_sha256'] == plan['input']['sha256']
receipt['status'] = 'QUERY_NATIVE_RETURNED' if reason is None else 'BLOCKED_RESOURCE'
(OUT / 'execution_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt, ensure_ascii=False, indent=2))
