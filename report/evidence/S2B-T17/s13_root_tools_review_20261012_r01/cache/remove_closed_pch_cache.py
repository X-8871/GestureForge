"""仅清理已结束 S13 编译的精确18份可重建预编译头，保留真实证据。"""
import hashlib
import json
from pathlib import Path
import stat
import time
import psutil

ROOT = Path(__file__).parents[4]
HERE = Path(__file__).parent
BASE = ROOT / "tmp/2B/S2B-T17/s13_tile_origin_20261012_r01"
GROUPS = [
    ("all_r01/feature", "Vtb_s2b_conv_feature_address", 145112000, 145111864, (17912,1791769515.5618167), (5724,1791769548.6821597)),
    ("all_r01/boundary", "Vtb_s2b_conv_validation", 145273818, 145274087, (35980,1791769552.777768), (37616,1791769583.9331288)),
    ("all_r02/feature", "Vtb_s2b_conv_feature_address", 145111953, 145111871, (8056,1791769623.8396304), (11036,1791769656.864038)),
    ("all_r02/boundary", "Vtb_s2b_conv_validation", 145274474, 145274039, (7808,1791769660.9621065), (18160,1791769692.07967)),
    ("all_r03/feature", "Vtb_s2b_conv_feature_address", 145111730, 145111783, (26240,1791769778.573146), (5964,1791769810.2919877)),
    ("all_r03/boundary", "Vtb_s2b_conv_validation", 145274248, 145274462, (31824,1791769814.607865), (32796,1791769845.6855254)),
    ("all_r03/geometry", "Vtb_s2b_geometry_specialization", 143459945, 143459740, (19540,1791769848.1104531), (37584,1791769880.9067883)),
    ("all_r03/route", "Vtb_s2b_route_specialization", 142770761, 142770684, (34288,1791769884.059796), (6452,1791769916.737169)),
    ("layer0_r01/layer0", "Vtb_s2b_conv_layer0", 146044313, 146044443, (31224,1791769993.753751), (27148,1791770023.732453)),
]

def exact(path, directory=False):
    """逐组件核验原拼写和类型，拒绝链接或重解析点。"""
    current = Path(path.anchor)
    for name in path.parts[1:]:
        assert name in {p.name for p in current.iterdir()}, str(path)
        current = current / name
        info = current.lstat()
        assert not stat.S_ISLNK(info.st_mode)
        assert not getattr(info, "st_file_attributes", 0) & 1024
    assert current.is_dir() if directory else current.is_file()
    return current

def digest(path):
    """流式核验实际文件原字节。"""
    value = hashlib.sha256()
    with exact(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            value.update(block)
    return value.hexdigest()

def main():
    """预检全部目标与保全材料后，逐份立即复核再删除。"""
    exact(ROOT, True); exact(BASE, True); exact(HERE, True)
    receipt = HERE / "closed_pch_cleanup_receipt.json"
    assert not receipt.exists()
    manifest_path = ROOT / "report/evidence/S2B-T17/s13_tile_origin_20261012_r01/delivery_manifest.json"
    assert digest(manifest_path) == "726df3cb0045f8b2fe4f6911f6f87e0515b1a1d29a4296937b0736614fa59d42"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bound = {row["path"]: row["sha256"] for row in manifest["files"]}
    for name, expected in bound.items():
        assert digest(ROOT / name) == expected, name
    identities = []
    targets = []
    for group, prefix, fast, slow, compile_identity, sim_identity in GROUPS:
        directory = exact(BASE / group / "obj_dir", True)
        assert directory.is_relative_to(BASE)
        for pid, birth in (compile_identity, sim_identity):
            try:
                observed = psutil.Process(pid).create_time()
                assert observed != birth, (pid, birth, "原进程仍运行")
                identities.append(dict(pid=pid, birth=birth, status="PID_REUSED", observed_birth=observed))
            except psutil.NoSuchProcess:
                identities.append(dict(pid=pid, birth=birth, status="ABSENT"))
        for suffix, size in (("__pch.h.fast.gch", fast), ("__pch.h.slow.gch", slow)):
            path = exact(directory / (prefix + suffix))
            assert path.stat().st_size == size
            assert path.relative_to(ROOT).as_posix() not in bound
            targets.append(dict(path=str(path), sha256=digest(path), bytes=size))
    assert len(targets) == 18 and sum(x["bytes"] for x in targets) == 2606866215
    before = psutil.disk_usage("C:/").free
    deleted = []
    for row in targets:
        path = exact(Path(row["path"]))
        assert path.is_relative_to(BASE) and path.stat().st_size == row["bytes"]
        assert digest(path) == row["sha256"]
        path.unlink()
        assert not path.exists()
        deleted.append(row)
    for name, expected in bound.items():
        assert digest(ROOT / name) == expected, "证据保全失败：" + name
    result = dict(status="REMOVED_EXACT_CLOSED_REBUILDABLE_PCH_ONLY", deleted=deleted,
                  completed_identities=identities, evidence_files_preserved=len(bound),
                  c_disk_free_before=before, c_disk_free_after=psutil.disk_usage("C:/").free,
                  available_ram_bytes=psutil.virtual_memory().available, observed_unix=time.time(),
                  limitations=["仅删除精确18份非冻结缓存；源、黄金、失败日志和引用exe全部保留。"])
    with receipt.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2); stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("deleted", "completed_identities")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
