import importlib.util
import sys
from pathlib import Path
stage = Path(sys.argv[1]).resolve()
source = stage / "prepare_s2a_t63_dynamic_rom.py"
spec = importlib.util.spec_from_file_location("s2a_t63_stage_preparer", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.RUN_DIR = stage
raise SystemExit(module.main(["--prepare"]))