/*
 * s5_publish_abi.h —— 生产者 v2 的 **sidecar 扩展**（阶段6 6-D 口径冻结 2026-10-30）
 *
 * 定位：不修改冻结的 32 B 显示 ABI（`s5_result_abi.h`），在结果块基址 +0x100 旁挂 32 B 的 `S5X1`。
 *   身份 A（Wong 2026-10-31 裁定，正式）：sidecar 基址 = 0x20800000 + 0x100（32 B）。
 *   32 B 头 + 16×16 B 项 = ABI 物理上限 0x120；sidecar 在 +0x100 处**故意覆盖第 14/15 号检测项槽位**
 *   （各 16 B），因此生产者限定 **n_dets ≤ 14**（>14 fail-closed 拒绝发布，禁止静默截断）。
 *   flush 范围 = [0x20800000, 0x20800120) = 288 B = 头 + 14 项（0x100）+ sidecar（0x20）。
 *
 * 原子发布（seqlock）：seqlock++（奇）→ 写头/项/sidecar（result_time 最后写）→ flush → seqlock++（偶）。
 * 消费者：读 seqlock（须偶）→ invalidate → 读整块 → 再读 seqlock（须偶且相同），否则重试（≤3，超限 TIMEOUT）。
 * 旧生产者未实现 seqlock（两次都读 0）→ 消费者按非原子路径处理（不声称原子）。
 */
#ifndef S5_PUBLISH_ABI_H
#define S5_PUBLISH_ABI_H

#include <stdint.h>

#include "s5_result_abi.h"

#define S5_PUB_SIDECAR_OFFSET 0x0100u
#define S5_PUB_SIDECAR_BASE (S5_RESULT_BASE + S5_PUB_SIDECAR_OFFSET) /* 0x20800100（身份 A） */
#define S5_PUB_SIDECAR_BYTES 32u
/* 发布范围 = sidecar 末尾（0x120 = 288 B = 头/14 项 0x100 + sidecar 32）：一次 flush 覆盖头、项、sidecar */
#define S5_PUB_PUBLISH_BYTES (S5_PUB_SIDECAR_OFFSET + S5_PUB_SIDECAR_BYTES)

#define S5_PUB_MAGIC2 0x53355831u /* "S5X1" */
#define S5_PUB_VERSION 1u

/* sidecar 字索引（偏移/4） */
#define S5_PUB_W_MAGIC2 0u
#define S5_PUB_W_VERSION 1u
#define S5_PUB_W_SESSION_ID 2u
#define S5_PUB_W_RESULT_SEQ 3u
#define S5_PUB_W_RTIME_LO 4u
#define S5_PUB_W_RTIME_HI 5u
#define S5_PUB_W_SEQLOCK 6u
#define S5_PUB_W_RESERVED 7u

#define S5_PUB_SEQ_LAST 0xFFFFFFFFu /* 0xFFFFFFFF→0 一律拒绝；0xFFFFFFFE→0xFFFFFFFF 正常 */
#define S5_PUB_SESSION_RETRY_MAX 8u /* session_id 碰撞时 +1 重试上限 */
/* n_dets 上限（身份 A，fail-closed）：>14 时生产端拒绝发布并置 status.overrun=1，打印 S5PROD REJECT n_dets。
 * 限制原因：sidecar 位于 +0x100，覆盖检测项槽位 14、15（各 16 B）；故可用槽位只有 0..13。 */
#define S5_PUB_NDETS_MAX 14u
#define S5_PUB_ITEMS_BYTES 0x0100u /* 头 32 B + 14×16 B 项：sidecar 起点 */

/* fail-closed 判定（主机可自检）：0=允许发布，-1=拒绝 */
static inline int S5Pub_NDetsOk(uint32_t n_dets)
{
    return (n_dets <= S5_PUB_NDETS_MAX) ? 0 : -1;
}

/* 身份 A 编译期断言：sidecar 在 +0x100，发布/flush 恰好 0x120（288 B） */
_Static_assert(S5_PUB_SIDECAR_BASE == 0x20800100u, "身份 A: sidecar 基址必须为 0x20800100");
_Static_assert(S5_PUB_PUBLISH_BYTES == 0x120u, "身份 A: 发布/flush 范围必须为 0x120");

/* 业务状态（冻结口径 §2，优先级自上而下） */
#define S5_BIZ_OK 0u
#define S5_BIZ_NO_HAND 1u
#define S5_BIZ_TIMEOUT 2u
#define S5_BIZ_ERROR 3u

/* 交互 200 ms 门限（冻结口径，与显示侧“超 1 帧 stale”不同） */
#define S5_BIZ_AGE_LIMIT_MS 200u

/* 生产者故障注入（编译期；默认 none）：
 *   0=none 1=overrun 2=stale 3=invalid 4=no_hand 5=按相位循环（none→no_hand→stale→overrun→invalid）
 * 用于 6-E E4 异常路径取证。 */
