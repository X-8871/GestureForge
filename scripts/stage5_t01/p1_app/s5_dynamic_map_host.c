/* S5-T02 宿主 CLI：用**同一份 C 核心**跑合成动态流并输出逐帧结果 JSONL（离线对拍用）。
 *
 * 说明：本程序是"板上执行体"的宿主可执行版本——几何/取整/线宽/标签锚点全部走 s5_dynamic_map.c，
 * 与冻结参考对拍由 verify_dynamic_map.py 完成。**本程序不是板上运行证据**；板上项仍 NOT_RUN。
 *
 * 输入（TSV，行首 # 为注释）：
 *   F <frame_index> <displayed_frame_id> <result_frame_id> <result_seq> <capture_ns> <result_ns> \
 *     <commit_ns> <stale_flag> <warmup_flag> <state> <nbox>
 *   B <class_id> <score> <x1> <y1> <x2> <y2> <label_w> <label_h>
 *   D <n_dropped>
 * 输出：每帧一行 JSON（含五元组、每框像素矩形/边框像素数/标签锚点、HUD 13 字段、计数快照）；
 *       末行 `{"summary":{...}}`。
 */
#include "s5_dynamic_map.h"

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define S5DH_MAX_LINE 4096
#define S5DH_MAX_BORDER_PIXELS 16384

static int g_canvas_w = 1280;
static int g_canvas_h = 720;

static void json_escape(const char *text, char *out, size_t capacity)
{
    size_t i = 0, j = 0;
    if (text == NULL) {
        text = "";
    }
    while (text[i] != '\0' && j + 2 < capacity) {
        char ch = text[i++];
        if (ch == '"' || ch == '\\') {
            out[j++] = '\\';
        }
        out[j++] = ch;
    }
    out[j] = '\0';
}

