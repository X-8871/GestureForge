"""独立Reviewer的轻量公开API反例；仅mock，绝不导入SDK或操作硬件。"""

import ast
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
import zipfile

RUN = Path(__file__).absolute().parent / "attempt_r02"
ROOT = RUN.parents[4]
sys.path.insert(0, str(ROOT))
from verification import s2b_board_jtag as j
from verification import test_s2b_board_jtag as fixture

BASE = "140e5f6b7c4511b0a0699fab3a91b87de2faf381"
MANIFEST = "report/evidence/S2B-T16/postconfig_20261011_r02/delivery_manifest.json"
SOURCES = ("verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py",
           "verification/test_s2b_cold_observation.py", "vitis/run_s2b_visibility_probe.py",
           "verification/test_s2b_visibility_probe.py")
EXPECTED = ("06c1f46d9906d39e76f9befddcdb50eaf20cf485ddb5e5d48145ab0553143432",
            "4c8c65ce8ce0314962cae59d58f40e67ac2b531d101e2dfffaba45ce0654d18e",
            "89d5258678d3f30f83d241a7dade6dff2bcc7246b1a359da5a7be79acfe4ff2c",
            "d1fc585ff6d0a26c2d13b8bbb7f476357347dbce274489b1cc5906045730fe8d",
            "5fbdc4f4743325b89b00be570df0e0ce2ac1b084e9c6e64a536c6f70f3dd18fe")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, obj):
    target = RUN / name
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, default=repr)
        stream.write("\n")


def snapshot(relative, raw=None):
    target = RUN / "source_snapshot" / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write((ROOT / relative).read_bytes() if raw is None else raw)


def native(label, command):
    started = time.monotonic()
    process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=90)
    (RUN / (label + "_stdout.log")).write_bytes(process.stdout)
    (RUN / (label + "_stderr.log")).write_bytes(process.stderr)
    row = {"command": command, "native_exit_code": process.returncode,
           "elapsed_seconds": time.monotonic() - started}
    save(label + "_native.json", row)
    return process


