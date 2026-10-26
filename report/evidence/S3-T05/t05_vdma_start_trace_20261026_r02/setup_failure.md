# VDMA start trace r02 — failed setup

- Result: BLOCKED_SETUP, no application/BSP copy or compilation was run.
- Cause: the launcher pre-created the evidence directory, then the build script incorrectly required that same directory not to exist.
- The only r02 file is the build script; no scratch output or source was created or changed.
- Recovery: r03 checks only whether its new scratch output path exists, then uses its already-created evidence directory.