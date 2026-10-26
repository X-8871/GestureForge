import json
from pathlib import Path


run_dir = Path(__file__).resolve().parent
repo_root = run_dir.parents[3]
stdout = (run_dir / "stdout.txt").read_bytes()
stderr = (run_dir / "stderr.txt").read_bytes()
clocks = (run_dir / "clocks.rpt").read_bytes()
provenance = json.loads((run_dir / "source_provenance.json").read_text(encoding="utf-8"))
prior_dir = repo_root / "report/evidence/S3-T05/t05_dcp_readonly_20261024_r01"
methodology = (prior_dir / "v3_methodology.rpt").read_bytes()
constraints = (prior_dir / "v3_constraints_exported.xdc").read_bytes()

required_stdout = [
    b"DCP_SHA256_EXPECTED=17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728",
    b"PROBE_RESULT=COMPLETE_READ_ONLY",
    b"PIN=design_1_i/axi_dynclk_0/PXL_CLK_O CLOCKS=axi_dynclk_0_PXL_CLK_O NETS=design_1_i/axi_dynclk_0_PXL_CLK_O",
    b"PIN=design_1_i/rgb2dvi_0/PixelClk CLOCKS=axi_dynclk_0_PXL_CLK_O NETS=design_1_i/axi_dynclk_0_PXL_CLK_O",
    b"PIN=design_1_i/rgb2dvi_0/SerialClk CLOCKS=I NETS=design_1_i/axi_dynclk_0_PXL_CLK_5X_O",
    b"INFO: [Common 17-206] Exiting Vivado",
]
for token in required_stdout:
    if token not in stdout:
        raise SystemExit(f"缺少预期 stdout 证据：{token.decode('ascii')}")

if stderr:
    raise SystemExit("stderr 非空")
if b"Period(ns)" not in clocks or b"axi_dynclk_0_PXL_CLK_O" not in clocks:
    raise SystemExit("clocks.rpt 缺少预期 clock 信息")
if b"design_1_i/rgb2dvi_0/U0/SerialClk" not in clocks:
    raise SystemExit("clocks.rpt 缺少 RGB2DVI SerialClk 生成时钟")
if b"TIMING-36#1 Critical Warning" not in methodology:
    raise SystemExit("基线方法报告缺少 TIMING-36#1")
if b"There is no rising/falling edge propagation between master clock axi_dynclk_0_PXL_CLK_O" not in methodology:
    raise SystemExit("基线 TIMING-36 原因文本不匹配")
if b"create_generated_clock -source [get_ports -scoped_to_current_instance PixelClk] -multiply_by 5 [get_ports -scoped_to_current_instance SerialClk]" not in constraints:
    raise SystemExit("导出 XDC 未包含待核对的 PixelClk 到 SerialClk 约束")
if provenance["input"]["sha256"] != "17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728":
    raise SystemExit("provenance DCP 哈希不匹配")

print("EVIDENCE_CONTENT_CHECK=PASS")