def audit():
    """独立校验绑定、原生包装状态、SDK AST和实际XSA，不执行SDK源码。"""
    raw = (ROOT / MANIFEST).read_bytes()
    assert sha(raw) == "7eba2c2962d59633f753cf8b54d61fdf19b89f5f9de419fb920b41894769e6de"
    snapshot("reviewed_delivery_manifest.json", raw)
    manifest = json.loads(raw)
    audit_rows = []
    for row in manifest["files"]:
        path = ROOT / row["path"]
        actual = sha(j.exact_path(path).read_bytes())
        assert actual == row["sha256"], row["path"]
        audit_rows.append({"path": row["path"], "sha256": actual, "bytes": path.stat().st_size})
    assert len(audit_rows) == 65
    save("binding_audit.json", {"status": "PASS", "files": audit_rows})
    for name, expected in zip(SOURCES, EXPECTED):
        actual = (ROOT / name).read_bytes()
        assert sha(actual) == expected, name
        snapshot(name, actual)
    for name in ("src/s2b_control_csr.sv", "verification/check_s2b_ps_smoke_layout.py",
                 "verification/check_stage_delivery.py", "verification/s2b_board_transport.py",
                 "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"):
        snapshot(name)
    delta = native("source_diff", ["git", "diff", BASE, "--", *SOURCES])
    assert delta.returncode == 0
    assert native("diff_check", ["git", "diff", "--check", "--", *SOURCES]).returncode == 0
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        result = native(mode, [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"),
                              "--mode", mode, "--manifest", str(ROOT / MANIFEST)])
        assert result.returncode == expected, (mode, result.returncode)
    source_path = "vitis/run_s2b_visibility_probe.py"
    old = native("baseline_entry", ["git", "show", BASE + ":" + source_path])
    assert old.returncode == 0
    gate_names = ("sdk_source_closure", "verify_sdk_files", "verify_serial_files",
                  "verify_runtime_sources", "verify_native_alias")
    def selected(raw):
        tree = ast.parse(raw.decode("utf-8"))
        return {node.name: ast.dump(node, include_attributes=False) for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name in gate_names}
    assert selected(old.stdout) == selected((ROOT / source_path).read_bytes())
    receipt = json.loads((ROOT / "report/evidence/S2B-T16/postconfig_20261011_r02/consumer_binding.json").read_text(encoding="utf-8"))
    sdk_rows = receipt["sdk_file_closure"]
    for row in sdk_rows.values():
        path = j.exact_path(row["path"])
        assert sha(path.read_bytes()) == row["sha256"]
        assert path.stat().st_size == row["bytes"]
    assert len(sdk_rows) == 192
    sdk = Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\target.py")
    sdk_raw = j.exact_path(sdk).read_bytes()
    sdk_tree = ast.parse(sdk_raw.decode("utf-8"))
    target = next(node for node in sdk_tree.body if isinstance(node, ast.ClassDef) and node.name == "Target")
    methods = {node.name: node for node in target.body if isinstance(node, ast.FunctionDef)}
    extracts = {}
    for name in ("mrd", "mwr"):
        node = methods[name]
        extracts[name] = {"line": node.lineno, "end_line": node.end_lineno,
                          "source": "\n".join(sdk_raw.decode("utf-8").splitlines()[node.lineno - 1:node.end_lineno])}
    save("sdk_public_api_excerpts.json", {"sdk_target_sha256": sha(sdk_raw), "sdk_files_checked": 192,
         "gate_ast_unchanged": list(gate_names), "real_sdk_imports": 0, "excerpts": extracts})
    xsa = ROOT / "report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa"
    data = xsa.read_bytes()
    assert sha(data) == "6cff0c6afd009bf051028c4b793cc99c3c0c700002c2fdb2d247a33d2fc076a7"
    generated = RUN / "generated_basis"
    generated.mkdir()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = ["ps7_init.c", "ps7_init.h", "ps7_init.tcl", "ps7_init_gpl.c", "ps7_init_gpl.h"]
        names += [name for name in archive.namelist() if name.endswith(".hwh")]
        members = {name: archive.read(name) for name in names}
        for name, content in members.items():
            (generated / Path(name).name).write_bytes(content)
            frozen = ROOT / "report/evidence/S2B-T16/postconfig_20261011_r02/generated_basis" / Path(name).name
            assert frozen.read_bytes() == content
    # 单独解析原C/Tcl，按字面地址和完整32位mask手算，不调用被审解析器得到期待值。
    c_text = members["ps7_init.c"].decode("utf-8")
    t_text = members["ps7_init.tcl"].decode("utf-8")
    expected = [("WRITE", 0xF8000008, 0xDF0D), ("MASKWRITE", 0xF8000900, 15, 15),
                ("MASKWRITE", 0xF8000240, 0xFFFFFFFF, 0), ("WRITE", 0xF8000004, 0x767B)]
    tables = {}
    for branch in ("1_0", "2_0", "3_0"):
        body = re.search(r"unsigned long ps7_post_config_" + branch + r"\[\]\s*=\s*\{(.*?)\};", c_text, re.S).group(1)
        ops = []
        for op, args in re.findall(r"EMIT_(WRITE|MASKWRITE)\(([^)]*)\)", body):
            ops.append((op, *[int(arg.strip().rstrip("U"), 16) for arg in args.split(",")]))
        assert ops == expected
        tcl = re.search(r"proc ps7_post_config_" + branch + r"\s*\{\}\s*\{(.*?)\n\}", t_text, re.S).group(1)
        assert "mwr -force 0XF8000008 0x0000DF0D" in tcl
        assert "mask_write 0XF8000900 0x0000000F 0x0000000F" in tcl
        assert "mask_write 0XF8000240 0xFFFFFFFF 0x00000000" in tcl
        assert "mwr -force 0XF8000004 0x0000767B" in tcl
        tables[branch] = {"c_operations": ops, "tcl_equivalent_checked": True}
    basis = j.postconfig_basis(data)
    assert len(basis["hwh_clock_consumers"]) == 5 and basis["hwh_clock_hz"] == 50000000
    save("actual_xsa_audit.json", {"status": "PASS", "xsa_sha256": sha(data), "tables": tables,
         "production_parse_matches": basis, "sdk_imports": 0})
    save("provenance_summary.json", {"status": "PASS", "sdk_file_count": 192,
         "sdk_main_definition_count": 19, "tcf_reset_definition_count": 2,
         "breakpoint_definition_count": 2, "total_definition_count": 23,
         "counts_are_distinct": True, "unchanged_gate_functions": list(gate_names)})


