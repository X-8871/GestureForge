-- rgb2dvi_wrap.vhd —— 阶段5（HDMI 显示链）P3b 自有薄封装
--
-- 为什么需要这一层：Verilog 实例化 VHDL entity 时**不能覆盖 generic**，而厂商
-- rgb2dvi 的默认 generic 是 kGenerateSerialClk=true / kRstActiveHigh=true，
-- 本设计需要 kGenerateSerialClk=false（外部 5x 串行时钟）与 kRstActiveHigh=false
-- （复位低有效）。因此用这层 VHDL 封装把 generic 固定下来，Verilog 侧只看到
-- 纯 std_logic 端口。
--
-- 厂商参考依据（只读，不改原文件）：
--   .../02_hdmi_out_test/.../ip/rgb2dvi_0/rgb2dvi_0.xci
--     MODELPARAM kGenerateSerialClk = false
--     MODELPARAM kClkRange          = 1
--     MODELPARAM kKstActiveHigh     = false（即 kRstActiveHigh=false）
--   .../repo/ip/rgb2dvi_v1_3/src/rgb2dvi.vhd:63-66, 101-129, 192
--
-- 许可：本文件为项目自有代码；被实例化的 rgb2dvi 及其 6 个子模块保持
--       Digilent BSD 3-clause 原许可与文件内容不变（复制到 src/rgb2dvi/）。

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity rgb2dvi_wrap is
   Port (
      -- DVI 1.0 TMDS 输出
      TMDS_Clk_p  : out std_logic;
      TMDS_Clk_n  : out std_logic;
      TMDS_Data_p : out std_logic_vector(2 downto 0);
      TMDS_Data_n : out std_logic_vector(2 downto 0);
      oen         : out std_logic;
      -- 异步复位（厂商语义：aRst 高有效 / aRst_n 低有效；此处只用低有效）
      aRst_n      : in  std_logic;
      -- 像素域视频输入（RGB888，与 BD 的 vid_data[23:0] 一一对应）
      vid_pData   : in  std_logic_vector(23 downto 0);
      vid_pVDE    : in  std_logic;
      vid_pHSync  : in  std_logic;
      vid_pVSync  : in  std_logic;
      PixelClk    : in  std_logic;  -- 74.21875 MHz（BD clk_out1）
      SerialClk   : in  std_logic); -- 371.09375 MHz（BD clk_out2，同一 MMCM 的 5x）
end rgb2dvi_wrap;

architecture Behavioral of rgb2dvi_wrap is
begin

   Inst_rgb2dvi: entity work.rgb2dvi
      generic map (
         kGenerateSerialClk => false,   -- 用外部 5x 时钟（与厂商参考工程配置一致）
         kClkPrimitive      => "MMCM",  -- 仅内部生成时生效，保留厂商原值
         kClkRange          => 1,       -- 仅内部生成时生效，保留厂商原值
         kRstActiveHigh     => false)   -- 低有效复位：由 aRst_n 驱动
      port map (
         TMDS_Clk_p  => TMDS_Clk_p,
         TMDS_Clk_n  => TMDS_Clk_n,
         TMDS_Data_p => TMDS_Data_p,
         TMDS_Data_n => TMDS_Data_n,
         oen         => oen,
         aRst        => '0',
         aRst_n      => aRst_n,
         vid_pData   => vid_pData,
         vid_pVDE    => vid_pVDE,
         vid_pHSync  => vid_pHSync,
         vid_pVSync  => vid_pVSync,
         PixelClk    => PixelClk,
         SerialClk   => SerialClk);

end Behavioral;