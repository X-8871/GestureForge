// 只读核验脚本（6 项）：2026-10-20 DSH 会话压缩锁（compaction/start 未闭合）事故与修复。
// 用法: node verify_incident.mjs <out.json> [session.v4.jsonl.zstd]
// 安全: 全部只读；不改写任何日志或配置；不伪造 compaction/end。
import { readFileSync, writeFileSync, statSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import zlib from 'node:zlib';

const outPath = process.argv[2];
const logPath =
  process.argv[3] ??
  'C:\\Users\\22061\\.dsh\\sessions\\--D-FPGA_Competition--\\session-f067ad85-4434-4f6a-bc01-d6c43068a0c5\\session.v4.jsonl.zstd';
const pluginIndex = 'C:\\Users\\22061\\.dsh\\profiles\\desktop\\node_modules\\dsh-batch-tool-calls\\lib\\index.js';
const patchPath = 'C:\\Users\\22061\\.dsh\\profiles\\desktop\\cordis.patch.yml';
const backupPath = 'C:\\Users\\22061\\.dsh\\profiles\\desktop\\cordis.patch.yml.bak-20261020-batch-fix';
const effectivePath = 'C:\\Users\\22061\\.dsh\\profiles\\desktop\\cordis.yml';

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const readText = (p) => readFileSync(p, 'utf8');
const linesOf = (p) => readText(p).split(/\r?\n/);
const MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd]);

/** 按 zstd 魔数偏移逐帧解码（帧间可能存在 4 字节非帧字段，故不能用连续流解码） */
function decodeSession(path) {
  const raw = readFileSync(path);
  const offsets = [];
  let i = 0;
  while ((i = raw.indexOf(MAGIC, i)) !== -1) {
    offsets.push(i);
    i += 4;
  }
  const parts = [];
  const failed = [];
  for (let k = 0; k < offsets.length; k += 1) {
    const end = k + 1 < offsets.length ? offsets[k + 1] : raw.length;
    try {
      parts.push(zlib.zstdDecompressSync(raw.subarray(offsets[k], end)));
    } catch (err) {
      failed.push({ frame: k, offset: offsets[k], error: String(err && err.message) });
    }
  }
  const text = Buffer.concat(parts).toString('utf8');
  const events = [];
  const parseErrors = [];
  for (const [idx, line] of text.split('\n').entries()) {
    if (line.trim() === '') continue;
    try {
      events.push(JSON.parse(line));
    } catch (err) {
      parseErrors.push({ line: idx, error: String(err && err.message) });
    }
  }
  return { raw, offsets, failed, events, parseErrors };
}

const session = decodeSession(logPath);
const seqs = session.events.map((e) => e.seq).filter((v) => typeof v === 'number');
const seqDup = seqs.filter((v, idx) => seqs.indexOf(v) !== idx);
const compactionStart = session.events.filter((e) => e.type === 'compaction/start');
const compactionEnd = session.events.filter((e) => e.type === 'compaction/end');
const tail = session.events.slice(-3);

const kindCounts = {};
for (const e of session.events) {
  const nested = e.data && typeof e.data === 'object' ? e.data.source : undefined;
  const kind = nested && typeof nested === 'object' ? String(nested.kind ?? '<none>') : e.source ? String(e.source.kind ?? '<none>') : '<absent>';
  kindCounts[kind] = (kindCounts[kind] ?? 0) + 1;
}

// ---- 6 项核验 ----
const pluginLines = linesOf(pluginIndex);
const patchLines = linesOf(patchPath);
const effectiveLines = linesOf(effectivePath);
const checks = [];

const gateLine = pluginLines.findIndex((l) => l.includes('const wantsReassert = cfg.reassertAfterCompaction'));
const sourceKindLine = pluginLines.findIndex((l) => l.includes("kind: 'plugin'") && l.includes('PLUGIN_SOURCE'));
checks.push({
  id: 'C1',
  name: '插件门控与来源格式仍在源码中（根因可复核）',
  pass: gateLine >= 0 && sourceKindLine >= 0,
  detail: {
    gate_line_number: gateLine + 1,
    gate_line_text: gateLine >= 0 ? pluginLines[gateLine].trim() : null,
    source_kind_line_number: sourceKindLine + 1,
    source_kind_line_text: sourceKindLine >= 0 ? pluginLines[sourceKindLine].trim() : null,
    plugin_index_sha256: sha256(readFileSync(pluginIndex)),
  },
});

const patchFlagLine = patchLines.findIndex((l) => l.includes('reassertAfterCompaction: false'));
const patchIdLine = patchLines.findIndex((l) => l.trim() === '- id: batch-tool-calls');
checks.push({
  id: 'C2',
  name: 'profile 覆盖含 batch-tool-calls 且 reassertAfterCompaction:false',
  pass: patchFlagLine >= 0 && patchIdLine >= 0,
  detail: {
    patch_path: patchPath,
    id_line_number: patchIdLine + 1,
    flag_line_number: patchFlagLine + 1,
    patch_sha256: sha256(readFileSync(patchPath)),
    patch_mtime: statSync(patchPath).mtime.toISOString(),
  },
});

