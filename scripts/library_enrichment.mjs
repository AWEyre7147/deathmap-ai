#!/usr/bin/env node
/** Maintained two-pass library enrichment CLI. Inputs are publications and an
 * approved template. Per-publication checkpoints survive interruption; exports
 * are versioned and cannot overwrite owner-reviewed workbooks. No live work is
 * performed on import, during --prepare-only, or during --export-only.
 */
import fs from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {createInterface} from 'node:readline/promises';
import {createHash} from 'node:crypto';
import {atomicJson} from './library_access.mjs';
import {chromiumFromModule} from './library_access.mjs';
import {binding,eligible,cooling} from './library_run_state.mjs';
import {browserAdapter,blockedAddress,publicRoute} from './library_browser.mjs';
import {connectionFailure} from './library_routes.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const runtime=path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies');
const usage=`Library enrichment
  node scripts/library_enrichment.mjs --output-dir <new run> [--input <publication JSON>]
  node scripts/library_enrichment.mjs --output-dir <run> --resume
  node scripts/library_enrichment.mjs --output-dir <run> --assisted
  node scripts/library_enrichment.mjs --output-dir <run> --export-only
Options: --prepare-only, --limit N, --paper-delay-seconds N (15),
 --request-delay-seconds N (3), --cooldown-seconds N (900), --python <executable>,
 --publication-registry <JSON>, --index-registry <JSON>, --template <xlsx>,
 --export-dir <new directory>, --playwright-module <installed package>,
 --max-context-characters N (60000; fixed for a run), --retry-routing,
 --only PUB-0001,PUB-0002 (selects eligible inputs, never forces completed work).
Cookies, login pages, whole article bodies and experimental files are not saved.`;

/** Parse bounded settings once, rejecting accidental unknown CLI flags. */
export function options(argv){
 const flags=new Set(['--resume','--assisted','--export-only','--prepare-only','--help','--retry-routing']);
 const values=new Set(['--input','--output-dir','--publication-registry','--index-registry','--template','--limit','--paper-delay-seconds','--request-delay-seconds','--cooldown-seconds','--python','--export-dir','--playwright-module','--max-context-characters','--only']);
 const out={};
 for(let i=0;i<argv.length;i++){
  const flag=argv[i];
  if(flags.has(flag))out[flag]=true;
  else if(values.has(flag)&&argv[i+1]&&!argv[i+1].startsWith('--'))out[flag]=argv[++i];
  else throw Error('Unknown or incomplete argument: '+flag);
 }
 for(const [flag,fallback,min,max] of [['--limit',Infinity,1,10000],['--paper-delay-seconds',15,1,3600],['--request-delay-seconds',3,1,300],['--cooldown-seconds',900,60,86400]]){
  const number=out[flag]===undefined?fallback:Number(out[flag]);
  const unlimited=flag==='--limit'&&out[flag]===undefined;
  if(!unlimited&&(!Number.isInteger(number)||number<min||number>max))throw Error('Invalid setting: '+flag);
  out[flag]=number;
 }
 if(out['--max-context-characters']!==undefined){const n=Number(out['--max-context-characters']);if(!Number.isInteger(n)||n<1000||n>240000)throw Error('Invalid text size guard');out['--max-context-characters']=n;}
 return out;
}

/** Launch Python with argument arrays and a known source path, never a shell. */
function bridgeFor(config){
 const cachedPython=path.join(runtime,'python/python.exe');
 const python=config['--python']??process.env.CODEX_PRIMARY_RUNTIME_PYTHON??(existsSync(cachedPython)?cachedPython:'python');
 return (command,args=[],body)=>{
  const parseArgs=command==='parse'?['--max-text',String(config['--max-context-characters']??60000)]:[];
  const child=spawnSync(python,['-X','utf8','-m','deathmap_ai.library_enrichment',command,...args,...parseArgs],{
   input:body,encoding:'utf8',maxBuffer:20000000,windowsHide:true,
   env:{...process.env,PYTHONPATH:[path.join(root,'src'),process.env.PYTHONPATH].filter(Boolean).join(path.delimiter)}});
  if(child.status!==0)throw Error(`Metadata bridge ${command} failed: ${child.stderr?.slice(-1200)??child.error?.name}`);
  return JSON.parse(child.stdout);
 };
}

