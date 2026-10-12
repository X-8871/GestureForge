// 读取本次监督原件；不停止进程，不替代守卫的现时身份核验。
import * as fs from 'node:fs/promises';
import { createHash } from 'node:crypto';

export function createConsumer(root, supervision, binding) {
  let index = 0;
  const sha = data => createHash('sha256').update(data).digest('hex');
  const complete = raw => {
    const text = raw.toString('utf8');
    return text.slice(0, text.lastIndexOf('\n') + 1).split('\n')
      .filter(Boolean).map(line => JSON.parse(line));
  };
  const same = (left, right, keys) => left && right && keys.every(key =>
    JSON.stringify(left[key]) === JSON.stringify(right[key]));
  return async function consume() {
    const at = Date.now();
    let row;
    try {
      const journalPath = supervision + '/supervision.jsonl';
      const samplesPath = supervision + '/guard/samples.jsonl';
      const journalRaw = await fs.readFile(journalPath);
      const samplesRaw = await fs.readFile(samplesPath);
      const journal = complete(journalRaw), samples = complete(samplesRaw);
      const ready = journal.find(item => item.kind === 'READY');
      const terminal = journal.find(item => item.kind === 'TERMINAL');
      const last = journal.at(-1), sample = samples.at(-1);
      const journalStat = await fs.stat(journalPath), sampleStat = await fs.stat(samplesPath);
      const fresh = at - journalStat.mtimeMs <= 10000 && at - sampleStat.mtimeMs <= 10000;
      const guardMatch = last?.kind === 'LIVE' && same(last.identity, ready?.guard_identity,
        ['pid', 'create_time', 'exe', 'cwd', 'cmdline']);
      const rootMatch = same(sample?.members?.[0], binding,
        ['pid', 'create_time', 'exe', 'cwd', 'cmdline', 'ppid']);
      const good = Boolean(ready && !terminal && guardMatch && rootMatch && fresh &&
        Array.isArray(sample?.alerts) && sample.alerts.length === 0 &&
        Array.isArray(sample?.uncertain) && sample.uncertain.length === 0 &&
        sample?.collection_observation?.closed === true);
      row = {
        index: index++, at_utc8: new Date(at + 8 * 3600000).toISOString().replace('Z', '+08:00'),
        status: good ? 'CONSUMED_LIVE_READY' : 'BLOCKED_RUNTIME_MONITOR',
        supervision_bytes: journalRaw.length, supervision_sha256: sha(journalRaw),
        samples_bytes: samplesRaw.length, samples_sha256: sha(samplesRaw),
        last_kind: last?.kind ?? null, fresh, guard_match: guardMatch, root_match: rootMatch,
        guard_identity: guardMatch ? last.identity : null,
        sample_index: sample?.index ?? null, sample_at: sample?.sample_ended_at_utc8 ?? null,
        tree_rss_bytes: sample?.tree_rss_bytes ?? null,
        available_ram_bytes: sample?.available_ram_bytes ?? null,
        c_disk_free_bytes: sample?.c_disk_free_bytes ?? null,
        alerts: sample?.alerts ?? null, uncertain: sample?.uncertain ?? null,
        terminal: terminal ?? null,
      };
    } catch (error) {
      row = { index: index++, at_utc8: new Date(at + 8 * 3600000).toISOString().replace('Z', '+08:00'),
        status: 'BLOCKED_RUNTIME_MONITOR', read_error: String(error) };
    }
    await fs.appendFile(root + '/root_consumption_r02.jsonl', JSON.stringify(row) + '\n', 'utf8');
    return row;
  };
}
