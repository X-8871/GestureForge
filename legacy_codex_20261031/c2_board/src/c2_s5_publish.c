#include "c2_s5_publish.h"

#include <math.h>
#include <string.h>

#if defined(__BYTE_ORDER__) && defined(__ORDER_LITTLE_ENDIAN__)
#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "C2 seqlock requires a little-endian target"
#endif
#endif

#define C2_STATUS_KNOWN_MASK (S5_RESULT_ST_VALID | S5_RESULT_ST_OVERRUN | S5_RESULT_ST_STALE)
#define C2_SIDELOCK_OFFSET (C2_SIDECAR_OFFSET + 0x18u)
#define C2_RETRY_LIMIT 8u

typedef struct C2EncodedDet {
    uint16_t x;
    uint16_t y;
    uint16_t w;
    uint16_t h;
    uint8_t cls;
    uint8_t score_q8;
} C2EncodedDet;

static void c2_put_u16(volatile uint8_t *destination, uint16_t value)
{
    destination[0] = (uint8_t)(value & 0xFFu);
    destination[1] = (uint8_t)((value >> 8) & 0xFFu);
}

static void c2_put_u32(volatile uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)(value & 0xFFu);
    destination[1] = (uint8_t)((value >> 8) & 0xFFu);
    destination[2] = (uint8_t)((value >> 16) & 0xFFu);
    destination[3] = (uint8_t)((value >> 24) & 0xFFu);
}

static void c2_store_seqlock(volatile void *destination, uint32_t value)
{
    *(volatile uint32_t *)destination = value;
}

static void c2_write_detection(
    volatile uint8_t *destination,
    const C2EncodedDet *detection)
{
    c2_put_u16(destination + 0u, detection->x);
    c2_put_u16(destination + 2u, detection->y);
    c2_put_u16(destination + 4u, detection->w);
    c2_put_u16(destination + 6u, detection->h);
    destination[8] = detection->cls;
    destination[9] = detection->score_q8;
    c2_put_u16(destination + 10u, 0u);
    c2_put_u32(destination + 12u, 0u);
}

static int c2_round_edge(double normalized, uint32_t extent, uint32_t *edge)
{
    double scaled;
    uint32_t rounded;

    if (edge == NULL || !isfinite(normalized) || normalized < 0.0 || normalized > 1.0) {
        return 0;
    }
    scaled = normalized * (double)extent;
    rounded = (uint32_t)(scaled + 0.5);
    if (rounded > extent) {
        return 0;
    }
    *edge = rounded;
    return 1;
}

static int c2_encode_detection(const s2a_t62_detection *source, C2EncodedDet *destination)
{
    uint32_t left;
    uint32_t top;
    uint32_t right;
    uint32_t bottom;
    double q8;

    if (source == NULL || destination == NULL ||
        source->class_id < 0 || source->class_id > 4 ||
        !isfinite(source->score) || source->score < 0.0 || source->score > 1.0 ||
        !c2_round_edge(source->x1, 640u, &left) ||
        !c2_round_edge(source->y1, 480u, &top) ||
        !c2_round_edge(source->x2, 640u, &right) ||
        !c2_round_edge(source->y2, 480u, &bottom) ||
        left >= 640u || top >= 480u || right <= left || bottom <= top) {
        return 0;
    }

    q8 = source->score * 255.0 + 0.5;
    destination->x = (uint16_t)left;
    destination->y = (uint16_t)top;
    destination->w = (uint16_t)(right - left);
    destination->h = (uint16_t)(bottom - top);
    destination->cls = (uint8_t)source->class_id;
    destination->score_q8 = (uint8_t)q8;
    return 1;
}

static C2PublishCode c2_poison(C2Publisher *publisher, C2PublishCode code)
{
    publisher->poisoned = 1u;
    publisher->busy = 0u;
    return code;
}

