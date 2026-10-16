"""隔离执行launcher的纯路径门禁，证明既有checkpoint不会被追加。"""
import ast
from pathlib import Path
import tempfile

source = Path(__file__).with_name("launch_build.py").read_text(encoding="utf-8")
tree = ast.parse(source)
guard = next(node for node in tree.body if isinstance(node, ast.If)
             and isinstance(node.test, ast.Call) and isinstance(node.test.func, ast.Name)
             and node.test.func.id == "any")
code = compile(ast.fix_missing_locations(ast.Module(body=[guard], type_ignores=[])),
               "isolated_launcher_path_guard", "exec")
with tempfile.TemporaryDirectory(prefix="s2b-launch-guard-") as directory:
    root = Path(directory)
    namespace = {"WORK": root / "work", "ARTIFACT": root / "artifacts", "RUN": root}
    exec(code, namespace)
    checkpoint = root / "checkpoints.jsonl"
    checkpoint.write_bytes(b"old-checkpoint\n")
    try:
        exec(code, namespace)
    except RuntimeError:
        pass
    else:
        raise AssertionError("既有checkpoint未阻断新Run")
    assert checkpoint.read_bytes() == b"old-checkpoint\n"
opens = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
         and isinstance(node.func, ast.Attribute) and node.func.attr == "open"
         and isinstance(node.func.value, ast.BinOp)
         and isinstance(node.func.value.right, ast.Constant)
         and node.func.value.right.value == "checkpoints.jsonl"]
assert len(opens) == 1 and isinstance(opens[0].args[0], ast.Constant) and opens[0].args[0].value == "x"
print("PASS missing-path accepted; existing-checkpoint rejected unchanged; single exclusive checkpoint open")
