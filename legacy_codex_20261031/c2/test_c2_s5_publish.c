#include "c2_s5_publish.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

typedef struct C2FlushEvent {
    size_t length;
    uint32_t seqlock;
    uint32_t magic;
    uint32_t n_dets;
    uint64_t result_time;
} C2FlushEvent;

typedef struct C2MockPlatform {
    volatile uint8_t *block;
    uint64_t clock_values[2];
    uint32_t clock_calls;
    uint32_t barrier_calls;
    uint32_t flush_calls;
    uint32_t fail_flush_at;
    C2FlushEvent events[8];
} C2MockPlatform;

static int g_failures;

#define C2_CHECK(expression) \
    do { \
        if (!(expression)) { \
            (void)fprintf(stderr, "测试失败：%s:%d：%s\n", __FILE__, __LINE__, #expression); \
            ++g_failures; \
            return; \
        } \
    } while (0)

#define C2_DECLARE_BLOCK(name) \
    volatile uint32_t name##_words[C2_RESULT_WRITE_BYTES / sizeof(uint32_t)]; \
    volatile uint8_t *name = (volatile uint8_t *)name##_words

static uint32_t c2_test_get_u32(const volatile uint8_t *source)
{
    return (uint32_t)source[0] |
           ((uint32_t)source[1] << 8) |
           ((uint32_t)source[2] << 16) |
           ((uint32_t)source[3] << 24);
}

static uint16_t c2_test_get_u16(const volatile uint8_t *source)
{
    return (uint16_t)((uint16_t)source[0] | ((uint16_t)source[1] << 8));
}

static uint64_t c2_test_get_u64(const volatile uint8_t *source)
{
    return (uint64_t)c2_test_get_u32(source) |
           ((uint64_t)c2_test_get_u32(source + 4u) << 32);
}

static int c2_mock_read_gt(void *context, uint64_t *ticks)
{
    C2MockPlatform *mock = (C2MockPlatform *)context;
    if (mock == NULL || ticks == NULL || mock->clock_calls >= 2u) {
        return 0;
    }
    *ticks = mock->clock_values[mock->clock_calls++];
    return 1;
}

static int c2_mock_flush(void *context, uintptr_t address, size_t length)
{
    C2MockPlatform *mock = (C2MockPlatform *)context;
    C2FlushEvent *event;
    uintptr_t base;

    if (mock == NULL || mock->block == NULL || mock->flush_calls >= 8u) {
        return 0;
    }
    base = (uintptr_t)mock->block;
    event = &mock->events[mock->flush_calls];
    event->length = length;
    event->seqlock = c2_test_get_u32(mock->block + C2_SIDECAR_OFFSET + 0x18u);
    event->magic = c2_test_get_u32(mock->block + 0x00u);
    event->n_dets = c2_test_get_u32(mock->block + 0x08u);
    event->result_time = c2_test_get_u64(mock->block + C2_SIDECAR_OFFSET + 0x10u);
    if ((mock->flush_calls < 2u && (address != base || length != C2_RESULT_WRITE_BYTES)) ||
        (mock->flush_calls >= 2u &&
         (address != base + C2_SIDECAR_OFFSET || length != C2_SIDECAR_BYTES))) {
        return 0;
    }
    ++mock->flush_calls;
    return mock->fail_flush_at == mock->flush_calls ? 0 : 1;
}

static void c2_mock_barrier(void *context)
{
    C2MockPlatform *mock = (C2MockPlatform *)context;
    if (mock != NULL) {
        ++mock->barrier_calls;
    }
}

static void c2_mock_reset(C2MockPlatform *mock, volatile uint8_t *block)
{
    (void)memset(mock, 0, sizeof(*mock));
    mock->block = block;
    mock->clock_values[0] = 10000u;
    mock->clock_values[1] = 10070u;
}

static C2PlatformOps c2_mock_ops(C2MockPlatform *mock)
{
    C2PlatformOps ops;
    ops.context = mock;
    ops.read_gt_ticks = c2_mock_read_gt;
    ops.flush_range = c2_mock_flush;
    ops.data_sync_barrier = c2_mock_barrier;
    return ops;
}

static C2FrameInput c2_default_input(const s2a_t62_detection *detections, size_t count)
{
    C2FrameInput input;
    input.frame_id = 77u;
    input.image_width = 640u;
    input.image_height = 480u;
    input.status_flags = S5_RESULT_ST_VALID;
    input.capture_ticks = 200u;
    input.infer_done_ticks = 300u;
    input.detections = detections;
    input.detection_count = count;
    return input;
}

static int c2_init(C2Publisher *publisher)
{
    return C2Publisher_Init(publisher, ((uint64_t)0x1234u << 10), 1u, 0x1234u) == C2_PUBLISH_OK;
}

static s2a_t62_detection c2_test_detection(void)
{
    s2a_t62_detection detection;
    detection.class_id = 3;
    detection.source_order = 9;
    detection.score = 0.75;
    detection.x1 = 0.10;
    detection.y1 = 0.20;
    detection.x2 = 0.50;
    detection.y2 = 0.60;
    return detection;
}

static int c2_test_host_little_endian(void)
{
    const uint32_t probe = 1u;
    return *((const uint8_t *)&probe) == 1u;
}

static void c2_expect_detection_rejected(s2a_t62_detection detection)
{
    C2_DECLARE_BLOCK(block);
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input = c2_default_input(&detection, 1u);

    (void)memset((void *)block, 0xCC, C2_RESULT_WRITE_BYTES);
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_PUBLISH_DETECTION_REJECTED);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == 0u);
    C2_CHECK((c2_test_get_u32(block + 0x1Cu) & S5_RESULT_ST_VALID) == 0u);
    C2_CHECK(C2_ClassifyBusinessState(c2_test_get_u32(block + 0x1Cu), 0u, 0u) == C2_STATE_ERROR);
}

