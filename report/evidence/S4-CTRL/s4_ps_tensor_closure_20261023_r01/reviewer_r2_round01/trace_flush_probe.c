#include "s4b_ps_trace.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static unsigned int header_flushes;
static unsigned int record_flushes;
static unsigned int full_record_flushes;
static unsigned int barrier_calls;

static void observe_flush(void *address, size_t length)
{
    uintptr_t start = (uintptr_t)address;
    uintptr_t end = start + length;
    uintptr_t header_start = (uintptr_t)&s4b_ps_trace_header_data;
    uintptr_t header_end = header_start + sizeof(s4b_ps_trace_header_data);
    uintptr_t records_start = (uintptr_t)s4b_ps_trace_records;
    uintptr_t records_end = records_start + sizeof(s4b_ps_trace_records);
    if (start <= header_start && end >= header_end) ++header_flushes;
    if (start < records_end && records_start < end) ++record_flushes;
    if (start <= records_start && end >= records_end) ++full_record_flushes;
}

static void observe_barrier(void)
{
    ++barrier_calls;
}

int main(void)
{
    int ok = s4b_ps_trace_initialize(
        UINT64_C(0x5342424f4f543039), 0x53421c00U, 0x53421fe7U,
        "1b7a322629518fa852d21097e7bec34afc0db60f72f1b84480e902f9d73aa514",
        observe_flush, observe_barrier);
    printf("initialize=%d header_flushes=%u record_flushes=%u full_record_flushes=%u barriers=%u record0_cpu_zero=%d\n",
           ok, header_flushes, record_flushes, full_record_flushes, barrier_calls,
           memcmp(&s4b_ps_trace_records[0], &(s4b_ps_trace_record){0}, sizeof(s4b_ps_trace_record)) == 0);
    return ok ? 0 : 1;
}
