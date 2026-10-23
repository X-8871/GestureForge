#include "s4b_ps_trace.h"

#include <limits.h>
#include <string.h>

_Static_assert(sizeof(uint32_t) == 4U, "旁路日志要求32位字段");
_Static_assert(sizeof(s4b_ps_trace_header) == 144U, "旁路日志头布局变化");
_Static_assert(sizeof(s4b_ps_trace_record) == 184U, "旁路记录布局变化");

s4b_ps_trace_header s4b_ps_trace_header_data __attribute__((aligned(64), used));
s4b_ps_trace_record s4b_ps_trace_records[S4B_PS_TRACE_CAPACITY]
    __attribute__((aligned(64), used));

static s4b_ps_trace_flush_fn s4b_flush_callback;
static s4b_ps_trace_barrier_fn s4b_barrier_callback;
static uint32_t s4b_trace_initialized;
static uint32_t s4b_run_input_crc32;
static uint32_t s4b_run_input_length;
static uint32_t s4b_run_expected_records;
static uint32_t s4b_run_reserved_records;
static uint32_t s4b_run_committed_records;
static uint32_t s4b_run_base_record_count;
static uint32_t s4b_run_input_write_seen;
static uint64_t s4b_run_input_write_start_ticks;
static uint64_t s4b_run_input_write_done_ticks;

static uint32_t s4b_saturating_increment(uint32_t value)
{
    return value == UINT32_MAX ? value : value + 1U;
}

uint32_t s4b_ps_trace_crc32(const uint8_t *bytes, size_t length)
{
    uint32_t crc = UINT32_MAX;
    size_t index;

    if (bytes == NULL && length != 0U) return 0U;
    for (index = 0U; index < length; ++index) {
        unsigned int bit;
        crc ^= (uint32_t)bytes[index];
        for (bit = 0U; bit < 8U; ++bit) {
            uint32_t mask = 0U - (crc & 1U);
            crc = (crc >> 1U) ^ (0xEDB88320U & mask);
        }
    }
    return ~crc;
}

static int s4b_hex_value(char value, uint32_t *digit)
{
    if (value >= '0' && value <= '9') {
        *digit = (uint32_t)(value - '0');
        return 1;
    }
    if (value >= 'a' && value <= 'f') {
        *digit = (uint32_t)(value - 'a') + 10U;
        return 1;
    }
    if (value >= 'A' && value <= 'F') {
        *digit = (uint32_t)(value - 'A') + 10U;
        return 1;
    }
    return 0;
}

static int s4b_parse_sha256(const char *text, uint32_t words[8])
{
    unsigned int word_index;

    if (text == NULL || words == NULL) return 0;
    for (word_index = 0U; word_index < 8U; ++word_index) {
        unsigned int char_index;
        uint32_t value = 0U;
        for (char_index = 0U; char_index < 8U; ++char_index) {
            uint32_t digit;
            if (!s4b_hex_value(text[word_index * 8U + char_index], &digit)) return 0;
            value = (value << 4U) | digit;
        }
        words[word_index] = value;
    }
    return 1;
}

static void s4b_store_ticks(uint32_t *low, uint32_t *high, uint64_t ticks)
{
    *low = (uint32_t)ticks;
    *high = (uint32_t)(ticks >> 32U);
}

static int s4b_header_is_ready(void)
{
    return s4b_trace_initialized != 0U &&
           s4b_ps_trace_header_data.magic == S4B_PS_TRACE_MAGIC &&
           s4b_ps_trace_header_data.schema_version == S4B_PS_TRACE_SCHEMA_VERSION;
}

static void s4b_flush_barrier(void *address, size_t length)
{
    s4b_flush_callback(address, length);
    s4b_barrier_callback();
}

static void s4b_update_header(void)
{
    s4b_ps_trace_header_data.header_crc32 = s4b_ps_trace_crc32(
        (const uint8_t *)&s4b_ps_trace_header_data,
        offsetof(s4b_ps_trace_header, header_crc32));
    s4b_flush_barrier(&s4b_ps_trace_header_data, sizeof(s4b_ps_trace_header_data));
}

