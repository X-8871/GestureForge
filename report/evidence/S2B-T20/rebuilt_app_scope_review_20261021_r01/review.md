# S2B-T20 rebuilt-app scope independent review

- Verdict: **CHANGES_REQUIRED**.
- Reviewed HEAD: `914b30a42ca39be5635140907efb5405132a4441` (`D:/FPGA_Competition/w2b`).
- Reviewed files and SHA-256:
  - `verification/s2b_rebuilt_app_acceptance.py`: `7a37140e2245aed5c8b52665590b57951ddf77836e7d92717ef58c71fa65bc61`
  - `verification/test_s2b_rebuilt_app_acceptance.py`: `3a864691f2f7354e24e9575cd600b8995be13cc2cd8bc6676336b01a0a2d6ab5`
  - `vitis/run_s2b_rebuilt_app_acceptance.py`: `9643a72e127782ad61d62ba44b63fdfa2c996d5249a480611ed03408410bd168`
- No source, STATE, HEAD, or hardware was changed by this reviewer.

## Blocking finding

The production wrapper and acceptance module disagree on the JTAG controller evidence directory name, making every real run fail before the recovery input checks or board operations:

1. `vitis/run_s2b_rebuilt_app_acceptance.py:155-158` creates `deployment_dir = run_dir / "deployment"` and constructs the production `JtagController` with that directory.
2. `verification/s2b_board_jtag.py:334-337` resolves that exact path into `controller.run`.
3. `verification/s2b_rebuilt_app_acceptance.py:210-215` requires `controller.run.name == run_id`.
4. The wrapper validates `run_id` as `rebuilt_app_acceptance_*`; the controller path basename is always the literal `deployment`. The predicate is therefore impossible. `execute` catches this and records `FAILED_REBUILT_APP_ACCEPTANCE`; it cannot reach the pre-reset snapshot, deployment, UART banner, cache probe, weights, or sample000.

Close condition: make the wrapper's controller evidence directory and the acceptance module's run-directory contract agree, retain unique per-run evidence, and add a wrapper-to-execute regression that uses the real directory layout without accessing hardware.

## Other reviewed requirements

- The suspected `application_source` omission is not present: `verify_recovery_inputs()` returns `"application_source": source_binding` at `verification/s2b_rebuilt_app_acceptance.py:140`, and `validate_config()` reads it at `vitis/run_s2b_rebuilt_app_acceptance.py:102-104`.
- Offline recovery verification pins the reviewed bundle, comparison, build result, prior app/init/XSA/BIT, new ELF, preparation, build details, source, and sample000 golden input. It explicitly sets `old_g0_receipt` to `NOT_REUSED`.
- The acceptance path checks a real production controller and UART, existing binding immutability, pre-reset `csr.idle`, both CPUs stopped, actual `controller.deploy()`, real banner, cache probe, weights at seq3, sample000 at seq4, then CPU stop and stable idle epoch1 with zero ledger. Module cleanup exceptions are saved as failures. These code paths do not mitigate the directory-contract blocker.

## Independent check

- Command: `python.exe -B -m unittest verification.test_s2b_rebuilt_app_acceptance` (bundled Python executable).
- Exit code: 0; 7 tests passed.
- The tests validate offline input pins and predicates but do not instantiate the wrapper's `deployment` directory and pass its controller through `execute`; thus they do not catch the blocker above.
- No board test was run. This is a code review result only, not G3/G4/G5 acceptance.
