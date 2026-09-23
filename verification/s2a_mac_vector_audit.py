"""独立审计 G0 冻结的 MAC 定向向量及其整数累加期望值。"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path


_EXPECTED_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_REPRODUCIBLE_COMMAND = "python -B verification/s2a_mac_vector_audit.py"
_INT32_MIN = -(1 << 31)
_INT32_MAX = (1 << 31) - 1


def _sha256(path: Path) -> str:
    """返回文件的 SHA-256 十六进制摘要。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _audit_case(vector: dict) -> dict:
    """仅按输入操作数和 bias 重新计算精确和与首次溢出位置。"""
    case_index = vector["case_index"]
    activations = vector["activation_int8"]
    weights = vector["weight_int8"]
    reduction_length = vector["k"]
    bias = vector["bias_int32"]
    if len(activations) != reduction_length or len(weights) != reduction_length:
        raise ValueError(f"case {case_index}: K 与操作数长度不一致")
    if not _INT32_MIN <= bias <= _INT32_MAX:
        raise ValueError(f"case {case_index}: bias 不在有符号 INT32 范围内")
    if any(not -128 <= value <= 127 for value in (*activations, *weights)):
        raise ValueError(f"case {case_index}: 操作数不在有符号 INT8 范围内")

    accumulator = bias
    first_overflow_index = None
    for product_index, (activation, weight) in enumerate(zip(activations, weights, strict=True)):
        accumulator += activation * weight
        if (first_overflow_index is None
                and not _INT32_MIN <= accumulator <= _INT32_MAX):
            first_overflow_index = product_index

    exact_sum = bias + sum(
        activation * weight
        for activation, weight in zip(activations, weights, strict=True)
    )
    declared_expected_result = vector["expected_int32_result"]
    recomputed_expected_result = None if first_overflow_index is not None else exact_sum
    mismatches = {
        "exact_int64_sum": exact_sum != vector["exact_int64_sum"],
        "first_int32_overflow_product_index": (
            first_overflow_index != vector["first_int32_overflow_product_index"]
        ),
        "expected_int32_result": (
            recomputed_expected_result != declared_expected_result
        ),
    }
    return {
        "case_index": case_index,
        "case_name": vector["case_name"],
        "k": reduction_length,
        "bias_int32": bias,
        "activation_int8": activations,
        "weight_int8": weights,
        "declared": {
            "exact_int64_sum": vector["exact_int64_sum"],
            "first_int32_overflow_product_index": (
                vector["first_int32_overflow_product_index"]
            ),
            "expected_int32_result": declared_expected_result,
        },
        "recomputed": {
            "exact_int64_sum": exact_sum,
            "first_int32_overflow_product_index": first_overflow_index,
            "expected_int32_result": recomputed_expected_result,
        },
        "mismatches": mismatches,
        "status": "PASS" if not any(mismatches.values()) else "MISMATCH",
    }


def main() -> int:
    """读取冻结清单、写出逐项审计证据，并按 mismatch 返回退出码。"""
    repository = Path(__file__).resolve().parents[1]
    manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
    artifact_path = repository / "report/evidence/S2A-T02/mac_directed_vector_audit.json"
    auditor_path = Path(__file__).resolve()

    manifest_bytes = manifest_path.read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    if manifest_sha256 != _EXPECTED_MANIFEST_SHA256:
        raise ValueError(
            "G0 manifest SHA-256 不匹配："
            f"expected={_EXPECTED_MANIFEST_SHA256} actual={manifest_sha256}"
        )
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    vectors = manifest["operator_test_plan"]["directed_case_vectors"]["int8_mac"]
    if len(vectors) != 16:
        raise ValueError(f"冻结 MAC 定向向量应为 16 项，实际为 {len(vectors)} 项")

    cases = [_audit_case(vector) for vector in vectors]
    mismatch_counts = {
        key: sum(case["mismatches"][key] for case in cases)
        for key in (
            "exact_int64_sum",
            "first_int32_overflow_product_index",
            "expected_int32_result",
        )
    }
    total_mismatches = sum(mismatch_counts.values())
    exit_code = 0 if total_mismatches == 0 else 1
    artifact = {
        "schema_version": 1,
        "task_id": "S2A-T02",
        "audit_id": "mac_directed_vector_audit",
        "status": "PASS" if exit_code == 0 else "MISMATCH",
        "command": _REPRODUCIBLE_COMMAND,
        "tool": {
            "name": "CPython",
            "version": platform.python_version(),
            "version_full": sys.version,
        },
        "auditor": {
            "path": "verification/s2a_mac_vector_audit.py",
            "sha256": _sha256(auditor_path),
        },
        "input": {
            "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
            "manifest_sha256": manifest_sha256,
        },
        "rules": {
            "exact_sum": "Python arbitrary-precision integer: bias plus every signed INT8 activation*weight product",
            "overflow": "After each ordered product addition, record the first prefix outside signed INT32 range",
            "expected_result": "null when any prefix overflows; otherwise equal to the exact sum",
        },
        "summary": {
            "vector_count": len(cases),
            "exact_int64_sum_mismatches": mismatch_counts["exact_int64_sum"],
            "first_int32_overflow_product_index_mismatches": mismatch_counts[
                "first_int32_overflow_product_index"
            ],
            "expected_int32_result_mismatches": mismatch_counts[
                "expected_int32_result"
            ],
            "total_mismatches": total_mismatches,
            "exit_code": exit_code,
        },
        "cases": cases,
    }
    artifact_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        "S2A-T02 directed audit: "
        f"vectors={len(cases)} mismatches={total_mismatches} "
        f"manifest_sha256={manifest_sha256} "
        f"auditor_sha256={artifact['auditor']['sha256']} "
        f"artifact_sha256={_sha256(artifact_path)}"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
