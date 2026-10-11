#!/usr/bin/env python3
"""候选UART独立端序/CRC/负例、真实C hostmock和109个冻结C解码回归。"""
from __future__ import annotations

import ctypes
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
import zlib

try:
    from . import s2b_board_transport as transport
except ImportError:
    import s2b_board_transport as transport

ROOT = Path(__file__).absolute().parents[1]
GCC = Path(r"D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\gcc.exe")
ASSETS = Path(r"D:\FPGA_Competition\report\evidence\S2A-T68\candidate8x8_109_20261006_130252")


def bit_crc(raw):
    """独立逐bit IEEE CRC手算实现，以标准123456789向量约束。"""
    crc = 0xFFFFFFFF
    for value in raw:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ (0xEDB88320 if crc & 1 else 0)
    return crc ^ 0xFFFFFFFF


def response_for(request, *, epoch=1, index=0, code=0, status=0xE04, heads=True, detection=None):
    """手工构造独立响应，CPU执行与黄金推理并未由此证明。"""
    detections = [] if detection is None else [detection]
    payload = struct.pack("<Q8I", epoch, status, 0, 0, len(detections), len(detections), index, request.repeat, code)
    if heads:
        payload += bytes([0x81]) * 5070 + bytes([0x7F]) * 20280
        for box in detections:
            payload += struct.pack("<ii5d", *box)
    header = struct.pack("<4sHH7I", b"S2BU", 1, request.op | 0x8000, request.sequence,
                         request.frame + index, request.width, request.height, request.repeat, len(payload), bit_crc(payload))
    return header + struct.pack("<I", bit_crc(header)), payload


class FragmentSerial:
    """模拟有界分片、空读和短写，不启动实际串口。"""
    def __init__(self, incoming=b"", step=13):
        self.incoming, self.written, self.step = bytearray(incoming), bytearray(), step
    def read(self, length):
        count = min(length, self.step, len(self.incoming))
        result = bytes(self.incoming[:count]); del self.incoming[:count]
        return result
    def write(self, raw):
        count = min(len(raw), self.step); self.written.extend(raw[:count]); return count


