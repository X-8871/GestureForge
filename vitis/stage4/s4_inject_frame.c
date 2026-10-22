/* 阶段4 单帧注入通路实现：契约校验 + 8 事件状态机 + 完整性 + 缓存维护方向。
 *
 * 设计要点：
 *  - 不内嵌任何绝对地址：区域表由调用方从地址图 JSON 读入；
 *  - 任何非法参数/顺序/完整性/覆盖行为都返回唯一非零错误码，并填充可定位的 report；
 *  - flush/invalidate 的范围按 64 B 向外取整，必须落在所属 region 内；
 *  - 注入模式（file_injection/synthetic）下 capture_time_ns 不可用，伪造即拒绝；
 *  - 本实现不做任何硬件访问。
 */

#include "s4_inject_frame.h"

#include <string.h>

/* ------------------------------------------------------------------ */
/* 名称表                                                              */
/* ------------------------------------------------------------------ */

static const char *const k_status_names[S4_INJECT_ERR_STATUS_COUNT] = {
    "OK",
    "ERR_NULL_ARG",
    "ERR_CONTRACT_VERSION",
    "ERR_SOURCE_KIND",
    "ERR_PIXEL_FORMAT",
    "ERR_GEOMETRY",
    "ERR_STRIDE",
    "ERR_LENGTH",
    "ERR_REGION_UNKNOWN",
    "ERR_BUFFER_RANGE",
    "ERR_ALIGNMENT",
    "ERR_BUFFER_OVERLAP",
    "ERR_NO_FREE_BUFFER",
    "ERR_NO_OVERWRITE",
    "ERR_DUPLICATE_FRAME",
    "ERR_OUT_OF_ORDER",
    "ERR_EVENT_ORDER",
    "ERR_INTEGRITY",
    "ERR_CONSUMER_TIMEOUT",
    "ERR_CAPTURE_TIME_FORGED",
    "ERR_MEASUREMENT_SCOPE",
    "ERR_DROPPED_FRAME",
    "ERR_FLUSH_COVERAGE",
    "ERR_SESSION",
    "ERR_CACHE_BARRIER",
    "ERR_CACHE_VISIBILITY",
    "ERR_CLI_ARGUMENT",
};

static const char *const k_event_names[S4_EV_COUNT] = {
    "producer_write_start",
    "producer_write_complete",
    "cache_flush_by_producer",
    "ownership_publish_to_consumer",
    "consumer_invalidate",
    "consumer_start",
    "consumer_done",
    "buffer_release_to_producer",
};

static const char *const k_state_names[S4_SLOT_STATE_COUNT] = {
    "FREE", "LOADING", "LOADED", "FLUSHED", "PUBLISHED",
    "CONSUMING", "CONSUMED", "INVALIDATED", "FAILED",
};

static const char *const k_source_names[S4_SRC_KIND_COUNT] = {
    "file_injection", "camera", "synthetic",
};

static const char *const k_format_names[S4_FMT_COUNT] = {
    "RGB888", "RGB565", "GRAY8", "INT8_CHW_416",
};

static const char *const k_integrity_names[S4_INTEGRITY_COUNT] = {
    "crc32_ieee", "sha256",
};

static const char *const k_scope_names[S4_SCOPE_COUNT] = {
    "MEASURED", "NOT_EXECUTED_OFFLINE",
};

const char *s4_inject_status_name(s4_inject_status status) {
    if ((int)status < 0 || status >= S4_INJECT_ERR_STATUS_COUNT) {
        return "UNKNOWN_STATUS";
    }
    return k_status_names[status];
}

const char *s4_inject_event_name(s4_inject_event event) {
    if ((int)event < 0 || event >= S4_EV_COUNT) {
        return "UNKNOWN_EVENT";
    }
    return k_event_names[event];
}

const char *s4_inject_slot_state_name(s4_inject_slot_state state) {
    if ((int)state < 0 || state >= S4_SLOT_STATE_COUNT) {
        return "UNKNOWN_STATE";
    }
    return k_state_names[state];
}

const char *s4_inject_source_kind_name(s4_inject_source_kind kind) {
    if ((int)kind < 0 || kind >= S4_SRC_KIND_COUNT) {
        return "UNKNOWN_SOURCE_KIND";
    }
    return k_source_names[kind];
}

const char *s4_inject_pixel_format_name(s4_inject_pixel_format format) {
    if ((int)format < 0 || format >= S4_FMT_COUNT) {
        return "UNKNOWN_PIXEL_FORMAT";
    }
    return k_format_names[format];
}

const char *s4_inject_integrity_name(s4_inject_integrity_algorithm algorithm) {
    if ((int)algorithm < 0 || algorithm >= S4_INTEGRITY_COUNT) {
        return "UNKNOWN_INTEGRITY";
    }
    return k_integrity_names[algorithm];
}

const char *s4_inject_scope_name(s4_inject_scope_value value) {
    if ((int)value < 0 || value >= S4_SCOPE_COUNT) {
        return "UNKNOWN_SCOPE";
    }
    return k_scope_names[value];
}

/* ------------------------------------------------------------------ */
/* 基础工具                                                            */
/* ------------------------------------------------------------------ */

uint32_t s4_inject_crc32(const void *data, size_t length) {
    const uint8_t *bytes = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFu;
    size_t index;
    if (bytes == NULL && length != 0u) {
        return 0u;
    }
    for (index = 0u; index < length; ++index) {
        uint32_t bit;
        crc ^= (uint32_t)bytes[index];
        for (bit = 0u; bit < 8u; ++bit) {
            crc = (crc & 1u) != 0u ? (crc >> 1) ^ 0xEDB88320u : (crc >> 1);
        }
    }
    return crc ^ 0xFFFFFFFFu;
}

/* SHA-256（FIPS 180-4）自包含实现，避免主机/目标侧依赖。 */
typedef struct {
    uint32_t state[8];
    uint64_t bit_length;
    uint8_t buffer[64];
    size_t buffer_length;
} s4_sha256_ctx;

static const uint32_t k_sha256_k[64] = {
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu, 0x59f111f1u,
    0x923f82a4u, 0xab1c5ed5u, 0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
    0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u, 0xe49b69c1u, 0xefbe4786u,
    0x0fc19dc6u, 0x240ca1ccu, 0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
    0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u,
    0x06ca6351u, 0x14292967u, 0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
    0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u, 0xa2bfe8a1u, 0xa81a664bu,
    0xc24b8b70u, 0xc76c51a3u, 0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
    0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au,
    0x5b9cca4fu, 0x682e6ff3u, 0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
    0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u,
};

static uint32_t rotr32(uint32_t value, uint32_t shift) {
    return (value >> shift) | (value << (32u - shift));
}

