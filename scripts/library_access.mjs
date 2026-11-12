/** Browser loading, privacy, timing and checkpoint helpers for library collection.
 * Imported by the maintained collector; no login probe, saved pilot input, batch
 * selection or network action runs on import. Current login/menu patterns are
 * OSU-specific and must not be represented as support for every institution.
 */
import fs from 'node:fs/promises';

/** Atomically replace a collector-owned JSON checkpoint. */
export async function atomicJson(file,value){
  await fs.writeFile(file+'.tmp',JSON.stringify(value,null,2));
  await fs.rename(file+'.tmp',file);
}

/** Resolve named or CommonJS browser exports without launching a browser. */
export function chromiumFromModule(module) {
  // Bundled CommonJS builds expose their public browser API under default.
  const chromium = module.chromium ?? module.default?.chromium;
  if (typeof chromium?.launch !== 'function') throw new TypeError('Browser API unavailable');
  return chromium;
}

/** Strip session-bearing query and fragment values from recorded addresses. */
export function safeAddress(value) {
  // Authentication URLs can contain SAML payloads, tickets and session IDs.
  // Retain only scheme, hostname and path in the probe's report.
  const url = new URL(value);
  return url.origin + url.pathname;
}

/** Preserve Retry-After timing without retaining unrelated response headers. */
export function rateLimitDetails(headers,now=Date.now()){
  const value=headers['retry-after'];
  let seconds=null;
  if(typeof value==='string'&&/^\d+$/.test(value.trim()))seconds=Number(value.trim());
  else if(typeof value==='string'&&Number.isFinite(Date.parse(value)))seconds=Math.max(0,Math.ceil((Date.parse(value)-now)/1000));
  if(!Number.isFinite(seconds)||seconds<0)seconds=null;
  const deadline=seconds===null?null:now+seconds*1000;
  return {observed_utc:new Date(now).toISOString(),retry_after_present:value!==undefined,
    retry_after_seconds:seconds,retry_not_before_utc:deadline!==null&&Number.isFinite(new Date(deadline).getTime())?new Date(deadline).toISOString():null,
    interpretation:'A cooldown instruction is not a guarantee of future access; no automatic retry.'};
}

/** Space explicit metadata requests; browser page resources remain separate. */
export function requestPacer(intervalMs,{now=Date.now,pause=ms=>new Promise(resolve=>setTimeout(resolve,ms))}={}){
  let last=null;
  return async()=>{
    if(last!==null){const delay=Math.max(0,intervalMs-(now()-last));if(delay)await pause(delay);}
    last=now();
  };
}

/** Recognize the current institutional menu without diagnosing login expiry. */
export function libraryMenuDestination(address){
  const u=new URL(address);
  return ['proxy.lib.ohio-state.edu','login.proxy.lib.ohio-state.edu'].includes(u.hostname)&&/^\/menu(?:\/|$)/.test(u.pathname);
}

/** Recognize current institutional authentication destinations. */
export function authenticationExpired(address){
  const u=new URL(address);
  return /(?:^|\.)ohio-state\.edu$/.test(u.hostname)&&(
    /webauth|shibboleth|sso/.test(u.hostname)||/\/(?:idp|cas|shibboleth)(?:\/|$)/i.test(u.pathname)
    ||(['proxy.lib.ohio-state.edu','login.proxy.lib.ohio-state.edu'].includes(u.hostname)&&/^\/login(?:\/|$)/.test(u.pathname)));
}
