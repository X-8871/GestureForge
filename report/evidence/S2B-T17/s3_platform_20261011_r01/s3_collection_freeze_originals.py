"""先固定 S3 既有原件，再即刻封存已关闭的根会话日志截止字节。"""
from collection_common import *
from datetime import datetime,timezone,timedelta
import re
started=time.monotonic()
for p in (ROOT,CACHE,REPORT,PRE,PROJECT):exact(p,"directory")
original=[binding(p) for directory in (REPORT,PRE) for p in sorted(directory.rglob("*")) if p.is_file()]
save(REPORT/"s3_collection_original_inventory.json",{"status":"ORIGINAL_RAW_BYTES_FIXED_BEFORE_COLLECTION","source_commit":BASELINE,"files":original,"source_current_s4_consumed":False})
text=(REPORT/"products.tcldict").read_text(encoding="utf-8")
matches=re.findall(r"native_log_source ([^\s{}]+)",text);require(len(matches)==1,"原根日志来源不唯一")
source=exact(Path(matches[0]));mapping=rawcopy(source,REPORT/"s3_collection_root_session_snapshot.log")
raw=(REPORT/"s3_collection_root_session_snapshot.log").read_bytes()
peaks=list(map(float,re.findall(rb"peak = ([0-9.]+)",raw)))
require(peaks and max(peaks)==2677.445,"累计根会话峰值不符")
save(REPORT/"s3_collection_root_session_snapshot.json",{"mapping":mapping,"closed_cutoff_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"source_same_before_after_copy":True,"root_reported_cumulative_peak_mb":max(peaks),"process_tree_peak_memory":"NOT_MEASURED","source_immutable_binding":False,"scope":"源路径仅为来源元数据，不作为未来不变依赖。副本绑定收集截止字节；包含旧S1/S2/S3会话，不将累计峰称为S3整体进程树峰。"})
original_check()
print(json.dumps({"status":"ORIGINALS_FIXED_ROOT_LOG_RAW_COPIED","original_files":len(original),"root_log":mapping,"elapsed_seconds":time.monotonic()-started},ensure_ascii=False))
