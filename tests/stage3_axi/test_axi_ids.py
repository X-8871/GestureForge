"""用正常和损坏的连接片段验证静态检查不会忽略高位或重复实例。"""

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "s3_check_axi_ids.py"
SPEC = importlib.util.spec_from_file_location("s3_axi", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ConnectionsTest(unittest.TestCase):
    """测试只针对连接检查，不声称覆盖真实 AXI 总线。"""

    def setUp(self):
        self.source = "\n".join(
            [f".S_AXI_HP0_{field}({{1'b0,1'b0,1'b0,1'b0,1'b0,axi_mem_intercon_M00_AXI_{field}}})" for field in ("ARID", "AWID", "WID")]
            + [f".m_axi_{field.lower()}(xbar_to_m00_couplers_{field}[0])" for field in ("BID", "RID")]
        )

    def test_complete(self):
        self.assertTrue(all(MODULE.inspect_connections(self.source).values()))

    def test_wrong_high_bit(self):
        self.assertFalse(all(MODULE.inspect_connections(self.source.replace("1'b0", "1'b1", 1)).values()))

    def test_wrong_response_bit(self):
        self.assertFalse(all(MODULE.inspect_connections(self.source.replace("BID[0]", "BID[1]")).values()))

    def test_duplicate(self):
        self.assertFalse(all(MODULE.inspect_connections(self.source + "\n" + self.source).values()))

    def test_missing(self):
        self.assertFalse(all(MODULE.inspect_connections("").values()))


if __name__ == "__main__":
    unittest.main()
