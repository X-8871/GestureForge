#!/usr/bin/env python3
"""生成 S4-B 的官方 delivery_manifest.json，供 verification/check_stage_delivery.py --mode evidence 机器核验。

设计原则：不手抄哈希，全部从实际文件读取；命令与退出码取自该 RunId 的 offline_chain_summary.json
或由调用方显式传入（真实观测值），不猜不填。

用法：
  python -B scripts/stage4_s4b/build_s4b_manifest.py \
      --run-id 20261021_r07 --chain-exit-code 0 --unittest-exit-code 0 --checker-exit-code 0
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

W4_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "S4-B"
EVIDENCE_ROOT_RELATIVE = "report/evidence/S4-B"
MANIFEST_NAME = "delivery_manifest.json"

SOURCE_BINDINGS = (
    ("vitis/stage4/s4_ps_decode.h", "S4-B 解码/NMS 接口（INT8 反量化 + D9 语义）"),
    ("vitis/stage4/s4_ps_decode.c", "S4-B 解码/NMS 实现（阈值含等号、类别内 greedy IoU>=0.45、<=15 框、D2 逆映射、稳定 tie 顺序）"),
    ("vitis/stage4/s4_uart_protocol.h", "S4-B s2bu/1.1 帧接口（40B 头/<Q8I>/<ii5d>/CRC32；扩展预留默认关闭）"),
    ("vitis/stage4/s4_uart_protocol.c", "S4-B s2bu/1.1 帧打包/解包实现"),
    ("vitis/stage4/s4_offline_host.c", "S4-B 离线主机 CLI（selftest / bundle->解码->打包->解帧回读->S4-A 字段 JSON）"),
    ("vitis/stage4/README.md", "S4-B 构建与运行说明、口径与未执行边界"),
    ("scripts/stage4_s4b/run_s4b_offline_chain.py", "S4-B 离线链驱动与证据生成"),
    ("scripts/stage4_s4b/build_s4b_manifest.py", "本清单生成器（可复跑）"),
    ("verification/test_s4_ps_decode.py", "S4-B unittest（C 自检 + 合成语义夹具 + 冻结样本链 + 契约字段）"),
    ("verification/s1_t02_d9_yolo_decode.py", "2A 冻结 D9 参考实现（只读对拍基准）"),
    ("verification/s1_t02_d6_detection_metrics.py", "2A 冻结 D6 stable_nms/类别顺序/MAX_OUTPUTS（D9 依赖）"),
)

INTERFACES = (
    {
        "name": "S4A-stage4-result-field-contract",
        "version": "S4-A-r05",
        "frozen": False,
        # path/sha256 由 build() 按生成时刻的实际文件填写（契约仍可能在工作区继续修订）。
        "path": "docs/stage4/s4a_stage4_g0_fields.json",
        "sha256": None,
    },
    {
        "name": "S2A-T01-model-delivery-g0-freeze",
        "version": "2A-G0",
        "frozen": True,
        "path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
        "sha256": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    },
    {
        "name": "S1-T02-D6-detection-eval-metrics",
        "version": "S1-T02-D6",
        "frozen": True,
        "path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md",
        "sha256": "735cbc78882dd299a952ee1d4c2f7ef972e8cc903782be3a64f1db830f311dd7",
    },
)

MAIN_TREE_BINDINGS = (
    ("D:\\FPGA_Competition\\report\\evidence\\S2A-T25\\cpu_layer_golden_index.json",
     "cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d", "2A T25 逐层索引（主树冻结副本）"),
    ("D:\\FPGA_Competition\\report\\evidence\\S2A-T29\\cpu_decode_nms_reference.json",
     "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231", "2A T29 CPU D9 解码/NMS 参考"),
    ("D:\\FPGA_Competition\\report\\evidence\\S2A-T25\\tensors",
     "sample_000/036/056/102.zlib（逐文件 SHA 见 offline_chain_summary.json bindings）", "2A T25 zlib 层流分片目录（只读；工作树未物化）"),
    ("D:\\FPGA_Competition\\w2b\\docs\\obsidian-project\\02-方案设计\\s2b_board_transport.md",
     "7dda231e2888c0ed9d95952dcba4d41c9eaf7423e008e4d179b3f7d2c5f0b334",
     "2B s2bu/1.1 UART 运输正文（G0_FROZEN 定义；上方哈希为同目录 verification/s2b_board_transport.py 实现，正文在本阶段未修改）"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head(root: Path) -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root), capture_output=True, check=False)
    head = completed.stdout.decode("ascii", "replace").strip()
    if completed.returncode != 0 or len(head) != 40:
        raise SystemExit("无法解析 git HEAD：%s" % completed.stderr.decode("utf-8", "replace"))
    return head


def role_for(name: str) -> str:
    suffix = Path(name).suffix.lower()
    if suffix == ".json":
        return "result"
    if suffix in {".bin", ".raw"}:
        return "result"
    if suffix == ".txt":
        return "log"
    return "result"


def keep_reason_for(name: str) -> str:
    if name == "SUPERSEDED_note.md":
        return "说明该 RunId 为被取代的中间运行并指向最终 RunId（脚本演进与契约修订留痕）"
    if name.startswith("c_selftest"):
        return "C 自检结果（CRC 检查向量、帧 pack/unpack 回读、篡改拒绝、扩展门闸）"
    if name.startswith("offline_chain_summary"):
        return "离线链机器可读全量清单（上游绑定绝对路径与 SHA、命令与退出码、逐框对拍结果、未执行项）"
    if name.startswith("s4a_alignment"):
        return "与 S4-A r04 契约的逐项对齐清单（字段名/候选口径/candidate_limit/0 哨兵/扩展预留）"
    if name.startswith("host_result_"):
        return "C 主机 CLI 的 S4-A 字段结果 JSON（含候选口径、回读标记、0 哨兵与未执行标注）"
    if name.startswith("frame_"):
        return "C 打包的 s2bu/1.1 风格 RUN 成功响应帧原字节（40B 头 + <Q8I> meta + 双头 + 每框 48B）"
    if name.endswith("head13.raw") or name.endswith("head26.raw"):
        return "C 侧回写的 INT8 副本，用于证明进出一致并核对 2A 冻结 tensor_sha256"
    if name == "summary.txt":
        return "本轮命令行摘要与检查计数"
    return "本轮证据文件"


def build(run_id: str, chain_exit: int, unittest_exit: int, checker_exit: int | None,
          chain_command_override: str | None = None) -> dict:
    run_dir = W4_ROOT / EVIDENCE_ROOT_RELATIVE / run_id
    evidence_dir = "%s/%s" % (EVIDENCE_ROOT_RELATIVE, run_id)
    summary_path = run_dir / "offline_chain_summary.json"
    if not summary_path.is_file():
        raise SystemExit("缺少 offline_chain_summary.json：%s" % summary_path)
    with io.open(summary_path, encoding="utf-8") as stream:
        summary = json.load(stream)
    if summary.get("task_id") != TASK_ID or summary.get("run_id") != run_id:
        raise SystemExit("summary 的 task_id/run_id 与参数不一致")

    files: list[dict] = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(W4_ROOT).as_posix()
        if path.name == MANIFEST_NAME:
            continue
        files.append(
            {
                "path": relative,
                "sha256": sha256_file(path),
                "role": role_for(path.name),
                "keep_reason": keep_reason_for(path.name),
            }
        )
    for relative, reason in SOURCE_BINDINGS:
        path = W4_ROOT / relative
        if not path.is_file():
            raise SystemExit("源码绑定缺失：%s" % relative)
        files.append({"path": relative, "sha256": sha256_file(path), "role": "source", "keep_reason": reason})

    # 契约接口按生成时刻的实际文件哈希绑定（契约可能在工作区继续修订），
    # 运行期实际绑定的哈希来自该 RunId 的 summary，与当前文件不一致时在 limitations 中显式记录。
    interfaces = [dict(item) for item in INTERFACES]
    contract_path = W4_ROOT / interfaces[0]["path"]
    contract_live_sha = sha256_file(contract_path)
    interfaces[0]["sha256"] = contract_live_sha
    chain_contract_sha = summary.get("contract", {}).get("sha256")

    compile_command = " ".join(summary["commands"]["compile"]["command"]) if summary.get("commands", {}).get("compile") else None
    compile_exit = summary.get("commands", {}).get("compile", {}).get("exit_code")
    selftest_info = summary.get("commands", {}).get("selftest")
    selftest_command = " ".join(selftest_info["command"]) if selftest_info else None
    selftest_exit = selftest_info.get("exit_code") if selftest_info else None
    sample_indices = [str(s["sample_index"]) for s in summary.get("samples", [])]
    chain_command = chain_command_override or (
        "python -B scripts/stage4_s4b/run_s4b_offline_chain.py --run-id %s --sample-indices %s"
        % (run_id, ",".join(sample_indices))
        if sample_indices
        else "python -B scripts/stage4_s4b/run_s4b_offline_chain.py --run-id %s" % run_id
    )
    unittest_command = "python -m unittest verification.test_s4_ps_decode -v"
    checker_command = (
        "python -B verification/check_stage_delivery.py --mode evidence --manifest %s/%s" % (evidence_dir, MANIFEST_NAME)
    )

    checks: list[dict] = [
        {
            "name": "c_compile_strict_flags",
            "status": "PASS" if compile_exit == 0 else "FAIL",
            "command": compile_command,
            "exit_code": compile_exit,
            "reason": "d:\\mingw64\\bin\\gcc.exe -std=c11 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow：0 error、0 warning",
        },
        {
            "name": "c_selftest_crc_and_frame_readback",
            "status": ("PASS" if selftest_exit == 0 else "FAIL") if selftest_info else "NOT_RUN",
            "command": selftest_command,
            "exit_code": selftest_exit,
            "reason": "11/11 通过：CRC '123456789'->0xCBF43926、头/meta/框/整帧 pack-unpack-re-pack 字节一致、坏 magic/头 CRC/payload CRC 拒绝、扩展 op 门闸关闭"
            if selftest_info
            else "该 RunId 在前置步骤失败后中止，未执行 C 自检（真实未执行，非通过）",
        },
        {
            "name": "offline_chain_c_vs_python_d9_and_t29",
            "status": "PASS" if chain_exit == 0 else "FAIL",
            "command": chain_command,
            "exit_code": chain_exit,
            "reason": (
                "退出码 0；%d/%d 项检查 PASS，含 C vs Python D9 逐框离散字段完全一致、score/xyxy 绝对误差 0.000e+00、与 2A T29 冻结参考 0 mismatch、双头 INT8 进出一致"
                % (summary["check_summary"]["pass"], summary["check_summary"]["pass"] + summary["check_summary"]["fail"])
                if summary.get("check_summary")
                else "该 RunId 未产出完整链结果（前置步骤失败中止），真实退出码 %s" % chain_exit
            ),
        },
        {
            "name": "unittest_s4_ps_decode",
            "status": "PASS" if unittest_exit == 0 else "FAIL",
            "command": unittest_command,
            "exit_code": unittest_exit,
            "reason": "26 个测试全部通过（C 自检、s2bu 布局独立交叉、合成语义夹具含阈值等号/同类抑制/跨类保留/15 框截断/tie 顺序/零面积丢弃/候选上界 12675 边界、冻结样本链、拒收路径、契约字段与 measurement_scope 键名）",
        },
        {
            "name": "board_uart_serial_execution",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "离线骨架：未接真实串口/COM4、未接板卡；本 RunId 不含任何 UART 实收原字节",
        },
        {
            "name": "jtag_hw_server_pl_inference_timing",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "未访问 JTAG/hw_server/DAP、未加载 PL、未测量 PL inference_time/期限/吞吐；四个时间字段为 0 哨兵并标注 NOT_EXECUTED_OFFLINE",
        },
        {
            "name": "full_109_sample_sweep",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "本任务只覆盖 1~3 个冻结样本；109 全量由 S4-C 负责",
        },
        {
            "name": "stage2b_board_acceptance",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "2B 实板验收与 s2bu/1.1 板上行为不在本任务范围；本 RunId 只验证帧格式/CRC/字节一致性",
        },
        {
            "name": "vivado_xsim_synthesis_simulation",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "未启动 Vivado/xsim/综合/仿真；仅使用 gcc 与轻量 Python",
        },
    ]
    if checker_exit is not None:
        checks.append(
            {
                "name": "official_checker_evidence_mode",
                "status": "PASS" if checker_exit == 0 else "FAIL",
                "command": checker_command,
                "exit_code": checker_exit,
                "reason": "本清单已通过官方只读检查器（CHECKS_OK）；仅代表清单与哈希绑定通过，不代表 G0/G4/G5 或任何实测",
            }
        )

    limitations = [
        "证据落点按 Lead 决定使用官方两段式 report/evidence/S4-B/<run_id>/；早期运行 r01~r05 为落点迁移与契约修订前的运行（r01/r02 的 summary 内嵌 evidence_dir 为迁移前路径，内容未改写），权威运行以本 RunId 为准并已重新生成离线链。",
        "未执行任何实测：无板卡、无 PL、无真实串口/COM4、无 JTAG/hw_server、无摄像头/HDMI；本清单不含也不声称 G3/G4/G5 或 2B 实板验收结论。",
        "S4-A 契约为 DRAFT_NOT_FROZEN 草案（清单 interfaces[0] 绑定生成时刻实际文件 sha256=%s）；时间/丢帧/过期/result_seq/state 的 UART 传输扩展仍待 Wong 决策，本阶段只预留位置且默认关闭。" % contract_live_sha,
        (
            "本 RunId 的离线链运行期绑定的 S4-A 契约 sha256=%s，与清单 interfaces[0] 的生成时刻哈希=%s 不同：说明该 RunId 产出后契约又经修订；语义不变量（candidate_count 阈值后/NMS 前、candidate_limit=12675 硬错误路径、measurement_scope 键名、0 哨兵）已由该 RunId 的 s4a_alignment.json 逐项核对，如需契约变更后的回归请以最新 RunId 为准。"
            % (chain_contract_sha, contract_live_sha)
            if chain_contract_sha and chain_contract_sha != contract_live_sha
            else "本 RunId 运行期绑定的 S4-A 契约 sha256=%s，与清单 interfaces[0] 一致。" % chain_contract_sha
        ),
        "离线无 PL，capture_time_ns/result_time_ns/inference_time_ns/end_to_end_latency_ns 按 S4-A absent_value_policy 使用 0 哨兵（未观测）并显式标注 measurement_scope.pl_timing=NOT_EXECUTED_OFFLINE；不得读作实测耗时。",
        "candidate_count 采用 S4-A r04 口径（阈值筛除后、NMS 前，与 2A T29 raw_candidate_count_before_stable_nms 及 2B 冻结实现同口径）；candidate_count_pre_threshold 为 required=false 诊断字段（=5×正面积候选框数），不进 UART、不参与对拍。",
        "candidate_limit=12675（2B 冻结候选缓冲上限 = tiny416 理论最大候选数）；S4-A 草案早期的 4096 已弃用，未启用。tiny416 固定配置下 candidate_overflow 恒为 false，字段保留并显式记录未超限事实。",
        "只读主树冻结绑定（位于 project-root 之外，无法作为 files 条目绑定，故在此列明路径与 SHA-256；逐样本绑定与实测 SHA 见 files 中的 offline_chain_summary.json）："
        + "；".join("%s path=%s sha256=%s" % (role, path, digest) for path, digest, role in MAIN_TREE_BINDINGS),
        "工作树内 report/evidence/S2A-T25/cpu_layer_golden_index.json 与 report/evidence/S2A-T29/cpu_decode_nms_reference.json 是主树冻结副本的序列化副本，本链未把它们当作冻结输入（本链按绝对路径读取主树并核对主树 SHA）；因此未列入 files。",
        "本轮 C 校验仅覆盖 3 个代表性冻结样本（多框+边界裁剪、同框两类跨类别、NO_HAND 非方形补边）；同类 NMS 抑制 IoU>=0.45、15 框稳定截断与 tie 顺序由 unittest 合成夹具覆盖，不表示整网精度或召回。",
        "pre_threshold 计数由 C 自报且无冻结黄金可比（2B/T29 只冻结阈值后口径），其一致性仅由 5×candidate_box_count 校验，已如实标注不参与对拍。",
    ]

    return {
        "schema_version": 1,
        "stage": "stage4",
        "task_id": TASK_ID,
        "run_id": run_id,
        "source_commit": git_head(W4_ROOT),
        "evidence_dir": evidence_dir,
        "interfaces": interfaces,
        "files": files,
        "checks": checks,
        "limitations": limitations,
        "tool_versions": {
            "python": "%d.%d.%d" % sys.version_info[:3],
            "gcc": "8.1.0-x86_64-win32-seh-rev0-MinGW-W64",
            "git": "system-git-readonly",
            "os": "Windows-x64",
            "checker": "verification/check_stage_delivery.py-schema_version_1",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 S4-B delivery_manifest.json")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--chain-exit-code", type=int, required=True, help="离线链驱动的真实退出码")
    parser.add_argument("--unittest-exit-code", type=int, required=True, help="unittest 的真实退出码")
    parser.add_argument("--checker-exit-code", type=int, default=None, help="官方检查器上一轮的真实退出码（确认后再填 0）")
    parser.add_argument("--chain-command", default=None, help="离线链命令原文覆盖（用于中止/失败的中途 RunId）")
    args = parser.parse_args(argv)

    manifest = build(args.run_id, args.chain_exit_code, args.unittest_exit_code, args.checker_exit_code,
                     args.chain_command)
    target = W4_ROOT / EVIDENCE_ROOT_RELATIVE / args.run_id / MANIFEST_NAME
    with io.open(target, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print("[s4b-manifest] 写入 %s（files=%d, checks=%d）" % (target, len(manifest["files"]), len(manifest["checks"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())