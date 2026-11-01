r"""生成 MVP 推理变体源：在 w4 阶段4 应用（S4-B-REAL 同一套推理路径）上定点插入

  1) S5RS 结果发布（ABI 复用阶段5 冻结头 `s5_result_abi.h`，不新增/不改布局）；
  2) 每帧 T0–T3 GT 时间戳 + `MVP TIME` 一行；
  3) 相机帧源（0x12000000 BGR888）→ D2 口径 letterbox → 416 INT8，编译期开关
     `-DS4D_FRAME_SRC_CAM=1`；=0 时保留原 host-request 主循环（相机未通可回退注入）。

fail-closed：所有锚点必须命中且只命中一次，否则退出码 11，不生成文件。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

W = Path(r"D:\codex-worktrees\w4")
OUT = Path(r"D:\tmp\lead\mvp_infer_20261031_r01")
SRC = W / "vitis" / "stage4" / "ps"
INFER = W / "tmp" / "4" / "S4-B-REAL-01" / "s4b_ps_tensor_20261023_r13" / "bundle_extract" / "bundle" / "workspace" / "infer" / "src"
ABI = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\src\s5_result_abi.h")

MVP_MACROS = r'''
/* ================= MVP（2026-10-31）：相机帧 → YOLO → S5RS 结果块 =================
 * 依据（只读）：
 *   · 结果块 ABI：`s5_result_abi.h`（阶段5 冻结，0x20800000，16 B/框，坐标 640×480）；
 *   · 帧源：相机 raw 在 0x12000000，BGR888 紧排；默认 1280×720（2,764,800 B），
 *     尺寸可用 `-DS4D_MVP_RAW_W/H` 覆盖（相机 ELF 定稿后以实测格式为准）；
 *   · 预处理：`s4d_sw_preproc_bgr888_to_chw_int8()`（D2 冻结口径，已与冻结张量逐字节对拍）；
 *   · 推理：`s2b_network_start_from_tensor()` + `s2a_decode_nms_reference()`（与 S4-B-REAL 同路径）。
 * 时间戳口径（全部 GT ticks → ms；分母已修好 S4D_MS_DIV）：
 *   t0_pre    = 预处理完成时刻
 *   t1_pl     = PL 2B 内核完成（DONE_SAFE）时刻
 *   t2_decode = 解码/NMS 完成时刻
 *   t3_pub    = S5RS 发布完成时刻
 *   dt_pre    = 预处理耗时（内部 t_begin→t0_pre）
 *   dt_pl     = t1_pl - t0_pre
 *   dt_dec    = t2_decode - t1_pl
 *   dt_all    = t3_pub - t_begin
 */
#ifndef S4D_FRAME_SRC_CAM
#define S4D_FRAME_SRC_CAM 1
#endif
#ifndef S4D_MVP_RAW_W
#define S4D_MVP_RAW_W 1280u
#endif
#ifndef S4D_MVP_RAW_H
#define S4D_MVP_RAW_H 720u
#endif
#define S4D_MVP_RAW_BYTES (S4D_MVP_RAW_W * S4D_MVP_RAW_H * 3u)
#define S4D_MVP_SESSION   0x534D5650u   /* 'SMVP'，S5RS 不消费 frame_id 以外字段 */
'''

MVP_FUNCS = r'''
/* ================= MVP 实现（必须在常量/工具函数定义之后） ================= */
_Static_assert(S4D_MVP_RAW_BYTES <= S4D_RAW_BYTES, "MVP raw frame 必须落在 RAW 区 [0x12000000,0x12C00000)");
_Static_assert(S5_RESULT_MAX_DETS >= S4D_DEC_MAX_BOX, "S5RS 容量必须 >= 解码上限（15）");
_Static_assert(S5_RESULT_ST_VALID == 0x00000001u, "S5RS status.bit0 必须为 valid=0x1（显示侧门控）");
_Static_assert((S5_RESULT_ST_VALID & 0x00000004u) == 0u, "MVP 不置 stale(bit2)，避免 47s/轮被 stale 挡显示");

static s2a_t62_detection s4d_mvp_dets[S5_RESULT_MAX_DETS];
static uint32_t s4d_mvp_ndet;

static uint32_t s4d_mvp_ms(uint64_t ticks)
{
    uint64_t ms = (ticks * 1000ull) / S4D_MS_DIV;
    return (uint32_t)ms;
}

/* 写 S5RS：先写框数据 + 头字段，flush 后再写 magic（读侧不会读到半成品，显示侧另有双读校验）。 */
static void s4d_mvp_publish(uint32_t frame_id, uint32_t ndet,
                            uint64_t t_cap, uint64_t t_inf, uint32_t status)
{
    volatile S5ResultHeader *hdr = (volatile S5ResultHeader *)(uintptr_t)S5_RESULT_BASE;
    volatile S5ResultDet *dets = (volatile S5ResultDet *)(uintptr_t)(S5_RESULT_BASE + S5_RESULT_DETS_OFFSET);
    uint32_t i;

    if (ndet > S5_RESULT_MAX_DETS) { ndet = S5_RESULT_MAX_DETS; }
    for (i = 0u; i < ndet; i++) {
        double x1 = s4d_mvp_dets[i].x1, y1 = s4d_mvp_dets[i].y1;
        double x2 = s4d_mvp_dets[i].x2, y2 = s4d_mvp_dets[i].y2;
        double s = s4d_mvp_dets[i].score;
        double w, h;
        uint32_t xs, ys, ws, hs, q;
        /* 归一化（相对相机原图 1280×720）→ 显示画布 640×480 坐标 */
        if (x1 < 0.0) x1 = 0.0;
        if (y1 < 0.0) y1 = 0.0;
        if (x2 > 1.0) x2 = 1.0;
        if (y2 > 1.0) y2 = 1.0;
        xs = (uint32_t)(x1 * (double)S5_RAW_OUT_W + 0.5);
        ys = (uint32_t)(y1 * (double)S5_RAW_OUT_H + 0.5);
        w = (x2 - x1) * (double)S5_RAW_OUT_W;
        h = (y2 - y1) * (double)S5_RAW_OUT_H;
        ws = (uint32_t)(w + 0.5);
        hs = (uint32_t)(h + 0.5);
        if (xs >= S5_RAW_OUT_W) xs = S5_RAW_OUT_W - 1u;
        if (ys >= S5_RAW_OUT_H) ys = S5_RAW_OUT_H - 1u;
        if (ws == 0u) ws = 1u;
        if (hs == 0u) hs = 1u;
        if (xs + ws > S5_RAW_OUT_W) ws = S5_RAW_OUT_W - xs;
        if (ys + hs > S5_RAW_OUT_H) hs = S5_RAW_OUT_H - ys;
        if (s < 0.0) s = 0.0;
        if (s > 1.0) s = 1.0;
        q = (uint32_t)(s * 255.0 + 0.5);
        if (q > 255u) q = 255u;
        dets[i].x = (uint16_t)xs;
        dets[i].y = (uint16_t)ys;
        dets[i].w = (uint16_t)ws;
        dets[i].h = (uint16_t)hs;
        dets[i].cls = (uint8_t)((s4d_mvp_dets[i].class_id < 0) ? 0 : s4d_mvp_dets[i].class_id);
        dets[i].score_q8 = (uint8_t)q;
        dets[i].reserved = 0u;
        dets[i].pad = 0u;
    }
    hdr->frame_id = frame_id;
    hdr->n_dets = ndet;
    hdr->cap_lo = (uint32_t)(t_cap & 0xFFFFFFFFu);
    hdr->cap_hi = (uint32_t)(t_cap >> 32);
    hdr->inf_lo = (uint32_t)(t_inf & 0xFFFFFFFFu);
    hdr->inf_hi = (uint32_t)(t_inf >> 32);
    hdr->status = status;
    s4d_region_flush(S5_RESULT_BASE, S5_RESULT_BLOCK_BYTES);
    __asm__ volatile("dsb sy" ::: "memory");
    hdr->magic = S5_RESULT_MAGIC;          /* 最后写 magic：之前的字节已 flush */
    s4d_region_flush(S5_RESULT_BASE, 32u);
    __asm__ volatile("dsb sy" ::: "memory");
}

/* 2B 引擎每帧必须 ACK 才能回到 IDLE/SAFE_REUSE；否则下一轮 START 直接返回 -2（not idle），
 * 自循环会以"每帧瞬间失败 → status=0"空转（r08/r09 现象：frame_id=0x37A、n_dets=0、status=0）。
 * S4-B 主机路径里 ACK 由 host 发 OP_ACK；MVP 自循环必须自己发：读 epoch 双读校验 → ACKLO/ACKHI → CMD=4 → 等 idle。 */
static int s4d_mvp_ack(void)
{
    uint64_t epoch = 0u;
    uint32_t spin;
    if (!s4d_read_epoch(&epoch) || epoch == UINT64_MAX) { return -1; }
    s4d_wr(S4D_CSR_ACKLO_W, (uint32_t)(epoch & 0xFFFFFFFFu));
    s4d_wr(S4D_CSR_ACKHI_W, (uint32_t)(epoch >> 32));
    s4d_wr(S4D_CSR_CMD, S4D_CMD_ACK);
    for (spin = 0u; spin < 2000000u; spin++) {
        uint32_t st = s4d_rd(S4D_CSR_STATUS);
        if (((st & 7u) == S4D_ST_IDLE) && ((st & S4D_SAFE_REUSE) != 0u) &&
            ((st & (S4D_OWNER_PL | S4D_AXI_PEND | S4D_HEAD_VALID | S4D_TERMINAL | S4D_FIRST_PEND)) == 0u)) {
            return 0;
        }
    }
    return -2;
}

/* MVP 主循环：相机 raw(0x12000000) → D2 letterbox 416 → 2B PL 网络 → 解码/NMS → S5RS。 */
__attribute__((used, noinline)) static void s4d_mvp_cam_loop(void)
{
    const uint8_t *raw = (const uint8_t *)(uintptr_t)S5_RAW_FRAME_BASE;
    int8_t *tensor = (int8_t *)(uintptr_t)S4D_TENSOR_BASE;
    uint32_t frame_id = 0u;

    xil_printf("\r\nMVP APP: CAM=%d raw=0x%08x %ux%u bgr888 bytes=%u s5rs=0x%08x\r\n",
               (int)S4D_FRAME_SRC_CAM, (unsigned)S5_RAW_FRAME_BASE,
               (unsigned)S4D_MVP_RAW_W, (unsigned)S4D_MVP_RAW_H,
               (unsigned)S4D_MVP_RAW_BYTES, (unsigned)S5_RESULT_BASE);
    {
        const uint8_t *w = (const uint8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_INPUT_BASE);
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_INPUT_BASE, 8u);
        xil_printf("MVP WEIGHTS: %s @0x%08x\r\n",
                   (memcmp(w, "GFINT8W1", 8u) == 0) ? "GFINT8W1 OK" : "MISSING(GFINT8W1)",
                   (unsigned)(S4D_TENSOR_BASE + S4D_INPUT_BASE));
    }

    for (;;) {
        uint64_t t_begin = s4d_gt_ticks();
        uint64_t t_pre, t_pl, t_dec, t_pub;
        uint32_t dt_pre, dt_pl, dt_dec, dt_all, raw_nz = 0u;
        uint32_t nz_i;
        int rc;

        /* 1) 帧源：相机 raw（BGR888，紧排）。先统计前 4 KB 非零字，判断"帧有没有进来" */
        s4d_region_invalidate(S5_RAW_FRAME_BASE, S4D_MVP_RAW_BYTES);
        {
            const volatile uint32_t *rw = (const volatile uint32_t *)(uintptr_t)S5_RAW_FRAME_BASE;
            for (nz_i = 0u; nz_i < 1024u; nz_i++) { if (rw[nz_i] != 0u) { raw_nz++; } }
        }
        /* 2) D2 冻结口径预处理：端点对齐双线性 + v/255 + 对称量化 1/127 + pad 0.5 */
        rc = s4d_sw_preproc_bgr888_to_chw_int8(raw, (int)S4D_MVP_RAW_W, (int)S4D_MVP_RAW_H, tensor);
        t_pre = s4d_gt_ticks();
        if (rc != 0) {
            xil_printf("MVP ERR preproc rc=%d frame=%u\r\n", rc, (unsigned)frame_id);
            s4d_mvp_publish(frame_id, 0u, t_begin, t_pre, 0u);
            frame_id++;
            continue;
        }
        s4d_region_flush(S4D_TENSOR_BASE, S4D_TENSOR_BYTES);

        /* 3) PL 2B 网络（DONE_SAFE 后返回） */
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF, S4D_HEAD13_BYTES);
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD26_OFF, S4D_HEAD26_BYTES);
        rc = s2b_network_start_from_tensor(S4D_MVP_SESSION, frame_id);
        t_pl = s4d_gt_ticks();
        if (rc != 0) {
            xil_printf("MVP ERR network rc=%d frame=%u\r\n", rc, (unsigned)frame_id);
            (void)s4d_mvp_ack();   /* 尽力把引擎从终态拉回 idle，避免后续每轮 -2 空转 */
            s4d_mvp_publish(frame_id, 0u, t_pre, t_pl, 0u);
            frame_id++;
            continue;
        }
        __asm__ volatile("dsb sy" ::: "memory");
        /* 3b) 每帧 ACK：释放 2B 引擎回 IDLE/SAFE_REUSE（缺失会让下一轮 START 返回 -2，status 永久 0） */
        if (s4d_mvp_ack() != 0) {
            xil_printf("MVP WARN ack failed frame=%u\r\n", (unsigned)frame_id);
        }

        /* 4) 解码/NMS（r13 冻结参考；坐标相对相机原图归一化） */
        s4d_cur_src_w = S4D_MVP_RAW_W;
        s4d_cur_src_h = S4D_MVP_RAW_H;
        rc = s2a_decode_nms_reference((const int8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD13_OFF),
                                      S4D_MVP_SESSION, frame_id,
                                      s4d_mvp_dets, &s4d_mvp_ndet);
        t_dec = s4d_gt_ticks();
        if (rc != 0) {
            xil_printf("MVP ERR decode rc=%d frame=%u\r\n", rc, (unsigned)frame_id);
            s4d_mvp_publish(frame_id, 0u, t_pre, t_pl, 0u);
            frame_id++;
            continue;
        }

        /* 5) 发布 S5RS（先数据后 magic；cap/inf 为 GT ticks）
         *   安全失败闸：raw 前 4 KB 全零（相机未通）时，零 logits 会让 sigmoid(0)*sigmoid(0)=0.25
         *   恰好命中 score>=0.25 阈值，解码器会吐出"假框"——因此显式丢弃为 n_dets=0（帧仍 valid=1，
         *   网络照跑用于验证链路），并打印 MVP NOTE raw_blank。 */
        if (raw_nz == 0u) {
            if (s4d_mvp_ndet != 0u) {
                xil_printf("MVP NOTE raw_blank n_dets=%u->0 (raw 前 4KB 全零，判定无相机帧)\r\n",
                           (unsigned)s4d_mvp_ndet);
            }
            s4d_mvp_ndet = 0u;
        }
        s4d_mvp_publish(frame_id, s4d_mvp_ndet, t_pre, t_pl,
                        S5_RESULT_ST_VALID);
        t_pub = s4d_gt_ticks();
        /* 5b) 回读自检：status 写入路径必须可观测（raw_blank 时 status 仍必须=0x1、n_dets=0） */
        {
            volatile S5ResultHeader *rb = (volatile S5ResultHeader *)(uintptr_t)S5_RESULT_BASE;
            uint32_t mg_rb, st_rb, n_rb;
            s4d_region_invalidate(S5_RESULT_BASE, 32u);
            __asm__ volatile("dsb sy" ::: "memory");
            mg_rb = rb->magic; st_rb = rb->status; n_rb = rb->n_dets;
            if ((mg_rb != S5_RESULT_MAGIC) || (st_rb != S5_RESULT_ST_VALID) || (n_rb != s4d_mvp_ndet)) {
                xil_printf("MVP ASSERT FAIL s5rs magic=0x%08x status=0x%x n=%u exp(magic=0x%08x status=0x%x n=%u)\r\n",
                           (unsigned)mg_rb, (unsigned)st_rb, (unsigned)n_rb,
                           (unsigned)S5_RESULT_MAGIC, (unsigned)S5_RESULT_ST_VALID,
                           (unsigned)s4d_mvp_ndet);
            }
            if (raw_nz == 0u) {
                xil_printf("MVP CHECK raw_blank status=0x%x n_dets=%u (exp status=0x1 n=0) %s\r\n",
                           (unsigned)st_rb, (unsigned)n_rb,
                           ((st_rb == S5_RESULT_ST_VALID) && (n_rb == 0u)) ? "OK" : "FAIL");
            }
        }
        dt_pre = s4d_mvp_ms(t_pre - t_begin);
        dt_pl = s4d_mvp_ms(t_pl - t_pre);
        dt_dec = s4d_mvp_ms(t_dec - t_pl);
        dt_all = s4d_mvp_ms(t_pub - t_begin);
        xil_printf("MVP TIME t0_pre=%u t1_pl=%u t2_decode=%u t3_pub=%u "
                   "dt_pre=%u dt_pl=%u dt_dec=%u dt_all=%u raw_nz=%u\r\n",
                   (unsigned)s4d_mvp_ms(t_pre), (unsigned)s4d_mvp_ms(t_pl),
                   (unsigned)s4d_mvp_ms(t_dec), (unsigned)s4d_mvp_ms(t_pub),
                   (unsigned)dt_pre, (unsigned)dt_pl, (unsigned)dt_dec, (unsigned)dt_all,
                   (unsigned)raw_nz);
        xil_printf("MVP S5RS frame=%u n_dets=%u magic=0x%08x status=0x%x\r\n",
                   (unsigned)frame_id, (unsigned)s4d_mvp_ndet,
                   (unsigned)((volatile S5ResultHeader *)(uintptr_t)S5_RESULT_BASE)->magic,
                   (unsigned)((volatile S5ResultHeader *)(uintptr_t)S5_RESULT_BASE)->status);
        frame_id++;
    }
}
'''

DISPATCH = r'''
#if defined(S4D_FRAME_SRC_CAM) && S4D_FRAME_SRC_CAM
    s4d_mvp_cam_loop();   /* MVP：相机帧自主循环（不返回） */
#endif
'''


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(text: str, needle: str, count: int = 1) -> None:
    n = text.count(needle)
    if n != count:
        print(f"[FAIL] 锚点命中 {n} 次（期望 {count}）：{needle!r}")
        sys.exit(11)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    src_dir = OUT / "src"
    src_dir.mkdir(exist_ok=True)
    # 1) 拷贝依赖（只读复制，不改原文件）
    copies = {
        SRC / "s4d_sw_preproc.c": src_dir / "s4d_sw_preproc.c",
        SRC / "s4d_sw_preproc.h": src_dir / "s4d_sw_preproc.h",
        SRC / "s4d_geometry.h": src_dir / "s4d_geometry.h",
        INFER / "s2a_ps_decode_nms_reference.c": src_dir / "s2a_ps_decode_nms_reference.c",
        INFER / "s2a_ps_decode_nms_reference.h": src_dir / "s2a_ps_decode_nms_reference.h",
        ABI: src_dir / "s5_result_abi.h",
    }
    for s, d in copies.items():
        if not s.is_file():
            print(f"[FAIL] 缺输入：{s}")
            return 12
        d.write_bytes(s.read_bytes())

    base = (SRC / "s4d_ps_app.c").read_bytes().decode("utf-8")
    text = base

    need(text, '#include "s2a_ps_decode_nms_reference.h"   /* r13 冻结解码参考：强符号 s2a_t62_decode_nms */')
    text = text.replace(
        '#include "s2a_ps_decode_nms_reference.h"   /* r13 冻结解码参考：强符号 s2a_t62_decode_nms */',
        '#include "s2a_ps_decode_nms_reference.h"   /* r13 冻结解码参考：强符号 s2a_t62_decode_nms */\n'
        '#include "s5_result_abi.h"   /* 阶段5 冻结结果块 ABI（0x20800000；只读引用，不改布局） */\n'
        + MVP_MACROS, 1)

    need(text, '/* ---------------- 主循环：轮询 HOST_REQ → 预处理 → 推理 → 发布 PS_RESULT ---------------- */')
    text = text.replace(
        '/* ---------------- 主循环：轮询 HOST_REQ → 预处理 → 推理 → 发布 PS_RESULT ---------------- */',
        MVP_FUNCS + '\n/* ---------------- 主循环：轮询 HOST_REQ → 预处理 → 推理 → 发布 PS_RESULT ---------------- */', 1)

    need(text, '    uint32_t last_frame = 0xFFFFFFFFu;\n    uint32_t result_seq = 0;')
    text = text.replace(
        '    uint32_t last_frame = 0xFFFFFFFFu;\n    uint32_t result_seq = 0;',
        DISPATCH + '\n    uint32_t last_frame = 0xFFFFFFFFu;\n    uint32_t result_seq = 0;', 1)

    dst = src_dir / "s4d_ps_app_mvp.c"
    dst.write_text(text, encoding="utf-8", newline="\n")
    rec = {
        "task": "S5-T01/MVP-infer",
        "generated_utc8": __import__("datetime").datetime.now(
            __import__("datetime").timezone(__import__("datetime").timedelta(hours=8))
        ).isoformat(timespec="seconds"),
        "base": {"path": str(SRC / "s4d_ps_app.c"), "sha256": sha(SRC / "s4d_ps_app.c"),
                 "bytes": (SRC / "s4d_ps_app.c").stat().st_size},
        "output": {"path": str(dst), "sha256": sha(dst), "bytes": dst.stat().st_size,
                   "lines": len(text.splitlines())},
        "inputs": {str(k): {"sha256": sha(k), "bytes": k.stat().st_size} for k in copies},
        "insertions": [
            {"id": "I1", "what": "include s5_result_abi.h + MVP 宏/发布函数/相机循环"},
            {"id": "I2", "what": "main() 内 S4D_FRAME_SRC_CAM=1 时进入 s4d_mvp_cam_loop()"},
        ],
        "switches": {"S4D_FRAME_SRC_CAM": "1=相机 0x12000000；0=回落原 host-request 注入主循环",
                     "S4D_MVP_RAW_W/H": "相机 raw 几何（默认 1280×720）"},
    }
    (OUT / "variant_transform_mvp.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] {dst} ({rec['output']['bytes']} B, sha {rec['output']['sha256'][:12]}…)")
    return 0


if __name__ == "__main__":
    sys.exit(main())