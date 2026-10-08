# 阶段2B PS-only 离线软件输入冻结

日期：2026-10-09（UTC+8）。版本：`s2b-ps-platform/1.0.1`。任务：S2B-T04。

## 批准范围

总控接受独立 R2 的离线 G2 PASS，批准下面的固定 PS-only、无位流 XSA 供 S2B-T06 的 Vitis 2026.1 standalone CPU0 UART/DDR 前置检查软件及必要官方 PS 初始化产物离线构建使用。冻结的是可恢复的软件输入候选；实际板卡适用性、DDR 校准、可用内存窗口、模型部署及 PS/PL 总线接口仍未冻结。

Wong 于2026-10-08明确答复「厂商已明确确认实板是XC7Z020-2」，离线目标为 `xc7z020clg400-2`；目标决策提交 `4b6fcfcfb41d9647d043dd62ad5329d60799a19e`。照片直接显示 XA7Z020/CLG400，差异保留在部署前核对项中。

## 固定输入

源码起始提交：`5b9122e425c1499b36b09e80cffda7bf50ca2ef0`。实际待提交源码以以下 SHA-256 绑定；下游同时记录包含本冻结记录和这些文件的实际 Git 提交，不使用模糊的“最新平台”。

| 仓库内精确路径 | SHA-256 |
|---|---|
| `vivado/s2b_ps_platform.tcl` | `b70871097f2e434f54b35ef4a13efe070d64b08254707e9d66d0dbf32e23cea9` |
| `board/ps_platform_fields.json` | `acc6307c709c55ae09d9b8223bfeac96d3163a5a2d7f37dbd29c5abfa399446b` |
| `board/ps_platform.md` | `42b9aba545527ad4dc50570db1b88625409c7b08b4f0569570133b6672e7344e` |
| `report/evidence/S2B-T04/ps_platform_20261008_r02/candidate_attempt1/s2b_ps_only.xsa` | `a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58` |
| `report/evidence/S2B-T04/ps_platform_20261008_r02/delivery_manifest.json` | `209aba77165fb0f9161620b422f11fff199be5935556b2c291a1476a52f6b80d` |
| `report/evidence/S2B-T04/ps_platform_20261008_r02/inputs_manifest.json` | `1d07366c515c26b62582dff0a64ef8f497956a3bc938777857909e3026447e18` |

参数及资料依据沿用既有字段表和平台说明，不另定义模型或总线语义。候选只有一个 PS7、DDR/FIXED_IO 外部接口；GP/HP/ACP、PL FCLK 和复位端口关闭。UART1 MIO48/49、BANK501 1.8V；DDR 候选32位、1GB、CL7/CWL6。旧例程的各 lane 0.25ns 是候选值，当前封装延时由 Vivado2026.1 派生。

## 验证与恢复依据

Developer 全新会话完整重建退出0，24.707秒。独立 Reviewer 另建全新 Vivado2026.1 Tcl/IPI、proxy 会话，完整重建退出0，23.482秒；helper 首次全局加载从0到1、无嵌套命名空间，关闭 R1 的首次加载作用域 P1。

独立核对通过178项交付绑定、15项输入绑定、73字段及50请求、10项拒绝覆盖检查、BD/HWH/wrapper 和三份初始化文件。独立 XSA 的容器时间戳可不同；实际 BD 及三份初始化文件逐字节一致，HWH 除根时间戳外一致。原始 products capture FAIL 和唯一严格复验 OK 均保留；Developer 末尾工具查询仍为 UNKNOWN/BLOCKED，其防覆盖功能由本次独立真实实验验证。

长期证据入口：`report/evidence/S2B-T04/ps_platform_freeze_20261009_r01/`。其中 `reviewer/review_evidence_bindings.json` 原字节 SHA 为 `b4290cff78f423e6395203dec267e11c981df77ebc930bb6ff91d9aaa8309d00`；53项必要实验证据按 `copy_mapping.json` 从临时路径精确映射恢复。R1 的100个文件和旧源码快照仍保留，旧清单通过 R2 的 `source_prior_mapping.json` 重放，不把 r01 作为当前冻结输入。平台说明中的“待独立审查”描述保留该次 Developer 交付时点，本记录补充其后通过与批准事实。

## 验收边界

本批准不授权上电、下载、烧录或运行板卡，也不表示阶段2B G0/G3/G4/G5通过。实物核对包括实际 PCB、芯片标识、DDR 颗粒/延时及 UART 接线；下游在独占 CPU0、CPU1停驻、DMA和其他 DDR writer静止的条件下，另行核验专属缓冲区、初始化路径和缓存维护。S2B-T05 的物理异常排空恢复候选仍等待 Wong 选择，原2A契约不改。
