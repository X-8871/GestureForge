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
static const char *dap_scenario;
static int diagnostic_active,diagnostic_status_reads;
static unsigned int sent_total,tx_fail_after=UINT_MAX;
static void barrier(void) { }
static uint64_t ticks(void) { return clock_value++; }
static uint64_t seconds_ticks(uint32_t seconds) { return (uint64_t)seconds * 10000U; }
static uint32_t csr_read(uint32_t offset)
{
    if (offset == 0x00CU) {
        if (diagnostic_active && physical_status == (OWNER_PL|2U) && dap_scenario!=NULL) {
            ++diagnostic_status_reads;
            if (strcmp(dap_scenario,"read_then_terminal")==0 && diagnostic_status_reads==1) {
                /* 状态读返回RUN，返回后真实状态已ERROR_SAFE：复现原裸STR竞态。 */
                physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=5U; pending=0;
                return OWNER_PL|2U;
            }
            return OWNER_PL|2U;
        }
        if (pending > 0) { --pending; return OWNER_PL | 2U; }
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
        if (regs[0x014U/4U]==200U && dap_scenario!=NULL) {
            diagnostic_active=1; diagnostic_status_reads=0;
            if (regs[0x028U/4U]==1U) { physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=5U; pending=0; }
        }
    } else if (value == 2U) {
        /* CPU应用绝不能通过裸Device写ABORT；真实冻结RTL终态会拒绝SLVERR。 */
        fprintf(stderr,"CPU_BARE_ABORT_STR_FORBIDDEN\n"); exit(86);
    }
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
static int uart_drain_done(void)
{
    int done=fflush(stdout)==0;
    if(done && diagnostic_active && get32(response+36U)==WAIT_DAP_ABORT && dap_scenario!=NULL) {
        /* DAP协同注入在完整UART ready后发生，不执行CPU的MMIO STR。 */
        if(strcmp(dap_scenario,"dap_race")==0 || strcmp(dap_scenario,"original_fault")==0) {
            physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=5U; pending=0;
            regs[0x064U/4U]=4U; fprintf(stderr,"DAP_SLVERR_TERMINAL error=5\n");
        } else if(strcmp(dap_scenario,"done_before_dap")==0) {
            physical_status=SAFE_REUSE|TERMINAL|HEAD_VALID|DONE_SAFE; regs[4]=0U; pending=0;
            regs[0x064U/4U]=4U; fprintf(stderr,"DAP_SLVERR_TERMINAL done\n");
        } else if(regs[0x02CU/4U]==1U) {
            physical_status=OWNER_PL|FAULT_ISOLATED; regs[4]=8U; pending=0;
            fprintf(stderr,"DAP_ABORT_DRAIN_ISOLATED\n");
        } else {
            if(physical_status!=(OWNER_PL|2U)) abort();
            physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=8U; pending=0;
            fprintf(stderr,"DAP_ACTUAL_ABORT epoch=%llu\n",(unsigned long long)epoch_value);
        }
    }
    return done;
}
int main(int argc,char **argv)
{
    int count,index;
    /* Windows管道必须使用原字节模式，不能把LF转换成CRLF。 */
    (void)_setmode(_fileno(stdin),_O_BINARY); (void)_setmode(_fileno(stdout),_O_BINARY);
    if (argc!=2 && argc!=3) return 90;
    if (argc==3) golden_path=argv[2];
    dap_scenario=getenv("S2B_MOCK_DAP_SCENARIO");
    if (getenv("S2B_MOCK_TX_FAIL_AFTER")!=NULL) tx_fail_after=(unsigned int)strtoul(getenv("S2B_MOCK_TX_FAIL_AFTER"),NULL,10);
    count=atoi(argv[1]);
    if (crc32_ieee((const uint8_t *)"123456789",9U)!=0xCBF43926U) return 91;
    for(index=0;index<count;++index) {
        if(index==1 && cache_probe_wait && getenv("S2B_MOCK_SKIP_DAP")==NULL) {
            uint32_t item;
            for(item=0U;item<64U;++item) put32(arena+item*4U,cache_dap_seed^(0x9E3779B9U*item));
        }
        if(!service_request()) return 2;
    }
    fprintf(stderr,"MOCK_OK epoch=%llu status=%x sequence=%u diag_pending=%d\n",(unsigned long long)epoch_value,physical_status,next_sequence,diag_ack_pending);
    return 0;
}
