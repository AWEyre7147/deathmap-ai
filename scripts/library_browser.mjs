/** Browser adapter for institutional article metadata. Login and CAPTCHA handling
 * remain user-operated. Bodies exist in memory only; experimental files and
 * Oncotarget are blocked. Existing platform allowlists supply routing lessons.
 */
import {deliveryPlatform,collectionFileAddress,doiProxyEntry} from './library_delivery.mjs';
import {authenticationExpired,libraryMenuDestination,requestPacer} from './library_access.mjs';
import {safeAddress} from './library_access.mjs';
import {cooldown,mergeContent} from './library_run_state.mjs';
import {createHash} from 'node:crypto';
import {chooseService,deliveryEntry,accessDestination,connectionFailure,routingFallback} from './library_routes.mjs';
export {chooseService} from './library_routes.mjs';

/** Keep a reusable public article address without transient authentication data. */
export function publicRoute(address){
 const u=new URL(address);const clean=new URL(u.origin+u.pathname);
 for(const key of ['id','doi']){const value=u.searchParams.get(key);if(value&&/^10\.\d{4,9}\/\S+$/.test(value))clean.searchParams.set(key,value);}
 return clean.href;
}

/** Match actual hosts, including the observed FASEB Wiley journal subdomain. */
export function platformFor(address){
 try{
  const u=new URL(address);
  if(u.protocol!=='https:'||u.username||u.password)return null;
  return deliveryPlatform(address)??((u.hostname.endsWith('.onlinelibrary.wiley.com')||/^[a-z0-9-]+-onlinelibrary-wiley-com\.proxy\.lib\.ohio-state\.edu$/.test(u.hostname))?'Wiley':null);
 }catch{return null;}
}

/** Block file requests, insecure URLs and the separately deferred publisher. */
export function blockedAddress(address){
 try{const u=new URL(address);return u.protocol!=='https:'||Boolean(u.username||u.password)||/oncotarget(?:\.com|-com\.proxy)/i.test(u.hostname)||collectionFileAddress(address);}
 catch{return true;}
}

/** Create a single-session adapter. Callback bridge parses bytes without saving
 * raw article bodies. Readiness has a hard timeout and a quiet response interval.
 */
