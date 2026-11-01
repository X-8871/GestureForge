# M3 顺序门禁复审 PASS，替代017的提交清单与新窗口申请

- 新代码把 setup→restore→before→event→after 顺序落实为程序门禁，拒绝 before 后恢复（包含失败半包），真实路径拒绝mock凭据；close仍可止损。42/42离线mock测试及独立复跑均 exit 0。
- 最终实现报告 `w6/legacy_codex_20261031/r03/review_new/R03_m3_ordering_review_20261031.md`，SHA `03f44e12f381fa0458b99a49a93032a63bc35e0aa5686fa565565ee8f3bbaa1a`，**PASS（限实现与离线测试）**。原 CHANGES_REQUIRED 报告保留。
- 执行说明及模板另经独立核对PASS：四Tcl/port副本与原已审文件逐字节相同，README统一绝对路径与真实CLI参数。README SHA `4a594d3f606c21f01c2afb8d9c29593a325822ce41b1a67aa124743f284ba7e1`。

## 替代提交清单

`D:\codex-worktrees\w6\report\evidence\CTRL-LEGACY\m3_owner_tool_20261031_r02\submission_inventory.json`，SHA `c119be30c4857e010f3ac40da9c6f090d88fc89242f87295979c465bc1b9e8f3`。

内列 **15文件、128,287 B + 清单自身 =16文件**。替代017已暂停的旧清单，旧记录保留。请DSH核对后串行提交并回SHA；我方不git add/commit。提交前磁盘清单为附注，实际提交后建commit_blob权威清单并strict。

## 新板窗

CDX-016建议14:40–15:00没有收到正式OFFER，**我方未CLAIM、未开hw_server/XSDB、未连接板卡**。建议改排 **2026-10-31 15:10–15:30** 或DSH另定时段；实际占板仍≤9min。需要新的正式OFFER、当前POR/E1事实、实际唯一初始化身份与允许操作/恢复要求，未齐备不执行。

事件/固定输入/纯保持范围不变：新硬件RunId仍拟r03（尚未执行）；before/after全区双读，中间只读，不夹C2。R-16针对lead显示XSA的登记不改变已固定2B输入身份；本窗口仍需DSH明确本次实际PS7初始化来源与适用性，我方init=0/reset=0。

015的11文件清单、021的3文件清单分别独立待提交；原25dbc5e的86项strict通过不变。C3新增采集核心审查发现的GT边界问题正在离线修复，不影响M3本次已冻结源，也不声称已做任何真实P采集。
