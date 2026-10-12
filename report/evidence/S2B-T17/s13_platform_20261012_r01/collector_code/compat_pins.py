"""S12隔离草稿的固定待冻结项；缺少真实冻结时阻断所有收集写入。"""
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).parents[4]
WORK = Path(__file__).parent
SOURCE_COMMIT = None
SOURCE_FREEZE = WORK / "__PENDING_S13_SOURCE_FREEZE__"
SOURCE_FREEZE_SHA = None
FUNCTIONAL_G1 = ROOT / "__PENDING_S13_FUNCTIONAL_G1__"
FUNCTIONAL_G1_SHA = None
FUNCTIONAL_G2 = ROOT / "__PENDING_S13_FUNCTIONAL_G2__"
FUNCTIONAL_G2_SHA = None
FUNCTIONAL_G2_EXPECTED_STATUS = None
SYNTH_MANIFEST = ROOT / "__PENDING_S13_SYNTH_MANIFEST__"
SYNTH_MANIFEST_SHA = None
SYNTH_G2 = ROOT / "__PENDING_S13_SYNTH_G2__"
SYNTH_G2_SHA = None
SYNTH_G2_EXPECTED_STATUS = None
SYNTH_CACHE = WORK / "__PENDING_S13_SYNTH_CACHE__"
PNR_CACHE = WORK / "__PENDING_S13_PNR_CACHE__"
PROJECT = WORK / "__PENDING_S13_PROJECT__"
SYNTH_REPORT = ROOT / "__PENDING_S13_SYNTH_REPORT__"
PNR_REPORT = ROOT / "__PENDING_S13_PNR_REPORT__"
SOURCE_PRE = ROOT / "__PENDING_S13_SOURCE_PRE__"
GUARD = WORK / "guard.py"
GUARD_SHA = "056cbd06289490589f17f70076046eb2811a4a256edb0ccd8d2b19b2537bff07"
SUP = WORK / "supervisor.py"
SUP_SHA = "7438201f3fa38fe84daaa3203634ec532f3f4069f6a13bfb155db9d055fe6325"
ARCHIVE = ROOT / "report/evidence/S2B-T17/s13_launch_tools_20261012_r01"
MAPPING_SHA = "8145418aee1328176f7d488320a9605ce07deaab101fe4119437bf1d9ff535a7"
RECOVERY_SHA = "dac56d7e6f67fccf5f0dea27c470e89e6b66b47a0444e7d17b6ae5c859ec34f6"
TOOLS_G2 = ROOT / "__PENDING_S13_TOOLS_G2__"
TOOLS_G2_SHA = None
TOOLS_G2_EXPECTED_STATUS = None
RUNTIME_CONFIG = WORK / "runtime_pins.json"
_CONFIG_SELECTOR = os.environ.get("S13_RUNTIME_CONFIG")
if _CONFIG_SELECTOR is not None:
    RUNTIME_CONFIG = Path(_CONFIG_SELECTOR)
_LOADED_CONFIG_SHA = None
_CONFIG_FIELDS = ("SOURCE_COMMIT", "SOURCE_FREEZE", "SOURCE_FREEZE_SHA", "FUNCTIONAL_G1", "FUNCTIONAL_G1_SHA", "FUNCTIONAL_G2", "FUNCTIONAL_G2_SHA", "FUNCTIONAL_G2_EXPECTED_STATUS", "SYNTH_MANIFEST", "SYNTH_MANIFEST_SHA", "SYNTH_G2", "SYNTH_G2_SHA", "SYNTH_G2_EXPECTED_STATUS", "SYNTH_CACHE", "PNR_CACHE", "PROJECT", "SYNTH_REPORT", "PNR_REPORT", "SOURCE_PRE", "TOOLS_G2", "TOOLS_G2_SHA", "TOOLS_G2_EXPECTED_STATUS")
_CONFIG_PATHS = {"SOURCE_FREEZE", "FUNCTIONAL_G1", "FUNCTIONAL_G2", "SYNTH_MANIFEST", "SYNTH_G2", "SYNTH_CACHE", "PNR_CACHE", "PROJECT", "SYNTH_REPORT", "PNR_REPORT", "SOURCE_PRE", "TOOLS_G2"}
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


