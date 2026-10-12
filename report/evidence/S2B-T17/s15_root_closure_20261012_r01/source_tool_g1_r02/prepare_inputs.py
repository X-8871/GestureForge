"""R2原件复制与真实前后request；仅新TMP创建，不覆写已有目录。"""
from pathlib import Path
import json
import source_closure as c
HERE=Path(__file__).parent;ROOT=c.ROOT
OLD=HERE.parent/'s15_source_closure_fallback_20261012_r01'
REVIEW=HERE.parent/'independent_s15_source_closure_review_20261012_r01'
def copy(source,target):
    assert source.is_file() and not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:stream.write(source.read_bytes())
    assert c.binding(source)['sha256']==c.binding(target)['sha256']
    return dict(original=c.binding(source),saved=c.binding(target))
baseline=[copy(p,HERE/'baseline_r01'/p.relative_to(OLD)) for p in sorted(OLD.rglob('*')) if p.is_file()]
for name,expected in [('final_review_receipt.json','080fb2d5c1c17d80f559776ecdd118d3b603438d9b3e6ccabb059c3099be99fe'),('original_file_index.json','b4414ddc30989d3dc4cad8394e249836f285d4eae959d493518d87a5646f9eea')]:assert c.binding(REVIEW/name)['sha256']==expected
review=[copy(p,HERE/'review_r01'/p.name) for p in sorted(REVIEW.iterdir()) if p.is_file()]
config=c.read(c.CONFIG);pre=Path(config['SOURCE_PRE'])
request=dict(source_commit=c.SOURCE,config=c.binding(c.CONFIG),source_before=c.binding(pre/'source_before.json'),source_after=c.binding(pre/'source_after.json'),source_admission=c.binding(c.ROOTRUN/'source_admission_r01.json'),
 capture_before=c.binding(c.WORK/'s15_runtime_source_before_r1.native.json'),capture_after=c.binding(c.WORK/'s15_runtime_source_after_r1.native.json'),
 budget_records=[c.binding(c.ROOTRUN/'supervision_r01/guard/guard_receipt.json'),c.binding(c.ROOTRUN/'native_consumer_r01/consumer_receipt.json')],budget_status='BLOCKED',additional_evidence=[])
assert request['source_after']['sha256']=='21d14d510273ae5ab0bd0b8d7fcc991d3e2935a19505c45b5c7503c89c045959'
c.save(HERE/'actual_request_r01.json',request)
c.save(HERE/'copied_original_index.json',dict(baseline_r01=baseline,review_r01=review,baseline_originals_unchanged=True))
print(json.dumps(dict(status='PREPARED_REAL_BEFORE_AFTER',baseline_files=len(baseline),review_files=len(review)),ensure_ascii=False))
