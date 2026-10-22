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
            self.records.append({"id": name.split("-")[0] + "-" + order_key, "file": name,
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
        path.write_text(json.dumps({"schema_version": "test", "state_changing_kinds":
                                    ["hardware_occupation", "hardware_release"], "records": self.records},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def run_gate(self, *, process: str = "stub-ok", lock: str = "stub-none", release_id: str | None = None,
                 registry: pathlib.Path | None = None, mailbox_root: pathlib.Path | None = None,
                 extra: list[str] | None = None, out_name: str = "out",
                 use_real_mailbox: bool = False) -> tuple[int, dict]:
        out_dir = self.tmp / out_name
        cmd = [sys.executable, "-B", str(GATE), "--out", str(out_dir),
               "--registry", str(registry or self.write_registry()),
               "--process-check", process, "--lock-check", lock, "--main-state", str(self.state)]
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
        self.add_plain_file("CDX-20261002-002-ordinary-runbook.md", "普通操作文档：提到释放与独占字样。\n")
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

    def test_04_plain_doc_body_words_cannot_masquerade(self) -> None:
        self.add_record_file("CDX-20261001-001-hw-release.md", "不再占用。\n",
                             kind="hardware_release", order_key="20261001-001")
        # 正文含“释放/独占”，但文件名无交接语义、无声明标记 → 中性，不得冒充通知
        self.add_plain_file("CDX-20261009-009-notes.md", "本节说明释放流程与独占要求：release/exclusive 均出现。\n")
        code, payload = self.run_gate(release_id="CDX-20261001-001")
        self.assertEqual(code, 0, payload.get("reasons"))
        kinds = [r.get("kind") for r in payload["neutral_records"]]
        self.assertIn("unregistered_neutral", kinds)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)