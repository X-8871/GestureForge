"""运行本轮CSR receipt相关回归。"""
import sys
import unittest


modules = (
    "verification.test_s2b_model_acceptance_runner",
    "verification.test_s2b_csr_board_acceptance",
    "verification.test_s2b_csr_busy_observer",
    "verification.test_s2b_board_acceptance",
    "verification.test_s2b_board_jtag",
)
suite = unittest.TestSuite()
loader = unittest.defaultTestLoader
for module in modules:
    suite.addTests(loader.loadTestsFromName(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
