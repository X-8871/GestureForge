"""S12隔离草稿的固定待冻结项；缺少真实冻结时阻断所有收集写入。"""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).parents[4]
WORK = Path(__file__).parent
SOURCE_COMMIT = '09e0135234ed257d1f878b80bf63eeefcdc6143f'
SOURCE_FREEZE = WORK / "source_freeze.json"
SOURCE_FREEZE_SHA = 'f8cbae8ce77e6caa7945d2e6485c28bc93a12ef0226d59c2abd8f42e38b01b77'
FUNCTIONAL_G1 = ROOT / "report/evidence/S2B-T17/s12_timing_cones_20261012_r01/delivery_manifest_r02.json"
FUNCTIONAL_G1_SHA = '2c8e3bd56c1c288333f168a767aadf8b7067f2450e97c25709f271553772ed54'
FUNCTIONAL_G2 = ROOT / "report/evidence/S2B-T17/independent_s12_functional_review_20261012_r01/raw/final_review_receipt.json"
FUNCTIONAL_G2_SHA = 'e6e4dd2b77a31b55d12b4fe4c1cc1ab1d4905fd3fbf9b4e045dffb38dbf79129'
FUNCTIONAL_G2_EXPECTED_STATUS = "PASS"
SYNTH_MANIFEST = ROOT / "__PENDING_S12_SYNTH_MANIFEST__"
SYNTH_MANIFEST_SHA = None
SYNTH_G2 = ROOT / "__PENDING_S12_SYNTH_G2__"
SYNTH_G2_SHA = None
SYNTH_G2_EXPECTED_STATUS = None
SYNTH_CACHE = WORK / "synth_cache"
PNR_CACHE = WORK / "pnr_cache"
PROJECT = WORK / "project"
SYNTH_REPORT = ROOT / "report/evidence/S2B-T17/s12_platform_20261012_r02"
PNR_REPORT = ROOT / "report/evidence/S2B-T17/s12_implementation_20261012_r02"
SOURCE_PRE = ROOT / "report/evidence/S2B-T17/s12_resume_source_preflight_20261012_r01"
GUARD = ROOT / "tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/guard.py"
GUARD_SHA = "a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac"
SUP = ROOT / "tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/supervisor.py"
SUP_SHA = "193416f869463c38065e257545720032438ab12c7bbe30beec6bc8c53d8f9ca0"
ARCHIVE = ROOT / "report/evidence/S2B-T17/s12_resource_guard_delivery_20261012_r01"
MAPPING_SHA = "52c8fcb9e6a829eafb3e6de2394b543d01feaa055eb34a2d507cf1ab2ba71103"
RECOVERY_SHA = "28bff3069ccecb4a8d801f3e6e8feddd1473119f542dabf50152493b2cc82568"
_LOADED_HELPER_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def require(condition, message):
    """未知项一律拒绝，不填充历史批准。"""
    if not condition:
        raise ValueError(message)

def exact(path, directory=False):
    """逐组件核验精确路径及类型，拒绝链接。"""
    path = Path(path)
    require(path.is_absolute(), "不是完整绝对路径")
    current = Path(path.anchor)
    for name in path.parts[1:]:
        require(name in {p.name for p in current.iterdir()}, "精确路径不存在："+str(path))
        current = current/name
        require(not current.is_symlink() and not current.is_junction(), "拒绝链接路径")
    require(current.is_dir() if directory else current.is_file(), "路径类型不同")
    return current

def pinned(path, digest):
    """哈希必须由最终冻结提供且与实际原字节相同。"""
    require(isinstance(digest, str) and re.fullmatch("[0-9a-f]{64}", digest), "BLOCKED_PENDING_S12_PINS：缺实际输入SHA")
    path = exact(path)
    require(hashlib.sha256(path.read_bytes()).hexdigest()==digest, "冻结输入漂移")
    return path

