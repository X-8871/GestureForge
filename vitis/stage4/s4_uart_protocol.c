/* 阶段4 s2bu/1.1 风格 UART 打包/解包实现（S4-B）。语义见 s4_uart_protocol.h。 */

#include "s4_uart_protocol.h"

#include <string.h>

static void s4_put_u16_le(uint8_t *out, uint16_t value)
{
    out[0] = (uint8_t)(value & 0xFFu);
    out[1] = (uint8_t)((value >> 8) & 0xFFu);
}

static void s4_put_u32_le(uint8_t *out, uint32_t value)
{
    out[0] = (uint8_t)(value & 0xFFu);
    out[1] = (uint8_t)((value >> 8) & 0xFFu);
    out[2] = (uint8_t)((value >> 16) & 0xFFu);
    out[3] = (uint8_t)((value >> 24) & 0xFFu);
}

static void s4_put_u64_le(uint8_t *out, uint64_t value)
{
    s4_put_u32_le(out, (uint32_t)(value & 0xFFFFFFFFu));
    s4_put_u32_le(out + 4, (uint32_t)((value >> 32) & 0xFFFFFFFFu));
}

static uint16_t s4_get_u16_le(const uint8_t *in)
{
    return (uint16_t)((uint16_t)in[0] | ((uint16_t)in[1] << 8));
}

static uint32_t s4_get_u32_le(const uint8_t *in)
{
    return (uint32_t)in[0] | ((uint32_t)in[1] << 8) | ((uint32_t)in[2] << 16) |
           ((uint32_t)in[3] << 24);
}

static uint64_t s4_get_u64_le(const uint8_t *in)
{
    return (uint64_t)s4_get_u32_le(in) | ((uint64_t)s4_get_u32_le(in + 4) << 32);
}

/* IEEE754 binary64 的原始 8 字节 little-endian 存取（不依赖宿主端序）。 */
static void s4_put_f64_le(uint8_t *out, double value)
{
    uint64_t bits;
    memcpy(&bits, &value, sizeof(bits));
    s4_put_u64_le(out, bits);
}

