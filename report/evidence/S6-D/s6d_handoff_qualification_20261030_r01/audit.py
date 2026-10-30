"""固定交付只读资格审计；不构造交互事件。"""
import datetime, hashlib, importlib.util, json, pathlib, struct, subprocess, sys, time
R=pathlib.Path('D:/codex-worktrees/w6')
M=pathlib.Path('D:/FPGA_Competition')
O=pathlib.Path(__file__).resolve().parent
RUN='s6d_handoff_qualification_20261030_r01'
REL='report/evidence/S6-D/'+RUN
C={'main':'a25ee008bd27ce4b25c003f0ce251e2c8962fc97','w4':'17fe51bbeb90ddeeb5ccc686fa9778ccfc2fdd61','w5':'2decd0dc2e2204ee60dceead4c30f091d039081d','w6':'ec1a35b5b367620c19d5a54597aad1b8d98e6c48'}
G='report/evidence/S5-T01/s5_g3_b_box_p3n_20261030_r01/'
S='report/evidence/S5-T01/s5_p3b_sw_20261030_r01/src/'
F='report/evidence/S5-T04/s5_freeze_20261027_r07/frozen_set.json'
D=['docs/obsidian-project/02-方案设计/阶段5_HDMI显示链G0方案_20261030.md','docs/obsidian-project/02-方案设计/阶段5_显示ABI与帧缓冲布局_20261030.md','docs/obsidian-project/04-提交材料/阶段验收/阶段5_HDMI显示链G3记录_20261030.md']
P=['report/evidence/S5-T03/s5t03_stage4_frozen_replay_20261027_r04/frames.jsonl','report/evidence/S5-T03/s5t03_stage4_positive_replay_20261027_r01/frames.jsonl']
B=[]
calls=0
def sha(b): return hashlib.sha256(b).hexdigest()
def git(root,*args):
    global calls
    calls+=1
    return subprocess.check_output(['git','-c','core.longpaths=true','-C',str(root),*args])
