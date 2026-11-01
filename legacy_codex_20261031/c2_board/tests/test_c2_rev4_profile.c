#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "c2_s5_publish.h"
#include "c2_integration_status.h"

typedef struct TestContext {
    uintptr_t address[8];
    size_t length[8];
    size_t flush_count;
    uint64_t ticks;
    uint32_t barrier_count;
} TestContext;

static int check(int condition, const char *name)
{
    if (condition == 0) {
        (void)fprintf(stderr, "FAIL %s\n", name);
        return 0;
    }
    return 1;
}

static int test_read_gt(void *context, uint64_t *ticks)
{
    TestContext *test = (TestContext *)context;
    if (test == NULL || ticks == NULL) {
        return 0;
    }
    *ticks = ++test->ticks;
    return 1;
}

static int test_flush(void *context, uintptr_t address, size_t length)
{
    TestContext *test = (TestContext *)context;
    if (test == NULL || test->flush_count >= 8u) {
        return 0;
    }
    test->address[test->flush_count] = address;
    test->length[test->flush_count] = length;
    ++test->flush_count;
    return 1;
}

static void test_dsb(void *context)
{
    TestContext *test = (TestContext *)context;
    if (test != NULL) {
        ++test->barrier_count;
    }
}

int main(void)
{
    _Alignas(4) uint8_t block[C2_RESULT_WRITE_BYTES];
    C2Publisher publisher;
    C2Publisher old_publisher;
    C2FrameInput input;
    C2PlatformOps ops;
    C2PublishReceipt receipt;
    TestContext context;
    C2PublishCode rc;
    s2a_t62_detection detections[15];
    uintptr_t base = (uintptr_t)block;
    int ok = 1;

    (void)memset(&context, 0, sizeof(context));
    (void)memset(&input, 0, sizeof(input));
    (void)memset(block, 0, sizeof(block));
    context.ticks = 100u;
    ops.context = &context;
    ops.read_gt_ticks = test_read_gt;
    ops.flush_range = test_flush;
    ops.data_sync_barrier = test_dsb;

    rc = C2Publisher_Init(&old_publisher, 16384u, 0u, 0u);
    ok &= check(rc == C2_ERR_PREVIOUS_SESSION_UNKNOWN, "旧Init仍拒绝缺失previous SID");
    rc = C2Publisher_InitRev4Session(&publisher, 16384u, 0u, 0u);
    ok &= check(rc == C2_PUBLISH_OK && publisher.session_id == 16u,
                "rev4 Init允许未知旧sidecar并固定本会话SID");
    rc = C2Publisher_InitRev4Session(&publisher, 16384u, 1u, 16u);
    ok &= check(rc == C2_PUBLISH_OK && publisher.session_id == 17u,
                "rev4 Init对真实可读旧SID执行递增避碰");
    rc = C2Publisher_InitRev4Session(&publisher, 16384u, 0u, 0u);
    ok &= check(rc == C2_PUBLISH_OK && publisher.session_id == 16u,
                "rev4 Init重置为本会话GT派生SID");

    input.frame_id = 1u;
    input.image_width = 640u;
    input.image_height = 480u;
    input.status_flags = S5_RESULT_ST_VALID;
    input.capture_ticks = 10u;
    input.infer_done_ticks = 20u;
    rc = C2Publisher_PublishRev4(&publisher, block, sizeof(block), &input, &ops, &receipt);
    ok &= check(rc == C2_PUBLISH_OK, "rev4 publish成功");
    ok &= check(context.flush_count == 3u, "rev4恰好三次flush");
    if (context.flush_count == 3u) {
        ok &= check(context.address[0] == base + C2_SIDECAR_OFFSET + 0x18u && context.length[0] == 4u,
                    "rev4先flush奇数锁字");
        ok &= check(context.address[1] == base && context.length[1] == C2_RESULT_WRITE_BYTES,
                    "rev4再flush完整288B结果块");
        ok &= check(context.address[2] == base + C2_SIDECAR_OFFSET + 0x18u && context.length[2] == 4u,
                    "rev4最后flush偶数锁字");
    }
    ok &= check(receipt.session_id == 16u && receipt.result_seq == 0u && receipt.seqlock == 2u,
                "rev4结果携带固定SID、首序号与稳定锁值");
    ok &= check(receipt.flush_gap_valid == 1u && receipt.result_time_to_flush_ticks == 1u,
                "rev4回执记录真实GT flush间隔");
    ok &= check(C2_ClassifyBusinessState(S5_RESULT_ST_VALID, 0u, 0u) == C2_STATE_NO_HAND,
                "有效零框状态分类为NO_HAND");
    ok &= check(C2_ClassifyBusinessState(S5_RESULT_ST_VALID | S5_RESULT_ST_OVERRUN, 0u, 0u) == C2_STATE_ERROR,
                "overrun状态分类为ERROR");
    ok &= check(C2_ClassifyBusinessState(S5_RESULT_ST_VALID | S5_RESULT_ST_STALE, 0u, 0u) == C2_STATE_TIMEOUT,
                "stale状态分类为TIMEOUT");
    ok &= check(C2_ClassifyBusinessState(S5_RESULT_ST_VALID, 1u, 0u) == C2_STATE_OK,
                "有效非零框状态分类为OK");

    (void)memset(detections, 0, sizeof(detections));
    for (size_t i = 0u; i < 15u; ++i) {
        detections[i].class_id = (int32_t)(i % 5u);
        detections[i].score = 0.75;
        detections[i].x1 = 0.10;
        detections[i].y1 = 0.10;
        detections[i].x2 = 0.20;
        detections[i].y2 = 0.20;
        detections[i].source_order = (int)i;
    }
    (void)memset(&context, 0, sizeof(context));
    context.ticks = 150u;
    ops.context = &context;
    (void)memset(block, 0, sizeof(block));
    rc = C2Publisher_InitRev4Session(&publisher, 16384u, 0u, 0u);
    ok &= check(rc == C2_PUBLISH_OK, "15框拒绝用例初始化");
    input.detections = detections;
    input.detection_count = 15u;
    rc = C2Publisher_PublishRev4(&publisher, block, sizeof(block), &input, &ops, &receipt);
    ok &= check(rc == C2_PUBLISH_TOO_MANY_REJECTED, "真实15框按safe14规则拒绝");
    ok &= check(input.detection_count == 15u, "15框用例未截断decoder计数");
    ok &= check(((uint32_t *)(void *)block)[2] == 0u &&
                    (((uint32_t *)(void *)block)[7] & S5_RESULT_ST_OVERRUN) != 0u &&
                    (((uint32_t *)(void *)block)[7] & S5_RESULT_ST_VALID) == 0u,
                "15框发布ERROR状态且n_dets=0");
    ok &= check(C2_IntegrationPass(1u, rc, 1u, 0, 1u) == 0u,
                "15框发布拒绝使最终CHAINB失败");

    (void)memset(&context, 0, sizeof(context));
    context.ticks = 170u;
    ops.context = &context;
    (void)memset(block, 0, sizeof(block));
    detections[0].class_id = 5;
    input.detection_count = 1u;
    rc = C2Publisher_PublishRev4(&publisher, block, sizeof(block), &input, &ops, &receipt);
    ok &= check(rc == C2_PUBLISH_DETECTION_REJECTED, "非法检测项返回正值拒绝码");
    ok &= check(((uint32_t *)(void *)block)[2] == 0u &&
                    (((uint32_t *)(void *)block)[7] & S5_RESULT_ST_VALID) == 0u,
                "非法检测项发布无效空错误帧");
    ok &= check(C2_IntegrationPass(1u, rc, 1u, 0, 1u) == 0u,
                "检测项拒绝使最终CHAINB失败");
    ok &= check(C2_IntegrationPass(1u, C2_PUBLISH_OK, 1u, -4, 1u) == 0u,
                "显示服务失败使最终CHAINB失败");
    ok &= check(C2_IntegrationPass(1u, C2_PUBLISH_OK, 1u, -1, 1u) == 0u,
                "未运行显示服务不能使最终CHAINB通过");
    ok &= check(C2_IntegrationPass(1u, C2_PUBLISH_OK, 1u, 0, 1u) == 1u,
                "2B、发布、读回和显示均成功才通过");

    (void)memset(&context, 0, sizeof(context));
    context.ticks = 200u;
    ops.context = &context;
    (void)memset(block, 0, sizeof(block));
    input.detections = NULL;
    input.detection_count = 0u;
    rc = C2Publisher_Init(&old_publisher, 16384u, 1u, 5u);
    ok &= check(rc == C2_PUBLISH_OK, "旧Init仍可由previous SID初始化");
    rc = C2Publisher_Publish(&old_publisher, block, sizeof(block), &input, &ops, &receipt);
    ok &= check(rc == C2_PUBLISH_OK && context.flush_count == 4u,
                "旧Publish接口保留四次flush行为");
    if (context.flush_count == 4u) {
        ok &= check(context.address[0] == base && context.length[0] == C2_RESULT_WRITE_BYTES,
                    "旧Publish首flush保持原范围");
        ok &= check(context.address[1] == base && context.length[1] == C2_RESULT_WRITE_BYTES,
                    "旧Publish第二flush保持原范围");
        ok &= check(context.address[2] == base + C2_SIDECAR_OFFSET && context.length[2] == C2_SIDECAR_BYTES,
                    "旧Publish时间flush保持原范围");
        ok &= check(context.address[3] == base + C2_SIDECAR_OFFSET && context.length[3] == C2_SIDECAR_BYTES,
                    "旧Publish末flush保持原范围");
    }

    if (ok == 0) {
        return 1;
    }
    (void)puts("PASS C2 rev4 profile, three-stage flush, receipt, and legacy API");
    return 0;
}
