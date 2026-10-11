"""完成独立反例、来源核查与只含必要原件的审查回执。"""
import copy, hashlib, json, math, os, pathlib, re, shutil, struct, subprocess, sys, time
import review as h
import psutil
R,W,E=h.R,h.W,h.E
def main():
    """保留原失败，不改开发者证据或项目源码。"""
    r03=W.parent/'independent_conv_validation_review_20261011_r03'
    assert (r03/'review.py').is_file()
    # 另建run仅重复轻量核验，以实际父进程捕获原生退出码；不重复RTL。
    actual=h.native('audit_r03',[sys.executable,'-B','-X','utf8',str(r03/'review.py'),'audit'],R)
    assert actual['exit_code']==0
    audit=h.js(r03/'audit_result.json');rtl=h.js(W/'independent_rtl_result.json')
    checker=h.load_module('independent_platform_checker',R/'verification/check_s2b_inference_platform.py')
    bindings=checker.check_static(R)
    fixture=W/'checker_fixture';assert not fixture.exists();fixture.mkdir()
    for p in bindings:
        dest=fixture/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/p,dest)
    profile_path=fixture/'board/s2b_inference_platform.json';profile=h.js(profile_path)
    path='src/s2b_conv_tile_engine.sv';raw=h.read(fixture/path)
    cases=[('删除batch拒绝',"(input_batch_count_latched != 32'd1)","(input_batch_count_latched == 32'd0)"),
        ('乘积缩成64位','logic [127:0] input_elements_wide;','logic [63:0] input_elements_wide;'),
        ('结果状态追加owner门禁','if (result_valid && result_ready)','if (result_valid && result_ready && buffer_owner_pl)'),
        ('改变OUTPUT_SCAN比较符','(output_byte_offset_wide >= output_elements_wide)','(output_byte_offset_wide > output_elements_wide)'),
        ('未授权额外常量因子',"input_elements_wide = {96'd0, input_channels_latched} *","input_elements_wide = 128'd2 * {96'd0, input_channels_latched} *")]
    rejected=[]
    for label,before,after in cases:
        assert raw.count(before)==1
        mutated=raw.replace(before,after);(fixture/path).write_text(mutated,encoding='utf-8',newline='\n')
        candidate=copy.deepcopy(profile)
        for row in candidate['source_derivation']['derived_sources']:
            if row['path']==path:row['sha256']=h.sha(fixture/path)
        profile_path.write_text(json.dumps(candidate,ensure_ascii=False),encoding='utf-8',newline='\n')
        try:checker.check_static(fixture)
        except ValueError as exc:rejected.append({'case':label,'self_reported_sha256':h.sha(fixture/path),'status':'REJECTED','reason':str(exc)})
        else:raise AssertionError('checker放行:'+label)
        # 再自报允许替换也必须失败。
        for row in candidate['source_derivation']['derived_sources']:
            if row['path']==path:row['replacements'].append([before,after])
        profile_path.write_text(json.dumps(candidate,ensure_ascii=False),encoding='utf-8',newline='\n')
        try:checker.check_static(fixture)
        except ValueError as exc:rejected.append({'case':label+'且自报允许替换','status':'REJECTED','reason':str(exc)})
        else:raise AssertionError('checker接受自授权:'+label)
    h.save('independent_checker_negatives.json',{'status':'PASS','cases':rejected,'count':len(rejected),'fixture_scope':'只在本审查tmp复制中篡改；被审源码与profile未改。'})
    model_path=R/'report/evidence/S2A-T01/tiny416_model_manifest.json'
    assert h.sha(model_path)=='9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a'
    model=h.js(model_path)['layers'][0]
    gf8=pathlib.Path('D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t02_d2_tiny416_int8_weight_r2/gesture_yolov4_tiny_416_int8_weights.gf8')
    data=gf8.read_bytes();scales=struct.unpack_from('<32f',data,60);biases=struct.unpack_from('<32f',data,188)
    assert list(scales)==model['weight_scale_per_output_channel'] and list(biases)==model['fused_bias_float32_per_output_channel']
    bias_acc=[]
    for scale,bias in zip(scales,biases):
        x=bias/(model['input_scale']*scale);bias_acc.append((-1 if x<0 else 1)*math.floor(abs(x)+.5))
    assert bias_acc==model['bias_accumulator_int32_per_output_channel']
    old=h.js(E/'conv_validation_20261011_r06/validation.json')
    prior=E/'conv_validation_20261011_r07/runner_source_used.py'
    assert old['source_sha256_pre']['verification/test_s2b_conv_validation_rtl.py']==h.sha(prior)
    old_text=h.read(prior);new_text=h.read(R/'verification/test_s2b_conv_validation_rtl.py')
    # 只保留实际函数/全TB/向量逐字符映射；CPU环境差异不进入边界RTL。
    h.save('extra_source_proof.json',{'status':'PASS','r06_runner_sha256':h.sha(prior),'r06_runner_matches_record':True,
        'model_sha256':h.sha(model_path),'gf8_sha256':h.sha(gf8),'gf8_scale_offset':60,'gf8_bias_offset':188,
        'gf8_scales_and_biases_equal_manifest':True,'independent_bias_rounding_equal_manifest':True,'bias_accumulator':bias_acc,
        'd2_source_sha256':h.sha(R/'verification/s1_t02_d2_int8_forward.py'),'d2_git_blob_sha256':hashlib.sha256(h.gitblob(h.BASE,'verification/s1_t02_d2_int8_forward.py')).hexdigest()})
    current={p:h.sha(R/p) for p in audit['source_sha256']};assert current==audit['source_sha256']
    processes=[{'pid':p.pid,'name':p.info['name']} for p in psutil.process_iter(['name']) if p.info['name'] and 'vtb_independent_s4' in p.info['name'].lower()]
    assert not processes
    result={'schema_version':1,'task_id':'S2B-T17-S4-G2','status':'PASS_G2_ONLY','created_utc8':time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
        'task_baseline_commit':h.BASE,'observed_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
        'developer_delivery_manifest':{'path':'report/evidence/S2B-T17/conv_validation_20261011_r15/delivery_manifest_r02.json','sha256':'0fcec217510cccca8e79ce9ff312ccfea60f8cf520c4fcd647857cae5080ed06'},
        'developer_source_freeze':{'path':'report/evidence/S2B-T17/conv_validation_20261011_r15/source_freeze.json','sha256':'d8f2af3f6ac243267c12d9a8ca1b8559b0ff1e69054492b4eab50dcdee62a846'},
        'source_sha256':current,'findings':[],
        'scope':'S4 CONV两项128位batch乘积化简及backend引用/profile0.1.4的独立软件等价G2。针对正常复位后的已定义二进制公开API；不以强制内部损坏或四态X/Z传播作为物理API。',
        'inductive_proof':[
            {'source':'src/s2a_conv_tile_engine.sv','lines':[164,165,260,264,314,315,341,344],'argument':'独立逐字符重建确认仅模块名和两个batch因子删除。原每项因子零扩展到128位，四个UINT32最大值乘积小于2^128，不存在原128位溢出；新三因子也不溢出。batch均1时整个128位乘积完全相同，32位上界比较和低32位长度比较保留。'},
            {'source':'src/s2a_conv_tile_engine.sv','lines':[311,314,315,328,331,333,341],'argument':'任一batch不是1，原首if必真，新首if逐字符相同，input/output宽乘积不参与此分支。层号越界或weight层号不匹配仍优先BAD_RANGE，其余BAD_ARGUMENT；包括batch0/2/UINT32_MAX与其他错误交叉，不依赖模型维度。'},
            {'source':'src/s2a_conv_tile_engine.sv','lines':[648,654,780,786,828,831,1043,1059,1068,1104,1131],'argument':'两batch锁存仅reset与IDLE的START握手赋值。ST_VALIDATE失败直接RESULT，成功才能TILE_PREP；OUTPUT_SCAN仅来自通过校验后的REQUANT与自身OUTPUT_RESPONSE回环。运行中端口变化不能修改锁存，abort回IDLE、reset清零、非法状态到RESULT不绕过成功校验。故OUTPUT_SCAN必持有两个batch1，output宽乘积亦相同。'},
            {'source':'src/s2b_conv_tile_engine.sv','lines':[1],'argument':'其余所有组合/时序文本完全相同。以reset相同状态为基、每周期相同外部输入归纳，修改节点在所有可消费位置相等，下一状态/全部公开输出相同。因此请求地址/INT8/Q31/背压/owner/abort/reset、错误优先和周期延迟均不变。实际双RTL和数学边界作为该归纳论证的独立验证。'}],
        'evidence_checks':{'independent_binding_checks':len(audit['checks']),'independent_checker_negatives':len(rejected),'source_files':37,'developer_files':197,'frozen2a_files':14,
            'independent_full_layer0_cpu_bytes':1384448,'independent_cpu_mismatches':0,'r10_real_rtl_bytes':1384448,'r10_real_rtl_cycles':27235743,
            'r10_evaluation':'审阅实际TB所有写请求选中字节!==T25对应字节即fatal、禁止重复、末尾全部seen覆盖及req/rsp等计数；源/TB/夹具/日志绑定准确，成功标记只能在所有检查之后。非仅digest或Developer文字自报。',
            'r06_mapping':'r06 runner实际SHA=保存的r07 runner副本，7个相关函数源码全文、生成TB、向量文本与当前一致；r06/r10实向量raw相同。CPU环境/采样变更不影响边界仿真。',
            'nonconv':'r11 pool19645/up3456、r12 direct15816/query4592720、r13 15层5234944输出/12286976请求已核对实际源码与原始日志；r13逐层cycles/count/digest与S3原日志一致。'},
        'independent_rtl':{'status':'PASS','hand_cases':36,'nonzero_synthetic_output_bytes':512,'requests':560,'cycles':21256,'all_public_output_comparison_cycles':21256,'response_errors':21,'raw80':1,'abort_states':20,'reset_states':20,'command_receipts':['independent_compile_native.json','independent_simulation_native.json'],'peak_tree_rss_bytes':rtl['commands'][0]['peak_tree_rss_bytes'],'cache_bytes':rtl['commands'][0]['cache_bytes']},
        'stage_checkers':{'evidence_exit_code':0,'inputs_exit_code':2,'inputs_reason':'物理接口0.1.1尚未冻结、G2/STA/109G3依赖声明NOT_RUN；包装通过不代表验收。'},
        'preserved_review_failure':{'path':str(W.parent/'independent_conv_validation_review_20261011_r01/audit_failure.json'),'reason':'审查脚本错误地要求r11状态等于普通PASS；原为精确PASS_GEOMETRY_SPECIALIZATION_G1。r01原脚本和失败JSON保留，r02/r03使用各run精确状态值后核验通过；与生产设计无关。','initial_native_exit_capture':'首轮工具输出含真实Python异常，但未将退出码字段持久化；不补造该码。'},
        'limitations':[
            '仅S4软件等价G2；未证明50MHz时序收敛，S3 WNS -18.745ns失败保持，S4综合/STA由总控后续执行。',
            '未重跑109新闭包整网、CSR/runtime计时器整core、postroute、bit、板上模型或G3/G4/G5。按修改影响，精确三替换及全API归纳证明配合边界/整layer0/非conv回归足以支持此G2范围。',
            '继承S3 ROUTE通用合法groups>=3与原2A非等价限制；该范围不适用tiny416冻结ROM可达profile，不能扩大为ROUTE全域等价。',
            'physical0.1.1仍未冻结、clock50MHz及visibility0保持；不审批实物身份、cache或部署。',
            'Developer r02预算/r03oracle宽度/r04单点夹具/r08换行门禁/r09线程门禁/r14包装/r15首次未声明文件失败保留且未判成设计失败；r07CPU线程限制证据不足不取代r10实际getter和线程计时。',
            '未保存完整layer0逐周期波形/输出dump；r10实际逐写字节断言、seen完整性、固定输入输出原文件和日志可重放。独立本轮保存小型数学黄金与TB，未复制大T25shard或构建缓存。',
            '工具调用量及全系统峰值内存未测；RTL树RSS以0.1秒采样、CPU进程OS峰为保守上界。'],
        'heavy_slot_released':True,'own_heavy_processes_remaining':processes,'git_commit':'Reviewer不提交，交由总控核对后提交。'}
    h.save('review_receipt.json',result)
    # 只选择审查自身的小型脚本、JSON、原始日志和独立TB；缓存/复制fixture不归档。
    files=[]
    for directory in (W.parent/'independent_conv_validation_review_20261011_r01',W,r03):
        for p in sorted(directory.iterdir()):
            if p.is_file() and p.suffix in ('.py','.json','.log','.sv'):
                files.append({'path':str(p.relative_to(R)).replace('\\','/'),'sha256':h.sha(p),'bytes':p.stat().st_size})
    h.save('raw_delivery_manifest.json',{'schema_version':1,'task_id':'S2B-T17-S4-G2','status':'PASS_G2_ONLY','files':files,'total_bytes':sum(p['bytes'] for p in files),'excluded':'obj_dir/、checker_fixture/、大T25/GF8/输入复制均不归档；manifest自身由总控单独纳入。'})
    print(json.dumps({'status':result['status'],'receipt':str(W/'review_receipt.json'),'receipt_sha256':h.sha(W/'review_receipt.json'),'raw_manifest':str(W/'raw_delivery_manifest.json'),'raw_manifest_sha256':h.sha(W/'raw_delivery_manifest.json'),'files':len(files),'bytes':sum(p['bytes'] for p in files)},ensure_ascii=False))
if __name__=='__main__':main()
