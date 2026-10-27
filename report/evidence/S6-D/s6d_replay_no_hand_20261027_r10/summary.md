# S6-D R08 临时依赖恢复补充包

- 类型：证据路径恢复补充；不是新回放执行，也不是独立技术审查。
- 来源运行：`s6d_replay_no_hand_20261027_r08`；原始清单 SHA 已在 `recovery_manifest.json` 绑定。
- R08 原结论：**BLOCKED**；阶段6核心：**NOT_RUN**。
- R08 预检子进程实际退出码：`2`；sidecar 原文 `2`。BLOCKED 检查字段仍为 `exit_code=null`。
- tmp 引用：9 个；按 R08 两清单声明 SHA 复制到 `recovery_inputs/`，源/目标 SHA 和 bytes 一致。
- R05、R06、R07 历史失败按轮次及文件逐项重述，见 `recovery_manifest.json` 和 R10 `inputs_manifest.json`；R08 原清单不改写。
- R10 本地自检只读验证 R08 清单哈希、映射与 R10 保存字节；原 R08 checker 仍需按映射恢复 tmp 路径后重跑。
- 恢复提示：只在目标缺失时按映射复制；目标已存在且哈希不同则停止，不覆盖。未执行 restore，也未重跑原 R08 checker。
- 阳性与 NO_HAND 输入资格结论保持 BLOCKED；没有调用核心、没有板上或 G3/G4/G5 结论。
