#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ov5640.h"
#include "expected_vendor.h"
/* 每种底层调用独立计数，失败点按调用序号注入。 */
static XIicPs iic;
static XIicPs_Config config;
static int lookup_n, cfg_n, clock_n, send_n, recv_n, busy_n;
static int no_config, cfg_fail, clock_fail, send_fail, recv_fail;
static int busy_from, busy_for;
static u8 high_id, low_id;
static u16 last_addr;
static u8 last_bytes[3];
static int last_count;
static s3_iic_device_id lookup_id;
static unsigned cases, checks;
static int compare_table;
static void check(int ok, int line)
{
    ++checks;
    if (!ok) { fprintf(stderr, "FAIL line=%d case=%u\n", line, cases); exit(1); }
}
#define CHECK(x) check((x), __LINE__)
static void reset(void)
{
    ++cases;
    lookup_n=cfg_n=clock_n=send_n=recv_n=busy_n=0;
    no_config=cfg_fail=clock_fail=send_fail=recv_fail=0;
    busy_from=busy_for=0;
    compare_table=0;
    high_id=0x56; low_id=0x40; last_addr=0;
    last_count=0; memset(last_bytes,0,sizeof(last_bytes));
    memset(&config,0,sizeof(config)); config.BaseAddress=0x12345678;
}
XIicPs_Config *XIicPs_LookupConfig(s3_iic_device_id device)
{
    ++lookup_n; lookup_id=device; return no_config ? NULL : &config;
}
int XIicPs_CfgInitialize(XIicPs *p, XIicPs_Config *c, u32 base)
{
    ++cfg_n; CHECK(p==&iic && c==&config && base==0x12345678);
    return cfg_fail ? 41 : XST_SUCCESS;
}
int XIicPs_SetSClk(XIicPs *p,u32 rate)
{
    ++clock_n; CHECK(p==&iic && rate==100000); return clock_fail ? 42 : XST_SUCCESS;
}
int XIicPs_BusIsBusy(XIicPs *p)
{
    ++busy_n; CHECK(p==&iic);
    /* 无界轮询回归必须明确失败，避免测试自身永久等待。 */
    CHECK(busy_n <= (int)(2*EXPECTED_WRITES+6+S3_I2C_BUSY_LIMIT));
    return busy_from && busy_n>=busy_from &&
           (!busy_for || busy_n<busy_from+busy_for);
}
int XIicPs_MasterSendPolled(XIicPs *p,u8 *bytes,int count,u16 slave)
{
    ++send_n; CHECK(p==&iic && slave==0x3c && count>=1 && count<=3);
    CHECK(bytes!=NULL); last_count=count;
    memcpy(last_bytes,bytes,(size_t)count);
    last_addr = count>=2 ? (u16)((bytes[0]<<8)|bytes[1]) : bytes[0];
    if (compare_table && send_n>2) {
        unsigned n=(unsigned)send_n-3;
        CHECK(n<EXPECTED_WRITES && count==3);
        CHECK(last_addr==expected_vendor[n].reg && bytes[2]==expected_vendor[n].val);
    }
    return send_n==send_fail ? 43 : XST_SUCCESS;
}
int XIicPs_MasterRecvPolled(XIicPs *p,u8 *bytes,int count,u16 slave)
{
    ++recv_n; CHECK(p==&iic && slave==0x3c && count==1);
    /* 即使失败也污染临时缓冲，以验证调用者输出被保留。 */
    *bytes = last_addr==0x300a ? high_id : last_addr==0x300b ? low_id : 0xe7;
    return recv_n==recv_fail ? 44 : XST_SUCCESS;
}
typedef int (*reader)(XIicPs *,u8,u16,u8 *);
static int read8(XIicPs *p,u8 s,u16 a,u8 *v) { return i2c_reg8_read(p,s,(u8)a,v); }
static void reads(reader read)
{
    u8 value;
    reset(); value=0xa5; CHECK(read(&iic,0x3c,0x300a,&value)==0);
    CHECK(send_n==1 && recv_n==1 && busy_n==3);
    CHECK(value==(read==read8 ? 0xe7 : 0x56));
    CHECK(last_count==(read==read8 ? 1 : 2));
    CHECK(last_bytes[0]==(read==read8 ? 0x0a : 0x30));
    if (read!=read8) CHECK(last_bytes[1]==0x0a);
    reset(); send_fail=1; value=0xa5;
    CHECK(read(&iic,0x3c,0x300a,&value)==43);
    CHECK(value==0xa5 && recv_n==0 && busy_n==1);
    reset(); recv_fail=1; value=0xa5;
    CHECK(read(&iic,0x3c,0x300a,&value)==44);
    CHECK(value==0xa5 && send_n==1 && busy_n==2);
    for (int phase=1;phase<=3;phase++) {
        reset(); busy_from=phase; value=0xa5;
        CHECK(read(&iic,0x3c,0x300a,&value)==S3_ERR_BUSY);
        CHECK(value==0xa5 && busy_n==phase-1+(int)S3_I2C_BUSY_LIMIT);
        CHECK(send_n==(phase>1) && recv_n==(phase>2));
    }
    for (int phase=1;phase<=3;phase++) {
        reset(); busy_from=phase; busy_for=S3_I2C_BUSY_LIMIT-1; value=0;
        CHECK(read(&iic,0x3c,0x300a,&value)==0);
        CHECK(busy_n==(int)S3_I2C_BUSY_LIMIT+2);
        CHECK(value==(read==read8 ? 0xe7 : 0x56));
    }
    reset(); value=0xa5; CHECK(read(NULL,0x3c,0,&value)==S3_ERR_ARGUMENT);
    CHECK(read(&iic,0x3c,0,NULL)==S3_ERR_ARGUMENT);
    CHECK(read(&iic,0x80,0,&value)==S3_ERR_ARGUMENT);
    CHECK(value==0xa5 && send_n==0 && recv_n==0 && busy_n==0);
}
static int write8(XIicPs *p,u8 s,u16 a,u8 v) { return i2c_reg8_write(p,s,(u8)a,v); }
static void writes(int (*write)(XIicPs *,u8,u16,u8))
{
    reset(); CHECK(write(&iic,0x3c,0x1234,0xab)==0);
    CHECK(send_n==1 && recv_n==0 && busy_n==2);
    CHECK(last_count==(write==write8 ? 2 : 3));
    CHECK(last_bytes[0]==(write==write8 ? 0x34 : 0x12));
    CHECK(last_bytes[last_count-1]==0xab);
    if (write!=write8) CHECK(last_bytes[1]==0x34);
    reset(); send_fail=1; CHECK(write(&iic,0x3c,0x1234,0xab)==43);
    CHECK(send_n==1 && busy_n==1 && recv_n==0);
    for(int phase=1;phase<=2;phase++) {
        reset(); busy_from=phase;
        CHECK(write(&iic,0x3c,0x1234,0xab)==S3_ERR_BUSY);
        CHECK(send_n==(phase>1) && busy_n==phase-1+(int)S3_I2C_BUSY_LIMIT);
    }
    for(int phase=1;phase<=2;phase++) {
        reset(); busy_from=phase; busy_for=S3_I2C_BUSY_LIMIT-1;
        CHECK(write(&iic,0x3c,0x1234,0xab)==0);
        CHECK(send_n==1 && recv_n==0 && busy_n==(int)S3_I2C_BUSY_LIMIT+1);
    }
    reset(); CHECK(write(NULL,0x3c,0,0)==S3_ERR_ARGUMENT);
    CHECK(write(&iic,0x80,0,0)==S3_ERR_ARGUMENT); CHECK(busy_n==0 && send_n==0);
}
int main(void)
{
    s3_iic_device_id device;
#ifdef SDT
    device=(UINTPTR)0x123456789abcdef0ULL;
    _Static_assert(sizeof(s3_iic_device_id)==sizeof(UINTPTR), "SDT width");
#else
    device=0xfedc;
    _Static_assert(sizeof(s3_iic_device_id)==sizeof(u16), "legacy width");
#endif
    reset(); CHECK(i2c_init(&iic,device,100000)==0);
    CHECK(lookup_id==device && lookup_n==1 && cfg_n==1 && clock_n==1 && busy_n==1);
    reset(); no_config=1; CHECK(i2c_init(&iic,device,100000)==XST_FAILURE);
    CHECK(cfg_n==0 && clock_n==0 && busy_n==0);
    reset(); cfg_fail=1; CHECK(i2c_init(&iic,device,100000)==41);
    CHECK(cfg_n==1 && clock_n==0 && busy_n==0);
    reset(); clock_fail=1; CHECK(i2c_init(&iic,device,100000)==42);
    CHECK(cfg_n==1 && clock_n==1 && busy_n==0);
    reset(); busy_from=1; CHECK(i2c_init(&iic,device,100000)==S3_ERR_BUSY);
    CHECK(busy_n==S3_I2C_BUSY_LIMIT);
    reset(); busy_from=1; busy_for=S3_I2C_BUSY_LIMIT-1;
    CHECK(i2c_init(&iic,device,100000)==0); CHECK(busy_n==S3_I2C_BUSY_LIMIT);
    reset(); CHECK(i2c_init(NULL,device,100000)==S3_ERR_ARGUMENT);
    CHECK(i2c_init(&iic,device,0)==S3_ERR_ARGUMENT); CHECK(lookup_n==0);
    reads(read8); reads(i2c_reg16_read); writes(write8); writes(i2c_reg16_write);
    reset(); compare_table=1; CHECK(sensor_init(&iic)==0); int total_sends=send_n;
    CHECK(recv_n==2 && total_sends==(int)EXPECTED_WRITES+2);
    CHECK(busy_n==(int)(2*EXPECTED_WRITES+6));
    /* 遍历两次 ID 读取与每次表写的所有外层忙检查点。 */
    for(int phase=1;phase<=(int)(2*EXPECTED_WRITES+6);phase++) {
        reset(); busy_from=phase; CHECK(sensor_init(&iic)==S3_ERR_BUSY);
        CHECK(busy_n==phase-1+(int)S3_I2C_BUSY_LIMIT);
        if (phase<=6) {
            CHECK(send_n==(phase+1)/3 && recv_n==phase/3);
        } else {
            int n=phase-7;
            CHECK(send_n==2+n/2+n%2 && recv_n==2);
        }
    }
    for(int n=1;n<=total_sends;n++) {
        reset(); send_fail=n; CHECK(sensor_init(&iic)==43);
        CHECK(send_n==n && recv_n==(n==1?0:n==2?1:2));
    }
    for(int n=1;n<=2;n++) {
        reset(); recv_fail=n; CHECK(sensor_init(&iic)==44);
        CHECK(send_n==n && recv_n==n);
    }
    reset(); high_id=0; CHECK(sensor_init(&iic)==S3_ERR_ID);
    CHECK(send_n==2 && recv_n==2);
    reset(); low_id=0; CHECK(sensor_init(&iic)==S3_ERR_ID);
    CHECK(send_n==2 && recv_n==2);
    reset(); CHECK(sensor_init(NULL)==S3_ERR_ARGUMENT); CHECK(send_n==0);
    const struct reginfo table[]={{0x1234,0x56},{0x2345,0x67},{SEQUENCE_END,0}};
    const struct reginfo missing_end[]={{0x1234,0x56},{0x2345,0x67}};
    const struct reginfo one[]={{0x1234,0x56}};
    reset(); CHECK(sensor_write_array(&iic,table,3)==0); CHECK(send_n==2);
    reset(); CHECK(sensor_write_array(&iic,table,2)==S3_ERR_TABLE); CHECK(send_n==2);
    reset(); CHECK(sensor_write_array(&iic,table,1)==S3_ERR_TABLE); CHECK(send_n==1);
    reset(); CHECK(sensor_write_array(&iic,missing_end,sizeof(missing_end)/sizeof(missing_end[0]))==S3_ERR_TABLE);
    CHECK(send_n==2);
    reset(); CHECK(sensor_write_array(&iic,one,sizeof(one)/sizeof(one[0]))==S3_ERR_TABLE);
    CHECK(send_n==1);
    reset(); CHECK(sensor_write_array(&iic,&table[2],1)==0); CHECK(send_n==0);
    reset(); CHECK(sensor_write_array(&iic,table,0)==S3_ERR_ARGUMENT);
    CHECK(sensor_write_array(&iic,NULL,3)==S3_ERR_ARGUMENT);
    CHECK(sensor_write_array(NULL,table,3)==S3_ERR_ARGUMENT); CHECK(send_n==0);
    printf("PASS cases=%u checks=%u vendor_writes=%d\n",cases,checks,total_sends-2);
    return 0;
}
