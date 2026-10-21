/*
 * 阶段4 S4-B 离线主机 CLI（冻结 heads -> 解码/NMS -> s2bu 风格帧 -> 解帧回读 -> 结果 JSON）。
 *
 * 本程序是离线骨架：不接触 UART、不接触 JTAG/hw_server、不启动 Vivado。
 * 它读取由 scripts/stage4_s4b/run_s4b_offline_chain.py 从 2A T25 冻结分片
 * 抽取并做哈希绑定的 heads bundle，输出：
 *   - S4-A 命名的结果字段 JSON（result_record.fields / detection_record.fields）
 *   - 可选：完整 s2bu/1.1 风格 RUN 成功响应帧原字节（--frame）
 *   - 可选：入参 INT8 原字节副本（--heads-dir，供外部逐字节哈希核对“进出一致”）
 *
 * bundle 格式（little-endian，全部为无符号小端字段）：
 *   0  8  magic "S4BUNDL1"
 *   8  4  version = 1
 *   12 4  geometry.width
 *   16 4  geometry.height
 *   20 4  frame_id
 *   24 4  sequence
 *   28 4  head13_len
 *   32 4  head26_len
 *   36 8  score_threshold (IEEE754 binary64)
 *   44 8  head13_scale    (IEEE754 binary64)
 *   52 8  head26_scale    (IEEE754 binary64)
 *   60 4  blob_crc32 (head13 || head26 的 IEEE CRC32)
 *   64 4  candidate_limit
 *   68 4  result_seq
 *   72 N  head13 raw INT8 字节
 *   72+head13_len  head26 raw INT8 字节
 *
 * 退出码：0 成功；2 用法错误；3 自检失败；4 文件/IO 错误；5 解码/协议错误；
 *         6 候选数达到缓冲上限（S4-A 硬错误路径，tiny416 固定配置下不可达）。
 *
 * 未执行/不适用：板上真实串口、真实期限、PL 时间戳、2B 验收均不在本程序范围；
 * 时间字段在 JSON 中以 0 哨兵（未观测）输出并列在 unavailable_fields 中，绝不伪造实测值。
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "s4_ps_decode.h"
#include "s4_uart_protocol.h"

#define S4_HOST_BUNDLE_MAGIC "S4BUNDL1"
#define S4_HOST_BUNDLE_VERSION 1u
#define S4_HOST_BUNDLE_HEADER_BYTES 72u
/* 完整 RUN 成功响应帧上限：40 + 40 + 5070 + 20280 + 15*48 = 26150 B。 */
#define S4_HOST_MAX_FRAME_BYTES \
    (S4_UART_HEADER_BYTES + S4_UART_RUN_HEAD_PORTION + S4_MAX_OUTPUTS * S4_UART_BOX_BYTES)
#define S4_HOST_MAX_TEXT 128u
#define S4_HOST_MAX_PATH 1024u

static const char *const S4_HOST_CLASS_NAMES[5] = {"fist", "palm", "one", "two_up", "three"};

typedef struct {
    uint32_t width;
    uint32_t height;
    uint32_t frame_id;
    uint32_t sequence;
    uint32_t head13_len;
    uint32_t head26_len;
    double score_threshold;
    double head13_scale;
    double head26_scale;
    uint32_t blob_crc32;
    uint32_t candidate_limit;
    uint32_t result_seq;
    uint8_t *blob;
    size_t blob_length;
} s4_bundle;

static uint32_t read_u32_le(const uint8_t *raw)
{
    return (uint32_t)raw[0] | ((uint32_t)raw[1] << 8) | ((uint32_t)raw[2] << 16) |
           ((uint32_t)raw[3] << 24);
}

