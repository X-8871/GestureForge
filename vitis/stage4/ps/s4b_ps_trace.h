#ifndef S4B_PS_TRACE_H
#define S4B_PS_TRACE_H

#include <stddef.h>
#include <stdint.h>

#define S4B_PS_TRACE_SCHEMA_VERSION 1U
#define S4B_PS_TRACE_CAPACITY 1000U
#define S4B_PS_TRACE_INPUT_BYTES 519168U
#define S4B_PS_TRACE_SESSION_MAX 0xFFFFFFFEU
#define S4B_PS_TRACE_INPUT_FORMAT_INT8_CHW_416 1U
#define S4B_PS_TRACE_DIAGNOSTIC_KIND_INT8_CHW_NETWORK_POSTPROCESS 1U
#define S4B_PS_TRACE_TIMEBASE_PS_GLOBAL_TIMER_TICKS 1U

#define S4B_PS_TRACE_MAGIC 0x53345054U
#define S4B_PS_TRACE_RECORD_MAGIC 0x53345243U

#define S4B_PS_TRACE_UNAVAILABLE_CAPTURE_TIME (1U << 0)
#define S4B_PS_TRACE_UNAPPROVED_INFERENCE_NS (1U << 1)

#define S4B_PS_TRACE_EVENT_INPUT_WRITE_START (1U << 0)
#define S4B_PS_TRACE_EVENT_INPUT_WRITE_DONE (1U << 1)
#define S4B_PS_TRACE_EVENT_START_COMMAND (1U << 2)
#define S4B_PS_TRACE_EVENT_TERMINAL_OBSERVED (1U << 3)
#define S4B_PS_TRACE_EVENT_TERMINAL_SAFE (1U << 4)
#define S4B_PS_TRACE_EVENT_POSTPROCESS_DONE (1U << 5)
#define S4B_PS_TRACE_EVENT_LOG_COMMIT (1U << 6)
#define S4B_PS_TRACE_EVENT_UART_START (1U << 7)
#define S4B_PS_TRACE_EVENT_UART_DONE (1U << 8)
#define S4B_PS_TRACE_EVENT_ACK_DONE (1U << 9)

enum s4b_ps_trace_reject_reason {
    S4B_PS_TRACE_REJECT_NONE = 0U,
    S4B_PS_TRACE_REJECT_NOT_INITIALIZED = 1U,
    S4B_PS_TRACE_REJECT_BAD_RANGE = 2U,
    S4B_PS_TRACE_REJECT_RANGE_EXHAUSTED = 3U,
    S4B_PS_TRACE_REJECT_LOG_FULL = 4U,
    S4B_PS_TRACE_REJECT_BAD_RUN = 5U,
    S4B_PS_TRACE_REJECT_RUN_ACTIVE = 6U,
    S4B_PS_TRACE_REJECT_RESULT_ORDER = 7U,
    S4B_PS_TRACE_REJECT_RESULT_SEQUENCE = 8U,
    S4B_PS_TRACE_REJECT_BAD_RECORD = 9U
};

enum s4b_ps_trace_ack_state {
    S4B_PS_TRACE_ACK_NOT_ATTEMPTED = 0U,
    S4B_PS_TRACE_ACK_SUCCEEDED = 1U,
    S4B_PS_TRACE_ACK_FAILED = 2U
};

typedef void (*s4b_ps_trace_flush_fn)(void *address, size_t length);
typedef void (*s4b_ps_trace_barrier_fn)(void);

/* 该头部只含32位字段，供主机按小端序解析且可独立校验。 */
typedef struct {
    uint32_t magic;
    uint32_t schema_version;
    uint32_t header_bytes;
    uint32_t record_bytes;
    uint32_t capacity;
    uint32_t record_count;
    uint32_t boot_seed_low;
    uint32_t boot_seed_high;
    uint32_t session_first;
    uint32_t session_last;
    uint32_t next_session_id;
    uint32_t session_range_exhausted;
    uint32_t rejected_request_count;
    uint32_t log_full_reject_count;
    uint32_t last_rejected_sequence;
    uint32_t last_rejected_frame;
    uint32_t last_rejected_reason;
    uint32_t run_active;
    uint32_t last_run_status;
    uint32_t active_session_id;
    uint32_t active_uart_sequence;
    uint32_t active_base_frame;
    uint32_t active_repeat_count;
    uint32_t active_next_repeat_index;
    uint32_t last_assigned_session_id;
    uint32_t diagnostic_kind;
    uint32_t timebase_kind;
    uint32_t derived_source_sha256_words[8];
    uint32_t header_crc32;
} s4b_ps_trace_header;

