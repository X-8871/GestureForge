"""独立小型双RTL：手算边界、非零INT8数据及公开握手扰动。"""
import json, math, os, re, shutil, subprocess, sys, time
import review as h
import psutil
R,W=h.R,h.W

def prepare():
    """根据公开端口声明接线；输入和黄金不调用开发向量生成器。"""
    original=h.read(R/'src/s2a_conv_tile_engine.sv').split(');',1)[0]
    ports=re.findall(r'\b(input|output)\s+logic\s*((?:signed\s*)?(?:\[[^\]]+\])?)\s*(\w+)',original)
    incoming=[n for d,w,n in ports if d=='input']
    outgoing=[n for d,w,n in ports if d=='output']
    skip={'clk','hard_reset','abort','start_valid','backend_req_ready','backend_rsp_valid','backend_rsp_rdata','backend_rsp_error','result_ready'}
    base={n:0 for n in incoming if n not in skip}
    base.update(buffer_owner_pl=1,input_base_address=0x1003,input_length_bytes=16,input_batch_count=1,input_channels=1,input_height=4,input_width=4,
        output_base_address=0x3001,output_length_bytes=512,output_batch_count=1,output_channels=32,output_height=4,output_width=4,
        kernel_height=1,kernel_width=1,stride_y=1,stride_x=1,groups=1,weight_package_base_address=0x2001,weight_package_length_bytes=128,
        quantized_weight_offset=4,quantized_weight_bytes=32,activation_mode=1)
    vectors=[]
    def add(label,updates,expected):
        values=dict(base);values.update(updates);vectors.append({'name':label,'values':values,'expected':expected})
    add('合法独立小层',{},0)
    for field in ('input_batch_count','output_batch_count'):
        for n in (0,2,0xffffffff):
            add(field+str(n),{field:n},1)
            add(field+str(n)+'长度错仍BAD_ARGUMENT',{field:n,'input_length_bytes':0},1)
            add(field+str(n)+'层号错优先BAD_RANGE',{field:n,'weight_layer_index':1},2)
    for field,length in (('input_base_address',16),('output_base_address',512),('weight_package_base_address',128)):
        for delta in (-1,0,1):add(field+'顶界'+str(delta),{field:(1<<32)-length+delta},2 if delta>0 else 0)
    add('input32位乘积回绕仍拒绝',{'input_height':65536,'input_width':65536,'input_length_bytes':0},3)
    add('output32位乘积回绕仍拒绝',{'output_height':65536,'output_width':65536,'output_length_bytes':0},3)
    add('input大乘积保留128位',{'input_height':0xffffffff,'input_width':0xffffffff,'input_length_bytes':1},3)
    add('output大乘积保留128位',{'output_height':0xffffffff,'output_width':0xffffffff,'output_length_bytes':32},3)
    add('inputbatch零不能掩盖大乘积',{'input_batch_count':0,'input_height':0xffffffff,'input_width':0xffffffff,'input_length_bytes':0},1)
    add('owner校验低',{'buffer_owner_pl':0},1)
    add('outputbatch索引非零',{'output_batch':1},1)
    add('MQ通道长度错',{'output_channels':31,'output_length_bytes':496,'quantized_weight_bytes':31},2)
    model=h.js(R/'report/evidence/S2A-T01/tiny416_model_manifest.json')['layers'][0]
    feature=[(i*17)%255-127 for i in range(16)]
    weight=[(i*13)%255-127 for i in range(32)]
    gold=[];math_rows=[]
    for c in range(32):
        for index in range(16):
            acc=feature[index]*weight[c]+model['bias_accumulator_int32_per_output_channel'][c]
            val=acc*(float(model['input_scale'])*float(model['weight_scale_per_output_channel'][c]))/float(model['output_scale'])
            if val<0:val*=.1
            q=max(-127,min(127,(-1 if val<0 else 1)*math.floor(abs(val)+.5)))
            gold.append(q&255)
            if index in (0,15):math_rows.append({'channel':c,'index':index,'input':feature[index],'weight':weight[c],'bias':model['bias_accumulator_int32_per_output_channel'][c],'accumulator':acc,'scaled':val,'int8':q})
    h.save('hand_vectors.json',vectors)
    h.save('synthetic_oracle.json',{'method':'逐点Python整数点积，加冻结manifest偏置；D2 binary64两步量化；不使用生产MQROM','feature':feature,'weight':weight,'golden_bytes':gold,'hand_points':math_rows,'golden_byte_count':len(gold),'model_sha256':h.sha(R/'report/evidence/S2A-T01/tiny416_model_manifest.json')})
    decl='\n'.join(f'logic {w} {n}=0;' for d,w,n in ports if n!='clk')
    decl+='\n'+'\n'.join(f'logic {w} new_{n};' for d,w,n in ports if d=='output')
    old='s2a_conv_tile_engine old('+','.join(f'.{n}({n})' for d,w,n in ports)+');'
    new='s2b_conv_tile_engine candidate('+','.join(f'.{n}('+('new_' if d=='output' else '')+n+')' for d,w,n in ports)+');'
    compare=' || '.join(f'{n} !== new_{n}' for n in outgoing)
    defaults=' '.join(f"{n}=32'h{v:x};" for n,v in base.items())
    hand='\n'.join('reset_all; defaults; '+' '.join(f"{n}=32'h{v:x};" for n,v in row['values'].items() if base[n]!=v)+f' validate_case({row["expected"]});' for row in vectors)
    bench='''`timescale 1ns/1ps
module tb_independent_s4;
logic clk=0;
__DECL__
__OLD__
__NEW__
integer ticks=0,checked=0,hand_count=0,pending=0,delay_left=0,requests=0,writes=0;
integer inject_class=-1,inject_error=0,inject_raw=0,abort_mask=0,reset_mask=0,error_cases=0;
logic [31:0] response_word=0;
logic [2:0] response_error=0;
logic [511:0] seen=0;
localparam logic [7:0] golden[0:511]='{__GOLD__};
always #5 clk=~clk;
always @(negedge clk) begin
 if(__COMPARE__) $fatal(1,"独立原新公开口比较失败tick=%0d",ticks);
 checked++;
end
task automatic tick;begin @(posedge clk);#1;ticks++;@(negedge clk);#1;end endtask
task automatic defaults;begin __DEFAULTS__ end endtask
task automatic reset_all;begin
 hard_reset=1;abort=0;start_valid=0;result_ready=0;backend_req_ready=0;backend_rsp_valid=0;backend_rsp_error=0;
 pending=0;delay_left=0;requests=0;writes=0;seen=0;inject_class=-1;inject_error=0;inject_raw=0;tick;hard_reset=0;tick;
end endtask
task automatic launch;begin start_valid=1;tick;start_valid=0;end endtask
task automatic validate_case(input integer expected);begin
 launch;tick;
 if(expected!=0)begin
  if(!result_valid || result_error_code!=expected || backend_req_valid)$fatal(1,"手算校验失败n=%0d want=%0d got=%0d",hand_count,expected,result_error_code);
  repeat(3)begin tick;if(!result_valid || result_error_code!=expected)$fatal(1,"错误结果不保持");end
  result_ready=1;tick;result_ready=0;
 end else begin if(result_valid)$fatal(1,"手算合法拒绝n=%0d error=%0d",hand_count,result_error_code);abort=1;tick;abort=0;end
 hand_count++;
end endtask
task automatic service;
logic accepted,responded;logic[31:0] req_addr,req_data;logic[3:0] rsel,wsel;logic wr;
integer address,index,category,bytevalue;
begin
 backend_req_ready=(ticks%7)!=1 && (ticks%7)!=2;
 backend_rsp_valid=pending!=0 && delay_left==0;
 backend_rsp_rdata=response_word;backend_rsp_error=response_error;
 #1;accepted=backend_req_valid && backend_req_ready;responded=backend_rsp_valid;
 req_addr=backend_req_addr;req_data=backend_req_wdata;rsel=backend_req_rstrb;wsel=backend_req_wstrb;wr=backend_req_write;
 tick;
 if(responded)pending=0;else if(pending!=0 && delay_left>0)delay_left--;
 if(accepted)begin
  if(pending!=0)$fatal(1,"独立服务多pending");
  requests++;pending=1;delay_left=ticks%4;response_word=0;response_error=0;
  if(wr)begin
   if(rsel!=0 || $countones(wsel)!=1)$fatal(1,"写strobe错误");
   category=2;
   for(integer lane=0;lane<4;lane++)if(wsel[lane])begin
    address=int'(req_addr)+lane;index=address-32'h3001;
    if(index<0 || index>=512)$fatal(1,"输出地址范围错误");
    if(seen[index])$fatal(1,"输出地址重复");
    if(req_data[lane*8+:8]!==golden[index])$fatal(1,"独立D2数学输出错idx=%0d expected=%0d got=%0d",index,golden[index],req_data[lane*8+:8]);
    seen[index]=1;writes++;
   end
  end else begin
   if(wsel!=0 || $countones(rsel)!=1)$fatal(1,"读strobe错误");
   category=-1;
   for(integer lane=0;lane<4;lane++)if(rsel[lane])begin
    address=int'(req_addr)+lane;
    if(address>=32'h1003 && address<32'h1013)begin category=0;index=address-32'h1003;bytevalue=(index*17)%255-127;end
    else if(address>=32'h2005 && address<32'h2025)begin category=1;index=address-32'h2005;bytevalue=(index*13)%255-127;end
    else $fatal(1,"独立读地址错误addr=%x",address);
    response_word[lane*8+:8]=inject_raw!=0 ? 8'h80 : 8'(bytevalue);
   end
  end
  if(category==inject_class)response_error=3'(inject_error);
 end
end endtask
task automatic run_result(input integer expected);
integer watchdog;
begin
 launch;tick;
 // 已通过VALIDATE后改变公开描述符与owner，内部锁存必须保持。
 input_batch_count=32'hffffffff;output_batch_count=0;input_base_address=0;output_base_address=0;buffer_owner_pl=0;
 watchdog=0;
 while(!result_valid && watchdog<20000)begin service;watchdog++;end
 if(!result_valid || result_error_code!=expected)$fatal(1,"独立结果错误want=%0d got=%0d",expected,result_error_code);
 if(expected==0 && (writes!=512 || seen!={512{1'b1}} || pending!=0))$fatal(1,"输出覆盖不全writes=%0d",writes);
 repeat(5)begin service;if(!result_valid || result_error_code!=expected)$fatal(1,"背压结果未保持");end
 result_ready=1;service;result_ready=0;
 if(busy || result_valid || !start_ready)$fatal(1,"结果ACK不回IDLE");
end endtask
initial begin
 __HAND__
 reset_all;defaults;run_result(0);
 $display("PASS_SYNTHETIC bytes=512 requests=%0d nonzero_data=1 descriptor_poison=1 owner_drop=1",requests);
 for(integer cls=0;cls<3;cls++)for(integer code=1;code<8;code++)begin
  reset_all;defaults;inject_class=cls;inject_error=code;run_result(code==1?1:code==2?2:6);error_cases++;
 end
 reset_all;defaults;inject_raw=1;run_result(1);
 for(integer action=0;action<2;action++)for(integer state_id=0;state_id<20;state_id++)begin
  integer watchdog;
  reset_all;defaults;if(state_id!=0)launch;watchdog=0;
  while(int'(old.state)!=state_id && watchdog<20000)begin service;watchdog++;end
  if(watchdog==20000)$fatal(1,"独立状态不可达%0d",state_id);
  // 只读定位实际可达状态；取消时故意同沿给READY/RSP。
  backend_req_ready=1;backend_rsp_valid=1;backend_rsp_error=3'd7;
  if(action==0)begin abort=1;abort_mask|=1<<state_id;end else begin hard_reset=1;reset_mask|=1<<state_id;end
  tick;abort=0;hard_reset=0;backend_rsp_valid=0;pending=0;tick;
  if(busy || result_valid || !start_ready)$fatal(1,"独立取消/复位未回IDLE");
 end
 $display("PASS_INDEPENDENT_S4 hand=%0d cycles=%0d compare_cycles=%0d response_errors=%0d raw80=1 abort_mask=%x reset_mask=%x",hand_count,ticks,checked,error_cases,abort_mask,reset_mask);
 $finish;
end
endmodule
'''
    for a,b in [('__DECL__',decl),('__OLD__',old),('__NEW__',new),('__COMPARE__',compare),('__DEFAULTS__',defaults),('__HAND__',hand),('__GOLD__',','.join("8'h%02x"%v for v in gold))]:bench=bench.replace(a,b)
    p=W/'tb_independent_s4.sv';assert not p.exists();p.write_text(bench,encoding='utf-8',newline='\n')
    return len(vectors)

