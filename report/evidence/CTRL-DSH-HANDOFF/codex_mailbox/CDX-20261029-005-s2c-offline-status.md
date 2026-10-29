# CDX-20261029-005：S2C 一日时限离线进度回执

- 时间：2026-10-29（UTC+8）
- 工作树：`D:\FPGA_Competition\w2c`
- 分支：`codex/stage2c-throughput`
- 当前 HEAD：`c03cc9bf53553fa8b823be5759114fea511af7c7`
- 冻结 2B：`07c3d3958578b9cc9d3b8eae3758711fe08724c2`，未修改。

## 已做

1. L0 对齐吞吐模型与候选路线已在 `docs/obsidian-project/02-方案设计/s2c_throughput_feasibility_20261029.md`，提交 `fa8e045e86f0146ee9c73bea433fe1224033c89d`、`1e138b2394d7316594ec5bccabafd189376ece3c`；模型可复算，但未取得真实候选整帧 cycles，故预测误差 ±20% 门槛尚未证明。
2. 16×16 冻结 tile 几何原型已提交 `c03cc9bf53553fa8b823be5759114fea511af7c7`。静态几何检查 66 个可达键、21 层 full tile、最大 patch 124416 B，退出码 0；`xvlog`/`xelab` 退出码 0。有效证据 RunId `S2C-RTL01/tile16_20261029_02`，6 个哈希项，strict hash-basis 检查退出码 0、0 mismatch。原失败 RunId `tile16_20261029_01` 保留于本地，旧 manifest 含日志项，**不作为有效交付清单**。
3. XSim 底层引擎启动失败 `-1073741502`（`0xC0000142`）；包装脚本返回 0 不能视为仿真通过，测试断言没有执行。未运行整网仿真或 100 MHz 综合。无逐位功能等价、真实 cycles、时序和新位流。

## 门控与对接

自评达到 ≥2 fps 的把握不足 80%，三项离线门控均未齐备，**不提出上板验证请求**。请仅按既有 `CDX-20261029-003` 提供已有时钟身份与 RunId 证据；不要求 DSH 新占板、不改变 4-D 任务。GitHub/论文检索结论见 `CDX-20261029-004-github-yolov4-scan.md`。
