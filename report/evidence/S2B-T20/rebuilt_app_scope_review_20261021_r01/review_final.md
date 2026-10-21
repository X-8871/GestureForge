# S2B-T20 rebuilt-app scope final re-review

- Verdict: **PASS (G2 code review only)** for the exact source bytes below.
- HEAD remained `914b30a42ca39be5635140907efb5405132a4441`.
- Final reviewed SHA-256:
  - `verification/s2b_rebuilt_app_acceptance.py`: `c153054a79fc59e2b138a3fe66734aa91060b33043c19fea2926ad889e8a396a`
  - `verification/test_s2b_rebuilt_app_acceptance.py`: `dfc2a92604f45f86dc0451ac891d46fdecf8957d9f67377670d44eace9224bba`
  - `vitis/run_s2b_rebuilt_app_acceptance.py`: `06c711e34e7e547c94bb6dde4fff2c320392223c1f7234396256e4c973e68685`

## Closed finding and final review

The previous `run_dir.name == run_id` assertion was removed. The acceptance module now validates that `controller.run` is exactly `<report/evidence/S2B-T18>/<run_id>/deployment`, verifies its parent run directory is a direct child of `S2B-T18`, and checks for a pre-existing result inside the deployment directory. The wrapper creates that same deployment path, verifies it through the shared helper, then passes the same controller object and run ID into `execute`.

The added offline regression creates the exact `run_id/deployment` layout, injects an actual `JtagController` instance initialized without hardware methods and a real `JtagWireSession`, then stops at a mocked `select_and_gate` boundary. It demonstrates that `execute` passes the corrected directory checks and proceeds to the first hardware gate without invoking hardware. The earlier mocked wrapper dispatch test separately checks the wrapper path handoff.

The initially suspected missing `application_source` field is present in `verify_recovery_inputs()` and consumed by `validate_config()`. The reviewed implementation also pins the independent rebuilt ELF and R04 init/XSA/BIT, recovery package/comparison/build records and sample000 preparation, explicitly avoids reusing the previous G0 receipt, checks a stable pre-reset safe IDLE snapshot, and requires actual controller/UART objects. The operational flow performs deployment, banner check, 256-byte cache probe, real seq3 weights, seq4 sample000, dynamic ACK, and verifies stopped CPU plus stable IDLE epoch 1 and zero ledger. Failure and cleanup errors propagate as failed results. These remain code-path findings; no hardware execution was performed.

## Independent verification

- `python.exe -B -m unittest verification.test_s2b_rebuilt_app_acceptance` — exit 0; 9 tests passed on the final SHA set.
- `python.exe -B vitis/run_s2b_rebuilt_app_acceptance.py --help` — exit 0; no config or device operation.
- Python built-in `compile()` over all three final reviewed UTF-8 sources — exit 0, no bytecode output.
- Developer reports `py_compile` exit 0; not repeated here because it writes bytecode.
- No board test; no G3/G4/G5 acceptance claim. The currently modified `.codex/STATE.md` belongs outside this review scope and was not touched.
