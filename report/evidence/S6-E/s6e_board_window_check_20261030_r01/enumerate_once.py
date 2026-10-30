"""本轮正式租约下的一次只读拓扑枚举；默认只做离线自检。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import subprocess
import sys
import time

ROOT = Path('D:/codex-worktrees/w6')
MAIN = Path('D:/FPGA_Competition')
RUN = Path(__file__).resolve().parent
BASE = '8d30a9ff693284d5d8fffcd676c6ca94627e6790'
OFFER = '4646d4852fa1e8584e3ccf69582672b127335bd4'
SERVER = Path('D:/Xilinx/2026.1/Vitis/bin/unwrapped/win64.o/hw_server.exe')
XSDB = Path('D:/Xilinx/2026.1/Vitis/bin/unwrapped/win64.o/xsdb.exe')
TOOL_HASHES = {SERVER: 'e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3',
               XSDB: '664dc93eb6cec40a2596162dbdf9bc42d5ab96ffbfc34d7515f8c68072fbac55'}
TZ = timezone(timedelta(hours=8))

def now():
    return datetime.now(TZ).isoformat(timespec='seconds')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(root, *args):
    return subprocess.check_output(['git', '-c', 'core.longpaths=true', '-C', str(root), *args], timeout=10)

def powershell(code):
    p = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', code],
                       capture_output=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8', errors='replace'))
    return json.loads(p.stdout.decode('utf-8-sig') or '{}')

def host():
    return powershell("[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false); "
        "$p=@(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object "
        "{$_.Name -in @('hw_server.exe','xsdb.exe','vivado.exe','xsim.exe','vitis.exe','cs_server.exe')} | "
        "Select-Object ProcessId,ParentProcessId,CreationDate,Name,ExecutablePath); "
        "$l=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | "
        "Where-Object {$_.LocalPort -in @(3121,23121)} | Select-Object LocalPort,OwningProcess); "
        "@{processes=$p;listeners=$l}|ConvertTo-Json -Depth 5 -Compress")

def idle(snapshot):
    if snapshot['processes'] or snapshot['listeners']:
        raise RuntimeError('存在相关进程或端口监听，不接管、不停止外部进程')

def validate(output, code):
    if code != 0 or 'S6_ENUM_ERROR=' in output:
        raise RuntimeError('枚举退出码或错误标记异常')
    for marker in ('S6_ENUM_BEGIN=1', 'S6_TARGETS_BEGIN', 'S6_TARGETS_END',
                   'S6_JTAG_BEGIN', 'S6_JTAG_END', 'S6_DISCONNECTED=1', 'S6_ENUM_END=1'):
        if output.splitlines().count(marker) != 1:
            raise RuntimeError('枚举标记缺失或重复：' + marker)
    target = output.split('S6_TARGETS_BEGIN\n', 1)[1].split('S6_TARGETS_END', 1)[0]
    chain = output.split('S6_JTAG_BEGIN\n', 1)[1].split('S6_JTAG_END', 1)[0]
    if not re.search(r'Cortex-A9\s*#0', target) or not re.search(r'Cortex-A9\s*#1', target):
        raise RuntimeError('未同时枚举两个A9目标')
    if not chain.strip() or re.search(r'no targets|all zeroes', target + chain, re.I):
        raise RuntimeError('JTAG链为空或异常')
    return {'targets_text': target.strip(), 'jtag_text': chain.strip()}

def selftest():
    good = ('S6_ENUM_BEGIN=1\nS6_TARGETS_BEGIN\nCortex-A9 #0\nCortex-A9 #1\n'
            'S6_TARGETS_END\nS6_JTAG_BEGIN\nxc7z020\nS6_JTAG_END\nS6_DISCONNECTED=1\nS6_ENUM_END=1\n')
    validate(good, 0)
    bad = [(good, 1), (good + 'S6_ENUM_ERROR=disconnect\n', 0),
           (good.replace('Cortex-A9 #1', ''), 0), (good.replace('xc7z020', ''), 0),
           (good.replace('S6_DISCONNECTED=1\n', ''), 0), (good + 'S6_ENUM_END=1\n', 0)]
    for output, code in bad:
        try:
            validate(output, code)
        except RuntimeError:
            continue
        raise AssertionError('应失败的枚举输出被接受')
    idle({'processes': [], 'listeners': []})
    for snapshot in ({'processes': [1], 'listeners': []}, {'processes': [], 'listeners': [1]}):
        try:
            idle(snapshot)
        except RuntimeError:
            continue
        raise AssertionError('忙态被接受')
    print('SELFTEST_PASS positive=2 negative=8; 未调用硬件')

def execute():
    execution = RUN / 'execution.json'
    if execution.exists() or (RUN / 'hw_server.log').exists() or (RUN / 'xsdb.log').exists():
        raise RuntimeError('RunId已使用，拒绝重跑')
    record = {'scope': 'READONLY_TOPOLOGY_ONLY', 'start_utc8': now(), 'status': 'NOT_RUN',
              'errors': [], 'commands': [], 'memory_or_register_access': False,
              'board_programmed': False, 'T6_A03': 'NOT_RUN', 'stage6_G5': '未通过'}
    server = xsdb = None
    guard = None
    streams = []
    start = time.monotonic()
    try:
        if git(ROOT, 'rev-parse', 'HEAD').decode().strip() != BASE:
            raise RuntimeError('w6基线漂移')
        if git(ROOT, 'rev-parse', '--abbrev-ref', 'HEAD').decode().strip() != 'stage6-interact-prep':
            raise RuntimeError('分支不符')
        lock = Path(git(ROOT, 'rev-parse', '--git-path', 'index.lock').decode().strip())
        if lock.exists() or git(ROOT, 'diff', '--cached', '--name-only').strip():
            raise RuntimeError('锁或暂存区非空')
        grant = git(MAIN, 'show', OFFER + ':.codex/STATE.md')
        if 'DSH 板卡会话 OFFERED'.encode() not in grant:
            raise RuntimeError('固定提交没有正式OFFER')
        state = (ROOT / '.codex/STATE.md').read_text(encoding='utf-8')
        if 'CLAIMED / Codex；脚本独立审查通过后执行一次' not in state:
            raise RuntimeError('本轮CLAIM缺失')
        receipt = json.loads((RUN / 'review_receipt.json').read_text(encoding='utf-8'))
        if receipt['status'] != 'PASS':
            raise RuntimeError('独立审查未通过')
        for name in ('enumerate_once.py', 'enumerate.tcl'):
            if digest(RUN / name) != receipt['files'][name]:
                raise RuntimeError('被审源码漂移：' + name)
        for path, expected in TOOL_HASHES.items():
            if not path.is_file() or digest(path) != expected:
                raise RuntimeError('工具路径/身份不符')
        record['preflight'] = host()
        idle(record['preflight'])
        live_state = (MAIN / '.codex/STATE.md').read_bytes()
        if 'DSH 板卡会话 OFFERED'.encode() not in live_state:
            raise RuntimeError('当前OFFER已撤回')
        mailbox = MAIN / 'report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox'
        mail_state = {p.name: digest(p) for p in mailbox.iterdir() if p.is_file()}
        def guard():
            if time.monotonic() - start > 60:
                raise RuntimeError('60秒总运行预算到期')
            if (MAIN / '.codex/STATE.md').read_bytes() != live_state:
                raise RuntimeError('主STATE变化，停止等候租约复核')
            if {p.name: digest(p) for p in mailbox.iterdir() if p.is_file()} != mail_state:
                raise RuntimeError('DSH通知变化，停止等候复核')
        def launch(argv, log):
            stream = (RUN / log).open('xb')
            streams.append(stream)
            p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                                 shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
            record['commands'].append({'argv': argv, 'pid': p.pid, 'start_utc8': now(), 'log': log})
            return p
        guard()
        server = launch([str(SERVER), '-s', 'tcp::3121'], 'hw_server.log')
        record['status'] = 'RUNNING'
        deadline = time.monotonic() + 10
        while True:
            guard()
            snapshot = host()
            guard()
            if time.monotonic() > deadline:
                raise RuntimeError('server启动核验已超过10秒预算')
            foreign = [p for p in snapshot['processes'] if p['ProcessId'] != server.pid]
            if foreign or server.poll() is not None:
                raise RuntimeError('外部进程出现或本次server退出')
            if snapshot['listeners']:
                if any(p['LocalPort'] != 3121 or p['OwningProcess'] != server.pid for p in snapshot['listeners']):
                    raise RuntimeError('端口监听者不属于本次server')
                break
            if time.monotonic() > deadline:
                raise RuntimeError('server未在10秒内监听')
            time.sleep(0.25)
        guard()
        if time.monotonic() > deadline:
            raise RuntimeError('启动XSDB前server核验预算已到期')
        xsdb = launch([str(XSDB), str(RUN / 'enumerate.tcl')], 'xsdb.log')
        deadline = time.monotonic() + 30
        next_owner_check = time.monotonic()
        while xsdb.poll() is None:
            guard()
            if time.monotonic() >= next_owner_check:
                snapshot = host()
                guard()
                if not snapshot['listeners'] or any(p['LocalPort'] != 3121 or p['OwningProcess'] != server.pid for p in snapshot['listeners']):
                    raise RuntimeError('枚举期间端口监听归属改变')
                if any(p['ProcessId'] not in (server.pid, xsdb.pid) for p in snapshot['processes']):
                    raise RuntimeError('枚举期间出现外部硬件会话')
                next_owner_check = time.monotonic() + 1
            if server.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError('server退出或xsdb超过30秒，不重试')
            time.sleep(0.25)
        guard()
        if time.monotonic() > deadline:
            raise RuntimeError('XSDB完成时已经超过30秒预算')
        streams[-1].flush()
        output = (RUN / 'xsdb.log').read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')
        record['topology'] = validate(output, xsdb.returncode)
        record['status'] = 'PASS_READONLY_TOPOLOGY'
    except Exception as exc:
        record['errors'].append(str(exc))
        record['status'] = 'FAIL_STOPPED' if server is not None else 'NOT_RUN'
    finally:
        # 仅使用本轮Popen持有的进程句柄，不按名称、PID树或端口杀进程。
        for name, proc in [('xsdb', xsdb), ('hw_server', server)]:
            if proc is not None:
                try:
                    if proc.poll() is None:
                        proc.terminate()
                        proc.wait(timeout=5)
                    record[name + '_exit_code'] = proc.returncode
                except Exception as exc:
                    record['errors'].append('本次进程清理失败：' + str(exc))
        for stream in streams:
            stream.close()
        try:
            record['postflight'] = host()
            idle(record['postflight'])
            if guard is not None:
                guard()
        except Exception as exc:
            record['errors'].append('收窗核验失败：' + str(exc))
        if record['errors'] and record['status'] == 'PASS_READONLY_TOPOLOGY':
            record['status'] = 'FAIL_STOPPED'
        record['end_utc8'] = now()
        record['elapsed_seconds'] = round(time.monotonic() - start, 3)
        execution.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record['status'] == 'PASS_READONLY_TOPOLOGY' else 1

if __name__ == '__main__':
    if sys.argv[1:] == ['--execute-once']:
        raise SystemExit(execute())
    if sys.argv[1:] not in ([], ['--self-test']):
        raise SystemExit('只接受--self-test或--execute-once')
    selftest()
