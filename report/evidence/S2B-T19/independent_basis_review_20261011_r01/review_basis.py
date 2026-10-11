"""只读核查 T19 官方候选依据及已完成导入原件，不启动任何 SDK 会话。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
root = Path.cwd()
out = Path(__file__).parent
basis = root / 'report/evidence/S2B-T19/official_reset_basis_20261011_r01'
runtime = root / 'report/evidence/S2B-T19/runtime_import_probe_20261011_r01'
start = time.monotonic()
checks = []
commands = []
inputs = []

def digest(path):
    """流式计算实际文件原始字节哈希。"""
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def load(path):
    """严格以 UTF-8 读取 JSON。"""
    return json.loads(Path(path).read_text(encoding='utf-8'))

def bind(path, expected=None):
    """绑定确切文件路径、类型、实际哈希与体积。"""
    path = Path(path)
    valid = path.is_file()
    row = {'path': str(path), 'sha256': digest(path) if valid else None, 'bytes': path.stat().st_size if valid else None}
    inputs.append(row)
    check('文件绑定 ' + str(path), valid and (expected is None or row['sha256'] == expected), row)
    return row

def check(name, valid, detail=None):
    """保存独立核验结果。"""
    checks.append({'name': name, 'status': 'PASS' if valid else 'FAIL', 'detail': detail})

def execute(name, argv, expected):
    """仅执行廉价只读包装检查并保留原生返回码。"""
    begin = time.monotonic()
    result = subprocess.run(argv, cwd=root, capture_output=True)
    (out / (name + '.stdout.log')).write_bytes(result.stdout)
    (out / (name + '.stderr.log')).write_bytes(result.stderr)
    row = {'name': name, 'command': argv, 'native_exit_code': result.returncode, 'elapsed_seconds': time.monotonic() - begin, 'stdout_sha256': digest(out / (name + '.stdout.log')), 'stderr_sha256': digest(out / (name + '.stderr.log'))}
    commands.append(row)
    check(name, result.returncode == expected, row)

names = ['cold_reset_basis_candidate.json', 'hp_visibility_basis_candidate.json', 'sdk_semantic_bindings.json', 'bsp_cache_bindings.json']
frozen_candidates = [bind(basis / name) for name in names]
cold, hp, sdk, bsp = [load(basis / name) for name in names]
check('候选明确未实际执行', cold['hardware_execution'] == hp['hardware_execution'] == bsp['hardware_execution'] == 'NOT_RUN' and sdk['sdk_runtime_execution'] == 'NOT_RUN' and cold['cold_lifecycle_proven'] is False and hp['visibility_proven'] is False)
for row in sdk['files']:
    bind(row['path'], row['sha256'])
    check('SDK 来源字节数 ' + row['path'], Path(row['path']).stat().st_size == row['bytes'])
for key in ['build_details', 'app_elf', 'init_elf', 'app_source']:
    bind(bsp[key]['path'], bsp[key]['sha256'])
for row in bsp['files'].values():
    bind(row['path'], row['sha256'])
build = load(bsp['build_details']['path'])
check('实际构建 ELF 和 app source 绑定', build['elf']['sha256'] == bsp['app_elf']['sha256'] and build['initializer_elf']['sha256'] == bsp['init_elf']['sha256'] and build['source_sha256']['vitis/s2b_inference_app.c'] == bsp['app_source']['sha256'])
target = Path(sdk['files'][1]['path']).read_text(encoding='utf-8')
reset = Path(sdk['files'][2]['path']).read_text(encoding='utf-8')
check('SDK system stop 客户端映射', "def rst(self, *args, type: str = 'system'" in target and "parser.add_argument('-s', '--stop'" in target and "rst_type = 'system'" in target and "argvar.update({'suspend': True})" in target and 'exec_in_dispatch_thread(tcf_reset.rst_cmd, node.id, rst_type, argvar)' in target and 'self.cp.reset(ctx, type, params, self.__DoneHWCommand(sync))' in reset)
check('绑定 JSON 不声称 SDK 服务端执行', sdk['reset_call_contract']['tcf_type'] == 'system' and sdk['reset_call_contract']['tcf_params'] == {'suspend': True} and '不声称服务端实现已执行' in sdk['reset_call_contract']['scope_source'])
cache_path = Path(bsp['files']['xil_cache.c']['path'])
cache = cache_path.read_text(encoding='utf-8')
l1 = cache.split('void Xil_L1DCacheEnable(void)', 1)[1].split('void Xil_L1DCacheDisable(void)', 1)[0]
l2 = cache.split('void Xil_L2CacheEnable(void)', 1)[1].split('void Xil_L2CacheDisable(void)', 1)[0]
check('L1 已启用分支会绕过失效', l1.index('return;') < l1.index('Xil_L1DCacheInvalidate();') < l1.index('CtrlReg |='))
check('L2 仅未启用分支失效并启用', 'if ((L2CCReg & 0x01U) == 0U)' in l2 and l2.index('Xil_L2CacheInvalidate();') < l2.index('L2CCReg | (0x01U)'))
check('BSP 非 AMP 包含 L2 路径', re.search(r'void Xil_DCacheEnable\(void\)\s*\{\s*Xil_L1DCacheEnable\(\);\s*#ifndef USE_AMP\s*Xil_L2CacheEnable\(\);', cache) is not None)
for name in ['bsp_compile_commands.json', 'app_disassembly.log', 'init_disassembly.log']:
    path = root / 'report/evidence/S2B-T15/full_build_20261011_r01' / name
    expected = build['files'][name]['sha256'] if name in build['files'] else next(row['log_sha256'] for row in build['commands'] if Path(row.get('log', '')).name == name)
    bind(path, expected)
compile_commands = load(root / 'report/evidence/S2B-T15/full_build_20261011_r01/bsp_compile_commands.json')
cache_compile = [row for row in compile_commands if Path(row['file']).name in ['xil_cache.c', 'boot.S']]
check('实际缓存及启动编译无 USE_AMP', len(cache_compile) == 2 and all('USE_AMP' not in row['command'] for row in cache_compile))
boot_path = Path(next(row['file'] for row in cache_compile if Path(row['file']).name == 'boot.S'))
bind(boot_path)
boot = boot_path.read_text(encoding='utf-8')
check('实际启动源码存在 SCU/L1/L2 先失效路径', '/*invalidate scu*/' in boot and 'bl\tinvalidate_dcache' in boot and '/* force invalidate */' in boot and boot.index('/* force invalidate */') < boot.index('/* enable the L2 Caches */'))
app_disasm = (root / 'report/evidence/S2B-T15/full_build_20261011_r01/app_disassembly.log').read_text(encoding='utf-8')
init_disasm = (root / 'report/evidence/S2B-T15/full_build_20261011_r01/init_disassembly.log').read_text(encoding='utf-8')
check('实际 ELF 包含启动失效和缓存启用分支', '<invalidate_dcache>' in app_disasm and '<invalidate_dcache>' in init_disasm and '<Xil_DCacheEnable>' in app_disasm and 'bl\t100e3c <Xil_L2CacheInvalidate>' in app_disasm and 'popne\t{r4, r5, r6, pc}' in app_disasm and 'tst\tr4, #4' in app_disasm)
t16 = root / 'verification/s2b_board_jtag.py'
bind(t16, '91bbf5bc8ac5ef9bee37ce6491627a6ac8f38a53b7bba113d1b83447b2ecddf0')
t16_source = t16.read_text(encoding='utf-8')
check('候选 sequence 在既有 T16 操作契约中', 'self.targets["apu"].rst, "--stop", type="system"' in t16_source and 'self.words(0xF800025C, 1)[0] == 0' in t16_source and '"cold_lifecycle_proven": False' in t16_source and 'self.call("fpga.full.compatibility_default", self.targets["fpga"].fpga, file=self.bindings["bit"]["path"])' in t16_source and 'wire.epoch == 0 and wire.abort_pending is None and not wire.sent_requests' in t16_source)
adapter = root / 'src/s2b_hp0_word_adapter.sv'
bind(adapter, '344f5553da157434039ec531ccef83cd74dba9c67533a0b88642438e5b5a8f62')
adapter_source = adapter.read_text(encoding='utf-8')
check('实际 adapter source cache 属性为 0000', "assign m_axi_arcache = 4'd0;" in adapter_source and "assign m_axi_awcache = 4'd0;" in adapter_source)
check('实际 adapter 单笔声明及 AW/W/B 闭合', 'q.held && !q.response_pending && !q.read_active && !q.write_active' in adapter_source and 'q.write_active && d.aw_accepted && d.w_accepted && d.b_seen' in adapter_source)
runtime_manifest = runtime / 'delivery_manifest_r02.json'
bind(runtime_manifest)
rm = load(runtime_manifest)
runtime_before = []
for row in rm['files']:
    runtime_before.append(bind(root / row['path'], row['sha256']))
result = load(runtime / 'runtime_result.json')
native = load(runtime / 'native_execution.json')
check('实际 Vitis 导入边界及测量', result['status'] == native['status'] == 'PASS_RUNTIME_IMPORT_ONLY' and result['python_version'].startswith('3.13.0') and result['pyserial_version'] == '3.5' and native['exit_code'] == 0 and native['elapsed_seconds'] == 3.8267712 and all(result[key] is False and native[key] is False for key in ['session_created', 'connection_attempted', 'serial_opened']))
check('101 实际模块 origin 数量', len(result['loaded_modules']) == 101)
for row in result['loaded_modules']:
    if row['file'] is not None:
        bind(row['file'], row['sha256'])
script = (runtime / 'probe_imports.py').read_text(encoding='utf-8')
check('导入探针脚本无会话创建/连接/打开串口', native['runtime_script_sha256'] == digest(runtime / 'probe_imports.py') == 'e65ed2ddbbc24364fdde70901fa0f745e2c8d74ea5cebd1b92d7a49abc321bd8' and not re.search(r'\.start_debug_session\s*\(|\.connect\s*\(|serial\.Serial\s*\(|\.open\s*\(\s*\)', script))
check('包装 r02 未知与 r03 原生 2 分开保留', load(runtime / 'packaging_attempt_r02.json')['exit_code'] is None and load(runtime / 'packaging_attempt_r03.json')['exit_code'] == 2)
execute('runtime_evidence_packaging', [sys.executable, '-X', 'utf8', '-B', 'verification/check_stage_delivery.py', '--mode', 'evidence', '--manifest', str(runtime_manifest)], 0)
url = hp['sources'][2]['url']
pdf_path = out / 'IHI0022H_amba_axi_protocol_spec.pdf'
download_start = time.monotonic()
pdf_download = {'url': url, 'status': 'NOT_RUN'}
try:
    if not pdf_path.exists():
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read(20_000_001)
            if len(body) > 20_000_000 or not body.startswith(b'%PDF-'):
                raise ValueError('原文 PDF 类型或体积预算异常')
            with pdf_path.open('xb') as output:
                output.write(body)
            pdf_download.update(final_url=response.url, http_status=response.status, content_type=response.headers.get('Content-Type'))
    recovery = load(out / 'curl_download_receipt.json') if (out / 'curl_download_receipt.json').is_file() else None
    pdf_download.update(status='PASS_OFFICIAL_PDF_DOWNLOAD', path=str(pdf_path), sha256=digest(pdf_path), bytes=pdf_path.stat().st_size, TLS_recovery_receipt=recovery)
except Exception as error:
    pdf_download.update(status='FAIL_DOWNLOAD', error=repr(error))
pdf_download['elapsed_seconds'] = time.monotonic() - download_start
(out / 'official_pdf_download.json').write_text(json.dumps(pdf_download,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
check('官方 Arm PDF 原字节来源', pdf_download['status'] == 'PASS_OFFICIAL_PDF_DOWNLOAD', pdf_download)
check('四份被审候选收尾未变', all(digest(row['path']) == row['sha256'] for row in frozen_candidates))
check('实际导入包收尾未变', all(digest(row['path']) == row['sha256'] for row in runtime_before))
if (out / 'curl_download_receipt.json').is_file():
    commands.append(load(out / 'curl_download_receipt.json'))
check('审查基线 HEAD 未变化', subprocess.run(['git','rev-parse','HEAD'],capture_output=True,cwd=root).stdout.decode().strip() == '1f2f9b964135ae6b92ccf557fd3f1de9639c3f46')
semantic_review = [
    {'scope':'UG585 1.15 Debug Resets; Reset Effects Table 1; System Reset Effects Table 1; Non-POR Resets','verdict':'SUPPORTED_CANDIDATE','meaning':'DAP系统调试复位范围与外部系统复位同类；PS FIFO及缓冲复位、PL需要重配置；启动模式保留、原因位累计，外部DDR内容不能推断清零。'},
    {'scope':'UG585 1.15 APU State After Reset Table 1; Reset Signal Sequencing','verdict':'SUPPORTED_CANDIDATE','meaning':'SCU/L2受到系统复位；L1/L2有效性未知，需先失效。BootROM期间外部PS_SRST_B锁定风险不能靠任意引脚操作绕开。'},
    {'scope':'UG585 1.15 AXI_HP Performance Optimization Summary; DDR Controller Core and Transaction Scheduler','verdict':'SUPPORTED_CANDIDATE','meaning':'HP写响应来自DDR/OCM从设备，收响应后发出的事务在该从设备后提交；不是DDR引脚物理持久性保证。DDR调度器考虑写读同址冲突。'},
    {'scope':'ARM IHI 0022H ID040120 PDF第15页/印刷xv; PDF第63页/A4-63; PDF第69页/A4-69; PDF第76页/A4-76','verdict':'SUPPORTED_WITH_EXPLICIT_AXI3_BOUNDARY','meaning':'Part A包含AXI3/4；0000对应不可缓存不可缓冲，映射Device Non-bufferable。AXI4额外设备同ID同slave排序不能套用AXI3；此处还依赖HP具体保证、每次单笔及完整B/R账本。'}
]
required_actual_before = ['独占服务器 PID/启动时间/路径及3121绑定、唯一线缆序列号与同链目标/芯片、双核状态和当前BOOT_MODE=0；非0立即阻断，system reset不能改变已采样boot mode。','固定所有SDK、T16/入口、候选依据、bit/postroute、implemented XSA、实际compiled XSA、ELF/BSP/启动路径哈希；独立runtime compatibility审查另行完成。','系统复位实际capability、TCF调用/原输出/异常，前后BOOT_MODE/REBOOT_STATUS/OCM_CFG/双核PC与Stopped；DBG_RST原已为1不能声称发生上升沿。','核对旧软件、CPU1/其他writer停止以及PS/DDR/互连/PL统一重建路径；复位、cache disable或稳定计数0单项均不能独自发布生命周期证明。']
required_actual_after = ['OCM init实际ready/fail断点、INIT_RESULT=2/return0与PC，完整兼容PL配置成功，再下载固定app；UART先开并原字节保存banner source/XSA绑定。','相同初始化链的L1/L2与SCU启动失效路径、实际缓存控制/内存属性；already-enabled分支可能跳过invalidate，不能仅由Xil_DCacheEnable名字证明。','两phase CPU→DAP flush和DAP→CPU invalidate的不同seed256B原字节、CRC/seq/frame/epoch与前后双完整稳定CSR；epoch0/IDLE_PS/PS owner/head0/账本0，全程没有LOAD或START。','结束后的完整CSR、双核状态、CPU0真实Stopped、串口/断点/会话/自有服务清理结果、命令/原生码/耗时/原文件SHA；失败保存并停止，不补写PASS。','模型部署前arena有效输入/参数重新初始化与缓存所有权交接；最终visibility1新bit/netlist/property及postroute和授权参数差异独审，并以同生命周期模型heads/boxes、异常恢复与1000任务完成真实验收。']
receipt = {'status':'PASS_CANDIDATE_BASIS_ONLY' if all(row['status']=='PASS' for row in checks) else 'CHANGES_REQUIRED','role':'INDEPENDENT_READ_ONLY_REVIEWER','scope':'只确认官方候选依据、SDK/BSP静态绑定与已完成runtime import原件；不审批runtime compatibility或G3/G4/G5','baseline_head':'1f2f9b964135ae6b92ccf557fd3f1de9639c3f46','checked_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':time.monotonic()-start,'hardware_execution':'NOT_RUN','SDK_session_created':False,'serial_opened':False,'cold_lifecycle_proven':False,'visibility_proven':False,'peak_process_tree_memory_bytes':None,'whole_review_wall_time':'NOT_MEASURED','inputs':inputs,'checks':checks,'commands':commands,'review_program_sha256':digest(Path(__file__)),'official_web_log_sha256':digest(out / 'official_web_reads.log'),'official_pdf':pdf_download,'semantic_review':semantic_review,'required_actual_before':required_actual_before,'required_actual_after':required_actual_after,'runtime_import_observed_elapsed_seconds':native['elapsed_seconds'],'recovery_note':'原证书链验证失败的Python下载与首轮审查收据分别保存在official_pdf_download_attempt_r01.json和receipt_attempt_r01.json；Windows curl Schannel默认TLS验证恢复成功，不关闭证书验证。','limitations':['T19/S2仍开发，入口源码未作为稳定独立实现审查对象。','本审查没有执行SDK/TCF/串口或实物动作；成功导入不能证明运行时兼容或缓存/模型通过。','没有把实际导入shell错误1替代原生2；包装失败和未知原生码分别保留。']}
(out / 'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':receipt['status'],'checks':len(checks),'failures':[row for row in checks if row['status']!='PASS'],'elapsed_seconds':receipt['elapsed_seconds'],'receipt_sha256':digest(out / 'receipt.json'),'candidate_bindings':frozen_candidates},ensure_ascii=False,indent=2))
sys.exit(0 if receipt['status']=='PASS_CANDIDATE_BASIS_ONLY' else 2)
