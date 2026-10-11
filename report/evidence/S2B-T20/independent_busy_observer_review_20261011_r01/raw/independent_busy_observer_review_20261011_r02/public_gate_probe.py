"""独立调用公开入口的拒绝路径；不制造visibility或最终PL批准，不替换准入函数。"""
import ast
import copy
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

run = Path(__file__).resolve().parent
root = run.parents[3]
sys.path.insert(0, str(root))
from verification import test_s2b_csr_busy_observer as fixture
from verification import s2b_csr_busy_observer as busy

fixture.TEST_PARENT = run / "public_cases"
fixture.TEST_PARENT.mkdir()
os.environ.pop("S2B_BUSY_FIXTURE_OUTPUT", None)
model, transport = busy.model, busy.transport
# 只重定向证据落盘根；原_new_run和全部准入函数保持执行，Git仍位于同一仓库。
original_csr_root = busy.csr.ROOT
busy.csr.ROOT = run / "public_output_root"
public_parent = busy.csr.ROOT / "report/evidence/S2B-T20"
public_parent.mkdir(parents=True)
preparation_path = root / "report/evidence/S2B-T18/root_corpus_prepare_20261011_r01/preparation.json"
build_path = root / "report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
rows = []


def save(path, value):
    """只写独立目录中的新结果。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


plan = busy.csr.bound_json(model.binding(preparation_path))
model.validate_plan(plan)
_, original_build = transport.verify_build(build_path)
rows.append({"name": "actual_109_plan_and_actual_full_build", "status": "PASS",
             "rows": len(plan["rows"]), "preparation": model.binding(preparation_path), "build": model.binding(build_path)})
for name, transform in (("missing_row", lambda data: data["rows"].pop()),
    ("duplicate_index", lambda data: data["rows"][1].update(index=0)),
    ("changed_input_sha", lambda data: data["rows"][0]["input"].update(sha256="0" * 64)),
    ("wrong_model_sha", lambda data: data["model_manifest"].update(sha256="0" * 64))):
    altered = copy.deepcopy(plan)
    transform(altered)
    try:
        model.validate_plan(altered)
    except Exception as error:
        rows.append({"name": name, "status": "PASS", "rejection": repr(error)})
    else:
        raise AssertionError(name + "被接受")


def run_public(name, mutate, expected):
    """使用真实类型、原生mock和真实文件准入；必须在新RUN发送之前阻断。"""
    case = fixture.BusyObserverTests("test_progress_change_nonempty_gold_success")
    case.setUp()
    try:
        scene_path = case.root / "scene.json"
        save(scene_path, {"schema_version": 1, "kind": "s2b-csr-uart-scene/1.0.0",
                          "expected_snapshot": {str(k): v for k, v in case.initial.items()}})
        config = {"schema_version": 1, "source_commit": head, "bindings": copy.deepcopy(case.controller.bindings),
                  "build_details": str(build_path), "visibility_proof": None, "visibility_review": None,
                  "visibility_review_sha256": None, "final_platform_manifest": None,
                  "final_review": None, "final_review_sha256": None, "scene": model.binding(scene_path)}
        parameters = {"controller": case.controller, "wire": case.wire, "observation_seconds": .1, "poll_seconds": .001}
        mutate(case, config, parameters)
        config_path = case.root / "config.json"
        save(config_path, config)
        config_binding = model.binding(config_path)
        if name == "config_sha_drift":
            config_binding["sha256"] = "0" * 64
        before_tx = case.tx.tell()
        before_sequence = case.wire.last_sequence
        before_operations = list(case.session.operations)
        output = public_parent / name
        try:
            busy.execute_busy_start(parameters["controller"], parameters["wire"], config_binding,
                output, preparation=model.binding(preparation_path),
                observation_seconds=parameters["observation_seconds"], poll_seconds=parameters["poll_seconds"])
        except Exception as error:
            rejection = repr(error)
        else:
            raise AssertionError(name + "公开入口未阻断")
        assert expected in rejection, rejection
        assert case.tx.tell() == before_tx and case.wire.last_sequence == before_sequence
        assert case.session.operations == before_operations
        result = json.loads((output / "busy_result.json").read_text(encoding="utf-8"))
        assert result["status"] == "BLOCKED_BEFORE_TX" and result["hardware_execution"] == "NOT_RUN"
        rows.append({"name": name, "status": "PASS", "rejection": rejection,
                     "new_tx_bytes": case.tx.tell()-before_tx, "new_native_operations": len(case.session.operations)-len(before_operations)})
        print(name + ": PASS", flush=True)
    finally:
        case.tearDown()
        gc.collect()


run_public("fake_controller_dict", lambda c, cfg, p: p.update(controller={"success": True}), "真实T16")
run_public("fake_wire_bool", lambda c, cfg, p: p.update(wire=True), "真实T16")
run_public("config_schema", lambda c, cfg, p: cfg.update(schema_version=True), "schema")
run_public("config_unknown_field", lambda c, cfg, p: cfg.update(success=True), "schema")
run_public("config_stale_head", lambda c, cfg, p: cfg.update(source_commit="6d3fd8567b579a51d4042667d47af7d94f2f5a97"), "基线")
run_public("config_binding_drift", lambda c, cfg, p: cfg["bindings"]["bit"].update(sha256="0"*64), "bindings")
run_public("config_sha_drift", lambda c, cfg, p: None, "SHA")
run_public("actual_build_mock_elf_mismatch", lambda c, cfg, p: None, "实际ELF")
run_public("actual_bound_input_drift", lambda c, cfg, p: (c.root / "sdk_target").write_bytes(b"MOCK_ONLY_CHANGED"), "SHA")
run_public("infinite_observation", lambda c, cfg, p: p.update(observation_seconds=float("inf")), "有限正秒数")
run_public("bool_poll", lambda c, cfg, p: p.update(poll_seconds=True), "有限正秒数")


def bad_build(case, config, parameters):
    """只用明确非批准的输入模拟仅写PASS字符串的伪构建。"""
    path = case.root / "not_a_build.json"
    save(path, {"status": "PASS", "scope": "MOCK_ONLY_NEGATIVE"})
    config["build_details"] = str(path)


def failed_wire(case, config, parameters):
    """让真实接收超时自行锁存失败，不手改failed标志。"""
    try:
        case.wire.receipt(case.wire.sent_requests[2][0])
    except Exception:
        assert case.wire.failed
    else:
        raise AssertionError("真实超时未发生")


run_public("fake_build_success_string", bad_build, "新整网XSA")
run_public("wire_native_timeout_latch", failed_wire, "UART失败")

# 核对公开入口调用次序和既有全门禁的真实函数引用；不把静态检查称为正向准入执行。
tree = ast.parse(Path(busy.__file__).read_text(encoding="utf-8"))
entry = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "execute_busy_start")
calls = sorted((node.lineno, ast.unparse(node.func)) for node in ast.walk(entry) if isinstance(node, ast.Call))
names = [name for _, name in calls]
assert names.index("csr.preflight") < names.index("model.validate_plan") < names.index("_request") < names.index("observer.execute")
admit_tree = ast.parse(Path(busy.csr.__file__).read_text(encoding="utf-8"))
preflight = next(node for node in admit_tree.body if isinstance(node, ast.FunctionDef) and node.name == "preflight")
assert any(isinstance(node, ast.Call) and ast.unparse(node.func) == "model.admit" for node in ast.walk(preflight))
save(run / "public_gate_result.json", {"status": "PASS_NEGATIVE_GATES_AND_STATIC_CHAIN", "count": len(rows), "cases": rows,
     "entry_calls": calls, "production_function_monkeypatches": [],
     "test_output_root_override": {"original": str(original_csr_root), "isolated": str(busy.csr.ROOT),
        "git_head_after_override": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=busy.csr.ROOT, text=True).strip()},
     "created_visibility_or_final_review_receipts": [],
     "public_positive_hardware_admission": "NOT_RUN",
     "reason": "当前仅有visibility0真实构建，未生成实际visibility1/cache/最终bit独审批准；正向全门禁须实板后实际证明。"})
