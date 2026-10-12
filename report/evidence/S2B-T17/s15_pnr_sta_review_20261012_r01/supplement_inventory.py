import json
from pathlib import Path
P=Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\s15_postroute_20261012_r01')
for r in [1,2]:
    for path in [P/'raw_root'/('supervision_r%02d'%r)/'supervisor_receipt.json',P/'raw_root'/('supervision_r%02d'%r)/'guard/guard_receipt.json',P/'raw_root'/('native_consumer_r%02d'%r)/'consumer_receipt.json']:
        d=json.loads(path.read_text(encoding='utf-8'))
        print(str(path.relative_to(P)),list(d))
        print({k:v for k,v in d.items() if isinstance(v,(int,str,float,bool)) or v is None})
    row=json.loads((P/'raw_root'/('supervision_r%02d'%r)/'guard/samples.jsonl').read_text(encoding='utf-8').splitlines()[0])
    print('SAMPLE KEYS',list(row))
print('TCL checkpoints:')
for l in (P/'native_jobs/s2b_inference_wrapper.tcl').read_text(encoding='utf-8').splitlines():
    if any(x in l for x in ['read_checkpoint','link_design','set_param','phys_opt_design','write_checkpoint']): print(l)
print('originalmapkeys',list(json.loads((P/'pnr_original_file_map.json').read_text(encoding='utf-8'))))
