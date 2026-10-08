"""核对冻结记录和证据映射数据，不判断批准权限或实物适用性。"""

import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]


def digest(path):
    """读取原始字节，核对完整精确文件目标。"""
    assert path.is_file(), str(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """只读核对固定源码、批准引用、53项实验和两个补充快照。"""
    approval = json.loads((RUN / "acceptance.json").read_text(encoding="utf-8"))
    mapping = json.loads((RUN / "copy_mapping.json").read_text(encoding="utf-8"))
    report = json.loads((RUN / "reviewer/review_evidence_bindings.json").read_text(encoding="utf-8"))
    assert approval["status"] == "ACCEPTED_OFFLINE_BUILD_INPUT"
    assert report["status"] == "PASS"
    assert report["issues"]["remaining_blocking_design_issues"] == []
    assert mapping["status"] == "EXACT_BYTE_COPY_PASS"
    assert len(report["artifacts"]) == 53 and len(mapping["files"]) == 55
    destinations = {item["source"]: item for item in mapping["files"]}
    assert len(destinations) == len(mapping["files"])
    for item in mapping["files"]:
        path = ROOT / item["destination"]
        assert digest(path) == item["sha256"]
        assert path.stat().st_size == item["bytes"]
    for item in report["artifacts"]:
        copied = destinations[item["path"]]
        assert copied["sha256"] == item["sha256"] and copied["bytes"] == item["bytes"]
    for item in report["source_baseline"]["fixed_files"]:
        # 原属性文件随后只追加冻结包规则，因此通过已保存快照恢复被审字节。
        path = ROOT / (destinations[item["path"]]["destination"] if item["path"] == ".gitattributes" else item["path"])
        assert digest(path) == item["sha256"]
    for name in ("formal_record", "candidate_xsa", "independent_review", "copy_mapping"):
        item = approval[name]
        assert digest(ROOT / item["path"]) == item["sha256"]
    assert approval["candidate_xsa"]["sha256"] == report["check_result"]["candidate_xsa_sha256"]
    print(json.dumps({"status": "FREEZE_BINDINGS_OK", "copied_files": 55,
                      "independent_experiment_files": 53, "blocking_design_issues": 0,
                      "scope": "只核对引用与文件数据，不代表批准权限、实物适用性或阶段2B验收"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
