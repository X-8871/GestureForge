# S2B-T20 deadline DONE_SAFE fix independent review

- Verdict: PASS (G2 code review only).
- Reviewed baseline: `bca323b1750caee783af5552c00769fd584fc1a6` (`D:/FPGA_Competition/w2b`).
- Scope: four task-card files and the cited T18 observation fixture. No source, STATE, hardware, or Git index changes were made by this reviewer.

## Reviewed content

The pre-fix observation rejected bit `0x200` before inspecting the phase. The actual fixture has `PHYS_STATUS=0xE04`: phase 4 (`DONE_SAFE`) with `HEAD_VALID`, so that ordering could never accept the required terminal state. `_normal_start_phase` now first validates the complete CSR snapshot, epoch, and frame; it rejects `HEAD_VALID` only for active phases 1/2/3 and rejects other phase values. Phase 4 then passes to the existing strict stable-terminal check, which still requires status exactly `0xE04`, error code 0, ledger 0, matching epoch/frame, and then writes the matching ACK. The ACK result is still checked with `csr.idle` and retained epoch. This preserves rejection of early active-phase `HEAD_VALID` and fail-closed handling of other phase/error states.

The regression test reads the real fixture at `report/evidence/S2B-T18/r10_interruption_observer_20261020_r02/observation.json`, asserts its diagnostic-only status and `0xE04` terminal status, exercises the full measured-start/ACK path with a deterministic runner, and checks the exact writes. A separate case verifies early `HEAD_VALID` remains rejected. The model-acceptance runner pin is updated to the reviewed deadline-flow source hash and a regression test checks that binding.

## Independent evidence

- Fixture SHA-256: `9b370b09fc943385744f2d4017f6f336c3cfa4a24b5ecd29cbb8cd06a2b3d323`; its status is `OBSERVATIONS_SAVED_NOT_ACCEPTANCE`, its CSR `0x00C` is 3588 (`0xE04`), epoch is 2, frame is 1, error is 0, and ledger field `0x068` is 0. This is diagnostic evidence for the regression, not board acceptance evidence.
- Reviewed source SHA-256: `verification/s2b_csr_deadline_flow.py` `12d266c8fbf095c65ed3ef73dd6b1509b23f093a42a10dbde47da45a9d502f3a`; `verification/test_s2b_csr_deadline_flow.py` `34cfde8458fa1b4c51d4be72a8aad98e4f2a6d1cf307ff69d2fd18ffd46c56e7`; `vitis/run_s2b_model_acceptance.py` `2e324e13292814f19a8aa91bc4a86b75019401176a561cd55e2993c67f830452`; `verification/test_s2b_model_acceptance_runner.py` `36e71677c7c411393e1c4a595c1d18bbda73b0c8d8189ea74ab213fb399f1dd9`.
- Command: `python.exe -B -m unittest verification.test_s2b_csr_deadline_flow verification.test_s2b_model_acceptance_runner` (using the bundled Python executable). Exit code 0; 51 tests ran, all passed.
- Command: `git diff --check bca323b -- verification/s2b_csr_deadline_flow.py verification/test_s2b_csr_deadline_flow.py vitis/run_s2b_model_acceptance.py verification/test_s2b_model_acceptance_runner.py`. Exit code 0.

## Limits

This review establishes the code-path fix and offline regressions only. It does not establish real-board execution, measured deadline performance, or G3/G4 acceptance. The worktree already contained unrelated modified/untracked material, including `.codex/STATE.md`; those files were excluded from review and left untouched. Git emitted only LF-to-CRLF working-copy warnings during diff inspection.
