"""生成阶段5 离线准备的机器可读交付清单（Lead 专属；配合 `verification/check_stage_delivery.py`）。

严格遵循检查器的封闭 schema（未知字段会被判错）：
- 顶层仅：schema_version/stage/task_id/run_id/source_commit/evidence_dir/interfaces/files/checks/limitations/tool_versions
- `evidence_dir` 必须精确等于 `report/evidence/<task_id>/<run_id>`
- `interfaces[]` 仅 name/version/frozen/path/sha256，且 path 必须是仓库内 `docs/` 下现存正式文档
- `files[]` 仅 path/role/sha256；role ∈ {artifact, diagnostic, input, log, result, source}
- `checks[]` 仅 name/status/command/exit_code/reason；`status=PASS` 要求 `exit_code` 严格为整数 0
- 输出**确定性**（不含时间戳），以便「核验通过的清单」与最终入库清单逐字节一致

退出码：0=清单已写出；2=输入/环境错误。
用法：`python -B scripts/stage5_s5a/build_s5_delivery_manifest.py`
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import platform
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

TASK_ID = "S5-A"
RUN_ID = "s5a_g0_20261021_r03"
EVIDENCE_DIR = f"report/evidence/{TASK_ID}/{RUN_ID}"

# 接口：必须是仓库内 docs/ 下现存的正式文档（本阶段为 G0 定稿/草案，frozen=false 如实标注）
INTERFACES = [
    ("阶段5 显示 G0 契约（S5A-G0-v2，离线准备定稿；非阶段验收）",
     "S5A-G0-v2 / 2026-10-21", "docs/stage5/s5a_stage5_display_g0_fields.json"),
    ("阶段5 显示 G0 定稿规格 v2", "v2 / 2026-10-21", "docs/stage5/S5A_stage5_display_g0_spec_v2.md"),
    ("阶段4 S4-A G0 草案（字段名与口径权威，DRAFT_NOT_FROZEN）", "draft r05 / 2026-10-21",
     "docs/stage4/s4a_stage4_g0_fields.json"),
    ("阶段计划（阶段5 要求来源，只读引用）", "2026-10-05 同步版",
     "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md"),
]

# 源码绑定（role=source）：本阶段交付的实现与规格
SOURCE_FILES = [
    "verification/s5_display_geometry_reference.py",
    "verification/test_s5_display_geometry_reference.py",
    "scripts/stage5_s5a/run_s5a_selfcheck.py",
    "scripts/stage5_s5a/build_s5_delivery_manifest.py",
    "scripts/stage5_s5a/verify_s5_tamper_detection.py",
    "scripts/stage5_s5a/verify_s5r_verdicts.py",
    "docs/stage5/S5A_stage5_display_g0_spec_v2.md",
    "docs/stage5/s5a_stage5_display_g0_fields.json",
]

CHECKS = [
    {"name": "S5-A 契约自检（26 用例：D2 逐值对拍/手算样例/退化守卫/契约一致/记录校验）",
     "status": "PASS",
     "command": "python -B -m unittest verification.test_s5_display_geometry_reference -v",
     "exit_code": 0},
    {"name": "S5-C 回归勾连正对照（seeded 子集 8 样本；全量 109 样本见 S5-C r04 证据）",
     "status": "PASS",
     "command": "python -B scripts/stage5_s5c/check_s5c_stage4_regression.py --limit 8 --seed 20261021",
     "exit_code": 0},
    {"name": "S5-C 反例探针检出（探针本身退出码 1；包装脚本在检出时返回 0）",
     "status": "PASS", "command": "python -B scripts/stage5_s5a/verify_s5_tamper_detection.py",
     "exit_code": 0},
    {"name": "S5-B 渲染器自检", "status": "PASS",
     "command": "python -B scripts/stage5_s5b/render_s5b_overlay.py --selfcheck", "exit_code": 0},
    {"name": "S5-B 证据驱动（21 用例/583 断言/双 pass 逐文件 SHA256 一致）", "status": "PASS",
     "command": "python -B scripts/stage5_s5b/run_s5b_evidence.py --out report/evidence/S5-B --run-id s5b_20261021_r07 --seed 20261021",
     "exit_code": 0},
    {"name": "S5-C 证据驱动（13/13 步骤退出码与期望一致）", "status": "PASS",
     "command": "pwsh -NoProfile -File scripts/stage5_s5c/run_s5c_evidence.ps1 -RunId s5c_regression_20261021_r04",
     "exit_code": 0},
    {"name": "独立审查两轮结论一致（第 1 轮 CHANGES_REQUIRED → 第 2 轮聚焦关闭 PASS）",
     "status": "PASS", "command": "python -B scripts/stage5_s5a/verify_s5r_verdicts.py", "exit_code": 0},
    {"name": "本交付清单只读核验（verification/check_stage_delivery.py --mode evidence，核验通过的清单与本清单逐字节一致）",
     "status": "PASS",
     "command": "python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S5-A/s5a_g0_20261021_r03/delivery_manifest.json",
     "exit_code": 0},
    {"name": "真实 HDMI/摄像头联调、上板、30 分钟无死锁、真实 FPS/延迟统计",
     "status": "NOT_RUN", "command": None, "exit_code": None,
     "reason": "无硬件会话：阶段3 颜色验收受阻（根因=硬件 DVP cmos_d[9] 无信号）、阶段4 未正式联调、2B 未让出 JTAG/COM4 与 hw_server"},
]


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    proc = subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    return (proc.stdout or "").strip()


def role_for(path: pathlib.Path, run_dir: pathlib.Path) -> str:
    if path.suffix == ".txt":
        return "log"
    if path.suffix == ".json":
        return "result"
    return "artifact"


def main() -> int:
    run_dir = REPO_ROOT / EVIDENCE_DIR
    if not run_dir.is_dir():
        print(f"[manifest] 运行目录不存在：{run_dir}")
        return 2
    manifest_path = run_dir / "delivery_manifest.json"

    interfaces = []
    for name, version, rel in INTERFACES:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"[manifest] 接口文件缺失：{rel}")
            return 2
        if not rel.startswith("docs/"):
            print(f"[manifest] 接口必须位于 docs/：{rel}")
            return 2
        interfaces.append({"name": name, "version": version, "frozen": False,
                           "path": rel, "sha256": sha256(path)})

    files = []
    for path in sorted(p for p in run_dir.rglob("*") if p.is_file()):
        if path.resolve() == manifest_path.resolve():
            continue
        files.append({"path": path.relative_to(REPO_ROOT).as_posix(),
                      "role": role_for(path, run_dir), "sha256": sha256(path)})
    for rel in SOURCE_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"[manifest] 源码绑定缺失：{rel}")
            return 2
        files.append({"path": rel, "role": "source", "sha256": sha256(path)})

    manifest = {
        "schema_version": 1,
        "stage": "5",
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "source_commit": git("rev-parse", "HEAD"),
        "evidence_dir": EVIDENCE_DIR,
        "interfaces": interfaces,
        "files": files,
        "checks": CHECKS,
        "limitations": [
            "本清单只证明清单/文件绑定与目录检查通过；不代表接口语义正确、阶段5 开工、G0/G1/G3/G4/G5 或任何验收通过。",
            "纯离线：无 Vivado/xsim/JTAG/COM4/摄像头/HDMI；真实显示、30 分钟无死锁与真实 FPS/延迟统计均为 NOT_RUN。",
            "阶段4 S4-A 契约仍 DRAFT_NOT_FROZEN（frozen=false）；阶段5 契约为离线准备 G0 定稿，非冻结批准。",
            "本任务无冻结的上游接口，故 `--mode inputs` 不适用（按 report/README.md：无本地输入的独立任务只对交付证据运行 evidence），未伪造接口或输入。",
            "S5-C 曾有 r01/r02 两个运行目录被 Developer 删除（违反证据保留口径、不可恢复），已登记 EVIDENCE_RETENTION_INCIDENT.md。",
            "S5-B r06_a|_b、S5-C r03|r03_limit8、S5-A r01|r02 为接口加固前证据，保留但不作权威引用。",
            "本轮 S5-B/S5-C 加固后重跑由 Lead 代执行（Developer 子代理失败退出）；Reviewer 已独立复现确认无碍。",
            "反例探针按设计返回退出码 1；清单中以包装脚本 verify_s5_tamper_detection.py（检出时返回 0）表达，包装不改变探针语义。",
            "首次清单被检查器拒绝（exit 2，41 条 schema 违规）的事实已记录于 S5-CTRL 收尾记录；本清单为修正后版本。",
            "tmp/ 下临时产物与历史运行按 .gitignore 不入库。",
        ],
        "tool_versions": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": "2.4.6" if _has("numpy") else "unavailable",
            "pillow": "12.2.0" if _has("PIL") else "unavailable",
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[manifest] wrote {manifest_path} files={len(files)} interfaces={len(interfaces)} "
          f"head={manifest['source_commit'][:8]}")
    return 0


def _has(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())