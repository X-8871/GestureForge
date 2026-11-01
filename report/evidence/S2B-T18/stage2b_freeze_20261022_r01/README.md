# 阶段2B最终冻结候选

RunId：`stage2b_freeze_20261022_r01`  
来源提交：`16ce2cdf8c00c6214435629d75a5e4b63acb66a9`  
状态：**候选输入已绑定；不代表G4/G5通过。**

## 文件

- `final_freeze_inventory.json`：范围、状态、SHA绑定与恢复依赖摘要。
- `inputs_manifest.json`：适配 `check_stage_delivery.py --mode inputs`。
- `delivery_manifest.json`：适配 `check_stage_delivery.py --mode evidence`；仅枚举本RunId小型产物。

- `artifacts/rebuilt_infer.elf`：从受SHA绑定的tmp ELF逐字节复制，供离线恢复。

## 核验命令

```bash
python -B tmp/2B/prepare_final_freeze_20261022.py --host-review report/evidence/S2B-T20/final_host_restore_review_20261022_r01/review_two_frame_and_ack_observer_r02.md
python -B verification/check_stage_delivery.py --mode inputs --manifest report/evidence/S2B-T18/stage2b_freeze_20261022_r01/inputs_manifest.json
python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-T18/stage2b_freeze_20261022_r01/delivery_manifest.json
```

清单保留各证据自身的PASS、FAILED、CHANGES_REQUIRED、UNKNOWN或BLOCKED边界。Git只保留代码/元数据；R04 bit/XSA、恢复包、重建ELF/init ELF、官方工具链/BSP以及模型原始数据是工作站/恢复归档依赖，不能删除；源代码仓库的干净检出不能单独重建全部二进制。
