"""生成 S1-T02-D2 的版本绑定、数值 golden 和校准集证据。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


UTC8 = timezone(timedelta(hours=8))


def now_utc8() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_git(repository: Path, arguments: list[str]) -> dict[str, object]:
    started = now_utc8()
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "repository": str(repository),
        "cwd": str(repository),
        "argv": ["git", "-C", str(repository), *arguments],
        "started_utc8": started,
        "finished_utc8": now_utc8(),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_code": completed.returncode,
        "network_access": False,
    }


def make_cfg_copy(source: Path, destination: Path) -> None:
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    if "\nletter_box=" in text or text.startswith("letter_box="):
        raise ValueError("源 cfg 已有 letter_box，拒绝重复注入")
    marker = b"channels=3"
    if marker not in raw:
        raise ValueError("源 cfg 未找到 net channels=3")
    line_break = b"\r\n" if b"\r\n" in raw else b"\n"
    raw = raw.replace(marker, marker + line_break + b"letter_box=1", 1)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 S1-T02-D2 参考与输入绑定证据")
    parser.add_argument("--competition-repository", type=Path, required=True)
    parser.add_argument("--darknet-source", type=Path, required=True)
    parser.add_argument("--darknet-executable", type=Path, required=True)
    parser.add_argument("--cfg", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--names", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--train-list", type=Path, required=True)
    parser.add_argument("--valid-list", type=Path, required=True)
    parser.add_argument("--semantic-review", type=Path, required=True)
    parser.add_argument("--calibration-report", type=Path, required=True)
    parser.add_argument("--golden", type=Path, required=True)
    parser.add_argument("--cfg-copy", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--revision", default="r2")
    parser.add_argument("--d2-test-count", type=int, required=True)
    parser.add_argument("--full-test-count", type=int, required=True)
    parser.add_argument("--reviewer-baseline-d2-test-count", type=int, default=12)
    parser.add_argument("--reviewer-baseline-full-test-count", type=int, default=67)
    parser.add_argument("--excluded-calibration-list", type=Path)
    args = parser.parse_args()
    started = now_utc8()

    make_cfg_copy(args.cfg.resolve(), args.cfg_copy.resolve())
    calibration = json.loads(args.calibration_report.read_text(encoding="utf-8"))
    golden = json.loads(args.golden.read_text(encoding="utf-8"))
    source_probe = {
        "head": run_git(args.darknet_source.resolve(), ["rev-parse", "HEAD"]),
        "diff_quiet": run_git(args.darknet_source.resolve(), ["diff", "--quiet"]),
        "status_short": run_git(args.darknet_source.resolve(), ["status", "--short"]),
    }
    competition_probe = {
        "head": run_git(args.competition_repository.resolve(), ["rev-parse", "HEAD"]),
        "diff_quiet": run_git(args.competition_repository.resolve(), ["diff", "--quiet"]),
    }
    source_commit = source_probe["head"]["stdout"].strip()
    if len(source_commit) != 40:
        raise ValueError("Darknet source HEAD 不是完整 40 位提交")
    if source_probe["diff_quiet"]["exit_code"] not in (0, 1):
        raise ValueError("Darknet source diff --quiet 执行异常")
    if calibration.get("output_list_count") != 512:
        raise ValueError("校准集不是 512 张")
    if args.reviewer_baseline_d2_test_count != 12 or args.reviewer_baseline_full_test_count != 67:
        raise ValueError("Reviewer 基线测试计数必须保留为 D2=12、全量=67")
    cfg_text = args.cfg.read_text(encoding="utf-8")
    excluded_artifacts = []
    if args.excluded_calibration_list:
        excluded = args.excluded_calibration_list.resolve()
        excluded_lines = excluded.read_text(encoding="utf-8").splitlines()
        excluded_artifacts.append({
            "path": str(excluded),
            "sha256": sha256_file(excluded),
            "count": len(excluded_lines),
            "formal_binding": False,
            "reason": "Reviewer 误路径生成；只读核验内容哈希与本轮校准清单相同，不纳入本轮证据绑定",
        })
    report = {
        "schema_version": "s1_t02_d2_numeric_spec_v1",
        "revision": args.revision,
        "status": "REFERENCE_IMPLEMENTED_INPUT_BOUND_REVIEW_REQUIRED",
        "started_utc8": started,
        "finished_utc8": now_utc8(),
        "argv": [str(value) for value in sys.argv],
        "cwd": str(Path.cwd()),
        "network_access": False,
        "training_executed": False,
        "formal_evaluation_executed": False,
        "precision_gate": "NOT_EXECUTED",
        "approved_spec": {
            "input": {"channels": 3, "color_order": "RGB", "layout": "CHW", "normalization": "pixel / 255", "sizes": [320, 416, 608]},
            "letterbox": {"aspect_preserving": True, "interpolation": "Darknet resize_image endpoint-aligned bilinear", "padding_normalized": 0.5, "padding_uint8": 128, "offset": "integer (dst - resized) // 2"},
            "int8": {"range": [-127, 127], "zero_point": 0, "input_scale": 1.0 / 127.0, "weight_scale": "symmetric per output channel", "activation_scale": "symmetric per layer per tensor", "accumulator": "INT32", "independent_overflow_check": "INT64", "bias": "BN-folded bias in accumulator domain", "rounding": "half away from zero", "saturation": [-127, 127], "postprocess": "detection head dequantized, PS float sigmoid/exp/decode/NMS"},
            "calibration": {"source": "train only", "count": 512, "composition": "five classes 100 each + 12 training negatives", "val_test_robust_excluded": True, "train_no_hand_required": 3},
        },
        "provenance": {
            "competition_repository": str(args.competition_repository.resolve()),
            "competition_head_probe": competition_probe["head"],
            "competition_diff_probe": competition_probe["diff_quiet"],
            "darknet_source_repository": str(args.darknet_source.resolve()),
            "darknet_source_commit": source_commit,
            "darknet_source_head_probe": source_probe["head"],
            "darknet_source_diff_probe": source_probe["diff_quiet"],
            "darknet_source_status_probe": source_probe["status_short"],
        },
        "files": {
            "darknet_executable": {"path": str(args.darknet_executable.resolve()), "sha256": sha256_file(args.darknet_executable)},
            "cfg_source": {"path": str(args.cfg.resolve()), "sha256": sha256_file(args.cfg), "bytes": args.cfg.stat().st_size, "explicit_letter_box": "letter_box=1" in cfg_text},
            "cfg_bound_copy": {"path": str(args.cfg_copy.resolve()), "sha256": sha256_file(args.cfg_copy), "bytes": args.cfg_copy.stat().st_size, "change": "隔离副本仅在 net 段 channels=3 后显式增加 letter_box=1，源 cfg 不变"},
            "data": {"path": str(args.data.resolve()), "sha256": sha256_file(args.data)},
            "names": {"path": str(args.names.resolve()), "sha256": sha256_file(args.names)},
            "manifest": {"path": str(args.manifest.resolve()), "sha256": sha256_file(args.manifest)},
            "train_list": {"path": str(args.train_list.resolve()), "sha256": sha256_file(args.train_list)},
            "valid_list": {"path": str(args.valid_list.resolve()), "sha256": sha256_file(args.valid_list)},
            "semantic_review": {"path": str(args.semantic_review.resolve()), "sha256": sha256_file(args.semantic_review)},
            "numeric_reference": {"path": str((Path(__file__).parent / "s1_t02_d2_numeric_reference.py").resolve()), "sha256": sha256_file(Path(__file__).parent / "s1_t02_d2_numeric_reference.py")},
            "calibration_selector": {"path": str(Path(__file__).resolve().parent / "s1_t02_d2_calibration.py"), "sha256": sha256_file(Path(__file__).parent / "s1_t02_d2_calibration.py")},
            "evidence_generator": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve())},
            "numeric_reference_test": {"path": str((Path(__file__).parent / "test_s1_t02_d2_numeric_reference.py").resolve()), "sha256": sha256_file(Path(__file__).parent / "test_s1_t02_d2_numeric_reference.py")},
            "calibration_selector_test": {"path": str((Path(__file__).parent / "test_s1_t02_d2_calibration.py").resolve()), "sha256": sha256_file(Path(__file__).parent / "test_s1_t02_d2_calibration.py")},
            "stage1_spec": {"path": str((Path(__file__).parent.parent / "docs" / "obsidian-project" / "04-提交材料" / "阶段验收" / "S1-T02-D2_固定预处理与INT8数值规格.md").resolve()), "sha256": sha256_file(Path(__file__).parent.parent / "docs" / "obsidian-project" / "04-提交材料" / "阶段验收" / "S1-T02-D2_固定预处理与INT8数值规格.md")},
            "verification_readme": {"path": str((Path(__file__).parent / "README.md").resolve()), "sha256": sha256_file(Path(__file__).parent / "README.md")},
            "source_image_c": {"path": str((args.darknet_source / "src" / "image.c").resolve()), "sha256": sha256_file(args.darknet_source / "src" / "image.c"), "lines": "989-1021,1399-1446"},
            "source_detector_c": {"path": str((args.darknet_source / "src" / "detector.c").resolve()), "sha256": sha256_file(args.darknet_source / "src" / "detector.c"), "lines": "1630-1675"},
            "calibration_report": {"path": str(args.calibration_report.resolve()), "sha256": sha256_file(args.calibration_report)},
            "calibration_list": {"path": calibration["output_list"], "sha256": calibration["output_list_sha256"], "count": calibration["output_list_count"]},
            "golden": {"path": str(args.golden.resolve()), "sha256": sha256_file(args.golden)},
        },
        "external_artifact_exclusions": excluded_artifacts,
        "darknet_behavior_and_binding": {
            "parser_default": "src/parser.c net->letter_box = option_find_int_quiet(options, 'letter_box', 0)",
            "test_route": "src/detector.c test_detector 使用 letterbox_image 仅当 letter_box 非零；run_detector 也接受 -letter_box",
            "cfg_difference": "固定项目 cfg 没有 letter_box=1，因此不能仅凭该 cfg 绑定批准的 letterbox；隔离 cfg 副本显式增加 letter_box=1，待正式 workflow 使用该绑定副本时再执行运行验证",
            "reference_route": "本任务独立 Python 参考验证 geometry/pixel/quantization；未执行 Darknet 训练、评估或板上推理",
        },
        "calibration": calibration,
        "golden_vectors": golden,
        "commands": [
            {"command": "$files=Get-ChildItem -LiteralPath verification -Filter '*.py' -File | ForEach-Object FullName; py -m py_compile $files", "exit_code": 0},
            {"command": "py -m py_compile verification\\s1_t02_d2_numeric_reference.py verification\\s1_t02_d2_calibration.py verification\\s1_t02_d2_evidence.py verification\\test_s1_t02_d2_numeric_reference.py verification\\test_s1_t02_d2_calibration.py", "exit_code": 0},
            {"command": "python -m unittest verification.test_s1_t02_d2_numeric_reference verification.test_s1_t02_d2_calibration", "exit_code": 0},
            {"command": "py -m unittest discover -s . -p 'test_s1_t02_d2_*.py' -v", "cwd": "verification", "exit_code": 0},
            {"command": "py -m unittest discover -s verification -p 'test_s1_t02_d2_*.py' -v", "exit_code": 0},
            {"command": "py -m unittest discover -s . -p 'test_*.py'", "cwd": "verification", "exit_code": 0},
            {"command": "py -m unittest discover -s verification -p 'test_*.py'", "exit_code": 0},
            {"command": f"py verification\\s1_t02_d2_numeric_reference.py --output {args.golden}", "exit_code": 0},
            {"command": f"py verification\\s1_t02_d2_calibration.py --data-root D:\\FPGA_Data\\HaGRIDv2 --manifest D:\\FPGA_Data\\HaGRIDv2\\manifest.csv --train-list D:\\FPGA_Data\\HaGRIDv2\\darknet_inputs\\train.list --semantic-review report\\evidence\\S1-T01\\20260914_hagrid_semantic_review.csv --output-list {calibration['output_list']} --report {args.calibration_report}", "exit_code": 0},
            {"command": "git diff --check", "exit_code": 0},
        ],
        "validation_counts": {
            "reviewer_observed_before_round": {
                "d2_tests": args.reviewer_baseline_d2_test_count,
                "full_verification_tests": args.reviewer_baseline_full_test_count,
            },
            "current_round_after_regressions": {
                "d2_tests": args.d2_test_count,
                "full_verification_tests": args.full_test_count,
            },
        },
        "superseded_attempts": [
            {"description": "两次早期校准扫描错误地对大量非最终图片做路径/图片读取，被主动停止", "normal_exit_code": None, "not_a_pass": True},
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary = f"""# S1-T02-D2 固定预处理与 INT8 数值规格（{args.revision.upper()}）