def blob(c,p): return git(M,'cat-file','blob',c+':'+p)
def wr(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def root(t): return M if t=='main' else pathlib.Path('D:/codex-worktrees')/t
def bind(t,p,n):
    b=blob(C[t],p);live=root(t)/p;disk=live.read_bytes() if live.is_file() else None
    (O/n).write_bytes(b)
    B.append(dict(tree=t,commit=C[t],path=p,sha256=sha(b),bytes=len(b),hash_basis='commit_blob',snapshot=REL+'/'+n,live_disk_sha256=sha(disk) if disk is not None else None,live_disk_matches_fixed_blob=disk==b))
    return b
def main():
    start=time.perf_counter()
    assert not (O/'audit_result.json').exists(),'不得覆盖已运行证据'
    observed={t:dict(head=git(root(t),'rev-parse','HEAD').decode().strip(),branch=git(root(t),'branch','--show-current').decode().strip(),status=git(root(t),'status','--short').decode('utf-8')) for t in C}
    docs=[bind('main',p,f'input_doc{i}.md').decode('utf-8') for i,p in enumerate(D)]
    bind('w4',S+'s5_result_abi.h','input_result_abi.h')
    bind('w4',S+'s5_real_source.c','input_real_source.c')
    gm=json.loads(bind('w4',G+'manifest.json','input_g3_manifest.json'))
    assert gm['hash_basis']=='commit_blob'
    members=[]
    for x in gm['items']:
        b=blob(C['w4'],x['path']);ok=sha(b)==x['sha256'] and len(b)==x['bytes']
        members.append(dict(path=x['path'],sha256=sha(b),bytes=len(b),hash_basis='commit_blob',commit=C['w4'],matches=ok))
    assert all(x['matches'] for x in members)
    seed=bind('w4',G+'g3b_seed_src640_80B.bin','input_seed80.bin')
    dump=bind('w4',G+'seed_block_src640_0x20800000.bin','input_dump96.bin')
    slog=json.loads(bind('w4',G+'S5b_seed_block.json','input_seed_block.json'))
    bind('w4',G+'S7_uart_output.txt','input_uart.txt')
    assert len(seed)==80 and len(dump)==96 and seed==dump[:80]
    assert sha(seed)=='a18c58508f5063caa8ecd7d0a57fd96830863088279a712fea4cc70918522b2f'
    assert slog['first80_equal'] and slog['seed80_sha256']==sha(seed) and slog['seed_dump96_sha256']==sha(dump)
    w=struct.unpack_from('<8I',seed)
    assert w[0]==0x53355253 and w[2]==3
    h={n:dict(offset=i*4,value=v,hex=f'0x{v:08X}') for i,(n,v) in enumerate(zip(['magic','frame_id','n_dets','cap_lo','cap_hi','inf_lo','inf_hi','status'],w))}
    det=[]
    for i in range(w[2]):
        v=struct.unpack_from('<4H2BHI',seed,32+i*16)
        d=dict(zip(['x','y','w','h','class_id','score_q8','reserved','pad'],v));d.update(offset=32+i*16,display_score=v[5]/255,display_pct=(v[5]*100+127)//255);det.append(d)
    wr('seed_decode.json',dict(header=h,detections=det,timing=dict(capture_gt_ticks=w[3]|w[4]<<32,inference_done_gt_ticks=w[5]|w[6]<<32,gt_hz_documented=333333343,publication_time=None,monotonic_clock_provenance_proven=False,conversion_to_business_time_performed=False),status_bits=dict(valid=bool(w[7]&1),overrun=bool(w[7]&2),stale_over_one_frame=bool(w[7]&4)),seed80_sha256=sha(seed),dump96_sha256=sha(dump),first80_equal=True,extra16_hex=dump[80:].hex(),extra16_is_fourth_detection=False,source_kind='JTAG写入种子结果块；不是实时推理产物',uart_real_means='显示消费者读取结果块和fixture图；不是生产推理证明',uart_gt_banner_warning='日志字面timer GT 333 Hz与ABI显式333333343不同；不据此补造时基',core_event_constructed=False,core_step_called=False))
    fb=bind('w5',F,'input_frozen_set.json');f=json.loads(fb)
    assert sha(fb)=='4461bbbcd22cf993c4e7bc2985c73f578f16f9996b51e262c6350995c5a8cb4c'
    assert len(f['members'])==f['coverage']['members']==len({m['id'] for m in f['members']})==93
    fm={}
    for m in f['members']:
        if m['scope']!='repo':continue
        if m['kind']=='file':fm[m['path']]=m
        else:
            for x in m['files']:fm[m['path'].rstrip('/')+'/'+x['path']]=x
    cb=bind('w6','verification/s6d_replay_preview_preflight.py','input_classifier.py')
    assert cb==(R/'verification/s6d_replay_preview_preflight.py').read_bytes()
    spec=importlib.util.spec_from_file_location('qualification_classifier',O/'input_classifier.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    old=[]
    for i,p in enumerate(P):
        b=bind('w5',p,f'input_replay{i}.jsonl');disk=(root('w5')/p).read_bytes();x=fm[p]
        assert sha(disk)==x['sha256'] and len(disk)==x['bytes']
        for line in b.decode('utf-8').splitlines():
            if not line.strip():continue
            frame=json.loads(line);q=mod.classify_frame(frame,frame.get('marking',{}));assert q['status']=='BLOCKED'
            old.append(dict(path=p,frame=frame,qualification=q,frozen_member_worktree_disk_matches=True,frozen_member_sha256=x['sha256'],frozen_member_hash_basis='worktree_disk',blob_sha256=sha(b),blob_hash_basis='commit_blob'))
    wr('old_replay_qualification.json',dict(frozen_members_declared=93,frozen_member_ids_unique=True,member_scope='93条声明结构和2个实际消费成员；未重跑159suite及其他221文件',selected_members_checked=2,records=old,classifier_scope='仅旧r07 replay，不用于新binary ABI业务适配'))
    rows=[
      ('geometry','已有','原图640×480，u16xywh，16B步进','input_result_abi.h:18-24；binary0x20/0x30/0x40','后续适配按正式交互坐标规则转换，不直接使用720p显示框'),
      ('class_score','不可直接复用','u8class/score_q8，显示按/255','input_result_abi.h:S5ResultDet；input_real_source.c:S5Real_ScoreToPct','生产方提供五类语义、业务分数含义及冻结映射'),
      ('frame_id','不可直接复用','结果块u32帧号已有；UART frame是显示循环帧号','binary0x04；input_uart.txt:frame=60/120/180','生产方冻结推理帧序、会话复位及回绕规则'),
      ('session_id_result_seq','缺失','32B头无session_id/result_seq','input_result_abi.h:S5ResultHeader；binary0x00..0x1F','推理/解码生产方交付会话与结果序号命名空间'),
      ('capture_time','不可直接复用','cap_lo/hi为GT ticks，种子值不是实测采集时间','binary0x0C/0x10；input_seed_block.json','生产方提供GT实测来源、频率、复位及单调域证明'),
      ('result_time','缺失','inf_lo/hi声明infer_done，无发布时刻及可信result_time_ns','binary0x14/0x18；input_doc1.md:505-511','生产方冻结infer_done到发布语义及同域单调时钟'),
      ('stale_200ms','不可直接复用','status.bit2超1帧；显示允许年龄47.3s+16.7ms','binary0x1Cbit2；input_doc0.md:133；input_result_abi.h:16','提供可重算age_result/age_frame，保持交互200ms'),
      ('business_state','缺失','valid/overrun/stale不等同OK/NO_HAND/ERROR/TIMEOUT','binary0x1C；input_real_source.c:S5Real_Parse','接口责任方冻结业务状态映射及异常优先级'),
      ('producer_delivery','缺失','固定文档明确生产写端尚未实现，仅消费者和JTAG种子','input_doc1.md:511；input_seed_block.json','推理/解码应用提交生产端与可恢复结果证据'),
      ('replay_scope','不可直接复用','旧replay capture0哨兵、result_time/stale=null、PRESENT未到OK','input_replay0.jsonl/1.jsonl；old_replay_qualification.json','交付replay_only范围与真实时间来源，不补造事件'),
      ('hardware_acceptance','不可直接复用','显示G3声称通过；P3n计算回归未跑、不主张G4/G5','input_doc2.md:81/104','显示S6-A..F旧误编号不替代w6交互6A/B/C验收')]
    mat=[dict(field=a,qualification=b,available=c,evidence=d,required_responsibility_input=e) for a,b,c,d,e in rows]
    wr('field_qualification.json',dict(latest_stage5_abi='2026-10-30 lead附二结果块ABI；pure display consumer',stage6_contract='已批准交互200ms及session/frame/result_seq；参数未改',scope='新binary仅字段审计；旧replay单独分类',rows=mat,status='BLOCKED',core_event_constructed=False,core_step_called=False,preview='NOT_RUN'))
    wr('gaps.json',dict(status='BLOCKED',gaps=[x for x in mat if x['qualification']!='已有'],hardware='NOT_RUN',T6_A03='NOT_RUN：缺实测P，47.3s推理耗时不替代P',G5='未通过',independent_review='NOT_RUN；总控另派Reviewer',P3n='VDMA0x43C00000/GPIO0x43C10000，仅记录；无2B/preproc/VTC操作',upstream_state_progress='不采用w4旧交互0%断言覆盖w6当前成果'))
    for n in ['check_stage_delivery.py','check_manifest_hash_basis.py']:
        b=bind('main','verification/'+n,n);assert b==(M/'verification'/n).read_bytes()
    closing={}
    for t in C:
        head=git(root(t),'rev-parse','HEAD').decode().strip();changed=[]
        for x in B:
            if x['tree']==t and sha(blob(head,x['path']))!=x['sha256']:changed.append(x['path'])
        closing[t]=dict(head=head,consumed_paths_changed_vs_fixed=changed)
    wr('source_bindings.json',dict(source_commits=C,observed_live_worktrees=observed,bindings=B,g3_manifest_members=members,g3_manifest_member_count=len(members),fixed_blob_authoritative=True,closing_heads=closing,latest_claim='截至本次收口核验；后续交付变化须重新审计'))
    result=dict(status='BLOCKED',g3_members_verified=len(members),seed_header_fields_decoded=8,seed_detections_decoded=3,seed_dump_first80_equal=True,old_replay_records_classified=len(old),frozen_members_structure_checked=93,frozen_selected_members_checked=2,qualification_fields=len(mat),core_event_constructed=False,core_step_called=False,preview='NOT_RUN',T6_A03='NOT_RUN',G5='未通过',time_utc8=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),elapsed_seconds=round(time.perf_counter()-start,3),peak_memory='未测',git_commands=calls,python_version=sys.version,git_version=git(M,'--version').decode().strip())
    wr('audit_result.json',result);wr('audit_stdout.txt',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
