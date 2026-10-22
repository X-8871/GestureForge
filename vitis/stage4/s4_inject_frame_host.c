/* 阶段4 单帧注入通路 —— 主机侧验证 harness（离线，不接板卡）。
 *
 * 作用：用 mock DDR（32 MiB 窗口）与 mock cache 行状态驱动 s4_inject_frame 状态机，
 * 执行由 op 脚本描述的帧/事件序列，输出机器可读 JSON，并把第一个非 OK 状态作为退出码。
 *
 * op 脚本（每行一条，`#` 起注释；`try ` 前缀表示记录错误但继续执行）：
 *   region name=<n> base=<hex> len=<hex>
 *   ring slots=<n>
 *   frame id=<u32> fmt=<RGB888|RGB565|GRAY8|INT8_CHW_416|bad> w=<u32> h=<u32> stride=<u32>
 *         [len=<bytes>] [offset=<hex>] [region=<name>] [source=<kind>] [base=<hex>]
 *         [capture=unavailable|<ns>] [capture_avail=<0|1>] [inject_ns=<ns>]
 *         [algorithm=crc32_ieee|sha256] [digest=auto|none|wrong|<hex>]
 *         [payload=file:<path>|pattern:<seed>] [payload_len=<n>]
 *         [clock=<name>] [freq=<hz>] [wrap=<text>] [domain=<text>] [contract=<ver>]
 *         [align=<bytes>] [scope_pl=<...>] [scope_uart=<...>] [scope_board=<...>]
 *   bind [slot=<n>]        生产者写入 mock DDR 并绑定（默认取空闲槽位）
 *   drop                   把当前 frame 记为丢帧
 *   advance slot=<n> ev=<event>
 *   consume slot=<n> [busy=<n>]
 *   timeout slot=<n>
 *   abort slot=<n>
 *   mock_flush base=<hex> len=<hex>        （故意绕过状态机的维护调用，用于反例）
 *   mock_invalidate base=<hex> len=<hex>
 *   note ...                                （仅记录）
 *
 * 退出码：0 = 全部非 try op 成功；否则为第一个非 try op 的 s4_inject_status。
 */

/* MinGW(MSVCRT) 的 printf 不支持 %llu；强制使用 MinGW 自带 ANSI stdio 实现，
 * 使 JSON 输出可移植且 -Wall -Wextra 下无格式告警。 */
#if defined(__MINGW32__) && !defined(__USE_MINGW_ANSI_STDIO)
#define __USE_MINGW_ANSI_STDIO 1
#endif

#include "s4_inject_frame.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MOCK_BASE 0x10000000ULL
#define MOCK_LEN 0x02000000ULL
#define MAX_TOKENS 40
#define MAX_LINE 4096
#define MAX_PAYLOAD (8u * 1024u * 1024u)
#define MAX_OPS 128
#define MAX_CACHE_EVENTS 64

typedef struct {
    unsigned long long base;
    unsigned long long len;
} mock_range;

typedef struct {
    unsigned char *producer_cache;
    unsigned char *ddr;
    unsigned char *consumer_view;
    unsigned char *dirty_lines;
    unsigned char *consumer_valid_lines;
    unsigned long long dirty_lost;
    mock_range flush_ranges[MAX_CACHE_EVENTS];
    mock_range invalidate_ranges[MAX_CACHE_EVENTS];
    mock_range write_ranges[MAX_CACHE_EVENTS];
    uint32_t write_crc32[MAX_CACHE_EVENTS];
    unsigned long write_count;
    unsigned long flush_count;
    unsigned long invalidate_count;
    unsigned long long flushed_bytes;
    unsigned long long invalidated_bytes;
    unsigned long barrier_count;
    unsigned long barrier_failures;
    int skip_next_flush;
    int skip_next_invalidate;
    int skip_next_barrier;
    int shift_next_invalidate;
} mock_cache;

typedef struct {
    unsigned index;
    char op[MAX_LINE];
    int status;
    const char *field;
    char reason[192];
    unsigned long long actual;
    int is_try;
} op_record;

typedef struct {
    s4_inject_frame_desc desc;
    unsigned char *payload;
    unsigned long long payload_length;
    int valid;
} pending_frame;

static mock_cache g_mock;
static s4_inject_ring g_ring;
static s4_inject_region g_regions[S4_INJECT_MAX_REGIONS];
static char g_region_names[S4_INJECT_MAX_REGIONS][S4_INJECT_REGION_NAME_MAX];
static unsigned g_region_count = 0u;
static op_record g_ops[MAX_OPS];
static unsigned g_op_count = 0u;
static int g_first_error = S4_INJECT_OK;
static unsigned long long g_bind_slot = 0u;
static unsigned long long g_consumer_crc32 = 0u;
static unsigned long long g_consumer_valid_bytes = 0u;
static unsigned long long g_consumer_padding_bytes = 0u;
static unsigned long long g_consumer_busy_ticks = 0u;
static unsigned long long g_consumer_reads = 0u;
static char g_last_reason[192] = "";
static int g_numeric_parse_error = 0;
static char g_numeric_parse_field[64] = "";

/* ------------------------------------------------------------------ */
/* mock cache / DDR                                                    */
/* ------------------------------------------------------------------ */

static int mock_ok(unsigned long long addr, unsigned long long len) {
    return len != 0u && addr >= MOCK_BASE && addr + len <= MOCK_BASE + MOCK_LEN &&
           addr + len >= addr;
}