static void emit_frame_json(FILE *out, int frame_index, const s5d_frame *frame,
                            const s5d_frame_result *result, const s5d_counters *counters,
                            const int *bx, const int *by, const int *box_border_counts,
                            int64_t virtual_time_ns)
{
    int i;
    char state_esc[64];
    json_escape(frame->state, state_esc, sizeof(state_esc));
    fprintf(out,
            "{\"schema_version\":\"gestureforge_s5t02_dynamic_map_v1\",\"frame_index\":%d,"
            "\"displayed_frame_id\":%u,\"result_frame_id\":%u,\"result_seq\":%u,"
            "\"age_result_ns\":%" PRId64 ",\"age_frame_ns\":%" PRId64 ",\"display_semantics\":\"%s\","
            "\"stale_flag\":%d,\"stale_effective\":%d,\"stale_reason\":\"%s\","
            "\"state\":\"%s\",\"warmup\":%d,\"boxes_drawn\":%d,\"zero_area_dropped\":%" PRIu64 ","
            "\"canvas\":[%d,%d],\"virtual_commit_ns\":%" PRId64 ",\"boxes\":[",
            frame_index, (unsigned)frame->displayed_frame_id, (unsigned)frame->frame_id,
            (unsigned)frame->result_seq, (long long)result->age_result_ns,
            (long long)result->age_frame_ns, result->display_semantics,
            frame->stale_flag, result->stale.stale_effective, result->stale.reason,
            state_esc, frame->warmup, result->nbox_drawn,
            (unsigned long long)result->zero_area_dropped, g_canvas_w, g_canvas_h,
            (long long)virtual_time_ns);
    for (i = 0; i < result->nbox_drawn; i++) {
        const s5d_drawn_box *box = &result->drawn[i];
        fprintf(out,
                "%s{\"class_id\":%d,\"score\":%.6f,\"x1\":%d,\"y1\":%d,\"x2\":%d,\"y2\":%d,"
                "\"border_pixels\":%d,\"label_x\":%d,\"label_y\":%d,\"label_placement\":\"%s\"}",
                i ? "," : "", box->class_id, box->score, box->rect.x1, box->rect.y1,
                box->rect.x2, box->rect.y2, box_border_counts[i], box->label_x, box->label_y,
                box->label_placement);
    }
    fprintf(out, "],\"hud\":{");
    for (i = 0; i < S5D_HUD_FIELD_COUNT; i++) {
        char value[64];
        switch (i) {
        case 0: snprintf(value, sizeof(value), "\"%s\"", S5D_NOT_AVAILABLE); break;  /* CAPTURE_FPS */
        case 1: snprintf(value, sizeof(value), "\"%s\"", S5D_NOT_AVAILABLE); break;  /* INFERENCE_FPS */
        case 2: snprintf(value, sizeof(value), "\"%s\"", S5D_NOT_AVAILABLE); break;  /* DISPLAY_FPS（离线不测） */
        case 3: snprintf(value, sizeof(value), "\"%s\"", S5D_NOT_AVAILABLE); break;  /* INFERENCE_TIME_NS */
        case 4: snprintf(value, sizeof(value), "%" PRId64 "", (long long)result->age_result_ns); break;
        case 5: snprintf(value, sizeof(value), "%" PRId64 "", (long long)result->age_frame_ns); break;
        case 6: snprintf(value, sizeof(value), "%u", (unsigned)frame->displayed_frame_id); break;
        case 7: snprintf(value, sizeof(value), "%d", result->nbox_drawn); break;
        case 8: snprintf(value, sizeof(value), "%" PRIu64 "",
                         (unsigned long long)(counters ? counters->stale_cleared : 0)); break;
        case 9: snprintf(value, sizeof(value), "%" PRIu64 "",
                         (unsigned long long)(counters ? counters->dropped_frames : 0)); break;
        case 10: snprintf(value, sizeof(value), "%" PRIu64 "",
                          (unsigned long long)(counters ? counters->timeouts : 0)); break;
        case 11: snprintf(value, sizeof(value), "\"%s\"", frame->warmup ? "WARM" : "STEADY"); break;
        default: snprintf(value, sizeof(value), "\"%s\"", result->display_semantics); break;
        }
        fprintf(out, "%s\"%s\":%s", i ? "," : "", S5D_HUD_FIELDS[i], value);
    }
    fprintf(out, "},\"counters\":{\"frames_committed\":%" PRIu64 ",\"warmup_frames\":%" PRIu64 ","
                 "\"dropped_frames\":%" PRIu64 ",\"timeouts\":%" PRIu64 ",\"error_results\":%" PRIu64 ","
                 "\"duplicate_results\":%" PRIu64 ",\"out_of_order_results\":%" PRIu64 ",\"stale_cleared\":%" PRIu64 ","
                 "\"zero_area_dropped\":%" PRIu64 ",\"boxes_drawn\":%" PRIu64 "}}\n",
            (unsigned long long)(counters ? counters->frames_committed : 0),
            (unsigned long long)(counters ? counters->warmup_frames : 0),
            (unsigned long long)(counters ? counters->dropped_frames : 0),
            (unsigned long long)(counters ? counters->timeouts : 0),
            (unsigned long long)(counters ? counters->error_results : 0),
            (unsigned long long)(counters ? counters->duplicate_results : 0),
            (unsigned long long)(counters ? counters->out_of_order_results : 0),
            (unsigned long long)(counters ? counters->stale_cleared : 0),
            (unsigned long long)(counters ? counters->zero_area_dropped : 0),
            (unsigned long long)(counters ? counters->boxes_drawn : 0));
    (void)bx;
    (void)by;
}