const effFlagLine = effectiveLines.findIndex((l) => l.includes('reassertAfterCompaction: false'));
const effIdLine = effectiveLines.findIndex((l) => l.trim() === '- id: batch-tool-calls');
checks.push({
  id: 'C3',
  name: '生效配置 cordis.yml 已带同一取值（说明覆盖已应用/热重载）',
  pass: effFlagLine >= 0 && effIdLine >= 0,
  detail: {
    effective_path: effectivePath,
    id_line_number: effIdLine + 1,
    flag_line_number: effFlagLine + 1,
    effective_sha256: sha256(readFileSync(effectivePath)),
    effective_mtime: statSync(effectivePath).mtime.toISOString(),
  },
});

let diffStats = null;
if (existsSync(backupPath)) {
  const a = linesOf(backupPath);
  const b = patchLines;
  const added = b.filter((l) => !a.includes(l)).length;
  const removed = a.filter((l) => !b.includes(l)).length;
  diffStats = {
    backup_path: backupPath,
    backup_sha256: sha256(readFileSync(backupPath)),
    backup_mtime: statSync(backupPath).mtime.toISOString(),
    added_lines: added,
    removed_lines: removed,
    backup_line_count: a.length,
    current_line_count: b.length,
  };
}
checks.push({
  id: 'C4',
  name: '存在修复前备份，且现行 patch 相对备份为纯新增（无其它配置漂移）',
  pass: diffStats !== null && diffStats.removed_lines === 0 && diffStats.added_lines > 0,
  detail: diffStats,
});

const lastSeq = seqs.length ? Math.max(...seqs) : null;
const lastEvent = session.events[session.events.length - 1];
const mtime = statSync(logPath).mtime.toISOString();
checks.push({
  id: 'C5',
  name: '卡死会话日志：末事件为未闭合 compaction/start，且无 compaction/end',
  pass:
    compactionEnd.length === 0 &&
    compactionStart.length > 0 &&
    lastEvent &&
    lastEvent.type === 'compaction/start' &&
    tail.length >= 2 &&
    tail[tail.length - 2].type === 'step/end',
  detail: {
    log_path: logPath,
    log_bytes: session.raw.length,
    log_sha256: sha256(session.raw),
    log_mtime: mtime,
    tail_events: tail.map((e) => ({ seq: e.seq ?? null, type: e.type ?? null, time: e.time ?? null })),
    compaction_start_count: compactionStart.length,
    compaction_end_count: compactionEnd.length,
    last_compaction_start_seq: compactionStart.length ? compactionStart[compactionStart.length - 1].seq : null,
    last_compaction_start_data: compactionStart.length ? compactionStart[compactionStart.length - 1].data ?? null : null,
  },
});

checks.push({
  id: 'C6',
  name: '魔数分帧可完整解码，事件数与 seq 区间可复核',
  pass:
    session.failed.length === 0 &&
    session.parseErrors.length === 0 &&
    session.events.length > 0 &&
    seqs.length > 0,
  detail: {
    frames_by_magic: session.offsets.length,
    frames_failed: session.failed.length,
    decoded_events: session.events.length,
    parse_errors: session.parseErrors.length,
    seq_min: seqs.length ? Math.min(...seqs) : null,
    seq_max: lastSeq,
    seq_values: seqs.length,
    duplicate_seq_count: seqDup.length,
    event_source_kind_counts: kindCounts,
  },
});

const result = {
  task: 'CTRL-HARNESS / session_compaction_lock_20261020_r01',
  verified_at_utc8: new Date().toISOString(),
  session_id: 'session-f067ad85-4434-4f6a-bc01-d6c43068a0c5',
  checks_total: checks.length,
  checks_passed: checks.filter((c) => c.pass).length,
  checks,
  measurements: {
    decoded_frames_by_magic: session.offsets.length,
    decoded_events: session.events.length,
    seq_min: seqs.length ? Math.min(...seqs) : null,
    seq_max: lastSeq,
    compaction_end_count: compactionEnd.length,
  },
  limits: [
    '本脚本只做静态/只读核验：不解锁、不修复、不重启、不写回任何日志或配置。',
    '帧间存在 4 字节非帧字段，故连续 zstd 流解码（zstdDecompressSync 整文件或 createZstdDecompress）会在首帧后失败；必须按魔数偏移逐帧解码。',
    '通过本脚本不代表新会话不会再触发 v4 source 报错；该结论需以新会话实际运行为准。',
  ],
};

writeFileSync(outPath, JSON.stringify(result, null, 2) + '\n');
process.stdout.write(
  JSON.stringify(
    {
      checks_passed: result.checks_passed,
      checks_total: result.checks_total,
      per_check: checks.map((c) => ({ id: c.id, pass: c.pass, name: c.name })),
      measurements: result.measurements,
      out: outPath,
    },
    null,
    2,
  ) + '\n',
);