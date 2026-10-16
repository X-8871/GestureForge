#!/usr/bin/env python3
"""S2B-T18：借用总控已部署会话执行固定模型验收；导入与准备不访问硬件。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import json
import os
import struct
import subprocess
import sys
import time

try:
    from . import s2b_board_transport as transport
    from . import s2b_fixed_capture_check as checker
    from . import check_s2b_inference_platform as platform
    from . import check_stage_delivery as delivery
except ImportError:
    import s2b_board_transport as transport
    import s2b_fixed_capture_check as checker
    import check_s2b_inference_platform as platform
    import check_stage_delivery as delivery

ROOT = Path(__file__).absolute().parents[1]
TZ = timezone(timedelta(hours=8))
STRESS_COUNT = 1000


def require(condition, message):
    """失败立即锁存，由总控独立恢复硬件。"""
    transport.require(condition, message)


def binding(path):
    """绑定已有精确普通文件的原始字节。"""
    path = transport.exact_path(path)
    return {"path": str(path), "sha256": transport.digest(path.read_bytes())}


def save(path, value):
    """独占创建、UTF-8写入并强制持久化；不覆盖已存在证据。"""
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def append(stream, value):
    """每帧追加持久化检查点，崩溃前已完成的帧仍可恢复。"""
    stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
    stream.flush(); os.fsync(stream.fileno())


def prepare(asset_root, run_dir):
    """离线逐个核验输入，不复制输入/GF8或重算CPU；仅提取双头参考。"""
    run = transport.new_directory(run_dir)
    record = {"schema_version": 1, "status": "NOT_RUN", "hardware_execution": "NOT_RUN",
              "scope": "固定109样本及同一输入连续1000次；CSR负向/复位/恢复由T16验收。",
              "source_sha256": binding(Path(__file__)), "created_at_utc8": datetime.now(TZ).isoformat(),
              "estimate": {"uart_weights_seconds": 513, "uart_109_inputs_seconds": 4913,
                           "stress_compute_hours": [6, 24], "kind": "ESTIMATE_NOT_MEASURED"},
              "limitations": ["未连接串口、未调用SDK；准备成功不代表板上验收。", "峰值内存未测。"]}
    try:
        weight_path, weight, rows = transport.load_assets(asset_root, range(109))
        record["weights"] = {"path": str(weight_path), "sha256": transport.digest(weight), "bytes": len(weight)}
        tags = {tag for row in rows for tag in row["sample"]["coverage_tags"]}
        require({"class:" + name for name in transport.CLASS_NAMES} <= tags and
                {"empty_ground_truth", "multi_ground_truth_boxes", "boundary_ground_truth_box"} <= tags,
                "冻结109样本覆盖标签不完整")
        source = binding(ROOT / checker.CPU_D9_RECORD_PATH)
        references = []
        for row in rows:
            reference = transport.reference_row(run, row)
            path = run / f"reference_{row['sample_index']:03d}.json"
            save(path, {"schema_version": 1, "kind": "s2b_fixed_reference",
                        "model_manifest_sha256": transport.MODEL_SHA,
                        "golden_source": {"kind": "frozen_cpu_d9", **source}, "samples": [reference]})
            references.append({"index": row["sample_index"], "sample_id": row["sample"]["sample_id"],
                               "input": {"path": str(row["input_path"]), "sha256": row["input_sha256"], "bytes": transport.INPUT_BYTES},
                               "reference": binding(path), "coverage_tags": row["sample"]["coverage_tags"]})
        record.update(preparation="PASS_OFFLINE_ASSET_BINDINGS", model_manifest=binding(ROOT / checker.MODEL_PATH),
                      samples_manifest=binding(ROOT / "report/evidence/S2A-T01/fixed_test_samples.json"),
                      golden_source=source, rows=references, coverage_tags=sorted(tags))
    except BaseException as error:
        record.update(status="FAIL_PREPARATION", error=repr(error))
        raise
    finally:
        save(run / "preparation.json", record)
    return run / "preparation.json"


def read_bound(item):
    """消费前核验实际原字节，不能用上一轮PASS声明代替。"""
    require(type(item) is dict and {"path", "sha256"} <= set(item), "缺少文件绑定")
    path = transport.exact_path(item["path"])
    raw = path.read_bytes()
    require(transport.digest(raw) == item["sha256"], "绑定文件发生漂移：" + str(path))
    return path, raw


def evidence_manifest(run, status, reason):
    """包装当前独立Run所有实际产物；包装检查不代表实物G4/G5。"""
    relative = run.relative_to(ROOT).as_posix()
    require(relative == f"report/evidence/S2B-T18/{run.name}", "正式运行须位于S2B-T18独立Run目录")
    files = [{"path": path.relative_to(ROOT).as_posix(), "sha256": binding(path)["sha256"], "role": "result"}
             for path in sorted(run.rglob("*")) if path.is_file()]
    for path in (Path(__file__), Path(transport.__file__), Path(checker.__file__), Path(platform.__file__)):
        files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": binding(path)["sha256"], "role": "source"})
    interfaces = []
    for name, version, path in (("UART候选", "s2bu/1.1", "docs/obsidian-project/02-方案设计/s2b_board_transport.md"),
                                ("PS/PL物理候选", "s2b-physical/1.0.0", "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md")):
        interfaces.append({"name": name, "version": version, "path": path,
                           "sha256": binding(ROOT / path)["sha256"], "frozen": True})
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8", check=True).stdout.strip()
    save(run / "delivery_manifest.json", {"schema_version": 1, "stage": "2B", "task_id": "S2B-T18",
         "run_id": run.name, "source_commit": revision, "evidence_dir": relative, "interfaces": interfaces,
         "files": files, "checks": [{"name": "完整模型corpus与连续压力", "status": status,
         "command": "verification.s2b_board_acceptance.execute(borrowed_controller, borrowed_wire, bound_preparation, explicit_bindings)",
         "exit_code": 0 if status == "PASS" else None if status == "BLOCKED" else 1, "reason": reason}],
         "tool_versions": {"Python": sys.version.split()[0]},
         "limitations": ["接口候选尚未由本runner冻结；inputs核验可受阻。", "本任务不完成CSR负向/复位/恢复及阶段G5。"]})


def admit(controller, wire, build_details, visibility_proof, review, review_sha256,
          final_platform_manifest, final_review, final_review_sha256):
    """复用现有证明/机器清单；独立审查来源由总控固定真实原件哈希。"""
    try:
        from .s2b_board_jtag import JtagController, JtagWireSession
    except ImportError:
        from s2b_board_jtag import JtagController, JtagWireSession
    require(type(controller) is JtagController and type(wire) is JtagWireSession, "必须借用总控真实T16对象")
    require(controller.app_running and controller.configured and not controller.failed and not controller.log.closed,
            "控制器未部署/已失败/已关闭")
    require(not wire.failed and wire.abort_pending is None, "UART失败或仍有诊断pending")
    controller.verify_bindings()
    path, build = transport.verify_build(build_details)
    for key, expected in (("app_elf", build["elf"]), ("init_elf", build["initializer_elf"]),
                          ("xsa", {"path": build["config"]["xsa"], "sha256": build["xsa_sha256"]})):
        require(controller.bindings[key] == {field: expected[field] for field in ("path", "sha256")},
                "部署与同一实际ELF/BSP编译XSA0不符：" + key)
    require(all(value is not None for value in (visibility_proof, review, review_sha256,
            final_platform_manifest, final_review, final_review_sha256)), "BLOCKED：缺少真实visibility1及最终PL独审绑定")
    sources = platform.check_static(ROOT)
    platform.check_visibility(ROOT, Path(visibility_proof), Path(review), sources, review_sha256)
    proof = platform.read_json(Path(visibility_proof))
    prior_elf = proof["runtime_bindings"]["elf"]
    prior_path = platform.relative_file(ROOT, prior_elf["path"])
    app_path, app_raw = read_bound(controller.bindings["app_elf"])
    # 两侧保留各自相对/绝对路径契约，仅比较精确核验后的实际文件身份与完整原字节SHA。
    prior_sha = transport.digest(prior_path.read_bytes())
    require(prior_path.samefile(app_path) and prior_sha == prior_elf["sha256"] ==
            controller.bindings["app_elf"]["sha256"] == transport.digest(app_raw),
            "缓存先验与正式运行ELF实际文件或完整SHA不同")
    manifest_path = transport.exact_path(final_platform_manifest)
    result = delivery.check_manifest("evidence", str(manifest_path), str(ROOT))
    require(result["status"] == "CHECKS_OK", "最终PL产物清单机器核验失败")
    manifest = platform.read_json(manifest_path)
    receipt_path, raw = read_bound({"path": str(final_review), "sha256": final_review_sha256})
    receipt = json.loads(raw.decode("utf-8"))
    require(receipt.get("status") == "PASS" and receipt.get("role") == "INDEPENDENT_REVIEWER" and
            receipt.get("approved_manifest_sha256") == binding(manifest_path)["sha256"] and
            receipt.get("approved_profile_sha256") == binding(Path(visibility_proof))["sha256"] and
            receipt.get("visibility_parameter") == 1 and receipt.get("same_runtime_bsp_mmu_macros") is True and
            receipt.get("only_visibility_parameter_changed") is True,
            "最终PL独审未绑定visibility1、唯一参数变化或同ELF/BSP兼容性")
    bit = controller.bindings["bit"]
    require(any(str(ROOT / item["path"]) == bit["path"] and item["sha256"] == bit["sha256"]
                for item in manifest["files"]), "当前部署bit不是最终被审清单的实际产物")
    require(all(item["status"] in ("PASS", "NOT_APPLICABLE") for item in manifest["checks"]),
            "最终PL清单含失败/未执行/受阻检查")
    return {"build_details": binding(path), "visibility_proof": binding(Path(visibility_proof)),
            "visibility_review": {"path": str(review), "sha256": review_sha256},
            "final_manifest": binding(manifest_path), "final_review": binding(receipt_path),
            "deployment_bindings": controller.bindings,
            "scope": "机器仅核验文件绑定；独立Reviewer真实来源由总控负责。"}


def validate_plan(plan):
    """重核对109条实际冻结身份，防止修改准备JSON后重复样本冒充完整覆盖。"""
    require(plan["hardware_execution"] == "NOT_RUN" and plan["preparation"] == "PASS_OFFLINE_ASSET_BINDINGS" and
            len(plan["rows"]) == 109 and [row["index"] for row in plan["rows"]] == list(range(109)),
            "准备清单不是完整109冻结样本")
    expected = {"model_manifest": (checker.MODEL_PATH, transport.MODEL_SHA),
                "samples_manifest": ("report/evidence/S2A-T01/fixed_test_samples.json", transport.SAMPLES_SHA),
                "golden_source": (checker.CPU_D9_RECORD_PATH, transport.CPU_D9_SHA),
                "source_sha256": (str(Path(__file__)), binding(Path(__file__))["sha256"])}
    documents = {}
    for key, (relative, digest) in expected.items():
        path, raw = read_bound(plan[key])
        require(path == transport.exact_path(ROOT / relative) and plan[key]["sha256"] == digest,
                "冻结准备绑定路径/摘要不符：" + key)
        if key != "source_sha256": documents[key] = json.loads(raw.decode("utf-8"))
    require(plan["weights"]["sha256"] == documents["model_manifest"]["bindings"]["gf8_package"]["sha256"],
            "权重不是冻结GF8")
    for index, row in enumerate(plan["rows"]):
        sample, golden = documents["samples_manifest"]["samples"][index], documents["golden_source"]["samples"][index]
        require(row["sample_id"] == sample["sample_id"] == golden["sample_id"] and
                row["input"]["sha256"] == sample["pl_input_sha256"] == golden["input"]["pl_input_sha256"] and
                row["coverage_tags"] == sample["coverage_tags"], "准备条目与冻结索引不符")
        _, raw = read_bound(row["reference"])
        document = json.loads(raw.decode("utf-8"))
        require(document["kind"] == "s2b_fixed_reference" and document["model_manifest_sha256"] == transport.MODEL_SHA and
                document["golden_source"] == {"kind": "frozen_cpu_d9", **plan["golden_source"]} and
                len(document["samples"]) == 1, "准备参考来源错误")
        reference = document["samples"][0]
        for key in ("frame_id", "sample_id", "input", "detections", "nms_output_box_count"):
            require(reference[key] == golden[key], "准备参考与冻结黄金不同：" + key)
        for name, length in transport.HEAD_LENGTHS.items():
            require(reference["head_tensors"][name]["tensor_sha256"] == golden["head_tensors"][name]["tensor_sha256"] and
                    reference["head_tensors"][name]["byte_length"] == length, "准备参考头摘要错误")


class AcceptanceRunner:
    """逐帧锁存原始结果；不打开/关闭串口，不调用SDK，不自动重试或重同步。"""
    def __init__(self, wire, run, admission):
        self.wire, self.run, self.admission = wire, transport.new_directory(run), admission
        self.failed = False
        self.started = time.monotonic()
        self.log = (self.run / "progress.jsonl").open("x", encoding="utf-8", newline="\n")
        self.record = {"schema_version": 1, "status": "IN_PROGRESS", "hardware_execution": "NOT_RUN",
                       "started_at_utc8": datetime.now(TZ).isoformat(), "admission": admission,
                       "completed_corpus": 0, "completed_stress": 0, "frames": [],
                       "limitations": ["CSR负向/复位/恢复未由本runner执行。", "峰值内存未测。"]}
        save(self.run / "started.json", self.record)

    def rx_position(self):
        """要求借用的接收日志为实际可重读磁盘文件。"""
        self.wire.rx_file.flush()
        return self.wire.rx_file.tell()

    def rx_slice(self, start):
        """读取此帧实际接收区间；即使receive抛错也保留部分字节。"""
        end = self.rx_position()
        path = transport.exact_path(self.wire.rx_file.name)
        with path.open("rb") as stream:
            stream.seek(start); raw = stream.read(end - start)
        require(len(raw) == end - start, "原UART日志截断")
        return raw, {"path": str(path), "offset": start, "bytes": len(raw), "sha256": transport.digest(raw)}

    def send(self, request, header, payload, source):
        """发送前持久化输入/期限绑定；短写失败仍保存真实T15发送统计。"""
        require(not self.failed and not self.wire.failed, "失败runner不能发送后续请求")
        planned = {"sequence": request.sequence, "frame": request.frame, "op": request.op,
                   "repeat": request.repeat, "header_hex": header.hex(), "source": source,
                   "payload_bytes": len(payload), "payload_sha256": transport.digest(payload)}
        if request.op == transport.OP_RUN:
            planned["core_timeout"], planned["drain_timeout"] = struct.unpack_from("<II", payload)
        save(self.run / f"request_{request.sequence:08d}.json", planned)
        start = len(self.wire.events)
        try:
            self.wire.send(request, header, payload, source)
        except BaseException:
            self.failed = self.wire.failed = True
            raise
        finally:
            save(self.run / f"send_{request.sequence:08d}.json", {"events": self.wire.events[start:]})

    def receive(self, request, index, row=None, phase="weights"):
        """保存原UART与所有head/框后再检查；失败不可丢弃已收到结果。"""
        require(not self.failed and not self.wire.failed, "已失败runner禁止继续")
        frame = request.frame + index
        directory = transport.new_directory(self.run / f"{phase}_{frame:08d}")
        start, previous_epoch, started = self.rx_position(), self.wire.epoch, time.monotonic()
        record = {"status": "IN_PROGRESS", "phase": phase, "sequence": request.sequence,
                  "frame": frame, "repeat_index": index, "repeat_total": request.repeat,
                  "request_header_hex": request.pack().hex(), "previous_epoch": previous_epoch}
        try:
            returned = self.wire.receive(request, index)
            raw, span = self.rx_slice(start)
            require(len(raw) >= transport.HEADER.size, "缺少原UART响应")
            parsed = transport.decode_response(raw[:40], raw[40:], request, index, previous_epoch)
            require(returned == parsed, "receive返回值与实际原UART不符")
            meta, heads, boxes = parsed
            record.update(meta=meta, detections=boxes, raw_uart=span)
            save(directory / "metadata.json", record)
            save(directory / "boxes.json", boxes)
            tensors = {}
            for name, payload in heads.items():
                path = directory / f"{name}.bin"
                with path.open("xb") as stream:
                    stream.write(payload); stream.flush(); os.fsync(stream.fileno())
                tensors[name] = {"path": str(path), "tensor_sha256": transport.digest(payload), "byte_length": len(payload)}
            if row is not None:
                reference_path, reference_raw = read_bound(row["reference"])
                reference = json.loads(reference_raw.decode("utf-8"))["samples"][0]
                # checker绑定冻结frame；真实连续frame只保存于UART/metadata，不改写黄金来源。
                capture = {"frame_id": reference["frame_id"], "sample_id": reference["sample_id"],
                           "input": reference["input"], "head_tensors": tensors,
                           "nms_output_box_count": len(boxes), "detections": boxes}
                capture_path = directory / "capture.json"
                save(capture_path, {"schema_version": 1, "kind": "s2b_fixed_capture",
                                   "model_manifest_sha256": transport.MODEL_SHA, "samples": [capture]})
                record["checker_identity_mapping"] = {"actual_frame": frame, "frozen_reference_frame": reference["frame_id"],
                                                       "reason": "同固定输入repeat；协议身份由原UART独立核验"}
                report = checker.check_capture(reference_path, capture_path)
                save(directory / "capture_check.json", report)
                require(report["status"] == "PASS_OFFLINE_CAPTURE_CHECK", "检测头或全部检测框与冻结黄金不一致")
            record["status"] = "PASS_RESPONSE_AND_CAPTURE" if row is not None else "PASS_PROTOCOL_RESPONSE"
            self.record["frames"].append({"phase": phase, "frame": frame, "sequence": request.sequence,
                                           "epoch": meta["epoch"], "directory": str(directory)})
            return meta
        except BaseException as error:
            self.failed = self.wire.failed = True
            record.update(status="FAIL_LATCHED", error=repr(error))
            raise
        finally:
            raw, span = self.rx_slice(start)
            with (directory / "uart_response_raw.bin").open("xb") as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            record.update(raw_uart=span, elapsed_seconds=time.monotonic() - started,
                          actual_raw_bytes=len(raw), raw_header_hex=raw[:40].hex())
            save(directory / "result.json", record)
            append(self.log, record)

    def models(self, plan, core_timeout, drain_timeout, *, stress_count=STRESS_COUNT):
        """完整109逐次请求后一次repeat1000，连续seq/frame/epoch由运输接口强制核验。"""
        require(not self.failed, "runner已失败")
        for timeout in (core_timeout, drain_timeout):
            require(type(timeout) is int and 1 <= timeout <= 0xFFFFFFFF, "deadline须为非零32-bit，不改变CSR语义")
        require(self.wire.epoch == 0 and self.wire.last_sequence < 0xFFFFFFFF - len(plan["rows"]) - 2,
                "正式模型请求需新冷会话epoch0且sequence空间足够")
        weight_path, weight = read_bound(plan["weights"])
        sequence = self.wire.last_sequence + 1
        request, header = transport.make_request(transport.OP_WEIGHTS, sequence, 0, weight)
        self.send(request, header, weight, plan["weights"])
        self.receive(request, 0)
        next_frame = 0
        for row in plan["rows"]:
            self.run_input(row, sequence + 1, next_frame, 1, core_timeout, drain_timeout, "corpus")
            sequence += 1; next_frame += 1; self.record["completed_corpus"] += 1
        self.run_input(plan["rows"][0], sequence + 1, next_frame, stress_count,
                       core_timeout, drain_timeout, "stress")

    def run_input(self, row, sequence, frame, repeat, core_timeout, drain_timeout, phase):
        """发送前重新绑定同一实际input；repeat不重复传输输入或复制黄金。"""
        _, raw = read_bound(row["input"])
        _, reference_raw = read_bound(row["reference"])
        reference = json.loads(reference_raw.decode("utf-8"))["samples"][0]
        require(transport.digest(raw) == reference["input"]["pl_input_sha256"], "输入与黄金身份不同")
        width, height = reference["input"]["geometry_wh"]
        payload = struct.pack("<II", core_timeout, drain_timeout) + raw
        request, header = transport.make_request(transport.OP_RUN, sequence, frame, payload,
                                               width=width, height=height, repeat=repeat)
        self.send(request, header, payload, row["input"])
        for index in range(repeat):
            self.receive(request, index, row, phase)
            if phase == "stress": self.record["completed_stress"] += 1

    def finish(self, status, error=None):
        """成功/失败均保存摘要，不关闭总控串口或尝试硬件恢复。"""
        self.record.update(status=status, finished_at_utc8=datetime.now(TZ).isoformat(),
                           elapsed_seconds=time.monotonic() - self.started, events=self.wire.events,
                           final_epoch=self.wire.epoch, final_sequence=self.wire.last_sequence,
                           uart_rx=binding(Path(self.wire.rx_file.name)))
        if error is not None: self.record["error"] = repr(error)
        save(self.run / "acceptance_result.json", self.record)
        self.log.close()
        return self.record


def execute(controller, wire, preparation, run_dir, *, build_details, visibility_proof=None,
            review=None, review_sha256=None, final_platform_manifest=None, final_review=None,
            final_review_sha256=None, core_timeout=0xFFFFFFFF, drain_timeout):
    """总控在实际持有会话中调用；缺少证明时只生成BLOCKED，不发送请求。"""
    run = transport.new_directory(run_dir)
    try:
        admitted = admit(controller, wire, build_details, visibility_proof, review, review_sha256,
                         final_platform_manifest, final_review, final_review_sha256)
        require(run.parent == transport.exact_path(ROOT / "report/evidence/S2B-T18", "directory"),
                "正式板上运行须使用S2B-T18独立RunId")
        preparation = transport.exact_path(preparation)
        plan = json.loads(preparation.read_text(encoding="utf-8"))
        validate_plan(plan)
        admitted["preparation"] = binding(preparation)
    except BaseException as error:
        save(run / "acceptance_result.json", {"schema_version": 1, "status": "BLOCKED_BEFORE_TX",
             "hardware_execution": "NOT_RUN", "error": repr(error)})
        # 测试隔离目录也可验证门禁；只有正式证据目录生成阶段机器清单。
        if run.parent == ROOT / "report/evidence/S2B-T18":
            evidence_manifest(run, "BLOCKED", "实际会话/证明/最终平台/准备绑定门禁未通过；未发送UART。")
        raise
    runner = AcceptanceRunner(wire, run / "frames", admitted)
    runner.record["hardware_execution"] = "BORROWED_SESSION_UART_REQUESTED"
    try:
        # banner可能已由总控在cache前消费；仍从该wire原UART的开头核验编译XSA0。
        wire.rx_file.flush()
        raw_path = transport.exact_path(wire.rx_file.name)
        build = json.loads(read_bound(admitted["build_details"])[1].decode("utf-8"))
        expected = f"S2B-INFERENCE/1 READY SOURCE={build['source_sha256']['vitis/s2b_inference_app.c']} XSA={build['xsa_sha256']} MODEL={transport.MODEL_SHA}\r\n".encode("ascii")
        with raw_path.open("rb") as stream: banner = stream.read(len(expected))
        require(banner == expected, "本次真实wire未消费匹配同ELF/XSA0的banner")
        runner.record["banner"] = {"path": str(raw_path), "offset": 0, "bytes": len(banner), "sha256": transport.digest(banner)}
        runner.models(plan, core_timeout, drain_timeout)
        require(runner.record["completed_corpus"] == 109 and runner.record["completed_stress"] == 1000,
                "样本数量未达到完整验收")
    except BaseException as error:
        runner.failed = wire.failed = True
        runner.finish("FAIL_LATCHED", error)
        evidence_manifest(run, "FAIL", "模型请求或逐帧协议/黄金检查失败；原UART与已收到产物保留，禁止自动恢复。")
        raise
    result = runner.finish("PASS_MODEL_CORPUS_AND_STRESS_ONLY")
    evidence_manifest(run, "PASS", "109个冻结输入及1000次同输入连续任务全部原UART/整数头/全部框检查通过；CSR负向由T16独立完成。")
    return result


def main():
    """命令行仅准备；板上execute必须由总控显式传入已部署实际会话。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--prepare-dir", type=Path, required=True)
    args = parser.parse_args()
    print(prepare(args.asset_root, args.prepare_dir))


if __name__ == "__main__":
    main()
