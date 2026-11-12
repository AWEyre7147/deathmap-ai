/** Publisher delivery policy, kept separate from browser access and extraction.
 * Service names nominate routes; journal titles inside aggregator parameters do
 * not identify a publisher service. DOI prefixes are routing hints only.
 */
import {deliveryPlatform,doiProxyEntry} from './library_delivery.mjs';

const PACKAGES=[
 ['Elsevier',/^(?:ScienceDirect|Elsevier|Cell Press)\b/i,['10.1016/','10.1074/']],
 ['Nature',/^(?:Nature\b|Springer Nature\b.*nature\.com)/i,['10.1038/']],
 ['Wiley',/^(?:Wiley|FEBS)\b/i,['10.1002/','10.1111/','10.1096/']],
 ['AAAS',/^(?:American Association for the Advancement of Science|AAAS|Science(?: Online| Journals)?$)/i,['10.1126/']],
 ['AACR',/^(?:American Association for Cancer Research|AACR)\b/i,['10.1158/']],
 ['OUP',/^Oxford\b/i,['10.1093/','10.1534/']],
 ['PNAS',/^(?:PNAS|Proceedings of the National Academy)\b/i,['10.1073/']],
 ['PLOS',/^Public Library of Science\b|^PLOS\b/i,['10.1371/']],
 ['eLife',/^eLife\b/i,['10.7554/']],
 ['Springer',/^Springer\b|^BioMed Central\b/i,['10.1007/','10.1186/']],
 ['TaylorFrancis',/^Taylor\b/i,['10.1080/']],
 ['LWW',/^Lippincott\b/i,[]],
 ['RUP',/^Rockefeller University Press\b/i,['10.1083/','10.1084/']],
 ['MDPI',/^MDPI\b/i,['10.3390/']],
 ['Frontiers',/^Frontiers\b/i,['10.3389/']],
 ['CompanyBiologists',/^(?:Company of Biologists|The Company of Biologists)\b/i,['10.1242/']],
 ['EMBO',/^EMBO\b/i,['10.15252/']],
 ['JCI',/^Journal of Clinical Investigation\b|^American Society for Clinical Investigation\b/i,['10.1172/']],
 ['Haematologica',/^Haematologica\b/i,['10.3324/']],
 ['LSA',/^Life Science Alliance\b/i,['10.26508/']],
 ['Impact',/^Aging\b/i,['10.18632/']],
 ['CSH',/^Cold Spring Harbor\b|^Genes (?:and|&) Development\b/i,['10.1101/gad.']],
 ['BioRxiv',/^bioRxiv\b/i,['10.1101/']],
 ['ResearchSquare',/^Research Square\b/i,['10.21203/']]
];
const AGGREGATOR=/EBSCO|Gale\b|Nexis|OhioLINK|\bEJC\b|PubMed Central|ProQuest|JSTOR|Ovid\b|ClinicalKey|Publicly Available Content Database/i;
const DIRECT=new Set(['PLOS','eLife','MDPI','Frontiers','JCI','Haematologica','LSA','Impact','BioRxiv','ResearchSquare']);

/** Prefer the appropriate named publisher package, never a generic "Journals"
 * match or a publisher name appearing inside another provider's query fields.
 */
export function chooseService(services,publication={}){
 const doi=(publication.DOI??'').toLowerCase();
 const hint=PACKAGES.find(([, ,prefixes])=>prefixes.some(p=>doi.startsWith(p)))?.[0];
 const candidates=[];
 for(const service of services){
  if(service.service_type&&service.service_type!=='getFullTxt')continue;
  let url;try{url=new URL(service.resolution_url);}catch{continue;}
  if(url.protocol!=='https:'||url.username||url.password)continue;
  const names=(service.fields?.package_display_name??[]).filter(n=>typeof n==='string');
  if(names.some(n=>AGGREGATOR.test(n)))continue;
  if(accessDestination(url.href))continue;
  const named=PACKAGES.find(([,pattern])=>names.some(n=>pattern.test(n)))?.[0];
  const hosted=deliveryPlatform(url.href);
  if(!named&&!hosted)continue;
  const current=service.fields?.current_access?.includes('true')?1:0;
  candidates.push({service,score:Number((named??hosted)===hint)*4+Number(Boolean(hosted))*2+current});
 }
 candidates.sort((a,b)=>b.score-a.score);
 return candidates[0]?.service;
}