class FramingTests(unittest.TestCase):
    """对真实public解析API注入协议错误和独立手算响应。"""
    def setUp(self):
        self.payload = struct.pack("<II", 0xFFFFFFFF, 12345) + bytes(transport.INPUT_BYTES)
        self.request, self.header = transport.make_request(2, 2, 7, self.payload, width=1440, height=1920)

    def test_ieee_crc_known_answer_and_header_offsets(self):
        self.assertEqual(bit_crc(b"123456789"), 0xCBF43926)
        self.assertEqual(zlib.crc32(b"123456789"), 0xCBF43926)
        self.assertEqual(len(self.header), 40)
        self.assertEqual(self.header[:16], b"S2BU\x01\x00\x02\x00\x02\x00\x00\x00\x07\x00\x00\x00")
        self.assertEqual(self.header[28:32], bytes.fromhex("08ec0700"))
        self.assertEqual(struct.unpack_from("<I", self.header, 36)[0], bit_crc(self.header[:36]))
        self.assertEqual(transport.Header.unpack(self.header), self.request)

    def test_header_corruption_truncation_magic_version(self):
        for index in range(40):
            raw = bytearray(self.header); raw[index] ^= 1
            with self.subTest(index=index), self.assertRaises(transport.TransportError):
                transport.Header.unpack(raw)
        for raw in (self.header[:-1], self.header + b"x"):
            with self.assertRaises(transport.TransportError): transport.Header.unpack(raw)

    def test_request_bad_length_deadline_dimensions_repeat_and_frame(self):
        for kwargs in ({"width": 0}, {"height": 65536}, {"repeat": 0}, {"repeat": 1001}, {"repeat": 1000, "frame": 0xFFFFFFFF}):
            current = {"frame": 7, "width": 1440, "height": 1920, "repeat": 1}; current.update(kwargs)
            with self.assertRaises(transport.TransportError): transport.make_request(2, 2, current.pop("frame"), self.payload, **current)
        for raw in (self.payload[:-1], struct.pack("<II", 0, 1) + bytes(transport.INPUT_BYTES)):
            with self.assertRaises(transport.TransportError): transport.make_request(2, 2, 7, raw, width=1440, height=1920)
        for seq in (0, 0xFFFFFFFF, True):
            with self.assertRaises(transport.TransportError): transport.make_request(2, seq, 7, self.payload, width=1440, height=1920)

    def test_complete_int8_heads_and_binary64_box(self):
        expected = (1, 6, 0.75, 0.125, 0.25, 0.5, 0.875)
        header, payload = response_for(self.request, detection=expected)
        meta, heads, boxes = transport.decode_response(header, payload, self.request, 0, 0)
        self.assertEqual(meta["epoch"], 1)
        self.assertEqual(len(heads["head13"]), 5070)
        self.assertEqual(heads["head13"][0], 0x81)
        self.assertEqual(boxes[0], {"class_id": 1, "class_name": "palm", "source_order": 6, "score": .75, "xyxy": [.125, .25, .5, .875]})

    def test_duplicate_epoch_missing_heads_wrong_metadata_and_crc(self):
        header, payload = response_for(self.request)
        for previous in (1, 2, -1):
            with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, self.request, 0, previous)
        for changed in (self.request.__dict__ | {"sequence": 3}, self.request.__dict__ | {"frame": 8}, self.request.__dict__ | {"width": 100}):
            with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, transport.Header(**changed), 0, 0)
        with self.assertRaises(transport.TransportError): transport.decode_response(header, payload[:-1], self.request, 0, 0)
        raw = bytearray(payload); raw[-1] ^= 1
        with self.assertRaises(transport.TransportError): transport.decode_response(header, raw, self.request, 0, 0)
        header, payload = response_for(self.request, heads=False)
        with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, self.request, 0, 0)

    def test_unsafe_and_error_response_never_publish_capture(self):
        for status in (0xD04, 0xE05, 0xF04, 0x1E04, 0x2E04, 0xC04):
            header, payload = response_for(self.request, status=status)
            with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, self.request, 0, 0)
        for code in range(1, 10):
            header, payload = response_for(self.request, code=code, heads=False)
            with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, self.request, 0, 0)

    def test_nonfinite_invalid_class_order_or_zero_area(self):
        for box in ((5, 5, .5, .1, .1, .2, .2), (1, 0, .5, .1, .1, .2, .2),
                    (1, 1, float("nan"), .1, .1, .2, .2), (1, 1, .5, .2, .1, .2, .2)):
            header, payload = response_for(self.request, detection=box)
            with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, self.request, 0, 0)

    def test_fragment_serial_raw_capture_short_write_duplicate_timeout(self):
        header, payload = response_for(self.request)
        stream, rx, tx = FragmentSerial(header + payload), io.BytesIO(), io.BytesIO()
        wire = transport.WireSession(stream, rx, tx, response_timeout=.5)
        meta, _, _ = wire.receive(self.request, 0)
        self.assertEqual(meta["epoch"], 1); self.assertEqual(rx.getvalue(), header + payload)
        request, raw = transport.make_request(4, 1, 0, struct.pack("<III", 0, 1, 2))
        wire.send(request, raw, struct.pack("<III", 0, 1, 2), {"fixture": "手算probe"})
        self.assertEqual(stream.written, raw + struct.pack("<III", 0, 1, 2))
        with self.assertRaises(transport.TransportError): wire.send(request, raw, struct.pack("<III", 0, 1, 2), {})
        with self.assertRaises(transport.TransportError): wire.read_exact(1, -1)

    def test_1000_responses_consecutive_frame_epoch_and_no_duplicates(self):
        request, _ = transport.make_request(2, 2, 0, self.payload, width=416, height=416, repeat=1000)
        for index in range(1000):
            header, payload = response_for(request, epoch=index + 1, index=index)
            meta, _, _ = transport.decode_response(header, payload, request, index, index)
            self.assertEqual(meta["epoch"], index + 1)
        header, payload = response_for(request, epoch=2, index=0)
        with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, request, 1, 1)

    def test_cache_probe_pattern_independent_response(self):
        seed = 0xA5A55A5A
        request, _ = transport.make_request(4, 1, 0, struct.pack("<III", 0, seed, 0x12345678))
        actual = b"".join(struct.pack("<I", seed ^ ((0x9E3779B9 * index) & 0xFFFFFFFF)) for index in range(64))
        self.assertEqual(actual[:8], bytes.fromhex("5a5aa5a5e323923b"))
        payload = struct.pack("<Q8I", 0, 0x400, 0, 0, 0, 0, 0, 1, 0) + actual
        header = transport.Header(0x8004, 1, 0, 0, 0, 1, len(payload), zlib.crc32(payload)).pack()
        meta, _, _ = transport.decode_response(header, payload, request, 0, 0)
        self.assertEqual(meta["probe_bytes"], actual)

    def test_host_frozen_binding_wrong_sha_and_sample_index(self):
        with mock.patch.object(transport, "MODEL_SHA", "0" * 64):
            with self.assertRaises(transport.TransportError): transport.load_assets(ASSETS, [0])
        with self.assertRaises(transport.TransportError):
            transport.verify_build(ROOT / "report/evidence/S2B-T15/unit_build_20261011_r02/build_details.json")
        for index in (-1, 109, True):
            with self.assertRaises(transport.TransportError): transport.load_assets(ASSETS, [index])
        original = transport.digest
        with mock.patch.object(transport, "digest", side_effect=lambda raw: "0" * 64 if len(raw) == transport.INPUT_BYTES else original(raw)):
            with self.assertRaises(transport.TransportError): transport.load_assets(ASSETS, [0])

    def test_banner_identity_limit_and_truncated_response_raw_preserved(self):
        source_sha, xsa_sha = "a" * 64, "b" * 64
        banner = f"S2B-INFERENCE/1 READY SOURCE={source_sha} XSA={xsa_sha} MODEL={transport.MODEL_SHA}\r\n".encode()
        rx = io.BytesIO()
        wire = transport.WireSession(FragmentSerial(banner), rx, io.BytesIO(), response_timeout=.1)
        self.assertEqual(wire.banner(source_sha, xsa_sha)["sha256"], transport.digest(banner))
        self.assertEqual(rx.getvalue(), banner)
        for incoming in (banner.replace(b"SOURCE=a", b"SOURCE=c"), b"X" * 321):
            with self.assertRaises(transport.TransportError):
                transport.WireSession(FragmentSerial(incoming), io.BytesIO(), io.BytesIO(), response_timeout=.1).banner(source_sha, xsa_sha)
        header, payload = response_for(self.request)
        raw = header + payload[:-1]
        rx = io.BytesIO()
        wire = transport.WireSession(FragmentSerial(raw, 4096), rx, io.BytesIO(), response_timeout=.01)
        with self.assertRaises(transport.TransportError): wire.receive(self.request, 0)
        self.assertEqual(rx.getvalue(), raw)
        self.assertEqual(wire.epoch, 0)
        self.assertTrue(wire.failed)
        with self.assertRaises(transport.TransportError): wire.receive(self.request, 0)

    def test_diagnostics_epoch_progress_reserved_status_and_send_header_binding(self):
        request, _ = transport.make_request(3, 1, 7, struct.pack("<III", 1, 100, 100))
        payload = transport.META.pack(1, 0xC05, 3, 0, 0, 0, 0, 1, 0)
        header = transport.Header(0x8003, 1, 7, 0, 0, 1, len(payload), zlib.crc32(payload)).pack()
        wire = transport.WireSession(FragmentSerial(header + payload), io.BytesIO(), io.BytesIO(), response_timeout=.5)
        self.assertEqual(wire.receive(request, 0)[0]["error_code"], 3)
        self.assertEqual(wire.epoch, 1)
        with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, request, 0, 1)
        header, payload = response_for(self.request, status=0x8000E04)
        with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, self.request, 0, 0)
        request, header = transport.make_request(4, 1, 0, struct.pack("<III", 0, 1, 2))
        with self.assertRaises(transport.TransportError): wire.send(request, bytes(40), struct.pack("<III", 0, 1, 2), {})

    def test_abort_two_phases_explicit_ack_and_pending_rejects(self):
        payload = struct.pack("<III", 2, 0xFFFFFFFF, 10000)
        request, header = transport.make_request(3, 1, 200, payload)
        ack_payload = struct.pack("<III", 3, 1, 0)
        ack, _ = transport.make_request(3, 2, 200, ack_payload)
        def packet(head, status, error, code):
            raw = struct.pack("<Q8I", 1, status, error, 0, 0, 0, 0, 1, code)
            prefix = struct.pack("<4sHH7I", b"S2BU", 1, 0x8003, head.sequence, head.frame, 0, 0, 1, len(raw), bit_crc(raw))
            return prefix + struct.pack("<I", bit_crc(prefix)) + raw
        incoming = packet(request, 0x102, 0, 10) + packet(request, 0xC05, 8, 0) + packet(ack, 0x400, 0, 0)
        wire = transport.WireSession(FragmentSerial(incoming), io.BytesIO(), io.BytesIO(), response_timeout=.5)
        wire.send(request, header, payload, {})
        meta, heads, boxes = wire.receive_abort_ready(request)
        self.assertEqual(meta["epoch"], 1); self.assertEqual(wire.epoch, 0); self.assertEqual((heads, boxes), ({}, []))
        with self.assertRaises(transport.TransportError): wire.acknowledge_abort(2)
        other, raw = transport.make_request(3, 2, 201, struct.pack("<III", 0, 0, 0))
        with self.assertRaises(transport.TransportError): wire.send(other, raw, struct.pack("<III", 0, 0, 0), {})
        final, _, _ = wire.receive(request, 0)
        self.assertEqual(final["error_code"], 8); self.assertEqual(wire.abort_pending["phase"], "ACK_REQUIRED")
        self.assertEqual(wire.epoch, 1)
        for wrong_epoch, wrong_frame in ((2, 200), (1, 201)):
            bad_payload = struct.pack("<III", 3, wrong_epoch, 0)
            bad, bad_header = transport.make_request(3, 2, wrong_frame, bad_payload)
            with self.assertRaises(transport.TransportError): wire.send(bad, bad_header, bad_payload, {})
        confirmed, _, _ = wire.acknowledge_abort(2)
        self.assertEqual(confirmed["phys_status"], 0x400); self.assertEqual(wire.epoch, 1)
        self.assertIsNone(wire.abort_pending)
        self.assertEqual(wire.last_sequence, 2)

    def test_abort_ready_wrong_phase_owner_epoch_and_missing_final_failstop(self):
        request, _ = transport.make_request(3, 1, 200, struct.pack("<III", 2, 10000, 10000))
        for status, epoch, code in ((0x102, 1, 10), (0x002, 1, 10), (0x400, 1, 10), (0x102, 2, 10), (0x102, 1, 0)):
            payload = transport.META.pack(epoch, status, 0, 0, 0, 0, 0, 1, code)
            header = transport.Header(0x8003, 1, 200, 0, 0, 1, len(payload), zlib.crc32(payload)).pack()
            if (status, epoch, code) == (0x102, 1, 10):
                with self.assertRaises(transport.TransportError): transport.decode_response(header, payload, request, 0, 0)
                wire = transport.WireSession(FragmentSerial(header + payload), io.BytesIO(), io.BytesIO(), response_timeout=.01)
                wire.receive_abort_ready(request)
                with self.assertRaises(transport.TransportError): wire.receive(request, 0)
                self.assertTrue(wire.failed); self.assertEqual(wire.epoch, 0)
            else:
                wire = transport.WireSession(FragmentSerial(header + payload), io.BytesIO(), io.BytesIO(), response_timeout=.1)
                with self.assertRaises(transport.TransportError): wire.receive_abort_ready(request)
                self.assertTrue(wire.failed); self.assertEqual(wire.epoch, 0)


