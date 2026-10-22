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
    unsigned char *ddr;
    unsigned char *dirty;
    unsigned char *valid;
    unsigned long long dirty_lost;
    mock_range flush_ranges[MAX_CACHE_EVENTS];
    mock_range invalidate_ranges[MAX_CACHE_EVENTS];
    unsigned long flush_count;
    unsigned long invalidate_count;
    unsigned long long flushed_bytes;
    unsigned long long invalidated_bytes;
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

/* ------------------------------------------------------------------ */
/* mock cache / DDR                                                    */
/* ------------------------------------------------------------------ */

static int mock_ok(unsigned long long addr, unsigned long long len) {
    return len != 0u && addr >= MOCK_BASE && addr + len <= MOCK_BASE + MOCK_LEN &&
           addr + len >= addr;
}

static void mock_mark(unsigned long long addr, unsigned long long len, int dirty) {
    unsigned long long line;
    for (line = (addr - MOCK_BASE) / S4_INJECT_CACHE_LINE_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_CACHE_LINE_BYTES; ++line) {
        g_mock.valid[line] = 1u;
        if (dirty) {
            g_mock.dirty[line] = 1u;
        }
    }
}

static int mock_write(unsigned long long addr, const unsigned char *data,
                      unsigned long long len) {
    if (!mock_ok(addr, len)) {
        return 0;
    }
    memcpy(g_mock.ddr + (addr - MOCK_BASE), data, (size_t)len);
    mock_mark(addr, len, 1);
    return 1;
}

