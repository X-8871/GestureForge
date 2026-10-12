#!/usr/bin/env python3
"""固定独立功能G2范围、原件哈希和真实限制；不修改生产或Git。"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib, json, subprocess

WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[3]

def sha(path):
    """原字节SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    """汇总已经完成的独立验证，保留全部失败尝试。"""
    static=json.loads((WORK/'static_r02/static_receipt.json').read_text(encoding='utf-8'))
    rtl=json.loads((WORK/'rtl_receipt.json').read_text(encoding='utf-8'))
    assert {p:sha(ROOT/p) for p in static['frozen_sha256']}==static['frozen_sha256']
    manifest=ROOT/'report/evidence/S2B-T17/s13_tile_origin_20261012_r01/delivery_manifest.json'
    developer=ROOT/'tmp/2B/S2B-T17/s13_tile_origin_20261012_r01/final_receipt.json'
    assert sha(manifest)=='726df3cb0045f8b2fe4f6911f6f87e0515b1a1d29a4296937b0736614fa59d42'
    assert sha(developer)=='371a20c261091e9c1d508ebf23914226338a74e1f62ca7b8ec51603b4d79798e'
    files=[]
    for relative in ('review_driver.py','artifact_audit.py','finalize_review.py','first_attempt_failure.json',
      'static_r02/static_receipt.json','static_r02/delivery_evidence.native.json','static_r02/delivery_evidence.stdout.bin','static_r02/delivery_evidence.stderr.bin',
      'static_r02/delivery_inputs.native.json','static_r02/delivery_inputs.stdout.bin','static_r02/delivery_inputs.stderr.bin',
      'artifact_audit_receipt.json','rtl_receipt.json','independent_cases.json','independent_compile.native.json','independent_compile.stdout.bin','independent_compile.stderr.bin',
      'independent_simulation.native.json','independent_simulation.stdout.bin','independent_simulation.stderr.bin',
      'rtl/tb_s2b_conv_validation.sv','rtl/validation_vectors.txt','rtl/source/s2a_conv_tile_engine.sv','rtl/source/s2b_conv_tile_engine.sv','rtl/source/s2a_network_descriptor_pkg.sv'):
        p=WORK/relative;assert p.is_file();files.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size))
    result=dict(schema_version=1,status='PASS_G2_FUNCTIONAL_ONLY',reviewer='独立Reviewer，实际gpt-6.1-sol/high',created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
      observed_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=static['frozen_sha256'],profile='s2b-inference-platform/0.1.13',
      developer_manifest=dict(path=manifest.relative_to(ROOT).as_posix(),sha256=sha(manifest)),developer_stop_receipt=dict(path=developer.relative_to(ROOT).as_posix(),sha256=sha(developer)),
      findings=[],scope=[
       '冻结四文件SHA、原14冻结源、18RTL闭包、上游精确派生、相对开发起点467463757158aed80d6f75afadff6a8458614a29仅六项替换、默认私有参数和公开接口保持。',
       '数学：两操作数乘积均64位unsigned随后signed cast；padding和scan零扩展后signed64。加减重组在Z/(2^64)中恒等，最终同signed解释；没有32位乘积或63位缩减。',
       '状态：START锁存描述符并清零tile；VALIDATE成功→PRE，PRE非阻塞登记origin及patch→SCAN。ADVANCE仅换输出组时origin保持；横纵tile变化→PRE→SCAN。tile/stride/pad在消费期均保持。',
       'hard_reset优先于abort、abort优先于case；START只在IDLE且无reset/abort有效；reset/abort/START清零origin。非法描述符→RESULT不消费坐标；下一合法START仍通过PRE。',
       'SCAN保持count结束→padding→地址越界→请求原优先顺序，REQUEST/RESPONSE及后端cancel、首错与结果保持状态未变。公开逐周期包含无效期输出保持值；20状态abort/reset，24种响应交叉与raw80独立重跑。',
       '独立种子722669586的114641数学向量、5个自报SHA及规则篡改反例拒绝；静态派生与声明50MHz/visibility0保持。',
       '独立干净小型单job重建：5996门禁向量+32完整连续任务；seed=19991077(0x1310A25)，stride1–3和非对称padding、输出8–12、请求与响应背压周期改变；808518cycles、162 PRE/47横/44纵/12762clear；compile0及simulation0。',
       '开发all_r03四组PASS和layer0_r01完整数值PASS来源逐一核验。真实编译SRC副本与当前源逐字节相同，五组生成bench与最终generator相同，完整CPU黄金/T25slice/GF8绑定成立。'],
      validation=dict(static_native_exit_code=0,artifact_audit_native_exit_code=0,algebra=static['algebra'],counterexamples=static['counterexamples'],compile_native=rtl['compile'],simulation_native=rtl['simulation'],
       evidence_native_exit_code=0,inputs_native_exit_code=2,inputs_reason='物理候选接口未冻结；非S13功能失败'),
      limitations=[
       '本PASS只批准所列SHA的S13功能G2；不批准50MHz STA/PNR/bit/fullXSA、109整网、cache或板上G3–G5。原S12 -2/50MHz WNS -2.402及91 fail未关闭，须另跑新综合。',
       '没有重复完整layer0重型仿真；核查已有真实全1384448字节零差异结果、公开逐周期、CPU/T25/GF8依据和实际编译SRC绑定；功能变化已用独立小型差分重建。',
       'all_r03 runner SHA312157cd…与layer0_r01/最终SHA5b61f808…不同；唯一差异是layer0附加monitor移除；all_r03总运行FAIL且没有source_sha256_post，不追认统一all通过或不存在快照。',
       'all_r01/r02非法fixture失败、all_r03编译0xC0000005未知原因及独立审查首次过强版本断言native1原件保留。首次外层stderr仅工具原件和精简转录，未另存完整原字节；完整delivery子进程原字节仍保存。',
       '独立RTL监视器复用已核查原完整表达式，与手算及新数学种子另核；新任务外部协议全公开差分无强制内部状态。寄存器组合feature向量是受控内部域，不能单独证明可达性。',
       'Verilator编译使用-Wno-fatal，包含既有warning；本功能G2不等于无warning lint。RSS峰为0.1秒采样进程树峰，不是OS真实全生命周期峰。',
       '仅读取生产与Developer证据；写入限定独立tmp；没有提交、切分支、Vivado、板卡/JTAG或CPU计算控制。'],raw_files=files,no_production_write=True,no_commit=True,stop=True)
    # 种子直接从真实输入原件取值，避免人工转录误差。
    cases=json.loads((WORK/'independent_cases.json').read_text(encoding='utf-8'));result['validation']['public_trace_seed']=cases['seed']
    result['scope'][6]=result['scope'][6].replace('19991077(0x1310A25)',str(cases['seed'])+'(0x1310A25)')
    p=WORK/'final_review_receipt.json'
    with p.open('x',encoding='utf-8',newline='\n') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(dict(status=result['status'],path=p.relative_to(ROOT).as_posix(),sha256=sha(p),compile_seconds=rtl['compile']['elapsed_seconds'],simulation_seconds=rtl['simulation']['elapsed_seconds'],peak_rss=rtl['compile']['peak_tree_rss_sampled_bytes'],public_trace_seed=cases['seed']),ensure_ascii=False))

if __name__=='__main__':main()
