# 读 G4 的 STATE 与相关文件（用完整哈希）
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import show

G4 = "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d"
F4 = "6b8e5f2a23ce6f7dec41fc9992141b3423612081"

show(["show", G4 + ":.codex/STATE.md"])
show(["diff", "--stat", F4, G4])
show(["diff", "--name-status", F4, G4])