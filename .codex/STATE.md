# 项目状态入口

更新：2026-10-18（UTC+8）。按适用 AGENTS.md 恢复；运行状态以代码与原始证据为准。

## 目标、位置与授权

- 本窗口持续完成阶段2B：tiny416固定输入上板、至少100黄金样本（现有109）、1000连续任务、CSR异常恢复及G4/G5；未通过不得称冻结，不自动进入阶段3或推送。
- 实施树为 `D:\FPGA_Competition\w2b`，分支 `codex/stage2b-dma-g0`；本轮起始HEAD为 `2e9e3c625abe523e54be36a3010966b9f679c80e`，恢复时以实际Git HEAD为准。主目录只作全局入口，旧C盘工作树不再用作运行目录。
- 用户确认器件 `XC7Z020-2CLG400I`，Vivado part `xc7z020clg400-2`；不再因旧XA照片解读阻断。DDR按用户“以手册为准”采用第12页 `MT41K256M16TW-107`、双x16/32-bit/1GiB候选；实装D9PSK解码与PCB修订仍未知，不声称已验证。
- 用户已授权本阶段必要易失PL/PS下载、DDR装载和板上验收，不含QSPI非易失烧写。2026-10-18最新确认：用户不在板卡旁边，无法接板/上电；本轮没有硬件操作。旧POR/独占记录不得复用为当前现场事实。
- 用户确认DMA按搬运功能验收：保留自定义AXI3 master/adapter；字节长度、cache、ownership、错误、取消、完成和连续任务标准不变。
- 与DSH串行共享工作区：不修改其主目录XPR差异，不结束其他窗口会话，不操作对方沙箱权限，不全量暂存。主目录DSH交出及环境补正见主STATE和 `.codex/DSH_HANDOFF_20261018.md`。

## 已核实的技术结果

- 2A tiny416/8×8空间tile/8路输出通道/双头及PS解码NMS已冻结。109离线整网与D9比较均通过、最大误差0；不重复整网离线仿真，不当作2B板上结果。
- 外层CSR/恢复RTL完整矩阵R07及独立R08均通过：146 directed、128 random、25 integration、6362 cycles，两类四相位全1。CSR SHA `4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1`；入口 `report/evidence/S2B-T11/control_r18_xsim_first_axi_20261016_r07/`、`control_r18_independent_20261016_r08/`。G2不替代板上恢复。
- 当前候选平台为 `s2b-physical-candidate/0.1.2`、UART `s2bu-candidate/1.1`，尚未整体冻结。当前源码/地址/cache/HP0契约见现有正式候选文档，不复用旧32×32分类规格。
- T19 R04已完成XC/-2、50MHz实际路由，setup +0.156ns、hold +0.078ns、TNS/THS零；DRC 393项/0 errors。原始input_record保持FAIL（profile标记未采到stdout），Vivado Job原生0及22项产物哈希已核对；不为采集标记问题重跑综合。入口 `report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/`。
- R04 bit SHA `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`；XSA SHA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`，内嵌bit一致。
- T15已按同R04 XSA重建BSP/ELF：infer SHA `a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8`，init SHA `237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1`；入口 `report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/`。原R04旧ELF来源不匹配的记录保留，不混用。
- 旧R04独立资格收据实际存在且PASS，SHA `f6d94bb66ffb678d1334a7194246029d955e62df6075369ca17c422a266f30fe`；只覆盖sample000入口机制，硬件/sample结果NOT_RUN。入口 `report/evidence/S2B-T19/qualification_single_sample_review_20261017_r04/`。
- 最新历史资格运行R14为BLOCKED、hardware_attempted=false、hardware_execution=NOT_RUN，原因是直接调用Python未使用官方Vitis2026.1环境。原件 `report/evidence/S2B-T19/single_sample_qualification_20261017_r14/model_qualification_result.json` 保持不变。

## 本轮离线闭环

- 官方 `D:\Xilinx\2026.1\Vitis\bin\vitis.bat -s` 已真实验证Vitis v2026.1/Python3.13及绑定XSDB/pyserial3.5导入，最终r03启动器/脚本均退出0；没有创建SDK会话、启动server、打开串口或操作板卡。入口 `report/evidence/S2B-T19/qualification_runtime_offline_20261018_r03/`；r01沙箱失败和r02成功原件均保留。
- 新增离线检查器 `verification/check_s2b_qualification_runtime.py`，使用显式配置/结果环境变量、UTC+8和独占结果文件创建。官方启动器退出0不能单独替代脚本结果。
- 旧C盘人工根已随历史树迁到 `D:\codex-worktrees\96a3`。runner仅固定迁移后的读取位置，保留用户原始C路径引用、两个JSON原字节及批准SHA：`c87a2f40…321ce5`、`e22fd0a1…c3d4c7ea`；没有改写历史JSON或扩大信任范围。
- 34项候选源码/平台绑定核验通过，30项入口单测由总控与独立Reviewer分别运行退出0。新canonical digest为 `cf57921c78d33828f5c5da71d5ba7c6dba8f53a8f12d535b804d527dc560c6aa`；旧R04 canonical已被正确拒绝，不能自动继承旧收据。
- 本轮独审PASS仅限离线迁移、入口代码和runtime checker；入口 `report/evidence/S2B-T19/offline_runtime_migration_review_20261018_r01/review_outcome.json`。单测/导入/包装检查均不代表G3/G4/G5。
- 109/1000执行器与CSR恢复执行器已存在，无需因本轮迁盘修改其功能。可复用 `report/evidence/S2B-T18/model_assets_20261016_r02/prep/preparation.json` 的109项输入/黄金引用；全部仍NOT_RUN。

## 当前阻碍与下一步

- 目前无法取得板卡上电/接线条件。已一次请求当前上电时间、此前启动拨码与独占操作确认，用户答复不在旁边、接不了板卡；不重复询问、不使用10月17日旧POR/03:30到期保管链。
- 板卡可用后：核对JTAG/USB-UART身份和启动模式，按当前平台验证PS/UART/安全DDR/cache前置；用新POR、当前源码digest、专属server身份及独立审查更新sample000资格输入/回执；旧配置/收据不直接启动。
- sample000仅使用最大有限CORE/DRAIN `0xFFFFFFFF`（50MHz约85.899秒）进行首测，UART观察450秒；量化正式部署期限仍属G4/G5，不能把估算当实测。出现故障/超时/黄金不符立即停止依赖任务并保留证据。
- 首样本真实DONE_SAFE/HEAD_VALID及全部双头整数/PS框比对通过后，绑定当前平台、ELF、实测可见性和正式G0/冷生命周期回执，运行T18 model scope：109黄金样本后同输入1000连续任务；再以独立Run执行CSR忙启动、非法参数、ABORT/ACK、复位恢复。正式runner当前G0/COLD锚点None，须凭真实材料固定，不能仅置状态求通过。
- 正式109、1000、板上异常恢复、当前完整arena/HP0可见性与期限量化均未完成；2B G3/G4/G5未通过。最终还需冻结接口、绑定可恢复产物并完成适用干净重建/板上检查和独审。
- 核心综合总预算10次，已启动6次、剩余4次，迁盘不重置。16GiB机器单重型；启动前检查真实进程/内存/空间；新构建缓存和工程放D盘tmp隔离目录，失败证据不覆盖。
- 2026-10-18本窗口只读主机快照无Vivado/xsim/Vitis/hw_server/XSDB进程，可用内存约5.77GiB；TEMP/TMP实际均为 `D:\tmp`。许可未继承DSH配置，今后启动本方Vivado前单独核实；不得使用其降级DRC的counter探针bit上板。