static void mock_mark(unsigned long long addr, unsigned long long len, int dirty) {
    unsigned long long line;
    for (line = (addr - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES; ++line) {
        g_mock.consumer_valid_lines[line] = 0u;
        if (dirty) {
            g_mock.dirty_lines[line] = 1u;
        }
    }
}

static int mock_write(unsigned long long addr, const unsigned char *data,
                      unsigned long long len) {
    if (!mock_ok(addr, len)) {
        return 0;
    }
    memcpy(g_mock.producer_cache + (addr - MOCK_BASE), data, (size_t)len);
    mock_mark(addr, len, 1);
    if (g_mock.write_count < MAX_CACHE_EVENTS) {
        g_mock.write_ranges[g_mock.write_count].base = addr;
        g_mock.write_ranges[g_mock.write_count].len = len;
        g_mock.write_crc32[g_mock.write_count] = s4_inject_crc32(data, (size_t)len);
    }
    g_mock.write_count += 1u;
    return 1;
}

static void mock_flush(unsigned long long addr, unsigned long long len) {
    unsigned long long line;
    if (!mock_ok(addr, len)) {
        return;
    }
    if (g_mock.skip_next_flush) {
        g_mock.skip_next_flush = 0;
        return;
    }
    memcpy(g_mock.ddr + (addr - MOCK_BASE), g_mock.producer_cache + (addr - MOCK_BASE),
           (size_t)len);
    for (line = (addr - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES; ++line) {
        g_mock.dirty_lines[line] = 0u;
    }
    if (g_mock.flush_count < MAX_CACHE_EVENTS) {
        g_mock.flush_ranges[g_mock.flush_count].base = addr;
        g_mock.flush_ranges[g_mock.flush_count].len = len;
    }
    g_mock.flush_count += 1u;
    g_mock.flushed_bytes += len;
}

static void mock_invalidate(unsigned long long addr, unsigned long long len) {
    unsigned long long line;
    if (!mock_ok(addr, len)) {
        return;
    }
    if (g_mock.skip_next_invalidate) {
        g_mock.skip_next_invalidate = 0;
        return;
    }
    if (g_mock.shift_next_invalidate) {
        g_mock.shift_next_invalidate = 0;
        if (addr > MOCK_BASE && mock_ok(addr - S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES, len)) {
            addr -= S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
        } else if (mock_ok(addr + S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES, len)) {
            addr += S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
        }
    }
    memcpy(g_mock.consumer_view + (addr - MOCK_BASE), g_mock.ddr + (addr - MOCK_BASE),
           (size_t)len);
    for (line = (addr - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES; ++line) {
        if (g_mock.dirty_lines[line] != 0u) {
            g_mock.dirty_lost += 1u; /* 未 flush 就 invalidate：真实数据会丢 */
        }
        g_mock.consumer_valid_lines[line] = 1u;
    }
    if (g_mock.invalidate_count < MAX_CACHE_EVENTS) {
        g_mock.invalidate_ranges[g_mock.invalidate_count].base = addr;
        g_mock.invalidate_ranges[g_mock.invalidate_count].len = len;
    }
    g_mock.invalidate_count += 1u;
    g_mock.invalidated_bytes += len;
}

static unsigned long long mock_dirty_bytes(unsigned long long addr, unsigned long long len) {
    unsigned long long line;
    unsigned long long total = 0u;
    if (!mock_ok(addr, len)) {
        return len;
    }
    for (line = (addr - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES; ++line) {
        const unsigned long long line_addr = MOCK_BASE + line * S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
        const unsigned long long line_end = line_addr + S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
        const unsigned long long overlap_start = line_addr > addr ? line_addr : addr;
        const unsigned long long overlap_end = line_end < addr + len ? line_end : addr + len;
        if (g_mock.dirty_lines[line] != 0u && overlap_start < overlap_end) {
            total += overlap_end - overlap_start;
        }
    }
    return total;
}

static void cache_flush_adapter(void *ctx, uint64_t addr, uint64_t len) {
    (void)ctx;
    mock_flush((unsigned long long)addr, (unsigned long long)len);
}

static void cache_invalidate_adapter(void *ctx, uint64_t addr, uint64_t len) {
    (void)ctx;
    mock_invalidate((unsigned long long)addr, (unsigned long long)len);
}

static int cache_barrier_adapter(void *ctx) {
    (void)ctx;
    if (g_mock.skip_next_barrier) {
        g_mock.skip_next_barrier = 0;
        g_mock.barrier_failures += 1u;
        return 0;
    }
    g_mock.barrier_count += 1u;
    return 1;
}

static int mock_consumer_range_valid(unsigned long long addr, unsigned long long len) {
    unsigned long long line;
    if (!mock_ok(addr, len)) {
        return 0;
    }
    for (line = (addr - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES; ++line) {
        if (g_mock.consumer_valid_lines[line] == 0u) {
            return 0;
        }
    }
    return 1;
}

/* ------------------------------------------------------------------ */
/* 解析工具                                                            */
/* ------------------------------------------------------------------ */

static const char *token_value(char **tokens, unsigned count, const char *key) {
    unsigned index;
    const size_t key_len = strlen(key);
    for (index = 0u; index < count; ++index) {
        if (strncmp(tokens[index], key, key_len) == 0 && tokens[index][key_len] == '=') {
            return tokens[index] + key_len + 1u;
        }
    }
    return NULL;
}

static void copy_text(char *destination, size_t capacity, const char *source);

static unsigned long long parse_u64_text(const char *value, const char *key,
                                         unsigned long long fallback) {
    char *end = NULL;
    unsigned long long parsed;
    int base = 10;
    if (value == NULL) {
        return fallback;
    }
    if (value[0] == '\0' || value[0] == '-' || value[0] == '+' ||
        value[0] == ' ' || value[0] == '\t') {
        g_numeric_parse_error = 1;
        copy_text(g_numeric_parse_field, sizeof(g_numeric_parse_field), key);
        return fallback;
    }
    if (value[0] == '0' && (value[1] == 'x' || value[1] == 'X')) {
        base = 16;
    }
    errno = 0;
    parsed = strtoull(value, &end, base);
    if (errno == ERANGE || end == value || end == NULL || *end != '\0') {
        g_numeric_parse_error = 1;
        copy_text(g_numeric_parse_field, sizeof(g_numeric_parse_field), key);
        return fallback;
    }
    return parsed;
}

static unsigned long long value_u64(char **tokens, unsigned count, const char *key,
                                    unsigned long long fallback) {
    return parse_u64_text(token_value(tokens, count, key), key, fallback);
}

static int cli_numeric_failure(s4_inject_validation_report *report) {
    if (!g_numeric_parse_error) {
        return 0;
    }
    report->status = S4_INJECT_ERR_CLI_ARGUMENT;
    report->field = g_numeric_parse_field;
    report->reason = "CLI 数值必须是完整、非负且不溢出的十进制或 0x 十六进制整数";
    report->expected = 0u;
    report->actual = 0u;
    return 1;
}

static const char *value_str(char **tokens, unsigned count, const char *key,
                             const char *fallback) {
    const char *value = token_value(tokens, count, key);
    return value == NULL ? fallback : value;
}

static const char *const k_source_names[S4_SRC_KIND_COUNT] = {
    "file_injection", "camera", "synthetic"};
static const char *const k_format_names[S4_FMT_COUNT] = {
    "RGB888", "RGB565", "GRAY8", "INT8_CHW_416"};
static const char *const k_scope_names[S4_SCOPE_COUNT] = {
    "MEASURED", "NOT_EXECUTED_OFFLINE"};
static const char *const k_integrity_names[S4_INTEGRITY_COUNT] = {
    "crc32_ieee", "sha256"};
static const char *const k_measurement_source_names[S4_MEAS_SCOPE_SOURCE_COUNT] = {
    "OFFLINE_REGRESSION", "BOARD_INJECTION", "CAMERA"};

static int lookup_enum(const char *value, const char *const *names, int count) {
    int index;
    for (index = 0; index < count; ++index) {
        if (strcmp(value, names[index]) == 0) {
            return index;
        }
    }
    return -1;
}

static int parse_enum(const char *value, const char *const *names, int count) {
    const int found = lookup_enum(value, names, count);
    return found >= 0 ? found : 99;
}

static unsigned char *read_file_bytes(const char *path, unsigned long long *out_len) {
    FILE *handle = fopen(path, "rb");
    long size;
    unsigned char *buffer;
    if (handle == NULL) {
        return NULL;
    }
    if (fseek(handle, 0L, SEEK_END) != 0) {
        fclose(handle);
        return NULL;
    }
    size = ftell(handle);
    if (size < 0 || (unsigned long long)size > MAX_PAYLOAD) {
        fclose(handle);
        return NULL;
    }
    rewind(handle);
    buffer = (unsigned char *)malloc((size_t)size + 1u);
    if (buffer == NULL) {
        fclose(handle);
        return NULL;
    }
    if (size > 0 && fread(buffer, 1u, (size_t)size, handle) != (size_t)size) {
        free(buffer);
        fclose(handle);
        return NULL;
    }
    fclose(handle);
    *out_len = (unsigned long long)size;
    return buffer;
}

static unsigned char *pattern_bytes(unsigned long long seed, unsigned long long length) {
    unsigned char *buffer = (unsigned char *)malloc((size_t)length + 1u);
    unsigned long long index;
    unsigned long long state = seed;
    if (buffer == NULL) {
        return NULL;
    }
    for (index = 0u; index < length; ++index) {
        state = state * 6364136223846793005ULL + 1442695040888963407ULL;
        buffer[index] = (unsigned char)((state >> 33) & 0xFFu);
    }
    return buffer;
}

/* ------------------------------------------------------------------ */
/* op 执行                                                             */
/* ------------------------------------------------------------------ */

static void fill_report(s4_inject_validation_report *report) {
    report->status = S4_INJECT_OK;
    report->field = NULL;
    report->reason = "OK";
    report->expected = 0u;
    report->actual = 0u;
}

static void copy_text(char *destination, size_t capacity, const char *source) {
    if (capacity == 0u) {
        return;
    }
    if (source == NULL) {
        destination[0] = '\0';
        return;
    }
    strncpy(destination, source, capacity - 1u);
    destination[capacity - 1u] = '\0';
}

static int copy_text_checked(char *destination, size_t capacity, const char *source,
                             const char *field, s4_inject_validation_report *report) {
    if (source == NULL || strlen(source) >= capacity) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = field;
        report->reason = "文本 CLI 参数为空或超出字段容量";
        return 0;
    }
    copy_text(destination, capacity, source);
    return 1;
}

static int parse_hex_digit(char value) {
    if (value >= '0' && value <= '9') {
        return value - '0';
    }
    if (value >= 'a' && value <= 'f') {
        return value - 'a' + 10;
    }
    if (value >= 'A' && value <= 'F') {
        return value - 'A' + 10;
    }
    return -1;
}

static int op_region(char **tokens, unsigned count, s4_inject_validation_report *report) {
    const char *name = value_str(tokens, count, "name", NULL);
    const unsigned long long base = value_u64(tokens, count, "base", 0u);
    const unsigned long long length = value_u64(tokens, count, "len", 0u);
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (name == NULL || g_region_count >= S4_INJECT_MAX_REGIONS) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "region.name";
        report->reason = "region 名称缺失或超出上限";
        return (int)report->status;
    }
    if (!copy_text_checked(g_region_names[g_region_count], S4_INJECT_REGION_NAME_MAX,
                           name, "region.name", report)) {
        return (int)report->status;
    }
    g_regions[g_region_count].name = g_region_names[g_region_count];
    g_regions[g_region_count].base_addr = (uint64_t)base;
    g_regions[g_region_count].length_bytes = (uint64_t)length;
    g_region_count += 1u;
    return S4_INJECT_OK;
}

static int op_ring(char **tokens, unsigned count, s4_inject_validation_report *report) {
    /* ring_init 按值复制回调结构；cache_ctx 本身须在 ring 生命周期内保持有效。 */
    static s4_inject_cache_ops ops;
    const unsigned long long slots = value_u64(tokens, count, "slots", 2u);
    const unsigned long long session_id = value_u64(tokens, count, "session", 1u);
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (slots > UINT32_MAX || session_id > UINT32_MAX) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = slots > UINT32_MAX ? "slots" : "session";
        report->reason = "slots/session 超出 uint32 表示范围";
        return (int)report->status;
    }
    ops.flush = cache_flush_adapter;
    ops.invalidate = cache_invalidate_adapter;
    ops.barrier = cache_barrier_adapter;
    return (int)s4_inject_ring_init(&g_ring, (uint32_t)slots, (uint32_t)session_id,
                                    g_regions, g_region_count, &ops, NULL, report);
}

static int op_frame(char **tokens, unsigned count, pending_frame *frame,
                    s4_inject_validation_report *report) {
    const unsigned long long width = value_u64(tokens, count, "w", 3u);
    const unsigned long long height = value_u64(tokens, count, "h", 2u);
    const unsigned long long frame_id = value_u64(tokens, count, "id", 1u);
    const unsigned long long session_id = value_u64(tokens, count, "session", 1u);
    const unsigned long long base_addr = value_u64(tokens, count, "base", MOCK_BASE);
    const unsigned long long offset = value_u64(tokens, count, "offset", 0u);
    const unsigned long long requested_length = value_u64(tokens, count, "len", ULLONG_MAX);
    const unsigned long long alignment = value_u64(tokens, count, "align", 64u);
    const unsigned long long capture_available = value_u64(tokens, count, "capture_avail", 0u);
    const unsigned long long injection_start = value_u64(tokens, count, "inject_ns", 1000000u);
    const unsigned long long clock_freq = value_u64(tokens, count, "freq", 100000000u);
    const unsigned long long capture_ns =
        (token_value(tokens, count, "capture") != NULL &&
         strcmp(value_str(tokens, count, "capture", "unavailable"), "unavailable") != 0)
            ? value_u64(tokens, count, "capture", 0u)
            : 0u;
    const int format = parse_enum(value_str(tokens, count, "fmt", "RGB888"), k_format_names,
                                  (int)S4_FMT_COUNT);
    unsigned long long stride = value_u64(tokens, count, "stride", 0u);
    unsigned long long derived = 0u;
    unsigned long long length;
    const char *region_name = value_str(tokens, count, "region", NULL);
    const char *payload_spec;
    const char *digest_spec;
    s4_inject_status derived_status = S4_INJECT_OK;
    unsigned long long payload_length_arg;
    unsigned long long pattern_seed;
    const char *contract_version;
    const char *source_text;
    const char *scope_source_text;
    const char *clock_text;
    const char *wrap_text;
    const char *epoch_text;
    const char *domain_text;
    int source;
    int scope_source;
    int algorithm;
    unsigned index;

    if (frame->payload != NULL) {
        free(frame->payload);
        frame->payload = NULL;
        frame->payload_length = 0u;
    }
    frame->valid = 0;
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (width > UINT32_MAX || height > UINT32_MAX || frame_id > UINT32_MAX ||
        session_id > UINT32_MAX || stride > UINT32_MAX || alignment > UINT32_MAX ||
        capture_available > 1u) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = width > UINT32_MAX ? "width" :
                        height > UINT32_MAX ? "height" :
                        frame_id > UINT32_MAX ? "frame_id" :
                        session_id > UINT32_MAX ? "session_id" :
                        stride > UINT32_MAX ? "stride_bytes" :
                        alignment > UINT32_MAX ? "alignment" : "capture_time_available";
        report->reason = "数值超出字段位宽或 capture_time_available 不是 0/1";
        return (int)report->status;
    }
    memset(&frame->desc, 0, sizeof(frame->desc));
    source_text = value_str(tokens, count, "source", "file_injection");
    source = lookup_enum(source_text, k_source_names, (int)S4_SRC_KIND_COUNT);
    scope_source_text = value_str(tokens, count, "scope_source", NULL);
    if (scope_source_text == NULL) {
        scope_source = source == (int)S4_SRC_CAMERA ? (int)S4_MEAS_SCOPE_CAMERA
                       : source == (int)S4_SRC_SYNTHETIC ? (int)S4_MEAS_SCOPE_OFFLINE_REGRESSION
                                                        : (int)S4_MEAS_SCOPE_BOARD_INJECTION;
    } else {
        scope_source = lookup_enum(scope_source_text, k_measurement_source_names,
                                   (int)S4_MEAS_SCOPE_SOURCE_COUNT);
    }
    contract_version = value_str(tokens, count, "contract", S4_INJECT_CONTRACT_VERSION);
    clock_text = value_str(tokens, count, "clock", "XTime_GlobalTimer");
    wrap_text = value_str(tokens, count, "wrap", "reject_wrap_explicit_reset");
    epoch_text = value_str(tokens, count, "epoch", "relative_to_ps_boot");
    domain_text = value_str(tokens, count, "domain", "PS 100MHz global timer");
    if (source < 0 || scope_source < 0) {
        report->status = source < 0 ? S4_INJECT_ERR_SOURCE_KIND : S4_INJECT_ERR_MEASUREMENT_SCOPE;
        report->field = source < 0 ? "source" : "measurement_scope.source_kind";
        report->reason = "source_kind 或 measurement_scope.source_kind 不在契约词表内";
        return (int)report->status;
    }
    if (format < 0 || format >= (int)S4_FMT_COUNT) {
        report->status = S4_INJECT_ERR_PIXEL_FORMAT;
        report->field = "pixel_format";
        report->reason = "pixel_format 不在契约词表内";
        return (int)report->status;
    }
    if (!copy_text_checked(frame->desc.contract_version, sizeof(frame->desc.contract_version),
                           contract_version, "contract_version", report) ||
        !copy_text_checked(frame->desc.region_name, sizeof(frame->desc.region_name),
                           region_name == NULL && g_region_count > 0u ? g_regions[0].name
                                                                     : (region_name == NULL ? "" : region_name),
                           "region_name", report) ||
        !copy_text_checked(frame->desc.clock_name, sizeof(frame->desc.clock_name),
                           clock_text, "clock", report) ||
        !copy_text_checked(frame->desc.wrap_handling, sizeof(frame->desc.wrap_handling),
                           wrap_text, "wrap_handling", report) ||
        !copy_text_checked(frame->desc.epoch_note, sizeof(frame->desc.epoch_note),
                           epoch_text, "epoch_note", report) ||
        !copy_text_checked(frame->desc.clock_domain, sizeof(frame->desc.clock_domain),
                           domain_text, "clock_domain", report)) {
        return (int)report->status;
    }
    frame->desc.source_kind = (s4_inject_source_kind)source;
    frame->desc.session_id = (uint32_t)session_id;
    frame->desc.frame_id = (uint32_t)frame_id;
    frame->desc.width = (uint32_t)width;
    frame->desc.height = (uint32_t)height;
    frame->desc.pixel_format = (s4_inject_pixel_format)format;
    if (stride == 0u && format >= 0 && format < (int)S4_FMT_COUNT) {
        stride = s4_inject_min_stride((s4_inject_pixel_format)format, (uint32_t)width);
    }
    frame->desc.stride_bytes = (uint32_t)stride;
    frame->desc.base_addr = (uint64_t)base_addr;
    frame->desc.offset_bytes = (uint64_t)offset;
    if (format >= 0 && format < (int)S4_FMT_COUNT) {
        derived = s4_inject_expected_frame_bytes((s4_inject_pixel_format)format, (uint32_t)stride,
                                                 (uint32_t)width, (uint32_t)height,
                                                 &derived_status);
    }
    length = token_value(tokens, count, "len") == NULL ? derived : requested_length;
    frame->desc.length_bytes = length;
    frame->desc.alignment = (uint32_t)alignment;
    if (token_value(tokens, count, "capture") != NULL &&
        strcmp(value_str(tokens, count, "capture", "unavailable"), "unavailable") != 0) {
        frame->desc.capture_time_state = S4_CAPTURE_PROVIDED;
        frame->desc.capture_time_ns = (uint64_t)capture_ns;
    } else {
        frame->desc.capture_time_state = S4_CAPTURE_UNAVAILABLE;
        frame->desc.capture_time_ns = 0u;
    }
    frame->desc.injection_start_ns = (uint64_t)injection_start;
    frame->desc.clock_freq_hz = (uint64_t)clock_freq;
    frame->desc.measurement_scope_source_kind = (s4_measurement_scope_source_kind)scope_source;
    frame->desc.scope_pl_timing = (s4_inject_scope_value)parse_enum(
        value_str(tokens, count, "scope_pl", "NOT_EXECUTED_OFFLINE"), k_scope_names,
        (int)S4_SCOPE_COUNT);
    frame->desc.scope_uart_transport = (s4_inject_scope_value)parse_enum(
        value_str(tokens, count, "scope_uart", "NOT_EXECUTED_OFFLINE"), k_scope_names,
        (int)S4_SCOPE_COUNT);
    frame->desc.scope_board_pl = (s4_inject_scope_value)parse_enum(
        value_str(tokens, count, "scope_board", "NOT_EXECUTED_OFFLINE"), k_scope_names,
        (int)S4_SCOPE_COUNT);
    /* 契约字段是 capture_time_available（true=有真实采集时间）；
     * C 侧字段 unavailable_capture_time 表示“capture_time 已列入 unavailable_fields”，
     * 二者互补：capture_avail=0（注入）=> unavailable=1，capture_avail=1（camera）=> unavailable=0。 */
    frame->desc.unavailable_capture_time = capture_available == 0u ? 1u : 0u;

    payload_spec = value_str(tokens, count, "payload", "pattern:1");
    if (strncmp(payload_spec, "file:", 5u) == 0) {
        frame->payload = read_file_bytes(payload_spec + 5u, &frame->payload_length);
    } else if (strncmp(payload_spec, "pattern:", 8u) == 0) {
        pattern_seed = parse_u64_text(payload_spec + 8u, "payload.seed", 0u);
        payload_length_arg = value_u64(tokens, count, "payload_len", length);
        if (cli_numeric_failure(report)) {
            return (int)report->status;
        }
        if (payload_length_arg > MAX_PAYLOAD || payload_length_arg > (unsigned long long)SIZE_MAX - 1u) {
            report->status = S4_INJECT_ERR_LENGTH;
            report->field = "payload_len";
            report->reason = "主机 payload 超出离线 harness 容量或 size_t 范围";
            return (int)report->status;
        }
        frame->payload_length = payload_length_arg;
        frame->payload = pattern_bytes(pattern_seed, frame->payload_length);
    } else {
        frame->payload = NULL;
    }
    if (frame->payload == NULL) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "payload";
        report->reason = "payload 不可读或生成失败";
        return (int)report->status;
    }
    frame->desc.integrity_algorithm = S4_INTEGRITY_CRC32_IEEE;
    algorithm = lookup_enum(value_str(tokens, count, "algorithm", "crc32_ieee"),
                            k_integrity_names, (int)S4_INTEGRITY_COUNT);
    if (algorithm < 0) {
        report->status = S4_INJECT_ERR_INTEGRITY;
        report->field = "frame_integrity.algorithm";
        report->reason = "algorithm 必须是 crc32_ieee 或 sha256";
        return (int)report->status;
    }
    if (algorithm == (int)S4_INTEGRITY_SHA256) {
        frame->desc.integrity_algorithm = S4_INTEGRITY_SHA256;
    }
    frame->desc.integrity_crc32 =
        s4_inject_crc32(frame->payload, (size_t)frame->payload_length);
    s4_inject_sha256(frame->payload, (size_t)frame->payload_length,
                     frame->desc.integrity_sha256);
    digest_spec = value_str(tokens, count, "digest", "auto");
    if (strcmp(digest_spec, "none") == 0) {
        frame->desc.integrity_crc32 = 0u;
        memset(frame->desc.integrity_sha256, 0, sizeof(frame->desc.integrity_sha256));
    } else if (strcmp(digest_spec, "wrong") == 0) {
        frame->desc.integrity_crc32 ^= 0x5A5A5A5Au;
        frame->desc.integrity_sha256[0] ^= 0xFFu;
    } else if (strcmp(digest_spec, "auto") != 0) {
        const size_t expected_hex = frame->desc.integrity_algorithm == S4_INTEGRITY_SHA256 ? 64u : 8u;
        if (strlen(digest_spec) != expected_hex) {
            report->status = S4_INJECT_ERR_CLI_ARGUMENT;
            report->field = "digest";
            report->reason = "digest 必须为与 algorithm 匹配的完整十六进制摘要";
            return (int)report->status;
        }
        for (index = 0u; index < expected_hex; index += 2u) {
            const int high = parse_hex_digit(digest_spec[index]);
            const int low = parse_hex_digit(digest_spec[index + 1u]);
            if (high < 0 || low < 0) {
                report->status = S4_INJECT_ERR_CLI_ARGUMENT;
                report->field = "digest";
                report->reason = "digest 含非十六进制字符";
                return (int)report->status;
            }
            if (frame->desc.integrity_algorithm == S4_INTEGRITY_SHA256) {
                frame->desc.integrity_sha256[index / 2u] = (uint8_t)((high << 4) | low);
            } else {
                frame->desc.integrity_crc32 =
                    (frame->desc.integrity_crc32 << 8) | (uint32_t)((high << 4) | low);
            }
        }
    }
    frame->valid = 1;
    return S4_INJECT_OK;
}

