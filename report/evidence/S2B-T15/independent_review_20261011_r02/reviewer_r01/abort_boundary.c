/* UART、缓存和CSR行为模型仅检验软件边界，不声明RTL或实物通过。 */
#define S2B_HOST_MOCK
#include "s2b_inference_app.c"
#include <stdlib.h>
#include <fcntl.h>
#include <io.h>
static uint32_t regs[64], physical_status=SAFE_REUSE;
static uint64_t epoch_value, clock_value;
static int pending;
static const char *golden_path;
static unsigned int sent_total,tx_fail_after=UINT_MAX;
static void barrier(void) { }
static uint64_t ticks(void) { return clock_value++; }
static uint64_t seconds_ticks(uint32_t seconds) { return (uint64_t)seconds * 10000U; }
static uint32_t csr_read(uint32_t offset)
{
    if (offset == 0x00CU) {
        if (pending > 0) { --pending; if(getenv("S2B_REVIEW_RACE")) { physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=9U; } return OWNER_PL | 2U; }
        if (physical_status == (OWNER_PL | 2U)) {
            /* 模拟PL在所有权期间写头；文件来自独立CPU黄金，不由应用生成。 */
            if (golden_path!=NULL) {
                FILE *source=fopen(golden_path,"rb");
                if (source==NULL || fseek(source,10772736L,SEEK_SET)!=0 ||
                    fread(arena+0x01A46100U,1U,HEAD13_BYTES,source)!=HEAD13_BYTES ||
                    fseek(source,11361870L,SEEK_SET)!=0 ||
                    fread(arena+0x01AD5E80U,1U,HEAD26_BYTES,source)!=HEAD26_BYTES || fclose(source)!=0) abort();
            }
            physical_status=SAFE_REUSE|TERMINAL|HEAD_VALID|DONE_SAFE;
        }
        return physical_status;
    }
    if (offset == 0x050U) return (uint32_t)epoch_value;
    if (offset == 0x054U) return (uint32_t)(epoch_value>>32);
    return regs[offset/4U];
}
static void csr_write(uint32_t offset, uint32_t value)
{
    if (offset != 8U) { regs[offset/4U]=value; return; }
    if (value == 1U) {
        if (physical_status != SAFE_REUSE) abort();
        ++epoch_value; regs[0x058U/4U]=regs[0x014U/4U];
        if (regs[0x01CU/4U] != INPUT_BYTES) { physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=3U; }
        else { physical_status=OWNER_PL|2U; regs[4]=0U; pending=1; }
    } else if (value == 2U) { if((physical_status&7U)!=1U && (physical_status&7U)!=2U) { fprintf(stderr,"SLVERR_ABORT_AFTER_TERMINAL state=%x\n",physical_status); exit(86); } physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=8U; pending=0; }
    else if (value == 4U) {
        uint64_t ack=((uint64_t)regs[0x060U/4U]<<32)|regs[0x05CU/4U];
        if (ack!=epoch_value || (physical_status&(SAFE_REUSE|TERMINAL))!=(SAFE_REUSE|TERMINAL)) abort();
        fprintf(stderr,"ACK %llu\n",(unsigned long long)epoch_value);
        physical_status=SAFE_REUSE; regs[4]=0U;
    } else abort();
}
static void flush_range(uint32_t offset, uint32_t length)
{
    if (physical_status & OWNER_PL || (offset & 63U) || (length & 63U) || offset+length>ARENA_BYTES) abort();
    fprintf(stderr,"FLUSH %08x %u\n",offset,length);
}
static void invalidate_range(uint32_t offset, uint32_t length)
{
    if (physical_status & OWNER_PL || (offset & 63U) || (length & 63U) || offset+length>ARENA_BYTES) abort();
    fprintf(stderr,"INVALIDATE %08x %u\n",offset,length);
}
static int uart_read_one(uint8_t *byte) { int value=getchar(); if (value==EOF) return 0; *byte=(uint8_t)value; return 1; }
static int uart_write_one(uint8_t byte) { if(sent_total>=tx_fail_after) return 0; ++sent_total; return putchar(byte)!=EOF; }
static int uart_drain_done(void) { return fflush(stdout)==0; }
int main(int argc,char **argv)
{
    int count,index;
    /* Windows管道必须使用原字节模式，不能把LF转换成CRLF。 */
    (void)_setmode(_fileno(stdin),_O_BINARY); (void)_setmode(_fileno(stdout),_O_BINARY);
    if (argc!=2 && argc!=3) return 90;
    if (argc==3) golden_path=argv[2];
    if (getenv("S2B_MOCK_TX_FAIL_AFTER")!=NULL) tx_fail_after=(unsigned int)strtoul(getenv("S2B_MOCK_TX_FAIL_AFTER"),NULL,10);
    count=atoi(argv[1]); if(getenv("S2B_REVIEW_RACE")) { weights_loaded=1; input_loaded=1; }
    if (crc32_ieee((const uint8_t *)"123456789",9U)!=0xCBF43926U) return 91;
    for(index=0;index<count;++index) {
        if(index==1 && cache_probe_wait && getenv("S2B_MOCK_SKIP_DAP")==NULL) {
            uint32_t item;
            for(item=0U;item<64U;++item) put32(arena+item*4U,cache_dap_seed^(0x9E3779B9U*item));
        }
        if(!service_request()) return 2;
    }
    fprintf(stderr,"MOCK_OK epoch=%llu status=%x sequence=%u\n",(unsigned long long)epoch_value,physical_status,next_sequence);
    return 0;
}
