r"""M2 判据基座勘误（2026-10-29 r01）：按复审关闭条件重算，不改写 2026-10-27 旧记录。

与 `m2_review_20261029_r01/verify_m2_basis.py` 的差别：
  1. 只认 **INT_STS(0xF800700C) bit[2]** 为 PCFG_DONE（UG585 v1.2 p.150 step 5），
     并把原记录使用的 STATUS(0xF8007014) bit[1] 明确标为**记录缺陷**（只作对照，不作判据）；
  2. 修正两处 hex 注释（DEVCGF_STATUS→0x40000A30、DEVCGF_CTRL→0x4E00E07F）并给出可复算依据；
  3. 显式写入限制：`INT_STS` 是 W1C，单次读到 0 ≠ 从未配置过 ⇒ M2 只能表述为**构造性推断**；
  4. 输出机器可读 verdict + 退出码（0=勘误自检通过，1=不一致）。

只读归档日志/JSON，不访问板卡、不写任何证据目录以外的文件。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

W4 = Path(r"D:\codex-worktrees\w4")
ARCH = W4 / "report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01"
LOG_R05 = ARCH / "execution_20261027_r05/M2_consumer_check.log"
JSON_R04 = ARCH / "execution_20261027_r04/M2_result.json"
JSON_R05 = ARCH / "execution_20261027_r05/M2_result.json"
OUT = Path(__file__).with_name("verify_m2_basis_r02_output.json")

# 归档十进制读数（r05 M2_consumer_check.log，逐行可复算）
RAW = {
    "DEVCGF_CTRL_0xF8007000": 1308680319,
    "DEVCGF_INT_STS_0xF800700C": 2818703370,
    "DEVCGF_STATUS_0xF8007014": 1073744432,
}
# 旧记录里写错的 hex 注释（r04 JSON / r05 README+JSON）
OLD_HEX = {
    "DEVCGF_CTRL_0xF8007000": "0x4E00FFFF",
    "DEVCGF_STATUS_0xF8007014": "0x40000010",
}
# 勘误后的正确 hex
NEW_HEX = {k: hex(v) for k, v in RAW.items()}


def bit(v: int, n: int) -> int:
    return (v >> n) & 1


def main() -> int:
    out: dict = {
        "task": "M2 判据基座勘误",
        "run_id": "s4d_m2_erratum_20261029_r01",
        "basis": {
            "pcfg_done_register": "0xF800700C INT_STS",
            "pcfg_done_bit": 2,
            "citation": "UG585 v1.2 p.150 'PL reconfiguration flow' step 5: Wait for PCFG_DONE (INT_STS-bit[2])",
            "wrong_in_old_record": "0xF8007014 STATUS bit[1]（记录缺陷，不得作判据）",
        },
        "readings": {},
        "hex_correction": {},
        "verdict": {},
        "limitation": ("INT_STS 为 W1C：单次读到 PCFG_DONE=0 只能支持"
                       "『本轮未见 PCFG_DONE 置位』的构造性推断，不能证明『从未配置过』"),
        "sources_read_only": [str(LOG_R05), str(JSON_R04), str(JSON_R05)],
    }
    int_sts = RAW["DEVCGF_INT_STS_0xF800700C"]
    status = RAW["DEVCGF_STATUS_0xF8007014"]
    for k, v in RAW.items():
        out["readings"][k] = {"decimal": v, "hex_correct": hex(v),
                              "bits_0_4": [bit(v, i) for i in range(5)],
                              "bits_27_30_31": [bit(v, i) for i in (27, 30, 31)]}
    ok_hex = True
    for k, old in OLD_HEX.items():
        match_new = int(old, 16) == RAW[k]
        out["hex_correction"][k] = {"old_recorded": old, "correct": NEW_HEX[k], "old_was_correct": match_new}
        ok_hex = ok_hex and not match_new
    pcfg_done = bit(int_sts, 2)
    out["verdict"] = {
        "pcfg_done_int_sts_bit2": pcfg_done,
        "old_basis_status_bit1": bit(status, 1),
        "status_bit4_pcfg_init_driver_view": bit(status, 4),
        "conclusion_pl_configured_this_round": ("NO" if pcfg_done == 0 else "YES"),
        "wording_required": ("本轮未见 PCFG_DONE 置位（INT_STS[2]=0）⇒ 构造性推断 PL 未配置；"
                            "不得表述为『排除其他 DDR consumer』或『从未配置』"),
        "old_hex_annotations_were_wrong": ok_hex,
        "erratum_self_check": "PASS" if (pcfg_done == 0 and ok_hex) else "FAIL",
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(out["verdict"], ensure_ascii=False, indent=2))
    return 0 if out["verdict"]["erratum_self_check"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())