static int op_bind(char **tokens, unsigned count, pending_frame *frame,
                   s4_inject_validation_report *report) {
    unsigned long long slot = value_u64(tokens, count, "slot", (unsigned long long)-1);
    uint32_t target = 0u;
    s4_inject_status status;
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (!frame->valid) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "frame";
        report->reason = "尚未用 frame op 描述帧";
        return (int)report->status;
    }
    status = s4_inject_validate(&frame->desc, g_regions, g_region_count, frame->payload,
                                (uint64_t)frame->payload_length, report);
    if (status != S4_INJECT_OK) {
        return (int)status;
    }
    if (frame->desc.base_addr > UINT64_MAX - frame->desc.offset_bytes ||
        !mock_ok(frame->desc.base_addr + frame->desc.offset_bytes,
                 frame->payload_length)) {
        report->status = S4_INJECT_ERR_BUFFER_RANGE;
        report->field = "mock_ddr";
        report->reason = "帧区间不在 mock DDR 窗口内；未修改 mock DDR";
        return (int)report->status;
    }
    if (slot == (unsigned long long)-1) {
        status = s4_inject_ring_acquire(&g_ring, &target, report);
        if (status != S4_INJECT_OK) {
            return (int)status;
        }
    } else {
        if (slot > UINT32_MAX) {
            report->status = S4_INJECT_ERR_CLI_ARGUMENT;
            report->field = "slot";
            report->reason = "slot 超出 uint32 表示范围";
            return (int)report->status;
        }
        target = (uint32_t)slot;
    }
    status = s4_inject_ring_bind(&g_ring, target, &frame->desc, frame->payload,
                                 frame->payload_length, report);
    if (status != S4_INJECT_OK) {
        return (int)status;
    }
    if (!mock_write(frame->desc.base_addr + frame->desc.offset_bytes, frame->payload,
                    frame->payload_length)) {
        report->status = S4_INJECT_ERR_BUFFER_RANGE;
        report->field = "mock_ddr";
        report->reason = "帧区间不在 mock DDR 窗口内";
        return (int)report->status;
    }
    g_bind_slot = target;
    report->actual = target;
    return S4_INJECT_OK;
}