static void mock_flush(unsigned long long addr, unsigned long long len) {
    unsigned long long line;
    if (!mock_ok(addr, len)) {
        return;
    }
    for (line = (addr - MOCK_BASE) / S4_INJECT_CACHE_LINE_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_CACHE_LINE_BYTES; ++line) {
        g_mock.dirty[line] = 0u;
        g_mock.valid[line] = 1u;
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
    for (line = (addr - MOCK_BASE) / S4_INJECT_CACHE_LINE_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_CACHE_LINE_BYTES; ++line) {
        if (g_mock.dirty[line] != 0u) {
            g_mock.dirty_lost += 1u; /* 未 flush 就 invalidate：真实数据会丢 */
        }
        g_mock.dirty[line] = 0u;
        g_mock.valid[line] = 0u;
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
    for (line = (addr - MOCK_BASE) / S4_INJECT_CACHE_LINE_BYTES;
         line <= (addr + len - 1u - MOCK_BASE) / S4_INJECT_CACHE_LINE_BYTES; ++line) {
        const unsigned long long line_addr = MOCK_BASE + line * S4_INJECT_CACHE_LINE_BYTES;
        const unsigned long long line_end = line_addr + S4_INJECT_CACHE_LINE_BYTES;
        const unsigned long long overlap_start = line_addr > addr ? line_addr : addr;
        const unsigned long long overlap_end = line_end < addr + len ? line_end : addr + len;
        if (g_mock.dirty[line] != 0u && overlap_start < overlap_end) {
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

static unsigned long long value_u64(char **tokens, unsigned count, const char *key,
                                    unsigned long long fallback) {
    const char *value = token_value(tokens, count, key);
    if (value == NULL) {
        return fallback;
    }
    return strtoull(value, NULL, 0);
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

static int op_region(char **tokens, unsigned count, s4_inject_validation_report *report) {
    const char *name = value_str(tokens, count, "name", NULL);
    if (name == NULL || g_region_count >= S4_INJECT_MAX_REGIONS) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "region.name";
        report->reason = "region 名称缺失或超出上限";
        return (int)report->status;
    }
    copy_text(g_region_names[g_region_count], S4_INJECT_REGION_NAME_MAX, name);
    g_regions[g_region_count].name = g_region_names[g_region_count];
    g_regions[g_region_count].base_addr = value_u64(tokens, count, "base", 0u);
    g_regions[g_region_count].length_bytes = value_u64(tokens, count, "len", 0u);
    g_region_count += 1u;
    return S4_INJECT_OK;
}

static int op_ring(char **tokens, unsigned count, s4_inject_validation_report *report) {
    /* 环只保存指针（s4_inject_ring_init 不复制结构），因此这里必须是静态存储期，
     * 否则 op_ring 返回后 cache 适配指针悬垂。 */
    static s4_inject_cache_ops ops;
    const unsigned long long slots = value_u64(tokens, count, "slots", 2u);
    ops.flush = cache_flush_adapter;
    ops.invalidate = cache_invalidate_adapter;
    return (int)s4_inject_ring_init(&g_ring, (uint32_t)slots, g_regions, g_region_count, &ops,
                                    NULL, report);
}

static int op_frame(char **tokens, unsigned count, pending_frame *frame,
                    s4_inject_validation_report *report) {
    const unsigned long long width = value_u64(tokens, count, "w", 3u);
    const unsigned long long height = value_u64(tokens, count, "h", 2u);
    const int format = parse_enum(value_str(tokens, count, "fmt", "RGB888"), k_format_names,
                                  (int)S4_FMT_COUNT);
    unsigned long long stride = value_u64(tokens, count, "stride", 0u);
    unsigned long long derived = 0u;
    unsigned long long length;
    const char *region_name = value_str(tokens, count, "region", NULL);
    const char *payload_spec;
    const char *digest_spec;
    s4_inject_status derived_status = S4_INJECT_OK;
    unsigned long long index;

    if (frame->payload != NULL) {
        free(frame->payload);
        frame->payload = NULL;
        frame->payload_length = 0u;
    }
    memset(&frame->desc, 0, sizeof(frame->desc));
    frame->desc.contract_version = value_str(tokens, count, "contract", S4_INJECT_CONTRACT_VERSION);
    frame->desc.source_kind = (s4_inject_source_kind)parse_enum(
        value_str(tokens, count, "source", "file_injection"), k_source_names,
        (int)S4_SRC_KIND_COUNT);
    copy_text(frame->desc.session_id, S4_INJECT_SESSION_ID_MAX,
              value_str(tokens, count, "session", "0123456789abcdef0123456789abcdef"));
    frame->desc.frame_id = (uint32_t)value_u64(tokens, count, "id", 1u);
    frame->desc.width = (uint32_t)width;
    frame->desc.height = (uint32_t)height;
    frame->desc.pixel_format = (s4_inject_pixel_format)format;
    if (stride == 0u && format >= 0 && format < (int)S4_FMT_COUNT) {
        stride = s4_inject_min_stride((s4_inject_pixel_format)format, (uint32_t)width);
    }
    frame->desc.stride_bytes = (uint32_t)stride;
    if (region_name == NULL) {
        region_name = g_region_count > 0u ? g_regions[0].name : "";
    }
    copy_text(frame->desc.region_name, S4_INJECT_REGION_NAME_MAX, region_name);
    frame->desc.base_addr = value_u64(tokens, count, "base", 0u);
    frame->desc.offset_bytes = value_u64(tokens, count, "offset", 0u);
    if (format >= 0 && format < (int)S4_FMT_COUNT) {
        derived = s4_inject_expected_frame_bytes((s4_inject_pixel_format)format, (uint32_t)stride,
                                                 (uint32_t)width, (uint32_t)height,
                                                 &derived_status);
    }
    length = value_u64(tokens, count, "len", derived);
    frame->desc.length_bytes = length;
    frame->desc.alignment = (uint32_t)value_u64(tokens, count, "align", 64u);
    /* 注意：token_present 只匹配孤立 key，无法匹配 "capture=<ns>"；
     * 这里必须用 token_value 判断 key 是否存在，否则 capture=<ns> 永远被忽略，
     * 注入模式“伪造采集时间必须被拒绝”的路径将无法被测验到。 */
    if (token_value(tokens, count, "capture") != NULL &&
        strcmp(value_str(tokens, count, "capture", "unavailable"), "unavailable") != 0) {
        frame->desc.capture_time_state = S4_CAPTURE_PROVIDED;
        frame->desc.capture_time_ns = value_u64(tokens, count, "capture", 0u);
    } else {
        frame->desc.capture_time_state = S4_CAPTURE_UNAVAILABLE;
        frame->desc.capture_time_ns = 0u;
    }
    frame->desc.injection_start_ns = value_u64(tokens, count, "inject_ns", 1000000u);
    copy_text(frame->desc.clock_name, S4_INJECT_CLOCK_NAME_MAX,
              value_str(tokens, count, "clock", "XTime_GlobalTimer"));
    frame->desc.clock_freq_hz = value_u64(tokens, count, "freq", 100000000u);
    frame->desc.wrap_handling = value_str(tokens, count, "wrap", "reject_wrap_explicit_reset");
    frame->desc.epoch_note = value_str(tokens, count, "epoch", "relative_to_ps_boot");
    frame->desc.clock_domain = value_str(tokens, count, "domain", "PS 100MHz global timer");
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
    {
        uint64_t capture_available = value_u64(tokens, count, "capture_avail", 0u);
        frame->desc.unavailable_capture_time = (capture_available == 0u) ? 1u : 0u;
    }

    payload_spec = value_str(tokens, count, "payload", "pattern:1");
    if (strncmp(payload_spec, "file:", 5u) == 0) {
        frame->payload = read_file_bytes(payload_spec + 5u, &frame->payload_length);
    } else if (strncmp(payload_spec, "pattern:", 8u) == 0) {
        const unsigned long long seed = strtoull(payload_spec + 8u, NULL, 0);
        frame->payload_length = value_u64(tokens, count, "payload_len", length);
        frame->payload = pattern_bytes(seed, frame->payload_length);
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
    if (strcmp(value_str(tokens, count, "algorithm", "crc32_ieee"), "sha256") == 0) {
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
        for (index = 0u; index < 64u && digest_spec[index] != '\0' &&
                         digest_spec[index + 1u] != '\0';
             index += 2u) {
            char pair[3];
            pair[0] = digest_spec[index];
            pair[1] = digest_spec[index + 1u];
            pair[2] = '\0';
            frame->desc.integrity_sha256[index / 2u] = (uint8_t)strtoul(pair, NULL, 16);
        }
        frame->desc.integrity_crc32 = (uint32_t)strtoul(digest_spec, NULL, 16);
    }
    frame->valid = 1;
    return S4_INJECT_OK;
}

static int op_bind(char **tokens, unsigned count, pending_frame *frame,
                   s4_inject_validation_report *report) {
    unsigned long long slot = value_u64(tokens, count, "slot", (unsigned long long)-1);
    uint32_t target = 0u;
    s4_inject_status status;
    if (!frame->valid) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "frame";
        report->reason = "尚未用 frame op 描述帧";
        return (int)report->status;
    }
    if (slot == (unsigned long long)-1) {
        status = s4_inject_ring_acquire(&g_ring, &target, report);
        if (status != S4_INJECT_OK) {
            return (int)status;
        }
    } else {
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
    g_consumer_busy_ticks += busy;
    if (slot >= g_ring.slot_count) {
        report->status = S4_INJECT_ERR_NULL_ARG;
        report->field = "slot";
        report->reason = "槽位越界";
        return (int)report->status;
    }
    status = s4_inject_ring_advance(&g_ring, (uint32_t)slot, S4_EV_CONSUMER_START, report);
    if (status != S4_INJECT_OK) {
        return (int)status;
    }
    status = s4_inject_ring_consumer_read(&g_ring, (uint32_t)slot, g_mock.ddr, MOCK_LEN, MOCK_BASE,
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
    return (int)s4_inject_ring_timeout(&g_ring, (uint32_t)value_u64(tokens, count, "slot", 0u),
                                       report);
}

static int op_abort(char **tokens, unsigned count, s4_inject_validation_report *report) {
    return (int)s4_inject_ring_abort(&g_ring, (uint32_t)value_u64(tokens, count, "slot", 0u),
                                     report);
}

static int op_mock_maintenance(char **tokens, unsigned count, int is_flush) {
    const unsigned long long base = value_u64(tokens, count, "base", 0u);
    const unsigned long long len = value_u64(tokens, count, "len", 0u);
    if (is_flush) {
        mock_flush(base, len);
    } else {
        mock_invalidate(base, len);
    }
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
        } else if (strcmp(tokens[0], "mock_flush") == 0) {
            status = op_mock_maintenance(tokens, count, 1);
        } else if (strcmp(tokens[0], "mock_invalidate") == 0) {
            status = op_mock_maintenance(tokens, count, 0);
        } else if (strcmp(tokens[0], "note") == 0) {
            status = S4_INJECT_OK;
        } else {
            report.status = S4_INJECT_ERR_NULL_ARG;
            report.field = "op";
            report.reason = "未知 op";
            status = (int)report.status;
        }
        if (index > 0u) {
            printf(",\n");
        }
        printf("{\"index\": %u, \"try\": %s, \"op\": \"%s\", \"status\": %d, "
               "\"status_name\": \"%s\", \"field\": %s, \"reason\": \"%s\", \"actual\": %llu}",
               index, is_try ? "true" : "false", joined, status,
               s4_inject_status_name((s4_inject_status)status),
               report.field == NULL ? "null" : "\"见 field 名\"",
               report.reason, report.actual);
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
           "\"invalidate_events\": %llu, \"timeout_events\": %llu, \"dropped_frames\": %llu,\n",
           g_ring.last_released_frame_id, (unsigned long long)g_ring.flush_events,
           (unsigned long long)g_ring.invalidate_events,
           (unsigned long long)g_ring.timeout_events, (unsigned long long)g_ring.dropped_frames);
    printf("    \"last_bind_slot\": %llu,\n", g_bind_slot);
    printf("    \"slots\": [");
    for (index = 0u; index < g_ring.slot_count; ++index) {
        const s4_inject_slot *slot = &g_ring.slots[index];
        printf("%s{\"slot\": %u, \"state\": \"%s\", \"frame_id\": %u, \"events_mask\": %u, "
               "\"integrity_checked\": %u, \"flush_bytes\": %llu, \"invalidate_bytes\": %llu}",
               index == 0u ? "" : ", ", index, s4_inject_slot_state_name(slot->state),
               slot->state == S4_SLOT_FREE ? 0u : slot->desc.frame_id, slot->observed_events,
               slot->integrity_checked, (unsigned long long)slot->flush_rounded_bytes,
               (unsigned long long)slot->invalidate_rounded_bytes);
    }
    printf("]\n  },\n");
}

static void print_mock(void) {
    unsigned index;
    printf("  \"mock_cache\": {\n");
    printf("    \"flush_count\": %lu, \"invalidate_count\": %lu, \"flushed_bytes\": %llu, "
           "\"invalidated_bytes\": %llu, \"dirty_lost_lines\": %llu,\n",
           g_mock.flush_count, g_mock.invalidate_count, (unsigned long long)g_mock.flushed_bytes,
           (unsigned long long)g_mock.invalidated_bytes, (unsigned long long)g_mock.dirty_lost);
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
    g_mock.ddr = (unsigned char *)calloc((size_t)MOCK_LEN, 1u);
    g_mock.dirty = (unsigned char *)calloc((size_t)(MOCK_LEN / S4_INJECT_CACHE_LINE_BYTES), 1u);
    g_mock.valid = (unsigned char *)calloc((size_t)(MOCK_LEN / S4_INJECT_CACHE_LINE_BYTES), 1u);
    if (g_mock.ddr == NULL || g_mock.dirty == NULL || g_mock.valid == NULL) {
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
    free(g_mock.ddr);
    free(g_mock.dirty);
    free(g_mock.valid);
    return status;
}