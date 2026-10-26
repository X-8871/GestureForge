from pathlib import Path


root = Path(__file__).resolve().parent
stdout = (root / "stdout.txt").read_text(encoding="utf-8", errors="replace")
stderr = (root / "stderr.txt").read_text(encoding="utf-8", errors="replace")
exit_code = (root / "exit_code.txt").read_text(encoding="ascii").strip()
assert "DCP_SHA256_EXPECTED=17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728" in stdout
assert "BAD_CLOCK=design_1_i/rgb2dvi_0/U0/SerialClk MASTER_CLOCK=axi_dynclk_0_PXL_CLK_O PERIOD=2.000" in stdout
assert "SERIAL_PORT_PIN=design_1_i/rgb2dvi_0/SerialClk CLOCKS_BEFORE=I" in stdout
assert "DELETE_CLOCKS_COMMAND_COUNT=0" in stdout
assert "VIVADO_DELETE_CLOCKS_COMMAND_UNAVAILABLE" in stdout
assert "IN_MEMORY_DIAGNOSTIC_RESULT=PASS" not in stdout
assert "Exiting Vivado" in stdout
assert stderr == ""
assert exit_code == "4"
print("R02_FAILURE_EVIDENCE_VALID")
