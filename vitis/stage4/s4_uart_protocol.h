/*
 * 阶段4 s2bu/1.1 风格 UART 帧打包/解包（S4-B 离线骨架）。
 *
 * 接口语义只读参考 2B 冻结正文（docs/obsidian-project/02-方案设计/s2b_board_transport.md，
 * s2bu/1.1，G0_FROZEN）与 verification/s2b_board_transport.py；本文件不改动
 * 2B 既有字段语义、顺序、端序与 CRC 定义：
 *
 *   40 B 头  : "<4sHH8I>" = magic "S2BU"、version=1、op、sequence、frame_id、
 *              width、height、repeat_count、payload_len、payload_crc32、header_crc32
 *   CRC32    : reflected polynomial 0xEDB88320，初值 0xFFFFFFFF，末异或 0xFFFFFFFF；
 *              "123456789" -> 0xCBF43926；header_crc32 覆盖前 36 B
 *   响应 op  : 请求 op | 0x8000
 *   响应 meta: "<Q8I>" 40 B = epoch(u64)、PHYS_STATUS、ERROR_CODE、LAST_REJECT、
 *              raw_candidate_count、box_count、repeat_index、repeat_total、response_code
 *   RUN 成功 : meta + head13(5070 B) + head26(20280 B) + box_count 个 "<ii5d>"（每框 48 B）
 *
 * 阶段4 需要的 result_seq/state/时间/丢帧/过期字段超出 s2bu/1.1 既有 payload
 * （见 S4-A uart_mapping.field_coverage 与 open_decision）。此处只保留
 * 位置与门闸，不启用任何新字段，也不改既有字段语义。
 */

#ifndef S4_UART_PROTOCOL_H
#define S4_UART_PROTOCOL_H

#include <stddef.h>
#include <stdint.h>

#include "s4_ps_decode.h"