static void test_publish_layout_and_seqlock(void)
{
    C2_DECLARE_BLOCK(block);
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2PublishReceipt receipt;
    s2a_t62_detection detection = c2_test_detection();
    C2FrameInput input = c2_default_input(&detection, 1u);
    C2PublishCode code;
    size_t index;

    (void)memset((void *)block, 0xAA, C2_RESULT_WRITE_BYTES);
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    code = C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, &receipt);
    C2_CHECK(code == C2_PUBLISH_OK);
    C2_CHECK(c2_test_get_u32(block + 0x00u) == S5_RESULT_MAGIC);
    C2_CHECK(c2_test_get_u32(block + 0x04u) == 77u);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == 1u);
    C2_CHECK(c2_test_get_u32(block + 0x1Cu) == S5_RESULT_ST_VALID);
    C2_CHECK(c2_test_get_u16(block + S5_RESULT_DETS_OFFSET + 0u) == 64u);
    C2_CHECK(c2_test_get_u16(block + S5_RESULT_DETS_OFFSET + 2u) == 96u);
    C2_CHECK(c2_test_get_u16(block + S5_RESULT_DETS_OFFSET + 4u) == 256u);
    C2_CHECK(c2_test_get_u16(block + S5_RESULT_DETS_OFFSET + 6u) == 192u);
    C2_CHECK(block[S5_RESULT_DETS_OFFSET + 8u] == 3u);
    C2_CHECK(block[S5_RESULT_DETS_OFFSET + 9u] == 191u);
    for (index = 10u; index < S5_RESULT_DET_BYTES; ++index) {
        C2_CHECK(block[S5_RESULT_DETS_OFFSET + index] == 0u);
    }
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 0u) == C2_SIDECAR_MAGIC);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 4u) == C2_SIDECAR_VERSION);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 8u) == 0x1235u);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 12u) == 0u);
    C2_CHECK(c2_test_get_u64(block + C2_SIDECAR_OFFSET + 16u) == 10000u);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 24u) == 2u);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 28u) == 0u);
    C2_CHECK(mock.flush_calls == 4u && mock.barrier_calls == 8u && mock.clock_calls == 2u);
    C2_CHECK(mock.events[0].seqlock == 1u && mock.events[0].magic == 0xAAAAAAAAu);
    C2_CHECK(mock.events[1].seqlock == 1u && mock.events[1].magic == S5_RESULT_MAGIC);
    C2_CHECK(mock.events[1].n_dets == 1u && mock.events[1].result_time == 0u);
    C2_CHECK(mock.events[2].seqlock == 1u && mock.events[2].result_time == 10000u);
    C2_CHECK(mock.events[3].seqlock == 2u && mock.events[3].result_time == 10000u);
    C2_CHECK(receipt.flush_gap_valid == 1u && receipt.result_time_to_flush_ticks == 70u);
    C2_CHECK(receipt.session_id == 0x1235u && receipt.result_seq == 0u && receipt.seqlock == 2u);
}

