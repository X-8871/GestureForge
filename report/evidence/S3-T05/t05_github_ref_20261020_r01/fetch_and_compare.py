# 对比社区 AN5642 仓库（HenryZzz6/dual_ov5640_an5642_hdmi）的 OV5640 初始化表与我们的厂商表关键寄存器。
# 只读研究：从 GitHub contents API 拉 3 个 LUT（分辨率各自的 I2C 表）并与本仓库已知值对照。
import base64, json, os, re, subprocess, sys

D = r'D:\codex-worktrees\dbdf\tmp\3\S3-CTRL\t05_live_r01'
BASE = ('https://api.github.com/repos/HenryZzz6/dual_ov5640_an5642_hdmi/contents/'
        'Src/dual_ov5640_an5642_hdmi.srcs/sources_1/new/')
FILES = ['lut_ov5640_rgb565_640_480.v', 'lut_ov5640_rgb565_1024_768.v', 'lut_ov5640_rgb565_480_272.v']
KEY = ['4300', '501f', '5001', '503d', '3820', '3821', '3406', '3035', '3036', '4740',
       '3017', '3018', '5580', '5583', '5388', '3c07']

# 我们本仓库已核实的值（厂商 ov5640.c 表 / 上板回读）
OURS = {'4300': '60', '501f': '01', '5001': 'a3', '503d': '00(默认,测试图时0x80)', '3820': '47', '3821': '00',
        '3035': '21', '3017': 'ff', '3018': 'ff', '5580': '06', '5583': '40', '5388': '6c'}


def fetch(name):
    path = os.path.join(D, 'gh_' + name + '.json')
    if not os.path.exists(path) or os.path.getsize(path) < 200:
        url = BASE + name
        subprocess.run(['curl', '-s', '--max-time', '60', url, '-o', path], check=False)
    with open(path, encoding='utf-8') as fh:
        j = json.load(fh)
    return base64.b64decode(j['content']).decode('utf-8', 'replace')


def table(txt):
    regs = {}
    for m in re.finditer(r"24'h([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})", txt):
        regs[m.group(1).lower()] = m.group(2).lower()
    return regs


lines = []
for f in FILES:
    try:
        txt = fetch(f)
    except Exception as exc:  # noqa: BLE001
        lines.append('%s FETCH_FAIL %s' % (f, exc))
        continue
    regs = table(txt)
    lines.append('== %s  条目数=%d' % (f, len(regs)))
    for k in KEY:
        got = regs.get(k, '--')
        ours = OURS.get(k, '?')
        flag = '' if got == '--' else ('  <== 与我们的 %s 不同' % ours if got != ours else '  (同)')
        lines.append('   %-5s 社区=%-4s 我们=%s%s' % (k, got, ours, flag))
    # 打印其分辨率/输出相关条目
    rel = [l.strip() for l in txt.splitlines() if re.search(r"24'h(3808|3809|380a|380b|380c|380d|3615|3612)", l)]
    if rel:
        lines.append('   分辨率相关: ' + ' | '.join(rel[:6]))

out = os.path.join(D, 'gh_register_compare.txt')
with open(out, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print('\n'.join(lines))