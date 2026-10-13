"""只读核验真实离线绑定；显式完整输入到齐后独占创建配置，不操作设备。"""

from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[3]
HELPER_SHA = "4f69f848f71acb4b2ff7709a4ab40bbb892f0b205137d434f7a5f302805e1f85"
BUILD = ROOT / "report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"
COLD = ROOT / "report/evidence/S2B-T19/official_reset_basis_20261011_r01/cold_reset_basis_candidate.json"
SERIAL_RECORD = ROOT / "report/evidence/S2B-T19/offline_probe_entry_20261011_r01/offline_result.json"
S15_RUN = ROOT / "report/evidence/S2B-T17/direct_bitgen_20261013T054357Z_ccbeeb35a2053320"


def require(value, message):
    """显式门禁，不依赖可优化掉的断言。"""
    if not value:
        raise RuntimeError(message)


def sha(path):
    """流式读取实际原字节，不复制大产物。"""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def load_probe():
    """项目入口导入安全；这里不调用run、runtime或身份枚举。"""
    source = ROOT / "vitis/run_s2b_visibility_probe.py"
    require(source.is_file(), "项目入口不存在")
    spec = importlib.util.spec_from_file_location("offline_visibility_config_entry", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, data, j):
    """只在本脚本的指定临时目录独占创建UTF-8文件。"""
    require(re.fullmatch(r"[A-Za-z0-9_-]+\.json", name), "输出仅允许简单JSON文件名")
    parent = j.exact_path(HERE, directory=True)
    target = parent / name
    require(not target.exists(), "拒绝覆盖已有输出：" + str(target))
    with target.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(data, output, ensure_ascii=False, indent=2, allow_nan=False)
        output.write("\n")
    return {"path": str(target), "sha256": sha(target)}