static void s4b_note_rejection(uint32_t uart_sequence, uint32_t frame_id,
                               uint32_t reason)
{
    if (!s4b_header_is_ready()) return;
    s4b_ps_trace_header_data.rejected_request_count = s4b_saturating_increment(
        s4b_ps_trace_header_data.rejected_request_count);
    if (reason == S4B_PS_TRACE_REJECT_LOG_FULL) {
        s4b_ps_trace_header_data.log_full_reject_count = s4b_saturating_increment(
            s4b_ps_trace_header_data.log_full_reject_count);
    }
    s4b_ps_trace_header_data.last_rejected_sequence = uart_sequence;
    s4b_ps_trace_header_data.last_rejected_frame = frame_id;
    s4b_ps_trace_header_data.last_rejected_reason = reason;
    s4b_update_header();
}

static int s4b_record_is_valid(const s4b_ps_trace_record *record)
{
    if (record == NULL || record->record_index >= S4B_PS_TRACE_CAPACITY) return 0;
    return record == &s4b_ps_trace_records[record->record_index] &&
           record->magic == S4B_PS_TRACE_RECORD_MAGIC &&
           record->schema_version == S4B_PS_TRACE_SCHEMA_VERSION &&
           record->record_bytes == sizeof(s4b_ps_trace_record);
}

static void s4b_update_record(s4b_ps_trace_record *record)
{
    record->record_crc32 = s4b_ps_trace_crc32(
        (const uint8_t *)record, offsetof(s4b_ps_trace_record, record_crc32));
    s4b_flush_barrier(record, sizeof(*record));
}

int s4b_ps_trace_initialize(uint64_t boot_seed, uint32_t session_first,
                            uint32_t session_last, const char *source_sha256_hex,
                            s4b_ps_trace_flush_fn flush,
                            s4b_ps_trace_barrier_fn barrier)
{
    uint32_t source_words[8];
    uint64_t seed_value = boot_seed;

    /* 参数全部通过后才初始化，失败时不破坏已有日志状态。 */
    if (s4b_trace_initialized != 0U || seed_value == 0U ||
        session_first == 0U || session_first > session_last ||
        session_last > S4B_PS_TRACE_SESSION_MAX || source_sha256_hex == NULL ||
        flush == NULL || barrier == NULL || !s4b_parse_sha256(source_sha256_hex, source_words)) {
        return 0;
    }

    memset(&s4b_ps_trace_header_data, 0, sizeof(s4b_ps_trace_header_data));
    memset(s4b_ps_trace_records, 0, sizeof(s4b_ps_trace_records));
    s4b_flush_callback = flush;
    s4b_barrier_callback = barrier;
    /* 先发布完整清零的记录区，再发布可供读取的日志头。 */
    s4b_flush_barrier(s4b_ps_trace_records, sizeof(s4b_ps_trace_records));
    s4b_ps_trace_header_data.magic = S4B_PS_TRACE_MAGIC;
    s4b_ps_trace_header_data.schema_version = S4B_PS_TRACE_SCHEMA_VERSION;
    s4b_ps_trace_header_data.header_bytes = (uint32_t)sizeof(s4b_ps_trace_header);
    s4b_ps_trace_header_data.record_bytes = (uint32_t)sizeof(s4b_ps_trace_record);
    s4b_ps_trace_header_data.capacity = S4B_PS_TRACE_CAPACITY;
    s4b_ps_trace_header_data.boot_seed_low = (uint32_t)boot_seed;
    s4b_ps_trace_header_data.boot_seed_high = (uint32_t)(boot_seed >> 32U);
    s4b_ps_trace_header_data.session_first = session_first;
    s4b_ps_trace_header_data.session_last = session_last;
    s4b_ps_trace_header_data.next_session_id = session_first;
    s4b_ps_trace_header_data.diagnostic_kind =
        S4B_PS_TRACE_DIAGNOSTIC_KIND_INT8_CHW_NETWORK_POSTPROCESS;
    s4b_ps_trace_header_data.timebase_kind = S4B_PS_TRACE_TIMEBASE_PS_GLOBAL_TIMER_TICKS;
    memcpy(s4b_ps_trace_header_data.derived_source_sha256_words, source_words,
           sizeof(source_words));
    s4b_trace_initialized = 1U;
    s4b_update_header();
    return 1;
}

