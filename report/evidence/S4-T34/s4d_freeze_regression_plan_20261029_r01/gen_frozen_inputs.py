r"""冻结回归清单生成器：把 G3/G4 需要核对的冻结输入逐项算 sha256，产出 FROZEN_INPUTS.json。

只读：不启动 Vivado/hw_server/xsdb，不写证据目录以外的文件。

用法：python -B gen_frozen_inputs.py [--check]
  --check：按 FROZEN_INPUTS.json 复核磁盘文件是否与声明一致（fail-closed，exit 0=一致/1=不一致/2=输入错误）
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

W4 = Path(r"D:\codex-worktrees\w4")
M = Path(r"D:\FPGA_Competition\w2b")
OUT_DIR = Path(__file__).resolve().parent
OUT = OUT_DIR / "FROZEN_INPUTS.json"

# (tag, role, path, sha256 or None=运行时计算并写入)
ITEMS: list[tuple[str, str, Path, str | None]] = [
    # ---- 位流（部署候选）----
    ("bit_p2d", "阶段5 合并计算体位流（方向 A，部署候选）",
     Path(r"D:\tmp\lead\p2d_merged_20261029_r01\out\s4d_p2d_r01.bit"),
     "58c66cdb53994d577156b4ff62eabc7187d2e88184ca965bb3395f63ec1a86a3"),
    ("xsa_p2d", "P2d 硬件平台（地址映射/寄存器供 PS 侧与 JTAG 使用）",
     Path(r"D:\tmp\lead\p2d_merged_20261029_r01\out\s4d_p2d_r01.xsa"),
     "4ebc631ed56c204f40d585acffa9a9aa0488938e99711c0cf8b5bad38426a3ab"),
    ("bd_tcl_p2d", "P2d BD 构建脚本（可重建性）",
     W4 / "report/evidence/S4-T34/s4d_p2d_merged_bitstream_20261029_r01/bd_p2d.tcl", None),
    # ---- 参考平台位流 ----
    ("bit_2b_baseline", "2B 平台基线位流（4-D 链路参考平台）",
     M / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit",
     "555a70c2"),
    # ---- 应用 ELF（时间基座 + 超时常量修正版）----
    ("elf_m4b_rebuilt", "M4-b 自检应用（core_timeout=0xFFFFFFFF）",
     Path(r"D:\tmp\lead\rebuild_timeout_20261029_r01\build\s4d_ps_app_sw0_m4b.elf"),
     "aaedaf3c99cd6d015c2bfa53f8399c3f75fcea1e9b720e870863d2513a4fb339"),
    ("elf_m4b_close", "M4-b 收口应用（含 TAIL13 诊断）",
     Path(r"D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_m4b.elf"),
     "553fbf7ea7de8bc75edaf99c0b4d5cb79ef39e556e768b91abd459d1cf240e84"),
    ("elf_chainA", "chain-lite A 应用（重建）",
     Path(r"D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_chainA.elf"),
     "87e049b4db8f7debd212f91b354648c2e83f845d419048ae5783d1a9923bdc52"),
    ("elf_chainB", "chain-lite B 应用（重建）",
     Path(r"D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_chainB.elf"),
     "06bb0209c81f9286e386ca07de9c4364523c9c16091ac361e43a2e4b95d4e7ae"),
    ("elf_p2c_dma", "PL 预处理 + DMA 自检应用（时间基座修正版）",
     Path(r"D:\tmp\lead\s4t35_pl_preproc_20261029_r01\build\s4d_ps_app_pl_dma.elf"),
     "bff4b80ff8dea2771b66cf72690a9585cafcdef4b5d682be1eef611e4a1f5be6"),
    ("elf_init", "PS 初始化 ELF（ps7_init 装载器）",
     W4 / "report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf",
     "237dd959"),
    # ---- 数据 ----
    ("fixture_raw", "fixture RAW（640x480 BGR888，非实拍）",
     W4 / "report/evidence/S4-T34/bringup_chainlite_b_20261028_r01/fixture/fixture_fist_000_640x480_bgr888.raw",
     "ce37aa772aec9d45084edc37f3a1e0fe1b258385ec57b1fd994d98614792dad4"),
    ("weights_gf8", "INT8 权重 GF8",
     Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8"),
     "f6feb6d4"),
    ("input_tensor", "bridge 输入张量（chain-lite A/B 与 M4-b 共用）",
     W4 / "report/evidence/S4-CTRL/s4t26_layer_divergence_20261026_r02/bridge_input_postquant_int8_chw.bin",
     "da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e"),
    ("head13_raw", "head13 参考（5,070 B，M4-b 比较基准）",
     W4 / "report/evidence/S4-B/20261021_r01/test_fist_000_head13.raw", "07b59ca3"),
    ("head13_padded", "head13 参考补齐版（5,072 B / 1268 字，收口预置用）",
     W4 / "report/evidence/S4-T34/bringup_window6_20261028_r03/W2_pre_head13_padded.bin",
     "ad45b1cce3e1f45ceeb4955f4b8aaf2021ba778d78554e5a096ec50aacae8895"),
    ("head26_raw", "head26 参考（20,280 B）",
     W4 / "report/evidence/S4-B/20261021_r01/test_fist_000_head26.raw", None),
    ("m3_snapshot", "M3 候选区登记快照（12,615,680 B）",
     W4 / "report/evidence/S4-T32/window_a_20261027_r01/m3_snapshot_orig.bin",
     "41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf"),
    # ---- 驱动/脚本（回归可复现性）----
    ("driver", "板级驱动 v3.2.7（所有窗口共用）",
     W4 / "scripts/stage4_s4b/run_bringup_driver.py",
     "6c41ff4c4c4043d8f53ff963806f8e3e5211086ca8de204b0773985898d4e461"),
    ("window_driver", "窗口驱动（M4-a/M4-b/M3 复检）",
     W4 / "scripts/stage4_s4b/run_window_b_driver.py", None),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def build() -> int:
    items, bad = [], []
    for tag, role, path, exp in ITEMS:
        if not path.is_file():
            bad.append({"tag": tag, "path": str(path), "problem": "missing"})
            continue
        got = sha256(path)
        ok = exp is None or got.startswith(exp)
        if not ok:
            bad.append({"tag": tag, "path": str(path), "problem": "sha_mismatch", "declared": exp, "actual": got})
        items.append({"tag": tag, "role": role, "path": str(path), "bytes": path.stat().st_size,
                      "sha256": got, "expected_prefix": exp, "match": ok})
    doc = {"purpose": "G3/G4 冻结回归的输入基线（fail-closed：任一不符即不得开跑）",
           "generated_utc8": __import__("datetime").datetime.now(
               __import__("datetime").timezone(__import__("datetime").timedelta(hours=8))).isoformat(timespec="seconds"),
           "hash_basis": "worktree_disk（输入文件非仓库内容；仓库内证据按 commit_blob）",
           "items": items, "problems": bad,
           "verdict": "OK" if not bad else "FAIL"}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"verdict": doc["verdict"], "items": len(items), "problems": bad}, ensure_ascii=False, indent=2))
    return 0 if not bad else 1


def check() -> int:
    if not OUT.is_file():
        print("FROZEN_INPUTS.json 不存在，先运行不带 --check 的生成模式")
        return 2
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    bad = []
    for it in doc["items"]:
        p = Path(it["path"])
        if not p.is_file():
            bad.append({"tag": it["tag"], "problem": "missing"})
            continue
        got = sha256(p)
        if got != it["sha256"]:
            bad.append({"tag": it["tag"], "problem": "sha_mismatch", "declared": it["sha256"], "actual": got})
    print(json.dumps({"verdict": "OK" if not bad else "FAIL", "checked": len(doc["items"]), "problems": bad},
                     ensure_ascii=False, indent=2))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else build())