MOCK_HEADER = r'''/* 测试注入层只用于主机编译，不映射任何真实MMIO或板卡。 */
#define S2B_HEAD13_SCALE 0.24267549589862975
#define S2B_HEAD26_SCALE 0.30223452951025775
static void barrier(void);
static uint32_t csr_read(uint32_t offset);
static void csr_write(uint32_t offset, uint32_t value);
static uint64_t ticks(void);
static uint64_t seconds_ticks(uint32_t seconds);
static void flush_range(uint32_t offset, uint32_t length);
static void invalidate_range(uint32_t offset, uint32_t length);
static int uart_read_one(uint8_t *byte);
static int uart_write_one(uint8_t byte);
static int uart_drain_done(void);
'''

MOCK_HARNESS = r'''/* UART、缓存和CSR行为模型仅检验软件边界，不声明RTL或实物通过。 */
#define S2B_HOST_MOCK
#include "s2b_inference_app.c"
#include <stdlib.h>
#include <fcntl.h>
#include <io.h>
static uint32_t regs[64], physical_status=SAFE_REUSE;
static uint64_t epoch_value, clock_value;
static int pending;
static const char *golden_path;
static const char *dap_scenario;
static int diagnostic_active,diagnostic_status_reads;
static unsigned int sent_total,tx_fail_after=UINT_MAX;
static void barrier(void) { }
static uint64_t ticks(void) { return clock_value++; }
static uint64_t seconds_ticks(uint32_t seconds) { return (uint64_t)seconds * 10000U; }
static uint32_t csr_read(uint32_t offset)
{
    if (offset == 0x00CU) {
        if (diagnostic_active && physical_status == (OWNER_PL|2U) && dap_scenario!=NULL) {
            ++diagnostic_status_reads;
            if (strcmp(dap_scenario,"read_then_terminal")==0 && diagnostic_status_reads==1) {
                /* 状态读返回RUN，返回后真实状态已ERROR_SAFE：复现原裸STR竞态。 */
                physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=5U; pending=0;
                return OWNER_PL|2U;
            }
            return OWNER_PL|2U;
        }
        if (pending > 0) { --pending; return OWNER_PL | 2U; }
        if (physical_status == (OWNER_PL | 2U)) {
            /* 模拟PL在所有权期间写头；文件来自独立CPU黄金，不由应用生成。 */
            if (golden_path!=NULL) {
                FILE *source=fopen(golden_path,"rb");
                if (source==NULL || fseek(source,10772736L,SEEK_SET)!=0 ||
                    fread(arena+0x01A46100U,1U,HEAD13_BYTES,source)!=HEAD13_BYTES ||
                    fseek(source,11361870L,SEEK_SET)!=0 ||
                    fread(arena+0x01AD5E80U,1U,HEAD26_BYTES,source)!=HEAD26_BYTES || fclose(source)!=0) abort();
            }
            physical_status=SAFE_REUSE|TERMINAL|HEAD_VALID|DONE_SAFE;
        }
        return physical_status;
    }
    if (offset == 0x050U) return (uint32_t)epoch_value;
    if (offset == 0x054U) return (uint32_t)(epoch_value>>32);
    return regs[offset/4U];
}
static void csr_write(uint32_t offset, uint32_t value)
{
    if (offset != 8U) { regs[offset/4U]=value; return; }
    if (value == 1U) {
        if (physical_status != SAFE_REUSE) abort();
        ++epoch_value; regs[0x058U/4U]=regs[0x014U/4U];
        if (regs[0x01CU/4U] != INPUT_BYTES) { physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=3U; }
        else { physical_status=OWNER_PL|2U; regs[4]=0U; pending=1; }
        if (regs[0x014U/4U]==200U && dap_scenario!=NULL) {
            diagnostic_active=1; diagnostic_status_reads=0;
            if (regs[0x028U/4U]==1U) { physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=5U; pending=0; }
        }
    } else if (value == 2U) {
        /* CPU应用绝不能通过裸Device写ABORT；真实冻结RTL终态会拒绝SLVERR。 */
        fprintf(stderr,"CPU_BARE_ABORT_STR_FORBIDDEN\n"); exit(86);
    }
    else if (value == 4U) {
        uint64_t ack=((uint64_t)regs[0x060U/4U]<<32)|regs[0x05CU/4U];
        if (ack!=epoch_value || (physical_status&(SAFE_REUSE|TERMINAL))!=(SAFE_REUSE|TERMINAL)) abort();
        fprintf(stderr,"ACK %llu\n",(unsigned long long)epoch_value);
        physical_status=SAFE_REUSE; regs[4]=0U;
    } else abort();
}
static void flush_range(uint32_t offset, uint32_t length)
{
    if (physical_status & OWNER_PL || (offset & 63U) || (length & 63U) || offset+length>ARENA_BYTES) abort();
    fprintf(stderr,"FLUSH %08x %u\n",offset,length);
}
static void invalidate_range(uint32_t offset, uint32_t length)
{
    if (physical_status & OWNER_PL || (offset & 63U) || (length & 63U) || offset+length>ARENA_BYTES) abort();
    fprintf(stderr,"INVALIDATE %08x %u\n",offset,length);
}
static int uart_read_one(uint8_t *byte) { int value=getchar(); if (value==EOF) return 0; *byte=(uint8_t)value; return 1; }
static int uart_write_one(uint8_t byte) { if(sent_total>=tx_fail_after) return 0; ++sent_total; return putchar(byte)!=EOF; }
static int uart_drain_done(void)
{
    int done=fflush(stdout)==0;
    if(done && diagnostic_active && get32(response+36U)==WAIT_DAP_ABORT && dap_scenario!=NULL) {
        /* DAP协同注入在完整UART ready后发生，不执行CPU的MMIO STR。 */
        if(strcmp(dap_scenario,"dap_race")==0 || strcmp(dap_scenario,"original_fault")==0) {
            physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=5U; pending=0;
            regs[0x064U/4U]=4U; fprintf(stderr,"DAP_SLVERR_TERMINAL error=5\n");
        } else if(strcmp(dap_scenario,"done_before_dap")==0) {
            physical_status=SAFE_REUSE|TERMINAL|HEAD_VALID|DONE_SAFE; regs[4]=0U; pending=0;
            regs[0x064U/4U]=4U; fprintf(stderr,"DAP_SLVERR_TERMINAL done\n");
        } else if(regs[0x02CU/4U]==1U) {
            physical_status=OWNER_PL|FAULT_ISOLATED; regs[4]=8U; pending=0;
            fprintf(stderr,"DAP_ABORT_DRAIN_ISOLATED\n");
        } else {
            if(physical_status!=(OWNER_PL|2U)) abort();
            physical_status=SAFE_REUSE|TERMINAL|ERROR_SAFE; regs[4]=8U; pending=0;
            fprintf(stderr,"DAP_ACTUAL_ABORT epoch=%llu\n",(unsigned long long)epoch_value);
        }
    }
    return done;
}
int main(int argc,char **argv)
{
    int count,index;
    /* Windows管道必须使用原字节模式，不能把LF转换成CRLF。 */
    (void)_setmode(_fileno(stdin),_O_BINARY); (void)_setmode(_fileno(stdout),_O_BINARY);
    if (argc!=2 && argc!=3) return 90;
    if (argc==3) golden_path=argv[2];
    dap_scenario=getenv("S2B_MOCK_DAP_SCENARIO");
    if (getenv("S2B_MOCK_TX_FAIL_AFTER")!=NULL) tx_fail_after=(unsigned int)strtoul(getenv("S2B_MOCK_TX_FAIL_AFTER"),NULL,10);
    count=atoi(argv[1]);
    if (crc32_ieee((const uint8_t *)"123456789",9U)!=0xCBF43926U) return 91;
    for(index=0;index<count;++index) {
        if(index==1 && cache_probe_wait && getenv("S2B_MOCK_SKIP_DAP")==NULL) {
            uint32_t item;
            for(item=0U;item<64U;++item) put32(arena+item*4U,cache_dap_seed^(0x9E3779B9U*item));
        }
        if(!service_request()) return 2;
    }
    fprintf(stderr,"MOCK_OK epoch=%llu status=%x sequence=%u diag_pending=%d\n",(unsigned long long)epoch_value,physical_status,next_sequence,diag_ack_pending);
    return 0;
}
'''


