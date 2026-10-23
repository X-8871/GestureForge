# 验证附录 claim_verification（v2：真实退出码）

每条声明的 exit_code 均为**真实 subprocess 退出码**；命令可独立复算（无占位符）；内置 self_test_false_claim 证明本工具对假声明会 FAIL；verdict 由**全部** claim 计算，且 claims 数量必须等于定义数 + 1，空列表/数量不符一律 NOT_ALL_VERIFIED。

- 生成：2026-10-24 02:05:45；判定：**ALL_CLAIMS_VERIFIED**
- 复算命令：`python -B verification/claim_verify.py --package s6b --run-dir report/evidence/S6-B/s6b_core_20261024_r08 --project-root D:\codex-worktrees\w6`

## S6B-C1-acquisition-id-lifecycle — VERIFIED

- 声明：BLK-r03-1：M8/M2/M12 等结束获取的转移分配新 acquisition_id（三例实测 [0,1]/[0,2]/[0,1,2]）
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -c "import json;d=json.load(open('report/evidence/S6-B/s6b_core_20261024_r08/run_report.json',encoding='utf-8'));ids={c['case_id']:[r.get('acquisition_id') for r in (c['observed'].get('action_records') or [])] for c in d['cases']};want={'C12-m8-two-acquisitions':[0,1],'C12-m2-m12-new-target':[0,2],'C12-gate-reopen-new-acquisition':[0,1,2]};bad={k:(want[k],ids.get(k)) for k in want if ids.get(k)!=want[k]};print('status=',d['status'],'ids=',{k:ids.get(k) for k in want});assert d['status']=='PASS';assert not bad, bad"`
- 真实退出码：0（期望 0）
- 可观察输出：["status= PASS ids= {'C12-m8-two-acquisitions': [0, 1], 'C12-m2-m12-new-target': [0, 2], 'C12-gate-reopen-new-acquisition': [0, 1, 2]}"]

## S6B-C2-action-records-fields — VERIFIED

- 声明：action_records 含四个必需字段，且四个 ACTION_* 事件名在证据中出现
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -c "import json;d=json.load(open('report/evidence/S6-B/s6b_core_20261024_r08/run_report.json',encoding='utf-8'));recs=[r for c in d['cases'] for r in (c['observed'].get('action_records') or [])];need=('action_type','target_id','acquisition_id','t_trigger_ns');miss=[k for k in need if not all(k in r for r in recs)];ev=set()
for r in recs: ev.update([r.get('event'),r.get('effective_event')])
four=[x for x in ('ACTION_SUBMITTED','ACTION_EFFECTIVE','ACTION_FAILED','ACTION_UNOBSERVED') if x not in ev];print('records=',len(recs),'missing_fields=',miss,'missing_events=',four);assert not miss and not four"`
- 真实退出码：0（期望 0）
- 可观察输出：['records= 25 missing_fields= [] missing_events= []']

## S6B-C3-no-dead-constants — VERIFIED

- 声明：核心与动作层没有定义后从未使用的常量
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B verification/s6b_no_dead_constants.py`
- 真实退出码：0（期望 0）
- 可观察输出：['unused=[]']

## S6B-C5-approved-package-scan — VERIFIED

- 声明：S6-B 侧等价断言：已批准版包内**不得出现 PENDING/待批准 陈述**（大小写不敏感机读扫描；逐行机读历史标记/非批准类状态/禁止性规则描述除外；probe_* 与 selfcheck_*failure* 按文件豁免）；S6-B 此前完全无 approval 断言，属不可接受缺口；含**两向注入自测**
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B verification/approved_package_scan.py --project-root D:\codex-worktrees\w6 --run-dir report/evidence/S6-B/s6b_core_20261024_r08 --inject-self-test --out D:\codex-worktrees\w6\tmp\6\claim_runs\s6b_core_20261024_r08\approved_package_scan.json`
- 真实退出码：0（期望 0）
- 可观察输出：['{"verdict": "AS_EXPECTED", "hits": 0, "self_test": "AS_EXPECTED", "missed_forms": [], "false_positive_forms": []}']

## S6B-C4-m4-counted-and-registrations — VERIFIED

- 声明：M4 计入覆盖；未实现项与开放行为偏差均已登记
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -c "import json;L=json.load(open('report/evidence/S6-B/s6b_core_20261024_r08/limitations_not_executed.json',encoding='utf-8'));print('not_implemented=',len(L.get('not_implemented') or []),'open_deviations=',len(L.get('open_behavior_deviations') or []),'counted=',L.get('reachability_counted'));assert L.get('not_implemented') and L.get('open_behavior_deviations') and any('M4' in str(x) for x in (L.get('reachability_counted') or []))"`
- 真实退出码：0（期望 0）
- 可观察输出：["not_implemented= 1 open_deviations= 1 counted= ['M4（TARGET_CONTINUES 不含 score ≥ T6-P02 → M10 不先命中；用例 C4-jitter-reset）']"]

## self_test_false_claim — VERIFIED

- 声明：故意为假的声明（assert 1==2）必须得到非 0 退出码——证明本工具会 FAIL
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -c "assert 1==2"`
- 真实退出码：1（期望 非 0）
- 可观察输出：['AssertionError']

本附录只证明这些声明在**本次真实执行**下成立；不代表独立审查或验收通过。
