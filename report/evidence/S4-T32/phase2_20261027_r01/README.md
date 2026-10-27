# S4-T32 Phase 2 基线构建 · 执行记录（2026-10-27）

- 开跑 2026-10-27T21:28:59+08:00，Vivado 2026.1，器件 xc7z020clg400-2，RTL 47 文件 + 冻结 BD（44,127 B）。
- **BD 打开、校验、wrapper 生成均成功**（BD_VALIDATE: OK）。
- **综合无法启动**：ERROR: [Common 17-345] A valid license was not found for feature 'Synthesis' and/or device 'xc7z020'；
  WARNING: [Common 17-348] ... A license feature for Synthesis was found but is expired；
  INFO: [Common 17-3922] A valid Vivado Design Suite ENTERPRISE license has been detected ... will expire on 06-oct-2026。
- 结论：**BLOCKED_ENVIRONMENT_LICENSE**（环境阻断，非设计失败）。未产出 bit/XSA/ELF。
- **未做任何绕过授权的尝试**；需由 DSH/Wong 提供有效 license 或改用已授权机器后重跑同一构建脚本。
- 本次未接触板卡；ENABLE=0；未 FROZEN；未 push；25 项遗留未动。
