"""只读审查requant实际RTL证据，独立商余数数学与定宽模型，不编译或调用Git。"""
import hashlib,json,random,re,sys,time
from pathlib import Path
import psutil
ROOT=Path(__file__).parents[4];W=Path(__file__).parent;F=ROOT/'report/evidence/S2B-T17/s12_requant_rtl_20261012_r01';T=time.monotonic();used={};checks=[];peak=0
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def use(p,role='input'):
    assert p.is_file();used[p.relative_to(ROOT).as_posix()]=role;return p
def read(p):return json.loads(use(p).read_text(encoding='utf-8'))
def text(p):return use(p,'source' if p.suffix in ('.py','.sv') else 'log').read_text(encoding='utf-8')
def ck(name,value,detail=None):checks.append(dict(name=name,passed=bool(value),detail=detail))
manifest=read(F/'delivery_manifest_r02.json');ck('主manifest冻结',sha(F/'delivery_manifest_r02.json')=='00358f98fe4d2584b5a0d2275fc3f9249b7caeb8d06229145234dc53392fca2d')
ck('当前主清单全部SHA',all((ROOT/r['path']).is_file() and sha(ROOT/r['path'])==r['sha256'] for r in manifest['files']),len(manifest['files']))
mapping=read(F/'restore_mapping.json')['rows'];ck('65 RAW恢复关系',len(mapping)==65 and all((ROOT/r['archive_path']).is_file() and sha(ROOT/r['archive_path'])==r['sha256'] and (ROOT/r['archive_path']).stat().st_size==r['bytes'] for r in mapping))
delivery=read(F/'raw/execute_r01/developer_delivery.json');result=read(F/'raw/execute_r01/result.json')
ck('actual交付/结果冻结',sha(F/'raw/execute_r01/developer_delivery.json')=='8fdd983af602674da44734d34adec66c600ac3fc0ba65f5987c6b51c1ceef173' and sha(F/'raw/execute_r01/result.json')=='f6b0a246819b1c31de3181f2fd9f2218e1106c1836263575986b68ce923ee391')
oldraw=use(F/'raw/full_source/original.sv','source');newraw=use(F/'raw/full_source/candidate.sv','source');ck('完整旧新CONV/当前生产SHA',sha(oldraw)=='51b76623b29a852ebf66cb818ef947d932c14055e4acbb20bd8fe811bb32d555' and sha(newraw)==sha(use(ROOT/'src/s2b_conv_tile_engine.sv','source'))=='c46ed3e1e8af0089b2a78434c0b34869a2b1f5cf11071688345828f4a9c28454')
for filename,rawpath,module in [('rq_original_engine.sv',oldraw,'rq_original_engine'),('rq_candidate_engine.sv',newraw,'rq_candidate_engine')]:
    original=rawpath.read_bytes().decode('utf-8').replace('\r\n','\n');prepared=text(F/'raw/prepare'/filename)
    ck('完整模块仅更名/LF '+module,original.count('module s2b_conv_tile_engine')==1 and prepared==original.replace('module s2b_conv_tile_engine','module '+module,1))
tb=text(F/'raw/prepare/tb_s12_requant.sv');prep=text(F/'raw/prepare/prepare.py');mutanttext=text(F/'raw/prepare/requant_mutants.sv');newsv=text(newraw);oldsv=text(oldraw)
ck('两態白盒/参数0/不声明公开可达',"FROZEN_CONV_DESCRIPTOR(1'b0)" in tb and tb.count(".clk('0)")==2 and 'original_engine.lane_accumulator[0] = accumulator' in tb and 'candidate_engine.lane_accumulator[0] = accumulator' in tb)
ck('独立SV256bit除法余数oracle',all(s in tb for s in ('logic [255:0] numerator, denominator, quotient, remainder','numerator / denominator','numerator % denominator','(remainder << 1) >= denominator','expected_oracle !== expected_file')))
ck('Python商余数参考不调用RTL模型','divmod(abs(acc) * multiplier, 1 << shift)' in prep and 'quotient += int(2 * remainder >= 1 << shift)' in prep)
max_product=(1<<31)*((1<<32)-1)
proof=['signed32绝对值范围0..2^31，32bit二补数求幅值含INT_MIN精确；U32乘积P≤2^63−2^31<2^63。','q=0不加半，R=P；q=1..63时半值≤2^62，P+half<2^64且R<2^63，旧signed64恢复正负没有截断溢出。','q=64半值2^63，P+half<2^64；64bit右移64为0。无限精度商余数也因P<2^63而舍入0。','q=65..255时64bit半值左移超过宽度得到0，右移超过宽度0；无限精度P/2^q<1/2同为0。','二态R≥128当且仅当|R[63:7]为1；否则R0..127，低byte及恢复符号精确。两版均对称饱和到−127..127，不产生−128。','正/负MQ按acc符号独立选择32bit M及完整byte q；acc=0选择正支但结果0。SV256bit分母2^q在q255仍可表示，余数<2^63，翻倍不溢出256bit。']
ck('全域64bit界限',max_product==(1<<63)-(1<<31) and max_product+(1<<63)<(1<<64),dict(max_product=max_product,proof=proof))
def oracle(a,pm,pq,nm,nq):
    # 独立无限精度定义：先整数商，按余数与半分母比较，再恢复符号。
    m,q=(nm,nq) if a<0 else (pm,pq);p=abs(a)*m;d=2**q;whole=p//d;rem=p-whole*d
    r=whole+int(rem*2>=d);return -min(r,127) if a<0 else min(r,127)
