# VDMA start trace r01 — failed setup

- Result: BLOCKED_SETUP, no compilation was run.
- Stage: git apply -p1 for v13 failed because the copied source was pristine vendor source, while v13 is a delta on top of v12. The exact error reported display_demo.c:259 context mismatch.
- No source, existing run, hardware, bitstream, or Git index was modified. The partial r01 scratch tree is preserved under tmp/s3r06/t05_vdma_start_trace_20261026_r01/.
- Recovery: r02 applies v12 first and v13 second to a new isolated app directory; no deletion or overwrite of r01.