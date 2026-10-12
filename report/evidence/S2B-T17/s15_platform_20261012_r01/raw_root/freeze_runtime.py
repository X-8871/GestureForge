"""ROOT在G2通过并提交后绑定本轮实际源码及唯一路径；不启动Vivado。"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
EXPECTED = {
    "src/s2b_conv_tile_engine.sv": "dee1d5e925d7c4fdd29bb9115103d34603ce050b5d43fa00d6147eacd6256aaf",
    "board/s2b_inference_platform.json": "c0b46d89b0ce063bd033586e1ba044bee4088c1bb91a2ea7b33bd285e24bc863",
    "verification/check_s2b_inference_platform.py": "5483bf21ab2510fdce4313b73b1753b52e76de0564cdeb5c7509ad9fd1dfff2a",
    "verification/test_s2b_conv_feature_address_rtl.py": "08daad9a6888963b1d0791d790c5e8fea7222607a4ee2e0724015acadf0cd5e6",
    "verification/test_s2b_s15_arithmetic_rtl.py": "71c81e1aee2cb7b05f9ac10d9a413aa59f452432132adb14fa7f8089de93e03b",
}


def exact(path, directory=False):
    """只接受完整精确名称及目标类型，拒绝链接。"""
    path = Path(path)
    assert path.is_absolute()
    cur = Path(path.anchor)
    for component in path.parts[1:]:
        assert component in {item.name for item in cur.iterdir()}, str(path)
        cur = cur / component
        assert not cur.is_symlink() and not cur.is_junction(), str(cur)
    assert cur.is_dir() if directory else cur.is_file(), str(cur)
    return cur


def bound(path):
    """原字节哈希、长度与仓库落点一并返回。"""
    path = exact(path)
    raw = path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),
                sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def git(*arguments):
    """仅读取明确Git对象；保留真正原生退出码。"""
    result = subprocess.run(["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", *arguments],
                            cwd=ROOT, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    return result.stdout


def save(path, value):
    """只创建新文件，禁止覆盖已经冻结的运行。"""
    exact(path.parent, True)
    assert not path.exists(), str(path)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--functional-review", required=True)
    parser.add_argument("--tools-review", required=True)
    parser.add_argument("--work", required=True)
    args = parser.parse_args()
    assert re.fullmatch("[0-9a-f]{40}", args.commit)
    assert git("rev-parse", "HEAD").decode("ascii").strip() == args.commit
    assert not git("diff", "--cached", "--name-only").strip()
    work = exact(args.work, True)
    assert work.parent == HERE.parent and work.name == "s15_launch_prepare_20261012_r02"
    f2 = exact(args.functional_review)
    t2 = exact(args.tools_review)
    reviews = [json.loads(p.read_text(encoding="utf-8")) for p in (f2, t2)]
    assert all(r.get("status", "").startswith("PASS") and r.get("stop") is True for r in reviews)
    # 监督器实际启动旧目录中的同字节守卫，明确保存该额外恢复依赖。
    guard_old = exact(ROOT / "tmp/2B/S2B-T17/s15_launch_prepare_20261012_r01/guard.py")
    guard_copy = exact(ROOT / "report/evidence/S2B-T17/s15_launch_tools_20261012_r01/tools/guard.py")
    guard_new = exact(work / "guard.py")
    expected_guard = "e055276318f6e215981bdceadb437ebe2bf50ec160b8d93c2d11c33bc89f886f"
    assert guard_old.read_bytes() == guard_new.read_bytes() == guard_copy.read_bytes()
    assert bound(guard_old)["sha256"] == expected_guard
    sup_spec = importlib.util.spec_from_file_location("s15_actual_supervisor", exact(work / "supervisor.py"))
    sup = importlib.util.module_from_spec(sup_spec)
    sup_spec.loader.exec_module(sup)
    assert sup.GUARD == guard_old and sup.GUARD_SHA == expected_guard
    for name, digest in EXPECTED.items():
        assert bound(ROOT / name)["sha256"] == digest, name
    g1 = exact(ROOT / "report/evidence/S2B-T17/s15_arithmetic_fix_20261012_r01/delivery_manifest_r02.json")
    assert bound(g1)["sha256"] == "d6f678d5d95869228fbc75348f4b56942ba15efaa3785b25511257bc5a4b5cc9"
    old = json.loads(exact(ROOT / "tmp/2B/S2B-T17/s14_launch_prepare_20261012_r01/source_freeze_r01.json").read_text(encoding="utf-8"))
    names = [r["path"] for r in old["source_files"]]
    names.append("verification/test_s2b_s15_arithmetic_rtl.py")
    assert len(names) == 46 and len(set(names)) == 46
    rows = []
    for name in names:
        row = bound(ROOT / name)
        raw = exact(ROOT / name).read_bytes()
        blob = git("show", args.commit + ":" + name)
        assert blob == raw or (b"\r\n" not in blob and blob.replace(b"\n", b"\r\n") == raw), name
        rows.append(row)
    hashes = {r["path"]: r["sha256"] for r in rows}
    assert all(hashes[k] == v for k, v in old["frozen14"].items())
    spec = importlib.util.spec_from_file_location("s15_actual_checker", exact(ROOT / "verification/check_s2b_inference_platform.py"))
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    static = checker.check_static(ROOT)
    profile = json.loads(exact(ROOT / "board/s2b_inference_platform.json").read_text(encoding="utf-8"))
    assert profile["version"] == "s2b-inference-platform/0.1.15"
    assert profile["clock_hz"] == 50000000 and profile["visibility_default"] == 0
    assert profile["rtl_sources"] == old["active_rtl_sources"] and len(profile["rtl_sources"]) == 18
    assert len(static) == 33 and all(hashes[k] == v for k, v in static.items())
    assert checker.FROZEN_CORE_SHA256 == old["frozen14"]
    freeze = dict(schema_version=1, source_commit=args.commit, profile=profile["version"],
                  tcl_builder_namespace_version="0.1.12", source_files=rows,
                  active_rtl_sources=profile["rtl_sources"], frozen14=old["frozen14"],
                  platform_static_source_count=len(static), static_source_sha256=static,
                  created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                  functional_g1=bound(g1), functional_g2=dict(bound(f2), status=reviews[0]["status"]),
                  tool_g2=dict(bound(t2), status=reviews[1]["status"]),
                  tool_runtime_dependencies=[dict(actual=bound(guard_old), recovery=bound(guard_copy),
                    reviewed_same_bytes=bound(guard_new), reason="监督器与消费器实际argv固定使用r01守卫；须恢复到原精确路径，13个r02对象不能单独恢复。")],
                  limitations=["只冻结实际已审源码；STA、postroute、实板及阶段验收仍未通过。"])
    freeze_path = work / "source_freeze_r01.json"
    save(freeze_path, freeze)
    pre = ROOT / "report/evidence/S2B-T17/s15_source_preflight_20261012_r01"
    report = ROOT / "report/evidence/S2B-T17/s15_platform_20261012_r01"
    project = work / "project_s15_r01"
    pnr_cache = work / "pnr_s15_r01"
    pnr_report = ROOT / "report/evidence/S2B-T17/s15_postroute_20261012_r01"
    for target in (pre, report, project, pnr_cache, pnr_report):
        exact(target.parent, True)
        assert not target.exists(), str(target)
    config = dict(SOURCE_COMMIT=args.commit, SOURCE_FREEZE=str(freeze_path), SOURCE_FREEZE_SHA=bound(freeze_path)["sha256"],
                  FUNCTIONAL_G1=str(g1), FUNCTIONAL_G1_SHA=bound(g1)["sha256"],
                  FUNCTIONAL_G2=str(f2), FUNCTIONAL_G2_SHA=bound(f2)["sha256"], FUNCTIONAL_G2_EXPECTED_STATUS=reviews[0]["status"],
                  SYNTH_MANIFEST=None, SYNTH_MANIFEST_SHA=None, SYNTH_G2=None, SYNTH_G2_SHA=None, SYNTH_G2_EXPECTED_STATUS=None,
                  SYNTH_CACHE=str(work), PNR_CACHE=str(pnr_cache), PROJECT=str(project), SYNTH_REPORT=str(report), PNR_REPORT=str(pnr_report),
                  SOURCE_PRE=str(pre), TOOLS_G2=str(t2), TOOLS_G2_SHA=bound(t2)["sha256"], TOOLS_G2_EXPECTED_STATUS=reviews[1]["status"])
    assert len(config) == 22
    save(work / "runtime_pins_synth_r1.json", config)
    save(HERE / "runtime_pins_input.json", config)
    print(json.dumps(dict(status="ACTUAL_POST_COMMIT_FREEZE_CREATED", source_commit=args.commit,
                          source_count=len(rows), static_count=len(static), freeze=bound(freeze_path),
                          runtime_config=bound(work / "runtime_pins_synth_r1.json")), ensure_ascii=False))


if __name__ == "__main__":
    main()
