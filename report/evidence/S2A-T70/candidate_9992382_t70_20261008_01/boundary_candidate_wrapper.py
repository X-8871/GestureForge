import hashlib
import subprocess
import sys
from pathlib import Path

repo = Path(r"D:\FPGA_Competition")
candidate_commit = "999238284157bed77cdb3a37e3e6eea52daeefc4"
expected_tree = "b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67"
engine_sha = "76ca735b14802e26f0a4b016989e13b43cf8bd904587ccea37651c757d089300"
tree = subprocess.check_output(["git", "-C", str(repo), "rev-parse", f"{candidate_commit}^{{tree}}"], text=True).strip()
if tree != expected_tree:
    raise SystemExit(f"candidate tree mismatch: {tree}")
sys.path.insert(0, str(repo / "verification"))
import test_s2a_conv_tile_boundary_rtl as runner
for relative in runner.SOURCES:
    working = (repo / relative).read_bytes()
    baseline = subprocess.check_output(["git", "-C", str(repo), "show", f"{candidate_commit}:{relative}"])
    if hashlib.sha256(working).digest() != hashlib.sha256(baseline).digest():
        raise SystemExit(f"source differs from candidate commit: {relative}")
if hashlib.sha256((repo / "src/s2a_conv_tile_engine.sv").read_bytes()).hexdigest() != engine_sha:
    raise SystemExit("candidate engine SHA mismatch")
runner.TILE_SHA = engine_sha
raise SystemExit(runner.main())