static void sha256_transform(s4_sha256_ctx *ctx, const uint8_t block[64]) {
    uint32_t w[64];
    uint32_t a, b, c, d, e, f, g, h;
    uint32_t index;
    for (index = 0u; index < 16u; ++index) {
        w[index] = ((uint32_t)block[index * 4u] << 24) |
                   ((uint32_t)block[index * 4u + 1u] << 16) |
                   ((uint32_t)block[index * 4u + 2u] << 8) |
                   (uint32_t)block[index * 4u + 3u];
    }
    for (index = 16u; index < 64u; ++index) {
        const uint32_t s0 = rotr32(w[index - 15u], 7u) ^ rotr32(w[index - 15u], 18u) ^
                            (w[index - 15u] >> 3);
        const uint32_t s1 = rotr32(w[index - 2u], 17u) ^ rotr32(w[index - 2u], 19u) ^
                            (w[index - 2u] >> 10);
        w[index] = w[index - 16u] + s0 + w[index - 7u] + s1;
    }
    a = ctx->state[0];
    b = ctx->state[1];
    c = ctx->state[2];
    d = ctx->state[3];
    e = ctx->state[4];
    f = ctx->state[5];
    g = ctx->state[6];
    h = ctx->state[7];
    for (index = 0u; index < 64u; ++index) {
        const uint32_t s1 = rotr32(e, 6u) ^ rotr32(e, 11u) ^ rotr32(e, 25u);
        const uint32_t ch = (e & f) ^ ((~e) & g);
        const uint32_t temp1 = h + s1 + ch + k_sha256_k[index] + w[index];
        const uint32_t s0 = rotr32(a, 2u) ^ rotr32(a, 13u) ^ rotr32(a, 22u);
        const uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        const uint32_t temp2 = s0 + maj;
        h = g;
        g = f;
        f = e;
        e = d + temp1;
        d = c;
        c = b;
        b = a;
        a = temp1 + temp2;
    }
    ctx->state[0] += a;
    ctx->state[1] += b;
    ctx->state[2] += c;
    ctx->state[3] += d;
    ctx->state[4] += e;
    ctx->state[5] += f;
    ctx->state[6] += g;
    ctx->state[7] += h;
}

void s4_inject_sha256(const void *data, size_t length, uint8_t out[32]) {
    s4_sha256_ctx ctx;
    const uint8_t *bytes = (const uint8_t *)data;
    size_t index;
    uint64_t bit_length;
    uint8_t tail[72];
    size_t tail_length;
    static const uint32_t init_state[8] = {
        0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
        0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u,
    };
    if (out == NULL) {
        return;
    }
    for (index = 0u; index < 8u; ++index) {
        ctx.state[index] = init_state[index];
    }
    ctx.bit_length = 0u;
    ctx.buffer_length = 0u;
    if (bytes != NULL && length != 0u) {
        size_t offset = 0u;
        while (offset < length) {
            const size_t chunk = (length - offset) < 64u ? (length - offset) : 64u;
            memcpy(ctx.buffer + ctx.buffer_length, bytes + offset, chunk);
            ctx.buffer_length += chunk;
            offset += chunk;
            if (ctx.buffer_length == 64u) {
                sha256_transform(&ctx, ctx.buffer);
                ctx.buffer_length = 0u;
            }
        }
    }
    bit_length = (uint64_t)length * 8u;
    tail_length = 0u;
    memcpy(tail, ctx.buffer, ctx.buffer_length);
    tail_length = ctx.buffer_length;
    tail[tail_length++] = 0x80u;
    if (tail_length > 56u) {
        while (tail_length < 64u) {
            tail[tail_length++] = 0u;
        }
        sha256_transform(&ctx, tail);
        tail_length = 0u;
    }
    while (tail_length < 56u) {
        tail[tail_length++] = 0u;
    }
    for (index = 0u; index < 8u; ++index) {
        tail[56u + index] = (uint8_t)((bit_length >> (56u - index * 8u)) & 0xFFu);
    }
    sha256_transform(&ctx, tail);
    for (index = 0u; index < 8u; ++index) {
        out[index * 4u] = (uint8_t)((ctx.state[index] >> 24) & 0xFFu);
        out[index * 4u + 1u] = (uint8_t)((ctx.state[index] >> 16) & 0xFFu);
        out[index * 4u + 2u] = (uint8_t)((ctx.state[index] >> 8) & 0xFFu);
        out[index * 4u + 3u] = (uint8_t)(ctx.state[index] & 0xFFu);
    }
}

uint32_t s4_inject_planes(s4_inject_pixel_format format) {
    return format == S4_FMT_INT8_CHW_416 ? 3u : 1u;
}

uint32_t s4_inject_min_stride(s4_inject_pixel_format format, uint32_t width) {
    switch (format) {
        case S4_FMT_RGB888:
            if (width > UINT32_MAX / 3u) {
                return 0u;
            }
            return width * 3u;
        case S4_FMT_RGB565:
            if (width > UINT32_MAX / 2u) {
                return 0u;
            }
            return width * 2u;
        case S4_FMT_GRAY8:
        case S4_FMT_INT8_CHW_416:
            return width;
        default:
            return 0u;
    }
}

uint64_t s4_inject_expected_frame_bytes(s4_inject_pixel_format format, uint32_t stride_bytes,
                                        uint32_t width, uint32_t height,
                                        s4_inject_status *status) {
    uint32_t minimum;
    uint64_t rows;
    uint64_t planes;
    if (status != NULL) {
        *status = S4_INJECT_OK;
    }
    if ((int)format < 0 || format >= S4_FMT_COUNT) {
        if (status != NULL) {
            *status = S4_INJECT_ERR_PIXEL_FORMAT;
        }
        return 0u;
    }
    if (width == 0u || height == 0u) {
        if (status != NULL) {
            *status = S4_INJECT_ERR_GEOMETRY;
        }
        return 0u;
    }
    if (format == S4_FMT_INT8_CHW_416 && (width != 416u || height != 416u)) {
        if (status != NULL) {
            *status = S4_INJECT_ERR_GEOMETRY;
        }
        return 0u;
    }
    minimum = s4_inject_min_stride(format, width);
    if (minimum == 0u) {
        if (status != NULL) {
            *status = S4_INJECT_ERR_STRIDE;
        }
        return 0u;
    }
    if (stride_bytes == 0u || stride_bytes < minimum) {
        if (status != NULL) {
            *status = S4_INJECT_ERR_STRIDE;
        }
        return 0u;
    }
    rows = (uint64_t)stride_bytes * (uint64_t)height;
    planes = (uint64_t)s4_inject_planes(format);
    if (planes != 0u && rows > UINT64_MAX / planes) {
        if (status != NULL) {
            *status = S4_INJECT_ERR_LENGTH;
        }
        return 0u;
    }
    return rows * planes;
}

int s4_inject_intervals_overlap(uint64_t a0, uint64_t a1, uint64_t b0, uint64_t b1) {
    const uint64_t start = a0 > b0 ? a0 : b0;
    const uint64_t end = a1 < b1 ? a1 : b1;
    return start < end;
}

uint64_t s4_inject_round_down(uint64_t value, uint64_t alignment) {
    if (alignment == 0u) {
        return value;
    }
    return value - (value % alignment);
}

