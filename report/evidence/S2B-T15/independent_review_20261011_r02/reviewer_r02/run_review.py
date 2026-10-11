"""独立轻量回归及六种终态交错审查；产物仅落在本次目录。"""
import sys
sys.dont_write_bytecode = True
import pathlib, tempfile, unittest, subprocess, json, hashlib, struct, os, time
目录=pathlib.Path(__file__).absolute().parent
根目录=目录.parents[3]
sys.path.insert(0,str(根目录))
from verification import test_s2b_board_transport as 测试
from verification import s2b_board_transport as 运输
原创建=tempfile.mkdtemp
def 创建(*args,**kwargs):
    kwargs['dir']=目录
    return 原创建(*args,**kwargs)
tempfile.mkdtemp=创建
开始=time.monotonic()
with (目录/'unittest.log').open('x',encoding='utf-8') as 流:
    结果=unittest.TextTestRunner(stream=流,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(测试))
assert 结果.wasSuccessful()
源码=r'''/* 独立终态交错模型，不代表实板或RTL通过。 */
#define S2B_HOST_MOCK
#include "s2b_inference_app.c"
#include <stdlib.h>
#include <fcntl.h>
#include <io.h>
static uint32_t r[64],st=SAFE_REUSE,sc,reads,acks;
static uint64_t ep,t;
static void barrier(void) {}
static uint64_t ticks(void) { return ++t; }
static uint64_t seconds_ticks(uint32_t s) { return (uint64_t)s*100U; }
static uint32_t csr_read(uint32_t off) {
 if(off==0x00cU) {
  if(st==(OWNER_PL|2U) && sc==1U && ++reads==1U) {
   st=SAFE_REUSE|TERMINAL|ERROR_SAFE;r[4]=5U;return OWNER_PL|2U;
  }
  return st;
 }
 if(off==0x050U) return (uint32_t)ep;
 if(off==0x054U) return (uint32_t)(ep>>32);
 return r[off/4U];
}
static void csr_write(uint32_t off,uint32_t val) {
 if(off!=8U) {r[off/4U]=val;return;}
 if(val==1U) {
  if(st!=SAFE_REUSE) exit(81);
  ++ep;r[0x058U/4U]=r[0x014U/4U];st=OWNER_PL|2U;
  if(sc==0U) {st=SAFE_REUSE|TERMINAL|ERROR_SAFE;r[4]=5U;}
 } else if(val==2U) {fputs("FORBIDDEN_CPU_ABORT\n",stderr);exit(86);}
 else if(val==4U) {
  if(st!=(SAFE_REUSE|TERMINAL|ERROR_SAFE) || r[4]!=8U ||
     (((uint64_t)r[0x060U/4U]<<32)|r[0x05cU/4U])!=ep) exit(82);
  ++acks;st=SAFE_REUSE;r[4]=0U;
 } else exit(83);
}
static void flush_range(uint32_t o,uint32_t n) {
 if(st&OWNER_PL || o+n>ARENA_BYTES) exit(84);
 fputs("FLUSH\n",stderr);
}
static void invalidate_range(uint32_t o,uint32_t n) {
 if(st&OWNER_PL || o+n>ARENA_BYTES) exit(85);
 fputs("INVALIDATE\n",stderr);
}
static int uart_read_one(uint8_t *b) {int v=getchar();if(v==EOF)return 0;*b=(uint8_t)v;return 1;}
static int uart_write_one(uint8_t b) {return putchar(b)!=EOF;}
static int uart_drain_done(void) {
 int ok=fflush(stdout)==0;
 if(ok && get32(response+36U)==WAIT_DAP_ABORT) {
  if(sc==3U) {st=SAFE_REUSE|TERMINAL|HEAD_VALID|DONE_SAFE;r[4]=0U;r[25]=4U;}
  else if(sc==5U) {st=OWNER_PL|FAULT_ISOLATED;r[4]=8U;}
  else {st=SAFE_REUSE|TERMINAL|ERROR_SAFE;r[4]=(sc==2U?5U:sc==4U?4U:8U);r[25]=(sc==2U?4U:0U);}
 }
 return ok;
}
int main(int argc,char **argv) {
 int i,count;
 _setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
 if(argc!=3)return 90;
 sc=(uint32_t)atoi(argv[1]);count=atoi(argv[2]);weights_loaded=input_loaded=1;
 for(i=0;i<count;++i) if(!service_request()) {
  fprintf(stderr,"FAILSTOP st=%x error=%u epoch=%llu ack=%u pending=%d\n",st,r[4],(unsigned long long)ep,acks,diag_ack_pending);return 2;
 }
 fprintf(stderr,"RETURN st=%x error=%u epoch=%llu ack=%u pending=%d\n",st,r[4],(unsigned long long)ep,acks,diag_ack_pending);return 0;
}
'''
with (目录/'independent_boundary.c').open('x',encoding='utf-8',newline='\n') as 流: 流.write(源码)
with (目录/'s2b_host_mock.h').open('x',encoding='utf-8',newline='\n') as 流: 流.write(测试.MOCK_HEADER)
命令=[str(测试.GCC),'-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(目录),'-I'+str(根目录/'vitis'),
      '-I'+str(根目录/'verification'),str(目录/'independent_boundary.c'),str(根目录/'verification/s2a_ps_decode_nms_reference.c'),'-o',str(目录/'independent_boundary.exe'),'-lm']