static int op_drop(pending_frame *frame, s4_inject_validation_report *report) {
    if (!frame->valid) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "frame";
        report->reason = "尚未用 frame op 描述帧";
        return (int)report->status;
    }
    return (int)s4_inject_ring_drop(&g_ring, &frame->desc, report);
}

static int op_advance(char **tokens, unsigned count, s4_inject_validation_report *report) {
    const unsigned long long slot = value_u64(tokens, count, "slot", 0u);
    const char *event_name = value_str(tokens, count, "ev", "");
    int event = -1;
    int index;
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (slot > UINT32_MAX) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = "slot";
        report->reason = "slot 超出 uint32 表示范围";
        return (int)report->status;
    }
    for (index = 0; index < (int)S4_EV_COUNT; ++index) {
        if (strcmp(event_name, s4_inject_event_name((s4_inject_event)index)) == 0) {
            event = index;
        }
    }
    if (event < 0) {
        report->status = S4_INJECT_ERR_EVENT_ORDER;
        report->field = "ev";
        report->reason = "未知事件名";
        return (int)report->status;
    }
    if (slot >= g_ring.slot_count) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "slot";
        report->reason = "槽位越界";
        return (int)report->status;
    }
    if ((s4_inject_event)event == S4_EV_PUBLISH &&
        g_ring.slots[slot].state == S4_SLOT_FLUSHED) {
        const s4_inject_slot *entry = &g_ring.slots[slot];
        const unsigned long long dirty =
            mock_dirty_bytes(entry->addr_start, entry->desc.length_bytes);
        if (dirty != 0u) {
            report->status = S4_INJECT_ERR_FLUSH_COVERAGE;
            report->field = "cache_flush_by_producer";
            report->reason = "发布时帧区间仍有脏 cache 行：flush 缺失或覆盖不足";
            report->expected = 0u;
            report->actual = dirty;
            return (int)report->status;
        }
    }
    return (int)s4_inject_ring_advance(&g_ring, (uint32_t)slot, (s4_inject_event)event, report);
}

