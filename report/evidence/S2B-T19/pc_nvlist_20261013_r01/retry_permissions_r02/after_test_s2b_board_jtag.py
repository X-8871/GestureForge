"""S2B-T16 离线mock SDK反例；不会导入XSDB或操作实物。"""

from pathlib import Path
import copy
from dataclasses import replace
import hashlib
import io
import json
import struct
import sys
import tempfile
from types import SimpleNamespace
import zipfile
import unittest

try:
    from . import s2b_board_jtag as j
except ImportError:
    import s2b_board_jtag as j


def elf_bytes(app=False, missing=None):
    """构造可由正式ELF解析器读取的最小ARM32测试文件。"""
    base = 0x100000 if app else 0
    names = ("s2b_ps_init_ready", "s2b_ps_init_fail", "s2b_ps_init_result", "s2b_ps_init_return")
    strings, symbols = bytearray(b"\0"), bytearray(16)
    for i, name in enumerate(names):
        if name == missing:
            continue
        offset = len(strings); strings.extend(name.encode() + b"\0")
        symbols.extend(struct.pack("<IIIBBH", offset, base + (0x100, 0x104, 0x180, 0x184)[i], 4, 0x12 if i < 2 else 0x11, 0, 1))
    shnames = b"\0.text\0.strtab\0.symtab\0.shstrtab\0"
    raw = bytearray(0x200)
    raw[0x100:0x200] = bytes(0x100)
    stroff = len(raw); raw.extend(strings)
    symoff = len(raw); raw.extend(symbols)
    shstroff = len(raw); raw.extend(shnames)
    while len(raw) % 4:
        raw.append(0)
    shoff = len(raw)
    for row in ((0,) * 10, (1, 1, 6, base + 0x100, 0x100, 0x100, 0, 0, 4, 0),
                (7, 3, 0, 0, stroff, len(strings), 0, 0, 1, 0),
                (15, 2, 0, 0, symoff, len(symbols), 2, 1, 4, 16),
                (23, 3, 0, 0, shstroff, len(shnames), 0, 0, 1, 0)):
        raw.extend(struct.pack("<10I", *row))
    raw[:52] = struct.pack("<16sHHIIIIIHHHHHH", b"\x7fELF\x01\x01\x01" + bytes(9), 2, 40, 1,
                          base + 0x100, 52, shoff, 0x5000000, 52, 32, 1, 40, 5, 4)
    raw[52:84] = struct.pack("<8I", 1, 0x100, base + 0x100, base + 0x100, 0x100, 0x100, 7, 4)
    return bytes(raw)


def target_rows():
    """实际历史枚举形状：DAP与FPGA分别在同一线缆的两个器件上下文。"""
    rows = {}
    for i, name in enumerate(j.NAMES):
        ctx = ("apu", "cpu0", "cpu1", "fpga")[i]
        rows[ctx] = {"name": name, "target_ctx": ctx, "target_id": 10 + i,
                     "parent_ctx": "apu" if i in (1, 2) else "", "parent": "APU" if i in (1, 2) else "",
                     "jtag_cable_ctx": "cable", "jtag_device_ctx": "fpga_device" if i == 3 else "dap_device",
                     "jtag_device_name": "xc7z020" if i == 3 else "arm_dap",
                     "jtag_cable_manufacturer": "Digilent", "jtag_cable_product": "JTAG-HS1", "jtag_cable_serial": "210512180081"}
    return rows