def inventory(probe):
    """重新核验构建及源码，静态收集SDK和pyserial纯Python闭包。"""
    j, transport = probe.helpers()
    require(sha(j.exact_path(ROOT / "verification/s2b_board_jtag.py")) == HELPER_SHA, "固定helper版本漂移")

    def bind(path):
        path = j.exact_path(path)
        return {"path": str(path), "sha256": sha(path)}

    def read(path):
        return probe.strict_json(j.exact_path(path).read_text(encoding="utf-8-sig"))

    _, build = transport.verify_build(str(j.exact_path(BUILD)))
    build_files = {}
    for name, row in build["files"].items():
        actual = bind(row["path"])
        require(actual["sha256"] == row["sha256"], "实际BSP/编译原件漂移：" + name)
        build_files[name] = actual
    cache_basis_path = COLD.parent / "bsp_cache_bindings.json"
    cache_basis = read(cache_basis_path)
    for name, row in cache_basis["files"].items():
        require(bind(row["path"])["sha256"] == row["sha256"], "缓存依据原件漂移：" + name)
    require(cache_basis["build_details"] == bind(BUILD), "缓存依据的构建绑定漂移")
    closure = probe.sdk_source_closure()
    sdk_files = {name: bind(path) for name, path in closure.items()}
    historical_serial = read(SERIAL_RECORD)["pyserial_files"]
    candidates = [row for row in historical_serial if Path(row["path"]).name == "__init__.py"
                  and Path(row["path"]).parent.name == "serial"]
    require(len(candidates) == 1, "历史真实pyserial入口不唯一")
    serial_init = j.exact_path(candidates[0]["path"])
    pyserial_files = [bind(path) for path in sorted(serial_init.parent.rglob("*.py"))]
    require({row["path"]: row["sha256"] for row in pyserial_files}
            == {row["path"]: row["sha256"] for row in historical_serial}, "历史真实pyserial闭包漂移")
    require(re.search(r"__version__\s*=\s*['\"]3\.5['\"]", serial_init.read_text(encoding="utf-8-sig")),
            "pyserial源码版本不是3.5")
    names = {
        "csr_source": ROOT / "src/s2b_control_csr.sv",
        "interface": ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
        "tool_source": ROOT / "verification/s2b_board_jtag.py",
        "elf_parser": ROOT / "verification/check_s2b_ps_smoke_layout.py",
        "delivery_parser": ROOT / "verification/check_stage_delivery.py",
        "transport_source": ROOT / "verification/s2b_board_transport.py",
        "entry_source": ROOT / "vitis/run_s2b_visibility_probe.py",
        "platform_checker": ROOT / "verification/check_s2b_inference_platform.py",
    }
    bindings = {key: bind(path) for key, path in names.items()}
    bindings.update(app_elf=bind(build["elf"]["path"]), init_elf=bind(build["initializer_elf"]["path"]),
                    xsa=bind(build["config"]["xsa"]), sdk_init=sdk_files["xsdb"],
                    sdk_target=sdk_files["xsdb.target"], pyserial_init=bind(serial_init))
    postconfig = j.postconfig_basis(j.bound_bytes(bindings["xsa"]))
    cold = read(COLD)
    require(cold["kind"] == "s2b-unified-cold-debug-reset-basis/1.0.0"
            and cold["cold_lifecycle_proven"] is False and cold["hardware_execution"] == "NOT_RUN",
            "官方冷恢复候选语义漂移")
    require("xsdb" not in sys.modules and "serial" not in sys.modules, "离线prepare意外导入SDK或串口")
    result = {
        "schema_version": 1, "status": "OFFLINE_BINDINGS_ONLY_NOT_DEPLOYMENT_APPROVAL",
        "head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True).stdout.decode("ascii").strip(),
        "config_keys": sorted(probe.CONFIG_KEYS), "bindings_without_bit": bindings,
        "build_details": bind(BUILD), "build_status": build["status"], "build_files": build_files,
        "r05_candidate_artifacts_not_approval": {
            "external_original_bit": bind(S15_RUN / "s2b_inference_wrapper_postroute_physopt.bit"),
            "implemented_xsa": bind(S15_RUN / "s2b_inference_implemented.xsa"),
        },
        "cold_basis": bind(COLD), "bsp_cache_basis": bind(cache_basis_path),
        "pyserial_source_record": bind(SERIAL_RECORD), "pyserial_files": pyserial_files,
        "sdk_files": sdk_files, "sdk_file_count": len(sdk_files),
        "sdk_total_bytes": sum(path.stat().st_size for path in closure.values()),
        "postconfig_basis": postconfig,
        "missing_inputs": ["真实独立Reviewer兼容receipt及root固定SHA", "root最终HEAD", "当前UART identity文件",
                           "root-owned server identity文件", "root选定RunId", "两个不同32位seed", "UART观察期限"],
        "hardware_execution": "NOT_RUN", "sdk_runtime_import": "NOT_RUN", "serial_opened": False,
        "limitations": ["不枚举现场进程或设备；identity是否当前有效由root和生产入口实测。",
                        "只核验原件绑定；官方冷恢复文件为候选依据，不能证明实板生命周期。",
                        "不生成独立兼容审批，不声称G2/G3/G4/G5通过。"],
    }
    return j, bind, read, result