uint64_t s4_inject_round_up(uint64_t value, uint64_t alignment) {
    uint64_t remainder;
    if (alignment == 0u) {
        return value;
    }
    remainder = value % alignment;
    if (remainder == 0u) {
        return value;
    }
    if (value > UINT64_MAX - (alignment - remainder)) {
        return UINT64_MAX;
    }
    return value + (alignment - remainder);
}

/* ------------------------------------------------------------------ */
/* 校验                                                                */
/* ------------------------------------------------------------------ */

static s4_inject_status fail(s4_inject_validation_report *report, s4_inject_status status,
                             const char *field, const char *reason, uint64_t expected,
                             uint64_t actual) {
    if (report != NULL) {
        report->status = status;
        report->field = field;
        report->reason = reason;
        report->expected = expected;
        report->actual = actual;
    }
    return status;
}

static int text_non_empty(const char *value) {
    return value != NULL && value[0] != '\0';
}

static s4_inject_status fail(s4_inject_validation_report *report, s4_inject_status status,
                             const char *field, const char *reason, uint64_t expected,
                             uint64_t actual);

static s4_inject_status validate_source_mapping(const s4_inject_frame_desc *desc,
                                                s4_inject_validation_report *report) {
    s4_measurement_scope_source_kind expected;
    if (desc->source_kind == S4_SRC_FILE_INJECTION) {
        expected = S4_MEAS_SCOPE_BOARD_INJECTION;
    } else if (desc->source_kind == S4_SRC_CAMERA) {
        expected = S4_MEAS_SCOPE_CAMERA;
    } else {
        expected = S4_MEAS_SCOPE_OFFLINE_REGRESSION;
    }
    if ((int)desc->measurement_scope_source_kind < 0 ||
        desc->measurement_scope_source_kind >= S4_MEAS_SCOPE_SOURCE_COUNT ||
        desc->measurement_scope_source_kind != expected) {
        return fail(report, S4_INJECT_ERR_MEASUREMENT_SCOPE, "measurement_scope.source_kind",
                    "顶层 source_kind 与 measurement_scope.source_kind 映射不一致",
                    (uint64_t)expected, (uint64_t)desc->measurement_scope_source_kind);
    }
    return S4_INJECT_OK;
}

static const s4_inject_region *find_region(const s4_inject_region *regions, uint32_t count,
                                           const char *name) {
    uint32_t index;
    if (name == NULL) {
        return NULL;
    }
    for (index = 0u; index < count; ++index) {
        if (regions[index].name != NULL && strcmp(regions[index].name, name) == 0) {
            return &regions[index];
        }
    }
    return NULL;
}

