#!/usr/bin/env python3
"""依据精确内容重复分析结果清理跨 split 的 HaGRIDv2 清单。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SPLIT_PRIORITY = {"train": 0, "val": 1, "test": 2}


def _now_iso() -> str:
    """返回东八区带偏移量的当前时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _sha256(path: Path) -> str:
    """计算文件 SHA-256。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_duplicate_report(path: Path) -> dict[str, Any]:
    """读取重复分析日志中的 JSON 结果行。"""

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith('{"status"'):
            payload = json.loads(line)
            if payload.get("status") != "PASS" or not isinstance(payload.get("duplicates"), dict):
                raise ValueError(f"重复分析报告状态无效：{path}")
            return payload
    raise ValueError(f"重复分析日志中未找到 JSON 结果：{path}")


def _select_drops(duplicate_report: dict[str, Any]) -> tuple[set[tuple[str, str]], list[dict[str, Any]]]:
    """按 train、val、test 优先级确定应从清单移除的行。"""

    drops: set[tuple[str, str]] = set()
    details: list[dict[str, Any]] = []
    for digest, items in duplicate_report["duplicates"].items():
        if not isinstance(items, list) or not items:
            raise ValueError(f"重复哈希组格式无效：{digest}")
        splits = {item["split"] for item in items}
        unknown = splits - set(SPLIT_PRIORITY)
        if unknown:
            raise ValueError(f"重复组含未知 split：{unknown}")
        kept_split = min(splits, key=SPLIT_PRIORITY.__getitem__)
        for item in items:
            if item["split"] == kept_split:
                continue
            key = (str(item["image"]), str(item["label"]))
            if key in drops:
                raise ValueError(f"重复行在分析结果中出现两次：{key}")
            drops.add(key)
            details.append({"hash": digest, "kept_split": kept_split, **item})
    details.sort(key=lambda item: (SPLIT_PRIORITY[item["split"]], item["image"]))
    return drops, details


def filter_manifest(input_manifest: Path, output_manifest: Path, duplicate_report_path: Path) -> dict[str, Any]:
    """生成去除跨 split 完全重复内容后的清单，不删除图片和标签。"""

    duplicate_report = _read_duplicate_report(duplicate_report_path)
    drops, drop_details = _select_drops(duplicate_report)
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    partial = output_manifest.with_name(output_manifest.name + ".partial")
    input_rows = 0
    output_rows = 0
    dropped_by_split: Counter[str] = Counter()
    seen_drops: set[tuple[str, str]] = set()
    try:
        with input_manifest.open("r", encoding="utf-8-sig", newline="") as source, partial.open(
            "w", encoding="utf-8", newline=""
        ) as target:
            reader = csv.DictReader(source)
            if not reader.fieldnames:
                raise ValueError("输入清单缺少表头")
            writer = csv.DictWriter(target, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                input_rows += 1
                key = (row.get("image", ""), row.get("label", ""))
                if key in drops:
                    seen_drops.add(key)
                    dropped_by_split[row.get("split", "")] += 1
                    continue
                writer.writerow(row)
                output_rows += 1
        if seen_drops != drops:
            missing = sorted(drops - seen_drops)
            raise ValueError(f"重复分析中的待删除行未全部出现在输入清单：{missing[:3]}")
        os.replace(partial, output_manifest)
    except Exception:
        if partial.exists():
            os.replace(partial, partial.with_suffix(partial.suffix + ".failed"))
        raise

    return {
        "status": "PASS",
        "created_at": _now_iso(),
        "input_manifest": str(input_manifest.resolve()),
        "output_manifest": str(output_manifest.resolve()),
        "duplicate_report": str(duplicate_report_path.resolve()),
        "policy": "跨 split 完全重复内容按 train > val > test 保留；只移除清单行，不删除原始图片或标签。",
        "input_manifest_sha256": _sha256(input_manifest),
        "output_manifest_sha256": _sha256(output_manifest),
        "duplicate_hashes": int(duplicate_report["duplicate_hashes"]),
        "duplicate_rows": sum(len(items) for items in duplicate_report["duplicates"].values()),
        "dropped_rows": len(drop_details),
        "dropped_by_split": dict(dropped_by_split),
        "input_rows": input_rows,
        "output_rows": output_rows,
        "dropped_items": drop_details,
    }


def main(argv: list[str] | None = None) -> int:
    """执行清单去重并输出报告。"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="原始清单")
    parser.add_argument("--output", type=Path, required=True, help="清洁清单")
    parser.add_argument("--duplicate-report", type=Path, required=True, help="重复分析日志")
    parser.add_argument("--report", type=Path, required=True, help="输出 JSON 证据")
    args = parser.parse_args(argv)
    try:
        report = filter_manifest(args.input, args.output, args.duplicate_report)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "input_rows", "output_rows", "dropped_rows", "dropped_by_split", "output_manifest_sha256")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
