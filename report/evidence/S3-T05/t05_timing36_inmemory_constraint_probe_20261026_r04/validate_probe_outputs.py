from pathlib import Path
import hashlib
import re


root = Path(__file__).resolve().parent
repo = root.parents[3]
dcp = repo / "tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp"
source_xdc = repo / "report/evidence/S3-T05/t05_dcp_readonly_20261024_r01/v3_constraints_exported.xdc"
candidate_xdc = root / "constraints_without_rgb2dvi_serial_generated_clock.xdc"
stdout = (root / "stdout.txt").read_text(encoding="utf-8", errors="replace")
stderr = (root / "stderr.txt").read_text(encoding="utf-8", errors="replace")
exit_code = (root / "exit_code.txt").read_text(encoding="ascii").strip()
bad_line = (
    b"create_generated_clock -source [get_ports -scoped_to_current_instance PixelClk] "
    b"-multiply_by 5 [get_ports -scoped_to_current_instance SerialClk]"
)

assert hashlib.sha256(dcp.read_bytes()).hexdigest() == "17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728"
source_bytes = source_xdc.read_bytes()
assert hashlib.sha256(source_bytes).hexdigest() == "b6ecb117565c2b8ce3b59757461c0cb590d9d47ea5d1e3fc432713ed7e8cbcd6"
assert source_bytes.count(bad_line) == 1
assert candidate_xdc.read_bytes() == source_bytes.replace(bad_line, b"", 1)

expected_stdout = [
    "METHODOLOGY_BEFORE_TIMING36=1 TIMING30=1 TIMING17=240 TIMING18=1",
    "SERIAL_PORT_PIN=design_1_i/rgb2dvi_0/SerialClk CLOCKS_AFTER=I",
    "BAD_GENERATED_CLOCK_COUNT_AFTER=0",
    "RETAINED_AUTO_CLOCK=I PERIOD=2.000",
    "METHODOLOGY_AFTER_TIMING36=0 TIMING30=0 TIMING17=240 TIMING18=1",
    "IN_MEMORY_DIAGNOSTIC_RESULT=PASS_WARNING_REMOVED_AUTO_CLOCK_I_RETAINED_NO_WRITEBACK",
]
for item in expected_stdout:
    assert item in stdout, item
assert "Exiting Vivado" in stdout
assert stderr == ""
assert exit_code == "0"

def rows(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        match.group(1): int(match.group(2))
        for match in re.finditer(
            r"^\|\s+TIMING-(\d+)\s+\|[^\r\n]*\|\s+(\d+)\s+\|$", text, re.M
        )
    }


assert rows(root / "methodology_before.rpt") == {"17": 240, "36": 1, "9": 1, "18": 1, "30": 1}
assert rows(root / "methodology_after.rpt") == {"17": 240, "9": 1, "18": 1}
clocks = (root / "clocks_after.rpt").read_text(encoding="utf-8", errors="replace")
assert re.search(r"^I\s+2\.000\s+", clocks, re.M)
print("R04_IN_MEMORY_DIAGNOSTIC_EVIDENCE_VALID")