def xsa_bytes():
    """独立最小生成依据fixture；不引用被测常量，不冒充实际XSA。"""
    generated = "unsigned long ps7GetSiliconVersion(){unsigned long mask=0xF0000000;unsigned long *addr=(unsigned long*)0XF8007080;unsigned long ps_version=(*addr & mask)>>28;return ps_version;}\n"
    for revision in ("1_0", "2_0", "3_0"):
        generated += f"unsigned long ps7_post_config_{revision}[]={{EMIT_WRITE(0XF8000008,0xDF0DU),EMIT_MASKWRITE(0XF8000900,0xFU,0xFU),EMIT_MASKWRITE(0XF8000240,0xFFFFFFFFU,0x0U),EMIT_WRITE(0XF8000004,0x767BU),EMIT_EXIT(),}};\n"
        generated += f"unsigned long ps7_clock_init_data_{revision}[]={{EMIT_MASKWRITE(0XF8000170,0x03F03F30U,0x00600600U),EMIT_EXIT(),}};\n"
        generated += f"unsigned long ps7_pll_init_data_{revision}[]={{EMIT_MASKPOLL(0XF800010C,0x1U),EMIT_MASKPOLL(0XF800010C,0x2U),EMIT_MASKPOLL(0XF800010C,0x4U),EMIT_EXIT(),}};\n"
    generated += "int ps7_post_config(){if(si_ver==PCW_SILICON_VERSION_1){ret=ps7_config(ps7_post_config_1_0);if(ret!=PS7_INIT_SUCCESS)return ret;}else if(si_ver==PCW_SILICON_VERSION_2){ret=ps7_config(ps7_post_config_2_0);if(ret!=PS7_INIT_SUCCESS)return ret;}else{ret=ps7_config(ps7_post_config_3_0);if(ret!=PS7_INIT_SUCCESS)return ret;}}"
    consumers = (("ps7", "M_AXI_GP0_ACLK"), ("ps7", "S_AXI_HP0_ACLK"), ("axi_gp0_lite", "aclk"), ("rst_fclk0", "slowest_sync_clk"), ("infer", "clk"))
    def port(name, connections, clock=False):
        frequency = ' CLKFREQUENCY="50000000"' if clock else ""
        frequency += ' POLARITY="ACTIVE_LOW"' if not clock else ""
        return f'<PORT NAME="{name}"{frequency}><CONNECTIONS>' + "".join(f'<CONNECTION INSTANCE="{instance}" PORT="{pin}"/>' for instance, pin in connections) + '</CONNECTIONS></PORT>'
    modules = {instance: [] for instance in ("ps7", "axi_gp0_lite", "rst_fclk0", "infer")}
    modules["ps7"].append(port("FCLK_CLK0", consumers, True))
    for instance, pin in consumers:
        modules[instance].append(port(pin, (("ps7", "FCLK_CLK0"),), True))
    modules["ps7"].append(port("FCLK_RESET0_N", (("rst_fclk0", "ext_reset_in"),)))
    modules["rst_fclk0"].append(port("ext_reset_in", (("ps7", "FCLK_RESET0_N"),)))
    modules["rst_fclk0"].append(port("peripheral_aresetn", (("axi_gp0_lite", "aresetn"), ("infer", "cold_resetn"))))
    hwh = "<SYSTEM>" + "".join(f'<MODULE INSTANCE="{instance}">' + ('<PARAMETERS><PARAMETER NAME="C_EXT_RESET_HIGH" VALUE="0"/></PARAMETERS>' if instance == "rst_fclk0" else "") + '<PORTS>' + "".join(ports) + '</PORTS></MODULE>' for instance, ports in modules.items()) + "</SYSTEM>"
    raw = io.BytesIO()
    with zipfile.ZipFile(raw, "w") as archive:
        archive.writestr("ps7_init.c", generated)
        archive.writestr("ps7_init.h", "#define PCW_SILICON_VERSION_1 0\n#define PCW_SILICON_VERSION_2 1\n#define FPGA0_FREQ 50000000\n")
        archive.writestr("unit.hwh", hwh)
    return raw.getvalue()


class FakeBp:
    """原生二元tuple状态及按对象移除行为。"""
    def __init__(self, core, address, key):
        self.core, self.address, self.key, self.hits = core, address, key, 0

    def status(self):
        return "Installed", {self.core._id: {"Address": hex(self.address), "HitCount": self.hits}}

    def remove(self):
        self.core.session._bptable.pop(self.key)


class FakeTarget:
    """只模拟本工具使用的SDK API，严格验证cache绕过选项。"""
    def __init__(self, session, row):
        self.session = session
        self._ctx, self._id, self._name = row["target_ctx"], row["target_id"], row["name"]
        self.running, self.position = False, 0xFFFFFF28

    def state(self):
        return "Running" if self.running else "Stopped (Breakpoint)"

    def stop(self):
        self.session.operations.append(("stop", self._name))
        self.running = False

    def rrd(self, *args, reg):
        if args != ("--nvlist",) or reg != "pc":
            raise AssertionError("PC必须使用官方nvlist结构化读回")
        return {"pc": self.position}

    def mrd(self, *args, address, size, word_size):
        if self._name != "APU":
            raise AssertionError("不得通过CPU读取DAP探针")
        values = [self.session.memory.get(address + 4 * i, 0) for i in range(size)]
        if self.session.flip_final_error and address == j.CSR_BASE + 0x00C and size == 27 and values[1] == 8:
            self.session.memory[j.CSR_BASE + 0x010] = 9
        return values[0] if size == 1 else values

    def mwr(self, *args, address, size, word_size, words):
        postconfig = address in (0xF8000004, 0xF8000008, 0xF8000900, 0xF8000240)
        self.session.operations.append(("postconfig_mwr" if postconfig else "mwr", args, address, size, word_size, words))
        if args != ("--bypass_cache_synq",):
            raise AssertionError("缺少防止cache造假的原生选项")
        if address in (0xF8000004, 0xF8000008):
            self.session.memory[0xF800000C] = 1 if address == 0xF8000004 else 0
            return None
        if address == j.CSR_BASE + 8:
            self.session.memory[j.CSR_BASE + 0x064] = 0 if words == [2] else (5 if words == [3] else 1)
            if self.session.side_effect:
                self.session.memory[j.CSR_BASE + 0x050] += 1
            if self.session.bus_error is not None:
                raise RuntimeError(self.session.bus_error)
            if words == [2] and self.session.abort_transition is not None:
                self.session.abort_transition()
            return None
        if not self.session.drop_write:
            for i, value in enumerate(words):
                self.session.memory[address + 4 * i] = value

    def dow(self, *, file, auto_stop, set_entry):
        self.session.operations.append(("dow", self._name, file))
        self.running = False
        self.position = 0x100000 + 0x100 if Path(file).name == "app_elf" else 0x100
        if self.session.fail_dow:
            self.running = True
            raise RuntimeError("download native failure")

    def bpadd(self, *, addr, type):
        key = len(self.session._bptable) + 20
        bp = FakeBp(self, int(addr, 16), key)
        self.session._bptable[key] = bp
        if self.session.fail_bp:
            raise RuntimeError("partial bp native failure")
        return bp

    def con(self, *args, **kwargs):
        self.session.operations.append(("con", self._name, args, kwargs))
        if args:
            self.position = 0x104 if self.session.fail_init else 0x100
            for bp in self.session._bptable.values():
                if isinstance(bp, FakeBp) and bp.address == self.position:
                    bp.hits += 1
            self.session.memory[0x180], self.session.memory[0x184] = (0x82, 1) if self.session.fail_init else (2, 0)
        else:
            self.running = True

    def fpga(self, *args, **kwargs):
        self.session.operations.append(("fpga", args, kwargs))
        if args == ("--config_status",):
            status = self.session.config_status_word
            print(f"CONFIG_STATUS: {status}")
            print(f"MOCK_LOWER(Bits [3:0]):{status & 15}")
            print(f"END OF STARTUP (EOS) STATUS(Bits [4]):{(status >> 4) & 1}")
            print(f"MOCK_UPPER(Bits [31:5]):{status >> 5}")
        elif not args and set(kwargs) == {"file"}:
            self.session.config_status_word = 16
        else:
            raise AssertionError("非预期FPGA API参数")

    def rst(self, *args, **kwargs):
        self.session.operations.append(("rst", args, kwargs))
        self.session.config_status_word = 0


