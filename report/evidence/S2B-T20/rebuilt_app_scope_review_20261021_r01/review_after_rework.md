# S2B-T20 rebuilt-app scope re-review

- Verdict: **CHANGES_REQUIRED**; the directory-contract blocker remains in this revision.
- Reviewed HEAD: `914b30a42ca39be5635140907efb5405132a4441`.
- Current SHA-256:
  - `verification/s2b_rebuilt_app_acceptance.py`: `20020faea3df5e5b711bfbe88677dc2dfb4b0d2fb554baa930fb5f9c40e53a55`
  - `verification/test_s2b_rebuilt_app_acceptance.py`: `48358f1bbaf483b2ed38bec1fb0617c82862f19c8fdcfded08bd35342b910fad`
  - `vitis/run_s2b_rebuilt_app_acceptance.py`: `06c711e34e7e547c94bb6dde4fff2c320392223c1f7234396256e4c973e68685`

## Remaining blocker

The new directory helper and wrapper dispatch now agree that `controller.run` is exactly `<T18 RunId>/deployment` (`validate_deployment_directory` in `verification/s2b_rebuilt_app_acceptance.py:155-162`; `_execute_acceptance` in `vitis/run_s2b_rebuilt_app_acceptance.py:104-111`). However, `acceptance.execute` assigns that returned deployment path to `run_dir` at line 220, then line 227 still requires `run_dir.name == run_id`. The returned path's basename is necessarily the literal `deployment`, so the condition always fails before `verify_recovery_inputs()` and before the initial CSR snapshot/deployment. That prevents the selected real-board scope from ever reaching its first acceptance action. The wrapper then records the acceptance as failed.

Close condition: compare the validated parent run directory's basename to `run_id` while preserving the existing check that the controller log directory is its `deployment` child; verify result and output binding locations against that layout with a wrapper-to-execute test.

The other concern from the first review remains closed: `verify_recovery_inputs()` returns `application_source` at line 140, and `validate_config()` reads that result. The new wrapper dispatch test validates the wrapper helper's path comparison, but its mock `execute_fn` does not execute `acceptance.execute`, so it does not cover the remaining basename assertion.

## Independent checks

- `python.exe -B -m unittest verification.test_s2b_rebuilt_app_acceptance` — exit 0; 8 tests passed.
- `python.exe -B vitis/run_s2b_rebuilt_app_acceptance.py --help` — exit 0; help only, no device operation.
- Python `compile()` over the three reviewed UTF-8 sources — exit 0; syntax-only check without writing bytecode.
- Developer-reported `py_compile` — reported exit 0; not independently run because it writes bytecode files.
- No hardware was accessed. Review and tests establish neither actual board execution nor G3/G4/G5 acceptance.
