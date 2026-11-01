"""在平台实现、独立兼容收据和专属服务身份就绪后生成探针配置。"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PREP = Path(__file__).resolve().parent
T15 = ROOT / "report/evidence/S2B-T15/csr_fixed_platform_offline_20261016_r03"
T13 = ROOT / "report/evidence/S2B-T13/platform_csr_fixed_20261016_r03"
T19 = ROOT / "report/evidence/S2B-T19"
TEMPLATE = T19 / "cache_probe_execution_20261015_r01/input_config.json"
UART_IDENTITY = PREP / "uart_identity.json"
POR_CONFIRMATION = T19 / "cold_confirmation_20261016_r01/operator_confirmation.json"
COLD_BASIS = T19 / "official_reset_basis_20261011_r01/cold_reset_basis_candidate.json"
SDK_INIT = Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\__init__.py")
RECEIPT_KEYS = {
    "schema_version", "kind", "role", "status", "scope", "visibility_parameter",
    "source_sha256", "artifacts", "checks",
}
ARTIFACT_KEYS = {
    "compiled_xsa", "implemented_xsa", "init_elf", "app_elf", "bit",
    "build_details", "platform_manifest",
}
COMPAT_CHECKS = {
    "same_ps7_config", "same_ps_init_bytes", "same_bsp_mmu_macros",
    "same_uart_ddr_csr_clocks", "full_model_core_present", "postroute_timing_pass",
}


class ConfigError(RuntimeError):
    """准备条件或绑定不满足时拒绝写入配置。"""


def require(condition: bool, message: str) -> None:
    """以显式检查阻止不完整或漂移的配置。"""
    if not condition:
        raise ConfigError(message)


def sha256(path: Path) -> str:
    """按原始字节计算文件摘要。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    """读取UTF-8 JSON并拒绝重复键。"""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "JSON包含重复字段：" + key)
            result[key] = value
        return result

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConfigError("无法读取有效UTF-8 JSON：" + str(path)) from error
    require(type(value) is dict, "JSON顶层必须为对象：" + str(path))
    return value


def binding(path: Path, *, allow_empty: bool = False) -> dict:
    """验证文件并生成摘要，仅包内空初始化文件允许零字节。"""
    path = path.resolve(strict=True)
    require(path.is_file() and (path.stat().st_size > 0 or allow_empty), "绑定目标不是非空文件：" + str(path))
    return {"path": str(path), "sha256": sha256(path)}


def repo_file(relative: str) -> dict:
    """绑定本工作树内的当前源码文件。"""
    path = (ROOT / relative).resolve(strict=True)
    require(path.is_relative_to(ROOT), "仓库绑定越出当前工作树：" + relative)
    return binding(path)


def import_probe_module():
    """加载纯Python探针定义以复用其SDK闭包算法，不导入SDK或操作硬件。"""
    path = ROOT / "vitis/run_s2b_visibility_probe.py"
    spec = importlib.util.spec_from_file_location("s2b_visibility_probe_config_source", path)
    require(spec is not None and spec.loader is not None, "无法加载探针源码")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sdk_closure(probe) -> dict:
    """重新枚举XSDB/TCF真实源码闭包并逐文件生成新摘要。"""
    require(SDK_INIT.is_file(), "Vitis XSDB入口不存在：" + str(SDK_INIT))
    paths = probe.sdk_source_closure()
    return {name: binding(path, allow_empty=path.name == "__init__.py")
            for name, path in sorted(paths.items())}


