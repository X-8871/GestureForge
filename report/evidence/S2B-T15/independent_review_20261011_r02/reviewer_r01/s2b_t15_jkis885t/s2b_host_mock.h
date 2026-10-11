/* 测试注入层只用于主机编译，不映射任何真实MMIO或板卡。 */
#define S2B_HEAD13_SCALE 0.24267549589862975
#define S2B_HEAD26_SCALE 0.30223452951025775
static void barrier(void);
static uint32_t csr_read(uint32_t offset);
static void csr_write(uint32_t offset, uint32_t value);
static uint64_t ticks(void);
static uint64_t seconds_ticks(uint32_t seconds);
static void flush_range(uint32_t offset, uint32_t length);
static void invalidate_range(uint32_t offset, uint32_t length);
static int uart_read_one(uint8_t *byte);
static int uart_write_one(uint8_t byte);
static int uart_drain_done(void);
