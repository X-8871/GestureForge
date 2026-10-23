# 验证附录 claim_verification（v2：真实退出码）

每条声明的 exit_code 均为**真实 subprocess 退出码**；命令可独立复算（无占位符）；内置 self_test_false_claim 证明本工具对假声明会 FAIL；verdict 由**全部** claim 计算，且 claims 数量必须等于定义数 + 1，空列表/数量不符一律 NOT_ALL_VERIFIED。

- 生成：2026-10-23 08:15:08；判定：**ALL_CLAIMS_VERIFIED**
- 复算命令：`python -B verification/claim_verify.py --package s6a --run-dir D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261023_r10 --project-root D:\codex-worktrees\w6`

## S6A-C1-m4-residual-regression — VERIFIED

- 声明：C16 能捕获评审给出的 3 条真实 M4 残留行（基线 PASS + 逐条注入 FAIL）
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B verification/m4_residual_regression.py --project-root D:\codex-worktrees\w6 --run-dir report/evidence/S6-A/s6a_g0_20261023_r10 --out D:\codex-worktrees\w6\tmp\6\claim_runs\s6a_g0_20261023_r10\m4_residual_regression.json`
- 真实退出码：0（期望 0）
- 可观察输出：['{"verdict": "ALL_AS_EXPECTED", "results": [["baseline", "PASS", "AS_EXPECTED"], ["R1-limitations-not-run", "FAIL", "AS_EXPECTED"], ["R2-coverage-item4", "FAIL", "AS_EXPECTED"], ["R3-state-line", "FAIL", "AS_EXPECTED"]]}']

## S6A-C2-hash-convention-both-directions — VERIFIED

- 声明：O1 换行口径接受器覆盖两个方向（CRLF→LF 与 LF→CRLF），内容不同必须拒绝
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B verification/hash_convention_check.py`
- 真实退出码：0（期望 0）
- 可观察输出：['{"verdict": "ALL_AS_EXPECTED", "cases": [["case_declared_lf_file_lf", "ACCEPT", "AS_EXPECTED"], ["case_declared_crlf_file_crlf", "ACCEPT", "AS_EXPECTED"], ["case_declared_lf_file_crlf", "ACCEPT", "AS_EXPECTED"], ["case_declared_crlf_file_lf", "ACCEPT", "AS_EXPECTED"], ["case_negative_content_differs", "REJECT", "AS_EXPECTED"]]}']

## S6A-C3-m4-two-representations — VERIFIED

- 声明：transitions[M4].reachability 与 reachability.transitions.M4.status 两个表示一致（NB-r03-10）
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -c "import json;d=json.load(open('docs/stage6/s6a_stage6_g0_behavior_v1.json',encoding='utf-8'));tr={e['id']:e for e in d['transitions']};r=d['reachability']['transitions'];bad=[k for k,v in tr.items() if 'reachability' in v and k in r and (('UNREACHABLE' in str(v['reachability']).upper()) != ('UNREACHABLE' in str(r[k]['status']).upper()))];print('conflicts=',bad);assert not bad,bad"`
- 真实退出码：0（期望 0）
- 可观察输出：['conflicts= []']

## S6A-C5-tool-self-tests — VERIFIED

- 声明：四个验证工具的自测两例全部符合预期（**引用套件产物**，不重跑）：守门 不改→静默/改→中止 exit1；export_selfproof 有效提交→0/不可解析→非0；claim_verify 正常→0/假声明→非0；m4_residual_regression 3 条真实残留被捕获→0/目录不存在→拒绝非0
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -c "import hashlib,json,pathlib,sys;p=pathlib.Path('tmp/6/tool_self_tests.json');assert p.is_file(),'缺少自测套件产物';d=json.loads(p.read_text(encoding='utf-8'));bad=[c['case_id'] for c in d['cases'] if c['verdict']!='AS_EXPECTED'];print('sha256=',hashlib.sha256(p.read_bytes()).hexdigest(),'verdict=',d['verdict'],'cases=',len(d['cases']));assert d['verdict']=='ALL_AS_EXPECTED' and not bad,bad"`
- 真实退出码：0（期望 0）
- 可观察输出：['sha256= 79c6b7165807223353422dded99aa3211b63c52cc44af21795bfc6859dc9e282 verdict= ALL_AS_EXPECTED cases= 10']

## S6A-C6-fresh-selfcheck-after-build — VERIFIED