class FakeSession:
    """借用会话含一个外部断点，测试工具不得删它。"""
    def __init__(self):
        self._curchan_obj = SimpleNamespace(remote_peer=SimpleNamespace(attrs={"TransportName": "TCP", "Host": "127.0.0.1", "Port": "3121"}))
        self.rows = target_rows()
        self.objects = {r["target_id"]: FakeTarget(self, r) for r in self.rows.values()}
        self._bptable = {1: object()}
        self.memory = {0xF800025C: 0, j.DDRC_MODE_STATUS: 1, j.CSR_BASE: 0x53324250, j.CSR_BASE + 4: 0x100,
                       j.CSR_BASE + 0x00C: 0x400, j.CSR_BASE + 0x050: 0,
                       0xF800000C: 1, 0xF8007080: 0x21234567, 0xF8000900: 0x12340000,
                       0xF8000240: 0xFFFFFFFF, 0xF8000170: 0x00600600, 0xF800010C: 7}
        self.memory.update({j.CSR_BASE + 0x01C: 519168, j.CSR_BASE + 0x020: 0x00100000, j.CSR_BASE + 0x024: 5903100})
        self.operations = []
        self.fail_init = self.fail_bp = self.fail_dow = self.drop_write = self.side_effect = False
        self.bus_error = "SLVERR"
        self.abort_transition = None
        self.flip_final_error = False
        self.config_status_word = 0

    def targets(self, *args, **kwargs):
        return copy.deepcopy(self.rows) if args else self.objects[kwargs["id"]]


class FakeSerial:
    """完整实际字节流mock：从真实TX头/载荷构造RX，仍经T15原解析器。"""
    def __init__(self, on_request):
        self.on_request, self.tx, self.rx = on_request, bytearray(), bytearray()

    def write(self, raw):
        self.tx.extend(raw)
        if len(self.tx) >= j.transport.HEADER.size:
            request = j.transport.Header.unpack(bytes(self.tx[:j.transport.HEADER.size]))
            if len(self.tx) == j.transport.HEADER.size + request.length:
                self.rx.extend(self.on_request(request, bytes(self.tx[j.transport.HEADER.size:])))
                self.tx.clear()
        return len(raw)

    def read(self, length):
        raw = bytes(self.rx[:length]); del self.rx[:length]
        return raw


def response(request, *, epoch=0, status=0x400, error=0, reject=0, code=0, probe=b"", sequence=None, frame=None):
    """独立编码实际UART原帧；不把caller字典交给被测控制器。"""
    payload = j.transport.META.pack(epoch, status, error, reject, 0, 0, 0, 1, code) + probe
    import zlib
    header = j.transport.Header(request.op | 0x8000, request.sequence if sequence is None else sequence,
                                request.frame if frame is None else frame, request.width, request.height,
                                request.repeat, len(payload), zlib.crc32(payload))
    return header.pack() + payload

