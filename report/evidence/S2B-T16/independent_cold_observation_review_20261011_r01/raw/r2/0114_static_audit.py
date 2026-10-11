"""独立只读差异/官方依据审计；结果仅创建在当前审查目录。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
BASELINE = "6d3fd8567b579a51d4042667d47af7d94f2f5a97"


def digest(raw):
    """按原字节计算SHA256。"""
    return hashlib.sha256(raw).hexdigest()


def definitions(text):
    """比较AST，排除与语义无关的行号。"""
    tree = ast.parse(text)
    return {node.name: ast.dump(node, include_attributes=False) for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))}


name = "vitis/run_s2b_visibility_probe.py"
before = subprocess.check_output(["git", "show", BASELINE + ":" + name], cwd=ROOT).decode("utf-8")
after = (ROOT / name).read_text(encoding="utf-8")
normalized = after.replace("# 固定T16完整字段观测候选；此绑定不替代总控核验独立G2及实板兼容批准。\n", "")
normalized = normalized.replace("1ce01c810715e6c20f2952d3488ebb6ce8f7792861075e1a25bbc1f91db7651b", "91bbf5bc8ac5ef9bee37ce6491627a6ac8f38a53b7bba113d1b83447b2ecddf0")
normalized = normalized.replace("必须使用固定T16候选精确版本", "必须使用已审T16 G2精确版本")
assert ast.dump(ast.parse(normalized), include_attributes=False) == ast.dump(ast.parse(before), include_attributes=False)
unchanged = [name for name, body in definitions(after).items() if name in definitions(before) and body == definitions(before)[name]]
required = ("sdk_source_closure", "verify_sdk_files", "verify_runtime_sources", "verify_native_alias", "_loaded_native_images", "run", "_runtime")
assert set(required) <= set(unchanged)
current = (ROOT / "verification/s2b_board_jtag.py").read_bytes()
coverage = '    require(occupied == set(range(32)), "CONFIG_STATUS字段metadata未完整覆盖位0..31")\n'.encode("utf-8")
assert current.count(coverage) == 1
reconstructed = current.replace(coverage, b"")
r1_sha = "b48533d9ea42eb779e7db55816539efc2a15a9249595b754f67d28394bcf59cf"
assert digest(reconstructed) == r1_sha
with (RUN / "reconstructed_r1_s2b_board_jtag.py").open("xb") as out:
    out.write(reconstructed)
ps7 = ROOT / "report/evidence/S2B-T15/full_build_20261011_r01/ps7_init.c"
assert ps7.is_file() and digest(ps7.read_bytes()) == "95f228bce034590569f2bec887cf2e7375997c62c935e43fe1e9d4a3a1818393"
text = ps7.read_text(encoding="utf-8")
assert "EMIT_MASKPOLL(0XF8006054, 0x00000007U)" in text and "while (!(*addr & mask))" in text
result = {
  "status": "PASS",
  "source_baseline": BASELINE,
  "t19_semantic_changes": ["固定T16源码SHA", "门禁提示由已审版本改称候选版本"],
  "t19_original_definitions_unchanged": unchanged,
  "t19_sdk_native_class_alias_method_gate_unchanged": True,
  "r1_production_reconstruction": {"sha256": digest(reconstructed), "expected": r1_sha,
      "method": "从R2原字节仅移除新增完整0..31覆盖断言；所得原字节SHA与R1冻结SHA完全相同。",
      "scope": "仅T16生产源完整恢复；R1两个测试源原副本未提供，不声称完整恢复。"},
  "r2_t16_vs_r1_exact_change": "只增加occupied == set(range(32))的require断言。",
  "ps7_mask_poll": {"path": str(ps7.relative_to(ROOT)), "sha256": digest(ps7.read_bytes()),
      "fact": "旧MASKPOLL只证明mask7非零；本次正常模式校验严格要求低3位等于1。"},
  "official_sources": [
      {"url": "https://docs.amd.com/api/khub/documents/FOs3lXmlcWxBhTIFxVKyGA/content", "title": "UG470 v1.17 表5-29 印刷107页", "fact": "EOS bit4表示启动序列是否结束。"},
      {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-ddrc-mode_sts_reg", "title": "UG585 v1.15 mode_sts_reg", "fact": "地址0xF8006054。"},
      {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-mode_sts_reg-Details", "title": "UG585 v1.15 mode_sts_reg Details", "fact": "operating_mode[2:0]仅1为normal；0/2..7不是normal。"}],
  "interface": {"path": "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
      "sha256": digest((ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md").read_bytes()),
      "reviewed_lines": [137, 139, 141, 143, 145], "fact": "完整冷恢复还需旧AXI生命周期结束、arena/cache与所有writer等事实；本次未批准。"},
  "hardware_calls": 0
}
with (RUN / "static_audit.json").open("x", encoding="utf-8", newline="\n") as out:
    json.dump(result, out, ensure_ascii=False, indent=2)
    out.write("\n")
print(json.dumps({"status": result["status"], "r1_production_sha256": r1_sha, "unchanged_t19_definitions": len(unchanged)}, ensure_ascii=False))
