#include "s4_inject_frame.h"
#include <stdio.h>
#include <string.h>

static void flush_cb(void *ctx, uint64_t addr, uint64_t len) {(void)ctx;(void)addr;(void)len;}
static void invalidate_cb(void *ctx, uint64_t addr, uint64_t len) {(void)ctx;(void)addr;(void)len;}
static int barrier_cb(void *ctx) {(void)ctx; return 1;}
static int fail(const char *name, int ok) {printf("{\"check\":\"%s\",\"status\":\"%s\"}\n", name, ok ? "PASS" : "FAIL"); return ok ? 0 : 1;}
int main(void) {
    s4_inject_ring ring;
    s4_inject_ring before;
    s4_inject_validation_report report;
    s4_inject_region bad = {"", UINT64_C(0x10700000), UINT64_C(0x400000)};
    s4_inject_region good = {"injection_frame_rgb", UINT64_C(0x10700000), UINT64_C(0x400000)};
    s4_inject_cache_ops valid = {flush_cb, invalidate_cb, barrier_cb};
    s4_inject_cache_ops invalid = {flush_cb, invalidate_cb, NULL};
    unsigned fails = 0;
    memset(&ring, 0, sizeof(ring));
    s4_inject_status st = s4_inject_ring_init(&ring, 1u, 7u, &bad, 1u, &valid, NULL, &report);
    fails += (unsigned)fail("initial_invalid_region_rejected_and_ring_unchanged", st == S4_INJECT_ERR_REGION_UNKNOWN && report.field != NULL && strcmp(report.field, "regions.name") == 0 && ring.initialized_magic == 0u && ring.session_initialized == 0u && ring.session_id == 0u);
    st = s4_inject_ring_init(&ring, 1u, 7u, &good, 1u, &valid, NULL, &report);
    fails += (unsigned)fail("same_session_retry_after_failed_initialization_succeeds", st == S4_INJECT_OK && ring.initialized_magic == S4_INJECT_RING_INITIALIZED_MAGIC && ring.session_id == 7u);
    memcpy(&before, &ring, sizeof(ring));
    st = s4_inject_ring_init(&ring, 1u, 8u, &bad, 1u, &valid, NULL, &report);
    fails += (unsigned)fail("invalid_idle_reset_preserves_entire_ring", st == S4_INJECT_ERR_REGION_UNKNOWN && memcmp(&ring, &before, sizeof(ring)) == 0 && ring.session_id == 7u && ring.initialized_magic == S4_INJECT_RING_INITIALIZED_MAGIC);
    st = s4_inject_ring_init(&ring, 1u, 8u, &good, 1u, &valid, NULL, &report);
    fails += (unsigned)fail("same_proposed_session_retry_after_invalid_reset_succeeds", st == S4_INJECT_OK && ring.session_id == 8u);
    memcpy(&before, &ring, sizeof(ring));
    st = s4_inject_ring_init(&ring, 0u, 9u, &good, 1u, &valid, NULL, &report);
    fails += (unsigned)fail("invalid_slot_count_preserves_entire_ring", st == S4_INJECT_ERR_NO_FREE_BUFFER && memcmp(&ring, &before, sizeof(ring)) == 0);
    st = s4_inject_ring_init(&ring, 1u, 9u, NULL, 0u, &valid, NULL, &report);
    fails += (unsigned)fail("null_region_table_preserves_entire_ring", st == S4_INJECT_ERR_NULL_ARG && memcmp(&ring, &before, sizeof(ring)) == 0);
    st = s4_inject_ring_init(&ring, 1u, 9u, &good, 1u, &invalid, NULL, &report);
    fails += (unsigned)fail("incomplete_cache_ops_preserves_entire_ring", st == S4_INJECT_ERR_NULL_ARG && memcmp(&ring, &before, sizeof(ring)) == 0);
    printf("{\"status\":\"%s\",\"checks\":7,\"failures\":%u}\n", fails == 0u ? "PASS" : "FAIL", fails);
    return fails == 0u ? 0 : 1;
}
