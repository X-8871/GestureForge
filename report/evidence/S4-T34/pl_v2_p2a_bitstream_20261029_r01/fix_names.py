# P2a 修复：RTL 的 s4d_preproc_v2_wrapper 与 BD 生成的 wrapper 重名 → 重命名 RTL 模块
import io, os

STAGE = r"D:\tmp\lead\p2a_20261029_r01\src"
rtl = os.path.join(STAGE, "rtl")

old_sv = os.path.join(rtl, "s4d_preproc_v2_wrapper.sv")
new_sv = os.path.join(rtl, "s4d_preproc_v2_wrap.sv")
t = io.open(old_sv, encoding="utf-8", newline="").read()
n = t.count("s4d_preproc_v2_wrapper")
t = t.replace("s4d_preproc_v2_wrapper", "s4d_preproc_v2_wrap")
io.open(new_sv, "w", encoding="utf-8", newline="\n").write(t)
os.remove(old_sv)

bd = os.path.join(STAGE, "bd_preproc_v2.tcl")
b = io.open(bd, encoding="utf-8", newline="").read()
b = b.replace("s4d_preproc_v2_wrapper.sv", "s4d_preproc_v2_wrap.sv")
b = b.replace("-reference s4d_preproc_v2_wrapper", "-reference s4d_preproc_v2_wrap")
io.open(bd, "w", encoding="utf-8", newline="\n").write(b)

print("RENAME_OK module_refs_in_rtl=%d" % n)
for line in b.splitlines():
    if "s4d_preproc_v2_wrap" in line:
        print("BD:", line.strip())