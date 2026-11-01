# C2 real-chainB r04 独立复审

审查时间：2026-11-01 00:13（UTC+8）  
结论：PASS（仅源码、ELF 与离线 host 回归范围）  
边界：只读核验实现及构建证据；未操作硬件、JTAG、UART、socket 或 vendor 工具；未修改源码、ELF、其他工作树或 Git。唯一审查输出为本报告。host 测试临时可执行文件写入获准的 D:\FPGA_Competition\tmp\c2_r04_review_20261101_0012\。

## 固定版本

- w6 HEAD：f0fab846304aec4aa1baeeb012f9ce2888e86812；源码目录仍为未跟踪目录 legacy_codex_20261031/c2_board/。
- ELF：D:\codex-worktrees\w6\tmp\c2_real_chainb_20261101_r04\c2_real_chainb_display.elf；1,345,984 B；SHA-256 77BC9EE36CB6E9D0BA13F82043D7CBCF633A05C152ABC73F7E4CF62377F2292C，与任务卡及 build_record 一致。
- 指定源码哈希实算一致：s4d_ps_app.c B295C476B3417BEA15A23356E2EFA7C747F70312EA290F32C6EC185EDC00B42E；s5_real_source.c F341158F17D7EF88CCFE509ABF90C7140E968D81BE1628E86997683EE849E3C1；c2_integration_status.h F1724CDD493D24DBCE7C11A2AC42B01912FC00B6D18509B5ECF93A3E7382BAD2；test_c2_rev4_profile.c EA34C80E960875B25DCAF0D36D3614A5E389B98F34771A43CB2BC1A068A02825。
- build_r04.ps1 SHA-256 38727E2D313093544CDC0874C21A535ECAB3C267F30728ABA5AFFCB1BAB35A23；build_record_r04.json SHA-256 28CA4648BDABAB92473C04CE5C99F4FB1BB2C93650CFCDD6B38ED5B5D056F4D0。
- build_record 的输入哈希逐项声明 hash_basis=worktree_disk；记录绑定源码、fixture、BSP、库、linker script、测试和 ELF。该基座适用于当前磁盘快照，不能替代 commit_blob 绑定。

## 原 P1 已关闭

代码位置：src/s4d_ps_app.c:980-1019、1034-1044；src/c2_integration_status.h:9-18。

最终汇总现在要求 2B 检测链成功、publish_rc 精确等于 C2_PUBLISH_OK、稳定读回成功、显示调用返回 0、ACK 回 idle；任一项缺失都返回 pass=0。发布返回负值或正值拒绝时均保留失败状态；发布被拒绝会显式记录 display 未执行，初值 -1 会使汇总失败；显示调用错误会记录 rc 并使汇总失败；读回不稳定时 c2_readback_pass 保持 0 并使汇总失败。最终 CHAINB 记录了 publish_rc、readback、display_rc。

测试文件 src/test_c2_rev4_profile.c（tests/test_c2_rev4_profile.c）覆盖 15 框因 safe14 被拒且不截断 decoder 计数、非法检测项返回正值拒绝码、拒绝结果不得最终 PASS、显示失败/未运行不得 PASS，以及所有环节成功才 PASS。业务状态也覆盖 ERROR、TIMEOUT、NO_HAND、OK。原有三阶段 Rev4 flush 与旧四次 flush 断言保留。

## 构建和离线核验

- 持久构建记录：10 个编译单元 exit=0；fixture objcopy、link、size、nm 均 exit=0；缺失符号为空；host test 编译及运行均 exit=0；记录状态 host_and_build=PASS、board_deployment=NOT_RUN、hdmi_physical_scanout=NOT_VERIFIED。编译日志均为空，确认此次修复的 warning 已清零。size 输出：text 982,012、data 1,412、bss 3,941,952、合计 4,925,376 B（0x4b27c0）。
- 独立重跑现成 R04 host test 二进制：输出 PASS，exit=0。
- 独立按当前源码重编并运行同一 host 测试，输出目录 D:\FPGA_Competition\tmp\c2_r04_review_20261101_0012\；命令 gcc -std=c11 -Wall -Wextra -Werror -pedantic -I <c2_board/src> <src/c2_s5_publish.c> <tests/test_c2_rev4_profile.c> -lm -o <隔离目录>/test_c2_rev4_profile.exe；编译 exit=0，运行 exit=0，输出 PASS C2 rev4 profile, three-stage flush, receipt, and legacy API。临时可执行文件 SHA-256 26470E214D8F21EFAD1E9A4EF7E59F18D80E8D1528966DC8ADAF4A1F60F09D80。
- 只读命令核验源码哈希、rg 位置、build_record、nm/readelf/strings 均成功（exit=0）。ELF 符号含 main、C2Publisher_InitRev4Session、C2Publisher_PublishRev4、C2_DisplayOneFrame 及 fixture start/end；字符串确认 CHAINB_SELFCHECK=1、C2_REAL_FIXTURE_MODE=1、PREPROC_SRC=0。fixture 哈希与前轮相同，ELF 内跨度 921,600 B。

## 保留边界

- 此 PASS 仅关闭源码/构建审查中的原 P1，不代表板级 G3/G4 或 HDMI 实物通过。板上装载、运行期真实结果/sidecar CRC 读回、VDMA/VTC 及物理扫描仍 NOT_RUN/NOT_VERIFIED。
- P3q XSA 的 512 MiB 声明与 1 GiB BSP 及 DDR 地址布置的错配仍未修复；本轮只沿用已记录的部署组合限制，不称官方匹配平台，也不要求重综合。
