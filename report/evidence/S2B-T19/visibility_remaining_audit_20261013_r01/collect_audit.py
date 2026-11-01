"""只读收集当前可见性差距，输出限定审查目录，不执行硬件或设计工具。"""
import hashlib
import json
import platform
import subprocess
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'report/evidence/S2B-T19/visibility_remaining_audit_20261013_r01'
BASE = '6019ed956f0008c4a97b42dc9e0aebb74f31f5c5'
started = time.monotonic()

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def bind(path):
    target = ROOT / path
    if not target.is_file():
        raise ValueError(f'精确文件不存在：{path}')
    raw = target.read_bytes()
    return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

compat_path = 'report/evidence/S2B-T17/implemented_export_independent_20261013_r01/runtime_compatibility_receipt_r01.json'
compat = read(compat_path)
old_path = 'report/evidence/S2B-T19/visibility_gap_audit_20261013_r01/collected_facts.json'
old = read(old_path)
source_bindings = [bind(p) for p in compat['source_sha256']]
matches = {b['path']: b['sha256'] == compat['source_sha256'][b['path']] for b in source_bindings}
assert all(matches.values()), '冻结33源发生变化，停止审查'
inputs = list(old['source_bindings'])
inputs += ['report/evidence/S2B-T19/visibility_gap_audit_20261013_r01/runtime_limits.json',
    'report/evidence/S2B-T19/cache_probe_execution_20261013_r02/summary.json',
    'report/evidence/S2B-T15/full_build_20261011_r01/bsp_compile_commands.json',
    'report/evidence/S2B-T17/implemented_export_independent_20261013_r01/independent_review_receipt_r01.json']
inputs = list(dict.fromkeys(inputs))
bindings = [bind(p) for p in inputs]
supp = read('report/evidence/S2B-T17/implemented_export_independent_20261013_r01/supplement_facts_r01.json')
dcp_path = Path(supp['fixed_pnr_dcp']['path'])
assert dcp_path.is_file(), '冻结DCP精确路径不存在'
dcp_hash = hashlib.sha256(dcp_path.read_bytes()).hexdigest()
assert dcp_hash == supp['fixed_pnr_dcp']['sha256'], 'DCP绑定不符'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
status = subprocess.check_output(['git', 'status', '--short', '--untracked-files=no'], cwd=ROOT, text=True)
save('input_bindings.json', {'schema_version': 1, 'baseline_head': BASE, 'observed_head': head,
    'source_sha256': compat['source_sha256'], 'current_sources_match': matches,
    'inputs': bindings, 'fixed_dcp': dict(supp['fixed_pnr_dcp'], current_sha256=dcp_hash),
    'scope': '仅当前指定索引和直接引用；未全量扫描历史证据',
    'worktree_status': status, 'excluded_changes': ['verification/s2b_board_jtag.py',
        'verification/test_s2b_board_jtag.py', 'verification/test_s2b_visibility_probe.py',
        'vitis/run_s2b_visibility_probe.py']})
