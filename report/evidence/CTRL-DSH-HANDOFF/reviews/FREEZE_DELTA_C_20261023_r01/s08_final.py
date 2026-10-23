import sys, os, json, hashlib, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import run

G4 = "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d"
F4 = "6b8e5f2a23ce6f7dec41fc9992141b3423612081"
CLONE = r"D:\FPGA_Competition\tmp\review\FREEZE_DELTA_C_20261023_r01\clone"

print("#### 我的临时克隆的 git status（证明 simulate-defect 会改写 run-dir）")
rc, out, err = run(["status", "--short"], cwd=CLONE)
print(f"[exit {rc}]\n{out}")
j = json.loads(open(os.path.join(CLONE, "report/evidence/S6-A/s6a_g0_20261023_r10/claim_verification.json"),
                    encoding="utf-8").read())
print("克隆内 r10 附录现状（我最后一次 empty 注入后）: verdict=", j["verdict"],
      " recorded=", j["claims_recorded"], " count_ok=", j["count_ok"],
      " generated_at=", j["generated_at_utc8"])

print("\n#### 冻结包内 fresh_selfcheck_pair.json 是否被清单绑定 + 哈希一致性")
man = json.loads(run(["show", f"{G4}:report/evidence/S6-A/s6a_g0_20261023_r10/delivery_manifest.json"])[1])
tgt = "report/evidence/S6-A/s6a_g0_20261023_r10/fresh_selfcheck_pair.json"
decl = [f for f in man.get("files", []) if f["path"] == tgt]
print("  清单声明条目:", json.dumps(decl, ensure_ascii=False))
blob = run(["cat-file", "blob", f"{G4}:{tgt}"])[1]
print("  提交内 blob LF 哈希:", hashlib.sha256(blob.encode("utf-8")).hexdigest())
wt = open(r"D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261023_r10\fresh_selfcheck_pair.json", "rb").read()
print("  w6 工作区原字节哈希:", hashlib.sha256(wt).hexdigest())
print("  w6 工作区 CRLF->LF 哈希:", hashlib.sha256(wt.replace(b"\r\n", b"\n")).hexdigest())

print("\n#### r10 与 r05 的 tool_self_tests.json 是否同内容")
a = run(["cat-file", "blob", f"{G4}:report/evidence/S6-A/s6a_g0_20261023_r10/tool_self_tests.json"])[1]
b = run(["cat-file", "blob", f"{G4}:report/evidence/S6-B/s6b_core_20261023_r05/tool_self_tests.json"])[1]
print("  同内容:", a == b, " sha256:", hashlib.sha256(a.encode()).hexdigest()[:16])

print("\n#### 声明 10/10 的位置（STATE）与套件产物对比")
st = run(["show", f"{G4}:.codex/STATE.md"])[1]
for i, ln in enumerate(st.splitlines(), 1):
    if "10/10" in ln or "20 分钟" in ln:
        print(f"  STATE:{i}: {ln.strip()[:200]}")

print("\n#### w6 只读性终检")
rc, out, err = run(["status", "--short"])
print(f"git status --short [exit {rc}]: {out.strip() or '(空 = 无改动)'}")
rc, out, _ = run(["rev-parse", "HEAD"])
print("HEAD =", out.strip())
rc, out, _ = run(["diff", "--stat", "HEAD"])
print("diff HEAD [exit %d]: %s" % (rc, out.strip() or "(无差异)"))