static int op_consume(char **tokens, unsigned count, s4_inject_validation_report *report) {
    const unsigned long long slot = value_u64(tokens, count, "slot", 0u);
    const unsigned long long busy = value_u64(tokens, count, "busy", 0u);
    s4_inject_status status;
    uint32_t crc = 0u;
    uint64_t valid_bytes = 0u;
    uint64_t padding_bytes = 0u;
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (busy > ULLONG_MAX - g_consumer_busy_ticks) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = "busy";
        report->reason = "累计 busy ticks 超出 uint64 范围";
        return (int)report->status;
    }
    if (slot > UINT32_MAX) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = "slot";
        report->reason = "slot 超出 uint32 表示范围";
        return (int)report->status;
    }
    if (slot >= g_ring.slot_count) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "slot";
        report->reason = "槽位越界";
        return (int)report->status;
    }
    g_consumer_busy_ticks += busy;
    status = s4_inject_ring_advance(&g_ring, (uint32_t)slot, S4_EV_INVALIDATE, report);
    if (status != S4_INJECT_OK) {
        return (int)status;
    }
    if (!mock_consumer_range_valid(g_ring.slots[slot].addr_start,
                                   g_ring.slots[slot].desc.length_bytes)) {
        report->status = S4_INJECT_ERR_CACHE_VISIBILITY;
        report->field = "consumer_invalidate";
        report->reason = "消费者视图无效：invalidate 范围/顺序缺失或 backing DDR 未可见";
        report->expected = 1u;
        report->actual = 0u;
        return (int)report->status;
    }
    status = s4_inject_ring_advance(&g_ring, (uint32_t)slot, S4_EV_CONSUMER_START, report);
    if (status != S4_INJECT_OK) {
        return (int)status;
    }
    status = s4_inject_ring_consumer_read(&g_ring, (uint32_t)slot, g_mock.consumer_view,
                                          MOCK_LEN, MOCK_BASE,
                                          &crc, &valid_bytes, &padding_bytes, report);
    if (status != S4_INJECT_OK) {
        return (int)status;
    }
    g_consumer_crc32 = crc;
    g_consumer_valid_bytes = valid_bytes;
    g_consumer_padding_bytes = padding_bytes;
    g_consumer_reads += 1u;
    return (int)s4_inject_ring_advance(&g_ring, (uint32_t)slot, S4_EV_CONSUMER_DONE, report);
}

