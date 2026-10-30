# C2：2B 解码结果发布适配

## 交付范围与审批

- 本目录是 `R-05/C2` 的隔离实现；不改阶段5/6冻结源、主目录、2B 源码或其他工作树，不执行 Git 暂存/提交、不推送、不启用 `ENABLE`，不启动硬件工具。
- Wong 于 **2026-10-31 00:50:59（UTC+8）**明确批准：“14框安全上限”：保持32 B ABI和sidecar `+0x100`；超过14框发布ERROR且禁止静默截断。之后用户最终以身份A确认 **DSH-022 rev3** 同为 `+0x100`/14项口径，本实现按该一致版本记录，不再等待DSH对齐。
- 冻结结果块为32 B头、16 B检测项步进；sidecar从基址 `0x20800000 + 0x100` 开始，占32 B。16个检测项会到 `0x120`，与 `+0x100` 的sidecar重叠。按已批准口径，本适配最多写14项：头32 B + 14×16 B = 256 B，sidecar正好从第14项之后开始。超过14项时发布 `n_dets=0,status=OVERRUN,valid=0` 的错误帧并返回明确拒绝码，不会截断后继续报OK。

## 冻结输入与真实接口

实现按以下文件SHA与commit固定只读输入；2B源文件的相关路径在该commit中无未提交差异：

| 输入 | 固定版本 / SHA-256 |
|---|---|
| 阶段6 6-D冻结口径文档 | 文件 SHA-256 `956585f80e19819e825558630a5a0d1172488a33a46b91d3b3ded6d3f18f55c0` |
| 阶段5结果ABI头 `s5_result_abi.h` | 文件 SHA-256 `0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c` |
| 2B上游 C 解码API工作树 | `D:/FPGA_Competition/w2b`，HEAD `07c3d3958578b9cc9d3b8eae3758711fe08724c2` |
| `s2a_ps_decode_nms_reference.h` | 文件 SHA-256 `edd61d7f47e2681ebd3b21f599c9637d41b257f5e0fc7b9b909f7962d758ce47` |
| `s2a_ps_decode_nms_reference.c` | 文件 SHA-256 `cf1904da1b6f9110a957ea788cdb7f9c6b7773d2fd8b7b61779063e5f995d845` |
| `s2b_inference_app.c` | 文件 SHA-256 `9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39` |
| S5生产者v2冻结记录 | 文件 SHA-256 `e964397b754f29e561c463e94720d3d7e75d508865eb0cfe20df0491cb87a95f` |
| 冻结记录中声明的 `s5_display_app.c` | 源码 SHA-256 前缀 `b2ec56e0` |
| 冻结记录中声明的 `s5_publish_abi.h` | 源码 SHA-256 前缀 `4ae38014` |

真实链路入口是 `D:/FPGA_Competition/w2b/vitis/s2b_inference_app.c` 中的 `s2a_t62_decode_nms()` 调用。其真实输入/输出 C 类型来自 `s2a_ps_decode_nms_reference.h`：检测项是 `s2a_t62_detection`，含类别、来源序号、double 分数以及裁剪到 `[0,1]` 的归一化 `x1,y1,x2,y2`。解码器最多返回15项，应用以容量15调用；适配器直接接收该结构及计数，不把mock结构冒充真实C类型。

冻结生产者v2文档报告了 `s5_display_app.c` 与 `s5_publish_abi.h` 的源码哈希，但在允许检查的 `w4` 冻结包中未携带这两个源文件；对指定的 `D:/tmp/lead/video-sw/src/` 与 `D:/tmp/stage5/video-sw/src/` 候选路径也未找到对应源码。因此本目录按已冻结文档实现旁挂区字节布局、状态和发布时序；不能声称已对生产者v2源码做编译链接或源码级回归。

DSH-020 `cd81325` rev2 曾将sidecar移动到 `+0x120` 并容纳16项；随后用户最终确认的DSH-022 rev3与Wong批准的 `+0x100`/14项口径一致，当前C2明确选择后者。rev2与rev3布局不可互换；若集成目标仍绑定DSH-020 rev2，不能接入本构建，须由DSH按已确认的rev3基线准备集成副本。

## 接口与写入行为