class IndependentTarget(fixture.FakeTarget):
    """补充SLCR写保护、键值及APU上下文语义，并独立记录原生调用。"""
    def mwr(self, *args, **kwargs):
        address, words = kwargs["address"], kwargs["words"]
        assert self._name == "APU"
        assert args == ("--bypass_cache_synq",) and kwargs["size"] == 1 and kwargs["word_size"] == 4
        if address == 0xF8000008:
            assert words == [0xDF0D]
        elif address == 0xF8000004:
            assert words == [0x767B]
        elif address in (0xF8000900, 0xF8000240):
            assert self.session.memory[0xF800000C] & 1 == 0
        return super().mwr(*args, **kwargs)


def case(name, configure=None, expected_failure=True):
    folder = RUN / "cases" / name
    folder.mkdir(parents=True)
    bindings = {}
    for key in ("init_elf", "app_elf", "bit"):
        file = folder / key
        file.write_bytes(fixture.elf_bytes(app=key == "app_elf") if key.endswith("elf") else b"INDEPENDENT_MOCK_BIT")
        bindings[key] = {"path": str(file), "sha256": sha(file.read_bytes())}
    paths = {"xsa": ROOT / "report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa",
             "csr_source": ROOT / "src/s2b_control_csr.sv",
             "interface": ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
             "sdk_target": Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\target.py"),
             "tool_source": Path(j.__file__).absolute(), "transport_source": Path(j.transport.__file__).absolute(),
             "elf_parser": ROOT / "verification/check_s2b_ps_smoke_layout.py",
             "delivery_parser": ROOT / "verification/check_stage_delivery.py"}
    bindings.update({key: {"path": str(path), "sha256": sha(path.read_bytes())} for key, path in paths.items()})
    session = fixture.FakeSession()
    session.objects = {row["target_id"]: IndependentTarget(session, row) for row in session.rows.values()}
    session.memory[0xF8000900] = 0xA5A50002
    session.memory[0xF8000240] = 0xC0F01234
    controller = j.JtagController(session, bindings, folder)
    controller.select_and_gate()
    controller.system_reset_stop(bindings["interface"])
    if configure:
        configure(session, controller, bindings)
    started = time.monotonic()
    error = None
    try:
        controller.deploy()
    except BaseException as caught:
        error = caught
    row = {"scenario": name, "scope": "MOCK_ONLY_NOT_HARDWARE", "raised": repr(error) if error else None,
           "controller_failed": controller.failed, "postconfigured": controller.postconfigured,
           "app_running": controller.app_running, "cold_lifecycle_proven": controller.record["cold_lifecycle_proven"],
           "api_calls": len(controller.record["calls"]), "operations": session.operations,
           "postconfiguration": controller.record.get("postconfiguration"),
           "elapsed_seconds": time.monotonic() - started, "real_sdk_calls": 0}
    try:
        assert bool(error) == expected_failure, (name, repr(error))
        assert not session.objects[12].running
        assert not controller.record["cold_lifecycle_proven"]
        assert set(session._bptable) == {1}
        if expected_failure:
            assert controller.failed and not controller.postconfigured and not controller.app_running
            assert not any(op[0] == "dow" and Path(op[2]).name == "app_elf" for op in session.operations)
            before = copy.deepcopy(session.operations)
            try:
                controller.deploy()
                raise AssertionError("失败锁存后deploy被放行")
            except j.JtagError:
                pass
            assert before == session.operations
        else:
            writes = [(op[2], op[5]) for op in session.operations if op[0] == "postconfig_mwr"]
            assert writes == [(0xF8000008, [0xDF0D]), (0xF8000900, [0xA5A5000F]),
                              (0xF8000240, [0]), (0xF8000004, [0x767B])]
            assert controller.postconfigured and controller.record["postconfiguration"]["status"] == "PASS"
        row["status"] = "PASS"
    except BaseException:
        row["status"] = "FAILED_INDEPENDENT_ASSERTION"
        row["review_traceback"] = traceback.format_exc()
        raise
    finally:
        controller.close()
        save("cases/" + name + "/independent_result.json", row)
    print(name + " PASS " + str(row["api_calls"]) + " simulated_API", flush=True)
    return row


