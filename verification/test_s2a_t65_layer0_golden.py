"""核验并导出 T65 sample0 layer0 首个卷积输出点的真实数据夹具。"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_DIR = ROOT / "report" / "evidence" / "S2A-T65" / "run01"
FIXED_SAMPLES_PATH = ROOT / "report" / "evidence" / "S2A-T01" / "fixed_test_samples.json"
MODEL_MANIFEST_PATH = ROOT / "report" / "evidence" / "S2A-T01" / "tiny416_model_manifest.json"
T23_PATH = ROOT / "report" / "evidence" / "S2A-T23" / "conv_requant_parameter_table.json"
T25_INDEX_PATH = ROOT / "report" / "evidence" / "S2A-T25" / "cpu_layer_golden_index.json"
DESCRIPTOR_PATH = ROOT / "src" / "s2a_network_descriptor_pkg.sv"
BACKEND_PATH = ROOT / "src" / "s2a_network_backend.sv"
GEOMETRY_PATH = ROOT / "src" / "int8_conv_tap_geometry.sv"
WEIGHT_ADDRESS_PATH = ROOT / "src" / "int8_conv_weight_address.sv"
D2_NUMERIC_PATH = ROOT / "verification" / "s1_t02_d2_numeric_reference.py"
MODEL_DELIVERY_PATH = ROOT / "verification" / "s2a_model_delivery.py"
BENCH_PATH = ROOT / "sim" / "tb_s2a_t65_layer0_golden.sv"
RUNNER_PATH = ROOT / "verification" / "run_s2a_t65_layer0_golden.ps1"
COMPILED_SV_FILES = (
    "src/s2a_network_descriptor_pkg.sv",
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/int8_maxpool_geometry.sv",
    "src/int8_maxpool_window.sv",
    "src/int8_route_query.sv",
    "src/int8_upsample_query.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_maxpool_engine.sv",
    "src/s2a_route_engine.sv",
    "src/s2a_upsample_engine.sv",
    "src/s2a_control_csr.sv",
    "src/s2a_network_backend.sv",
    "sim/tb_s2a_t65_layer0_golden.sv",
)

PINNED_SHA256 = {
    "report/evidence/S2A-T01/fixed_test_samples.json": "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed",
    "report/evidence/S2A-T01/tiny416_model_manifest.json": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "report/evidence/S2A-T23/conv_requant_parameter_table.json": "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1",
    "src/int8_conv_tap_geometry.sv": "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "src/int8_conv_weight_address.sv": "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "src/int8_mac_accumulator.sv": "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
    "src/int8_maxpool_geometry.sv": "0e1d398a479990dc2e614fda734fac14ddf8217c1197b1a52f9be0efe3b1905a",
    "src/int8_maxpool_window.sv": "0ea5865e939a691ccb7fea4602fd31211c816d13424ac7c77c89713ff5a15653",
    "src/int8_route_query.sv": "2f13e90858f6e665cf05444aac8e4db396b09f798acedd51e37bfd2c56f1dd64",
    "src/int8_upsample_query.sv": "9212f70c31fab6c6e5a30551c5d1fd7b6eeeafa4c1f2cbd20fe157015faa370c",
    "src/s2a_conv_engine.sv": "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "src/s2a_maxpool_engine.sv": "3dbb1fd41fbe773debade2629e8e7565554d14051a906466042906bb925de7b7",
    "src/s2a_route_engine.sv": "4748df19474e6b90e11bb760854311da92ba8d19a5b1d4b12e3d7b2b7968fe44",
    "src/s2a_upsample_engine.sv": "2c08bbc9c1d85e94de448f613617a5d584fe5682d0c4858d550bf377302e195b",
    "src/s2a_control_csr.sv": "97fc62dd1967ea9486db1c6e48134283d62005805a0ca5ef44d6ea70ab2fc9d2",
    "src/s2a_network_backend.sv": "38f0563baccf091024ca93b5a488a869a69f6e61b837695564dade653f465e26",
    "src/s2a_network_descriptor_pkg.sv": "295df973188878388ff8ef48c50dfacb1fe3d23a169369d737d1babe0507dc14",
    "sim/tb_s2a_t65_layer0_golden.sv": "3d7c9769356977124dff920c72547a3f4e6d35a0d828cb30f0def8a03f184772",
    "verification/s1_t02_d2_numeric_reference.py": "ea48281fa1c1ba14006f6131ff377c7e4523da8c7e4977b0949d454a7c9ded90",
    "verification/s2a_model_delivery.py": "4831fff0e8ebb189ac9767ae423ad8d5268fc5bee5e333cc2a132112ccfdaab8",
    "verification/run_s2a_t65_layer0_golden.ps1": "d48be24e1514642f7a9349f1a6b91f40bcafb040905e91c0116b2ae64129d3d6",
}
EXPECTED_OFFICIAL_MANIFEST_SHA256 = "fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74"
EXPECTED_IMAGE_SHA256 = "6dbd72693bc6ad2af6121ffe95e2ee5e9c14597a4c4d16a6db8cdf07d8e43b0e"
EXPECTED_GF8_SHA256 = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
EXPECTED_INPUT_SHA256 = "da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e"
EXPECTED_LAYER0_SHA256 = "220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8"
EXPECTED_T25_SHARD_SHA256 = "49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e"
EXPECTED_BACKEND_BASELINE = "ec686741e0553ebc4a8701129e381526e0b06974"
INPUT_BYTES = 519_168
INPUT_HEIGHT = 416
INPUT_WIDTH = 416
INPUT_CHANNELS = 3
OUTPUT_ADDRESS = 0x0100_0000
INPUT_BASE_ADDRESS = 0x0000_0000
WEIGHT_BASE_ADDRESS = 0x0010_0000
GOLDEN_FIRST_BYTE_INDEX = 0


class FixtureError(RuntimeError):
    """表示冻结来源、数据映射或输出夹具不符合要求。"""


def require(condition: bool, message: str) -> None:
    """不满足前置条件时以中文停止，避免生成不完整夹具。"""
    if not condition:
        raise FixtureError(message)


def sha256_bytes(payload: bytes) -> str:
    """计算字节流 SHA-256。"""
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    """以分块方式计算文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path, description: str) -> dict[str, Any]:
    """读取 UTF-8 JSON 对象并拒绝非对象根节点。"""
    require(path.is_file(), f"{description} 精确路径不存在或不是文件：{path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{description} 根节点不是 JSON 对象：{path}")
    return value