plan = {
    'schema_version': 1, 'status': 'NOT_RUN', 'kind': 'bounded-postroute-hp0-query-plan/1.0.0',
    'input': dict(supp['fixed_pnr_dcp']), 'tool': 'Vivado 2026.1 Tcl，仅独占已确认会话或隔离只读会话',
    'preconditions': ['重新核对精确DCP路径及SHA；不得修改/重保存DCP',
        '核对活跃Vivado/重型进程与16GiB资源门禁，证明会话归属；本审查不启动Vivado',
        '新RunId，完整记录Tcl原命令/输出/退出码/版本/用时/采样峰值内存；无重型流程'],
    'budget': {'expected_minutes': '2–5（待测）', 'hard_timeout_seconds': 300,
        'max_ps7_cells': 1, 'max_ps7_pins': 1024, 'max_segments_per_signal': 128,
        'max_leaf_pins_per_signal': 256, 'max_cone_endpoints_per_signal': 256},
    'sequence': [
        {'command': 'open_checkpoint <精确路径，来自input.path>', 'purpose': '加载固定postroute网表，无综合/实现'},
        {'command': 'get_cells -hierarchical -filter {REF_NAME == PS7}', 'purpose': '必须唯一PS7；记录NAME/REF_NAME/LOC'},
        {'command': 'get_pins -of_objects <唯一PS7对象>', 'purpose': '限定枚举actual NAME/REF_PIN_NAME/DIRECTION，找到实际HP0 AR/AW/R/W/B信号，不猜层次名称'},
        {'command': 'get_nets -segments -of_objects <每个实际HP0 ARCACHE/AWCACHE逐bit pin>', 'purpose': '逐bit记录完整segment及leaf driver/load，常量根必须GND/逻辑0，无属性改写者'},
        {'command': 'get_pins -leaf -of_objects <限定segments>; get_cells -of_objects <leaf pins>', 'purpose': '记录REF_NAME/REF_PIN_NAME/DIRECTION；拒绝未追踪段、多个driver及未解释LUT/桥'},
        {'command': '同样逐signal查询HP0 AWVALID/AWREADY/WVALID/WREADY/BVALID/BREADY/BID/BRESP和ARVALID/ARREADY/RVALID/RREADY/RID/RLAST/RRESP',
         'purpose': '核对全部地址/数据/响应路线同属实际PS7 HP0，GP converter不可误当HP桥'},
        {'command': 'all_fanin -flat -startpoints_only -to <HP0 AW/W/AR实际pins>; all_fanout -flat -endpoints_only -from <HP0 B/R实际pins>',
         'purpose': '受数量上限约束，关联adapter声明/接受/响应/账本FF及core；保留受控路径图或数据而非布尔结论'},
        {'command': 'report_property <选中的actual cells/pins/nets>; report_utilization -hierarchical',
         'purpose': '记录模型backend、CONV/MAC/quantizer/route/pool/upsample及状态/输出路径物理保留，不能仅看HWH名或资源总数'}],
    'interpretation': [
        '无早B只指PL路径不自行合成、截留或提前完成最终slave响应；合法AXI3 B可先于AW握手，不能用AXI4 AW-before-B判故障。',
        '完整AW/W/B真实完成与账本闭合是另一个源逻辑/协议审查项；GP STATUS读不是HP写屏障。',
        'PS7内DDR slave提交语义依赖已核官方UG585与AXI3非Bufferable依据；物理连线不证明cache维护或DRAM持久性。',
        '若优化后层次消失，需追踪实际leaf逻辑及启动/HP请求/检测头写路径；无法映射就BLOCKED，不填full_model_core_present=true。',
        'visibility0查询结果只为现有网表事实。visibility1实际新综合实现后重复查询与STA，不复用C0/ECO作为最终模型证明。'],
    'stop_conditions': ['对象缺失/不唯一/超过数量预算', 'DCP哈希变化或未知会话归属',
        '超时/OOM/可用资源越界', '遇到未解释驱动/桥/响应源/属性改写'],
    'hardware_execution': 'NOT_RUN', 'implemented_in_this_audit': False}
save('postroute_query_plan.json', plan)
cold_required = [
    '独占hw_server PID/启动时间/可执行路径/3121及唯一电缆与同链CPU/APU/PL身份；实际BOOT_MODE=0及双核Stopped',
    '冻结bit、DCP、implemented XSA、compiled XSA、ELF、OCM init、BSP/启动/cache/MMU/编译宏、SDK与流程源码SHA',
    'system-stop真实TCF调用/原输出/异常；复位前后BOOT_MODE、REBOOT_STATUS、OCM_CFG、双核PC与Stopped；原因位累积不冒充新上升沿',
    '系统复位作用PS FIFO/缓冲/SCU/L2且PL被复位的官方依据 + 实际EOS0→完整固定bit配置→EOS1/postconfig原始结果；不把单独PL reset、计数0或API返回作为清空旧生命周期',
    '固定OCM init实际ready/fail断点、INIT_RESULT2/return0/PC/DDRC状态；重新下载app与源码/compiled XSA banner原字节',
    '实际启动与BSP L1/L2/SCU初始化路径，already-enabled分支核对；SCTLR/TTBR/实际32个1MiB arena页表项和CSR Device项原观察及无额外alias/其他writer依据',
    '两不同seed256B两phaseCPU/DAP完整原字节、UART header/CRC/seq/frame和DAP写后读回；前后两个完整稳定CSR含epoch0、IDLE_PS、PS owner、HEAD0、ledger0；无LOAD/START',
    'CPU1始终Stopped的真实前后观测及其他DMA/PS writer关闭依据；离散停核观测不能声称连续硬件监控',
    '模型任务前合法输入/全部参数和必要feature重新初始化，专属padding与cache行范围，NOLOAD不等于DDR清零；任务ownership各时点的真实数据与cache交接',
    '结束完整CSR/双核状态，CPU0真Stopped、UART/断点/SDK及自有服务清理；失败原件不改PASS',
    '真实新visibility1位流/网表属性/STA及兼容独审，同生命周期全head/box、109样本、1000连续任务及异常恢复原始证据']