C2PublishCode C2Publisher_Init(
    C2Publisher *publisher,
    uint64_t gt_at_start,
    uint32_t previous_session_valid,
    uint32_t previous_session_id)
{
    uint32_t candidate;
    uint32_t retry;

    if (publisher == NULL) {
        return C2_ERR_ARGUMENT;
    }
    (void)memset(publisher, 0, sizeof(*publisher));
    if (previous_session_valid == 0u) {
        return C2_ERR_PREVIOUS_SESSION_UNKNOWN;
    }
    if (previous_session_valid != 1u || previous_session_id > 0xFFFFu) {
        return C2_ERR_ARGUMENT;
    }

    candidate = (uint32_t)((gt_at_start >> 10) & 0xFFFFu);
    if (candidate == previous_session_id) {
        for (retry = 0u; retry < C2_RETRY_LIMIT && candidate == previous_session_id; ++retry) {
            candidate = (candidate + 1u) & 0xFFFFu;
        }
    }
    if (candidate == previous_session_id) {
        return C2_ERR_SESSION_COLLISION;
    }

    publisher->session_id = candidate;
    publisher->even_seqlock = 0u;
    publisher->initialized = 1u;
    return C2_PUBLISH_OK;
}

C2PublishCode C2Publisher_InitRev4Session(
    C2Publisher *publisher,
    uint64_t gt_at_start,
    uint32_t previous_session_valid,
    uint32_t previous_session_id)
{
    uint32_t candidate;
    uint32_t retry;

    if (publisher == NULL || previous_session_valid > 1u ||
        (previous_session_valid == 1u && previous_session_id > 0xFFFFu)) {
        return C2_ERR_ARGUMENT;
    }
    (void)memset(publisher, 0, sizeof(*publisher));
    candidate = (uint32_t)((gt_at_start >> 10) & 0xFFFFu);
    if (previous_session_valid == 1u && candidate == previous_session_id) {
        for (retry = 0u; retry < C2_RETRY_LIMIT && candidate == previous_session_id; ++retry) {
            candidate = (candidate + 1u) & 0xFFFFu;
        }
    }
    if (previous_session_valid == 1u && candidate == previous_session_id) {
        return C2_ERR_SESSION_COLLISION;
    }

    publisher->session_id = candidate;
    publisher->even_seqlock = 0u;
    publisher->initialized = 1u;
    return C2_PUBLISH_OK;
}

C2BusinessState C2_ClassifyBusinessState(uint32_t status_flags, uint32_t n_dets, uint64_t age_ticks)
{
    if ((status_flags & ~C2_STATUS_KNOWN_MASK) != 0u ||
        (status_flags & S5_RESULT_ST_VALID) == 0u ||
        (status_flags & S5_RESULT_ST_OVERRUN) != 0u ||
        n_dets > C2_SAFE_MAX_DETS) {
        return C2_STATE_ERROR;
    }
    if ((status_flags & S5_RESULT_ST_STALE) != 0u || age_ticks > C2_TIMEOUT_GT_TICKS) {
        return C2_STATE_TIMEOUT;
    }
    if (n_dets == 0u) {
        return C2_STATE_NO_HAND;
    }
    return C2_STATE_OK;
}

uint32_t C2_AgePublishMs(uint64_t now_ticks, uint64_t result_time_ticks, uint32_t *valid)
{
    uint64_t delta;
    uint64_t whole_seconds;
    uint64_t remainder;
    uint64_t milliseconds;

    if (valid == NULL) {
        return 0u;
    }
    *valid = 0u;
    if (now_ticks < result_time_ticks) {
        return 0u;
    }
    delta = now_ticks - result_time_ticks;
    whole_seconds = delta / C2_GT_TICKS_PER_SECOND;
    remainder = delta % C2_GT_TICKS_PER_SECOND;
    if (whole_seconds > (uint64_t)UINT32_MAX / 1000u) {
        *valid = 1u;
        return UINT32_MAX;
    }
    milliseconds = whole_seconds * 1000u +
                   (remainder * 1000u) / C2_GT_TICKS_PER_SECOND;
    *valid = 1u;
    return milliseconds > UINT32_MAX ? UINT32_MAX : (uint32_t)milliseconds;
}

