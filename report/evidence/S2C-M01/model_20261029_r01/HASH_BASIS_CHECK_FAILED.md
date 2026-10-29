# r01 manifest 哈希基座校验失败原始输出

命令：

```text
python -B D:\FPGA_Competition\verification\check_manifest_hash_basis.py --repo D:\FPGA_Competition\w2c --paths report/evidence/S2C-M01/model_20261029_r01/manifest.json --paths report/evidence/S2C-M01/model_20261029_r02/manifest.json --mode declared-only --json
```

真实退出码：`1`。检查发现 r01 manifest 中 `profile.json` 的SHA转录错误；保留原 r01 manifest 字节不变。r02将保存更正说明，并只对r02有效manifest重新运行门禁。

校验器原始JSON输出：

```json
{
  "repo": "D:\\FPGA_Competition\\w2c",
  "commit": null,
  "mode": "declared-only",
  "manifests_seen": 2,
  "manifests_basis_errors": false,
  "entries_checked": 8,
  "mismatched": 1,
  "entries_skipped_undeclared": 0,
  "manifests_skipped_no_basis": 0,
  "verdict": "FAIL",
  "problems": [
    {
      "manifest": "report\\evidence\\S2C-M01\\model_20261029_r01\\manifest.json",
      "index": 1,
      "path": "D:/wb-out-r3/task_l0/profile.json",
      "basis": "worktree_disk",
      "declared": "1318675585a618be650629efb6c83b125c5befb5dbfc691fc60759eafea00e73",
      "actual": "1318675585a618be650629efb6c83b125c5befb5dbfc691fc60759efaea00e73",
      "problem": "hash_mismatch"
    }
  ]
}
```
