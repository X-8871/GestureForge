"""在执行前同步输入清单的注入时序说明和准备脚本哈希。"""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
assert not (RUN / "result.json").exists()
path = RUN / "preflight/delivery_manifest.json"
old_digest = hashlib.sha256(path.read_bytes()).hexdigest()
assert old_digest == "804ddcdff23c9ebb26290fcefed5e8efa3ee55dfcdc8be9331c9c21aeb153642"
manifest = json.loads(path.read_text(encoding="utf-8"))
for entry in manifest["files"]:
    entry["keep_reason"] = "绑定严格单线程工具设置、六份原RTL和epoch注入对照TB。"
    if entry["path"] == (RUN / "prepare_diag_run.py").relative_to(ROOT).as_posix():
        entry["sha256"] = hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
manifest["checks"][0]["reason"] = "原导出脚本逐字节验证；仅PRJ目录引用、TB诊断和epoch白盒注入时序改变，不改协议断言或验收。"
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
new_digest = hashlib.sha256(path.read_bytes()).hexdigest()
driver = RUN / "execute_xsim.py"
text = driver.read_text(encoding="utf-8")
assert text.count(old_digest) == 1
driver.write_text(text.replace(old_digest, new_digest), encoding="utf-8", newline="\n")
print(json.dumps({"preflight_sha256": new_digest, "driver_sha256": hashlib.sha256(driver.read_bytes()).hexdigest()}))