/** Delay in short chunks so Ctrl-C can stop long configured publication gaps. */
async function pause(ms,stopping){
 const deadline=Date.now()+ms;
 while(!stopping()&&Date.now()<deadline)await new Promise(resolve=>setTimeout(resolve,Math.min(1000,deadline-Date.now())));
}

/** Execute the approved operations. Browser work requires the explicit normal or
 * assisted CLI path; preparation and exporting cannot accidentally invoke it.
 */
export async function main(argv=process.argv.slice(2)){
 const config=options(argv);if(config['--help']){console.log(usage);return;}
 if(!config['--output-dir'])throw Error('Supply --output-dir. Use --help for operations.');
 if(config['--prepare-only']&&(config['--assisted']||config['--export-only']))throw Error('Preparation cannot run an assisted pass or export');
 const output=path.resolve(config['--output-dir']);const bridge=bridgeFor(config);
 const resume=Boolean(config['--resume']||config['--assisted']||config['--export-only']);
 const manifestPath=path.join(output,'manifest.json'),statePath=path.join(output,'state.json');
 let manifest,state;
 const sourceArgs=['--input',path.resolve(config['--input']??path.join(root,'data/orcs/publication-index.json')),
  '--registry',path.resolve(config['--publication-registry']??path.join(root,'data/orcs/enrichment-publication-registry.json')),
  '--template',path.resolve(config['--template']??path.join(root,'data/templates/Library-Enrichment-Template.xlsx'))];
 if(resume){
  manifest=JSON.parse(await fs.readFile(manifestPath,'utf8'));state=JSON.parse(await fs.readFile(statePath,'utf8'));
  if(state.binding!==binding(manifest))throw Error('Saved manifest binding mismatch');
  if(!config['--export-only']){
   const current=bridge('prepare',['--input',path.resolve(config['--input']??manifest.source_path),
    '--registry',path.resolve(config['--publication-registry']??manifest.publication_registry),
    '--template',path.resolve(config['--template']??manifest.template)]);
   current.content_limits={max_context_characters:config['--max-context-characters']??manifest.content_limits.max_context_characters};
   if(binding(current)!==state.binding)throw Error('Input, registry, rules or template changed; use the same inputs or a new run');
  }
 }else{
  manifest=bridge('prepare',sourceArgs);
  manifest.content_limits={max_context_characters:config['--max-context-characters']??60000};
  await fs.mkdir(output,{recursive:false});
  state={schema:'library-run/1',binding:binding(manifest),attempts:[],cooldown:null,assisted_passes:0};
  await atomicJson(manifestPath,manifest);await atomicJson(statePath,state);
 }
 config['--max-context-characters']=manifest.content_limits.max_context_characters;
 // An exclusive lock prevents two collectors from allocating or overwriting
 // the same run. A dead process lock is recoverable, never a live one.
 const lockPath=path.join(output,'run.lock');
 try{const saved=JSON.parse(await fs.readFile(lockPath,'utf8'));let active=true;try{process.kill(saved.pid,0);}catch(e){if(e.code==='ESRCH')active=false;}
  if(active)throw Error('Another process owns this run');await fs.unlink(lockPath);
 }catch(e){if(e.code!=='ENOENT')throw e;}
 const lock=await fs.open(lockPath,'wx');await lock.writeFile(JSON.stringify({pid:process.pid}));
 let browser,input,stopped=false;
 const interrupt=()=>{stopped=true;input?.close();};process.once('SIGINT',interrupt);
 const exportNow=()=>{
  const destination=path.resolve(config['--export-dir']??path.join(output,'exports',new Date().toISOString().replaceAll(':','-')));
  const args=['--run-dir',output,'--output',destination];if(config['--index-registry'])args.push('--index-registry',path.resolve(config['--index-registry']));
  return bridge('export',args);
 };
 try{
  if(resume){state=JSON.parse(await fs.readFile(statePath,'utf8'));if(state.binding!==binding(manifest))throw Error('Run changed before lock acquisition');}
  if(config['--prepare-only']){console.log(`Prepared ${manifest.publications.length} publications. No browser or network requests.`);return;}
  if(config['--export-only']){console.log(JSON.stringify(exportNow(),null,2));return;}
  if(cooling(state)){
   console.log(`Cooldown remains active until ${state.cooldown.not_before_utc}. Progress is saved; no browser opened.`);return;
  }
  const mode=config['--assisted']?'assisted':'automatic';
  let scope=manifest.publications;
  if(config['--only']){
   const ids=config['--only'].split(',');const inputs=new Map(scope.map(p=>[p['Publication Index'],p]));
   if(ids.length!==new Set(ids).size||ids.some(id=>!inputs.has(id)))throw Error('--only contains duplicate or unknown publication indices');
   scope=ids.map(id=>inputs.get(id));
  }
  const chosen=scope.filter(p=>eligible(p,state.attempts,mode,Boolean(config['--retry-routing']))).slice(0,config['--limit']);
  if(!chosen.length){console.log('No publications are eligible for this pass.');console.log(JSON.stringify(exportNow(),null,2));return;}
  const pass=mode==='assisted'?state.assisted_passes+1:0;
  await atomicJson(statePath,state);
  const codePaths=['scripts/library_enrichment.mjs','scripts/library_browser.mjs','scripts/library_routes.mjs','scripts/library_run_state.mjs','src/deathmap_ai/library_content.py','src/deathmap_ai/library_enrichment.py',
   'scripts/library_delivery.mjs','scripts/library_access.mjs','src/deathmap_ai/library_nature.py'];
  const hashes=[];for(const file of codePaths)hashes.push({file,sha256:createHash('sha256').update(await fs.readFile(path.join(root,file))).digest('hex')});
  const execution={started_utc:new Date().toISOString(),node_version:process.version,mode,pass_number:pass,
   retry_routing:Boolean(config['--retry-routing']),routing_policy:'native-publisher/3',selection:config['--only']??'all eligible inputs',
   pacing:{paper_seconds:config['--paper-delay-seconds'],request_seconds:config['--request-delay-seconds'],fallback_cooldown_seconds:config['--cooldown-seconds']},code:hashes};
  const executionPath=path.join(output,`execution-${Date.now()}.json`);
  await atomicJson(executionPath,execution);
  const live=chosen.some(p=>p.DOI&&!/oncotarget/i.test(p.Journal));
  let adapter;
  if(live){
   const cachedModules=path.join(runtime,'node/node_modules');
   const moduleRoot=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES??cachedModules;
   const req=existsSync(moduleRoot)?createRequire(path.join(moduleRoot,'package.json')):createRequire(import.meta.url);
   const chromium=chromiumFromModule(await import(pathToFileURL(req.resolve(config['--playwright-module']??'playwright')).href));
   browser=await chromium.launch({channel:'chrome',headless:false});
   execution.browser_version=browser.version();await atomicJson(executionPath,execution);
   const context=await browser.newContext({acceptDownloads:false});
   adapter=await browserAdapter(context,bridge,{requestIntervalMs:config['--request-delay-seconds']*1000,cooldownSeconds:config['--cooldown-seconds'],maxText:config['--max-context-characters']});
   input=createInterface({input:process.stdin,output:process.stdout});
   const first=chosen.find(p=>p.DOI&&!/oncotarget/i.test(p.Journal));
   const loginOutcome=await adapter.login(first,input);
   if(loginOutcome){
    state.attempts.push({publication_index:first['Publication Index'],mode,pass_number:pass,started_utc:new Date().toISOString(),completed_utc:new Date().toISOString(),...loginOutcome});
    if(loginOutcome.cooldown)state.cooldown=loginOutcome.cooldown;
    if(mode==='assisted')state.assisted_passes=pass;
    await atomicJson(statePath,state);console.log(JSON.stringify(exportNow(),null,2));return;
   }
  }
  let count=0,failures=0;
  for(const publication of chosen){
   if(stopped)break;
   const index=publication['Publication Index'];console.log(`${index}: ${mode} pass`);
   if(count&&adapter)await pause(config['--paper-delay-seconds']*1000,()=>stopped);
   if(stopped)break;
   const attempt={publication_index:index,mode,pass_number:pass,started_utc:new Date().toISOString()};
   let result;
   if(!publication.DOI)result={outcome:'missing_doi'};
   else if(/oncotarget/i.test(publication.Journal))result={outcome:'deferred'};
   else try{
    let route;
    try{route=await adapter.resolve(publication);}catch(e){route={outcome:connectionFailure(e)?'connection_interrupted':'request_error',error_class:e.name};}
    if(route.outcome)result=route;
    else{
     // The route is used in memory; only the service ID and safe destination are
     // persisted. Query parameters can contain institutional session state.
     attempt.service_id=route.service_id;attempt.route_source=route.route_source;attempt.resolver_sha256=route.resolver_sha256;
     const previousCorrection=[...state.attempts].reverse().find(a=>a.publication_index===index&&a.corrected_route)?.corrected_route;
     if(previousCorrection){route.url=previousCorrection;route.institutional=false;attempt.route_source='owner_corrected_route';attempt.corrected_route=previousCorrection;}
     if(blockedAddress(route.url))result={outcome:'deferred'};
     else{
      result=await adapter.collect(publication,route.url,{institutional:route.institutional??false});
      result=await adapter.repairRoute(publication,result);
      if(result.outcome==='authentication_expired'&&!stopped){
       await input.question(`${index}: renew OSU sign-in in Chrome, then press Enter to inspect the loaded page: `);
       result=await adapter.collect(publication,route.url,{navigate:false});
      }
     }
    }
    if(mode==='assisted'&&!['rate_limited','connection_interrupted','service_unavailable'].includes(result.outcome)&&!stopped){
     const choice=(await input.question(`${index}: load the article or solve its challenge. Enter = inspect, s = skip, q = stop, or paste a corrected HTTPS article URL: `)).trim();
     if(choice.toLowerCase()==='q'){stopped=true;break;}
     if(choice.toLowerCase()==='s')result={...result,outcome:'skipped'};
     else if(choice.startsWith('https://')){
      if(blockedAddress(choice))result={outcome:'deferred'};
      else{
       attempt.corrected_route=publicRoute(choice);
       result=await adapter.collect(publication,choice);
       if(!['rate_limited','connection_interrupted','service_unavailable'].includes(result.outcome)){
        await input.question('Let that page finish loading, then press Enter: ');
        result=await adapter.collect(publication,choice,{navigate:false});
       }
      }
     }else if(choice==='')result=await adapter.collect(publication,route.url??'https://doi.org/'+publication.DOI,{navigate:false});
     else result={...result,outcome:'skipped'};
    }
   }catch(e){if(stopped)break;result={outcome:connectionFailure(e)?'connection_interrupted':'request_error',error_class:e.name};}
   if(stopped)break;
   Object.assign(attempt,result,{completed_utc:new Date().toISOString()});
   state.attempts.push(attempt);if(mode==='assisted')state.assisted_passes=pass;if(result.cooldown)state.cooldown=result.cooldown;
   await atomicJson(statePath,state);count++;
   console.log(`${index}: ${result.outcome}. Saved ${state.attempts.length} attempts.`);
   failures=result.outcome==='retrieved'?0:failures+1;
   // Conservatively pause the entire queue on 429: shared institutional limits
   // cannot reliably be distinguished from an individual publisher limit.
   if(['rate_limited','authentication_expired','institutional_access_required','external_authentication_required','connection_interrupted','service_unavailable'].includes(result.outcome)||(mode==='automatic'&&failures>=5))break;
  }
  console.log(JSON.stringify(exportNow(),null,2));
 }finally{
  process.removeListener('SIGINT',interrupt);input?.close();if(browser)await browser.close().catch(()=>{});await lock.close();await fs.unlink(lockPath);
 }
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))main().catch(e=>{console.error(e.message);process.exitCode=1;});