def main():
    """inspect仅写离线清单；generate需要总控提供全部真实必填输入。"""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--output-name", default="offline_binding_inventory.json")
    generate = commands.add_parser("generate")
    for name in ("compat-receipt", "compat-receipt-sha256", "source-commit", "uart-identity", "owned-server-identity", "run-id"):
        generate.add_argument("--" + name, required=True)
    for name in ("cpu-seed", "dap-seed"):
        generate.add_argument("--" + name, type=lambda value: int(value, 0), required=True)
    generate.add_argument("--response-timeout-seconds", type=float, required=True)
    generate.add_argument("--output-name", default="visibility_probe_config.json")
    args = parser.parse_args()
    probe = load_probe()
    j, bind, read, data = inventory(probe)
    if args.mode == "inspect":
        print(json.dumps(save(args.output_name, data, j), ensure_ascii=False))
        return
    require(re.fullmatch(r"[0-9a-f]{40}", args.source_commit) and args.source_commit == data["head"], "最终HEAD必须精确一致")
    receipt_binding = bind(args.compat_receipt)
    require(receipt_binding["sha256"] == args.compat_receipt_sha256, "root固定独审SHA不符")
    receipt = read(args.compat_receipt)
    require(set(receipt) == {"schema_version", "kind", "role", "status", "scope", "visibility_parameter", "source_sha256", "artifacts", "checks"}, "兼容receipt字段不符")
    require(type(receipt["schema_version"]) is int and receipt["schema_version"] == 1
            and receipt["kind"] == "s2b-runtime-platform-compatibility/1.0.0"
            and receipt["role"] == "INDEPENDENT_REVIEWER" and receipt["status"] == "PASS"
            and receipt["scope"] == "visibility0_cache_probe_only"
            and type(receipt["visibility_parameter"]) is int and receipt["visibility_parameter"] == 0, "独审批准范围不符")
    require(set(receipt["checks"]) == probe.COMPAT_CHECKS and all(value is True for value in receipt["checks"].values()), "独审兼容事实不全")
    checker = __import__("check_s2b_inference_platform")
    require(receipt["source_sha256"] == checker.check_static(ROOT), "独审源码闭包漂移")
    artifacts = receipt["artifacts"]
    require(set(artifacts) == probe.ARTIFACT_KEYS, "独审产物字段不符")
    for name, row in artifacts.items():
        require(bind(row["path"]) == row, "独审产物原字节漂移：" + name)
    bindings = data["bindings_without_bit"]
    for name, expected in (("compiled_xsa", bindings["xsa"]), ("app_elf", bindings["app_elf"]),
                           ("init_elf", bindings["init_elf"]), ("build_details", data["build_details"])):
        require(artifacts[name] == expected, "独审编译绑定不符：" + name)
    require(artifacts["implemented_xsa"]["path"] != artifacts["compiled_xsa"]["path"], "implemented/compiled XSA不能混同")
    platform = read(artifacts["platform_manifest"]["path"])
    require(type(platform.get("schema_version")) is int and platform["schema_version"] == 1
            and type(platform.get("checks")) is list and platform["checks"]
            and all(row.get("status") == "PASS" or (row.get("status") == "NOT_APPLICABLE"
                    and type(row.get("reason")) is str and row["reason"].strip()) for row in platform["checks"]), "平台清单存在受阻项或schema不符")
    command = [sys.executable, "-B", bindings["delivery_parser"]["path"], "--mode", "evidence", "--manifest", artifacts["platform_manifest"]["path"]]
    checked = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
    require(checked.returncode == 0, "平台证据包装失败：" + checked.stdout.decode("utf-8", errors="replace"))
    server_binding = bind(args.owned_server_identity)
    server = read(args.owned_server_identity)
    native = server.get("native")
    require(server.get("status") == "OWNED_SERVER_READY" and type(native) is dict, "owned server记录未就绪")
    require(type(native.get("ProcessId")) is int and native["ProcessId"] > 0
            and re.fullmatch(r"[0-9]+", str(native.get("CreationTimeFileTimeUtc", ""))), "服务身份格式错误")
    native_path = j.exact_path(native["ExecutablePath"])
    require(native_path.name == "hw_server.exe" and sha(native_path) == server["native_sha256"], "服务原生来源不符")
    uart = read(args.uart_identity)
    require(type(uart) is dict and set(uart) == {"port", "name", "pnp_device_id", "config_manager_error_code"}
            and uart["port"] == "COM4" and type(uart["name"]) is str and uart["name"].endswith("(COM4)")
            and type(uart["pnp_device_id"]) is str and uart["pnp_device_id"] and uart["config_manager_error_code"] == 0,
            "当前UART identity字段不符")
    require(args.cpu_seed != args.dap_seed, "两个seed必须不同")
    j.pattern(args.cpu_seed)
    j.pattern(args.dap_seed)
    require(0 < args.response_timeout_seconds <= 60, "UART观察期限须0..60秒")
    parent = j.exact_path(ROOT / "report/evidence/S2B-T19", directory=True)
    require(re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id), "RunId含非法字符")
    run_dir = parent / args.run_id
    require(not run_dir.exists(), "运行目录必须尚未创建")
    bindings["bit"] = artifacts["bit"]
    config = dict(schema_version=1, source_commit=args.source_commit, run_dir=str(run_dir),
                  build_details=data["build_details"], bindings=bindings, compat_review=receipt_binding,
                  cold_basis=data["cold_basis"], owned_hw_server_identity=server_binding,
                  uart_identity=uart, cpu_seed=args.cpu_seed, dap_seed=args.dap_seed,
                  response_timeout_seconds=args.response_timeout_seconds,
                  pyserial_files=data["pyserial_files"], sdk_files=data["sdk_files"])
    require(set(config) == probe.CONFIG_KEYS, "生成字段与生产入口不一致")
    probe.verify_sdk_files(config)
    probe.verify_serial_files(config)
    require("xsdb" not in sys.modules and "serial" not in sys.modules, "离线prepare意外导入SDK或串口")
    print(json.dumps(save(args.output_name, config, j), ensure_ascii=False))


if __name__ == "__main__":
    main()
