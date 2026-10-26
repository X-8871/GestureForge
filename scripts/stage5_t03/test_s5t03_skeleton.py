#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线用例骨架：坐标映射 / 帧关联 / 异常与过期 / 长跑回归。

运行（真实退出码）：`python -B scripts/stage5_t03/test_s5t03_skeleton.py -v`
退出码：0 = 全部通过；1 = 存在失败/错误。

覆盖（对应 `CDX-20261022-014` §4/§5，全部**离线**）：
- 坐标映射：手算样例 + 冻结参考实现同源 + 越界裁剪/零面积 + 2 px 偶数线宽语义
- 帧关联：顺序 / 迟到 / 跳帧 / 重复 / 乱序，≥100 帧五元组按 `displayed_frame_id` 索引、语义唯一 B
- 异常与过期：`age==limit` 不过期、`limit+1` 过期、显式 `stale_flag`、每结果只计一次、
  零框 ≠ 过期、`TIMEOUT`/`ERROR`/`DROPPED` 分列、无效记录不绘制
- 长跑回归（离线虚拟时钟加速 ≥30 分钟）：每帧恰一次提交事件（无死锁）、时间戳单调、计数可复算
- 契约完整性：`S5A-G0-v2` 未被改动、几何参考实现未分叉、既有合成源证据未被改写

硬边界：不碰硬件、不读 UART/JTAG、不跑 Vivado；结论只适用于**合成动态流**，不得升级为真实集成结论。
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
for entry in (str(REPO_ROOT), str(HERE)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

# 中文日志在 GBK 控制台重定向下会崩：入口统一 UTF-8（不依赖宿主 locale）
for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except (ValueError, OSError):   # pragma: no cover - 非文本流
            pass

import s5t03_display_pipeline as P  # noqa: E402
import s5t03_dynamic_stream as S  # noqa: E402
import recompute_from_log as RC  # noqa: E402  （独立复算器，不导入流水线内存状态）

R = P.REFERENCE

PARAMS_PATH = REPO_ROOT / "docs" / "stage5" / "s5t03_offline_skeleton_params_v1.json"
CONTRACT_PATH = REPO_ROOT / "docs" / "stage5" / "s5a_stage5_display_g0_fields.json"
BINDING_PATH = REPO_ROOT / "docs" / "stage5" / "s5t03_input_contract_binding_v1.json"
BASE_COMMIT = "654c72eb8e883b1a43fe8b6c3f073a9cb6f023b9"
UNTOUCHED_PATHS = ("report/evidence/S5-A", "report/evidence/S5-B",
                   "report/evidence/S5-C", "report/evidence/S5-T01")

def _baseline_evidence_files() -> tuple[str, ...]:
    """基线提交中 UNTOUCHED_PATHS 下的全部文件（用于内容哈希比对；不随新增而变）。"""
    listed = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-tree", "-r", "--name-only",
                             BASE_COMMIT, "--", *UNTOUCHED_PATHS],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    return tuple(line.strip() for line in listed.stdout.splitlines() if line.strip())


EXISTING_EVIDENCE_FILES = _baseline_evidence_files() if BASE_COMMIT else ()


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_params() -> dict:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


PARAMS = load_params()
NEW = PARAMS["newly_frozen_for_skeleton_only"]
INHERIT = PARAMS["inherited_from_s5a_g0_v2"]["items"]

# 证据脚本在跑完本套件后读取的实测摘要（避免为收集数字重复跑长跑）
LAST_MIXED: dict = {}
LAST_LONG: dict = {}
# 证据脚本可设置该目录：用例会把帧级事件日志落盘（N-4），供独立复算器复算
LOG_DIR: pathlib.Path | None = None
LOG_DUMPS: dict = {}


def dump_log(pipeline, name: str) -> pathlib.Path:
    """把帧级事件日志落盘（LOG_DIR 未设置时用临时目录，保证单独运行也能自检）。"""
    global LOG_DIR
    if LOG_DIR is None:
        LOG_DIR = pathlib.Path(tempfile.mkdtemp(prefix="s5t03_logs_"))
    path = pathlib.Path(LOG_DIR) / name
    LOG_DUMPS[name] = pipeline.log.dump_jsonl(path, compact=True)
    return path


def stream(mode: str, frames: int, *, seed: int | None = None, warmup: int = 0) -> list[dict]:
    return S.build_stream(mode, frames, params=PARAMS,
                          seed=NEW["seed"] if seed is None else seed,
                          frame_period_ns=NEW["long_run_virtual_frame_period_ns"],
                          warmup_frames=warmup)


def run(mode: str, frames: int, *, seed: int | None = None, warmup: int = 0):
    pipeline = P.DisplayPipeline(canvas_width=1280, canvas_height=720,
                                 input_scope_label="synthetic_dynamic_reference",
                                 params=PARAMS)
    summary = P.run_stream(pipeline, stream(mode, frames, seed=seed, warmup=warmup))
    commits = pipeline.log.commit_events()
    measured = {
        "mode": mode,
        "frames": frames,
        "seed": NEW["seed"] if seed is None else seed,
        "commit_events": summary["commit_events"],
        "events": summary["events"],
        "counters": dict(summary["counters"]),
        "virtual_elapsed_ns": (commits[-1]["overlay_commit_ns"] - commits[0]["overlay_commit_ns"]
                               if commits else 0),
    }
    if frames >= NEW["long_run_min_frames"]:
        LAST_LONG.update(measured)
    elif mode == "mixed":
        LAST_MIXED.update(measured)
    return pipeline, summary