s4_inject_status s4_inject_validate(const s4_inject_frame_desc *desc,
                                    const s4_inject_region *regions, uint32_t region_count,
                                    const uint8_t *payload, uint64_t payload_length,
                                    s4_inject_validation_report *report) {
    const s4_inject_region *region;
    uint64_t addr_start;
    uint64_t addr_end;
    uint64_t expected;
    s4_inject_status derived = S4_INJECT_OK;

    if (report != NULL) {
        report->status = S4_INJECT_OK;
        report->field = NULL;
        report->reason = "OK";
        report->expected = 0u;
        report->actual = 0u;
    }
    if (desc == NULL) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, NULL, "帧描述为空", 0u, 0u);
    }
    if (regions == NULL || region_count == 0u || region_count > S4_INJECT_MAX_REGIONS) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, "regions", "区域表为空或超出上限", 0u,
                    region_count);
    }
    if (desc->contract_version == NULL ||
        strcmp(desc->contract_version, S4_INJECT_CONTRACT_VERSION) != 0) {
        return fail(report, S4_INJECT_ERR_CONTRACT_VERSION, "contract_version",
                    "contract_version 与契约不一致", 0u, 0u);
    }
    if ((int)desc->source_kind < 0 || desc->source_kind >= S4_SRC_KIND_COUNT) {
        return fail(report, S4_INJECT_ERR_SOURCE_KIND, "source_kind",
                    "source_kind 不在契约枚举内", 0u, (uint64_t)desc->source_kind);
    }
    if (desc->frame_id == UINT32_MAX) {
        return fail(report, S4_INJECT_ERR_OUT_OF_ORDER, "frame_id",
                    "frame_id=0xFFFFFFFF 为保留回绕值；必须开启新会话前停止分配",
                    UINT32_MAX - 1u, desc->frame_id);
    }
    if ((int)desc->pixel_format < 0 || desc->pixel_format >= S4_FMT_COUNT) {
        return fail(report, S4_INJECT_ERR_PIXEL_FORMAT, "pixel_format",
                    "pixel_format 不在契约枚举内", 0u, (uint64_t)desc->pixel_format);
    }
    if (desc->width == 0u || desc->height == 0u) {
        return fail(report, S4_INJECT_ERR_GEOMETRY, "width/height",
                    "geometry 宽高必须大于 0", 1u, 0u);
    }
    if (desc->stride_bytes == 0u ||
        s4_inject_min_stride(desc->pixel_format, desc->width) == 0u ||
        desc->stride_bytes < s4_inject_min_stride(desc->pixel_format, desc->width)) {
        return fail(report, S4_INJECT_ERR_STRIDE, "stride_bytes",
                    "stride_bytes 小于该格式每行有效字节数",
                    (uint64_t)s4_inject_min_stride(desc->pixel_format, desc->width),
                    (uint64_t)desc->stride_bytes);
    }
    expected = s4_inject_expected_frame_bytes(desc->pixel_format, desc->stride_bytes, desc->width,
                                              desc->height, &derived);
    if (derived != S4_INJECT_OK) {
        return fail(report, derived, "length_bytes", "按格式推导的帧长度失败", 0u, 0u);
    }
    if (desc->length_bytes != expected) {
        return fail(report, S4_INJECT_ERR_LENGTH, "buffer.length_bytes",
                    "length_bytes 不等于 stride*height*planes", expected, desc->length_bytes);
    }
    region = find_region(regions, region_count, desc->region_name);
    if (region == NULL) {
        return fail(report, S4_INJECT_ERR_REGION_UNKNOWN, "buffer.region_name",
                    "region_name 不在地址图内", 0u, 0u);
    }
    if (desc->base_addr != region->base_addr) {
        return fail(report, S4_INJECT_ERR_BUFFER_RANGE, "buffer.base_addr",
                    "base_addr 与地址图该 region 不一致", region->base_addr, desc->base_addr);
    }
    addr_start = region->base_addr + desc->offset_bytes;
    if (addr_start < region->base_addr) {
        return fail(report, S4_INJECT_ERR_BUFFER_RANGE, "buffer.offset_bytes",
                    "offset 溢出", 0u, desc->offset_bytes);
    }
    addr_end = addr_start + desc->length_bytes;
    if (region->length_bytes > UINT64_MAX - region->base_addr || addr_end < addr_start ||
        addr_end > region->base_addr + region->length_bytes) {
        return fail(report, S4_INJECT_ERR_BUFFER_RANGE, "buffer",
                    "帧区间超出所属 region", region->base_addr + region->length_bytes, addr_end);
    }
    if (desc->alignment < S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES ||
        (desc->alignment & (desc->alignment - 1u)) != 0u) {
        return fail(report, S4_INJECT_ERR_ALIGNMENT, "buffer.alignment",
                    "alignment 必须为 >=64 的 2 的幂", S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES,
                    desc->alignment);
    }
    if ((addr_start % (uint64_t)desc->alignment) != 0u) {
        return fail(report, S4_INJECT_ERR_ALIGNMENT, "buffer.offset_bytes",
                    "帧起始地址未按 alignment 对齐", 0u, addr_start % desc->alignment);
    }
    if ((int)desc->integrity_algorithm < 0 ||
        desc->integrity_algorithm >= S4_INTEGRITY_COUNT) {
        return fail(report, S4_INJECT_ERR_INTEGRITY, "frame_integrity.algorithm",
                    "frame_integrity.algorithm 不在契约枚举内", 0u,
                    (uint64_t)desc->integrity_algorithm);
    }
    if (!text_non_empty(desc->clock_name) || desc->clock_freq_hz == 0u) {
        return fail(report, S4_INJECT_ERR_MEASUREMENT_SCOPE, "timestamp_source",
                    "timestamp_source 必须含非空 clock 与 freq_hz>0", 1u, desc->clock_freq_hz);
    }
    if (!text_non_empty(desc->wrap_handling) || desc->epoch_note == NULL) {
        return fail(report, S4_INJECT_ERR_MEASUREMENT_SCOPE, "timestamp_source",
                    "timestamp_source 必须声明 wrap_handling 与 epoch_note", 1u, 0u);
    }
    if (!text_non_empty(desc->clock_domain)) {
        return fail(report, S4_INJECT_ERR_MEASUREMENT_SCOPE, "clock_domain",
                    "clock_domain 必须非空", 1u, 0u);
    }
    if ((int)desc->scope_pl_timing < 0 || desc->scope_pl_timing >= S4_SCOPE_COUNT ||
        (int)desc->scope_uart_transport < 0 || desc->scope_uart_transport >= S4_SCOPE_COUNT ||
        (int)desc->scope_board_pl < 0 || desc->scope_board_pl >= S4_SCOPE_COUNT) {
        return fail(report, S4_INJECT_ERR_MEASUREMENT_SCOPE, "measurement_scope",
                    "measurement_scope 取值不在契约枚举内", 0u, 0u);
    }
    if (validate_source_mapping(desc, report) != S4_INJECT_OK) {
        return report != NULL ? report->status : S4_INJECT_ERR_MEASUREMENT_SCOPE;
    }
    if (desc->source_kind == S4_SRC_FILE_INJECTION) {
        if (desc->capture_time_state != S4_CAPTURE_UNAVAILABLE || desc->capture_time_ns != 0u) {
            return fail(report, S4_INJECT_ERR_CAPTURE_TIME_FORGED, "capture_time_ns",
                        "注入模式 capture_time_available=false，capture_time_ns 必须为 0 哨兵",
                        0u, desc->capture_time_ns);
        }
        if (desc->unavailable_capture_time != 1u) {
            return fail(report, S4_INJECT_ERR_MEASUREMENT_SCOPE,
                        "measurement_scope.unavailable_fields",
                        "注入下 capture_time_ns 必须列入 unavailable_fields", 1u,
                        desc->unavailable_capture_time);
        }
        if (desc->injection_start_ns == 0u) {
            return fail(report, S4_INJECT_ERR_MEASUREMENT_SCOPE, "injection_start_ns",
                        "注入模式必须记录非零 injection_start_ns", 1u, 0u);
        }
    } else if (desc->source_kind == S4_SRC_CAMERA) {
        if (desc->capture_time_state != S4_CAPTURE_PROVIDED || desc->capture_time_ns == 0u ||
            desc->unavailable_capture_time != 0u) {
            return fail(report, S4_INJECT_ERR_MEASUREMENT_SCOPE, "capture_time_ns",
                        "camera 模式要求可用且非零采集时间，unavailable_fields 不得包含该字段",
                        1u, desc->capture_time_ns);
        }
    } else {
        if (desc->capture_time_state != S4_CAPTURE_UNAVAILABLE ||
            desc->capture_time_ns != 0u || desc->unavailable_capture_time != 1u) {
            return fail(report, S4_INJECT_ERR_CAPTURE_TIME_FORGED, "capture_time_ns",
                        "synthetic 模式 capture_time_available=false，capture_time_ns 必须为 0 哨兵并列入 unavailable_fields",
                        0u, desc->capture_time_ns);
        }
    }
    if (payload == NULL) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, "payload",
                    "非零帧长必须提供可读 payload，禁止跳过 CRC/SHA 校验", desc->length_bytes,
                    payload_length);
    }
    if (sizeof(size_t) < sizeof(uint64_t) && payload_length > (uint64_t)SIZE_MAX) {
        return fail(report, S4_INJECT_ERR_LENGTH, "payload_length",
                    "payload_length 超出 size_t 可表示范围", (uint64_t)SIZE_MAX,
                    payload_length);
    }
    if (payload_length != desc->length_bytes) {
        return fail(report, S4_INJECT_ERR_LENGTH, "frame_integrity.length_bytes",
                    "实际写入字节数与 length_bytes 不一致", desc->length_bytes,
                    payload_length);
    }
    if (desc->integrity_algorithm == S4_INTEGRITY_CRC32_IEEE) {
        const uint32_t actual = s4_inject_crc32(payload, (size_t)payload_length);
        if (actual != desc->integrity_crc32) {
            return fail(report, S4_INJECT_ERR_INTEGRITY, "frame_integrity.value",
                        "CRC32 与声明不一致", desc->integrity_crc32, actual);
        }
    } else {
        uint8_t digest[32];
        s4_inject_sha256(payload, (size_t)payload_length, digest);
        if (memcmp(digest, desc->integrity_sha256, sizeof(digest)) != 0) {
            return fail(report, S4_INJECT_ERR_INTEGRITY, "frame_integrity.value",
                        "SHA-256 与声明不一致", 0u, 0u);
        }
    }
    return S4_INJECT_OK;
}

/* ------------------------------------------------------------------ */
/* 事件状态机                                                          */
/* ------------------------------------------------------------------ */

s4_inject_event s4_inject_expected_event(s4_inject_slot_state state) {
    switch (state) {
        case S4_SLOT_LOADING:
            return S4_EV_WRITE_COMPLETE;
        case S4_SLOT_LOADED:
            return S4_EV_FLUSH;
        case S4_SLOT_FLUSHED:
            return S4_EV_PUBLISH;
        case S4_SLOT_PUBLISHED:
            return S4_EV_INVALIDATE;
        case S4_SLOT_INVALIDATED:
            return S4_EV_CONSUMER_START;
        case S4_SLOT_CONSUMING:
            return S4_EV_CONSUMER_DONE;
        case S4_SLOT_CONSUMED:
            return S4_EV_RELEASE;
        default:
            return S4_EV_COUNT;
    }
}

