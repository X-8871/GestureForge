# 仅核验已关闭的原始证据；不连接硬件，不覆盖原始日志。
from collections import Counter
from pathlib import Path
import datetime
import hashlib
import json

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
RAW = RUN / 'uart_raw.bin'
HW = RUN / 'ps_smoke_result.json'
PRIOR = ROOT / 'report/evidence/S2B-T06/ps_jtag_retry_20261009_165853_r02/ps_smoke_result.json'
assert RAW.is_file() and HW.is_file() and PRIOR.is_file()
raw = RAW.read_bytes()
hw = json.loads(HW.read_text(encoding='utf-8'))
prior_bytes = PRIOR.read_bytes()
prior = json.loads(prior_bytes.decode('utf-8'))
lines = [
    'BEGIN S2B-T06-1',
    'BUILD c_sha256=8b4bfcf517c821a7c345ec7af61ebf1eb5120a32cc827c22b2be25887c8edef5 xsa_sha256=a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58',
    'UART base=0xE0001000 baud=115200 data=8 parity=N stop=1 flow=NONE clock_hz=100000000',
    'BUFFER begin=0x01100000 end_exclusive=0x01200000 bytes=1048576 words=262144 align=64 cacheline=32',
    'CONFIG cpu=0 passes=2 patterns=8 words_per_pattern=262144 order=WRITE_DSB_FLUSH_DSB_INVALIDATE_DSB_READ',
]
lines += [f'PATTERN_PASS pass={p} pattern={n} words=262144 mismatches=0'
          for p in range(2) for n in range(8)]
lines += ['PASS passes=2 patterns=8 verified_words=4194304 mismatches=0', 'END S2B-T06-1']
expected = ('\r\n'.join(lines) + '\r\n').encode('ascii')
protocol_ok = raw == expected
capture_text = (RUN / 'uart_capture_stdout.log').read_text(encoding='utf-8-sig')
closed_rows = [json.loads(row[len('CAPTURE_CLOSED '):])
               for row in capture_text.splitlines() if row.startswith('CAPTURE_CLOSED ')]
closed = closed_rows[0] if len(closed_rows) == 1 else None
capture_ok = (closed is not None and closed['captured_bytes'] == len(raw)
              and closed['reason'] == 'stop_flag' and closed['exit_code'] == 0
              and not closed['cleanup_errors'] and not closed['limit_600s_reached'])
reads = Counter((r['name'], r['address'], r['value']) for r in hw['readbacks'])
expected_reads = Counter({
    ('BOOT_MODE_GATE', 0xF800025C, 0): 2,
    ('OCM_CFG_GATE', 0xF8000910, 0x18): 2,
    ('INIT_RESULT_REUSED_GATE', 0x9200, 2): 2,
    ('INIT_RETURN_CODE_REUSED_GATE', 0x39C0, 0): 2,
    ('PRIOR_SMOKE_RESULT_GATE', 0x114140, 2): 1,
    ('PRIOR_END_INSTRUCTION_GATE', 0x10AD58, 0xEAFFFFFE): 1,
    ('SMOKE_RESULT', 0x114140, 2): 1,
})
prior_ok = (hashlib.sha256(prior_bytes).hexdigest() == 'f02143baec914d6436d2fbb672831ea8a9d4aa3c2fda27de37836989809fa8f8'
            and prior['status'] == 'PS_SMOKE_EXECUTION_SAVED'
            and prior['ps_initialization'] == 'HARDWARE_GATES_SAVED'
            and not prior['cleanup_errors'])
bp_rows = hw['breakpoint_status']
bp_ok = len(bp_rows) == 3
for row, name, count in zip(bp_rows, ['end', 'end_before_con', 'end_after_con'], [0, 0, 1]):
    bp_ok = bp_ok and row['name'] == name and len(row['status']) == 1
    for status in row['status'].values():
        bp_ok = (bp_ok and int(status['Address'], 16) == 0x10AD58
                 and status['HitCount'] == count and 'Error' not in status)
hardware_ok = (hw['status'] == 'HARDWARE_GATES_SAVED'
               and hw['ps_initialization'] == 'REUSED_PRIOR_SUCCESS'
               and hw['prior_initialization_provenance']['executed_init_this_run'] is False
               and hw['smoke_execution'] == 'HARDWARE_GATES_SAVED'
               and not hw['cleanup_errors'] and len(hw['downloads']) == 1
               and hw['downloads'][0]['phase'] == 'smoke'
               and hw['downloads'][0]['sha256'] == '9be608b847da26988f42105e2ab856c454d6dd7090c87b7dc95064f4cc05e847'
               and reads == expected_reads and bp_ok and prior_ok
               and hw['final_pc'] == {'cpu0': 0x10AD58, 'cpu1': 0xFFFFFF34}
               and all(s.startswith('Stopped') for s in hw['final_states'].values()))
passed = protocol_ok and capture_ok and hardware_ok
record = {
    'schema_version': 1,
    'checked_at_utc8': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
    'status': 'PASS_UART_DDR_RETEST' if passed else 'FAIL_UART_DDR_RETEST',
    'ps_initialization': 'PRIOR_SUCCESS_REUSED_NOT_RERUN',
    'hardware_gates_ok': hardware_ok,
    'prior_initialization_binding_ok': prior_ok,
    'capture_closure_ok': capture_ok,
    'complete_23_line_raw_protocol_ok': protocol_ok,
    'breakpoint_install_and_one_hit_ok': bp_ok,
    'uart_raw_sha256': hashlib.sha256(raw).hexdigest(),
    'uart_raw_bytes': len(raw),
    'ps_smoke_result_sha256': hashlib.sha256(HW.read_bytes()).hexdigest(),
    'prior_result_sha256': hashlib.sha256(prior_bytes).hexdigest(),
    'pattern_pass_count': 16 if passed else None,
    'verified_words': 4194304 if passed else None,
    'mismatches': 0 if passed else None,
    'reported_config_clock_hz': 100000000 if protocol_ok else None,
    'clock_measurement': 'NOT_RUN',
    'capture_closed_record': closed,
    'limits': [
        '本Run仅重跑修正诊断字段的smoke；真实PS初始化发生在绑定的旧r02，不是本Run重新初始化。',
        '100MHz是BSP软件配置值，不是实测时钟频率。',
        '只验证固定1MiB DDR区域，不是全容量扫描、长期稳定性或带宽测试。',
        '两核停止仅为最后会话内观测，不代表断开后的持续监测。',
        '此实板功能结果不代表阶段2B完整PS/PL/AXI接口或G4/G5验收。',
    ],
}
with (RUN / 'uart_acceptance.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
with (RUN / 'uart_readable.txt').open('xb') as stream:
    stream.write(raw)
print(json.dumps(record, ensure_ascii=False, indent=2))
raise SystemExit(0 if passed else 2)
