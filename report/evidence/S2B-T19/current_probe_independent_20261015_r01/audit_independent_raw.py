import ast,json,re,runpy,struct,hashlib,zipfile,xml.etree.ElementTree as ET,sys
from pathlib import Path
root=Path.cwd(); sys.path.insert(0,str(root/'verification')); run=root/'report/evidence/S2B-T19/current_probe_scope_20261015_r01'; summary=json.loads((run/'summary.json').read_text(encoding='utf-8')); a=summary['audit']; sha=lambda b:hashlib.sha256(b).hexdigest()
for rel,h in a['input_sha256'].items(): assert sha((root/rel).read_bytes())==h,rel
v0=root/'report/evidence/S2B-T19/visibility0_hp_rebuild_20261014_r02'; v1=root/'report/evidence/S2B-T19/visibility1_timing_current_20261014_r01'; bsp=root/'report/evidence/S2B-T15/visibility1_xsa_20261014_r02'
art=a['bound_artifacts_without_platform_manifest']; assert set(art)=={'compiled_xsa','implemented_xsa','init_elf','app_elf','bit','build_details'}
for key,x in art.items(): assert Path(x['path']).is_file() and sha(Path(x['path']).read_bytes())==x['sha256'],key
z={}
for kind in ['compiled_xsa','implemented_xsa']:
 with zipfile.ZipFile(art[kind]['path']) as f:
  assert f.testzip() is None and len(f.namelist())==len(set(f.namelist()))
  z[kind]={name:f.read(name) for name in f.namelist()}
 assert json.loads(z[kind]['xsa.json'])['devices'][0]['part']['name']=='xc7z020clg400-2'
trees={k:ET.fromstring(v['s2b_inference.hwh']) for k,v in z.items()}
params=[{x.get('NAME'):x.get('VALUE') for x in t.findall(".//MODULE[@INSTANCE='ps7']/PARAMETERS/PARAMETER")} for t in trees.values()]
assert len(params[0])==937 and params[0]==params[1]
for name in ['ps7_init.c','ps7_init.h','ps7_init.html','ps7_init.tcl','ps7_init_gpl.c','ps7_init_gpl.h']:
 assert z['compiled_xsa'][name]==z['implemented_xsa'][name]
 if (bsp/name).is_file():assert (bsp/name).read_bytes()==z['compiled_xsa'][name]
parser=runpy.run_path(str(root/'verification/check_s2b_ps_smoke_layout.py'))
parsed={}
for name in ['infer.elf','init.elf']:
 raw=(bsp/name).read_bytes(); e=parser['parse_elf'](raw); parsed[name]=e
 sec=next(s for s in e['sections'] if s['name']=='.mmu_tbl'); table=struct.unpack_from('<4096I',raw,sec['offset'])
 assert all(table[i]==(i<<20)|0x15de6 for i in range(0x100,0x120))
 assert table[0x43c]==0x43c00c02 and table[0xe00]==0xe0000c06
 for i in range(0x100,0x120):
  assert [n for n,x in enumerate(table) if x&3==2 and x&0xfff00000==i<<20]==[i]
parser['verify_cache_contract']((bsp/'xil_cache.c').read_text(encoding='utf-8'))
mac=(bsp/'xparameters.h').read_text(encoding='utf-8')
for k,v in {'XPAR_UART1_BASEADDR':0xe0001000,'XPAR_UART1_HIGHADDR':0xe0001fff,'XPAR_UART1_CLOCK_FREQ':100000000,'XPAR_INFER_BASEADDR':0x43c00000,'XPAR_INFER_HIGHADDR':0x43c0ffff,'XPAR_PS7_DDR_0_BASEADDRESS':0x100000,'XPAR_PS7_DDR_0_HIGHADDRESS':0x3fffffff}.items():
 assert parser['macro_int'](mac,k)==v
assert [x.attrib for x in trees['compiled_xsa'].findall('.//MEMRANGE')]==[x.attrib for x in trees['implemented_xsa'].findall('.//MEMRANGE')]
for kind,visibility in [('compiled_xsa','1'),('implemented_xsa','0')]:
 infer=trees[kind].findall(".//MODULE[@INSTANCE='infer']"); assert len(infer)==1 and infer[0].get('MODTYPE')=='s2b_inference_top'
 assert {x.get('NAME'):x.get('VALUE') for x in infer[0].findall('./PARAMETERS/PARAMETER')}['PROFILE_VISIBILITY_PROVEN']==visibility
