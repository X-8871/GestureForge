# 阶段三缓存清理记录（2026-10-22）

授权：Wong（阶段4/5 已开始，阶段三无用垃圾可清理）。范围仅限阶段三名下可重建构建缓存。

## 保留（绝不动）

- `tmp/s3r06/t04_dualmsb_20261021_r01`（冻结/部署产物与其构建树）
- `tmp/s3r06/t04_gray_20261021_r01`（冻结/部署产物与其构建树）
- `tmp/s3r06/t04_j11cmos2_elf_v10`（冻结/部署产物与其构建树）
- `tmp/s3r06/t04_j11cmos2_elf_v11`（冻结/部署产物与其构建树）
- `tmp/s3r06/t04_j11cmos2_elf_v12`（冻结/部署产物与其构建树）
- `tmp/s3r06/t04_j11cmos2_elf_v9`（冻结/部署产物与其构建树）
- `tmp/s3r06/t04_sof_fix_20261020_r01`（冻结/部署产物与其构建树）
- `tmp/s3r06/t04_stdluma_20261022_r01`（冻结/部署产物与其构建树）
- `report/**`、其它阶段目录、主仓、`NA/`、`clockInfo.txt`

## 删除前冻结哈希复核（全部一致才继续）

- tmp/s3r06/t04_dualmsb_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit `30db09ba8e4e9df8` ⇒ OK
- tmp/s3r06/t04_gray_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit `2f72aaa42936225e` ⇒ OK
- tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/an5642_j11cmos2_v10_read.elf `1457cda4867649dc` ⇒ OK
- tmp/s3r06/t04_j11cmos2_elf_v11/elf_build/app/an5642_j11cmos2_v11_freeze.elf `c01133b1bb0204f0` ⇒ OK
- tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app/an5642_j11cmos2_v12_bars_freeze.elf `527a74fca6ea0774` ⇒ OK
- tmp/s3r06/t04_stdluma_20261022_r01/design_1_wrapper.xsa `90e1bdee1f5baaf9` ⇒ OK
- tmp/s3r06/t04_stdluma_20261022_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit `44e609ccc62647c1` ⇒ OK

## 已删除（41 项，合计 1659.7 MB）

- `tmp/s3r06/t04_display_bluefix_20261021_r01` （187.7 MB）
- `tmp/s3r06/t04_j10cmos2_20261020_r01` （181.0 MB）
- `tmp/s3r06/t04_bluefix_20261020_r01` （180.9 MB）
- `tmp/s3r06/t04_camera_20261020_r03` （180.8 MB）
- `tmp/s3r06/t04_camera_j11_20261020_r01` （180.8 MB）
- `tmp/s3r06/t04_camera_j11cmos2_20261020_r01` （180.8 MB）
- `tmp/s3r06/t04_camera_20261020_r02` （142.8 MB）
- `tmp/s3r06/t04_camera_20261020_r01` （132.1 MB）
- `tmp/s3r06/t04_j11cmos2_elf_v8` （26.5 MB）
- `tmp/s3r06/t04_j11cmos2_elf_v7` （25.1 MB）
- `tmp/s3r06/t04_j11cmos2_elf_v6` （24.8 MB）
- `tmp/s3r06/t04_j11cmos2_elf_v5` （24.2 MB）
- `tmp/s3r06/t04_camera_j11_elf_r01` （23.8 MB）
- `tmp/s3r06/t04_camera_diag2_r02` （23.8 MB）
- `tmp/s3r06/t04_camera_j11cmos2_elf_v4` （23.7 MB）
- `tmp/s3r06/t04_camera_j11cmos2_elf_v3` （23.7 MB）
- `tmp/s3r06/t04_camera_j11cmos2_elf_r01` （23.7 MB）
- `tmp/s3r06/t04_camera_diag2_r01` （23.5 MB）
- `tmp/3/S3-T05/t05_sensor_register_pdf_20261021_r01` （12.6 MB）
- `tmp/3/S3-T05/colpose1_20261022_r01` （5.7 MB）
- `tmp/s3r06/t04_ila_bd_20261020_r02` （5.7 MB）
- `tmp/s3r06/t04_ila_bd_20261020_r01` （5.6 MB）
- `tmp/3/S3-T05/pose2_20261022_r01` （4.6 MB）
- `tmp/3/S3-T05/pose1_20261022_r01` （4.6 MB）
- `tmp/3/S3-T05/frame_export_20261022_r01` （3.5 MB）
- `tmp/3/S3-T05/frame_gray_20261022_r01` （3.3 MB）
- `tmp/3/S3-T05/bars_20261022_r01` （2.6 MB）
- `tmp/3/S3-T05/t05_methodology_baseline_20261021_r01` （0.5 MB）
- `tmp/3/S3-T05/t05_bounded_build_20261021_r01` （0.2 MB）
- `tmp/s3r06/t04_app_diag_patch_scratch_v4` （0.2 MB）
- `tmp/s3r06/t04_app_diag_patch_scratch_v3` （0.2 MB）
- `tmp/s3r06/t04_app_diag_patch_scratch_v2` （0.2 MB）
- `tmp/s3r06/t04_app_diag_patch_scratch` （0.2 MB）
- `tmp/s3r06/t04_ila_20261020_r01` （0.0 MB）
- `tmp/3/S3-T05/t05_methodology_baseline_control_20261021_r01` （0.0 MB）
- `tmp/3/S3-T05/dualmsb_dump_20261022_r01` （0.0 MB）
- `tmp/3/S3-T05/gray_dump_20261021_r01` （0.0 MB）
- `tmp/3/S3-T05/stdluma_verify_20261022_r01` （0.0 MB）
- `tmp/3/S3-T05/v9read_dump_20261021_r01` （0.0 MB）
- `tmp/3/S3-T05/codex_dumpmock_20261021_r01` （0.0 MB）
- `tmp/3/S3-T05/t05_dump_retest_20261021_r02` （0.0 MB）

## 安全闸门

- 无 Vivado/xsdb/xsim 运行：是
- index.lock：无
- 冻结哈希任一不符即拒绝执行 ✓
- 越界路径（report/、主仓等）即拒绝执行 ✓

## 限制

- 未清理主仓与其它阶段缓存（无授权）；留在 `tmp/` 的冻结 run 目录未迁出。
