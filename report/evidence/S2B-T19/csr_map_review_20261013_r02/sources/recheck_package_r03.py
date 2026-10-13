"""保留检查字段缺失原件，补齐未执行项的null并重核包装。"""
from pathlib import Path
source=Path(__file__).with_name("recheck_package.py").read_text(encoding="utf-8")
source=source.replace('    data["files"]=', '    data["checks"][2].update(command=None,exit_code=None)\n    data["files"]=')
source=source.replace("evidence_check_r02_","evidence_check_r03_")
source=source.replace('"final_review_receipt_r03.json"','"final_review_receipt_r04.json"')
source=source.replace('receipt["limitations"].append(', 'receipt["limitations"].append("提升后的第一次检查native2为NOT_RUN缺少command/exit_code字段；原始日志保留，补齐null后重核。")\nreceipt["limitations"].append(')
exec(compile(source,str(Path(__file__)),"exec"))
