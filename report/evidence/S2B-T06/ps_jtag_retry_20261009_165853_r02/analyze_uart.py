# 本脚本只核验已关闭采集的原始证据，不连接硬件，也不修改原始日志。
from pathlib import Path
import datetime
import hashlib
import json

RUN = Path(__file__).resolve().parent
RAW = RUN / 'uart_raw.bin'
HW = RUN / 'ps_smoke_result.json'
assert RUN.is_dir() and RAW.is_file() and HW.is_file()
raw = RAW.read_bytes()
hw = json.loads(HW.read_text(encoding='utf-8'))
lines = [
    'BEGIN S2B-T06-1',
    'BUILD c_sha256=d2bb6f0941c2e3765c5a71f889d2e7e1e0428429237f5443510e81cedd16786b xsa_sha256=a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58',
    'UART base=0xE0001000 baud=115200 data=8 parity=N stop=1 flow=NONE clock_hz=0',
    'BUFFER begin=0x01100000 end_exclusive=0x01200000 bytes=1048576 words=262144 align=64 cacheline=32',
    'CONFIG cpu=0 passes=2 patterns=8 words_per_pattern=262144 order=WRITE_DSB_FLUSH_DSB_INVALIDATE_DSB_READ',
]
lines += [f'PATTERN_PASS pass={p} pattern={n} words=262144 mismatches=0'
          for p in range(2) for n in range(8)]
lines += ['PASS passes=2 patterns=8 verified_words=4194304 mismatches=0', 'END S2B-T06-1']
expected = ('\r\n'.join(lines) + '\r\n').encode('ascii')
protocol_ok = raw == expected
capture_text = (RUN / 'uart_capture_stdout.log').read_text(encoding='utf-8-sig')
closed_rows = [json.loads(line[len('CAPTURE_CLOSED '):])
               for line in capture_text.splitlines() if line.startswith('CAPTURE_CLOSED ')]
closed = closed_rows[0] if len(closed_rows) == 1 else None
capture_ok = (closed is not None and closed['captured_bytes'] == len(raw)
              and closed['reason'] == 'stop_flag' and closed['exit_code'] == 0
              and not closed['cleanup_errors'] and not closed['limit_600s_reached'])
reads = {r['name']: r['value'] for r in hw['readbacks']}
hardware_ok = (hw['status'] == 'PS_SMOKE_EXECUTION_SAVED'
               and hw['ps_initialization'] == 'HARDWARE_GATES_SAVED'
               and hw['smoke_execution'] == 'HARDWARE_GATES_SAVED'
               and not hw['cleanup_errors'] and len(hw['downloads']) == 2
               and reads == {'BOOT_MODE': 0, 'OCM_CFG': 24, 'INIT_RESULT': 2,
                             'INIT_RETURN_CODE': 0, 'SMOKE_RESULT': 2}
               and hw['final_pc'] == {'cpu0': 0x0010AD58, 'cpu1': 0xFFFFFF34}
               and all(s.startswith('Stopped') for s in hw['final_states'].values()))
functional_ok = protocol_ok and capture_ok and hardware_ok
record = {
    'schema_version': 1,
    'checked_at_utc8': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
    'status': 'PASS_FUNCTIONAL_WITH_CLOCK_REPORT_DEFECT' if functional_ok else 'FAIL_FUNCTIONAL_CHECK',
    'overall_corrected_version_acceptance': 'NOT_RUN',
    'hardware_gates_ok': hardware_ok,
    'capture_closure_ok': capture_ok,
    'raw_matches_23_line_legacy_protocol': protocol_ok,
    'uart_raw_sha256': hashlib.sha256(raw).hexdigest(),
    'uart_raw_bytes': len(raw),
    'ps_smoke_result_sha256': hashlib.sha256(HW.read_bytes()).hexdigest(),
    'expected_line_count': len(lines),
    'pattern_pass_count': 16 if functional_ok else None,
    'verified_words': 4194304 if functional_ok else None,
    'mismatches': 0 if functional_ok else None,
    'clock_diagnostic': {
        'status': 'FAIL_DIAGNOSTIC_FIELD',
        'reported_clock_hz': 0,
        'generated_driver_config_clock_hz': 100000000,
        'physical_clock_measurement': 'NOT_RUN',
        'cause': '旧应用读取 uart.InputClockHz；实际驱动初始化和波特率计算使用 uart.Config.InputClockHz。',
        'effect': '诊断字段错误；不影响本版本实际 UART 配置或 DDR 检查。原始字节保持不变。',
    },
    'capture_closed_record': closed,
    'limits': [
        '本结果绑定旧源码与旧 ELF；修正版本上板验收另行记录，不能继承该结果。',
        '只验证 1 MiB DDR 区域，不是全容量扫描、长期稳定性或带宽测试。',
        '最后核状态只为会话断开前观测，不是断开后的持续监测。',
        '本项功能结果不代表阶段2B的PS/PL/AXI接口冻结或G4/G5通过。',
    ],
}
with (RUN / 'uart_acceptance.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
with (RUN / 'uart_readable.txt').open('xb') as stream:
    stream.write(raw)
print(json.dumps(record, ensure_ascii=False, indent=2))
raise SystemExit(0 if functional_ok else 2)