static void test_fourteen_limit_and_error_publish(void)
{
    uint32_t guarded_words[C2_RESULT_WRITE_BYTES / sizeof(uint32_t) + 2u];
    volatile uint8_t *block = (volatile uint8_t *)&guarded_words[1];
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input;
    s2a_t62_detection detections[15];
    size_t index;

    (void)memset(guarded_words, 0xA5, sizeof(guarded_words));
    for (index = 0u; index < 15u; ++index) {
        detections[index] = c2_test_detection();
        detections[index].class_id = (int32_t)(index % 5u);
        detections[index].x1 = (double)index / 32.0;
        detections[index].x2 = ((double)index + 4.0) / 32.0;
    }
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    input = c2_default_input(detections, 1u);
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_PUBLISH_OK);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == 1u);
    C2_CHECK(block[S5_RESULT_DETS_OFFSET + 8u] == 0u);

    c2_mock_reset(&mock, block);
    input = c2_default_input(detections, 15u);
    input.frame_id = 78u;
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_PUBLISH_TOO_MANY_REJECTED);
    C2_CHECK(c2_test_get_u32(block + 0x04u) == 78u);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == 0u);
    C2_CHECK(c2_test_get_u32(block + 0x1Cu) == S5_RESULT_ST_OVERRUN);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 12u) == 1u);
    for (index = 0u; index < C2_SAFE_MAX_DETS * S5_RESULT_DET_BYTES; ++index) {
        C2_CHECK(block[S5_RESULT_DETS_OFFSET + index] == 0u);
    }
    C2_CHECK(mock.events[0].seqlock == 3u && mock.events[0].magic == S5_RESULT_MAGIC);
    C2_CHECK(mock.events[1].seqlock == 3u && mock.events[1].n_dets == 0u);
    C2_CHECK(mock.events[3].seqlock == 4u);
    C2_CHECK(guarded_words[0] == 0xA5A5A5A5u);
    C2_CHECK(guarded_words[(C2_RESULT_WRITE_BYTES / sizeof(uint32_t)) + 1u] == 0xA5A5A5A5u);
    C2_CHECK(c2_test_get_u32(block + S5_RESULT_DETS_OFFSET + 13u * S5_RESULT_DET_BYTES) == 0u);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET) == C2_SIDECAR_MAGIC);
}

