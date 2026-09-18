# D6 robustness 目录文件增量盘点 R2

状态：**BLOCKED_DIRECTORY_SNAPSHOT_CANNOT_MEET_MINIMUM_COUNTS**。

目录快照：D:/FPGA_Data/HaGRIDv2/dataset；元数据扫描时间（UTC+8）09/18/2026 21:26:44 至 09/18/2026 21:29:01；两次扫描 canonical 哈希一致。
批准 manifest：D:/FPGA_Data/HaGRIDv2/manifest.csv，SHA-256 fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74，57,672,948 bytes，158,680 data rows；158,680 个规范化唯一 image 路径。

## 路径契约与精确比较

以 HaGRIDv2 根解析时，全部 158,680 条 manifest image 路径均对应现存文件。其标准 dataset/ 前缀路径有 158,675 条，和 dataset 子树精确路径交集为 158,675，缺失 0。另 5 条 user_no_hand/... 路径不在 dataset 子树相对路径命名空间内；从 HaGRIDv2 根解析后文件均存在，并由 train.list 引用 3 条、valid.list 引用 2 条。

dataset 子树图像文件共 158,705 个，唯一规范化路径 158,705 个。相对 manifest image 路径集合，子树有 30 条路径未精确匹配（唯一30），但这不等于30个独立内容样本。

5 个 user_no_hand manifest 路径与 dataset 子树文件按 basename 对应；两边文件大小和 LastWriteTimeUtc 相同。完整相对路径不同。没有读取文件内容或比较内容哈希，因此只报告路径名与文件元数据对应，不认定图像内容相同或重复。

train.list SHA-256：4d8e965e7fc3f5d8a9f1ec3613fadb72c50b8463f78feebf863fd26978c8e3fa；valid.list SHA-256：8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c。

## 扩展名分布

| 扩展名 | 文件数 |
|---|---:|
|.jpg|158700|
|.png|5|

## Manifest 外路径类别分布（相对 dataset 子树路径）

| 路径类别 | 路径数 |
|---|---:|
|fist|3|
|no_gesture|7|
|one|4|
|palm|4|
|three|2|
|two_up|5|
|user_no_hand|5|

目标类别额外路径：fist 3、palm 4、one 4、two_up 5、three 2，逐类均远低于至少 100 张。no_gesture 额外路径 7；user_no_hand 子树路径 5，远低于条件桶至少 100 张。路径与文件属性盘点不能认证条件类别、person/session 隔离或内容唯一性。

整体目录 path+size 清单 canonical SHA-256：46642ac0b7343b8a726276dabc850b3221c624a19a3840466496b35866aca16e。子树中未精确匹配 manifest 的 path+size 子清单 SHA-256：b1e848f9f8b1a38da1450daf452b8a3968c93489f609dcd38e851a700e8501e4。序列化为 NFC 规范化、/ 分隔、保留大小写、dataset/ 前缀；每行路径、TAB、无前导零十进制字节数、LF；按整行 Ordinal 升序；UTF-8 无 BOM，尾部 LF。哈希仅绑定路径和大小，不是内容哈希。

## 结论与限制

当前可见目录快照中的五个目标类别分别有 2–5 条额外路径（fist 3、palm 4、one 4、two_up 5、three 2）；no_gesture 额外路径为 7 条，user_no_hand 子树路径为 5 条，均低于 Wong 批准的每类/条件至少 100 张。它们不足以单独形成最低规模 robustness 集；现有目录快照也不能认证任何额外路径为 robustness 样本。

本次只读取路径、扩展名、大小、时间戳及 train/valid.list 路径行；没有读取图片、标签或标注 JSON。multi-hand、occlusion、small-target、non-target、person/session 隔离、图像内容身份及许可证状态均未验证。结论只绑定上述目录快照和批准 manifest，不代表盘点所有原始数据。

图像扩展名范围（大小写不敏感）：.jpg, .jpeg, .png, .bmp, .webp, .tif, .tiff, .gif, .heic, .heif, .avif；其他扩展名未计入。遇到 reparse point 目录不会继续递归。机器报告：20260918_s1_t02_d6_robustness_directory_inventory_r2.json。