s4_inject_status s4_inject_ring_init(s4_inject_ring *ring, uint32_t slot_count,
                                     uint32_t session_id,
                                     const s4_inject_region *regions, uint32_t region_count,
                                     const s4_inject_cache_ops *cache, void *cache_ctx,
                                     s4_inject_validation_report *report) {
    s4_inject_region staged_regions[S4_INJECT_MAX_REGIONS];
    char staged_region_names[S4_INJECT_MAX_REGIONS][S4_INJECT_REGION_NAME_MAX];
    s4_inject_cache_ops staged_cache;
    uint32_t index;
    uint32_t previous_session_id = 0u;
    uint32_t has_previous_session_id = 0u;
    if (ring == NULL) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, NULL, "ring 为空", 0u, 0u);
    }
    if (ring->initialized_magic == S4_INJECT_RING_INITIALIZED_MAGIC) {
        const uint32_t held_count = s4_inject_ring_held_count(ring);
        if (held_count != 0u) {
            return fail(report, S4_INJECT_ERR_EVENT_ORDER, "ring.reset",
                        "在途或 FAILED 槽仍持有帧，不能通过重初始化释放；须先完成或确认停止并 abort",
                        0u, held_count);
        }
    }
    if (slot_count == 0u || slot_count > S4_INJECT_MAX_SLOTS) {
        return fail(report, S4_INJECT_ERR_NO_FREE_BUFFER, "slot_count", "槽位数超出上限",
                    S4_INJECT_MAX_SLOTS, slot_count);
    }
    if (regions == NULL || region_count == 0u || region_count > S4_INJECT_MAX_REGIONS) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, "regions", "区域表为空或超出上限", 0u,
                    region_count);
    }
    if (cache == NULL || cache->flush == NULL || cache->invalidate == NULL ||
        cache->barrier == NULL) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, "cache_ops",
                    "必须提供 flush、invalidate 与 barrier 回调", 1u, 0u);
    }
    staged_cache = *cache;
    for (index = 0u; index < region_count; ++index) {
        size_t name_length;
        size_t name_index;
        if (regions[index].name == NULL) {
            return fail(report, S4_INJECT_ERR_NULL_ARG, "regions.name",
                        "region 名称为空", 1u, 0u);
        }
        name_length = strlen(regions[index].name);
        if (name_length == 0u || name_length >= S4_INJECT_REGION_NAME_MAX) {
            return fail(report, S4_INJECT_ERR_REGION_UNKNOWN, "regions.name",
                        "region 名称为空或超出固定缓冲区", S4_INJECT_REGION_NAME_MAX - 1u,
                        name_length);
        }
        for (name_index = 0u; name_index <= name_length; ++name_index) {
            staged_region_names[index][name_index] = regions[index].name[name_index];
        }
        staged_regions[index] = regions[index];
        staged_regions[index].name = staged_region_names[index];
    }
    if (ring->initialized_magic == S4_INJECT_RING_INITIALIZED_MAGIC) {
        if (session_id == ring->session_id ||
            (ring->has_previous_session_id != 0u && session_id == ring->previous_session_id)) {
            return fail(report, S4_INJECT_ERR_SESSION, "session_id",
                        "ring 重置必须使用新 u32 session_id；PS 分配器须保证会话标识不复用",
                        ring->session_id, session_id);
        }
        previous_session_id = ring->session_id;
        has_previous_session_id = 1u;
    }
    memset(ring, 0, sizeof(*ring));
    ring->slot_count = slot_count;
    ring->initialized_magic = S4_INJECT_RING_INITIALIZED_MAGIC;
    ring->session_id = session_id;
    ring->session_initialized = 1u;
    ring->previous_session_id = previous_session_id;
    ring->has_previous_session_id = has_previous_session_id;
    ring->region_count = region_count;
    for (index = 0u; index < region_count; ++index) {
        size_t name_length = strlen(staged_regions[index].name);
        size_t name_index;
        for (name_index = 0u; name_index <= name_length; ++name_index) {
            ring->region_name_storage[index][name_index] = staged_regions[index].name[name_index];
        }
        ring->regions[index] = staged_regions[index];
        ring->regions[index].name = ring->region_name_storage[index];
    }
    ring->cache_ops = staged_cache;
    ring->cache_configured = 1u;
    ring->cache_ctx = cache_ctx;
    for (index = 0u; index < slot_count; ++index) {
        ring->slots[index].state = S4_SLOT_FREE;
    }
    return S4_INJECT_OK;
}

uint32_t s4_inject_ring_held_count(const s4_inject_ring *ring) {
    uint32_t index;
    uint32_t held = 0u;
    if (ring == NULL) {
        return 0u;
    }
    for (index = 0u; index < ring->slot_count; ++index) {
        const s4_inject_slot_state state = ring->slots[index].state;
        if (state != S4_SLOT_FREE) {
            held += 1u;
        }
    }
    return held;
}

s4_inject_status s4_inject_ring_acquire(s4_inject_ring *ring, uint32_t *out_slot,
                                       s4_inject_validation_report *report) {
    uint32_t index;
    if (ring == NULL || out_slot == NULL) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, NULL, "ring/out_slot 为空", 0u, 0u);
    }
    for (index = 0u; index < ring->slot_count; ++index) {
        if (ring->slots[index].state == S4_SLOT_FREE) {
            *out_slot = index;
            return S4_INJECT_OK;
        }
    }
    return fail(report, S4_INJECT_ERR_NO_FREE_BUFFER, "slots",
                "队列满：所有槽位仍被持有，生产者不得覆盖", 0u, ring->slot_count);
}

static s4_inject_status validate_ring_sequence(const s4_inject_ring *ring,
                                               const s4_inject_frame_desc *desc,
                                               s4_inject_validation_report *report) {
    uint32_t index;
    if (ring->session_initialized != 0u && ring->session_id != desc->session_id) {
        return fail(report, S4_INJECT_ERR_SESSION, "session_id",
                    "同一 ring 会话内 session_id 不得变化；重启/复位需用新 u32 session_id 重新初始化",
                    ring->session_id, desc->session_id);
    }
    if (desc->frame_id == UINT32_MAX) {
        return fail(report, S4_INJECT_ERR_OUT_OF_ORDER, "frame_id",
                    "frame_id=0xFFFFFFFF 为保留回绕值，须以新 session_id 重开会话",
                    UINT32_MAX - 1u, desc->frame_id);
    }
    for (index = 0u; index < ring->slot_count; ++index) {
        const s4_inject_slot *other = &ring->slots[index];
        if (other->state != S4_SLOT_FREE && other->desc.frame_id == desc->frame_id) {
            return fail(report, S4_INJECT_ERR_DUPLICATE_FRAME, "frame_id",
                        "同一 session_id 内 frame_id 已接纳且仍占有槽位",
                        0u, desc->frame_id);
        }
    }
    if (ring->has_accepted_frame != 0u && desc->frame_id <= ring->last_accepted_frame_id) {
        const s4_inject_status status = desc->frame_id == ring->last_accepted_frame_id
                                            ? S4_INJECT_ERR_DUPLICATE_FRAME
                                            : S4_INJECT_ERR_OUT_OF_ORDER;
        return fail(report, status, "frame_id",
                    "frame_id 必须在同一会话内严格递增；回绕前必须重新分配 session_id",
                    ring->last_accepted_frame_id, desc->frame_id);
    }
    return S4_INJECT_OK;
}

