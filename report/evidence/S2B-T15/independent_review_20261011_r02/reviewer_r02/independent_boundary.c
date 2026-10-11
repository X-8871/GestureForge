/* 独立终态交错模型，不代表实板或RTL通过。 */
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
