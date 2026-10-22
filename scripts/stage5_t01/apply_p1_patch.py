"""S5-T01 P1 最小补丁：在阶段3 应用 `display_demo.c` 的 `DisplayStart(&dispCtrl);` 之后插入一行调用。

- 幂等（已插入则不再插入）；锚点必须**恰好出现一次**，否则报错退出（不做模糊匹配）。
- 不改动其它任何行；不修改 dbdf 源文件（只作用于本树已复制的构建目录）。
退出码：0=已打补丁/已存在；1=锚点异常；2=输入错误。
用法：python -B scripts/stage5_t01/apply_p1_patch.py <构建目录下的 display_demo.c>
"""

from __future__ import annotations

import pathlib
import sys

ANCHOR = "\tStatus = DisplayStart(&dispCtrl);"
INSERT = """
	/* S5-T01 P1（Wong 2026-10-22 决策 B）：合成视频源 + 软件叠框；本调用永不返回 */
	{
		extern void s5_overlay_loop(u8 **pFrames, u32 num_frames, u32 stride, DisplayCtrl *disp);
		s5_overlay_loop(pFrames, DISPLAY_NUM_FRAMES, DEMO_STRIDE, &dispCtrl);
	}
"""
MARKER = "s5_overlay_loop("


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: apply_p1_patch.py <display_demo.c>")
        return 2
    path = pathlib.Path(sys.argv[1])
    if not path.exists():
        print(f"[patch] 文件不存在：{path}")
        return 2
    text = path.read_text(encoding="utf-8", errors="strict")
    if MARKER in text:
        print("[patch] 已存在 S5 调用，跳过（幂等）")
        return 0
    count = text.count(ANCHOR)
    if count != 1:
        print(f"[patch] 锚点出现 {count} 次（要求恰好 1 次），拒绝打补丁")
        return 1
    patched = text.replace(ANCHOR, ANCHOR + INSERT, 1)
    path.write_text(patched, encoding="utf-8")
    print("[patch] 已在 DisplayStart 后插入 s5_overlay_loop 调用（1 处）")
    return 0


if __name__ == "__main__":
    sys.exit(main())