bits=[x for x in z['implemented_xsa'] if x.endswith('.bit')];assert len(bits)==1 and sha(z['implemented_xsa'][bits[0]])==art['bit']['sha256']
profile=json.loads((root/'board/s2b_inference_platform.json').read_text(encoding='utf-8')); assert len(profile['rtl_sources'])==18
oldmanifest=json.loads((v0/'delivery_manifest.json').read_text(encoding='utf-8')); pinned={x['path']:x['sha256'] for x in oldmanifest['files']}
for rel in profile['rtl_sources']:
 assert sha((root/rel).read_bytes())==pinned[rel]==sha((v1/'sources'/Path(rel).name).read_bytes())
checker=runpy.run_path(str(root/'verification/check_s2b_inference_platform.py'));closure=checker['check_static'](root)
assert closure==a['facts']['full_model_core_present']['source_sha256_for_entry']
for kind,heading in [('setup_max','WNS'),('hold_min','WHS')]:
 text=(v0/('postroute_'+kind+'_r02.rpt')).read_text(encoding='utf-8'); assert 'Design State : Routed' in text and 'Speed File   : -2' in text and 'All user specified timing constraints are met.' in text
 lines=text.splitlines(); i=next(n for n,x in enumerate(lines) if x.strip().startswith(heading+'(ns)')); values=lines[i+2].split()
 assert len(values)==8 and float(values[0])>=0 and float(values[1])==0 and int(values[2])==0 and float(values[4])>=0 and float(values[5])==0 and int(values[6])==0
cov=(v0/'postroute_check_timing_r02.rpt').read_text(encoding='utf-8')
for x in ['no_clock','unconstrained_internal_endpoints','no_input_delay','no_output_delay']:assert re.search(r'checking '+x+r' \(0\)',cov)
assert re.search(r'clk_fpga_0\s+20\.000',(v0/'postroute_clocks_r02.rpt').read_text(encoding='utf-8'))
route=(v0/'postroute_route_status_r02.rpt').read_text(encoding='utf-8');assert re.search(r'nets with routing errors.*:\s*0',route) and re.search(r'fully routed nets.*:\s*28621',route)
gp=root/'report/evidence/S2B-T01/gp0_software_contract_20261014_r03/audit_gp0_software_contract.py'
tree=ast.parse(gp.read_text(encoding='utf-8')); samples=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='SAMPLES' for x in n.targets))
assert len(samples)==31
new=(bsp/'infer.elf').read_bytes(); e=parsed['infer.elf']; text=next(s for s in e['sections'] if s['name']=='.text'); asm=(bsp/'app_disassembly.log').read_text(encoding='utf-8')
for addr,word,fragment,purpose in samples:
 offset=text['offset']+addr-text['address']; assert text['address']<=addr<text['address']+text['size']
 assert struct.unpack_from('<I',new,offset)[0]==word
 line=next(x.strip() for x in asm.splitlines() if x.strip().startswith(f'{addr:06x}:'))
 assert int(line.split()[1],16)==word and fragment in ' '.join(line.lower().split()), (hex(addr),fragment,line)
for addr,load in [(0x10bc28,1),(0x10bf70,0)]:
 w=struct.unpack_from('<I',new,text['offset']+addr-text['address'])[0]
 assert (w>>26)&3==1 and (w>>22)&1==0 and (w>>20)&1==load
assert all((0x1005>>bit)&1 for bit in [0,2,12])
old=root/'report/evidence/S2B-T15/visibility1_xsa_20261014_r01'
for name,expected in [('infer.elf',{'.text','.rodata'}),('init.elf',{'.note.gnu.build-id'})]:
 left=(old/name).read_bytes(); le=parser['parse_elf'](left); right=(bsp/name).read_bytes(); re_=parsed[name]
 ls={s['name']:s for s in le['sections'] if s['flags']&2}; rs={s['name']:s for s in re_['sections'] if s['flags']&2}; assert ls.keys()==rs.keys()
 different=set()
 for k,l in ls.items():
  r=rs[k]; assert all(l[x]==r[x] for x in ['type','flags','address','size','align'])
  if l['type']!=8:
   lb=left[l['offset']:l['offset']+l['size']];rb=right[r['offset']:r['offset']+r['size']]
   if lb!=rb:
    different.add(k)
    if k=='.rodata':assert lb.count(b't19_visibility1_20261014_r01')==3 and lb.replace(b't19_visibility1_20261014_r01',b't19_visibility1_20261014_r02')==rb
    else:
     header=bytes.fromhex('040000001400000003000000474e5500');o=lb.find(header);assert o>=0 and rb.find(header)==o
     assert [i for i,(x,y) in enumerate(zip(lb,rb)) if x!=y]==list(range(o+16,o+36))
 assert different==expected
print(json.dumps({'status':'INDEPENDENT_RAW_FACTS_PASS','input_count':len(a['input_sha256']),'closure_count':len(closure),'ps_parameters':937,'init_members':6,'gp0_words':31,'checks':a['checks'],'dynamic_hardware':'NOT_RUN'},ensure_ascii=False))
