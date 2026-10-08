# S2B-T06 PS前置检查软件离线候选冻结

日期：2026-10-09（UTC+8）。候选版本：`s2b-ps-smoke/1.0.0`。

## 批准范围

总控依据阶段2B已有授权及独立G2-r01 PASS，批准固定PS-only CPU0 UART/DDR检查软件、同XSA的最小OCM初始化ELF和对应人工操作说明作为离线前置检查候选。开发方与Reviewer均已停写；固定源码、候选和真实审查证据见下表及绑定清单。

本批准仅接受已完成的G1/G2离线结果。板卡初始化、UART和DDR执行为`NOT_RUN`，G3/G4和阶段2B G5尚未通过；模型部署、整网检测头/框比对、1000次连续任务及布局后时序均未执行。后续依赖实板前置检查的任务须取得真实结果。PS/PL恢复语义候选仍待Wong选择，本批准不冻结该接口或物理模型地址。

## 固定输入及源码

- 被审仓库基线：`00f51b664fefdaf0c63e605af2427333579fa5f3`。本轮新源码通过下列实际文件SHA绑定，不能把它们称为已包含在旧基线提交中；总控提交后以对应Git版本恢复。
- 唯一上游输入提交：`90652b45ef31e763bd3e6f7527e2fd080ece61a8`。接口为`stage2b_ps_platform_offline_freeze_20261009.md`的`s2b-ps-platform/1.0.1`，SHA `89512d94859abf083e958a2e53139d8f4ab0c0a61989c76eb8794eba9c9db6c1`。
- XSA：`report/evidence/S2B-T04/ps_platform_20261008_r02/candidate_attempt1/s2b_ps_only.xsa`，SHA `a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58`；不改用旧r01或独立重建XSA。
- 离线器件目标使用Wong最新转述的厂商确认`xc7z020clg400-2`。XA照片、实际PCB版本、接线、电平、时钟和DDR候选校准等实物核对项保留在操作说明中。

| 固定源码 | SHA-256 |
|---|---|
| `vitis/s2b_ps_smoke.c` | `d2bb6f0941c2e3765c5a71f889d2e7e1e0428429237f5443510e81cedd16786b` |
| `vitis/build_s2b_ps_smoke.py` | `addff3a419609ac8203c8838edfd6fd56fb53baccf40efc403fca4eb36b50d76` |
| `verification/check_s2b_ps_smoke_layout.py` | `6c12023cc9660d392a0f3e393df2ebaf425af8a4cbb51886a35749d0c6fa0f77` |
| `vitis/s2b_ps_smoke.md` | `c15290c48ccbc03c55418c2efa0ca2df815eacdeffb60e53363eca4fba490db5` |

## 交付候选及操作入口

操作入口为仓库`vitis/s2b_ps_smoke.md`，包含精确绝对路径、文件SHA、冷JTAG独占前提、2026.1 PythonXSDB命令、断点/状态联合判据、原始UART记录、异常停止与恢复步骤。首次实物操作须有相应明确授权；本轮未连接或操作板卡。

当前人工路线只使用`report/evidence/S2B-T06/ps_smoke_20261008_r01/build_08/`中的两份固定ELF；Reviewer的重建ELF仅是独立验证证据。

| 固定产物 | SHA-256 |
|---|---|
| `s2b_ps_smoke.elf` | `8b9803682c9585a8dad91daf96f3f102de948466025e0cf28ee4b96e6cfde428` |
| `s2b_ps_smoke.map` | `7273e22fd811804eafe538b173c42bbf50b3311e6c489c69f23add95cf28b218` |
| `s2b_ps_init.elf` | `366ad1f4831eba9db0510c0e5343d34e3b355f72c8f8bcae419903814246024c` |
| `s2b_ps_init.map` | `aebac0c4c66014d859f38b34f409afee4039dc6ec516d25f4cf74d509df35efa` |

