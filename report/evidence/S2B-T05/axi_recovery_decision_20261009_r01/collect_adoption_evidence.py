"""只读核对本次方案批准的文档、历史绑定和差异，保存被审字节快照。"""

from pathlib import Path
import hashlib
import json
import platform
import subprocess
import time


def sha256(data):
    """计算原始字节摘要，不进行换行转换。"""
    return hashlib.sha256(data).hexdigest()


def main():
    """只生成当前批准记录的证据，不执行实现、仿真或实物操作。"""
    started = time.monotonic()
    run = Path(__file__).resolve().parent
    root = run.parents[3]
    assert (root / 'AGENTS.md').is_file()
    assert run.relative_to(root).as_posix() == 'report/evidence/S2B-T05/axi_recovery_decision_20261009_r01'
    baseline = '5ae71a74bd08aabf2bde57a849990b3ad82200ba'
    commands = []

    def git(*args):
        """记录真实只读命令和退出码；任何失败立即中止。"""
        argv = ['git', *args]
        result = subprocess.run(argv, cwd=root, capture_output=True)
        commands.append({'argv': argv, 'exit_code': result.returncode})
        assert result.returncode == 0, result.stderr.decode('utf-8', errors='replace')
        return result.stdout

    assert git('rev-parse', 'HEAD').decode().strip() == baseline
    names = {
        'docs/obsidian-project/02-方案设计/系统设计.md': ('a7ba351263cc62da3b53d1b45165e7f15597ee43690b4a52f1e197dae1d16431', 'approved_system_design_snapshot.md'),
        '.codex/STATE.md': ('7ed5874e1115b93ebbc9f7d04eadbeb63be88f9fa9a10cc6e4990585a7f03932', 'approved_STATE_snapshot.md'),
        '.gitattributes': ('1a3a4e567e4311a47bcae955c133649ae256569013852ed9d5228edc32266fa7', 'approved_attributes_snapshot.txt'),
    }
    bound = {}
    for name, (expected, snapshot) in names.items():
        path = root / name
        assert path.is_file(), name
        data = path.read_bytes()
        assert sha256(data) == expected, name
        bound[name] = {'sha256': expected, 'bytes': len(data), 'snapshot': snapshot}

    before = (run / 'prior_candidate_snapshot.md').read_text(encoding='utf-8')
    after = (root / 'docs/obsidian-project/02-方案设计/系统设计.md').read_text(encoding='utf-8')
    old_header = '### 阶段2B物理异常恢复候选（待Wong决定，未冻结）'
    new_header = '### 阶段2B物理异常恢复原则（Wong已批准采用）'
    suffix = '## 模型和数据验证'
    assert before.split(old_header)[0] == after.split(new_header)[0]
    assert before.split(suffix, 1)[1] == after.split(suffix, 1)[1]
    section = after.split(new_header, 1)[1].split(suffix, 1)[0]
    rows = [line for line in section.splitlines() if line.startswith('| ')][1:]
    assert len(rows) == 7
    old_state = (run / 'prior_STATE_git_snapshot.md').read_text(encoding='utf-8').splitlines()
    assert git('show', baseline + ':.codex/STATE.md') == (run / 'prior_STATE_git_snapshot.md').read_bytes()
    new_state = (root / '.codex/STATE.md').read_text(encoding='utf-8').splitlines()
    assert len(old_state) == len(new_state) == 48
    changed = [i for i, (a, b) in enumerate(zip(old_state, new_state), 1) if a != b]
    assert changed == [45, 48]
    approval = json.loads((run / 'user_approval.json').read_text(encoding='utf-8'))
    assert approval['authority']['quote'] == '可以采用这个方案'
    assert approval['proposal_id'] == 'S2B-AXI-RECOVERY-20261008'
    assert approval['decision_version'] == 's2b-axi-recovery-principles/1.0.0'
    assert approval['decision_version'] in section
    assert '可以采用这个方案' in section and '2026-10-09' in section

    prior_path = root / 'report/evidence/S2B-T05/axi_abort_contract_20261008_r01/delivery_manifest.json'
    assert prior_path.is_file()
    assert sha256(prior_path.read_bytes()) == '7e476b21b0dbcbc8d80317b9c7fb9c81f88ef8083f18733dfec024b51ce45985'
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    historical = []
    for item in [*prior['files'], *prior['interfaces']]:
        path = root / item['path']
        assert path.is_file() and sha256(path.read_bytes()) == item['sha256'], item['path']
        historical.append({'path': item['path'], 'sha256': item['sha256']})
    assert (run / 'prior_candidate_snapshot.md').read_bytes() == (root / prior['files'][2]['path']).read_bytes()
    tracked_changed = set(git('diff', '--name-only', '-z').decode('utf-8').split('\0')) - {''}
    assert tracked_changed == set(names)
    git('diff', '--check', '--', *names)
    diff = git('diff', '--', *names)
    assert not git('diff', '--cached', '--name-only')
    for name, (_, snapshot) in names.items():
        destination = run / snapshot
        assert not destination.exists(), snapshot
        destination.write_bytes((root / name).read_bytes())
    destination = run / 'source_diff.patch'
    assert not destination.exists()
    destination.write_bytes(diff)
    result = {
        'status': 'PASS_DOCUMENT_ADOPTION_BINDINGS',
        'source_commit': baseline,
        'proposal_id': approval['proposal_id'],
        'decision_version': approval['decision_version'],
        'source_files': bound,
        'historical_bindings_unchanged': historical,
        'recovery_rows': len(rows),
        'STATE_lines': len(new_state),
        'STATE_changed_lines': changed,
        'outside_recovery_section': 'UNCHANGED',
        'commands': commands,
        'tool_versions': {'Python': platform.python_version(), 'Git': git('--version').decode().strip()},
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'execution_count': 1,
        'peak_memory': '未测',
        'limits': ['仅文档批准与绑定核验，不是AXI仿真。', '未实现RTL/驱动，未执行实板操作，阶段2B G0/G3/G4/G5未通过。'],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
