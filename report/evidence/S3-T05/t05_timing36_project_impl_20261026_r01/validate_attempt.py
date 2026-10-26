from pathlib import Path
import hashlib


root = Path(__file__).resolve().parent
repo = root.parents[3]
stdout = (root / "stdout.txt").read_text(encoding="utf-8", errors="replace")
stderr = (root / "stderr.txt").read_text(encoding="utf-8", errors="replace")
exit_code = (root / "exit_code.txt").read_text(encoding="ascii").strip()
project_xpr = repo / "tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.xpr"
source_xdc = repo / "tmp/s3r06/t04_sof_fix_20261020_r01/vendor_src/my_ip/rgb2dvi_v1_3/src/rgb2dvi_clocks.xdc"
assert hashlib.sha256(project_xpr.read_bytes()).hexdigest() == "f7606f5b3a53a852b88f3494c35e552aaa3861a7270b71354e8e9a73796c2087"
assert hashlib.sha256(source_xdc.read_bytes()).hexdigest() == "e6ceadc3fcfcf59fe1f5eaf13f8f94d862e9513ad6cd2e850a035c312c8d2002"
assert "PROJECT_RGB2DVI_CLOCK_XDC_COUNT=0" in stdout
assert "PROJECT_HAS_NO_RGB2DVI_CLOCK_XDC" in stdout
assert "SYNTHESIS_STATUS=" not in stdout
assert "IMPLEMENTATION_STATUS=" not in stdout
assert "Exiting Vivado" in stdout
assert stderr == ""
assert exit_code == "1"
print("R01_QUERY_FAILURE_EVIDENCE_VALID")
