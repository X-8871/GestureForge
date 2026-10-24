#!/usr/bin/env python3
"""离线证据修复的定向验证；夹具只写操作系统临时目录，不改原证据。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[3]
BASE = "2487eb8f65ba7f9a8e8e11e90ab14a8afb2344d6"
SCRIPT = REPO / "scripts/stage3_t17/verify_t17_blob_identity.py"
TEST = SCRIPT.with_name("test_verify_t17_blob_identity.py")
SCOPE = "report/evidence/S3-T05/t05_stage3_window_20261024_r01"


def main():
    """每个输出仅允许首次创建，避免覆盖失败或既有运行证据。"""
    records = []

    def write(name, data):
        (OUT / name).open("xb").write(data)

    def run(name, argv, expected=0):
        cp = subprocess.run(argv, cwd=REPO, capture_output=True)
        write(name + ".stdout.txt", cp.stdout)
        write(name + ".stderr.txt", cp.stderr)
        records.append({"name": name, "command": argv, "cwd": str(REPO),
                        "exit_code": cp.returncode, "expected_exit_code": expected,
                        "matched": cp.returncode == expected})
        return cp

    with tempfile.TemporaryDirectory(prefix="t17_fix_validation_") as tmp:
        run("targeted_regression", [sys.executable, "-B", str(TEST)])
        selftest_json = Path(tmp) / "selftest.json"
        run("legacy_selftest", [sys.executable, "-B", str(SCRIPT), "--selftest",
             "--fixture-dir", str(Path(tmp) / "fixtures"), "--json-out", str(selftest_json)])
        write("legacy_selftest.json", selftest_json.read_bytes())
        historical_json = Path(tmp) / "historical.json"
        run("historical_fixed_scope", [sys.executable, "-B", str(SCRIPT),
            "--repo-root", str(REPO), "--commit", BASE, "--scope", SCOPE,
            "--certify", SCOPE, "--json-out", str(historical_json)])
        write("historical_fixed_scope.json", historical_json.read_bytes())

        spec = importlib.util.spec_from_file_location("directed_tests", TEST)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        case = module.BlobIdentityTests()
        case.setUp()
        try:
            old = subprocess.run(["git", "-C", str(REPO), "show",
                BASE + ":scripts/stage3_t17/verify_t17_blob_identity.py"],
                capture_output=True, check=True).stdout
            old_script = Path(tmp) / "old_verifier.py"
            old_script.write_bytes(old)
            # 复现评审中的只读 Gitdir 视图，仅留下 README；期望旧版假通过、新版拒绝。
            view = Path(tmp) / "view"
            (view / module.SCOPE).mkdir(parents=True)
            (view / ".git").write_text("gitdir: " + str(case.repo / ".git") + "\n", encoding="utf-8")
            (view / module.SCOPE / "README.md").write_bytes((case.run_dir / "README.md").read_bytes())
            for name, script, expected in (("original_bug_readme_view", old_script, 0),
                                            ("fixed_readme_view", SCRIPT, 1)):
                run(name, [sys.executable, "-B", str(script), "--repo-root", str(view),
                    "--commit", case.commit, "--scope", module.SCOPE,
                    "--certify", module.SCOPE], expected)
            for name, script, expected in (("original_bug_absent_scope", old_script, 0),
                                            ("fixed_absent_scope", SCRIPT, 1)):
                run(name, [sys.executable, "-B", str(script), "--repo-root", str(view),
                    "--commit", case.commit, "--scope", "absent/run",
                    "--certify", "absent/run"], expected)
        finally:
            case.doCleanups()

    # 参考帧以独立哈希绑定，不扩大文本认证范围。
    replay = json.loads((OUT / "replay_input.json").read_text(encoding="utf-8"))
    frame = (REPO / replay["path"]).read_bytes()
    fixed_frame = subprocess.run(["git", "-C", str(REPO), "show",
        replay["source_fixed_commit"] + ":" + replay["path"]], check=True, capture_output=True).stdout
    frame_check = {"worktree_sha256": hashlib.sha256(frame).hexdigest(),
                   "fixed_blob_sha256": hashlib.sha256(fixed_frame).hexdigest(),
                   "size_bytes": len(frame), "copied_or_modified": False,
                   "matched": frame == fixed_frame and len(frame) == replay["size_bytes"]
                   and hashlib.sha256(frame).hexdigest() == replay["sha256"]}
    write("frame_binding_check.json", json.dumps(frame_check, ensure_ascii=False, indent=2).encode("utf-8"))
    outputs = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            body = path.read_bytes()
            outputs.append({"path": path.name, "size_bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
    sources = [{"path": str(path.relative_to(REPO)).replace("\\", "/"),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in (SCRIPT, TEST)]
    git_version = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    passed = all(item["matched"] for item in records) and frame_check["matched"]
    manifest = {"schema_version": 1, "task_id": "S3-T05", "run_id": OUT.name,
        "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "source_baseline": BASE, "source_files": sources,
        "interface_version": "verify_t17_blob_identity CLI，固定树文本集合双向比较；无总线或硬件接口变更",
        "tools": {"python": sys.version, "git": git_version}, "commands": records,
        "outputs": outputs, "result": "PASS" if passed else "FAIL",
        "environment_failures": [{"command": "首次沙箱内 python -B test_verify_t17_blob_identity.py",
            "exit_code": 1, "reason": "ResourceUnavailable：python.exe 启动拒绝访问；随后经 require_escalated 执行。"}],
        "limitations": ["不递归绑定本清单自身", "源码修改未包含在 source_baseline，以实际文件哈希绑定",
            "仅离线回归，无硬件操作；不是 G2/G3/G4/G5", "二进制不由文本验证器认证；参考帧另以哈希绑定",
            "原始漏洞命令退出0是预期失败对照，原输出保留", "进程身份 CIM 查询拒绝访问；仅 Get-Process 可读核验，未结束任何进程",
            "耗时以测试输出为准；峰值内存及工具调用总量未测"]}
    write("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
    print(json.dumps({"result": manifest["result"], "commands": len(records),
                      "frame_match": frame_check["matched"]}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
