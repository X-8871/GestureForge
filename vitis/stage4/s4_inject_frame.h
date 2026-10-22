/* 阶段4 单帧注入通路：输入帧契约校验 + 8 事件状态机（离线可验证）。
 *
 * 本文件是共享契约 `docs/stage4/s4b_shared_input_result_contract.json` 的实现侧：
 *  - 字段名/枚举取值与契约一致（contract_version / source_kind / pixel_format /
 *    buffer.region_name / frame_integrity / injection_start_ns / measurement_scope）；
 *  - 事件顺序与契约 `input_frame_contract.events.order` 一一对应；
 *  - 区域地址/长度由调用方从 `docs/stage4/S4B_stage4_address_map.json` 读入，
 *    本文件不内嵌任何绝对地址，也不猜地址；
 *  - 注入模式下 capture_time_ns 不可用（UNAVAILABLE），不接受任何伪造值。
 *
 * 主机侧使用 mock cache/DDR 验证；PS 侧只需替换 s4_inject_cache_ops 为 BSP 的
 * Xil_DCacheFlushRange / Xil_DCacheInvalidateRange 适配。本文件不依赖 Xilinx 头。
 */

#ifndef S4_INJECT_FRAME_H
#define S4_INJECT_FRAME_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define S4_INJECT_CONTRACT_VERSION "s4-shared-io/1.1.0"
#define S4_INJECT_CACHE_LINE_BYTES 64u
#define S4_INJECT_MAX_SLOTS 4u
#define S4_INJECT_MAX_REGIONS 8u
#define S4_INJECT_SESSION_ID_MAX 40u
#define S4_INJECT_REGION_NAME_MAX 48u
#define S4_INJECT_CLOCK_NAME_MAX 48u

/* 状态码：同时作为进程退出码（0 = OK）。任何非零码都必须能定位到唯一原因。 */
typedef enum {
    S4_INJECT_OK = 0,
    S4_INJECT_ERR_NULL_ARG = 1,
    S4_INJECT_ERR_CONTRACT_VERSION = 2,
    S4_INJECT_ERR_SOURCE_KIND = 3,
    S4_INJECT_ERR_PIXEL_FORMAT = 4,
    S4_INJECT_ERR_GEOMETRY = 5,
    S4_INJECT_ERR_STRIDE = 6,
    S4_INJECT_ERR_LENGTH = 7,
    S4_INJECT_ERR_REGION_UNKNOWN = 8,
    S4_INJECT_ERR_BUFFER_RANGE = 9,
    S4_INJECT_ERR_ALIGNMENT = 10,
    S4_INJECT_ERR_BUFFER_OVERLAP = 11,
    S4_INJECT_ERR_NO_FREE_BUFFER = 12,   /* 队列满：无空闲槽位 */
    S4_INJECT_ERR_NO_OVERWRITE = 13,     /* 试图覆盖仍被持有的槽位 */
    S4_INJECT_ERR_DUPLICATE_FRAME = 14,
    S4_INJECT_ERR_OUT_OF_ORDER = 15,
    S4_INJECT_ERR_EVENT_ORDER = 16,
    S4_INJECT_ERR_INTEGRITY = 17,
    S4_INJECT_ERR_CONSUMER_TIMEOUT = 18,
    S4_INJECT_ERR_CAPTURE_TIME_FORGED = 19,
    S4_INJECT_ERR_MEASUREMENT_SCOPE = 20,
    S4_INJECT_ERR_DROPPED_FRAME = 21,
    S4_INJECT_ERR_FLUSH_COVERAGE = 22,   /* flush 未覆盖整帧（方向/范围错误） */
    S4_INJECT_ERR_STATUS_COUNT = 23
} s4_inject_status;

typedef enum {
    S4_SRC_FILE_INJECTION = 0,
    S4_SRC_CAMERA = 1,
    S4_SRC_SYNTHETIC = 2,
    S4_SRC_KIND_COUNT = 3
} s4_inject_source_kind;

typedef enum {
    S4_FMT_RGB888 = 0,
    S4_FMT_RGB565 = 1,
    S4_FMT_GRAY8 = 2,
    S4_FMT_INT8_CHW_416 = 3,
    S4_FMT_COUNT = 4
} s4_inject_pixel_format;

typedef enum {
    S4_INTEGRITY_CRC32_IEEE = 0,
    S4_INTEGRITY_SHA256 = 1,
    S4_INTEGRITY_COUNT = 2
} s4_inject_integrity_algorithm;