static s4_inject_status validate_no_frame_overlap(const s4_inject_ring *ring, uint32_t slot,
                                                  uint64_t start, uint64_t end,
                                                  s4_inject_validation_report *report) {
    uint32_t index;
    for (index = 0u; index < ring->slot_count; ++index) {
        const s4_inject_slot *other = &ring->slots[index];
        if (index != slot && other->state != S4_SLOT_FREE &&
            s4_inject_intervals_overlap(start, end, other->addr_start, other->addr_end)) {
            return fail(report, S4_INJECT_ERR_BUFFER_OVERLAP, "buffer",
                        "写入前拒绝与在途或 FAILED 槽位相交的帧区间",
                        other->addr_start, start);
        }
    }
    return S4_INJECT_OK;
}

s4_inject_status s4_inject_ring_bind(s4_inject_ring *ring, uint32_t slot,
                                     const s4_inject_frame_desc *desc,
                                     const uint8_t *payload, uint64_t payload_length,
                                     s4_inject_validation_report *report) {
    s4_inject_status status;
    const uint64_t now_events = 1u << (unsigned)S4_EV_WRITE_START;
    uint64_t addr_start;
    uint64_t addr_end;
    if (ring == NULL || desc == NULL) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, NULL, "ring/desc 为空", 0u, 0u);
    }
    if (slot >= ring->slot_count) {
        return fail(report, S4_INJECT_ERR_NO_FREE_BUFFER, "slot", "槽位下标越界", ring->slot_count,
                    slot);
    }
    if (ring->slots[slot].state != S4_SLOT_FREE) {
        return fail(report, S4_INJECT_ERR_NO_OVERWRITE, "slot",
                    "目标槽位仍被持有，禁止覆盖", S4_SLOT_FREE,
                    (uint64_t)ring->slots[slot].state);
    }
    status = s4_inject_validate(desc, ring->regions, ring->region_count, payload, payload_length,
                                report);
    if (status != S4_INJECT_OK) {
        return status;
    }
    status = validate_ring_sequence(ring, desc, report);
    if (status != S4_INJECT_OK) {
        return status;
    }
    addr_start = desc->base_addr + desc->offset_bytes;
    addr_end = addr_start + desc->length_bytes;
    status = validate_no_frame_overlap(ring, slot, addr_start, addr_end, report);
    if (status != S4_INJECT_OK) {
        return status;
    }
    if (ring->session_initialized != 0u && ring->session_id != desc->session_id) {
        return fail(report, S4_INJECT_ERR_SESSION, "session_id", "ring 会话标识不匹配",
                    ring->session_id, desc->session_id);
    }
    ring->session_id = desc->session_id;
    ring->session_initialized = 1u;
    ring->last_accepted_frame_id = desc->frame_id;
    ring->has_accepted_frame = 1u;
    ring->slots[slot].desc = *desc;
    ring->slots[slot].addr_start = addr_start;
    ring->slots[slot].addr_end = addr_end;
    ring->slots[slot].written_bytes = desc->length_bytes;
    ring->slots[slot].observed_events = (uint32_t)now_events;
    ring->slots[slot].integrity_checked = 1u;
    ring->slots[slot].flush_rounded_bytes = 0u;
    ring->slots[slot].invalidate_rounded_bytes = 0u;
    ring->slots[slot].consumer_started = 0u;
    ring->slots[slot].consumer_stopped_confirmed = 0u;
    ring->slots[slot].state = S4_SLOT_LOADING;
    ring->in_flight += 1u;
    return S4_INJECT_OK;
}

static s4_inject_status rounded_maintenance_range(const s4_inject_ring *ring,
                                                  const s4_inject_slot *slot, uint64_t *out_start,
                                                  uint64_t *out_end,
                                                  s4_inject_validation_report *report) {
    const s4_inject_region *region = find_region(ring->regions, ring->region_count,
                                                 slot->desc.region_name);
    const uint64_t start = s4_inject_round_down(slot->addr_start, S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES);
    const uint64_t end = s4_inject_round_up(slot->addr_end, S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES);
    if (region == NULL) {
        return fail(report, S4_INJECT_ERR_REGION_UNKNOWN, "buffer.region_name",
                    "region_name 不在地址图内", 0u, 0u);
    }
    if (end < slot->addr_end || region->length_bytes > UINT64_MAX - region->base_addr ||
        start < region->base_addr || end > region->base_addr + region->length_bytes) {
        return fail(report, S4_INJECT_ERR_FLUSH_COVERAGE, "cache_maintenance",
                    "对外 64 B 取整后的维护范围超出所属 region",
                    region->base_addr + region->length_bytes, end);
    }
    *out_start = start;
    *out_end = end;
    return S4_INJECT_OK;
}

