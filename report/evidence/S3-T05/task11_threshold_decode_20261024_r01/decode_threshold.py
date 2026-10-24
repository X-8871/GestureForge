"""只读解码已冻结 OOC 网表中的 SOF 阈值 LUT，并穷举其组合真值表。"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


TASK_ID = "S3-T05"
RUN_ID = "task11_threshold_decode_20261024_r01"
EXPECTED_COMMIT = "1d54894be4d547955034eeff8bce853dd4286fac"
EXPECTED_PATCH_SHA256 = "fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5"
EXPECTED_NETLIST_SHA256 = "7b8f457c1cd5377367b3032369ba72fc5d00ac465629ecd970d6fb7e479b852a"
EXPECTED_LUT_INIT = 0x00A8
THRESHOLD = 16384
COUNTER_WIDTH = 16


def sha256_file(path: Path) -> tuple[str, int]:
    """返回文件原始字节的 SHA-256 与字节数。"""
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def git_text(root: Path, *args: str) -> str:
    """只读查询当前 Git 工作树信息。"""
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def require(condition: bool, message: str) -> None:
    """在输入或网表结构不符合冻结依据时停止。"""
    if not condition:
        raise ValueError(message)


def decode_netlist(netlist_text: str) -> tuple[int, dict[str, str]]:
    """核对顶层计数器总线、模块端口方向及 LUT4 实例引脚映射。"""
    top_instances = list(
        re.finditer(
            r"(?s)\b[\w]+_cmos_8_16bit\s+cmos_8_16bit_m0\s*\((.*?)\);",
            netlist_text,
        )
    )
    require(len(top_instances) == 1, "期望唯一的 cmos_8_16bit_m0 实例")
    top_ports = top_instances[0].group(1)
    require(
        re.search(
            r"\.S\s*\(\s*cmos_hblank_low_cnt_reg\s*\[\s*15\s*:\s*14\s*\]\s*\)",
            top_ports,
        )
        is not None,
        "cmos_8_16bit_m0 的 S 端口未连接计数器 [15:14]",
    )

    module_match = re.search(
        r"(?m)^module\s+[\w]+_cmos_8_16bit\b", netlist_text
    )
    require(module_match is not None, "找不到 cmos_8_16bit 模块声明")
    module_end = netlist_text.find("endmodule", module_match.start())
    require(module_end >= 0, "cmos_8_16bit 模块缺少 endmodule")
    module_text = netlist_text[module_match.start() : module_end]
    require(
        re.search(r"(?m)^\s*input\s+\[1:0\]\s*S\s*;", module_text)
        is not None,
        "cmos_8_16bit 的 S 端口不是 input [1:0]",
    )

    lut_matches = list(
        re.finditer(
            r"(?s)LUT4\s*#\s*\(\s*\.INIT\s*\(\s*16'h([0-9a-fA-F]+)\s*\)\s*\)\s*"
            r"s_axis_tuser_i_2\s*\((.*?)\);",
            netlist_text,
        )
    )
    require(len(lut_matches) == 1, "期望唯一的 s_axis_tuser_i_2 LUT4 实例")
    init = int(lut_matches[0].group(1), 16)
    require(init == EXPECTED_LUT_INIT, f"LUT INIT 与冻结值不符：0x{init:04X}")

    pin_map = {
        f"I{index}": signal.strip()
        for index, signal in re.findall(
            r"\.I([0-3])\s*\(\s*([^,)]+?)\s*\)", lut_matches[0].group(2)
        )
    }
    expected_pin_map = {
        "I0": "cmos_hblank",
        "I1": "S[1]",
        "I2": "S[0]",
        "I3": "cmos_hblank_d0",
    }
    require(pin_map == expected_pin_map, f"LUT 引脚映射不符：{pin_map}")
    return init, pin_map


def run_exhaustive(init: int) -> dict[str, object]:
    """穷举 16 位计数器、当前 hblank 与前一拍 hblank 的所有组合。"""
    total = 0
    lut_true_count = 0
    expected_true_count = 0
    mismatch_count = 0
    first_mismatch: dict[str, int] | None = None

    for counter in range(1 << COUNTER_WIDTH):
        counter_bit_15 = (counter >> 15) & 1
        counter_bit_14 = (counter >> 14) & 1
        for current_hblank in (0, 1):
            for previous_hblank in (0, 1):
                lut_index = (
                    current_hblank
                    | (counter_bit_15 << 1)
                    | (counter_bit_14 << 2)
                    | (previous_hblank << 3)
                )
                lut_value = (init >> lut_index) & 1
                expected_value = int(
                    current_hblank == 1
                    and counter >= THRESHOLD
                    and previous_hblank == 0
                )
                total += 1
                lut_true_count += lut_value
                expected_true_count += expected_value
                if lut_value != expected_value:
                    mismatch_count += 1
                    if first_mismatch is None:
                        first_mismatch = {
                            "counter": counter,
                            "current_hblank": current_hblank,
                            "previous_hblank": previous_hblank,
                            "lut_value": lut_value,
                            "expected_value": expected_value,
                        }

    require(total == 262144, f"组合总数错误：{total}")
    require(expected_true_count == 49152, f"期望真值数错误：{expected_true_count}")
    require(lut_true_count == 49152, f"LUT 真值数错误：{lut_true_count}")
    require(mismatch_count == 0, f"发现真值表差异：{mismatch_count}")
    return {
        "total_combinations": total,
        "lut_true_count": lut_true_count,
        "reference_true_count": expected_true_count,
        "mismatch_count": mismatch_count,
        "first_mismatch": first_mismatch,
    }


def write_result_exclusive(path: Path, payload: dict[str, object]) -> None:
    """只在本 RunId 内以排他方式创建结果 JSON，拒绝覆盖。"""
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)


def main() -> int:
    """验证冻结输入、解码 LUT，并仅在全部条件通过时写入 PASS 结果。"""
    script_path = Path(__file__).resolve()
    run_dir = script_path.parent
    root = script_path.parents[4]
    result_path = run_dir / "result.json"
    require(not result_path.exists(), "result.json 已存在，拒绝覆盖此 RunId")

    source_commit = git_text(root, "rev-parse", "HEAD")
    source_branch = git_text(root, "branch", "--show-current")
    require(source_commit == EXPECTED_COMMIT, "当前 HEAD 与任务基线不一致")
    require(source_branch == "codex/stage3-video", "当前分支与任务工作树不符")

    patch_path = root / "board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
    netlist_path = (
        root
        / "tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/"
        / "design_1_alinx_ov5640_0_0_synth_1/"
        / "design_1_alinx_ov5640_0_0_sim_netlist.v"
    )
    patch_sha256, patch_size = sha256_file(patch_path)
    netlist_sha256, netlist_size = sha256_file(netlist_path)
    require(patch_sha256 == EXPECTED_PATCH_SHA256, "补丁 SHA-256 与冻结值不符")
    require(netlist_sha256 == EXPECTED_NETLIST_SHA256, "网表 SHA-256 与冻结值不符")

    netlist_text = netlist_path.read_text(encoding="utf-8")
    init, pin_map = decode_netlist(netlist_text)
    exhaustive = run_exhaustive(init)
    created = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")

    payload: dict[str, object] = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "created_utc8": created,
        "source_commit": source_commit,
        "source_branch": source_branch,
        "inputs": {
            "patch": {
                "path": "board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch",
                "sha256": patch_sha256,
                "size_bytes": patch_size,
            },
            "netlist": {
                "path": netlist_path.relative_to(root).as_posix(),
                "sha256": netlist_sha256,
                "size_bytes": netlist_size,
            },
        },
        "decode": {
            "lut_instance": "s_axis_tuser_i_2",
            "lut_type": "LUT4",
            "lut_init_hex": "00A8",
            "pin_map": pin_map,
            "counter_bus_connection": "S[1:0] <- cmos_hblank_low_cnt_reg[15:14]",
            "boolean_equation": "current_hblank && (counter[15] || counter[14]) && !previous_hblank",
            "unsigned_threshold": THRESHOLD,
        },
        "exhaustive": {
            "counter_width_bits": COUNTER_WIDTH,
            "counter_values": 1 << COUNTER_WIDTH,
            "current_hblank_values": 2,
            "previous_hblank_values": 2,
            **exhaustive,
        },
        "verdict": "PASS_STATIC_THRESHOLD_DECODE",
        "limitations": [
            "仅证明当前哈希固定的 OOC 网表 LUT4 组合真值表等价于阈值判定；RTL 顺序等价、计数器状态更新与饱和行为仍未证明。"
        ],
        "python_version": sys.version.split()[0],
    }
    write_result_exclusive(result_path, payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"解码失败：{exc}", file=sys.stderr)
        raise SystemExit(2)
