# 阶段3 T03/T04：厂商应用源码 -> Cortex-A9 standalone ELF（通用版，随应用源码自动适配）
# 用法：在 HSI 生成的 app 目录内执行
#   make -f Makefile.app [EXEC=<输出名>.elf] [BSP_DIR=<bsp 子目录>]
# 依赖：PATH 内可用 arm-none-eabi-gcc（Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin）与 make（Vitis\gnuwin\bin）
# 说明：与厂商 Vitis 参考工程等价的编译/链接参数（Cortex-A9 + VFPv3 hard-float、libxil.a、lscript.ld）。
#       源码自动发现：顶层 *.c + 一级子目录（display_ctrl/ dynclk/ i2c/ ...），无需按应用逐个改脚本。

CC := arm-none-eabi-gcc
BSP_DIR ?= empty_application_bsp
PROC ?= ps7_cortexa9_0
EXEC ?= app.elf

CC_FLAGS := -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard
OPT_FLAGS := -O2 -c
LN_FLAGS := -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -Wl,-build-id=none -specs=Xilinx.spec -Wl,--start-group,-lxil,-lgcc,-lc,--end-group -Wl,--gc-sections

# 自动发现源码目录：排除 BSP 目录，避免把 BSP 源码重复编进应用
SRC_DIRS := . $(filter-out $(BSP_DIR),$(sort $(patsubst %/,%,$(dir $(wildcard */*.c)))))
c_SOURCES := $(foreach d,$(SRC_DIRS),$(wildcard $(d)/*.c))
OBJS := $(patsubst %.c,%.o,$(c_SOURCES))

INCLUDEPATH := -I$(BSP_DIR)/$(PROC)/include $(foreach d,$(SRC_DIRS),-I$(d))
LIBPATH := -L$(BSP_DIR)/$(PROC)/lib
LIBS := $(BSP_DIR)/$(PROC)/lib/libxil.a
LSCRIPT := -Tlscript.ld

.PHONY: all bsp clean
all: $(EXEC)

$(EXEC): $(LIBS) $(OBJS)
	@echo "APP_SOURCES=$(c_SOURCES)"
	$(CC) -o $@ $(OBJS) $(CC_FLAGS) $(LN_FLAGS) $(LIBPATH) $(LSCRIPT)

$(LIBS):
	$(MAKE) -C $(BSP_DIR)

%.o: %.c
	$(CC) $(OPT_FLAGS) $(CC_FLAGS) -c $< -o $@ $(INCLUDEPATH)

bsp:
	$(MAKE) -C $(BSP_DIR)

clean:
	rm -f $(OBJS) $(EXEC)