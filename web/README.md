# GestureForge 三模型摄像头对比网页

## 启动

在 `D:\FPGA_Competition` 根目录执行：

```powershell
py web\gestureforge_web.py --host 127.0.0.1 --port 8765
```

打开 [http://127.0.0.1:8765/](http://127.0.0.1:8765/)，点击“启动摄像头”。浏览器只把当前 JPEG 帧提交给本机服务；服务在系统临时目录短暂写入帧文件，推理结束后删除，不上传也不保存摄像头图像。

每次请求使用独立工作目录，Darknet 可能生成的 `predictions.jpg`、`bad.list` 和输入帧会随该目录一起清理；服务异常或超时也会执行同样的清理。

## 对比方法

1. 在“当前真实手势”中选择实际的五类手势。
2. 点击“同帧跑三模型”，等待三张卡片分别返回结果。
3. 对每张卡片点击“正确”或“错误”；统计保存在当前浏览器的 `localStorage`，点击右上角按钮可以清空。
4. `full608` 只作 PC 对照，tiny320/tiny416 是板上候选；卡片上的人工样本百分比不等于官方 test mAP。

也可以使用“导入一帧”绕过摄像头权限先验证接口。服务启动前可执行：

```powershell
py web\gestureforge_web.py --check
```

该检查会验证 Darknet 可执行文件、三套 cfg/data/weights 和权重 SHA；模型注册表位于 `web\gestureforge_web.py`，保留三个独立模型 ID，后续可以切换到已留证旧版本实现回滚。

## 固定推理口径

服务端使用 `score_threshold=0.25`、NMS IoU=`0.45`、每图最多输出 15 框。正式数值门槛和 D3 PC 基准分别见 `report/evidence/S1-T02/20260922_s1_t02_d6_metric_policy_r2.json` 与 `20260922_s1_t02_d3_pc_benchmark_r1.json`。
