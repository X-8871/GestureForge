"""从精确旧原件生成最小隔离兼容草稿，保留可复核差异及来源哈希。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import compat_pins as p

WORK=p.WORK; ROOT=p.ROOT
INPUTS={
 "tmp/2B/S2B-T17/s12_physical_prepare_20261012_r01/execution_plan.json":"9163d0d6369f0bece4af19911099cd600f9890e3de359c11eb3dcb7d472119c7",
 "tmp/2B/S2B-T17/s12_physical_prepare_20261012_r01/collector_patch_plan.json":"0ec53c6fbd8243af8b8d512f40fd8668338118143c9a199c607b107cb5225d84",
 "tmp/2B/S2B-T17/s11_collection_20261012_r01/collector.py":"8bb59a7485a2f03adb6d71d5923913d724952077a961af208fff18f76b8c6cc9",
 "tmp/2B/S2B-T17/s11_collection_20261012_r01/native.py":"d6a8860f910444e76d5526e47a2167fe54685f5cdbc823665ee29e6722d2f3c3",
 "tmp/2B/S2B-T17/s11_impl_collection_20261012_r01/collector.py":"ee0e697b59d7a9b9b6de22bd44fc93c7fbedade1e1710dd7dfb909e1654a8d35",
 "tmp/2B/S2B-T17/s11_impl_collection_20261012_r01/source_after_check.py":"15edba9468b8dd3c99dc55135913cbc98d2f625220d94a10f76b18601346b3a8",
 "tmp/2B/S2B-T17/s11_impl_collection_20261012_r01/native_source_after.py":"8e9a12ce58f5ec045cd6c454d62936d918b6f6a47fa15d096243591855d57ddd",
 "tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/guard.py":p.GUARD_SHA,
 "tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/supervisor.py":p.SUP_SHA,
 "report/evidence/S2B-T17/s12_resource_guard_delivery_20261012_r01/archive_mapping.json":p.MAPPING_SHA,
 "report/evidence/S2B-T17/s12_resource_guard_delivery_20261012_r01/recovery_entry.json":p.RECOVERY_SHA,
}

def write(name,text):
 """仅写新草稿；旧失败、准备和正式包不可覆盖。"""
 with (WORK/name).open('x',encoding='utf-8',newline='') as stream: stream.write(text)

def replace_once(text,old,new):
 """结构不吻合即停止，禁止猜测性替换。"""
 p.require(text.count(old)==1,'替换目标不唯一：'+old)
 return text.replace(old,new)

def assignment(text,name,value):
 """仅替换独立常量行，不触碰业务计算。"""
 pattern=r'^'+name+r'=.*$'
 p.require(len(re.findall(pattern,text,re.M))==1,'常量不唯一：'+name)
 return re.sub(pattern,name+'='+value,text,flags=re.M)

def add_gates(text,names,pnr=False):
 """公开运行入口第一条有效语句前加入冻结拒绝门禁。"""
 nodes=[node for node in ast.parse(text).body if isinstance(node,ast.FunctionDef) and node.name in names]
 p.require(len(nodes)==len(names),'入口函数缺失')
 lines=text.splitlines(True)
 for node in sorted(nodes,key=lambda n:n.lineno,reverse=True):
  first=node.body[0]
  after=first.end_lineno if isinstance(first,ast.Expr) and isinstance(first.value,ast.Constant) and isinstance(first.value.value,str) else node.lineno
  lines.insert(after,' '*first.col_offset+'compat_pins.require_ready('+('pnr=True' if pnr else '')+')\n')
 return ''.join(lines)

def emit(name,original,new):
 """语法解析与完整逐行差异同时保存，不能仅给摘要。"""
 ast.parse(new)
 write(name,new)
 write(name+'.diff',''.join(difflib.unified_diff(original.splitlines(True),new.splitlines(True),fromfile='原件:'+name,tofile='S12隔离草稿:'+name)))

def main():
 """完整草稿可导入/help，但真实pins不足时运行入口全部BLOCKED。"""
 sources={}; rows=[]
 for name,digest in INPUTS.items():
  path=p.pinned(ROOT/name,digest); raw=path.read_bytes()
  sources[name]=raw.decode('utf-8')
  rows.append(dict(path=name,absolute_path=str(path),sha256=digest,bytes=len(raw)))
 write('input_bindings.json',json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 old=sources['tmp/2B/S2B-T17/s11_collection_20261012_r01/collector.py']
 new=old.replace('s11_','s12_').replace('S11','S12').replace('s2b-inference-platform/0.1.11','s2b-inference-platform/0.1.12')
 new=replace_once(new,'ROOT=Path(__file__).parents[4]','import compat_pins\nROOT=Path(__file__).parents[4]')
 for name,value in dict(WORK='Path(__file__).parent',CACHE='compat_pins.SYNTH_CACHE',PROJECT='compat_pins.PROJECT',REPORT='compat_pins.SYNTH_REPORT',PRE='compat_pins.SOURCE_PRE',FREEZE='compat_pins.SOURCE_FREEZE',FREEZE_SHA='compat_pins.SOURCE_FREEZE_SHA').items(): new=assignment(new,name,value)
 new=add_gates(new,('load_freeze','prepare','source','closed_gate','collect','seal'))
 new=replace_once(new,'for name in ("collector.py","native.py"):', 'for name in ("collector.py","native.py","compat_pins.py"):')
 new=replace_once(new,'for path in (WORK/"collector.py",WORK/"native.py",ROOT/gate["preparation_receipt"]["path"],CLASSIFIER):', 'for path in (WORK/"collector.py",WORK/"native.py",WORK/"compat_pins.py",ROOT/gate["preparation_receipt"]["path"],CLASSIFIER):')
 new=replace_once(new,'hashes={r["path"]:r["sha256"] for r in rows}','hashes={r["path"]:r["sha256"] for r in rows}\n    require(len(hashes)==43,"本轮冻结43源闭包不同")')
 new=replace_once(new,'static=checker.check_static(ROOT)','static=checker.check_static(ROOT)\n    require(len(static)==33,"本轮实际static33闭包不同")')
 emit('collector.py',old,new)
 common_sha=hashlib.sha256((WORK/'collector.py').read_bytes()).hexdigest()
 old=sources['tmp/2B/S2B-T17/s11_impl_collection_20261012_r01/collector.py']
 new=old.replace('s11_','s12_').replace('S11','S12').replace('s2b-inference-platform/0.1.11','s2b-inference-platform/0.1.12')
 new=replace_once(new,'ROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent','import compat_pins\nROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent')
 replacements=dict(CACHE='compat_pins.PNR_CACHE',PROJECT='compat_pins.PROJECT',REPORT='compat_pins.PNR_REPORT',COMMIT='compat_pins.SOURCE_COMMIT',EVIDENCE_HEAD_AT_PREPARATION='None',COMMON='WORK/\'collector.py\'',COMMON_SHA=repr(common_sha),FREEZE='compat_pins.SOURCE_FREEZE',FREEZE_SHA='compat_pins.SOURCE_FREEZE_SHA',SYNTH='compat_pins.SYNTH_MANIFEST',SYNTH_SHA='compat_pins.SYNTH_MANIFEST_SHA',REVIEW="ROOT/'tmp/2B/S2B-T17/independent_s12_resource_guard_r04_review_20261012_r01/final_review_receipt.json'",REVIEW_SHA="'f528d50934d7e5c4c4cadbc0ae6db2d9708806d992cc222499de06e3ad83d350'",GUARD='compat_pins.GUARD',GUARD_SHA='compat_pins.GUARD_SHA',SUP='compat_pins.SUP',SUP_SHA='compat_pins.SUP_SHA')
 for name,value in replacements.items(): new=assignment(new,name,value)
 start=new.index('def permanent(path):'); end=new.index('def prepare(',start)
 new=new[:start]+'''def permanent(path):
 """正式原件直接绑定；临时工具只从S12正式映射核原恢复路径/SHA。"""
 if path.is_relative_to(ROOT/'report'): return c.binding(path)
 return compat_pins.resolve_permanent(path)
'''+new[end:]
 old_binding=next(line for line in new.splitlines() if line.startswith(' source_binding='))
 new=replace_once(new,old_binding," source_binding=SYNTH.parent/'s12_source_binding.json'; bound=c.read(source_binding)")
 old_deps=next(line for line in new.splitlines() if line.startswith(' deps=['))
 new=replace_once(new,old_deps," deps=[c.binding(FREEZE),c.binding(SYNTH),c.binding(source_binding),c.binding(compat_pins.FUNCTIONAL_G1),c.binding(compat_pins.FUNCTIONAL_G2),c.binding(compat_pins.SYNTH_G2),c.binding(WORK/'compat_pins.py'),permanent(REVIEW),permanent(REVIEW.with_name('raw_manifest.jsonl')),permanent(GUARD),permanent(SUP)]")
 new=replace_once(new,"WORK/'source_after_check.py',WORK/'native_source_after.py'):","WORK/'source_after_check.py',WORK/'native_source_after.py',WORK/'compat_pins.py'):")
 new=new.replace("'prepared_receipt_r04.json'","'prepared_receipt.json'")
 new=new.replace("['launch_invalid','launch','wait','open_run','reports','close']","['launch','wait','open_run','reports','close']")
 new=replace_once(new,"('launch_invalid','launch','wait','open_run','reports','close')","('launch','wait','open_run','reports','close')")
 old_invalid=" c.require(tags['launch_invalid']['code']==1 and '-to_step' in tags['launch_invalid']['command'],'非法to_step失败原件不同')"
 new=replace_once(new,old_invalid," c.require(labels.count('launch_invalid')<=1,'实际invalid失败记录重复')\n if 'launch_invalid' in tags:\n  invalid=tags['launch_invalid']\n  c.require(isinstance(invalid['code'],int) and not isinstance(invalid['code'],bool) and invalid['code']!=0 and invalid['command']=='launch_runs impl_1 -to_step post_route_phys_opt_design -jobs 1','可选历史invalid必须是真实非0精确失败原件')")
 new=new.replace('继承综合FAIL，不由包装0关闭。','继承本轮真实综合STA状态，不由包装0关闭。').replace('不将932051证据HEAD改作被测RTL基线。','准备期HEAD未冻结，不用旧证据HEAD替代本轮源码基线。')
 new=add_gates(new,('prepare','closed_gate','collect'),True)
 emit('impl_collector.py',old,new)
 old=sources['tmp/2B/S2B-T17/s11_impl_collection_20261012_r01/source_after_check.py']
 new=old.replace('S11','S12').replace('s11_','s12_')
 new=replace_once(new,'ROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent','import compat_pins\nROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent')
 for name,value in dict(COMMIT='compat_pins.SOURCE_COMMIT',CACHE='compat_pins.PNR_CACHE',COMMON="WORK/'collector.py'",COMMON_SHA=repr(common_sha)).items(): new=assignment(new,name,value)
 new=replace_once(new,"args=parser.parse_args(); assert re.fullmatch('[0-9a-f]{40}',args.expected_head)","args=parser.parse_args(); compat_pins.require_ready(pnr=True); assert re.fullmatch('[0-9a-f]{40}',args.expected_head)")
 new=replace_once(new,"before_path=ROOT/'report/evidence/S2B-T17/s12_source_preflight_20261012_r01/source_before.json'; before=c.read(before_path)","before_path=compat_pins.SOURCE_PRE/'source_before.json'; before=c.read(before_path)")
 new=new.replace("str(ROOT/'tmp/2B/S2B-T17/s11p1')","str(compat_pins.PROJECT)").replace("str(ROOT/'report/evidence/S2B-T17/s12_implementation_20261012_r01')","str(compat_pins.PNR_REPORT)")
 new=new.replace('继承before/a710/43/原14不符','继承本轮before/commit/43/原14不符').replace('43份Git blob逐项按a710核对','43份Git blob逐项按本轮COMMIT核对')
 emit('source_after_check.py',old,new)
 old=sources['tmp/2B/S2B-T17/s11_impl_collection_20261012_r01/native_source_after.py']
 new=replace_once(old,"ROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent; CACHE=ROOT/'tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01'","import compat_pins\nROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent; CACHE=compat_pins.PNR_CACHE")
 new=replace_once(new,'args=parser.parse_args(); out=args.output_dir','args=parser.parse_args(); compat_pins.require_ready(pnr=True); out=args.output_dir')
 emit('native_source_after.py',old,new)
 old=sources['tmp/2B/S2B-T17/s11_collection_20261012_r01/native.py']
 new=old.replace('s11_','s12_')
 new=replace_once(new,'from collector import CACHE,ROOT,WORK,binding,exact,fresh,save,require','import compat_pins\nfrom collector import CACHE,ROOT,WORK,binding,exact,fresh,save,require')
 new=replace_once(new,'args=parser.parse_args()','args=parser.parse_args()\ncompat_pins.require_ready()')
 emit('native.py',old,new)
 resolved=[p.resolve_permanent(path,digest) for path,digest in ((p.GUARD,p.GUARD_SHA),(p.SUP,p.SUP_SHA))]
 write('recovery_resolution.json',json.dumps(dict(status='READ_ONLY_FIXED_RESTORE_MAPPING_VERIFIED',objects=resolved,restore_executed=False),ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(dict(status='DRAFTS_GENERATED_BLOCKED_PENDING_REAL_PINS',count=5,common_sha256=common_sha,input_count=len(rows)),ensure_ascii=False))

if __name__=='__main__': main()
