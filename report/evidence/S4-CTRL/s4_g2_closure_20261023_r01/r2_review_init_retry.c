#include "s4_inject_frame.h"
#include <stdio.h>
#include <string.h>
static void cb(void *ctx, uint64_t start, uint64_t length) {(void)ctx;(void)start;(void)length;}
static int barrier(void *ctx) {(void)ctx; return 0;}
int main(void) {
    s4_inject_ring ring;
    s4_inject_validation_report report;
    s4_inject_region bad = {"", UINT64_C(0x10700000), UINT64_C(0x400000)};
    s4_inject_region good = {"injection_frame_rgb", UINT64_C(0x10700000), UINT64_C(0x400000)};
    s4_inject_cache_ops cache = {cb, cb, barrier};
    s4_inject_status first, retry, fresh;
    memset(&ring, 0, sizeof(ring));
    first = s4_inject_ring_init(&ring, 1u, 7u, &bad, 1u, &cache, NULL, &report);
    printf("first=%s field=%s magic=0x%08x session=%u regions=%u\n", s4_inject_status_name(first), report.field ? report.field : "(null)", ring.initialized_magic, ring.session_id, ring.region_count);
    retry = s4_inject_ring_init(&ring, 1u, 7u, &good, 1u, &cache, NULL, &report);
    printf("retry_same_session=%s field=%s reason=%s\n", s4_inject_status_name(retry), report.field ? report.field : "(null)", report.reason ? report.reason : "(null)");
    fresh = s4_inject_ring_init(&ring, 1u, 8u, &good, 1u, &cache, NULL, &report);
    printf("retry_new_session=%s field=%s reason=%s\n", s4_inject_status_name(fresh), report.field ? report.field : "(null)", report.reason ? report.reason : "(null)");
    return 0;
}
