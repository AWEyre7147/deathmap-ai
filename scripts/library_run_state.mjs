/** Durable attempt selection for the library collector. Pure queue/cooldown
 * functions are independently tested without browsers or external requests.
 */
import {createHash} from 'node:crypto';
import {rateLimitDetails} from './library_access.mjs';
import {journalLanding} from './library_routes.mjs';

/** Bind resumptions to normalized publication inputs, template and content rules. */
export function binding(manifest){return createHash('sha256').update(JSON.stringify(manifest)).digest('hex');}

/** Select unfinished work. An HTTP 429 gets only one later automatic retry;
 * a failed request is not silently retried or interpreted as unavailable.
 */
export function eligible(publication,attempts,mode='automatic',retryRouting=false){
 const history=attempts.filter(a=>a.publication_index===publication['Publication Index']);
 if(history.some(a=>a.outcome==='retrieved'))return false;
 if(!publication.DOI||/oncotarget/i.test(publication.Journal))return history.length===0;
 if(mode==='assisted')return true;
 if(!history.length)return true;
 const last=history.at(-1);
 if(['authentication_expired','connection_interrupted','service_unavailable'].includes(last.outcome))return true;
 if(retryRouting&&['unsupported_platform','repository_redirect','delivery_intermediary','library_route_unavailable','institutional_access_required','external_authentication_required'].includes(last.outcome))return true;
 if(retryRouting&&last.outcome==='article_identity_unverified'&&journalLanding(last.destination,last.platform))return true;
 return last.outcome==='rate_limited'&&history.filter(a=>a.mode==='automatic'&&a.outcome==='rate_limited').length<2;
}

/** Honor server Retry-After, with a conservative fallback only if it is absent. */
export function cooldown(headers,platform,now=Date.now(),fallbackSeconds=900){
 const details=rateLimitDetails(headers,now);
 return {...details,platform,not_before_utc:details.retry_not_before_utc??new Date(now+fallbackSeconds*1000).toISOString()};
}

/** A persisted cooldown applies across processes and cannot be bypassed by resume. */
export function cooling(state,now=Date.now()){
 return Boolean(state.cooldown&&Date.parse(state.cooldown.not_before_utc)>now);
}

/** Merge DOI-verified representations without changing publisher headings/types. */
export function mergeContent(current,extra,maxText=60000){
 if(!extra?.doi_verified)return current;
 const paragraphs=new Map((current.context??[]).map(p=>[p.text,p]));
 for(const p of extra.context??[])paragraphs.set(p.text,p);
 const materials=new Map((current.materials??[]).map(m=>[m.url||m.native_reference||m.native_id,m]));
 for(const m of extra.materials??[])materials.set(m.url||m.native_reference||m.native_id,m);
 const context=[];let characters=0;const notes=[...(current.notes??[]),...(extra.notes??[])];
 for(const p of paragraphs.values()){
  if(characters+p.text.length>maxText){notes.push('Merged selected text size guard');continue;}
  characters+=p.text.length;context.push(p);
 }
 const listed=[...materials.values()];
 const finalNotes=notes.filter(n=>!['No qualifying methods or availability text retained','No explicit supporting listing retained'].includes(n));
 if(!context.length)finalNotes.push('No qualifying methods or availability text retained');
 if(!listed.length)finalNotes.push('No explicit supporting listing retained');
 return {...current,doi_verified:true,context,materials:listed,notes:[...new Set(finalNotes)],outcome:context.length||listed.length?'retrieved':'parser_incomplete'};
}