def check_pinned_files() -> dict[str, str]:
    """核对任务卡固定的仓库源码与规格版本。"""
    hashes: dict[str, str] = {}
    for relative, expected in PINNED_SHA256.items():
        path = ROOT / Path(relative)
        require(path.is_file(), f"冻结绑定文件缺失：{path}")
        actual = sha256_file(path)
        require(actual == expected, f"冻结绑定 SHA 不匹配：{path}，expected={expected} actual={actual}")
        hashes[relative] = actual
    return hashes


def check_compiled_source_bindings() -> None:
    """确认 runner 的 xvlog 源清单与逐文件 SHA 绑定完全一致。"""
    require(RUNNER_PATH.is_file(), f"T65 runner 缺失：{RUNNER_PATH}")
    runner = RUNNER_PATH.read_text(encoding="utf-8")
    match = re.search(r"\$sourcePaths\s*=\s*@\((.*?)^\s*\)", runner, re.DOTALL | re.MULTILINE)
    require(match is not None, "无法解析 runner 的 xvlog sourcePaths 清单")
    actual_paths = tuple(re.findall(r"'([^']+\.sv)'", match.group(1)))
    expected_paths = tuple(str(ROOT / Path(relative)) for relative in COMPILED_SV_FILES)
    require(actual_paths == expected_paths,
            f"runner xvlog 清单与冻结顺序/路径不同：actual={actual_paths} expected={expected_paths}")
    missing_bindings = set(COMPILED_SV_FILES) - set(PINNED_SHA256)
    require(not missing_bindings, f"xvlog 输入缺少 SHA-256 固定绑定：{sorted(missing_bindings)}")
    require(len(actual_paths) == len(set(actual_paths)), "runner xvlog 清单存在重复源文件")


def parse_sv_u32_array(package: str, name: str) -> list[int]:
    """从冻结 SystemVerilog 包解析 38 项十六进制数组。"""
    match = re.search(
        rf"\b{name}\s*\[0:37\]\s*=\s*'\{{(.*?)\n\s*\}};",
        package,
        re.DOTALL,
    )
    require(match is not None, f"无法从 descriptor package 读取数组：{name}")
    tokens = re.findall(r"\b\d+'[hH]([0-9A-Fa-f_]+)", match.group(1))
    require(len(tokens) == 38, f"descriptor package 数组 {name} 应为 38 项，实际 {len(tokens)}")
    return [int(token.replace("_", ""), 16) for token in tokens]


def signed_int8(value: int) -> int:
    """按补码解释一个字节。"""
    return value - 256 if value >= 128 else value