findings = [
    {'id': 'VRA-01', 'priority': 1, 'status': 'BLOCKED', 'location': 'verification/check_s2b_inference_platform.py:551',
     'finding': '指定现有索引未提供实际postroute AxCACHE完整路径与最终HP0响应路径审计。源0000、BD/HWH直连和STA PASS不能充当该证明。',
     'closure': '执行已绑定DCP有限只读查询并由独审核对实际leaf/属性/响应来源；visibility1新网表重复核查'},
    {'id': 'VRA-02', 'priority': 1, 'status': 'BLOCKED', 'location': 'src/s2b_control_csr.sv:238',
     'finding': '当前硬件START准入没有visibility条件，visibility0可启动；参数在src/s2b_control_csr.sv:183/263/330/346门控安全恢复、ACK/安全终态。不能声称START不可达被综合剪除。',
     'closure': '独立核查物理计算启动/HP/输出路径保留；visibility1改变安全逻辑需实际新综合、实现、setup/hold/脉宽/约束审查及固定bit/XSA'},
    {'id': 'VRA-03', 'priority': 1, 'status': 'BLOCKED', 'location': compat_path + ':46',
     'finding': 'full_model_core_present=true在现有收据只证HWH实例及当前33源/PNR源闭包，scope严格visibility0_cache_probe_only；不是实物模型可执行或visibility1安全归还结论。',
     'closure': '限定解释旧收据；新visibility1网表/参数/时序/运行兼容独审及板上实际模型验收'},
    {'id': 'VRA-04', 'priority': 1, 'status': 'BLOCKED', 'location': 'vitis/s2b_inference_app.c:379',
     'finding': '256B探针只覆盖0x10000000起256字节的两master缓存交互；ELF有专属32MiB NOLOAD segment和USE_AMP静态排除，但完整arena真实MMU/cache/CPU1/旧事务冷生命周期不能由这些静态事实推出。r01失败，r02 cache NOT_RUN。',
     'closure': cold_required},
    {'id': 'VRA-05', 'priority': 2, 'status': 'PENDING_TEXT_REBIND', 'location': 'board/s2b_inference_platform.md:37',
     'finding': '证明schema正文版本仍0.1.8，实际JSON/检查器0.1.15；说明文件属于现有33源闭包，本审查未改。',
     'closure': '后续文本修订独审及新33源证明/runtime compatibility重绑定。纯文本修订不要求因此重综合；visibility参数改变则另须新综合实现STA。'}]
