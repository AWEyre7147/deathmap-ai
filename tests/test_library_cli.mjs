/** A full automatic/resume/export cycle using fake browser/API responses only. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
test('CLI preserves completed rows, refuses an active cooldown, and resumes unfinished work',{timeout:60000},async(t)=>{
 const temp=await fs.mkdtemp(path.join(root,'outputs/library-cli-fixture-'));
 // Remove synthetic checkpoints even when an assertion fails; real run evidence is separate.
 t.after(()=>fs.rm(temp,{recursive:true,force:true}));
 const source=path.join(temp,'input.json'),registry=path.join(temp,'pub-registry.json'),indices=path.join(temp,'indices.json'),run=path.join(temp,'run'),log=path.join(temp,'requests.jsonl');
 await fs.writeFile(source,JSON.stringify([
  {'Publication Index':'PUB-0001',DOI:'10.1234/pass',Title:'Example pass',Journal:'Example'},
  {'Publication Index':'PUB-0002',DOI:'10.1234/rate',Title:'Example limited',Journal:'Example'},
  {'Publication Index':'PUB-0003',DOI:'',Title:'Missing identifier',Journal:'Example'}]));
 await fs.writeFile(registry,'[]');
 const args=[path.join(root,'scripts/library_enrichment.mjs'),'--output-dir',run,'--input',source,'--publication-registry',registry,'--index-registry',indices,
  '--paper-delay-seconds','1','--request-delay-seconds','1','--playwright-module',path.join(root,'tests/fixtures/library_browser_mock.cjs')];
 const call=(extra=[],mode='limited')=>spawnSync(process.execPath,[...args,...extra],{cwd:root,input:'\n',encoding:'utf8',timeout:30000,windowsHide:true,env:{...process.env,LIBRARY_MOCK_LOG:log,LIBRARY_MOCK_MODE:mode}});
 const first=call();assert.equal(first.status,0,first.stderr);
 let state=JSON.parse(await fs.readFile(path.join(run,'state.json'),'utf8'));
 assert.deepEqual(state.attempts.map(a=>a.outcome),['retrieved','rate_limited']);
 const before=await fs.readFile(log,'utf8');
 const blocked=call(['--resume']);assert.equal(blocked.status,0,blocked.stderr);assert.match(blocked.stdout,/Cooldown remains active/);
 assert.equal(await fs.readFile(log,'utf8'),before,'cooldown opened a browser or issued a request');
 // This is a synthetic checkpoint. Move its fake deadline into the past to
 // exercise the next process; never edit a real publisher cooldown this way.
 state.cooldown.not_before_utc=new Date(Date.now()-1000).toISOString();
 await fs.writeFile(path.join(run,'state.json'),JSON.stringify(state));
 const resumed=call(['--resume'],'recovered');assert.equal(resumed.status,0,resumed.stderr);
 state=JSON.parse(await fs.readFile(path.join(run,'state.json'),'utf8'));
 assert.equal(state.attempts.filter(a=>a.publication_index==='PUB-0001').length,1);
 assert.deepEqual(state.attempts.map(a=>a.outcome),['retrieved','rate_limited','retrieved','missing_doi']);
 const exports=await fs.readdir(path.join(run,'exports'));
 const latest=JSON.parse(await fs.readFile(path.join(run,'exports',exports.sort().at(-1),'database.json'),'utf8'));
 assert.equal(latest.rows.Publications.length,3);assert.equal(latest.rows['Article Context'].length,2);
 assert.ok(latest.rows['Article Context'].every(r=>r['Content Type']===''));
 const logBeforeExport=await fs.readFile(log,'utf8');
 const exported=call(['--export-only']);assert.equal(exported.status,0,exported.stderr);
 assert.equal(await fs.readFile(log,'utf8'),logBeforeExport,'offline export issued requests');
 const scoped=call(['--resume','--retry-routing','--only','PUB-0001']);assert.equal(scoped.status,0,scoped.stderr);
 assert.equal(await fs.readFile(log,'utf8'),logBeforeExport,'scoped repair repeated a successful publication');
 const invalid=call(['--resume','--only','PUB-9999']);assert.equal(invalid.status,1);assert.match(invalid.stderr,/unknown publication/);
});
test('a disconnected service stops the CLI before the next publication',{timeout:30000},async(t)=>{
 const temp=await fs.mkdtemp(path.join(root,'outputs/library-disconnect-fixture-'));
 // Remove synthetic checkpoints even when an assertion fails; real run evidence is separate.
 t.after(()=>fs.rm(temp,{recursive:true,force:true}));
 const source=path.join(temp,'input.json'),registry=path.join(temp,'registry.json'),run=path.join(temp,'run');
 await fs.writeFile(source,JSON.stringify([
  {'Publication Index':'PUB-0001',DOI:'10.1234/pass',Title:'Example',Journal:'Example'},
  {'Publication Index':'PUB-0002',DOI:'10.1234/rate',Title:'Example',Journal:'Example'},
  {'Publication Index':'PUB-0003',DOI:'10.1234/later',Title:'Example',Journal:'Example'}]));
 await fs.writeFile(registry,'[]');
 const result=spawnSync(process.execPath,[path.join(root,'scripts/library_enrichment.mjs'),'--output-dir',run,'--input',source,
  '--publication-registry',registry,'--index-registry',path.join(temp,'ids.json'),'--paper-delay-seconds','1','--request-delay-seconds','1',
  '--playwright-module',path.join(root,'tests/fixtures/library_browser_mock.cjs')],
  {cwd:root,input:'\n',encoding:'utf8',timeout:25000,windowsHide:true,env:{...process.env,LIBRARY_MOCK_MODE:'disconnected'}});
 assert.equal(result.status,0,result.stderr);
 const state=JSON.parse(await fs.readFile(path.join(run,'state.json'),'utf8'));
 assert.deepEqual(state.attempts.map(a=>a.outcome),['retrieved','connection_interrupted']);
 assert.ok(!state.attempts.some(a=>a.publication_index==='PUB-0003'));
});
