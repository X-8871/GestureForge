#ifndef C2_S5_PUBLISH_H
#define C2_S5_PUBLISH_H

#include <stddef.h>
#include <stdint.h>

#include "s2a_ps_decode_nms_reference.h"
#include "s5_result_abi.h"

#define C2_SIDECAR_OFFSET 0x100u
#define C2_SIDECAR_BYTES 32u
#define C2_SIDECAR_MAGIC 0x53355831u
#define C2_SIDECAR_VERSION 1u
#define C2_SAFE_MAX_DETS ((C2_SIDECAR_OFFSET - S5_RESULT_DETS_OFFSET) / S5_RESULT_DET_BYTES)
#define C2_RESULT_WRITE_BYTES (C2_SIDECAR_OFFSET + C2_SIDECAR_BYTES)
#define C2_GT_TICKS_PER_SECOND 333333343ull
#define C2_TIMEOUT_GT_TICKS ((C2_GT_TICKS_PER_SECOND * 200ull) / 1000ull)
_Static_assert(C2_SAFE_MAX_DETS == 14u, "旁挂区与16项布局重叠，安全项数必须为14");
_Static_assert(C2_SIDECAR_OFFSET + C2_SIDECAR_BYTES == S5_RESULT_BLOCK_BYTES,
               "旁挂区必须恰好落在冻结结果块末端");

typedef struct C2Publisher {
    uint32_t session_id;
    uint32_t last_result_seq;
    uint32_t even_seqlock;
    uint32_t has_result;
    uint32_t initialized;
    uint32_t busy;
    uint32_t poisoned;
} C2Publisher;

typedef struct C2FrameInput {
    uint32_t frame_id;
    uint32_t image_width;
    uint32_t image_height;
    uint32_t status_flags;
    uint64_t capture_ticks;
    uint64_t infer_done_ticks;
    const s2a_t62_detection *detections;
    size_t detection_count;
} C2FrameInput;

typedef struct C2PlatformOps {
    void *context;
    int (*read_gt_ticks)(void *context, uint64_t *ticks);
    int (*flush_range)(void *context, uintptr_t address, size_t length);
    void (*data_sync_barrier)(void *context);
} C2PlatformOps;

typedef struct C2PublishReceipt {
    uint32_t session_id;
    uint32_t result_seq;
    uint32_t seqlock;
    uint32_t status_flags;
    uint32_t n_dets;
    uint64_t result_time_ticks;
    uint64_t flush_complete_ticks;
    uint64_t result_time_to_flush_ticks;
    uint32_t flush_gap_valid;
} C2PublishReceipt;

typedef enum C2PublishCode {
    C2_PUBLISH_OK = 0,
    C2_PUBLISH_UPSTREAM_INVALID = 1,
    C2_PUBLISH_TOO_MANY_REJECTED = 2,
    C2_PUBLISH_DETECTION_REJECTED = 3,
    C2_ERR_ARGUMENT = -1,
    C2_ERR_PREVIOUS_SESSION_UNKNOWN = -2,
    C2_ERR_SESSION_COLLISION = -3,
    C2_ERR_SEQUENCE_EXHAUSTED = -4,
    C2_ERR_SEQLOCK_EXHAUSTED = -5,
    C2_ERR_BUSY = -6,
    C2_ERR_POISONED = -7,
    C2_ERR_CLOCK = -8,
    C2_ERR_FLUSH = -9,
    C2_ERR_ALIGNMENT = -10
} C2PublishCode;

typedef enum C2BusinessState {
    C2_STATE_ERROR = 0,
    C2_STATE_TIMEOUT = 1,
    C2_STATE_NO_HAND = 2,
    C2_STATE_OK = 3
} C2BusinessState;

/* 缺少可核验的上一会话ID时拒绝初始化，防止伪称跨POR唯一。 */
C2PublishCode C2Publisher_Init(
    C2Publisher *publisher,
    uint64_t gt_at_start,
    uint32_t previous_session_valid,
    uint32_t previous_session_id);

/* rev4入口：只保证本次运行中SID恒定；旧sidecar不可读时不主张跨POR唯一。 */
C2PublishCode C2Publisher_InitRev4Session(
    C2Publisher *publisher,
    uint64_t gt_at_start,
    uint32_t previous_session_valid,
    uint32_t previous_session_id);

/* 将2B解码器输出写入调用方指定的0x20800000映射地址；基址须4字节对齐。 */
C2PublishCode C2Publisher_Publish(
    C2Publisher *publisher,
    volatile uint8_t *result_block,
    size_t result_block_bytes,
    const C2FrameInput *input,
    const C2PlatformOps *ops,
    C2PublishReceipt *receipt);

/* rev4入口：奇锁行、288 B payload、偶锁行三阶段发布；旧入口保持原行为。 */
C2PublishCode C2Publisher_PublishRev4(
    C2Publisher *publisher,
    volatile uint8_t *result_block,
    size_t result_block_bytes,
    const C2FrameInput *input,
    const C2PlatformOps *ops,
    C2PublishReceipt *receipt);

/* 按冻结优先级映射业务状态；age_ticks由消费端相对result_time计算。 */
C2BusinessState C2_ClassifyBusinessState(uint32_t status_flags, uint32_t n_dets, uint64_t age_ticks);

/* GT差值转整数毫秒；超大值饱和到UINT32_MAX，时钟回退返回0。 */
uint32_t C2_AgePublishMs(uint64_t now_ticks, uint64_t result_time_ticks, uint32_t *valid);

#endif
