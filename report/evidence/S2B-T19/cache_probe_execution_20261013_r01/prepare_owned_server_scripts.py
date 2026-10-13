"""从已核验旧服务脚本派生本次独占服务脚本，不执行设备操作。"""
from pathlib import Path
import hashlib
import json

root = Path(__file__).absolute().parents[4]
source = root / "tmp/2B/S2B-T14/jtag_readonly_20261011_r02"
folder = Path(__file__).absolute().parent
old = str(source)
new = str(folder)
rows = []
for name in ["start_owned_server.ps1", "close_owned_server.ps1"]:
    path = source / name
    if not path.is_file() or not folder.is_dir() or (folder / name).exists():
        raise RuntimeError("来源、目录或新脚本目标不符合")
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    if text.count(old) != 1:
        raise RuntimeError("原运行目录不是唯一精确字面量")
    text = text.replace(old, new)
    if name.startswith("start"):
        text = text.replace("供已审只读目标枚举使用", "供已审visibility0下载与缓存检查使用")
    else:
        text = text.replace("hardware_program_execution='NOT_RUN'", "hardware_program_execution='SEE_VISIBILITY_PROBE_RESULT'")
        text = text.replace("仅连接与枚举，SDK已disconnect/dispose", "本次易失部署与缓存观测，SDK及UART闭合见独立入口运行结果")
    with (folder / name).open("x", encoding="utf-8", newline="") as out:
        out.write(text)
    rows.append({"source": str(path), "source_sha256": hashlib.sha256(raw).hexdigest(), "derived": str(folder / name), "derived_sha256": hashlib.sha256((folder / name).read_bytes()).hexdigest(), "changes": "仅本次运行目录和操作说明文字；独占/PID/时间/映像/监听门禁保持。"})
with (folder / "server_script_bindings.json").open("x", encoding="utf-8", newline="\n") as out:
    json.dump(rows, out, ensure_ascii=False, indent=2)
    out.write("\n")
print(json.dumps(rows, ensure_ascii=False))
