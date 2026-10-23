import hashlib, importlib.util, json, os, sys
from pathlib import Path
root=Path(r'D:\codex-worktrees\w4')
run=Path(os.environ['REVIEW_RUN'])
tmp=Path(os.environ['TEMP'])
paths={
 'manifest': root/'report/evidence/S4-B/s4b_pl_geometry_g2_20261023_r01/frozen_sources.json',
 'generator': root/'scripts/stage4_s4b/build_s4b_preproc_geometry.py',
 'tests': root/'verification/test_s4b_preproc_geometry.py',
 'd2': root/'verification/s1_t02_d2_numeric_reference.py',
}
expected={
 'manifest':'544cd0ab3044661113116fc492edc8fab82aebdfa0afcd73521d9231dc757a76',
 'generator':'c3d8029c3c4bbbdac3a299166c3324a48e595076673a1013d34cfeb881ec0140',
 'tests':'d2bb38a7e9ad048e05a3a3d058360af84cd3b342b680589041dc0acb1a21c8f2',
 'd2':'6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f',
}
actual={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in paths.items()}
assert actual==expected,(actual,expected)
assert tmp.is_absolute() and tmp.is_dir() and run in tmp.parents
spec=importlib.util.spec_from_file_location('geometry_path_probe',paths['generator'])
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
base=run/'trailing_alias.json'
alias=str(base)+'.'
assert not os.path.lexists(str(base)) and not os.path.lexists(alias)
validated=mod._validate_absolute_output_path(alias)
meta=mod.build_s4b_preproc_geometry(3,3,5,5)
written=mod.write_s4b_preproc_geometry(meta,validated)
result={'run_id':run.name,'TEMP':str(tmp),'TMP':str(tmp),'hashes_before_import':actual,'requested_path':alias,'writer_returned':written,'normal_name_exists':os.path.lexists(str(base)),'trailing_dot_name_exists':os.path.lexists(alias),'samefile':os.path.samefile(str(base),alias) if os.path.lexists(str(base)) and os.path.lexists(alias) else None,'directory_names':sorted(p.name for p in run.iterdir() if p.is_file())}
(run/'path_probe.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))