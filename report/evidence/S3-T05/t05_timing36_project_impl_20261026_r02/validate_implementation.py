from pathlib import Path
import hashlib
import re


root = Path(__file__).resolve().parent
repo = root.parents[3]
tmp = repo / "tmp/3/S3-T05/t05_timing36_project_impl_20261026_r02"
base = repo / "tmp/s3r06/t04_sof_fix_20261020_r01"
source_xdc = base / "vendor_src/my_ip/rgb2dvi_v1_3/src/rgb2dvi_clocks.xdc"
candidate_source_xdc = tmp / "vendor_src/my_ip/rgb2dvi_v1_3/src/rgb2dvi_clocks.xdc"
generated_xdc = tmp / "project/ov5640_single.gen/sources_1/bd/design_1/ip/design_1_rgb2dvi_0_0/src/rgb2dvi_clocks.xdc"
routed_dcp = tmp / "project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp"
bitstream = tmp / "project/ov5640_single.runs/impl_1/design_1_wrapper.bit"
exported_xdc = root / "constraints_routed_exported.xdc"
candidate_evidence_xdc = root / "rgb2dvi_clocks_candidate.xdc"
archived_outputs = root / "outputs"
bad_line = b"create_generated_clock -source [get_ports PixelClk] -multiply_by 5 [get_ports SerialClk]"

assert hashlib.sha256(source_xdc.read_bytes()).hexdigest() == "e6ceadc3fcfcf59fe1f5eaf13f8f94d862e9513ad6cd2e850a035c312c8d2002"
candidate_bytes = candidate_source_xdc.read_bytes()
assert hashlib.sha256(candidate_bytes).hexdigest() == "a8a46ceac24c4ba73d64d9066f6be09d20e02207d20b49963022c06eb088ecd1"
assert generated_xdc.read_bytes() == candidate_bytes
assert candidate_evidence_xdc.read_bytes() == candidate_bytes
assert bad_line not in candidate_bytes
assert hashlib.sha256(routed_dcp.read_bytes()).hexdigest() == "e5f5a429a1eff9e6602f3bca92cefdcca562f1ee39a8e2a0aba0351c58562a84"
assert hashlib.sha256(bitstream.read_bytes()).hexdigest() == "6b23e209effd55a440447c59608f76bbb03cd4f06b3832f0777843cc54a67b01"
assert bitstream.stat().st_size == 1668969
assert (archived_outputs / "vivado_project_after_open.xpr").read_bytes() == (tmp / "project/ov5640_single.xpr").read_bytes()
assert (archived_outputs / "base_design_1.bd").read_bytes() == (base / "project/ov5640_single.srcs/sources_1/bd/design_1/design_1.bd").read_bytes()
assert (archived_outputs / "base_design_1_routed_reference.dcp").read_bytes() == (base / "project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp").read_bytes()
assert (archived_outputs / "rgb2dvi_clocks_generated.xdc").read_bytes() == generated_xdc.read_bytes()
assert (archived_outputs / "design_1_wrapper_routed.dcp").read_bytes() == routed_dcp.read_bytes()
assert (archived_outputs / "design_1_wrapper.bit").read_bytes() == bitstream.read_bytes()
assert hashlib.sha256(exported_xdc.read_bytes()).hexdigest() == "0d1d8a3f161baad7fe8ca2a48d69f1a9029f26f0e42f1258960f774b162e8676"
assert bad_line not in exported_xdc.read_bytes()

stdout = (root / "stdout.txt").read_text(encoding="utf-8", errors="replace")
stderr = (root / "stderr.txt").read_text(encoding="utf-8", errors="replace")
stdout_bitgen = (root / "stdout_bitgen.txt").read_text(encoding="utf-8", errors="replace")
stderr_bitgen = (root / "stderr_bitgen.txt").read_text(encoding="utf-8", errors="replace")
assert (root / "exit_code.txt").read_text(encoding="ascii").strip() == "0"
assert (root / "bitgen_exit_code.txt").read_text(encoding="ascii").strip() == "0"
assert "SYNTHESIS_STATUS=synth_design Complete!" in stdout
assert "SYNTHESIS_PROGRESS=100%" in stdout
assert "IMPLEMENTATION_STATUS=route_design Complete!" in stdout
assert "IMPLEMENTATION_PROGRESS=100%" in stdout
assert "SERIAL_PORT_PIN=design_1_i/rgb2dvi_0/SerialClk CLOCKS=I" in stdout
assert "SERIAL_AUTO_CLOCK=I PERIOD=2.000" in stdout
assert "METHODOLOGY_TIMING36=0 TIMING30=0 TIMING17=240 TIMING18=1 TIMING9=1" in stdout
assert "PROJECT_IMPL_DIAGNOSTIC_RESULT=PASS_FULL_SYNTH_IMPL_ROUTE_CAPTURED_NO_BOARD_ACCESS" in stdout
assert "IMPLEMENTATION_STATUS_AFTER_BITGEN=write_bitstream Complete!" in stdout_bitgen
assert "IMPLEMENTATION_PROGRESS_AFTER_BITGEN=100%" in stdout_bitgen
assert "BITSTREAM_GENERATION_RESULT=PASS_NOT_PROGRAMMED" in stdout_bitgen
assert "Exiting Vivado" in stdout and "Exiting Vivado" in stdout_bitgen
assert stderr == "" and stderr_bitgen == ""

def timing_rows(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        match.group(1): int(match.group(2))
        for match in re.finditer(r"^\|\s+TIMING-(\d+)\s+\|[^\r\n]*\|\s+(\d+)\s+\|$", text, re.M)
    }


rows = timing_rows(root / "methodology_routed.rpt")
assert rows.get("17") == 240
assert rows.get("18") == 1
assert rows.get("9") == 1
assert "36" not in rows and "30" not in rows

timing = (root / "timing_summary_routed.rpt").read_text(encoding="utf-8", errors="replace")
assert "1.055        0.000                      0                21479        0.059        0.000                      0                21344" in timing
for condition in ("no_clock (240)", "unconstrained_internal_endpoints (520)", "no_input_delay (9)", "no_output_delay (5)"):
    assert condition in timing, condition
drc = (root / "drc_routed.rpt").read_text(encoding="utf-8", errors="replace")
assert "Checks found: 8" in drc
print("R02_PROJECT_IMPLEMENTATION_EVIDENCE_VALID")
