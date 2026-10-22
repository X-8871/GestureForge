import copy
import hashlib
import json
from pathlib import Path

root = Path(r"D:\codex-worktrees\w4")
contract_path = root / "docs/stage4/s4b_shared_input_result_contract.json"
contract_md_path = root / "docs/stage4/S4B_shared_input_result_contract.md"
s4a_path = root / "docs/stage4/s4a_stage4_g0_fields.json"
s4a_md_path = root / "docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md"
address_path = root / "docs/stage4/S4B_stage4_address_map.json"
runbook_path = root / "docs/stage4/S4B_injection_path_runbook.md"
header_path = root / "vitis/stage4/s4_inject_frame.h"
w5_path = Path(r"D:\codex-worktrees\w5\docs\stage5\s5a_stage5_display_g0_fields.json")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def find_key(obj, name):
    if isinstance(obj, dict):
        if name in obj:
            return obj[name]
        for value in obj.values():
            found = find_key(value, name)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_key(value, name)
            if found is not None:
                return found
    return None

def first_field(obj, name):
    fields = obj["input_frame_contract"]["fields"]
    return next(field for field in fields if field["name"] == name)

contract = read_json(contract_path)
s4a = read_json(s4a_path)
address = read_json(address_path)
w5 = read_json(w5_path)
runbook_lines = runbook_path.read_text(encoding="utf-8").splitlines()
roles = find_key(contract, "mapping_key_roles")
unique_key = find_key(contract, "unique_mapping_key")
hud = find_key(contract, "hud_field_sources")
display = find_key(contract, "display_linkage")
stale = find_key(contract, "stale_rule")
input_contract = contract["input_frame_contract"]
vocab = input_contract["vocabulary_mapping"]["source_kind"]
truth = input_contract["vocabulary_mapping"]["capture_time_truth_table"]
s4a_map = s4a["uart_plan_b_freeze"]["result_bypass_log_mapping"]
scope_kinds = {key: body["source_kind"] for key, body in s4a["scope_freeze"].items() if key != "description"}
runbook_step = next((line for line in runbook_lines if "# 4)" in line), "")
runbook_step_no = next((i for i, line in enumerate(runbook_lines, 1) if "# 4)" in line), None)
runbook_summary_no = next((i for i, line in enumerate(runbook_lines, 1) if "覆盖：阶段4 单帧注入通路" in line), None)
checks = []
def record(name, passed, evidence):
    checks.append({"name": name, "status": "PASS" if passed else "FAIL", "evidence": evidence})

record("contract_identity", contract.get("revision") == "r03" and contract.get("status") == "DRAFT_PENDING_REVIEW",
       {"revision": contract.get("revision"), "status": contract.get("status")})
record("s4a_r06_identity", s4a.get("status") == "G0_ROUND_FROZEN_R06" and s4a.get("revision") == "r06",
       {"status": s4a.get("status"), "revision": s4a.get("revision"), "sha256": sha(s4a_path)})
record("s4a_markdown_binding", sha(s4a_md_path) in contract_md_path.read_text(encoding="utf-8"),
       {"actual_sha256": sha(s4a_md_path), "contract_line": 13})
record("address_map_remains_draft", address.get("status") == "DRAFT_PENDING_REVIEW" and "DRAFT_PENDING_REVIEW" in contract_md_path.read_text(encoding="utf-8"),
       {"address_status": address.get("status"), "contract_line": 14, "address_sha256": sha(address_path)})
record("session_id_u32_and_c_binding", first_field(contract, "session_id").get("type") == "uint32" and "uint32_t session_id;" in header_path.read_text(encoding="utf-8"),
       {"contract_type": first_field(contract, "session_id").get("type"), "C_header_line": 147})
expected_map = {"file_injection": "BOARD_INJECTION", "synthetic": "OFFLINE_REGRESSION", "camera": "CAMERA"}
record("source_kind_bijection", vocab.get("map") == expected_map and scope_kinds == expected_map,
       {"contract_map": vocab.get("map"), "s4a_scopes": scope_kinds})