环境=dict(os.environ,PATH=str(测试.GCC.parent)+os.pathsep+os.environ.get('PATH',''))
编译=subprocess.run(命令,capture_output=True,env=环境)
assert 编译.returncode==0,编译.stderr
请求,头=运输.make_request(3,1,77,struct.pack('<III',2,0xFFFFFFFF,10000))
基础=头+struct.pack('<III',2,0xFFFFFFFF,10000)
记录=[]
for 编号,错误,码,准备 in [(0,5,7,False),(1,5,7,False),(2,5,7,True),(3,0,7,True),(4,4,7,True),(5,8,8,True)]:
    运行=subprocess.run([str(目录/'independent_boundary.exe'),str(编号),'1'],input=基础,capture_output=True,env=环境,timeout=15)
    assert 运行.returncode==2 and b'FORBIDDEN_CPU_ABORT' not in 运行.stderr
    接收=运输.WireSession(测试.FragmentSerial(运行.stdout,4096),__import__('io').BytesIO(),__import__('io').BytesIO(),response_timeout=.1)
    if 准备: 接收.receive_abort_ready(请求)
    try: 接收.receive(请求,0)
    except 运输.TransportError: pass
    else: raise AssertionError('失败终态被当作成功')
    实际=接收.events[-1]['raw_meta']
    assert 实际[2]==错误 and 实际[-1]==码 and 接收.failed and 接收.epoch==0
    assert b'ack=0 pending=0' in 运行.stderr and 运行.stderr.count(b'INVALIDATE')==1
    (目录/f'boundary_{编号}.bin').write_bytes(运行.stdout)
    (目录/f'boundary_{编号}.log').write_bytes(运行.stderr)
    记录.append({'scenario':编号,'exit_code':运行.returncode,'meta':实际,'stderr_sha256':运输.digest(运行.stderr),'stdout_sha256':运输.digest(运行.stdout)})
# 独立检查正确ACK、错误epoch/frame/mode/seq、pending新任务以及无pending的ACK。
for 标签,帧,序列,操作,模式,期望 in [('correct',77,2,3,3,0),('wrong_epoch',77,2,3,3,2),('wrong_frame',78,2,3,3,2),
    ('wrong_phase',77,2,3,0,2),('old_sequence',77,1,3,3,2),('pending_run',77,2,2,0,2)]:
    载荷=struct.pack('<III',模式,2 if 标签=='wrong_epoch' else 1,0)
    if 操作==2:
        额外=运输.Header(2,序列,帧,416,416,1,运输.INPUT_BYTES+8,0).pack()
    else:
        _,额外头=运输.make_request(3,序列,帧,载荷);额外=额外头+载荷
    运行=subprocess.run([str(目录/'independent_boundary.exe'),'6','2'],input=基础+额外,capture_output=True,env=环境,timeout=15)
    assert 运行.returncode==期望
    assert (b'ack=1 pending=0' if 期望==0 else b'ack=0 pending=1') in 运行.stderr
    if 期望==0:
        接收=运输.WireSession(测试.FragmentSerial(运行.stdout,4096),__import__('io').BytesIO(),__import__('io').BytesIO(),response_timeout=.1)
        接收.last_sequence=1;接收.receive_abort_ready(请求);接收.receive(请求,0)
        assert 接收.epoch==1 and 接收.abort_pending['phase']=='ACK_REQUIRED'
        assert 接收.acknowledge_abort(2)[0]['phys_status']==0x400 and 接收.abort_pending is None
    (目录/f'ack_{标签}.bin').write_bytes(运行.stdout);(目录/f'ack_{标签}.log').write_bytes(运行.stderr)
    记录.append({'ack_case':标签,'exit_code':运行.returncode,'stderr_sha256':运输.digest(运行.stderr),'stdout_sha256':运输.digest(运行.stdout)})
输出={'status':'PASS','tests':结果.testsRun,'failures':len(结果.failures),'errors':len(结果.errors),'skipped':len(结果.skipped),
      'elapsed_seconds':time.monotonic()-开始,'native_directory':str(测试.NativeTests.directory),'independent_boundary_cases':记录,'compile_command':命令,'compile_exit_code':编译.returncode}
with (目录/'test_result.json').open('x',encoding='utf-8',newline='\n') as 流: json.dump(输出,流,ensure_ascii=False,indent=2)
print(json.dumps({'status':输出['status'],'tests':结果.testsRun,'boundary_cases':len(记录),'elapsed_seconds':输出['elapsed_seconds']},ensure_ascii=False))
