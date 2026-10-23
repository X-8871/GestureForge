#include "s4b_ps_trace.h"
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

static void flush_noop(void *address, size_t length) { (void)address; (void)length; }
static void barrier_noop(void) { }
int main(void)
{
    uint32_t session = 0U;
    if (!s4b_ps_trace_initialize(UINT64_C(0x5342424f4f543039),
            0x53421c00U, 0x53421fe7U,
            "1b7a322629518fa852d21097e7bec34afc0db60f72f1b84480e902f9d73aa514",
            flush_noop, barrier_noop)) return 1;
    if (!s4b_ps_trace_begin_run(15U, 10U, 1U, 0x12345678U,
            S4B_PS_TRACE_INPUT_BYTES, &session)) return 2;
    printf("boot_seed=%016" PRIx64 " first_session=%08" PRIx32 " frame=%" PRIu32 "\n",
           UINT64_C(0x5342424f4f543039), session, s4b_ps_trace_header_data.active_base_frame);
    return 0;
}