int main(int argc, char **argv)
{
    FILE *in = stdin, *out = stdout;
    char line[S5DH_MAX_LINE];
    s5d_frame frame;
    s5d_frame_result result;
    s5d_counters counters;
    int have_frame = 0, frame_index = 0, rc = 0;
    int declared_nbox = -1;
    int bx[S5DH_MAX_BORDER_PIXELS], by[S5DH_MAX_BORDER_PIXELS], counts[S5D_MAX_BOXES];
    int label_w[S5D_MAX_BOXES], label_h[S5D_MAX_BOXES];
    int *border_x = NULL, *border_y = NULL;
    int64_t virtual_time_ns = 0;
    char state_storage[64] = {0};   /* B2：跨 F/E 行存活，绝不指向块内局部 */

    if (argc > 1 && strcmp(argv[1], "--help") == 0) {
        fprintf(stderr, "用法：s5_dynamic_map_host [stream.tsv] [out.jsonl] [--canvas WxH]\n");
        return 2;
    }
    if (argc > 3 && strcmp(argv[3], "--canvas") == 0 && argc > 4) {
        if (sscanf(argv[4], "%dx%d", &g_canvas_w, &g_canvas_h) != 2 || g_canvas_w <= 0 || g_canvas_h <= 0) {
            fprintf(stderr, "画布参数非法：%s\n", argv[4]);
            return 2;
        }
    }
    if (argc > 1 && strcmp(argv[1], "-") != 0) {
        in = fopen(argv[1], "r");
        if (in == NULL) {
            fprintf(stderr, "打不开输入：%s\n", argv[1]);
            return 2;
        }
    }
    if (argc > 2 && strcmp(argv[2], "-") != 0) {
        out = fopen(argv[2], "w");
        if (out == NULL) {
            fprintf(stderr, "打不开输出：%s\n", argv[2]);
            return 2;
        }
    }
    border_x = bx;
    border_y = by;
    memset(&counters, 0, sizeof(counters));
    memset(&frame, 0, sizeof(frame));

    while (fgets(line, sizeof(line), in) != NULL) {
        char kind;
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\0') {
            continue;
        }
        kind = line[0];
        if (kind == 'F') {
            char state[64];
            int stale_flag = 0, warmup = 0, nbox = 0, consumed = 0;
            long long capture = 0, result_ns = 0, commit = 0;
            unsigned dfid = 0, rfid = 0, rseq = 0;
            if (have_frame) {                      /* 上一帧缺 B 行也照常处理（nbox 以 F 为准） */
                rc = 0;
            }
            if (sscanf(line, "F %d %u %u %u %" PRId64 " %" PRId64 " %" PRId64 " %d %d %31s %d%n",
                       &frame_index, &dfid, &rfid, &rseq, &capture, &result_ns, &commit,
                       &stale_flag, &warmup, state, &nbox, &consumed) < 11) {
                fprintf(stderr, "F 行解析失败：%s", line);
                rc = 3;
                break;
            }
            memset(&frame, 0, sizeof(frame));
            frame.capture_time_ns = capture;
            frame.result_time_ns = result_ns;
            frame.overlay_commit_ns = commit;
            frame.frame_id = rfid;
            frame.displayed_frame_id = dfid;
            frame.result_seq = rseq;
            frame.stale_flag = stale_flag;
            frame.warmup = warmup;
            /* B2：复制进持久缓冲（原实现把块内局部数组的地址存进跨行使用的结构体 = 悬挂指针） */
            snprintf(state_storage, sizeof(state_storage), "%s", state);
            frame.state = state_storage;
            frame.nbox = 0;
            declared_nbox = nbox;                  /* 记录声明值，E 行核验 */
            have_frame = 1;
            virtual_time_ns = commit;
        } else if (kind == 'B') {
            int class_id = 0, lw = 0, lh = 0;
            double score = 0.0, x1 = 0, y1 = 0, x2 = 0, y2 = 0;
            if (!have_frame) {
                fprintf(stderr, "B 行出现在 F 行之前：%s", line);
                rc = 3;
                break;
            }
            if (sscanf(line, "B %d %lf %lf %lf %lf %lf %d %d",
                       &class_id, &score, &x1, &y1, &x2, &y2, &lw, &lh) < 8) {
                fprintf(stderr, "B 行解析失败：%s", line);
                rc = 3;
                break;
            }
            if (frame.nbox >= S5D_MAX_BOXES) {
                fprintf(stderr, "超过 15 框：%s", line);
                rc = 4;
                break;
            }
            frame.boxes[frame.nbox].class_id = class_id;
            frame.boxes[frame.nbox].score = score;
            frame.boxes[frame.nbox].xyxy.x1 = x1;
            frame.boxes[frame.nbox].xyxy.y1 = y1;
            frame.boxes[frame.nbox].xyxy.x2 = x2;
            frame.boxes[frame.nbox].xyxy.y2 = y2;
            label_w[frame.nbox] = lw;
            label_h[frame.nbox] = lh;
            frame.nbox++;
        } else if (kind == 'D') {
            unsigned long long dropped = 0;
            if (sscanf(line, "D %" PRIu64 "", &dropped) == 1) {
                counters.dropped_frames += dropped;
            }
        } else if (kind == 'E') {                  /* E = 结束当前 F（可选，显式） */
            if (declared_nbox >= 0 && declared_nbox != frame.nbox) {
                fprintf(stderr, "F 行声明 nbox=%d 与实际 B 行数 %d 不一致（frame_index=%d）\n",
                        declared_nbox, frame.nbox, frame_index);
                rc = 3;
                break;
            }
            s5d_status status = s5d_process_frame(&frame, g_canvas_w, g_canvas_h,
                                                  NULL, label_w, label_h, frame.nbox, &result, &counters);
            int i;
            if (status != S5D_OK) {
                fprintf(stderr, "s5d_process_frame 失败：status=%d（frame_index=%d）\n",
                        (int)status, frame_index);
                rc = 4;
                break;
            }
            for (i = 0; i < result.nbox_drawn; i++) {
                int recomputed = (int)s5d_border_pixels(&result.drawn[i].rect, S5D_DISPLAY_LINE_WIDTH_PX,
                                                        g_canvas_w, g_canvas_h, border_x, border_y,
                                                        S5DH_MAX_BORDER_PIXELS);
                if (recomputed != result.drawn[i].border_pixels) {
                    fprintf(stderr, "border_pixels 自校不一致：核心 %d vs 宿主 %d（box=%d）\n",
                            result.drawn[i].border_pixels, recomputed, i);
                    rc = 5;
                    break;
                }
                counts[i] = recomputed;             /* 使用核心值（已互校） */
            }
            if (rc != 0) {
                break;
            }
            emit_frame_json(out, frame_index, &frame, &result, &counters, border_x, border_y,
                            counts, virtual_time_ns);
            declared_nbox = -1;
            have_frame = 0;
        } else {
            fprintf(stderr, "未知行类型 '%c'：%s", kind, line);
            rc = 3;
            break;
        }
    }
    if (rc == 0 && have_frame) {                   /* 文件末尾未显式 E：补处理 */
        s5d_status status = s5d_process_frame(&frame, g_canvas_w, g_canvas_h, NULL, label_w, label_h, frame.nbox,
                                              &result, &counters);
        int i;
        if (status != S5D_OK) {
            fprintf(stderr, "s5d_process_frame 失败（尾部）：status=%d\n", (int)status);
            rc = 4;
        } else {
            for (i = 0; i < result.nbox_drawn; i++) {
                counts[i] = (int)s5d_border_pixels(&result.drawn[i].rect, S5D_DISPLAY_LINE_WIDTH_PX,
                                                   g_canvas_w, g_canvas_h, border_x, border_y,
                                                   S5DH_MAX_BORDER_PIXELS);
            }
            emit_frame_json(out, frame_index, &frame, &result, &counters, border_x, border_y,
                            counts, virtual_time_ns);
        }
    }
    if (rc == 0) {
        fprintf(out, "{\"summary\":{\"canvas\":[%d,%d],\"frames_committed\":%" PRIu64 ","
                     "\"warmup_frames\":%" PRIu64 ",\"dropped_frames\":%" PRIu64 ",\"timeouts\":%" PRIu64 ","
                     "\"error_results\":%" PRIu64 ",\"duplicate_results\":%" PRIu64 ",\"out_of_order_results\":%" PRIu64 ","
                     "\"stale_cleared\":%" PRIu64 ",\"zero_area_dropped\":%" PRIu64 ",\"boxes_drawn\":%" PRIu64 ","
                     "\"stale_age_limit_ns\":%" PRId64 ",\"line_width_px\":%d,\"semantics\":\"%s\","
                     "\"contract_id\":\"%s\"}}\n",
                g_canvas_w, g_canvas_h, (unsigned long long)counters.frames_committed,
                (unsigned long long)counters.warmup_frames, (unsigned long long)counters.dropped_frames,
                (unsigned long long)counters.timeouts, (unsigned long long)counters.error_results,
                (unsigned long long)counters.duplicate_results,
                (unsigned long long)counters.out_of_order_results,
                (unsigned long long)counters.stale_cleared,
                (unsigned long long)counters.zero_area_dropped,
                (unsigned long long)counters.boxes_drawn, (long long)S5D_STALE_AGE_LIMIT_NS,
                S5D_DISPLAY_LINE_WIDTH_PX, S5D_DISPLAY_SEMANTICS, S5D_CONTRACT_ID);
    }
    if (in != stdin) { fclose(in); }
    if (out != stdout) { fclose(out); }
    return rc;
}