static void test_fourteen_limit_success_and_sidecar_boundary(void)
{
    uint32_t guarded_words[C2_RESULT_WRITE_BYTES / sizeof(uint32_t) + 2u];
    volatile uint8_t *block = (volatile uint8_t *)&guarded_words[1];
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input;
    s2a_t62_detection detections[C2_SAFE_MAX_DETS];
    size_t index;
    size_t last_detection = S5_RESULT_DETS_OFFSET + (C2_SAFE_MAX_DETS - 1u) * S5_RESULT_DET_BYTES;

    (void)memset(guarded_words, 0xA5, sizeof(guarded_words));
    for (index = 0u; index < C2_SAFE_MAX_DETS; ++index) {
        detections[index] = c2_test_detection();
        detections[index].class_id = (int32_t)(index % 5u);
        detections[index].x1 = (double)index / 32.0;
        detections[index].x2 = ((double)index + 4.0) / 32.0;
    }
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    input = c2_default_input(detections, C2_SAFE_MAX_DETS);
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_PUBLISH_OK);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == C2_SAFE_MAX_DETS);
    C2_CHECK((c2_test_get_u32(block + 0x1Cu) & S5_RESULT_ST_VALID) != 0u);
    C2_CHECK(c2_test_get_u16(block + last_detection) == 260u);
    C2_CHECK(c2_test_get_u16(block + last_detection + 2u) == 96u);
    C2_CHECK(c2_test_get_u16(block + last_detection + 4u) == 80u);
    C2_CHECK(block[last_detection + 8u] == 3u);
    C2_CHECK(block[last_detection + 9u] == 191u);
    C2_CHECK(last_detection + S5_RESULT_DET_BYTES == C2_SIDECAR_OFFSET);
    C2_CHECK((uintptr_t)(block + C2_SIDECAR_OFFSET) % sizeof(uint32_t) == 0u);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET) == C2_SIDECAR_MAGIC);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 0x18u) == 2u);
    C2_CHECK(guarded_words[0] == 0xA5A5A5A5u);
    C2_CHECK(guarded_words[(C2_RESULT_WRITE_BYTES / sizeof(uint32_t)) + 1u] == 0xA5A5A5A5u);
}

static void test_invalid_detection_publishes_error(void)
{
    C2_DECLARE_BLOCK(block);
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    s2a_t62_detection detection = c2_test_detection();
    C2FrameInput input = c2_default_input(&detection, 1u);

    (void)memset((void *)block, 0, C2_RESULT_WRITE_BYTES);
    detection.class_id = 5;
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_PUBLISH_DETECTION_REJECTED);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == 0u);
    C2_CHECK(c2_test_get_u32(block + 0x1Cu) == 0u);
    C2_CHECK(C2_ClassifyBusinessState(c2_test_get_u32(block + 0x1Cu), 0u, 0u) == C2_STATE_ERROR);
}

static void test_nonfinite_and_invalid_box_inputs(void)
{
    s2a_t62_detection detection = c2_test_detection();

    detection.score = NAN;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.score = INFINITY;
    c2_expect_detection_rejected(detection);
    detection.score = -INFINITY;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.x1 = NAN;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.y1 = INFINITY;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.x2 = -INFINITY;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.x1 = -0.001;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.y2 = 1.001;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.x1 = 0.6;
    detection.x2 = 0.5;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.x1 = detection.x2;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.y1 = detection.y2;
    c2_expect_detection_rejected(detection);
    detection = c2_test_detection();
    detection.x1 = 0.5;
    detection.x2 = 0.5001;
    c2_expect_detection_rejected(detection);
}

static void test_score_q8_bounds_and_canvas_edge(void)
{
    C2_DECLARE_BLOCK(block);
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input;
    s2a_t62_detection detections[3];
    size_t index;

    for (index = 0u; index < 3u; ++index) {
        detections[index] = c2_test_detection();
        detections[index].x1 = 0.9;
        detections[index].y1 = 0.9;
        detections[index].x2 = 1.0;
        detections[index].y2 = 1.0;
    }
    detections[0].score = 0.0;
    detections[1].score = 0.5;
    detections[2].score = 1.0;
    (void)memset((void *)block, 0, C2_RESULT_WRITE_BYTES);
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    input = c2_default_input(detections, 3u);
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_PUBLISH_OK);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == 3u);
    for (index = 0u; index < 3u; ++index) {
        volatile uint8_t *entry = block + S5_RESULT_DETS_OFFSET + index * S5_RESULT_DET_BYTES;
        C2_CHECK(c2_test_get_u16(entry + 0u) == 576u);
        C2_CHECK(c2_test_get_u16(entry + 2u) == 432u);
        C2_CHECK(c2_test_get_u16(entry + 4u) == 64u);
        C2_CHECK(c2_test_get_u16(entry + 6u) == 48u);
    }
    C2_CHECK(block[S5_RESULT_DETS_OFFSET + 9u] == 0u);
    C2_CHECK(block[S5_RESULT_DETS_OFFSET + S5_RESULT_DET_BYTES + 9u] == 128u);
    C2_CHECK(block[S5_RESULT_DETS_OFFSET + 2u * S5_RESULT_DET_BYTES + 9u] == 255u);
}

