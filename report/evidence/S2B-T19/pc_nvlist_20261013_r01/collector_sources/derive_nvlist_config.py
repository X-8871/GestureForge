"""保持原配置生成器，仅派生新helper源码哈希绑定，不执行设备动作。"""
from pathlib import Path
import hashlib
import json
folder=Path(__file__).absolute().parent
original=folder/"prepare_visibility_config.py"
target=folder/"prepare_visibility_config_nvlist.py"
assert original.is_file() and folder.is_dir() and not target.exists()
raw=original.read_bytes();assert hashlib.sha256(raw).hexdigest()=="df86d4b6437a29dce84fb2a707021ea7953e578e61b9c18f4683e4d7bcc273f8"
old=b"06c1f46d9906d39e76f9befddcdb50eaf20cf485ddb5e5d48145ab0553143432"
new=b"4f69f848f71acb4b2ff7709a4ab40bbb892f0b205137d434f7a5f302805e1f85"
assert raw.count(old)==1
derived=raw.replace(old,new);target.write_bytes(derived)
record={"original":str(original),"original_sha256":hashlib.sha256(raw).hexdigest(),"derived":str(target),"derived_sha256":hashlib.sha256(derived).hexdigest(),"changes":"仅HELPER_SHA的一个64字符字面量；原receipt、配置字段、HEAD、身份、产物及SDK/pyserial门禁完全保留。","hardware_execution":"NOT_RUN"}
with (folder/"config_nvlist_derivation.json").open("x",encoding="utf-8",newline="\n") as out:json.dump(record,out,ensure_ascii=False,indent=2);out.write("\n")
print(json.dumps(record,ensure_ascii=False))
