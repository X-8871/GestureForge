"""真实捕获轻量逻辑fixture；工具批准仅由独立审查给出。"""
from pathlib import Path
import sys
sys.path.insert(0,'C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition\\tmp\\2B\\S2B-T17\\s15_launch_prepare_20261012_r02')
import native_capture as n
import compat_pins as pins
n.HERE=Path(__file__).parent;n.ROOT=Path('C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition')
pins.SOURCE_PRE=Path('C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition\\tmp\\2B\\S2B-T17\\s15_launch_prepare_20261012_r02\\r2_fixtures_r02\\pre');pins.SYNTH_REPORT=Path('C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition\\tmp\\2B\\S2B-T17\\s15_launch_prepare_20261012_r02\\r2_fixtures_r02\\report')
raise SystemExit(n.main())
