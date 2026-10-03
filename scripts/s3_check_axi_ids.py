"""核对厂商参考生成 HDL 的 AXI ID 连接，不代替总线事务验证。"""

import argparse
import hashlib
import json
from pathlib import Path
import re


def inspect_connections(text):
    """检查有效一位请求零扩展到六位，响应保留相同最低位。"""
    compact = re.sub(r"\s+", "", text)
    checks = {}
    for field in ("ARID", "AWID", "WID"):
        expected = (
            f".S_AXI_HP0_{field}("
            "{1'b0,1'b0,1'b0,1'b0,1'b0,"
            f"axi_mem_intercon_M00_AXI_{field}}})"
        )
        checks[f"ps_{field}_zero_extension"] = compact.count(expected) == 1
    for field in ("BID", "RID"):
        expected = f".m_axi_{field.lower()}(xbar_to_m00_couplers_{field}[0])"
        checks[f"xbar_{field}_lower_bit"] = compact.count(expected) == 1
    return checks


def main():
    """将只读核对结果写入不存在的结果文件。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("generated_hdl", type=Path)
    parser.add_argument("new_report", type=Path)
    args = parser.parse_args()
    if not args.generated_hdl.is_absolute() or not args.generated_hdl.is_file():
        parser.error("生成 HDL 必须是存在的绝对文件路径")
    if not args.new_report.is_absolute() or not args.new_report.parent.is_dir():
        parser.error("结果必须使用绝对路径且父目录存在")
    raw = args.generated_hdl.read_bytes()
    checks = inspect_connections(raw.decode("utf-8"))
    # 两个合法的一位标识经零扩展及最低位提取仍保持不变。
    legal_ids = [0, 1]
    roundtrip = all(((value & 0x3F) & 1) == value for value in legal_ids)
    report = {
        "scope": "仅静态连接与两种一位 ID 的算术恒等检查；不是 AXI 事务仿真或板测",
        "source": str(args.generated_hdl),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "checks": checks,
        "legal_id_count": len(legal_ids),
        "roundtrip": roundtrip,
        "pass": all(checks.values()) and roundtrip,
        "limitations": ["未证明上游始终只发送合法一位 ID", "未证明 PS 的运行时响应", "不关闭 BD 位宽警告的整体事务验收项"],
    }
    with args.new_report.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print("PASS_STATIC_ID_CONNECTIONS_ONLY" if report["pass"] else "FAIL_STATIC_ID_CONNECTIONS")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