- `C2Publisher_Init()` 用 `GT_at_start >> 10` 派生16位初值；调用方必须明确给出可核验的上一会话ID。缺失时返回 `C2_ERR_PREVIOUS_SESSION_UNKNOWN`，不初始化、不写DDR、不假称跨POR唯一。碰撞时最多按冻结规则递增重试8次。
- 第一条 `result_seq=0`，后续严格 `+1`；`0xFFFFFFFF` 后拒绝，不回绕。seqlock从偶数0开始，每条发布按奇/偶各加1；为避免未冻结的计数回绕，临近 `uint32` 上限时停止发布。
- 仅接受640×480图像；2B解码的归一化xyxy按四舍五入换算到640×480源坐标，`x+w≤640`、`y+h≤480`。类别必须为0–4，分数必须有限且在0–1，Q8按 `round(score×255)` 编码。越界、非有限值、零面积框均写无效ERROR帧，不发布部分检测项。
- `C2Publisher`及其状态只允许一个推理生产线程串行调用；多线程/中断重入不属于此接口保证。
- 结果块基址必须4字节对齐，否则返回 `C2_ERR_ALIGNMENT` 且不写DDR。seqlock用一次 `volatile uint32_t` 存储更新；此字写入要求小端、对齐的32位访问，并要求目标编译器在Cortex-A9上生成单条字存储。C语言本身不保证volatile访问原子。GCC 8.1.0主机 `-O0 -S` 检查中该helper为一条 `movl %edx,(%rax)`；主机测试还验证小端布局和未对齐地址拒绝。该x86主机证据不等于ARM目标反汇编、DDR观察原子性、DSB及cache-flush回调验收，后者仍须由目标构建/板上证据确认。
- 显示结果32 B头与前14项逐字段按小端序写入。旁挂区 `S5X1` 在 `+0x100`，32 B、版本1、session、result_seq、GT结果时间、seqlock、reserved=0。
- 发布分四次flush：先写奇seqlock、屏障并flush整块；再写头/14项/sidecar非时间字段并flush整块；再采样GT、写 `result_time` 并flush旁挂区；最后写偶seqlock并再次flush旁挂区。任何写入期间flush/GT采样失败都会将publisher置为poisoned，之后拒绝继续写，避免以稳定偶数发布不完整数据。
- `result_time` 在最后一段flush之前采样，不能等于“最终flush完成时刻”。若调用方提供receipt，最后偶数seqlock flush后再采样一次GT，并在receipt给出 `flush_complete_ticks` 与 `result_time_to_flush_ticks`；此差值是本次发布的可观测误差界。完成时钟读取失败时标记 `flush_gap_valid=0`，不伪报误差为零。冻结消费者按GT年龄计算时需把该差值纳入解释。
- `C2_ClassifyBusinessState()` 逐项执行冻结优先级：未知状态位/`valid=0`/`overrun=1`/不安全计数 → ERROR；`stale=1` 或GT年龄严格超过200 ms → TIMEOUT；有效且0项 → NO_HAND；其他 → OK。GT阈值直接按ticks比较，避免整数毫秒向下取整把略超200 ms判为未超时。

## 集成接缝（此轮未改2B或S5冻结源）

建议在2B `infer_one()` 中、`s2a_t62_decode_nms()` 成功后且发送UART响应前，由集成方调用本适配器。生产者只需新增本目录的C源并链接2B既有解码器；输出指针必须映射到 `S5_RESULT_BASE`。接缝大致如下，变量名以2B应用内局部对象为准：

```c
C2FrameInput result;
result.frame_id = request->frame + index;
result.image_width = request->width;
result.image_height = request->height;
result.capture_ticks = capture_end_ticks;
result.infer_done_ticks = infer_done_ticks;
result.detections = boxes;
result.detection_count = count;
result.status_flags = decoded == S2A_T62_OK ? S5_RESULT_ST_VALID : 0u;

publish_rc = C2Publisher_Publish(
    &publisher,
    (volatile uint8_t *)(uintptr_t)S5_RESULT_BASE,
    C2_RESULT_WRITE_BYTES,
    &result,
    &platform_ops,
    &receipt);
```

当前2B应用接收UART图像数据，并未在 `s2a_t62_decode_nms()` 的C接口中携带拍摄结束GT时间。集成方不得用frame编号、推理开始时刻或任意常量填充 `capture_ticks`；必须在真实采集/输入边界采样并传入。`infer_done_ticks` 应在decoder成功返回后立即从真实GT读取。若板上调用链无法提供有明確事件定义的capture GT，6-D可信cap/age验收保持BLOCKED。