def i8(v):return (v+128)%256-128
def fixed(a,pm,pq,nm,nq,mutation=-1):
    m,q=(nm,nq) if a<0 else (pm,pq)
    if mutation==6 and a<0:m,q=pm,pq
    if mutation==5:q&=63
    p=abs(a)*m
    if mutation==3:p&=0xffffffff
    rounding=(1<<(q-1)) if 0<q<=64 else 0
    if mutation==0:rounding=0
    r=((p+rounding)&((1<<64)-1))>>q if q<64 else 0
    if mutation==2:
        return (-127 if a<0 else 127) if r>=256 else i8(-i8(r) if a<0 else i8(r))
    if mutation==1 and r>=128:return -128 if a<0 else 127
    negative=a<0 and mutation!=4
    return (-127 if negative else 127) if r>=128 else i8(-r if negative else r)
hand=[((1,1,1,2,0),1),((-1,1,0,1,1),-1),((-128,3,1,1,0),-127),((127,1,0,9,0),127),((-2147483648,0,255,0xffffffff,0),-127),((-2147483648,1,0,0xffffffff,64),0),((2147483647,0xffffffff,63,0,255),1),((2147483647,0xffffffff,64,0,255),0)]
ck('独立手算半值/INT_MIN/64边界',all(oracle(*inp)==expected==fixed(*inp) for inp,expected in hand))
count=0;bad=0;mutation_hits=[0]*7;legal=0;selected_shifts=set();rng=random.Random(20261012012);randombad=0;randomseen=0
vec=use(F/'raw/prepare/vectors.txt','input')
with vec.open(encoding='utf-8') as f:
    for line in f:
        av,mqv,ev,index=line.split();av=int(av,16);a=av-(1<<32) if av&(1<<31) else av;mq=int(mqv,16);pm=mq>>48;pq=(mq>>40)&255;nm=(mq>>8)&0xffffffff;nq=mq&255;expected=i8(int(ev,16));inputs=(a,pm,pq,nm,nq)
        mathematical=oracle(*inputs);bad+=mathematical!=expected or fixed(*inputs)!=mathematical
        for i in range(7):mutation_hits[i]+=fixed(*inputs,i)!=mathematical
        selected_shifts.add(nq if a<0 else pq);legal+=1<=pm<=0x3fffffff and 1<=nm<=0x3fffffff and pq<=47 and nq<=47
        if count>=118791:
            randomseen+=1
            if randomseen<=10000:regenerated=(rng.randrange(-2**31,2**31),rng.randrange(1,2**30),rng.randrange(48),rng.randrange(1,2**30),rng.randrange(48))
            else:regenerated=(rng.randrange(-2**31,2**31),rng.randrange(2**32),rng.randrange(256),rng.randrange(2**32),rng.randrange(256))
            randombad+=inputs!=regenerated
        if int(index)!=count:bad+=1
        count+=1
        if count%8192==0:peak=max(peak,psutil.Process().memory_info().rss)
