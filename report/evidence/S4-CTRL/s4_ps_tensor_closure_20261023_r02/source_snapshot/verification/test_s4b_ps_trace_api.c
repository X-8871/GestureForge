#include "s4b_ps_trace.h"

#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint32_t flush_count;
static uint32_t barrier_count;
static uint32_t last_callback;
static uint32_t full_record_flushes;
static char callback_order[16];
static uint32_t callback_order_count;

static void record_callback(char operation)
{
    if (callback_order_count < sizeof(callback_order)) {
        callback_order[callback_order_count] = operation;
        ++callback_order_count;
    }
}

static void test_flush(void *address, size_t length)
{
    assert(address != NULL);
    assert(length != 0U);
    assert(last_callback != 1U);
    if (address == (void *)s4b_ps_trace_records &&
        length == sizeof(s4b_ps_trace_records)) {
        ++full_record_flushes;
        record_callback('R');
    } else if (address == (void *)&s4b_ps_trace_header_data &&
               length == sizeof(s4b_ps_trace_header_data)) {
        record_callback('H');
    }
    last_callback = 1U;
    ++flush_count;
}

static void test_barrier(void)
{
    assert(last_callback == 1U);
    record_callback('B');
    last_callback = 2U;
    ++barrier_count;
}

static uint32_t independent_crc32(const uint8_t *bytes, size_t length)
{
    uint32_t value = 0xFFFFFFFFU;
    size_t index;

    for (index = 0U; index < length; ++index) {
        unsigned int bit;
        value ^= (uint32_t)bytes[index];
        for (bit = 0U; bit < 8U; ++bit) {
            value = (value >> 1U) ^ ((value & 1U) != 0U ? 0xEDB88320U : 0U);
        }
    }
    return ~value;
}

static void complete_record(s4b_ps_trace_record *record, uint32_t index,
                            int observed, int safe)
{
    s4b_ps_trace_mark_start_command(record, 0x100000000ULL + index);
    s4b_ps_trace_mark_terminal(record, 0x200000000ULL + index,
                               700U + index, 0x1234U + index,
                               0xA0U + index, 0xB0U + index,
                               observed, safe, 0x300000000ULL + index);
    if (safe != 0) {
        s4b_ps_trace_mark_postprocess(record, 0U, 3U, 7U,
                                      0x400000000ULL + index);
    }
    s4b_ps_trace_set_response(record, 0U, safe != 0 ? 0U : UINT32_MAX,
                              safe != 0 ? 3U : 0U,
                              safe != 0 ? 7U : 0U);
}

static void test_session_range_exhaustion(void)
{
    uint32_t assigned = 0U;

    assert(s4b_ps_trace_initialize(0x202610230001ULL,
                                   S4B_PS_TRACE_SESSION_MAX,
                                   S4B_PS_TRACE_SESSION_MAX,
                                   "0123456789abcdef0123456789abcdef"
                                   "0123456789abcdef0123456789abcdef",
                                   test_flush, test_barrier) != 0);
    assert(s4b_ps_trace_begin_run(1U, 1U, 1U, 0x11111111U,
                                  S4B_PS_TRACE_INPUT_BYTES, &assigned) != 0);
    assert(assigned == S4B_PS_TRACE_SESSION_MAX);
    {
        s4b_ps_trace_record *record = s4b_ps_trace_begin_result(0U, 1U);
        assert(record != NULL);
        complete_record(record, 0U, 1, 1);
        assert(s4b_ps_trace_commit(record, 0x500000001ULL) != 0);
    }
    assert(s4b_ps_trace_end_run(1) != 0);
    assert(s4b_ps_trace_header_data.session_range_exhausted == 1U);
    assert(s4b_ps_trace_header_data.next_session_id == 0U);
    assert(s4b_ps_trace_begin_run(2U, 2U, 1U, 0x22222222U,
                                  S4B_PS_TRACE_INPUT_BYTES, &assigned) == 0);
    assert(s4b_ps_trace_header_data.last_rejected_reason ==
           S4B_PS_TRACE_REJECT_RANGE_EXHAUSTED);
    assert(s4b_ps_trace_header_data.last_assigned_session_id ==
           S4B_PS_TRACE_SESSION_MAX);
}

