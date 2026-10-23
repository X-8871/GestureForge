# 证据模板说明（阶段 A 预生成，到货即用）

本目录是**模板**，不是证据；模板中的 `<...>` 必须用真实值替换后才可作为证据使用。

## 到货后实测的落点约定

1. 选一个**新 RunId**（不覆盖任何旧轮次），例如 `t17_color_retest_20261023_r01`。
2. 硬件门禁文件：
   - `report/evidence/S3-T17/hw_authorization.json` ← 按 `hw_authorization_template.json` 据实填写
     （`wong_go` 与 `codex_hw_release` 必须同时为 true）；未填写时执行器对 `link`/`baseline`/`bars`
     一律退出 3，**不会动板**。
3. 实测入口：
   ```bash
   bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id <run_id>
   bash scripts/stage3_t17/run_t17_color_retest.sh all --run-id <run_id> --allow-hardware
   ```
   原始抓取落在 `tmp/3/S3-T17/<run_id>/`（缓存，不入库）；判定 JSON 与日志落在
   `report/evidence/S3-T17/<run_id>/`。
4. 打包清单（退出码只接受真实值，未列出的阶段即未执行）：
   ```bash
   python -B scripts/stage3_t17/make_t17_manifest.py \
     --evidence-dir report/evidence/S3-T17/<run_id> --run-id <run_id> \
     --command "bash scripts/stage3_t17/run_t17_color_retest.sh all --run-id <run_id> --allow-hardware" \
     --exit-code preflight=0 --exit-code baseline_capture=<..> --exit-code baseline_judge=<..> \
     --exit-code bars_capture=<..> --exit-code bars_judge=<..> --exit-code restore=<..> \
     --limitation "<逐项>" --not-run "<逐项>"
   ```
5. 判定脚本退出码：`0=通过 / 1=复现旧缺陷 / 2=用法或输入错误 / 3=非典型`；与旧
   `analyze_missing_msb_signature.py`（`0=符合旧缺位签名 / 1=不符合`）**语义相反**，报告中必须注明所用脚本。