"""仅供本轮自有原生轻量夹具；不提供生产启动入口。"""
import json
from pathlib import Path
import sys
import supervisor

if __name__ == "__main__":
    directory = supervisor.exact(sys.argv[1], True)
    binding = json.loads((directory/"binding.json").read_text(encoding="utf-8"))
    if binding.get("fixture_test") is not True:
        raise ValueError("仅允许显式fixture")
    command = [sys.executable, "-X", "utf8", "-B", str(supervisor.GUARD), "--plan", str(directory/"plan.json"), "--binding", str(directory/"binding.json"), "--output-dir", str(directory/"supervision"/"guard")]
    inputs = [{"path": str(path), "sha256": supervisor.sha(path)} for path in (supervisor.GUARD, directory/"plan.json", directory/"binding.json")]
    raise SystemExit(supervisor.supervise(command, binding, directory/"supervision", inputs))
