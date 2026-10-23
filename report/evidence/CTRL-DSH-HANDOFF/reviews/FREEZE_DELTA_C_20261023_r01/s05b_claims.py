# 检查 5b：r10 包内声明的真实性
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import run

G4 = "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d"
R10 = "report/evidence/S6-A/s6a_g0_20261023_r10"


def get(path, rev=G4):
    rc, out, err = run(["show", f"{rev}:{path}"])
    return out if rc == 0 else None


print("################ transport_clone_check.py 默认输出路径 ################")
rc, out, _ = run(["show", "HEAD:verification/transport_clone_check.py"])
for ln in (out or "").splitlines():
    if "add_argument" in ln or "default" in ln:
        print("   ", ln.strip())

print("\n################ r10/fix_record.json ################")
print(json.dumps(json.loads(get(f"{R10}/fix_record.json")), ensure_ascii=False, indent=2)[:6000])

print("\n################ r10/selfcheck_result.json 摘要 ################")
j = json.loads(get(f"{R10}/selfcheck_result.json"))
print("status =", j.get("status"), " keys =", sorted(j.keys()))
for c in (j.get("checks") or []):
    print(f"   {c.get('id'):6s} {c.get('status'):8s} {str(c.get('detail'))[:120]}")

print("\n################ r10/check_evidence_mode_output.txt ################")
print(get(f"{R10}/check_evidence_mode_output.txt"))
print("################ r10/check_inputs_mode_output.txt ################")
print(get(f"{R10}/check_inputs_mode_output.txt"))
print("################ r10/selfcheck_c11_stdout.txt（末 40 行）################")
t = get(f"{R10}/selfcheck_c11_stdout.txt") or ""
print("\n".join(t.splitlines()[-40:]))

print("\n################ r10/S6A_run_summary.md ################")
print(get(f"{R10}/S6A_run_summary.md"))

print("\n################ 两份 transport_clone_selfproof.json（G4）################")
for p in ["report/evidence/S6-A/s6a_g0_20261023_r10_selfproof/transport_clone_selfproof.json",
          "report/evidence/S6-B/s6b_core_20261023_r05_selfproof/transport_clone_selfproof.json"]:
    print(f"--- {p} ---")
    print(json.dumps(json.loads(get(p)), ensure_ascii=False, indent=2))

print("\n################ 两份 export_selfproof.json（G4）subject 详情 ################")
for p in ["report/evidence/S6-A/s6a_g0_20261023_r10_selfproof/export_selfproof.json",
          "report/evidence/S6-B/s6b_core_20261023_r05_selfproof/export_selfproof.json"]:
    j = json.loads(get(p))
    print(f"--- {p}: verdict={j.get('verdict')}")
    for k, v in j.items():
        if k == "subjects":
            for s in v:
                print(f"    subject label={s.get('label')} verdict={s.get('verdict')} "
                      f"checks={[ (c.get('id'), c.get('status'), c.get('exit_code')) for c in (s.get('checks') or []) ]}")
        else:
            print(f"    {k} = {json.dumps(v, ensure_ascii=False)[:200]}")