int s4b_ps_trace_begin_run(uint32_t uart_sequence, uint32_t base_frame,
                           uint32_t repeat_count, uint32_t input_crc32,
                           uint32_t input_length, uint32_t *session_id)
{
    uint32_t reason = S4B_PS_TRACE_REJECT_NONE;
    uint64_t last_frame;
    uint32_t assigned_session;

    if (!s4b_header_is_ready()) return 0;
    if (session_id == NULL || repeat_count == 0U || repeat_count > S4B_PS_TRACE_CAPACITY ||
        input_length != S4B_PS_TRACE_INPUT_BYTES) {
        reason = S4B_PS_TRACE_REJECT_BAD_RUN;
    } else if (s4b_ps_trace_header_data.run_active != 0U) {
        reason = S4B_PS_TRACE_REJECT_RUN_ACTIVE;
    } else if (s4b_ps_trace_header_data.record_count > S4B_PS_TRACE_CAPACITY ||
               repeat_count > S4B_PS_TRACE_CAPACITY -
                                  s4b_ps_trace_header_data.record_count) {
        reason = S4B_PS_TRACE_REJECT_LOG_FULL;
    } else if (s4b_ps_trace_header_data.next_session_id == 0U ||
               s4b_ps_trace_header_data.session_range_exhausted != 0U) {
        reason = S4B_PS_TRACE_REJECT_RANGE_EXHAUSTED;
    } else {
        last_frame = (uint64_t)base_frame + (uint64_t)repeat_count - 1U;
        if (last_frame > UINT32_MAX) reason = S4B_PS_TRACE_REJECT_BAD_RUN;
    }
    if (reason != S4B_PS_TRACE_REJECT_NONE) {
        s4b_note_rejection(uart_sequence, base_frame, reason);
        return 0;
    }

    assigned_session = s4b_ps_trace_header_data.next_session_id;
    s4b_ps_trace_header_data.last_assigned_session_id = assigned_session;
    if (assigned_session == s4b_ps_trace_header_data.session_last) {
        s4b_ps_trace_header_data.next_session_id = 0U;
        s4b_ps_trace_header_data.session_range_exhausted = 1U;
    } else {
        s4b_ps_trace_header_data.next_session_id = assigned_session + 1U;
    }
    s4b_ps_trace_header_data.run_active = 1U;
    s4b_ps_trace_header_data.last_run_status = 0U;
    s4b_ps_trace_header_data.active_session_id = assigned_session;
    s4b_ps_trace_header_data.active_uart_sequence = uart_sequence;
    s4b_ps_trace_header_data.active_base_frame = base_frame;
    s4b_ps_trace_header_data.active_repeat_count = repeat_count;
    s4b_ps_trace_header_data.active_next_repeat_index = 0U;
    s4b_run_input_crc32 = input_crc32;
    s4b_run_input_length = input_length;
    s4b_run_expected_records = repeat_count;
    s4b_run_reserved_records = 0U;
    s4b_run_committed_records = 0U;
    s4b_run_base_record_count = s4b_ps_trace_header_data.record_count;
    s4b_run_input_write_start_ticks = 0U;
    s4b_run_input_write_done_ticks = 0U;
    s4b_run_input_write_seen = 0U;
    *session_id = assigned_session;
    s4b_update_header();
    return 1;
}

void s4b_ps_trace_note_rejection(uint32_t uart_sequence, uint32_t frame_id,
                                 uint32_t reason)
{
    s4b_note_rejection(uart_sequence, frame_id, reason);
}

void s4b_ps_trace_set_input_write_ticks(uint64_t start_ticks,
                                        uint64_t done_ticks)
{
    if (!s4b_header_is_ready() || s4b_ps_trace_header_data.run_active == 0U) return;
    s4b_run_input_write_start_ticks = start_ticks;
    s4b_run_input_write_done_ticks = done_ticks;
    s4b_run_input_write_seen = 1U;
}