int main(int argc, char **argv)
{
    static const char source_sha[] =
        "0123456789abcdef0123456789abcdef"
        "0123456789abcdef0123456789abcdef";
    static const uint8_t crc_vector[] = "123456789";
    uint32_t session_id = 0U;
    uint32_t next_session_id = 0U;
    uint32_t before_rejects;
    uint32_t index;
    s4b_ps_trace_header zero_header;
    s4b_ps_trace_record *record;

    if (argc == 2 && strcmp(argv[1], "--range-exhaustion") == 0) {
        test_session_range_exhaustion();
        puts("PASS session_range_exhaustion");
        return 0;
    }

    assert(s4b_ps_trace_crc32(crc_vector, sizeof(crc_vector) - 1U) == 0xCBF43926U);
    assert(s4b_ps_trace_crc32(NULL, 0U) == 0U);
    assert(s4b_ps_trace_crc32(NULL, 1U) == 0U);
    memset(&zero_header, 0, sizeof(zero_header));
    assert(memcmp(&s4b_ps_trace_header_data, &zero_header, sizeof(zero_header)) == 0);
    memset(s4b_ps_trace_records, 0xA5, sizeof(s4b_ps_trace_records));

    assert(s4b_ps_trace_initialize(0x202610230002ULL, 0U, 102U,
                                   source_sha, test_flush, test_barrier) == 0);
    assert(memcmp(&s4b_ps_trace_header_data, &zero_header, sizeof(zero_header)) == 0);
    assert(s4b_ps_trace_initialize(0x202610230002ULL, 100U, 102U,
                                   source_sha, test_flush, test_barrier) != 0);
    assert(full_record_flushes == 1U);
    assert(callback_order_count >= 4U);
    assert(memcmp(callback_order, "RBHB", 4U) == 0);
    for (index = 0U; index < S4B_PS_TRACE_CAPACITY; ++index) {
        static const s4b_ps_trace_record zero_record = {0U};
        assert(memcmp(&s4b_ps_trace_records[index], &zero_record,
                      sizeof(zero_record)) == 0);
    }
    assert(s4b_ps_trace_header_data.magic == S4B_PS_TRACE_MAGIC);
    assert(s4b_ps_trace_header_data.schema_version == S4B_PS_TRACE_SCHEMA_VERSION);
    assert(s4b_ps_trace_header_data.header_bytes == sizeof(s4b_ps_trace_header));
    assert(s4b_ps_trace_header_data.record_bytes == sizeof(s4b_ps_trace_record));
    assert(s4b_ps_trace_header_data.header_crc32 == independent_crc32(
        (const uint8_t *)&s4b_ps_trace_header_data,
        offsetof(s4b_ps_trace_header, header_crc32)));

    before_rejects = s4b_ps_trace_header_data.rejected_request_count;
    assert(s4b_ps_trace_begin_run(8U, UINT32_MAX, 2U, 0x12345678U,
                                  S4B_PS_TRACE_INPUT_BYTES, &session_id) == 0);
    assert(s4b_ps_trace_header_data.last_rejected_reason == S4B_PS_TRACE_REJECT_BAD_RUN);
    assert(s4b_ps_trace_header_data.rejected_request_count == before_rejects + 1U);
    assert(s4b_ps_trace_header_data.last_assigned_session_id == 0U);
    assert(s4b_ps_trace_header_data.run_active == 0U);
    assert(s4b_ps_trace_begin_run(9U, 10U, 1U, 0x12345678U,
                                  S4B_PS_TRACE_INPUT_BYTES - 1U, &session_id) == 0);
    assert(s4b_ps_trace_header_data.last_rejected_reason == S4B_PS_TRACE_REJECT_BAD_RUN);
    assert(s4b_ps_trace_begin_run(10U, 20U, 2U, 0x89ABCDEFU,
                                  S4B_PS_TRACE_INPUT_BYTES, &session_id) != 0);
    assert(session_id == 100U);
    assert(s4b_ps_trace_begin_result(1U, 21U) == NULL);
    assert(s4b_ps_trace_header_data.record_count == 0U);
    assert(s4b_ps_trace_header_data.active_next_repeat_index == 0U);
    assert(s4b_ps_trace_header_data.last_rejected_reason == S4B_PS_TRACE_REJECT_RESULT_ORDER);
    s4b_ps_trace_set_input_write_ticks(0xABCDEF0102030405ULL,
                                       0xABCDEF0506070809ULL);

    record = s4b_ps_trace_begin_result(0U, 20U);
    assert(record != NULL);
    assert(record->session_id == 100U);
    assert(record->frame_id == 20U);
    assert(record->result_seq == 1U);
    assert(record->repeat_index == 0U);
    assert(record->uart_sequence == 10U);
    assert(record->input_crc32 == 0x89ABCDEFU);
    assert(record->input_length == S4B_PS_TRACE_INPUT_BYTES);
    assert(record->capture_time_available == 0U);
    assert(record->capture_time_ns == 0U);
    assert((record->unavailable_fields_mask & S4B_PS_TRACE_UNAVAILABLE_CAPTURE_TIME) != 0U);
    assert((record->event_flags & (S4B_PS_TRACE_EVENT_INPUT_WRITE_START |
                                   S4B_PS_TRACE_EVENT_INPUT_WRITE_DONE)) ==
           (S4B_PS_TRACE_EVENT_INPUT_WRITE_START | S4B_PS_TRACE_EVENT_INPUT_WRITE_DONE));
    complete_record(record, 0U, 1, 1);
    assert(record->terminal_observation_ticks_low == 0U);
    assert(record->terminal_observation_ticks_high == 3U);
    assert(record->terminal_safe == 1U);
    assert(s4b_ps_trace_commit(record, 0x500000000ULL) != 0);
    assert(s4b_ps_trace_header_data.record_count == 1U);
    assert(record->record_crc32 == independent_crc32((const uint8_t *)record,
        offsetof(s4b_ps_trace_record, record_crc32)));
    s4b_ps_trace_mark_uart(record, 0x600000000ULL, 0x600000005ULL, 1);
    s4b_ps_trace_mark_ack(record, 1);
    assert((record->event_flags & S4B_PS_TRACE_EVENT_UART_START) != 0U);
    assert((record->event_flags & S4B_PS_TRACE_EVENT_ACK_DONE) != 0U);
    assert(record->ack_state == S4B_PS_TRACE_ACK_SUCCEEDED);
    assert(s4b_ps_trace_end_run(0) != 0);

    assert(s4b_ps_trace_begin_run(11U, 30U, 1U, 0x10203040U,
                                  S4B_PS_TRACE_INPUT_BYTES, &session_id) != 0);
    assert(session_id == 101U);
    record = s4b_ps_trace_begin_result(0U, 30U);
    assert(record != NULL);
    complete_record(record, 1U, 0, 0);
    assert(record->terminal_safe == 0U);
    assert((record->event_flags & S4B_PS_TRACE_EVENT_TERMINAL_OBSERVED) == 0U);
    assert(record->terminal_status == 0x1235U);
    assert(record->terminal_observation_ticks_low == 0U);
    assert(s4b_ps_trace_commit(record, 0x500000001ULL) != 0);
    assert(s4b_ps_trace_end_run(0) != 0);

    assert(s4b_ps_trace_begin_run(12U, 1000U, 998U, 0x55667788U,
                                  S4B_PS_TRACE_INPUT_BYTES, &session_id) != 0);
    assert(session_id == 102U);
    for (index = 0U; index < 998U; ++index) {
        record = s4b_ps_trace_begin_result(index, 1000U + index);
        assert(record != NULL);
        s4b_ps_trace_mark_terminal(record, index, 1000U + index, 0x1236U,
                                   0U, 0U, 0, 0, 0U);
        s4b_ps_trace_set_response(record, 0U, UINT32_MAX, 0U, 0U);
        assert(s4b_ps_trace_commit(record, index) != 0);
    }
    assert(s4b_ps_trace_end_run(1) != 0);
    assert(s4b_ps_trace_header_data.record_count == S4B_PS_TRACE_CAPACITY);
    assert(s4b_ps_trace_header_data.run_active == 0U);
    assert(s4b_ps_trace_header_data.last_run_status == 1U);
    assert(s4b_ps_trace_begin_run(13U, 2000U, 1U, 0xAABBCCDDU,
                                  S4B_PS_TRACE_INPUT_BYTES, &next_session_id) == 0);
    assert(s4b_ps_trace_header_data.last_rejected_reason == S4B_PS_TRACE_REJECT_LOG_FULL);
    assert(s4b_ps_trace_header_data.log_full_reject_count == 1U);
    assert(s4b_ps_trace_header_data.record_count == S4B_PS_TRACE_CAPACITY);
    assert(s4b_ps_trace_records[0].session_id == 100U);
    assert(s4b_ps_trace_records[0].frame_id == 20U);
    assert(s4b_ps_trace_records[0].record_crc32 == independent_crc32(
        (const uint8_t *)&s4b_ps_trace_records[0],
        offsetof(s4b_ps_trace_record, record_crc32)));
    assert(s4b_ps_trace_records[S4B_PS_TRACE_CAPACITY - 1U].session_id == 102U);
    assert(s4b_ps_trace_header_data.header_crc32 == independent_crc32(
        (const uint8_t *)&s4b_ps_trace_header_data,
        offsetof(s4b_ps_trace_header, header_crc32)));
    assert(flush_count == barrier_count);
    assert(flush_count > S4B_PS_TRACE_CAPACITY);
    assert(last_callback == 2U);
    puts("PASS trace_api checks=1000_records_crc_order_sessions_capacity_init_flush=records_barrier_header_barrier");
    return 0;
}