def require_ready(pnr=False):
    """先阻断缺失commit，再核真实G1/G2与唯一路径；不创建目录。"""
    require(hashlib.sha256(exact(Path(__file__)).read_bytes()).hexdigest()==_LOADED_HELPER_SHA, "冻结门禁代码在导入后漂移")
    require(isinstance(SOURCE_COMMIT, str) and re.fullmatch("[0-9a-f]{40}", SOURCE_COMMIT), "BLOCKED_PENDING_S12_PINS：缺ROOT最终commit/43源冻结/RunIds/功能G2")
    for path in (SYNTH_CACHE, PNR_CACHE, PROJECT, SYNTH_REPORT, PNR_REPORT, SOURCE_PRE):
        require("__PENDING_" not in str(path) and path.is_absolute() and path.is_relative_to(ROOT), "BLOCKED_PENDING_S12_PINS：缺实际唯一RunId")
    require(len({str(path) for path in (SYNTH_CACHE, PNR_CACHE, PROJECT, SYNTH_REPORT, PNR_REPORT, SOURCE_PRE)})==6, "RunId落点重复")
    pinned(SOURCE_FREEZE, SOURCE_FREEZE_SHA)
    pinned(FUNCTIONAL_G1, FUNCTIONAL_G1_SHA)
    review=json.loads(pinned(FUNCTIONAL_G2, FUNCTIONAL_G2_SHA).read_text(encoding="utf-8"))
    require(isinstance(FUNCTIONAL_G2_EXPECTED_STATUS, str) and FUNCTIONAL_G2_EXPECTED_STATUS.startswith("PASS") and review.get("status")==FUNCTIONAL_G2_EXPECTED_STATUS, "功能G2未绑定实际PASS原件")
    if pnr:
        pinned(SYNTH_MANIFEST, SYNTH_MANIFEST_SHA)
        review=json.loads(pinned(SYNTH_G2, SYNTH_G2_SHA).read_text(encoding="utf-8"))
        require(isinstance(SYNTH_G2_EXPECTED_STATUS, str) and SYNTH_G2_EXPECTED_STATUS.startswith("PASS") and review.get("status")==SYNTH_G2_EXPECTED_STATUS, "综合G2未绑定实际PASS原件")
    resolve_permanent(GUARD, GUARD_SHA)
    resolve_permanent(SUP, SUP_SHA)

def resolve_permanent(original, expected=None):
    """只读取正式去重映射，核对固定原恢复路径、对象SHA；绝不恢复或覆盖。"""
    original=exact(original)
    digest=hashlib.sha256(original.read_bytes()).hexdigest()
    if expected is not None:
        require(digest==expected, "固定工具输入漂移")
    mapping=json.loads(pinned(ARCHIVE/"archive_mapping.json", MAPPING_SHA).read_text(encoding="utf-8"))
    recovery=json.loads(pinned(ARCHIVE/"recovery_entry.json", RECOVERY_SHA).read_text(encoding="utf-8"))
    require(recovery["fixed_project_root"]==str(ROOT), "恢复根目录不同")
    require(recovery["fixed_guard_sha256"]==GUARD_SHA and recovery["fixed_supervisor_sha256"]==SUP_SHA, "恢复固定工具SHA不同")
    if original in (GUARD, SUP):
        required=GUARD_SHA if original==GUARD else SUP_SHA
        require(digest==required, "固定guard/sup不可重pin")
        tools=[row for row in recovery["tool_files"] if row["destination_absolute_path"]==str(original) and row["sha256"]==required]
        require(len(tools)==1, "原绝对恢复目标不唯一或漂移")
    rows=[row for row in mapping["binding_rows"] if row["original_absolute_path"]==str(original) and row["sha256"]==digest]
    require(bool(rows), "正式映射缺少原路径与原SHA")
    saved={row["archived_repo_path"] for row in rows}
    require(len(saved)==1, "归档映射对象不唯一")
    artifact=pinned(ROOT/next(iter(saved)), digest)
    require(artifact.is_relative_to(ARCHIVE), "永久对象不在工具正式包")
    if original in (GUARD, SUP):
        require(tools[0]["artifact_repo_path"]==artifact.relative_to(ROOT).as_posix(), "恢复入口与映射对象不同")
    return dict(path=artifact.relative_to(ROOT).as_posix(), sha256=digest, bytes=artifact.stat().st_size)
