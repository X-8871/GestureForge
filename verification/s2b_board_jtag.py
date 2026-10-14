"""S2B-T16：供总控持有的 Vitis 2026.1 XSDB 会话调用；导入不操作硬件。"""

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
import copy
import hashlib
import io
import json
import re
import struct
import sys
import time
import traceback
import xml.etree.ElementTree as ET
import zipfile

TZ = timezone(timedelta(hours=8))
CABLE = ("Digilent", "JTAG-HS1", "210512180081")
NAMES = ("APU", "ARM Cortex-A9 MPCore #0", "ARM Cortex-A9 MPCore #1", "xc7z020")
PROBE_ADDRESS, PROBE_WORDS = 0x10000000, 64
CSR_BASE = 0x43C00000
DDRC_MODE_STATUS = 0xF8006054
EOS_NAME = "END OF STARTUP (EOS) STATUS"
SLCR_LOCK, SLCR_UNLOCK, SLCR_LOCKSTA = 0xF8000004, 0xF8000008, 0xF800000C
PS_VERSION, LEVEL_SHIFTER, FPGA_RESET = 0xF8007080, 0xF8000900, 0xF8000240
FPGA0_CLOCK, PLL_STATUS = 0xF8000170, 0xF800010C
CSR_SNAPSHOT = tuple(range(0x00C, 0x030, 4)) + (0x050, 0x054, 0x058, 0x05C, 0x060, 0x068, 0x06C, 0x070, 0x074)
IDENTITY_KEYS = ("name", "target_ctx", "parent_ctx", "parent", "jtag_cable_ctx", "jtag_device_ctx",
                 "jtag_device_name", "jtag_cable_manufacturer", "jtag_cable_product", "jtag_cable_serial")
# 既有ELF解析器使用同目录绝对导入；兼容模块导入和Vitis脚本两种入口。
if str(Path(__file__).absolute().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).absolute().parent))
try:
    from . import s2b_board_transport as transport
except ImportError:
    import s2b_board_transport as transport


