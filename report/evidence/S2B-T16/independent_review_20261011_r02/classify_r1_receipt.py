"""分类真实R1审查结论，不改写探针原生退出码或原始收据。"""
from pathlib import Path
import json
import sys

receipt = Path(__file__).parent / "reviewer_r01/review_receipt.json"
result = json.loads(receipt.read_text(encoding="utf-8"))
print(result["status"])
sys.exit(0 if result["status"] == "PASS" else 2)
