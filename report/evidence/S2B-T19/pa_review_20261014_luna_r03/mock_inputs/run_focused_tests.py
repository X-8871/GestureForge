import json
import tempfile
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[4]
fixture_root = Path(__file__).resolve().parent / "fixtures"
fixture_root.mkdir(exist_ok=True)
import sys
sys.path.insert(0, str(root))

from verification import test_s2b_board_jtag as jtag_tests
from verification import test_s2b_visibility_probe as probe_tests

original_mkdtemp = tempfile.mkdtemp

def isolated_mkdtemp(*args, **kwargs):
    prefix = kwargs.get("prefix", args[1] if len(args) > 1 else "")
    prefix = prefix or ""
    if prefix.startswith(("unit_lifecycle_", "unit_preflight_", "unit_csr_map_")):
        kwargs = dict(kwargs)
        kwargs["dir"] = str(fixture_root)
    return original_mkdtemp(*args, **kwargs)

tempfile.mkdtemp = isolated_mkdtemp

names = (
    "verification.test_s2b_board_jtag.JtagTests.test_pa_pair_refreshes_fpga_current_id_without_selecting_old_pa_id",
    "verification.test_s2b_board_jtag.JtagTests.test_dynamic_selection_rejects_wrong_context_id_name_session_or_current_object",
    "verification.test_s2b_board_jtag.JtagTests.test_exact_pa_topology_and_invalid_variants",
    "verification.test_s2b_visibility_probe.SdkBoundaryTests.test_official_public_targets_reselects_current_id_without_mutating_previous_id",
    "verification.test_s2b_visibility_probe.CsrDebugMapTests.test_cleanup_uses_current_apu_id_after_pa_topology_change",
    "verification.test_s2b_visibility_probe.CsrDebugMapTests.test_cleanup_rejects_drift_extra_design_or_foreign_target_before_unload",
    "verification.test_s2b_visibility_probe.CsrDebugMapTests.test_delayed_unload_stack_order_and_empty_file_means_no_dump",
    "verification.test_s2b_visibility_probe.CsrDebugMapTests.test_unload_exception_still_cancels_and_preserves_original_failure",
    "verification.test_s2b_visibility_probe.CsrDebugMapTests.test_stack_schedule_failure_keeps_public_unload_and_reports_failure",
    "verification.test_s2b_visibility_probe.CsrDebugMapTests.test_stack_cancel_failure_preserves_open_descriptor_and_failure_evidence",
)
loader = unittest.TestLoader()
suite = unittest.TestSuite(loader.loadTestsFromName(name) for name in names)
result = unittest.TextTestRunner(verbosity=2).run(suite)
summary = {
    "scope": "offline_pa_topology_and_owned_unload_diagnostics",
    "test_names": names,
    "run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "successful": result.wasSuccessful(),
    "fixture_root": str(fixture_root),
}
summary_path = Path(__file__).resolve().parent / "focused_test_summary.json"
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if result.wasSuccessful() else 1)
