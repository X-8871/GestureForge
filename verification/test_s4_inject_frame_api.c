#include "s4_inject_frame.h"

#include <stdio.h>
#include <string.h>

static s4_inject_ring g_ring;
static uint8_t g_backing[2048];
static unsigned g_check_count;
static unsigned g_failure_count;
static unsigned g_flush_count;
static unsigned g_invalidate_count;
static unsigned g_barrier_count;
static unsigned g_cache_context;

#define CHECK(label, expression)                                                        \
    do {                                                                                \
        const int check_passed = (expression) ? 1 : 0;                                 \
        ++g_check_count;                                                                \
        printf("{\"check\":\"%s\",\"status\":\"%s\"}\n", (label),                    \
               check_passed != 0 ? "PASS" : "FAIL");                                  \
        if (check_passed == 0) {                                                        \
            ++g_failure_count;                                                         \
        }                                                                               \
    } while (0)

static void flush_range(void *ctx, uint64_t addr, uint64_t length) {
    (void)addr;
    (void)length;
    if (ctx == &g_cache_context) {
        ++g_flush_count;
    }
}

static void invalidate_range(void *ctx, uint64_t addr, uint64_t length) {
    (void)addr;
    (void)length;
    if (ctx == &g_cache_context) {
        ++g_invalidate_count;
    }
}

static int cache_barrier(void *ctx) {
    if (ctx != &g_cache_context) {
        return 0;
    }
    ++g_barrier_count;
    return 1;
}

static s4_inject_status initialize_ring(uint32_t session_id,
                                        s4_inject_validation_report *report) {
    const char local_region_name[] = "local_region";
    const s4_inject_region local_region = {
        local_region_name, UINT64_C(0x10000000), UINT64_C(2048)};
    const s4_inject_cache_ops local_cache = {
        flush_range, invalidate_range, cache_barrier};
    return s4_inject_ring_init(&g_ring, 2u, session_id, &local_region, 1u,
                               &local_cache, &g_cache_context, report);
}

static void make_frame(s4_inject_frame_desc *desc, uint32_t session_id,
                       uint32_t frame_id, uint64_t offset,
                       const uint8_t *payload) {
    memset(desc, 0, sizeof(*desc));
    (void)strcpy(desc->contract_version, S4_INJECT_CONTRACT_VERSION);
    desc->source_kind = S4_SRC_FILE_INJECTION;
    desc->session_id = session_id;
    desc->frame_id = frame_id;
    desc->width = 4u;
    desc->height = 4u;
    desc->pixel_format = S4_FMT_RGB888;
    desc->stride_bytes = 12u;
    (void)strcpy(desc->region_name, "local_region");
    desc->base_addr = UINT64_C(0x10000000);
    desc->offset_bytes = offset;
    desc->length_bytes = 48u;
    desc->alignment = S4_INJECT_MAINTENANCE_ALIGNMENT_BYTES;
    desc->integrity_algorithm = S4_INTEGRITY_CRC32_IEEE;
    desc->integrity_crc32 = s4_inject_crc32(payload, 48u);
    desc->capture_time_state = S4_CAPTURE_UNAVAILABLE;
    desc->injection_start_ns = 1u;
    (void)strcpy(desc->clock_name, "XTime");
    desc->clock_freq_hz = UINT64_C(100000000);
    (void)strcpy(desc->wrap_handling, "reject_wrap_explicit_reset");
    (void)strcpy(desc->epoch_note, "relative_to_ps_boot");
    (void)strcpy(desc->clock_domain, "PS global timer");
    desc->measurement_scope_source_kind = S4_MEAS_SCOPE_BOARD_INJECTION;
    desc->scope_pl_timing = S4_SCOPE_NOT_EXECUTED_OFFLINE;
    desc->scope_uart_transport = S4_SCOPE_NOT_EXECUTED_OFFLINE;
    desc->scope_board_pl = S4_SCOPE_NOT_EXECUTED_OFFLINE;
    desc->unavailable_capture_time = 1u;
}

