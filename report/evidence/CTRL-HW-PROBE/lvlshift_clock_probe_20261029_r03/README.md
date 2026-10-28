# 电平转换 / PL 配置生命周期 / CSR 读 探针 r03（2026-10-29 02:55–03:05，DSH）

## 三次短探针（普通命令，无 -force）
### r02：编程 → 系统复位
1. Vivado batch program_hw_devices（bit 555a70c2…）: exit 0，PROGRAM_DONE。
2. W1 四动作后 `0xF8000900`（LVL_SHFTR_EN）读回 **0x0F**（使能成功）。
3. `rst -system -stop`（系统复位）后读 CSR：**`Cannot access FPGA: Bitstream is not programmed`**
   ⇒ **系统复位会清掉已加载的 PL 配置**。
### r03：系统复位 → init → 编程 → 读
4. `rst -system -stop` → `dow init.elf`（无输出）→ `con` → 停核：`0xF8000900 = 0x00000000`。
5. 重新编程 PL（exit 0）。
6. CSR 读（移位器=0）：`Cannot access FPGA: Level shifters are not enabled`。
7. 置 `0xF8000900=0x0F`（读回 0xF）后 CSR 读：**`Timeout waiting for the Instruction Complete bit`**
   ⇒ AXI 读发出、无响应；随后 DAP 再次粘连（`APB AP transaction error`），`mrd` 报 Invalid target。
### 结论与边界
- **已证**：① 系统复位会清 PL 配置；② LVL_SHFTR_EN 上电/复位后为 0，需显式置 0x0F；③ 移位器=0 时 CSR 读必失败。
- **未证**：本轮 `dow init.elf` 无可见输出、未能确认 ps7_init 是否真正执行（DDR/FCLK 是否配置），因此
  "编程后 CSR 仍 timeout" **不能**单独判定位流/PL 损坏；也可能是 PS 侧时钟/复位未配置。
- **新假设（待决定性验证）**：应用首次 CSR 读挂住 = 该时刻 **PL 无时钟/无响应**；可由应用侧直接读
  SLCR（PL 无关）取证：`0xF8000900`、`0xF8000170`（FCLK_CTRL0：CLKACT0/DIVISOR0）。
- 边界：DAP 粘连需整机断电；全程未用 -force、未烧 QSPI、未改线；`ENABLE=0`。