#define S5_PROD_FAULT_NONE 0
#define S5_PROD_FAULT_OVERRUN 1
#define S5_PROD_FAULT_STALE 2
#define S5_PROD_FAULT_INVALID 3
#define S5_PROD_FAULT_NO_HAND 4
#define S5_PROD_FAULT_CYCLE 5

/* 纯函数（主机可自检） */
/* ================= rev4：seqlock 严格顺序（写者/消费者统一走这两个函数） =================
 * 写者（冻结顺序）：
 *   ① seqlock++（奇） → 单独 clean/flush 该 4 B 锁行 → DSB
 *   ② 写 32 B 头 + 检测项（≤14）+ sidecar 非时间字段 → 最后写 result_time
 *   ③ clean/flush [0x20800000,0x20800120)（288 B）→ DSB
 *   ④ seqlock++（偶） → clean/flush 锁行 → DSB
 * 消费者（冻结顺序）：
 *   ① 先 invalidate（锁行 + payload 区间）
 *   ② 读 seqlock(s1)，奇则重试（≤3）
 *   ③ 读 payload → DMB
 *   ④ 再读 seqlock(s2)，要求 s1==s2 且为偶，否则重试（≤3，超限 TIMEOUT）
 * 禁止"只读一次锁"或"先取锁后 invalidate"。 */
typedef struct S5PubMem {
    void *ctx;
    volatile uint32_t *payload; /* 指向 0x20800000；host 自检用普通内存 */
    void (*flush)(void *ctx, const volatile void *addr, uint32_t bytes);      /* clean/flush */
    void (*invalidate)(void *ctx, const volatile void *addr, uint32_t bytes); /* invalidate */
    void (*barrier)(void *ctx); /* 写者 DSB / 消费者读后 DMB */
} S5PubMem;

/* 写者：blk = 完整 0x120 镜像（PackBlock + PackSidecar，rtime/锁字段可填 0）；sl = seqlock 计数（偶）。
 * 返回 0=发布完成；-1=参数/起始状态错误。 */
int S5Pub_WritePublish(S5PubMem *m, uint32_t *sl, const uint32_t *blk, uint64_t result_time_ticks);

/* 消费者可观测轨迹（v5：仅观测，不改变协议）：用于 S5CONS 打印与 E6-A 取证 */
typedef struct S5PubReadTrace {
    uint32_t attempts; /* 总尝试次数（1..3） */
    uint32_t retries;  /* 重试次数 = attempts-1（0..2） */
    uint32_t s1_last;  /* 最后一次尝试读到的第一次锁值（须偶才算有效） */
    uint32_t s2_last;  /* 最后一次尝试读到的第二次锁值（与 s1 不同即撕裂） */
} S5PubReadTrace;

/* 消费者：blk_out = 0x120 输出缓冲；sl_out = 读到的稳定 seqlock 值；tr 可为 NULL。
 * 返回 0=一致（s1==s2 且为偶）；-1=重试超限（TIMEOUT）/参数错误。 */
int S5Pub_ReadPublish(S5PubMem *m, uint32_t *blk_out, uint32_t *sl_out, S5PubReadTrace *tr);

const char *S5Pub_StateName(uint32_t state);

/* 打包 sidecar 的 8 个 u32（seqlock/result_time 由调用方按协议填） */
void S5Pub_PackSidecar(uint32_t *sc, uint32_t session_id, uint32_t result_seq,
                       uint64_t result_time_ticks, uint32_t seqlock);

/* result_seq 递增规则：last → *out。
 * 返回 0=接受（*out = last+1，0xFFFFFFFE→0xFFFFFFFF 正常）；-1=拒绝（0xFFFFFFFF→0，或新值 ≤ last）。 */
int S5Pub_NextSeq(uint32_t last, uint32_t *out);

/* age_publish = (now - result_time) × 1000 / COUNTS_PER_SECOND（ms，下取整；时间戳为 0/未来 → 0） */
uint32_t S5Pub_AgePublishMs(uint64_t now_ticks, uint64_t result_time_ticks);

/* 消费者视角的一帧快照（头 + sidecar） */
typedef struct S5PubView {
    uint32_t status;      /* 32 B 头里的 status */
    uint32_t n_dets;      /* 32 B 头里的 n_dets */
    uint32_t session_id;  /* sidecar */
    uint32_t result_seq;  /* sidecar */
    uint32_t seqlock;     /* sidecar：偶=稳定 */
    uint64_t result_time; /* sidecar：发布完成时刻 GT ticks */
} S5PubView;

/* 业务状态映射（冻结口径 §2，优先级：valid=0 → ERROR；overrun → ERROR；stale 或 age>200ms → TIMEOUT；
 * valid=1 && n_dets=0 → NO_HAND；否则 OK） */
uint32_t S5Pub_BizState(const S5PubView *v, uint32_t age_publish_ms);

/* seqlock 一致性判定：0=一致（偶且相同）/ -1=不一致（奇或两次不同，调用方重试） */
int S5Pub_SeqlockStable(uint32_t s_first, uint32_t s_second);

#endif /* S5_PUBLISH_ABI_H */