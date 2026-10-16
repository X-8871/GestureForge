"""固定已提交的监督器运行时，使CSR诊断不读取在制监督器。"""
import hashlib
import json
from pathlib import Path
import shutil

RUN = Path(__file__).resolve().parent
OLD = RUN.parent / "control_r18_xsim_execution_20261016_r02/source_snapshot"
RUNTIME = RUN / "frozen_runtime"
expected = {
    "s2b_process_supervisor.py": "6b6a60d187914f12f04f03399cb2e70a6b423fe262d6b2f135b58d2d83f9b96a",
    "s15_job_guard.py": "102f396c0e696bc611da5759d204f0bb25ee006026a7ada85f13b6eb9325035a",
}
assert not RUNTIME.exists()
RUNTIME.mkdir()
for name, digest in expected.items():
    source = OLD / name
    assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == digest
    shutil.copy2(source, RUNTIME / name)
driver_path = RUN / "execute_xsim.py"
assert hashlib.sha256(driver_path.read_bytes()).hexdigest() == "166b35b46f9b8e3aa7dda48a545cdeada67b43b2de67f9052e7506c4cc7b2632"
driver = driver_path.read_text(encoding="utf-8")
before = 'sys.path.insert(0, str(ROOT))\nfrom verification.s2b_process_supervisor import supervise_process, GIB'
after = ('RUNTIME = EVIDENCE / "frozen_runtime"\n'
         + 'FROZEN_RUNTIME_SHA256 = ' + repr(expected) + '\n'
         + 'for runtime_name, runtime_digest in FROZEN_RUNTIME_SHA256.items():\n'
         + '    if hashlib.sha256((RUNTIME / runtime_name).read_bytes()).hexdigest() != runtime_digest:\n'
         + '        raise RuntimeError("冻结监督器运行时哈希不符")\n'
         + 'sys.path.insert(0, str(RUNTIME))\n'
         + 'from s2b_process_supervisor import supervise_process, GIB')
assert driver.count(before) == 1
driver = driver.replace(before, after)
before = 'source = ROOT / "verification" / name'
assert driver.count(before) == 1
driver = driver.replace(before, 'source = RUNTIME / name')
driver_path.write_text(driver, encoding="utf-8", newline="\n")
print(json.dumps({"driver_sha256": hashlib.sha256(driver_path.read_bytes()).hexdigest(),
                  "runtime_source": "abe095e提交中的r02原始快照；空Job准入和资源标准不改"}, ensure_ascii=False))
