// 仅在隔离目录构造读取器反例，不访问实际监督器写入路径。
import * as fs from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const here=path.dirname(new URL(import.meta.url).pathname).replace(/^\/([A-Za-z]:)/,'$1');
const modulePath=process.argv[2];
const {createConsumer}=await import(pathToFileURL(modulePath));
const binding={pid:5832,create_time:1791766374.8010526,exe:'owned.exe',cwd:'owned',cmdline:['owned.exe'],ppid:13724};
const guard={pid:24184,create_time:1791767427.2851894,exe:'python.exe',cwd:'owned',cmdline:['guard.py']};
const cases=[['good',{}],['missing_alerts',{delete:'alerts'}],['missing_uncertain',{delete:'uncertain'}],['wrong_alerts_type',{alerts:{}}],['wrong_uncertain_type',{uncertain:0}],['has_alert',{alerts:['alert']}],['has_uncertain',{uncertain:['unknown']}],['not_closed',{closed:false}],['terminal',{terminal:true}],['root_identity_mismatch',{root_bad:true}],['guard_identity_mismatch',{guard_bad:true}],['stale',{stale:true}]];
const results=[];
for (const [name,change] of cases) {
  const root=path.join(here,'fixture_'+name),sup=path.join(root,'supervision');
  await fs.mkdir(path.join(sup,'guard'),{recursive:true});
  const sample={members:[structuredClone(binding)],alerts:[],uncertain:[],collection_observation:{closed:true}};
  if(change.delete) delete sample[change.delete];
  if('alerts' in change) sample.alerts=change.alerts;
  if('uncertain' in change) sample.uncertain=change.uncertain;
  if('closed' in change) sample.collection_observation.closed=change.closed;
  if(change.root_bad) sample.members[0].pid++;
  const live=structuredClone(guard);if(change.guard_bad) live.pid++;
  const journal=[{kind:'READY',guard_identity:guard},{kind:'LIVE',identity:live}];
  if(change.terminal)journal.push({kind:'TERMINAL'});
  const jp=path.join(sup,'supervision.jsonl'),sp=path.join(sup,'guard','samples.jsonl');
  await fs.writeFile(jp,journal.map(r=>JSON.stringify(r)+'\n').join(''),{flag:'wx'});
  await fs.writeFile(sp,JSON.stringify(sample)+'\n',{flag:'wx'});
  if(change.stale){await fs.utimes(jp,new Date(0),new Date(0));await fs.utimes(sp,new Date(0),new Date(0));}
  const actual=await createConsumer(root,sup,binding)();
  results.push({name,expected:name==='good'?'CONSUMED_LIVE_READY':'BLOCKED_RUNTIME_MONITOR',actual:actual.status});
}
const result={results,pass:results.every(r=>r.expected===r.actual)};
await fs.writeFile(path.join(here,'consumer_cases.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
