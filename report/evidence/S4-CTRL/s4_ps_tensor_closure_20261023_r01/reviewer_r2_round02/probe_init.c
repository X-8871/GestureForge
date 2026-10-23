#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "s4b_ps_trace.h"

static char events[16];
static size_t event_count;
static uint32_t flush_calls;
static uint32_t barrier_calls;
static uint32_t records_flushes;

static void add_event(char value) { assert(event_count < sizeof(events)); events[event_count++] = value; }
static void cache_flush(void *address, size_t length)
{
    size_t index;
    ++flush_calls;
    if (address == (void *)s4b_ps_trace_records) {
        assert(length == sizeof(s4b_ps_trace_records));
        for (index = 0U; index < length; ++index) assert(((const uint8_t *)address)[index] == 0U);
        ++records_flushes;
        add_event('R');
    } else if (address == (void *)&s4b_ps_trace_header_data) {
        assert(length == sizeof(s4b_ps_trace_header_data));
        assert(s4b_ps_trace_header_data.magic == S4B_PS_TRACE_MAGIC);
        assert(s4b_ps_trace_header_data.boot_seed_low == 0x4f543131U);
        add_event('H');
    } else {
        assert(!"unexpected flush region");
    }
}
static void dsb(void) { ++barrier_calls; add_event('B'); }

int main(void)
{
    static const char source[] = "1be7a551e26f61be1327cdb56672b08d86d17d16433ac405ebd263d5f35bf436";
    s4b_ps_trace_header header_before;
    s4b_ps_trace_record *records_before;
    size_t bytes = sizeof(s4b_ps_trace_records);
    memset(&s4b_ps_trace_header_data, 0x5a, sizeof(s4b_ps_trace_header_data));
    memset(s4b_ps_trace_records, 0xa5, sizeof(s4b_ps_trace_records));
    header_before = s4b_ps_trace_header_data;
    records_before = (s4b_ps_trace_record *)malloc(bytes);
    assert(records_before != NULL);
    memcpy(records_before, s4b_ps_trace_records, bytes);
    assert(s4b_ps_trace_initialize(0x5342424f4f543131ULL, 0U, 9U, source,
                                   cache_flush, dsb) == 0);
    assert(memcmp(&header_before, &s4b_ps_trace_header_data, sizeof(header_before)) == 0);
    assert(memcmp(records_before, s4b_ps_trace_records, bytes) == 0);
    assert(flush_calls == 0U && barrier_calls == 0U && event_count == 0U);
    assert(s4b_ps_trace_initialize(0x5342424f4f543131ULL, 5U, 9U, source,
                                   cache_flush, dsb) != 0);
    assert(records_flushes == 1U && flush_calls == 2U && barrier_calls == 2U);
    assert(event_count == 4U && memcmp(events, "RBHB", 4U) == 0);
    header_before = s4b_ps_trace_header_data;
    memcpy(records_before, s4b_ps_trace_records, bytes);
    assert(s4b_ps_trace_initialize(0x5342424f4f543132ULL, 10U, 12U, source,
                                   cache_flush, dsb) == 0);
    assert(memcmp(&header_before, &s4b_ps_trace_header_data, sizeof(header_before)) == 0);
    assert(memcmp(records_before, s4b_ps_trace_records, bytes) == 0);
    assert(flush_calls == 2U && barrier_calls == 2U && event_count == 4U);
    free(records_before);
    puts("PASS init_preserves_on_invalid_and_reinit; flush_order=records,barrier,header,barrier; full_records_zeroed_before_publish");
    return 0;
}