static C2PublishCode c2_publisher_publish_internal(
    C2Publisher *publisher,
    volatile uint8_t *result_block,
    size_t result_block_bytes,
    const C2FrameInput *input,
    const C2PlatformOps *ops,
    C2PublishReceipt *receipt,
    uint32_t rev4_mode)
{
    C2EncodedDet encoded[C2_SAFE_MAX_DETS];
    size_t encoded_count = 0u;
    size_t index;
    uint32_t status_flags;
    uint32_t result_seq;
    uint32_t odd_seqlock;
    uint32_t even_seqlock;
    C2PublishCode completed_code = C2_PUBLISH_OK;
    uint64_t result_time_ticks;
    uint64_t completion_ticks;

    if (publisher == NULL || result_block == NULL || input == NULL || ops == NULL ||
        ops->read_gt_ticks == NULL || ops->flush_range == NULL ||
        ops->data_sync_barrier == NULL || result_block_bytes < C2_RESULT_WRITE_BYTES ||
        publisher->initialized == 0u) {
        return C2_ERR_ARGUMENT;
    }
    if (((uintptr_t)result_block & 3u) != 0u) {
        return C2_ERR_ALIGNMENT;
    }
    if (publisher->poisoned != 0u) {
        return C2_ERR_POISONED;
    }
    if (publisher->busy != 0u) {
        return C2_ERR_BUSY;
    }
    if ((input->status_flags & ~C2_STATUS_KNOWN_MASK) != 0u) {
        return C2_ERR_ARGUMENT;
    }
    if (publisher->even_seqlock > UINT32_MAX - 2u) {
        return C2_ERR_SEQLOCK_EXHAUSTED;
    }
    if (publisher->has_result != 0u && publisher->last_result_seq == UINT32_MAX) {
        return C2_ERR_SEQUENCE_EXHAUSTED;
    }

    result_seq = publisher->has_result != 0u ? publisher->last_result_seq + 1u : 0u;
    odd_seqlock = publisher->even_seqlock + 1u;
    even_seqlock = publisher->even_seqlock + 2u;
    status_flags = input->status_flags & (S5_RESULT_ST_OVERRUN | S5_RESULT_ST_STALE);

    if ((input->status_flags & S5_RESULT_ST_OVERRUN) != 0u) {
        status_flags |= S5_RESULT_ST_OVERRUN;
        completed_code = C2_PUBLISH_UPSTREAM_INVALID;
    } else if ((input->status_flags & S5_RESULT_ST_VALID) != 0u) {
        if (input->detection_count > C2_SAFE_MAX_DETS) {
            status_flags |= S5_RESULT_ST_OVERRUN;
            completed_code = C2_PUBLISH_TOO_MANY_REJECTED;
        } else if (input->image_width != 640u || input->image_height != 480u ||
            input->infer_done_ticks < input->capture_ticks ||
            (input->detection_count != 0u && input->detections == NULL)) {
            completed_code = C2_PUBLISH_UPSTREAM_INVALID;
        } else {
            for (index = 0u; index < input->detection_count; ++index) {
                if (!c2_encode_detection(&input->detections[index], &encoded[encoded_count])) {
                    completed_code = C2_PUBLISH_DETECTION_REJECTED;
                    break;
                }
                ++encoded_count;
            }
            if (completed_code == C2_PUBLISH_OK) {
                status_flags |= S5_RESULT_ST_VALID;
            }
        }
    } else {
        completed_code = C2_PUBLISH_UPSTREAM_INVALID;
    }

    if (completed_code != C2_PUBLISH_OK) {
        status_flags &= ~S5_RESULT_ST_VALID;
        encoded_count = 0u;
    }
    if ((status_flags & S5_RESULT_ST_OVERRUN) != 0u) {
        status_flags &= ~S5_RESULT_ST_VALID;
        encoded_count = 0u;
    }

    publisher->busy = 1u;
    c2_store_seqlock(result_block + C2_SIDELOCK_OFFSET, odd_seqlock);
    ops->data_sync_barrier(ops->context);
    if (!ops->flush_range(ops->context,
                          rev4_mode != 0u ? (uintptr_t)(result_block + C2_SIDELOCK_OFFSET) : (uintptr_t)result_block,
                          rev4_mode != 0u ? sizeof(uint32_t) : C2_RESULT_WRITE_BYTES)) {
        return c2_poison(publisher, C2_ERR_FLUSH);
    }
    ops->data_sync_barrier(ops->context);

    c2_put_u32(result_block + 0x00u, S5_RESULT_MAGIC);
    c2_put_u32(result_block + 0x04u, input->frame_id);
    c2_put_u32(result_block + 0x08u, (uint32_t)encoded_count);
    c2_put_u32(result_block + 0x0Cu, (uint32_t)input->capture_ticks);
    c2_put_u32(result_block + 0x10u, (uint32_t)(input->capture_ticks >> 32));
    c2_put_u32(result_block + 0x14u, (uint32_t)input->infer_done_ticks);
    c2_put_u32(result_block + 0x18u, (uint32_t)(input->infer_done_ticks >> 32));
    c2_put_u32(result_block + 0x1Cu, status_flags);
    for (index = 0u; index < C2_SAFE_MAX_DETS; ++index) {
        C2EncodedDet empty = {0u, 0u, 0u, 0u, 0u, 0u};
        volatile uint8_t *destination = result_block + S5_RESULT_DETS_OFFSET + index * S5_RESULT_DET_BYTES;
        c2_write_detection(destination, index < encoded_count ? &encoded[index] : &empty);
    }

    c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x00u, C2_SIDECAR_MAGIC);
    c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x04u, C2_SIDECAR_VERSION);
    c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x08u, publisher->session_id);
    c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x0Cu, result_seq);
    c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x10u, 0u);
    c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x14u, 0u);
    c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x1Cu, 0u);
    if (rev4_mode != 0u) {
        if (!ops->read_gt_ticks(ops->context, &result_time_ticks)) {
            return c2_poison(publisher, C2_ERR_CLOCK);
        }
        c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x10u, (uint32_t)result_time_ticks);
        c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x14u, (uint32_t)(result_time_ticks >> 32));
    }
    ops->data_sync_barrier(ops->context);
    if (!ops->flush_range(ops->context, (uintptr_t)result_block, C2_RESULT_WRITE_BYTES)) {
        return c2_poison(publisher, C2_ERR_FLUSH);
    }
    ops->data_sync_barrier(ops->context);

    if (rev4_mode == 0u) {
        if (!ops->read_gt_ticks(ops->context, &result_time_ticks)) {
            return c2_poison(publisher, C2_ERR_CLOCK);
        }
        c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x10u, (uint32_t)result_time_ticks);
        c2_put_u32(result_block + C2_SIDECAR_OFFSET + 0x14u, (uint32_t)(result_time_ticks >> 32));
        ops->data_sync_barrier(ops->context);
        if (!ops->flush_range(ops->context, (uintptr_t)(result_block + C2_SIDECAR_OFFSET), C2_SIDECAR_BYTES)) {
            return c2_poison(publisher, C2_ERR_FLUSH);
        }
        ops->data_sync_barrier(ops->context);
    }

    c2_store_seqlock(result_block + C2_SIDELOCK_OFFSET, even_seqlock);
    ops->data_sync_barrier(ops->context);
    if (!ops->flush_range(ops->context,
                          rev4_mode != 0u ? (uintptr_t)(result_block + C2_SIDELOCK_OFFSET)
                                          : (uintptr_t)(result_block + C2_SIDECAR_OFFSET),
                          rev4_mode != 0u ? sizeof(uint32_t) : C2_SIDECAR_BYTES)) {
        return c2_poison(publisher, C2_ERR_FLUSH);
    }
    ops->data_sync_barrier(ops->context);

    publisher->even_seqlock = even_seqlock;
    publisher->last_result_seq = result_seq;
    publisher->has_result = 1u;
    publisher->busy = 0u;

    if (receipt != NULL) {
        (void)memset(receipt, 0, sizeof(*receipt));
        receipt->session_id = publisher->session_id;
        receipt->result_seq = result_seq;
        receipt->seqlock = even_seqlock;
        receipt->status_flags = status_flags;
        receipt->n_dets = (uint32_t)encoded_count;
        receipt->result_time_ticks = result_time_ticks;
        if (ops->read_gt_ticks(ops->context, &completion_ticks) && completion_ticks >= result_time_ticks) {
            receipt->flush_complete_ticks = completion_ticks;
            receipt->result_time_to_flush_ticks = completion_ticks - result_time_ticks;
            receipt->flush_gap_valid = 1u;
        }
    }

    return completed_code;
}

C2PublishCode C2Publisher_Publish(
    C2Publisher *publisher,
    volatile uint8_t *result_block,
    size_t result_block_bytes,
    const C2FrameInput *input,
    const C2PlatformOps *ops,
    C2PublishReceipt *receipt)
{
    return c2_publisher_publish_internal(publisher, result_block, result_block_bytes,
                                         input, ops, receipt, 0u);
}

C2PublishCode C2Publisher_PublishRev4(
    C2Publisher *publisher,
    volatile uint8_t *result_block,
    size_t result_block_bytes,
    const C2FrameInput *input,
    const C2PlatformOps *ops,
    C2PublishReceipt *receipt)
{
    return c2_publisher_publish_internal(publisher, result_block, result_block_bytes,
                                         input, ops, receipt, 1u);
}
