"""复用已核验的PS初始化状态，只运行修正UART诊断字段的CPU0 smoke。"""

from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import traceback


ROOT = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
RUN = ROOT / 'report/evidence/S2B-T06/ps_uart_clock_retest_20261009_172557_r01'
BUILD = ROOT / 'report/evidence/S2B-T06/ps_uart_clock_fix_20261009_172254_r02/build'
PRIOR_BUILD = ROOT / 'report/evidence/S2B-T06/ps_smoke_20261008_r01/build_08'
CAPTURE = ROOT / 'report/evidence/S2B-T06/ps_smoke_hw_20261009_101728_r01/capture_uart.ps1'
NATIVE = {'ProcessId': 39576, 'ParentProcessId': 37840,
          'ExecutablePath': r'D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe',
          'CreationTimeFileTimeUtc': '134359925214792270'}
FIXED = {
    'operation_package': (ROOT / 'vitis/s2b_ps_smoke.md', 'd6cf1e83e0871c3a43cc8f5f107eb4f0635641efd72191724259d889b61e75d1'),
    'prior_init_elf': (PRIOR_BUILD / 's2b_ps_init.elf', '366ad1f4831eba9db0510c0e5343d34e3b355f72c8f8bcae419903814246024c'),
    'prior_smoke_elf': (PRIOR_BUILD / 's2b_ps_smoke.elf', '8b9803682c9585a8dad91daf96f3f102de948466025e0cf28ee4b96e6cfde428'),
    'smoke_elf': (BUILD / 's2b_ps_smoke.elf', '9be608b847da26988f42105e2ab856c454d6dd7090c87b7dc95064f4cc05e847'),
    'layout_binding': (BUILD / 'layout_binding.json', '886e5d3945e5c93012fbcd021bf1dc3a23c711b4404d4e5d58b07cc715d44911'),
    'build_details': (BUILD / 'build_details.json', 'ccfd286e048e5ed45994be26b0887da54c84d8f0d5fd2757835ac82eae2f172d'),
    'prior_result': (ROOT / 'report/evidence/S2B-T06/ps_jtag_retry_20261009_165853_r02/ps_smoke_result.json', 'f02143baec914d6436d2fbb672831ea8a9d4aa3c2fda27de37836989809fa8f8'),
    'prior_runner': (ROOT / 'report/evidence/S2B-T06/ps_jtag_retry_20261009_165853_r02/ps_smoke_runner.py', '5265f0989a3e69e80677b12548ffe19ebcd48a0bdafb80c270bbf1fa2833bb81'),
    'authorization': (RUN / 'authorization.json', 'fb862e7c6d7491d22bbc4bf075df33d6214fbbc10b17c8a9eedd781fb0202bff'),
    'warm_basis': (RUN / 'old_and_warm_review_receipt.json', 'e3a3480a7fbe2417e9302aa886db70d0bfc4a1dd0790fc6e3cc842de94162930'),
    'xsa': (ROOT / 'report/evidence/S2B-T04/ps_platform_20261008_r02/candidate_attempt1/s2b_ps_only.xsa', 'a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58'),
    'c_source': (ROOT / 'vitis/s2b_ps_smoke.c', '8b4bfcf517c821a7c345ec7af61ebf1eb5120a32cc827c22b2be25887c8edef5'),
    'state_result': (ROOT / 'report/evidence/S2B-T06/ps_jtag_retry_20261009_120653_r01/ps_state_result.json', '072b9f65d10da992300532f2873c3a8b843e2f24cf270b4789e00155d0b014e6'),
    'server_identity': (RUN / 'hw_server_identity.json', 'e8771c4e850f73531fa83cd51fb83fcc0ab9c052631d18ab348750a97918be72'),
    'capture_source': (CAPTURE, '3b78f5b54dc7413821400e2c5df3bc1c73a93375b9b71ede9bec42a99e16605d'),
    'native_server': (Path(NATIVE['ExecutablePath']), 'e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3'),
    'sdk_session': (Path(r'D:\Xilinx\2026.1\Vitis\cli\xsdb\session.py'), 'e1c85985ada7176182de0b59ddbbc44ecf7cd0047adcc42d94563dbb85da7b7b'),
    'sdk_target': (Path(r'D:\Xilinx\2026.1\Vitis\cli\xsdb\target.py'), 'a853cb0a0d86e52bc588b045f648e1184708fc2d35ba2bd3b9eb11847288cf71'),
    'sdk_breakpoint': (Path(r'D:\Xilinx\2026.1\Vitis\cli\xsdb\_breakpoint.py'), '22b86a6e877a29ce3329846a90a46f3fae21dca44cfd5646403625f02984eb3b'),
    'frontend': (Path(r'D:\Xilinx\2026.1\Vitis\bin\vitis.bat'), '9a305c248c966207c3e785d38fe92f01b51aeb1f3450896e8617c10a1a8a56f7'),
    'api_basis': (ROOT / 'report/evidence/S2B-T06/ps_smoke_20261008_r01/xsdb_operating_basis_r03.json', '7964b0a15ee7dc17d30ebb4a16c8cfb5faa71ecd50f4901e1d9239168e38355f'),
}
TZ = timezone(timedelta(hours=8))


