# 最终进程保护轻量验证

独立Reviewer对5份冻结文件复核并串行实际复跑：direct 8个unittest方法（构造测试含两个子场景，合计9个夹具场景）、supervisor 10项均通过，退出0、无skip。命令和UTC+8时间由两份run.json记录；原始stdout/stderr保留，7份fixture_result原字节回执复制至fixture_receipts。测试生成的辅助脚本/伪许可证是可重建夹具，不是冻结依赖；未读取真实许可证内容。

修复覆盖非有限时间预算拒绝、挂起root只按原始HANDLE/出生时刻及稳定单成员Job核验、Job构造读回异常关闭句柄，以及低内存/超时/监控失败的本Job隔离清理。运行中进程的idle attach/READY检查保持原语义。Reviewer结论PASS仅覆盖上述源码和微型回归。

未运行RTL编译/仿真或板卡；不表示T11矩阵或2B验收通过。峰值内存未测。前3个Run的失败/阻断原因与原件分别保留，不被本次PASS覆盖。