s4b_ps_trace_record *s4b_ps_trace_begin_result(uint32_t repeat_index,
                                               uint32_t frame_id)
{
    uint64_t expected_frame;
    s4b_ps_trace_record *record;

    if (!s4b_header_is_ready() || s4b_ps_trace_header_data.run_active == 0U) {
        s4b_note_rejection(0U, frame_id, S4B_PS_TRACE_REJECT_NOT_INITIALIZED);
        return NULL;
    }
    expected_frame = (uint64_t)s4b_ps_trace_header_data.active_base_frame + repeat_index;
    if (repeat_index != s4b_run_reserved_records || repeat_index >= s4b_run_expected_records ||
        expected_frame > UINT32_MAX || frame_id != (uint32_t)expected_frame ||
        s4b_ps_trace_header_data.record_count >= S4B_PS_TRACE_CAPACITY ||
        s4b_run_base_record_count > S4B_PS_TRACE_CAPACITY ||
        s4b_ps_trace_header_data.record_count !=
            s4b_run_base_record_count + s4b_run_committed_records ||
        s4b_run_reserved_records != s4b_run_committed_records) {
        s4b_note_rejection(s4b_ps_trace_header_data.active_uart_sequence, frame_id,
                           S4B_PS_TRACE_REJECT_RESULT_ORDER);
        return NULL;
    }
    if (repeat_index >= UINT32_MAX - 1U) {
        s4b_note_rejection(s4b_ps_trace_header_data.active_uart_sequence, frame_id,
                           S4B_PS_TRACE_REJECT_RESULT_SEQUENCE);
        return NULL;
    }

    record = &s4b_ps_trace_records[s4b_ps_trace_header_data.record_count];
    memset(record, 0, sizeof(*record));
    record->magic = S4B_PS_TRACE_RECORD_MAGIC;
    record->schema_version = S4B_PS_TRACE_SCHEMA_VERSION;
    record->record_bytes = (uint32_t)sizeof(*record);
    record->record_index = s4b_ps_trace_header_data.record_count;
    record->session_id = s4b_ps_trace_header_data.active_session_id;
    record->frame_id = frame_id;
    record->result_seq = repeat_index + 1U;
    record->repeat_index = repeat_index;
    record->uart_sequence = s4b_ps_trace_header_data.active_uart_sequence;
    record->input_crc32 = s4b_run_input_crc32;
    record->input_length = s4b_run_input_length;
    record->input_format = S4B_PS_TRACE_INPUT_FORMAT_INT8_CHW_416;
    record->capture_time_available = 0U;
    record->capture_time_ns = 0U;
    record->unavailable_fields_mask = S4B_PS_TRACE_UNAVAILABLE_CAPTURE_TIME |
                                      S4B_PS_TRACE_UNAPPROVED_INFERENCE_NS;
    s4b_store_ticks(&record->input_write_start_ticks_low,
                    &record->input_write_start_ticks_high,
                    s4b_run_input_write_start_ticks);
    s4b_store_ticks(&record->input_write_done_ticks_low,
                    &record->input_write_done_ticks_high,
                    s4b_run_input_write_done_ticks);
    if (s4b_run_input_write_seen != 0U) {
        record->event_flags |= S4B_PS_TRACE_EVENT_INPUT_WRITE_START |
                               S4B_PS_TRACE_EVENT_INPUT_WRITE_DONE;
    }
    ++s4b_run_reserved_records;
    s4b_ps_trace_header_data.active_next_repeat_index = s4b_run_reserved_records;
    s4b_update_header();
    return record;
}

void s4b_ps_trace_mark_start_command(s4b_ps_trace_record *record,
                                     uint64_t ticks)
{
    if (!s4b_record_is_valid(record)) return;
    s4b_store_ticks(&record->start_command_ticks_low,
                    &record->start_command_ticks_high, ticks);
    record->event_flags |= S4B_PS_TRACE_EVENT_START_COMMAND;
}

void s4b_ps_trace_mark_terminal(s4b_ps_trace_record *record,
                                uint64_t epoch, uint32_t frame_id,
                                uint32_t status, uint32_t error,
                                uint32_t reject, int terminal_observed,
                                int safe,
                                uint64_t observation_ticks)
{
    if (!s4b_record_is_valid(record)) return;
    if (terminal_observed != 0) {
        s4b_store_ticks(&record->terminal_observation_ticks_low,
                        &record->terminal_observation_ticks_high, observation_ticks);
    }
    record->epoch_low = (uint32_t)epoch;
    record->epoch_high = (uint32_t)(epoch >> 32U);
    record->terminal_frame = frame_id;
    record->terminal_status = status;
    record->terminal_error = error;
    record->terminal_reject = reject;
    record->terminal_safe = terminal_observed != 0 && safe != 0 ? 1U : 0U;
    if (terminal_observed != 0) record->event_flags |= S4B_PS_TRACE_EVENT_TERMINAL_OBSERVED;
    if (terminal_observed != 0 && safe != 0) {
        record->event_flags |= S4B_PS_TRACE_EVENT_TERMINAL_SAFE;
    }
}

