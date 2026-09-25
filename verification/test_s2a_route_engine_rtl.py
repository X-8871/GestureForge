"""在系统 TEMP 验证 T15：官方全通道覆盖、真实 memory 黄金及错误取消恢复。"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_MANIFEST_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _vectors(manifest: dict, work: Path) -> list[dict]:
    """从冻结清单生成地址，按 D2 浮点 scale 独立计算 half-away 黄金。"""
    layers = {int(v["layer_index"]): v for v in manifest["layers"]}
    rows = []
    details = []
    for layer_id, channel, x in [(3, 0, 0), (6, 32, 5)]:
        layer = layers[layer_id]
        sources = layer["input_tensor_indices"]
        values = [len(sources), layer["route_groups"], layer["route_group_id"], channel, 0, x]
        selected = None
        remaining = channel
        for index in range(2):
            if index >= len(sources):
                values.extend([0]*8)
                continue
            producer = layers[sources[index]]
            _, c, h, w = producer["output_shape_nchw"]
            start, end = layer["route_source_channel_ranges"][index]
            ratio = layer["input_scales"][index] / layer["output_scale"]
            multiplier = math.floor(ratio*(1 << 31) + 0.5)
            values.extend([producer["tensor_address"], producer["tensor_length_bytes"],
                           c, h, w, start, end, multiplier])
            if selected is None and remaining < end-start:
                address = producer["tensor_address"] + (start+remaining)*h*w+x
                raw = 0xA5
                for shift in (0, 8, 16, 24):
                    raw ^= (address >> shift) & 255
                signed = raw if raw < 128 else raw-256
                if signed == -128:
                    raise AssertionError("smoke 选中非法 INT8 输入")
                magnitude = math.floor(abs(signed*ratio)+0.5)
                golden = max(-127, min(127, -magnitude if signed < 0 else magnitude))
                selected = (address, index, golden & 255, signed, multiplier)
            remaining -= end-start
        _, c, h, w = layer["output_shape_nchw"]
        values.extend([layer["tensor_address"], layer["tensor_length_bytes"], c, h, w])
        address, index, golden, signed, multiplier = selected
        output = layer["tensor_address"] + channel*h*w+x
        values.extend([address, output, index, golden])
        rows.append(" ".join(f"{v:08X}" for v in values))
        details.append(dict(layer=layer_id, source_address=address, source_index=index,
                            source_signed=signed, multiplier_q31=multiplier,
                            output_address=output, expected_byte=golden))
    (work / "route_smoke.dat").write_text("2\n"+"\n".join(rows)+"\n", encoding="ascii")
    amap = manifest["address_map"]
    image, weights = amap["input"], amap["weight_package"]
    ranges = sorted({(v["tensor_address"], v["tensor_address"]+v["tensor_length_bytes"])
                     for v in manifest["layers"] if v["op"] != "yolo"})
    header = [image["address"], image["address"]+image["length_bytes"],
              weights["address"], weights["address"]+weights["length_bytes"], len(ranges)]
    lines = [" ".join(f"{v:08X}" for v in header)]
    lines.extend(f"{a:08X} {b:08X}" for a,b in ranges)
    (work / "memory_ranges.dat").write_text("\n".join(lines)+"\n", encoding="ascii")
    return details


class TestS2ARouteEngineSmoke(unittest.TestCase):
    def test_memory_smoke(self) -> None:
        self.assertEqual(_sha(_MANIFEST), _MANIFEST_SHA)
        work = Path(tempfile.mkdtemp(prefix="s2a_t15_route_smoke_"))
        print(f"T15 smoke log_dir={work}", flush=True)
        details = _vectors(json.loads(_MANIFEST.read_text(encoding="utf-8")), work)
        sources = [_ROOT / name for name in (
            "src/int8_route_query.sv", "src/s2a_route_engine.sv",
            "src/s2a_memory_master.sv", "sim/s2a_memory_model.sv",
            "sim/tb_s2a_route_engine.sv")]
        phases = [("xvlog", ["-sv", *map(str, sources)]),
                  ("xelab", ["-top", "tb_s2a_route_engine", "-snapshot", "route_smoke"]),
                  ("xsim", ["-R", "route_smoke"])]
        deadline = time.monotonic()+600
        codes = []
        for name, args in phases:
            tool = _BIN / (name+".bat")
            self.assertTrue(tool.is_file(), str(tool))
            command = " ".join('"'+s+'"' if " " in s else s for s in [str(tool), *args])
            remain = deadline-time.monotonic()
            self.assertGreater(remain, 0, "Vivado 总计超过 600 秒")
            result = subprocess.run('cmd.exe /d /s /c "'+command+'"', cwd=work,
                                    capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=remain, check=False)
            output = result.stdout+"\n"+result.stderr
            (work/(name+".log")).write_text(output, encoding="utf-8")
            codes.append(result.returncode)
            self.assertEqual(result.returncode, 0, f"{name} 日志 {work}: {output[-4000:]}")
            self.assertNotIn("FAIL", output, f"{name} 断言失败：{work}")
        self.assertIn("PASS S2A-T15 route smoke cases=2 input_reads=2 writes=2 readbacks=2", output)
        print(json.dumps(dict(phases=codes, vectors=details,
                              sources_sha256={str(s.relative_to(_ROOT)): _sha(s) for s in sources},
                              vector_sha256=_sha(work/"route_smoke.dat")), ensure_ascii=False))





def _initial_byte(address: int) -> int:
    return 0xA5 ^ (address & 255) ^ ((address >> 8) & 255) ^ ((address >> 16) & 255) ^ ((address >> 24) & 255)


def _materialize_full(manifest: dict, work: Path, benchmark: bool) -> dict:
    """T06 流保留所有通道；候选值黄金仅用于绑定，memory 黄金来自地址初始化。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("t15_t06", _ROOT / "verification/test_s2a_route_rtl.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    t06 = module._materialize_vectors(manifest, work/"t06_vectors.dat", work/"t06_expected.dat")
    evidence_path = _ROOT/"report/evidence/S2A-T06/route_query_simulation.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    bindings = evidence["bindings"]
    for key in ("vector_sha256", "expected_stream_sha256", "golden_output_sha256"):
        if t06[key] != bindings[key]:
            raise AssertionError(f"T06 {key} changed")
    for key, filename in [("rtl_sha256", "src/int8_route_query.sv"),
                          ("runner_sha256", "verification/test_s2a_route_rtl.py"),
                          ("testbench_sha256", "sim/tb_s2a_route_query.sv")]:
        if _sha(_ROOT/filename) != bindings[key]:
            raise AssertionError(f"T06 {filename} changed")
    if evidence["result"] != "PASS" or bindings["manifest_sha256"] != _MANIFEST_SHA:
        raise AssertionError("T06 evidence invalid")
    layers = {v["layer_index"]: v for v in manifest["layers"]}
    selected = {}
    for line in (work/"t06_vectors.dat").read_text(encoding="ascii").splitlines():
        fields = line.split()
        cls, lid, case, y, x = map(int, fields[:5])
        if cls == 2 or (benchmark and (cls != 0 or case != 0)):
            continue
        selected.setdefault(lid, []).append((cls, case, y, x, fields))
    result = {"t06": t06, "layers": {}}
    for lid, cases in selected.items():
        layer = layers[lid]
        counts = dict(spatial=0, random=0, directed=0, queries=0, legal=0, raw80=0)
        golden_sha = hashlib.sha256()
        input_sha = hashlib.sha256()
        path = work/f"layer_{lid}.dat"
        with path.open("w", encoding="ascii", newline="\n") as stream:
            stream.write(str(len(cases))+"\n")
            for cls, case, y, x, fields in cases:
                count, groups, group_id, channels, height, width = map(int, fields[5:11])
                values = [count, groups, group_id, 0, y, x]
                sources = []
                for i in range(2):
                    base, length, c, start, end = map(int, fields[11+i*6:16+i*6])
                    multiplier = int(fields[16+i*6], 16)
                    values.extend([base,length,c,height if i<count else 0,width if i<count else 0,start,end,multiplier])
                    if i<count:
                        producer = layers[layer["input_tensor_indices"][i]]
                        if (base,length,c,start,end) != (producer["tensor_address"],producer["tensor_length_bytes"],
                            producer["output_shape_nchw"][1],*layer["route_source_channel_ranges"][i]):
                            raise AssertionError("T06 source descriptor differs from G0")
                        sources.append((base,start,end,layer["input_scales"][i]))
                if (channels,height,width) != tuple(layer["output_shape_nchw"][1:]):
                    raise AssertionError("T06 output descriptor differs from G0")
                values.extend([layer["tensor_address"],layer["tensor_length_bytes"],channels,height,width])
                stream.write(f"{cls} {lid} {case}\n"+" ".join(f"{v:08X}" for v in values)+"\n")
                for channel in range(channels):
                    index = 0 if channel < sources[0][2]-sources[0][1] else 1
                    local = channel if index==0 else channel-(sources[0][2]-sources[0][1])
                    base,start,end,scale=sources[index]
                    address=base+((start+local)*height+y)*width+x
                    output=layer["tensor_address"]+(channel*height+y)*width+x
                    raw=_initial_byte(address)
                    input_sha.update(f"{address:08X} {raw:02X}\n".encode("utf-8"))
                    signed=raw if raw<128 else raw-256
                    error=int(signed == -128)
                    scaled=float(signed)*scale/layer["output_scale"]
                    value=max(-127,min(127,math.floor(scaled+0.5) if scaled>=0 else -math.floor(-scaled+0.5))) & 255
                    if error: value=0
                    readback=_initial_byte(output) if error else value
                    golden_line=" ".join(f"{v:08X}" for v in [address,output,index,value,error,readback])+"\n"
                    stream.write(golden_line)
                    golden_sha.update(golden_line.encode("ascii"))
                    counts["queries"]+=1
                    counts["raw80" if error else "legal"]+=1
                counts["spatial"]+=1
                counts["random" if cls==0 else "directed"]+=1
        result["layers"][str(lid)]={"counts":counts,"vector_sha256":_sha(path),"memory_golden_sha256":golden_sha.hexdigest(),"memory_input_sha256":input_sha.hexdigest()}
    return result


def _vivado(work: Path, top: str, compile_only: bool = False, timeout: float = 600) -> list[dict]:
    sources=[_ROOT/name for name in ("src/int8_route_query.sv","src/s2a_route_engine.sv",
             "src/s2a_memory_master.sv","sim/s2a_memory_model.sv","sim/tb_s2a_route_engine.sv")]
    phases=[("xvlog",["-sv",*map(str,sources)]),("xelab",["-top",top,"-snapshot",top])]
    if not compile_only: phases=[("xsim",["-R",top])]
    results=[]
    for name,args in phases:
        command=" ".join('"'+s+'"' if " " in s else s for s in [str(_BIN/(name+".bat")),*args])
        started=time.monotonic()
        process=subprocess.run('cmd.exe /d /s /c "'+command+'"',cwd=work,
                               capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
        output=process.stdout+"\n"+process.stderr
        (work/(top+"_"+name+".log")).write_text(output,encoding="utf-8")
        if process.returncode or "FAIL" in output or "Fatal:" in output:
            raise AssertionError(f"{name} failure exit={process.returncode} log={work}: {output[-2500:]}")
        results.append(dict(phase=name,command=command,cwd=str(work),exit_code=process.returncode,seconds=time.monotonic()-started,output=output))
    return results


def _run_full(benchmark: bool = False) -> dict:
    import re
    import shutil
    work=Path(tempfile.mkdtemp(prefix="s2a_t15_route_bench_" if benchmark else "s2a_t15_route_full_"))
    print(f"T15 work={work}",flush=True)
    if _sha(_MANIFEST) != _MANIFEST_SHA: raise AssertionError("G0 changed")
    manifest=json.loads(_MANIFEST.read_text(encoding="utf-8"))
    _vectors(manifest,work)
    vectors=_materialize_full(manifest,work,benchmark)
    (work/"vectors_metadata.json").write_text(json.dumps(vectors,indent=2),encoding="utf-8")
    phase_records=_vivado(work,"tb_s2a_route_engine_full",True)
    layer_results={}
    if not benchmark:
        phase_records.extend(_vivado(work,"tb_s2a_route_engine_exceptions",True))
        exception_phase=_vivado(work,"tb_s2a_route_engine_exceptions")
        exception_match=re.search(r"PASS S2A-T15 exceptions (.*)",exception_phase[0]["output"])
        if not exception_match: raise AssertionError("missing exception completion")
        exception_counts={k:int(v) for k,v in re.findall(r"(\w+)=(\d+)",exception_match.group(1))}
        if exception_counts != dict(half_away=6,invalid=15,bus_errors=8,cancels=4,recoveries=28,result_cases=57):
            raise AssertionError(f"exception counts changed {exception_counts}")
        phase_records.extend(exception_phase)
        print(json.dumps(dict(exceptions=exception_counts)),flush=True)
    for lid,metadata in vectors["layers"].items():
        shutil.copyfile(work/f"layer_{lid}.dat",work/"route_full.dat")
        phases=_vivado(work,"tb_s2a_route_engine_full",timeout=600)
        output=phases[0]["output"]
        found=re.search(r"PASS S2A-T15 route full (.*)",output)
        if not found: raise AssertionError(f"missing completion {work}")
        observed={k:int(v) for k,v in re.findall(r"(\w+)=(\d+)",found.group(1))}
        expected=metadata["counts"]
        for key in ("spatial","queries","legal","raw80"):
            if observed[key]!=expected[key]: raise AssertionError(f"{lid}: {key} count mismatch")
        if (observed["reads"],observed["writes"],observed["readbacks"],observed["accepted"],observed["responses"]) != (
            2*expected["queries"],expected["legal"],expected["queries"],2*expected["queries"]+expected["legal"],2*expected["queries"]+expected["legal"]):
            raise AssertionError("memory transaction counts mismatch")
        shutil.copyfile(work/"tb_s2a_route_engine_full_xsim.log",work/f"layer_{lid}_xsim.log")
        layer_results[lid]=observed
        phase_records.extend(phases)
        print(json.dumps(dict(layer=lid,seconds=phases[0]["seconds"],counts=observed)),flush=True)

    report=dict(work_dir=str(work),vectors=vectors,layers=layer_results,phases=phase_records)
    if not benchmark: report["exceptions"]=exception_counts
    (work/"run_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    return report


def _acceptance() -> None:
    """两个全新 TEMP 目录独立生成并运行，计数与输入/黄金哈希必须一致。"""
    files=["src/s2a_route_engine.sv","sim/tb_s2a_route_engine.sv", "verification/test_s2a_route_engine_rtl.py",
           "src/int8_route_query.sv","src/s2a_memory_master.sv","sim/s2a_memory_model.sv",
           "report/evidence/S2A-T01/tiny416_model_manifest.json",
           "report/evidence/S2A-T06/route_query_simulation.json",
           "report/evidence/S2A-T10/memory_model_simulation.json",
           "report/evidence/S2A-T12/runtime_protocol_simulation.json"]
    # G0 正式规格路径从已绑定 T12 证据解析，使用仓库实际存在文件校验。
    dependency=json.loads((_ROOT/files[9]).read_text(encoding="utf-8"))
    g0_path=dependency["bindings"]["g0_spec_path"]
    if not (_ROOT/g0_path).is_file(): raise AssertionError("G0 spec path missing")
    files.append(g0_path)
    bindings={name:_sha(_ROOT/name) for name in files}
    for evidence_name, checks in [
        ("report/evidence/S2A-T10/memory_model_simulation.json", {"model_sha256":"sim/s2a_memory_model.sv"}),
        ("report/evidence/S2A-T12/runtime_protocol_simulation.json", {"memory_model_sha256":"sim/s2a_memory_model.sv","memory_master_sha256":"src/s2a_memory_master.sv"})]:
        dependency=json.loads((_ROOT/evidence_name).read_text(encoding="utf-8"))
        if dependency["result"] != "PASS": raise AssertionError("dependency not PASS")
        for key, filename in {**checks,"manifest_sha256":"report/evidence/S2A-T01/tiny416_model_manifest.json","g0_spec_sha256":g0_path}.items():
            if dependency["bindings"][key] != bindings[filename]: raise AssertionError(f"dependency hash mismatch {key}")
    baseline="c47cd864f7c2e9891e2fd3e4b4063d5bfede0224"
    if subprocess.run(["git","merge-base","--is-ancestor",baseline,"HEAD"],cwd=_ROOT).returncode:
        raise AssertionError("source baseline is not ancestor")
    runs=[_run_full(),_run_full()]
    for key in ("vectors","layers","exceptions"):
        if runs[0][key] != runs[1][key]: raise AssertionError(f"deterministic rerun differs: {key}")
    if bindings != {name:_sha(_ROOT/name) for name in files}: raise AssertionError("sources changed during acceptance")
    counts=runs[0]["vectors"]["layers"]
    random_queries=sum(v["counts"]["queries"]*1000//1016 for v in counts.values())
    directed_queries=sum(v["counts"]["queries"]*16//1016 for v in counts.values())
    if (random_queries,directed_queries) != (2208000,35328): raise AssertionError("official coverage changed")
    compact_runs=[]
    for run in runs:
        compact_runs.append(dict(layers=run["layers"],exceptions=run["exceptions"],
            phases=[dict(phase=v["phase"],exit_code=v["exit_code"],
                         command=v["command"].replace(str(_ROOT),"{repository}"),cwd="{system_TEMP}/s2a_t15_route_full_*")
                    for v in run["phases"]]))
    evidence=dict(schema_version=1,task="S2A-T15",result="PASS",seed=20260922,bindings=bindings,baseline_ancestor=baseline,
        random_queries=random_queries,directed_queries=directed_queries,
        total_queries=random_queries+directed_queries,deterministic_runs=2,
        vectors=runs[0]["vectors"],runs=compact_runs,
        logs="完整 stdout、实际命令/cwd、耗时及 run_report.json 仅保留系统 TEMP/s2a_t15_route_full_*；仓库证据不收录完整日志。",
        scope="11 个冻结 route 层，每层官方 1000 随机+16 定向空间坐标，全部输出通道；逐元素真实总线输入、写回及读回。",
        input_semantics="T06 官方 materialize 流及候选值黄金用于来源绑定和空间/描述符复用；实际 memory 输入为未修改的 T10 initial_byte(address)，raw 0x80 返回 BAD_ARGUMENT 并禁止写回，非 T06 候选值加载。",
        golden_semantics="Python 按 G0 source mapping 和原始浮点 input_scale/output_scale 计算 D2 half-away 黄金，不复用 RTL Q31 计算；另有6项正负奇数/2手算半舍入真实内存测试。",
        fixture_semantics="仅每个独立 spatial 的全部通道写回和真实 readback 完成且总线空闲后清 patch_count，保留 stall_index；异常/取消/复位测试全过程不清 patch。",
        limitations=["仅算子与 T10 memory、T12 memory master 集成；未执行真实 controller/runtime shell 与 route engine 联调，soft reset/timeout 到 abort 映射尚未验证。",
                     "buffer_owner_pl 固定为 1；T15 未单独验证 owner 门控，依赖 T12 已冻结协议证据。",
                     "未执行综合、时序、板测、完整网络黄金或 G5；仿真 PASS 不表示阶段完成。"])
    out=_ROOT/"report/evidence/S2A-T15"
    if not out.parent.is_dir(): raise AssertionError("missing evidence parent")
    out.mkdir(exist_ok=True)
    (out/"route_simulation.json").write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    print("PASS S2A-T15 deterministic acceptance runs=2 queries_per_run=2243328",flush=True)


if __name__ == "__main__":
    import os
    mode=os.environ.get("S2A_T15_MODE","smoke")
    if mode == "full":
        _acceptance()
    elif mode == "benchmark":
        _run_full(True)
    else:
        unittest.main()
