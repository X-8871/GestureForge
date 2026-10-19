"""生成 S3-T04 应用诊断补丁：只给厂商摄像头应用加 UART 诊断打印，不改任何寄存器时序与配置。

做三件事：
1) 从官方源复制一份应用目录到 scratch；
2) 在 main() 关键节点插入 S3_DIAG 打印（应用启动、传感器 CHIP ID、显示启动状态、VDMA 写入启动）；
3) 用 git diff --no-index 生成 unified diff，并对全新副本验证补丁可干净应用。

输出补丁不进 Git 之外的地方；只写调用方给定的输出路径。
"""
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT_PATCH = Path(sys.argv[2])
SCRATCH = Path(sys.argv[3])

if SCRATCH.exists():
    shutil.rmtree(SCRATCH)
SCRATCH.mkdir(parents=True)
ORIG = SCRATCH / "orig"
WORK = SCRATCH / "work"
shutil.copytree(SRC, ORIG)
shutil.copytree(SRC, WORK)

FILE = "display_demo.c"
target = WORK / FILE
with open(target, "r", encoding="utf-8", newline="") as fh:
    raw = fh.read()
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

insertions = [
    (
        "int main(void)\n{\n\n\tint Status;",
        "int main(void)\n{\n\n\tint Status;\n\txil_printf(\"S3_DIAG_APP_ENTER\\r\\n\");",
    ),
    (
        "\tsensor_init(&ps_i2c0);\n",
        "\tsensor_init(&ps_i2c0);\n"
        "\t/* S3-DIAG: 传感器 I2C 连通性诊断；OV5640 CHIP ID 期望 0x5640 */\n"
        "\t{\n"
        "\t\tu8 s3_id_hi = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x300A);\n"
        "\t\tu8 s3_id_lo = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x300B);\n"
        "\t\txil_printf(\"S3_DIAG_SENSOR_ID=0x%02X%02X\\r\\n\", s3_id_hi, s3_id_lo);\n"
        "\t}\n",
    ),
    (
        "\tStatus = DisplayStart(&dispCtrl);\n",
        "\tStatus = DisplayStart(&dispCtrl);\n\txil_printf(\"S3_DIAG_DISPLAY_START status=%d\\r\\n\", Status);\n",
    ),
    (
        "\tvdma_write_init(XPAR_AXIVDMA_1_DEVICE_ID,1280 * 3,720,1280 * 3,(unsigned int)dispCtrl.framePtr[dispCtrl.curFrame]);\n",
        "\tvdma_write_init(XPAR_AXIVDMA_1_DEVICE_ID,1280 * 3,720,1280 * 3,(unsigned int)dispCtrl.framePtr[dispCtrl.curFrame]);\n"
        "\txil_printf(\"S3_DIAG_VDMA_WRITE_STARTED\\r\\n\");\n",
    ),
    (
        "\tsensor_init(&ps_i2c0);\n"
        "\t/* S3-DIAG: 传感器 I2C 连通性诊断；OV5640 CHIP ID 期望 0x5640 */\n",
        "\tsensor_init(&ps_i2c0);\n"
        "\t/* S3-DIAG2: I2C 控制器寄存器 + 整总线扫描 + CHIP ID 重试读取。\n"
        "\t * 只读探测：用于区分“I2C 总线/连接不通（无任何 ACK）”与“器件存在但地址/配置不符”。*/\n"
        "\t{\n"
        "\t\tXIicPs *s3_iic = &ps_i2c0;\n"
        "\t\tint s3_a, s3_s, s3_s2;\n"
        "\t\tint s3_found = 0;\n"
        "\t\tu8 s3_wr[2];\n"
        "\t\txil_printf(\"S3_DIAG2_IIC_BASE=0x%08X\\r\\n\", (unsigned int)s3_iic->Config.BaseAddress);\n"
        "\t\txil_printf(\"S3_DIAG2_IIC_CR=0x%08X SR=0x%08X ISR=0x%08X\\r\\n\",\n"
        "\t\t\t(unsigned int)XIicPs_ReadReg(s3_iic->Config.BaseAddress, XIICPS_CR_OFFSET),\n"
        "\t\t\t(unsigned int)XIicPs_ReadReg(s3_iic->Config.BaseAddress, XIICPS_SR_OFFSET),\n"
        "\t\t\t(unsigned int)XIicPs_ReadReg(s3_iic->Config.BaseAddress, XIICPS_ISR_OFFSET));\n"
        "\t\tfor (s3_a = 0x08; s3_a < 0x78; s3_a++) {\n"
        "\t\t\tu8 s3_rd = 0;\n"
        "\t\t\ts3_wr[0] = 0x30; s3_wr[1] = 0x0A;\n"
        "\t\t\ts3_s = XIicPs_MasterSendPolled(s3_iic, s3_wr, 2, (u8)s3_a);\n"
        "\t\t\twhile (XIicPs_BusIsBusy(s3_iic));\n"
        "\t\t\tif (s3_s != XST_SUCCESS) { continue; }\n"
        "\t\t\ts3_s2 = XIicPs_MasterRecvPolled(s3_iic, &s3_rd, 1, (u8)s3_a);\n"
        "\t\t\twhile (XIicPs_BusIsBusy(s3_iic));\n"
        "\t\t\txil_printf(\"S3_DIAG2_DEV=0x%02X recv=%d val=0x%02X\\r\\n\", s3_a, s3_s2, s3_rd);\n"
        "\t\t\ts3_found++;\n"
        "\t\t}\n"
        "\t\txil_printf(\"S3_DIAG2_SCAN_ACK_COUNT=%d\\r\\n\", s3_found);\n"
        "\t\t{\n"
        "\t\t\tint s3_t;\n"
        "\t\t\tfor (s3_t = 0; s3_t < 3; s3_t++) {\n"
        "\t\t\t\tu8 s3_h = (u8)i2c_reg16_read(s3_iic, 0x3c, 0x300A);\n"
        "\t\t\t\tu8 s3_l = (u8)i2c_reg16_read(s3_iic, 0x3c, 0x300B);\n"
        "\t\t\t\txil_printf(\"S3_DIAG2_CHIPID_TRY%d=0x%02X%02X\\r\\n\", s3_t, s3_h, s3_l);\n"
        "\t\t\t\tusleep(200000);\n"
        "\t\t\t}\n"
        "\t\t}\n"
        "\t}\n"
        "\t/* S3-DIAG: 传感器 I2C 连通性诊断；OV5640 CHIP ID 期望 0x5640 */\n",
    ),
]