/* 时间戳拆为两个字，避免32位ABI下结构体填充差异。 */
typedef struct {
    uint32_t magic;
    uint32_t schema_version;
    uint32_t record_bytes;
    uint32_t record_index;
    uint32_t session_id;
    uint32_t frame_id;
    uint32_t result_seq;
    uint32_t repeat_index;
    uint32_t uart_sequence;
    uint32_t input_crc32;
    uint32_t input_length;
    uint32_t input_format;
    uint32_t capture_time_available;
    uint32_t capture_time_ns;
    uint32_t unavailable_fields_mask;
    uint32_t input_write_start_ticks_low;
    uint32_t input_write_start_ticks_high;
    uint32_t input_write_done_ticks_low;
    uint32_t input_write_done_ticks_high;
    uint32_t start_command_ticks_low;
    uint32_t start_command_ticks_high;
    uint32_t terminal_observation_ticks_low;
    uint32_t terminal_observation_ticks_high;
    uint32_t postprocess_done_ticks_low;
    uint32_t postprocess_done_ticks_high;
    uint32_t log_commit_ticks_low;
    uint32_t log_commit_ticks_high;
    uint32_t uart_send_start_ticks_low;
    uint32_t uart_send_start_ticks_high;
    uint32_t uart_send_done_ticks_low;
    uint32_t uart_send_done_ticks_high;
    uint32_t epoch_low;
    uint32_t epoch_high;
    uint32_t terminal_frame;
    uint32_t terminal_status;
    uint32_t terminal_error;
    uint32_t terminal_reject;
    uint32_t terminal_safe;
    uint32_t decode_status;
    uint32_t detection_count;
    uint32_t raw_candidate_count;
    uint32_t response_status;
    uint32_t uart_send_status;
    uint32_t ack_state;
    uint32_t event_flags;
    uint32_t record_crc32;
} s4b_ps_trace_record;

extern s4b_ps_trace_header s4b_ps_trace_header_data;
extern s4b_ps_trace_record s4b_ps_trace_records[S4B_PS_TRACE_CAPACITY];

int s4b_ps_trace_initialize(uint64_t boot_seed, uint32_t session_first,
                            uint32_t session_last, const char *source_sha256_hex,
                            s4b_ps_trace_flush_fn flush,
                            s4b_ps_trace_barrier_fn barrier);
int s4b_ps_trace_begin_run(uint32_t uart_sequence, uint32_t base_frame,
                           uint32_t repeat_count, uint32_t input_crc32,
                           uint32_t input_length, uint32_t *session_id);
void s4b_ps_trace_note_rejection(uint32_t uart_sequence, uint32_t frame_id,
                                 uint32_t reason);
/* 仅记录CPU从staging复制到arena的耗时，不表示cache flush或DDR可见时刻。 */
void s4b_ps_trace_set_input_write_ticks(uint64_t start_ticks,
                                        uint64_t done_ticks);
s4b_ps_trace_record *s4b_ps_trace_begin_result(uint32_t repeat_index,
                                               uint32_t frame_id);
void s4b_ps_trace_mark_start_command(s4b_ps_trace_record *record,
                                     uint64_t ticks);
void s4b_ps_trace_mark_terminal(s4b_ps_trace_record *record,
                                uint64_t epoch, uint32_t frame_id,
                                uint32_t status, uint32_t error,
                                uint32_t reject, int terminal_observed,
                                int safe,
                                uint64_t observation_ticks);
void s4b_ps_trace_mark_postprocess(s4b_ps_trace_record *record,
                                   uint32_t decode_status,
                                   uint32_t detection_count,
                                   uint32_t raw_candidate_count,
                                   uint64_t ticks);
void s4b_ps_trace_set_response(s4b_ps_trace_record *record,
                               uint32_t response_status,
                               uint32_t decode_status,
                               uint32_t detection_count,
                               uint32_t raw_candidate_count);
int s4b_ps_trace_commit(s4b_ps_trace_record *record, uint64_t ticks);
void s4b_ps_trace_mark_uart(s4b_ps_trace_record *record,
                            uint64_t start_ticks, uint64_t done_ticks,
                            int sent);
void s4b_ps_trace_mark_ack(s4b_ps_trace_record *record, int succeeded);
int s4b_ps_trace_end_run(int completed);
uint32_t s4b_ps_trace_crc32(const uint8_t *bytes, size_t length);

#endif