另一个部署前置是上一会话ID的持久保存及读取。当前冻结口径要求和上一POR会话不相同，但本接口只接收上游提供的上一ID，不自行访问QSPI或其他持久介质。没有获批准且可审计的读取来源时，初始化fail-closed，板上真实写入不可执行。

## 主机单测

`run_host_tests.ps1` 可由Windows PowerShell 5.1或PowerShell 7执行；脚本使用ASCII命令文本以兼容5.1对无BOM UTF-8脚本的解析。固定命令为：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\codex-worktrees\w6\legacy_codex_20261031\c2\run_host_tests.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File D:\codex-worktrees\w6\legacy_codex_20261031\c2\run_host_tests.ps1
```

脚本以 `-std=c11 -Wall -Wextra -Werror -pedantic` 编译本适配、2B冻结commit内的解码API和测试；每次将构建产物写入系统临时目录下的唯一 `c2-host-<GUID>` 目录，并在结束时删除，不写源码目录。用例覆盖实际2B decoder调用到发布路径、14项成功且第14项/sidecar边界与前后guard检查、15项覆盖既有有效帧后发布ERROR且不截断、NaN/±Inf、越界/反向/零面积/舍入退化框、`x2=y2=1`画布边界、score 0/0.5/1的Q8结果、未对齐地址拒绝、状态优先级、200 ms严格边界、跨POR前会话输入缺失、序号耗尽、奇偶seqlock flush次序和flush失败poison。主机mock只用于检查回调时序和字节布局，不作为板上结果，也不证明目标硬件的32位原子可见性。

## 板上验证计划（未执行，板窗由DSH统一调度）

1. 独立Reviewer先审C2源与主机证据；所选 `+0x100`/14项口径已由Wong及DSH-022 rev3确认。DSH冻结该C2源码的精确hash。确认 `ENABLE=0`、不push，现有阶段5/6冻结ELF/bit/XSA保持原样。
2. DSH提供独立临时构建副本；仅在该副本接入C2源，不覆盖冻结P3q或阶段6文件。交叉编译前固定2B解码器HEAD、C2源hash、S5 ABI头hash、工具/BSP及linker script，并做大小/符号检查；从目标反汇编确认seqlock更新为对齐的单条32位存储。
3. 板卡运行前由DSH确认板卡独占租约与当前阶段6运行版本；本任务Agent不启动`hw_server`、XSDB或操作硬件。DSH解决并记录两项可信输入：真实capture GT事件的取样位置、可持久读取的previous `session_id` 来源。任一输入缺失则停止板上C2写入并回报BLOCKED。
4. 在DSH授权窗口先做只读DDR快照，确认结果块基址和当前拥有者；运行独立临时ELF后读取 `0x20800000..0x2080011F`。用seqlock读两遍并要求相同偶数，核对头、检测项、sidecar、session与序号；不写QSPI、不烧录冻结区、不复用旧RunId。
5. 真实推理输入至少包含空检测与非空检测；检测框须来自板上2B decoder，记录frame_id、decoder输出计数、序号和状态。若decoder输出15项，必须观察到ERROR且n_dets=0，不能接受14项截断结果。分别验证真实invalid/overrun/stale路径；无受控真实故障源时记NOT_RUN，不能以主机mock冒充。
6. 从GT复算 `age_publish`，记录result_time到最终flush完成的本次tick间隔及其有效性；判据为年龄≤200 ms，且读者按偶数seqlock取得一致快照。保存本轮源码绑定、ELF/日志/回读哈希与限制；板窗关闭由DSH确认。任何硬件动作由DSH统一调度并执行。

主机验证：2026-10-31 01:14:50–01:14:51（UTC+8），Windows PowerShell 5.1.26100.8457与PowerShell 7.6.5分别执行上面的 `-NoProfile -ExecutionPolicy Bypass -File ...` 命令，均输出 `PASS：C2发布、边界、时序及真实2B解码接口测试`、退出码0；逐字节独立副本由PowerShell 5.1再执行一次，退出码0。GCC `x86_64-win32-seh-rev0` 8.1.0，独立 `-O0 -S`汇编检查退出码0并看到单条主机 `movl` 字存储。板上步骤全部NOT_RUN。缺少真实capture GT接缝、previous-session持久来源、ARM目标反汇编/DDR原子可见性证据，以及冻结S5生产者v2源码文件的源码级绑定；这些限制不因主机单测PASS而关闭。