class JtagTests(unittest.TestCase):
    """每例创建隔离临时证据，反例必须失败且后续操作锁止。"""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.bindings = {}
        for name in ("init_elf", "app_elf", "xsa", "bit", "csr_source", "interface", "sdk_target"):
            path = self.directory / name
            path.write_bytes(elf_bytes(app=name == "app_elf") if name.endswith("elf") else xsa_bytes() if name == "xsa" else name.encode())
            self.bindings[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.bindings["tool_source"] = {"path": str(Path(j.__file__).absolute()), "sha256": hashlib.sha256(Path(j.__file__).read_bytes()).hexdigest()}
        for key, name in (("elf_parser", "check_s2b_ps_smoke_layout.py"), ("delivery_parser", "check_stage_delivery.py")):
            path = Path(j.__file__).absolute().parent / name
            self.bindings[key] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        path = Path(j.transport.__file__).absolute()
        self.bindings["transport_source"] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.run = self.directory / "run"; self.run.mkdir()
        self.session = FakeSession()
        self.controller = j.JtagController(self.session, self.bindings, self.run)

    def tearDown(self):
        if not self.controller.log.closed:
            self.controller.close()
        self.temp.cleanup()

    def ready(self):
        self.controller.select_and_gate()
        self.controller.system_reset_stop(self.bindings["interface"])

    def exchange(self, phase, cpu_seed, dap_seed):
        seed = cpu_seed if phase == 0 else dap_seed
        values = j.pattern(seed)
        if phase == 0:
            for i, value in enumerate(values):
                self.session.memory[j.PROBE_ADDRESS + 4 * i] = value
        return struct.pack("<64I", *values)

    def cache_wire(self, exchange=None, mutate_frame=None):
        exchange = self.exchange if exchange is None else exchange
        def callback(request, payload):
            phase, cpu, dap = struct.unpack("<III", payload)
            raw = response(request, probe=exchange(phase, cpu, dap))
            return raw if mutate_frame is None else mutate_frame(raw, phase)
        return j.JtagWireSession(FakeSerial(callback), io.BytesIO(), io.BytesIO(), response_timeout=0.02)

    def abort_wire(self, *, epoch=7, frame=19, final_epoch=None, final_error=8, final_status=0xC05, final_code=0,
                   sequence=None, wire_frame=None, ready=True):
        if not self.controller.app_running:
            self.controller.deploy()
        self.session.memory[j.CSR_BASE + 0x050] = epoch
        self.session.memory[j.CSR_BASE + 0x00C] = 0x102
        self.session.memory[j.CSR_BASE + 0x058] = frame
        def callback(request, payload):
            first = response(request, epoch=epoch, status=0x102, code=10) if ready else b""
            second = response(request, epoch=epoch if final_epoch is None else final_epoch, status=final_status,
                              error=final_error, code=final_code, sequence=sequence, frame=wire_frame)
            return first + second
        wire = j.JtagWireSession(FakeSerial(callback), io.BytesIO(), io.BytesIO(), response_timeout=0.02)
        wire.epoch = epoch - 1
        request, header = j.transport.make_request(j.transport.OP_DIAG, 1, frame, struct.pack("<III", 2, 1000, 1000))
        wire.send(request, header, struct.pack("<III", 2, 1000, 1000), {"kind": "mock_actual_diag"})
        def transition():
            self.session.memory[j.CSR_BASE + 0x00C] = 0xC05
            self.session.memory[j.CSR_BASE + 0x010] = 8
        self.session.abort_transition = transition
        return wire, request

    def scene(self, kind):
        raw = {"kind": kind, "expected_snapshot": {str(k): v for k, v in self.controller.csr_snapshot().items()}}
        path = self.directory / "scene.json"; path.write_text(json.dumps(raw), encoding="utf-8")
        return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def test_native_target_dynamic_ids_and_real_two_device_shape(self):
        self.ready(); self.assertEqual(self.controller.targets["cpu0"]._id, 11)

    def test_pc_nvlist_bounds_and_exact_sdk_arguments(self):
        self.controller.select_and_gate()
        for label, target_id in (("cpu0", 11), ("cpu1", 12)):
            for value in (0, 0xFFFFFFFF):
                with self.subTest(label=label, value=value):
                    self.session.objects[target_id].position = value
                    self.assertEqual(self.controller.pc(label), value)
                    row = self.controller.record["calls"][-1]
                    self.assertEqual(row["api"], label + ".rrd.pc")
                    self.assertEqual(row["args"], ("--nvlist",))
                    self.assertEqual(row["kwargs"], {"reg": "pc"})
                    self.assertEqual(row["return_type"], "dict")
                    self.assertEqual(row["return_repr"], repr({"pc": value}))

    def test_pc_nvlist_preserves_actual_async_info_and_raw_stderr(self):
        self.controller.select_and_gate()
        actual = "Info: ARM Cortex-A9 MPCore #1 (target 3) Stopped at 0xffffff34 (Suspended)\npc: ffffff34\n\n"
        diagnostic = "原始SDK诊断\n"
        def read(*args, reg):
            self.assertEqual(args, ("--nvlist",))
            self.assertEqual(reg, "pc")
            print(actual, end="")
            print(diagnostic, file=sys.stderr, end="")
            return {"pc": 0xFFFFFF34}
        self.session.objects[12].rrd = read
        self.controller.system_reset_stop(self.bindings["interface"])
        self.assertEqual(self.controller.record["system_reset"]["after"]["cpu1_pc"], 0xFFFFFF34)
        self.controller.close()
        rows = [json.loads(line) for line in (self.run / "jtag_calls.jsonl").read_text(encoding="utf-8").splitlines()]
        rows = [row for row in rows if row["api"] == "cpu1.rrd.pc"]
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row["stdout"], actual)
            self.assertEqual(row["stderr"], diagnostic)
            self.assertEqual(row["return_repr"], repr({"pc": 0xFFFFFF34}))

    def test_pc_nvlist_invalid_structure_locks_and_cleans_owned_breakpoints(self):
        class DictSubclass(dict):
            """字典子类不属于官方承诺的精确返回类型。"""
        invalid = (("bool", {"pc": True}), ("negative", {"pc": -1}),
                   ("oversized", {"pc": 0x100000000}), ("missing", {}),
                   ("extra", {"pc": 0x100, "r0": 0}), ("na", {"pc": "N/A"}),
                   ("empty", {"pc": ""}), ("errors", {"pc": 0x100, "error": "unavailable"}),
                   ("nested_error", {"pc": {"error": "unavailable"}}),
                   ("none", None), ("string", "pc: 00000100"), ("list", [0x100]),
                   ("tuple", ("pc", 0x100)), ("integer", 0x100),
                   ("dict_subclass", DictSubclass(pc=0x100)), ("float", {"pc": 256.0}),
                   ("hex_string", {"pc": "0x100"}), ("wrong_case", {"PC": 0x100}))
        for index, (name, value) in enumerate(invalid):
            with self.subTest(name=name):
                if index:
                    self.tearDown(); self.setUp()
                self.ready()
                self.controller.add_bp(0x100)
                def read(*args, reg):
                    self.assertEqual(args, ("--nvlist",))
                    self.assertEqual(reg, "pc")
                    # 合法文本不能补救不合法的官方结构化返回。
                    print("pc: 00000100")
                    return value
                self.session.objects[11].rrd = read
                with self.assertRaisesRegex(j.JtagError, "PC结构化"):
                    self.controller.deploy()
                self.assertTrue(self.controller.failed)
                self.assertFalse(self.controller.owned_bps)
                self.assertEqual(set(self.session._bptable), {1})
                self.assertFalse(self.session.objects[11].running)
                self.assertEqual([row[0] for row in self.session.operations if row[0] in ("stop", "con", "dow")], ["dow", "stop"])
                before = len(self.controller.record["calls"])
                with self.assertRaisesRegex(j.JtagError, "控制器已失败"):
                    self.controller.deploy()
                self.assertEqual(len(self.controller.record["calls"]), before)
                self.controller.close()
                result = json.loads((self.run / "jtag_result.json").read_text(encoding="utf-8"))
                self.assertEqual(result["status"], "FAILED")

    def test_pc_nvlist_sdk_exception_keeps_raw_output_locks_and_cleans(self):
        self.ready()
        normal = self.session.objects[11].rrd
        reads = 0
        def read(*args, reg):
            nonlocal reads
            reads += 1
            if reads == 1:
                return normal(*args, reg=reg)
            print("Info: 官方异步状态\n", end="")
            print("原始SDK异常诊断\n", file=sys.stderr, end="")
            raise RuntimeError("native rrd failed")
        self.session.objects[11].rrd = read
        with self.assertRaisesRegex(RuntimeError, "native rrd failed"):
            self.controller.deploy()
        self.assertTrue(self.controller.failed)
        self.assertFalse(self.controller.owned_bps)
        self.assertEqual(set(self.session._bptable), {1})
        self.assertFalse(self.session.objects[11].running)
        self.assertNotIn("cpu0.con.app", [row["api"] for row in self.controller.record["calls"]])
        row = next(row for row in self.controller.record["calls"] if row["api"] == "cpu0.rrd.pc" and row["status"] == "RAISED")
        self.assertEqual(row["args"], ("--nvlist",))
        self.assertEqual(row["stdout"], "Info: 官方异步状态\n")
        self.assertEqual(row["stderr"], "原始SDK异常诊断\n")
        self.assertEqual(row["exception_type"], "RuntimeError")
        before = len(self.controller.record["calls"])
        with self.assertRaisesRegex(j.JtagError, "控制器已失败"):
            self.controller.deploy()
        self.assertEqual(len(self.controller.record["calls"]), before)

    def test_pc_nvlist_invalid_before_reset_prevents_physical_mutations(self):
        self.controller.select_and_gate()
        self.session.objects[12].rrd = lambda *args, reg: {"pc": "N/A"}
        with self.assertRaisesRegex(j.JtagError, "PC结构化"):
            self.controller.system_reset_stop(self.bindings["interface"])
        self.assertTrue(self.controller.failed)
        self.assertFalse(self.session.operations)
        before = len(self.controller.record["calls"])
        with self.assertRaisesRegex(j.JtagError, "控制器已失败"):
            self.controller.deploy()
        self.assertEqual(len(self.controller.record["calls"]), before)

    def test_target_ambiguity(self):
        self.session.rows["fpga"]["name"] = "APU"
        with self.assertRaises(j.JtagError): self.ready()
        self.assertFalse(self.session.operations)

    def test_cable_mismatch(self):
        self.session.rows["cpu1"]["jtag_cable_serial"] = "other"
        with self.assertRaises(j.JtagError): self.ready()

    def test_cpu_parent_mismatch(self):
        self.session.rows["cpu1"]["parent_ctx"] = "other"
        with self.assertRaises(j.JtagError): self.ready()

    def test_cpu1_running_refuses_without_stop(self):
        self.session.objects[12].running = True
        with self.assertRaises(j.JtagError): self.ready()
        self.assertFalse(self.session.operations)

    def test_cpu0_running_refuses_without_stop(self):
        self.session.objects[11].running = True
        with self.assertRaises(j.JtagError): self.ready()
        self.assertFalse(self.session.operations)

    def test_boot_mode_nonzero(self):
        self.session.memory[0xF800025C] = 1
        with self.assertRaises(j.JtagError): self.ready()
        self.assertFalse(self.session.operations)

    def test_source_drift_failstop(self):
        self.ready(); self.controller.deploy()
        Path(self.bindings["csr_source"]["path"]).write_bytes(b"changed")
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(), 1, 2)
        self.assertFalse(self.session.objects[11].running)
        with self.assertRaises(j.JtagError): self.controller.deploy()

    def test_deploy_native_order_and_only_cpu0_continue(self):
        self.ready(); self.controller.deploy()
        ops = [r[0] for r in self.session.operations]
        self.assertEqual(ops, ["rst", "fpga", "dow", "con", "fpga", "fpga"] + ["postconfig_mwr"] * 4 + ["dow", "con"])
        self.assertEqual(self.session.operations[4][1], ())
        self.assertEqual(set(self.session.operations[4][2]), {"file"})
        self.assertEqual(set(self.session._bptable), {1})
        self.assertFalse(self.controller.record["cold_lifecycle_proven"])

    def test_missing_actual_symbol_refuses_before_download(self):
        self.ready()
        raw = elf_bytes(missing="s2b_ps_init_fail")
        with self.assertRaises(j.JtagError): j.init_layout(raw)
        Path(self.bindings["init_elf"]["path"]).write_bytes(raw)
        self.bindings["init_elf"]["sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaises(RuntimeError): self.controller.deploy()
        self.assertEqual([r[0] for r in self.session.operations], ["rst", "fpga"])

    def test_actual_symbol_addresses(self):
        entry, symbols = j.init_layout(elf_bytes())
        self.assertEqual(entry, 0x100)
        self.assertEqual(symbols["s2b_ps_init_result"], 0x180)

    def test_init_failed_blocks_bit_and_app(self):
        self.ready(); self.session.fail_init = True
        with self.assertRaises(j.JtagError): self.controller.deploy()
        self.assertFalse(any(r[0] == "fpga" and not r[1] for r in self.session.operations))
        self.assertEqual(set(self.session._bptable), {1})

    def test_partial_bp_failure_owned_cleanup(self):
        self.ready(); self.session.fail_bp = True
        with self.assertRaises(RuntimeError): self.controller.deploy()
        self.assertEqual(set(self.session._bptable), {1})

    def test_download_failure_halts_touched_cpu0(self):
        self.ready(); self.session.fail_dow = True
        with self.assertRaises(RuntimeError): self.controller.deploy()
        self.assertFalse(self.session.objects[11].running)
        self.assertIn(("stop", j.NAMES[1]), self.session.operations)

    def test_pattern_independent_known_words(self):
        self.assertEqual(j.pattern(0)[:4], [0, 0x9E3779B9, 0x3C6EF372, 0xDAA66D2B])
        self.assertEqual(j.pattern(0)[63], 0xEFA6F487)
        self.assertEqual(j.pattern(0xFFFFFFFF)[1], 0x61C88646)

    def test_cache_bypass_flag_all_64_words(self):
        self.ready(); self.controller.deploy()
        result = self.controller.cache_probe(self.cache_wire(), 0x12345678, 0xA5A5A5A5)
        writes = [r for r in self.session.operations if r[0] == "mwr"]
        self.assertEqual(writes[0][1:5], (("--bypass_cache_synq",), 0x10000000, 64, 4))
        self.assertEqual(len(writes[0][5]), 64)
        self.assertEqual(result["status"], "CROSS_MASTER_256_BYTES_MATCHED")

    def test_cache_bad_uart_seed_blocks_dap_write(self):
        self.ready(); self.controller.deploy()
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(lambda *a: bytes(256)), 1, 2)
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))

    def test_cache_truncated_uart(self):
        self.ready(); self.controller.deploy()
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(lambda *a: bytes(255)), 1, 2)

    def test_cache_cpu_flush_not_visible(self):
        self.ready(); self.controller.deploy()
        def exchange(phase, cpu, dap):
            return struct.pack("<64I", *j.pattern(cpu))
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(exchange), 1, 2)

    def test_cache_dap_write_not_visible(self):
        self.ready(); self.controller.deploy(); self.session.drop_write = True
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(), 1, 2)

    def test_cache_invalidate_wrong_seed(self):
        self.ready(); self.controller.deploy()
        def exchange(phase, cpu, dap):
            return self.exchange(phase, cpu, dap) if phase == 0 else struct.pack("<64I", *j.pattern(cpu))
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(exchange), 1, 2)

    def test_cache_same_seed_refuses(self):
        self.ready(); self.controller.deploy()
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(), 1, 1)

    def test_negative_bad_encoding_explicit_slverr(self):
        self.ready()
        result = self.controller.negative_start("bad_encoding", self.scene("bad_encoding"))
        self.assertEqual(result["status"], "EXPECTED_SLVERR_REJECTION_SAVED")

    def test_negative_busy_explicit_slverr(self):
        self.ready(); self.session.memory[j.CSR_BASE + 0x00C] = 0x102
        result = self.controller.negative_start("busy", self.scene("busy"))
        self.assertEqual(result["kind"], "busy")

    def test_negative_okay_cannot_pass(self):
        self.ready(); self.session.bus_error = None
        with self.assertRaisesRegex(j.JtagError, "SLVERR_UNPROVEN"):
            self.controller.negative_start("bad_encoding", self.scene("bad_encoding"))

    def test_negative_generic_bus_error_cannot_pass(self):
        self.ready(); self.session.bus_error = "DAP transaction error"
        with self.assertRaisesRegex(j.JtagError, "SLVERR_UNPROVEN"):
            self.controller.negative_start("bad_encoding", self.scene("bad_encoding"))

    def test_negative_decerr_cannot_pass(self):
        self.ready(); self.session.bus_error = "DECERR"
        with self.assertRaisesRegex(j.JtagError, "SLVERR_UNPROVEN"):
            self.controller.negative_start("bad_encoding", self.scene("bad_encoding"))

    def test_negative_side_effect_epoch_blocks(self):
        self.ready(); self.session.side_effect = True
        with self.assertRaisesRegex(j.JtagError, "epoch"):
            self.controller.negative_start("bad_encoding", self.scene("bad_encoding"))

    def test_negative_busy_idle_not_valid(self):
        self.ready()
        with self.assertRaises(j.JtagError): self.controller.negative_start("busy", self.scene("busy"))
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))

    def test_error_message_mention_does_not_prove_response(self):
        self.assertEqual(j.bus_error_kind(RuntimeError("timeout waiting for SLVERR")), "UNKNOWN")

    def test_system_stop_never_claims_cold_por(self):
        self.ready()
        self.controller.system_reset_stop(self.bindings["interface"])
        self.assertIn(("rst", ("--stop",), {"type": "system"}), self.session.operations)
        self.assertFalse(self.controller.record["cold_lifecycle_proven"])

    def test_target_context_drift_latches_failure(self):
        self.ready(); self.session.rows["cpu1"]["target_id"] = 30
        with self.assertRaises(j.JtagError): self.controller.deploy()
        self.assertTrue(self.controller.failed)

    def test_current_selection_and_state_reason_are_not_identity(self):
        self.ready()
        self.session.rows["fpga"].update(is_current=1, state_reason="changed")
        self.controller.gate()

    def test_peer_redirection_blocks_write(self):
        self.ready(); self.session._curchan_obj.remote_peer.attrs["Port"] = "9999"
        with self.assertRaises(j.JtagError): self.controller.deploy()
        self.assertEqual([r[0] for r in self.session.operations], ["rst", "fpga"])

    def test_deploy_without_current_system_reset_refuses(self):
        self.controller.select_and_gate()
        with self.assertRaises(j.JtagError): self.controller.deploy()
        self.assertFalse(self.session.operations)

    def test_caller_binding_mutation_not_adopted(self):
        self.ready()
        self.bindings["bit"]["sha256"] = "0" * 64
        self.controller.verify_bindings()
        self.assertNotEqual(self.bindings["bit"], self.controller.bindings["bit"])

    def test_internal_binding_change_blocks_before_sdk(self):
        self.ready()
        before = list(self.session.operations)
        self.controller.bindings["bit"]["sha256"] = "0" * 64
        with self.assertRaises(j.JtagError): self.controller.deploy()
        self.assertEqual(before, self.session.operations)

    def test_closed_controller_blocks_before_sdk(self):
        self.ready(); self.controller.close()
        before = list(self.session.operations)
        with self.assertRaises(j.JtagError): self.controller.deploy()
        self.assertEqual(before, self.session.operations)

    def test_abort_expected_error_safe_requires_real_csr(self):
        self.ready(); self.session.bus_error = None
        wire, request = self.abort_wire()
        result = self.controller.dap_abort(wire, request)
        self.assertEqual(result["status"], "ACTUAL_ERROR_SAFE_ABORTED_SAVED")
        self.assertEqual(wire.abort_pending["phase"], "ACK_REQUIRED")

    def test_abort_wrong_epoch_prevents_command(self):
        self.ready(); wire, request = self.abort_wire()
        self.session.memory[j.CSR_BASE + 0x050] = 999
        with self.assertRaises(j.JtagError): self.controller.dap_abort(wire, request)
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))

    def test_abort_native_slverr_race_never_success(self):
        self.ready(); wire, request = self.abort_wire()
        with self.assertRaises(j.JtagError): self.controller.dap_abort(wire, request)
        self.assertEqual(self.controller.record["dap_abort"][0]["response"], "SLVERR")

    def test_abort_write_only_not_final_pass(self):
        self.ready(); self.session.bus_error = None
        wire, request = self.abort_wire()
        wire.stream.rx = wire.stream.rx[:j.transport.HEADER.size + j.transport.META.size]
        with self.assertRaises(j.JtagError): self.controller.dap_abort(wire, request)
        self.assertTrue(wire.failed)

    def test_abort_done_cannot_replace_error_safe(self):
        self.ready(); self.session.bus_error = None
        wire, request = self.abort_wire(final_status=0xE04, final_error=0)
        with self.assertRaises(j.JtagError): self.controller.dap_abort(wire, request)

    def test_R1_cache_RUN_epoch7_rejected_before_phase_and_mwr(self):
        self.ready(); self.controller.deploy(); wire = self.cache_wire()
        self.session.memory[j.CSR_BASE + 0x00C] = 0x102
        self.session.memory[j.CSR_BASE + 0x050] = 7
        with self.assertRaises(j.JtagError): self.controller.cache_probe(wire, 1, 2)
        self.assertFalse(wire.sent_requests)
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))

    def test_R1_cache_IDLE_epoch7_rejected_before_phase_and_mwr(self):
        self.ready(); self.controller.deploy(); wire = self.cache_wire()
        self.session.memory[j.CSR_BASE + 0x050] = 7
        with self.assertRaises(j.JtagError): self.controller.cache_probe(wire, 1, 2)
        self.assertFalse(wire.sent_requests)
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))

    def test_R1_abort_no_actual_WAIT_rejected(self):
        self.ready(); self.session.bus_error = None
        wire, request = self.abort_wire(ready=False)
        with self.assertRaises(j.JtagError): self.controller.dap_abort(wire, request)
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))

    def test_R1_abort_wrong_UART_epoch999_rejected(self):
        self.ready(); self.session.bus_error = None
        wire, request = self.abort_wire(final_epoch=999)
        with self.assertRaises(j.JtagError): self.controller.dap_abort(wire, request)
        self.assertTrue(wire.failed)

    def test_R1_abort_error8_to9_between_complete_snapshots_rejected(self):
        self.ready(); self.session.bus_error = None
        wire, request = self.abort_wire()
        self.session.flip_final_error = True
        with self.assertRaisesRegex(j.JtagError, "快照正在变化"):
            self.controller.dap_abort(wire, request)
        self.assertEqual(self.session.memory[j.CSR_BASE + 0x010], 9)

    def test_R1_caller_bool_or_dictionary_not_UART_proof(self):
        self.ready(); self.controller.deploy()
        with self.assertRaises(j.JtagError): self.controller.dap_abort(True, {"epoch": 7, "error_code": 8})
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))

    def test_cache_callback_bytes_no_longer_accepted(self):
        self.ready(); self.controller.deploy()
        with self.assertRaises(j.JtagError): self.controller.cache_probe(lambda *args: bytes(256), 1, 2)

    def test_cache_actual_payload_CRC_error(self):
        self.ready(); self.controller.deploy()
        def mutate(raw, phase):
            return raw[:-1] + bytes([raw[-1] ^ 0x80])
        wire = self.cache_wire(mutate_frame=mutate)
        with self.assertRaises(j.JtagError): self.controller.cache_probe(wire, 1, 2)
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))
        self.assertTrue(self.controller.record["failed_uart_receipt_attempts"])

    def test_cache_actual_header_sequence_error(self):
        self.ready(); self.controller.deploy()
        def mutate(raw, phase):
            head = j.transport.Header.unpack(raw[:40])
            return replace(head, sequence=99).pack() + raw[40:]
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(mutate_frame=mutate), 1, 2)

    def test_abort_actual_final_frame_mismatch(self):
        self.ready(); self.session.bus_error = None
        wire, request = self.abort_wire(wire_frame=999)
        with self.assertRaises(j.JtagError): self.controller.dap_abort(wire, request)

    def test_abort_actual_final_sequence_mismatch(self):
        self.ready(); self.session.bus_error = None
        wire, request = self.abort_wire(sequence=999)
        with self.assertRaises(j.JtagError): self.controller.dap_abort(wire, request)

    def test_cache_start_between_phase0_and_DAP_write_rejected(self):
        self.ready(); self.controller.deploy()
        def exchange(phase, cpu, dap):
            raw = self.exchange(phase, cpu, dap)
            self.session.memory[j.CSR_BASE + 0x050] = 1
            self.session.memory[j.CSR_BASE + 0x00C] = 0x102
            return raw
        with self.assertRaises(j.JtagError): self.controller.cache_probe(self.cache_wire(exchange), 1, 2)
        self.assertFalse(any(r[0] == "mwr" for r in self.session.operations))

    def test_saved_raw_native_exception_and_utc8(self):
        self.ready(); self.session.bus_error = "DAP transaction error"
        with self.assertRaises(j.JtagError): self.controller.negative_start("bad_encoding", self.scene("bad_encoding"))
        self.controller.close()
        rows = [json.loads(s) for s in (self.run / "jtag_calls.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all(r["time_utc8"].endswith("+08:00") for r in rows))
        self.assertTrue(any(r.get("exception_repr") == "RuntimeError('DAP transaction error')" for r in rows))
        self.assertEqual(json.loads((self.run / "jtag_result.json").read_text(encoding="utf-8"))["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
