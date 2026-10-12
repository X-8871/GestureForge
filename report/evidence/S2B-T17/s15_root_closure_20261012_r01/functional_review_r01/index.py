"""冻结真原件索引；保留编译缓存，声明可恢复性与未采集项。"""
from pathlib import Path
import sys, json, hashlib, shutil
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_tile_origin_rtl as previous
def sha(path):
    """真实原字节SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    """严格UTF8读取。"""
    return json.loads(path.read_text(encoding='utf-8'))
stop=read(HERE/'final_stop_receipt.json');assert stop['stop'] and stop['status']=='PASS_G2_FUNCTIONAL_ONLY'
for row in stop['reviewed5source']:assert sha(ROOT/row['path'])==row['sha256']
assert read(HERE/'post_audit.native.json')['native_exit_code']==0
assert read(HERE/'review_driver_r02.native.json')['native_exit_code']==0
assert read(HERE/'review_driver.native.json')['native_exit_code']==1
assert previous.git('rev-parse','HEAD').decode().strip()==stop['source_commit']
files=[];cache=[]
for path in sorted(HERE.rglob('*')):
    if not path.is_file():continue
    if 'obj_dir' in path.parts or '__pycache__' in path.parts:
        cache.append(dict(path=path.relative_to(ROOT).as_posix(),size_bytes=path.stat().st_size,kind='GCH' if path.suffix=='.gch' else 'REBUILDABLE_COMPILE_CACHE'))
    else:files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),size_bytes=path.stat().st_size))
index=dict(schema_version=1,status=stop['status'],stop=True,source_commit=stop['source_commit'],reviewed5source=stop['reviewed5source'],
 final_stop_receipt=dict(path=(HERE/'final_stop_receipt.json').relative_to(ROOT).as_posix(),sha256=sha(HERE/'final_stop_receipt.json')),files=files,
 preserved_unindexed_cache=cache,cache_reason='obj_dir为可重建编译缓存；索引真实源副本、bench、向量、工具版本和compile/simulation/native两流及直接wait记录即可恢复。GCH仍保留，等待ROOT核验终态与恢复依赖后按授权清理；本审查不删除。',
 manifest_cache_dependency='本次真原件索引与G1 delivery_manifest_r02均不依赖该独立obj_dir/GCH。',
 failure_history='r01 Git LF与冻结RAW CRLF直接比较导致假漂移；原始driver复制保存，native1/两流/失败receipt全保留；r02成功独立目录，补充explicit RAW_IDENTICAL/EXACT_LF_TO_CRLF关系关闭。',
 unknown=['首轮launcher修改一个日志name前未留其独立源码快照；原真实driver命令与native记录完整、实际reviewer_r01源码已保存，不把launcher重建称原件。','100ms采样无法获得瞬时内存峰；工具调用总量未测。','最初沙箱拒绝执行的宿主错误在工具结果中；未启动native子进程，不混作native1。'],
 limits=stop['limitations'],disk_free_bytes=shutil.disk_usage(HERE).free,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat())
with (HERE/'artifact_hash_index.json').open('x',encoding='utf-8',newline='\n') as stream:
    json.dump(index,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(status=index['status'],stop=True,files=len(files),bytes=sum(row['size_bytes'] for row in files),cache_files=len(cache),cache_bytes=sum(row['size_bytes'] for row in cache),index_sha256=sha(HERE/'artifact_hash_index.json'),receipt_sha256=sha(HERE/'final_stop_receipt.json')),ensure_ascii=True),flush=True)
