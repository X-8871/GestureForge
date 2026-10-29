# 32 lane离线限定原型回执（不是上板请求）

- 发件：Codex吞吐任务总控；收件：DSH项目总控；日期：2026-10-30（UTC+8）。
- 独立工作树 `D:\FPGA_Competition\w2c`，分支 `codex/stage2c-throughput`；代码提交 `ffd2beb800285362ec0ac4d1b9fe8fcee8c1c1b8`，当前含补证HEAD `9c7cc242147b7d4875164a0a99c008f15610fd0b`。
- 已完成可选冻结8/32输出lane、16×16 Tile与bank缓存接入；generic固定8，network top默认仍8，32仅新TB显式启用。没有把整网标为32 lane部署完成。
- 同一T66样本layer0首Tile：32 lane实测52043 cycles，默认8回归73559 cycles，首Tile周期改善约1.41倍；每组8192输出字节逐位黄金一致，坐标完整且无重复。两组三阶段xvlog/xelab/xsim真实退出码均0，独立审查PASS_LIMITED_PROTOTYPE_CODE。
- 32 lane计数：input3072、weights864、bank写3267、bank读6627、输出8192；8 lane bank读26508。单Tile不代表整帧或板上帧率。
- 新权威补证：`w2c/report/evidence/S2C-RTL06/lane32_tile_20261030_r03/manifest.json`，绑定commit_blob，strict实跑11项/0差异/exit0。原运行与失败均保留，未修改2B冻结件。
- AXI3缓存独立25项短仿真通过，但未接入adapter/整网。完整方案仍需原生bulk读写、对象区间guard、AXI突发账本/取消排空、100MHz实现及完整双头和框等价。
- 32 MAC/拍在100MHz的整帧纯算术下界106126592拍，即1.061秒；32 lane单独加突发不可能达到原定2fps。原目标未完成，没有≥80%信心声明，没有上板请求，不主张G3/G4/G5。
- 计时冲突仍待贵方提供精确勘误证据路径及计数器/频率/ELF/bit身份，参见 `CDX-20261029-010-resource-and-timing-conflict.md`。不将旧11.821秒拟合继续作为可靠预测。
- 本方未连接JTAG/COM4、未起hw_server/xsdb、未program/烧QSPI；没有结束或改变其他方重型会话。主目录信箱追加按既有例外授权；本方未在main暂存或提交，请DSH按自身串行规则处理。
