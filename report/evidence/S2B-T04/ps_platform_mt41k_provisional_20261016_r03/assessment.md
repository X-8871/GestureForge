# S2B-T04 R03 PS7 DDR 暂定配置审计

## 结论与范围

R03 将用户授权的暂定料号 `MT41K256M16TW-107` 写入 PS7 配置脚本，并在字段表中绑定手册输入、器件族几何来源及 R02 读回。状态为 **PROVISIONAL_OFFLINE_CANDIDATE**。本轮没有启动 Vivado，也没有在当前源码上重新生成 PS7 BD、XSA 或 bitstream；配置的时序适配仍 **BLOCKED**，实物验证为 **NOT_RUN**。

## 源码基线和哈希

- 工作树基线 HEAD：`aeaea942dfba1add885a926a6056b55ee1840df9`。
- `vivado/s2b_ps_platform.tcl` SHA-256：`2be7961f03a69f624c8c4da0bbfabe9a3a54c743a656909eb3117f4724c06556`。
- `board/ps_platform_fields.json` SHA-256：`182bfa003bd3d2d9a997a09ccae9b35e97c67375eb39712724f9d3d2dfb9bfdf`。
- `board/ps_platform.md` SHA-256：`e2c015e0ee3760d6c172439e76396f44230a5d7e1ba9d0e54c408dda7e3cb27a`。
- R02 输入 `report/evidence/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/candidate_readback.tcldict` SHA-256：`5FE5A32103B6BEED8EF984665D0270DA3F19E060B0389BB46B4B728AEFF00CB0`。
- `validate_candidate.py` SHA-256：`7d04db0b20092f031eb101e2a60c940108ab73bee916ab045d632ff7862e0605`。

## 变化

- PS7 `CONFIG.PCW_UIPARAM_DDR_PARTNO` 字面量改为 `MT41K256M16TW-107`。
- 保留 2×16-bit、32-bit 总线、单颗 4-Gbit、合计 1-GB、行 15/列 10/8 banks（Bank 地址 3-bit）和 533.333333-MHz 请求值。手册提供器件布置、总容量和频率输入；R02 对 PS7 MT41K 候选的离线读回用于映射交叉核对。R03 未产生新的 Vivado readback。
- 明确 DDR3L 是 DRAM 技术族，PS7 `CONFIG.PCW_UIPARAM_DDR_MEMORY_TYPE` 使用 IP 枚举 `DDR 3`。
- 从 Tcl 请求中移除旧的 0.25-ns board-delay 和 0-ns DQS-to-clock 候选。R03 不设置 CL/CWL、tAA/tRCD/tRP、板级延时或 DDR 电源字段。
- `validate_candidate.py` 逐项解析并比较 JSON 候选和 Tcl 的 DDR 枚举、总线/颗粒宽度、单颗容量、行列/Bank 几何与请求频率；同时要求请求中的 DDR 属性集合仅含许可字段，从而拒绝 CL/CWL、其他 DDR 时序、速度档、板级及封装延时属性。
- JSON 保持 schema version 1，新增可选 `active_ddr_candidate` 与 `historical_field_scope`；原 `fields`、`review_state` 和 `candidate_artifacts` 明确保留为 2026-10-08 R2 历史。仓库内未发现解析字段表业务字段的代码消费者。`verification/check_s2b_inference_platform.py` 通过静态检查，但这不代表该检查审阅 DDR 时序或实板行为。

## 输入来源和适用范围

- 只读手册 `D:/FPGA/AX7Z020/AX7Z020/AX7Z020开发板用户手册.pdf`，SHA-256 `7d9e34045501637bc6277f7ad372f168165fc6969c640092909f1317b10ccedf`：第 8、12、13 页。第 12 页作为暂定板级输入；它不证明当前实物或 PCB 版次。
- Micron [MT41K256M16TW 产品目录](https://www.micron.com/products/memory/dram-components/ddr3-sdram/part-catalog/part-detail/mt41k256m16tw)，访问日期 2026-10-16：器件族组织 `32 Meg x 16 x 8 banks`。扩展后缀 [MT41K256M16TW-107-M-P 页面](https://www.micron.com/products/memory/dram-components/ddr3-sdram/part-catalog/part-detail/mt41k256m16tw-107-m-p)的规格不外推至裸料号。
- AMD [UG585 DDR Controller](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/DDR-Controller) 与 [UG933 Zynq PCB Design Guide](https://docs.amd.com/api/khub/documents/emfVNNoDnc5paYCtwGzwPg/content)，访问日期 2026-10-16：分别作 PS 支持 DDR3/DDR3L 及通用 DDR VCCO/PCB 设计参考，不是板卡供电或实物适配证明。
- 旧配置来源：旧字段表和说明引用 AX7020 V2.2 资料中的 Hynix `H5TQ4G63AFR-PBC`，并使用 PS7 profile `MT41J256M16 RE-125`。这组值留在历史记录，不作为 R03 活动输入；R03 依据用户指定的 AX7Z020 开发板手册暂用 `MT41K256M16TW-107`。

## 未解决项

- 未取得适用于裸料号 `MT41K256M16TW-107`、533.333333 MHz 的可核验 Micron timing table；时序兼容性 **BLOCKED**。R02 Vivado 的 CL/CWL 与 timing 属性只是旧候选读回，不构成此项通过。
- 当前实板实装 DDR 料号、PCB 版次、VDD/VDDQ/VTT 及走线延时未确认或测量。原理图的一般标注、手册照片及器件族资料均不能替代实物证据。
- 未对 R03 修改后的 Tcl 运行 Vivado；没有 XSA、bitstream、PS 初始化、DDR 训练或板上执行。
- 既有可见性证明与Reviewer收据仍绑定此前源码哈希；本任务没有改写这些证据。后续若以R03源码继续使用该证明，必须按当前源码哈希重新绑定并独立复审。
- 证据清单检查仅核对目录、源码与文件哈希，不代表独立审查、G0/G3/G4/G5 或阶段验收。

## 离线检查

- `validate_candidate.py` 逐项 JSON/Tcl DDR 配置绑定断言：通过，退出码 0；核对 DDR3L/PS7 `DDR 3`、总线宽度、单颗宽度/容量、行列/Bank 几何和频率，并检查请求属性白名单排除全部其他 DDR 时序、speed-bin、板级及封装延时字段。
- `verification/check_s2b_inference_platform.py` 静态检查：通过，退出码 0；输出 `PLATFORM_STATIC:OK visibility=0 rtl_sources=18`。该检查不运行 Vivado或板卡。
- `git diff --check`：通过，退出码 0。
- `verification/check_stage_delivery.py --mode evidence`：通过，退出码 0，输出 `CHECKS_OK`；仅核验清单和哈希。
- Python：`3.12.14`。
- 没有专用 PS7 DDR Python 单元测试；未运行综合、实现或硬件验证。
