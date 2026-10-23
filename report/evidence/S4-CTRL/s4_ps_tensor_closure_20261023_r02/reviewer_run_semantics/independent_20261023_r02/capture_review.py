import pathlib
import subprocess
import sys

root = pathlib.Path(r"D:\codex-worktrees\w4")
out = pathlib.Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-02A-G2\independent_20261023_r02")
python = r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe"
commands = {
    "unittest": [python, "-B", "-m", "unittest", "-v", "verification.test_s4b_ps_tensor"],
    "probe": [python, "-B", str(out / "probe_s4b_status_semantics.py")],
}
failed = False
for name, command in commands.items():
    result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out / (name + ".stdout.log")).write_bytes(result.stdout)
    (out / (name + ".stderr.log")).write_bytes(result.stderr)
    (out / (name + ".native_exit_code.txt")).write_text(str(result.returncode) + "\n", encoding="ascii")
    print(name, "native_exit_code=" + str(result.returncode))
    if result.returncode:
        failed = True
sys.exit(1 if failed else 0)