def cases():
    """独立组合反例：部分成功、持续清理失败、完整读回、身份及来源漂移。"""
    results = [case("happy_actual_xsa", expected_failure=False)]
    for nibble in (0, 1, 15):
        results.append(case("revision_" + str(nibble), lambda s, c, b, n=nibble: s.memory.update({0xF8007080: n << 28 | 0x7654321}), False))
    for address, value in ((0xF800000C, 0), (0xF8000170, 0x00600610), (0xF800010C, 6), (0xF8007080, True)):
        results.append(case("precondition_" + hex(address), lambda s, c, b, a=address, v=value: s.memory.update({a: v})))
    for label in ("unlock_partial", "unlock_partial_cleanup_exception", "unlock_partial_cleanup_ignored", "lock_ignored",
                  "upper_level_corrupt", "reset_high_bit", "clock_after_lock", "peer_drift", "target_drift", "boot_drift", "source_drift"):
        def configure(s, c, b, fault=label):
            original = s.objects[10].mwr
            def mutate(*args, **kw):
                address = kw["address"]
                if address == 0xF8000004 and fault in ("unlock_partial_cleanup_ignored", "lock_ignored"):
                    s.operations.append(("ignored_lock_mock", args, address, kw["words"]))
                    return None
                original(*args, **kw)
                if address == 0xF8000008:
                    if fault.startswith("unlock_partial"):
                        raise RuntimeError("独立原解锁部分成功异常")
                    if fault == "peer_drift": s._curchan_obj.remote_peer.attrs["Host"] = "localhost_changed"
                    if fault == "target_drift": s.rows["cpu0"]["target_ctx"] = "ctx_changed"
                    if fault == "boot_drift": s.memory[0xF800025C] = 1
                    if fault == "source_drift": Path(b["bit"]["path"]).write_bytes(b"INDEPENDENT_DRIFT")
                if address == 0xF8000004 and fault == "unlock_partial_cleanup_exception":
                    raise RuntimeError("独立cleanup异常")
                if address == 0xF8000004 and fault == "clock_after_lock": s.memory[0xF800010C] = 3
                if address == 0xF8000900 and fault == "upper_level_corrupt": s.memory[address] ^= 0x10000
                if address == 0xF8000240 and fault == "reset_high_bit": s.memory[address] = 1 << 31
            s.objects[10].mwr = mutate
        results.append(case(label, configure))
        last = results[-1]
        if label.startswith("unlock_partial"):
            assert "独立原解锁部分成功异常" in last["raised"]
        if label in ("peer_drift", "target_drift", "boot_drift", "source_drift"):
            assert len([op for op in last["operations"] if op[0] == "postconfig_mwr"]) == 1
    defaults = {0x14: 0, 0x18: 0, 0x1C: 519168, 0x20: 0x00100000, 0x24: 5903100,
                0x28: 0, 0x2C: 0, 0x5C: 0, 0x60: 0, 0x64: 0, 0x6C: 0, 0x70: 0, 0x74: 0}
    for offset, expected in defaults.items():
        results.append(case("cold_default_" + hex(offset), lambda s, c, b, o=offset, e=expected: s.memory.update({0x43C00000 + o: e ^ 1})))
    for offset in (0, 4, 0xC, 0x10, 0x50, 0x54, 0x58, 0x68):
        results.append(case("cold_identity_state_" + hex(offset), lambda s, c, b, o=offset: s.memory.update({0x43C00000 + o: 0xDEAD})))
    def unstable(s, c, b):
        original = s.objects[10].mrd
        def read(*args, **kw):
            result = original(*args, **kw)
            if kw["address"] == 0x43C0000C: s.memory[0x43C00074] += 1
            return result
        s.memory[0x43C00074] = 0
        s.objects[10].mrd = read
    results.append(case("cold_csr_unstable", unstable))
    def native_failure(s, c, b):
        original = s.objects[10].mrd
        def read(*args, **kw):
            if kw["address"] == 0xF8000900:
                print("独立原生部分stdout", flush=True)
                print("独立原生stderr", file=sys.stderr, flush=True)
                raise RuntimeError("独立mrd原生异常")
            return original(*args, **kw)
        s.objects[10].mrd = read
    results.append(case("public_mrd_native_exception", native_failure))
    save("independent_cases_summary.json", {"status": "PASS", "scenarios": len(results),
         "mock_api_calls": sum(row["api_calls"] for row in results), "real_sdk_calls": 0,
         "hardware_operations": 0, "cases": results})


if __name__ == "__main__":
    audit()
    cases()
    assert not any(name == "xsdb" or name.startswith("xsdb.") or name == "serial" for name in sys.modules)
