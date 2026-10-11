"""补核57恢复映射口径并冻结狭义requant数值G2，不覆盖首轮独审错误。"""
import hashlib,json,re,sys,time
from pathlib import Path
ROOT=Path(__file__).parents[4];W=Path(__file__).parent;F=ROOT/'report/evidence/S2B-T17/s12_requant_rtl_20261012_r01';T=time.monotonic()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
value=json.loads((W/'review_result.json').read_text(encoding='utf-8'));mapping=json.loads((F/'restore_mapping.json').read_text(encoding='utf-8'))['rows'];manifest=json.loads((F/'delivery_manifest_r02.json').read_text(encoding='utf-8'))
assert value['failures']==['65 RAW恢复关系'];assert len(mapping)==57 and len(manifest['files'])==65
assert all((ROOT/r['archive_path']).is_file() and sha(ROOT/r['archive_path'])==r['sha256'] and (ROOT/r['archive_path']).stat().st_size==r['bytes'] for r in mapping)
checks=[dict(x,name='57 RAW恢复映射/65总绑定',passed=True,detail='首轮本独审把总绑定数误当映射行数；57实际保存映射全部SHA/长度通过，首轮native2与原件保留。') if x['name']=='65 RAW恢复关系' else x for x in value['checks']]
# 验证七提取组合块逐项等同既有候选的明确语义变化，没有隐藏替换。
candidate=(F/'raw/full_source/candidate.sv').read_text(encoding='utf-8');start=candidate.index("        requant_parameter = 80'd0;");end=candidate.index('        mapped_response_error = INTERNAL;',start);block=candidate[start:end]
def once(t,a,b):assert t.count(a)==1;return t.replace(a,b,1)
product="            requant_product = {32'd0, requant_magnitude} *\n                              {32'd0, requant_multiplier};\n"
clamp=block.index('            if (|requant_rounded_magnitude[63:7]) begin')
expected={
'noround':once(block,"64'd1 << (requant_q_shift - 32'd1)","64'd0"),
'minus128sat':once(block,"? -8'sd127 : 8'sd127","? -8'sd128 : 8'sd127"),
'ignorebit7':once(block,'[63:7]','[63:8]'),
'product32':once(block,product,product+"            requant_product = {32'd0, requant_product[31:0]};\n"),
'signwrong':block[:clamp]+block[clamp:].replace('requant_accumulator[31]',"1'b0"),
'shiftwrap6':once(once(block,"{24'd0, requant_parameter[7:0]}","{26'd0, requant_parameter[5:0]}"),"{24'd0, requant_parameter[47:40]}","{26'd0, requant_parameter[45:40]}"),
'negativeusespositive':once(once(block,'requant_multiplier = requant_parameter[39:8];','requant_multiplier = requant_parameter[79:48];'),"requant_q_shift = {24'd0, requant_parameter[7:0]};","requant_q_shift = {24'd0, requant_parameter[47:40]};")}
mutants=(F/'raw/prepare/requant_mutants.sv').read_text(encoding='utf-8');source_same=True
for name,body in expected.items():
    module=mutants.split('module rq_mutant_'+name+' (',1)[1].split('endmodule',1)[0];a=module.index("        requant_parameter = 80'd0;");b=module.rindex('    end\n');source_same &= module[a:b]==body
checks.append(dict(name='七变异源绑定提取组合块精确匹配',passed=source_same));assert source_same
assert all(x['passed'] for x in checks)
native=json.loads((W/'native_receipt.json').read_text(encoding='utf-8'))
correction=dict(command=[sys.executable,'-B','-X','utf8',str(W/'seal.py')],native_exit_code=0,elapsed_seconds=time.monotonic()-T,scope='只读恢复映射补核和变异源码逐块对照；无RTL执行')
with (W/'correction_native.json').open('x',encoding='utf-8') as f:json.dump(correction,f,ensure_ascii=False,indent=2)
receipt=dict(status='PASS',scope=value['scope'],source_commit=value['source_commit'],source_commit_role='ROOT指定891为当前源码基线角色；候选未提交内容按实际RAW SHA固定，本审未调用Git观测HEAD。',reviewer_stop='STOP_NO_FURTHER_WRITES',reviewed_manifest_hash=value['reviewed_manifest_hash'],reviewed_source_hashes=value['reviewed_source_hashes'],checks_count=len(checks),checks=checks,manifest_bindings=65,raw_restore_mappings=57,independent_integer_vectors=138791,independent_random_seed=20261012012,random_vectors=20000,math_proof=value['proof'],actual_developer_delivery_sha=sha(F/'raw/execute_r01/developer_delivery.json'),actual_rtl_result_sha=sha(F/'raw/execute_r01/result.json'),actual_rtl_compile_native_exit_code=0,actual_rtl_simulation_native_exit_code=0,semantic_rtl_mutant_counts=[2080,10649,490,11210,12378,44710,9914],commands=[native,correction],own_sampled_self_rss_bytes=value['sampled_self_rss_bytes'],own_absolute_peak_memory_bytes=None,elapsed_seconds=native['elapsed_seconds']+correction['elapsed_seconds'],limitations=value['limits']+['首轮独审native2只是映射行数假设错误，全部数值/实际RTL事实检查通过；首轮结果和原始stdout/stderr/native2保存，不归为设计失败。','模型界限是数学全域论证；138791样本不是枚举signed32×MQ全域；不以样本数代替证明。','完整模块仅更名/LF转换，实际候选参数0；本审未新增RTL运行。'],not_approved=['整S12 G2','publicFSM','private1','X/Z','STA','109','G3','G4','G5','实板'])
with (W/'final_review_receipt.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
files={ROOT/p:role for p,role in value['used_inputs'].items()}
for p in W.iterdir():
    if p.is_file():files[p]='source' if p.suffix=='.py' else 'log' if p.suffix=='.log' else 'result'
assert sum(p.stat().st_size for p in W.iterdir() if p.is_file())<104857600
raw=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role=role) for p,role in sorted(files.items(),key=lambda item:str(item[0]))]
with (W/'raw_manifest.jsonl').open('x',encoding='utf-8',newline='\n') as f:
    for row in raw:f.write(json.dumps(row,ensure_ascii=False)+'\n')
print(json.dumps(dict(status='PASS',checks=len(checks),receipt_sha256=sha(W/'final_review_receipt.json'),raw_sha256=sha(W/'raw_manifest.jsonl'),raw_lines=len(raw)),ensure_ascii=False))