export async function browserAdapter(context,bridge,{requestIntervalMs=3000,cooldownSeconds=900,settleTimeoutMs=20000,quietMs=2500,maxText=60000}={}){
 const page=await context.newPage(),pace=requestPacer(requestIntervalMs);
 let documents=new Map(),content=new Map(),lastResponse=Date.now(),pending=0,lastHttp=null,rate=null,serviceFailure=null,epoch=0,documentKind='html',observedPII=null;
 await context.route('**/*',route=>blockedAddress(route.request().url())?route.abort():route.continue());
 page.on('download',download=>download.cancel().catch(()=>{}));
 page.on('response',response=>{
  const req=response.request(),u=new URL(response.url());
  if(['linkinghub.elsevier.com','linkinghub-elsevier-com.proxy.lib.ohio-state.edu'].includes(u.hostname)){
   const match=u.pathname.match(/^\/retrieve\/pii\/(S[A-Za-z0-9]+)$/);if(match)observedPII=match[1];
  }
  if(req.resourceType()==='document'&&response.frame()===page.mainFrame()){
   lastHttp=response.status();lastResponse=Date.now();
   documentKind=/xml/i.test(response.headers()['content-type']??'')?'xml':'html';
   if(response.status()===429)rate=response.allHeaders().then(h=>cooldown(h,platformFor(response.url())??u.hostname,Date.now(),cooldownSeconds));
   if(response.status()>=500)serviceFailure=response.allHeaders().then(h=>({outcome:'service_unavailable',http:response.status(),...(h['retry-after']?{cooldown:cooldown(h,platformFor(response.url())??u.hostname,Date.now(),cooldownSeconds)}:{})}));
  }
  if(!platformFor(response.url()))return;
  if(req.resourceType()==='document'&&response.status()===200){
   const generation=epoch;
   pending++;
   documents.set(safeAddress(response.url()),response.body().catch(()=>null).finally(()=>{if(generation===epoch){pending--;lastResponse=Date.now();}}));
  }
  // Only browser-observed article content endpoints are eligible. No guessed
  // file/attachment URL is fetched independently of the page's own requests.
  if(platformFor(response.url())==='Elsevier'&&/^\/sdfe\/arp\/pii\/[^/]+\/(?:body|abstract|attachments)$/.test(u.pathname)){
   if(response.status()===429)rate=response.allHeaders().then(h=>cooldown(h,'Elsevier',Date.now(),cooldownSeconds));
   if(response.status()>=500)serviceFailure=response.allHeaders().then(h=>({outcome:'service_unavailable',http:response.status(),...(h['retry-after']?{cooldown:cooldown(h,'Elsevier',Date.now(),cooldownSeconds)}:{})}));
   if(response.status()===200){
    const generation=epoch;pending++;
    content.set(safeAddress(response.url()),response.body().catch(()=>null).finally(()=>{if(generation===epoch){pending--;lastResponse=Date.now();}}));
   }
  }
 });
 async function settle(){
  const started=Date.now();
  while(Date.now()-started<settleTimeoutMs){
   if(rate||serviceFailure||authenticationExpired(page.url())||libraryMenuDestination(page.url())||accessDestination(page.url()))break;
   if(pending===0&&Date.now()-lastResponse>quietMs)break;
   await new Promise(r=>setTimeout(r,250));
  }
 }
 return {page,
  async login(publication,input){
   let navigationError;
   await page.goto(doiProxyEntry(publication.DOI),{waitUntil:'domcontentloaded',timeout:45000}).catch(e=>{navigationError=e;});
   if(connectionFailure(navigationError))return {outcome:'connection_interrupted'};
   await input.question('Complete OSU sign-in in Chrome, then press Enter. Leave access challenges for the assisted pass: ');
   if(rate)return {outcome:'rate_limited',cooldown:await rate};
   if(serviceFailure)return await serviceFailure;
   if(authenticationExpired(page.url()))return {outcome:'authentication_expired'};
   const access=accessDestination(page.url());
   if(['institutional_access_required','external_authentication_required'].includes(access))return {outcome:access,destination:publicRoute(page.url())};
   return null;
  },
  async resolve(publication){
   const url=new URL('https://search.library.osu.edu/view/uresolver/01OHIOLINK_OSU/openurl');
   for(const [key,value] of Object.entries({svc_dat:'CTO',response_type:'xml',url_ver:'Z39.88-2004',rft_id:'info:doi/'+publication.DOI}))url.searchParams.set(key,value);
   await pace();const response=await context.request.get(url.href,{maxRedirects:0,timeout:20000});
   try{
    if(response.status()===429)return {outcome:'rate_limited',cooldown:cooldown(response.headers(),'Alma',Date.now(),cooldownSeconds)};
    if(response.status()>=500)return {outcome:'service_unavailable',http:response.status(),...(response.headers()['retry-after']?{cooldown:cooldown(response.headers(),'Alma',Date.now(),cooldownSeconds)}:{})};
    if(response.status()!==200)return {outcome:'library_route_unavailable',http:response.status()};
    const body=await response.body();if(body.length>2000000)return {outcome:'resolver_size_limit'};
    const services=bridge('alma',[],body),selected=chooseService(services,publication);
    return {...deliveryEntry(publication,selected),resolver_sha256:createHash('sha256').update(body).digest('hex')};
   }finally{await response.dispose();}
  },
  async repairRoute(publication,failed){
   const fallback=routingFallback(publication,failed);
   if(!fallback)return failed;
   let result;
   if(fallback.kind==='wiley_root_bootstrap'){
    // Reuse the actual origin reached by OSU's Wiley entry. Do not construct
    // article paths on an institutional menu or a different hosting platform.
    result=await this.collect(publication,fallback.url,{repair:false});
    if(result.outcome==='retrieved'||!['article_identity_unverified','parser_incomplete'].includes(result.outcome))return {...result,routing_repair:fallback.kind};
    if(platformFor(page.url())!=='Wiley')return {...result,routing_repair:fallback.kind};
    const article=new URL('/doi/full/'+publication.DOI,new URL(page.url()).origin).href;
    result=await this.collect(publication,article,{repair:false});
   }else result=await this.collect(publication,fallback.url,{institutional:fallback.institutional});
   return {...result,routing_repair:fallback.kind,original_delivery:{outcome:failed.outcome,destination:failed.destination}};
  },
  async collect(publication,route,{navigate=true,repair=true,institutional=false}={}){
   if(navigate){
    epoch++;documents=new Map();content=new Map();lastHttp=null;rate=null;serviceFailure=null;pending=0;lastResponse=Date.now();documentKind='html';observedPII=null;
    await pace();
    let navigationError;
    await page.goto(route,{waitUntil:'domcontentloaded',timeout:45000}).catch(e=>{navigationError=e;});
    if(connectionFailure(navigationError))return {outcome:'connection_interrupted',error_class:navigationError.name};
    if(navigationError&&!documents.has(safeAddress(page.url())))return {outcome:'navigation_incomplete',error_class:navigationError.name};
   }
   await settle();
   if(repair&&(/clinicalkey|linkinghub/.test(new URL(page.url()).hostname)||libraryMenuDestination(page.url()))&&observedPII&&!rate&&!serviceFailure&&![401,403].includes(lastHttp)){
    const article='https://www.sciencedirect.com/science/article/pii/'+observedPII;
    return this.collect(publication,'https://login.proxy.lib.ohio-state.edu/login?url='+encodeURIComponent(article),{repair:false});
   }
   const destination=publicRoute(page.url()),platform=platformFor(page.url());
   const base={destination,platform};
   if(rate)return {...base,outcome:'rate_limited',cooldown:await rate};
   if(serviceFailure)return {...base,...await serviceFailure};
   if(authenticationExpired(page.url()))return {...base,outcome:'authentication_expired'};
   if(libraryMenuDestination(page.url()))return {...base,outcome:'library_route_unavailable'};
   const access=accessDestination(page.url());if(access)return {...base,outcome:access};
   if([401,403].includes(lastHttp))return {...base,outcome:'access_block'};
   if(lastHttp>=400)return {...base,outcome:'article_http_error',http:lastHttp};
   if(!platform)return {...base,outcome:'unsupported_platform'};
   // Alma may legitimately land at an unproxied publisher. Carry the intended
   // institutional policy forward instead of treating a public preview as the
   // library's response. Never retry this transition after a block or outage.
   if(institutional&&repair&&navigate&&!new URL(page.url()).hostname.endsWith('.proxy.lib.ohio-state.edu')){
    const entry='https://login.proxy.lib.ohio-state.edu/login?url='+encodeURIComponent(page.url());
    return this.collect(publication,entry,{repair:false});
   }
   let body=documents.has(safeAddress(page.url()))?await documents.get(safeAddress(page.url())):null;
   let responseType=documentKind;
   if(!body){
    // A manually loaded page may predate the response listener. Replay only its
    // observed article destination; no automatic redirect or auth-page parsing.
    await pace();const response=await context.request.get(page.url(),{maxRedirects:0,timeout:30000});
    try{
     if(response.status()===429)return {...base,outcome:'rate_limited',cooldown:cooldown(response.headers(),platform,Date.now(),cooldownSeconds)};
     if(response.status()>=500)return {...base,outcome:'service_unavailable',http:response.status(),...(response.headers()['retry-after']?{cooldown:cooldown(response.headers(),platform,Date.now(),cooldownSeconds)}:{})};
     if(response.status()!==200)return {...base,outcome:'access_block'};
     responseType=/xml/i.test(response.headers()['content-type']??'')?'xml':'html';body=await response.body();
    }finally{await response.dispose();}
   }
   if(!body||body.length>10000000)return {...base,outcome:'response_size_limit'};
   let data=bridge('parse',['--publication',JSON.stringify(publication),'--address',destination,'--kind',responseType],body);
   if(data.doi_verified&&data.article_pii){
    const articleContent=[...content].filter(([url])=>new URL(url).pathname.split('/')[4]===data.article_pii).sort(([a],[b])=>Number(b.endsWith('/body'))-Number(a.endsWith('/body'))).slice(0,2);
    for(const [url,payload] of articleContent){
     if(new URL(url).pathname.split('/')[4]!==data.article_pii)continue;
     const bytes=await payload;if(!bytes||bytes.length>5000000)continue;
     const extra=bridge('parse',['--publication',JSON.stringify(publication),'--address',url,'--kind','json','--article-bound'],bytes);
     data=mergeContent(data,extra,maxText);
    }
   }
   return {...base,outcome:data.outcome,data,response_sha256:createHash('sha256').update(body).digest('hex'),response_bytes:body.length};
  }
 };
}
