"""复用原生资源监测器运行补充；不重跑消费者整组。"""

import sys
from run_native import RUN, execute

if __name__ == "__main__":
    raise SystemExit(execute("supplement", [sys.executable, "-B", str(RUN / "supplement.py")]))
