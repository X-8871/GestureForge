# -*- coding: utf-8 -*-
"""独立评审：用真实 git 字节重跑 r01/r02/r03 旧包，并自算哈希与提交证据比对。

严格复刻 s6a_rerun_legacy_failures.py 的调用方式，但所有落盘都写到隔离评审目录。
"""
import json, subprocess, os, sys, hashlib

WT = r"D:\codex-worktrees\w6"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "legacy_rerun")
os.makedirs(WORK, exist_ok=True)
R04 = os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r04")

LEGACY = [
    ("r01", "old", "1fe4648cba5a9f1ffc87dbe21cea732b72716bff", "s6a_g0_20261022_r01",
     "old_package_under_test.json", "selfcheck_old_package_failure.json"),
    ("r02", "r02", "3b59674f93e8a2c020a0670fa475ee6a15330833", "s6a_g0_20261022_r02",
     "r02_package_under_test.json", "selfcheck_r02_blk1_failure.json"),
    ("r03", "r03", "2ce290f495e3bd50b249158be9f4f876a5f8e3fb", "s6a_g0_20261022_r03",
     "r03_package_under_test.json", "selfcheck_r03_failure.json"),
]

def blob(rev, rel):
    p = subprocess.run(["git", "-C", WT, "cat-file", "blob", f"{rev}:{rel}"], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", "replace"))
    return p.stdout

out = []
def P(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    out.append(line)

P("=" * 96)
P("旧包重跑（最终版自检 + 真实 git 字节）")
P("=" * 96)

for label, tag, commit, evrun, pkgname, failname in LEGACY:
    base = f"report/evidence/S6-A/{evrun}"
    paths = {
        "behavior": "docs/stage6/s6a_stage6_g0_behavior_v1.json",
        "doc": "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
        "cases": f"{base}/hand_computed_cases.json",
        "bindings": f"{base}/upstream_bindings.json",
        "state": ".codex/STATE.md",
    }
    extracted = {}
    myhashes = {}
    for key, rel in paths.items():
        payload = blob(commit, rel)
        p = os.path.join(WORK, f"{tag}_{key}{os.path.splitext(rel)[1]}")
        with open(p, "wb") as f:
            f.write(payload)
        extracted[key] = p
        myhashes[rel] = hashlib.sha256(payload).hexdigest()

    outfile = os.path.join(WORK, f"my_{tag}_failure.json")
    cmd = [sys.executable, "-B", os.path.join(WT, "verification/s6_g0_selfcheck.py"),
           "--json", extracted["behavior"], "--doc", extracted["doc"],
           "--cases", extracted["cases"], "--upstream", extracted["bindings"],
           "--out", outfile, "--project-root", WT,
           "--evidence-dir", os.path.join(WT, base)]
    if os.path.isfile(extracted["state"]):
        cmd += ["--state", extracted["state"]]
    p = subprocess.run(cmd, capture_output=True, cwd=WT)
    res = json.load(open(outfile, encoding="utf-8"))
    myfailed = [c["id"] for c in res["checks"] if c["status"] == "FAIL"]

    committed = json.load(open(os.path.join(R04, failname), encoding="utf-8"))
    cfailed = [c["id"] for c in committed["checks"] if c["status"] == "FAIL"]

    P("")
    P(f"--- {label}  commit={commit}")
    P(f"    我的重跑: exit={p.returncode}  status={res['status']}  FAILED={myfailed}")
    P(f"    提交证据: exit(observed)={committed.get('inputs',{}).get('evidence_dir') is not None} "
      f"status={committed['status']}  FAILED={cfailed}")
    P(f"    失败项一致 = {myfailed == cfailed}")
    if myfailed != cfailed:
        P(f"      仅我有={sorted(set(myfailed)-set(cfailed))} 仅提交有={sorted(set(cfailed)-set(myfailed))}")
    # 逐项失败详情对比
    md = {c["id"]: c["detail"] for c in res["checks"] if c["status"] == "FAIL"}
    cd = {c["id"]: c["detail"] for c in committed["checks"] if c["status"] == "FAIL"}
    same_detail = all(md.get(k) == cd.get(k) for k in set(md) | set(cd))
    P(f"    失败详情逐字一致 = {same_detail}")
    for k in myfailed:
        P(f"      [{k}] 我: {md[k][:230]}")
        P(f"      [{k}] 提交: {cd.get(k, '<无>')[:230]}")

    # 哈希比对
    cpkg = json.load(open(os.path.join(R04, pkgname), encoding="utf-8"))
    P(f"    哈希比对（我对 git 字节自算 vs 提交的 package_under_test）：")
    allok = True
    for row in cpkg["files_under_test"]:
        rel = row["path"]
        mine = myhashes.get(rel)
        ok = (mine == row["sha256"])
        allok &= ok
        P(f"      {'OK ' if ok else 'MISMATCH'} {rel}")
        if not ok:
            P(f"         mine={mine} committed={row['sha256']}")
    P(f"    全部哈希一致 = {allok}")
    P(f"    提交证据记录的 observed.exit_code={cpkg.get('observed',{}).get('exit_code')} "
      f"status={cpkg.get('observed',{}).get('status')} "
      f"failed_checks={cpkg.get('observed',{}).get('failed_checks')}")

P("")
P("=" * 96)
P("r04 自身入库自检结果 vs 我的重跑")
P("=" * 96)
mine = json.load(open(os.path.join(HERE, "my_selfcheck_r04.json"), encoding="utf-8"))
comm = json.load(open(os.path.join(R04, "selfcheck_result.json"), encoding="utf-8"))
P(f"  我:   status={mine['status']} checks={len(mine['checks'])} errors={len(mine['errors'])}")
P(f"  入库: status={comm['status']} checks={len(comm['checks'])} errors={len(comm['errors'])}")
P(f"  逐项状态一致 = {[(c['id'],c['status']) for c in mine['checks']] == [(c['id'],c['status']) for c in comm['checks']]}")
P(f"  逐项 detail 逐字一致 = {[c['detail'] for c in mine['checks']] == [c['detail'] for c in comm['checks']]}")
P(f"  入库 inputs.behavior_json_sha256 = {comm['inputs']['behavior_json_sha256']}")
P(f"  入库 inputs.human_doc_sha256     = {comm['inputs']['human_doc_sha256']}")
P(f"  入库 inputs.hand_cases_sha256    = {comm['inputs']['hand_cases_sha256']}")

with open(os.path.join(HERE, "legacy_rerun.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")