import hashlib, zipfile, difflib

p3g = r'D:\codex-worktrees\w4\report\evidence\S5-T01\s5_g3_g_p3g_screen_20261030_r03\ps7_init_from_xsa.tcl'
p3b_xsa = r'D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.xsa'
g = open(p3g, 'rb').read()
with zipfile.ZipFile(p3b_xsa) as z:
    names = [n for n in z.namelist() if n.lower().endswith('ps7_init.tcl')]
    b = z.read(names[0]) if names else b''
print('p3g_sha', hashlib.sha256(g).hexdigest(), len(g))
print('p3b_sha', hashlib.sha256(b).hexdigest(), len(b))
print('identical', g == b)
if g != b:
    gl = [x.strip() for x in g.decode('utf-8', 'replace').splitlines()]
    bl = [x.strip() for x in b.decode('utf-8', 'replace').splitlines()]
    d = [l for l in difflib.unified_diff(bl, gl, lineterm='')
         if l.startswith(('+', '-')) and not l.startswith(('+++', '---'))]
    print('diff_lines', len(d))
    for l in d[:12]:
        print(l)