初始化ELF只在低OCM `[0,0x30000)` 和高OCM `[0xFFFF0000,0xFFFFFE00)` 分配，顶部512字节留给CPU1。使用同XSA原`ps7_init.c/h`及官方OCM linker；实际启动代码和构造函数已核查，最终初始化构造函数只有`frame_dummy`。成功必须同时满足ready停点、原返回码0、结果2及CPU1条件，再直接下载smoke，保持PS/DDR状态。

smoke专属区间为`[0x01100000,0x01200000)`，1MiB、64字节对齐、NOLOAD/NOBITS；与实际ELF全部ALLOC/LOAD、向量、栈、heap及清零区互不重叠。这是本候选的分配归属证据，实板独占及物理正确性须实际确认。两轮均启用DCache，每轮8模式，每模式写入后执行屏障、写回、屏障、失效、屏障再读回；总计4,194,304个word。成功须完整16行PATTERN_PASS、BUILD/BEGIN/PASS/END、零不匹配、最终状态2及正确返回停点同时成立。

## 独立验证及证据

- Developer全新build_08：43.5643445秒，Vitis CLI和有效结果均0，平台与两个应用API均为整数SUCCESS0，27次API和6个子命令，联合布局及14项反例通过。
- Reviewer在隔离本地clone中运行同一原builder，真实重建48.032秒，native/effective均0，三个build API均整数0；两个ELF的布局及16个关键函数机器码独立核查通过。
- 36项独立核查、9个真实CLI符合预期；原14反例复验通过，另三例修改真实ELF后重新绑定SHA，缓冲区可执行、LOAD落入保留区、构造函数指向DDR均被语义拒绝。包含独立手算、真实非零命令日志保全、源码/编译头/config绑定及本机SDK操作语义核对。
- Developer清单284项实际字节SHA全一致。独立最小审查清单110项及清单自身已逐字节复制，共111文件/4,339,999字节；原路径通过`reviewer_copy_mapping.json`保留。
- 原build_01至07、旧FSBL/标识符诊断和审查工具自身三次失败均保留。未补造缺失traceback；NUL与LF两种Git状态口径分开记录。审查任务卡“两轮cache on/off”转写错误已按真实源码及正式要求纠正，不变更验收标准。
- 两次构建均记录自有server结束，实物均`NOT_RUN`。全进程树峰值内存和跨全部工具的调用总数未测；上述API/子命令计数仅覆盖各次builder。

| 主要证据 | SHA-256 |
|---|---|
| Developer `ps_smoke_20261008_r01/inputs_manifest_r03.json` | `9b35050163c2cc47306e2b5f5fc4ed0e5d9835afa1fd158ff68a3959ef123778` |
| Developer `ps_smoke_20261008_r01/delivery_manifest.json` | `e9249d71554eed3913244961b2a5c884db88d79fd9a863d2906b8e18d6a3fa26` |
| 正式审查收据 `ps_smoke_offline_freeze_20261009_r01/reviewer_r01/review/f04/semantic_review_receipt.json` | `a591c05a89e75bb96acf2be9a0b9b2fb56e9b237f174debd045ef092f4e2173b` |
| 审查原件绑定 `ps_smoke_offline_freeze_20261009_r01/reviewer_r01/review/f04/review_evidence_bindings.json` | `6bf5e032f670f563d2fa532aa5e66ebf7ecfbf0c83516043ece975c342e79c48` |
| 审查复制映射 `ps_smoke_offline_freeze_20261009_r01/reviewer_copy_mapping.json` | `63d175cbbe671ff857b1a4f2c84460fe9890afee84b28b1c49339793b3863c42` |

以上证据路径均以`report/evidence/S2B-T06/`为父目录。总控批准和最终绑定清单位于同一offline_freeze Run的`acceptance.json`与`delivery_manifest.json`。包装CHECKS_OK只表示文件绑定有效；各项结果与适用关口仍按本记录区分。后续人工结果另建全新Run并记录实际源码/ELF/XSA、板卡和原始输入输出，不写回本离线Run。