def exact_file(path):
    """逐分量拒绝大小写替代、通配符和链接；只消费确实存在的普通文件。"""
    path = Path(path)
    if not path.is_absolute() or any(part in ('.', '..') for part in path.parts) or any(c in str(path) for c in '*?[]'):
        raise RuntimeError('输入必须为精确绝对文件路径：' + str(path))
    current = Path(path.anchor)
    for name in path.parts[1:]:
        matches = [p for p in current.iterdir() if p.name.casefold() == name.casefold()]
        if len(matches) != 1 or matches[0].name != name:
            raise RuntimeError('路径分量不存在或存在大小写歧义：' + str(path))
        current = matches[0]
        if current.stat(follow_symlinks=False).st_file_attributes & 0x400:
            raise RuntimeError('拒绝链接或重解析点：' + str(current))
    if not current.is_file():
        raise RuntimeError('输入不是文件：' + str(current))
    return current


def verified_bytes(path, expected):
    """固定输入原字节及SHA，禁止用声明替代实际文件核验。"""
    if not isinstance(expected, str) or re.fullmatch(r'[0-9a-fA-F]{64}', expected) is None:
        raise RuntimeError('输入SHA必须为完整64位十六进制。')
    data = exact_file(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected.lower():
        raise RuntimeError('输入SHA变化：' + str(path))
    return data


def strict_json(data):
    """拒绝重复键和非有限常量，避免不同解释器消费不同前提。"""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise RuntimeError('JSON包含重复键：' + key)
            result[key] = value
        return result

    def invalid(value):
        raise RuntimeError('JSON包含非法常量：' + value)

    if isinstance(data, bytes):
        data = data.decode('utf-8-sig')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def validate_targets(properties):
    """按重新枚举的同一线缆及父上下文选择两核，拒绝额外或未知设备。"""
    names = ('APU', 'ARM Cortex-A9 MPCore #0', 'ARM Cortex-A9 MPCore #1', 'xc7z020')
    if type(properties) is not dict or len(properties) != 4:
        raise RuntimeError('目标返回结构或数量改变。')
    selected = {}
    for ctx, target in properties.items():
        name = target['name']
        if name not in names or name in selected or target['target_ctx'] != ctx:
            raise RuntimeError('目标名称或上下文不一致。')
        if (target['jtag_cable_manufacturer'], target['jtag_cable_product'], target['jtag_cable_serial']) != ('Digilent', 'JTAG-HS1', '210512180081'):
            raise RuntimeError('线缆身份改变。')
        if type(target['target_id']) is not int or target['target_id'] <= 0:
            raise RuntimeError('目标ID无效。')
        selected[name] = target
    if len({t['target_id'] for t in selected.values()}) != 4 or len({t['jtag_cable_ctx'] for t in selected.values()}) != 1:
        raise RuntimeError('目标ID或线缆上下文不唯一。')
    apu = selected['APU']
    for name in names[1:3]:
        cpu = selected[name]
        if cpu['parent_ctx'] != apu['target_ctx'] or cpu['parent'] != 'APU' or cpu['jtag_device_ctx'] != apu['jtag_device_ctx']:
            raise RuntimeError('CPU不属于同一唯一APU。')
    return selected


def main():
    """在旧成功终点及初始化状态门禁通过后仅执行新版smoke；失败停止CPU0。"""
    if str(Path(__file__)) != str(RUN / 'ps_smoke_runner.py') or not RUN.is_dir():
        raise RuntimeError('脚本或Run目录不符合已核实的精确路径。')
    result_path = RUN / 'ps_smoke_result.json'
    if any(p.name.casefold() == result_path.name.casefold() for p in RUN.iterdir()):
        raise RuntimeError('结果文件已存在或有大小写冲突，拒绝覆盖。')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    now = lambda: datetime.now(TZ).isoformat()
    started = time.monotonic()
    record = {'started_at': now(), 'status': 'IN_PROGRESS', 'source_commit': '117911e63cd7468418f11847ffedc9293dbca075',
              'calls': [], 'observations': [], 'downloads': [], 'cleanup_errors': [],
              'ps_initialization': 'NOT_RUN_THIS_RUN', 'smoke_execution': 'NOT_RUN', 'uart_acceptance': 'NOT_RUN',
              'overall_uart_ddr_acceptance': 'NOT_RUN', 'cold_jtag_proven': False,
              'final_observation_scope': 'final_states/final_pc仅为本次会话内disconnect前的最后观测，不证明断开后仍保持停止。',
              'limitations': ['物理资料及照片真实性由总控和独立审查核实；schema核验本身不能证明实物事实。',
                             'CPU1只在门禁前后观测，不是持续采样；本脚本不恢复CPU1。',
                             '硬件PC及结果门禁保存不代表完整UART/DDR验收通过。', '峰值内存及全部上层工具调用量未测。']}
    session = channel = sdk = None
    cores, owned_bps, removed_bps = {}, [], set()
    smoke_attempted = False

    def emit(item):
        print(json.dumps(item, ensure_ascii=False, default=str), flush=True)

    def call(api, function, *args, **kwargs):
        """逐API保存真实stdout、stderr、返回类型与repr及异常原文。"""
        item = {'time': now(), 'api': api, 'args': list(args), 'kwargs': kwargs, 'state': 'CALLING'}
        record['calls'].append(item)
        emit(item)
        output, errors = io.StringIO(), io.StringIO()
        clock = time.monotonic()
        try:
            with redirect_stdout(output), redirect_stderr(errors):
                value = function(*args, **kwargs)
            item.update(state='DONE', return_repr=repr(value), return_type=type(value).__name__)
            return value
        except BaseException as error:
            item.update(state='FAILED', error=repr(error), traceback=traceback.format_exc())
            raise
        finally:
            item.update(finished_at=now(), elapsed_seconds=time.monotonic() - clock,
                        stdout=output.getvalue(), stderr=errors.getvalue())
            emit(item)

    def host_query(label, command):
        """只读查询服务/采集进程；不启动server或打开串口。"""
        command = "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); " + command
        probe = subprocess.run(['powershell.exe', '-NoProfile', '-Command', command], capture_output=True, timeout=15)
        item = {'time': now(), 'host_query': label, 'command': command, 'exit_code': probe.returncode,
                'stdout': probe.stdout.decode('utf-8-sig'), 'stderr': probe.stderr.decode('utf-8-sig')}
        record['calls'].append(item)
        emit(item)
        if probe.returncode != 0 or item['stderr']:
            raise RuntimeError('只读进程查询失败：' + label)
        return strict_json(item['stdout'])

    def check_server():
        """核对唯一服务的PID、父链、路径、启动时间、文件SHA及3121监听。"""
        identity = strict_json(verified_bytes(*FIXED['server_identity']))
        verified_bytes(*FIXED['native_server'])
        if identity['status'] != 'OWNED_SERVER_READY' or identity['native'] != NATIVE or identity['launcher_pid'] != 37840:
            raise RuntimeError('已保存服务身份与固定本次服务不同。')
        command = (
            "$servers=@(Get-CimInstance Win32_Process -Filter \"Name='hw_server.exe'\" | "
            "Select-Object ProcessId,ParentProcessId,ExecutablePath,@{Name='CreationTimeFileTimeUtc';Expression={[string]$_.CreationDate.ToFileTimeUtc()}}); "
            "$launcher=Get-CimInstance Win32_Process -Filter 'ProcessId=37840' | "
            "Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,@{Name='CreationTimeFileTimeUtc';Expression={[string]$_.CreationDate.ToFileTimeUtc()}}; "
            "$listeners=@(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess); "
            "[pscustomobject]@{servers=$servers;launcher=$launcher;listeners=$listeners}|ConvertTo-Json -Depth 5"
        )
        data = host_query('server_identity', command)
        if data['servers'] != [NATIVE] or data['launcher'] != identity['ancestor_chain'][1]:
            raise RuntimeError('服务或launcher父链身份改变。')
        if not data['listeners'] or any(type(p['OwningProcess']) is not int or p['OwningProcess'] != 39576 or p['LocalPort'] != 3121 for p in data['listeners']):
            raise RuntimeError('3121监听不是本次唯一服务。')

    def check_profile():
        """绑定总控确认的原字节profile及实际资料、照片；不替总控作物理推断。"""
        profile = strict_json(verified_bytes(RUN / 'physical_profile.json', profile_sha))
        fields = ('confirmed_ddr', 'confirmed_ps_clk', 'confirmed_uart_mio', 'confirmed_voltage', 'confirmed_cold_boot', 'confirmed_exclusive_writers')
        if profile['status'] != 'PROFILE_CONFIRMED' or any(profile.get(f) is not True for f in fields):
            raise RuntimeError('板级及独占前提尚未确认。')
        if any(not isinstance(profile.get(f), str) or not profile[f].strip() for f in ('board_version', 'reason')):
            raise RuntimeError('缺少PCB版本或真实确认依据。')
        for field in ('source_documents', 'user_photos'):
            rows = profile[field]
            if type(rows) is not list or not rows:
                raise RuntimeError('缺少实际资料或用户照片来源。')
            for row in rows:
                text = row['path']
                if not isinstance(text, str) or not text or '..' in Path(text).parts:
                    raise RuntimeError('资料或照片路径无效。')
                path = Path(text)
                if field == 'user_photos' and not path.is_absolute():
                    raise RuntimeError('用户照片必须绑定实际完整路径。')
                if not path.is_absolute():
                    path = ROOT / path
                verified_bytes(path, row['sha256'])
                if field == 'source_documents':
                    pages = row['pages']
                    if type(pages) is not list or not pages or any(type(p) is not int or p <= 0 for p in pages):
                        raise RuntimeError('资料必须绑定实际正整数页码。')
        record['physical_profile'] = profile

    def check_uart(required_seconds=0):
        """用ReadWrite共享读取实际采集日志；门禁失败禁止dow/con。"""
        identity = strict_json(verified_bytes(RUN / 'uart_capture_identity.json', uart_sha))
        raw, flag, log = RUN / 'uart_raw.bin', RUN / 'stop_capture.flag', RUN / 'uart_capture_stdout.log'
        exact_file(raw)
        exact_file(log)
        if any(p.name.casefold() == flag.name.casefold() for p in RUN.iterdir()):
            raise RuntimeError('采集停止标记已出现，禁止继续。')
        if identity['status'] != 'CAPTURE_OPEN' or identity['port'] != 'COM4' or identity['raw_path'] != str(raw) or identity['stop_flag'] != str(flag):
            raise RuntimeError('采集记录不属于本次Run/COM4。')
        if type(identity['pid']) is not int or identity['pid'] <= 0 or type(identity['parent_pid']) is not int or identity['parent_pid'] <= 0:
            raise RuntimeError('采集PID无效。')
        command = (
            "$process=Get-CimInstance Win32_Process -Filter 'ProcessId=" + str(identity['pid']) + "' | "
            "Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine,@{Name='CreationTimeFileTimeUtc';Expression={[string]$_.CreationDate.ToFileTimeUtc()}}; "
            "$stream=[System.IO.File]::Open('" + str(log) + "',[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::ReadWrite); "
            "$reader=$null; try {$reader=[System.IO.StreamReader]::new($stream,[System.Text.UTF8Encoding]::new($false,$true),$false); $text=$reader.ReadToEnd()} "
            "finally {if ($null -ne $reader) {$reader.Dispose()} else {$stream.Dispose()}}; "
            "[pscustomobject]@{process=$process;log_text=$text;raw_bytes=([System.IO.FileInfo]::new('" + str(raw) + "')).Length}|ConvertTo-Json -Depth 5"
        )
        data = host_query('uart_capture_live', command)
        expected = {'ProcessId': identity['pid'], 'ParentProcessId': identity['parent_pid'],
                    'CreationTimeFileTimeUtc': identity['creation_time_filetime_utc'],
                    'ExecutablePath': identity['executable_path'], 'CommandLine': identity['command_line']}
        if data['process'] != expected:
            raise RuntimeError('采集进程身份、创建时间或命令行改变。')
        # 命令行全串已由哈希绑定；另核对固定脚本、端口和两个本Run路径。
        if any(token not in identity['command_line'] for token in (str(CAPTURE), '-Port COM4', str(raw), str(flag))):
            raise RuntimeError('采集命令行未使用固定脚本及本Run参数。')
        text = data['log_text']
        if 'CAPTURE_CLOSED ' in text or 'CAPTURE_ERROR ' in text:
            raise RuntimeError('采集已关闭或失败。')
        openings = [strict_json(line[len('CAPTURE_OPEN '):]) for line in text.splitlines() if line.startswith('CAPTURE_OPEN ')]
        if len(openings) != 1 or openings[0] != identity['observed_open']:
            raise RuntimeError('真实CAPTURE_OPEN与已绑定记录不一致。')
        opened = openings[0]
        expected_open = {'port': 'COM4', 'raw_path': str(raw), 'stop_flag_path': str(flag), 'baud': 115200,
                         'format': '8N1', 'flow_control': 'None', 'dtr': False, 'rts': False,
                         'read_timeout_ms': 200, 'limit_seconds': 600}
        if set(opened) != set(expected_open) | {'time'} or any(type(opened[k]) is not type(v) or opened[k] != v for k, v in expected_open.items()):
            raise RuntimeError('采集配置不是固定115200/8N1/无流控/DTR和RTS关闭。')
        opened_at = datetime.fromisoformat(opened['time'])
        checked_at = datetime.fromisoformat(identity['checked_at_utc8'])
        current = datetime.now(TZ)
        age = (current - opened_at).total_seconds()
        if opened_at.utcoffset() != timedelta(hours=8) or checked_at.utcoffset() != timedelta(hours=8) or not opened_at <= checked_at <= current or not 0 <= age < 600 - required_seconds:
            raise RuntimeError('采集超过600秒保护或不足本次阻塞运行的剩余时间。')
        verified_bytes(RUN / 'uart_capture_identity.json', uart_sha)
        record['observations'].append({'time': now(), 'gate': 'UART_LIVE', 'age_seconds': age,
                                       'required_seconds': required_seconds, 'raw_bytes': data['raw_bytes'], 'pid': identity['pid']})

    def state(label):
        value = call(label + '.state', cores[label].state)
        record['observations'].append({'time': now(), 'core': label, 'state': value})
        if not isinstance(value, str) or not (value == 'Running' or value.startswith('Stopped')):
            raise RuntimeError('CPU状态未知：' + label)
        return value

    def both_stopped():
        values = {label: state(label) for label in ('cpu0', 'cpu1')}
        if any(not value.startswith('Stopped') for value in values.values()):
            raise RuntimeError('CPU0/CPU1停止前提不成立。')
        return values

    def pc(label):
        value = call(label + '.rrd', cores[label].rrd, reg='pc')
        item = record['calls'][-1]
        match = re.fullmatch(r'\s*pc:\s*([0-9a-fA-F]{8})\s*', item['stdout'])
        if value is not None or item['stderr'] or match is None:
            raise RuntimeError('PC输出不是唯一完整8位十六进制：' + label)
        number = int(match.group(1), 16)
        record['observations'].append({'time': now(), 'core': label, 'pc': number, 'pc_hex': '0x%08X' % number})
        return number

    def word(label, address):
        value = call('cpu0.mrd.' + label, cores['cpu0'].mrd, '--value', address=address, size=1, word_size=4)
        if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
            raise RuntimeError('单word读回类型或范围无效：' + label)
        record.setdefault('readbacks', []).append({'time': now(), 'name': label, 'address': address,
                                                  'value': value, 'value_hex': '0x%08X' % value})
        return value

    def add_bp(label, address):
        """连部分失败时注册的对象也只按本次新增表项追踪，绝不删除其他断点。"""
        before = dict(session._bptable)
        try:
            bp = call('cpu0.bpadd.' + label, cores['cpu0'].bpadd, addr='0x%08X' % address, type='hw')
        finally:
            for key, obj in session._bptable.items():
                if key not in before and not any(obj is old for old in owned_bps):
                    owned_bps.append(obj)
        added = [obj for key, obj in session._bptable.items() if key not in before]
        if len(added) != 1 or bp is not added[0]:
            raise RuntimeError('断点创建返回值与本次新增对象不一致。')
        bp_status(label, bp, address)
        return bp

    def bp_status(label, bp, address, hit=False):
        """按已安装API的真实二元tuple和目标字典判断安装与命中。"""
        value = call('bp.status.' + label, bp.status)
        if type(value) is not tuple or len(value) != 2 or type(value[0]) is not str or type(value[1]) is not dict:
            raise RuntimeError('断点status返回结构未知。')
        mapping = value[1]
        if set(mapping) != {cpu0_id} or type(mapping[cpu0_id]) is not dict:
            raise RuntimeError('断点未明确安装到本次唯一CPU0。')
        row = mapping[cpu0_id]
        addr = row.get('Address')
        count = row.get('HitCount')
        if 'Error' in row or not isinstance(addr, str) or re.fullmatch(r'0x[0-9a-fA-F]+', addr) is None or int(addr, 16) != address or type(count) is not int or count < 0 or (hit and count == 0):
            raise RuntimeError('断点地址、安装状态或实际命中数不满足门禁。')
        record.setdefault('breakpoint_status', []).append({'time': now(), 'name': label, 'text': value[0], 'status': mapping})
        return row

    def remove_bp(bp):
        if id(bp) not in removed_bps:
            call('bp.remove', bp.remove)
            removed_bps.add(id(bp))

    def check_session_options():
        """只读核对SDK下载默认门禁，禁止通过修改会话属性绕过。"""
        fields = vars(session)
        required = ('_force_mem_accesses', '_profile_config', '_gprof')
        if any(name not in fields for name in required):
            raise RuntimeError('SDK会话缺少固定下载门禁属性。')
        force, profile, gprof = (fields[name] for name in required)
        observed = {'time': now(), 'gate': 'SESSION_DOWNLOAD_OPTIONS',
                    'force_type': type(force).__name__, 'force_repr': repr(force),
                    'profile_type': type(profile).__name__, 'profile_repr': repr(profile),
                    'gprof_type': type(gprof).__name__, 'gprof_repr': repr(gprof)}
        record['observations'].append(observed)
        if type(force) not in (int, bool) or force != 0 or type(profile) is not dict or profile or gprof is not None:
            raise RuntimeError('下载前会话必须force为0/False、profile为空dict、gprof为None。')

    def operation_gate(entry, required_seconds=0, require_prior_smoke=False):
        """每次dow/con前重新核对输入和同一PS状态、profile、采集及服务。"""
        for path, digest in FIXED.values():
            verified_bytes(path, digest)
        check_profile()
        check_server()
        check_session_options()
        both_stopped()
        current_pc = {label: pc(label) for label in ('cpu0', 'cpu1')}
        values = {'BOOT_MODE': word('BOOT_MODE_GATE', 0xF800025C),
                  'OCM_CFG': word('OCM_CFG_GATE', 0xF8000910),
                  'INIT_RESULT': word('INIT_RESULT_REUSED_GATE', 0x9200),
                  'INIT_RETURN_CODE': word('INIT_RETURN_CODE_REUSED_GATE', 0x39C0)}
        if current_pc != {'cpu0': entry, 'cpu1': 0xFFFFFF34} or values != {'BOOT_MODE': 0, 'OCM_CFG': 0x18, 'INIT_RESULT': 2, 'INIT_RETURN_CODE': 0}:
            raise RuntimeError('当前双核PC/JTAG模式/完整OCM配置/旧初始化状态改变。')
        if require_prior_smoke:
            values['PRIOR_SMOKE_RESULT'] = word('PRIOR_SMOKE_RESULT_GATE', 0x114140)
            values['PRIOR_END_INSTRUCTION'] = word('PRIOR_END_INSTRUCTION_GATE', 0x10AD58)
            if values['PRIOR_SMOKE_RESULT'] != 2 or values['PRIOR_END_INSTRUCTION'] != 0xEAFFFFFE:
                raise RuntimeError('旧smoke成功状态或终点指令未通过。')
        check_uart(required_seconds)
        record['observations'].append({'time': now(), 'gate': 'WARM_OPERATION', 'pc': current_pc,
                                       'readbacks': values, 'require_prior_smoke': require_prior_smoke})

    def halt_cpu0():
        """异常立即停止仍Running的CPU0；已Stopped不重复stop，不恢复任何核。"""
        if 'cpu0' not in cores:
            return False
        value = state('cpu0')
        if value == 'Running':
            call('cpu0.stop', cores['cpu0'].stop)
            if not state('cpu0').startswith('Stopped'):
                raise RuntimeError('异常后的CPU0停止未确认。')
        return value == 'Running'

    # 结果必须先CreateNew预留；所有失败保留实际原文，不能覆盖Run重试。
    with result_path.open('x', encoding='utf-8', newline='\n') as stream:
        try:
            if sys.flags.optimize != 0:
                raise RuntimeError('只接受未优化Python。')
            profile_sha = os.environ.get('S2B_PHYSICAL_PROFILE_SHA256')
            uart_sha = os.environ.get('S2B_UART_IDENTITY_SHA256')
            for value in (profile_sha, uart_sha):
                if not isinstance(value, str) or re.fullmatch(r'[0-9a-fA-F]{64}', value) is None:
                    raise RuntimeError('两项任务专用环境变量必须给出完整64位SHA。')
            record['input_hash_environment'] = {'S2B_PHYSICAL_PROFILE_SHA256': profile_sha, 'S2B_UART_IDENTITY_SHA256': uart_sha}
            record['executed_source_sha256'] = hashlib.sha256(exact_file(Path(__file__)).read_bytes()).hexdigest()
            record['fixed_inputs'] = {name: {'path': str(path), 'sha256': digest} for name, (path, digest) in FIXED.items()}
            for path, digest in FIXED.values():
                verified_bytes(path, digest)
            previous = strict_json(verified_bytes(*FIXED['state_result']))
            if previous['status'] != 'PS_STATE_READBACK_SAVED' or previous['cleanup_errors']:
                raise RuntimeError('本Run前置读回尚未成功并清理完成。')
            record['target_identity_baseline'] = {'path': str(FIXED['state_result'][0]), 'sha256': FIXED['state_result'][1],
                                                 'purpose': '旧r01成功读回仅核对同线缆/目标ctx身份，不证明当前停止状态或本次物理冷启动。'}
            expected_targets = validate_targets(previous['target_properties'])
            prior = strict_json(verified_bytes(*FIXED['prior_result']))
            if (prior['status'] != 'PS_SMOKE_EXECUTION_SAVED' or prior['cleanup_errors'] or
                prior['ps_initialization'] != 'HARDWARE_GATES_SAVED' or prior['smoke_execution'] != 'HARDWARE_GATES_SAVED' or
                prior['final_pc'] != {'cpu0': 0x10AD58, 'cpu1': 0xFFFFFF34} or
                any(not isinstance(prior['final_states'].get(label), str) or not prior['final_states'][label].startswith('Stopped') for label in ('cpu0', 'cpu1'))):
                raise RuntimeError('旧初始化/smoke证据未满足成功、终点及清理条件。')
            for name, key in (('init_elf', 'prior_init_elf'), ('smoke_elf', 'prior_smoke_elf')):
                expected = {'path': str(FIXED[key][0]), 'sha256': FIXED[key][1]}
                if prior['fixed_inputs'][name] != expected:
                    raise RuntimeError('旧实测未使用固定原初始化或smoke ELF。')
            for name, address, value in (('INIT_RESULT', 0x9200, 2), ('INIT_RETURN_CODE', 0x39C0, 0), ('SMOKE_RESULT', 0x114140, 2)):
                rows = [item for item in prior['readbacks'] if item['name'] == name]
                if len(rows) != 1 or type(rows[0]['address']) is not int or rows[0]['address'] != address or type(rows[0]['value']) is not int or rows[0]['value'] != value:
                    raise RuntimeError('旧实测的结果地址/原返回码/状态绑定不符。')
            prior_targets = validate_targets(prior['target_properties'])
            identity_keys = ('target_ctx', 'name', 'parent_ctx', 'jtag_device_ctx', 'jtag_device_name', 'jtag_device_index', 'jtag_cable_ctx')
            if any(prior_targets[name][key] != expected_targets[name][key] for name in prior_targets for key in identity_keys):
                raise RuntimeError('旧成功实测和身份基线目标上下文不一致。')
            record['prior_initialization_provenance'] = {'status': 'REUSED_PRIOR_SUCCESS',
                'result_path': str(FIXED['prior_result'][0]), 'result_sha256': FIXED['prior_result'][1],
                'init_elf_path': str(FIXED['prior_init_elf'][0]), 'init_elf_sha256': FIXED['prior_init_elf'][1],
                'init_result_address': 0x9200, 'init_result': 2, 'init_return_address': 0x39C0, 'init_return_code': 0,
                'executed_init_this_run': False, 'cold_boot_proven_this_run': False}
            check_profile()
            check_uart(150)
            check_server()
            import xsdb
            sdk = xsdb
            session = call('xsdb.start_debug_session', sdk.start_debug_session)
            check_session_options()
            channel = call('session.connect', session.connect, host='127.0.0.1', port=3121, server='hw_server')
            check_server()
            properties = call('session.targets', session.targets, '--target_properties')
            record['target_properties'] = properties
            selected = validate_targets(properties)
            keys = ('target_ctx', 'name', 'parent_ctx', 'jtag_device_ctx', 'jtag_device_name', 'jtag_device_index', 'jtag_cable_ctx')
            for name, target in selected.items():
                if any(target[k] != expected_targets[name][k] for k in keys):
                    raise RuntimeError('当前目标ctx与本Run前置读回不同。')
            for label, name in (('cpu0', 'ARM Cortex-A9 MPCore #0'), ('cpu1', 'ARM Cortex-A9 MPCore #1')):
                target = selected[name]
                obj = call('session.targets', session.targets, id=target['target_id'])
                if vars(obj).get('_ctx') != target['target_ctx'] or vars(obj).get('_id') != target['target_id'] or vars(obj).get('_name') != name:
                    raise RuntimeError('选中的Target对象不符合实际上下文。')
                cores[label] = obj
            cpu0, cpu0_id = cores['cpu0'], selected['ARM Cortex-A9 MPCore #0']['target_id']
            # 按固定包在当前连接内建立停核前提，不依赖旧会话的停止状态。
            record['states_on_selection'] = {label: state(label) for label in ('cpu0', 'cpu1')}
            record['initial_stop_requested'] = []
            for label in ('cpu0', 'cpu1'):
                current_state = state(label)
                if current_state == 'Running':
                    record['initial_stop_requested'].append(label)
                    call(label + '.stop.initial', cores[label].stop)
                stopped = state(label)
                record.setdefault('initial_states_after', {})[label] = stopped
                if not stopped.startswith('Stopped'):
                    raise RuntimeError('当前连接内初始停核未确认：' + label)
            both_stopped()
            initial_pc = {label: pc(label) for label in ('cpu0', 'cpu1')}
            record['initial_gate'] = {'pc': initial_pc, 'initialization': 'REUSED_PRIOR_SUCCESS'}
            operation_gate(0x10AD58, 120, require_prior_smoke=True)
            record['ps_initialization'] = 'REUSED_PRIOR_SUCCESS'
            smoke_attempted = True
            record['smoke_execution'] = 'IN_PROGRESS'
            record['downloads'].append({'time': now(), 'phase': 'smoke', 'path': str(FIXED['smoke_elf'][0]), 'sha256': FIXED['smoke_elf'][1]})
            call('cpu0.dow.smoke', cpu0.dow, file=str(FIXED['smoke_elf'][0]), auto_stop=True, set_entry=True)
            both_stopped()
            if pc('cpu0') != 0x100000 or pc('cpu1') != 0xFFFFFF34:
                raise RuntimeError('smoke ELF下载后的PC不是固定入口。')
            end = add_bp('end', 0x10AD58)
            if bp_status('end_before_con', end, 0x10AD58)['HitCount'] != 0:
                raise RuntimeError('本次新end断点运行前已有命中。')
            operation_gate(0x100000, 120)
            call('cpu0.con.smoke', cpu0.con, '--block', timeout=120)
            both_stopped()
            end_pc = pc('cpu0')
            pc('cpu1')
            smoke_result = word('SMOKE_RESULT', 0x114140)
            end_status = bp_status('end_after_con', end, 0x10AD58, hit=True)
            if end_pc != 0x10AD58 or smoke_result != 2 or end_status['HitCount'] != 1 or pc('cpu1') != 0xFFFFFF34:
                raise RuntimeError('smoke最终PC或已写回DDR结果未通过。')
            check_uart()
            record['smoke_execution'] = 'HARDWARE_GATES_SAVED'
            record['status'] = 'HARDWARE_GATES_SAVED'
        except BaseException as error:
            record.update(status='PS_SMOKE_FAILED', error=repr(error), traceback=traceback.format_exc())
            # 必须先停止本次仍运行的CPU0，再保留诊断，绝不进入下一阶段。
            try:
                halt_cpu0()
            except BaseException as halt_error:
                record['cleanup_errors'].append('CPU0停止：' + repr(halt_error))
            diagnostics = [(label + '_state', lambda label=label: state(label)) for label in cores]
            diagnostics += [(label + '_pc', lambda label=label: pc(label)) for label in cores]
            if 'cpu0' in cores:
                diagnostics += [('reused_init_result', lambda: word('FAILURE_REUSED_INIT_RESULT', 0x9200)), ('reused_init_return_code', lambda: word('FAILURE_REUSED_INIT_RETURN_CODE', 0x39C0))]
            if smoke_attempted:
                diagnostics += [('smoke_result', lambda: word('FAILURE_SMOKE_RESULT', 0x114140))]
            for label, function in diagnostics:
                try:
                    record.setdefault('failure_readbacks', {})[label] = function()
                except BaseException as read_error:
                    record.setdefault('failure_readback_errors', {})[label] = repr(read_error)
            emit({'time': now(), 'event': 'PS_SMOKE_FAILED', 'traceback': record['traceback']})
        finally:
            # 各项清理独立尝试，只移除本次对象；不终止采集/server，不resume/reset。
            if 'cpu0' in cores:
                try:
                    was_running = halt_cpu0()
                    record['final_states'] = {label: state(label) for label in cores}
                    record['final_pc'] = {label: pc(label) for label in cores}
                    if any(not value.startswith('Stopped') for value in record['final_states'].values()):
                        raise RuntimeError('最终两核停止状态不成立。')
                    if record['status'] == 'HARDWARE_GATES_SAVED' and (was_running or record['final_pc'] != {'cpu0': 0x10AD58, 'cpu1': 0xFFFFFF34}):
                        raise RuntimeError('成功门禁后CPU0状态或最终停止PC改变。')
                except BaseException as error:
                    record['cleanup_errors'].append('最终核状态：' + repr(error))
            for bp in owned_bps:
                try:
                    remove_bp(bp)
                except BaseException as error:
                    record['cleanup_errors'].append('本次断点移除：' + repr(error))
            if session is not None and channel is not None:
                try:
                    call('session.disconnect', session.disconnect, chan=channel)
                except BaseException as error:
                    record['cleanup_errors'].append('disconnect：' + repr(error))
            if sdk is not None:
                try:
                    call('xsdb.dispose', sdk.dispose)
                except BaseException as error:
                    record['cleanup_errors'].append('dispose：' + repr(error))
            if record['cleanup_errors']:
                record['status'] = 'PS_SMOKE_FAILED'
            record.update(finished_at=now(), elapsed_seconds=time.monotonic() - started,
                          api_call_count=sum('api' in item for item in record['calls']),
                          host_query_count=sum('host_query' in item for item in record['calls']))
            json.dump(record, stream, ensure_ascii=False, indent=2, default=str)
            stream.write('\n')
            stream.flush()
            emit({'time': now(), 'event': 'PS_SMOKE_RESULT', 'record': record})
    return 0 if record['status'] == 'HARDWARE_GATES_SAVED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