#ifdef __cplusplus
extern "C" {
#endif

#define S4_UART_HEADER_BYTES 40u
#define S4_UART_META_BYTES 40u
#define S4_UART_BOX_BYTES 48u
#define S4_UART_VERSION 1u
#define S4_UART_RESPONSE_FLAG 0x8000u

/* op：1 LOAD_WEIGHTS、2 RUN_INPUT、3 IDLE_DIAGNOSTICS、4 CACHE_PROBE。 */
#define S4_UART_OP_LOAD_WEIGHTS 1u
#define S4_UART_OP_RUN_INPUT 2u
#define S4_UART_OP_IDLE_DIAGNOSTICS 3u
#define S4_UART_OP_CACHE_PROBE 4u

/* response_code：0 成功；1 坏头；2 payload CRC；3 seq；4 长度/op；5 准入状态；
 * 6 参数；7 板端/探针失败；8 软件观察期限；9 C 解码失败；10 WAIT_DAP_ABORT 中间响应。 */
#define S4_UART_CODE_OK 0u
#define S4_UART_CODE_BAD_HEADER 1u
#define S4_UART_CODE_PAYLOAD_CRC 2u
#define S4_UART_CODE_SEQUENCE 3u
#define S4_UART_CODE_LENGTH_OR_OP 4u
#define S4_UART_CODE_ADMISSION 5u
#define S4_UART_CODE_ARGUMENT 6u
#define S4_UART_CODE_BOARD_FAILURE 7u
#define S4_UART_CODE_SOFT_DEADLINE 8u
#define S4_UART_CODE_DECODE_FAILURE 9u
#define S4_UART_CODE_ABORT_READY 10u

/* PHYS_STATUS 关键位（2B 正文与 verification/s2b_board_transport.py 的定义）。 */
#define S4_UART_STATUS_STATE_MASK 0x00000007u
#define S4_UART_STATUS_STATE_DONE 4u
#define S4_UART_STATUS_HEAD_VALID (1u << 9)
#define S4_UART_STATUS_SAFE_MASK ((1u << 10) | (1u << 11))
#define S4_UART_STATUS_UNSAFE_MASK ((1u << 8) | (1u << 12) | (1u << 13))

/*
 * 离线骨架使用的合成 DONE_SAFE 状态字：state=4、HEAD_VALID、SAFE 两位置位、
 * UNSAFE 位清零。它只满足 2B decode_response 的谓词，不是板上实测状态。
 */
#define S4_UART_PHYS_STATUS_DONE_SAFE \
    (S4_UART_STATUS_STATE_DONE | S4_UART_STATUS_HEAD_VALID | S4_UART_STATUS_SAFE_MASK)

/* RUN 成功响应的精确字节数：40 + 40 + 5070 + 20280 + 48 * box_count。 */
#define S4_UART_RUN_HEAD_PORTION (S4_UART_META_BYTES + S4_HEAD13_BYTES + S4_HEAD26_BYTES)

/*
 * 阶段4 扩展预留（默认禁用）：
 * S4-A uart_mapping.open_decision 仍为 OPEN_AWAITING_DECISION（选项 A：新 op/TLV）。
 * 在新决策落地前，任何扩展 op 都必须被拒绝，既有字段语义保持 2B 冻结原样。
 */
#define S4_UART_OP_EXT_BASE 0x0100u
#define S4_UART_ENABLE_EXTENSION 0

typedef enum {
    S4_UART_OK = 0,
    S4_UART_ERR_ARGUMENT = -1,
    S4_UART_ERR_MAGIC = -2,
    S4_UART_ERR_VERSION = -3,
    S4_UART_ERR_HEADER_CRC = -4,
    S4_UART_ERR_PAYLOAD_CRC = -5,
    S4_UART_ERR_LENGTH = -6,
    S4_UART_ERR_CAPACITY = -7,
    S4_UART_ERR_UNSUPPORTED = -8
} s4_uart_status;

/* 结果状态（S4-A state_enum），由 s2bu/1.1 既有字段派生，不新增传输字段。
 *
 * DROPPED 不能由单帧响应派生（它需要“采集侧存在该帧但未产生结果”的事实，而 gf 响应
 * 只描述已产生的这一个结果），因此 s4_uart_result_state_from_meta() 永不返回 DROPPED；
 * 保留该枚举仅为与 S4-A state_enum 对称及未来扩展（多帧/采集侧记录）。 */
typedef enum {
    S4_UART_STATE_OK = 0,
    S4_UART_STATE_NO_HAND = 1,
    S4_UART_STATE_TIMEOUT = 2,
    S4_UART_STATE_ERROR = 3,
    S4_UART_STATE_DROPPED = 4
} s4_uart_result_state;

typedef struct {
    uint16_t version;
    uint16_t op;
    uint32_t sequence;
    uint32_t frame_id;
    uint32_t width;
    uint32_t height;
    uint32_t repeat_count;
    uint32_t payload_len;
    uint32_t payload_crc32;
    uint32_t header_crc32;
} s4_uart_header;

typedef struct {
    uint64_t epoch;
    uint32_t phys_status;
    uint32_t error_code;
    uint32_t last_reject;
    uint32_t raw_candidate_count;
    uint32_t box_count;
    uint32_t repeat_index;
    uint32_t repeat_total;
    uint32_t response_code;
} s4_uart_meta;

typedef struct {
    int32_t class_id;
    int32_t source_order;
    double score;
    double x1;
    double y1;
    double x2;
    double y2;
} s4_uart_box;

/* IEEE CRC32：reflected 0xEDB88320、初值 0xFFFFFFFF、末异或 0xFFFFFFFF。 */
uint32_t s4_uart_crc32(const uint8_t *data, size_t length);

void s4_uart_header_pack(const s4_uart_header *header, uint8_t out[S4_UART_HEADER_BYTES]);
s4_uart_status s4_uart_header_unpack(const uint8_t raw[S4_UART_HEADER_BYTES], s4_uart_header *header);

void s4_uart_meta_pack(const s4_uart_meta *meta, uint8_t out[S4_UART_META_BYTES]);
void s4_uart_meta_unpack(const uint8_t raw[S4_UART_META_BYTES], s4_uart_meta *meta);

void s4_uart_box_pack(const s4_uart_box *box, uint8_t out[S4_UART_BOX_BYTES]);
void s4_uart_box_unpack(const uint8_t raw[S4_UART_BOX_BYTES], s4_uart_box *box);

/* 扩展 op 门闸：启用前恒返回 1（拒绝）。 */
int s4_uart_op_is_reserved(uint16_t op);

/* 由既有响应字段派生 S4-A state（不新增传输字段）。 */
s4_uart_result_state s4_uart_result_state_from_meta(const s4_uart_meta *meta);

/* 该 meta 是否满足 2B RUN 成功谓词（DONE_SAFE + HEAD_VALID + 无 UNSAFE + error 0 + code 0）。 */
int s4_uart_meta_is_run_success(const s4_uart_meta *meta);

/*
 * 组装 RUN 成功响应帧（头部 op = 请求 op | 0x8000，payload 按冻结顺序拼接）。
 * detections 只取前 det_count 个，det_count 必须 <= 15，且必须等于 meta->box_count。
 * out_length 返回实际写入字节数。容量不足返回 S4_UART_ERR_CAPACITY。
 */
s4_uart_status s4_uart_pack_run_response(
    uint32_t sequence,
    uint32_t frame_id,
    uint32_t width,
    uint32_t height,
    uint32_t op,
    s4_uart_meta *meta,
    const int8_t *head13,
    const int8_t *head26,
    const s4_detection *detections,
    size_t det_count,
    uint8_t *out,
    size_t out_capacity,
    size_t *out_length);

/*
 * 解包并核对一个 RUN 成功响应帧：头 CRC、payload CRC、op|0x8000、sequence、
 * frame_id/几何、payload 长度、双头长度。head13/head26 返回帧内指针（指向 raw，
 * 只读）。boxes 可为 NULL（此时 box_capacity 必须为 0），仅校验框字节数。
 */
s4_uart_status s4_uart_unpack_run_response(
    const uint8_t *raw,
    size_t length,
    uint32_t expect_sequence,
    uint32_t expect_frame_id,
    uint32_t expect_width,
    uint32_t expect_height,
    s4_uart_header *response_header,
    s4_uart_meta *meta,
    const uint8_t **head13,
    const uint8_t **head26,
    s4_uart_box *boxes,
    size_t box_capacity,
    size_t *box_count);

#ifdef __cplusplus
}
#endif

#endif /* S4_UART_PROTOCOL_H */