- 声明：构建结束后**新鲜自检两次**（间隔 30s）均 ALL_PASS 且 C11 不再报任何被声明文件哈希不符（证明「清单写在被绑定文件之后」的结构问题已修、且构建后无残留写入者）
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B verification/s6a_fresh_selfcheck_twice.py --project-root D:\codex-worktrees\w6 --run-dir report/evidence/S6-A/s6a_g0_20261023_r10 --gap-seconds 30`
- 真实退出码：0（期望 0）
- 可观察输出：['{"verdict": "BOTH_ALL_PASS", "first": [0, "PASS"], "second": [0, "PASS"]}']

## S6A-C4-selfcheck-all-pass — VERIFIED

- 声明：S6-A 自检 17 项 ALL_PASS（含 C16 语义扫描与两表示法交叉断言）
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B verification/s6_g0_selfcheck.py --json docs/stage6/s6a_stage6_g0_behavior_v1.json --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases report/evidence/S6-A/s6a_g0_20261023_r10/hand_computed_cases.json --upstream report/evidence/S6-A/s6a_g0_20261023_r10/upstream_bindings.json --out D:\codex-worktrees\w6\tmp\6\claim_runs\s6a_g0_20261023_r10\selfcheck_replay.json --project-root D:\codex-worktrees\w6 --evidence-dir D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261023_r10 --state .codex/STATE.md`
- 真实退出码：0（期望 0）
- 可观察输出：['{"status": "ALL_PASS", "errors": [], "checks": [{"id": "C1", "name": "JSON 身份与必填块", "status": "PASS", "detail": "identity ok"}, {"id": "C2", "name": "ID 唯一性与最小规模", "status": "PASS", "detail": "unique ok"}, {"id": "C3", "name": "文档↔JSON 标识集合双向一致", "status": "PASS", "detail": "10 不变量 / 14 迁移(含 from/to) / 24 参数(§14 行) / 20 事件 / 7 状态 / 28 行为行 / 2 动作类型 双向一致"}, {"id": "C4", "name": "待批准纪律", "status": "PASS", "detail": "24 项参数与指标 PENDING_APPROVAL"}, {"id": "C5", "name": "五类动作映射一致", "status": "PASS", "detail": "5 类映射一致，target 唯一"}, {"id": "C6", "name": "硬不变量与唯一触发解释", "status": "PASS", "detail": "H-1..H-10 齐全，ONCE_PER_ACQUISITION 唯一"}, {"id": "C7", "name": "人工手算样例独立复算", "status": "PASS", "detail": "32 个样例全部由输入独立复算一致（HC-16/17/20 手算推导、HC-27 帧时刻序列推导、HC-28/29 逐帧 score/几何序列推导、HC-30 锁存 STABLE + 门在 TIMEOUT 帧开启的角落序列、HC-31 30fps 取较晚完成帧、HC-32 完成帧超出所给序列（序列不足以判定，F7））"}, {"id": "C8", "name": "上游只读文件哈希复算", "status": "PASS", "detail": "11 个上游绑定哈希一致（外部树按提交版本复算）；工作副本漂移（非失败，已在上游绑定中记录）：s4a_stage4_g0_fields(657ea2fb), s4a_stage4_g0_doc(75278f8d)"}, {"id": "C9", "name": "文档必备覆盖与章节", "status": "PASS", "detail": "关键词与章节齐全"}, {"id": "C10", "name": "禁止声明扫描（窄口径）", "status": "PASS", "detail": "未发现禁止声明"}, {"id": "C11", "name": "证据清单/STATE 声明 vs 实际文件", "status": "PASS", "detail": "实际文件 43 个；STATE 声明 37 个文件、3 个目录与 2 个含路径文件全部存在"}, {"id": "C12", "name": "谓词拆分一致性（B-05/R3-B01/R3-B02）", "status": "PASS", "detail": "谓词定义、引用、禁用标识符与全量双向绑定一致"}, {"id": "C13", "name": "冷却全局门一致性（B-03/H-10）", "status": "PASS", "detail": "全局门字段与引用一致"}, {"id": "C14", "name": "W_min/窗口完成口径（B-04/N-05/F1）", "status": "PASS", "detail": "W_min 仅下界；窗口完成按 T6-S03 取较晚，B07/B27/§9 与 JSON 文本一致"}, {"id": "C15", "name": "H-4/NO_HAND 一致性（B-02）", "status": "PASS", "detail": "NO_HAND 不推进匹配计数、零框不得完成窗口"}, {"id": "C16", "name": "迁移可达性与覆盖声明（N-02/N-03/BLK-r07-1/BLK-r08-1）", "status": "PASS", "detail": "M4 可达并计入覆盖（M7 构造上不参与覆盖）；11 个交付文件经语义扫描一致"}, {"id": "C17", "name": "STABLE 锁存语义一致性（观察项）", "status": "PASS", "detail": "STABLE 锁存（WITHIN_ACQUISITION）：退出路径 [\'M10\', \'M2\', \'M5\']，无 STABLE→CANDIDATE 迁移，U6-16 待确认"}]}']

## self_test_false_claim — VERIFIED

- 声明：故意为假的声明（assert 1==2）必须得到非 0 退出码——证明本工具会 FAIL
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -c "assert 1==2"`
- 真实退出码：1（期望 非 0）
- 可观察输出：['AssertionError']

本附录只证明这些声明在**本次真实执行**下成立；不代表独立审查或验收通过。
