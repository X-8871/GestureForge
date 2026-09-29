import hashlib
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parent
runner = root.parents[3] / "verification" / "test_s2a_conv_layer35_row21_all_channels_rtl.py"
spec = importlib.util.spec_from_file_location("t57_r8_batch_gate", runner)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
unit = root / "_r8_batch_signature_gate_unit"
if unit.exists():
    raise SystemExit("refusing to reuse synthetic batch fixture")
unit.mkdir()
module.RUN_ROOT = unit
custom = unit / "xsim_run.tcl"
custom.write_text('puts "R8_STATIC_ONLY"\nrun all\nquit\n', encoding="utf-8")
module.XSIM_CUSTOM_TCL = custom
snapshot = f"{module.TOP}_behav"
key = f"Behavioral:{module.SIMSET}:Functional:{module.TOP}"
xelab = f"--debug off --snapshot {snapshot} xil_defaultlib.{module.TOP}"

def make_xsim(path_token=None, wdb=False):
    token = custom.resolve().as_posix() if path_token is None else path_token
    command = f"{snapshot} -key {{{key}}} -tclbatch {{{token}}} -log simulate.log"
    if wdb:
        command += " -wdb sim.wdb"
    return command

def write_snapshots(xsim_command):
    stage = {}
    for phase in ("before_compile", "after_compile", "after_elaborate"):
        elab_name = f"elaborate.{phase}.bat"
        sim_name = f"simulate.{phase}.bat"
        (unit / elab_name).write_text(f"call xelab {xelab}\n", encoding="utf-8")
        (unit / sim_name).write_text(f"call xsim {xsim_command}\n", encoding="utf-8")
        stage[f"elaborate_{phase}_batch_path"] = str(unit / elab_name)
        stage[f"simulate_{phase}_batch_path"] = str(unit / sim_name)
    stage["elaborate_batch_path"] = str(unit / "elaborate.after_elaborate.bat")
    stage["simulate_batch_path"] = str(unit / "simulate.after_elaborate.bat")
    stage["elaborate_command_signature"] = xelab
    stage["simulate_command_signature"] = xsim_command
    return stage

results = []
valid = write_snapshots(make_xsim())
parsed = module._verify_batch_script_snapshots(valid)
if len(parsed) != 6:
    raise SystemExit("positive fixture did not bind all six snapshots")
results.append({"case": "valid_r8_forward_slash_signature", "passed": True, "snapshots": len(parsed)})

changed = make_xsim() + " -nosort"
changed_stage = write_snapshots(make_xsim())
(unit / "simulate.after_elaborate.bat").write_text(f"call xsim {changed}\n", encoding="utf-8")
try:
    module._verify_batch_script_snapshots(changed_stage)
except module.T57Error:
    results.append({"case": "changed_signature_rejected", "passed": True})
else:
    raise SystemExit("changed signature unexpectedly accepted")

backslash_token = str(custom.resolve())
backslash_stage = write_snapshots(make_xsim(backslash_token))
try:
    module._verify_batch_script_snapshots(backslash_stage)
except module.T57Error:
    results.append({"case": "backslash_tclbatch_rejected", "passed": True})
else:
    raise SystemExit("backslash -tclbatch unexpectedly accepted")

wdb_stage = write_snapshots(make_xsim(wdb=True))
try:
    module._verify_batch_script_snapshots(wdb_stage)
except module.T57Error:
    results.append({"case": "wdb_signature_rejected", "passed": True})
else:
    raise SystemExit("-wdb signature unexpectedly accepted")

duplicate_stage = write_snapshots(make_xsim())
with (unit / "simulate.after_elaborate.bat").open("a", encoding="utf-8") as stream:
    stream.write(f"call xsim {make_xsim()}\n")
try:
    module._verify_batch_script_snapshots(duplicate_stage)
except module.T57Error:
    results.append({"case": "duplicate_xsim_command_rejected", "passed": True})
else:
    raise SystemExit("duplicate xsim command unexpectedly accepted")

summary = {
    "schema": "GestureForge-S2A-T57-R8-batch-signature-gate-test-v1",
    "status": "PASS_STATIC_SYNTHETIC_FIXTURES",
    "simulator_started": False,
    "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
    "cases": results,
}
result_path = unit / "r8_batch_signature_gate_results.json"
with result_path.open("xb") as stream:
    stream.write((json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
print(f"R8_BATCH_SIGNATURE_GATE_TEST=PASS cases={len(results)} snapshots=6")
