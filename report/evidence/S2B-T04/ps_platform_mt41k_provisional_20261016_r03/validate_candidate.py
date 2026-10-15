"""核对R03暂定DDR字段与PS7 Tcl请求的一致性。"""

import json
from pathlib import Path


def main() -> int:
    """执行不启动Vivado的配置源码断言。"""
    root = Path(__file__).resolve().parents[4]
    fields = json.loads(
        (root / "board/ps_platform_fields.json").read_text(encoding="utf-8")
    )
    tcl = (root / "vivado/s2b_ps_platform.tcl").read_text(encoding="utf-8")
    candidate = fields["active_ddr_candidate"]
    requested = tcl.split("proc ::s2b_ps_platform::requested {} {", 1)[1].split("\n}", 1)[0]

    config = {}
    for raw_line in requested.splitlines():
        line = raw_line.strip()
        if not line.startswith("CONFIG."):
            continue
        if line.endswith("\\"):
            line = line[:-1].rstrip()
        if line.endswith("]"):
            line = line[:-1].rstrip()
        parts = line.split(maxsplit=1)
        assert len(parts) == 2
        name, value = parts
        assert name not in config
        assert value.startswith("{") and value.endswith("}")
        config[name] = value[1:-1]

    assert candidate["status"] == "PROVISIONAL_OFFLINE_CANDIDATE"
    assert candidate["partno_literal"] == "MT41K256M16TW-107"
    assert "CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41K256M16TW-107}" in requested
    assert "MT41J256M16" not in requested
    assert candidate["dram_family"] == "DDR3L"
    assert candidate["ps7_memory_type_enum"] == "DDR 3"
    assert f"候选DRAM技术族为 {candidate['dram_family']}" in requested

    geometry = candidate["geometry_candidate"]
    assert geometry["device_count"] == 2
    assert geometry["bits_per_device"] == 16
    assert geometry["density_bits_per_device"] == 4_294_967_296
    assert geometry["density_bits_per_device"] // (1024 * 1024) == int(
        geometry["ps7_device_capacity_enum"].split()[0]
    )
    assert geometry["total_capacity_bytes"] == 1_073_741_824
    assert geometry["ps7_bus_width_enum"] == "32 Bit"
    assert int(geometry["ps7_bus_width_enum"].split()[0]) == (
        geometry["device_count"] * geometry["bits_per_device"]
    )
    assert geometry["total_capacity_bytes"] == (
        geometry["density_bits_per_device"] * geometry["device_count"] // 8
    )
    assert geometry["row_address_bits"] == 15
    assert geometry["column_address_bits"] == 10
    assert geometry["bank_address_bits"] == 3
    assert geometry["bank_count"] == 8
    assert geometry["bank_count"] == 1 << geometry["bank_address_bits"]
    assert (1 << geometry["row_address_bits"]) * (
        1 << geometry["column_address_bits"]
    ) == 32 * 1024 * 1024
    assert candidate["requested_ddr_clock_mhz"] == 533.333333

    expected_settings = {
        "CONFIG.PCW_UIPARAM_DDR_PARTNO": candidate["partno_literal"],
        "CONFIG.PCW_UIPARAM_DDR_MEMORY_TYPE": candidate["ps7_memory_type_enum"],
        "CONFIG.PCW_UIPARAM_DDR_BUS_WIDTH": geometry["ps7_bus_width_enum"],
        "CONFIG.PCW_UIPARAM_DDR_DRAM_WIDTH": f"{geometry['bits_per_device']} Bits",
        "CONFIG.PCW_UIPARAM_DDR_DEVICE_CAPACITY": geometry["ps7_device_capacity_enum"],
        "CONFIG.PCW_UIPARAM_DDR_ROW_ADDR_COUNT": str(geometry["row_address_bits"]),
        "CONFIG.PCW_UIPARAM_DDR_COL_ADDR_COUNT": str(geometry["column_address_bits"]),
        "CONFIG.PCW_UIPARAM_DDR_BANK_ADDR_COUNT": str(geometry["bank_address_bits"]),
        "CONFIG.PCW_UIPARAM_DDR_FREQ_MHZ": f"{candidate['requested_ddr_clock_mhz']:.6f}",
    }
    for name, expected in expected_settings.items():
        assert config.get(name) == expected, (name, config.get(name), expected)

    allowed_ddr_settings = {
        "CONFIG.PCW_UIPARAM_DDR_ENABLE",
        *expected_settings.keys(),
        "CONFIG.PCW_UIPARAM_DDR_ECC",
        "CONFIG.PCW_UIPARAM_DDR_TRAIN_WRITE_LEVEL",
        "CONFIG.PCW_UIPARAM_DDR_TRAIN_READ_GATE",
        "CONFIG.PCW_UIPARAM_DDR_TRAIN_DATA_EYE",
    }
    requested_ddr_settings = {name for name in config if "DDR" in name}
    assert requested_ddr_settings == allowed_ddr_settings, (
        requested_ddr_settings - allowed_ddr_settings,
        allowed_ddr_settings - requested_ddr_settings,
    )

    assert candidate["timing_status"] == "BLOCKED"
    assert candidate["explicit_timing_values_set_by_r03"] == []
    forbidden = (
        "PCW_UIPARAM_DDR_CL",
        "PCW_UIPARAM_DDR_CWL",
        "PCW_UIPARAM_DDR_SPEED_BIN",
        "PCW_UIPARAM_ACT_DDR_FREQ",
        "PCW_UIPARAM_DDR_T_",
        "PCW_UIPARAM_DDR_T_RCD",
        "PCW_UIPARAM_DDR_BOARD_DELAY",
        "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY",
        "PCW_PACKAGE_DDR_",
    )
    assert not any(name in requested for name in forbidden)
    print("JSON/TCL provisional binding assertions: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
