from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def ceil_tiles(length: int, edge: int) -> list[int]:
    return [min(edge, length - start) for start in range(0, length, edge)]


def expected_tiles(profile: dict) -> dict[int, dict[tuple[int, int], tuple[int, int, int]]]:
    result = {}
    for layer in profile["static"]["per_layer"]:
        if layer["op"] != "conv":
            continue
        out_h, out_w = layer["out_hw"]
        stride_y, stride_x = layer["stride"]
        kernel = round(layer["k"] ** 0.5)
        tile_rows = ceil_tiles(out_h, 16)
        tile_cols = ceil_tiles(out_w, 16)
        rows = {}
        for extent_y in tile_rows:
            for extent_x in tile_cols:
                patch_h = (extent_y - 1) * stride_y + kernel
                patch_w = (extent_x - 1) * stride_x + kernel
                rows[(extent_y, extent_x)] = (patch_h, patch_w, patch_h * patch_w * layer["in_ch"])
        result[layer["layer"]] = rows
    return result


def parse_tile_table(source: str) -> dict[tuple[int, int, int], tuple[int, int, int]]:
    pattern = re.compile(
        r"42'h([0-9A-Fa-f]+): frozen_conv_tile_lookup_16 = "
        r"\{32'd(\d+), 32'd(\d+), 32'd(\d+)\};"
    )
    parsed = {}
    for match in pattern.finditer(source):
        key, patch_h, patch_w, patch_bytes = (int(value, 16) if index == 0 else int(value)
                                               for index, value in enumerate(match.groups()))
        parsed[(key >> 10, (key >> 5) & 0x1F, key & 0x1F)] = (patch_h, patch_w, patch_bytes)
    return parsed


def parse_full_table(source: str) -> dict[int, tuple[int, int, int, int]]:
    pattern = re.compile(
        r"32'd(\d+): frozen_full_tile_lookup_16 = "
        r"\{19'd(\d+), 19'd(\d+), 32'd(\d+), 29'd(\d+)\};"
    )
    return {int(layer): tuple(int(value) for value in match.groups()[1:])
            for match in pattern.finditer(source)
            for layer in [match.groups()[0]]}


def verify(profile_path: Path, rtl_path: Path) -> None:
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    source = rtl_path.read_text(encoding="utf-8")
    expected = expected_tiles(profile)
    actual = parse_tile_table(source)
    expected_flat = {
        (layer, extent_y, extent_x): geometry
        for layer, extents in expected.items()
        for (extent_y, extent_x), geometry in extents.items()
    }
    if actual != expected_flat:
        missing = sorted(set(expected_flat) - set(actual))
        extra = sorted(set(actual) - set(expected_flat))
        mismatched = sorted(key for key in set(actual) & set(expected_flat)
                            if actual[key] != expected_flat[key])
        raise AssertionError(f"tile表不匹配：缺失={missing[:5]} 额外={extra[:5]} 数值不符={mismatched[:5]}")

    full_actual = parse_full_table(source)
    full_expected = {}
    for layer in profile["static"]["per_layer"]:
        if layer["op"] != "conv":
            continue
        extent_y = min(16, layer["out_hw"][0])
        extent_x = min(16, layer["out_hw"][1])
        stride_y, stride_x = layer["stride"]
        kernel = round(layer["k"] ** 0.5)
        patch_h = (extent_y - 1) * stride_y + kernel
        patch_w = (extent_x - 1) * stride_x + kernel
        full_expected[layer["layer"]] = (patch_h, patch_w, patch_h * patch_w,
                                          patch_h * patch_w * layer["in_ch"])
    if full_actual != full_expected:
        raise AssertionError("16×16全tile patch边界表与冻结逐层形状不符")

    required = (
        "localparam integer TILE_EDGE = FROZEN_CONV_DESCRIPTOR ? 16 : 8;",
        "localparam integer MAX_FEATURE_PATCH_BYTES = FROZEN_CONV_DESCRIPTOR ? 124416 : 51200;",
        "localparam integer OUTPUT_BLOCK_BYTES = FROZEN_CONV_DESCRIPTOR ? 2048 : 512;",
        "tile_origin_y <=",
        "tile_origin_x <=",
        "feature_scan_in_bounds =",
        "frozen_conv_tile_lookup_16({layer_index_latched, tile_prep_extent_y[4:0], tile_prep_extent_x[4:0]})",
    )
    if any(fragment not in source for fragment in required):
        raise AssertionError("RTL缺少16×16 tile边界/patch容量/坐标保护绑定")

    if expected[0][(16, 16)] != (33, 33, 3267):
        raise AssertionError("layer0 stride2+padding tile patch锚点错误")
    if expected[35][(16, 16)] != (18, 18, 124416):
        raise AssertionError("layer35完整tile patch锚点错误")
    if expected[35][(16, 10)] != (18, 12, 82944):
        raise AssertionError("layer35尾tile patch锚点错误")
    if max(value[2] for extents in expected.values() for value in extents.values()) != 124416:
        raise AssertionError("最大feature patch容量计算错误")
    print(f"PASS S2C-RTL01 tile_keys={len(expected_flat)} full_layers={len(full_expected)} max_patch=124416B")


def main() -> int:
    parser = argparse.ArgumentParser(description="核对16×16冻结网络tile patch表")
    parser.add_argument("--profile", type=Path, default=Path(r"D:\wb-out-r3\task_l0\profile.json"))
    parser.add_argument("--rtl", type=Path, default=Path("src/s2b_conv_tile_engine.sv"))
    args = parser.parse_args()
    verify(args.profile, args.rtl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