def serial_closure(template: dict) -> tuple[dict, list[dict]]:
    """使用已安装pyserial纯Python包路径，重新枚举并哈希完整闭包。"""
    old = template.get("bindings", {}).get("pyserial_init", {})
    require(set(old) == {"path", "sha256"}, "旧配置缺少pyserial入口位置提示")
    package = Path(old["path"]).resolve(strict=True)
    require(package.name == "__init__.py" and package.parent.name == "serial", "pyserial入口目录结构异常")
    files = sorted(package.parent.rglob("*.py"))
    require(files and package in files and len(files) <= 100, "pyserial闭包为空、入口缺失或超出规模")
    rows = [binding(path, allow_empty=path.name == "__init__.py") for path in files]
    require(len({row["path"] for row in rows}) == len(rows), "pyserial文件路径重复")
    return binding(package), rows


def run_git_head() -> str:
    """读取当前实际提交，不沿用历史模板中的提交值。"""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="ascii", timeout=10,
    )
    head = result.stdout.strip()
    require(re.fullmatch(r"[0-9a-f]{40}", head) is not None, "当前HEAD不是完整提交SHA")
    return head


def platform_artifacts(platform_dir: Path) -> tuple[dict, dict, dict]:
    """只接受通过顶层实现、时序、位流和清理门槛的平台Run。"""
    platform_dir = platform_dir.resolve(strict=True)
    require(platform_dir.is_dir() and platform_dir.is_relative_to(ROOT / "report/evidence/S2B-T14"),
            "--platform-run必须指向本仓库S2B-T14目录内的Run")
    result_path = platform_dir / "result.json"
    record_path = platform_dir / "input_record.json"
    require(result_path.is_file() and record_path.is_file(), "平台Run缺少result/input_record")
    result = read_json(result_path)
    record = read_json(record_path)
    require(str(result.get("status", "")).startswith("PASS"), "平台Run尚未PASS：" + str(result.get("status")))
    require(result.get("hardware_execution") == "NOT_RUN", "平台Run硬件状态与离线实现任务不符")
    job = result.get("job", {})
    require(job.get("status") == "PASS" and job.get("exit_code") == 0 and job.get("cleanup_confirmed") is True,
            "平台Run监督器未成功或未确认清理")
    require(result.get("native_log_has_failure") is False, "平台原生日志含失败标记")
    require(result.get("timing_slacks_nonnegative") is True and result.get("xsa_contains_bit") is True,
            "平台Run时序或含位流XSA门槛未通过")
    require(result.get("missing_or_empty_artifacts") == [], "平台Run仍有缺失或空产物")
    require(record.get("source_commit") == result.get("source_commit"), "平台Run输入与结果源码提交不一致")
    artifacts = {}
    for key, name in (("implemented_xsa", "s2b_inference.xsa"), ("bit", "s2b_inference.bit")):
        path = platform_dir / name
        row = binding(path)
        require(result.get("artifact_sha256", {}).get(name) == row["sha256"], "平台产物摘要与结果记录不符：" + name)
        artifacts[key] = row
    return result, record, artifacts