expected_truth = {
    "file_injection": {"capture_time_available": False, "capture_time_ns": 0, "unavailable_fields_contains_capture_time_ns": True},
    "synthetic": {"capture_time_available": False, "capture_time_ns": 0, "unavailable_fields_contains_capture_time_ns": True},
    "camera": {"capture_time_available": True, "capture_time_ns": "nonzero", "unavailable_fields_contains_capture_time_ns": False},
}
record("capture_time_truth_table", truth == expected_truth and "source_kind" in first_field(contract, "measurement_scope").get("semantics", ""),
       {"truth_table": truth, "contract_lines": [36, 38, 41, 56]})
expected_roles = {
    "stage4a_join_key": s4a_map["join_key"],
    "ps_log_primary_key": s4a_map["ps_log_primary_key"],
    "uart_observable_key": s4a_map["uart_observable_key"],
    "contract_result_key": ["session_id", "frame_id", "result_seq"],
}
roles_ok = all(roles[key]["fields"] == value for key, value in expected_roles.items() if key != "contract_result_key")
roles_ok = roles_ok and roles["contract_result_key"]["fields"] == expected_roles["contract_result_key"]
record("key_roles_match_s4a", roles_ok and unique_key == expected_roles["contract_result_key"],
       {"s4a": s4a_map, "contract_roles": roles, "contract_unique_key": unique_key})
record("uart_option_b_preserved", s4a["uart_plan_b_freeze"]["interface"] == "s2bu/1.1" and
       s4a["uart_plan_b_freeze"]["interface_unchanged"] is True and
       s4a["uart_plan_b_freeze"]["extension_closed"] is True and
       "PS 侧旁路日志" in s4a["uart_plan_b_freeze"]["side_channel"],
       {"s4a": s4a["uart_plan_b_freeze"], "contract_md_lines": [84, 85]})
record("display_semantics_matches_w5", display["fields"][-1]["values"] == [w5["display_semantics"]["value"]] and
       w5["display_semantics"]["value"] == "B_latest_result_overlay",
       {"contract_values": display["fields"][-1]["values"], "w5_value": w5["display_semantics"]["value"], "w5_sha256": sha(w5_path)})
record("hud_13_fields_match_w5", set(hud) == set(find_key(w5, "hud_fields")) and len(hud) == 13,
       {"contract_count": len(hud), "w5_count": len(find_key(w5, "hud_fields")), "keys": sorted(hud)})
not_frozen = {item["id"]: item["status"] for item in s4a["g0_round_freeze"]["not_frozen_items"]}
record("stale_200ms_not_approved", stale["stale_limit_ns"] is None and
       stale["stale_limit_status"] == "DRAFT_PENDING_APPROVAL" and
       stale["stale_limit_draft_value_ms"] == 200 and
       not_frozen.get("stale_age_limit") == "DRAFT_PENDING_APPROVAL",
       {"contract": stale, "s4a_status": not_frozen.get("stale_age_limit"), "s4a_lines": [90, 97, 901]})
boundary = s4a["candidate_limit_boundary_test"]
record("candidate_boundary_spec", boundary["limit"] == 12675 and
       boundary["exact_limit_case"]["candidate_count"] == 12675 and
       boundary["over_limit_case"]["append_attempt"] == 12676 and
       boundary["over_limit_case"]["expected_error"] == "S2A_T62_INVALID_ARGUMENT" and
       boundary["truncation_defined"] is False and
       boundary["deprecated_4096"]["enabled"] is False,
       {"limit": boundary["limit"], "exact": boundary["exact_limit_case"], "over": boundary["over_limit_case"], "deprecated_4096": boundary["deprecated_4096"]})
events = input_contract["events"]["order"]
expected_events = ["producer_write_start", "producer_write_complete", "cache_flush_by_producer",
                   "ownership_publish_to_consumer", "consumer_invalidate", "consumer_start",
                   "consumer_done", "buffer_release_to_producer"]
record("contract_and_address_input_order", events == expected_events and
       "所有权发布后，消费者必须先对输入帧区间 invalidate + DSB，再开始读取" in address["consumer_rule"],
       {"contract_order": events, "address_consumer_rule": address["consumer_rule"]})
wrong_order = runbook_step.find("读结果") >= 0 and runbook_step.find("读结果") < runbook_step.find("invalidate")
record("4d_runbook_heads_order", not wrong_order,
       {"line": runbook_step_no, "text": runbook_step, "required": "等 PL done → invalidate + DSB → 读结果 → 释放"})
