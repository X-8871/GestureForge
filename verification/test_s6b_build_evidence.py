"""S6-B builder 摘要与清单 evidence 结果的一致性回归。"""

import unittest

from s6b_build_evidence import (
    evidence_check_manifest_entry,
    format_evidence_summary_rows,
    update_evidence_summary_rows,
)


class S6BEvidenceSummaryRegression(unittest.TestCase):
    """摘要明确区分首次预检与最终收敛检查。"""

    def test_iteration_zero_failure_and_final_pass_are_reported_separately(self):
        first_precheck = {
            "command_text": "python check_stage_delivery.py --mode evidence --iteration 0",
            "exit_code": 2,
        }
        final_run = {
            "command_text": "python check_stage_delivery.py --mode evidence",
            "exit_code": 0,
        }
        final_check = evidence_check_manifest_entry(final_run)
        initial_rows = format_evidence_summary_rows(None, None)
        summary = "\n".join(("| 步骤 | 命令 | 实测退出码 |", "|---|---|---|", *initial_rows, ""))

        updated = update_evidence_summary_rows(summary, first_precheck, final_check)
        rows = [line for line in updated.splitlines() if line.startswith("| 交付检查 evidence ")]

        self.assertEqual(len(rows), 2)
        self.assertIn("首次预检（fixpoint iteration 0）", rows[0])
        self.assertIn("--iteration 0", rows[0])
        self.assertIn("实测 2", rows[0])
        self.assertIn("最终收敛检查", rows[1])
        self.assertIn(final_check["command"], rows[1])
        self.assertIn(f"实测 {final_check['exit_code']}", rows[1])
        self.assertEqual(final_check["status"], "PASS")
        self.assertEqual(final_check["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