def build_config(platform_dir: Path, compat_path: Path, server_path: Path, run_id: str) -> dict:
    """核对所有当前依赖后独占创建input_config.json。"""
    require(re.fullmatch(r"[A-Za-z0-9_-]+", run_id) is not None, "run-id只允许ASCII字母、数字、下划线、连字符")
    template = read_json(TEMPLATE)
    require(template.get("schema_version") == 1, "历史模板schema不支持")
    probe = import_probe_module()
    head = run_git_head()

    build_path = T15 / "artifacts/build_details.json"
    build = read_json(build_path)
    require(build.get("status") == "PASS_OFFLINE_FULL_XSA_BUILD" and build.get("hardware_execution") == "NOT_RUN",
            "当前T15离线BSP/ELF构建未通过")
    require(isinstance(build.get("source_commit"), str) and re.fullmatch(r"[0-9a-f]{40}", build["source_commit"]),
            "T15构建记录缺少完整源提交绑定")
    source_hashes = build.get("source_sha256")
    require(type(source_hashes) is dict and source_hashes, "T15构建缺少源码摘要闭包")
    for relative, expected in source_hashes.items():
        source = (ROOT / relative).resolve(strict=True)
        require(source.is_relative_to(ROOT) and source.is_file() and sha256(source) == expected,
                "T15构建源码闭包与当前工作树漂移：" + relative)
    build_binding = binding(build_path)
    init_binding = binding(Path(build["initializer_elf"]["path"]))
    app_binding = binding(Path(build["elf"]["path"]))
    compiled_xsa = binding(Path(build["config"]["xsa"]))
    require(build["initializer_elf"]["sha256"] == init_binding["sha256"], "T15 init ELF摘要漂移")
    require(build["elf"]["sha256"] == app_binding["sha256"], "T15 app ELF摘要漂移")
    require(build["config"]["xsa_sha256"] == compiled_xsa["sha256"], "T15编译XSA摘要漂移")

    platform_result, _, platform_rows = platform_artifacts(platform_dir)
    compat_path = compat_path.resolve(strict=True)
    compat = read_json(compat_path)
    require(set(compat) == RECEIPT_KEYS, "兼容收据字段不符合探针schema")
    require(compat.get("schema_version") == 1 and compat.get("kind") == "s2b-runtime-platform-compatibility/1.0.0",
            "兼容收据类型或版本错误")
    require(compat.get("role") == "INDEPENDENT_REVIEWER" and compat.get("status") == "PASS"
            and compat.get("scope") == "visibility0_cache_probe_only" and compat.get("visibility_parameter") == 0,
            "兼容收据尚未批准visibility0限定范围")
    require(type(compat.get("checks")) is dict and set(compat["checks"]) == COMPAT_CHECKS
            and all(value is True for value in compat["checks"].values()), "兼容收据检查项不完整")

    artifact_rows = compat.get("artifacts")
    require(type(artifact_rows) is dict and set(artifact_rows) == ARTIFACT_KEYS, "兼容收据产物绑定字段不全")
    for key, row in artifact_rows.items():
        require(type(row) is dict and set(row) == {"path", "sha256"}, "兼容收据产物绑定格式错误：" + key)
        actual = binding(Path(row["path"]))
        require(actual == row, "兼容收据产物路径或摘要漂移：" + key)
        require(Path(actual["path"]).is_relative_to(ROOT), "兼容收据引用非当前工作树产物：" + key)
    expected_artifacts = {
        "compiled_xsa": compiled_xsa, "implemented_xsa": platform_rows["implemented_xsa"],
        "init_elf": init_binding, "app_elf": app_binding, "bit": platform_rows["bit"],
        "build_details": build_binding,
    }
    for key, expected in expected_artifacts.items():
        require(artifact_rows[key] == expected, "兼容收据没有绑定当前产物：" + key)

    manifest_binding = artifact_rows["platform_manifest"]
    manifest = read_json(Path(manifest_binding["path"]))
    checks = manifest.get("checks")
    require(type(checks) is list and checks and all(
        item.get("status") == "PASS" or
        (item.get("status") == "NOT_APPLICABLE" and isinstance(item.get("reason"), str) and item["reason"].strip())
        for item in checks
    ), "最终平台清单存在未通过或未解释项目")
    checker = ROOT / "verification/check_s2b_inference_platform.py"
    sys.path.insert(0, str(ROOT / "verification"))
    import check_s2b_inference_platform
    require(Path(check_s2b_inference_platform.__file__).resolve() == checker.resolve(), "平台静态检查器导入来源不符")
    source_hashes = check_s2b_inference_platform.check_static(ROOT)
    require(compat.get("source_sha256") == source_hashes, "兼容收据源码闭包与当前工作树不匹配")
    subprocess.run(
        [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"),
         "--mode", "evidence", "--manifest", manifest_binding["path"]],
        cwd=ROOT, check=True, capture_output=True, timeout=30,
    )

    server_path = server_path.resolve(strict=True)
    server = read_json(server_path)
    require(server.get("status") == "OWNED_SERVER_READY" and isinstance(server.get("native"), dict),
            "专属hw_server身份记录尚未就绪")
    require(server.get("hardware_program_execution") == "NOT_RUN", "服务身份记录不得混入编程动作")
    server_binding = binding(server_path)

    uart = read_json(UART_IDENTITY)
    require(uart == {
        "port": "COM4", "name": "Silicon Labs CP210x USB to UART Bridge (COM4)",
        "pnp_device_id": r"USB\VID_10C4&PID_EA60\D02E61162787ED11A536569F9D1CC348",
        "config_manager_error_code": 0,
    }, "现有只读UART身份快照与已确认设备不一致")
    cold = binding(COLD_BASIS)
    confirmation = read_json(POR_CONFIRMATION)
    require(confirmation.get("kind") == "external-por-operator-confirmation/1.0.0"
            and confirmation.get("operator") == "Wong", "缺少Wong的POR人工确认记录")

    serial_binding, serial_files = serial_closure(template)
    sdk_files = sdk_closure(probe)
    sdk_init = binding(SDK_INIT)
    sdk_target = binding(SDK_INIT.parent / "target.py")
    tool = repo_file("verification/s2b_board_jtag.py")
    require(tool["sha256"] == probe.JTAG_SHA, "T16 JTAG工具源码不符合探针固定版本")
    bindings = {
        "init_elf": init_binding,
        "app_elf": app_binding,
        "xsa": compiled_xsa,
        "bit": platform_rows["bit"],
        "csr_source": repo_file("src/s2b_control_csr.sv"),
        "interface": repo_file("docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"),
        "sdk_target": sdk_target,
        "tool_source": tool,
        "elf_parser": repo_file("verification/check_s2b_ps_smoke_layout.py"),
        "delivery_parser": repo_file("verification/check_stage_delivery.py"),
        "transport_source": repo_file("verification/s2b_board_transport.py"),
        "entry_source": repo_file("vitis/run_s2b_visibility_probe.py"),
        "platform_checker": repo_file("verification/check_s2b_inference_platform.py"),
        "sdk_init": sdk_init,
        "pyserial_init": serial_binding,
    }
    output = PREP / "input_config.json"
    run_dir = T19 / run_id
    require(not output.exists() and not run_dir.exists(), "拒绝覆盖已有配置或Run目录")
    result = {
        "schema_version": 1,
        "source_commit": head,
        "run_dir": str(run_dir.resolve()),
        "build_details": build_binding,
        "bindings": bindings,
        "compat_review": binding(compat_path),
        "cold_basis": cold,
        "owned_hw_server_identity": server_binding,
        "uart_identity": uart,
        "cpu_seed": template["cpu_seed"],
        "dap_seed": template["dap_seed"],
        "response_timeout_seconds": template["response_timeout_seconds"],
        "pyserial_files": serial_files,
        "sdk_files": sdk_files,
    }
    require(set(result) == set(probe.CONFIG_KEYS), "生成配置字段与入口schema不匹配")
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return result


def main() -> int:
    """验证依赖并一次性生成配置，不启动服务或触碰硬件。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform-run", required=True, type=Path, help="T14通过的完整实现Run目录")
    parser.add_argument("--compat-review", required=True, type=Path, help="独立Reviewer交付的visibility0兼容收据")
    parser.add_argument("--owned-server-identity", required=True, type=Path, help="本次专属hw_server身份收据")
    parser.add_argument("--run-id", required=True, help="新的T19探针Run目录名")
    args = parser.parse_args()
    result = build_config(args.platform_run, args.compat_review, args.owned_server_identity, args.run_id)
    print(json.dumps({"status": "CONFIG_READY", "path": str(PREP / "input_config.json"),
                      "source_commit": result["source_commit"], "run_dir": result["run_dir"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigError as error:
        print("配置未生成：" + str(error), file=sys.stderr)
        raise SystemExit(2)