summary = next((line for line in runbook_lines if "覆盖：阶段4 单帧注入通路" in line), "")
record("runbook_scope_summary_clear", "读取结果/invalidate" not in summary,
       {"line": runbook_summary_no, "text": summary, "detail_lines": [45, 47, 51, 52]})

bindings = contract["upstream_bindings"]
binding_rows = []
for binding in bindings:
    raw_path = Path(binding["path"])
    actual_path = raw_path if raw_path.is_absolute() else root / raw_path
    actual = sha(actual_path) if actual_path.is_file() else None
    binding_rows.append({"id": binding["id"], "expected": binding.get("sha256"), "actual": actual,
                         "status": "MATCH" if actual is not None and actual == binding.get("sha256") else "MISSING_OR_MISMATCH"})
record("six_upstream_hashes", len(binding_rows) == 6 and all(row["status"] == "MATCH" for row in binding_rows),
       binding_rows)

mutations = []
def semantic_core(candidate):
    candidate_field = next(field for field in candidate["input_frame_contract"]["fields"] if field["name"] == "session_id")
    candidate_roles = find_key(candidate, "mapping_key_roles")
    candidate_vocab = candidate["input_frame_contract"]["vocabulary_mapping"]["source_kind"]["map"]
    candidate_truth = candidate["input_frame_contract"]["vocabulary_mapping"]["capture_time_truth_table"]
    return (candidate_field.get("type") == "uint32" and
            candidate_roles["stage4a_join_key"]["fields"] == s4a_map["join_key"] and
            candidate_roles["ps_log_primary_key"]["fields"] == s4a_map["ps_log_primary_key"] and
            candidate_roles["uart_observable_key"]["fields"] == s4a_map["uart_observable_key"] and
            candidate_vocab == expected_map and candidate_truth == expected_truth)
mutant = copy.deepcopy(contract)
next(field for field in mutant["input_frame_contract"]["fields"] if field["name"] == "session_id")["type"] = "string"
mutations.append({"name": "session_id_string", "rejected": not semantic_core(mutant)})
mutant = copy.deepcopy(contract)
mutant["input_frame_contract"]["vocabulary_mapping"]["source_kind"]["map"]["synthetic"] = "synthetic"
mutations.append({"name": "synthetic_wrong_target", "rejected": not semantic_core(mutant)})
mutant = copy.deepcopy(contract)
mutant["input_frame_contract"]["vocabulary_mapping"]["capture_time_truth_table"]["synthetic"]["capture_time_available"] = True
mutations.append({"name": "synthetic_capture_available_true", "rejected": not semantic_core(mutant)})
mutant = copy.deepcopy(contract)
mutant["result_contract"]["ps_side_log"]["mapping_key_roles"]["ps_log_primary_key"]["fields"] = ["session_id", "frame_id"]
mutations.append({"name": "ps_log_key_role_swapped", "rejected": not semantic_core(mutant)})
mutation_pass = all(row["rejected"] for row in mutations)

result = {
    "review": "S4-G2-R1-02",
    "head": "af85d5a8495598262395165492df5e4d0bfb723c",
    "branch": "stage4-infer-prep",
    "contract_json_sha256": sha(contract_path),
    "contract_md_sha256": sha(contract_md_path),
    "s4a_json_sha256": sha(s4a_path),
    "s4a_md_sha256": sha(s4a_md_path),
    "address_map_sha256": sha(address_path),
    "runbook_sha256": sha(runbook_path),
    "checks": checks,
    "mutation_probes": mutations,
    "mutation_probes_all_rejected": mutation_pass,
    "failures": [item for item in checks if item["status"] != "PASS"],
    "status": "PASS" if all(item["status"] == "PASS" for item in checks) and mutation_pass else "CHANGES_REQUIRED",
    "limits": ["32-bit behavior and real board/PS/BSP/PL/UART/camera execution were not performed."]
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "checks": len(checks),
                  "failures": result["failures"], "mutation_probes": mutations,
                  "mutation_probes_all_rejected": mutation_pass,
                  "file_hashes": {k: result[k] for k in ("contract_json_sha256", "contract_md_sha256", "s4a_json_sha256", "s4a_md_sha256", "address_map_sha256", "runbook_sha256")}}, ensure_ascii=False, indent=2))

