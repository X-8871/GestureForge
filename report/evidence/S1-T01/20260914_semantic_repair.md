# S1-T01 复审后语义整改证据（开发侧）

日期：2026-09-14（UTC+8）
固定基线：`f6364bb5dcf6de1d74c30c346fb53e9ac9a89a42`
范围：AUD-S1-T01-008 / AC03 / AC04 语义整改；不代替独立复审签结。

## 数据现状核对

- 实际数据根目录：`D:\FPGA_Data\HaGRIDv2`；消息中给出的 `D:\FPGA\_Data\HaGRIDv2` 不存在。
- HaGRIDv2 官方 `dataset/no_gesture` 的 2164 条 JSON 记录全部有 `bboxes`，没有记录可仅凭官方 `no_gesture` 路径证明为真实无手；目录中另有 2 张未被官方 JSON 引用的 `-checkpoint` 图片，不擅自写入清单。
- Wong 已观察通过的 1～10 号带框候选登记为 `target_gesture`。
- Wong 观察到的 11～15 号为捂脸/遮挡，画面存在手但不属于五类目标，登记为 `non_target_gesture`；不登记为 `no_hand`，不计入无手数量。
- 当前没有开发侧可诚实登记的 5 张真实无手图片；采集要求见 `20260914_no_hand_collection_sheet.md`。在 Wong 提供并逐张确认前，`no_hand=0/5`。

## 本轮实现

- `verification/s1_t01_dataset_check.py` 新增 `--semantic-review` 和人工语义 CSV 校验。
- `no_hand` 只接受语义表中的 `sample_role=no_hand`、`manual_result=confirmed_no_hand`、空 `.txt` 标签、图片 SHA-256 一致、人工复核人和实际 UTC+8 时间；目录名和空标签本身不提供无手语义。
- `non_target_gesture`、`target_gesture` 和未绑定语义的空标签分别统计。
- 语义表的图片/标签使用规范化物理路径绑定，`..`、大小写等别名重复映射会失败；对应回归已加入。
- 新增 `20260914_hagrid_semantic_review.csv`，不覆盖外部正式 `manifest.csv`。

## 实际命令、版本与退出码

工作目录：`D:\FPGA_Competition`
受控解释器：`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
运行版本：CPython `3.12.14`；Pillow `12.3.0`。

| 用途 | 实际命令 | 退出码 | 结果/证据 |
|---|---|---:|---|
| 官方 `no_gesture` 元数据核对 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "import json,pathlib,collections; root=pathlib.Path(r'D:\FPGA_Data\HaGRIDv2\dataset\annotations'); files=list(root.rglob('no_gesture*.json'))+[p for p in root.rglob('*.json') if p.parent.name=='no_gesture']; records=[v for p in files for v in json.loads(p.read_text(encoding='utf-8')).values() if isinstance(v,dict)]; print('files',len(files),'records',len(records),'empty_boxes',sum(not v.get('bboxes') for v in records),'shape_counts',collections.Counter((len(v.get('labels',[])),len(v.get('bboxes',[]))) for v in records))"` | 0 | 实际输出：3 个 JSON、2164 条记录、0 条空 `bboxes`；本条只用于语义筛查，不替代图片人工观察 |
| 新增数据检查器定向回归 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest verification.test_s1_t01_dataset_check -v` | 0 | 11 项通过；包含未提供语义表不计 `no_hand`、语义角色分开统计、语义路径别名重复、PNG/PNM/JPEG 损坏等 |
| 全量 Python 回归 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s verification -p 'test_*.py' -q` | 0 | 21 项通过；日志：`20260914_python_regression.log` |
| Python 编译检查 | `$pyFiles = @(rg --files verification -g '*.py'); & 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile $pyFiles` | 0 | 11 个 Python 文件通过 |
| 语义绑定全量清单检查 | `& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_dataset_check.py --data-root 'D:\FPGA_Data\HaGRIDv2' --manifest 'D:\FPGA_Data\HaGRIDv2\manifest.csv' --semantic-review 'report\evidence\S1-T01\20260914_hagrid_semantic_review.csv' --report 'report\evidence\S1-T01\20260914_hagrid_dataset_check_semantic.json'` | 2 | 19:08:27 启动，20:27:01 写出；约 78 分钟；158675/158675 有效；这是因明确 `no_hand=0` 导致的预期阻断 |

完整命令输出日志：`20260914_hagrid_dataset_check_semantic.log`；现行清洁报告和日志分别为同一结果的机械同步副本：`20260914_hagrid_dataset_check_clean.json`、`20260914_hagrid_dataset_check_clean.log`。

## 全量报告关键统计

| 项目 | train | val | test | 总计 |
|---|---:|---:|---:|---:|
| 有效清单行 | 117998 | 15193 | 25484 | 158675 |
| `no_hand` | 0 | 0 | 0 | 0 |
| `non_target_gesture` | 5 | 0 | 0 | 5 |
| 未分类空标签 | 1460 | 199 | 496 | 2155 |

语义角色计数：`target_gesture=10`、`non_target_gesture=5`、`no_hand=0`。`AC02` 自动检查通过；`AC03` 因真实无手为 0、train/val 均缺无手而退出码为 2；`AC04` 仍为人工抽查待完成/未完全关闭。报告未把未分类空标签写成无手。

## 尚未完成与恢复

- 新增真实无手样本：`0/5`；需要 Wong 按操作单提供至少 5 张真实图片、同名空 `.txt`、来源/许可、split/session/person、SHA-256 和人工复核时间。
- 收到样本后先确认没有同一检查器或训练进程，再把 5 条记录追加到语义表并逐张观察；使用相同检查命令重跑，确认 `no_hand` 分项达到门槛后再生成新报告。
- 当前未启动正式长训、INT8、RTL、板卡烧录或板卡验收；AC01/G0、AC05～AC07、G1、G2、G4 状态不因本轮整改改变。
- 本证据不代替独立复审确认；独立复审仍需核对新提交、哈希和 AC04 定义。