static void test_unaligned_result_block_rejected(void)
{
    uint32_t words[C2_RESULT_WRITE_BYTES / sizeof(uint32_t) + 1u];
    volatile uint8_t *block = (volatile uint8_t *)words;
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input = c2_default_input(NULL, 0u);

    (void)memset(words, 0x5A, sizeof(words));
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    C2_CHECK(C2Publisher_Publish(&publisher, block + 1u, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_ERR_ALIGNMENT);
    C2_CHECK(mock.flush_calls == 0u);
    C2_CHECK(block[0] == 0x5Au && block[C2_RESULT_WRITE_BYTES] == 0x5Au);
}

static void test_upstream_error_and_status_priority(void)
{
    C2FrameInput input;
    input = c2_default_input(NULL, 0u);
    C2_CHECK(C2_ClassifyBusinessState(0u, 2u, 0u) == C2_STATE_ERROR);
    C2_CHECK(C2_ClassifyBusinessState(S5_RESULT_ST_VALID | S5_RESULT_ST_OVERRUN, 1u, 0u) == C2_STATE_ERROR);
    C2_CHECK(C2_ClassifyBusinessState(S5_RESULT_ST_VALID | S5_RESULT_ST_STALE, 0u, 0u) == C2_STATE_TIMEOUT);
    C2_CHECK(C2_ClassifyBusinessState(S5_RESULT_ST_VALID, 1u, C2_TIMEOUT_GT_TICKS) == C2_STATE_OK);
    C2_CHECK(C2_ClassifyBusinessState(S5_RESULT_ST_VALID, 1u, C2_TIMEOUT_GT_TICKS + 1u) == C2_STATE_TIMEOUT);
    C2_CHECK(C2_ClassifyBusinessState(S5_RESULT_ST_VALID, 0u, 0u) == C2_STATE_NO_HAND);
    C2_CHECK(C2_ClassifyBusinessState(S5_RESULT_ST_VALID, 1u, 0u) == C2_STATE_OK);
    input.status_flags = 0u;
    C2_CHECK(input.status_flags == 0u);
}

static void test_upstream_invalid_publishes_error(void)
{
    C2_DECLARE_BLOCK(block);
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input = c2_default_input(NULL, 0u);

    (void)memset((void *)block, 0, C2_RESULT_WRITE_BYTES);
    input.status_flags = 0u;
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_PUBLISH_UPSTREAM_INVALID);
    C2_CHECK(c2_test_get_u32(block + 0x04u) == input.frame_id);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == 0u);
    C2_CHECK(c2_test_get_u32(block + 0x1Cu) == 0u);
    C2_CHECK(c2_test_get_u32(block + C2_SIDECAR_OFFSET + 24u) == 2u);
}

static void test_age_conversion_and_clock_rollback(void)
{
    uint32_t valid = 0u;
    C2_CHECK(C2_AgePublishMs(333333343u, 0u, &valid) == 1000u && valid == 1u);
    C2_CHECK(C2_AgePublishMs(66666668u, 0u, &valid) == 199u && valid == 1u);
    C2_CHECK(C2_AgePublishMs(9u, 10u, &valid) == 0u && valid == 0u);
    C2_CHECK(C2_AgePublishMs(UINT64_MAX, 0u, &valid) == UINT32_MAX && valid == 1u);
}

static void test_missing_previous_session_and_seq_exhaustion(void)
{
    C2_DECLARE_BLOCK(block);
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input = c2_default_input(NULL, 0u);

    C2_CHECK(C2Publisher_Init(&publisher, 0x123400u, 0u, 0u) == C2_ERR_PREVIOUS_SESSION_UNKNOWN);
    C2_CHECK(publisher.initialized == 0u);
    (void)memset((void *)block, 0, C2_RESULT_WRITE_BYTES);
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    publisher.has_result = 1u;
    publisher.last_result_seq = UINT32_MAX;
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) ==
             C2_ERR_SEQUENCE_EXHAUSTED);
    C2_CHECK(mock.flush_calls == 0u);
}