class NativeTests(unittest.TestCase):
    """严格编译真实新应用和冻结C参考，并检查软件实例及109个CPU黄金。"""
    @classmethod
    def setUpClass(cls):
        transport.exact_path(GCC)
        cls.directory = Path(tempfile.mkdtemp(prefix="s2b_t15_", dir=ROOT / "tmp/2B/S2B-T15"))
        (cls.directory / "s2b_host_mock.h").write_text(MOCK_HEADER, encoding="utf-8", newline="\n")
        (cls.directory / "mock.c").write_text(MOCK_HARNESS, encoding="utf-8", newline="\n")
        cls.exe = cls.directory / "mock.exe"
        command = [str(GCC), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-I" + str(cls.directory),
                   "-I" + str(ROOT / "vitis"), "-I" + str(ROOT / "verification"), str(cls.directory / "mock.c"),
                   str(ROOT / "verification/s2a_ps_decode_nms_reference.c"), "-o", str(cls.exe), "-lm"]
        env = dict(os.environ, PATH=str(GCC.parent) + os.pathsep + os.environ.get("PATH", ""))
        result = subprocess.run(command, capture_output=True, env=env)
        transport.write_json_new(cls.directory / "compile_record.json", {"command": command, "exit_code": result.returncode,
                                  "stdout": result.stdout.decode("utf-8", errors="replace"), "stderr": result.stderr.decode("utf-8", errors="replace")})
        if result.returncode: raise RuntimeError(f"gcc退出{result.returncode}：" + result.stderr.decode("utf-8", errors="replace"))
        cls.compile_command = command
        cls.case_count = 0

    @classmethod
    def tearDownClass(cls):
        # 缓存与失败原件留给总控核对；本测试不自动删除运行目录。
        pass

    def run_mock(self, requests, count, expected, golden_path=None, environment=None):
        command = [str(self.exe), str(count)]
        if golden_path is not None: command.append(str(golden_path))
        incoming = b"".join(requests)
        started = time.monotonic()
        result = subprocess.run(command, input=incoming, capture_output=True, timeout=30,
                                env=None if environment is None else dict(os.environ, **environment))
        case = transport.new_directory(self.directory / f"mock_case_{self.__class__.case_count:03d}")
        self.__class__.case_count += 1
        (case / "stdout.bin").write_bytes(result.stdout)
        (case / "stderr.log").write_bytes(result.stderr)
        transport.write_json_new(case / "case_result.json", {"command": command, "expected_exit_code": expected,
            "exit_code": result.returncode, "environment_overrides": environment, "elapsed_seconds": time.monotonic() - started,
            "input_bytes": len(incoming), "input_sha256": transport.digest(incoming), "stdout_sha256": transport.digest(result.stdout),
            "stderr_sha256": transport.digest(result.stderr)})
        self.assertEqual(result.returncode, expected, result.stderr.decode("utf-8", errors="replace"))
        return result

    def mode2_fixture(self, core=0xFFFFFFFF, drain=10000):
        """以真实LOAD/RUN建立诊断输入，随后独立DAP测试模型提交/拒绝ABORT。"""
        _, weight, rows = transport.load_assets(ASSETS, [0])
        row = rows[0]; gold = row["golden"]
        load, header = transport.make_request(1, 1, 0, weight)
        run_payload = struct.pack("<II", 0xFFFFFFFF, 10000) + row["input_path"].read_bytes()
        run, run_header = transport.make_request(2, 2, gold["frame_id"], run_payload,
                                                width=gold["input"]["geometry_wh"][0], height=gold["input"]["geometry_wh"][1])
        diag_payload = struct.pack("<III", 2, core, drain)
        diag, diag_header = transport.make_request(3, 3, 200, diag_payload)
        return [header + weight, run_header + run_payload, diag_header + diag_payload], (load, run, diag)

    def mode2_wire(self, result, requests):
        """先消费前置LOAD/RUN，保留完整诊断原字节供两个phase核验。"""
        wire = transport.WireSession(FragmentSerial(result.stdout, 4096), io.BytesIO(), io.BytesIO(), response_timeout=1)
        wire.receive(requests[0], 0); wire.receive(requests[1], 0)
        wire.last_sequence = 3
        return wire

    def test_c_mode2_dap_abort_final_held_until_explicit_ack(self):
        packets, requests = self.mode2_fixture()
        result = self.run_mock(packets, 3, 0, ASSETS / "fixtures/sample_000/golden_unique.bin", {"S2B_MOCK_DAP_SCENARIO": "normal"})
        wire = self.mode2_wire(result, requests)
        self.assertEqual(wire.receive_abort_ready(requests[2])[0]["phys_status"] & 7, 2)
        self.assertEqual(wire.receive(requests[2], 0)[0]["error_code"], 8)
        self.assertIn(b"status=c05 sequence=4 diag_pending=1", result.stderr)
        self.assertNotIn(b"ACK 2", result.stderr)
        self.assertNotIn(b"CPU_BARE_ABORT", result.stderr)
        ack_payload = struct.pack("<III", 3, 2, 0)
        ack, ack_header = transport.make_request(3, 4, 200, ack_payload)
        result = self.run_mock(packets + [ack_header + ack_payload], 4, 0,
                               ASSETS / "fixtures/sample_000/golden_unique.bin", {"S2B_MOCK_DAP_SCENARIO": "normal"})
        wire = self.mode2_wire(result, requests)
        wire.receive_abort_ready(requests[2]); wire.receive(requests[2], 0)
        self.assertEqual(wire.acknowledge_abort(4)[0]["phys_status"], 0x400)
        self.assertIn(b"ACK 2", result.stderr)
        self.assertIn(b"diag_pending=0", result.stderr)

    def test_c_mode2_short_deadline_and_terminal_interleavings_preserve_original(self):
        for scenario, core, drain, error, code, ready in (("normal", 1, 10000, 5, 7, False),
                ("read_then_terminal", 0xFFFFFFFF, 10000, 5, 7, False),
                ("dap_race", 0xFFFFFFFF, 10000, 5, 7, True),
                ("done_before_dap", 0xFFFFFFFF, 10000, 0, 7, True),
                ("original_fault", 0xFFFFFFFF, 10000, 5, 7, True),
                ("normal", 0xFFFFFFFF, 1, 8, 8, True)):
            packets, requests = self.mode2_fixture(core, drain)
            result = self.run_mock(packets, 3, 2, ASSETS / "fixtures/sample_000/golden_unique.bin", {"S2B_MOCK_DAP_SCENARIO": scenario})
            wire = self.mode2_wire(result, requests)
            if ready: wire.receive_abort_ready(requests[2])
            with self.assertRaises(transport.TransportError): wire.receive(requests[2], 0)
            self.assertEqual(wire.epoch, 1)
            meta = wire.events[-1]["raw_meta"]
            self.assertEqual(meta[2], error); self.assertEqual(meta[-1], code)
            self.assertNotIn(b"CPU_BARE_ABORT", result.stderr)
            self.assertNotIn(b"ACK 2", result.stderr)
            self.assertEqual(result.stderr.count(b"INVALIDATE 01000000"), 3)

    def test_c_mode3_wrong_epoch_frame_phase_or_new_task_never_ack(self):
        packets, _ = self.mode2_fixture()
        for frame, phase, epoch in ((200, 3, 3), (201, 3, 2), (200, 0, 2)):
            payload = struct.pack("<III", phase, epoch, 0)
            _, header = transport.make_request(3, 4, frame, payload)
            result = self.run_mock(packets + [header + payload], 4, 2,
                                  ASSETS / "fixtures/sample_000/golden_unique.bin", {"S2B_MOCK_DAP_SCENARIO": "normal"})
            self.assertNotIn(b"ACK 2", result.stderr)
        payload = struct.pack("<III", 3, 0, 0)
        _, header = transport.make_request(3, 1, 200, payload)
        result = self.run_mock([header + payload], 1, 2)
        self.assertNotIn(b"ACK", result.stderr)
        _, forbidden_header = transport.make_request(3, 4, 200, struct.pack("<III", 0, 0, 0))
        # 仅更改op并重新计算header CRC，证明pending在读新RUN payload之前拒绝。
        forbidden = transport.Header(2, 4, 200, 416, 416, 1, transport.INPUT_BYTES + 8, 0).pack()
        result = self.run_mock(packets + [forbidden], 4, 2,
                              ASSETS / "fixtures/sample_000/golden_unique.bin", {"S2B_MOCK_DAP_SCENARIO": "normal"})
        self.assertNotIn(b"ACK 2", result.stderr)

    def test_c_reject_header_crc_length_sequence_without_start(self):
        payload = bytes(transport.WEIGHT_BYTES)
        request, header = transport.make_request(1, 1, 0, payload)
        for offset in (0, 36):
            changed = bytearray(header); changed[offset] ^= 1
            result = self.run_mock([bytes(changed)], 1, 2)
            self.assertNotIn(b"FLUSH", result.stderr)
            raw_head = transport.Header.unpack(result.stdout[:40]); meta = transport.META.unpack_from(result.stdout[40:])
            self.assertEqual(meta[0], 0); self.assertEqual(meta[-1], 1); self.assertEqual(raw_head.length, 40)
        bad_length = transport.Header(1, 1, 0, 0, 0, 1, transport.WEIGHT_BYTES - 1, 0).pack()
        result = self.run_mock([bad_length], 1, 2)
        self.assertEqual(transport.META.unpack_from(result.stdout[40:])[-1], 4)
        duplicate = transport.Header(1, 2, 0, 0, 0, 1, transport.WEIGHT_BYTES, 0).pack()
        result = self.run_mock([duplicate], 1, 2)
        self.assertEqual(transport.META.unpack_from(result.stdout[40:])[-1], 3)

    def test_c_payload_crc_never_copies_arena_or_starts(self):
        payload = b"GFINT8W1" + bytes(transport.WEIGHT_BYTES - 8)
        _, header = transport.make_request(1, 1, 0, payload)
        changed = bytearray(payload); changed[-1] = 1
        result = self.run_mock([header + changed], 1, 2)
        self.assertNotIn(b"FLUSH", result.stderr)
        self.assertEqual(transport.META.unpack_from(result.stdout[40:])[-1], 2)

    def test_c_cache_probe_phase_order_identity_and_actual_readback(self):
        seeds = (0xA5A55A5A, 0x12345678)
        raw0 = struct.pack("<III", 0, *seeds); raw1 = struct.pack("<III", 1, *seeds)
        first, h0 = transport.make_request(4, 1, 0, raw0); second, h1 = transport.make_request(4, 2, 0, raw1)
        result = self.run_mock([h0 + raw0, h1 + raw1], 2, 0)
        wire = transport.WireSession(FragmentSerial(result.stdout), io.BytesIO(), io.BytesIO(), response_timeout=1)
        for request, seed in ((first, seeds[0]), (second, seeds[1])):
            meta, _, _ = wire.receive(request, 0)
            expected = b"".join(struct.pack("<I", seed ^ ((0x9E3779B9 * index) & 0xFFFFFFFF)) for index in range(64))
            self.assertEqual(meta["probe_bytes"], expected)
        self.assertIn(b"MOCK_OK epoch=0 status=400", result.stderr)
        self.assertIn(b"FLUSH 00000000 256", result.stderr); self.assertIn(b"INVALIDATE 00000000 256", result.stderr)
        self.run_mock([transport.make_request(4, 1, 0, raw1)[1] + raw1], 1, 2)
        bad = struct.pack("<III", 1, seeds[0] ^ 1, seeds[1])
        self.run_mock([h0 + raw0, transport.make_request(4, 2, 0, bad)[1] + bad], 2, 2)
        mismatch = self.run_mock([h0 + raw0, h1 + raw1], 2, 2, environment={"S2B_MOCK_SKIP_DAP": "1"})
        rx = io.BytesIO()
        wire = transport.WireSession(FragmentSerial(mismatch.stdout), rx, io.BytesIO(), response_timeout=1)
        initial = wire.receive(first, 0)[0]["probe_bytes"]
        with self.assertRaises(transport.TransportError): wire.receive(second, 0)
        self.assertEqual(rx.getvalue(), mismatch.stdout)
        self.assertEqual(mismatch.stdout[-256:], initial)
        self.assertNotIn(b"ACK", mismatch.stderr)

    def test_c_illegal_parameter_start_error_safe_then_matching_ack(self):
        raw = struct.pack("<III", 1, 0xFFFFFFFF, 1000)
        request, header = transport.make_request(3, 1, 7, raw)
        result = self.run_mock([header + raw], 1, 0)
        meta, heads, boxes = transport.decode_response(result.stdout[:40], result.stdout[40:], request, 0, 0)
        self.assertEqual(meta["epoch"], 1); self.assertEqual(meta["error_code"], 3)
        self.assertEqual(heads, {}); self.assertEqual(boxes, [])
        self.assertIn(b"MOCK_OK epoch=1 status=400", result.stderr)

    def test_c_load_run_repeat_complete_heads_decode_cache_and_ack(self):
        weight_path, weight, rows = transport.load_assets(ASSETS, [0])
        self.assertTrue(weight_path.is_file())
        row = rows[0]
        raw = row["input_path"].read_bytes()
        payload = struct.pack("<II", 0xFFFFFFFF, 10000) + raw
        _, h0 = transport.make_request(1, 1, 0, weight)
        gold = row["golden"]
        request, h1 = transport.make_request(2, 2, gold["frame_id"], payload,
                                            width=gold["input"]["geometry_wh"][0],
                                            height=gold["input"]["geometry_wh"][1], repeat=2)
        result = self.run_mock([h0 + weight, h1 + payload], 2, 0, ASSETS / "fixtures/sample_000/golden_unique.bin")
        wire = transport.WireSession(FragmentSerial(result.stdout), io.BytesIO(), io.BytesIO(), response_timeout=2)
        load, _ = transport.make_request(1, 1, 0, weight)
        wire.receive(load, 0)
        from verification.s2b_fixed_capture_check import compare_detections
        for index in range(2):
            meta, heads, detections = wire.receive(request, index)
            self.assertEqual(meta["epoch"], index + 1)
            for name, value in heads.items():
                self.assertEqual(transport.digest(value), gold["head_tensors"][name]["tensor_sha256"])
            self.assertTrue(compare_detections(gold["detections"], detections, 1e-6)["match"])
            if index == 0:
                # 实际走过应用二进制输出、PC保存和既有独立checker三段接口。
                capture_dir = transport.new_directory(self.directory / "mock_capture")
                captured = transport.capture_row(capture_dir, row, request.frame, heads, detections)
                reference = transport.reference_row(capture_dir, row)
                transport.write_json_new(capture_dir / "reference.json", {"schema_version": 1, "kind": "s2b_fixed_reference",
                    "model_manifest_sha256": transport.MODEL_SHA, "samples": [reference],
                    "golden_source": {"kind": "frozen_cpu_d9", "path": "report/evidence/S2A-T29/cpu_decode_nms_reference.json", "sha256": transport.CPU_D9_SHA}})
                transport.write_json_new(capture_dir / "capture.json", {"schema_version": 1, "kind": "s2b_fixed_capture",
                    "model_manifest_sha256": transport.MODEL_SHA, "samples": [captured]})
                from verification.s2b_fixed_capture_check import check_capture
                comparison = check_capture(capture_dir / "reference.json", capture_dir / "capture.json")
                transport.write_json_new(self.directory / "mock_capture_check.json", comparison)
                self.assertEqual(comparison["status"], "PASS_OFFLINE_CAPTURE_CHECK")
        self.assertIn(b"MOCK_OK epoch=2 status=400", result.stderr)
        self.assertEqual(result.stderr.count(b"FLUSH 01000000"), 2)
        self.assertEqual(result.stderr.count(b"INVALIDATE 01000000"), 4)
        self.assertEqual(result.stderr.count(b"ACK"), 2)

        failure = self.run_mock([h0 + weight, h1 + payload], 2, 2,
                                ASSETS / "fixtures/sample_000/golden_unique.bin",
                                environment={"S2B_MOCK_TX_FAIL_AFTER": "220"})
        self.assertEqual(len(failure.stdout), 220)
        self.assertNotIn(b"ACK", failure.stderr)
        self.assertNotIn(b"MOCK_OK", failure.stderr)

    def test_frozen_native_c_decoder_against_all_109(self):
        sys.path.insert(0, str(ROOT / "verification"))
        import numpy as np
        import test_s2a_ps_decode_nms_c as frozen
        before_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(GCC.parent) + os.pathsep + before_path
        library = None
        receipt = {"status": "FAIL", "tested_samples": [], "frozen_c_sha256": transport.digest((ROOT / "verification/s2a_ps_decode_nms_reference.c").read_bytes()),
                   "golden_d9_sha256": transport.digest((ROOT / "report/evidence/S2A-T29/cpu_decode_nms_reference.json").read_bytes())}
        try:
            library, compile_record = frozen.compile_library(self.directory)
            gold = json.loads((ROOT / "report/evidence/S2A-T29/cpu_decode_nms_reference.json").read_text(encoding="utf-8"))["samples"]
            self.assertEqual(len(gold), 109)
            for index, row in enumerate(gold):
                heads = {}
                with transport.exact_path(ASSETS / "fixtures" / f"sample_{index:03d}" / "golden_unique.bin").open("rb") as source:
                    for name, head in row["head_tensors"].items():
                        source.seek(head["byte_offset"]); raw = source.read(head["byte_length"])
                        self.assertEqual(hashlib.sha256(raw).hexdigest(), head["tensor_sha256"])
                        key = "13x13" if name == "head13" else "26x26"
                        heads[key] = np.frombuffer(raw, dtype=np.int8).astype(np.float64).reshape(head["shape_nchw"])
                        heads[key] *= head["int8_scale"]
                actual, raw_count = frozen.c_decode(library, heads, *row["input"]["geometry_wh"], .25)
                for detection in actual:
                    detection["class_name"] = transport.CLASS_NAMES[detection["class_id"]]
                from s2b_fixed_capture_check import compare_detections
                comparison = compare_detections(row["detections"], actual, 1e-6)
                receipt["tested_samples"].append({"sample_id": row["sample_id"], "head_tensors": row["head_tensors"],
                                                  "comparison": comparison, "actual_detections": actual, "actual_raw_candidate_count": raw_count})
                self.assertTrue(comparison["match"], row["sample_id"])
                self.assertEqual(raw_count, row["raw_candidate_count_before_stable_nms"])
            self.assertEqual(compile_record["exit_code"], 0)
            receipt["status"] = "PASS_109_FROZEN_NATIVE_C_DECODE"
        finally:
            transport.write_json_new(self.directory / "native_decoder_109_result.json", receipt)
            os.environ["PATH"] = before_path
            if library is not None: frozen.unload_library(library)


if __name__ == "__main__":
    unittest.main(verbosity=2)