void s4b_ps_trace_mark_postprocess(s4b_ps_trace_record *record,
                                   uint32_t decode_status,
                                   uint32_t detection_count,
                                   uint32_t raw_candidate_count,
                                   uint64_t ticks)
{
    if (!s4b_record_is_valid(record)) return;
    s4b_store_ticks(&record->postprocess_done_ticks_low,
                    &record->postprocess_done_ticks_high, ticks);
    record->decode_status = decode_status;
    record->detection_count = detection_count;
    record->raw_candidate_count = raw_candidate_count;
    record->event_flags |= S4B_PS_TRACE_EVENT_POSTPROCESS_DONE;
}

void s4b_ps_trace_set_response(s4b_ps_trace_record *record,
                               uint32_t response_status,
                               uint32_t decode_status,
                               uint32_t detection_count,
                               uint32_t raw_candidate_count)
{
    if (!s4b_record_is_valid(record)) return;
    record->response_status = response_status;
    record->decode_status = decode_status;
    record->detection_count = detection_count;
    record->raw_candidate_count = raw_candidate_count;
}

int s4b_ps_trace_commit(s4b_ps_trace_record *record, uint64_t ticks)
{
    if (!s4b_header_is_ready() || s4b_ps_trace_header_data.run_active == 0U ||
        !s4b_record_is_valid(record) || record->record_index !=
            s4b_ps_trace_header_data.record_count ||
        s4b_run_reserved_records != s4b_run_committed_records + 1U) {
        return 0;
    }
    s4b_store_ticks(&record->log_commit_ticks_low,
                    &record->log_commit_ticks_high, ticks);
    record->event_flags |= S4B_PS_TRACE_EVENT_LOG_COMMIT;
    record->record_crc32 = s4b_ps_trace_crc32(
        (const uint8_t *)record, offsetof(s4b_ps_trace_record, record_crc32));
    /* 先使完整记录可见，再发布头部计数，主机不会读到未落盘的记录。 */
    s4b_flush_barrier(record, sizeof(*record));
    ++s4b_ps_trace_header_data.record_count;
    ++s4b_run_committed_records;
    s4b_update_header();
    return 1;
}

void s4b_ps_trace_mark_uart(s4b_ps_trace_record *record,
                            uint64_t start_ticks, uint64_t done_ticks,
                            int sent)
{
    if (!s4b_record_is_valid(record) || record->record_index >=
            s4b_ps_trace_header_data.record_count) return;
    s4b_store_ticks(&record->uart_send_start_ticks_low,
                    &record->uart_send_start_ticks_high, start_ticks);
    s4b_store_ticks(&record->uart_send_done_ticks_low,
                    &record->uart_send_done_ticks_high, done_ticks);
    record->uart_send_status = sent != 0 ? 2U : 1U;
    record->event_flags |= S4B_PS_TRACE_EVENT_UART_START |
                           S4B_PS_TRACE_EVENT_UART_DONE;
    s4b_update_record(record);
}

void s4b_ps_trace_mark_ack(s4b_ps_trace_record *record, int succeeded)
{
    if (!s4b_record_is_valid(record) || record->record_index >=
            s4b_ps_trace_header_data.record_count) return;
    record->ack_state = succeeded != 0 ? S4B_PS_TRACE_ACK_SUCCEEDED :
                                         S4B_PS_TRACE_ACK_FAILED;
    record->event_flags |= S4B_PS_TRACE_EVENT_ACK_DONE;
    s4b_update_record(record);
}

int s4b_ps_trace_end_run(int completed)
{
    int valid;

    if (!s4b_header_is_ready() || s4b_ps_trace_header_data.run_active == 0U) return 0;
    valid = completed == 0 ||
            (s4b_run_reserved_records == s4b_run_expected_records &&
             s4b_run_committed_records == s4b_run_expected_records);
    s4b_ps_trace_header_data.run_active = 0U;
    s4b_ps_trace_header_data.last_run_status = completed != 0 && valid != 0 ? 1U : 2U;
    s4b_update_header();
    return valid;
}
