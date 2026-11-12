/** No-network Playwright fixture for checkpoint/cooldown CLI integration tests. */
const {EventEmitter}=require('node:events');
const fs=require('node:fs');
const log=value=>{if(process.env.LIBRARY_MOCK_LOG)fs.appendFileSync(process.env.LIBRARY_MOCK_LOG,JSON.stringify(value)+'\n');};
class Page extends EventEmitter{
 constructor(){super();this.location='about:blank';this.frame={};}
 url(){return this.location;}
 mainFrame(){return this.frame;}
 async goto(address){
  let u=new URL(address);if(u.searchParams.has('url'))u=new URL(u.searchParams.get('url'));
  const id=u.pathname.split('/').at(-1);this.location='https://www-nature-com.proxy.lib.ohio-state.edu/articles/'+id;
  if(id==='rate'&&process.env.LIBRARY_MOCK_MODE==='disconnected')throw Error('page.goto: net::ERR_INTERNET_DISCONNECTED');
  const status=id==='rate'&&process.env.LIBRARY_MOCK_MODE!=='recovered'?429:200;
  const html=`<html><head><meta name="citation_doi" content="10.1234/${id}"></head><body><h1>Example article</h1><h2>Methods</h2><p>Source design for ${id}.</p><h2>Supporting information</h2><a href="https://static.example.org/${id}.xlsx">Table S1</a></body></html>`;
  log({kind:'navigate',status,id});
  const response={url:()=>this.location,status:()=>status,headers:()=>({'content-type':'text/html','retry-after':'120'}),allHeaders:async()=>({'retry-after':'120'}),request:()=>({resourceType:()=> 'document'}),frame:()=>this.frame,body:async()=>Buffer.from(html)};
  this.emit('response',response);
 }
}
const chromium={launch:async()=>{
 log({kind:'launch'});
 return {version:()=> 'fixture/1',close:async()=>{},newContext:async()=>({
  route:async()=>{},newPage:async()=>new Page(),
  request:{get:async address=>{
   log({kind:'metadata',address});const id=new URL(address).searchParams.get('rft_id').split('/').at(-1);
   const xml=`<context><context_service context_service_id="1"><keys><key id="package_display_name">Nature</key></keys><resolution_url>https://www-nature-com.proxy.lib.ohio-state.edu/articles/${id}</resolution_url></context_service></context>`;
   return {status:()=>200,body:async()=>Buffer.from(xml),headers:()=>({'content-type':'application/xml'}),dispose:async()=>{}};
  }}
 })};
}};
module.exports={chromium};