def main():
    """检查重型任务和资源后，在独占槽运行单job编译及仿真。"""
    h.save('resource_before_rtl.json',{'ram_available_bytes':psutil.virtual_memory().available,'disk_free_bytes':shutil.disk_usage(W).free,
        'existing_tools':[{'pid':p.pid,'name':p.info['name'],'rss':p.memory_info().rss,'cpu':list(p.cpu_times())[:2]} for p in psutil.process_iter(['name']) if p.info['name'] and any(s in p.info['name'].lower() for s in ('vivado','verilator','cc1plus','vtb_'))],
        'slot':'root已授权唯一heavy槽，既有Vivado为空闲root会话','rss_limit':1610612736,'cache_limit':314572800,'jobs':1,'threads':1})
    assert psutil.virtual_memory().available>=2147483648
    count=prepare();tool=R.__class__('D:/FPGA_S2A_MSYS2_20261001/env')
    exe=tool/'mingw64/bin/verilator_bin.exe';assert exe.is_file()
    env=os.environ.copy();env['PATH']=str(tool/'usr/bin')+os.pathsep+str(tool/'mingw64/bin')+os.pathsep+env['PATH'];env['VERILATOR_ROOT']=str(tool/'mingw64/share/verilator');env['PYTHONUTF8']='1'
    sources=['src/s2a_network_descriptor_pkg.sv','src/s2a_conv_tile_engine.sv','src/s2b_conv_tile_engine.sv']
    hashes={p:h.sha(R/p) for p in sources}
    cmd=[str(exe),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--output-split','10000','--output-split-cfuncs','100','--top-module','tb_independent_s4','--Mdir','obj_dir','-MAKEFLAGS','PYTHON3=\'"'+sys.executable+'"\'','-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1',*[str(R/p) for p in sources],'tb_independent_s4.sv']
    compile=h.native('independent_compile',cmd,W,120,env)
    assert compile['exit_code']==0
    sim=h.native('independent_simulation',[str(W/'obj_dir/Vtb_independent_s4.exe')],W,120,env)
    assert sim['exit_code']==0
    log=h.read(W/'independent_simulation.log')
    assert 'PASS_SYNTHETIC bytes=512' in log and 'PASS_INDEPENDENT_S4 hand='+str(count) in log and 'abort_mask=000fffff reset_mask=000fffff' in log
    assert hashes=={p:h.sha(R/p) for p in sources}
    h.save('independent_rtl_result.json',{'status':'PASS','commands':[compile,sim],'source_sha256':hashes,'hand_cases':count,'synthetic_bytes':512,'response_error_cases':21,'raw80':1,'abort_reset_states_each':20,'tool_version':subprocess.check_output([str(exe),'--version'],env=env,text=True).strip(),'script_sha256':h.sha(W/'rtl_review.py'),'tb_sha256':h.sha(W/'tb_independent_s4.sv')})
    print(log)
if __name__=='__main__':main()