save('review_receipt.json', {'schema_version': 1, 'kind': 's2b-visibility-remaining-gap-audit/1.0.0',
    'role': 'INDEPENDENT_REVIEWER', 'status': 'CHANGES_REQUIRED',
    'scope': 'visibility1 G0差距，只读事实核对；非visibility1批准、非G3/G4/G5',
    'baseline_head': BASE, 'observed_head': head,
    'checked_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'source_sha256': compat['source_sha256'], 'source_count': len(source_bindings),
    'existing_evidence_search_scope': inputs, 'global_absence_claimed': False,
    'proved_facts': {'source_closure_33_matches': all(matches.values()),
        'existing_runtime_scope': compat['scope'], 'existing_visibility': compat['visibility_parameter'],
        'fixed_dcp_current_sha256': dcp_hash, 'axcache_source': '0000',
        'bd_hwh_hp0': 'AXI3/64bit/id6/50MHz/infer直连，无BD HP桥；非postroute证明',
        'pnr_sta_visibility0': old['existing_pnr_timing'],
        'runtime_static_arena': '32MiB NOLOAD [0x10000000,0x12000000)；不证明内容初始化/运行时属性',
        'hardware_start_visibility0': '准入没有visibility条件，允许START；默认首次先验禁止发START由入口流程保证',
        'software_entry_visibility0': '只接受visibility0_cache_probe_only兼容收据，只执行op4两phase，不LOAD/START；C应用非硬件visibility参数门禁',
        'axi3_response_rule': '匹配B要求先前W_ACCEPTED、不要求AW_ACCEPTED；保留AW直到握手，AW/W/B三项完成才闭合；允许合法B-before-AW',
        'latest_completed_cache_run': read('report/evidence/S2B-T19/cache_probe_execution_20261013_r02/summary.json')},
    'findings': findings, 'required_cold_gate_raw_observations': cold_required,
    'minimal_next_work': ['根控冻结PC修复后另Run执行真实visibility0 cache/cold并独审原始两phase证据；失败继续保存并诊断',
        '先有限只读DCP HP0属性/响应/计算路径查询，完善hp_path_audit；不重跑旧STA',
        '准确修订板说明版本及重新绑定闭包/兼容/证明；冻结cold/cache/hp G0依据，独审批准参数启用',
        'visibility1授权参数从冻结源重建，执行新综合实现STA/网表审计/bit+implemented XSA与实际ELF兼容审查',
        '同生命周期板上模型heads/boxes/异常恢复/109及1000任务验收；未达到则保持2B受阻'],
    'not_run': ['Vivado/ROSS/SDK导入/串口/板操作', 'postroute查询', 'visibility1构建/模型运行', '大测试/单元测试'],
    'elapsed_seconds': time.monotonic() - started, 'peak_memory_bytes': None,
    'peak_memory_reason': '只读脚本未采样进程树峰值', 'repeat_count': 1,
    'limitations': ['未全量扫描历史证据，不声称仓库全局不存在HP审计',
        '官方语义依据使用SHA核验的既有独审候选与官方PDF绑定；本轮未重新联网或全文解析PDF',
        '4个PC修改归其他Reviewer，未将其作为本轮稳定运行实现批准',
        '父任务可能推进提交；本审查固定33源逐文件SHA，结论不替代后续运行收据',
        '源START可达不证明实际综合后全部数学路径保留，须网表核查；不允许常量ECO冒充visibility1重建']} )
files = [bind(OUT.relative_to(ROOT).as_posix() + '/' + n) for n in
    ('input_bindings.json', 'postroute_query_plan.json', 'review_receipt.json')]
for b in files:
    b.update(role='result', keep_reason='保全限定只读独立差距事实、哈希与未执行查询计划，非硬件通过')
files.append(dict(bind(Path(__file__).relative_to(ROOT).as_posix()), role='input'))
save('delivery_manifest.json', {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T19',
    'run_id': 'visibility_remaining_audit_20261013_r01', 'source_commit': BASE,
    'evidence_dir': OUT.relative_to(ROOT).as_posix(),
    'interfaces': [{'name': '物理候选，未冻结', 'version': 's2b-physical-candidate/0.1.1',
        'frozen': False, **bind('docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md')}],
    'files': files, 'checks': [{'name': '只读当前33源与冻结DCP哈希匹配', 'status': 'PASS',
        'command': [str(Path(__file__)), '静态读取/哈希/受控证据解析'], 'exit_code': 0},
        {'name': 'visibility1 G0证明', 'status': 'BLOCKED', 'reason': '详见review_receipt VRA-01至04；cold/cache与postroute属性审计待执行'},
        {'name': 'Vivado/硬件/大测试', 'status': 'NOT_RUN', 'reason': '本轮限定只读审查'}],
    'tool_versions': {'python': platform.python_version(), 'git': subprocess.check_output(['git','--version'], text=True).strip()},
    'limitations': ['CHANGES_REQUIRED不代表已批准visibility1或通过2B；evidence包装检查不验证接口或硬件语义']})
print(json.dumps({'status': 'CHANGES_REQUIRED', 'head': head, 'sources_match': all(matches.values()),
    'receipt': str(OUT / 'review_receipt.json'), 'elapsed_seconds': time.monotonic() - started}, ensure_ascii=False))
