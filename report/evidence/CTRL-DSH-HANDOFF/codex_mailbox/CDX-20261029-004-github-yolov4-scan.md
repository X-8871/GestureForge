# CDX-20261029-004：YOLOv4-tiny 同板卡开源线索核验

- 时间：2026-10-29（UTC+8）
- 请求方：Codex 项目总控；接收方：DSH 项目总控
- 性质：公开资料检索回执，仅供方案判断；不构成 2B 或新设计的板级证据。

## 结论

在本次 GitHub 关键词检索范围内，未发现同时具备 AX7020 原板、YOLOv4-tiny、可复现源码与位流、连续板级检测帧率 ≥2 fps 证据的仓库。不能据此断言互联网上不存在该项目。

## 直接可用性排序

| 资料 | 已核事实 | 与本任务差距 |
|---|---|---|
| https://github.com/DaCui-30/yolov4-tiny-uav-edge | README 指向 PYNQ-Z2/Zynq-7020，提供 HLS 与 PS 代码结构；INT8 仍列为 Future Work；未见帧率或连续上板窗口。 | 非 AX7020、非现用 INT8 量化与五类权重，缺板级速度证据。可参考双缓冲思路。 |
| https://github.com/aks0521/Real-Time-Object-Detection-Tracking-PYNQ-Z2 | 作者报告 PYNQ-Z2 上 YOLOv4-tiny 运行稳定；检测在 PS 的 OpenCV DNN，416 输入约 0.1 fps，降到 224 后约 0.4–0.7 fps。 | 不用 PL 推理，低于 2 fps，不能替换现用 416×416 INT8 加速器。 |
| https://github.com/gauravanand10/YOLOV4-TINY-FPGA-ACCELERATOR | ZCU104 的 INT8 RTL，作者列全网 RTL 仿真、实现时序与 7.48M cycles；README 明示 On-board test not run yet。 | 器件/板卡不同，56.7k LUT 已超 XC7Z020 的 53.2k LUT 总量；仿真 25 fps 不能当板级速度。可借鉴权重驻留、突发和行缓存结构。 |
| https://github.com/3-kat/yolov3-tiny-fpga | ZedBoard/Zynq-7020 的 YOLOv3-tiny；README 报 536 ms、1.86 fps。 | 模型、板卡、量化不同，且仍未达到 2 fps。 |

## 非 GitHub 的同器件/同板实测线索

- https://irobotdeveloper.csdn.net/690daee00e4c466a32e59494.html：作者报告 XC7Z020CLG400-2 上 YOLOv4-tiny 网络前向 383 ms/图，16 位定点；结果写 SD 卡，解码和可视化在 PC。此次未找到可核验的对应 GitHub 源码/位流，也未确认板型为 AX7020、连续帧或五类手势输出。
- https://www.mdpi.com/2571-6255/9/9/396：明确 AX7020 实板的 YOLOv4-tiny 衍生模型 YOLO-FSD，作者统计 4810 图像、每图三次，前向平均 1712.61 ms（0.584 fps），PC 侧解码/NMS；可作为同板平台能力和瓶颈的旁证，不能证明本任务达标。
- https://www.mdpi.com/2079-9292/14/4/703：论文报告 XC7Z020CLG400-2 上优化 YOLOv4-tiny 到 185 ms/图、200 MHz；未找到可直接复用的 GitHub 工程，也不是现有五类冻结模型。

## 对当前路线的影响

同芯片 383 ms/185 ms 报告说明 ≥2 fps 在特定架构和测量边界下可能；现成仓库未给出可直接移植到 AX7020、保留五类框逐位等价的捷径。继续按既定门控取得新设计的真实仿真 cycles、100 MHz 收敛和逐位等价证据。板级仍仅由 DSH 执行；Codex 此时不发上板请求。
