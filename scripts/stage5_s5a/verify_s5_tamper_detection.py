"""S5-A 包装核验：S5-C 篡改探针必须被检出（探针本身退出码 1，本包装在其检出时返回 0）。

为什么需要包装：项目交付清单 `checks[].status=PASS` 要求 `exit_code` 严格为 0；而「反例必须失败」的
原始探针按设计返回 1。本包装把「检出」翻译为 0，便于机器清单如实表达，同时不改变探针语义。
退出码：0=检出成功（探针 exit 1）；1=未检出或探针异常（含探针 exit 0 或 2）；2=环境错误。
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "stage5_s5c" / "check_s5c_stage4_regression.py"


def main() -> int:
    # Windows 控制台默认 GBK：统一改为 UTF-8 + replace，避免打印被审输出时 UnicodeEncodeError
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if not CHECKER.exists():
        print(f"[tamper] 检查器缺失：{CHECKER}")
        return 2
    with tempfile.TemporaryDirectory(prefix="s5_tamper_") as tmp:
        out_dir = pathlib.Path(tmp) / "tamper"
        cmd = [sys.executable, "-B", str(CHECKER), "--run-id", "wrap_tamper_source_order",
               "--out", str(out_dir), "--limit", "8", "--seed", "20261021",
               "--tamper-probe", "source_order"]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        print(f"[tamper] cmd: {' '.join(cmd)}")
        print(f"[tamper] probe exit_code={proc.returncode}")
        tail = (proc.stdout or "") + (proc.stderr or "")
        print("\n".join(tail.splitlines()[-4:]))
    if proc.returncode == 1:
        print("[tamper] DETECTED -> wrapper exit 0")
        return 0
    if proc.returncode in (0, 2):
        print(f"[tamper] NOT_DETECTED（探针退出码 {proc.returncode}）-> wrapper exit 1")
        return 1
    print(f"[tamper] 探针异常退出码 {proc.returncode} -> wrapper exit 1")
    return 1


if __name__ == "__main__":
    sys.exit(main())