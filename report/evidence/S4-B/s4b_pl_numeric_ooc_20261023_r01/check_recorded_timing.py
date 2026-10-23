import pathlib
import sys

# 只检查本包原始时序报告，不执行Vivado或更改约束。
report = pathlib.Path(__file__).with_name('timing_summary.rpt').read_text(encoding='utf-8')
if 'Timing constraints are not met.' in report:
    print('TIMING_NOT_CLOSED: preserved report states timing constraints are not met')
    sys.exit(1)
if 'All user specified timing constraints are met.' in report:
    print('RECORDED_TIMING_MET')
    sys.exit(0)
print('UNKNOWN_REPORT_STATUS')
sys.exit(2)