/* C 侧以状态表示契约的 capture_time_available：UNAVAILABLE ⇔ false（注入/合成），
 * PROVIDED ⇔ true（仅 camera 且给出真实首个有效像素时刻）。 */
typedef enum { S4_CAPTURE_UNAVAILABLE = 0, S4_CAPTURE_PROVIDED = 1 } s4_capture_time_state;

typedef enum {
    S4_SCOPE_MEASURED = 0,
    S4_SCOPE_NOT_EXECUTED_OFFLINE = 1,
    S4_SCOPE_COUNT = 2   /* 取值域与契约 measurement_scope 一致，不得自造枚举 */
} s4_inject_scope_value;

/* 契约事件顺序（下标即顺序，必须 1:1 使用）。 */
typedef enum {
    S4_EV_WRITE_START = 0,
    S4_EV_WRITE_COMPLETE = 1,
    S4_EV_FLUSH = 2,
    S4_EV_PUBLISH = 3,
    S4_EV_CONSUMER_START = 4,
    S4_EV_CONSUMER_DONE = 5,
    S4_EV_INVALIDATE = 6,
    S4_EV_RELEASE = 7,
    S4_EV_COUNT = 8
} s4_inject_event;

typedef enum {
    S4_SLOT_FREE = 0,
    S4_SLOT_LOADING = 1,
    S4_SLOT_LOADED = 2,
    S4_SLOT_FLUSHED = 3,
    S4_SLOT_PUBLISHED = 4,
    S4_SLOT_CONSUMING = 5,
    S4_SLOT_CONSUMED = 6,
    S4_SLOT_INVALIDATED = 7,
    S4_SLOT_FAILED = 8,
    S4_SLOT_STATE_COUNT = 9
} s4_inject_slot_state;

typedef struct {
    const char *name;      /* 必须与地址图 region.name 相同 */
    uint64_t base_addr;
    uint64_t length_bytes;
} s4_inject_region;

typedef struct {
    void (*flush)(void *ctx, uint64_t addr, uint64_t length_bytes);
    void (*invalidate)(void *ctx, uint64_t addr, uint64_t length_bytes);
} s4_inject_cache_ops;

typedef struct {
    const char *contract_version;
    s4_inject_source_kind source_kind;
    char session_id[S4_INJECT_SESSION_ID_MAX];
    uint32_t frame_id;
    uint32_t width;
    uint32_t height;
    s4_inject_pixel_format pixel_format;
    uint32_t stride_bytes;
    char region_name[S4_INJECT_REGION_NAME_MAX];
    uint64_t base_addr;
    uint64_t offset_bytes;
    uint64_t length_bytes;
    uint32_t alignment;
    s4_inject_integrity_algorithm integrity_algorithm;
    uint32_t integrity_crc32;
    uint8_t integrity_sha256[32];
    s4_capture_time_state capture_time_state;
    uint64_t capture_time_ns;      /* 仅 camera 模式可为真值 */
    uint64_t injection_start_ns;   /* 仅 file_injection 模式有意义 */
    char clock_name[S4_INJECT_CLOCK_NAME_MAX];
    uint64_t clock_freq_hz;
    const char *wrap_handling;
    const char *epoch_note;
    const char *clock_domain;
    s4_inject_scope_value scope_pl_timing;
    s4_inject_scope_value scope_uart_transport;
    s4_inject_scope_value scope_board_pl;
    uint32_t unavailable_capture_time; /* 1 = capture_time 列入 unavailable_fields */
} s4_inject_frame_desc;

typedef struct {
    s4_inject_status status;
    const char *field;    /* 定位字段名（NULL 表示非字段级错误） */
    const char *reason;   /* 稳定、可定位的人类可读原因 */
    uint64_t expected;
    uint64_t actual;
} s4_inject_validation_report;

typedef struct {
    s4_inject_slot_state state;
    s4_inject_frame_desc desc;
    uint64_t addr_start;
    uint64_t addr_end;
    uint64_t written_bytes;
    uint32_t observed_events;      /* 位掩码 */
    uint32_t integrity_checked;    /* 1 = 已按契约校验完整性 */
    uint64_t flush_rounded_bytes;
    uint64_t invalidate_rounded_bytes;
    uint32_t consumer_started;
} s4_inject_slot;