static void test_flush_failure_poisoning(void)
{
    C2_DECLARE_BLOCK(block);
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input = c2_default_input(NULL, 0u);

    (void)memset((void *)block, 0, C2_RESULT_WRITE_BYTES);
    c2_mock_reset(&mock, block);
    mock.fail_flush_at = 2u;
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) == C2_ERR_FLUSH);
    C2_CHECK(publisher.poisoned == 1u && c2_test_get_u32(block + C2_SIDECAR_OFFSET + 24u) == 1u);
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) == C2_ERR_POISONED);
    C2_CHECK(mock.flush_calls == 2u);
}

static void test_real_2b_decoder_interface(void)
{
    double head13[3u * 10u * 13u * 13u];
    double head26[3u * 10u * 26u * 26u];
    s2a_t62_detection detections[15];
    size_t count = 0u;
    size_t raw_count = 0u;
    C2_DECLARE_BLOCK(block);
    C2Publisher publisher;
    C2MockPlatform mock;
    C2PlatformOps ops;
    C2FrameInput input;
    int decode_rc;

    (void)memset(head13, 0x00, sizeof(head13));
    (void)memset(head26, 0x00, sizeof(head26));
    for (size_t index = 0u; index < sizeof(head13) / sizeof(head13[0]); ++index) {
        head13[index] = -100.0;
    }
    for (size_t index = 0u; index < sizeof(head26) / sizeof(head26[0]); ++index) {
        head26[index] = -100.0;
    }
    head13[0u * 169u] = 0.0;
    head13[1u * 169u] = 0.0;
    head13[2u * 169u] = 0.0;
    head13[3u * 169u] = 0.0;
    head13[4u * 169u] = 12.0;
    head13[5u * 169u] = 12.0;

    decode_rc = s2a_t62_decode_nms(head13, sizeof(head13) / sizeof(head13[0]),
                                   head26, sizeof(head26) / sizeof(head26[0]),
                                   640u, 480u, 0.25, detections, 15u, &count, &raw_count);
    C2_CHECK(decode_rc == S2A_T62_OK);
    C2_CHECK(count == 1u && raw_count == 1u);
    (void)memset((void *)block, 0, C2_RESULT_WRITE_BYTES);
    c2_mock_reset(&mock, block);
    ops = c2_mock_ops(&mock);
    C2_CHECK(c2_init(&publisher));
    input = c2_default_input(detections, count);
    C2_CHECK(C2Publisher_Publish(&publisher, block, C2_RESULT_WRITE_BYTES, &input, &ops, NULL) == C2_PUBLISH_OK);
    C2_CHECK(c2_test_get_u32(block + 0x08u) == 1u);
    C2_CHECK(c2_test_get_u32(block + 0x1Cu) == S5_RESULT_ST_VALID);
}

int main(void)
{
    if (!c2_test_host_little_endian()) {
        (void)fprintf(stderr, "失败：测试主机必须为小端序\n");
        return 2;
    }
    test_publish_layout_and_seqlock();
    test_fourteen_limit_and_error_publish();
    test_fourteen_limit_success_and_sidecar_boundary();
    test_invalid_detection_publishes_error();
    test_nonfinite_and_invalid_box_inputs();
    test_score_q8_bounds_and_canvas_edge();
    test_unaligned_result_block_rejected();
    test_upstream_error_and_status_priority();
    test_upstream_invalid_publishes_error();
    test_age_conversion_and_clock_rollback();
    test_missing_previous_session_and_seq_exhaustion();
    test_flush_failure_poisoning();
    test_real_2b_decoder_interface();
    if (g_failures != 0) {
        (void)fprintf(stderr, "失败：%d项\n", g_failures);
        return 1;
    }
    (void)printf("PASS：C2发布、边界、时序及真实2B解码接口测试\n");
    return 0;
}