static int op_timeout(char **tokens, unsigned count, s4_inject_validation_report *report) {
    const unsigned long long slot = value_u64(tokens, count, "slot", 0u);
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (slot > UINT32_MAX) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = "slot";
        report->reason = "slot 超出 uint32 表示范围";
        return (int)report->status;
    }
    return (int)s4_inject_ring_timeout(&g_ring, (uint32_t)slot, report);
}

static int op_abort(char **tokens, unsigned count, s4_inject_validation_report *report) {
    const unsigned long long slot = value_u64(tokens, count, "slot", 0u);
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (slot > UINT32_MAX) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = "slot";
        report->reason = "slot 超出 uint32 表示范围";
        return (int)report->status;
    }
    return (int)s4_inject_ring_abort(&g_ring, (uint32_t)slot, report);
}

static int op_consumer_stopped(char **tokens, unsigned count,
                               s4_inject_validation_report *report) {
    const unsigned long long slot = value_u64(tokens, count, "slot", 0u);
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (slot > UINT32_MAX) {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = "slot";
        report->reason = "slot 超出 uint32 表示范围";
        return (int)report->status;
    }
    return (int)s4_inject_ring_confirm_consumer_stopped(&g_ring, (uint32_t)slot, report);
}

static int op_mock_maintenance(char **tokens, unsigned count, int is_flush,
                               s4_inject_validation_report *report) {
    const unsigned long long base = value_u64(tokens, count, "base", 0u);
    const unsigned long long len = value_u64(tokens, count, "len", 0u);
    if (cli_numeric_failure(report)) {
        return (int)report->status;
    }
    if (is_flush) {
        mock_flush(base, len);
    } else {
        mock_invalidate(base, len);
    }
    return S4_INJECT_OK;
}

static int op_mock_fault(char **tokens, unsigned count, s4_inject_validation_report *report) {
    const char *fault = value_str(tokens, count, "name", "");
    if (strcmp(fault, "skip_flush") == 0) {
        g_mock.skip_next_flush = 1;
    } else if (strcmp(fault, "skip_invalidate") == 0) {
        g_mock.skip_next_invalidate = 1;
    } else if (strcmp(fault, "shift_invalidate") == 0) {
        g_mock.shift_next_invalidate = 1;
    } else if (strcmp(fault, "skip_barrier") == 0) {
        g_mock.skip_next_barrier = 1;
    } else {
        report->status = S4_INJECT_ERR_CLI_ARGUMENT;
        report->field = "mock_fault.name";
        report->reason = "未知 mock fault；允许 skip_flush/skip_invalidate/shift_invalidate/skip_barrier";
        return (int)report->status;
    }
    report->status = S4_INJECT_OK;
    report->field = NULL;
    report->reason = "mock fault 已安排，仅用于离线反例";
    return S4_INJECT_OK;
}

