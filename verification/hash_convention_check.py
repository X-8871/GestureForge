#!/usr/bin/env python3
"""O1 换行口径接受器的**双向反例**验证（工作区修正的判别力证明）。

用例（每个方向各一，外加一个负例）：
* `case_declared_lf_file_lf`：清单声明 LF 哈希、文件为 LF → 必须接受（原字节路径）
* `case_declared_crlf_file_crlf`：清单声明 CRLF 哈希、文件为 CRLF → 必须接受（原字节路径）
* `case_declared_lf_file_crlf`：清单声明 LF 哈希、文件为 CRLF → 必须接受（CRLF→LF 方向）
* `case_declared_crlf_file_lf`：清单声明 CRLF 哈希、文件为 LF → 必须接受（**LF→CRLF 反方向**；即 inputs[0] 那类失配）
* `case_negative_content_differs`：声明另一内容的哈希 → 必须**拒绝**（防止接受器过宽）

实现方式：直接调用 `verification/check_stage_delivery.py` 里真实的 `_check_hash`（不是复刻逻辑），
因此证明的是交付检查器实际使用的接受器。退出码 0 = 全部符合预期，1 = 存在不符合项。
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(r"D:\codex-worktrees\w6")
CHECKER = ROOT / "verification/check_stage_delivery.py"
OUT = ROOT / "tmp/6/hash_convention_check.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_stage_delivery_mod", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    checker = load_checker()
    assert hasattr(checker, "verify_hash"), "交付检查器未暴露 verify_hash"
    assert hasattr(checker, "hash_variants"), "交付检查器未提供 hash_variants（双向接受器）"

    body_crlf = b'{\r\n  "k": "\xe4\xb8\xad\xe6\x96\x87",\r\n  "n": 1\r\n}\r\n'
    body_lf = body_crlf.replace(b"\r\n", b"\n")
    other = b'{\n  "k": "other",\n  "n": 2\n}\n'
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        file_crlf = tmp_path / "crlf.json"
        file_lf = tmp_path / "lf.json"
        file_other = tmp_path / "other.json"
        file_crlf.write_bytes(body_crlf)
        file_lf.write_bytes(body_lf)
        file_other.write_bytes(other)
        cases = [
            ("case_declared_lf_file_lf", file_lf, sha(body_lf), True, "清单 LF ↔ 文件 LF"),
            ("case_declared_crlf_file_crlf", file_crlf, sha(body_crlf), True, "清单 CRLF ↔ 文件 CRLF"),
            ("case_declared_lf_file_crlf", file_crlf, sha(body_lf), True, "CRLF→LF 方向"),
            ("case_declared_crlf_file_lf", file_lf, sha(body_crlf), True, "LF→CRLF 反方向"),
            ("case_negative_content_differs", file_other, sha(body_crlf), False, "内容不同必须拒绝"),
        ]
        for case_id, path, declared, should_accept, note in cases:
            errors: list[str] = []
            warnings: list[str] = []
            checker.verify_hash(path, declared, f"{case_id}: ", errors, warnings, {})
            accepted = not errors
            results.append({
                "case_id": case_id,
                "note": note,
                "declared": declared[:16] + "…",
                "file_bytes_convention": "CRLF" if b"\r\n" in path.read_bytes() else "LF",
                "expected": "ACCEPT" if should_accept else "REJECT",
                "observed": "ACCEPT" if accepted else "REJECT",
                "verdict": "AS_EXPECTED" if accepted == should_accept else "UNEXPECTED",
                "errors": errors,
                "hash_variants": sorted(h[:12] + "…" for h in checker.hash_variants(path)),
            })

    payload = {
        "schema_version": 1,
        "artifact": "hash_convention_counterexamples",
        "rule": "O1 换行口径：清单可绑原字节/归一化(LF)哈希；接受器接受原字节、CRLF→LF、LF→CRLF 三种口径，但内容不同必须拒绝。",
        "checker": "verification/check_stage_delivery.py::verify_hash（真实函数，未复刻）",
        "cases": results,
        "verdict": ("ALL_AS_EXPECTED" if all(r["verdict"] == "AS_EXPECTED" for r in results)
                    else "UNEXPECTED_RESULT"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"],
                      "cases": [(r["case_id"], r["observed"], r["verdict"]) for r in results]},
                     ensure_ascii=False))
    return 0 if payload["verdict"] == "ALL_AS_EXPECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())