class T01_ContractIntegrity(unittest.TestCase):
    """契约与参考实现：显示阈值/几何未改；记录校验已登记 repeat_index 正整数规则。"""

    def test_g0_contract_matches_registered_hash(self):
        expected = PARAMS["inherited_from_s5a_g0_v2"]["contract_json_sha256"]
        self.assertEqual(sha256_file(CONTRACT_PATH), expected,
                         "S5A-G0-v2 JSON 字节与登记哈希不符：本骨架不得改显示契约的阈值/几何/语义")
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertIn("stale_domain_note", contract["stale_and_age"],
                      "N-1：stale 判定域差异必须登记在契约中并提请正式 G0 裁定")
        self.assertIn("本轮已把措辞改为与实现一致", contract["stale_and_age"]["stale_domain_note"])
        # 旧措辞不得再出现在定义/判定规则字段中（note 里作为「历史曾写」引用是允许的）
        for field in ("stage4_stale_definition", "stage5_clear_rule"):
            self.assertNotIn("仅对 state ∈ {OK, NO_HAND} 定义", contract["stale_and_age"][field],
                             f"N-1：{field} 的旧措辞必须已改正（显示侧判定不带 state 守卫）")

    def test_geometry_reference_not_forked(self):
        expected = PARAMS["inherited_from_s5a_g0_v2"]["geometry_reference_sha256"]
        reference_path = REPO_ROOT / PARAMS["inherited_from_s5a_g0_v2"]["geometry_reference_path"]
        self.assertEqual(sha256_file(reference_path), expected)
        self.assertIs(P.REFERENCE, R, "骨架必须直接引用冻结参考实现，不得另建几何模块")

    def test_inherited_thresholds_match_contract(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["contract_id"], "S5A-G0-v2")
        self.assertEqual(contract["stale_and_age"]["stale_age_limit_ns"], INHERIT["stale_age_limit_ns"])
        self.assertEqual(contract["overlay_layout"]["line_width_px_1080p"], INHERIT["display_line_width_px"])
        self.assertEqual(contract["scoring"]["max_outputs_per_image"], INHERIT["max_outputs_per_image"])
        self.assertEqual(contract["display_semantics"]["value"], INHERIT["display_semantics"])
        self.assertEqual(contract["overlay_layout"]["hud_fields"], INHERIT["hud_fields"])
        self.assertEqual(R.STALE_AGE_LIMIT_NS, INHERIT["stale_age_limit_ns"])
        self.assertEqual(R.STALE_AGE_LIMIT_NS, 200_000_000)
        self.assertFalse(R.is_stale(200_000_000), "age == limit 不得判过期")
        self.assertTrue(R.is_stale(200_000_001))

    def test_binding_json_declares_scope_labels(self):
        binding = json.loads(BINDING_PATH.read_text(encoding="utf-8"))
        labels = binding["input_scope_labels"]["labels"]
        self.assertIn("camera_live_colour", labels)
        self.assertIn("camera_capture_replay_colour", labels)
        # B-1：按阶段4 r04 重绑——两个彩色标签都映射 camera，回放以 timing_claim_scope 区分
        self.assertEqual(labels["camera_live_colour"]["maps_to_source_kind"], "camera")
        self.assertEqual(labels["camera_capture_replay_colour"]["maps_to_source_kind"], "camera")
        self.assertTrue(labels["camera_capture_replay_colour"]["capture_time_available"])
        self.assertEqual(labels["camera_capture_replay_colour"]["timing_claim_scope"], "replay_only")
        self.assertEqual(labels["camera_live_colour"]["timing_claim_scope"], "real_live")
        self.assertEqual(labels["camera_capture_replay_colour"]["mapping_status"],
                         "ALIGNED_WITH_STAGE4_R04")
        self.assertEqual(binding["status"], "BINDING_ALIGNED_WITH_STAGE4_R04_NOT_FROZEN")
        self.assertEqual(binding["relation_to_frozen_contract"]["display_contract"], "S5A-G0-v2")
        self.assertIn("stale_age_limit_ns", binding["relation_to_frozen_contract"]["unchanged"])
        # 取代关系与 UR 状态
        self.assertIn("7a9507ab4a2067d493b4d9ff47b331c747f33796", binding["supersedes"]["replaced_by"])
        self.assertIn("f6fa9f0", binding["supersedes"]["reason"])
        ups = {item["id"]: item.get("status") for item in binding["unresolved_and_requests"]}
        self.assertEqual(ups["UR-1"], "REISSUED_ON_R04")
        self.assertEqual(ups["UR-2"], "RESOLVED")
        # N-1 stale 判定域登记
        self.assertIn("pending_formal_g0", binding["relation_to_frozen_contract"]["stale_domain"])
        # N-7 相关：部署一致性的措辞（XSA 前缀 vs bit/ELF 全哈希）
        consistency = binding["stage3_deployment_binding"]["consistency_with_015_r03"]
        self.assertIn("全哈希", consistency["bit"])
        self.assertIn("前缀", consistency["xsa"])
        # NB-5：绑定层必须断言 capture_time_ns 非零要求与 carry_fields（防止回退为 0 哨兵/删字段）
        replay = labels["camera_capture_replay_colour"]
        self.assertIn("真实抓取时刻", replay["capture_time_ns"])
        self.assertIn("不得填 0 哨兵", replay["capture_time_ns"])
        self.assertTrue(labels["camera_live_colour"]["capture_time_ns"].startswith("非零"))
        carry = " ".join(replay["carry_fields"])
        for field in ("frame_integrity", "replay_source_path", "replay_source_file_sha256",
                      "replay_source_width", "replay_source_height", "replay_source_stride_bytes",
                      "replay_source_byte_order", "stage3_capture_evidence_entry",
                      "source_frame_id", "source_capture_time_ns"):
            self.assertIn(field, carry, f"carry_fields 缺少 {field}")
        # NB-5：绑定层关闭 ≠ 实现完成（实现状态必须显式登记）
        impl = binding["implementation_status"]
        self.assertIn("尚未实现", impl["statement"])
        self.assertTrue(any("camera_capture_replay_colour" in item for item in impl["not_implemented"]))
        # NB-1：等价 frame_id 规则必须登记在绑定里
        self.assertIn("duplicate_frame_id_display_rule",
                      binding["frame_association_keys"]["rejection_policy"])
        self.assertIn("repeat_index_validation",
                      binding["frame_association_keys"]["rejection_policy"])
        self.assertIn("result_key_validation",
                      binding["frame_association_keys"]["rejection_policy"])
        self.assertIn("reject_reason", binding["frame_association_keys"]["rejection_policy"]["logging_rule"])
        # NB-2：漂移登记结构
        impact = binding["impacted_by_this_revision"]
        self.assertIn("registration_rule", impact)
        registered = {m for entry in impact["entries"] for m in entry["manifests"]}
        self.assertIn("report/evidence/S5-CTRL/S5-A01/s5_ctrl_20261022_r02/delivery_manifest.json", registered)
        self.assertIn("report/evidence/S5-T01/s5t01_board_overlay_20261022_r01/run_manifest.json", registered)
        self.assertIn("report/evidence/S5-T01/s5t01_prereq_20261022_r02/run_manifest.json", registered)

    def test_drift_registration_covers_old_hash_bindings(self):
        """NB-2：凡在清单里以旧哈希绑定 S5A-G0-v2 JSON 的包都必须被登记（扫描即判据）。"""
        binding = json.loads(BINDING_PATH.read_text(encoding="utf-8"))
        impact = binding["impacted_by_this_revision"]
        old_hash = impact["old_hash"]
        registered = {m for entry in impact["entries"] for m in entry["manifests"]}
        found = set()
        for path in (REPO_ROOT / "report" / "evidence").rglob("*manifest*.json"):
            if not path.is_file():
                continue
            if old_hash in path.read_text(encoding="utf-8", errors="replace"):
                found.add(path.relative_to(REPO_ROOT).as_posix())
        self.assertGreaterEqual(len(found), 15, "扫描命中数异常偏低：判据可能失效")
        self.assertEqual(found - registered, set(),
                         f"存在未登记的旧哈希绑定：{sorted(found - registered)}")
        self.assertEqual(registered - found, set(),
                         f"登记了但扫描未命中（登记过时）：{sorted(registered - found)}")

    def test_existing_synthetic_evidence_untouched(self):
        """不得**改动/删除/改名**既有合成源证据；在此目录下**新增**证据包（新 RunId）不算违反。

        修订（2026-10-27，S5-T02 复审 B1 裁决）：原判据用 `git diff --name-only`，会把
        `report/evidence/S5-T01/<新 RunId>/**` 这类**新增**文件也算作"改动"，与任务卡 §4
        （允许 `report/evidence/S5-T01/<新RunId>/**`）冲突；且未 track 时看不见、track 后立刻变红
        （套件结论随提交状态漂移）。现按 `--name-status` 只对 **M/D/R**（改动/删除/改名）判违反。
        """
        command = ["git", "-C", str(REPO_ROOT), "diff", "--name-status", BASE_COMMIT, "--",
                   *UNTOUCHED_PATHS]
        completed = subprocess.run(command, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        violations = [line for line in completed.stdout.splitlines()
                      if line.strip() and line.split()[0][0] in ("M", "D", "R")]
        self.assertEqual(violations, [],
                         f"既有合成源证据被改动/删除/改名：{violations}")
        # 另：既有**文件**的内容哈希必须与基线提交一致（防止改名规避）
        for rel in EXISTING_EVIDENCE_FILES:
            # 按**字节**取 blob（避免 Windows GBK 默认编码破坏非 ASCII 内容）
            blob = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{BASE_COMMIT}:{rel}"],
                                  capture_output=True)
            self.assertEqual(blob.returncode, 0, f"基线中不存在该证据：{rel}")
            # 归一化换行后再比对（仓库 core.autocrlf=true，checkout 可能改写工作区换行；
            # 该判据只关心**内容**是否被改动，不应因 EOL 差异误报）
            baseline = hashlib.sha256(blob.stdout.replace(b"\r\n", b"\n")).hexdigest()
            live_bytes = (REPO_ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
            live = hashlib.sha256(live_bytes).hexdigest()
            self.assertEqual(live, baseline, f"既有证据内容被改动：{rel}")


class T02_CoordinateMapping(unittest.TestCase):
    """坐标映射：手算样例 + 参考同源 + 裁剪/零面积 + 线宽语义。"""

    def test_hand_computed_cases_match_reference(self):
        for case in NEW["coordinate_cases"]:
            px = R.original_norm_to_display_px(case["xyxy"], 1280, 720)
            self.assertEqual(px, case["hand_computed_px"],
                             f"{case['id']}: 参考实现 {px} 与手算 {case['hand_computed_px']} 不一致")

    def test_pipeline_uses_reference_mapping(self):
        case = NEW["coordinate_cases"][1]          # C2-quarter
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        record = S.make_record(session_id=1, frame_id=3, result_seq=1, sequence=1,
                               capture_time_ns=1_000_000_000,
                               result_time_ns=1_000_000_100,
                               inference_time_ns=1_000_000, state="OK",
                               detections=[S.make_detection(0, box=tuple(case["xyxy"]))])
        self.assertEqual(R.validate_result_record(record), [])
        pipeline.submit_result(record)
        event = pipeline.commit_frame(3, 1_000_000_200)["event"]
        self.assertTrue(event["drawn"])
        self.assertEqual(event["box_px"][0]["px"], case["hand_computed_px"])

    def test_geometry_resolutions_and_odd_padding(self):
        for width, height in NEW["geometry_resolutions"]:
            geom = R.letterbox_geometry(width, height, 416, 416)
            self.assertTrue(geom["new_width"] >= 1 and geom["new_height"] >= 1)
        odd = R.letterbox_geometry(683, 384, 416, 416)
        self.assertEqual((odd["new_width"], odd["new_height"]), (416, 233))
        self.assertEqual(odd["offset_y"], 91, "奇数总补边不得对称化/重新居中")
        self.assertEqual(odd["pad_bottom"], 92, "下侧补边差必须原样保留（91/92）")

    def test_edge_and_degenerate_cases(self):
        e1 = R.clip_unit_box([-0.1, -0.2, 1.1, 1.2])
        self.assertTrue(e1["clipped"] and not e1["zero_area"])
        self.assertEqual(e1["xyxy"], (0.0, 0.0, 1.0, 1.0))
        e2 = R.clip_unit_box([-0.5, -0.5, 0.0, 0.5])
        self.assertTrue(e2["clipped"] and e2["zero_area"], "裁剪后零面积必须判零面积且不绘制")
        with self.assertRaises(R.ContractViolation):
            R.clip_unit_box([0.6, 0.6, 0.4, 0.4])

    def test_border_line_width_semantics(self):
        pixels = R.border_pixel_sets(10, 10, 20, 20, R.DISPLAY_LINE_WIDTH_PX, 1280, 720)
        self.assertEqual(len(pixels), len(set(pixels)))
        self.assertEqual(list(pixels), sorted(pixels))
        for x, y in ((9, 10), (10, 10), (9, 20), (10, 20), (20, 10), (19, 10)):
            self.assertIn((x, y), pixels, "偶数线宽居中：几何线 p 占 {p-1, p}")
        clipped = R.border_pixel_sets(0, 0, 5, 5, R.DISPLAY_LINE_WIDTH_PX, 1280, 720)
        for x, y in clipped:
            self.assertTrue(0 <= x < 1280 and 0 <= y < 720, "边框像素必须钳到画布内")
        self.assertNotIn((-1, 0), clipped)

    def test_zero_area_box_not_drawn_but_counted(self):
        pipeline, summary = run("mixed", NEW["stream_samples"]["mixed_frames"])
        self.assertGreaterEqual(summary["counters"]["zero_area_dropped"], 1)
        for event in pipeline.log.commit_events():
            if event["zero_area_dropped"]:
                self.assertGreaterEqual(event["boxes"], 1)


class T03_FrameAssociation(unittest.TestCase):
    """帧关联：五元组、语义唯一、显示帧号与结果帧号如实记录。"""

    def _five_tuples(self, pipeline):
        return pipeline.log.five_tuples()

    def test_sequential_120_frames(self):
        pipeline, summary = run("sequential", NEW["frame_association_sample_frames"])
        five = self._five_tuples(pipeline)
        self.assertEqual(len(five), NEW["frame_association_sample_frames"])
        self.assertGreaterEqual(len(five), NEW["frame_association_min_frames_required"])
        for index, entry in enumerate(five):
            self.assertEqual(entry["displayed_frame_id"], index, "五元组必须可按 displayed_frame_id 索引")
            self.assertEqual(entry["result_frame_id"], index)
            self.assertEqual(entry["display_semantics"], "B_latest_result_overlay")
        self.assertEqual(len({entry["display_semantics"] for entry in five}), 1,
                         "单一证据包内 display_semantics 必须唯一")
        self.assertEqual(summary["counters"]["frames_committed"],
                         NEW["frame_association_sample_frames"])

    def test_late_results_recorded_truthfully(self):
        pipeline, _ = run("late", NEW["frame_association_sample_frames"])
        five = self._five_tuples(pipeline)
        self.assertEqual(len(five), NEW["frame_association_sample_frames"])
        mismatches = 0
        for entry in five:
            if entry["displayed_frame_id"] >= 2:
                self.assertEqual(entry["result_frame_id"], entry["displayed_frame_id"] - 2,
                                 "结果显示 frame_id 不得被改写成显示帧号以掩盖错配")
                mismatches += 1
        self.assertEqual(mismatches, NEW["frame_association_sample_frames"] - 2)
        self.assertGreater(five[10]["age_frame_ns"], 0)

    def test_skip_mode_ages_grow_and_stale_occurs(self):
        pipeline, summary = run("skip", NEW["frame_association_sample_frames"])
        five = self._five_tuples(pipeline)
        self.assertEqual(len(five), NEW["frame_association_sample_frames"])
        self.assertGreaterEqual(summary["counters"]["stale_cleared"], 1, "空档必须触发过期且被计数")
        self.assertGreater(max(e["age_frame_ns"] for e in five), R.STALE_AGE_LIMIT_NS)

    def test_duplicate_and_out_of_order_counted(self):
        pipeline_dup, summary_dup = run("dup", NEW["stream_samples"]["dup_frames"])
        self.assertGreaterEqual(summary_dup["counters"]["duplicate_results"], 1,
                                "重复结果必须计数")
        self.assertEqual(summary_dup["counters"]["frames_committed"],
                         NEW["stream_samples"]["dup_frames"])
        pipeline_ooo, summary_ooo = run("ooo", NEW["stream_samples"]["ooo_frames"])
        self.assertGreaterEqual(summary_ooo["counters"]["out_of_order_results"], 1,
                                "乱序结果必须计数")
        self.assertEqual(len(self._five_tuples(pipeline_ooo)),
                         NEW["stream_samples"]["ooo_frames"])
        # B-2：被判乱序/重复的提交必须记 FAIL 且带拒绝原因（r04：拒绝不得只记计数）
        fails = [e for e in pipeline_ooo.log.submit_events()
                 if e.get("outcome") == "out_of_order"]
        self.assertTrue(fails, "必须存在 out_of_order 提交事件")
        for event in fails:
            self.assertEqual(event["verdict"], P.VERDICT_FAIL)
            self.assertTrue(event.get("reject_reason"), "拒绝必须记录原因")
        for event in pipeline_dup.log.submit_events():
            if event.get("outcome") == "duplicate":
                self.assertEqual(event["verdict"], P.VERDICT_FAIL)

    def test_out_of_order_rejected_and_does_not_update_latest(self):
        """B-2：乱序帧不得改变叠加内容（其框必须与前一帧逐值相同），且不进入已接受集合。"""
        pipeline, _ = run("ooo", NEW["stream_samples"]["ooo_frames"])
        commits = pipeline.log.commit_events()
        submits = {i: e for i, e in enumerate(pipeline.log.events)
                   if e.get("event_type") == "result_submit" and e.get("outcome") == "out_of_order"}
        self.assertTrue(submits, "ooo 流必须注入乱序提交")
        # 乱序提交发生在其显示帧提交之前：该帧的框必须与前一帧相同
        checked = 0
        for index, event in enumerate(pipeline.log.events):
            if event.get("event_type") != "result_submit" or event.get("outcome") != "out_of_order":
                continue
            later = [e for e in pipeline.log.events[index + 1:]
                     if e.get("event_type") == "overlay_commit"]
            earlier = [e for e in pipeline.log.events[:index]
                       if e.get("event_type") == "overlay_commit"]
            self.assertTrue(earlier and later, "乱序提交必须在某个显示提交之前")
            self.assertEqual(earlier[-1]["box_px"], later[0]["box_px"],
                             "乱序结果被拒绝后，本帧绘制内容必须与前一帧逐值相同")
            checked += 1
        self.assertGreaterEqual(checked, 1)
        # 被拒绝的键不得进入已接受集合
        for event in pipeline.log.submit_events():
            if event.get("outcome") == "out_of_order":
                key = (event["session_id"], event["frame_id"], event["result_seq"])
                self.assertNotIn(key, pipeline.accepted_keys, "乱序结果不得写入已接受集合")

    def test_frame_id_regression_rejected_with_fail(self):
        """B-2：frame_id 回退必须拒绝并记 FAIL（阶段4 r04 frame_sequence_rules）。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        base = S.make_record(session_id=3, frame_id=10, result_seq=1, sequence=1,
                             capture_time_ns=1_000_000_000, result_time_ns=1_000_000_100,
                             inference_time_ns=1_000_000, state="OK",
                             detections=[S.make_detection(0)])
        self.assertEqual(pipeline.submit_result(base)["outcome"], "accepted")
        before = pipeline.commit_frame(10, 1_010_000_000)["event"]
        regressed = S.make_record(session_id=3, frame_id=9, result_seq=2, sequence=2,
                                  capture_time_ns=1_000_000_000, result_time_ns=1_000_000_100,
                                  inference_time_ns=1_000_000, state="OK",
                                  detections=[S.make_detection(1)])
        outcome = pipeline.submit_result(regressed)
        self.assertEqual(outcome["outcome"], "out_of_order")
        self.assertEqual(outcome["verdict"], "FAIL")
        self.assertEqual(outcome["reject_reason"], "regressed_frame_id")
        event = pipeline.log.submit_events()[-1]
        self.assertEqual(event["verdict"], "FAIL")
        self.assertTrue(event["rejected"])
        self.assertEqual(pipeline.counters["out_of_order_results"], 1)
        after = pipeline.commit_frame(11, 1_020_000_000)["event"]
        self.assertEqual(before["box_px"], after["box_px"], "被拒绝的回退结果不得改变绘制内容")
        self.assertNotIn((3, 9, 2), pipeline.accepted_keys)
        self.assertEqual(pipeline.latest["frame_id"], 10, "拒绝后最新结果必须保持不变")

    def test_result_seq_regression_rejected_with_fail(self):
        """B-2：同一 session 的 result_seq 回退同样必须拒绝并记 FAIL。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        good = S.make_record(session_id=4, frame_id=10, result_seq=5, sequence=5,
                             capture_time_ns=1_000_000_000, result_time_ns=1_000_000_100,
                             inference_time_ns=1_000_000, state="OK",
                             detections=[S.make_detection(0)])
        self.assertEqual(pipeline.submit_result(good)["outcome"], "accepted")
        regressed = S.make_record(session_id=4, frame_id=12, result_seq=4, sequence=6,
                                  capture_time_ns=1_000_000_000, result_time_ns=1_000_000_100,
                                  inference_time_ns=1_000_000, state="OK",
                                  detections=[S.make_detection(1)])
        outcome = pipeline.submit_result(regressed)
        self.assertEqual(outcome["outcome"], "out_of_order")
        self.assertEqual(outcome["verdict"], "FAIL")
        self.assertEqual(outcome["reject_reason"], "regressed_result_seq")
        self.assertEqual(pipeline.counters["out_of_order_results"], 1)
        self.assertNotIn((4, 12, 4), pipeline.accepted_keys)
        self.assertEqual(pipeline.latest["frame_id"], 10)

    # ── NB-1：等价 frame_id fail-closed ──────────────────────────────────
    @staticmethod
    def _record(session: int, frame_id: int, seq: int, *, detections: int = 1,
                repeat_index: int = 1, declared: bool = False) -> dict:
        record = S.make_record(session_id=session, frame_id=frame_id, result_seq=seq, sequence=seq,
                               capture_time_ns=1_000_000_000, result_time_ns=1_000_000_100,
                               inference_time_ns=1_000_000, state="OK",
                               detections=[S.make_detection(i) for i in range(detections)],
                               repeat_index=repeat_index)
        if declared:
            record["repeat_declared"] = True
        return record

    def test_equivalent_frame_id_without_declaration_rejected(self):
        """NB-1：同 session 等价 frame_id + 新 result_seq 且未声明 ⇒ 拒绝并记 FAIL。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        self.assertEqual(pipeline.submit_result(self._record(6, 30, 1))["outcome"], "accepted")
        before = pipeline.commit_frame(30, 1_010_000_000)["event"]
        outcome = pipeline.submit_result(self._record(6, 30, 2, detections=2))
        self.assertEqual(outcome["outcome"], "duplicate_frame_id")
        self.assertEqual(outcome["verdict"], "FAIL")
        self.assertIn("equivalent_frame_id_not_declared", outcome["reject_reason"])
        event = pipeline.log.submit_events()[-1]
        self.assertTrue(event["rejected"])
        self.assertEqual(event["declared_repeat_basis"], "no_declaration")
        self.assertEqual(pipeline.counters["duplicate_frame_id_results"], 1)
        self.assertEqual(pipeline.counters["duplicate_results"], 0,
                         "等价 frame_id 不得与同结果键重复混计")
        self.assertEqual(pipeline.counters["out_of_order_results"], 0, "不得削弱 B-2 分类")
        self.assertNotIn((6, 30, 2), pipeline.accepted_keys)
        after = pipeline.commit_frame(31, 1_020_000_000)["event"]
        self.assertEqual(before["box_px"], after["box_px"], "被拒等价帧不得改变绘制内容")
        self.assertEqual(pipeline.latest["result_seq"], 1, "被拒等价帧不得更新最新结果")

    def test_equivalent_frame_id_with_declared_repeat_accepted(self):
        """NB-1 二阶：显式声明（repeat_index 递增 / repeat_declared）才放行。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        self.assertEqual(pipeline.submit_result(self._record(7, 40, 1))["outcome"], "accepted")
        outcome = pipeline.submit_result(self._record(7, 40, 2, repeat_index=2, declared=True))
        self.assertEqual(outcome["outcome"], "accepted")
        self.assertEqual(outcome["verdict"], "PASS")
        self.assertEqual(pipeline.counters["duplicate_frame_id_results"], 0)
        self.assertEqual(pipeline.latest["result_seq"], 2)
        self.assertEqual(pipeline.log.submit_events()[-1]["declared_repeat_basis"], "repeat_declared")
        # 仅 repeat_index 递增（无 repeat_declared）同样构成显式声明
        outcome2 = pipeline.submit_result(self._record(7, 40, 3, repeat_index=3))
        self.assertEqual(outcome2["outcome"], "accepted")
        self.assertEqual(pipeline.log.submit_events()[-1]["declared_repeat_basis"], "repeat_index_incremented")

    def test_declared_lower_repeat_preserves_historical_maximum(self):
        """较小显式重放不得使后续未声明编号绕过历史最大值。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        for seq, index, declared in ((1, 1, False), (2, 5, False), (3, 1, True)):
            record = self._record(8, 30, seq, repeat_index=index, declared=declared)
            self.assertEqual(R.validate_result_record(record), [])
            self.assertEqual(pipeline.submit_result(record)["outcome"], "accepted")
        before = pipeline.commit_frame(30, 1_010_000_000)["event"]
        accepted_before = set(pipeline.accepted_keys)
        latest_before = dict(pipeline.latest)
        outcome = pipeline.submit_result(self._record(8, 30, 4, repeat_index=2))
        self.assertEqual(outcome["outcome"], "duplicate_frame_id")
        self.assertEqual(outcome["verdict"], "FAIL")
        self.assertIn("equivalent_frame_id_not_declared", outcome["reject_reason"])
        self.assertEqual(pipeline.accepted_frame_repeats[(8, 30)], 5)
        self.assertEqual(pipeline.accepted_keys, accepted_before)
        self.assertEqual(pipeline.latest, latest_before)
        after = pipeline.commit_frame(31, 1_020_000_000)["event"]
        self.assertEqual(before["box_px"], after["box_px"])
        self.assertEqual(pipeline.counters["duplicate_frame_id_results"], 1)
        self.assertEqual(pipeline.submit_result(
            self._record(8, 30, 5, repeat_index=6))["outcome"], "accepted")
        self.assertEqual(pipeline.accepted_frame_repeats[(8, 30)], 6)

    def test_repeat_fields_require_strict_domain(self):
        """repeat_index 必须是严格正整数；声明字段如存在必须是布尔值。"""
        valid = self._record(10, 40, 1)
        self.assertEqual(R.validate_result_record(valid), [])
        for value in (1.5, 5.5, "2", "bad", 0, -1, True, None, 1 << 32):
            with self.subTest(repeat_index=value):
                malformed = dict(valid)
                malformed["repeat_index"] = value
                self.assertTrue(any("repeat_index 必须是 uint32" in item
                                    for item in R.validate_result_record(malformed)))
        missing = dict(valid)
        del missing["repeat_index"]
        self.assertTrue(any("缺少必需字段 repeat_index" in item
                            for item in R.validate_result_record(missing)))
        malformed_declaration = dict(valid, repeat_declared=1)
        self.assertTrue(any("repeat_declared 必须是布尔值" in item
                            for item in R.validate_result_record(malformed_declaration)))

    def test_malformed_repeat_is_rejected_before_accepted_state_mutation(self):
        """浮点/非数值重复编号按 schema 拒绝，不触碰已接受状态或抛出转换异常。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        accepted = self._record(11, 50, 1)
        self.assertEqual(pipeline.submit_result(accepted)["outcome"], "accepted")
        accepted_keys = set(pipeline.accepted_keys)
        latest = dict(pipeline.latest)
        last_result_seq = dict(pipeline.last_result_seq)
        last_frame_id = dict(pipeline.last_frame_id)
        accepted_repeats = dict(pipeline.accepted_frame_repeats)

        malformed_values = (1.5, 5.5, "bad", 0, -1, True, 1 << 32)
        for seq, malformed_value in enumerate(malformed_values, start=2):
            with self.subTest(repeat_index=malformed_value):
                record = self._record(11, 50 + seq, seq)
                record["repeat_index"] = malformed_value
                record["repeat_declared"] = True
                outcome = pipeline.submit_result(record)
                self.assertEqual(outcome["outcome"], "invalid")
                self.assertEqual(outcome["verdict"], "FAIL")
                event = pipeline.log.submit_events()[-1]
                self.assertEqual(event["reject_reason"], "schema_violation")
                self.assertIn("repeat_index 必须是 uint32", " ".join(event["problems"]))
                self.assertEqual(pipeline.accepted_keys, accepted_keys)
                self.assertEqual(pipeline.latest, latest)
                self.assertEqual(pipeline.last_result_seq, last_result_seq)
                self.assertEqual(pipeline.last_frame_id, last_frame_id)
                self.assertEqual(pipeline.accepted_frame_repeats, accepted_repeats)
        self.assertEqual(pipeline.counters["invalid_records"], len(malformed_values))

    def test_result_key_fields_require_uint32_before_lookup(self):
        """会话键与阶段4关联键必须是精确整数并落在声明的 uint32 域内。"""
        valid = self._record(13, 60, 1)
        for field, value in (
            ("session_id", "17"),
            ("session_id", True),
            ("session_id", -1),
            ("session_id", 1 << 32),
            ("frame_id", 1.0),
            ("frame_id", -1),
            ("frame_id", 1 << 32),
            ("result_seq", "2"),
            ("result_seq", True),
            ("result_seq", 0),
            ("result_seq", 1 << 32),
        ):
            with self.subTest(field=field, value=value):
                malformed = dict(valid)
                malformed[field] = value
                self.assertTrue(R.validate_result_record(malformed))
                with self.assertRaises(P.SkeletonInputError):
                    P.result_key(malformed)
        # 边界值可通过结构校验；session/frame 为 uint32，result_seq 从 1 起。
        boundary = dict(valid, session_id=(1 << 32) - 1, frame_id=(1 << 32) - 1,
                        result_seq=(1 << 32) - 1)
        self.assertEqual(R.validate_result_record(boundary), [])

    def test_malformed_join_keys_leave_state_untouched_and_are_logged(self):
        """超范围 repeat_index 与字符串 session_id 都按 schema 拒绝并持久化原因。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        self.assertEqual(pipeline.submit_result(self._record(17, 70, 1))["outcome"], "accepted")
        accepted_keys = set(pipeline.accepted_keys)
        latest = dict(pipeline.latest)
        last_result_seq = dict(pipeline.last_result_seq)
        last_frame_id = dict(pipeline.last_frame_id)
        accepted_repeats = dict(pipeline.accepted_frame_repeats)

        overrange_repeat = self._record(17, 71, 2)
        overrange_repeat["repeat_index"] = 1 << 32
        overrange_repeat["repeat_declared"] = True
        malformed_session = self._record(17, 72, 3)
        malformed_session["session_id"] = "17"
        for record in (overrange_repeat, malformed_session):
            outcome = pipeline.submit_result(record)
            self.assertEqual(outcome["outcome"], "invalid")
            self.assertEqual(outcome["verdict"], "FAIL")
            self.assertEqual(pipeline.accepted_keys, accepted_keys)
            self.assertEqual(pipeline.latest, latest)
            self.assertEqual(pipeline.last_result_seq, last_result_seq)
            self.assertEqual(pipeline.last_frame_id, last_frame_id)
            self.assertEqual(pipeline.accepted_frame_repeats, accepted_repeats)

        with tempfile.TemporaryDirectory(prefix="s5t03_invalid_keys_") as temp_dir:
            path = pathlib.Path(temp_dir) / "events.jsonl"
            pipeline.log.dump_jsonl(path, compact=True)
            submits = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                       if json.loads(line).get("t") == "sub"]
        invalids = [event for event in submits if event["oc"] == "invalid"]
        self.assertEqual(len(invalids), 2)
        self.assertTrue(all(event["vf"] == "FAIL" and event["rr"] == "schema_violation"
                            for event in invalids))
        self.assertEqual(invalids[0]["ri"], 1 << 32)
        self.assertTrue(invalids[0]["rd"])
        self.assertEqual(invalids[1]["sid"], "17")
        audit = RC.recompute(submits)["rejection_audit"]
        self.assertEqual(audit["missing_reject_reason_events"], 0)
        self.assertEqual(audit["missing_repeat_context_events"], 0)

    def test_compact_log_persists_rejection_reasons_and_repeat_context(self):
        """N-4：落盘拒绝原因与重复声明上下文必须可审计、可由独立复算器读取。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        self.assertEqual(pipeline.submit_result(self._record(12, 30, 1))["outcome"], "accepted")
        self.assertEqual(pipeline.submit_result(self._record(12, 30, 1))["outcome"], "duplicate")
        self.assertEqual(pipeline.submit_result(self._record(12, 29, 2))["outcome"], "out_of_order")
        self.assertEqual(pipeline.submit_result(self._record(12, 30, 3))["outcome"], "duplicate_frame_id")
        declared = self._record(12, 30, 4, repeat_index=2, declared=True)
        self.assertEqual(pipeline.submit_result(declared)["outcome"], "accepted")
        overrange_repeat = self._record(12, 31, 5)
        overrange_repeat["repeat_index"] = 1 << 32
        overrange_repeat["repeat_declared"] = True
        self.assertEqual(pipeline.submit_result(overrange_repeat)["outcome"], "invalid")
        malformed_session = self._record(12, 32, 6)
        malformed_session["session_id"] = "17"
        self.assertEqual(pipeline.submit_result(malformed_session)["outcome"], "invalid")

        with tempfile.TemporaryDirectory(prefix="s5t03_repeat_log_") as temp_dir:
            path = pathlib.Path(temp_dir) / "events.jsonl"
            pipeline.log.dump_jsonl(path, compact=True)
            events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        submits = [event for event in events if event.get("t") == "sub"]
        self.assertTrue(submits)
        for event in submits:
            for field in ("rr", "ri", "rd", "rb", "pri"):
                self.assertIn(field, event, f"紧凑提交日志缺少 {field}")
        rejected = [event for event in submits if event["vf"] == "FAIL"]
        self.assertEqual(len(rejected), 5)
        self.assertTrue(all(event["rr"] for event in rejected))
        by_outcome = {event["oc"]: event for event in rejected if event["oc"] != "invalid"}
        self.assertEqual(by_outcome["duplicate"]["rr"], "duplicate_result_key")
        self.assertEqual(by_outcome["out_of_order"]["rr"], "regressed_frame_id")
        repeat_rejection = by_outcome["duplicate_frame_id"]
        self.assertEqual(repeat_rejection["ri"], 1)
        self.assertIsNone(repeat_rejection["rd"])
        self.assertEqual(repeat_rejection["rb"], "no_declaration")
        self.assertEqual(repeat_rejection["pri"], 1)
        invalids = [event for event in rejected if event["oc"] == "invalid"]
        self.assertEqual(invalids[0]["ri"], 1 << 32)
        self.assertEqual(invalids[1]["sid"], "17")
        declared_accept = [event for event in submits if event["oc"] == "accepted"][-1]
        self.assertEqual((declared_accept["ri"], declared_accept["rd"], declared_accept["rb"],
                          declared_accept["pri"]), (2, True, "repeat_declared", 1))
        audit = RC.recompute(events)["rejection_audit"]
        self.assertEqual(audit["missing_reject_reason_events"], 0)
        self.assertEqual(audit["missing_repeat_context_events"], 0)

    def test_nb1_discriminating_power_legacy_accept_would_fail(self):
        """判别力对照：复刻 r02 语义（无等价 frame_id 记忆）时该判据会变红。"""
        class _NoRepeatMemory(dict):
            def get(self, key, default=None):    # 复刻 r02：不记忆已接受 frame_id
                return None

        def submit_pair(memory_off: bool) -> str:
            pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
            if memory_off:
                pipeline.accepted_frame_repeats = _NoRepeatMemory()
            pipeline.submit_result(self._record(8, 50, 1))
            return pipeline.submit_result(self._record(8, 50, 2))["outcome"]

        self.assertEqual(submit_pair(False), "duplicate_frame_id", "现语义必须拒绝")
        self.assertEqual(submit_pair(True), "accepted",
                         "旧（r02）语义下会被放行 ⇒ 本断言具有判别力")

    def test_equiv_stream_mode_covers_rule(self):
        """NB-1 覆盖：`equiv` 流既有未声明必拒，也有声明放行。"""
        pipeline, summary = run("equiv", NEW["stream_samples"]["equiv_frames"])
        counters = summary["counters"]
        self.assertGreaterEqual(counters["duplicate_frame_id_results"], 1)
        accepted_declared = [e for e in pipeline.log.submit_events()
                             if e.get("outcome") == "accepted" and e.get("declared_repeat_basis")]
        self.assertGreaterEqual(len(accepted_declared), 1, "必须存在显式声明放行路径的覆盖")
        rejected = [e for e in pipeline.log.submit_events() if e.get("outcome") == "duplicate_frame_id"]
        for event in rejected:
            self.assertEqual(event["verdict"], P.VERDICT_FAIL)
        self.assertEqual(counters, pipeline.recompute()["counters"])
        for event in pipeline.log.submit_events():
            if event.get("outcome") == "duplicate_frame_id":
                self.assertNotIn((event["session_id"], event["frame_id"], event["result_seq"]),
                                 pipeline.accepted_keys)

    def test_duplicate_does_not_update_latest_result(self):
        """重复结果不更新最新结果：重复帧的绘制内容必须与前一帧完全相同。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        record = S.make_record(session_id=1, frame_id=5, result_seq=1, sequence=1,
                               capture_time_ns=1_000_000_000, result_time_ns=1_000_000_100,
                               inference_time_ns=1_000_000, state="OK",
                               detections=[S.make_detection(0)])
        pipeline.submit_result(record)
        first = pipeline.commit_frame(5, 1_010_000_000)["event"]
        duplicate = pipeline.submit_result(dict(record))
        self.assertEqual(duplicate["outcome"], "duplicate")
        second = pipeline.commit_frame(6, 1_020_000_000)["event"]
        self.assertEqual(first["box_px"], second["box_px"], "重复结果不得改变叠加内容")
        self.assertEqual(pipeline.counters["duplicate_results"], 1)


class T04_StaleAndExceptions(unittest.TestCase):
    """过期边界与异常分列。"""

    def _pipeline_with(self, *, age_frame_ns: int, stale_flag: bool):
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        capture = 1_000_000_000
        record = S.make_record(session_id=9, frame_id=11, result_seq=1, sequence=1,
                               capture_time_ns=capture, result_time_ns=capture,
                               inference_time_ns=1_000_000, state="OK", stale=stale_flag,
                               detections=[S.make_detection(0)])
        self.assertEqual(R.validate_result_record(record), [])
        pipeline.submit_result(record)
        return pipeline, capture

    def test_age_equals_limit_not_stale(self):
        pipeline, capture = self._pipeline_with(age_frame_ns=R.STALE_AGE_LIMIT_NS, stale_flag=False)
        event = pipeline.commit_frame(11, capture + R.STALE_AGE_LIMIT_NS)["event"]
        self.assertFalse(event["stale_effective"], "age == limit 不得判过期")
        self.assertEqual(event["stale_reason"], R.STALE_REASON_NONE)
        self.assertTrue(event["drawn"])
        self.assertEqual(pipeline.counters["stale_cleared"], 0)

    def test_age_limit_plus_one_stale_and_counted_once(self):
        pipeline, capture = self._pipeline_with(age_frame_ns=R.STALE_AGE_LIMIT_NS + 1, stale_flag=False)
        for frame_id in (11, 12, 13, 14, 15):
            event = pipeline.commit_frame(frame_id, capture + R.STALE_AGE_LIMIT_NS + 1)["event"]
            self.assertTrue(event["stale_effective"])
            self.assertFalse(event["drawn"])
            self.assertEqual(event["boxes"], 0)
        self.assertEqual(pipeline.counters["stale_cleared"], 1, "同一结果键只计一次")
        self.assertEqual(pipeline.counters["stale_cleared"],
                         pipeline.recompute()["counters"]["stale_cleared"])

    def test_explicit_stale_flag_with_small_age(self):
        pipeline, capture = self._pipeline_with(age_frame_ns=0, stale_flag=True)
        event = pipeline.commit_frame(11, capture + 1_000_000)["event"]
        self.assertTrue(event["stale_effective"])
        self.assertEqual(event["stale_reason"], R.STALE_REASON_FLAG)
        self.assertFalse(event["drawn"])

    def test_mixed_stream_exception_counters(self):
        pipeline, summary = run("mixed", NEW["stream_samples"]["mixed_frames"])
        counters = summary["counters"]
        for key in ("zero_hand_frames", "timeouts", "error_results", "dropped_frames",
                    "invalid_records", "stale_cleared", "zero_area_dropped"):
            self.assertGreaterEqual(counters[key], 1, f"{key} 必须被计数（不得隐藏异常）")
        for event in pipeline.log.commit_events():
            if event["state"] == "NO_HAND" and not event["stale_effective"]:
                self.assertEqual(event["boxes"], 0, "NO_HAND 必须 boxes=0")
                self.assertFalse(event["drawn"], "零框是合法结果，不得绘制、也不得与过期混淆")
            if event["state"] in ("TIMEOUT", "ERROR", "DROPPED"):
                self.assertFalse(event["drawn"])
                self.assertNotEqual(event["state"], "NO_HAND", "超时/错误不得冒充零框")
        invalid_expected = len([i for i in range(NEW["stream_samples"]["mixed_frames"])
                                if i % S.MIXED_MODULUS == 30])
        self.assertEqual(counters["invalid_records"], invalid_expected,
                         "无效记录数必须与注入数一致")
        self.assertEqual(counters, pipeline.recompute()["counters"], "计数必须可由事件日志复算")

    def test_hud_thirteen_fields_and_unavailable_marked(self):
        _, summary = run("mixed", NEW["stream_samples"]["mixed_frames"])
        hud = summary["hud_last"]
        self.assertEqual(sorted(hud), sorted(INHERIT["hud_fields"]))
        self.assertEqual(len(hud), 13)
        for key in ("capture_fps", "inference_fps", "display_fps"):
            self.assertEqual(hud[key], "UNAVAILABLE", f"{key} 无实测时必须标 UNAVAILABLE，不得用 0 伪装")
        self.assertEqual(hud["display_semantics"], "B_latest_result_overlay")


class T05_LongRunVirtual(unittest.TestCase):
    """长跑回归：离线虚拟时钟加速 ≥30 分钟（**不是**板上耐久）。"""

    def test_long_run_virtual_30min_no_deadlock(self):
        frames = NEW["long_run_min_frames"]
        pipeline, summary = run("mixed", frames)
        commits = pipeline.log.commit_events()
        self.assertEqual(len(commits), frames, "每显示帧必须恰好一条提交事件（缺事件即死锁）")
        self.assertEqual(summary["commit_events"], frames)
        self.assertEqual(len(pipeline.log.five_tuples()), frames)
        first, last = commits[0]["overlay_commit_ns"], commits[-1]["overlay_commit_ns"]
        elapsed = last - first
        self.assertGreaterEqual(elapsed, NEW["long_run_virtual_duration_ns"],
                                f"虚拟时长 {elapsed} ns 未达 30 分钟")
        # N-2：判据用区间数（= 帧数 − 1），并核实余量
        period = NEW["long_run_virtual_frame_period_ns"]
        period_count = NEW["long_run_period_count"]
        self.assertEqual(period_count, frames - 1, "区间数必须等于帧数 − 1")
        self.assertEqual(elapsed, period_count * period,
                         "virtual_elapsed 必须等于区间数 × 周期")
        self.assertEqual(elapsed - NEW["long_run_virtual_duration_ns"],
                         NEW["long_run_margin_ns"], "余量必须为冻结的 1.08 ms")
        previous = None
        for event in commits:
            if previous is not None:
                self.assertGreaterEqual(event["overlay_commit_ns"], previous,
                                        "提交时间戳必须单调不减")
            previous = event["overlay_commit_ns"]
        self.assertEqual(summary["counters"]["frames_committed"], frames)
        self.assertEqual(summary["counters"], pipeline.recompute()["counters"],
                         "长跑计数必须可由事件日志完全复算")
        self.assertGreaterEqual(summary["counters"]["overlay_drawn_frames"], 1)
        self.assertEqual(pipeline.counters["duplicate_results"],
                         pipeline.log.recompute()["counters"]["duplicate_results"])
        # N-4：长跑帧级事件日志随证据落盘
        long_log = dump_log(pipeline, "events_long_run.jsonl.gz")
        self.assertTrue(long_log.is_file(), "长跑事件日志必须落盘")
        self.assertEqual(LOG_DUMPS["events_long_run.jsonl.gz"]["events"], len(pipeline.log.events))
        self.assertEqual(RC.recompute_file(long_log)["counters"],
                         summary["counters"], "长跑落盘日志的独立复算必须与在线计数一致")

    def test_disk_event_log_recomputable_independently(self):
        """N-4：落盘日志必须能被**独立**复算器复算出与在线计数逐项相同的计数。"""
        pipeline, summary = run("mixed", NEW["stream_samples"]["mixed_frames"])
        path = dump_log(pipeline, "events_mixed_240.jsonl")
        self.assertIsNotNone(path)
        recomputed = RC.recompute_file(path)
        self.assertEqual(recomputed["counters"], summary["counters"],
                         "独立复算器结果必须与在线计数逐项相同")
        self.assertEqual(recomputed["commit_events"], summary["commit_events"])
        self.assertEqual(recomputed["unique_displayed_frames"], summary["commit_events"],
                         "每显示帧恰一次提交（无重复/缺失）")
        self.assertTrue(recomputed["timestamps_monotonic"])
        self.assertEqual(recomputed["rejection_audit"]["missing_reject_reason_events"], 0,
                         "落盘混合日志中每个 FAIL 提交都必须保留拒绝原因")
        self.assertEqual(recomputed["rejection_audit"]["missing_repeat_context_events"], 0,
                         "落盘混合日志必须保留 repeat/declaration 上下文键")
        self.assertGreater(recomputed["rejection_audit"]["repeated_frame_events"], 0,
                           "混合日志必须覆盖并保留重复/乱序提交上下文")
        # 格式自检：紧凑日志的字段集必须与冻结声明一致
        first_lines = path.read_text(encoding="utf-8").strip().splitlines()[:2]
        for line in first_lines:
            payload = json.loads(line)
            fields = tuple(payload)
            self.assertTrue(fields == RC.COMPACT_SUBMIT_FIELDS or fields == RC.COMPACT_COMMIT_FIELDS
                            or set(fields) <= (set(RC.COMPACT_SUBMIT_FIELDS) | set(RC.COMPACT_COMMIT_FIELDS)),
                            f"紧凑日志字段与声明不符：{fields}")

    def test_counter_units_declared(self):
        """N-3 / NB-3：JSON 14 键（14 计数 + definition）与流水线 14 条**逐字相等**。"""
        units = NEW["counter_units"]
        self.assertIn("definition", units, "JSON 必须保留 definition 说明键")
        counters = {key: value for key, value in units.items() if key != "definition"}
        self.assertEqual(len(counters), len(P.COUNTER_KEYS),
                         "JSON 计数器条目数必须与流水线 COUNTER_KEYS 相同")
        self.assertEqual(sorted(counters), sorted(P.COUNTER_KEYS))
        self.assertEqual(sorted(P.COUNTER_UNITS), sorted(P.COUNTER_KEYS))
        for key in P.COUNTER_KEYS:
            self.assertIsInstance(counters[key], str)
            self.assertTrue(counters[key].strip())
            self.assertEqual(counters[key], P.COUNTER_UNITS[key],
                             f"NB-3：{key} 的 JSON 与流水线文本必须逐字相等")


class T06_StreamSchema(unittest.TestCase):
    """合成流自身必须符合被消费记录 schema（除刻意注入的无效记录）。"""

    def test_all_modes_conform_except_injected_invalid(self):
        for mode, frames in (("sequential", NEW["frame_association_sample_frames"]),
                             ("skip", NEW["stream_samples"]["skip_frames"]),
                             ("late", NEW["stream_samples"]["late_frames"]),
                             ("dup", NEW["stream_samples"]["dup_frames"]),
                             ("ooo", NEW["stream_samples"]["ooo_frames"]),
                             ("equiv", NEW["stream_samples"]["equiv_frames"])):
            for step in stream(mode, frames):
                for record in step["results"]:
                    self.assertEqual(R.validate_result_record(record), [],
                                     f"{mode}: 合成流记录必须通过冻结 schema 校验")
                    self.assertEqual(record["source_kind"], "synthetic")
                    self.assertFalse(record["capture_time_available"])
                    self.assertIn("capture_time_ns", record["unavailable_fields"])
        invalid_seen = 0
        for step in stream("mixed", NEW["stream_samples"]["mixed_frames"]):
            for record in step["results"]:
                problems = R.validate_result_record(record)
                if problems:
                    invalid_seen += 1
                    self.assertEqual(record["state"], "NO_HAND")
        self.assertEqual(invalid_seen,
                         len([i for i in range(NEW["stream_samples"]["mixed_frames"])
                              if i % S.MIXED_MODULUS == 30]))

    def test_stream_is_deterministic_for_seed(self):
        first = stream("mixed", 64)
        second = stream("mixed", 64)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        other = stream("mixed", 64, seed=NEW["seed"] + 1)
        self.assertNotEqual(json.dumps(first, sort_keys=True), json.dumps(other, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