static int advance_ok(uint32_t slot, s4_inject_event event,
                      s4_inject_validation_report *report) {
    return s4_inject_ring_advance(&g_ring, slot, event, report) == S4_INJECT_OK;
}

static int start_consumer(uint32_t slot, s4_inject_validation_report *report) {
    return advance_ok(slot, S4_EV_WRITE_COMPLETE, report) &&
           advance_ok(slot, S4_EV_FLUSH, report) &&
           advance_ok(slot, S4_EV_PUBLISH, report) &&
           advance_ok(slot, S4_EV_INVALIDATE, report) &&
           advance_ok(slot, S4_EV_CONSUMER_START, report);
}

static int finish_frame(uint32_t slot, s4_inject_validation_report *report) {
    return start_consumer(slot, report) &&
           advance_ok(slot, S4_EV_CONSUMER_DONE, report) &&
           advance_ok(slot, S4_EV_RELEASE, report);
}

int main(void) {
    s4_inject_validation_report report;
    s4_inject_frame_desc frame_a;
    s4_inject_frame_desc frame_b;
    const char empty_region_name[] = "";
    const s4_inject_region invalid_region = {
        empty_region_name, UINT64_C(0x10000000), UINT64_C(2048)};
    const s4_inject_cache_ops test_cache_ops = {
        flush_range, invalidate_range, cache_barrier};
    s4_inject_ring ring_snapshot;
    s4_inject_status geometry_status = S4_INJECT_OK;
    s4_inject_status status;
    uint8_t payload_a[48];
    uint8_t payload_b[48];
    uint64_t large_bytes;
    uint64_t valid_bytes = 0u;
    uint64_t padding_bytes = 0u;
    uint32_t read_crc = 0u;
    uint32_t index;

    for (index = 0u; index < 48u; ++index) {
        payload_a[index] = (uint8_t)(0x10u + index);
        payload_b[index] = (uint8_t)(0x80u + index);
    }
    memset(&g_ring, 0, sizeof(g_ring));
    status = s4_inject_ring_init(&g_ring, 2u, 7u, &invalid_region, 1u,
                                 &test_cache_ops, &g_cache_context, &report);
    CHECK("invalid_initial_region_name_preserves_uninitialized_ring",
          status == S4_INJECT_ERR_REGION_UNKNOWN && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_REGION_UNKNOWN") == 0 &&
              report.field != NULL && strcmp(report.field, "regions.name") == 0 &&
              g_ring.initialized_magic == 0u && g_ring.session_initialized == 0u &&
              g_ring.session_id == 0u);
    CHECK("same_session_retry_after_initial_region_failure",
          initialize_ring(7u, &report) == S4_INJECT_OK &&
              g_ring.initialized_magic == S4_INJECT_RING_INITIALIZED_MAGIC &&
              g_ring.session_id == 7u);
    make_frame(&frame_a, 7u, 10u, 0u, payload_a);
    make_frame(&frame_b, 7u, 11u, 0u, payload_b);

    status = s4_inject_ring_bind(&g_ring, 0u, &frame_a, NULL, 48u, &report);
    CHECK("null_payload_rejected",
          status == S4_INJECT_ERR_NULL_ARG && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_NULL_ARG") == 0 &&
              report.field != NULL && strcmp(report.field, "payload") == 0 &&
              strstr(report.reason, "禁止跳过 CRC/SHA") != NULL &&
              g_ring.slots[0].state == S4_SLOT_FREE &&
              g_ring.slots[0].integrity_checked == 0u);

    CHECK("first_in_flight_frame_binds",
          s4_inject_ring_bind(&g_ring, 0u, &frame_a, payload_a, 48u, &report) ==
              S4_INJECT_OK);
    memcpy(g_backing, payload_a, sizeof(payload_a));
    status = s4_inject_ring_bind(&g_ring, 1u, &frame_b, payload_b, 48u, &report);
    CHECK("overlap_rejected_before_mock_write",
          status == S4_INJECT_ERR_BUFFER_OVERLAP && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_BUFFER_OVERLAP") == 0 &&
              report.field != NULL && strcmp(report.field, "buffer") == 0 &&
              strstr(report.reason, "写入前拒绝") != NULL &&
              g_ring.slots[1].state == S4_SLOT_FREE &&
              memcmp(g_backing, payload_a, sizeof(payload_a)) == 0);

    make_frame(&frame_b, 7u, 9u, 64u, payload_b);
    status = s4_inject_ring_bind(&g_ring, 1u, &frame_b, payload_b, 48u, &report);
    CHECK("in_flight_sequence_10_then_9_rejected",
          status == S4_INJECT_ERR_OUT_OF_ORDER && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_OUT_OF_ORDER") == 0 &&
              report.field != NULL && strcmp(report.field, "frame_id") == 0 &&
              strstr(report.reason, "严格递增") != NULL);

    CHECK("consumer_starts_after_input_invalidate",
          start_consumer(0u, &report));
#if SIZE_MAX < UINT64_MAX
    {
        const uint64_t oversized_ddr_length = (uint64_t)SIZE_MAX + UINT64_C(1);
        status = s4_inject_ring_consumer_read(
            &g_ring, 0u, g_backing, oversized_ddr_length,
            UINT64_C(0x10000000), &read_crc, &valid_bytes, &padding_bytes, &report);
        CHECK("32_bit_consumer_read_ddr_length_exceeds_size_t_rejected",
              status == S4_INJECT_ERR_LENGTH && report.status == status &&
                  strcmp(s4_inject_status_name(status), "ERR_LENGTH") == 0 &&
                  report.field != NULL && strcmp(report.field, "ddr_length") == 0 &&
                  strstr(report.reason, "超出 size_t") != NULL &&
                  report.expected == (uint64_t)SIZE_MAX &&
                  g_ring.slots[0].state == S4_SLOT_CONSUMING);
    }
#else
    CHECK("64_bit_consumer_read_size_bounds_behavior_not_applicable",
          sizeof(size_t) >= sizeof(uint64_t));
#endif
    CHECK("local_ops_and_region_name_remain_valid",
          s4_inject_ring_consumer_read(&g_ring, 0u, g_backing, sizeof(g_backing),
                                       UINT64_C(0x10000000), &read_crc,
                                       &valid_bytes, &padding_bytes, &report) ==
                  S4_INJECT_OK &&
              read_crc == frame_a.integrity_crc32 && valid_bytes == 48u &&
              padding_bytes == 0u &&
              advance_ok(0u, S4_EV_CONSUMER_DONE, &report) &&
              advance_ok(0u, S4_EV_RELEASE, &report));

    CHECK("maintenance_callbacks_called",
          g_flush_count == 1u && g_invalidate_count == 1u && g_barrier_count == 2u);
    CHECK("rgb888_stride_overflow_rejected",
          s4_inject_min_stride(S4_FMT_RGB888, UINT32_MAX) == 0u);
    CHECK("rgb565_u64_product_boundary",
          (large_bytes = s4_inject_expected_frame_bytes(
               S4_FMT_RGB565, UINT32_MAX, UINT32_MAX / 2u,
               UINT32_MAX, &geometry_status)) != 0u &&
              geometry_status == S4_INJECT_OK &&
              large_bytes == (uint64_t)UINT32_MAX * (uint64_t)UINT32_MAX);
    CHECK("int8_chw_requires_416_square",
          s4_inject_expected_frame_bytes(S4_FMT_INT8_CHW_416, 416u, 416u,
                                         415u, &geometry_status) == 0u &&
              geometry_status == S4_INJECT_ERR_GEOMETRY);
    CHECK("int8_chw_valid_bytes_include_three_planes",
          s4_inject_expected_frame_bytes(S4_FMT_INT8_CHW_416, 416u, 416u,
                                         416u, &geometry_status) == UINT64_C(519168) &&
              geometry_status == S4_INJECT_OK);
#if SIZE_MAX < UINT64_MAX
    {
        const uint64_t wide_length = s4_inject_expected_frame_bytes(
            S4_FMT_RGB888, 3u, 1u, UINT32_MAX, &geometry_status);
        const s4_inject_region wide_region = {
            "local_region", UINT64_C(0x10000000), wide_length};
        make_frame(&frame_a, 7u, 1u, 0u, payload_a);
        frame_a.width = 1u;
        frame_a.height = UINT32_MAX;
        frame_a.stride_bytes = 3u;
        frame_a.length_bytes = wide_length;
        status = s4_inject_validate(&frame_a, &wide_region, 1u, payload_a,
                                    wide_length, &report);
        CHECK("32_bit_size_t_payload_length_overflow_rejected",
              geometry_status == S4_INJECT_OK && wide_length > (uint64_t)SIZE_MAX &&
                  status == S4_INJECT_ERR_LENGTH && report.status == status &&
                  report.field != NULL && strcmp(report.field, "payload_length") == 0 &&
                  strstr(report.reason, "超出 size_t") != NULL);
    }
#else
    CHECK("64_bit_size_t_payload_length_branch_not_applicable",
          sizeof(size_t) >= sizeof(uint64_t));
#endif

    make_frame(&frame_a, 7u, 11u, 64u, payload_a);
    status = s4_inject_ring_bind(&g_ring, 1u, &frame_a, payload_a, 48u, &report);
    CHECK("timeout_test_frame_binds", status == S4_INJECT_OK);
    CHECK("timeout_marks_failed_slot_and_keeps_memory",
          advance_ok(1u, S4_EV_WRITE_COMPLETE, &report) &&
              advance_ok(1u, S4_EV_FLUSH, &report) &&
              advance_ok(1u, S4_EV_PUBLISH, &report) &&
              (status = s4_inject_ring_timeout(&g_ring, 1u, &report)) ==
                  S4_INJECT_ERR_CONSUMER_TIMEOUT && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_CONSUMER_TIMEOUT") == 0 &&
              report.field != NULL && strcmp(report.field, "consumer_done") == 0 &&
              strstr(report.reason, "FAILED 槽仍占有帧") != NULL &&
              g_ring.slots[1].state == S4_SLOT_FAILED &&
              s4_inject_ring_held_count(&g_ring) == 1u);
    CHECK("reset_cannot_drop_failed_slot",
          (status = s4_inject_ring_init(&g_ring, 2u, 8u, NULL, 0u, NULL, NULL, &report)) ==
              S4_INJECT_ERR_EVENT_ORDER && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_EVENT_ORDER") == 0 &&
              report.field != NULL && strcmp(report.field, "ring.reset") == 0 &&
              strstr(report.reason, "仍持有帧") != NULL &&
              s4_inject_ring_held_count(&g_ring) == 1u);
    CHECK("abort_requires_stop_confirmation",
          (status = s4_inject_ring_abort(&g_ring, 1u, &report)) == S4_INJECT_ERR_EVENT_ORDER &&
              report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_EVENT_ORDER") == 0 &&
              report.field != NULL && strcmp(report.field, "consumer_stopped_confirmed") == 0 &&
              strstr(report.reason, "未收到消费者停止") != NULL &&
              g_ring.slots[1].state == S4_SLOT_FAILED);
    make_frame(&frame_b, 7u, 12u, 64u, payload_b);
    CHECK("failed_slot_still_blocks_overlapping_frame",
          s4_inject_ring_bind(&g_ring, 0u, &frame_b, payload_b, 48u, &report) ==
              S4_INJECT_ERR_BUFFER_OVERLAP &&
              g_ring.slots[0].state == S4_SLOT_FREE);
    CHECK("stop_confirmation_then_abort_releases_memory",
          s4_inject_ring_confirm_consumer_stopped(&g_ring, 1u, &report) == S4_INJECT_OK &&
              s4_inject_ring_abort(&g_ring, 1u, &report) == S4_INJECT_OK &&
              s4_inject_ring_held_count(&g_ring) == 0u);
    memcpy(&ring_snapshot, &g_ring, sizeof(g_ring));
    status = s4_inject_ring_init(&g_ring, 2u, 8u, &invalid_region, 1u,
                                 &test_cache_ops, &g_cache_context, &report);
    CHECK("invalid_idle_ring_reset_preserves_ring_and_session",
          status == S4_INJECT_ERR_REGION_UNKNOWN && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_REGION_UNKNOWN") == 0 &&
              report.field != NULL && strcmp(report.field, "regions.name") == 0 &&
              memcmp(&g_ring, &ring_snapshot, sizeof(g_ring)) == 0 &&
              g_ring.initialized_magic == S4_INJECT_RING_INITIALIZED_MAGIC &&
              g_ring.session_id == 7u && g_ring.slot_count == 2u);
    CHECK("ring_reset_rejects_same_session",
          (status = initialize_ring(7u, &report)) == S4_INJECT_ERR_SESSION &&
              report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_SESSION") == 0 &&
              report.field != NULL && strcmp(report.field, "session_id") == 0 &&
              strstr(report.reason, "新 u32 session_id") != NULL &&
              memcmp(&g_ring, &ring_snapshot, sizeof(g_ring)) == 0);
    CHECK("ring_reset_uses_new_session",
          initialize_ring(8u, &report) == S4_INJECT_OK);
    make_frame(&frame_a, 8u, 10u, 0u, payload_a);
    CHECK("dropped_frame_advances_session_sequence",
          s4_inject_ring_drop(&g_ring, &frame_a, &report) == S4_INJECT_OK &&
              g_ring.last_accepted_frame_id == 10u && g_ring.dropped_frames == 1u);
    make_frame(&frame_a, 8u, 9u, 0u, payload_a);
    CHECK("dropped_frame_regression_rejected",
          (status = s4_inject_ring_drop(&g_ring, &frame_a, &report)) ==
                  S4_INJECT_ERR_OUT_OF_ORDER && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_OUT_OF_ORDER") == 0 &&
              report.field != NULL && strcmp(report.field, "frame_id") == 0 &&
              strstr(report.reason, "严格递增") != NULL && g_ring.dropped_frames == 1u);
    make_frame(&frame_a, 8u, UINT32_MAX, 0u, payload_a);
    CHECK("frame_id_reserved_wrap_rejected",
          (status = s4_inject_ring_bind(&g_ring, 0u, &frame_a, payload_a, 48u, &report)) ==
              S4_INJECT_ERR_OUT_OF_ORDER && report.status == status &&
              strcmp(s4_inject_status_name(status), "ERR_OUT_OF_ORDER") == 0 &&
              report.field != NULL && strcmp(report.field, "frame_id") == 0 &&
              g_ring.slots[0].state == S4_SLOT_FREE);
    make_frame(&frame_a, 8u, 20u, 0u, payload_a);
    make_frame(&frame_b, 8u, 21u, 64u, payload_b);
    CHECK("two_nonoverlap_frames_bind",
          s4_inject_ring_bind(&g_ring, 0u, &frame_a, payload_a, 48u, &report) == S4_INJECT_OK &&
              s4_inject_ring_bind(&g_ring, 1u, &frame_b, payload_b, 48u, &report) == S4_INJECT_OK);
    CHECK("release_order_regression_rejected",
          finish_frame(1u, &report) &&
              finish_frame(0u, &report) == 0 &&
              report.status == S4_INJECT_ERR_OUT_OF_ORDER &&
              strcmp(s4_inject_status_name(report.status), "ERR_OUT_OF_ORDER") == 0 &&
              report.field != NULL && strcmp(report.field, "frame_id") == 0 &&
              strstr(report.reason, "递增 frame_id 顺序") != NULL &&
              g_ring.slots[0].state == S4_SLOT_CONSUMED);

    CHECK("final_summary",
          g_failure_count == 0u);
    printf("{\"status\":\"%s\",\"checks\":%u,\"failures\":%u}\n",
           g_failure_count == 0u ? "PASS" : "FAIL", g_check_count, g_failure_count);
    return g_failure_count == 0u ? 0 : 1;
}