class JtagWireSession(transport.WireSession):
    """复用T15实际串口协议解析；额外保留每次已发送请求与完整原始响应。"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sent_requests, self.rx_chunks, self.receipt_attempts = {}, [], []

    def send(self, request, header, payload, source_binding):
        """只在T15已完成真实stream.write之后登记不可变原字节。"""
        result = super().send(request, header, payload, source_binding)
        self.sent_requests[request.sequence] = (request, bytes(header), bytes(payload))
        return result

    def read_exact(self, length, deadline):
        """保留T15返回的真实串口字节，不接受调用方成功字典或bool。"""
        raw = super().read_exact(length, deadline)
        self.rx_chunks.append(raw)
        return raw

    def receipt(self, request, *, abort_ready=False):
        """调用T15原生接收，再复用同一decode_response核对保存的完整原header/payload。"""
        require(type(request) is transport.Header and request.sequence in self.sent_requests, "缺少真实已发送请求")
        sent, header, request_payload = self.sent_requests[request.sequence]
        require(sent == request and header == request.pack(), "请求身份变化")
        start, previous_epoch = len(self.rx_chunks), self.epoch
        try:
            result = self.receive_abort_ready(request) if abort_ready else self.receive(request, 0)
        finally:
            raw = b"".join(self.rx_chunks[start:])
            self.receipt_attempts.append({"request_header_hex": header.hex(), "request_payload_hex": request_payload.hex(),
                                          "raw_received_hex": raw.hex(), "abort_ready": abort_ready})
        require(len(raw) >= transport.HEADER.size, "实际UART响应缺少完整头")
        raw_header, payload = raw[:transport.HEADER.size], raw[transport.HEADER.size:]
        parsed = transport.decode_response(raw_header, payload, request, 0, previous_epoch, abort_ready=abort_ready)
        require(type(result) is tuple and len(result) == 3 and result == parsed, "UART返回值与实际原字节不符")
        return {"request_header_hex": header.hex(), "request_payload_hex": request_payload.hex(),
                "header_hex": raw_header.hex(), "payload_hex": payload.hex(), "meta": parsed[0]}


class JtagError(RuntimeError):
    """门禁或真实读回失败；当前控制器永久锁存失败。"""


def require(condition, message):
    """不受 Python 优化选项影响的门禁。"""
    if not condition:
        raise JtagError(message)


def parse_config_status(value, stdout, stderr):
    """严格消费SDK config_status原始输出；UG470表5-29规定EOS位4。"""
    require(value is None and type(stdout) is str and type(stderr) is str and not stderr,
            "CONFIG_STATUS返回类型或stderr错误")
    lines = stdout.splitlines()
    require(len(lines) >= 2, "CONFIG_STATUS缺少字段metadata")
    header = re.fullmatch(r"CONFIG_STATUS: (0|[1-9][0-9]*)", lines[0])
    require(header is not None, "CONFIG_STATUS原字格式未知")
    status = int(header.group(1))
    require(0 <= status <= 0xFFFFFFFF, "CONFIG_STATUS原字越界")
    fields, occupied, eos = [], set(), []
    for line in lines[1:]:
        match = re.fullmatch(r" *([^\r\n]+?)\(Bits \[(0|[1-9][0-9]*)(?::(0|[1-9][0-9]*))?\]\):(0|[1-9][0-9]*)", line)
        require(match is not None, "CONFIG_STATUS字段格式未知")
        name, high, low, field_value = match.groups()
        require(name == name.strip() and bool(name), "CONFIG_STATUS字段名称为空或不规范")
        high, low = int(high), int(low) if low is not None else int(high)
        field_value = int(field_value)
        require(0 <= low <= high < 32, "CONFIG_STATUS位号越界或倒置")
        bits = set(range(low, high + 1))
        require(not bits & occupied, "CONFIG_STATUS重复或重叠字段")
        occupied.update(bits)
        mask = (1 << (high - low + 1)) - 1
        require(field_value <= mask and field_value == (status >> low) & mask,
                "CONFIG_STATUS字段位宽或原字不一致")
        field = {"name": name, "high": high, "low": low, "value": field_value}
        fields.append(field)
        if name == EOS_NAME:
            eos.append(field)
    require(len(eos) == 1 and eos[0]["high"] == eos[0]["low"] == 4,
            "CONFIG_STATUS缺少唯一EOS位4 metadata")
    require(occupied == set(range(32)), "CONFIG_STATUS字段metadata未完整覆盖位0..31")
    return {"status_word": status, "status_word_hex": f"0x{status:08X}", "fields": fields, "eos": eos[0]["value"]}


def exact_path(path, directory=False):
    """逐分量精确核验路径名称，并拒绝链接与重解析点。"""
    path = Path(path)
    require(path.is_absolute() and not any(c in str(path) for c in "*?[]") and ".." not in path.parts,
            "需要精确绝对路径")
    current = Path(path.anchor)
    for name in path.parts[1:]:
        rows = [p for p in current.iterdir() if p.name.casefold() == name.casefold()]
        require(len(rows) == 1 and rows[0].name == name, "路径名称不存在或大小写冲突：" + str(path))
        current = rows[0]
        require(not current.is_symlink() and not (getattr(current.stat(follow_symlinks=False), "st_file_attributes", 0) & 0x400),
                "拒绝链接或重解析点")
    require(current.is_dir() if directory else current.is_file(), "目标类型错误：" + str(path))
    return current


def bound_bytes(binding):
    """实际消费前重新核验完整 SHA；不会以 PASS 或角色声明代替核验。"""
    require(type(binding) is dict and set(binding) == {"path", "sha256"}, "绑定格式错误")
    expected = binding["sha256"]
    require(type(expected) is str and re.fullmatch(r"[0-9a-f]{64}", expected), "SHA必须完整小写64位")
    raw = exact_path(binding["path"]).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected, "绑定文件发生漂移：" + binding["path"])
    return raw


def postconfig_basis(raw):
    """只消费固定XSA的生成表及HWH；不执行生成C/Tcl或SDK私有初始化。"""
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        hwh = [name for name in names if name.endswith(".hwh")]
        require(len(hwh) == 1 and names.count("ps7_init.c") == names.count("ps7_init.h") == 1,
                "XSA生成成员缺失或歧义")
        members = {}
        for name in ("ps7_init.c", "ps7_init.h", hwh[0]):
            require(archive.getinfo(name).file_size <= 4 * 1024 * 1024, "XSA生成成员超出预算")
            members[name] = archive.read(name)
    source = re.sub(r"/\*.*?\*/|//[^\r\n]*", "", members["ps7_init.c"].decode("utf-8"), flags=re.S)
    header = members["ps7_init.h"].decode("utf-8")
    for name, value in (("PCW_SILICON_VERSION_1", 0), ("PCW_SILICON_VERSION_2", 1), ("FPGA0_FREQ", 50000000)):
        require(re.findall(r"^\s*#define\s+" + name + r"\s+([0-9]+)\s*$", header, re.M) == [str(value)],
                "生成silicon/FPGA0定义变化：" + name)
    def table(name):
        rows = re.findall(r"unsigned\s+long\s+" + name + r"\[\]\s*=\s*\{(.*?)\};", source, re.S)
        require(len(rows) == 1, "生成表缺失或歧义：" + name)
        operations = []
        def consume(match):
            operation, args = match.groups()
            parts = [] if not args.strip() else [part.strip() for part in args.split(",")]
            require(all(re.fullmatch(r"0[xX][0-9A-Fa-f]+U?", part) for part in parts), "生成表参数未知")
            operations.append((operation, *[int(part.rstrip("U"), 16) for part in parts]))
            return ""
        residue = re.sub(r"EMIT_([A-Z]+)\(([^()]*)\)\s*,", consume, rows[0])
        require(not residue.strip() and operations and operations[-1] == ("EXIT",), "生成表含未支持内容")
        return operations
    expected = [("WRITE", SLCR_UNLOCK, 0xDF0D), ("MASKWRITE", LEVEL_SHIFTER, 0xF, 0xF),
                ("MASKWRITE", FPGA_RESET, 0xFFFFFFFF, 0), ("WRITE", SLCR_LOCK, 0x767B), ("EXIT",)]
    tables = {}
    for revision in ("1_0", "2_0", "3_0"):
        operations = table("ps7_post_config_" + revision)
        require(operations == expected, "生成postconfig动作与已批准四动作不同")
        clock = [row for row in table("ps7_clock_init_data_" + revision) if row[1:2] == (FPGA0_CLOCK,)]
        require(clock == [("MASKWRITE", FPGA0_CLOCK, 0x03F03F30, 0x00600600)], "生成FPGA0 clock不符")
        pll = [row for row in table("ps7_pll_init_data_" + revision) if row[0] == "MASKPOLL" and row[1] == PLL_STATUS]
        require(pll == [("MASKPOLL", PLL_STATUS, 1), ("MASKPOLL", PLL_STATUS, 2), ("MASKPOLL", PLL_STATUS, 4)],
                "生成PLL锁定位依据不符")
        tables[revision] = {"operations": operations, "clock": clock[0], "pll_masks": [row[2] for row in pll]}
    # 精确核对生成函数的版本读取与分支语义；else仍为3.0而非拒绝未知nibble。
    compact = re.sub(r"\s+", "", source)
    require("unsignedlongmask=0xF0000000;unsignedlong*addr=(unsignedlong*)0XF8007080;unsignedlongps_version=(*addr&mask)>>28;returnps_version;" in compact,
            "生成silicon读取语义不同")
    require("if(si_ver==PCW_SILICON_VERSION_1){ret=ps7_config(ps7_post_config_1_0);if(ret!=PS7_INIT_SUCCESS)returnret;}elseif(si_ver==PCW_SILICON_VERSION_2){ret=ps7_config(ps7_post_config_2_0);if(ret!=PS7_INIT_SUCCESS)returnret;}else{ret=ps7_config(ps7_post_config_3_0);if(ret!=PS7_INIT_SUCCESS)returnret;}" in compact,
            "生成postconfig版本分支不同")
    root = ET.fromstring(members[hwh[0]])
    def port(instance, name):
        ports = root.findall(f".//MODULE[@INSTANCE='{instance}']/PORTS/PORT[@NAME='{name}']")
        require(len(ports) == 1, "HWH端口缺失或歧义")
        return ports[0]
    def connections(node):
        return {(item.get("INSTANCE"), item.get("PORT")) for item in node.findall("./CONNECTIONS/CONNECTION")}
    consumers = {("ps7", "M_AXI_GP0_ACLK"), ("ps7", "S_AXI_HP0_ACLK"), ("axi_gp0_lite", "aclk"),
                 ("rst_fclk0", "slowest_sync_clk"), ("infer", "clk")}
    clock_port = port("ps7", "FCLK_CLK0")
    require(clock_port.get("CLKFREQUENCY") == "50000000" and connections(clock_port) == consumers,
            "HWH FCLK0时钟连接/频率不同")
    for instance, name in consumers:
        node = port(instance, name)
        require(node.get("CLKFREQUENCY") == "50000000" and connections(node) == {("ps7", "FCLK_CLK0")},
                "HWH消费时钟不同")
    require(connections(port("ps7", "FCLK_RESET0_N")) == {("rst_fclk0", "ext_reset_in")} and
            connections(port("rst_fclk0", "ext_reset_in")) == {("ps7", "FCLK_RESET0_N")} and
            connections(port("rst_fclk0", "peripheral_aresetn")) == {("axi_gp0_lite", "aresetn"), ("infer", "cold_resetn")},
            "HWH cold reset连接不同")
    require(all(port(instance, name).get("POLARITY") == "ACTIVE_LOW" for instance, name in
                (("ps7", "FCLK_RESET0_N"), ("rst_fclk0", "ext_reset_in"), ("rst_fclk0", "peripheral_aresetn"))) and
            [item.get("VALUE") for item in root.findall(".//MODULE[@INSTANCE='rst_fclk0']/PARAMETERS/PARAMETER[@NAME='C_EXT_RESET_HIGH']")] == ["0"],
            "HWH cold reset极性不同")
    return {"member_sha256": {name: hashlib.sha256(value).hexdigest() for name, value in members.items()},
            "tables": tables, "hwh_clock_hz": 50000000, "hwh_clock_consumers": sorted(consumers),
            "meaning": "编译XSA的生成依据；implemented连接仍须T19独立兼容闭包批准，寄存器读回不等于实测频率。"}


def validate_targets(properties):
    """只接受同链四主体及官方递归枚举暴露的完整双核PA物理访问子目标。"""
    require(type(properties) is dict and len(properties) in (4, 6), "目标数量或类型错误")
    selected, physical = {}, []
    for ctx, row in properties.items():
        require(type(row) is dict and row.get("name") in (*NAMES, "PA"), "目标歧义")
        require(row.get("target_ctx") == ctx and type(row.get("target_id")) is int and row["target_id"] > 0, "目标ID/上下文错误")
        require(tuple(row.get(k) for k in ("jtag_cable_manufacturer", "jtag_cable_product", "jtag_cable_serial")) == CABLE,
                "线缆身份不符")
        require(all(type(row.get(k)) is str and row[k] for k in ("jtag_cable_ctx", "jtag_device_ctx")), "目标链缺失")
        if row["name"] == "PA":
            physical.append(row)
        else:
            require(row["name"] not in selected, "目标歧义")
            selected[row["name"]] = row
    require(set(selected) == set(NAMES) and len({r["target_id"] for r in properties.values()}) == len(properties), "目标不唯一")
    require(len({r["jtag_cable_ctx"] for r in properties.values()}) == 1, "设备不在同一线缆")
    apu = selected["APU"]
    require(apu.get("jtag_device_name") == "arm_dap" and selected[NAMES[3]].get("jtag_device_name") == "xc7z020", "DAP/FPGA器件类型不符")
    for name in NAMES[1:3]:
        require(selected[name].get("parent_ctx") == apu["target_ctx"] and selected[name].get("parent") == "APU" and
                selected[name]["jtag_device_ctx"] == apu["jtag_device_ctx"] and selected[name].get("jtag_device_name") == "arm_dap", "CPU父链不符")
    if physical:
        require(len(physical) == 2, "PA目标必须为完整双核对")
        for name in NAMES[1:3]:
            cpu = selected[name]
            matches = [row for row in physical if row.get("parent_ctx") == cpu["target_ctx"]]
            require(len(matches) == 1, "PA父核缺失或重复")
            row = matches[0]
            # 官方递归原地展开APU的children缓存，parent文字与level是显示副作用；真实父链使用parent_ctx。
            require(row["target_ctx"] == cpu["target_ctx"] + ".pa" and row.get("parent") == "APU" and
                    type(row.get("level")) is int and row["level"] == 1, "PA上下文或官方显示属性不符")
            require(all(row.get(key) == cpu.get(key) for key in set(row) | set(cpu) if key.startswith("jtag_")), "PA线缆或DAP父链不符")
    return selected


def pattern(seed):
    """冻结的64个小端word模式，测试以独立常量验证。"""
    require(type(seed) is int and 0 <= seed <= 0xFFFFFFFF, "seed不是32-bit整数")
    return [seed ^ ((0x9E3779B9 * i) & 0xFFFFFFFF) for i in range(PROBE_WORDS)]


def init_layout(raw):
    """用实际ELF符号表取得停点/诊断地址，并核对全部OCM LOAD和ALLOC。"""
    try:
        from .check_s2b_ps_smoke_layout import parse_elf
    except ImportError:
        from check_s2b_ps_smoke_layout import parse_elf
    parsed = parse_elf(raw)
    intervals = ((0, 0x30000), (0xFFFF0000, 0xFFFFFE00))
    def ocm(begin, size):
        return any(low <= begin and begin + size <= high for low, high in intervals)
    require(ocm(parsed["entry"], 4), "init入口不属于OCM")
    loads = [p for p in parsed["programs"] if p["type"] == 1 and p["memory_size"]]
    require(loads, "init缺少LOAD")
    for p in loads:
        require(p["virtual"] == p["physical"] and ocm(p["physical"], p["memory_size"]), "init LOAD越界")
    for s in parsed["sections"]:
        if s["flags"] & 2 and s["size"]:
            require(ocm(s["address"], s["size"]), "init ALLOC越界")
    symbols = {}
    for name, expected_type in (("s2b_ps_init_ready", 2), ("s2b_ps_init_fail", 2),
                                ("s2b_ps_init_result", 1), ("s2b_ps_init_return", 1)):
        rows = [s for s in parsed["symbols"] if s["name"] == name and s["section"] != 0]
        require(len(rows) == 1 and rows[0]["type"] == expected_type and rows[0]["size"] >= 4 and
                rows[0]["value"] % 4 == 0 and ocm(rows[0]["value"], rows[0]["size"]), "ELF符号缺失/歧义/类型错误：" + name)
        symbols[name] = rows[0]["value"]
    require(len(set(symbols.values())) == 4, "init符号地址重叠")
    return parsed["entry"], symbols


def bus_error_kind(error):
    """仅识别明确响应原文；通用DAP/超时异常不能证明SLVERR。"""
    text = str(error)
    attrs = getattr(error, "getAttributes", None)
    if callable(attrs):
        data = attrs()
        if type(data) is dict and type(data.get("Format")) is str:
            text = data["Format"]
    if re.fullmatch(r"(?:AXI transaction failed: )?SLVERR", text):
        return "SLVERR"
    if re.fullmatch(r"(?:AXI transaction failed: )?DECERR", text):
        return "DECERR"
    return "UNKNOWN"


class JtagController:
    """消费总控已连接localhost3121的会话；不start/kill/disconnect任何外部服务。"""
    def __init__(self, session, bindings, evidence_dir):
        self.session, self.bindings = session, copy.deepcopy(bindings)
        self.binding_identity = json.dumps(self.bindings, ensure_ascii=False, sort_keys=True)
        self.run = exact_path(evidence_dir, directory=True)
        require(not any(p.name.casefold() in ("jtag_calls.jsonl", "jtag_result.json") for p in self.run.iterdir()), "证据路径已存在")
        self.log = (self.run / "jtag_calls.jsonl").open("x", encoding="utf-8", newline="\n")
        self.failed, self.targets, self.selected, self.owned_bps = False, {}, {}, []
        self.initialized, self.configured, self.app_running, self.cpu0_touched = False, False, False, False
        self.postconfigured = False
        self.record = {"schema_version": 1, "status": "IN_PROGRESS", "cold_lifecycle_proven": False,
                       "hardware_execution": "REQUESTED_BY_CALLER", "bindings": self.bindings, "calls": [], "cleanup_errors": [],
                       "limitations": ["调试system复位不证明物理POR或旧AXI生命周期结束。", "CPU1门禁为离散观测。",
                                       "SDK通用DAP错误不证明SLVERR；需要明确原响应。", "峰值内存未测。"]}
        try:
            self.peer = dict(session._curchan_obj.remote_peer.attrs)
            require(self.peer.get("TransportName") == "TCP" and self.peer.get("Host") in ("localhost", "127.0.0.1") and
                    self.peer.get("Port") == "3121", "必须借用总控连接的localhost:3121会话")
            self.record["borrowed_session_peer"] = self.peer
            self.verify_bindings()
        except BaseException:
            self.log.close()
            raise

    def verify_bindings(self):
        """全部实际产物/源码须由总控选定；不接受伪造review角色字段。"""
        require(json.dumps(self.bindings, ensure_ascii=False, sort_keys=True) == self.binding_identity, "运行期间禁止更换固定输入绑定")
        require(type(self.bindings) is dict and {"init_elf", "app_elf", "xsa", "bit", "csr_source", "interface", "sdk_target", "tool_source", "elf_parser", "delivery_parser", "transport_source"} <= set(self.bindings), "缺少部署绑定")
        for binding in self.bindings.values():
            bound_bytes(binding)
        require(exact_path(self.bindings["tool_source"]["path"]) == exact_path(Path(__file__)), "运行工具源码未绑定")
        for key, name in (("elf_parser", "check_s2b_ps_smoke_layout.py"), ("delivery_parser", "check_stage_delivery.py")):
            require(exact_path(self.bindings[key]["path"]) == exact_path(Path(__file__).absolute().parent / name), "运行解析器未绑定")
        require(exact_path(self.bindings["transport_source"]["path"]) == exact_path(Path(transport.__file__)), "实际T15协议解析器未绑定")

    def call(self, name, function, *args, **kwargs):
        """逐次保存SDK真实返回、标准输出、异常和原始上下文，追加即时落盘。"""
        require(not self.log.closed, "控制器已关闭，禁止调用SDK")
        row = {"time_utc8": datetime.now(TZ).isoformat(), "api": name, "args": args, "kwargs": kwargs}
        self.record["calls"].append(row)
        out, err, started = io.StringIO(), io.StringIO(), time.monotonic()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                result = function(*args, **kwargs)
            row.update(status="RETURNED", return_type=type(result).__name__, return_repr=repr(result))
            return result
        except BaseException as error:
            row.update(status="RAISED", exception_type=type(error).__name__, exception_repr=repr(error), traceback=traceback.format_exc())
            attrs = getattr(error, "getAttributes", None)
            if callable(attrs):
                row["native_attributes"] = attrs()
            raise
        finally:
            row.update(elapsed_seconds=time.monotonic() - started, stdout=out.getvalue(), stderr=err.getvalue())
            self.log.write(json.dumps(row, ensure_ascii=False, default=repr) + "\n"); self.log.flush()

    def guarded(self, function):
        """失败后禁止进一步任务；仅允许停止本次运行CPU0及清理自有断点。"""
        require(not self.failed, "控制器已失败，禁止继续")
        try:
            self.verify_bindings()
            return function()
        except BaseException as error:
            self.failed = True
            self.record.update(status="FAILED", error=repr(error), traceback=traceback.format_exc())
            if self.cpu0_touched or self.app_running or self.initialized or self.owned_bps:
                self.fail_stop()
            if isinstance(error, transport.TransportError):
                raise JtagError("真实UART帧校验失败：" + str(error)) from error
            raise

    def state(self, label):
        """只接受SDK已知核状态。"""
        value = self.call(label + ".state", self.targets[label].state)
        require(type(value) is str and (value == "Running" or value.startswith("Stopped")), "未知核状态")
        return value

    def gate(self, both=True):
        """写入/继续前核对当前目标链、静止CPU1和JTAG启动模式。"""
        require(dict(self.session._curchan_obj.remote_peer.attrs) == self.peer, "借用会话被重定向")
        current = validate_targets(self.call("session.targets.properties", self.session.targets, "--target_properties"))
        require(all(all(current[name].get(k) == self.selected[name].get(k) for k in IDENTITY_KEYS) for name in NAMES),
                "目标上下文/父链改变，禁止后续操作")
        self.refresh_targets(current)
        require(self.state("cpu1").startswith("Stopped"), "CPU1未停止")
        if both:
            require(self.state("cpu0").startswith("Stopped"), "CPU0未停止")
        require(self.words(0xF800025C, 1)[0] == 0, "BOOT_MODE不是JTAG=0")

    def refresh_targets(self, selected):
        """仅用当前枚举ID调用公开选择器；实际对象必须精确绑定固定上下文及本会话。"""
        targets = {}
        for label, name in zip(("apu", "cpu0", "cpu1", "fpga"), NAMES):
            row = selected[name]
            obj = self.call("session.targets." + label, self.session.targets, id=row["target_id"])
            require(vars(obj).get("_ctx") == row["target_ctx"] and vars(obj).get("_id") == row["target_id"] and
                    vars(obj).get("_name") == name and vars(obj).get("session") is self.session and
                    self.session._curtarget is obj, "SDK对象不符合当前上下文或会话")
            targets[label] = obj
        self.targets, self.selected = targets, selected

    def select_and_gate(self):
        """首次仅枚举和只读门禁，Running时拒绝，不自行停止旧应用。"""
        def action():
            self.refresh_targets(validate_targets(self.call("session.targets.properties", self.session.targets, "--target_properties")))
            self.gate()
            self.record["targets"] = self.selected
            return self.selected
        return self.guarded(action)

    def words(self, address, count):
        """在APU memory上下文直接mrd，不选CPU，保存全字节读回。"""
        value = self.call("apu.mrd", self.targets["apu"].mrd, "--value", address=address, size=count, word_size=4)
        rows = [value] if count == 1 else value
        require(type(rows) is list and len(rows) == count and all(type(v) is int and 0 <= v <= 0xFFFFFFFF for v in rows), "DAP读回类型/长度错误")
        self.record.setdefault("readbacks", []).append({"address": address, "words": rows,
                                                       "raw_le_hex": struct.pack("<" + "I" * count, *rows).hex()})
        return rows

    def system_reset_stop(self, cold_basis):
        """只执行SDK支持system-stop；外部统一冷生命周期事实不能由此API推断。"""
        def action():
            require(not self.initialized and not self.configured and not self.app_running, "部署已开始，禁止复位回绕")
            raw = bound_bytes(cold_basis)
            require(raw, "冷恢复依据为空")
            self.gate()
            before = {"boot_mode": self.words(0xF800025C, 1)[0], "reboot_status": self.words(0xF8000258, 1)[0],
                      "ocm_cfg": self.words(0xF8000910, 1)[0], "cpu0_pc": self.pc(), "cpu1_pc": self.pc("cpu1")}
            self.call("apu.rst.system.stop", self.targets["apu"].rst, "--stop", type="system")
            self.gate()
            after = {"boot_mode": self.words(0xF800025C, 1)[0], "reboot_status": self.words(0xF8000258, 1)[0],
                     "ocm_cfg": self.words(0xF8000910, 1)[0], "cpu0_pc": self.pc(), "cpu1_pc": self.pc("cpu1")}
            self.record["system_reset"] = {"basis": cold_basis, "cold_lifecycle_proven": False,
                                            "before": before, "after": after,
                                            "meaning": "TCF XilinxReset system-stop实际执行；总控结合官方non-POR范围与实测另行判断统一冷生命周期。"}
            self.observe_config_status("after_system_reset", 0)
        return self.guarded(action)

    def observe_config_status(self, phase, expected_eos):
        """只调用已绑定Target方法；原始输出始终由call保存，拒绝state推断。"""
        observation = {"phase": phase, "expected_eos": expected_eos, "status": "IN_PROGRESS",
                       "call_index": len(self.record["calls"])}
        self.record.setdefault("configuration_observations", []).append(observation)
        try:
            value = self.call("fpga.config_status." + phase, self.targets["fpga"].fpga, "--config_status")
            row = self.record["calls"][-1]
            observation.update(parse_config_status(value, row["stdout"], row["stderr"]))
            require(observation["eos"] == expected_eos, "CONFIG_STATUS EOS实际观测不符：" + phase)
            observation["status"] = "PASS"
        except BaseException as error:
            observation.update(status="FAILED", error=repr(error))
            raise

    def pc(self, label="cpu0"):
        """按官方rrd的nvlist返回严格读取32位PC，原始输出由call完整保存。"""
        require(label in ("cpu0", "cpu1"), "PC核标签错误")
        value = self.call(label + ".rrd.pc", self.targets[label].rrd, "--nvlist", reg="pc")
        require(type(value) is dict and set(value) == {"pc"} and
                type(value["pc"]) is int and 0 <= value["pc"] <= 0xFFFFFFFF,
                "PC结构化返回类型/字段/32位范围错误")
        return value["pc"]

    def add_bp(self, address):
        """包括部分失败新增对象，只登记和移除本控制器拥有的断点。"""
        before = dict(self.session._bptable)
        try:
            bp = self.call("cpu0.bpadd", self.targets["cpu0"].bpadd, addr=f"0x{address:08X}", type="hw")
        finally:
            added = [obj for key, obj in self.session._bptable.items() if key not in before]
            for obj in added:
                if not any(obj is existing for existing in self.owned_bps):
                    self.owned_bps.append(obj)
        require(len(added) == 1 and bp is added[0], "新增断点对象不明确")
        self.bp_hits(bp, address)
        return bp

    def bp_hits(self, bp, address):
        """要求断点安装在实际CPU0且原生HitCount可用。"""
        value = self.call("bp.status", bp.status)
        cpu_id = self.selected[NAMES[1]]["target_id"]
        require(type(value) is tuple and len(value) == 2 and type(value[0]) is str and type(value[1]) is dict and
                set(value[1]) == {cpu_id}, "断点状态不是当前唯一CPU0")
        row = value[1][cpu_id]
        require(type(row) is dict and "Error" not in row and type(row.get("Address")) is str and
                re.fullmatch(r"0x[0-9a-fA-F]+", row["Address"]) and int(row["Address"], 16) == address and
                type(row.get("HitCount")) is int and row["HitCount"] >= 0, "断点未安装或命中字段错误")
        return row["HitCount"]

    def remove_owned(self):
        """独立尝试清理每个自有对象，保留失败，不删除共享会话的其他断点。"""
        for bp in list(self.owned_bps):
            try:
                self.call("owned.bp.remove", bp.remove)
                self.owned_bps.remove(bp)
            except BaseException as error:
                self.record["cleanup_errors"].append(repr(error))

    def fail_stop(self):
        """失败后只停止本次可能运行的CPU0，CPU1不resume/reset。"""
        if "cpu0" in self.targets:
            try:
                if self.state("cpu0") == "Running":
                    self.call("cpu0.stop.failure", self.targets["cpu0"].stop)
                require(self.state("cpu0").startswith("Stopped"), "失败后的CPU0未停止")
            except BaseException as error:
                self.record["cleanup_errors"].append(repr(error))
        self.remove_owned()

    def _postconfig(self, basis):
        """EOS1后、app前复现已绑定生成表；失败只允许同身份下已解锁SLCR重锁。"""
        observation = {"status": "IN_PROGRESS", "basis": basis, "steps": [], "cleanup": []}
        self.record["postconfiguration"] = observation
        unlock_attempted = False
        def write(label, address, value):
            self.verify_bindings(); self.gate()
            self.call("apu.mwr.postconfig." + label, self.targets["apu"].mwr, "--bypass_cache_synq",
                      address=address, size=1, word_size=4, words=[value])
        def clock_snapshot(label, table):
            clock, pll = self.words(FPGA0_CLOCK, 1)[0], self.words(PLL_STATUS, 1)[0]
            snapshot = {"label": label, "clock_word": clock, "pll_word": pll,
                        "clock_mask": table["clock"][2], "clock_expected": table["clock"][3],
                        "pll_masks": table["pll_masks"]}
            observation.setdefault("clock_observations", []).append(snapshot)
            require(clock & snapshot["clock_mask"] == snapshot["clock_expected"], "FPGA0 clock生成参数读回不符")
            require(all(pll & mask == mask for mask in table["pll_masks"]), "PLL锁定位读回不符")
        try:
            require(self.initialized and self.configured and not self.postconfigured and not self.app_running and
                    self.record["configuration_observations"][-1]["phase"] == "after_full_bit" and
                    self.record["configuration_observations"][-1]["status"] == "PASS" and
                    self.record["configuration_observations"][-1]["eos"] == 1, "postconfig缺少本次EOS1前置事实")
            self.verify_bindings(); self.gate()
            revision = self.words(PS_VERSION, 1)[0]
            nibble = (revision >> 28) & 0xF
            branch = "1_0" if nibble == 0 else "2_0" if nibble == 1 else "3_0"
            table = basis["tables"][branch]
            observation["silicon"] = {"address": PS_VERSION, "word": revision, "nibble": nibble, "branch": branch}
            before = {"locksta": self.words(SLCR_LOCKSTA, 1)[0], "level_shifter": self.words(LEVEL_SHIFTER, 1)[0],
                      "fpga_reset": self.words(FPGA_RESET, 1)[0]}
            observation["before"] = before
            clock_snapshot("before_unlock", table)
            require(before["locksta"] & 1 == 1, "postconfig前SLCR未锁定，不能取得解锁所有权")
            # 不读取write-only LOCK/UNLOCK；实际状态由LOCKSTA bit0核验。
            self.verify_bindings(); self.gate(); unlock_attempted = True
            write("unlock", SLCR_UNLOCK, table["operations"][0][2])
            self.verify_bindings(); self.gate()
            unlocked = self.words(SLCR_LOCKSTA, 1)[0]
            observation["steps"].append({"operation": "unlock", "locksta": unlocked})
            require(unlocked & 1 == 0, "SLCR解锁LOCKSTA读回不符")
            for operation, address, mask, value in table["operations"][1:3]:
                self.verify_bindings(); self.gate()
                old = self.words(address, 1)[0]
                expected = (old & (~mask & 0xFFFFFFFF)) | (value & mask)
                step = {"operation": operation, "address": address, "mask": mask, "value": value,
                        "before": old, "expected": expected, "status": "IN_PROGRESS"}
                observation["steps"].append(step)
                write("level_shifter" if address == LEVEL_SHIFTER else "fpga_reset", address, expected)
                self.verify_bindings(); self.gate()
                actual = self.words(address, 1)[0]
                step.update(after=actual, status="PASS" if actual == expected else "FAILED")
                require(actual == expected, "postconfig完整RMW读回不符")
            write("lock", SLCR_LOCK, table["operations"][3][2])
            self.verify_bindings(); self.gate()
            locked = self.words(SLCR_LOCKSTA, 1)[0]
            observation["steps"].append({"operation": "lock", "locksta": locked})
            require(locked & 1 == 1, "SLCR重锁LOCKSTA读回不符")
            self.verify_bindings(); self.gate()
            clock_snapshot("after_lock", table)
            observation["cold_csr"] = self.cold_idle("postconfig_before_app")
            # 核对T11真实cold reset默认；已有cache/异常命令的门禁语义不由此扩展。
            defaults = {0x014: 0, 0x018: 0, 0x01C: transport.INPUT_BYTES, 0x020: 0x00100000,
                        0x024: transport.WEIGHT_BYTES, 0x028: 0, 0x02C: 0, 0x05C: 0, 0x060: 0,
                        0x064: 0, 0x06C: 0, 0x070: 0, 0x074: 0}
            observation["cold_reset_defaults"] = {"expected": defaults,
                "actual": {address: observation["cold_csr"][address] for address in defaults}}
            require(observation["cold_reset_defaults"]["actual"] == defaults, "app前CSR不是本次cold reset默认")
            self.gate()
            self.postconfigured = True
            observation["status"] = "PASS"
        except BaseException as error:
            observation.update(status="FAILED", error=repr(error), traceback=traceback.format_exc())
            if unlock_attempted:
                cleanup = {"status": "IN_PROGRESS"}
                observation["cleanup"].append(cleanup)
                try:
                    # 原门禁仍必须成立；不强制访问、不重新解锁，不以清理覆盖原异常。
                    self.verify_bindings(); self.gate()
                    locksta = self.words(SLCR_LOCKSTA, 1)[0]
                    cleanup["before_locksta"] = locksta
                    if locksta & 1 == 0:
                        write("cleanup_lock", SLCR_LOCK, 0x767B)
                        cleanup["after_locksta"] = self.words(SLCR_LOCKSTA, 1)[0]
                        require(cleanup["after_locksta"] & 1 == 1, "失败清理SLCR未重锁")
                        cleanup["status"] = "RELOCKED"
                    else:
                        cleanup["status"] = "ALREADY_LOCKED"
                except BaseException as cleanup_error:
                    cleanup.update(status="FAILED", error=repr(cleanup_error), traceback=traceback.format_exc())
                    self.record["cleanup_errors"].append(repr(cleanup_error))
            raise

    def deploy(self):
        """OCM init→EOS1→生成postconfig及冷CSR→DDR app，CPU1始终不继续。"""
        def action():
            require(not self.initialized and not self.configured and not self.app_running, "禁止重复部署")
            require("system_reset" in self.record and any(row["phase"] == "after_system_reset" and
                    row["status"] == "PASS" and row.get("eos") == 0
                    for row in self.record.get("configuration_observations", [])),
                    "部署前必须保存本控制器system-stop及实际EOS0观测")
            basis = postconfig_basis(bound_bytes(self.bindings["xsa"]))
            self.record["postconfig_basis"] = basis
            entry, symbols = init_layout(bound_bytes(self.bindings["init_elf"]))
            try:
                from .check_s2b_ps_smoke_layout import parse_elf
            except ImportError:
                from check_s2b_ps_smoke_layout import parse_elf
            app = parse_elf(bound_bytes(self.bindings["app_elf"]))
            require(0x100000 <= app["entry"] < 0x1100000, "app DDR入口不符")
            loads = [p for p in app["programs"] if p["type"] == 1 and p["memory_size"]]
            require(loads, "app缺少LOAD")
            for p in loads:
                in_app = 0x100000 <= p["physical"] and p["physical"] + p["memory_size"] <= 0x1100000
                arena_noload = p["physical"] == 0x10000000 and p["memory_size"] == 0x2000000 and p["file_size"] == 0
                require(p["virtual"] == p["physical"] and (in_app or arena_noload), "app LOAD越界或arena包含下载数据")
            self.record["init_symbols"] = symbols
            self.gate()
            self.cpu0_touched = True
            self.call("cpu0.dow.init", self.targets["cpu0"].dow, file=self.bindings["init_elf"]["path"], auto_stop=True, set_entry=True)
            self.gate(); require(self.pc() == entry, "init入口PC不匹配")
            ready_address, fail_address = symbols["s2b_ps_init_ready"], symbols["s2b_ps_init_fail"]
            ready, fail = self.add_bp(ready_address), self.add_bp(fail_address)
            require(self.bp_hits(ready, ready_address) == self.bp_hits(fail, fail_address) == 0, "新断点已有命中")
            self.verify_bindings(); self.gate()
            self.call("cpu0.con.init", self.targets["cpu0"].con, "--block", timeout=30)
            self.gate()
            require(self.pc() == ready_address and self.bp_hits(ready, ready_address) > 0 and self.bp_hits(fail, fail_address) == 0,
                    "init ready/fail/PC不符")
            require(self.words(symbols["s2b_ps_init_result"], 1) == [2] and self.words(symbols["s2b_ps_init_return"], 1) == [0],
                    "INIT_RESULT/原返回码不符")
            self.initialized = True
            self.record["initialization"] = {"status": "READY_RESULT2_RETURN0", "ready_address": ready_address,
                                              "result": 2, "return_code": 0}
            mode_word = self.words(DDRC_MODE_STATUS, 1)[0]
            self.record["ddrc_observation"] = {"address": DDRC_MODE_STATUS, "word": mode_word,
                                               "word_hex": f"0x{mode_word:08X}", "operating_mode": mode_word & 7,
                                               "status": "PASS" if mode_word & 7 == 1 else "FAILED"}
            require(mode_word & 7 == 1, "DDRC operating_mode不是normal=1，禁止PL/app下载")
            self.remove_owned(); require(not self.owned_bps and not self.record["cleanup_errors"], "自有断点清理失败")
            self.verify_bindings(); self.gate()
            self.call("fpga.full.compatibility_default", self.targets["fpga"].fpga, file=self.bindings["bit"]["path"])
            self.observe_config_status("after_full_bit", 1)
            self.configured = True
            self._postconfig(basis)
            self.verify_bindings(); self.gate()
            require(self.postconfigured and self.record["postconfiguration"]["status"] == "PASS", "postconfig未完成，禁止app")
            self.call("cpu0.dow.app", self.targets["cpu0"].dow, file=self.bindings["app_elf"]["path"], auto_stop=True, set_entry=True)
            self.gate()
            require(0x100000 <= app["entry"] < 0x1100000 and self.pc() == app["entry"], "app DDR入口PC不符")
            self.app_running = True
            self.call("cpu0.con.app", self.targets["cpu0"].con)
            self.gate(both=False)
            require(self.state("cpu0") == "Running", "app未运行")
            self.record["deployment"] = "INIT_FULL_BIT_APP_SAVED_UART_ACCEPTANCE_PENDING"
        return self.guarded(action)

    def full_csr(self):
        """一次完整CSR快照；使用连续DAP读取减少SDK调用。"""
        values = self.words(CSR_BASE + 0x00C, 27)
        return {0: self.words(CSR_BASE, 1)[0], 4: self.words(CSR_BASE + 4, 1)[0],
                **{0x00C + i * 4: value for i, value in enumerate(values)}}

    def stable_csr(self, label):
        """两份完整CSR快照必须逐字一致；包括错误、配置、epoch、frame、拒绝和账本。"""
        first, second = self.full_csr(), self.full_csr()
        self.record.setdefault("stable_csr", []).append({"label": label, "first": first, "second": second})
        require(first == second, "完整CSR快照正在变化：" + label)
        require(first[0] == 0x53324250 and first[4] == 0x100, "CSR ID/ABI不匹配")
        return first

    def cold_idle(self, label):
        """每次cache动作独立证明冷epoch0、IDLE/ownerPS/head0/账本0，不能只凭CPU静止。"""
        self.verify_bindings(); self.gate(both=False)
        snapshot = self.stable_csr(label)
        require(snapshot[0x00C] == 0x400 and snapshot[0x010] == 0 and snapshot[0x050] == snapshot[0x054] == 0 and
                snapshot[0x058] == 0 and snapshot[0x068] == 0, "CACHE_PROBE需要稳定冷IDLE/epoch0/ownerPS/账本0")
        return snapshot

    def check_wire(self, wire):
        """只接受实际T15派生会话；调用方bool、bytes、字典或自定义callback均不是接收证据。"""
        require(type(wire) is JtagWireSession and not wire.failed, "必须使用未失败的JtagWireSession实际UART会话")

    def cache_probe(self, wire, cpu_seed, dap_seed):
        """自行发送两phase实际OP4并解析CRC/seq/frame；DAP维护前后核对冷IDLE。"""
        def action():
            self.check_wire(wire)
            require(self.app_running, "需要本次已运行的应用")
            cpu_words, dap_words = pattern(cpu_seed), pattern(dap_seed)
            require(cpu_seed != dap_seed, "两phase种子必须不同")
            require(wire.epoch == 0 and wire.abort_pending is None and not wire.sent_requests, "cache必须在本次UART尚未LOAD/START前执行")
            self.cold_idle("before_phase0")
            receipts = []
            def phase(number):
                payload = struct.pack("<III", number, cpu_seed, dap_seed)
                request, header = transport.make_request(transport.OP_CACHE_PROBE, wire.last_sequence + 1, 0, payload)
                self.call("wire.OP4.send", wire.send, request, header, payload, {"kind": "cache_probe", "phase": number})
                receipt = self.call("wire.OP4.receive_actual", wire.receipt, request)
                self.record.setdefault("uart_receipts", []).append(receipt)
                receipts.append(receipt)
                meta = receipt["meta"]
                require(meta["epoch"] == 0 and meta["phys_status"] == 0x400 and meta["error_code"] == 0 and
                        meta["response_code"] == 0 and meta["index"] == 0 and meta["total"] == 1, "OP4实际UART不是冷IDLE成功帧")
                return meta["probe_bytes"]
            raw0 = phase(0)
            require(type(raw0) is bytes and raw0 == struct.pack("<64I", *cpu_words), "CPU phase0原始256B/seed错误")
            self.cold_idle("after_phase0_before_dap_read")
            require(self.words(PROBE_ADDRESS, PROBE_WORDS) == cpu_words, "CPU Flush后DAP全量读回错误")
            self.cold_idle("before_dap_write")
            self.call("apu.mwr.cache_probe.bypass", self.targets["apu"].mwr, "--bypass_cache_synq",
                      address=PROBE_ADDRESS, size=PROBE_WORDS, word_size=4, words=dap_words)
            self.cold_idle("after_dap_write")
            require(self.words(PROBE_ADDRESS, PROBE_WORDS) == dap_words, "DAP写入后全量读回错误")
            self.cold_idle("before_phase1")
            raw1 = phase(1)
            require(type(raw1) is bytes and raw1 == struct.pack("<64I", *dap_words), "CPU Invalidate后原始256B/seed错误")
            self.cold_idle("after_phase1")
            self.record["cache_probe"] = {"status": "CROSS_MASTER_256_BYTES_MATCHED", "address": PROBE_ADDRESS,
                                           "cpu_seed": cpu_seed, "dap_seed": dap_seed, "phase0_raw_hex": raw0.hex(), "phase1_raw_hex": raw1.hex(),
                                           "wire_session_identity": {"python_object_id": id(wire), "transport_source_sha256": self.bindings["transport_source"]["sha256"],
                                               "rx_file": str(getattr(wire.rx_file, "name", "MEMORY_MOCK")), "tx_header_file": str(getattr(wire.tx_header_file, "name", "MEMORY_MOCK"))},
                                           "phase0_receipt": receipts[0], "phase1_receipt": receipts[1]}
            return self.record["cache_probe"]
        try:
            return self.guarded(action)
        except BaseException:
            if type(wire) is JtagWireSession:
                wire.failed = True
                self.record["failed_uart_receipt_attempts"] = copy.deepcopy(wire.receipt_attempts)
            raise

    def csr_snapshot(self):
        """状态及账本必须稳定；不能在自然推进的任务上声称零额外副作用。"""
        return {offset: self.words(CSR_BASE + offset, 1)[0] for offset in CSR_SNAPSHOT}

    def negative_start(self, kind, scene_binding):
        """只在总控选择的静止场景中注入；未知原生总线异常明确阻断。"""
        def action():
            require(kind in ("bad_encoding", "busy"), "未知负向场景")
            raw = bound_bytes(scene_binding)
            scene = json.loads(raw.decode("utf-8"))
            require(type(scene) is dict and scene.get("kind") == kind and type(scene.get("expected_snapshot")) is dict, "场景依据格式不符")
            self.gate()
            require(self.words(CSR_BASE, 1) == [0x53324250] and self.words(CSR_BASE + 4, 1) == [0x100], "CSR ID/ABI不符")
            before = self.csr_snapshot()
            require(before == self.csr_snapshot(), "场景正在推进，不能证明零额外副作用")
            require({str(k): v for k, v in before.items()} == scene["expected_snapshot"], "实际CSR不符合总控安全场景")
            phase = before[0x00C] & 7
            if kind == "busy":
                require(phase in (1, 2, 3) and before[0x00C] & 0x100, "busy场景未被PL拥有")
            else:
                require(phase == 0 and before[0x00C] == 0x400 and before[0x068] == 0, "非法编码场景不是安全IDLE")
            response = "OKAY"
            try:
                self.call("apu.mwr.negative_start", self.targets["apu"].mwr, "--bypass_cache_synq",
                          address=CSR_BASE + 8, size=1, word_size=4, words=[3 if kind == "bad_encoding" else 1])
            except Exception as error:
                response = bus_error_kind(error)
            after = self.csr_snapshot()
            reject = self.words(CSR_BASE + 0x064, 1)[0]
            self.record.setdefault("negative_start", []).append({"kind": kind, "scene_binding": scene_binding,
                "native_response": response, "before": before, "after": after, "last_reject": reject})
            require(after == self.csr_snapshot() == before, "拒绝写导致状态/epoch/owner/ledger/参数/故障变化")
            require(reject == (5 if kind == "bad_encoding" else 1), "LAST_REJECT不符合规格")
            require(response == "SLVERR", "SLVERR_UNPROVEN：原生响应=" + response)
            self.gate()
            return {"status": "EXPECTED_SLVERR_REJECTION_SAVED", "kind": kind}
        return self.guarded(action)

    def dap_abort(self, wire, request):
        """自行消费真实WAIT帧再合法ABORT；真实final与两份一致CSR吻合后才确认。"""
        def action():
            self.check_wire(wire)
            require(self.app_running, "ABORT需要本控制器本次已部署运行的应用")
            require(type(request) is transport.Header and request.op == transport.OP_DIAG and
                    request.sequence == wire.last_sequence and request.sequence in wire.sent_requests, "ABORT必须绑定最后实际发送的DIAG请求")
            mode, core, drain = struct.unpack("<III", wire.sent_requests[request.sequence][2])
            require(mode == 2 and core > 0 and drain > 0, "ABORT请求不是合法mode2")
            ready = self.call("wire.abort.receive_ready_actual", wire.receipt, request, abort_ready=True)
            self.record.setdefault("uart_receipts", []).append(ready)
            ready_meta, epoch = ready["meta"], ready["meta"]["epoch"]
            self.gate(both=False)
            before = self.full_csr()
            event = {"requested_epoch": epoch, "before": before, "response": "NOT_SENT", "status": "IN_PROGRESS"}
            self.record.setdefault("dap_abort", []).append(event)
            require(before[0] == 0x53324250 and before[4] == 0x100 and
                    ((before[0x054] << 32) | before[0x050]) == epoch and before[0x00C] & 7 in (1, 2) and
                    before[0x00C] & 0x100 and not before[0x00C] & (0x400 | 0x800 | 0x200 | 0x2000) and
                    before[0x010] == ready_meta["error_code"] == 0 and before[0x058] == request.frame,
                    "ABORT前已终态/恢复/frame或epoch错误；不写COMMAND")
            try:
                self.call("apu.mwr.legal_abort", self.targets["apu"].mwr, "--bypass_cache_synq",
                          address=CSR_BASE + 8, size=1, word_size=4, words=[2])
                event["response"] = "SDK_RETURNED_WITHOUT_EXCEPTION"
            except Exception as error:
                event.update(response=bus_error_kind(error), exception_repr=repr(error), status="WRITE_EXCEPTION")
                event["after"] = self.stable_csr("abort_write_exception")
                raise JtagError("ABORT原生写异常/终态race；保留诊断且不继续任务") from error
            receipt = self.call("wire.abort.receive_final_actual", wire.receipt, request)
            self.record["uart_receipts"].append(receipt)
            final_meta = receipt["meta"]
            self.gate(both=False)
            final = self.stable_csr("abort_final_after_uart"); event["after"] = final
            require(((final[0x054] << 32) | final[0x050]) == epoch == final_meta["epoch"] and
                    final[0x00C] == final_meta["phys_status"] == 0xC05 and final[0x010] == final_meta["error_code"] == 8 and
                    final[0x064] == final_meta["last_reject"] and final[0x058] == request.frame and final[0x068] == 0 and
                    final_meta["response_code"] == 0 and final_meta["index"] == 0 and final_meta["total"] == 1,
                    "ABORT未达到真实ERROR_SAFE/code8/账本零；不得ACK或重用")
            event["status"] = "ACTUAL_ERROR_SAFE_ABORTED_SAVED"
            return event
        try:
            return self.guarded(action)
        except BaseException:
            if type(wire) is JtagWireSession:
                wire.failed = True
                self.record["failed_uart_receipt_attempts"] = copy.deepcopy(wire.receipt_attempts)
            raise

    def close(self):
        """保存结果与原生日志，正常关闭不停止已部署应用，也不释放外部会话。"""
        if self.log.closed:
            return
        self.remove_owned()
        if self.record["cleanup_errors"]:
            self.failed = True; self.record["status"] = "FAILED"
        if not self.failed:
            self.record["status"] = "API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING"
        self.record["finished_at_utc8"] = datetime.now(TZ).isoformat()
        self.log.close()
        with (self.run / "jtag_result.json").open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(self.record, stream, ensure_ascii=False, indent=2, default=repr); stream.write("\n")
