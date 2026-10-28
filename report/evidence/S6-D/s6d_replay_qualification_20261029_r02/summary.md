# S6-D replay-only资格核验

- 判定：**BLOCKED**；阶段6核心：**NOT_RUN**。
- 当前阶段6提交：`56004d3a766e99dd8aef4203bba418865556eef0`；核心SHA-256：`b75948f504fbf732958b16b14bb892de1865bd4defa97dc704bbb8dbf64ad9bc`。
- 阶段4冻结：`s4-shared-io/1.3.0 r07`，仅 `FROZEN_OFFLINE_ONLY`；记录SHA-256：`012f5ea4b6d21cf54b806ec46799bbff967ff41da24a47a52e09a4e9f019dfbd`。
- 阶段5冻结集：`S5T04-OFFLINE-SCOPE-FROZEN-20261027-R03`；w5 HEAD：`2decd0dc2e2204ee60dceead4c30f091d039081d`。
- NO_HAND：result_time_ns=None、stale=None；资格BLOCKED。
- 阳性帧：state=PRESENT、capture_time_ns=0（FILE_INJECTION哨兵）、stale=None；资格BLOCKED。
- 未构造核心事件、未调用状态机；回放结论不表示实时、板级或G3/G4/G5。
