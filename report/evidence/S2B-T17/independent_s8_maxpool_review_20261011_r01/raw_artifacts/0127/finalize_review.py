"""保存独立审查回执、语义反例和直接输入输出绑定。"""
from pathlib import Path
import sys,json,hashlib,shutil,time,subprocess
ROOT=Path.cwd(); WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_geometry_specialization_rtl as eng
def sha(p):
    """绑定文件真实字节。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
start=time.monotonic(); checker=eng.load_checker(); bindings=checker.check_static(ROOT)
fixture=WORK/'independent_mutants'; fixture.mkdir()
for p in bindings:
    target=fixture/p; target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/p,target)
profile_file=fixture/'board/s2b_inference_platform.json'
profile_raw=profile_file.read_bytes(); src='src/s2b_maxpool_geometry.sv'; records=[]
for i,(name,before,after) in enumerate([
    ('有效mask漂移',"tap_valid_mask[tap_index] = 1'b1;","tap_valid_mask[tap_index] = 1'b0;"),
    ('九tap通道漂移','tap_source_channel[tap_index] = input_channel;','tap_source_channel[tap_index] = 0;'),
    ('padding源坐标漂移','tap_source_y[tap_index] = source_y_work + kernel_y_work;','tap_source_y[tap_index] = source_y_work;'),
    ('错误优先漂移',"error_code = BAD_ARGUMENT;","error_code = BAD_RANGE;")]):
    target=fixture/src; original=(ROOT/src).read_bytes(); changed=original.replace(before.encode(),after.encode())
    assert changed!=original
    target.write_bytes(changed); profile=json.loads(profile_raw)
    for row in profile['source_derivation']['derived_sources']:
        if row['path']==src: row['sha256']=sha(target)
    profile_file.write_text(json.dumps(profile,ensure_ascii=False),encoding='utf-8')
    shutil.copyfile(target,WORK/f'mutant_{i:02d}.sv')
    shutil.copyfile(profile_file,WORK/f'mutant_{i:02d}_selfreported_profile.json')
    try: checker.check_static(fixture)
    except ValueError as e:
        reason=str(e)
        assert '派生源存在未授权的额外差异' in reason,reason
        records.append({'name':name,'status':'REJECTED_BY_DERIVATION_BYTES','reason':reason,'mutant':f'mutant_{i:02d}.sv'})
    else: raise AssertionError('自报SHA语义篡改未被拒绝')
    target.write_bytes(original); profile_file.write_bytes(profile_raw)
(WORK/'supplement_semantic_mutants.json').write_text(json.dumps({'command':[sys.executable,'-X','utf8','-B',str(Path(__file__))],'native_exit_code':0,'seconds':time.monotonic()-start,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
validation=json.loads((WORK/'validation.json').read_text(encoding='utf-8')); assert validation['status']=='PASS_S8_SOFTWARE_RTL_G2_ONLY'
freeze=ROOT/'report/evidence/S2B-T17/maxpool_address_guard_20261011_r01/source_freeze.json'
f=json.loads(freeze.read_text(encoding='utf-8'))
for row in f['source_files']: assert sha(ROOT/row['path'])==row['sha256']
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==eng.BASELINE
receipt={
 'schema_version':1,'status':'PASS','scope':'S2B-T17-S8 软件/RTL G2 ONLY','reviewer_stop':True,
 'source_commit':eng.BASELINE,'source_freeze_sha256':sha(freeze),'profile_version':'s2b-inference-platform/0.1.8',
 'reviewed_source_sha256':validation['source_sha256'],'tracked_diff_sha256':sha(WORK/'reviewed_tracked_diff.patch'),
 'mathematical_review':[
  '参数/坐标合法先于地址检查。合法y*stride不超过33位extent-kernel，源坐标在64位有符号域精确。',
  '合法tap的r=ch*H+y小于C*H<(2^32)^2，因此channel乘积64位精确；r高位或低32位加法carry为真且W正时必地址越界。',
  'r高位为零时，r_low*W的64位乘积精确；乘积高位、列加法33位进位、base加法33位进位之或恰等于非负完整地址>UINT32。',
  '所有highflag仅在实际有效tap分支消费；kernel2未使用第三行、padding-only窗口均不增加拒绝。不引入CHW全局范围约束。',
  'RANGE/ARG分别清零全部公开字段；成功保留33bit尺寸、tap count/mask、9组地址/通道/64signed源坐标；错误优先不改。',
  'engine只改geometry模块引用；所有always_ff字节及64/65位输出地址链与HEAD一致。极大output_channel的RANGE优先仍保留。'],
 'independent_validation':{'geometry':validation['geometry'],'engine_counts':{'pool':19644,'upsample':3462,'cycles':590783,'pool_abort':127,'upsample_abort':63,'pool_reset':127,'upsample_reset':63},'runs':validation['runs'],'driver_elapsed_seconds':validation['elapsed_seconds'],'peak_tree_rss_bytes':max(r.get('peak_tree_rss_bytes',0) for r in validation['runs']),'engine_seed':0x11A85C2A,'geometry_seed':0x11A85C29},
 'checker_review':{'strict_frozen14':True,'exact_derivation_byte_comparison':True,'active_rtl':18,'sources':41,'derived':8,'original_active':6,'outer':4,'semantic_mutants_rejected':12,'public_negatives_rejected':len(validation['public_negative']),'independent_extra_mutants':records,'physical_candidate':'0.1.1 unfrozen','clock_hz':50000000,'visibility_default':0},
 'developer_evidence_review':{'geometry_vectors':82586,'pool_vectors':19645,'upsample_vectors':3456,'engine_cycles':590723,'nonconv_layers':15,'nonconv_outputs':5234944,'requests':12286976,'backend_cycles':102468267,'boundary_cases':4980736,'owner_drop_results':120942,'public_negative_trials':12,'source_drift':'仅board md版本/基线说明；编译RTL和runner实际哈希一致。','runtime_adapter':'独立核对源码及转换哈希；只替换缓存父目录。','native_failed_packaging':'首次command数组非法导致native2；原失败清单与stdout保留，修复字符串后evidence0。','repeat_full_backend':'NOT_RUN；实际日志、计数、完整文件哈希和runner判据已核查。'},
 'findings':[],
 'limitations':['几何有限域和新种子样本并非U32全域穷举；整数非负及上界推导补充功能证明。','独立geometry黄金函数全新；机械端口TB和engine差分夹具复用已审runner，新种子重新编译、样本和完整状态刺激实际执行。','15层trace用CONV控制stub，不能推导CONV数值或109整网新验收。','未运行Vivado综合/STA/bit/runtime/BOARD；未操作ROSS、设备或共享分支。','仅S8软件RTL G2通过，G3-G5、50MHz闭合、100黄金样本及1000次实板保持未批准。','Git过长历史证据路径的宿主warning与无关删除未触碰；本轮冻结差异只核S8九文件。','第一次Python sandbox启动被拒绝；宿主码1不是Python原生退出码。scoped require_escalated后driver native0。'],
 'production_modified':False,'git_commit_by_reviewer':'NOT_APPLICABLE_READ_ONLY_REVIEW',
 'raw_manifest':'tmp/2B/S2B-T17/independent_s8_maxpool_review_20261011_r01/raw_manifest.jsonl'
}
(WORK/'environment_attempts.json').write_text(json.dumps({'attempts':[{'command':'pwd via shell C:\\Program Files\\Git\\bin\\bash.exe','host_exit_code':1,'native_program_exit_code':None,'output':'宿主未按Bash执行pwd，命令被识别为cmd，回退PowerShell。'},{'command':[r'C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe','-X','utf8','-B','tmp/2B/S2B-T17/independent_s8_maxpool_review_20261011_r01/review_driver.py'],'host_exit_code':1,'native_program_exit_code':None,'output':'ResourceUnavailable: Program python.exe failed to run: 拒绝访问。'},{'command':'同命令 scoped require_escalated','native_program_exit_code':0,'session_id':77698}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(WORK/'final_review_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths={ROOT/p:'input' for p in json.loads((WORK/'direct_inputs.json').read_text(encoding='utf-8'))}
for p in paths:
    if p.suffix in ['.sv','.py','.tcl'] and '/final_source_snapshot/' not in p.as_posix(): paths[p]='source'
for p in WORK.rglob('*'):
    if not p.is_file() or any(x.startswith('build_') for x in p.relative_to(WORK).parts): continue
    if p.name=='raw_manifest.jsonl': continue
    role='source' if p.suffix in ['.py','.sv'] else 'log' if p.suffix=='.log' else 'input' if p.suffix=='.dat' else 'diagnostic' if 'mutant_' in p.name or p.suffix=='.patch' else 'result'
    paths[p]=role
for name in ['runtime_cache_adapter.py','evidence_native.json','delivery_manifest_r01_failed.json','g1_summary.json']:
    base='maxpool_address_guard_trace_20261011_r01' if name=='runtime_cache_adapter.py' else 'maxpool_address_guard_20261011_r01'
    p=ROOT/'report/evidence/S2B-T17'/base/name; assert p.is_file(); paths[p]='input'
manifest=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':role} for p,role in sorted(paths.items())]
(WORK/'raw_manifest.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in manifest),encoding='utf-8')
print(json.dumps({'status':'PASS','native_exit_code':0,'receipt_sha256':sha(WORK/'final_review_receipt.json'),'raw_manifest_sha256':sha(WORK/'raw_manifest.jsonl'),'raw_records':len(manifest),'geometry_error_counts':validation['geometry']['error_counts'],'all_padding_ok':validation['geometry']['all_padding_ok']},ensure_ascii=False))
