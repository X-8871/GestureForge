"""为本轮visibility0硬件探针绑定已审输入并创建唯一配置。"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(r"D:\FPGA_Competition\w2b")
GENERATOR = ROOT / "report/evidence/S2B-T19/board_probe_configuration_20261016_r03/generate_input_config.py"
PREPARATION = ROOT / "report/evidence/S2B-T19/board_probe_configuration_20261017_r01"
PLATFORM_RUN = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r08"
COMPAT_REVIEW = ROOT / "report/evidence/S2B-T19/current_probe_independent_20261016_r01/runtime_compatibility_receipt.json"
OWNED_SERVER = ROOT / "tmp/2B/S2B-T19/board_probe_20261017_r01/hw_server_identity.json"
RUN_ID = "cache_probe_execution_20261017_r01"

spec = spec_from_file_location("s2b_probe_config_generator", GENERATOR)
if spec is None or spec.loader is None:
    raise RuntimeError("无法载入已核验配置生成器")
generator = module_from_spec(spec)
spec.loader.exec_module(generator)
generator.PREP = PREPARATION
result = generator.build_config(PLATFORM_RUN, COMPAT_REVIEW, OWNED_SERVER, RUN_ID)
print(result["source_commit"])
print(result["run_dir"])