/** Reuse the pilot's direct/public DOI versus institutional DOI policy when no
 * trustworthy native Alma service exists. Never fall back to the first service.
 */
export function deliveryEntry(publication,service){
 const doi=(publication.DOI??'').toLowerCase();
 const family=PACKAGES.find(([, ,prefixes])=>prefixes.some(p=>doi.startsWith(p)))?.[0];
 if(service)return {url:service.resolution_url,service_id:service.service_id??null,route_source:'alma_native_publisher_service',institutional:!DIRECT.has(family)};
 return {url:DIRECT.has(family)?'https://doi.org/'+encodeURI(publication.DOI):doiProxyEntry(publication.DOI),
  service_id:null,route_source:DIRECT.has(family)?'direct_publisher_doi_fallback':'institutional_doi_fallback',institutional:!DIRECT.has(family)};
}

/** Recognize journal landing pages without mistaking an article's missing DOI
 * for a routing defect. Only explicit, known hosting structures qualify.
 */
export function journalLanding(address,platform){
 let u;try{u=new URL(address);}catch{return false;}
 const p=u.pathname.replace(/\/$/,'');
 if(platform==='OUP')return /^\/[a-z][a-z0-9-]*$/i.test(p);
 if(platform==='Frontiers')return /^\/journals\/[^/]+$/i.test(p)||p==='';
 return false;
}

/** One bounded article-delivery fallback for menus/homepages, not access blocks.
 * Open-access Nature/EMBO journal routes are tried through the public DOI entry;
 * Wiley reuses the established root-entry bootstrap rather than a stale service.
 */
export function routingFallback(publication,result){
 let pathname;try{pathname=new URL(result.destination??'https://invalid.example/').pathname;}catch{return null;}
 const menu=result.outcome==='library_route_unavailable'&&/\/menu\/?$/.test(pathname);
 const homepage=result.outcome==='article_identity_unverified'&&journalLanding(result.destination,result.platform);
 if(!menu&&!homepage)return null;
 const doi=(publication.DOI??'').toLowerCase();
 if(menu&&/^(?:10\.1002\/|10\.1111\/|10\.1096\/)/.test(doi))return {kind:'wiley_root_bootstrap',url:'https://login.proxy.lib.ohio-state.edu/login?url=https://onlinelibrary.wiley.com/'};
 const publicDelivery=doi.startsWith('10.1038/')||doi.startsWith('10.15252/')||doi.startsWith('10.1080/')||doi.startsWith('10.1016/j.xcrm.')||result.platform==='Frontiers';
 return {kind:publicDelivery?'public_doi_after_bad_delivery':'institutional_doi_after_bad_delivery',
  url:publicDelivery?'https://doi.org/'+encodeURI(publication.DOI):doiProxyEntry(publication.DOI),institutional:!publicDelivery};
}

/** Distinguish additional access/selection screens from publisher extractors.
 * An OhioLINK selection screen is not proof that the OSU login expired.
 */
export function accessDestination(address){
 let u;try{u=new URL(address);}catch{return null;}
 if(u.hostname==='ohiolink.edu'||u.hostname.endsWith('.ohiolink.edu'))return 'institutional_access_required';
 if(u.hostname==='pmc.ncbi.nlm.nih.gov'||u.hostname==='www.ncbi.nlm.nih.gov'&&u.pathname.startsWith('/pmc/'))return 'repository_redirect';
 if(/^(?:login|auth)\.ebsco(?:host)?\.com$/.test(u.hostname))return 'external_authentication_required';
 if(/(?:^|\.)(?:ebsco|ebscohost|ovid|proquest|gale)\.com$/.test(u.hostname)||/(?:ebsco|ovid)-com\.proxy\.lib\.ohio-state\.edu$/.test(u.hostname))return 'delivery_intermediary';
 return null;
}

/** Navigation failures must stop the queue rather than parse a stale prior page. */
export function connectionFailure(error){
 return /net::ERR_(?:INTERNET_DISCONNECTED|NETWORK_CHANGED|PROXY_CONNECTION_FAILED|TUNNEL_CONNECTION_FAILED|CONNECTION_(?:RESET|CLOSED|REFUSED|TIMED_OUT)|NAME_NOT_RESOLVED)|ECONNRESET|ENETUNREACH|ENOTFOUND|ECONNREFUSED|socket (?:hang up|disconnected)|network socket disconnected|browser (?:has been )?(?:closed|disconnected)|Target page, context or browser has been closed/i.test(error?.message??'');
}
