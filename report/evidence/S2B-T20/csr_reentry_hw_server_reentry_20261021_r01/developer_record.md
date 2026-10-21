# S2B-T20 historical/current hw_server reentry Developer record

- Baseline: `836de11989b76118153624a896c7d6fb31448447` (`D:/FPGA_Competition/w2b`).
- Scope changed: `vitis/run_s2b_model_acceptance.py`, `verification/test_s2b_model_acceptance_runner.py` only.
- Hardware/board: not accessed. No formal board test was run.
- Commit: none, as directed.

## Change summary

`validate_csr_reentry` now permits historical and current `hw_server` PID/creation-time values to differ only when the executable path is identical and COM name/port/PNP identity still matches with a healthy device status. Historical model snapshots continue to be checked against the historical model input config, including its PID and creation time. The fixed historical R02 CSR failure snapshots are also checked against that historical config; its three deployment bindings are still matched to current `app_elf`, `bit`, and `xsa`.

The returned reentry evidence records both identities, whether PID and creation time changed, the matching executable and COM/PNP facts, and explicitly records `NOT_CLAIMED_HISTORICAL_TO_CURRENT_CONTINUITY_UNPROVEN`. Current process/listener/serial identity checks in `ProductionRuntime` were not changed.

Focused regression coverage accepts only PID/creation-time changes, rejects changed executable path and COM/PNP identity, and rejects a corrupted historical R02 process snapshot.

## Verification

- `python.exe -B -m unittest verification.test_s2b_model_acceptance_runner.ModelAcceptanceRunnerTests.test_csr_reentry_requires_bound_complete_model_pass_and_same_hardware` — exit 0; 1 test passed.
- `python.exe -B -m unittest verification.test_s2b_model_acceptance_runner` — exit 0; 43 tests passed.
- `git diff --check -- vitis/run_s2b_model_acceptance.py verification/test_s2b_model_acceptance_runner.py` — exit 0.
- Final source SHA-256: `vitis/run_s2b_model_acceptance.py` `e2ecadf7252146acefde0227e55417cbe713f8282ca2b36dd089c960229ef4e6`; `verification/test_s2b_model_acceptance_runner.py` `0756eda99ac5707e9eaab09a54ed0d27c46bba83ed39af6fd3a1eacaf1b93940`.

No pycache or temporary files were written by the checks (`-B` used). The existing unrelated untracked evidence in the shared worktree was not modified. `.codex/STATE.md` was not modified.