for old, new in insertions:
    if old not in text:
        print(f"INSERT_CONTEXT_NOT_FOUND: {old.splitlines()[0][:60]}")
        sys.exit(2)
    if text.count(old) != 1:
        print(f"INSERT_CONTEXT_NOT_UNIQUE: {old.splitlines()[0][:60]} count={text.count(old)}")
        sys.exit(2)
    text = text.replace(old, new)

if crlf:
    text = text.replace("\n", "\r\n")
with open(target, "w", encoding="utf-8", newline="") as fh:
    fh.write(text)

# 生成 unified diff（保留 git 风格路径，便于 git apply -p1）
cp = subprocess.run(
    ["git", "diff", "--no-index", "--src-prefix=a/", "--dst-prefix=b/", str(ORIG / FILE), str(WORK / FILE)],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
)
diff = cp.stdout
# 只保留 hunk，自己写稳定表头，避免绝对路径/CRLF 差异导致 git apply 跳过
lines = diff.splitlines()
try:
    first_hunk = next(i for i, ln in enumerate(lines) if ln.startswith("@@"))
except StopIteration:
    print("NO_HUNK_IN_DIFF")
    sys.exit(2)
hunks = "\n".join(lines[first_hunk:]) + "\n"
diff = f"--- a/{FILE}\n+++ b/{FILE}\n{hunks}"
if not diff.strip():
    print("EMPTY_DIFF")
    sys.exit(2)
OUT_PATCH.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATCH, "w", encoding="utf-8", newline="") as fh:
    fh.write(diff)

# 验证：对全新副本应用补丁
VERIFY = SCRATCH / "verify"
shutil.copytree(SRC, VERIFY)
res = subprocess.run(
    ["git", "apply", "--verbose", "-p1", str(OUT_PATCH)],
    cwd=VERIFY, capture_output=True, text=True, encoding="utf-8", errors="replace",
)
print(f"PATCH={OUT_PATCH}")
print(f"GIT_APPLY_EXIT={res.returncode}")
print(res.stdout.strip()[-500:])
print(res.stderr.strip()[-500:])
if res.returncode != 0:
    sys.exit(3)
with open(VERIFY / FILE, "r", encoding="utf-8", newline="") as fh:
    verify_text = fh.read()
print(f"VERIFY_HAS_APP_ENTER={'S3_DIAG_APP_ENTER' in verify_text}")
print(f"VERIFY_HAS_SENSOR_ID={'S3_DIAG_SENSOR_ID' in verify_text}")
print(f"VERIFY_HAS_DISPLAY_START={'S3_DIAG_DISPLAY_START' in verify_text}")
print(f"VERIFY_HAS_VDMA_WRITE={'S3_DIAG_VDMA_WRITE_STARTED' in verify_text}")
print(f"PATCH_LINES={len(diff.splitlines())}")