ck('实际138791向量独立oracle与定宽模型',count==138791 and bad==0 and selected_shifts==set(range(256)),dict(count=count,mismatches=bad,selected_q_count=len(selected_shifts),legal_both_mq_vectors=legal))
ck('实际20000随机种子/两支合法统计',randomseen==20000 and randombad==0 and legal==19026,dict(seed=20261012012,random_count=randomseen,random_reproduction_mismatch=randombad))
hits=[2080,10649,490,11210,12378,44710,9914];ck('独立七变异数学预期与实际RTL计数一致',mutation_hits==hits,mutation_hits)
log=text(F/'raw/execute_r01/simulation.stdout.log');actualhits=[(int(i),int(n)) for i,n in re.findall(r'MUTANT_SEMANTIC_KILLED id=(\d+) count=(\d+)',log)]
ck('实际RTL输出击杀而非hash拒绝',actualhits==list(enumerate(hits)) and 'S12_REQUANT_FULL_RTL_PASS vectors=138791 mutants=7 mismatches=0' in log and len(re.findall('MUTANT_SEMANTIC_WITNESS',log))==7)
for mut in delivery['semantic_mutants']:
    w=mut['first_witness'];a=int(w['acc_hex'],16);a=a-(1<<32) if a&(1<<31) else a;mq=int(w['mq_hex'],16);inputs=(a,mq>>48,(mq>>40)&255,(mq>>8)&0xffffffff,mq&255)
    ck('独立击杀首个见证 '+mut['name'],fixed(*inputs,mut['id'])==i8(int(w['actual_hex'],16)) and oracle(*inputs)==i8(int(w['oracle_hex'],16)) and fixed(*inputs,mut['id'])!=oracle(*inputs))
for name in ('compile','simulation'):
    native=read(F/'raw/execute_r01'/(name+'.native.json'));ck('实际原生命令 '+name,native['native_exit_code']==0 and native['command']==delivery[name]['command'])
command=delivery['compile']['command'];stderr=text(F/'raw/execute_r01/compile.stderr.log');warnings=sorted(set(re.findall(r'%Warning-([A-Z0-9_]+)',stderr)))
ck('只关闭白盒BLKANDNBLK且诊断保留',[s for s in command if s.startswith('-Wno-')]==['-Wno-fatal','-Wno-BLKANDNBLK'] and '-Wall' in command and '%Error' not in stderr and bool(warnings),dict(retained_warning_classes=warnings,warning_fatality_disabled_for_fixture=True,production_lint_approval=False))
ck('native一次执行范围',delivery['heavy_runs']==1 and delivery['repeat_runs']==0 and delivery['inner_wrapper_native_exit_code']==delivery['outer_guard_exec_native_exit_code']==0)
early=read(F/'raw/early_limits/failure_supplement.json');summary=read(F/'archive_summary.json');ck('早期缺raw与过期NOT_RUN澄清透明',early['new_transcriptions'][0]['raw_stderr'] is False and early['new_transcriptions'][0]['failed_python_native_exit_code'] is None and '原样继承' in delivery['stale_prepare_limitations_in_original_result'] and 'X/Z' in summary['not_run'] and 'private1' in summary['not_run'])
failed=[x['name'] for x in checks if not x['passed']];value=dict(status='CHANGES_REQUIRED' if failed else 'PASS',scope='仅S12 requant二态signed32/U32/byte q数值子检查G2；publicFSM/private1/XZ/STA/109/实物未在本Run验证。',source_commit=manifest['source_commit'],reviewed_manifest_hash=sha(F/'delivery_manifest_r02.json'),reviewed_source_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in (oldraw,newraw,ROOT/'src/s2b_conv_tile_engine.sv')},checks=checks,failures=failed,proof=proof,independent_vector_oracle_count=count,used_inputs=used,elapsed_seconds=time.monotonic()-T,sampled_self_rss_bytes=max(peak,psutil.Process().memory_info().rss),absolute_peak_memory_bytes=None,limits=['独立只读Python数学，不编译RTL、不调用Git/Vivado/硬件或真实任务PID。','完整引擎实际运行只候选参数0，七mutant为源绑定提取组合块，不批准全核心变异覆盖。','BLKANDNBLK仅白盒内部赋值豁免；-Wno-fatal允许fixture警告继续，原诊断完整保留，不构成生产lint通过。','早期原stderr/失败脚本缺失仍未闭合，保存转录不冒充原字节。','891为本次记录源码基线角色；未重新调用Git观测当前HEAD。','采样峰是离散观测，绝对峰未测。'],reviewer_stop='STOP_READ_ONLY_NO_FURTHER_WRITES')
with (W/'review_result.json').open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:value[k] for k in ('status','failures','elapsed_seconds','sampled_self_rss_bytes')},ensure_ascii=False));raise SystemExit(2 if failed else 0)