typedef struct {
    s4_inject_slot slots[S4_INJECT_MAX_SLOTS];
    uint32_t slot_count;
    s4_inject_region regions[S4_INJECT_MAX_REGIONS];
    uint32_t region_count;
    const s4_inject_cache_ops *cache;
    void *cache_ctx;
    uint32_t last_released_frame_id;
    uint32_t in_flight;
    uint64_t flush_events;
    uint64_t invalidate_events;
    uint64_t timeout_events;
    uint64_t dropped_frames;
    uint64_t flushes_without_write;
    uint32_t dropped_ids[S4_INJECT_MAX_SLOTS];
    uint32_t dropped_id_count;
} s4_inject_ring;

/* ---- 名称与基础工具 ---- */
const char *s4_inject_status_name(s4_inject_status status);
const char *s4_inject_event_name(s4_inject_event event);
const char *s4_inject_slot_state_name(s4_inject_slot_state state);
const char *s4_inject_source_kind_name(s4_inject_source_kind kind);
const char *s4_inject_pixel_format_name(s4_inject_pixel_format format);
const char *s4_inject_integrity_name(s4_inject_integrity_algorithm algorithm);
const char *s4_inject_scope_name(s4_inject_scope_value value);

uint32_t s4_inject_crc32(const void *data, size_t length);
void s4_inject_sha256(const void *data, size_t length, uint8_t out[32]);
uint32_t s4_inject_planes(s4_inject_pixel_format format);
uint32_t s4_inject_min_stride(s4_inject_pixel_format format, uint32_t width);
uint64_t s4_inject_expected_frame_bytes(s4_inject_pixel_format format, uint32_t stride_bytes,
                                        uint32_t width, uint32_t height,
                                        s4_inject_status *status);
int s4_inject_intervals_overlap(uint64_t a0, uint64_t a1, uint64_t b0, uint64_t b1);
uint64_t s4_inject_round_down(uint64_t value, uint64_t alignment);
uint64_t s4_inject_round_up(uint64_t value, uint64_t alignment);

/* ---- 契约校验（参数/长度/格式/stride/geometry/region/越界/对齐/时间戳） ---- */
s4_inject_status s4_inject_validate(const s4_inject_frame_desc *desc,
                                    const s4_inject_region *regions, uint32_t region_count,
                                    const uint8_t *payload, uint64_t payload_length,
                                    s4_inject_validation_report *report);

/* ---- 环与状态机 ---- */
s4_inject_status s4_inject_ring_init(s4_inject_ring *ring, uint32_t slot_count,
                                     const s4_inject_region *regions, uint32_t region_count,
                                     const s4_inject_cache_ops *cache, void *cache_ctx,
                                     s4_inject_validation_report *report);
s4_inject_status s4_inject_ring_acquire(s4_inject_ring *ring, uint32_t *out_slot,
                                       s4_inject_validation_report *report);
s4_inject_status s4_inject_ring_bind(s4_inject_ring *ring, uint32_t slot,
                                     const s4_inject_frame_desc *desc,
                                     const uint8_t *payload, uint64_t payload_length,
                                     s4_inject_validation_report *report);
s4_inject_status s4_inject_ring_advance(s4_inject_ring *ring, uint32_t slot, s4_inject_event event,
                                       s4_inject_validation_report *report);
s4_inject_status s4_inject_ring_timeout(s4_inject_ring *ring, uint32_t slot,
                                       s4_inject_validation_report *report);
s4_inject_status s4_inject_ring_abort(s4_inject_ring *ring, uint32_t slot,
                                     s4_inject_validation_report *report);
s4_inject_status s4_inject_ring_drop(s4_inject_ring *ring, const s4_inject_frame_desc *desc,
                                    s4_inject_validation_report *report);
s4_inject_status s4_inject_ring_consumer_read(s4_inject_ring *ring, uint32_t slot,
                                             const uint8_t *ddr_bytes, uint64_t ddr_length,
                                             uint64_t ddr_base, uint32_t *out_crc32,
                                             uint64_t *out_valid_bytes,
                                             uint64_t *out_padding_bytes,
                                             s4_inject_validation_report *report);
uint32_t s4_inject_ring_held_count(const s4_inject_ring *ring);
s4_inject_event s4_inject_expected_event(s4_inject_slot_state state);

#ifdef __cplusplus
}
#endif

#endif /* S4_INJECT_FRAME_H */