static double read_f64_le(const uint8_t *raw)
{
    const uint64_t bits = (uint64_t)read_u32_le(raw) | ((uint64_t)read_u32_le(raw + 4) << 32);
    double value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static int read_entire_file(const char *path, uint8_t **out_data, size_t *out_length)
{
    FILE *stream = fopen(path, "rb");
    long size;
    uint8_t *data;
    if (stream == NULL) {
        fprintf(stderr, "[s4_host] 无法打开文件：%s\n", path);
        return -1;
    }
    if (fseek(stream, 0L, SEEK_END) != 0) {
        fclose(stream);
        return -1;
    }
    size = ftell(stream);
    if (size < 0) {
        fclose(stream);
        return -1;
    }
    if (fseek(stream, 0L, SEEK_SET) != 0) {
        fclose(stream);
        return -1;
    }
    data = (uint8_t *)malloc((size_t)size == 0u ? 1u : (size_t)size);
    if (data == NULL) {
        fclose(stream);
        return -1;
    }
    if ((size_t)size != 0u && fread(data, 1u, (size_t)size, stream) != (size_t)size) {
        free(data);
        fclose(stream);
        return -1;
    }
    fclose(stream);
    *out_data = data;
    *out_length = (size_t)size;
    return 0;
}

static int write_entire_file(const char *path, const uint8_t *data, size_t length)
{
    FILE *stream = fopen(path, "wb");
    if (stream == NULL) {
        fprintf(stderr, "[s4_host] 无法写入文件：%s\n", path);
        return -1;
    }
    if (length != 0u && fwrite(data, 1u, length, stream) != length) {
        fclose(stream);
        return -1;
    }
    if (fclose(stream) != 0) {
        return -1;
    }
    return 0;
}

static int load_bundle(const char *path, s4_bundle *bundle)
{
    uint8_t *raw = NULL;
    size_t length = 0u;
    memset(bundle, 0, sizeof(*bundle));
    if (read_entire_file(path, &raw, &length) != 0) {
        return 4;
    }
    if (length < S4_HOST_BUNDLE_HEADER_BYTES ||
        memcmp(raw, S4_HOST_BUNDLE_MAGIC, 8u) != 0) {
        fprintf(stderr, "[s4_host] bundle magic/长度错误：%s\n", path);
        free(raw);
        return 4;
    }
    if (read_u32_le(raw + 8) != S4_HOST_BUNDLE_VERSION) {
        fprintf(stderr, "[s4_host] bundle version 不受支持：%u\n", read_u32_le(raw + 8));
        free(raw);
        return 4;
    }
    bundle->width = read_u32_le(raw + 12);
    bundle->height = read_u32_le(raw + 16);
    bundle->frame_id = read_u32_le(raw + 20);
    bundle->sequence = read_u32_le(raw + 24);
    bundle->head13_len = read_u32_le(raw + 28);
    bundle->head26_len = read_u32_le(raw + 32);
    bundle->score_threshold = read_f64_le(raw + 36);
    bundle->head13_scale = read_f64_le(raw + 44);
    bundle->head26_scale = read_f64_le(raw + 52);
    bundle->blob_crc32 = read_u32_le(raw + 60);
    bundle->candidate_limit = read_u32_le(raw + 64);
    bundle->result_seq = read_u32_le(raw + 68);

    if (bundle->head13_len != S4_HEAD13_BYTES || bundle->head26_len != S4_HEAD26_BYTES ||
        bundle->width == 0u || bundle->height == 0u ||
        length != (size_t)S4_HOST_BUNDLE_HEADER_BYTES +
                      (size_t)bundle->head13_len + (size_t)bundle->head26_len) {
        fprintf(stderr, "[s4_host] bundle 头几何/长度与阶段4 冻结值不符\n");
        free(raw);
        return 4;
    }
    bundle->blob = raw + S4_HOST_BUNDLE_HEADER_BYTES;
    bundle->blob_length = (size_t)bundle->head13_len + (size_t)bundle->head26_len;
    if (s4_uart_crc32(bundle->blob, bundle->blob_length) != bundle->blob_crc32) {
        fprintf(stderr, "[s4_host] bundle 数据 CRC32 不匹配\n");
        free(raw);
        return 4;
    }
    bundle->blob = (uint8_t *)malloc(bundle->blob_length);
    if (bundle->blob == NULL) {
        free(raw);
        return 4;
    }
    memcpy(bundle->blob, raw + S4_HOST_BUNDLE_HEADER_BYTES, bundle->blob_length);
    free(raw);
    return 0;
}

/* ------------------------------------------------------------------ 自检 */

typedef struct {
    int passed;
    int failed;
    FILE *json;
} s4_selftest_report;

static void selftest_record(s4_selftest_report *report, const char *name, int pass,
                            const char *expected, const char *actual)
{
    if (pass) {
        ++report->passed;
    } else {
        ++report->failed;
    }
    if (report->json != NULL) {
        fprintf(report->json,
                "    {\"name\": \"%s\", \"pass\": %s, \"expected\": \"%s\", \"actual\": \"%s\"},\n",
                name, pass ? "true" : "false", expected, actual);
    }
}

static void hex32(char *buffer, size_t capacity, uint32_t value)
{
    snprintf(buffer, capacity, "0x%08X", value);
}

/* 手工十进制格式化 u64：避免宿主 msvcrt 不支持 "%llu"（PS 侧 newlib 与新宿主都可移植）。 */
static void decimal_u64(char *buffer, size_t capacity, uint64_t value)
{
    char reversed[24];
    size_t count = 0u;
    size_t index;
    if (capacity == 0u) {
        return;
    }
    if (value == 0u) {
        if (capacity >= 2u) {
            buffer[0] = '0';
            buffer[1] = '\0';
        } else {
            buffer[0] = '\0';
        }
        return;
    }
    while (value != 0u && count < sizeof(reversed)) {
        reversed[count] = (char)('0' + (char)(value % 10u));
        value /= 10u;
        ++count;
    }
    if (count + 1u > capacity) {
        buffer[0] = '\0';
        return;
    }
    for (index = 0u; index < count; ++index) {
        buffer[index] = reversed[count - 1u - index];
    }
    buffer[count] = '\0';
}

static int run_selftest(const char *json_path)
{
    s4_selftest_report report;
    char expected[S4_HOST_MAX_TEXT];
    char actual[S4_HOST_MAX_TEXT];
    uint8_t head13[S4_HEAD13_BYTES];
    uint8_t head26[S4_HEAD26_BYTES];
    size_t index;
    uint8_t frame[S4_HOST_MAX_FRAME_BYTES];
    size_t frame_length = 0u;
    s4_uart_header header;
    s4_uart_header unpacked_header;
    s4_uart_meta meta;
    s4_uart_meta unpacked_meta;
    s4_uart_box box;
    s4_uart_box unpacked_box;
    s4_uart_box readback_boxes[3];
    s4_detection detections[3];
    const uint8_t *read_head13 = NULL;
    const uint8_t *read_head26 = NULL;
    size_t read_box_count = 0u;
    uint8_t repack[S4_HOST_MAX_FRAME_BYTES];
    size_t repack_length = 0u;
    int all_pass;
    int rc = 0;

    memset(&report, 0, sizeof(report));
    report.json = fopen(json_path, "wb");
    if (report.json == NULL) {
        fprintf(stderr, "[s4_host] 无法写入自检 JSON：%s\n", json_path);
        return 4;
    }
    fprintf(report.json, "{\n");
    fprintf(report.json, "  \"schema_version\": \"gestureforge_s4b_offline_selftest_v1\",\n");
    fprintf(report.json, "  \"mode\": \"selftest\",\n");
    fprintf(report.json, "  \"checks\": [\n");

    /* 1. CRC32 检查向量：123456789 -> 0xCBF43926 */
    {
        static const uint8_t vector[] = {'1', '2', '3', '4', '5', '6', '7', '8', '9'};
        const uint32_t crc = s4_uart_crc32(vector, sizeof(vector));
        hex32(expected, sizeof(expected), 0xCBF43926u);
        hex32(actual, sizeof(actual), crc);
        selftest_record(&report, "crc32_check_vector_123456789", crc == 0xCBF43926u, expected, actual);
    }
    /* 2. CRC32 空串 -> 0 */
    {
        const uint32_t crc = s4_uart_crc32(NULL, 0u);
        hex32(expected, sizeof(expected), 0u);
        hex32(actual, sizeof(actual), crc);
        selftest_record(&report, "crc32_empty", crc == 0u, expected, actual);
    }
    /* 3. 头部 pack -> unpack 回读一致 + 逐字节 LE 布局 */
    {
        uint8_t raw_header[S4_UART_HEADER_BYTES];
        int pass;
        header.version = S4_UART_VERSION;
        header.op = (uint16_t)(S4_UART_OP_RUN_INPUT | S4_UART_RESPONSE_FLAG);
        header.sequence = 0x01020304u;
        header.frame_id = 0x0A0B0C0Du;
        header.width = 1440u;
        header.height = 1920u;
        header.repeat_count = 1u;
        header.payload_len = 25390u;
        header.payload_crc32 = 0xDEADBEEFu;
        header.header_crc32 = 0u;
        s4_uart_header_pack(&header, raw_header);
        pass = s4_uart_header_unpack(raw_header, &unpacked_header) == S4_UART_OK &&
               unpacked_header.op == header.op && unpacked_header.sequence == header.sequence &&
               unpacked_header.frame_id == header.frame_id && unpacked_header.width == 1440u &&
               unpacked_header.height == 1920u && unpacked_header.repeat_count == 1u &&
               unpacked_header.payload_len == 25390u &&
               unpacked_header.payload_crc32 == 0xDEADBEEFu &&
               unpacked_header.header_crc32 == s4_uart_crc32(raw_header, 36u) &&
               memcmp(raw_header, "S2BU", 4u) == 0 && raw_header[4] == 1u &&
               raw_header[6] == 0x02u && raw_header[7] == 0x80u && raw_header[8] == 0x04u &&
               raw_header[9] == 0x03u && raw_header[10] == 0x02u && raw_header[11] == 0x01u;
        snprintf(expected, sizeof(expected), "pack==unpack且LE布局正确");
        snprintf(actual, sizeof(actual), "%s", pass ? "一致" : "不一致");
        selftest_record(&report, "header_pack_unpack_roundtrip", pass, expected, actual);
        /* 篡改一个字节必须被 header CRC 拒绝 */
        raw_header[12] ^= 0x01u;
        pass = s4_uart_header_unpack(raw_header, &unpacked_header) == S4_UART_ERR_HEADER_CRC;
        snprintf(expected, sizeof(expected), "拒绝S4_UART_ERR_HEADER_CRC");
        snprintf(actual, sizeof(actual), "%s", pass ? "已拒绝" : "未拒绝");
        selftest_record(&report, "header_crc_rejects_tamper", pass, expected, actual);
        /* 错误 magic 必须被拒绝 */
        raw_header[0] = (uint8_t)'X';
        pass = s4_uart_header_unpack(raw_header, &unpacked_header) == S4_UART_ERR_MAGIC;
        snprintf(expected, sizeof(expected), "拒绝S4_UART_ERR_MAGIC");
        snprintf(actual, sizeof(actual), "%s", pass ? "已拒绝" : "未拒绝");
        selftest_record(&report, "header_rejects_bad_magic", pass, expected, actual);
    }
    /* 4. meta pack -> unpack 回读一致 + 长度 40 */
    {
        uint8_t raw_meta[S4_UART_META_BYTES];
        int pass;
        meta.epoch = 0x1122334455667788ull;
        meta.phys_status = S4_UART_PHYS_STATUS_DONE_SAFE;
        meta.error_code = 0u;
        meta.last_reject = 0u;
        meta.raw_candidate_count = 12675u;
        meta.box_count = 3u;
        meta.repeat_index = 0u;
        meta.repeat_total = 1u;
        meta.response_code = S4_UART_CODE_OK;
        s4_uart_meta_pack(&meta, raw_meta);
        s4_uart_meta_unpack(raw_meta, &unpacked_meta);
        pass = memcmp(&meta, &unpacked_meta, sizeof(meta)) == 0 &&
               raw_meta[0] == 0x88u && raw_meta[7] == 0x11u && raw_meta[8] == 0x04u &&
               raw_meta[9] == 0x0Eu && s4_uart_meta_is_run_success(&meta) == 1;
        snprintf(expected, sizeof(expected), "meta回读一致且RUN成功谓词成立");
        snprintf(actual, sizeof(actual), "%s", pass ? "一致" : "不一致");
        selftest_record(&report, "meta_pack_unpack_roundtrip", pass, expected, actual);
    }
    /* 5. 单框 pack -> unpack 回读一致（含负 class_id 字段宽度与 binary64 逐位） */
    {
        uint8_t raw_box[S4_UART_BOX_BYTES];
        int pass;
        box.class_id = 3;
        box.source_order = 6302;
        box.score = 0.49964644915172746;
        box.x1 = 0.7053431486534868;
        box.y1 = 0.3119120420071644;
        box.x2 = 0.7790610973714354;
        box.y2 = 0.4307042652355936;
        s4_uart_box_pack(&box, raw_box);
        s4_uart_box_unpack(raw_box, &unpacked_box);
        pass = unpacked_box.class_id == box.class_id && unpacked_box.source_order == box.source_order &&
               unpacked_box.score == box.score && unpacked_box.x1 == box.x1 &&
               unpacked_box.y1 == box.y1 && unpacked_box.x2 == box.x2 && unpacked_box.y2 == box.y2 &&
               raw_box[0] == 3u && raw_box[4] == 0x9Eu && raw_box[5] == 0x18u;
        snprintf(expected, sizeof(expected), "48B逐位一致");
        snprintf(actual, sizeof(actual), "%s", pass ? "一致" : "不一致");
        selftest_record(&report, "box_pack_unpack_roundtrip", pass, expected, actual);
    }
    /* 6. RUN 成功响应帧 pack -> unpack -> re-pack 字节一致（含双头与 3 框） */
    {
        int pass;
        int repack_pass;
        for (index = 0u; index < S4_HEAD13_BYTES; ++index) {
            head13[index] = (uint8_t)(int8_t)((int)(index % 251) - 125);
        }
        for (index = 0u; index < S4_HEAD26_BYTES; ++index) {
            head26[index] = (uint8_t)(int8_t)((int)((index * 7u) % 253) - 126);
        }
        for (index = 0u; index < 3u; ++index) {
            detections[index].class_id = (int32_t)index;
            detections[index].source_order = (int32_t)(index * 5 + index);
            detections[index].score = 0.9 - 0.1 * (double)index;
            detections[index].x1 = 0.1 * (double)index;
            detections[index].y1 = 0.2;
            detections[index].x2 = 0.1 * (double)index + 0.3;
            detections[index].y2 = 0.6;
        }
        meta.epoch = 1u;
        meta.phys_status = S4_UART_PHYS_STATUS_DONE_SAFE;
        meta.error_code = 0u;
        meta.last_reject = 0u;
        meta.raw_candidate_count = 42u;
        meta.box_count = 3u;
        meta.repeat_index = 0u;
        meta.repeat_total = 1u;
        meta.response_code = S4_UART_CODE_OK;
        pass = s4_uart_pack_run_response(7u, 5u, 1440u, 1920u, S4_UART_OP_RUN_INPUT, &meta,
                                        (const int8_t *)head13, (const int8_t *)head26,
                                        detections, 3u, frame, sizeof(frame), &frame_length) ==
                   S4_UART_OK &&
               frame_length == S4_UART_HEADER_BYTES + S4_UART_RUN_HEAD_PORTION + 3u * S4_UART_BOX_BYTES;
        if (pass) {
            pass = s4_uart_unpack_run_response(frame, frame_length, 7u, 5u, 1440u, 1920u,
                                               &unpacked_header, &unpacked_meta, &read_head13,
                                               &read_head26, readback_boxes, 3u,
                                               &read_box_count) == S4_UART_OK &&
                   read_box_count == 3u &&
                   memcmp(read_head13, head13, S4_HEAD13_BYTES) == 0 &&
                   memcmp(read_head26, head26, S4_HEAD26_BYTES) == 0 &&
                   unpacked_meta.box_count == 3u && unpacked_header.op == 0x8002u;
        }
        snprintf(expected, sizeof(expected), "unpack成功且双头48B*3逐字节一致");
        snprintf(actual, sizeof(actual), "%s", pass ? "一致" : "不一致");
        selftest_record(&report, "run_response_pack_unpack_roundtrip", pass, expected, actual);

        /* re-pack：从解出的结构重新打包，必须与原始帧逐字节相同 */
        if (pass) {
            s4_detection rebuilt[3];
            size_t i;
            for (i = 0u; i < 3u; ++i) {
                rebuilt[i].class_id = readback_boxes[i].class_id;
                rebuilt[i].source_order = readback_boxes[i].source_order;
                rebuilt[i].score = readback_boxes[i].score;
                rebuilt[i].x1 = readback_boxes[i].x1;
                rebuilt[i].y1 = readback_boxes[i].y1;
                rebuilt[i].x2 = readback_boxes[i].x2;
                rebuilt[i].y2 = readback_boxes[i].y2;
            }
            repack_pass = s4_uart_pack_run_response(7u, 5u, 1440u, 1920u, S4_UART_OP_RUN_INPUT,
                                                   &unpacked_meta, (const int8_t *)read_head13,
                                                   (const int8_t *)read_head26, rebuilt, 3u,
                                                   repack, sizeof(repack),
                                                   &repack_length) == S4_UART_OK &&
                          repack_length == frame_length &&
                          memcmp(repack, frame, frame_length) == 0;
        } else {
            repack_pass = 0;
        }
        snprintf(expected, sizeof(expected), "re-pack与原始帧逐字节相同");
        snprintf(actual, sizeof(actual), "%s", repack_pass ? "一致" : "不一致");
        selftest_record(&report, "run_response_repack_byte_identical", repack_pass, expected, actual);

        /* payload 篡改必须被 payload CRC 拒绝 */
        if (pass) {
            frame[frame_length - 1u] ^= 0x01u;
            repack_pass = s4_uart_unpack_run_response(frame, frame_length, 7u, 5u, 1440u, 1920u,
                                                     &unpacked_header, &unpacked_meta,
                                                     &read_head13, &read_head26, readback_boxes,
                                                     3u, &read_box_count) ==
                         S4_UART_ERR_PAYLOAD_CRC;
        } else {
            repack_pass = 0;
        }
        snprintf(expected, sizeof(expected), "拒绝S4_UART_ERR_PAYLOAD_CRC");
        snprintf(actual, sizeof(actual), "%s", repack_pass ? "已拒绝" : "未拒绝");
        selftest_record(&report, "payload_crc_rejects_tamper", repack_pass, expected, actual);
    }
    /* 7. 扩展 op 门闸：未决策前必须拒绝 */
    {
        const int pass = s4_uart_op_is_reserved(S4_UART_OP_EXT_BASE) == 1 &&
                         s4_uart_op_is_reserved(S4_UART_OP_RUN_INPUT) == 0;
        snprintf(expected, sizeof(expected), "扩展op保留且未启用");
        snprintf(actual, sizeof(actual), "%s", pass ? "已拒绝" : "未拒绝");
        selftest_record(&report, "extension_op_gate_closed", pass, expected, actual);
    }

    all_pass = report.failed == 0;
    fprintf(report.json, "    {\"name\": \"__summary__\", \"pass\": %s, \"passed\": %d, \"failed\": %d}\n",
            all_pass ? "true" : "false", report.passed, report.failed);
    fprintf(report.json, "  ],\n");
    fprintf(report.json, "  \"all_pass\": %s\n", all_pass ? "true" : "false");
    fprintf(report.json, "}\n");
    fclose(report.json);
    printf("[s4_host] selftest passed=%d failed=%d all_pass=%d\n", report.passed, report.failed,
           all_pass);
    if (report.failed == 0) {
        rc = 0;
    } else {
        rc = 3;
    }
    return rc;
}

/* ------------------------------------------------------------- bundle 模式 */

static void json_double(FILE *stream, double value)
{
    fprintf(stream, "%.17g", value);
}

static void write_detections(FILE *stream, const s4_detection *detections, size_t count,
                             uint32_t width, uint32_t height)
{
    size_t index;
    fprintf(stream, "  \"detections\": [");
    for (index = 0u; index < count; ++index) {
        fprintf(stream, "%s\n    {", index == 0u ? "" : ",");
        fprintf(stream, "\"class_id\": %d, ", (int)detections[index].class_id);
        fprintf(stream, "\"class_name\": \"%s\", ",
                S4_HOST_CLASS_NAMES[detections[index].class_id & 7]);
        fprintf(stream, "\"score\": ");
        json_double(stream, detections[index].score);
        fprintf(stream, ", \"xyxy\": [");
        json_double(stream, detections[index].x1);
        fprintf(stream, ", ");
        json_double(stream, detections[index].y1);
        fprintf(stream, ", ");
        json_double(stream, detections[index].x2);
        fprintf(stream, ", ");
        json_double(stream, detections[index].y2);
        fprintf(stream, "], \"xyxy_px\": [");
        json_double(stream, detections[index].x1 * (double)width);
        fprintf(stream, ", ");
        json_double(stream, detections[index].y1 * (double)height);
        fprintf(stream, ", ");
        json_double(stream, detections[index].x2 * (double)width);
        fprintf(stream, ", ");
        json_double(stream, detections[index].y2 * (double)height);
        fprintf(stream, "], \"source_order\": %d}", (int)detections[index].source_order);
    }
    fprintf(stream, "%s  ],\n", count == 0u ? "" : "\n");
}

/*
 * 候选数达到缓冲上限时的硬错误结果记录（S4-A：state=ERROR、error_code=BAD_ARGUMENT(1)、
 * detections=[]，不定义候选截断语义）。tiny416 固定配置下该分支不可达，此处为防御性实现。
 * 退出码 6。
 */
static int write_candidate_overflow_json(const char *json_path, const s4_bundle *bundle,
                                        size_t candidate_count, size_t pre_threshold_count,
                                        size_t candidate_box_count)
{
    FILE *json = fopen(json_path, "wb");
    if (json == NULL) {
        fprintf(stderr, "[s4_host] 无法写入结果 JSON：%s\n", json_path);
        return -1;
    }
    fprintf(json, "{\n");
    fprintf(json, "  \"schema_version\": \"gestureforge_s4b_offline_host_result_v1\",\n");
    fprintf(json, "  \"mode\": \"bundle\",\n");
    fprintf(json, "  \"s4a_contract\": \"docs/stage4/s4a_stage4_g0_fields.json\",\n");
    fprintf(json, "  \"frame_id\": %u,\n", bundle->frame_id);
    fprintf(json, "  \"result_seq\": %u,\n", bundle->result_seq);
    fprintf(json, "  \"geometry\": {\"width\": %u, \"height\": %u},\n", bundle->width, bundle->height);
    fprintf(json, "  \"state\": \"ERROR\",\n");
    fprintf(json, "  \"detection_count\": 0,\n");
    write_detections(json, NULL, 0u, bundle->width, bundle->height);
    fprintf(json, "  \"candidate_count\": %u,\n", (unsigned)candidate_count);
    fprintf(json, "  \"candidate_count_pre_threshold\": %u,\n", (unsigned)pre_threshold_count);
    fprintf(json, "  \"candidate_box_count\": %u,\n", (unsigned)candidate_box_count);
    fprintf(json, "  \"candidate_overflow\": true,\n");
    fprintf(json, "  \"candidate_limit\": %u,\n", bundle->candidate_limit);
    fprintf(json, "  \"capture_time_ns\": 0,\n");
    fprintf(json, "  \"result_time_ns\": 0,\n");
    fprintf(json, "  \"inference_time_ns\": 0,\n");
    fprintf(json, "  \"end_to_end_latency_ns\": 0,\n");
    fprintf(json, "  \"dropped_frames\": 0,\n");
    fprintf(json, "  \"stale\": false,\n");
    fprintf(json, "  \"error_code\": 1,\n");
    fprintf(json,
            "  \"measurement_scope\": {\"pl_timing\": \"NOT_EXECUTED_OFFLINE\", "
            "\"uart_transport\": \"NOT_EXECUTED_OFFLINE\", \"board_pl\": \"NOT_EXECUTED_OFFLINE\", "
            "\"unavailable_fields\": [\"capture_time_ns\", \"result_time_ns\", "
            "\"inference_time_ns\", \"end_to_end_latency_ns\"]},\n");
    fprintf(json,
            "  \"candidate_count_semantics\": {\"candidate_overflow_rule\": \"S4-A 硬错误路径："
            "候选数达到缓冲上限 => state=ERROR、error_code=BAD_ARGUMENT(1)、detections=[]；"
            "本合同不定义候选截断\"},\n");
    fprintf(json, "  \"decode\": {\"status\": %d, \"note\": \"candidate_overflow 硬错误\"},\n",
            S4_DECODE_CANDIDATE_OVERFLOW);
    fprintf(json, "  \"head_bytes_unchanged\": true\n");
    fprintf(json, "}\n");
    fclose(json);
    return 0;
}

static int run_bundle(const char *bundle_path, const char *json_path, const char *frame_path,
                      const char *heads_dir)
{
    s4_bundle bundle;
    int load_rc = load_bundle(bundle_path, &bundle);
    if (load_rc != 0) {
        return load_rc;
    }

    {
        const int8_t *head13 = (const int8_t *)bundle.blob;
        const int8_t *head26 = (const int8_t *)(bundle.blob + bundle.head13_len);
        uint8_t *snapshot;
        s4_detection detections[S4_MAX_OUTPUTS];
        size_t detection_count = 0u;
        size_t candidate_count = 0u;
        size_t pre_threshold_candidate_count = 0u;
        size_t candidate_box_count = 0u;
        int candidate_overflow = 0;
        int decode_status;
        int head_bytes_unchanged;
        uint32_t resized_width = 0u;
        uint32_t resized_height = 0u;
        uint32_t pad_left = 0u;
        uint32_t pad_top = 0u;
        int geometry_status;
        uint8_t frame[S4_HOST_MAX_FRAME_BYTES];
        size_t frame_length = 0u;
        s4_uart_meta meta;
        s4_uart_header response_header;
        s4_uart_meta read_meta;
        const uint8_t *read_head13 = NULL;
        const uint8_t *read_head26 = NULL;
        s4_uart_box read_boxes[S4_MAX_OUTPUTS];
        size_t read_box_count = 0u;
        s4_uart_status pack_status;
        s4_uart_status unpack_status;
        uint8_t repack[S4_HOST_MAX_FRAME_BYTES];
        size_t repack_length = 0u;
        int repack_byte_identical = 0;
        int readback_field_identical = 0;
        int readback_heads_identical = 0;
        int readback_boxes_identical = 0;
        FILE *json = NULL;
        size_t index;
        s4_uart_result_state result_state;
        char epoch_text[24];

        snapshot = (uint8_t *)malloc(bundle.blob_length);
        if (snapshot == NULL) {
            free(bundle.blob);
            return 4;
        }
        memcpy(snapshot, bundle.blob, bundle.blob_length);

        decode_status = s4_decode_nms_int8(head13, (size_t)bundle.head13_len,
                                          head26, (size_t)bundle.head26_len,
                                          bundle.width, bundle.height,
                                          bundle.score_threshold, bundle.head13_scale,
                                          bundle.head26_scale, detections, S4_MAX_OUTPUTS,
                                          &detection_count, &candidate_count,
                                          &pre_threshold_candidate_count, &candidate_box_count,
                                          &candidate_overflow);
        /* 进出一致：解码前后 INT8 原字节必须逐字节相同 */
        head_bytes_unchanged = memcmp(snapshot, bundle.blob, bundle.blob_length) == 0;
        free(snapshot);
        if (decode_status == S4_DECODE_CANDIDATE_OVERFLOW) {
            /* 硬错误路径（tiny416 固定配置下不可达，见 s4_ps_decode.h）。 */
            fprintf(stderr, "[s4_host] 候选数达到缓冲上限：按 S4-A 硬错误语义输出 ERROR 记录\n");
            (void)write_candidate_overflow_json(json_path, &bundle, candidate_count,
                                               pre_threshold_candidate_count, candidate_box_count);
            free(bundle.blob);
            return 6;
        }
        if (decode_status != S4_DECODE_OK) {
            fprintf(stderr, "[s4_host] 解码失败，status=%d\n", decode_status);
            free(bundle.blob);
            return 5;
        }
        if (!head_bytes_unchanged) {
            fprintf(stderr, "[s4_host] INT8 原字节在解码中被改写\n");
            free(bundle.blob);
            return 5;
        }
        geometry_status = s4_letterbox_geometry(bundle.width, bundle.height, &resized_width,
                                                &resized_height, &pad_left, &pad_top);

        meta.epoch = 1u;
        meta.phys_status = S4_UART_PHYS_STATUS_DONE_SAFE;
        meta.error_code = 0u;
        meta.last_reject = 0u;
        meta.raw_candidate_count = (uint32_t)candidate_count;
        meta.box_count = (uint32_t)detection_count;
        meta.repeat_index = 0u;
        meta.repeat_total = 1u;
        meta.response_code = S4_UART_CODE_OK;
        pack_status = s4_uart_pack_run_response(bundle.sequence, bundle.frame_id, bundle.width,
                                               bundle.height, S4_UART_OP_RUN_INPUT, &meta,
                                               head13, head26, detections, detection_count,
                                               frame, sizeof(frame), &frame_length);
        if (pack_status != S4_UART_OK) {
            fprintf(stderr, "[s4_host] 帧打包失败，status=%d\n", (int)pack_status);
            free(bundle.blob);
            return 5;
        }
        unpack_status = s4_uart_unpack_run_response(frame, frame_length, bundle.sequence,
                                                    bundle.frame_id, bundle.width, bundle.height,
                                                    &response_header, &read_meta, &read_head13,
                                                    &read_head26, read_boxes, S4_MAX_OUTPUTS,
                                                    &read_box_count);
        if (unpack_status != S4_UART_OK) {
            fprintf(stderr, "[s4_host] 帧解包失败，status=%d\n", (int)unpack_status);
            free(bundle.blob);
            return 5;
        }
        readback_heads_identical = memcmp(read_head13, head13, S4_HEAD13_BYTES) == 0 &&
                                   memcmp(read_head26, head26, S4_HEAD26_BYTES) == 0;
        readback_boxes_identical = read_box_count == detection_count;
        if (readback_boxes_identical) {
            for (index = 0u; index < read_box_count; ++index) {
                if (read_boxes[index].class_id != detections[index].class_id ||
                    read_boxes[index].source_order != detections[index].source_order ||
                    read_boxes[index].score != detections[index].score ||
                    read_boxes[index].x1 != detections[index].x1 ||
                    read_boxes[index].y1 != detections[index].y1 ||
                    read_boxes[index].x2 != detections[index].x2 ||
                    read_boxes[index].y2 != detections[index].y2) {
                    readback_boxes_identical = 0;
                    break;
                }
            }
        }
        readback_field_identical = read_meta.epoch == meta.epoch &&
                                   read_meta.phys_status == meta.phys_status &&
                                   read_meta.error_code == meta.error_code &&
                                   read_meta.last_reject == meta.last_reject &&
                                   read_meta.raw_candidate_count == meta.raw_candidate_count &&
                                   read_meta.box_count == meta.box_count &&
                                   read_meta.repeat_index == meta.repeat_index &&
                                   read_meta.repeat_total == meta.repeat_total &&
                                   read_meta.response_code == meta.response_code &&
                                   response_header.sequence == bundle.sequence &&
                                   response_header.frame_id == bundle.frame_id &&
                                   response_header.width == bundle.width &&
                                   response_header.height == bundle.height &&
                                   response_header.op ==
                                       (uint16_t)(S4_UART_OP_RUN_INPUT | S4_UART_RESPONSE_FLAG);
        {
            s4_detection rebuilt[S4_MAX_OUTPUTS];
            for (index = 0u; index < read_box_count; ++index) {
                rebuilt[index].class_id = read_boxes[index].class_id;
                rebuilt[index].source_order = read_boxes[index].source_order;
                rebuilt[index].score = read_boxes[index].score;
                rebuilt[index].x1 = read_boxes[index].x1;
                rebuilt[index].y1 = read_boxes[index].y1;
                rebuilt[index].x2 = read_boxes[index].x2;
                rebuilt[index].y2 = read_boxes[index].y2;
            }
            repack_byte_identical =
                s4_uart_pack_run_response(bundle.sequence, bundle.frame_id, bundle.width,
                                          bundle.height, S4_UART_OP_RUN_INPUT, &read_meta,
                                          (const int8_t *)read_head13,
                                          (const int8_t *)read_head26, rebuilt, read_box_count,
                                          repack, sizeof(repack), &repack_length) == S4_UART_OK &&
                repack_length == frame_length && memcmp(repack, frame, frame_length) == 0;
        }

        if (frame_path != NULL) {
            if (write_entire_file(frame_path, frame, frame_length) != 0) {
                free(bundle.blob);
                return 4;
            }
        }
        if (heads_dir != NULL) {
            char path[S4_HOST_MAX_PATH];
            snprintf(path, sizeof(path), "%s/head13.raw", heads_dir);
            if (write_entire_file(path, (const uint8_t *)head13, S4_HEAD13_BYTES) != 0) {
                free(bundle.blob);
                return 4;
            }
            snprintf(path, sizeof(path), "%s/head26.raw", heads_dir);
            if (write_entire_file(path, (const uint8_t *)head26, S4_HEAD26_BYTES) != 0) {
                free(bundle.blob);
                return 4;
            }
        }

        result_state = s4_uart_result_state_from_meta(&read_meta);
        decimal_u64(epoch_text, sizeof(epoch_text), read_meta.epoch);

        json = fopen(json_path, "wb");
        if (json == NULL) {
            fprintf(stderr, "[s4_host] 无法写入结果 JSON：%s\n", json_path);
            free(bundle.blob);
            return 4;
        }
        fprintf(json, "{\n");
        fprintf(json, "  \"schema_version\": \"gestureforge_s4b_offline_host_result_v1\",\n");
        fprintf(json, "  \"mode\": \"bundle\",\n");
        fprintf(json, "  \"s4a_contract\": \"docs/stage4/s4a_stage4_g0_fields.json\",\n");
        fprintf(json, "  \"s4a_result_fields_authority\": \"result_record.fields\",\n");
        fprintf(json, "  \"frame_id\": %u,\n", bundle.frame_id);
        fprintf(json, "  \"result_seq\": %u,\n", bundle.result_seq);
        fprintf(json, "  \"geometry\": {\"width\": %u, \"height\": %u},\n", bundle.width,
                bundle.height);
        fprintf(json, "  \"state\": \"%s\",\n",
                result_state == S4_UART_STATE_OK       ? "OK"
                : result_state == S4_UART_STATE_NO_HAND ? "NO_HAND"
                : result_state == S4_UART_STATE_TIMEOUT ? "TIMEOUT"
                                                        : "ERROR");
        fprintf(json, "  \"detection_count\": %u,\n", (unsigned)detection_count);
        write_detections(json, detections, detection_count, bundle.width, bundle.height);
        fprintf(json, "  \"candidate_count\": %u,\n", read_meta.raw_candidate_count);
        fprintf(json, "  \"candidate_count_pre_threshold\": %u,\n",
                (unsigned)pre_threshold_candidate_count);
        fprintf(json, "  \"candidate_box_count\": %u,\n", (unsigned)candidate_box_count);
        fprintf(json,
                "  \"candidate_count_semantics\": {\"candidate_count\": \"S4-A 契约口径：阈值筛除后、"
                "稳定排序截断到 15 之前、NMS 前（与 2A T29 raw_candidate_count_before_stable_nms 及 2B "
                "冻结实现同口径，与 UART raw_candidate_count 同值，可被 T29 黄金独立验证）\", "
                "\"candidate_count_pre_threshold\": \"S4-A 可选诊断字段：阈值筛除前的候选机会数 = "
                "5 * candidate_box_count，不参与对拍口径、不进 UART\", "
                "\"candidate_box_count\": \"非契约附加透明字段：通过几何/正面积校验的候选框数\", "
                "\"candidate_overflow_rule\": \"按 2B 参考实现为硬错误路径（候选数达到缓冲上限即 "
                "S2A_T62_INVALID_ARGUMENT，无截断）；tiny416 理论上界 = 上限 = 12675，本实现仅在尝试追加第 "
                "12676 个候选时置位（不可达），故恒 false 并显式记录未超限事实\", "
                "\"divergence_open\": false, \"resolved_by\": \"S4-A 契约 2026-10-21 修订（Lead 裁决 + r05 复核）\"},\n");
        fprintf(json, "  \"candidate_overflow\": %s,\n", candidate_overflow ? "true" : "false");
        fprintf(json, "  \"candidate_limit\": %u,\n", bundle.candidate_limit);
        /* 离线无 PL：时间字段按 S4-A absent_value_policy 用 0 哨兵（未观测），字段不省略。 */
        fprintf(json, "  \"capture_time_ns\": 0,\n");
        fprintf(json, "  \"result_time_ns\": 0,\n");
        fprintf(json, "  \"inference_time_ns\": 0,\n");
        fprintf(json, "  \"end_to_end_latency_ns\": 0,\n");
        fprintf(json, "  \"dropped_frames\": 0,\n");
        fprintf(json, "  \"stale\": false,\n");
        fprintf(json, "  \"error_code\": %u,\n", read_meta.error_code);
        /* 注意：unavailable_fields 只出现在 measurement_scope 内（S4-A evidence_annotation 规定），
         * 顶层不再重复该键，避免两处取值歧义。 */
        fprintf(json,
                "  \"measurement_scope\": {\"pl_timing\": \"NOT_EXECUTED_OFFLINE\", "
                "\"uart_transport\": \"NOT_EXECUTED_OFFLINE\", "
                "\"board_pl\": \"NOT_EXECUTED_OFFLINE\", "
                "\"unavailable_fields\": [\"capture_time_ns\", \"result_time_ns\", "
                "\"inference_time_ns\", \"end_to_end_latency_ns\"], "
                "\"note\": \"键名与取值按 S4-A evidence_annotation.measurement_scope；离线骨架无 PL/UART/板卡，"
                "四个时间字段为 0 哨兵，不是实测耗时\"},\n");
        fprintf(json,
                "  \"field_source_notes\": {\"state\": \"由 s2bu/1.1 PHYS_STATUS/ERROR_CODE/"
                "box_count/response_code 派生，非传输字段\", \"timing\": \"离线无 PL，未测量，"
                "用 0 哨兵并按 state 判别\", \"dropped_frames\": \"单帧离线链，无丢帧事实\", "
                "\"stale\": \"无显示层，离线恒 false\"},\n");
        fprintf(json, "  \"decode\": {\"status\": %d, \"score_threshold\": ", decode_status);
        json_double(json, bundle.score_threshold);
        fprintf(json, ", \"head13_scale\": ");
        json_double(json, bundle.head13_scale);
        fprintf(json, ", \"head26_scale\": ");
        json_double(json, bundle.head26_scale);
        fprintf(json, ", \"max_outputs\": %u, \"nms_iou\": 0.45, \"head13_len\": %u, "
                      "\"head26_len\": %u},\n",
                S4_MAX_OUTPUTS, bundle.head13_len, bundle.head26_len);
        fprintf(json,
                "  \"geometry_letterbox\": {\"status\": %d, \"resized_width\": %u, "
                "\"resized_height\": %u, \"pad_left\": %u, \"pad_top\": %u},\n",
                geometry_status, resized_width, resized_height, pad_left, pad_top);
        fprintf(json,
                "  \"uart\": {\"interface\": \"s2bu/1.1\", \"op_request\": %u, "
                "\"op_response\": %u, \"sequence\": %u, \"repeat_count\": 1, "
                "\"repeat_index\": 0, \"repeat_total\": 1, \"payload_len\": %u, "
                "\"response_code\": %u, \"epoch\": %s, \"phys_status\": %u, "
                "\"raw_candidate_count\": %u, \"box_count\": %u, \"frame_bytes\": %u},\n",
                S4_UART_OP_RUN_INPUT, (unsigned)response_header.op, bundle.sequence,
                response_header.payload_len, read_meta.response_code, epoch_text,
                read_meta.phys_status, read_meta.raw_candidate_count, read_meta.box_count,
                (unsigned)frame_length);
        fprintf(json, "  \"uart_crc\": {\"payload_crc32\": \"0x%08X\", \"header_crc32\": \"0x%08X\"},\n",
                response_header.payload_crc32, response_header.header_crc32);
        fprintf(json,
                "  \"readback\": {\"pack_status\": %d, \"unpack_status\": %d, "
                "\"field_identical\": %s, \"heads_identical\": %s, \"boxes_identical\": %s, "
                "\"repack_byte_identical\": %s, \"frame_length\": %u, \"decoded_box_count\": %u},\n",
                (int)pack_status, (int)unpack_status, readback_field_identical ? "true" : "false",
                readback_heads_identical ? "true" : "false",
                readback_boxes_identical ? "true" : "false",
                repack_byte_identical ? "true" : "false", (unsigned)frame_length,
                (unsigned)read_box_count);
        fprintf(json, "  \"head_bytes_unchanged\": %s\n", head_bytes_unchanged ? "true" : "false");
        fprintf(json, "}\n");
        fclose(json);

        printf("[s4_host] bundle=%s frame_id=%u detections=%u candidates_pre_threshold=%u "
               "candidates_thresholded=%u candidate_boxes=%u state=%d "
               "head_bytes_unchanged=%d readback_ok=%d frame_bytes=%u\n",
               bundle_path, bundle.frame_id, (unsigned)detection_count,
               (unsigned)pre_threshold_candidate_count, (unsigned)candidate_count,
               (unsigned)candidate_box_count, (int)result_state, head_bytes_unchanged,
               readback_field_identical && readback_heads_identical &&
                   readback_boxes_identical && repack_byte_identical,
               (unsigned)frame_length);
        free(bundle.blob);
        return 0;
    }
}

static void print_usage(void)
{
    printf("用法：\n");
    printf("  s4_offline_host --selftest --json <out.json>\n");
    printf("  s4_offline_host --bundle <bundle.bin> --json <out.json> "
           "[--frame <frame.bin>] [--heads-dir <dir>]\n");
}

int main(int argc, char **argv)
{
    const char *bundle_path = NULL;
    const char *json_path = NULL;
    const char *frame_path = NULL;
    const char *heads_dir = NULL;
    int selftest = 0;
    int index;

    for (index = 1; index < argc; ++index) {
        if (strcmp(argv[index], "--selftest") == 0) {
            selftest = 1;
        } else if (strcmp(argv[index], "--bundle") == 0 && index + 1 < argc) {
            bundle_path = argv[++index];
        } else if (strcmp(argv[index], "--json") == 0 && index + 1 < argc) {
            json_path = argv[++index];
        } else if (strcmp(argv[index], "--frame") == 0 && index + 1 < argc) {
            frame_path = argv[++index];
        } else if (strcmp(argv[index], "--heads-dir") == 0 && index + 1 < argc) {
            heads_dir = argv[++index];
        } else {
            print_usage();
            return 2;
        }
    }
    if (json_path == NULL) {
        print_usage();
        return 2;
    }
    if (selftest) {
        return run_selftest(json_path);
    }
    if (bundle_path == NULL) {
        print_usage();
        return 2;
    }
    return run_bundle(bundle_path, json_path, frame_path, heads_dir);
}