s4_inject_status s4_inject_ring_advance(s4_inject_ring *ring, uint32_t slot, s4_inject_event event,
                                       s4_inject_validation_report *report) {
    s4_inject_slot *entry;
    s4_inject_event expected;
    if (ring == NULL) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, NULL, "ring 为空", 0u, 0u);
    }
    if (slot >= ring->slot_count || (int)event < 0 || event >= S4_EV_COUNT) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, "slot/event", "槽位或事件越界",
                    ring->slot_count, slot);
    }
    entry = &ring->slots[slot];
    if (entry->state == S4_SLOT_FREE) {
        return fail(report, S4_INJECT_ERR_EVENT_ORDER, "state", "槽位空闲，事件序列未开始",
                    (uint64_t)S4_SLOT_LOADING, (uint64_t)entry->state);
    }
    if (entry->state == S4_SLOT_FAILED) {
        return fail(report, S4_INJECT_ERR_EVENT_ORDER, "state", "槽位已失败，需显式 abort 恢复",
                    (uint64_t)S4_SLOT_LOADING, (uint64_t)entry->state);
    }
    expected = s4_inject_expected_event(entry->state);
    if (event != expected) {
        return fail(report, S4_INJECT_ERR_EVENT_ORDER, "event",
                    "事件顺序与契约 events.order 不一致", (uint64_t)expected, (uint64_t)event);
    }
    switch (event) {
        case S4_EV_WRITE_COMPLETE: {
            if (entry->written_bytes != entry->desc.length_bytes) {
                return fail(report, S4_INJECT_ERR_LENGTH, "written_bytes",
                            "写入字节数与 length_bytes 不一致", entry->desc.length_bytes,
                            entry->written_bytes);
            }
            entry->state = S4_SLOT_LOADED;
            break;
        }
        case S4_EV_FLUSH: {
            uint64_t start = 0u;
            uint64_t end = 0u;
            s4_inject_status status;
            if (ring->cache_configured == 0u || ring->cache_ops.flush == NULL ||
                ring->cache_ops.barrier == NULL) {
                return fail(report, S4_INJECT_ERR_NULL_ARG, "cache_ops",
                            "未提供 flush 适配，禁止跳过缓存维护", 0u, 0u);
            }
            status = rounded_maintenance_range(ring, entry, &start, &end, report);
            if (status != S4_INJECT_OK) {
                return status;
            }
            ring->cache_ops.flush(ring->cache_ctx, start, end - start);
            if (ring->cache_ops.barrier(ring->cache_ctx) == 0) {
                return fail(report, S4_INJECT_ERR_CACHE_BARRIER, "cache.flush_barrier",
                            "producer flush 后 DSB/barrier 失败，禁止发布所有权", 1u, 0u);
            }
            ring->flush_events += 1u;
            entry->flush_rounded_bytes = end - start;
            entry->state = S4_SLOT_FLUSHED;
            break;
        }
        case S4_EV_PUBLISH: {
            entry->state = S4_SLOT_PUBLISHED;
            break;
        }
        case S4_EV_INVALIDATE: {
            uint64_t start = 0u;
            uint64_t end = 0u;
            s4_inject_status status;
            if (ring->cache_configured == 0u || ring->cache_ops.invalidate == NULL ||
                ring->cache_ops.barrier == NULL) {
                return fail(report, S4_INJECT_ERR_NULL_ARG, "cache_ops",
                            "未提供 invalidate 与 barrier 适配", 0u, 0u);
            }
            status = rounded_maintenance_range(ring, entry, &start, &end, report);
            if (status != S4_INJECT_OK) {
                return status;
            }
            ring->cache_ops.invalidate(ring->cache_ctx, start, end - start);
            if (ring->cache_ops.barrier(ring->cache_ctx) == 0) {
                return fail(report, S4_INJECT_ERR_CACHE_BARRIER, "cache.invalidate_barrier",
                            "consumer invalidate 后 DSB/barrier 失败，禁止读取帧", 1u, 0u);
            }
            ring->invalidate_events += 1u;
            entry->invalidate_rounded_bytes = end - start;
            entry->state = S4_SLOT_INVALIDATED;
            break;
        }
        case S4_EV_CONSUMER_START: {
            if (entry->invalidate_rounded_bytes == 0u) {
                return fail(report, S4_INJECT_ERR_CACHE_VISIBILITY, "consumer_invalidate",
                            "消费者 start 前必须完成输入帧 invalidate 与 barrier", 1u, 0u);
            }
            entry->consumer_started = 1u;
            entry->state = S4_SLOT_CONSUMING;
            break;
        }
        case S4_EV_CONSUMER_DONE: {
            if (entry->consumer_started != 1u) {
                return fail(report, S4_INJECT_ERR_EVENT_ORDER, "consumer_done",
                            "消费者未 start 即 done", 1u, 0u);
            }
            entry->state = S4_SLOT_CONSUMED;
            break;
        }
        case S4_EV_RELEASE: {
            if (ring->has_released_frame != 0u &&
                entry->desc.frame_id <= ring->last_released_frame_id) {
                return fail(report, S4_INJECT_ERR_OUT_OF_ORDER, "frame_id",
                            "释放结果必须遵循 S4-A 同一会话内递增 frame_id 顺序",
                            ring->last_released_frame_id, entry->desc.frame_id);
            }
            ring->last_released_frame_id = entry->desc.frame_id;
            ring->has_released_frame = 1u;
            entry->state = S4_SLOT_FREE;
            if (ring->in_flight > 0u) {
                ring->in_flight -= 1u;
            }
            break;
        }
        default:
            return fail(report, S4_INJECT_ERR_EVENT_ORDER, "event", "未知事件", 0u,
                        (uint64_t)event);
    }
    entry->observed_events |= (uint32_t)(1u << (unsigned)event);
    if (report != NULL) {
        report->status = S4_INJECT_OK;
        report->field = NULL;
        report->reason = "OK";
        report->expected = 0u;
        report->actual = 0u;
    }
    return S4_INJECT_OK;
}

s4_inject_status s4_inject_ring_timeout(s4_inject_ring *ring, uint32_t slot,
                                       s4_inject_validation_report *report) {
    s4_inject_slot *entry;
    if (ring == NULL || slot >= ring->slot_count) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, "slot", "槽位越界", ring ? ring->slot_count : 0u,
                    slot);
    }
    entry = &ring->slots[slot];
    if (entry->state != S4_SLOT_PUBLISHED && entry->state != S4_SLOT_INVALIDATED &&
        entry->state != S4_SLOT_CONSUMING) {
        return fail(report, S4_INJECT_ERR_EVENT_ORDER, "state",
                    "仅已发布/消费中的帧可判超时", (uint64_t)S4_SLOT_PUBLISHED,
                    (uint64_t)entry->state);
    }
    entry->state = S4_SLOT_FAILED;
    ring->timeout_events += 1u;
    return fail(report, S4_INJECT_ERR_CONSUMER_TIMEOUT, "consumer_done",
                "消费者未在期限内完成：FAILED 槽仍占有帧，须另取消费者停止确认，不得用超时推断完成", 0u,
                entry->desc.frame_id);
}

s4_inject_status s4_inject_ring_confirm_consumer_stopped(
    s4_inject_ring *ring, uint32_t slot, s4_inject_validation_report *report) {
    if (ring == NULL || slot >= ring->slot_count) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, "slot",
                    "ring 为空或槽位越界", ring == NULL ? 0u : ring->slot_count, slot);
    }
    if (ring->slots[slot].state != S4_SLOT_FAILED) {
        return fail(report, S4_INJECT_ERR_EVENT_ORDER, "state",
                    "仅 FAILED 槽可记录消费者停止/复位确认",
                    (uint64_t)S4_SLOT_FAILED, (uint64_t)ring->slots[slot].state);
    }
    ring->slots[slot].consumer_stopped_confirmed = 1u;
    if (report != NULL) {
        report->status = S4_INJECT_OK;
        report->field = NULL;
        report->reason = "主机 mock 或外部适配器确认消费者已停止或复位";
        report->expected = 0u;
        report->actual = 0u;
    }
    return S4_INJECT_OK;
}

