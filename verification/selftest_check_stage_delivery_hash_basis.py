#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_stage_delivery 内联 hash_basis 支持的自测（导入式，不依赖 CLI）。"""
import sys

sys.path.insert(0, r'D:\FPGA_Competition\verification')
import check_stage_delivery as c  # noqa: E402

fails = []


def check(name, cond):
    print(('PASS' if cond else 'FAIL'), name)
    if not cond:
        fails.append(name)


# 1) 字段白名单：内联 hash_basis 不再被判"未知字段"
errs = []
c._required_keys({'hash_basis': 'commit_blob', 'hash_basis_commit': 'a' * 40},
                 set(), c.TOP_LEVEL_FIELDS, '清单', errs)
check('manifest-inline-basis-allowed', errs == [])

errs = []
c._required_keys({'path': 'x', 'sha256': 'a' * 64, 'role': 'source', 'hash_basis': 'commit_blob'},
                 {'path', 'sha256', 'role'}, c.FILE_FIELDS, 'files[0]', errs)
check('file-inline-basis-allowed', errs == [])

# 2) 取值校验
errs = []
c._valid_hash_basis({'hash_basis': 'commit_blob'}, 'L', errs, allow_commit_field=True)
check('valid-commit_blob', errs == [])

errs = []
c._valid_hash_basis({'hash_basis': 'worktree_disk'}, 'L', errs, allow_commit_field=True)
check('valid-worktree_disk', errs == [])

errs = []
c._valid_hash_basis({'hash_basis': 'disk'}, 'L', errs, allow_commit_field=True)
check('invalid-basis-rejected', len(errs) == 1)

errs = []
c._valid_hash_basis({'hash_basis_commit': 'HEAD'}, 'L', errs, allow_commit_field=True)
check('symbolic-HEAD-rejected', len(errs) == 1)

errs = []
c._valid_hash_basis({'hash_basis_commit': 'A' * 40}, 'L', errs, allow_commit_field=True)
check('uppercase-sha-rejected', len(errs) == 1)

errs = []
c._valid_hash_basis({'hash_basis_commit': 'a' * 40}, 'L', errs, allow_commit_field=True)
check('good-sha-accepted', errs == [])

# 3) 未声明基座仍合法（legacy 兼容）
errs = []
c._valid_hash_basis({}, 'L', errs, allow_commit_field=True)
check('absent-basis-compatible', errs == [])

print()
print('SELFTEST_PASS' if not fails else f'SELFTEST_FAIL: {fails}')
sys.exit(0 if not fails else 1)