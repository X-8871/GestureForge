#!/usr/bin/env python3
"""为 S2A-T59 生成并核验 row23 的独立 CPU oracle 与准备证据。"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).absolute().parents[1]
BASE_HEAD = "7b8bad78a456310d2ca797a02e3a5a7f873f9c18"
T56_REPORT = ROOT / "report/evidence/S2A-T56/layer35_row20_all_channels.json"
T56_REPORT_SHA256 = "44a25b6b5af6f8868dd2cb9780c4834bdd87860ba43a71b0c696c0b67627da12"
T56_SUMMARY = ROOT / "report/evidence/S2A-T56/mcp_project_run01/simulation_summary.json"
T56_SUMMARY_SHA256 = "eceb674cdc63c25bcc990885e27a81690efbd1312a095a07fd1d8c3235ac9e0b"
T56_RUNNER = ROOT / "verification/test_s2a_conv_layer35_row20_all_channels_rtl.py"
T56_RUNNER_SHA256 = "74be10fa915cd9cdb38d4d0329f72c529322317cda758789098489bc1ad4fd58"
T58_PREPARE_REPORT = ROOT / "report/evidence/S2A-T58/run02/prepare_summary.json"
T58_PREPARE_SHA256 = "f5b170ba5ec2c25fd8c7c917035ab6bb1fe46847198bd74ea0ffb27cbbdcbba6"
T58_MANIFEST = ROOT / "report/evidence/S2A-T58/run02/fixture/fixture_manifest.json"
T58_MANIFEST_SHA256 = "b81128d84ba543efbbb39053f84fa6c1bab9e57109a738d2ea4284e97a670c70"
T58_GOLDEN_SHA256 = "0892e785cfb724eb10c9fd39b5bdba2836fa4eb9c0374dd31e5fd2aa7ce50271"
T58_RUN01_PREPARE_REPORT = ROOT / "report/evidence/S2A-T58/run01/prepare_summary.json"
T58_RUN01_PREPARE_SHA256 = "33c67467387ec6ecd2c6945fb34c0485b351ed7b60f449135158f33e19b9f341"
T58_RUN01_MANIFEST_SHA256 = "895dd04ba9d50e22705849783842f921d319982ef9b7b00834af774bb2dc9b48"
T58_RUN01_ROW22_TB_SHA256 = "57fc1a6e1db1e4ae90661c007ebfa4e6f7a5cdbd8ac3fbc1d7bf8aebfb2cfdec"
T58_PROJECT_PREFLIGHT = ROOT / "report/evidence/S2A-T58/run02/project_preflight_binding.json"
T58_PROJECT_PREFLIGHT_SHA256 = "24fd56415f60f5fe441d039d9f5458be21a4f95759244aa32e13828e9676cb4d"
T58_RUN02_SOURCE_HASHES = {
    "src/int8_conv_tap_geometry.sv":
        "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "src/int8_conv_weight_address.sv":
        "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "src/int8_mac_accumulator.sv":
        "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
    "src/s2a_conv_engine.sv":
        "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "src/s2a_conv_layer35_channel_probe.sv":
        "91f1e954c1a50a0047861b40df75d1f0523ae2307f03d0c7328abaf4d5469ef4",
    "sim/tb_s2a_conv_layer35_row22_all_channels.sv":
        "d66dc1f1d58e5214ddbc4739b878f3662d281d40d19b2d5c49a280a885ace688",
    "verification/test_s2a_conv_layer35_row22_all_channels_rtl.py":
        "c61c5ed246fc0568a520db58a9dfaabf8e7b3152476faf33190f52565c2f0b07",
}
T54_RUNNER = ROOT / "verification/test_s2a_conv_layer35_row18_all_channels_rtl.py"
T54_RUNNER_SHA256 = "4ec6a743d6a80c380505be2a8601879c311a7f42e07323027098c07a8dadd4f3"
T16_PROOF_PATH = Path(r"D:\FPGA_Competition\report\evidence\S2A-T16\conv_requant_proof.json")
T16_PROOF_SHA256 = "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"
T17_ENGINE_PATH = Path(r"D:\FPGA_Competition\report\evidence\S2A-T17\conv_engine_simulation.json")
T17_ENGINE_SHA256 = "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2"
T20_SCHEDULER_PATH = Path(r"D:\FPGA_Competition\report\evidence\S2A-T20\conv_layer_scheduler_simulation.json")
T20_SCHEDULER_SHA256 = "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"
T16_PROOF_SOURCE_PATH = Path(r"D:\FPGA_Competition\verification\s2a_conv_requant_proof.py")
T16_PROOF_SOURCE_SHA256 = "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"
D2_FORWARD_SOURCE_PATH = Path(r"D:\FPGA_Competition\verification\s1_t02_d2_int8_forward.py")
D2_FORWARD_SOURCE_SHA256 = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
UPSTREAM_BINDINGS = {
    "T16_conv_requant_proof": (T16_PROOF_PATH, T16_PROOF_SHA256),
    "T17_conv_engine_evidence": (T17_ENGINE_PATH, T17_ENGINE_SHA256),
    "T20_layer_scheduler_evidence": (T20_SCHEDULER_PATH, T20_SCHEDULER_SHA256),
    "T16_requant_proof_source": (T16_PROOF_SOURCE_PATH, T16_PROOF_SOURCE_SHA256),
    "D2_forward_reference_source": (D2_FORWARD_SOURCE_PATH, D2_FORWARD_SOURCE_SHA256),
    "oracle_source": (T54_RUNNER, T54_RUNNER_SHA256),
}
PREPARATION_INPUT_KEYS = (
    "T56_parent_report", "T56_summary", "T58_parent_prepare_summary",
    "T58_parent_fixture_manifest", "T58_parent_golden",
    "T58_parent_project_preflight_binding", "G0_specification",
    "T01_manifest", "T23_parameter_table", "GF8_package",
    "weight_layer35", "oracle_source", "T16_conv_requant_proof",
    "T17_conv_engine_evidence", "T20_layer_scheduler_evidence",
    "T16_requant_proof_source", "D2_forward_reference_source",
)
G0_PATH = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
G0_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
T01_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T01_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
T23_PATH = ROOT / "report/evidence/S2A-T23/conv_requant_parameter_table.json"
T23_SHA256 = "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1"
GF8_SHA256 = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
EXPECTED_PARAMETER_DIGEST_SHA256 = "93a49c25387a459cb2964d988ac6e803d8ba9c8a3fcab664b948efb6354e3f29"
T56_PARENT_SOURCES = (
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
    "sim/tb_s2a_conv_layer35_row20_all_channels.sv",
    "sim/s2a_t56_no_wave.tcl",
    "verification/test_s2a_conv_layer35_row20_all_channels_rtl.py",
)
RTL_PATHS = T56_PARENT_SOURCES[:5]
T59_SOURCE_PATHS = (
    *RTL_PATHS,
    "sim/tb_s2a_conv_layer35_row23_all_channels.sv",
    "verification/test_s2a_conv_layer35_row23_all_channels_rtl.py",
    "verification/test_s2a_t59_upstream_fail_closed.py",
)
T59_RUNNER_RELATIVE = "verification/test_s2a_conv_layer35_row23_all_channels_rtl.py"
XPR_PATH = ROOT / "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr"
EVIDENCE_ROOT = ROOT / "report/evidence/S2A-T59"
ROOT_PROJECT_PREFLIGHT = EVIDENCE_ROOT / "project_preflight_binding.json"
ROOT_PROJECT_PREFLIGHT_SHA256 = "79177d4f0591762d9cccce9700fc4104a6a7c7c4fe7cc89ae136928e1e06b5d1"
RUN05_PREPARE_REPORT = EVIDENCE_ROOT / "run05/prepare_summary.json"
RUN05_PREPARE_REPORT_SHA256 = "ed42285130ba07d82b6b64cf437c27b52ec12a610bc2d2a94554670367342929"
RUN05_FIXTURE_MANIFEST = EVIDENCE_ROOT / "run05/fixture/fixture_manifest.json"
RUN05_FIXTURE_MANIFEST_SHA256 = "52f008959ecef8c73969bec7f46ced7af8ebedd1b5b05d2976d0d55d1428908a"
RUN05_FAILED_AUDIT = EVIDENCE_ROOT / "run05/upstream_fail_closed_audit.json"
RUN05_FAILED_AUDIT_SHA256 = "b3734cd917e0a7248b702137a1fe72215f18b8b0d13169cad33c890eafcc21f2"
RUN06_PREPARE_REPORT = EVIDENCE_ROOT / "run06/prepare_summary.json"
RUN06_PREPARE_REPORT_SHA256 = "3666d5b419dacd608d3a6a2b22ea22dfabe0ae63ad80ef325ff3593c943eeeaf"
RUN06_FIXTURE_MANIFEST = EVIDENCE_ROOT / "run06/fixture/fixture_manifest.json"
RUN06_FIXTURE_MANIFEST_SHA256 = "9d59acf04fba74eea5a34cd5165b92803dd020204308c49580428686e4fa9a8b"
RUN06_PROJECT_PREFLIGHT = EVIDENCE_ROOT / "run06/project_preflight_binding.json"
RUN06_PROJECT_PREFLIGHT_SHA256 = "67e6dbfeedcb29d0325a4c15038513f1a0bc6523bf98d7638e5a89bcc3eb3afb"
RUN06_AUDIT = EVIDENCE_ROOT / "run06/upstream_fail_closed_audit.json"
RUN06_AUDIT_SHA256 = "60ff1be9a5b39e1cc1b3e7b8910bcaf774d4ffa735dad178270c968f52f74f04"
RUN07_PREPARE_REPORT = EVIDENCE_ROOT / "run07/prepare_summary.json"
RUN07_PREPARE_REPORT_SHA256 = "989118b9794ea29050a608ddc9065d17a2dc6dec1db37b94b8e0a5068a535350"
RUN07_PROJECT_PREFLIGHT = EVIDENCE_ROOT / "run07/project_preflight_binding.json"
RUN07_PROJECT_PREFLIGHT_SHA256 = "1ce2e3b1ae8645eb0f5b418cb34e1266677583a97c4da7d75832b9d826b28fc8"
RUN07_FIXTURE_MANIFEST = EVIDENCE_ROOT / "run07/fixture/fixture_manifest.json"
RUN07_FIXTURE_MANIFEST_SHA256 = "9624a69734aca61c8d9db9d7609e2cc800430312fe0a3533dee6a2f0da35f3a4"
RUN07_GOLDEN_SHA256 = "95f93d520186a64693996fa6cf9184417539c37ea8535359a7cd1579f47fc07e"
RUN07_AUDIT = EVIDENCE_ROOT / "run07/upstream_fail_closed_audit.json"
RUN07_AUDIT_SHA256 = "8a8184bf520f32bb22ad46db6204351ba3489211a1641f2affda4775e576d435"
RUN07_FEATURE_SHA256 = "f7cbcdae9627c974b0210b3329be66a4264d96d0e2474d3c7f30a1b9c2f59ff1"
RUN07_WEIGHTS_SHA256 = "e7b7d6fd8511b918d0a3ee372ef9d35eb4f3a2827fac77e28cf4f9d775d85bc2"
RUN07_VECTORS_SHA256 = "7498cd69be4ce7b686d829ed2583997da0a7b3d186d94414ff086c5678f60c36"
RUN07_SOURCE_HASHES = {
    "src/int8_conv_tap_geometry.sv":
        "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "src/int8_conv_weight_address.sv":
        "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "src/int8_mac_accumulator.sv":
        "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
    "src/s2a_conv_engine.sv":
        "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "src/s2a_conv_layer35_channel_probe.sv":
        "91f1e954c1a50a0047861b40df75d1f0523ae2307f03d0c7328abaf4d5469ef4",
    "sim/tb_s2a_conv_layer35_row23_all_channels.sv":
        "ec05bd426da1ce40c60884e82f260dc75ee7d0d94b8ad0ec06f2a5b3ee8b0cb2",
    "verification/test_s2a_conv_layer35_row23_all_channels_rtl.py":
        "4ca36bb4942c703ce0abb793115cead290cbe50835ac0420d84ce3bc445694dc",
    "verification/test_s2a_t59_upstream_fail_closed.py":
        "f95cb13df847700f62600d9f4ada8a476c2317240719ec674237109e6a971010",
}
RUN08_PREPARE_REPORT = EVIDENCE_ROOT / "run08/prepare_summary.json"
RUN08_PREPARE_REPORT_SHA256 = "a0122ab29c9d9d8b60828be22d5fdb4502ccf5ed91ce816e79185eba7fc2c5d8"
RUN08_PROJECT_PREFLIGHT = EVIDENCE_ROOT / "run08/project_preflight_binding.json"
RUN08_PROJECT_PREFLIGHT_SHA256 = "40b28e2292480bcf0c2ad1635e5fb111c4d8fb9c453b4a05ce5abd1649cbed59"
RUN08_FIXTURE_MANIFEST = EVIDENCE_ROOT / "run08/fixture/fixture_manifest.json"
RUN08_FIXTURE_MANIFEST_SHA256 = "e9ce03673345bb6b094568cb0ce98e7832cda29c2b87a04988ccebbee8be9092"
RUN08_GOLDEN_SHA256 = "95f93d520186a64693996fa6cf9184417539c37ea8535359a7cd1579f47fc07e"
RUN08_FEATURE_SHA256 = "f7cbcdae9627c974b0210b3329be66a4264d96d0e2474d3c7f30a1b9c2f59ff1"
RUN08_WEIGHTS_SHA256 = "e7b7d6fd8511b918d0a3ee372ef9d35eb4f3a2827fac77e28cf4f9d775d85bc2"
RUN08_VECTORS_SHA256 = "7498cd69be4ce7b686d829ed2583997da0a7b3d186d94414ff086c5678f60c36"
RUN08_SOURCE_HASHES = {
    "src/int8_conv_tap_geometry.sv":
        "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "src/int8_conv_weight_address.sv":
        "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "src/int8_mac_accumulator.sv":
        "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
    "src/s2a_conv_engine.sv":
        "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "src/s2a_conv_layer35_channel_probe.sv":
        "91f1e954c1a50a0047861b40df75d1f0523ae2307f03d0c7328abaf4d5469ef4",
    "sim/tb_s2a_conv_layer35_row23_all_channels.sv":
        "ae733794f0c987476a7ca1ad861e23061cafb3ab581713c4c4c79eef842007f3",
    "verification/test_s2a_conv_layer35_row23_all_channels_rtl.py":
        "3b78c823c27148401c30f6b1adb90b0a34211f9f73e1c2f13b59684a08f63c80",
    "verification/test_s2a_t59_upstream_fail_closed.py":
        "f95cb13df847700f62600d9f4ada8a476c2317240719ec674237109e6a971010",
}
RUN08_ROOT = EVIDENCE_ROOT / "run08"
RUN09_ROOT = EVIDENCE_ROOT / "run09"
RUN09_PREPARE_REPORT = RUN09_ROOT / "prepare_summary.json"
RUN09_PREPARE_REPORT_SHA256 = "48f21ee9c4b5ca9cf6594e92083495e970863a2aef3a9b79603764b3053c49be"
RUN09_PROJECT_PREFLIGHT = RUN09_ROOT / "project_preflight_binding.json"
RUN09_PROJECT_PREFLIGHT_SHA256 = "0057b855ba99346bf5acfd063f2a48a130f8cadcd6eed002f59cdded6fe04529"
RUN09_FIXTURE_MANIFEST = RUN09_ROOT / "fixture/fixture_manifest.json"
RUN09_FIXTURE_MANIFEST_SHA256 = "345cda39864937b3bc24129dbebf6b1b8558896c8dde97637a262f18b5c5e6fd"
RUN09_GOLDEN_SHA256 = "95f93d520186a64693996fa6cf9184417539c37ea8535359a7cd1579f47fc07e"
RUN09_FEATURE_SHA256 = "f7cbcdae9627c974b0210b3329be66a4264d96d0e2474d3c7f30a1b9c2f59ff1"
RUN09_WEIGHTS_SHA256 = "e7b7d6fd8511b918d0a3ee372ef9d35eb4f3a2827fac77e28cf4f9d775d85bc2"
RUN09_VECTORS_SHA256 = "7498cd69be4ce7b686d829ed2583997da0a7b3d186d94414ff086c5678f60c36"
RUN09_SOURCE_HASHES = {
    "src/int8_conv_tap_geometry.sv":
        "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "src/int8_conv_weight_address.sv":
        "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "src/int8_mac_accumulator.sv":
        "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
    "src/s2a_conv_engine.sv":
        "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "src/s2a_conv_layer35_channel_probe.sv":
        "91f1e954c1a50a0047861b40df75d1f0523ae2307f03d0c7328abaf4d5469ef4",
    "sim/tb_s2a_conv_layer35_row23_all_channels.sv":
        "77a606b0f6342e8c56b5bb79f79d9aa64adb52071afe4f1da9f4d9fd0bd46417",
    "verification/test_s2a_conv_layer35_row23_all_channels_rtl.py":
        "2033a6dd2bdb89c0805ea3ef1928a9faa2401915fc60cab10e654b8ebb6c8b5b",
    "verification/test_s2a_t59_upstream_fail_closed.py":
        "f95cb13df847700f62600d9f4ada8a476c2317240719ec674237109e6a971010",
}
RUN_ROOT = EVIDENCE_ROOT / "run10"
PROJECT_PREFLIGHT = RUN_ROOT / "project_preflight_binding.json"
FIXTURE_ROOT = RUN_ROOT / "fixture"
PREPARE_REPORT = RUN_ROOT / "prepare_summary.json"
FAIL_CLOSED_AUDIT = RUN07_AUDIT
PRIOR_ATTEMPT_ARTIFACTS = {
    "run05": {
        "prepare_summary": (RUN05_PREPARE_REPORT, RUN05_PREPARE_REPORT_SHA256),
        "fixture_manifest": (RUN05_FIXTURE_MANIFEST, RUN05_FIXTURE_MANIFEST_SHA256),
        "upstream_fail_closed_audit": (RUN05_FAILED_AUDIT, RUN05_FAILED_AUDIT_SHA256),
    },
    "run06": {
        "prepare_summary": (RUN06_PREPARE_REPORT, RUN06_PREPARE_REPORT_SHA256),
        "fixture_manifest": (RUN06_FIXTURE_MANIFEST, RUN06_FIXTURE_MANIFEST_SHA256),
        "project_preflight_binding": (RUN06_PROJECT_PREFLIGHT, RUN06_PROJECT_PREFLIGHT_SHA256),
        "upstream_fail_closed_audit": (RUN06_AUDIT, RUN06_AUDIT_SHA256),
    },
    "run07": {
        "prepare_summary": (RUN07_PREPARE_REPORT, RUN07_PREPARE_REPORT_SHA256),
        "project_preflight_binding": (RUN07_PROJECT_PREFLIGHT, RUN07_PROJECT_PREFLIGHT_SHA256),
        "fixture_manifest": (RUN07_FIXTURE_MANIFEST, RUN07_FIXTURE_MANIFEST_SHA256),
        "golden": (EVIDENCE_ROOT / "run07/fixture/golden.bin", RUN07_GOLDEN_SHA256),
        "feature": (EVIDENCE_ROOT / "run07/fixture/feature_input.bin", RUN07_FEATURE_SHA256),
        "weights": (EVIDENCE_ROOT / "run07/fixture/layer35_weights.bin", RUN07_WEIGHTS_SHA256),
        "vectors": (EVIDENCE_ROOT / "run07/fixture/vectors.txt", RUN07_VECTORS_SHA256),
        "upstream_fail_closed_audit": (RUN07_AUDIT, RUN07_AUDIT_SHA256),
    },
    "run08": {
        "prepare_summary": (RUN08_PREPARE_REPORT, RUN08_PREPARE_REPORT_SHA256),
        "project_preflight_binding":
            (RUN08_PROJECT_PREFLIGHT, RUN08_PROJECT_PREFLIGHT_SHA256),
        "fixture_manifest": (RUN08_FIXTURE_MANIFEST, RUN08_FIXTURE_MANIFEST_SHA256),
        "golden": (EVIDENCE_ROOT / "run08/fixture/golden.bin", RUN08_GOLDEN_SHA256),
        "feature": (EVIDENCE_ROOT / "run08/fixture/feature_input.bin", RUN08_FEATURE_SHA256),
        "weights": (EVIDENCE_ROOT / "run08/fixture/layer35_weights.bin", RUN08_WEIGHTS_SHA256),
        "vectors": (EVIDENCE_ROOT / "run08/fixture/vectors.txt", RUN08_VECTORS_SHA256),
    },
    "run09": {
        "prepare_summary": (RUN09_PREPARE_REPORT, RUN09_PREPARE_REPORT_SHA256),
        "project_preflight_binding":
            (RUN09_PROJECT_PREFLIGHT, RUN09_PROJECT_PREFLIGHT_SHA256),
        "fixture_manifest": (RUN09_FIXTURE_MANIFEST, RUN09_FIXTURE_MANIFEST_SHA256),
        "golden": (RUN09_ROOT / "fixture/golden.bin", RUN09_GOLDEN_SHA256),
        "feature": (RUN09_ROOT / "fixture/feature_input.bin", RUN09_FEATURE_SHA256),
        "weights": (RUN09_ROOT / "fixture/layer35_weights.bin", RUN09_WEIGHTS_SHA256),
        "vectors": (RUN09_ROOT / "fixture/vectors.txt", RUN09_VECTORS_SHA256),
    },
}
POINTS = tuple((23, x) for x in range(26))
RAW_COUNT = 6_656
INT8_COUNT = 6_656
RAW_BYTES = RAW_COUNT * 4
INT8_BYTES = INT8_COUNT
GOLDEN_BYTES = RAW_BYTES + INT8_BYTES
FEATURE_BYTES = 259_584
WEIGHT_BYTES = 884_736
PROCESS_NAMES = (
    "vivado.exe", "vivado_lab.exe", "xsim.exe", "xsimk.exe",
    "xelab.exe", "xvlog.exe", "xvhdl.exe", "xsct.exe",
)
POWERSHELL_PREFLIGHT = r"""
$ErrorActionPreference = 'Stop'
$repoRoot = 'D:\FPGA_Competition'
function Assert-ContainedPath {
    param([string]$Candidate, [string]$Container)
    foreach ($value in @($Candidate, $Container)) {
        $components = $value -split '[\\/]+'
        if ($components -contains '.' -or $components -contains '..') {
            throw "路径含点组件：$value"
        }
    }
    $fullCandidate = [IO.Path]::GetFullPath($Candidate)
    $fullContainerRoot = [IO.Path]::GetFullPath($Container).TrimEnd('\')
    if ([String]::Equals(
        $fullCandidate, $fullContainerRoot,
        [StringComparison]::OrdinalIgnoreCase)) {
        return
    }
    $fullContainer = $fullContainerRoot + '\'
    if (-not $fullCandidate.StartsWith(
        $fullContainer, [StringComparison]::OrdinalIgnoreCase)) {
        throw "路径脱离固定根目录：$fullCandidate；root=$Container"
    }
}
$requiredDirectories = @(
    'D:\',
    'D:\FPGA_Competition',
    'D:\FPGA_Competition\report',
    'D:\FPGA_Competition\report\evidence',
    'D:\FPGA_Competition\report\evidence\S2A-T58',
    'D:\FPGA_Competition\report\evidence\S2A-T58\run02',
    'D:\FPGA_Competition\report\evidence\S2A-T58\run02\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run01',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run01\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run02',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run02\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run03',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run03\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run04',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run04\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run05',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run05\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run06',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run06\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run07',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run07\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run08',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run08\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run09',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run09\fixture',
    'D:\FPGA_Competition\vivado',
    'D:\FPGA_Competition\vivado\AX7Z020_Gesture'
)
foreach ($path in $requiredDirectories) {
    $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if (-not $item.PSIsContainer -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "路径链不是普通目录：$path"
    }
}
$xpr = 'D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$xprItem = Get-Item -LiteralPath $xpr -Force -ErrorAction Stop
if ($xprItem.PSIsContainer -or
    (($xprItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
    throw "目标 XPR 不是普通文件：$xpr"
}
$evidenceRoot = 'D:\FPGA_Competition\report\evidence\S2A-T59'
$t58EvidenceRoot = 'D:\FPGA_Competition\report\evidence\S2A-T58'
$t58Run02 = 'D:\FPGA_Competition\report\evidence\S2A-T58\run02'
$run01 = Join-Path $evidenceRoot 'run01'
$run02 = Join-Path $evidenceRoot 'run02'
$run03 = Join-Path $evidenceRoot 'run03'
$run04 = Join-Path $evidenceRoot 'run04'
$run05 = Join-Path $evidenceRoot 'run05'
$run06 = Join-Path $evidenceRoot 'run06'
$run07 = Join-Path $evidenceRoot 'run07'
$run08 = Join-Path $evidenceRoot 'run08'
$run09 = Join-Path $evidenceRoot 'run09'
$run10 = Join-Path $evidenceRoot 'run10'
$run10Preflight = Join-Path $run10 'project_preflight_binding.json'
$oldRootBinding = Join-Path $evidenceRoot 'project_preflight_binding.json'
$oldBindingItem = Get-Item -LiteralPath $oldRootBinding -Force -ErrorAction Stop
if ($oldBindingItem.PSIsContainer -or
    (($oldBindingItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
    throw "既有 T59 根级绑定不是普通文件：$oldRootBinding"
}
Assert-ContainedPath -Candidate $evidenceRoot -Container $repoRoot
Assert-ContainedPath -Candidate $t58EvidenceRoot -Container $repoRoot
Assert-ContainedPath -Candidate $oldRootBinding -Container $evidenceRoot
$rootBindingShaExpected = '79177d4f0591762d9cccce9700fc4104a6a7c7c4fe7cc89ae136928e1e06b5d1'
$sha256 = [System.Security.Cryptography.SHA256]::Create()
try {
    $rootBindingStream = [IO.File]::OpenRead($oldRootBinding)
    try {
        $rootBindingSha = [BitConverter]::ToString(
            $sha256.ComputeHash($rootBindingStream)).Replace('-', '').ToLowerInvariant()
    } finally {
        $rootBindingStream.Dispose()
    }
} finally {
    $sha256.Dispose()
}
if ($rootBindingSha -ne $rootBindingShaExpected) {
    throw "T59 根级绑定 SHA-256 不匹配：$rootBindingSha"
}
Assert-ContainedPath -Candidate $run10 -Container $evidenceRoot
if (Test-Path -LiteralPath $run10 -PathType Any) {
    throw "T59 run10 目标已存在，拒绝覆盖：$run10"
}
if (Test-Path -LiteralPath $run10Preflight -PathType Any) {
    throw "T59 run10 预检绑定目标已存在，拒绝覆盖：$run10Preflight"
}
$expectedRootEntries = @(
    'project_preflight_binding.json', 'run01', 'run02', 'run03', 'run04',
    'run05', 'run06', 'run07', 'run08', 'run09'
)
$actualRootEntries = @(Get-ChildItem -LiteralPath $evidenceRoot -Force |
    ForEach-Object { $_.Name } | Sort-Object)
if (($actualRootEntries -join '|') -ne ($expectedRootEntries -join '|')) {
    throw 'T59 根目录与预期 run01-run09/根级旧绑定不一致；拒绝写入 run10'
}
$pendingRoots = @(
    $t58Run02, $run01, $run02, $run03, $run04,
    $run05, $run06, $run07, $run08, $run09
)
foreach ($root in $pendingRoots) {
    if ($root -eq $t58Run02) {
        $boundary = $t58EvidenceRoot
    } else {
        $boundary = $evidenceRoot
    }
    Assert-ContainedPath -Candidate $root -Container $boundary
    $runBoundary = $root
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($root)
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($entry in [IO.Directory]::EnumerateFileSystemEntries($directory)) {
            Assert-ContainedPath -Candidate $entry -Container $runBoundary
            $attributes = [IO.File]::GetAttributes($entry)
            if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "既有 T59 证据目录中发现 reparse point：$entry"
            }
            if (($attributes -band [IO.FileAttributes]::Directory) -ne 0) {
                $pending.Push($entry)
            }
        }
    }
}
$names = @('vivado.exe', 'vivado_lab.exe', 'xsim.exe', 'xsimk.exe',
           'xelab.exe', 'xvlog.exe', 'xvhdl.exe', 'xsct.exe')
$processes = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
    Where-Object { $names -contains $_.Name.ToLowerInvariant() } |
    Sort-Object ProcessId |
    ForEach-Object {
        [ordered]@{ name = $_.Name; process_id = [int]$_.ProcessId }
    })
$result = [ordered]@{
    path_chain_valid = $true
    checked_directories = $requiredDirectories
    checked_xpr = $xpr
    evidence_root = $evidenceRoot
    run10_path = $run10
    target_absent = $true
    existing_run01 = $true
    existing_run02 = $true
    existing_run03 = $true
    existing_run04 = $true
    existing_run05 = $true
    existing_run06 = $true
    existing_run07 = $true
    existing_run08 = $true
    existing_run09 = $true
    existing_run10 = $false
    root_binding_sha256 = $rootBindingSha
    process_names = $names
    processes_before_prepare = $processes
}
[Console]::Out.Write((ConvertTo-Json -InputObject $result -Depth 5 -Compress))
"""

POWERSHELL_PROCESS_SNAPSHOT = r"""
$ErrorActionPreference = 'Stop'
$names = @('vivado.exe', 'vivado_lab.exe', 'xsim.exe', 'xsimk.exe',
           'xelab.exe', 'xvlog.exe', 'xvhdl.exe', 'xsct.exe')
$processes = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
    Where-Object { $names -contains $_.Name.ToLowerInvariant() } |
    Sort-Object ProcessId |
    ForEach-Object {
        [ordered]@{ name = $_.Name; process_id = [int]$_.ProcessId }
    })
$result = [ordered]@{ process_names = $names; processes = $processes }
[Console]::Out.Write((ConvertTo-Json -InputObject $result -Depth 4 -Compress))
"""


class T59Error(RuntimeError):
    """表示 S2A-T59 冻结输入或准备证据核验失败。"""


class T59UpstreamShaMismatch(T59Error):
    """表示某项冻结上游的 SHA-256 门禁拒绝了变更内容。"""

    def __init__(self, dependency_key: str, path: Path,
                 expected_sha256: str, actual_sha256: str) -> None:
        self.failure_record = {
            "code": "EXPECTED_UPSTREAM_SHA_MISMATCH",
            "dependency_key": dependency_key,
            "dependency_path": str(path.absolute()),
            "expected_sha256": expected_sha256,
            "actual_sha256": actual_sha256,
        }
        super().__init__(
            f"冻结上游 SHA-256 不匹配：{dependency_key}：{path} "
            f"expected={expected_sha256} actual={actual_sha256}"
        )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T59Error(message)


def _absolute_lexical_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    _require(not any(part in (".", "..") for part in candidate.parts),
             f"拒绝含点路径组件的文件路径：{candidate}")
    return Path(os.path.abspath(os.fspath(candidate)))


def _guard_repo_path(path: Path, *,
                     containment_root: Path = ROOT,
                     must_exist: bool = True,
                     expected_kind: str | None = None,
                     lstat_func: Any = os.lstat) -> Path:
    candidate = _absolute_lexical_path(path)
    boundary = _absolute_lexical_path(containment_root)
    try:
        candidate.relative_to(boundary)
    except ValueError as error:
        raise T59Error(
            f"路径不在允许的真实根目录内：path={candidate} root={boundary}"
        ) from error

    components = list(reversed([candidate, *candidate.parents]))
    for index, component in enumerate(components):
        is_target = component == candidate
        try:
            metadata = lstat_func(component)
        except FileNotFoundError as error:
            _require(is_target and not must_exist,
                     f"路径组件不存在：{component}")
            continue
        except OSError as error:
            raise T59Error(f"无法检查路径组件：{component}：{error}") from error
        attributes = int(getattr(metadata, "st_file_attributes", 0))
        reparse_flag = int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
        _require(not stat.S_ISLNK(metadata.st_mode) and
                 (attributes & reparse_flag) == 0,
                 f"路径组件是 symlink/reparse point：{component}")
        if not is_target:
            _require(stat.S_ISDIR(metadata.st_mode),
                     f"路径祖先组件不是目录：{component}")
        elif expected_kind == "file":
            _require(stat.S_ISREG(metadata.st_mode),
                     f"目标路径不是普通文件：{component}")
        elif expected_kind == "directory":
            _require(stat.S_ISDIR(metadata.st_mode),
                     f"目标路径不是普通目录：{component}")

    if must_exist:
        resolved_candidate = candidate.resolve(strict=True)
        resolved_boundary = boundary.resolve(strict=True)
    else:
        resolved_candidate = candidate.resolve(strict=False)
        resolved_boundary = boundary.resolve(strict=True)
    try:
        resolved_candidate.relative_to(resolved_boundary)
    except ValueError as error:
        raise T59Error(
            f"路径经组件检查后仍不属于允许的真实根目录："
            f"path={resolved_candidate} root={resolved_boundary}"
        ) from error
    return candidate


def _safe_path_string(path: Path, *,
                      containment_root: Path = ROOT,
                      expected_kind: str | None = None) -> str:
    guarded = _guard_repo_path(
        path, containment_root=containment_root,
        must_exist=True, expected_kind=expected_kind,
    )
    return str(guarded)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    path = _guard_repo_path(path, expected_kind="file")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    path = _guard_repo_path(path, expected_kind="file")
    data = path.read_bytes()
    value = json.loads(data.decode("utf-8"))
    _require(isinstance(value, dict), f"JSON 根节点不是对象：{path}")
    return value, _sha256(data)


def _write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    path = _guard_repo_path(
        path, containment_root=RUN_ROOT, must_exist=False,
        expected_kind="file",
    )
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(payload)


def _artifact(path: Path) -> dict[str, Any]:
    path = _guard_repo_path(path, expected_kind="file")
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": _sha_file(path)}


def _verify_pinned_file(path: Path, expected_sha256: str, *,
                        containment_root: Path = ROOT,
                        label: str) -> dict[str, Any]:
    guarded = _guard_repo_path(
        path, containment_root=containment_root, expected_kind="file",
    )
    actual = _sha_file(guarded)
    _require(actual == expected_sha256,
             f"{label} SHA-256 不匹配：expected={expected_sha256} actual={actual}")
    return _artifact(guarded)


def _guard_fixed_external_file(path: Path, expected_path: Path) -> Path:
    candidate = _absolute_lexical_path(path)
    expected = _absolute_lexical_path(expected_path)
    _require(candidate == expected,
             f"外部冻结输入路径与 T01 manifest 不一致：{candidate}")
    components = list(reversed([candidate, *candidate.parents]))
    for component in components:
        is_target = component == candidate
        try:
            metadata = os.lstat(component)
        except OSError as error:
            raise T59Error(f"无法检查外部冻结输入路径组件：{component}：{error}") from error
        attributes = int(getattr(metadata, "st_file_attributes", 0))
        reparse_flag = int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
        _require(not stat.S_ISLNK(metadata.st_mode) and
                 (attributes & reparse_flag) == 0,
                 f"外部冻结输入路径组件是 symlink/reparse point：{component}")
        if is_target:
            _require(stat.S_ISREG(metadata.st_mode),
                     f"外部冻结输入目标不是普通文件：{component}")
        else:
            _require(stat.S_ISDIR(metadata.st_mode),
                     f"外部冻结输入祖先组件不是目录：{component}")
    resolved_candidate = candidate.resolve(strict=True)
    resolved_expected = expected.resolve(strict=True)
    _require(resolved_candidate == resolved_expected,
             f"外部冻结输入实际路径与固定路径不一致：{resolved_candidate}")
    return candidate


def _verify_gf8_package_record(record: dict[str, Any], label: str) -> Path:
    manifest, manifest_sha256 = _read_json(T01_PATH)
    _require(manifest_sha256 == T01_SHA256,
             "T01 manifest SHA-256 不匹配，无法验证外部 GF8 输入")
    package = manifest.get("bindings", {}).get("gf8_package", {})
    expected_path = Path(str(package.get("path", "")))
    expected_sha256 = str(package.get("sha256", "")).lower()
    expected_bytes = int(package.get("bytes", -1))
    _require(expected_sha256 == GF8_SHA256 and expected_bytes > 0,
             "T01 manifest 中的 GF8 固定摘要或长度不匹配")
    path = _guard_fixed_external_file(
        Path(str(record.get("path", ""))), expected_path,
    )
    _require(int(record.get("bytes", -1)) == expected_bytes and
             int(record.get("bytes", -1)) == path.stat().st_size and
             str(record.get("sha256", "")).lower() == expected_sha256,
             f"{label} 路径或长度/SHA 绑定不匹配：{path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    _require(digest.hexdigest() == expected_sha256,
             f"{label} 外部冻结输入 SHA-256 不匹配：{path}")
    return path


def _verify_root_binding() -> str:
    _guard_repo_path(EVIDENCE_ROOT, containment_root=ROOT,
                     expected_kind="directory")
    binding_path = _guard_repo_path(
        ROOT_PROJECT_PREFLIGHT, containment_root=EVIDENCE_ROOT,
        expected_kind="file",
    )
    expected_path = _absolute_lexical_path(
        EVIDENCE_ROOT / "project_preflight_binding.json"
    )
    _require(binding_path == expected_path,
             "T59 根级旧绑定路径与固定路径不一致")
    actual_sha256 = _sha_file(binding_path)
    _require(actual_sha256 == ROOT_PROJECT_PREFLIGHT_SHA256,
             "T59 根级旧绑定 SHA-256 不匹配")
    return actual_sha256


def _audit_run_root_paths(run_root: Path) -> list[str]:
    guarded_root = _guard_repo_path(
        run_root, containment_root=EVIDENCE_ROOT,
        expected_kind="directory",
    )
    discovered_files: list[str] = []
    pending = [guarded_root]
    while pending:
        directory = pending.pop()
        directory = _guard_repo_path(
            directory, containment_root=guarded_root,
            expected_kind="directory",
        )
        with os.scandir(directory) as entries:
            for entry in entries:
                child = _guard_repo_path(
                    Path(entry.path), containment_root=guarded_root,
                    expected_kind=None,
                )
                metadata = os.lstat(child)
                if stat.S_ISDIR(metadata.st_mode):
                    pending.append(child)
                else:
                    _require(stat.S_ISREG(metadata.st_mode),
                             f"准备证据中发现非普通文件：{child}")
                    discovered_files.append(
                        child.relative_to(guarded_root).as_posix()
                    )
    return sorted(discovered_files)


def _expect_path_rejection(callback: Any, label: str) -> dict[str, str]:
    try:
        callback()
    except T59Error:
        return {"case": label, "result": "PASS"}
    raise T59Error(f"路径负向测试未 fail closed：{label}")


def _run_path_guard_negative_tests() -> dict[str, Any]:
    global EVIDENCE_ROOT, ROOT_PROJECT_PREFLIGHT
    cases: list[dict[str, str]] = []
    link_method = "single_file_reparse_metadata"
    with tempfile.TemporaryDirectory(
            prefix=".t59_path_guard_", dir=EVIDENCE_ROOT) as temporary:
        temporary_root = Path(temporary)
        target = temporary_root / "target.bin"
        target.write_bytes(b"target")
        link = temporary_root / "single_file_link.bin"
        try:
            os.symlink(target, link)
            link_method = "actual_single_file_symlink"
            cases.append(_expect_path_rejection(
                lambda: _guard_repo_path(
                    link, containment_root=EVIDENCE_ROOT,
                    expected_kind="file",
                ),
                "single_file_symlink_or_reparse",
            ))
        except OSError:
            def synthetic_reparse_lstat(path: Path) -> Any:
                metadata = os.lstat(path)
                if _absolute_lexical_path(Path(path)) == _absolute_lexical_path(target):
                    return SimpleNamespace(
                        st_mode=metadata.st_mode,
                        st_file_attributes=
                            int(getattr(metadata, "st_file_attributes", 0)) | 0x400,
                    )
                return metadata

            cases.append(_expect_path_rejection(
                lambda: _guard_repo_path(
                    target, containment_root=EVIDENCE_ROOT,
                    expected_kind="file", lstat_func=synthetic_reparse_lstat,
                ),
                "single_file_symlink_or_reparse",
            ))

        outside_path: Path | None = None
        with tempfile.TemporaryDirectory(prefix="t59_outside_root_") as outside:
            outside_path = Path(outside) / "outside.bin"
            outside_path.write_bytes(b"outside")
            cases.append(_expect_path_rejection(
                lambda: _guard_repo_path(
                    outside_path, containment_root=ROOT,
                    expected_kind="file",
                ),
                "repository_outside_path",
            ))
            t01_manifest, _ = _read_json(T01_PATH)
            gf8_record = dict(t01_manifest["bindings"]["gf8_package"])
            gf8_record["path"] = str(outside_path)
            cases.append(_expect_path_rejection(
                lambda: _verify_gf8_package_record(
                    gf8_record, "T59 GF8_package path replacement negative test",
                ),
                "fixed_external_path_substitution",
            ))

        root_binding_copy = temporary_root / "tampered_root_binding.json"
        root_binding_bytes = _guard_repo_path(
            ROOT_PROJECT_PREFLIGHT, containment_root=EVIDENCE_ROOT,
            expected_kind="file",
        ).read_bytes()
        root_binding_copy.write_bytes(root_binding_bytes + b" ")
        original_evidence_root = EVIDENCE_ROOT
        original_root_binding = ROOT_PROJECT_PREFLIGHT
        EVIDENCE_ROOT = temporary_root
        ROOT_PROJECT_PREFLIGHT = root_binding_copy
        try:
            cases.append(_expect_path_rejection(
                _verify_root_binding,
                "root_binding_sha_tamper",
            ))
        finally:
            EVIDENCE_ROOT = original_evidence_root
            ROOT_PROJECT_PREFLIGHT = original_root_binding

        history_copy = temporary_root / "tampered_run07_summary.json"
        history_bytes = RUN07_PREPARE_REPORT.read_bytes()
        history_copy.write_bytes(history_bytes[:-1] + bytes([history_bytes[-1] ^ 1]))
        original_pins = PRIOR_ATTEMPT_ARTIFACTS["run07"]
        changed_pins = dict(original_pins)
        changed_pins["prepare_summary"] = (
            history_copy, RUN07_PREPARE_REPORT_SHA256,
        )
        PRIOR_ATTEMPT_ARTIFACTS["run07"] = changed_pins
        try:
            cases.append(_expect_path_rejection(
                _prior_attempts_record,
                "historical_file_sha_tamper",
            ))
        finally:
            PRIOR_ATTEMPT_ARTIFACTS["run07"] = original_pins

    _require(len(cases) == 5 and all(case["result"] == "PASS" for case in cases),
             "T59 路径 fail-closed 负向测试未全部通过")
    return {
        "schema": "GestureForge-S2A-T59-path-fail-closed-v1",
        "status": "PASS",
        "single_file_test_method": link_method,
        "cases": cases,
    }


def _current_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False,
    )
    _require(result.returncode == 0, f"读取 Git HEAD 失败：{result.stderr.strip()}")
    return result.stdout.strip()


def _is_git_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False,
    )
    return result.returncode == 0


def _require_head_descends_from(ancestor: str, descendant: str, label: str) -> None:
    _require(bool(ancestor) and bool(descendant) and
             _is_git_ancestor(ancestor, descendant),
             f"{label} 不是冻结基线的后代：baseline={ancestor} current={descendant}")


def _verify_file_record(record: dict[str, Any], label: str) -> Path:
    if label == "T59 输入 GF8_package":
        return _verify_gf8_package_record(record, label)
    path = Path(str(record.get("path", "")))
    if not path.is_absolute():
        path = ROOT / path
    path = _guard_repo_path(path, expected_kind="file")
    if "bytes" in record:
        _require(path.stat().st_size == int(record["bytes"]),
                 f"{label} 字节数不符：{path}")
    if "sha256" in record:
        _require(_sha_file(path) == str(record["sha256"]).lower(),
                 f"{label} SHA-256 不符：{path}")
    return path


def _expected_upstream_records() -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for name, (path, expected_sha256) in UPSTREAM_BINDINGS.items():
        path = _guard_repo_path(path, expected_kind="file")
        actual_sha256 = _sha_file(path)
        if actual_sha256 != expected_sha256:
            raise T59UpstreamShaMismatch(name, path, expected_sha256, actual_sha256)
        records[name] = {
            "path": str(path),
            "sha256": expected_sha256,
        }
    return records


def _verify_upstream_records(preparation_inputs: dict[str, Any]) -> None:
    for name, (path, expected_sha256) in UPSTREAM_BINDINGS.items():
        expected = {
            "path": _safe_path_string(path, expected_kind="file"),
            "sha256": expected_sha256,
        }
        record = preparation_inputs.get(name)
        _require(record == expected,
                 f"T59 冻结上游路径/SHA-256 绑定不符：{name}")
        checked_path = _verify_file_record(
            {"path": str(record["path"])}, f"T59 冻结上游 {name}"
        )
        actual_sha256 = _sha_file(checked_path)
        if actual_sha256 != expected_sha256:
            raise T59UpstreamShaMismatch(
                name, checked_path, expected_sha256, actual_sha256
            )
        _require(checked_path == _guard_repo_path(path, expected_kind="file"),
                 f"T59 冻结上游文件复核失败：{name}")


def _verify_loader_upstream_records(input_bindings: dict[str, Any],
                                    expected: dict[str, dict[str, str]]) -> None:
    loader_to_t59 = {
        "T16_proof": "T16_conv_requant_proof",
        "T17_engine_evidence": "T17_conv_engine_evidence",
        "T20_scheduler_evidence": "T20_layer_scheduler_evidence",
        "T16_script": "T16_requant_proof_source",
        "D2_forward_reference": "D2_forward_reference_source",
    }
    for loader_key, t59_key in loader_to_t59.items():
        _require(input_bindings.get(loader_key) == expected.get(t59_key),
                 f"T54 loader 返回的上游绑定与 T59 冻结路径/SHA 不一致：{loader_key}")


def _quantization_parameter_coverage(inputs: dict[str, Any]) -> dict[str, Any]:
    channels = inputs.get("channels", [])
    mq_values = inputs.get("mq_values", ())
    _require(len(channels) == 256 and len(mq_values) == 256,
             "T23 layer35 M/Q 输入没有覆盖全部 256 个输出通道")
    digest = hashlib.sha256()
    fields = ("positive_Q", "positive_M", "negative_Q", "negative_M")
    for index, channel in enumerate(channels):
        _require(int(channel.get("channel", -1)) == index,
                 f"T23 layer35 通道索引不连续：index={index}")
        values = tuple(int(channel[field]) for field in
                       ("positive_M", "positive_Q", "negative_M", "negative_Q"))
        _require(values == tuple(mq_values[index]),
                 f"T54 loader M/Q 值与 T23 channel record 不一致：channel={index}")
        digest.update((f"{index},{int(channel['positive_Q'])},{int(channel['positive_M'])},"
                       f"{int(channel['negative_Q'])},{int(channel['negative_M'])}\n").encode("ascii"))
    t16, _ = _read_json(T16_PROOF_PATH)
    t23, _ = _read_json(T23_PATH)
    t16_layer = next((row for row in t16.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    t23_layer = next((row for row in t23.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    expected_digest = (t23_layer or {}).get("candidate_parameter_sha256")
    _require(t16_layer is not None and t23_layer is not None and
             digest.hexdigest() == expected_digest ==
             t16_layer.get("candidate_parameter_sha256") ==
             EXPECTED_PARAMETER_DIGEST_SHA256,
             "T23 layer35 Q+/M+/Q-/M- canonical digest 与冻结摘要或 T16 proof 不匹配")
    return {
        "source": str(T23_PATH.resolve()),
        "source_sha256": T23_SHA256,
        "channel_count": len(channels),
        "first_channel": int(channels[0]["channel"]),
        "last_channel": int(channels[-1]["channel"]),
        "fields_in_digest_order": list(fields),
        "canonical_parameter_digest_sha256": digest.hexdigest(),
    }


def _verify_parent() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _require_head_descends_from(BASE_HEAD, _current_head(), "当前 HEAD")
    _require(T56_REPORT.is_file() and _sha_file(T56_REPORT) == T56_REPORT_SHA256,
             "T56 canonical 报告缺失或 SHA-256 不匹配")
    parent, _ = _read_json(T56_REPORT)
    _require(parent.get("task_id") == "S2A-T56" and
             parent.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             parent.get("acceptance_status") == "PASS_INDEPENDENT_REVIEW_DATA_ONLY",
             "T56 父报告状态或独立审查状态不匹配")
    _require(parent.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=20, x=0..25; not full layer or network",
             "T56 父报告范围不匹配")
    bindings = parent.get("bindings", {})
    _require(bindings.get("fixed_points_yx") == [[20, x] for x in range(26)],
             "T56 父报告固定坐标不是 y=20、x=0..25")
    parent_sources = bindings.get("T56_source_hashes", {})
    _require(set(parent_sources) == set(T56_PARENT_SOURCES),
             "T56 父报告源码绑定集合不匹配")
    for relative, expected in parent_sources.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == str(expected).lower(),
                 f"T56 已审查源码绑定不匹配：{relative}")
    _require(parent_sources.get(T56_RUNNER.relative_to(ROOT).as_posix()) ==
             T56_RUNNER_SHA256, "T56 runner SHA-256 与冻结值不符")

    simulation = parent.get("simulation", {})
    _require(simulation.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             simulation.get("raw_int32_compares") == RAW_COUNT and
             simulation.get("int8_compares") == INT8_COUNT and
             simulation.get("progress_checkpoint_count") == 256 and
             simulation.get("raw_byte_identical_to_independent_golden") is True and
             simulation.get("int8_byte_identical_to_independent_golden") is True and
             simulation.get("raw_mismatch_bytes") == 0 and
             simulation.get("int8_mismatch_bytes") == 0 and
             simulation.get("wdb_generated") is False,
             "T56 仿真证据字段不匹配")
    t56_run = bindings.get("mcp_project_run01", {})
    _require(t56_run.get("summary_sha256") == T56_SUMMARY_SHA256,
             "T56 仿真摘要 SHA-256 与 canonical 绑定不匹配")
    summary, _ = _read_json(_verify_file_record(
        {"path": str(T56_SUMMARY), "sha256": T56_SUMMARY_SHA256},
        "T56 仿真摘要",
    ))
    _require(summary.get("status") == "PASS_SIMULATION_DATA",
             "T56 仿真摘要不是 PASS_SIMULATION_DATA")
    _require(bindings.get("G0_specification", {}).get("sha256") == G0_SHA256 and
             bindings.get("T01_manifest", {}).get("sha256") == T01_SHA256 and
             bindings.get("T23_parameter_table", {}).get("sha256") == T23_SHA256 and
             bindings.get("GF8_package", {}).get("sha256") == GF8_SHA256,
             "T56 继承的 G0/T01/T23/GF8 SHA-256 与冻结值不匹配")
    artifacts = simulation.get("artifacts", {})
    for name in ("compile.log", "elaborate.log", "simulate.log",
                 "observed_raw.bin", "observed_output.bin"):
        _require(name in artifacts, f"T56 缺少仿真工件绑定：{name}")
        _verify_file_record(artifacts[name], f"T56 {name}")
    return parent, bindings, simulation


def _load_oracle_runner(runtime_head: str) -> tuple[Any, str]:
    _require(T54_RUNNER.is_file() and _sha_file(T54_RUNNER) == T54_RUNNER_SHA256,
             "T54 独立 oracle 源码缺失或 SHA-256 不匹配")
    spec = importlib.util.spec_from_file_location("s2a_t54_reviewed_oracle_for_t58",
                                                  T54_RUNNER)
    _require(spec is not None and spec.loader is not None,
             "无法载入 T54 独立 oracle")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    historical_head = str(module.BASE_HEAD)
    module.BASE_HEAD = runtime_head
    return module, historical_head


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in T59_SOURCE_PATHS:
        path = ROOT / relative
        _require(path.is_file(), f"缺少 T59 源码：{relative}")
        hashes[relative] = _sha_file(path)
    return hashes


def _vectors_bytes(vectors: list[tuple[int, int, int, int, int, int, int, int]]) -> bytes:
    return ("".join(" ".join(str(value) for value in vector) + "\n"
                    for vector in vectors)).encode("ascii")


def _verify_tb_run_paths() -> dict[str, list[str]]:
    tb_path = _guard_repo_path(
        ROOT / "sim/tb_s2a_conv_layer35_row23_all_channels.sv",
        expected_kind="file",
    )
    source = tb_path.read_text(encoding="utf-8")
    paths = re.findall(r'\$fopen\("([^"]+)"', source)
    expected_inputs = [
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\fixture\\feature_input.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\fixture\\layer35_weights.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\fixture\\golden.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\fixture\\vectors.txt",
    ]
    expected_outputs = [
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\observed_raw.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\observed_output.bin",
    ]
    _require(len(paths) == 6 and sorted(paths) == sorted(expected_inputs + expected_outputs),
             "T59 testbench 的六个 $fopen 路径未全部固定到 run10")
    _require(not any(re.search(r"\\run0[1-9]\\", path) for path in paths),
             "T59 testbench 仍引用旧 run01-run09 路径")
    return {"fixture_inputs": expected_inputs, "observed_outputs": expected_outputs}



def _verify_t58_parent() -> dict[str, Any]:
    _require(T58_PREPARE_REPORT.is_file() and
             _sha_file(T58_PREPARE_REPORT) == T58_PREPARE_SHA256,
             "T58 run02 row22 summary SHA 不匹配")
    _require(T58_MANIFEST.is_file() and
             _sha_file(T58_MANIFEST) == T58_MANIFEST_SHA256,
             "T58 run02 row22 manifest SHA 不匹配")
    _require(T58_PROJECT_PREFLIGHT.is_file() and
             _sha_file(T58_PROJECT_PREFLIGHT) == T58_PROJECT_PREFLIGHT_SHA256,
             "T58 run02 project preflight SHA 不匹配")
    summary, summary_sha = _read_json(T58_PREPARE_REPORT)
    manifest, manifest_sha = _read_json(T58_MANIFEST)
    project_binding, project_binding_sha = _read_json(T58_PROJECT_PREFLIGHT)
    points = [[22, x] for x in range(26)]
    _require(summary.get("task_id") == "S2A-T58" and
             summary.get("run_id") == "run02" and
             summary.get("status") == "PREPARED_NOT_SIMULATED" and
             summary.get("baseline_head") == BASE_HEAD and
             summary.get("preparation_head") == "5ff5f33be90a90030dae8bfa4d3e3378a99ab080" and
             summary.get("scope") == "tiny416 cfg section36 layer35; all 256 output channels at y=22, x=0..25" and
             summary.get("bindings", {}).get("fixed_points_yx") == points,
             "T58 run02 row22 prepare 身份/范围不匹配")
    oracle = summary.get("oracle", {})
    _require(manifest.get("task_id") == "S2A-T58" and
             manifest.get("run_id") == "run02" and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("baseline_head") == BASE_HEAD and
             manifest.get("preparation_head") == summary.get("preparation_head") and
             manifest.get("fixed_points_yx") == points and manifest.get("oracle") == oracle and
             oracle.get("raw_int32_count") == RAW_COUNT and
             oracle.get("quantized_int8_count") == INT8_COUNT and
             oracle.get("d2_t23_match_count") == INT8_COUNT and
             oracle.get("combined_golden_sha256") == T58_GOLDEN_SHA256 and
             summary.get("simulation", {}).get("status") == "NOT_RUN",
             "T58 run02 row22 oracle/manifest 状态不匹配")
    _require_head_descends_from(BASE_HEAD, summary["preparation_head"],
                                "T58 run02 准备时 HEAD")
    _require_head_descends_from(summary["preparation_head"], _current_head(),
                                "当前 HEAD 相对 T58 run02 准备时 HEAD")
    sources = summary.get("bindings", {}).get("T58_source_hashes", {})
    _require(sources == T58_RUN02_SOURCE_HASHES and
             manifest.get("T58_source_hashes") == sources and
             project_binding.get("T58_source_hashes") == sources and
             manifest.get("runner_source_sha256") ==
             sources["verification/test_s2a_conv_layer35_row22_all_channels_rtl.py"],
             "T58 run02 row22 源码哈希集合不匹配")
    for rel, digest in sources.items():
        source_path = ROOT / rel
        _require(source_path.is_file() and not source_path.is_symlink() and
                 _sha_file(source_path) == str(digest).lower(),
                 f"T58 run02 源码 SHA 不匹配：{rel}")
    _require(project_binding.get("schema") ==
             "GestureForge-S2A-T58-project-preflight-v2" and
             project_binding.get("status") == "READ_ONLY_BOUND" and
             project_binding.get("task_id") == "S2A-T58" and
             project_binding.get("run_id") == "run02" and
             project_binding.get("baseline_head") == BASE_HEAD and
             project_binding.get("preparation_head") ==
             summary.get("preparation_head") and
             project_binding.get("run_directory") ==
             str(T58_PREPARE_REPORT.parent.resolve()) and
             project_binding.get("project_xpr_path") == str(XPR_PATH.resolve()) and
             project_binding.get("target_xpr_sha256_before_prepare") ==
             project_binding.get("target_xpr_sha256_after_prepare") ==
             _project_xpr_sha() and
             project_binding.get("target_xpr_unchanged") is True and
             project_binding.get("mcp_status") == "NOT_QUERIED" and
             project_binding.get("vivado_opened") is False and
             project_binding.get("vivado_cli_invoked") is False,
             "T58 run02 project binding 状态、HEAD 或真实 XPR SHA 不匹配")
    project_record = _artifact(T58_PROJECT_PREFLIGHT)
    summary_project_record = summary.get("project_preflight", {})
    _require(summary_project_record.get("path") == project_record["path"] and
             summary_project_record.get("bytes") == project_record["bytes"] and
             summary_project_record.get("sha256") == project_binding_sha and
             manifest.get("project_preflight_binding") == project_record,
             "T58 run02 summary/manifest 未绑定 project preflight")
    fixture = summary.get("fixture", {})
    mrec = fixture.get("manifest", {})
    _require(mrec.get("path") == str(T58_MANIFEST.resolve()) and
             mrec.get("sha256") == manifest_sha == T58_MANIFEST_SHA256,
             "T58 run02 summary/manifest SHA 绑定不匹配")
    files, manifest_files = fixture.get("files", {}), manifest.get("files", {})
    names = {"feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt"}
    fixture_root = T58_MANIFEST.parent
    _require(set(files) == names and set(manifest_files) == names and
             fixture.get("root") == str(fixture_root.resolve()) and
             manifest.get("fixture_root") == str(fixture_root.resolve()),
             "T58 run02 fixture 集合或根路径不匹配")
    for name in sorted(names):
        _require(files[name] == manifest_files[name],
                 f"T58 run02 fixture 双向绑定不匹配：{name}")
        verified_path = _verify_file_record(files[name], f"T58 run02 parent {name}")
        _require(verified_path.resolve() == (fixture_root / name).resolve(),
                 f"T58 run02 fixture 不属于已验证的 run02：{name}")
    golden = dict(files["golden.bin"])
    _require(golden.get("sha256") == T58_GOLDEN_SHA256 and golden.get("bytes") == GOLDEN_BYTES,
             "T58 run02 parent golden 摘要不匹配")
    return {
        "run_id": "run02",
        "preparation_head": summary["preparation_head"],
        "prepare_summary": _artifact(T58_PREPARE_REPORT),
        "fixture_manifest": _artifact(T58_MANIFEST),
        "project_preflight_binding": project_record,
        "golden": golden,
        "source_hashes": sources,
        "status": "PREPARED_NOT_SIMULATED",
        "external_verify_only": {
            "command": "python -B verification/test_s2a_conv_layer35_row22_all_channels_rtl.py --verify-only",
            "exit_code": 0,
            "raw_int32": RAW_COUNT,
            "int8": INT8_COUNT,
            "d2_t23_matches": INT8_COUNT,
            "simulation": "NOT_RUN",
        },
    }

def _runtime_preflight() -> dict[str, Any]:
    _guard_repo_path(ROOT, containment_root=ROOT, expected_kind="directory")
    _guard_repo_path(EVIDENCE_ROOT, containment_root=ROOT, expected_kind="directory")
    _guard_repo_path(RUN08_ROOT, containment_root=EVIDENCE_ROOT,
                     expected_kind="directory")
    prior_attempts = _prior_attempts_record()
    run08_contained_files = _audit_run_root_paths(RUN08_ROOT)
    expected_run08_files = sorted({
        "prepare_summary.json", "project_preflight_binding.json",
        "fixture/feature_input.bin", "fixture/layer35_weights.bin",
        "fixture/golden.bin", "fixture/vectors.txt",
        "fixture/fixture_manifest.json",
    })
    _require(run08_contained_files == expected_run08_files and
             any(attempt.get("run_id") == "run08"
                 for attempt in prior_attempts),
             "T59 preflight 未完整复核 run08 文件与路径链")
    run09_contained_files = _audit_run_root_paths(RUN09_ROOT)
    expected_run09_files = sorted({
        "prepare_summary.json", "project_preflight_binding.json",
        "fixture/feature_input.bin", "fixture/layer35_weights.bin",
        "fixture/golden.bin", "fixture/vectors.txt",
        "fixture/fixture_manifest.json",
    })
    _require(run09_contained_files == expected_run09_files and
             any(attempt.get("run_id") == "run09"
                 for attempt in prior_attempts),
             "T59 preflight 未完整复核保留的 run09 文件与路径链")
    _guard_repo_path(RUN_ROOT, containment_root=EVIDENCE_ROOT,
                     must_exist=False)
    root_binding_sha256 = _verify_root_binding()
    executable = "powershell.exe"
    result = subprocess.run(
        [executable, "-NoProfile", "-NonInteractive", "-Command",
         POWERSHELL_PREFLIGHT],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=30,
    )
    _require(result.returncode == 0,
             f"PowerShell 路径/进程预检失败：{result.stderr.strip()}")
    try:
        snapshot = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise T59Error(f"PowerShell 预检输出不是 JSON：{error}") from error
    _require(isinstance(snapshot, dict) and
             snapshot.get("path_chain_valid") is True and
             snapshot.get("checked_xpr") == str(XPR_PATH.resolve()) and
             snapshot.get("evidence_root") == str(EVIDENCE_ROOT.resolve()) and
             snapshot.get("run10_path") == str(RUN_ROOT) and
             snapshot.get("target_absent") is True and
             snapshot.get("existing_run01") is True and
             snapshot.get("existing_run02") is True and
             snapshot.get("existing_run03") is True and
             snapshot.get("existing_run04") is True and
             snapshot.get("existing_run05") is True and
             snapshot.get("existing_run06") is True and
             snapshot.get("existing_run07") is True and
             snapshot.get("existing_run08") is True and
             snapshot.get("existing_run09") is True and
             snapshot.get("existing_run10") is False and
             snapshot.get("root_binding_sha256") == root_binding_sha256 and
             snapshot.get("root_binding_sha256") == ROOT_PROJECT_PREFLIGHT_SHA256 and
             tuple(snapshot.get("process_names", ())) == PROCESS_NAMES and
             snapshot.get("processes_before_prepare") == [],
              "T59 路径/reparse 或 8 类 Vivado/XSim 进程门禁不通过")
    snapshot["run08_contained_files"] = run08_contained_files
    snapshot["run08_pinned_artifact_count"] = len(next(
        attempt for attempt in prior_attempts if attempt.get("run_id") == "run08"
    )["artifacts"])
    snapshot["run09_contained_files"] = run09_contained_files
    snapshot["run09_pinned_artifact_count"] = len(next(
        attempt for attempt in prior_attempts if attempt.get("run_id") == "run09"
    )["artifacts"])
    snapshot["powershell_exit_code"] = result.returncode
    snapshot["mcp_status"] = "NOT_QUERIED"
    return snapshot


def _runtime_process_snapshot() -> dict[str, Any]:
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
         POWERSHELL_PROCESS_SNAPSHOT],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=30,
    )
    _require(result.returncode == 0,
             f"PowerShell Vivado/XSim 进程快照失败：{result.stderr.strip()}")
    try:
        snapshot = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise T59Error(f"PowerShell 进程快照不是 JSON：{error}") from error
    _require(isinstance(snapshot, dict) and
             tuple(snapshot.get("process_names", ())) == PROCESS_NAMES and
             snapshot.get("processes") == [],
             "T59 当前存在 Vivado/XSim 相关进程，拒绝继续")
    return {
        "process_names": list(PROCESS_NAMES),
        "processes": snapshot["processes"],
        "powershell_exit_code": result.returncode,
    }


def _prior_attempts_record() -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for run_id, artifact_pins in PRIOR_ATTEMPT_ARTIFACTS.items():
        artifacts: dict[str, dict[str, Any]] = {}
        for name, (path, expected_sha256) in artifact_pins.items():
            path = _guard_repo_path(
                path, containment_root=EVIDENCE_ROOT,
                expected_kind="file",
            )
            _require(_sha_file(path) == expected_sha256,
                     f"T59 {run_id} 历史工件 SHA-256 已变化：{path}")
            artifacts[name] = _artifact(path)
        records[run_id] = {
            "task_id": "S2A-T59",
            "run_id": run_id,
            "artifacts": artifacts,
        }
    run07_summary, _ = _read_json(RUN07_PREPARE_REPORT)
    run07_manifest, _ = _read_json(RUN07_FIXTURE_MANIFEST)
    run07_binding, _ = _read_json(RUN07_PROJECT_PREFLIGHT)
    run07_audit, _ = _read_json(RUN07_AUDIT)
    run07_fixture_files = {
        name: (EVIDENCE_ROOT / "run07/fixture" / name)
        for name in ("feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt")
    }
    run07_fixture_hashes = {
        "feature_input.bin": RUN07_FEATURE_SHA256,
        "layer35_weights.bin": RUN07_WEIGHTS_SHA256,
        "golden.bin": RUN07_GOLDEN_SHA256,
        "vectors.txt": RUN07_VECTORS_SHA256,
    }
    _require(
        run07_summary.get("task_id") == "S2A-T59" and
        run07_summary.get("run_id") == "run07" and
        run07_summary.get("status") == "PREPARED_NOT_SIMULATED" and
        run07_manifest.get("task_id") == "S2A-T59" and
        run07_manifest.get("run_id") == "run07" and
        run07_manifest.get("status") == "PREPARED_NOT_SIMULATED" and
        run07_binding.get("task_id") == "S2A-T59" and
        run07_binding.get("run_id") == "run07" and
        run07_summary.get("schema") == "GestureForge-S2A-T59-preparation-summary-v6" and
        run07_manifest.get("schema") == "GestureForge-S2A-T59-fixture-manifest-v6" and
        run07_summary.get("bindings", {}).get("T59_source_hashes") == RUN07_SOURCE_HASHES and
        run07_manifest.get("T59_source_hashes") == RUN07_SOURCE_HASHES and
        run07_binding.get("T59_source_hashes") == RUN07_SOURCE_HASHES and
        run07_summary.get("scope") ==
        "tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25" and
        run07_summary.get("bindings", {}).get("fixed_points_yx") ==
        [[23, x] for x in range(26)] and
        run07_manifest.get("fixed_points_yx") == [[23, x] for x in range(26)] and
        run07_summary.get("T58_parent") == run07_manifest.get("T58_parent") and
        run07_summary.get("fail_closed_audit") ==
        run07_manifest.get("fail_closed_audit") ==
        _artifact(RUN07_AUDIT) and
        run07_binding.get("run_directory") ==
        str((EVIDENCE_ROOT / "run07").resolve()) and
        run07_manifest.get("runner_source_sha256") ==
        RUN07_SOURCE_HASHES[T59_RUNNER_RELATIVE] and
        run07_summary.get("oracle", {}).get("raw_int32_count") == RAW_COUNT and
        run07_summary.get("oracle", {}).get("quantized_int8_count") == INT8_COUNT and
        run07_summary.get("oracle", {}).get("d2_t23_match_count") == INT8_COUNT and
        run07_manifest.get("oracle") == run07_summary.get("oracle") and
        run07_summary.get("simulation", {}).get("status") == "NOT_RUN",
        "T59 run07 历史摘要、manifest、旧源码哈希或准备状态不匹配")
    _require(
        _sha_file(T58_RUN01_PREPARE_REPORT) == T58_RUN01_PREPARE_SHA256 and
        _sha_file(T58_RUN01_PREPARE_REPORT.parent / "fixture/fixture_manifest.json") ==
        T58_RUN01_MANIFEST_SHA256 and
        run07_summary.get("T58_parent", {}).get("prepare_summary", {}).get("path") ==
        str(T58_RUN01_PREPARE_REPORT.resolve()) and
        run07_summary.get("T58_parent", {}).get("prepare_summary", {}).get("sha256") ==
        T58_RUN01_PREPARE_SHA256 and
        run07_summary.get("T58_parent", {}).get("fixture_manifest", {}).get("path") ==
        str((T58_RUN01_PREPARE_REPORT.parent / "fixture/fixture_manifest.json").resolve()) and
        run07_summary.get("T58_parent", {}).get("fixture_manifest", {}).get("sha256") ==
        T58_RUN01_MANIFEST_SHA256,
        "T59 run07 历史摘要的 T58 run01 父绑定不匹配")
    old_t58_summary, _ = _read_json(T58_RUN01_PREPARE_REPORT)
    _require(old_t58_summary.get("bindings", {}).get("T58_source_hashes", {}).get(
        "sim/tb_s2a_conv_layer35_row22_all_channels.sv") ==
        T58_RUN01_ROW22_TB_SHA256 and
        run07_audit.get("task_id") == "S2A-T59" and
        run07_audit.get("run_id") == "run07" and
        run07_audit.get("status") == "PASS" and
        run07_audit.get("audit_script_sha256") ==
        RUN07_SOURCE_HASHES["verification/test_s2a_t59_upstream_fail_closed.py"] and
        len(run07_audit.get("cases", [])) == len(UPSTREAM_BINDINGS) and
        all(case.get("result") == "PASS" for case in run07_audit.get("cases", [])),
        "T59 run07 历史 T58 SHA 或 6 项 fail-closed 结果不匹配")
    _require(
        set(run07_manifest.get("files", {})) == set(run07_fixture_files) and
        all(
            run07_manifest["files"][name].get("path") == str(path.resolve()) and
            run07_manifest["files"][name].get("sha256") ==
            run07_fixture_hashes[name]
            for name, path in run07_fixture_files.items()
        ),
        "T59 run07 历史 fixture 路径或 SHA-256 不匹配")
    records["run07"].update({
        "status": "PREPARED_NOT_SIMULATED",
        "audit_status": "PASS",
        "audit_case_count": len(run07_audit.get("cases", [])),
        "historical_verify_only_observation": {
            "status": "FAIL",
            "actual_exit_code": 1,
            "reason_code": "T58_RUN01_ROW22_SOURCE_SHA_MISMATCH",
            "expected_row22_tb_sha256": T58_RUN01_ROW22_TB_SHA256,
            "observed_row22_tb_sha256": T58_RUN02_SOURCE_HASHES[
                "sim/tb_s2a_conv_layer35_row22_all_channels.sv"],
            "T59_runner_sha256": RUN07_SOURCE_HASHES[T59_RUNNER_RELATIVE],
            "T59_testbench_sha256":
                RUN07_SOURCE_HASHES["sim/tb_s2a_conv_layer35_row23_all_channels.sv"],
            "observation_source": "父任务在 run08 修复前提供的 G0 诊断；不是 run07 原件中的仿真或验收记录",
        },
    })
    run08_summary, _ = _read_json(RUN08_PREPARE_REPORT)
    run08_manifest, _ = _read_json(RUN08_FIXTURE_MANIFEST)
    run08_binding, _ = _read_json(RUN08_PROJECT_PREFLIGHT)
    run08_fixture_paths = {
        name: RUN08_ROOT / "fixture" / name
        for name in ("feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt")
    }
    run08_fixture_hashes = {
        "feature_input.bin": RUN08_FEATURE_SHA256,
        "layer35_weights.bin": RUN08_WEIGHTS_SHA256,
        "golden.bin": RUN08_GOLDEN_SHA256,
        "vectors.txt": RUN08_VECTORS_SHA256,
    }
    run08_artifact_files = _audit_run_root_paths(RUN08_ROOT)
    _require(
        run08_summary.get("task_id") == "S2A-T59" and
        run08_summary.get("run_id") == "run08" and
        run08_summary.get("schema") == "GestureForge-S2A-T59-preparation-summary-v7" and
        run08_summary.get("status") == "PREPARED_NOT_SIMULATED" and
        run08_summary.get("baseline_head") == BASE_HEAD and
        run08_summary.get("scope") ==
        "tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25" and
        run08_summary.get("oracle", {}).get("raw_int32_count") == RAW_COUNT and
        run08_summary.get("oracle", {}).get("quantized_int8_count") == INT8_COUNT and
        run08_summary.get("oracle", {}).get("d2_t23_match_count") == INT8_COUNT and
        run08_summary.get("simulation", {}).get("status") == "NOT_RUN" and
        run08_summary.get("bindings", {}).get("T59_source_hashes") == RUN08_SOURCE_HASHES and
        run08_manifest.get("task_id") == "S2A-T59" and
        run08_manifest.get("run_id") == "run08" and
        run08_manifest.get("schema") == "GestureForge-S2A-T59-fixture-manifest-v7" and
        run08_manifest.get("status") == "PREPARED_NOT_SIMULATED" and
        run08_manifest.get("T59_source_hashes") == RUN08_SOURCE_HASHES and
        run08_binding.get("task_id") == "S2A-T59" and
        run08_binding.get("run_id") == "run08" and
        run08_binding.get("schema") == "GestureForge-S2A-T59-project-preflight-v6" and
        run08_binding.get("T59_source_hashes") == RUN08_SOURCE_HASHES and
        run08_manifest.get("runner_source_sha256") ==
        RUN08_SOURCE_HASHES[T59_RUNNER_RELATIVE] and
        run08_summary.get("T58_parent") == run08_manifest.get("T58_parent") and
        run08_summary.get("fail_closed_audit") ==
        run08_manifest.get("fail_closed_audit") ==
        _artifact(RUN07_AUDIT) and
        run08_manifest.get("fixed_points_yx") == [[23, x] for x in range(26)],
        "T59 run08 历史摘要、manifest、来源哈希或状态不匹配")
    _require(
        run08_artifact_files == sorted({
            "prepare_summary.json", "project_preflight_binding.json",
            "fixture/feature_input.bin", "fixture/layer35_weights.bin",
            "fixture/golden.bin", "fixture/vectors.txt",
            "fixture/fixture_manifest.json",
        }) and
        set(run08_manifest.get("files", {})) == set(run08_fixture_paths) and
        all(
            run08_manifest["files"][name].get("path") ==
            _safe_path_string(path, containment_root=RUN08_ROOT, expected_kind="file") and
            run08_manifest["files"][name].get("sha256") == run08_fixture_hashes[name]
            for name, path in run08_fixture_paths.items()
        ),
        "T59 run08 历史目录路径、文件集合或 fixture SHA-256 不匹配")
    run08_verify_report = _run08_unverified_source_report(
        run08_artifact_files)
    run08_schema_audit = _run08_source_report_schema_negative_test(
        run08_verify_report)
    records["run08"].update({
        "status": "PREPARED_NOT_SIMULATED",
        "historical_verify_only": run08_verify_report,
        "history_schema_audit": run08_schema_audit,
    })
    run09_summary, _ = _read_json(RUN09_PREPARE_REPORT)
    run09_manifest, _ = _read_json(RUN09_FIXTURE_MANIFEST)
    run09_binding, _ = _read_json(RUN09_PROJECT_PREFLIGHT)
    run09_fixture_paths = {
        name: RUN09_ROOT / "fixture" / name
        for name in ("feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt")
    }
    run09_fixture_hashes = {
        "feature_input.bin": RUN09_FEATURE_SHA256,
        "layer35_weights.bin": RUN09_WEIGHTS_SHA256,
        "golden.bin": RUN09_GOLDEN_SHA256,
        "vectors.txt": RUN09_VECTORS_SHA256,
    }
    run09_tb_paths = {
        "fixture_inputs": [
            r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run09\\fixture\\feature_input.bin",
            r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run09\\fixture\\layer35_weights.bin",
            r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run09\\fixture\\golden.bin",
            r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run09\\fixture\\vectors.txt",
        ],
        "observed_outputs": [
            r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run09\\observed_raw.bin",
            r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run09\\observed_output.bin",
        ],
    }
    run09_artifact_files = _audit_run_root_paths(RUN09_ROOT)
    _require(
        run09_summary.get("schema") ==
        "GestureForge-S2A-T59-preparation-summary-v8" and
        run09_summary.get("task_id") == "S2A-T59" and
        run09_summary.get("run_id") == "run09" and
        run09_summary.get("status") == "PREPARED_NOT_SIMULATED" and
        run09_summary.get("baseline_head") == BASE_HEAD and
        run09_summary.get("scope") ==
        "tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25" and
        run09_summary.get("tb_io_paths") == run09_tb_paths and
        run09_summary.get("bindings", {}).get("fixed_points_yx") ==
        [[23, x] for x in range(26)] and
        run09_summary.get("oracle", {}).get("raw_int32_count") == RAW_COUNT and
        run09_summary.get("oracle", {}).get("quantized_int8_count") == INT8_COUNT and
        run09_summary.get("oracle", {}).get("d2_t23_match_count") == INT8_COUNT and
        run09_summary.get("simulation", {}).get("status") == "NOT_RUN" and
        run09_summary.get("bindings", {}).get("T59_source_hashes") ==
        RUN09_SOURCE_HASHES and
        run09_manifest.get("schema") ==
        "GestureForge-S2A-T59-fixture-manifest-v8" and
        run09_manifest.get("task_id") == "S2A-T59" and
        run09_manifest.get("run_id") == "run09" and
        run09_manifest.get("status") == "PREPARED_NOT_SIMULATED" and
        run09_manifest.get("T59_source_hashes") == RUN09_SOURCE_HASHES and
        run09_manifest.get("runner_source_sha256") ==
        RUN09_SOURCE_HASHES[T59_RUNNER_RELATIVE] and
        run09_manifest.get("tb_io_paths") == run09_tb_paths and
        run09_binding.get("schema") ==
        "GestureForge-S2A-T59-project-preflight-v7" and
        run09_binding.get("task_id") == "S2A-T59" and
        run09_binding.get("run_id") == "run09" and
        run09_binding.get("T59_source_hashes") == RUN09_SOURCE_HASHES and
        run09_binding.get("run_directory") == str(RUN09_ROOT.resolve()) and
        run09_summary.get("T58_parent") == run09_manifest.get("T58_parent") and
        run09_manifest.get("fixed_points_yx") == [[23, x] for x in range(26)],
        "T59 run09 历史准备摘要、来源哈希、路径或范围不匹配")
    _require(
        run09_artifact_files == sorted({
            "prepare_summary.json", "project_preflight_binding.json",
            "fixture/feature_input.bin", "fixture/layer35_weights.bin",
            "fixture/golden.bin", "fixture/vectors.txt",
            "fixture/fixture_manifest.json",
        }) and
        set(run09_manifest.get("files", {})) == set(run09_fixture_paths) and
        all(
            run09_manifest["files"][name].get("path") ==
            _safe_path_string(path, containment_root=RUN09_ROOT, expected_kind="file") and
            run09_manifest["files"][name].get("sha256") == run09_fixture_hashes[name]
            for name, path in run09_fixture_paths.items()
        ),
        "T59 run09 历史目录路径、文件集合或 fixture SHA-256 不匹配")
    run09_verify_report = _run09_unverified_source_report(run09_artifact_files)
    run09_schema_audit = _run09_source_report_schema_negative_test(
        run09_verify_report)
    records["run09"].update({
        "status": "PREPARED_NOT_SIMULATED",
        "verify_only": run09_verify_report,
        "history_schema_audit": run09_schema_audit,
    })
    run05_audit, _ = _read_json(RUN05_FAILED_AUDIT)
    run05_cases = run05_audit.get("cases", [])
    _require(run05_audit.get("status") == "FAIL" and
             run05_audit.get("run_id") == "run05" and
             len(run05_cases) == len(UPSTREAM_BINDINGS) and
             all(case.get("result") == "FAIL" and
                 case.get("actual_exit_code") == 1 and
                 case.get("failure_record") is None
                 for case in run05_cases),
             "T59 run05 保留的 FAIL 审计内容不匹配")
    run06_audit, _ = _read_json(RUN06_AUDIT)
    run06_cases = run06_audit.get("cases", [])
    _require(run06_audit.get("status") == "PASS" and
             run06_audit.get("run_id") == "run06" and
             len(run06_cases) == len(UPSTREAM_BINDINGS) and
             {case.get("dependency_key") for case in run06_cases} ==
             set(UPSTREAM_BINDINGS) and
             all(case.get("result") == "PASS" and
                 case.get("actual_exit_code") == 1 and
                 case.get("failure_record", {}).get("code") ==
                 "EXPECTED_UPSTREAM_SHA_MISMATCH" and
                 case.get("failure_record", {}).get("dependency_key") ==
                 case.get("dependency_key") and
                 case.get("failure_record", {}).get("dependency_path") ==
                 case.get("temp_dependency_path") and
                 case.get("failure_record", {}).get("expected_sha256") ==
                 case.get("expected_sha256") and
                 case.get("failure_record", {}).get("actual_sha256") ==
                 case.get("mutated_sha256")
                 for case in run06_cases),
             "T59 run06 保留的 6/6 PASS 结构化审计内容不匹配")
    records["run05"].update({
        "status": "FAIL",
        "prepare_status": "PREPARED_NOT_SIMULATED",
        "audit_status": "FAIL",
        "audit_case_count": len(run05_cases),
        "audit_actual_exit_codes": [case["actual_exit_code"] for case in run05_cases],
        "failure_reason": "旧审计未取得结构化错误记录，六项均保留为 FAIL",
    })
    records["run06"].update({
        "status": "FAIL",
        "prepare_status": "PREPARED_NOT_SIMULATED",
        "audit_status": "PASS",
        "audit_case_count": len(run06_cases),
        "audit_actual_exit_codes": [case["actual_exit_code"] for case in run06_cases],
        "verify_only": {
            "status": "FAIL",
            "actual_exit_code": 1,
            "expected_exit_code": 2,
            "reason_code": "STALE_AUDIT_EXIT_CODE_EXPECTATION",
        },
    })
    return [records["run05"], records["run06"], records["run07"],
            records["run08"], records["run09"]]


def _run09_unverified_source_report(
        run09_artifact_files: list[str]) -> dict[str, Any]:
    """保留 run09 旧 runner 声明，但明确其不是原始执行记录。"""

    return {
        "status": "UNVERIFIED_SOURCE_REPORT",
        "verified": False,
        "source_report": {
            "type": "RUN09_PREPARATION_RUNNER_DECLARATION",
            "runner_path": T59_RUNNER_RELATIVE,
            "runner_sha256": RUN09_SOURCE_HASHES[T59_RUNNER_RELATIVE],
            "invocation_independently_confirmed": False,
        },
        "reported_claim": {
            "reported_exit_code": 1,
            "reported_reason_code":
                "FIXED_GF8_INPUT_REJECTED_BY_REPO_ONLY_GUARD",
            "reported_observed_path":
                r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8",
        },
        "raw_command_output": {
            "status": "NOT_PRESERVED",
            "path": None,
            "bytes": None,
            "sha256": None,
        },
        "run09_artifact_files": run09_artifact_files,
    }


def _validate_run09_source_report(record: dict[str, Any],
                                  expected_files: list[str]) -> None:
    """拒绝把 run09 的无原始日志历史声明标成实测结果。"""

    _require(set(record) == {
        "status", "verified", "source_report", "reported_claim",
        "raw_command_output", "run09_artifact_files",
    }, "T59 run09 未验证来源报告字段集合异常")
    _require(record.get("status") == "UNVERIFIED_SOURCE_REPORT" and
             record.get("verified") is False,
             "T59 run09 来源报告不得标为已验证")
    _require(record.get("source_report") == {
        "type": "RUN09_PREPARATION_RUNNER_DECLARATION",
        "runner_path": T59_RUNNER_RELATIVE,
        "runner_sha256": RUN09_SOURCE_HASHES[T59_RUNNER_RELATIVE],
        "invocation_independently_confirmed": False,
    }, "T59 run09 来源报告必须说明它不是独立执行记录")
    _require(record.get("reported_claim") == {
        "reported_exit_code": 1,
        "reported_reason_code":
            "FIXED_GF8_INPUT_REJECTED_BY_REPO_ONLY_GUARD",
        "reported_observed_path":
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8",
    }, "T59 run09 未验证来源报告中的声明字段不匹配")
    _require(record.get("raw_command_output") == {
        "status": "NOT_PRESERVED",
        "path": None,
        "bytes": None,
        "sha256": None,
    }, "T59 run09 不得声称存在未绑定的原始命令输出")
    _require(record.get("run09_artifact_files") == expected_files and
             not any("stderr" in name.lower() or "verify" in name.lower()
                     for name in expected_files),
             "T59 run09 声明与已核验文件清单不符")


def _run09_source_report_schema_negative_test(
        valid_record: dict[str, Any]) -> dict[str, Any]:
    """验证旧格式的实测断言和未绑定日志声明会被拒绝。"""

    expected_files = valid_record.get("run09_artifact_files")
    _require(isinstance(expected_files, list),
             "T59 run09 schema 负测缺少原始目录清单")
    _validate_run09_source_report(valid_record, expected_files)
    mutations = (
        ("reject_actual_exit_code", lambda value: value.update(
            {"actual_exit_code": 1})),
        ("reject_unbound_stderr_claim", lambda value: value[
            "raw_command_output"].update({
                "status": "PRESERVED", "path": "verify.stderr",
                "bytes": 12, "sha256": "0" * 64,
            })),
        ("reject_verified_status", lambda value: value.update(
            {"verified": True})),
    )
    results = []
    for case_id, mutate in mutations:
        candidate = copy.deepcopy(valid_record)
        mutate(candidate)
        try:
            _validate_run09_source_report(candidate, expected_files)
        except T59Error:
            results.append({"case_id": case_id, "result": "PASS"})
        else:
            raise T59Error(
                f"T59 run09 来源报告 schema 负测未拒绝：{case_id}")
    return {
        "schema": "GestureForge-S2A-T59-run09-unverified-source-report-v1",
        "status": "PASS",
        "case_count": len(results),
        "cases": results,
    }


def _run08_unverified_source_report(
        run08_artifact_files: list[str]) -> dict[str, Any]:
    """保留 run08 旧脚本中的审核声明，但明确没有原始记录。"""

    return {
        "status": "UNVERIFIED_SOURCE_REPORT",
        "verified": False,
        "source_report": {
            "type": "RUN08_PREPARATION_RUNNER_DECLARATION",
            "runner_path": T59_RUNNER_RELATIVE,
            "runner_sha256": RUN08_SOURCE_HASHES[T59_RUNNER_RELATIVE],
            "invocation_independently_confirmed": False,
        },
        "reported_claim": {
            "reported_verify_only_status": "PASS",
            "reported_exit_code": 0,
            "reported_result": "PREPARED_NOT_SIMULATED",
            "reported_simulation": "NOT_RUN",
            "reported_review_status": "CHANGES_REQUIRED",
            "reported_review_finding":
                "旧 attempt 缺少逐组件 reparse 与 repo/run-root containment 门禁",
        },
        "raw_command_output": {
            "status": "NOT_PRESERVED",
            "path": None,
            "bytes": None,
            "sha256": None,
        },
        "review_artifact": {
            "status": "NOT_PRESERVED",
            "path": None,
            "bytes": None,
            "sha256": None,
        },
        "run08_artifact_files": run08_artifact_files,
    }


def _validate_run08_source_report(record: dict[str, Any],
                                  expected_files: list[str]) -> None:
    """拒绝把 run08 无原件的历史声明标成实测或审查结论。"""

    _require(set(record) == {
        "status", "verified", "source_report", "reported_claim",
        "raw_command_output", "review_artifact", "run08_artifact_files",
    }, "T59 run08 未验证来源报告字段集合异常")
    _require(record.get("status") == "UNVERIFIED_SOURCE_REPORT" and
             record.get("verified") is False,
             "T59 run08 来源报告不得标为已验证")
    _require(record.get("source_report") == {
        "type": "RUN08_PREPARATION_RUNNER_DECLARATION",
        "runner_path": T59_RUNNER_RELATIVE,
        "runner_sha256": RUN08_SOURCE_HASHES[T59_RUNNER_RELATIVE],
        "invocation_independently_confirmed": False,
    }, "T59 run08 来源报告必须说明它不是独立执行或审核记录")
    _require(record.get("reported_claim") == {
        "reported_verify_only_status": "PASS",
        "reported_exit_code": 0,
        "reported_result": "PREPARED_NOT_SIMULATED",
        "reported_simulation": "NOT_RUN",
        "reported_review_status": "CHANGES_REQUIRED",
        "reported_review_finding":
            "旧 attempt 缺少逐组件 reparse 与 repo/run-root containment 门禁",
    }, "T59 run08 来源报告中的声明字段不匹配")
    missing_record = {
        "status": "NOT_PRESERVED",
        "path": None,
        "bytes": None,
        "sha256": None,
    }
    _require(record.get("raw_command_output") == missing_record and
             record.get("review_artifact") == missing_record,
             "T59 run08 不得声称存在未绑定的原始命令输出或审查报告")
    _require(record.get("run08_artifact_files") == expected_files and
             not any("stderr" in name.lower() or "verify" in name.lower() or
                     "review" in name.lower() or "audit" in name.lower()
                     for name in expected_files),
             "T59 run08 来源声明与已核验文件清单不符")


def _run08_source_report_schema_negative_test(
        valid_record: dict[str, Any]) -> dict[str, Any]:
    """验证 run08 声明不能升级成 PASS、审核结论或实测退出码。"""

    expected_files = valid_record.get("run08_artifact_files")
    _require(isinstance(expected_files, list),
             "T59 run08 schema 负测缺少原始目录清单")
    _validate_run08_source_report(valid_record, expected_files)
    mutations = (
        ("reject_measured_pass", lambda value: value.update(
            {"status": "PASS"})),
        ("reject_actual_exit_code", lambda value: value.update(
            {"actual_exit_code": 0})),
        ("reject_review_status_upgrade", lambda value: value.update(
            {"review_status": "CHANGES_REQUIRED"})),
        ("reject_unbound_verify_output", lambda value: value[
            "raw_command_output"].update({
                "status": "PRESERVED", "path": "verify.stdout",
                "bytes": 1, "sha256": "0" * 64,
            })),
        ("reject_verified_upgrade", lambda value: value.update(
            {"verified": True})),
    )
    results = []
    for case_id, mutate in mutations:
        candidate = copy.deepcopy(valid_record)
        mutate(candidate)
        try:
            _validate_run08_source_report(candidate, expected_files)
        except T59Error:
            results.append({"case_id": case_id, "result": "PASS"})
        else:
            raise T59Error(
                f"T59 run08 来源报告 schema 负测未拒绝：{case_id}")
    return {
        "schema": "GestureForge-S2A-T59-run08-unverified-source-report-v1",
        "status": "PASS",
        "case_count": len(results),
        "cases": results,
    }

def _ensure_run10_absent() -> None:
    _guard_repo_path(EVIDENCE_ROOT, containment_root=ROOT,
                     expected_kind="directory")
    _guard_repo_path(RUN_ROOT, containment_root=EVIDENCE_ROOT,
                     must_exist=False)
    _verify_root_binding()
    _prior_attempts_record()
    expected_root_entries = {
        "project_preflight_binding.json", "run01", "run02", "run03", "run04",
        "run05", "run06", "run07", "run08", "run09",
    }
    actual_root_entries = {entry.name for entry in EVIDENCE_ROOT.iterdir()}
    _require(actual_root_entries == expected_root_entries,
             "T59 根目录内容与 run01-run09/根级旧绑定不一致，拒绝创建 run10")

def _project_xpr_sha() -> str:
    _require(XPR_PATH.is_file(), f"目标 XPR 缺失：{XPR_PATH}")
    return _sha_file(XPR_PATH)


def _prepare() -> dict[str, Any]:
    parent, parent_bindings, parent_simulation = _verify_parent()
    t58_parent = _verify_t58_parent()
    tb_io_paths = _verify_tb_run_paths()
    runtime = _runtime_preflight()
    _ensure_run10_absent()
    path_guard_audit = _run_path_guard_negative_tests()
    prior_attempts = _prior_attempts_record()
    historical_audit_record = next(
        attempt["artifacts"]["upstream_fail_closed_audit"]
        for attempt in prior_attempts if attempt["run_id"] == "run07"
    )
    current_head = _current_head()
    _require_head_descends_from(BASE_HEAD, current_head, "T59 运行 HEAD")
    xpr_sha_before = _project_xpr_sha()

    oracle_runner, historical_oracle_head = _load_oracle_runner(current_head)
    inputs = oracle_runner._load_frozen_inputs()
    input_bindings = inputs["bindings"]
    upstream_records = _expected_upstream_records()
    _verify_loader_upstream_records(input_bindings, upstream_records)
    parameter_coverage = _quantization_parameter_coverage(inputs)
    _require(input_bindings["T01_manifest"]["sha256"] == T01_SHA256 and
             input_bindings["T23_parameter_table"]["sha256"] == T23_SHA256 and
             input_bindings["GF8_package"]["sha256"] == GF8_SHA256,
             "独立 oracle 返回的模型/量化输入绑定不匹配")
    _require(inputs["weight_sha256"] ==
             parent_bindings["weight_layer35"]["sha256"] and
             len(inputs["weight_bytes"]) == WEIGHT_BYTES,
             "layer35 GF8 权重与 T56 继承权重不一致")
    oracle = oracle_runner._build_oracle(inputs, progress=True, points=POINTS)
    _require(len(oracle["feature"]) == FEATURE_BYTES and
             len(oracle["raw_values"]) == RAW_COUNT and
             len(oracle["quantized_values"]) == INT8_COUNT and
             len(oracle["combined_golden"]) == GOLDEN_BYTES,
             "T59 oracle 输出长度或比较数错误")
    _require(oracle["oracle"]["raw_int32_count"] == RAW_COUNT and
             oracle["oracle"]["quantized_int8_count"] == INT8_COUNT and
             oracle["oracle"]["d2_t23_match_count"] == INT8_COUNT and
             all(y == 23 for y, _ in POINTS) and
             tuple(x for _, x in POINTS) == tuple(range(26)),
             "T59 oracle 点集或 raw/INT8/D2 逐项计数错误")

    source_hashes = _source_hashes()
    blobs = {
        "feature_input.bin": oracle["feature"],
        "layer35_weights.bin": inputs["weight_bytes"],
        "golden.bin": oracle["combined_golden"],
        "vectors.txt": _vectors_bytes(oracle["vectors"]),
    }
    expected_sizes = {
        "feature_input.bin": FEATURE_BYTES,
        "layer35_weights.bin": WEIGHT_BYTES,
        "golden.bin": GOLDEN_BYTES,
    }
    for name, content in blobs.items():
        _require(name not in expected_sizes or
                 len(content) == expected_sizes[name],
                 f"T59 fixture 长度错误：{name}")

    _ensure_run10_absent()
    _guard_repo_path(RUN_ROOT, containment_root=EVIDENCE_ROOT,
                     must_exist=False)
    RUN_ROOT.mkdir(parents=False, exist_ok=False)
    _guard_repo_path(FIXTURE_ROOT, containment_root=RUN_ROOT,
                     must_exist=False, expected_kind="directory")
    FIXTURE_ROOT.mkdir(parents=False, exist_ok=False)
    for name, content in blobs.items():
        with (FIXTURE_ROOT / name).open("xb") as stream:
            stream.write(content)

    fixture_files = {
        name: _artifact(FIXTURE_ROOT / name)
        for name in sorted(blobs)
    }
    preparation_inputs = {
        "T56_parent_report": {
            "path": str(T56_REPORT.resolve()),
            "sha256": T56_REPORT_SHA256,
        },
        "T56_summary": {
            "path": str(T56_SUMMARY.resolve()),
            "sha256": T56_SUMMARY_SHA256,
        },
        "T58_parent_prepare_summary": t58_parent["prepare_summary"],
        "T58_parent_fixture_manifest": t58_parent["fixture_manifest"],
        "T58_parent_golden": t58_parent["golden"],
        "T58_parent_project_preflight_binding":
            t58_parent["project_preflight_binding"],
        "G0_specification": {"path": str(G0_PATH.resolve()), "sha256": G0_SHA256},
        "T01_manifest": input_bindings["T01_manifest"],
        "T23_parameter_table": input_bindings["T23_parameter_table"],
        "GF8_package": input_bindings["GF8_package"],
        "weight_layer35": {
            "byte_offset": inputs["layer35_weight_offset"],
            "bytes": len(inputs["weight_bytes"]),
            "sha256": inputs["weight_sha256"],
        },
        "oracle_source": {
            "path": str(T54_RUNNER.resolve()),
            "sha256": T54_RUNNER_SHA256,
        },
        **upstream_records,
    }
    _verify_upstream_records(preparation_inputs)
    runtime["processes_after_prepare"] = _runtime_process_snapshot()
    xpr_sha_after = _project_xpr_sha()
    _require(xpr_sha_after == xpr_sha_before,
             "T59 prepare 期间真实 XPR SHA-256 发生变化")
    _require(_current_head() == current_head,
             "T59 prepare 期间 Git HEAD 发生变化")
    preflight = {
        "schema": "GestureForge-S2A-T59-project-preflight-v7",
        "status": "READ_ONLY_BOUND",
        "task_id": "S2A-T59",
        "run_id": "run10",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "run_directory": str(RUN_ROOT.resolve()),
        "prior_attempts": prior_attempts,
        "path_guard_audit": path_guard_audit,
        "project_name": "AX7Z020_Gesture",
        "project_xpr_path": str(XPR_PATH.resolve()),
        "target_xpr_sha256_before_prepare": xpr_sha_before,
        "target_xpr_sha256_after_prepare": xpr_sha_after,
        "target_xpr_unchanged": True,
        "T59_source_hashes": source_hashes,
        "preparation_inputs": preparation_inputs,
        "runtime_preflight": runtime,
        "mcp_status": "NOT_QUERIED",
        "vivado_opened": False,
        "vivado_cli_invoked": False,
    }
    _require(not PROJECT_PREFLIGHT.exists(),
             f"拒绝覆盖 T59 工程预检绑定：{PROJECT_PREFLIGHT}")
    _write_json_exclusive(PROJECT_PREFLIGHT, preflight)
    project_preflight_record = _artifact(PROJECT_PREFLIGHT)

    fixture_manifest_path = FIXTURE_ROOT / "fixture_manifest.json"
    fixture_manifest = {
        "schema": "GestureForge-S2A-T59-fixture-manifest-v8",
        "task_id": "S2A-T59",
        "run_id": "run10",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "prior_attempts": prior_attempts,
        "fail_closed_audit": historical_audit_record,
        "path_guard_audit": path_guard_audit,
        "parent_report": preparation_inputs["T56_parent_report"],
        "T58_parent": t58_parent,
        "generator_source": preparation_inputs["oracle_source"],
        "runner_source_sha256": source_hashes[T59_RUNNER_RELATIVE],
        "T59_source_hashes": source_hashes,
        "preparation_inputs": preparation_inputs,
        "project_preflight_binding": project_preflight_record,
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "files": fixture_files,
        "oracle": oracle["oracle"],
        "quantization_parameter_coverage": parameter_coverage,
        "fixed_points_yx": [list(point) for point in POINTS],
        "tb_io_paths": tb_io_paths,
    }
    _write_json_exclusive(fixture_manifest_path, fixture_manifest)

    layer = inputs["layer35"]
    summary = {
        "schema": "GestureForge-S2A-T59-preparation-summary-v8",
        "task_id": "S2A-T59",
        "run_id": "run10",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "prior_attempts": prior_attempts,
        "fail_closed_audit": historical_audit_record,
        "path_guard_audit": path_guard_audit,
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25",
        "tb_io_paths": tb_io_paths,
        "T56_parent_report": {
            "path": str(T56_REPORT.resolve()),
            "sha256": T56_REPORT_SHA256,
            "acceptance_status": parent["acceptance_status"],
            "fixed_points_yx": parent_bindings["fixed_points_yx"],
        },
        "T56_summary": {
            "path": str(T56_SUMMARY.resolve()),
            "sha256": T56_SUMMARY_SHA256,
        },
        "T58_parent": t58_parent,
        "T56_simulation": {
            key: parent_simulation[key] for key in (
                "raw_int32_compares", "int8_compares",
                "progress_checkpoint_count",
                "raw_byte_identical_to_independent_golden",
                "int8_byte_identical_to_independent_golden",
            )
        },
        "oracle_source": {
            "path": str(T54_RUNNER.resolve()),
            "sha256": T54_RUNNER_SHA256,
            "methods": ["_load_frozen_inputs", "_build_oracle"],
            "historical_BASE_HEAD": historical_oracle_head,
            "runtime_BASE_HEAD": current_head,
            "reason": "T54 loader 的历史精确 HEAD 守卫在内存中绑定到本次 current_head；独立验证冻结 BASE_HEAD 为当前及本次 HEAD 的祖先，并保持 T54 上游文件哈希校验。",
        },
        "bindings": {
            **preparation_inputs,
            "fail_closed_audit": historical_audit_record,
            "path_guard_audit": path_guard_audit,
            "model": {
                "name": "tiny416",
                "cfg_section": layer["cfg_section"],
                "layer_index": layer["layer_index"],
                "input_shape_nchw": layer["input_shape_nchw"],
                "output_shape_nchw": layer["output_shape_nchw"],
                "kernel_hw": layer["kernel_hw"],
                "stride_hw": layer["stride_hw"],
                "padding_lrtb": layer["padding_lrtb"],
                "padding_value_int8": layer["padding_value_int8"],
                "layout": layer["layout"],
                "accumulator_bits": layer["accumulator_bits"],
            },
        "fixed_points_yx": [list(point) for point in POINTS],
        "tb_io_paths": tb_io_paths,
            "T56_source_hashes": parent_bindings["T56_source_hashes"],
            "T59_source_hashes": source_hashes,
            "project_preflight_binding": project_preflight_record,
        },
        "fixture": {
            "root": str(FIXTURE_ROOT.resolve()),
            "files": fixture_files,
            "manifest": _artifact(fixture_manifest_path),
            "golden_layout": {
                "raw_int32_le_bytes": RAW_BYTES,
                "int8_bytes": INT8_BYTES,
                "total_bytes": GOLDEN_BYTES,
                "order": "全部 raw INT32 little-endian，随后全部 INT8",
            },
        },
        "feature_fixture": oracle["fixture"],
        "oracle": oracle["oracle"],
        "quantization_parameter_coverage": parameter_coverage,
        "expected_counts": oracle["expected_counts"],
        "project_preflight": {
            **project_preflight_record,
            "project_name": "AX7Z020_Gesture",
            "target_xpr_sha256": xpr_sha_after,
            "target_xpr_unchanged": True,
        },
        "runtime_preflight": runtime,
        "simulation": {
            "status": "NOT_RUN",
            "reason": "本任务只准备 CPU oracle 与 fixture，未创建 T59 launcher/Tcl，也未运行 Vivado/XSim。",
        },
        "review": {
            "G2": "NOT_REVIEWED",
            "G3": "NOT_CLAIMED",
            "G4": "NOT_CLAIMED",
            "G5": "NOT_CLAIMED",
        },
        "limitations": [
            "仅覆盖 y=23、x=0..25、256 个输出通道，不代表 layer35 全层或整网。",
            "本报告仅为 CPU oracle 与 fixture 准备结果，未运行 RTL 仿真。",
        ],
    }
    _write_json_exclusive(PREPARE_REPORT, summary)
    print(json.dumps({
        "result": summary["status"],
        "prepare_report": str(PREPARE_REPORT.resolve()),
        "project_preflight": str(PROJECT_PREFLIGHT.resolve()),
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "source_hashes": source_hashes,
        "counts": {
            "raw_int32": RAW_COUNT,
            "int8": INT8_COUNT,
            "progress_checkpoints_expected": 256,
        },
        "oracle": oracle["oracle"],
        "fixture_files": fixture_files,
        "project_preflight_binding": project_preflight_record,
    }, ensure_ascii=False, indent=2), flush=True)
    return summary


def _verify_fail_closed_audit(preparation: dict[str, Any],
                              manifest: dict[str, Any],
                              prepared_hashes: dict[str, Any]) -> None:
    record = preparation.get("fail_closed_audit")
    _require(isinstance(record, dict) and
             preparation.get("bindings", {}).get("fail_closed_audit") == record and
             manifest.get("fail_closed_audit") == record,
             "T59 六项 fail-closed 审计未由 summary/manifest 双向绑定")
    audit_path = _verify_file_record(record, "T59 fail-closed 审计 JSON")
    _require(audit_path.resolve() == FAIL_CLOSED_AUDIT.resolve(),
             "T59 fail-closed 审计路径不属于 run07")
    audit, _ = _read_json(audit_path)
    expected_keys = set(UPSTREAM_BINDINGS)
    cases = audit.get("cases", [])
    _require(audit.get("schema") == "GestureForge-S2A-T59-upstream-fail-closed-v2" and
             audit.get("task_id") == "S2A-T59" and
             audit.get("run_id") == "run07" and
             audit.get("status") == "PASS" and
             audit.get("verify_mode") == "--verify-only" and
             audit.get("audit_script_sha256") ==
             prepared_hashes.get("verification/test_s2a_t59_upstream_fail_closed.py") and
             len(cases) == len(expected_keys) and
             {case.get("dependency_key") for case in cases} == expected_keys,
             "T59 fail-closed 审计身份、源码绑定或六项覆盖数不匹配")
    for case in cases:
        dependency_key = case["dependency_key"]
        path, expected_sha256 = UPSTREAM_BINDINGS[dependency_key]
        failure = case.get("failure_record")
        temp_dependency_path = str(case.get("temp_dependency_path", ""))
        _require(case.get("dependency_path") == str(path.resolve()) and
                 case.get("expected_sha256") == expected_sha256 and
                 case.get("expected_rejection") ==
                 "exit_code=1 and structured EXPECTED_UPSTREAM_SHA_MISMATCH matches dependency key/path/SHA" and
                 case.get("actual_exit_code") == 1 and
                 isinstance(failure, dict) and
                 failure.get("code") == "EXPECTED_UPSTREAM_SHA_MISMATCH" and
                 failure.get("dependency_key") == dependency_key and
                 failure.get("dependency_path") == temp_dependency_path and
                 failure.get("expected_sha256") == expected_sha256 and
                 failure.get("actual_sha256") == case.get("mutated_sha256") and
                 failure.get("actual_sha256") != expected_sha256 and
                 case.get("temp_cleanup_policy") ==
                 "TemporaryDirectory 在 verify-only 子进程结束后清理" and
                 case.get("temp_path_cleaned") is True and
                 not Path(str(case.get("temp_root_path", ""))).exists() and
                 case.get("result") == "PASS",
                 f"T59 fail-closed 审计案例未命中预期 SHA 门禁：{dependency_key}")


def _verify_prepared_fixture(preparation: dict[str, Any]) -> tuple[dict[str, Any], str, bytes]:
    fixture = preparation.get("fixture")
    _require(isinstance(fixture, dict), "T59 prepare_summary 缺少 fixture 对象")
    _require(Path(str(fixture.get("root", ""))).resolve() == FIXTURE_ROOT.resolve(),
             "T59 fixture 根目录与准备摘要绑定不一致")
    manifest_record = fixture.get("manifest")
    _require(isinstance(manifest_record, dict),
             "T59 prepare_summary 缺少 fixture manifest 绑定")
    manifest_path = _verify_file_record(manifest_record, "T59 fixture manifest")
    _require(manifest_path.resolve() == (FIXTURE_ROOT / "fixture_manifest.json").resolve(),
             "T59 fixture manifest 路径不匹配")
    manifest, manifest_sha256 = _read_json(manifest_path)
    _require(manifest_sha256 == str(manifest_record.get("sha256", "")).lower(),
             "T59 fixture manifest SHA-256 与 prepare_summary 不一致")
    _require(manifest.get("schema") == "GestureForge-S2A-T59-fixture-manifest-v8" and
             manifest.get("task_id") == "S2A-T59" and
             manifest.get("run_id") == "run10" and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("baseline_head") == BASE_HEAD and
             manifest.get("current_head") == preparation.get("current_head") and
             manifest.get("fixture_root") == str(FIXTURE_ROOT.resolve()) and
             manifest.get("fixed_points_yx") == [list(point) for point in POINTS] and
             preparation.get("tb_io_paths") == manifest.get("tb_io_paths") ==
             _verify_tb_run_paths(),
             "T59 fixture manifest 的 schema、基线、根目录或坐标不匹配")
    _require(manifest.get("parent_report", {}).get("sha256") == T56_REPORT_SHA256 and
             manifest.get("T58_parent") == preparation.get("T58_parent") == _verify_t58_parent(),
             "T59 manifest 未绑定已审 T56/T58 父证据")
    _require(preparation.get("tb_io_paths") == _verify_tb_run_paths(),
             "T59 prepare_summary 的 testbench 输入/输出路径不属于 run10")

    prepared_hashes = preparation.get("bindings", {}).get("T59_source_hashes")
    _require(isinstance(prepared_hashes, dict) and
             set(prepared_hashes) == set(T59_SOURCE_PATHS) and
             manifest.get("T59_source_hashes") == prepared_hashes,
             "T59 manifest 与 prepare_summary 源码绑定不一致")
    for relative, expected in prepared_hashes.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == str(expected).lower(),
                 f"T59 准备后源码哈希变化：{relative}")
    _require(manifest.get("runner_source_sha256") ==
             prepared_hashes.get(T59_RUNNER_RELATIVE),
             "T59 manifest 未绑定 runner SHA-256")
    preparation_inputs = {
        key: preparation.get("bindings", {}).get(key)
        for key in PREPARATION_INPUT_KEYS
    }
    _require(all(isinstance(value, dict) for value in preparation_inputs.values()) and
             manifest.get("preparation_inputs") == preparation_inputs,
             "T59 manifest 与 prepare_summary 的冻结输入绑定不一致")
    _verify_upstream_records(preparation_inputs)
    _verify_fail_closed_audit(preparation, manifest, prepared_hashes)
    project_preflight_record = preparation.get("bindings", {}).get(
        "project_preflight_binding")
    _require(isinstance(project_preflight_record, dict) and
             manifest.get("project_preflight_binding") == project_preflight_record,
             "T59 manifest 与 prepare_summary 的本地工程预检绑定不一致")

    expected_names = {
        "feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt",
    }
    prepared_files = fixture.get("files")
    manifest_files = manifest.get("files")
    _require(isinstance(prepared_files, dict) and set(prepared_files) == expected_names and
             isinstance(manifest_files, dict) and set(manifest_files) == expected_names,
             "T59 fixture 文件集合不匹配")
    for name in sorted(expected_names):
        prepared_record = prepared_files[name]
        manifest_file_record = manifest_files[name]
        _require(isinstance(prepared_record, dict) and
                 isinstance(manifest_file_record, dict),
                 f"T59 fixture 文件绑定格式错误：{name}")
        prepared_path = _verify_file_record(prepared_record, f"T59 prepare_summary {name}")
        manifest_file_path = _verify_file_record(manifest_file_record,
                                                 f"T59 manifest {name}")
        expected_path = FIXTURE_ROOT / name
        _require(prepared_path.resolve() == expected_path.resolve() and
                 manifest_file_path.resolve() == expected_path.resolve() and
                 prepared_record.get("bytes") == manifest_file_record.get("bytes") and
                 str(prepared_record.get("sha256", "")).lower() ==
                 str(manifest_file_record.get("sha256", "")).lower(),
                 f"T59 fixture 路径或摘要/manifest 绑定不一致：{name}")

    expected_sizes = {
        "feature_input.bin": FEATURE_BYTES,
        "layer35_weights.bin": WEIGHT_BYTES,
        "golden.bin": GOLDEN_BYTES,
    }
    for name, size in expected_sizes.items():
        _require(prepared_files[name].get("bytes") == size,
                 f"T59 fixture 字节数错误：{name}")

    prepared_oracle = preparation.get("oracle")
    _require(isinstance(prepared_oracle, dict) and
             manifest.get("oracle") == prepared_oracle and
             prepared_oracle.get("raw_int32_count") == RAW_COUNT and
             prepared_oracle.get("quantized_int8_count") == INT8_COUNT and
             prepared_oracle.get("d2_t23_match_count") == INT8_COUNT,
             "T59 oracle 字段或逐项计数不匹配")
    _require(manifest.get("quantization_parameter_coverage") ==
             preparation.get("quantization_parameter_coverage"),
             "T59 manifest 与 prepare_summary 的 T23 通道参数覆盖绑定不一致")
    golden = (FIXTURE_ROOT / "golden.bin").read_bytes()
    raw_golden = golden[:RAW_BYTES]
    int8_golden = golden[RAW_BYTES:]
    combined_sha256 = _sha256(golden)
    raw_sha256 = _sha256(raw_golden)
    int8_sha256 = _sha256(int8_golden)
    _require(len(golden) == GOLDEN_BYTES and len(raw_golden) == RAW_BYTES and
             len(int8_golden) == INT8_BYTES and
             combined_sha256 == prepared_oracle.get("combined_golden_sha256") and
             raw_sha256 == prepared_oracle.get("raw_int32_le_sha256") and
             int8_sha256 == prepared_oracle.get("quantized_int8_sha256"),
             "T59 combined/raw/INT8 golden 字节摘要不匹配")
    vector_lines = (FIXTURE_ROOT / "vectors.txt").read_text(
        encoding="ascii").splitlines()
    _require(len(vector_lines) == RAW_COUNT,
             "T59 vectors.txt 行数不等于 6656")
    for index, line in enumerate(vector_lines):
        values = [int(value) for value in line.split()]
        _require(len(values) == 8 and values[0] == index // 26 and
                 values[1] == 23 and values[2] == index % 26,
                 f"T59 vectors.txt 坐标或字段错误：row={index}")
    return manifest, manifest_sha256, golden


def _verify_runtime_oracle(preparation: dict[str, Any]) -> str:
    runtime_head = _current_head()
    _require_head_descends_from(BASE_HEAD, runtime_head,
                                "T59 verify-only 当前 HEAD")
    oracle_runner, historical_head = _load_oracle_runner(runtime_head)
    inputs = oracle_runner._load_frozen_inputs()
    expected_upstream = _expected_upstream_records()
    _verify_loader_upstream_records(inputs["bindings"], expected_upstream)
    coverage = _quantization_parameter_coverage(inputs)
    _require(coverage == preparation.get("quantization_parameter_coverage"),
             "verify-only 重载的 T23 Q+/M+/Q-/M- 覆盖摘要不匹配")
    oracle = oracle_runner._build_oracle(inputs, progress=False, points=POINTS)
    _require(oracle["oracle"] == preparation.get("oracle") and
             oracle["fixture"] == preparation.get("feature_fixture") and
             oracle["expected_counts"] == preparation.get("expected_counts"),
             "verify-only 重算的 T54 oracle/feature fixture/传输计数不匹配")
    _require(oracle["combined_golden"] == (FIXTURE_ROOT / "golden.bin").read_bytes() and
             oracle["feature"] == (FIXTURE_ROOT / "feature_input.bin").read_bytes() and
             inputs["weight_bytes"] ==
             (FIXTURE_ROOT / "layer35_weights.bin").read_bytes() and
             _vectors_bytes(oracle["vectors"]) ==
             (FIXTURE_ROOT / "vectors.txt").read_bytes(),
             "verify-only 重算的 feature/weight/golden/vectors 与 run10 字节不一致")
    _require(len(oracle["raw_values"]) == RAW_COUNT and
             len(oracle["quantized_values"]) == INT8_COUNT and
             oracle["oracle"].get("d2_t23_match_count") == INT8_COUNT and
             all(point[0] == 23 for point in POINTS) and
             tuple(point[1] for point in POINTS) == tuple(range(26)),
             "verify-only T59 y=23 / raw / INT8 / D2-T23 覆盖数错误")
    source = preparation.get("oracle_source", {})
    _require(source.get("historical_BASE_HEAD") == historical_head and
             source.get("runtime_BASE_HEAD") == preparation.get("current_head") and
             source.get("path") == str(T54_RUNNER.resolve()) and
             source.get("sha256") == T54_RUNNER_SHA256,
             "T59 summary 的 T54 runtime/current_head 来源记录不匹配")
    return runtime_head


def _verify_prepared() -> dict[str, Any]:
    root_binding_sha256 = _verify_root_binding()
    prior_attempts = _prior_attempts_record()
    run08_contained_files = _audit_run_root_paths(RUN08_ROOT)
    run09_contained_files = _audit_run_root_paths(RUN09_ROOT)
    parent, parent_bindings, _ = _verify_parent()
    t58_parent = _verify_t58_parent()
    _require(PREPARE_REPORT.is_file(), "缺少 T59 prepare_summary.json")
    preparation, prepare_sha256 = _read_json(PREPARE_REPORT)
    current_tree_files = _audit_run_root_paths(RUN_ROOT)
    path_guard_audit = _run_path_guard_negative_tests()
    _require(preparation.get("schema") ==
             "GestureForge-S2A-T59-preparation-summary-v8" and
             preparation.get("task_id") == "S2A-T59" and
             preparation.get("run_id") == "run10" and
             preparation.get("status") == "PREPARED_NOT_SIMULATED" and
             preparation.get("baseline_head") == BASE_HEAD and
             preparation.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25" and
             preparation.get("tb_io_paths") == _verify_tb_run_paths() and
             preparation.get("bindings", {}).get("fixed_points_yx") ==
             [list(point) for point in POINTS] and
             preparation.get("path_guard_audit") == path_guard_audit and
             preparation.get("T58_parent") == t58_parent,
             "T59 prepare_summary schema、状态、范围或基线不匹配")
    recorded_head = str(preparation.get("current_head", ""))
    current_head = _current_head()
    _require_head_descends_from(BASE_HEAD, recorded_head, "T59 记录的 current_head")
    _require_head_descends_from(recorded_head, current_head,
                                "当前 HEAD 相对 T59 记录的 current_head")
    manifest, _, _ = _verify_prepared_fixture(preparation)
    _require(manifest.get("path_guard_audit") == path_guard_audit,
              "T59 run10 manifest 未绑定路径负向测试结果")
    revalidated_head = _verify_runtime_oracle(preparation)
    _require(revalidated_head == current_head,
             "T59 verify-only 期间 Git HEAD 发生变化")

    project_record = preparation.get("project_preflight", {})
    _require(project_record.get("path") == str(PROJECT_PREFLIGHT.resolve()) and
             PROJECT_PREFLIGHT.is_file(),
             "T59 prepare_summary 的只读工程预检路径不匹配")
    project_binding, project_sha256 = _read_json(PROJECT_PREFLIGHT)
    _require(preparation.get("prior_attempts") == prior_attempts and
             manifest.get("prior_attempts") == prior_attempts and
             project_binding.get("prior_attempts") == prior_attempts,
             "T59 run10 未双向绑定保留的 run05/run06/run07/run08/run09 历史尝试")
    current_xpr_sha256 = _sha_file(XPR_PATH)
    binding_record = preparation.get("bindings", {}).get(
        "project_preflight_binding")
    _require(isinstance(binding_record, dict),
             "T59 prepare_summary 缺少自身工程预检摘要绑定")
    _require(project_sha256 == project_record.get("sha256") ==
             binding_record.get("sha256") and
             project_record.get("bytes") == binding_record.get("bytes") and
             project_record.get("path") == binding_record.get("path") ==
             str(PROJECT_PREFLIGHT.resolve()) and
              project_binding.get("schema") ==
              "GestureForge-S2A-T59-project-preflight-v7" and
             project_binding.get("task_id") == "S2A-T59" and
               project_binding.get("run_id") == "run10" and
             project_binding.get("baseline_head") == BASE_HEAD and
             project_binding.get("current_head") == recorded_head and
             project_binding.get("run_directory") == str(RUN_ROOT.resolve()) and
             project_binding.get("project_xpr_path") == str(XPR_PATH.resolve()) and
             project_binding.get("target_xpr_sha256_before_prepare") ==
             current_xpr_sha256 ==
             project_binding.get("target_xpr_sha256_after_prepare") and
             project_binding.get("target_xpr_unchanged") is True and
             project_record.get("target_xpr_sha256") == current_xpr_sha256 and
             project_record.get("target_xpr_unchanged") is True,
             "T59 prepare_summary、manifest、本地工程预检与真实 XPR SHA 不一致")
    _require(project_binding.get("path_guard_audit") == path_guard_audit and
             preparation.get("bindings", {}).get("path_guard_audit") ==
             path_guard_audit and
             project_binding.get("runtime_preflight", {}).get(
                 "root_binding_sha256") == root_binding_sha256,
             "T59 路径负向测试或根绑定 SHA 未双向绑定")
    expected_source_hashes = _source_hashes()
    _require(project_binding.get("T59_source_hashes") == expected_source_hashes ==
             preparation.get("bindings", {}).get("T59_source_hashes"),
             "T59 工程预检绑定的源码哈希与当前文件不一致")
    preparation_inputs = {
        key: preparation.get("bindings", {}).get(key)
        for key in PREPARATION_INPUT_KEYS
    }
    _require(project_binding.get("preparation_inputs") == preparation_inputs,
             "T59 工程预检绑定与 prepare_summary 输入绑定不一致")
    _verify_upstream_records(preparation_inputs)
    _require(preparation_inputs["T56_parent_report"] == {
                 "path": str(T56_REPORT.resolve()),
                 "sha256": T56_REPORT_SHA256,
             } and
             preparation_inputs["T56_summary"] == {
                 "path": str(T56_SUMMARY.resolve()),
                 "sha256": T56_SUMMARY_SHA256,
             } and
             preparation_inputs["T58_parent_prepare_summary"] ==
                 t58_parent["prepare_summary"] and
             preparation_inputs["T58_parent_fixture_manifest"] ==
                 t58_parent["fixture_manifest"] and
             preparation_inputs["T58_parent_golden"] == t58_parent["golden"] and
             preparation_inputs["T58_parent_project_preflight_binding"] ==
                 t58_parent["project_preflight_binding"] and
             preparation_inputs["G0_specification"] == {
                 "path": str(G0_PATH.resolve()),
                 "sha256": G0_SHA256,
             } and
             preparation_inputs["T01_manifest"].get("path") ==
                 str(T01_PATH.resolve()) and
             preparation_inputs["T01_manifest"].get("sha256") == T01_SHA256 and
             preparation_inputs["T23_parameter_table"].get("path") ==
                 str(T23_PATH.resolve()) and
             preparation_inputs["T23_parameter_table"].get("sha256") == T23_SHA256 and
             preparation_inputs["GF8_package"].get("sha256") == GF8_SHA256 and
             preparation_inputs["weight_layer35"] ==
                 parent_bindings.get("weight_layer35") and
             preparation_inputs["oracle_source"] == {
                 "path": str(T54_RUNNER.resolve()),
                 "sha256": T54_RUNNER_SHA256,
             },
             "T59 工程预检绑定未指向冻结 G0/T01/T23/GF8/T56/oracle 输入")
    for name in (
        "T56_parent_report", "T56_summary", "T58_parent_prepare_summary",
        "T58_parent_fixture_manifest", "T58_parent_golden",
        "T58_parent_project_preflight_binding", "G0_specification",
        "T01_manifest", "T23_parameter_table", "GF8_package", "oracle_source",
        "T16_conv_requant_proof", "T17_conv_engine_evidence",
        "T20_layer_scheduler_evidence", "T16_requant_proof_source",
        "D2_forward_reference_source",
    ):
        record = preparation_inputs[name]
        _require(isinstance(record, dict), f"T59 输入绑定格式错误：{name}")
        source_path = _verify_file_record(record, f"T59 输入 {name}")
        _require(source_path.is_file(), f"T59 输入文件缺失：{name}")
    _require(project_binding.get("mcp_status") == "NOT_QUERIED" and
             project_binding.get("vivado_opened") is False and
             project_binding.get("vivado_cli_invoked") is False,
             "T59 工程预检不得声称查询 MCP 或打开/启动 Vivado")
    runtime = preparation.get("runtime_preflight", {})
    _require(runtime.get("path_chain_valid") is True and
             runtime.get("checked_xpr") == str(XPR_PATH.resolve()) and
             runtime.get("evidence_root") == str(EVIDENCE_ROOT.resolve()) and
             runtime.get("run10_path") == str(RUN_ROOT) and
             runtime.get("target_absent") is True and
             runtime.get("existing_run01") is True and
             runtime.get("existing_run02") is True and
             runtime.get("existing_run03") is True and
             runtime.get("existing_run04") is True and
             runtime.get("existing_run05") is True and
             runtime.get("existing_run06") is True and
             runtime.get("existing_run07") is True and
             runtime.get("existing_run08") is True and
              runtime.get("existing_run09") is True and
              runtime.get("existing_run10") is False and
              runtime.get("run08_contained_files") == run08_contained_files and
              runtime.get("run08_pinned_artifact_count") == 7 and
              runtime.get("run09_contained_files") == run09_contained_files and
              runtime.get("run09_pinned_artifact_count") == 7 and
             runtime.get("root_binding_sha256") == ROOT_PROJECT_PREFLIGHT_SHA256 and
             runtime.get("process_names") == list(PROCESS_NAMES) and
             runtime.get("processes_before_prepare") == [] and
             runtime.get("processes_after_prepare") == {
                 "process_names": list(PROCESS_NAMES),
                 "processes": [],
                 "powershell_exit_code": 0,
             } and
             runtime.get("mcp_status") == "NOT_QUERIED" and
             project_binding.get("runtime_preflight") == runtime,
             "T59 prepare_summary 路径/进程/MCP 状态不匹配")
    postflight_now = _runtime_process_snapshot()
    _require(postflight_now["processes"] == [] and
             _project_xpr_sha() == current_xpr_sha256 and
             _verify_root_binding() == root_binding_sha256,
             "T59 verify-only 当前进程门禁或真实 XPR SHA 不匹配")
    _require(preparation.get("simulation", {}).get("status") == "NOT_RUN",
             "T59 当前证据不应包含仿真状态")
    expected_files = {
        "prepare_summary.json",
        "project_preflight_binding.json",
        "fixture/feature_input.bin",
        "fixture/layer35_weights.bin",
        "fixture/golden.bin",
        "fixture/vectors.txt",
        "fixture/fixture_manifest.json",
    }
    actual_files = {
        path.relative_to(RUN_ROOT).as_posix()
        for path in RUN_ROOT.rglob("*") if path.is_file()
    }
    _require(actual_files == expected_files,
             f"T59 run10 文件集合不匹配：extra={sorted(actual_files - expected_files)} "
             f"missing={sorted(expected_files - actual_files)}")
    _require(current_tree_files == sorted(expected_files),
              "T59 run10 的 containment/reparse 文件清单与预期不一致")
    print(json.dumps({
        "result": "PREPARED_NOT_SIMULATED",
        "prepare_summary_sha256": prepare_sha256,
        "fixture_manifest_sha256": preparation["fixture"]["manifest"]["sha256"],
        "golden_sha256": preparation["oracle"]["combined_golden_sha256"],
        "baseline_head": BASE_HEAD,
        "prepared_current_head": recorded_head,
        "revalidated_current_head": current_head,
        "output_counts": {
            "raw_int32": RAW_COUNT,
            "int8": INT8_COUNT,
            "d2_t23_matches": INT8_COUNT,
        },
        "simulation": "NOT_RUN",
    }, ensure_ascii=False, indent=2))
    return preparation


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare-only", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    mode.add_argument("--audit-history-only", action="store_true",
                      help="只读核验固定历史证据与 run09 来源报告 schema")
    args = parser.parse_args()
    try:
        if args.audit_history_only:
            attempts = _prior_attempts_record()
            run08 = next(attempt for attempt in attempts
                         if attempt.get("run_id") == "run08")
            run09 = next(attempt for attempt in attempts
                         if attempt.get("run_id") == "run09")
            _require(run08.get("historical_verify_only", {}).get("status") ==
                     "UNVERIFIED_SOURCE_REPORT" and
                     run08.get("history_schema_audit", {}).get("status") ==
                     "PASS" and
                     run08.get("history_schema_audit", {}).get("case_count") == 5 and
                     run09.get("verify_only", {}).get("status") ==
                     "UNVERIFIED_SOURCE_REPORT" and
                     run09.get("history_schema_audit", {}).get("status") ==
                     "PASS" and
                     run09.get("history_schema_audit", {}).get("case_count") == 3,
                     "T59 run09 历史 schema 审计未通过")
            print(json.dumps({
                "result": "PASS",
                "run08_verify_only_status":
                    run08["historical_verify_only"]["status"],
                "run08_raw_command_output":
                    run08["historical_verify_only"]["raw_command_output"]["status"],
                "run08_review_artifact":
                    run08["historical_verify_only"]["review_artifact"]["status"],
                "run08_schema_negative_case_count":
                    run08["history_schema_audit"]["case_count"],
                "run09_verify_only_status":
                    run09["verify_only"]["status"],
                "run09_raw_command_output":
                    run09["verify_only"]["raw_command_output"]["status"],
                "schema_negative_case_count":
                    run09["history_schema_audit"]["case_count"],
                "run09_artifact_files":
                    run09["verify_only"]["run09_artifact_files"],
            }, ensure_ascii=False, sort_keys=True, indent=2))
        elif args.prepare_only:
            _prepare()
        else:
            _verify_prepared()
        return 0
    except T59UpstreamShaMismatch as error:
        print("T59_FAILURE_JSON=" + json.dumps(
            error.failure_record, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"),
        ), file=sys.stderr, flush=True)
        print(f"FAIL T59 {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"FAIL T59 {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
