from pathlib import Path


root = Path(__file__).resolve().parent
stdout = (root / "stdout.txt").read_text(encoding="utf-8", errors="replace")
stderr = (root / "stderr.txt").read_text(encoding="utf-8", errors="replace")
exit_code = (root / "exit_code.txt").read_text(encoding="ascii").strip()
assert "DCP_SHA256_EXPECTED=17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728" in stdout
assert "SERIAL_CLOCK_PIN_COUNT=0; OBJECTS=" in stdout
assert "Exiting Vivado" in stdout
assert stderr == ""
assert exit_code == "1"
print("R01_FAILURE_EVIDENCE_VALID")