s4_inject_status s4_inject_ring_abort(s4_inject_ring *ring, uint32_t slot,
                                     s4_inject_validation_report *report) {
    if (ring == NULL || slot >= ring->slot_count) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, "slot", "槽位越界", 0u, slot);
    }
    if (ring->slots[slot].state != S4_SLOT_FAILED) {
        return fail(report, S4_INJECT_ERR_EVENT_ORDER, "state", "仅失败槽位可 abort",
                    (uint64_t)S4_SLOT_FAILED, (uint64_t)ring->slots[slot].state);
    }
    if (ring->slots[slot].consumer_stopped_confirmed == 0u) {
        return fail(report, S4_INJECT_ERR_EVENT_ORDER, "consumer_stopped_confirmed",
                    "未收到消费者停止或复位确认，FAILED 槽不得释放", 1u, 0u);
    }
    ring->slots[slot].state = S4_SLOT_FREE;
    if (ring->in_flight > 0u) {
        ring->in_flight -= 1u;
    }
    return S4_INJECT_OK;
}

s4_inject_status s4_inject_ring_drop(s4_inject_ring *ring, const s4_inject_frame_desc *desc,
                                    s4_inject_validation_report *report) {
    uint32_t index;
    if (ring == NULL || desc == NULL) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, NULL, "ring/desc 为空", 0u, 0u);
    }
    for (index = 0u; index < ring->slot_count; ++index) {
        const s4_inject_slot *entry = &ring->slots[index];
        if (entry->state != S4_SLOT_FREE && entry->state != S4_SLOT_FAILED &&
            entry->desc.frame_id == desc->frame_id) {
            return fail(report, S4_INJECT_ERR_DUPLICATE_FRAME, "frame_id",
                        "该 frame_id 已在环内，不能同时记为丢帧", 0u, desc->frame_id);
        }
    }
    {
        const s4_inject_status sequence = validate_ring_sequence(ring, desc, report);
        if (sequence != S4_INJECT_OK) {
            return sequence;
        }
    }
    ring->dropped_frames += 1u;
    ring->session_id = desc->session_id;
    ring->session_initialized = 1u;
    ring->last_accepted_frame_id = desc->frame_id;
    ring->has_accepted_frame = 1u;
    if (report != NULL) {
        report->status = S4_INJECT_OK;
        report->field = NULL;
        report->reason = "OK";
        report->expected = 0u;
        report->actual = 0u;
    }
    return S4_INJECT_OK;
}

s4_inject_status s4_inject_ring_consumer_read(s4_inject_ring *ring, uint32_t slot,
                                             const uint8_t *ddr_bytes, uint64_t ddr_length,
                                             uint64_t ddr_base, uint32_t *out_crc32,
                                             uint64_t *out_valid_bytes,
                                             uint64_t *out_padding_bytes,
                                             s4_inject_validation_report *report) {
    const s4_inject_slot *entry;
    const uint8_t *frame_bytes;
    uint64_t offset;
    uint64_t ddr_end;
    const uint64_t size_max = (uint64_t)SIZE_MAX;
    const uint64_t valid_row = (uint64_t)s4_inject_min_stride(
        ring != NULL && slot < ring->slot_count ? ring->slots[slot].desc.pixel_format
                                               : S4_FMT_RGB888,
        ring != NULL && slot < ring->slot_count ? ring->slots[slot].desc.width : 0u);
    if (ring == NULL || ddr_bytes == NULL || slot >= ring->slot_count) {
        return fail(report, S4_INJECT_ERR_NULL_ARG, NULL, "参数为空或槽位越界", 0u, slot);
    }
    entry = &ring->slots[slot];
    if (entry->state != S4_SLOT_CONSUMING || entry->invalidate_rounded_bytes == 0u) {
        return fail(report, S4_INJECT_ERR_EVENT_ORDER, "consumer_start",
                    "消费者必须先完成 input invalidate/barrier，再 start 后读取",
                    (uint64_t)S4_SLOT_CONSUMING, (uint64_t)entry->state);
    }
    if (ddr_length > size_max) {
        return fail(report, S4_INJECT_ERR_LENGTH, "ddr_length",
                    "DDR 影像长度超出 size_t 可表示范围", size_max, ddr_length);
    }
    if (ddr_length > UINT64_MAX - ddr_base) {
        return fail(report, S4_INJECT_ERR_BUFFER_RANGE, "buffer",
                    "DDR 基址与影像长度相加溢出", UINT64_MAX - ddr_base, ddr_length);
    }
    ddr_end = ddr_base + ddr_length;
    if (entry->addr_start < ddr_base || entry->addr_end > ddr_end) {
        return fail(report, S4_INJECT_ERR_BUFFER_RANGE, "buffer",
                    "帧区间超出提供的 DDR 影像范围", ddr_end, entry->addr_end);
    }
    offset = entry->addr_start - ddr_base;
    if (offset > size_max) {
        return fail(report, S4_INJECT_ERR_LENGTH, "offset",
                    "消费者读取偏移超出 size_t 可表示范围", size_max, offset);
    }
    if (offset > ddr_length || entry->desc.length_bytes > ddr_length - offset) {
        return fail(report, S4_INJECT_ERR_BUFFER_RANGE, "buffer.length_bytes",
                    "消费者读取区间超出 DDR 影像长度", ddr_length, offset);
    }
    if (entry->desc.length_bytes > size_max - offset) {
        return fail(report, S4_INJECT_ERR_LENGTH, "length_bytes",
                    "消费者偏移与读取长度之和超出 size_t 可表示范围",
                    size_max - offset, entry->desc.length_bytes);
    }
    frame_bytes = ddr_bytes + (size_t)offset;
    if (entry->desc.integrity_algorithm == S4_INTEGRITY_CRC32_IEEE) {
        const uint32_t actual = s4_inject_crc32(frame_bytes, (size_t)entry->desc.length_bytes);
        if (out_crc32 != NULL) {
            *out_crc32 = actual;
        }
        if (actual != entry->desc.integrity_crc32) {
            return fail(report, S4_INJECT_ERR_INTEGRITY, "frame_integrity.value",
                        "消费者读到的数据与声明 CRC32 不一致", entry->desc.integrity_crc32, actual);
        }
    } else {
        uint8_t digest[32];
        s4_inject_sha256(frame_bytes, (size_t)entry->desc.length_bytes, digest);
        if (out_crc32 != NULL) {
            *out_crc32 = s4_inject_crc32(frame_bytes, (size_t)entry->desc.length_bytes);
        }
        if (memcmp(digest, entry->desc.integrity_sha256, sizeof(digest)) != 0) {
            return fail(report, S4_INJECT_ERR_INTEGRITY, "frame_integrity.value",
                        "消费者读到的数据与声明 SHA-256 不一致", 0u, 0u);
        }
    }
    if (out_valid_bytes != NULL) {
        *out_valid_bytes = valid_row * (uint64_t)entry->desc.height *
                           (uint64_t)s4_inject_planes(entry->desc.pixel_format);
    }
    if (out_padding_bytes != NULL) {
        *out_padding_bytes =
            ((uint64_t)entry->desc.stride_bytes - valid_row) * (uint64_t)entry->desc.height *
            (uint64_t)s4_inject_planes(entry->desc.pixel_format);
    }
    if (report != NULL) {
        report->status = S4_INJECT_OK;
        report->field = NULL;
        report->reason = "OK";
        report->expected = 0u;
        report->actual = 0u;
    }
    return S4_INJECT_OK;
}
