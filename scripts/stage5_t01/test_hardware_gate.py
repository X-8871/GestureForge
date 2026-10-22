"""S5-T01 门禁 v2 的隔离合成测试（CDX-20261022-014 §0.4）。

- 全部用**临时目录里的合成信箱/合成登记表**，不读真实信箱、不打开 JTAG/COM4、不启动 hw_server。
- 通过子进程调用 CLI，检查**真实退出码**与 JSON 判定，不只看内部函数。
- 附一条 `real_parity`（只读解析真实信箱 + 真实登记表），用于在真实门禁之前核对登记表绑定。

用法：python -B -m unittest scripts.stage5_t01.test_hardware_gate -v
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

W5 = pathlib.Path(r"D:\codex-worktrees\w5")
GATE = W5 / "scripts/stage5_t01/check_hardware_gate.py"
REAL_REGISTRY = W5 / "scripts/stage5_t01/hardware_handoff_registry.json"
REAL_MAILBOXES = [pathlib.Path(r"D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF/codex_mailbox"),
                  pathlib.Path(r"D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF/dsh_mailbox")]
BASE_STATE = "测试主 STATE：硬件相关叙述占位。\n"


def sha_of(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GateCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="s5gate_"))
        self.mailbox = self.tmp / "mailbox"
        self.mailbox.mkdir(parents=True, exist_ok=True)
        self.state = self.tmp / "STATE.md"
        self.state.write_text(BASE_STATE, encoding="utf-8")
        self.records: list[dict] = []

    def add_record_file(self, name: str, text: str, *, kind: str, order_key: str, scope: str = "JTAG+COM4",
                        quote: str | None = None, register: bool = True, sha_override: str | None = None) -> pathlib.Path:
        path = self.mailbox / name
        path.write_text(text, encoding="utf-8")
        if register:
            self.records.append({"id": name.split("-")[0] + "-" + order_key,
                                 "file": f"{self.mailbox.name}/{name}",
                                 "sha256": sha_override or sha_of(path), "order_key": order_key,
                                 "kind": kind, "hardware_scope": scope, "issuer": "test",
                                 **({"evidence_quote": quote} if quote else {})})
        return path

    def add_plain_file(self, name: str, text: str) -> pathlib.Path:
        path = self.mailbox / name
        path.write_text(text, encoding="utf-8")
        return path

    def write_registry(self) -> pathlib.Path:
        path = self.tmp / "registry.json"
        path.write_text(json.dumps({"schema_version": "test",
                                    "state_changing_kinds": ["hardware_occupation", "hardware_release"],
                                    "neutral_kinds": ["hardware_request", "operation_doc", "delivery_receipt",
                                                       "ack", "report", "decision"],
                                    "records": self.records},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def run_gate(self, *, process: str = "stub-ok", lock: str = "stub-none", release_id: str | None = None,
                 registry: pathlib.Path | None = None, mailbox_root: pathlib.Path | None = None,
                 extra: list[str] | None = None, out_name: str = "out",
                 use_real_mailbox: bool = False, port: str = "stub-none",
                 process_csv: pathlib.Path | None = None) -> tuple[int, dict]:
        out_dir = self.tmp / out_name
        cmd = [sys.executable, "-B", str(GATE), "--out", str(out_dir),
               "--registry", str(registry or self.write_registry()),
               "--process-check", process, "--lock-check", lock, "--main-state", str(self.state),
               "--port-check", port]
        if process_csv is not None:
            cmd += ["--process-csv", str(process_csv)]
        if not use_real_mailbox:
            cmd += ["--mailbox-root", str(mailbox_root or self.mailbox)]
        if release_id:
            cmd += ["--release-id", release_id]
        cmd += extra or []
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        gate_json = out_dir / "hardware_gate.json"
        payload = json.loads(gate_json.read_text(encoding="utf-8")) if gate_json.exists() else {}
        return proc.returncode, payload

    # ── §0.4 情形 ────────────────────────────────────────────────────────────────
    def test_01_release_then_plain_doc_stays_released_go(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "本任务不再占用硬件。\n",
                             kind="hardware_release", order_key="20261001-001")
        # 真正普通（不含任何交接语义）的未登记文档 → 中性
        self.add_plain_file("CDX-20261002-002-ordinary-runbook.md", "普通操作文档：本节说明构建与自检步骤。\n")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 0, payload.get("reasons"))
        self.assertEqual(payload["hardware_state"], "RELEASED")
        self.assertEqual(payload["release_basis"], "mailbox_release")

    def test_02_release_then_new_occupation_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        self.add_record_file("CDX-20261003-003-hw-resume.md", "本任务独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261003-003")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertEqual(payload["hardware_state"], "OCCUPIED")
        self.assertTrue(any("占用态" in r for r in payload["reasons"]))

    def test_03_occupation_then_valid_release_go(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261001-001")
        self.add_record_file("CDX-20261005-005-hw-release.md", "2B 本任务不再占用硬件。\n",
                             kind="hardware_release", order_key="20261005-005", quote="不再占用硬件")
        code, payload = self.run_gate(release_id="CDX-20261005-005")
        self.assertEqual(code, 0, payload.get("reasons"))
        self.assertEqual(payload["hardware_state"], "RELEASED")

    def test_04_unregistered_body_words_block_not_neutral(self) -> None:
        """BI-2 收紧后：未登记且**正文**含"释放/独占"⇒ BLOCKED（既不能冒充通知，也不能被静默忽略）。

        对照：已登记为 operation_doc 的同类文件必须仍中性（见 test_27）。
        """
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        self.add_plain_file("CDX-20261009-009-notes.md", "本节说明释放流程与独占要求：release/exclusive 均出现。\n")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("正文含交接语义" in r or "未登记的硬件交接记录" in r for r in payload["reasons"]),
                        payload["reasons"])

    def test_05_unregistered_filename_hint_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        self.add_plain_file("CDX-20261010-010-hardware-handover-fake.md", "无登记却自称交接。\n")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("未登记的硬件交接记录" in r for r in payload["reasons"]))

    def test_06_unregistered_declaration_marker_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        self.add_plain_file("CDX-20261011-011-note.md", "<!-- hw_handoff_kind: hardware_release -->\n自称让出\n")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("未登记的硬件交接记录" in r for r in payload["reasons"]))

    def test_07_registry_hash_mismatch_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n", kind="hardware_release",
                             order_key="20261001-001", sha_override="0" * 64)
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("哈希不匹配" in r for r in payload["reasons"]))

    def test_08_evidence_quote_mismatch_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "正文里没有那句话。\n", kind="hardware_release",
                             order_key="20261001-001", quote="本任务不再占用硬件")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("证据原文不匹配" in r for r in payload["reasons"]))

    def test_09_release_not_after_occupation_blocks(self) -> None:
        # order_key 反向（登记表顺序与哈希都合法，但顺序矛盾）→ 判 OCCUPIED
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        self.add_record_file("CDX-20261002-002-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261002-002")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertEqual(payload["hardware_state"], "OCCUPIED")

    def test_10_index_lock_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        code, payload = self.run_gate(release_id="CDX-20261001-001", lock="stub-lock")
        self.assertEqual(code, 1)
        self.assertTrue(any("index.lock" in r for r in payload["reasons"]))

    def test_11_process_enumeration_failure_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        code, payload = self.run_gate(release_id="CDX-20261001-001", process="stub-fail")
        self.assertEqual(code, 1)
        self.assertTrue(any("无法枚举系统进程" in r for r in payload["reasons"]))

    def test_12_process_hit_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        code, payload = self.run_gate(release_id="CDX-20261001-001", process="stub-hit")
        self.assertEqual(code, 1)
        self.assertTrue(any("检测到硬件/重型进程" in r for r in payload["reasons"]))

    def test_13_release_id_mismatch_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        code, payload = self.run_gate(release_id="CDX-99999999-999")
        self.assertEqual(code, 1)
        self.assertTrue(any("未提供匹配的 --release-id" in r for r in payload["reasons"]))

    def test_14_authorization_without_bound_source_rejected(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261001-001")
        code, payload = self.run_gate(extra=["--authorized-by", "Wong", "--authorization-note", "允许上板"])
        self.assertEqual(code, 1)
        self.assertIsNone(payload["authorization"])
        self.assertIsNotNone(payload["rejected_authorization"])

    def test_15_authorization_with_bound_source_allows_unknown_state(self) -> None:
        src = self.tmp / "auth.txt"
        src.write_text("Wong 2026-10-22：允许本次只读上板操作。\n", encoding="utf-8")
        note = "允许本次只读上板操作"
        # 非空信箱但**无状态类记录**（归属不可核验）——授权可用路径；空信箱另有 fail-closed 用例
        self.add_plain_file("CDX-20261001-001-ordinary-notes.md", "普通记录，不含硬件交接语义。\n")
        code, payload = self.run_gate(extra=["--authorized-by", "Wong", "--authorization-note", note,
                                            "--authorization-source", str(src),
                                            "--authorization-source-sha256", sha_of(src)])
        self.assertEqual(code, 0, payload.get("reasons"))
        self.assertEqual(payload["release_basis"], "operator_authorization")
        self.assertTrue(payload["authorization_ownership_unverifiable"])

    def test_16_authorization_cannot_override_real_occupation(self) -> None:
        src = self.tmp / "auth.txt"
        src.write_text("Wong：允许上板\n", encoding="utf-8")
        self.add_record_file("CDX-20261001-001-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261001-001")
        code, payload = self.run_gate(extra=["--authorized-by", "Wong", "--authorization-note", "允许上板",
                                            "--authorization-source", str(src),
                                            "--authorization-source-sha256", sha_of(src)])
        self.assertEqual(code, 1)
        self.assertEqual(payload["hardware_state"], "OCCUPIED")
        self.assertTrue(any("不能覆盖真实占用" in r for r in payload["reasons"]))

    def test_17_missing_registry_blocks(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        code, payload = self.run_gate(release_id="CDX-20261001-001", registry=self.tmp / "nope.json")
        self.assertEqual(code, 1)
        self.assertTrue(any("登记表不存在" in r for r in payload["reasons"]))

    def test_18_real_parity_release_state_and_registry_binding(self) -> None:
        """只读解析真实信箱 + 真实登记表：应判 RELEASED 且 GO（用替身进程/锁，避免误碰硬件）。"""
        self.assertTrue(REAL_REGISTRY.exists())
        code, payload = self.run_gate(process="stub-ok", lock="stub-none",
                                      registry=REAL_REGISTRY, use_real_mailbox=True,
                                      release_id="CDX-20261022-007", out_name="real_parity")
        self.assertEqual(code, 0, payload.get("reasons"))
        self.assertEqual(payload["hardware_state"], "RELEASED")
        self.assertEqual(payload["effective_release"]["id"], "CDX-20261022-007")
        self.assertEqual(payload["latest_occupation"]["id"], "CDX-20261022-006")
        self.assertEqual(payload["registry"]["records_total"], len(json.loads(REAL_REGISTRY.read_text(encoding="utf-8"))["records"]))

    def test_19_recursive_self_reference_registry_scan_covers_all_mailbox_files(self) -> None:
        """真实登记表必须覆盖全部真实信箱 MD（防止“漏登记 → 被误判为不可识别交接”）。"""
        registry = json.loads(REAL_REGISTRY.read_text(encoding="utf-8"))
        registered = {r["file"].split("/")[-1] for r in registry["records"]}
        actual = {p.name for root in REAL_MAILBOXES if root.is_dir() for p in root.glob("*.md")}
        missing = sorted(actual - registered)
        self.assertEqual(missing, [], f"信箱存在未登记文件：{missing}")


    # ── BI-1 / BI-2 关闭条件（2026-10-22 审查 CHANGES_REQUIRED 后新增） ──────────
    def test_20_registry_missing_file_blocks(self) -> None:
        """BI-1 B4：登记项指向的文件缺席（等于删/改名登记文件）⇒ BLOCKED。"""
        self.add_plain_file("CDX-20261001-001-hw-release.md", "普通记录。\n")
        self.records.append({"id": "CDX-20261002-002",
                             "file": f"{self.mailbox.name}/CDX-20261002-002-hw-release.md",
                             "sha256": "0" * 64, "order_key": "20261002-002", "kind": "hardware_release"})
        code, payload = self.run_gate(release_id="CDX-20261002-002")
        self.assertEqual(code, 1)
        self.assertTrue(any("缺席" in r for r in payload["reasons"]), payload["reasons"])

    def test_21_registry_missing_sha256_blocks(self) -> None:
        """BI-1 B5：登记项缺 sha256 ⇒ BLOCKED（不得跳过绑定）。"""
        path = self.mailbox / "CDX-20261001-001-hw-release.md"
        path.write_text("本任务不再占用硬件。\n", encoding="utf-8")
        self.records.append({"id": "CDX-20261001-001", "file": f"{self.mailbox.name}/{path.name}",
                             "order_key": "20261001-001", "kind": "hardware_release"})
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("缺 sha256" in r for r in payload["reasons"]), payload["reasons"])

    def test_22_registry_duplicate_registration_blocks(self) -> None:
        """BI-1 B3c：同一文件重复登记（后一条中性）⇒ BLOCKED。"""
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        self.records.append({"id": "CDX-20261001-001b",
                             "file": f"{self.mailbox.name}/CDX-20261001-001-hw-release.md",
                             "sha256": sha_of(self.mailbox / "CDX-20261001-001-hw-release.md"),
                             "order_key": "20261001-001b", "kind": "operation_doc"})
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("重复登记" in r for r in payload["reasons"]), payload["reasons"])

    def test_23_registry_bad_kind_blocks(self) -> None:
        """BI-1 B12：kind 拼写错误 ⇒ BLOCKED（不得静默中性）。"""
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_relase", order_key="20261001-001")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("kind 非法" in r for r in payload["reasons"]), payload["reasons"])

    def test_24_state_record_missing_order_key_blocks(self) -> None:
        """BI-1 B8b：状态类登记项缺 order_key ⇒ BLOCKED。"""
        self.add_record_file("CDX-20261001-001-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261001-001")
        self.records[0].pop("order_key")
        code, payload = self.run_gate()
        self.assertEqual(code, 1)
        self.assertTrue(any("缺 order_key" in r for r in payload["reasons"]), payload["reasons"])

    def test_25_registry_prefix_mismatch_blocks(self) -> None:
        """BI-1 B11：file 的目录前缀与实际信箱不符 ⇒ BLOCKED。"""
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        self.records[0]["file"] = "dsh_mailbox/CDX-20261001-001-hw-release.md"
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any(("缺席" in r) or ("前缀" in r) or ("未被应用" in r) for r in payload["reasons"]),
                        payload["reasons"])

    def test_26_unregistered_body_occupation_blocks(self) -> None:
        """BI-2 B6：未登记、文件名中性、正文自称占用 ⇒ BLOCKED。"""
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        self.add_plain_file("CDX-20261009-009-notes.md", "现由本任务独占使用 JTAG 与 COM4。\n")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertTrue(any("正文含交接语义" in r for r in payload["reasons"]), payload["reasons"])

    def test_27_registered_operation_doc_with_handoff_words_stays_neutral(self) -> None:
        """回归护栏：已登记为 operation_doc 的文件，正文含"释放/独占"仍必须中性（014 不得回归）。"""
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        path = self.mailbox / "CDX-20261022-014-runbook.md"
        path.write_text("本节说明释放流程与独占要求，并引用 release/exclusive。\n", encoding="utf-8")
        self.records.append({"id": "CDX-20261022-014", "file": f"{self.mailbox.name}/{path.name}",
                             "sha256": sha_of(path), "order_key": "20261022-014", "kind": "operation_doc"})
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 0, payload.get("reasons"))
        kinds = {r.get("file"): r.get("kind") for r in payload["neutral_records"]}
        self.assertEqual(kinds.get(path.name), "operation_doc")
        self.assertNotIn(path.name, payload.get("unregistered_neutral_files") or [])

    def test_28_occupied_release_basis_is_null(self) -> None:
        """非阻断观察修复：OCCUPIED 时 release_basis 必须为 null（不得写得像授权放行）。"""
        src = self.tmp / "auth.txt"
        src.write_text("Wong：允许上板\n", encoding="utf-8")
        self.add_record_file("CDX-20261001-001-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261001-001")
        code, payload = self.run_gate(extra=["--authorized-by", "Wong", "--authorization-note", "允许上板",
                                            "--authorization-source", str(src),
                                            "--authorization-source-sha256", sha_of(src)])
        self.assertEqual(code, 1)
        self.assertIsNone(payload["release_basis"])


    # ── 第二轮审查 BI-1 残余（file 身份归一化）关闭条件 ──────────────────────────
    def test_29_backslash_state_record_is_applied_not_dropped(self) -> None:
        """反斜杠写法必须与正斜杠等价：占用必须**被应用**（判 OCCUPIED→BLOCKED），不得静默中性。"""
        self.add_record_file("CDX-20261001-001-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261001-001")
        self.records[0]["file"] = f"{self.mailbox.name}\\CDX-20261001-001-hw-resume.md"
        code, payload = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(payload["hardware_state"], "OCCUPIED")
        self.assertNotIn("CDX-20261001-001-hw-resume.md", payload.get("unregistered_neutral_files") or [])
        self.assertFalse(any("未被应用" in r for r in payload["reasons"]), payload["reasons"])

    def test_30_bare_and_prefixed_duplicate_blocks(self) -> None:
        """裸名 + 前缀名混写同一文件 ⇒ 按 basename 判重复登记 → BLOCKED。"""
        self.add_record_file("CDX-20261001-001-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261001-001")
        path = self.mailbox / "CDX-20261001-001-hw-resume.md"
        self.records.append({"id": "CDX-20261001-001b", "file": path.name,   # 裸名
                             "sha256": sha_of(path), "order_key": "20261001-001b", "kind": "operation_doc"})
        code, payload = self.run_gate()
        self.assertEqual(code, 1)
        self.assertTrue(any("重复登记" in r or "缺少信箱目录前缀" in r for r in payload["reasons"]),
                        payload["reasons"])

    def test_31_duplicate_order_key_among_state_records_blocks(self) -> None:
        """两条状态类记录共用同一 order_key（排序歧义）⇒ BLOCKED。"""
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        p2 = self.mailbox / "CDX-20261001-002-hw-release-b.md"
        p2.write_text("不再占用（第二条）。\n", encoding="utf-8")
        self.records.append({"id": "CDX-20261001-002", "file": f"{self.mailbox.name}/{p2.name}",
                             "sha256": sha_of(p2), "order_key": "20261001-001",   # 与上条同 key
                             "kind": "hardware_release"})
        code, payload = self.run_gate()
        self.assertEqual(code, 1)
        self.assertTrue(any("order_key 重复" in r for r in payload["reasons"]), payload["reasons"])

    def test_32_occupied_reason_not_misleading(self) -> None:
        """非阻断观察 1：OCCUPIED 时不得输出"未提供匹配的 --release-id"这类误导理由。"""
        self.add_record_file("CDX-20261001-001-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261001-001")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 1)
        self.assertFalse(any("未提供匹配的 --release-id" in r for r in payload["reasons"]),
                         payload["reasons"])


    # ── 第三轮复审非阻断项 → 加固 ────────────────────────────────────────────────
    def test_33_occupied_reason_discriminating_fixture(self) -> None:
        """复审建议的可判别夹具：让出(920)+占用(921)，传 --release-id 920。

        固定版只应输出"占用态…"；若 OCCUPIED 守卫被回退，会额外出现
        "未提供匹配的 --release-id"（即使 id 相同）⇒ 该断言可判别。
        """
        self.add_record_file("CDX-20261001-920-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-920")
        self.add_record_file("CDX-20261002-921-hw-resume.md", "独占 JTAG/COM4。\n",
                             kind="hardware_occupation", order_key="20261002-921")
        code, payload = self.run_gate(release_id="CDX-20261001-920")
        self.assertEqual(code, 1)
        self.assertTrue(any("占用态" in r for r in payload["reasons"]), payload["reasons"])
        self.assertFalse(any("未提供匹配的 --release-id" in r for r in payload["reasons"]),
                         payload["reasons"])

    def test_34_cross_mailbox_same_basename_is_not_shadowed(self) -> None:
        """复审非阻断 3（既有 fail-open）：两信箱同名文件必须**都解析**，不得互相遮蔽。

        夹具：root1 的 X.md 正文自称占用（未登记）；root2 的 X.md 登记为 operation_doc
        + 一条更早的让出。若 scan 仍按 basename 去重（后者覆盖前者），门禁会 GO；
        修复后必须 BLOCKED（未登记交接 / 未被应用 之一）。
        """
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        dup_name = "CDX-20261009-009-notice.md"
        self.add_plain_file(dup_name, "现由本任务独占使用 JTAG 与 COM4。\n")   # root1：自称占用（未登记）
        root2 = self.tmp / "other_mailbox"
        root2.mkdir(exist_ok=True)
        p2 = root2 / dup_name
        p2.write_text("普通记录（登记为 operation_doc）。\n", encoding="utf-8")
        self.records.append({"id": "CDX-20261009-009", "file": f"{root2.name}/{dup_name}",
                             "sha256": sha_of(p2), "order_key": "20261009-009", "kind": "operation_doc"})
        code, payload = self.run_gate(release_id="CDX-20261001-001",
                                      extra=["--mailbox-root", str(root2)])
        self.assertEqual(code, 1, payload.get("reasons"))
        self.assertTrue(any(("正文含交接语义" in r) or ("未被应用" in r) or ("未登记的硬件交接" in r)
                            for r in payload["reasons"]), payload["reasons"])

    def test_35_tooling_wrapper_process_does_not_block(self) -> None:
        """2026-10-23 发现：ROSS 的 `vivado-mcp-server-…` 工具包装器不得被当作硬件占用。

        真实硬件进程（hw_server 等）仍必须阻断（见 test_12）；工具包装器单列 `tooling_processes`。
        """
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        code, payload = self.run_gate(release_id="CDX-20261001-001", process="stub-tooling")
        self.assertEqual(code, 0, payload.get("reasons"))
        self.assertEqual(payload["hardware_processes"], [])
        self.assertTrue(payload.get("tooling_processes"), "工具进程应被单列")
        self.assertFalse(any("检测到硬件/重型进程" in r for r in payload["reasons"]))

    # ── 第四轮复审关闭条件 B1：必须经过**真实分类路径**（classify_process_rows）─────────
    def _csv(self, rows: list[tuple[str, str]], name: str = "procs.csv") -> pathlib.Path:
        path = self.tmp / name
        path.write_text("\n".join(f'"{n}","{p}","Console","1","1 K"' for n, p in rows) + "\n",
                        encoding="utf-8")
        return path

    def test_36_tooling_name_via_real_classification_is_not_blocking(self) -> None:
        """伪造 tasklist CSV 经**真实分类函数** ⇒ `vivado-mcp-server-*` 单列且不阻断（GO）。

        判别力：若分类逻辑被删除（全部命中即阻断），本用例必失败。
        """
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        csv = self._csv([("vivado-mcp-server-windows-amd64-2026.9.1.exe", "10888"),
                         ("notepad.exe", "4242")])
        code, payload = self.run_gate(release_id="CDX-20261001-001", process="stub-csv", process_csv=csv)
        self.assertEqual(code, 0, payload.get("reasons"))
        self.assertEqual(payload["hardware_processes"], [])
        self.assertEqual([p["name"] for p in payload.get("tooling_processes") or []],
                         ["vivado-mcp-server-windows-amd64-2026.9.1.exe"])

    def test_37_all_hardware_names_via_real_classification_block(self) -> None:
        """伪造 CSV 含 6 类真实硬件进程名 ⇒ 全部判硬件且阻断。

        判别力：若 `TOOLING_PATTERN` 放宽为 `vivado`（把 `vivado.exe` 也当工具），本用例必失败。
        """
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        names = ["vivado.exe", "hw_server.exe", "xsdb.exe", "vitis.exe", "xsim.exe", "cs_server.exe",
                 "vivado-mcp-server-windows-amd64-2026.9.1.exe"]
        csv = self._csv([(n, str(9000 + i)) for i, n in enumerate(names)])
        code, payload = self.run_gate(release_id="CDX-20261001-001", process="stub-csv", process_csv=csv)
        self.assertEqual(code, 1)
        self.assertEqual(sorted(p["name"] for p in payload["hardware_processes"]), sorted(names[:-1]))
        self.assertEqual([p["name"] for p in payload["tooling_processes"]], [names[-1]])
        self.assertTrue(any("检测到硬件/重型进程" in r for r in payload["reasons"]))

    def test_38_port_3121_listening_blocks_even_if_names_are_tooling(self) -> None:
        """第二道门：进程名像工具但 **3121 有监听** ⇒ 视为硬件会话存在，必须阻断（防伪装命名）。"""
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        csv = self._csv([("vivado-mcp-server-windows-amd64-2026.9.1.exe", "10888")])
        code, payload = self.run_gate(release_id="CDX-20261001-001", process="stub-csv",
                                      process_csv=csv, port="stub-listening")
        self.assertEqual(code, 1)
        self.assertTrue(payload.get("port_3121_listening"))
        self.assertTrue(any("3121" in r for r in payload["reasons"]), payload["reasons"])


if __name__ == "__main__":
    unittest.main(verbosity=2)