r"""M2 复审：只读复核 2026-10-27 M2（"无其他 DDR consumer"）构造性判据的寄存器/位基座与记录一致性。

用法：python -B verify_m2_basis.py [--json]

只用已归档的十进制读数（来自
  report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01/execution_20261027_r05/M2_consumer_check.log）
重算 hex 与位定义，并对照 r04/r05 的 JSON 记录，输出 PASS/FAIL 判据。

依据（本地正式资料）：UG585 v1.2 p.150 「PL reconfiguration flow」step 5：
  "Wait for PCFG_DONE to be set High by the PL (INT_STS-bit[2])"
⇒ PCFG_DONE 在 **0xF800700C（INT_STS）bit[2]**，不是 0xF8007014（STATUS）的 bit[1]。

本脚本不改任何文件；退出码 0=复核脚本自身完成（不代表 M2 通过）。
"""
from __future__ import annotations

import json
import sys

# r05 原始十进制读数（M2_consumer_check.log）
RAW = {
    "DEVCGF_CTRL_0xF8007000": 1308680319,
    "DEVCGF_INT_STS_0xF800700C": 2818703370,
    "DEVCGF_STATUS_0xF8007014": 1073744432,
}
# 归档 JSON 里的 hex 注释（r04 / r05）
RECORDED_HEX = {
    "DEVCGF_CTRL_0xF8007000": "0x4E00FFFF",      # r04 JSON
    "DEVCGF_STATUS_0xF8007014": "0x40000010",    # r04 + r05 README/JSON
}


def bits(v: int) -> dict:
    return {f"bit{i}": (v >> i) & 1 for i in (0, 1, 2, 3, 4, 27, 30, 31)}


def main() -> int:
    out = {"raw_decimal": RAW, "derived": {}, "record_hex_check": {}, "verdict": {}}
    for k, v in RAW.items():
        out["derived"][k] = {"hex": hex(v), "bits": bits(v)}

    ok = True
    for k, claimed in RECORDED_HEX.items():
        actual = hex(RAW[k])
        match = int(claimed, 16) == RAW[k]
        out["record_hex_check"][k] = {"recorded": claimed, "actual": actual, "match": match}
        ok = ok and match

    int_sts = RAW["DEVCGF_INT_STS_0xF800700C"]
    status = RAW["DEVCGF_STATUS_0xF8007014"]
    out["verdict"] = {
        "pcfg_done_register": "0xF800700C INT_STS, bit[2]（UG585 v1.2 p.150 step 5）",
        "pcfg_done_value": (int_sts >> 2) & 1,
        "status_bit1_value(被原记录当作 PCFG_DONE)": (status >> 1) & 1,
        "status_bit4_value(PCFG_INIT, 见驱动口径)": (status >> 4) & 1,
        "record_cites_wrong_register": True,
        "record_hex_annotations_all_correct": ok,
        "conclusion_holds_if_rebased_on_int_sts": ((int_sts >> 2) & 1) == 0,
        "note": ("INT_STS[2]=0 与『PL 未配置』相容，但『构造性排除』仍需补："
                 "① 以 INT_STS[2] 作为唯一 PCFG_DONE 依据；② 修正 hex 注释；"
                 "③ 明确 INT_STS 可被写 1 清除，单次为 0 不等于从未配置过。"),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())