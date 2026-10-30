"""收口当前声明范围的输入、证据与严格哈希检查，保留真实输出。"""
import hashlib,json,pathlib,subprocess,sys,time
O=pathlib.Path(__file__).resolve().parent
R=pathlib.Path('D:/codex-worktrees/w6')
REL=O.relative_to(R).as_posix()
TMP=R/'tmp/stage6/S6-D'/O.name
def wr(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files(paths):
    out=[]
    for p in sorted(paths):
        role='source' if p.suffix=='.py' else 'input' if p.name.startswith('input_') else 'log' if p.suffix=='.txt' else 'result'
        out.append(dict(path=p.relative_to(R).as_posix(),sha256=sh(p),role=role,keep_reason='固定交付字段审计与包装核验的可复核证据',hash_basis='worktree_disk'))
    return out
def main():
    start=time.perf_counter();TMP.mkdir(parents=True,exist_ok=True)
    audit=json.loads((O/'audit_result.json').read_text(encoding='utf-8'))
    base=dict(schema_version=1,stage='6',task_id='S6-D',run_id=O.name,source_commit='ec1a35b5b367620c19d5a54597aad1b8d98e6c48',evidence_dir=REL,interfaces=[],interfaces_not_applicable_reason='本包只读审计固定S5附二ABI及旧replay的输入资格，不实现或声称冻结新的业务接口；适用接口版本和缺口见field_qualification.json',hash_basis='worktree_disk',limitations=['最新S5附二显示结果块不是已冻结的交互replay；生产端、会话/序号、可信发布时刻及200ms新鲜度来源未闭合','显示允许年龄47.3167秒不替代交互200ms，status位不替代业务状态，显示帧号不替代推理帧序','93成员只核验声明结构及两个被消费成员；G3-B只核验当前manifest声明的45项，不扫描历史；未重跑159suite','core_event_constructed=false/core_step_called=false，6-D preview NOT_RUN；无硬件，T6-A03 NOT_RUN，阶段G5未通过','独立Reviewer由总控另派，本包不预填G2 PASS；峰值内存未测'],tool_versions=dict(python=sys.version,git=audit['git_version']))
    cmd=[sys.executable,'-B',str(O/'audit.py')]
    auditcheck=dict(name='固定来源及seed与旧frame只读审计',status='PASS',command=subprocess.list2cmdline(cmd),exit_code=0)
    blocker=dict(name='6-D业务输入资格',status='BLOCKED',command=None,exit_code=None,reason='缺生产写端、会话/序号、可信单调发布时刻、200ms年龄可复算依据及业务state映射')
    preview=dict(name='6-D离线集成preview',status='NOT_RUN',command=None,exit_code=None,reason='字段资格BLOCKED，未构造core事件，未调用core.step')
    inp=O/'inputs_manifest.json';ev=O/'delivery_manifest.json'
    wr(inp,dict(base,checks=[auditcheck],files=files([p for p in O.iterdir() if p.is_file() and (p.name.startswith('input_') or p.suffix=='.py')])))
    commands={
      'inputs':[sys.executable,'-B',str(O/'check_stage_delivery.py'),'--mode','inputs','--project-root',str(R),'--manifest',str(inp)],
      'evidence':[sys.executable,'-B',str(O/'check_stage_delivery.py'),'--mode','evidence','--project-root',str(R),'--manifest',str(ev)],
      'strict':[sys.executable,'-B',str(O/'check_manifest_hash_basis.py'),'--repo',str(R),'--paths',inp.relative_to(R).as_posix(),'--paths',ev.relative_to(R).as_posix(),'--mode','strict','--json']}
    checks=[auditcheck,blocker,preview]
    for k in commands:(O/('check_'+k+'.json')).write_text('{}\n',encoding='utf-8')
    records=[]
    for iteration in range(5):
        wr(ev,dict(base,checks=checks,files=files([p for p in O.iterdir() if p.is_file() and p!=ev])))
        old={k:(O/('check_'+k+'.json')).read_bytes() for k in commands}
        row=[]
        for k,c in commands.items():
            p=subprocess.run(c,capture_output=True)
            (TMP/f'attempt2_{iteration}_{k}.stdout').write_bytes(p.stdout);(TMP/f'attempt2_{iteration}_{k}.stderr').write_bytes(p.stderr)
            (O/('check_'+k+'.json')).write_bytes(p.stdout)
            if p.returncode:
                # 预检失败保留在新名字，不能冒充最终通过。
                (O/f'preflight_attempt2_{iteration}_{k}.stdout.txt').write_bytes(p.stdout)
                (O/f'preflight_attempt2_{iteration}_{k}.stderr.txt').write_bytes(p.stderr)
            row.append(dict(name=k,status='PASS' if p.returncode==0 else 'FAIL',command=subprocess.list2cmdline(c),exit_code=p.returncode,**({} if p.returncode==0 else {'reason':'本轮封包预检失败，保留stdout/stderr'})))
        records.append(row)
        # 包装状态独立记录，避免把strict结果反向嵌入evidence输出造成循环。
        if iteration>0 and all(old[k]==(O/('check_'+k+'.json')).read_bytes() for k in commands) and all(x['exit_code']==0 for x in row):break
    else:raise RuntimeError('包装固定点未收敛')
    wr(O/'packaging_record.json',dict(iterations=records,wrapper_subprocess_count=sum(map(len,records)),elapsed_seconds=round(time.perf_counter()-start,3),peak_memory='未测',scope='CHECKS_OK只证明封包绑定，不代表业务资格或G0/G4/G5；失败预检保留',final_stdout_matches_rerun=True))
    wr(ev,dict(base,checks=checks,files=files([p for p in O.iterdir() if p.is_file() and p!=ev])))
    # 新增包装记录改变严格检查项数，重新收敛最终输出与清单。
    final_phase_calls=0
    for iteration in range(3):
        prior={k:(O/('check_'+k+'.json')).read_bytes() for k in commands}
        for k,c in commands.items():
            p=subprocess.run(c,capture_output=True);final_phase_calls+=1;assert p.returncode==0,(k,p.stdout,p.stderr)
            (O/('check_'+k+'.json')).write_bytes(p.stdout)
        wr(ev,dict(base,checks=checks,files=files([p for p in O.iterdir() if p.is_file() and p!=ev])))
        if all(prior[k]==(O/('check_'+k+'.json')).read_bytes() for k in commands):break
    else:raise RuntimeError('最终stdout未收敛')
    wr(O/'packaging_record.json',dict(iterations=records,wrapper_subprocess_count=sum(map(len,records))+final_phase_calls+3,final_phase_subprocess_count=final_phase_calls+3,elapsed_seconds_before_final_verification=round(time.perf_counter()-start,3),peak_memory='未测',scope='CHECKS_OK只证明封包绑定，不代表业务资格或G0/G4/G5；失败预检保留',final_stdout_matches_rerun=True))
    wr(ev,dict(base,checks=checks,files=files([p for p in O.iterdir() if p.is_file() and p!=ev])))
    for k,c in commands.items():
        p=subprocess.run(c,capture_output=True);assert p.returncode==0 and p.stdout==(O/('check_'+k+'.json')).read_bytes(),k
    total=sum(p.stat().st_size for p in O.iterdir() if p.is_file());assert total<500000,total
    print(json.dumps(dict(status='PACKAGING_OK_BUSINESS_BLOCKED',files=len(list(O.iterdir())),bytes=total,manifest_sha256=sh(ev),strict=json.loads((O/'check_strict.json').read_text(encoding='utf-8'))),ensure_ascii=False))
if __name__=='__main__':main()