/* ------------------------------------------------------------------ */
/* op 脚本执行与 JSON 输出                                             */
/* ------------------------------------------------------------------ */

static void record_op(unsigned index, const char *op, int status,
                      const s4_inject_validation_report *report, int is_try) {
    op_record *record = &g_ops[index];
    record->index = index;
    copy_text(record->op, sizeof(record->op), op);
    record->status = status;
    record->field = report->field;
    copy_text(record->reason, sizeof(record->reason), report->reason);
    record->actual = report->actual;
    record->is_try = is_try;
    g_op_count = index + 1u;
    if (status != S4_INJECT_OK) {
        copy_text(g_last_reason, sizeof(g_last_reason), report->reason);
        if (!is_try && g_first_error == S4_INJECT_OK) {
            g_first_error = status;
        }
    }
}

static void print_json_string(const char *value) {
    const unsigned char *cursor = (const unsigned char *)(value == NULL ? "" : value);
    putchar('"');
    while (*cursor != 0u) {
        if (*cursor == '"' || *cursor == '\\') {
            putchar('\\');
            putchar((int)*cursor);
        } else if (*cursor < 0x20u) {
            printf("\\u%04x", (unsigned)*cursor);
        } else {
            putchar((int)*cursor);
        }
        cursor += 1;
    }
    putchar('"');
}

static int run_script(FILE *handle) {
    char line[MAX_LINE];
    char *tokens[MAX_TOKENS];
    char joined[MAX_LINE];
    pending_frame frame;
    s4_inject_validation_report report;
    unsigned index = 0u;
    int is_try;
    int status;

    memset(&frame, 0, sizeof(frame));
    fill_report(&report);
    while (fgets(line, (int)sizeof(line), handle) != NULL) {
        char *cursor = line;
        unsigned count = 0u;
        unsigned part;
        while (*cursor != '\0') {
            while (*cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n') {
                *cursor = '\0';
                cursor += 1;
            }
            if (*cursor == '\0' || *cursor == '#') {
                break;
            }
            if (count < MAX_TOKENS) {
                tokens[count++] = cursor;
            }
            while (*cursor != '\0' && *cursor != ' ' && *cursor != '\t' && *cursor != '\r' &&
                   *cursor != '\n') {
                cursor += 1;
            }
        }
        if (count == 0u) {
            continue;
        }
        is_try = 0;
        if (strcmp(tokens[0], "try") == 0) {
            is_try = 1;
            for (part = 1u; part < count; ++part) {
                tokens[part - 1u] = tokens[part];
            }
            count -= 1u;
            if (count == 0u) {
                continue;
            }
        }
        if (index >= MAX_OPS) {
            break;
        }
        g_numeric_parse_error = 0;
        g_numeric_parse_field[0] = '\0';
        joined[0] = '\0';
        for (part = 0u; part < count; ++part) {
            if (part > 0u) {
                copy_text(joined + strlen(joined), sizeof(joined) - strlen(joined), " ");
            }
            copy_text(joined + strlen(joined), sizeof(joined) - strlen(joined), tokens[part]);
        }
        fill_report(&report);
        if (strcmp(tokens[0], "region") == 0) {
            status = op_region(tokens, count, &report);
        } else if (strcmp(tokens[0], "ring") == 0) {
            status = op_ring(tokens, count, &report);
        } else if (strcmp(tokens[0], "frame") == 0) {
            status = op_frame(tokens, count, &frame, &report);
        } else if (strcmp(tokens[0], "bind") == 0) {
            status = op_bind(tokens, count, &frame, &report);
        } else if (strcmp(tokens[0], "drop") == 0) {
            status = op_drop(&frame, &report);
        } else if (strcmp(tokens[0], "advance") == 0) {
            status = op_advance(tokens, count, &report);
        } else if (strcmp(tokens[0], "consume") == 0) {
            status = op_consume(tokens, count, &report);
        } else if (strcmp(tokens[0], "timeout") == 0) {
            status = op_timeout(tokens, count, &report);
        } else if (strcmp(tokens[0], "abort") == 0) {
            status = op_abort(tokens, count, &report);
        } else if (strcmp(tokens[0], "consumer_stopped") == 0) {
            status = op_consumer_stopped(tokens, count, &report);
        } else if (strcmp(tokens[0], "mock_fault") == 0) {
            status = op_mock_fault(tokens, count, &report);
        } else if (strcmp(tokens[0], "mock_flush") == 0) {
            status = op_mock_maintenance(tokens, count, 1, &report);
        } else if (strcmp(tokens[0], "mock_invalidate") == 0) {
            status = op_mock_maintenance(tokens, count, 0, &report);
        } else if (strcmp(tokens[0], "note") == 0) {
            status = S4_INJECT_OK;
        } else {
            report.status = S4_INJECT_ERR_NULL_ARG;
            report.field = "op";
            report.reason = "未知 op";
            status = (int)report.status;
        }
        if (g_numeric_parse_error && status == S4_INJECT_OK) {
            status = (int)S4_INJECT_ERR_CLI_ARGUMENT;
            (void)cli_numeric_failure(&report);
        }
        if (index > 0u) {
            printf(",\n");
        }
        printf("{\"index\": %u, \"try\": %s, \"op\": ", index,
               is_try ? "true" : "false");
        print_json_string(joined);
        printf(", \"status\": %d, \"status_name\": ", status);
        print_json_string(s4_inject_status_name((s4_inject_status)status));
        printf(", \"field\": ");
        if (report.field == NULL) {
            printf("null");
        } else {
            print_json_string(report.field);
        }
        printf(", \"reason\": ");
        print_json_string(report.reason);
        printf(", \"actual\": %llu}", report.actual);
        record_op(index, joined, status, &report, is_try);
        index += 1u;
        if (status != S4_INJECT_OK && !is_try) {
            break;
        }
    }
    if (frame.payload != NULL) {
        free(frame.payload);
        frame.payload = NULL;
    }
    return g_first_error;
}