static double s4_get_f64_le(const uint8_t *in)
{
    const uint64_t bits = s4_get_u64_le(in);
    double value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

uint32_t s4_uart_crc32(const uint8_t *data, size_t length)
{
    uint32_t crc = 0xFFFFFFFFu;
    size_t index;
    if (data == NULL && length != 0u) {
        return 0u;
    }
    for (index = 0u; index < length; ++index) {
        unsigned bit;
        crc ^= (uint32_t)data[index];
        for (bit = 0u; bit < 8u; ++bit) {
            if ((crc & 1u) != 0u) {
                crc = (crc >> 1) ^ 0xEDB88320u;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc ^ 0xFFFFFFFFu;
}

void s4_uart_header_pack(const s4_uart_header *header, uint8_t out[S4_UART_HEADER_BYTES])
{
    out[0] = (uint8_t)'S';
    out[1] = (uint8_t)'2';
    out[2] = (uint8_t)'B';
    out[3] = (uint8_t)'U';
    s4_put_u16_le(out + 4, header->version);
    s4_put_u16_le(out + 6, header->op);
    s4_put_u32_le(out + 8, header->sequence);
    s4_put_u32_le(out + 12, header->frame_id);
    s4_put_u32_le(out + 16, header->width);
    s4_put_u32_le(out + 20, header->height);
    s4_put_u32_le(out + 24, header->repeat_count);
    s4_put_u32_le(out + 28, header->payload_len);
    s4_put_u32_le(out + 32, header->payload_crc32);
    s4_put_u32_le(out + 36, s4_uart_crc32(out, 36u));
}

s4_uart_status s4_uart_header_unpack(const uint8_t raw[S4_UART_HEADER_BYTES], s4_uart_header *header)
{
    uint32_t declared;
    if (raw == NULL || header == NULL) {
        return S4_UART_ERR_ARGUMENT;
    }
    if (raw[0] != (uint8_t)'S' || raw[1] != (uint8_t)'2' || raw[2] != (uint8_t)'B' ||
        raw[3] != (uint8_t)'U') {
        return S4_UART_ERR_MAGIC;
    }
    header->version = s4_get_u16_le(raw + 4);
    if (header->version != S4_UART_VERSION) {
        return S4_UART_ERR_VERSION;
    }
    header->op = s4_get_u16_le(raw + 6);
    header->sequence = s4_get_u32_le(raw + 8);
    header->frame_id = s4_get_u32_le(raw + 12);
    header->width = s4_get_u32_le(raw + 16);
    header->height = s4_get_u32_le(raw + 20);
    header->repeat_count = s4_get_u32_le(raw + 24);
    header->payload_len = s4_get_u32_le(raw + 28);
    header->payload_crc32 = s4_get_u32_le(raw + 32);
    header->header_crc32 = s4_get_u32_le(raw + 36);
    declared = s4_uart_crc32(raw, 36u);
    if (declared != header->header_crc32) {
        return S4_UART_ERR_HEADER_CRC;
    }
    return S4_UART_OK;
}

void s4_uart_meta_pack(const s4_uart_meta *meta, uint8_t out[S4_UART_META_BYTES])
{
    s4_put_u64_le(out, meta->epoch);
    s4_put_u32_le(out + 8, meta->phys_status);
    s4_put_u32_le(out + 12, meta->error_code);
    s4_put_u32_le(out + 16, meta->last_reject);
    s4_put_u32_le(out + 20, meta->raw_candidate_count);
    s4_put_u32_le(out + 24, meta->box_count);
    s4_put_u32_le(out + 28, meta->repeat_index);
    s4_put_u32_le(out + 32, meta->repeat_total);
    s4_put_u32_le(out + 36, meta->response_code);
}

void s4_uart_meta_unpack(const uint8_t raw[S4_UART_META_BYTES], s4_uart_meta *meta)
{
    meta->epoch = s4_get_u64_le(raw);
    meta->phys_status = s4_get_u32_le(raw + 8);
    meta->error_code = s4_get_u32_le(raw + 12);
    meta->last_reject = s4_get_u32_le(raw + 16);
    meta->raw_candidate_count = s4_get_u32_le(raw + 20);
    meta->box_count = s4_get_u32_le(raw + 24);
    meta->repeat_index = s4_get_u32_le(raw + 28);
    meta->repeat_total = s4_get_u32_le(raw + 32);
    meta->response_code = s4_get_u32_le(raw + 36);
}

void s4_uart_box_pack(const s4_uart_box *box, uint8_t out[S4_UART_BOX_BYTES])
{
    s4_put_u32_le(out, (uint32_t)box->class_id);
    s4_put_u32_le(out + 4, (uint32_t)box->source_order);
    s4_put_f64_le(out + 8, box->score);
    s4_put_f64_le(out + 16, box->x1);
    s4_put_f64_le(out + 24, box->y1);
    s4_put_f64_le(out + 32, box->x2);
    s4_put_f64_le(out + 40, box->y2);
}

void s4_uart_box_unpack(const uint8_t raw[S4_UART_BOX_BYTES], s4_uart_box *box)
{
    box->class_id = (int32_t)s4_get_u32_le(raw);
    box->source_order = (int32_t)s4_get_u32_le(raw + 4);
    box->score = s4_get_f64_le(raw + 8);
    box->x1 = s4_get_f64_le(raw + 16);
    box->y1 = s4_get_f64_le(raw + 24);
    box->x2 = s4_get_f64_le(raw + 32);
    box->y2 = s4_get_f64_le(raw + 40);
}

int s4_uart_op_is_reserved(uint16_t op)
{
#if S4_UART_ENABLE_EXTENSION
    (void)op;
    return 0;
#else
    return op >= S4_UART_OP_EXT_BASE && (op & S4_UART_RESPONSE_FLAG) == 0u;
#endif
}

s4_uart_result_state s4_uart_result_state_from_meta(const s4_uart_meta *meta)
{
    /* 注意：DROPPED 不在此派生（单帧响应无采集侧事实；见 s4_uart_protocol.h 的枚举注释）。 */
    if (meta->response_code == S4_UART_CODE_OK) {
        return meta->box_count >= 1u ? S4_UART_STATE_OK : S4_UART_STATE_NO_HAND;
    }
    if (meta->error_code == 5u || meta->response_code == S4_UART_CODE_SOFT_DEADLINE) {
        return S4_UART_STATE_TIMEOUT;
    }
    return S4_UART_STATE_ERROR;
}

int s4_uart_meta_is_run_success(const s4_uart_meta *meta)
{
    return (meta->phys_status & S4_UART_STATUS_STATE_MASK) == S4_UART_STATUS_STATE_DONE &&
           (meta->phys_status & S4_UART_STATUS_SAFE_MASK) == S4_UART_STATUS_SAFE_MASK &&
           (meta->phys_status & S4_UART_STATUS_HEAD_VALID) != 0u &&
           (meta->phys_status & S4_UART_STATUS_UNSAFE_MASK) == 0u &&
           meta->error_code == 0u && meta->response_code == S4_UART_CODE_OK;
}

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
    size_t *out_length)
{
    s4_uart_header header;
    size_t payload_length;
    size_t offset = 0u;
    size_t index;

    if (meta == NULL || head13 == NULL || head26 == NULL || out == NULL ||
        out_length == NULL || det_count > S4_MAX_OUTPUTS ||
        det_count != (size_t)meta->box_count) {
        return S4_UART_ERR_ARGUMENT;
    }
    if (det_count != 0u && detections == NULL) {
        return S4_UART_ERR_ARGUMENT;
    }
    payload_length = (size_t)S4_UART_RUN_HEAD_PORTION + det_count * (size_t)S4_UART_BOX_BYTES;
    if (S4_UART_HEADER_BYTES + payload_length > out_capacity) {
        return S4_UART_ERR_CAPACITY;
    }

    s4_uart_meta_pack(meta, out + S4_UART_HEADER_BYTES);
    offset = S4_UART_HEADER_BYTES + S4_UART_META_BYTES;
    memcpy(out + offset, head13, S4_HEAD13_BYTES);
    offset += S4_HEAD13_BYTES;
    memcpy(out + offset, head26, S4_HEAD26_BYTES);
    offset += S4_HEAD26_BYTES;
    for (index = 0u; index < det_count; ++index) {
        s4_uart_box box;
        box.class_id = detections[index].class_id;
        box.source_order = detections[index].source_order;
        box.score = detections[index].score;
        box.x1 = detections[index].x1;
        box.y1 = detections[index].y1;
        box.x2 = detections[index].x2;
        box.y2 = detections[index].y2;
        s4_uart_box_pack(&box, out + offset);
        offset += S4_UART_BOX_BYTES;
    }

    header.version = S4_UART_VERSION;
    header.op = (uint16_t)(op | S4_UART_RESPONSE_FLAG);
    header.sequence = sequence;
    header.frame_id = frame_id;
    header.width = width;
    header.height = height;
    header.repeat_count = 1u;
    header.payload_len = (uint32_t)payload_length;
    header.payload_crc32 = s4_uart_crc32(out + S4_UART_HEADER_BYTES, payload_length);
    header.header_crc32 = 0u;
    s4_uart_header_pack(&header, out);
    *out_length = S4_UART_HEADER_BYTES + payload_length;
    return S4_UART_OK;
}

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
    size_t *box_count)
{
    s4_uart_header header;
    s4_uart_status status;
    size_t payload_length;
    size_t offset;
    size_t index;

    if (raw == NULL || length < S4_UART_HEADER_BYTES + S4_UART_RUN_HEAD_PORTION ||
        response_header == NULL || meta == NULL || head13 == NULL || head26 == NULL ||
        box_count == NULL) {
        return S4_UART_ERR_ARGUMENT;
    }
    status = s4_uart_header_unpack(raw, &header);
    if (status != S4_UART_OK) {
        return status;
    }
    if ((header.op & S4_UART_RESPONSE_FLAG) == 0u ||
        (header.op & (uint16_t)~S4_UART_RESPONSE_FLAG) != S4_UART_OP_RUN_INPUT) {
        return S4_UART_ERR_UNSUPPORTED;
    }
    if (header.sequence != expect_sequence || header.frame_id != expect_frame_id ||
        header.width != expect_width || header.height != expect_height) {
        return S4_UART_ERR_ARGUMENT;
    }
    if (header.repeat_count != 1u) {
        return S4_UART_ERR_LENGTH;
    }
    payload_length = (size_t)header.payload_len;
    if (S4_UART_HEADER_BYTES + payload_length != length) {
        return S4_UART_ERR_LENGTH;
    }
    if (s4_uart_crc32(raw + S4_UART_HEADER_BYTES, payload_length) != header.payload_crc32) {
        return S4_UART_ERR_PAYLOAD_CRC;
    }
    if (payload_length < (size_t)S4_UART_RUN_HEAD_PORTION ||
        (payload_length - (size_t)S4_UART_RUN_HEAD_PORTION) % (size_t)S4_UART_BOX_BYTES != 0u) {
        return S4_UART_ERR_LENGTH;
    }
    s4_uart_meta_unpack(raw + S4_UART_HEADER_BYTES, meta);
    if (meta->box_count !=
        (uint32_t)((payload_length - (size_t)S4_UART_RUN_HEAD_PORTION) / (size_t)S4_UART_BOX_BYTES)) {
        return S4_UART_ERR_LENGTH;
    }
    if (meta->box_count > S4_MAX_OUTPUTS) {
        return S4_UART_ERR_LENGTH;
    }
    if (meta->box_count > box_capacity) {
        return S4_UART_ERR_CAPACITY;
    }

    offset = S4_UART_HEADER_BYTES + S4_UART_META_BYTES;
    *head13 = raw + offset;
    offset += S4_HEAD13_BYTES;
    *head26 = raw + offset;
    offset += S4_HEAD26_BYTES;
    for (index = 0u; index < (size_t)meta->box_count; ++index) {
        s4_uart_box box;
        s4_uart_box_unpack(raw + offset, &box);
        if (boxes != NULL) {
            boxes[index] = box;
        }
        offset += S4_UART_BOX_BYTES;
    }
    *response_header = header;
    *box_count = (size_t)meta->box_count;
    return S4_UART_OK;
}