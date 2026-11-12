/** Simulated browser events verify access recovery without a real browser. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {browserAdapter,publicRoute} from '../scripts/library_browser.mjs';
const publication={'Publication Index':'PUB-0001',DOI:'10.1234/test',Title:'Example'};
function fixture(){
 const page=new EventEmitter();page.location='about:blank';page.status=200;page.redirect=null;const frame={};
 page.url=()=>page.location;page.mainFrame=()=>frame;
 page.goto=async address=>{
  page.location=page.redirect??address;
  page.emit('response',{url:()=>page.location,status:()=>page.status,headers:()=>({'content-type':'text/html'}),allHeaders:async()=>({'retry-after':'120'}),
   request:()=>({resourceType:()=> 'document'}),frame:()=>frame,body:async()=>Buffer.from('publisher document')});
 };
 const context={newPage:async()=>page,route:async()=>{},request:{get:async()=>{throw Error('Unexpected replay request');}}};
 const bridge=()=>({doi_verified:true,outcome:'retrieved',context:[{heading:'Methods',text:'Source description.',native_type:''}],materials:[],notes:[]});
 return {page,context,bridge};
}
test('loaded browser document is reused without an independent metadata GET',async()=>{
 const {context,bridge}=fixture();const adapter=await browserAdapter(context,bridge,{settleTimeoutMs:0});
 const result=await adapter.collect(publication,'https://www.nature.com/articles/test');
 assert.equal(result.outcome,'retrieved');assert.equal(result.data.context[0].native_type,'');
});
test('assisted Enter can inspect a renewed login without navigating away',async()=>{
 const {page,context,bridge}=fixture();const adapter=await browserAdapter(context,bridge,{settleTimeoutMs:0});
 page.redirect='https://webauth.service.ohio-state.edu/idp/profile';
 assert.equal((await adapter.collect(publication,'https://www.nature.com/articles/test')).outcome,'authentication_expired');
 page.redirect=null;await page.goto('https://www.nature.com/articles/test');
 assert.equal((await adapter.collect(publication,'unused',{navigate:false})).outcome,'retrieved');
});
test('a rate limit during initial login is returned before collection starts',async()=>{
 const {page,context,bridge}=fixture();const adapter=await browserAdapter(context,bridge,{settleTimeoutMs:0});
 page.status=429;page.redirect='https://www.nature.com/articles/test';
 const result=await adapter.login(publication,{question:async()=>''});
 assert.equal(result.outcome,'rate_limited');assert.equal(result.cooldown.retry_after_seconds,120);
});
test('public corrected routes preserve DOI identifiers but drop session values',()=>{
 const result=publicRoute('https://journals.plos.org/plosone/article?id=10.1234/test&token=private');
 assert.ok(result.includes('id=10.1234%2Ftest'));assert.ok(!result.includes('private'));
});
test('OhioLINK selection pauses instead of masquerading as an unknown publisher',async()=>{
 const {page,context,bridge}=fixture();const adapter=await browserAdapter(context,bridge,{settleTimeoutMs:0});
 page.redirect='https://go.ohiolink.edu/acprod/odb_ejc/r/ohl/go/selection';
 assert.equal((await adapter.collect(publication,'https://www.nature.com/articles/test')).outcome,'institutional_access_required');
});
test('disconnected navigation does not parse the previous publication page',async()=>{
 const {page,context}=fixture();let calls=0;
 const adapter=await browserAdapter(context,()=>{calls++;throw Error('Stale document parsed');},{settleTimeoutMs:0});
 page.location='https://www.nature.com/articles/previous';
 page.goto=async()=>{throw Error('page.goto: net::ERR_INTERNET_DISCONNECTED');};
 assert.equal((await adapter.collect(publication,'https://www.nature.com/articles/test')).outcome,'connection_interrupted');
 assert.equal(calls,0);
});
test('503 with Retry-After stops without a document replay',async()=>{
 const {page,context,bridge}=fixture();const adapter=await browserAdapter(context,bridge,{settleTimeoutMs:0});
 page.status=503;
 const result=await adapter.collect(publication,'https://www.nature.com/articles/test');
 assert.equal(result.outcome,'service_unavailable');assert.equal(result.cooldown.retry_after_seconds,120);
});
test('a protected native service retains its institutional route policy',async()=>{
 const {page,context,bridge}=fixture();const original=page.goto;const visits=[];
 page.goto=async address=>{
  visits.push(address);
  page.redirect=address.startsWith('https://login.proxy.lib.ohio-state.edu/')?'https://www-nature-com.proxy.lib.ohio-state.edu/articles/test':null;
  return original(address);
 };
 const adapter=await browserAdapter(context,bridge,{settleTimeoutMs:0,requestIntervalMs:1});
 const result=await adapter.collect(publication,'https://www.nature.com/articles/test',{institutional:true});
 assert.equal(result.outcome,'retrieved');assert.equal(visits.length,2);
 assert.ok(visits[1].startsWith('https://login.proxy.lib.ohio-state.edu/login?url='));
});
test('Wiley menu repair bootstraps its known root then opens the expected DOI',async()=>{
 const {page,context,bridge}=fixture();const original=page.goto;const visits=[];
 page.goto=async address=>{
  visits.push(address);page.redirect=address.startsWith('https://login.proxy.lib.ohio-state.edu/')?'https://onlinelibrary-wiley-com.proxy.lib.ohio-state.edu/':null;
  return original(address);
 };
 const parser=(command,args)=>{
  const address=args[args.indexOf('--address')+1];
  return new URL(address).pathname==='/'?{doi_verified:false,outcome:'article_identity_unverified',context:[],materials:[]}:bridge();
 };
 const adapter=await browserAdapter(context,parser,{settleTimeoutMs:0,requestIntervalMs:1});
 const result=await adapter.repairRoute({...publication,DOI:'10.1002/example'},{outcome:'library_route_unavailable',destination:'https://login.proxy.lib.ohio-state.edu/menu'});
 assert.equal(result.outcome,'retrieved');assert.equal(visits.length,2);
 assert.equal(new URL(visits[1]).pathname,'/doi/full/10.1002/example');
});
test('Wiley bootstrap does not advance after a blocked root page',async()=>{
 const {page,context,bridge}=fixture();let visits=0;const original=page.goto;
 page.status=403;page.redirect='https://onlinelibrary-wiley-com.proxy.lib.ohio-state.edu/';
 page.goto=async address=>{visits++;return original(address);};
 const adapter=await browserAdapter(context,bridge,{settleTimeoutMs:0,requestIntervalMs:1});
 const result=await adapter.repairRoute({...publication,DOI:'10.1002/example'},{outcome:'library_route_unavailable',destination:'https://login.proxy.lib.ohio-state.edu/menu'});
 assert.equal(result.outcome,'access_block');assert.equal(visits,1);
});
test('journal homepage repair uses DOI delivery without changing identity checks',async()=>{
 const {page,context,bridge}=fixture();const original=page.goto;const visits=[];
 page.goto=async address=>{visits.push(address);page.redirect='https://academic-oup-com.proxy.lib.ohio-state.edu/nar/article/123';return original(address);};
 const adapter=await browserAdapter(context,bridge,{settleTimeoutMs:0,requestIntervalMs:1});
 const result=await adapter.repairRoute({...publication,DOI:'10.1093/nar/example'},{outcome:'article_identity_unverified',platform:'OUP',destination:'https://academic-oup-com.proxy.lib.ohio-state.edu/nar'});
 assert.equal(result.outcome,'retrieved');assert.equal(result.routing_repair,'institutional_doi_after_bad_delivery');assert.equal(visits.length,1);
});
