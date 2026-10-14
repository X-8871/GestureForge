# S2B平台检查器精确路径 preflight 修复记录

## 范围与结论

本任务只修复 `verification/check_s2b_inference_platform.py` 的精确文件路径 helper，并新增 `verification/test_s2b_platform_paths.py`。HEAD 基线为 `5b4b140d9540759a6940b339e93278371c06987e`。未修改 RTL、派生规则、模型、板卡、接口或构建参数；未启动 Vitis、Vivado 或 JTAG。

修复前，指定的静态 preflight 命令以退出码 1 失败，目录枚举在 `C:\Users\22061` 收到 Windows `WinError 5`。修复后，同一静态 preflight 退出码为 0。

当逐级枚举父目录成功时，helper 仍逐项匹配目录返回的原始名称。仅在 `Path.iterdir()` 抛出 `PermissionError` 时，才从该父目录开始逐组件执行 `lstat`，拒绝符号链接/reparse 点和中间非目录，并以 `resolve(strict=True)` 的路径字符串逐字符比较实际大小写。其他枚举错误继续失败；没有使用 Windows 路径对象的大小写折叠比较。

## 回归与静态检查

| 检查 | 命令 | 结果 | 原生退出码 / 耗时 |
|---|---|---|---|
| 修复前故障复现 | `python -B verification/check_s2b_inference_platform.py --root 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'` | `C:\Users\22061` 目录枚举触发 `WinError 5` | 1 / 0.207 s |
| 路径回归 | `python -B -m unittest verification.test_s2b_platform_paths -v` | 11 项；OK，1 项跳过 | 0 / 0.374 s |
| 当前静态 preflight | `python -B verification/check_s2b_inference_platform.py --root 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'` | `PLATFORM_STATIC:OK visibility=0 rtl_sources=18` | 0 / 0.293 s |
| evidence 清单核验 | `python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-T19/platform_path_preflight_20261014_r01/delivery_manifest.json` | `CHECKS_OK`；仅清单绑定和目录枚举检查通过 | 0 / 0.315 s |

回归覆盖常规精确路径、盘符根与中间父目录的注入式枚举拒绝、拒绝注入是否实际发生、非 `PermissionError` 不被吞掉、大小写错误、缺失文件、中间分量非目录、符号链接元数据和 reparse 属性。真实 Windows 符号链接创建测试因账户缺少所需特权（`WinError 1314`）跳过；其拒绝分支由合成 `lstat` 元数据用例覆盖。完整 unittest 输出保存在 [`unit_test_output.txt`](unit_test_output.txt)。

静态 preflight 仍是 `visibility=0` 检查，只说明当前静态源码检查通过，不代表 visibility=1、BD、时序、Vivado 构建或实板验证通过。输出保存在 [`platform_preflight.txt`](platform_preflight.txt)。本次 Python 为 3.12.14（Codex bundled runtime）。

## 源码绑定

| 文件 | SHA-256 |
|---|---|
| `verification/check_s2b_inference_platform.py` | `dfd64cff1fd5ed8f61961dbde22802a3ba1ed2f0171f0c0327a71503f2b6737e` |
| `verification/test_s2b_platform_paths.py` | `d3a544e5b5f18b2cb33db8d90478a2e8c910c0cfadc19d854f873cda1e35c32d` |
以上测试源码哈希绑定首次运行，原始源码已保存为 `test_source_before_symlink_fixture.py.snapshot`。后续有效符号链接类型与异常原因断言修正后的测试源码 SHA-256 为 `42267e6e08f66c00f140aa53f7d37dd454f6458b405113144cb102c13d3243a5`；对应回归为 10 项通过、1 项因 WinError 1314 跳过，见 `fixture_correction.json` 和 `unit_test_output_r02.txt`。