def write_new_or_verify(path: Path, payload: bytes) -> None:
    """只创建新夹具；同名文件存在时仅接受内容完全一致的复用。"""
    if path.exists():
        require(path.is_file(), f"夹具目标不是普通文件：{path}")
        require(path.read_bytes() == payload, f"拒绝覆盖内容不同的既有夹具：{path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def parse_expected_tap_byte_function(bench: str, function_name: str) -> dict[int, int]:
    """从 bench 常量函数读取 reduction index 到冻结字节的映射。"""
    function_match = re.search(
        rf"function\s+automatic\s+logic\s+\[7:0\]\s+{re.escape(function_name)}\s*"
        r"\(\s*input\s+integer\s+reduction_index\s*\)\s*;(.*?)endfunction",
        bench,
        re.DOTALL | re.IGNORECASE,
    )
    require(function_match is not None, f"bench 缺少常量函数：{function_name}")
    case_match = re.search(r"case\s*\(\s*reduction_index\s*\)(.*?)endcase", function_match.group(1), re.DOTALL)
    require(case_match is not None, f"bench 常量函数缺少 reduction_index case：{function_name}")
    body = case_match.group(1)
    require(re.search(rf"default\s*:\s*{re.escape(function_name)}\s*=\s*8'[hH]xx\s*;", body, re.IGNORECASE) is not None,
            f"bench 常量函数对非有效 tap 必须返回未知值：{function_name}")
    parsed: dict[int, int] = {}
    assignment_pattern = re.compile(
        rf"([0-9]+(?:\s*,\s*[0-9]+)*)\s*:\s*{re.escape(function_name)}\s*=\s*8'[hH]([0-9a-f]{{2}})\s*;",
        re.IGNORECASE,
    )
    for index_list, byte_hex in assignment_pattern.findall(body):
        for index_text in index_list.split(","):
            index = int(index_text.strip())
            require(index not in parsed, f"bench 常量函数重复 reduction index：{function_name}[{index}]")
            parsed[index] = int(byte_hex, 16)
    require(len(parsed) == 12, f"bench 常量函数必须覆盖 12 个有效 tap：{function_name}，实际 {len(parsed)}")
    return parsed


def require_sample0_tap_bytes_match(
    input_payload: bytes | bytearray,
    weight_payload: bytes | bytearray,
    input_taps: list[dict[str, int]],
    expected_input_bytes: dict[int, int],
    expected_weight_bytes: dict[int, int],
) -> None:
    """逐项核对 fixture 的选中输入/权重字节与 bench 独立常量。"""
    for tap in input_taps:
        reduction_index = tap["reduction_index"]
        input_offset = tap["input_address"] - INPUT_BASE_ADDRESS
        require(0 <= input_offset < len(input_payload), f"sample0 tap 输入地址越界：{tap}")
        require(reduction_index in expected_input_bytes and reduction_index in expected_weight_bytes,
                f"bench 常量未覆盖有效 reduction index：{reduction_index}")
        require(input_payload[input_offset] == expected_input_bytes[reduction_index],
                f"sample0 输入 tap fixture 与独立常量不符：reduction={reduction_index} address={input_offset}")
        require(reduction_index < len(weight_payload), f"layer0 权重 tap 索引越界：{tap}")
        require(weight_payload[reduction_index] == expected_weight_bytes[reduction_index],
                f"layer0 权重 tap fixture 与独立常量不符：reduction={reduction_index}")


def check_tap_corruption_rejection(
    input_raw: bytes,
    weight_raw: bytes,
    input_taps: list[dict[str, int]],
    expected_input_bytes: dict[int, int],
    expected_weight_bytes: dict[int, int],
) -> None:
    """离线证明全零和每个选中字节变异都会触发 fixture 拒绝。"""
    def expect_rejected(input_payload: bytes | bytearray, weight_payload: bytes | bytearray, label: str) -> None:
        try:
            require_sample0_tap_bytes_match(
                input_payload, weight_payload, input_taps, expected_input_bytes, expected_weight_bytes
            )
        except FixtureError:
            return
        raise FixtureError(f"离线损坏回归失败，未拒绝：{label}")

    expect_rejected(bytes(len(input_raw)), weight_raw, "全零 sample0 输入")
    expect_rejected(input_raw, bytes(len(weight_raw)), "全零 layer0 权重")
    for tap in input_taps:
        reduction_index = tap["reduction_index"]
        input_offset = tap["input_address"] - INPUT_BASE_ADDRESS
        changed_input = bytearray(input_raw)
        changed_input[input_offset] ^= 1
        expect_rejected(changed_input, weight_raw, f"输入 tap reduction={reduction_index} 单字节变异")
        changed_weights = bytearray(weight_raw)
        changed_weights[reduction_index] ^= 1
        expect_rejected(input_raw, changed_weights, f"权重 tap reduction={reduction_index} 单字节变异")


def check_bench_and_runner(
    input_taps: list[dict[str, int]],
    input_raw: bytes,
    weight_raw: bytes,
    golden_byte: int,
) -> dict[str, str]:
    """检查 bench 常量、真实后端和 runner 编译源均绑定冻结输入。"""
    require(BENCH_PATH.is_file(), f"T65 SystemVerilog bench 缺失：{BENCH_PATH}")
    require(RUNNER_PATH.is_file(), f"T65 PowerShell runner 缺失：{RUNNER_PATH}")
    bench = BENCH_PATH.read_text(encoding="utf-8")
    runner = RUNNER_PATH.read_text(encoding="utf-8")
    check_compiled_source_bindings()
    for token in (
        "s2a_network_backend u_backend",
        "s2a_control_csr u_csr",
        "S2A_GF8_WEIGHT_OFFSET[0]",
        "S2A_GF8_WEIGHT_BYTES[0]",
        "S2A_OUTPUT_ADDRESS[0]",
        "$fread(input_bytes",
        "$fread(weight_bytes",
        "$fread(expected_first_byte",
        "input_tap_seen",
        "weight_tap_seen",
        "expected_sample0_input_tap_byte(init_index)",
        "expected_sample0_weight_tap_byte(init_index)",
        "input_bytes[expected_input_address[init_index] - INPUT_BASE_ADDRESS]",
        "weight_bytes[expected_weight_address[init_index] - layer0_weight_start_address]",
        "sample0 layer0 首个输出字节",
    ):
        require(token in bench, f"bench 缺少必要的真实数据/独立常量检查：{token}")
    require("assign mem_rdata = 32'd0" not in bench, "bench 仍把 memory read data 固定为零")
    require("!==" in bench and "$fatal" in bench, "bench 必须对不匹配字节立即 fatal")
    require("[switch]$RunSimulation" in runner and "[switch]$PrepareOnly" in runner and
            "if (-not $RunSimulation)" in runner,
            "runner 必须默认只准备夹具，仿真需显式开关")

    expected_input_bytes = {
        tap["reduction_index"]: tap["input_byte_signed"] & 0xFF for tap in input_taps
    }
    expected_weight_bytes = {
        tap["reduction_index"]: tap["weight_byte_signed"] & 0xFF for tap in input_taps
    }
    bench_input_bytes = parse_expected_tap_byte_function(bench, "expected_sample0_input_tap_byte")
    bench_weight_bytes = parse_expected_tap_byte_function(bench, "expected_sample0_weight_tap_byte")
    require(bench_input_bytes == expected_input_bytes,
            f"bench 输入 tap 常量与 sample0 fixture/provenance 不符：bench={bench_input_bytes} fixture={expected_input_bytes}")
    require(bench_weight_bytes == expected_weight_bytes,
            f"bench 权重 tap 常量与 GF8 fixture/provenance 不符：bench={bench_weight_bytes} fixture={expected_weight_bytes}")
    require_sample0_tap_bytes_match(input_raw, weight_raw, input_taps, bench_input_bytes, bench_weight_bytes)
    check_tap_corruption_rejection(input_raw, weight_raw, input_taps, bench_input_bytes, bench_weight_bytes)

    golden_match = re.search(
        r"localparam\s+logic\s+\[7:0\]\s+EXPECTED_T25_FIRST_BYTE\s*=\s*8'[hH]([0-9a-f]{2})",
        bench,
        re.IGNORECASE,
    )
    require(golden_match is not None and int(golden_match.group(1), 16) == golden_byte == 0xFF,
            "bench T25 独立首字节常量必须与 golden fixture 的 0xff 相同")
    return {
        "sim/tb_s2a_t65_layer0_golden.sv": sha256_file(BENCH_PATH),
        "verification/run_s2a_t65_layer0_golden.ps1": sha256_file(RUNNER_PATH),
        "verification/test_s2a_t65_layer0_golden.py": sha256_file(Path(__file__)),
    }


def materialize_fixture(evidence_dir: Path) -> dict[str, Any]:
    """绑定 sample0 预处理、GF8 layer0 权重和 T25 首个输出点。"""
    evidence_root = (ROOT / "report" / "evidence" / "S2A-T65").resolve()
    output_dir = evidence_dir.resolve()
    require(output_dir != evidence_root and evidence_root in output_dir.parents,
            f"夹具输出必须位于 D 盘项目的 S2A-T65 evidence 子目录：{output_dir}")

    source_hashes = check_pinned_files()
    check_compiled_source_bindings()
    fixed = read_json(FIXED_SAMPLES_PATH, "T01 fixed samples")
    manifest = read_json(MODEL_MANIFEST_PATH, "T01 model manifest")
    t23 = read_json(T23_PATH, "T23 参数表")
    t25 = read_json(T25_INDEX_PATH, "T25 golden index")
    require(fixed.get("schema_version") == "gestureforge_s2a_fixed_test_samples_v1",
            "T01 fixed samples schema 不匹配")
    require(manifest.get("status") == "G0_FROZEN" and manifest.get("model", {}).get("model_id") == "tiny416",
            "T01 tiny416 manifest 未保持 G0_FROZEN")
    require(t23.get("schema_version") == "gestureforge_s2a_conv_requant_parameter_table_v1" and
            t23.get("status") == "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH",
            "T23 表状态或 schema 与冻结证据不匹配")
    require(t25.get("schema_version") == "gestureforge_s2a_cpu_layer_golden_index_v2" and
            t25.get("status") == "COMPLETE",
            "T25 CPU golden index 未完成或 schema 不匹配")

    require(fixed.get("model_manifest_binding", {}).get("sha256") == PINNED_SHA256[
        "report/evidence/S2A-T01/tiny416_model_manifest.json"],
        "T01 samples 未绑定冻结 tiny416 manifest")
    require(fixed.get("sample_count") == 109 and isinstance(fixed.get("samples"), list) and
            len(fixed["samples"]) == 109, "固定测试清单不是冻结的 109 项")
    sample = fixed["samples"][0]
    require(sample.get("frame_id") == 0 and sample.get("sample_id") == "test_fist_000" and
            sample.get("source") == "official_hagrid_test",
            "T65 目标不是固定样本 0 test_fist_000")
    require(sample.get("pl_input_sha256") == EXPECTED_INPUT_SHA256,
            "T01 sample0 PL 输入 SHA 与冻结 T65 目标不符")
    require(fixed.get("official_test_manifest", {}).get("sha256") == EXPECTED_OFFICIAL_MANIFEST_SHA256,
            "官方 test manifest SHA 未与 T01 固定值一致")

    official_manifest_path = Path(fixed["official_test_manifest"]["path"]).resolve()
    require(official_manifest_path.is_file(), f"官方 manifest 精确路径缺失：{official_manifest_path}")
    actual_official_manifest_sha = sha256_file(official_manifest_path)
    require(actual_official_manifest_sha == EXPECTED_OFFICIAL_MANIFEST_SHA256,
            f"官方 manifest 当前 SHA 不匹配：{official_manifest_path}")
    image_path = (official_manifest_path.parent / sample["relative_image"]).resolve()
    require(image_path.is_file(), f"sample0 原图精确路径缺失：{image_path}")
    actual_image_sha = sha256_file(image_path)
    require(actual_image_sha == sample.get("image_sha256") == EXPECTED_IMAGE_SHA256,
            f"sample0 原图 SHA 与固定样本不匹配：{image_path}")

    sys.path.insert(0, str(ROOT))
    delivery = importlib.import_module("verification.s2a_model_delivery")
    numeric = importlib.import_module("verification.s1_t02_d2_numeric_reference")
    rgb = delivery.decode_rgb(image_path)
    require(str(rgb.dtype) == "uint8" and list(rgb.shape) == [sample["height"], sample["width"], 3],
            "sample0 按冻结 OpenCV 解码后的 RGB shape/dtype 不匹配")
    preprocessed = numeric.preprocess_rgb_uint8_to_chw_int8(
        rgb.tolist(), INPUT_WIDTH, INPUT_HEIGHT
    )
    import numpy as np

    input_tensor = np.asarray(preprocessed, dtype=np.int8)
    require(list(input_tensor.shape) == [INPUT_CHANNELS, INPUT_HEIGHT, INPUT_WIDTH],
            f"D2 预处理张量 shape 不匹配：{input_tensor.shape}")
    input_raw = np.ascontiguousarray(input_tensor).tobytes(order="C")
    input_sha = sha256_bytes(input_raw)
    require(len(input_raw) == INPUT_BYTES and input_sha == sample["pl_input_sha256"] == EXPECTED_INPUT_SHA256,
            f"重建的 T01 sample0 INT8 输入不匹配：bytes={len(input_raw)} SHA={input_sha}")

    bindings = manifest.get("bindings", {})
    package_path = Path(bindings.get("gf8_package", {}).get("path", "")).resolve()
    require(package_path.is_file(), f"G0 GF8 包精确路径缺失：{package_path}")
    package_sha = sha256_file(package_path)
    require(package_sha == bindings["gf8_package"].get("sha256") == EXPECTED_GF8_SHA256,
            f"G0 GF8 包 SHA 不匹配：{package_path}")
    package = package_path.read_bytes()
    require(len(package) == bindings["gf8_package"].get("bytes") == 5_903_100,
            "G0 GF8 包文件长度不匹配")
    require(package[:8] == b"GFINT8W1", "GF8 package magic 不匹配")
    version, layer_count, package_width, package_height, package_channels = struct.unpack_from(
        "<IIIII", package, 8
    )
    require((version, layer_count, package_width, package_height, package_channels) ==
            (1, 21, 416, 416, 3), "GF8 package header 与冻结 tiny416 不匹配")

    layer0 = manifest["layers"][0]
    require(layer0.get("layer_index") == 0 and layer0.get("op") == "convolutional" and
            layer0.get("input_shape_nchw") == [1, 3, 416, 416] and
            layer0.get("output_shape_nchw") == [1, 32, 208, 208] and
            layer0.get("kernel_hw") == [3, 3] and layer0.get("stride_hw") == [2, 2] and
            layer0.get("padding_lrtb") == [1, 1, 1, 1] and
            layer0.get("layout") == "NCHW",
            "T01 layer0 descriptor 与目标卷积几何不匹配")
    package_layer_header = struct.unpack_from("<8I", package, 28)
    layer_id, filters, inputs, groups, kernel, weight_count, _bn_count, scale_count = package_layer_header
    require((layer_id, filters, inputs, groups, kernel, weight_count, scale_count) ==
            (0, 32, 3, 1, 3, 864, 32),
            f"GF8 layer0 OIHW 记录头不匹配：{package_layer_header}")
    offsets = delivery.parse_package_offsets(package_path)[0]
    expected_offsets = layer0["gf8_parameter_offsets"]
    for key in ("record_offset", "weight_scale_offset", "fused_bias_offset",
                "quantized_weight_offset", "quantized_weight_bytes"):
        require(offsets[key] == expected_offsets[key],
                f"GF8 layer0 {key} 与 T01 manifest 不一致：{offsets[key]} != {expected_offsets[key]}")
    weight_offset = offsets["quantized_weight_offset"]
    weight_length = offsets["quantized_weight_bytes"]
    weight_raw = package[weight_offset:weight_offset + weight_length]
    require(len(weight_raw) == 864, "GF8 layer0 权重切片长度不是 864 字节")

    descriptor_text = DESCRIPTOR_PATH.read_text(encoding="utf-8")
    desc_weight_offsets = parse_sv_u32_array(descriptor_text, "S2A_GF8_WEIGHT_OFFSET")
    desc_weight_bytes = parse_sv_u32_array(descriptor_text, "S2A_GF8_WEIGHT_BYTES")
    desc_output_addresses = parse_sv_u32_array(descriptor_text, "S2A_OUTPUT_ADDRESS")
    require(desc_weight_offsets[0] == weight_offset and desc_weight_bytes[0] == weight_length,
            "T64 layer0 GF8 descriptor 偏移/长度与绑定 GF8 数据不一致")
    require(desc_output_addresses[0] == layer0.get("tensor_address") == OUTPUT_ADDRESS,
            "T64/T01 layer0 输出地址不一致")
    require(layer0.get("tensor_length_bytes") == 1_384_448,
            "T01 layer0 输出张量长度不匹配")

    t23_layer0 = t23["layers"][0]
    t23_channel0 = t23_layer0["channels"][0]
    require(t23_layer0.get("layer_index") == 0 and t23_layer0.get("channel_count") == 32 and
            t23_channel0.get("channel") == 0,
            "T23 layer0/channel0 参数记录缺失")
    bias = int(layer0["bias_accumulator_int32_per_output_channel"][0])
    input_channels = layer0["input_shape_nchw"][1]
    kernel_height, kernel_width = layer0["kernel_hw"]
    stride_y, stride_x = layer0["stride_hw"]
    pad_left, _pad_right, pad_top, _pad_bottom = layer0["padding_lrtb"]
    input_taps: list[dict[str, int]] = []
    accumulator = bias
    for input_channel in range(input_channels):
        for kernel_y in range(kernel_height):
            for kernel_x in range(kernel_width):
                input_y = kernel_y - pad_top
                input_x = kernel_x - pad_left
                if not (0 <= input_y < INPUT_HEIGHT and 0 <= input_x < INPUT_WIDTH):
                    continue
                reduction_index = input_channel * kernel_height * kernel_width + kernel_y * kernel_width + kernel_x
                input_offset = (input_channel * INPUT_HEIGHT + input_y) * INPUT_WIDTH + input_x
                weight_package_offset = weight_offset + reduction_index
                input_value = signed_int8(input_raw[input_offset])
                weight_value = signed_int8(package[weight_package_offset])
                product = input_value * weight_value
                accumulator += product
                input_taps.append({
                    "reduction_index": reduction_index,
                    "input_channel": input_channel,
                    "kernel_y": kernel_y,
                    "kernel_x": kernel_x,
                    "input_y": input_y,
                    "input_x": input_x,
                    "input_address": INPUT_BASE_ADDRESS + input_offset,
                    "input_byte_signed": input_value,
                    "weight_package_offset": weight_package_offset,
                    "weight_address": WEIGHT_BASE_ADDRESS + weight_package_offset,
                    "weight_byte_signed": weight_value,
                    "product": product,
                })
    require(len(input_taps) == 12, f"layer0 point0 有效 tap 应为 12 项，实际 {len(input_taps)}")
    require(all(row["input_byte_signed"] == 64 for row in input_taps),
            "layer0 point0 冻结 sample0 输入 tap 值与复核基线不符")
    require(sum(row["weight_byte_signed"] for row in input_taps) == 206,
            "layer0 point0 GF8 权重和与逐项复核不符")
    require(accumulator == -8_713 and -(1 << 31) <= accumulator < (1 << 31),
            f"layer0 point0 INT32 accumulator 不匹配：{accumulator}")
    if accumulator < 0:
        multiplier = int(t23_channel0["negative_M"])
        q_shift = int(t23_channel0["negative_Q"])
    else:
        multiplier = int(t23_channel0["positive_M"])
        q_shift = int(t23_channel0["positive_Q"])
    magnitude = abs(accumulator)
    requantized_magnitude = (magnitude * multiplier + (1 << (q_shift - 1))) >> q_shift
    requantized_signed = -requantized_magnitude if accumulator < 0 else requantized_magnitude
    requantized_signed = max(-127, min(127, requantized_signed))

    golden_sample = next(
        (row for row in t25.get("samples", []) if row.get("sample_id") == sample["sample_id"]),
        None,
    )
    require(golden_sample is not None and golden_sample.get("sample_index") == 0 and
            golden_sample.get("frame_id") == 0,
            "T25 未提供 sample0 的逐层 CPU golden")
    require(golden_sample.get("preprocessed_input", {}).get("sha256") == input_sha,
            "T25 sample0 golden 与重建 PL 输入 SHA 不一致")
    shard = golden_sample["network"]["compressed_shard"]
    shard_path = (ROOT / Path(shard["path"])).resolve()
    require(shard_path.is_file(), f"T25 sample0 shard 精确路径缺失：{shard_path}")
    actual_shard_sha = sha256_file(shard_path)
    require(actual_shard_sha == shard.get("sha256") == EXPECTED_T25_SHARD_SHA256,
            f"T25 sample0 shard SHA 不匹配：{shard_path}")
    shard_raw = zlib.decompress(shard_path.read_bytes())
    require(len(shard_raw) == shard["decompressed_bytes"] and
            len(shard_raw) == 11_382_150,
            "T25 sample0 解压后的网络张量流长度不匹配")
    require(sha256_bytes(shard_raw) == shard["decompressed_sha256"],
            "T25 sample0 解压张量流 SHA 不匹配")
    tensor = next((row for row in golden_sample["network"]["tensors"] if row.get("layer_index") == 0), None)
    require(tensor is not None and tensor.get("shape_nchw") == [1, 32, 208, 208] and
            tensor.get("element_type") == "int8_twos_complement" and tensor.get("stored") is True and
            tensor.get("byte_offset") == 0 and tensor.get("byte_length") == 1_384_448,
            "T25 layer0 tensor shape、NCHW 类型或 stream 映射不匹配")
    layer0_raw = shard_raw[tensor["byte_offset"]:tensor["byte_offset"] + tensor["byte_length"]]
    require(len(layer0_raw) == tensor["byte_length"] and
            sha256_bytes(layer0_raw) == tensor["tensor_sha256"] == EXPECTED_LAYER0_SHA256,
            "T25 sample0 layer0 输出 tensor SHA 不匹配")
    golden_byte = layer0_raw[GOLDEN_FIRST_BYTE_INDEX]
    golden_signed = signed_int8(golden_byte)
    require(golden_signed == requantized_signed == -1,
            f"独立点积/T23 重定标与 T25 第一个输出字节不一致：scalar={requantized_signed}, golden={golden_signed}")

    bench_runner_hashes = check_bench_and_runner(input_taps, input_raw, weight_raw, golden_byte)
    source_hashes.update(bench_runner_hashes)

    input_file = output_dir / "fixture" / "sample0_input_chw_int8.bin"
    weights_file = output_dir / "fixture" / "sample0_layer0_gf8_weights.bin"
    golden_file = output_dir / "fixture" / "sample0_layer0_output_point0.bin"
    write_new_or_verify(input_file, input_raw)
    write_new_or_verify(weights_file, weight_raw)
    write_new_or_verify(golden_file, bytes([golden_byte]))
    t25_index_sha = sha256_file(T25_INDEX_PATH)
    evidence = {
        "schema_version": "gestureforge_s2a_t65_layer0_golden_fixture_v1",
        "task_id": "S2A-T65-PREP",
        "status": "OFFLINE_FIXTURE_VERIFIED_SIMULATION_NOT_RUN",
        "scope": "sample0 layer0 CONV output NCHW index [0,0,0,0] only",
        "baseline_commit": EXPECTED_BACKEND_BASELINE,
        "sample": {
            "sample_index": 0,
            "sample_id": sample["sample_id"],
            "frame_id": sample["frame_id"],
            "image_path": str(image_path),
            "image_sha256": actual_image_sha,
            "preprocessing_oracle": "verification/s1_t02_d2_numeric_reference.py::preprocess_rgb_uint8_to_chw_int8",
            "preprocessing_decoder": "verification/s2a_model_delivery.py::decode_rgb",
            "input_shape_nchw": [1, INPUT_CHANNELS, INPUT_HEIGHT, INPUT_WIDTH],
            "input_dtype": "signed int8 two's complement",
            "input_byte_order": "contiguous CHW, channel then row then column",
            "input_bytes": len(input_raw),
            "input_sha256": input_sha,
            "input_fixture_path": str(input_file.resolve()),
            "input_fixture_sha256": sha256_bytes(input_raw),
        },
        "weights": {
            "package_path": str(package_path),
            "package_sha256": package_sha,
            "package_format": "GFINT8W1 v1 little-endian header",
            "layer_index": 0,
            "weight_layout": "output-channel-major; reduction index=input_channel*kernel_h*kernel_w+kernel_y*kernel_w+kernel_x",
            "quantized_weight_offset_bytes": weight_offset,
            "quantized_weight_offset_hex": f"0x{weight_offset:08x}",
            "quantized_weight_bytes": weight_length,
            "slice_path": str(weights_file.resolve()),
            "slice_sha256": sha256_bytes(weight_raw),
            "t64_descriptor_offset_matches": True,
            "t64_descriptor_length_matches": True,
        },
        "golden": {
            "index_path": str(T25_INDEX_PATH.resolve()),
            "index_sha256": t25_index_sha,
            "sample_shard_path": str(shard_path),
            "sample_shard_sha256": actual_shard_sha,
            "sample_shard_decompressed_sha256": sha256_bytes(shard_raw),
            "layer_index": 0,
            "tensor_shape_nchw": tensor["shape_nchw"],
            "tensor_byte_offset": tensor["byte_offset"],
            "tensor_byte_length": tensor["byte_length"],
            "tensor_sha256": sha256_bytes(layer0_raw),
            "first_output_linear_index": GOLDEN_FIRST_BYTE_INDEX,
            "first_output_nchw_index": [0, 0, 0, 0],
            "first_output_address": OUTPUT_ADDRESS,
            "first_output_byte_hex": f"0x{golden_byte:02x}",
            "first_output_byte_signed": golden_signed,
            "fixture_path": str(golden_file.resolve()),
            "fixture_sha256": sha256_bytes(bytes([golden_byte])),
        },
        "independent_point0_recalculation": {
            "geometry_source": "src/int8_conv_tap_geometry.sv",
            "weight_address_source": "src/int8_conv_weight_address.sv",
            "reduction_order": "input_channel, kernel_y, kernel_x",
            "valid_reduction_taps": len(input_taps),
            "taps": input_taps,
            "bias_accumulator_int32": bias,
            "weight_sum": sum(row["weight_byte_signed"] for row in input_taps),
            "dot_product": sum(row["product"] for row in input_taps),
            "accumulator_int32": accumulator,
            "selected_multiplier": multiplier,
            "selected_q_shift": q_shift,
            "requantized_signed_int8": requantized_signed,
            "matches_t25_first_output": True,
        },
        "source_sha256": source_hashes,
        "runtime_claims": {
            "vivado_or_xsim_invoked": False,
            "layer0_full_tensor_verified": False,
            "whole_network_verified": False,
        },
    }
    summary_path = output_dir / "fixture_manifest.json"
    summary_bytes = (json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    write_new_or_verify(summary_path, summary_bytes)
    return evidence


def main() -> int:
    """执行只读核验并在指定 D 盘 evidence 子目录生成最小夹具。"""
    parser = argparse.ArgumentParser(description="核验 T65 sample0 layer0 首个输出点夹具")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()
    evidence = materialize_fixture(args.evidence_dir)
    print("PASS: T65 离线夹具核验；仅 sample0 layer0 首个输出点")
    print("tap_constants=PASS; zero-fill and 24 selected-byte mutations rejected")
    print(f"sample0_input_sha256={evidence['sample']['input_sha256']}")
    print(f"layer0_weights_sha256={evidence['weights']['slice_sha256']}")
    print(f"valid_taps={evidence['independent_point0_recalculation']['valid_reduction_taps']} accumulator={evidence['independent_point0_recalculation']['accumulator_int32']}")
    print(f"T25_first_byte={evidence['golden']['first_output_byte_hex']} signed={evidence['golden']['first_output_byte_signed']}")
    print(f"fixture_manifest={args.evidence_dir.resolve() / 'fixture_manifest.json'}")
    print("SIMULATION_NOT_RUN")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FixtureError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
