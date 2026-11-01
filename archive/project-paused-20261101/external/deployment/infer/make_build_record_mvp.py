r"""生成 MVP 推理 ELF 的构建记录（只读汇总，不重算构建；不 git）。"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC8 = timezone(timedelta(hours=8))
OUT = Path(r"D:\tmp\lead\mvp_infer_20261031_r01")
WEIGHTS = Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2"
               r"\gesture_yolov4_tiny_416_int8_weights.gf8")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def exits() -> dict:
    d = {}
    for line in read(OUT / "logs" / "exit_codes_mvp.txt").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = int(v.strip())
    return d


def variant(tag: str) -> dict:
    elf = OUT / "build" / f"{tag}.elf"
    nm = read(OUT / "build" / f"{tag}.nm.txt")
    od = read(OUT / "build" / f"{tag}.objdump.txt")
    st = read(OUT / "build" / f"{tag}.strings.txt")
    def sym(name: str):
        m = re.search(rf"^([0-9a-f]+)\s+\S+\s+\S?\s*{re.escape(name)}$", nm, re.M)
        return m.group(1) if m else None
    return {
        "path": str(elf), "sha256": sha(elf), "bytes": elf.stat().st_size,
        "size_output": read(OUT / "build" / f"{tag}.size.txt").strip(),
        "_start": sym("_start"), "main": sym("main"), "bss_end": sym("__bss_end"),
        "symbols": {k: sym(k) for k in ("s4d_mvp_cam_loop", "s4d_mvp_publish",
                                         "s2b_network_start_from_tensor", "s2a_decode_nms_reference",
                                         "s4d_sw_preproc_bgr888_to_chw_int8")},
        "disasm_evidence": {
            "s5rs_base_0x20800000_hits": len(re.findall(r"545259520\s*;\s*0x20800000", od)),
            "s5rs_magic_halves": bool(re.search(r"movw\s+\w+, #21075\s*;\s*0x5253", od)
                                       and re.search(r"movt\s+\w+, #21301\s*;\s*0x5335", od)),
            "gt_regs_0xf8f00200_204": bool(re.search(r"#63728\s*;\s*0xf8f0", od)
                                            and re.search(r"#516", od) and re.search(r"#512", od)),
            "calls_network_and_decode": bool(re.search(r"<s2b_network_start_from_tensor>", od)
                                              and re.search(r"<s2a_decode_nms_reference>", od)),
        },
        "uart_strings": {
            "MVP_APP": "MVP APP: CAM=%d raw=0x%08x %ux%u bgr888 bytes=%u s5rs=0x%08x" in st,
            "MVP_WEIGHTS": "MVP WEIGHTS: %s @0x%08x" in st,
            "MVP_TIME": "MVP TIME t0_pre=%u t1_pl=%u t2_decode=%u t3_pub=%u "
                        "dt_pre=%u dt_pl=%u dt_dec=%u dt_all=%u raw_nz=%u" in st,
            "MVP_S5RS": "MVP S5RS frame=%u n_dets=%u magic=0x%08x" in st,
        },
    }


def main() -> int:
    t = OUT / "variant_transform_mvp.json"
    transform = json.loads(read(t))
    rec = {
        "task_id": "S5-T01/MVP-infer",
        "phase": "MVP：相机帧 → YOLOv4-tiny 2B PL → 解码/NMS → S5RS 0x20800000（离线构建）",
        "generated_utc8": datetime.now(UTC8).isoformat(timespec="seconds"),
        "boundary": "离线：未碰板卡/JTAG/COM4/hw_server；未跑 Vivado 综合/实现；未 git；"
                    "ENABLE=0；不主张 G3/G4/G5",
        "base_source": transform["base"],
        "transform": {"path": str(t), "sha256": sha(t),
                      "insertions": transform["insertions"], "switches": transform["switches"]},
        "inputs": transform["inputs"],
        "exit_codes": exits(),
        "variants": {
            "core0": variant("s4d_ps_app_mvp"),
            "core1": variant("s4d_ps_app_mvp_core1"),
        },
        "linker_scripts": {
            "core0": {"path": r"D:\codex-worktrees\w4\tmp\4\S4-T34\ps_app_build\lscript_s4t34.ld",
                      "sha256": sha(Path(r"D:\codex-worktrees\w4\tmp\4\S4-T34\ps_app_build\lscript_s4t34.ld"))},
            "core1": {"path": str(OUT / "src" / "lscript_s4t34_core1.ld"),
                      "sha256": sha(OUT / "src" / "lscript_s4t34_core1.ld"),
                      "note": "ORIGIN 0x00100000→0x02000000；budget ASSERT 0x03000000"},
        },
        "weights_package": {
            "path": str(WEIGHTS), "bytes": WEIGHTS.stat().st_size, "sha256": sha(WEIGHTS),
            "first8_ascii": WEIGHTS.read_bytes()[:8].decode("ascii", "replace"),
            "first_word_le_hex": "0x" + WEIGHTS.read_bytes()[:4][::-1].hex().upper(),
            "load_addr": "0x10100000", "load_method": "xsdb: dow -data <file> 0x10100000 + verify -data",
        },
        "warnings": {"compile_app_mvp_log": read(OUT / "logs" / "compile_app_mvp.log").strip(),
                     "note": "唯一告警为基线与新源码都已有的 S4D_ST_ERROR 宏重定义"},
        "unknowns": [
            "47.3 s/轮的 dt_pre/dt_pl/dt_dec 比例：待板上 MVP TIME 实测",
            "core1 ELF 上板行为（UART/缓存/DDR 依赖 core0 ps7_init）：未验证",
            "相机帧同步/撕裂与 1280×960 变体：待相机 ELF 定稿",
            "显示 ELF 的具体相机变体与 SHA：以 video-sw 交付为准（不在本任务写区）",
        ],
    }
    p = OUT / "variant_build_mvp.json"
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] {p} sha={sha(p)}")
    for k, v in rec["variants"].items():
        print(f"[OK] {k}: {v['sha256'][:12]}… bytes={v['bytes']} _start={v['_start']} bss_end={v['bss_end']}")
    print(f"[OK] exit codes all0={all(x == 0 for x in rec['exit_codes'].values())} "
          f"({len(rec['exit_codes'])} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())