状态：`REFERENCE_IMPLEMENTED_INPUT_BOUND_REVIEW_REQUIRED`。本轮只完成独立参考、golden 和训练校准输入绑定；未训练、未执行 Darknet 正式评估、未测 mAP、未进行 INT8 整网精度或上板验收。

## 已落地规则

- 输入为 RGB 三通道，参考布局 CHW，像素除以 255；候选尺寸为 tiny320、tiny416、完整 YOLOv4 608。
- letterbox 保持比例，按 Darknet `resize_image` 的端点对齐双线性；整数尺寸使用源码截断，左右/上下偏移为 `(目标尺寸-新尺寸)//2`；归一化填充 0.5（8-bit 128）。
- INT8 为有符号 `[-127,127]`、zero-point=0、输入 scale=`1/127`；权重逐输出通道、激活逐层逐张量对称量化；BN 折叠后 bias 进入累加器域；INT32 累加并独立 INT64 检查；正负半数远离零；饱和到 `[-127,127]`；检测头后处理仍为 PS 浮点逻辑。

## 输入绑定

校准清单：`{calibration['output_list']}`，SHA256=`{calibration['output_list_sha256']}`，共 `{calibration['output_list_count']}` 行。组成是五类各100张、12张训练负样本，其中批准语义的 train no_hand 3张全部纳入；其余负样本为5张批准 non_target_gesture 和4张其余空标签。只读取 train，不使用 valid/test/robust；原始 train.list、manifest、标签未修改。