def load_runtime_config():
    """只读严格JSON数据；缺文件继续待冻结，禁止借配置改guard/SUP或资源门槛。"""
    global _LOADED_CONFIG_SHA
    if _CONFIG_SELECTOR is not None:
        require(str(RUNTIME_CONFIG)==_CONFIG_SELECTOR and RUNTIME_CONFIG.parent==WORK and re.fullmatch(r"runtime_pins_(?:synth|pnr)_r[0-9]+\.json", RUNTIME_CONFIG.name), "配置选择器不是本目录精确新版本文件")
        exact(RUNTIME_CONFIG)
    if not RUNTIME_CONFIG.exists():
        return
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "配置重复键")
            result[key] = value
        return result
    raw = exact(RUNTIME_CONFIG).read_bytes()
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    require(type(data) is dict and set(data)==set(_CONFIG_FIELDS), "配置字段缺失或超出白名单")
    for key, value in data.items():
        if key in _CONFIG_PATHS:
            if value is None and key in {"SYNTH_MANIFEST", "SYNTH_G2"}:
                continue
            require(type(value) is str and str(Path(value))==value and Path(value).is_absolute() and Path(value).is_relative_to(ROOT), "配置路径不能规范化、越界或非绝对："+key)
            globals()[key] = Path(value)
        else:
            require(value is None or type(value) is str, "配置标量类型错误："+key)
            globals()[key] = value
    _LOADED_CONFIG_SHA = hashlib.sha256(raw).hexdigest()


def runtime_config_binding():
    """实际配置原字节与本进程导入时必须一致，另由ROOT/清单绑定该SHA。"""
    require(_LOADED_CONFIG_SHA is not None and hashlib.sha256(exact(RUNTIME_CONFIG).read_bytes()).hexdigest()==_LOADED_CONFIG_SHA, "运行配置未冻结或导入后漂移")
    return dict(path=RUNTIME_CONFIG.relative_to(ROOT).as_posix(), sha256=_LOADED_CONFIG_SHA, bytes=RUNTIME_CONFIG.stat().st_size)

def require_ready(pnr=False):
    """先阻断缺失commit，再核真实G1/G2与唯一路径；不创建目录。"""
    require(hashlib.sha256(exact(Path(__file__)).read_bytes()).hexdigest()==_LOADED_HELPER_SHA, "冻结门禁代码在导入后漂移")
    require(isinstance(SOURCE_COMMIT, str) and re.fullmatch("[0-9a-f]{40}", SOURCE_COMMIT), "BLOCKED_PENDING_S12_PINS：缺ROOT最终commit/43源冻结/RunIds/功能G2")
    runtime_config_binding()
    for path in (SYNTH_CACHE, PNR_CACHE, PROJECT, SYNTH_REPORT, PNR_REPORT, SOURCE_PRE):
        require("__PENDING_" not in str(path) and path.is_absolute() and path.is_relative_to(ROOT), "BLOCKED_PENDING_S12_PINS：缺实际唯一RunId")
    require(len({str(path) for path in (SYNTH_CACHE, PNR_CACHE, PROJECT, SYNTH_REPORT, PNR_REPORT, SOURCE_PRE)})==6, "RunId落点重复")
    pinned(SOURCE_FREEZE, SOURCE_FREEZE_SHA)
    pinned(FUNCTIONAL_G1, FUNCTIONAL_G1_SHA)
    review=json.loads(pinned(FUNCTIONAL_G2, FUNCTIONAL_G2_SHA).read_text(encoding="utf-8"))
    require(isinstance(FUNCTIONAL_G2_EXPECTED_STATUS, str) and FUNCTIONAL_G2_EXPECTED_STATUS.startswith("PASS") and review.get("status")==FUNCTIONAL_G2_EXPECTED_STATUS, "功能G2未绑定实际PASS原件")
    review=json.loads(pinned(TOOLS_G2, TOOLS_G2_SHA).read_text(encoding="utf-8"))
    require(isinstance(TOOLS_G2_EXPECTED_STATUS, str) and TOOLS_G2_EXPECTED_STATUS.startswith("PASS") and review.get("status")==TOOLS_G2_EXPECTED_STATUS, "S13新guard/SUP/consumer工具G2未冻结")
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


load_runtime_config()
