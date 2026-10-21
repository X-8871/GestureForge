# S2B-T20 deadline evidence-save independent review

- Verdict: **PASS (G2 code review only)**.
- Reviewed HEAD: `3b753853f6d066b6f6a2a6fe23c27644d6aff0e0` (`D:/FPGA_Competition/w2b`).
- Reviewed SHA-256:
  - `verification/s2b_csr_deadline_flow.py`: `972f6b47b0dfde5cbceb53f49c43668dc5740d405f04791efae333bb46d1a55d`
  - `verification/test_s2b_csr_deadline_flow.py`: `e6f0158229aa3f7330f7b6512c548c7b694ceac26f7db78ba1aef4455a1a75fd`
  - `vitis/run_s2b_model_acceptance.py`: `d32bc9adc0ade31827481c3b1c882133a1e6d32ae81ec024e217532974657ad3`
  - `verification/test_s2b_model_acceptance_runner.py`: `0756eda99ac5707e9eaab09a54ed0d27c46bba83ed39af6fd3a1eacaf1b93940` (unchanged; its existing source-pin test covers the current deadline module).

## Review findings

The exclusive-create collision is closed. `_save_epoch_causality` maps the three known stages to distinct immutable paths: `deadline_epoch_causality_after_normal_start.json`, `deadline_epoch_causality_after_core_timeout.json`, and `deadline_epoch_causality_after_drain_limit.json`. The only three execute call sites use those respective stage names, so completion of START no longer precludes saving CORE or DRAIN observations. Unknown stages fail closed through `model.require`; `_save` still uses exclusive creation and UTF-8 serialization.

The new regression uses an actual `TemporaryDirectory`, calls the helper sequentially for all three stages with evolving epoch data, then verifies exactly the three expected files and each saved snapshot's stage-specific values. The source pin in `vitis/run_s2b_model_acceptance.py` matches the final deadline module hash; the existing runner test verifies that pin against the current source bytes.

## Independent verification

- Command: `python.exe -B -m unittest verification.test_s2b_csr_deadline_flow verification.test_s2b_model_acceptance_runner` using the bundled Python runtime.
- Exit code: 0; 52 tests passed.
- Command: `git diff --check -- verification/s2b_csr_deadline_flow.py verification/test_s2b_csr_deadline_flow.py vitis/run_s2b_model_acceptance.py verification/test_s2b_model_acceptance_runner.py`.
- Exit code: 0. Git emitted only LF-to-CRLF working-copy warnings for the two edited deadline-flow files.

No hardware was operated or tested. This review confirms the code fix and offline checks only; it does not establish R11/G3/G4/G5 acceptance. `.codex/STATE.md` was already modified in the shared worktree and was not changed by this reviewer. No source or test files were modified by the review.