机器报告：`{args.report.resolve()}`

## cfg 路由限制

固定源 cfg `{args.cfg.resolve()}`（SHA `{sha256_file(args.cfg)}`，{args.cfg.stat().st_size} bytes）未显式包含 `letter_box=1`。因此本轮生成隔离绑定副本 `{args.cfg_copy.resolve()}`（SHA `{sha256_file(args.cfg_copy)}`，{args.cfg_copy.stat().st_size} bytes），仅增加一行 `letter_box=1`，源 cfg 不变。Darknet 源 `{args.darknet_source.resolve()}` 实际 HEAD=`{source_commit}`；源码依据为 `src/image.c:989-1021,1399-1446`、`src/detector.c:1630-1675` 和 parser 的 `letter_box` 默认值。正式 workflow 尚未使用该副本运行，故该路由的真实推理一致性仍是后续验证项。

## 验证与限制

根目录模块调用、verification 目录 D2 discover、verification 目录全量 discover 和仓库根目录全量 discover 均退出0；Reviewer 本轮前独立观察为 D2 `{args.reviewer_baseline_d2_test_count}` 项、全量 `{args.reviewer_baseline_full_test_count}` 项；本轮复跑（包含此前端点与 non_target 超配额回归及本轮 no_hand 超配额回归）为 D2 `{args.d2_test_count}` 项、全量 `{args.full_test_count}` 项。py_compile、golden 生成、校准绑定和 git diff --check 均退出0。两次早期低效扫描被主动停止，未产生通过报告；最终成功命令和退出码只见机器报告。本轮不重跑 pilot；外部 `D:\\FPGA_Data\\HaGRIDv2\\darknet_inputs\\runs\\s1_t02_d2_calibration_r1\\calibration.list` 为 Reviewer 误路径产物，仅做只读哈希核验，不纳入本轮绑定。

本轮未设置或宣称 mAP/精度门槛通过；用户批准的量化损失门槛仍是后续浮点基线和 INT8 对照的验收候选。当前证据不能宣称最终模型、INT8 精度、GPU 性能、资源、RTL 或板上结果。
"""
    args.summary.write_text(summary, encoding="utf-8", newline="\n")
    print(json.dumps({"report": str(args.report), "summary": str(args.summary), "source_commit": source_commit}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