static void print_ring(void) {
    unsigned index;
    printf("  \"ring\": {\n");
    printf("    \"slot_count\": %u, \"in_flight\": %u, \"held\": %u,\n", g_ring.slot_count,
           g_ring.in_flight, s4_inject_ring_held_count(&g_ring));
    printf("    \"last_released_frame_id\": %u, \"flush_events\": %llu, "
           "\"has_released_frame\": %u, \"session_id\": %u, \"session_initialized\": %u, "
           "\"last_accepted_frame_id\": %u, \"has_accepted_frame\": %u, "
           "\"invalidate_events\": %llu, \"timeout_events\": %llu, \"dropped_frames\": %llu,\n",
           g_ring.last_released_frame_id, (unsigned long long)g_ring.flush_events,
           g_ring.has_released_frame, g_ring.session_id, g_ring.session_initialized,
           g_ring.last_accepted_frame_id, g_ring.has_accepted_frame,
           (unsigned long long)g_ring.invalidate_events,
           (unsigned long long)g_ring.timeout_events, (unsigned long long)g_ring.dropped_frames);
    printf("    \"last_bind_slot\": %llu,\n", g_bind_slot);
    printf("    \"slots\": [");
    for (index = 0u; index < g_ring.slot_count; ++index) {
        const s4_inject_slot *slot = &g_ring.slots[index];
        printf("%s{\"slot\": %u, \"state\": \"%s\", \"session_id\": %u, "
               "\"frame_id\": %u, \"source_kind\": \"%s\", \"measurement_scope_source_kind\": \"%s\", "
               "\"capture_time_ns\": %llu, \"unavailable_capture_time\": %u, "
               "\"consumer_stopped_confirmed\": %u, \"events_mask\": %u, "
               "\"integrity_checked\": %u, \"flush_bytes\": %llu, \"invalidate_bytes\": %llu}",
               index == 0u ? "" : ", ", index, s4_inject_slot_state_name(slot->state),
               slot->state == S4_SLOT_FREE ? 0u : slot->desc.session_id,
               slot->state == S4_SLOT_FREE ? 0u : slot->desc.frame_id,
               slot->state == S4_SLOT_FREE ? "none" : s4_inject_source_kind_name(slot->desc.source_kind),
               slot->state == S4_SLOT_FREE ? "none" :
                   k_measurement_source_names[slot->desc.measurement_scope_source_kind],
               (unsigned long long)(slot->state == S4_SLOT_FREE ? 0u : slot->desc.capture_time_ns),
               slot->state == S4_SLOT_FREE ? 0u : slot->desc.unavailable_capture_time,
               slot->consumer_stopped_confirmed, slot->observed_events,
               slot->integrity_checked, (unsigned long long)slot->flush_rounded_bytes,
               (unsigned long long)slot->invalidate_rounded_bytes);
    }
    printf("]\n  },\n");
}

static void print_mock(void) {
    unsigned index;
    printf("  \"mock_cache\": {\n");
    printf("    \"flush_count\": %lu, \"invalidate_count\": %lu, \"flushed_bytes\": %llu, "
           "\"invalidated_bytes\": %llu, \"dirty_lost_lines\": %llu, "
           "\"barrier_count\": %lu, \"barrier_failures\": %lu,\n",
           g_mock.flush_count, g_mock.invalidate_count, (unsigned long long)g_mock.flushed_bytes,
           (unsigned long long)g_mock.invalidated_bytes, (unsigned long long)g_mock.dirty_lost,
           g_mock.barrier_count, g_mock.barrier_failures);
    printf("    \"flush_ranges\": [");
    for (index = 0u; index < g_mock.flush_count && index < MAX_CACHE_EVENTS; ++index) {
        printf("%s[%llu, %llu]", index == 0u ? "" : ", ", g_mock.flush_ranges[index].base,
               g_mock.flush_ranges[index].base + g_mock.flush_ranges[index].len);
    }
    printf("],\n    \"invalidate_ranges\": [");
    for (index = 0u; index < g_mock.invalidate_count && index < MAX_CACHE_EVENTS; ++index) {
        printf("%s[%llu, %llu]", index == 0u ? "" : ", ", g_mock.invalidate_ranges[index].base,
               g_mock.invalidate_ranges[index].base + g_mock.invalidate_ranges[index].len);
    }
    printf("],\n    \"write_count\": %lu, \"write_records\": [", g_mock.write_count);
    for (index = 0u; index < g_mock.write_count && index < MAX_CACHE_EVENTS; ++index) {
        printf("%s{\"range\": [%llu, %llu], \"length\": %llu, \"crc32\": %u}",
               index == 0u ? "" : ", ", g_mock.write_ranges[index].base,
               g_mock.write_ranges[index].base + g_mock.write_ranges[index].len,
               g_mock.write_ranges[index].len, g_mock.write_crc32[index]);
    }
    printf("]\n  },\n");
}

int main(int argc, char **argv) {
    FILE *handle;
    int status;
    unsigned index;
    if (argc < 2) {
        fprintf(stderr, "usage: %s <op_script>\n", argv[0]);
        return (int)S4_INJECT_ERR_NULL_ARG;
    }
    g_mock.producer_cache = (unsigned char *)calloc((size_t)MOCK_LEN, 1u);
    g_mock.ddr = (unsigned char *)calloc((size_t)MOCK_LEN, 1u);
    g_mock.consumer_view = (unsigned char *)calloc((size_t)MOCK_LEN, 1u);
    g_mock.dirty_lines = (unsigned char *)calloc((size_t)(MOCK_LEN / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES), 1u);
    g_mock.consumer_valid_lines =
        (unsigned char *)calloc((size_t)(MOCK_LEN / S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES), 1u);
    if (g_mock.producer_cache == NULL || g_mock.ddr == NULL || g_mock.consumer_view == NULL ||
        g_mock.dirty_lines == NULL || g_mock.consumer_valid_lines == NULL) {
        fprintf(stderr, "mock allocation failed\n");
        return (int)S4_INJECT_ERR_NULL_ARG;
    }
    handle = fopen(argv[1], "r");
    if (handle == NULL) {
        fprintf(stderr, "cannot open op script: %s\n", argv[1]);
        return (int)S4_INJECT_ERR_NULL_ARG;
    }
    printf("{\n  \"tool\": \"s4_inject_frame_host\",\n  \"contract_version\": \"%s\",\n",
           S4_INJECT_CONTRACT_VERSION);
    printf("  \"ops\": [\n");
    status = run_script(handle);
    fclose(handle);
    printf("\n  ],\n");
    printf("  \"status\": %d,\n  \"status_name\": \"%s\",\n  \"last_failure_reason\": \"%s\",\n",
           status, s4_inject_status_name((s4_inject_status)status), g_last_reason);
    print_ring();
    print_mock();
    printf("  \"consumer\": {\"reads\": %llu, \"last_crc32\": %llu, \"valid_bytes\": %llu, "
           "\"padding_bytes\": %llu, \"padding_consumed\": 0, \"busy_ticks\": %llu},\n",
           g_consumer_reads, g_consumer_crc32, g_consumer_valid_bytes, g_consumer_padding_bytes,
           g_consumer_busy_ticks);
    printf("  \"op_count\": %u\n}\n", g_op_count);
    for (index = 0u; index < g_op_count; ++index) {
        /* 保持 g_ops 可读（JSON 已逐条写出），无额外动作 */
    }
    free(g_mock.producer_cache);
    free(g_mock.ddr);
    free(g_mock.consumer_view);
    free(g_mock.dirty_lines);
    free(g_mock.consumer_valid_lines);
    return status;
}
