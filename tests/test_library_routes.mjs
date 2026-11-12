/** Regression cases from the stopped run and previously saved Alma pilots.
 * These files are read offline; no publication identifiers are used as queries.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {chooseService,deliveryEntry,accessDestination,connectionFailure,journalLanding,routingFallback} from '../scripts/library_routes.mjs';
import {eligible} from '../scripts/library_run_state.mjs';

const service=(name,fields={})=>({service_type:'getFullTxt',resolution_url:'https://ohiolink-osu.alma.exlibrisgroup.com/view/action/uresolver.do',fields:{package_display_name:[name],...fields}});
test('publisher title mentions in an aggregator do not outrank the native package',()=>{
 const aggregator=service('EBSCOhost MEDLINE with Full Text',{parse_parameters:['jtitle=Nature; platform=Nature'],current_access:['true']});
 const native=service('Nature');
 assert.equal(chooseService([aggregator,native],{DOI:'10.1038/nbt.3567'}),native);
});
test('Journals at Ovid and OhioLINK are not native-publisher packages',()=>{
 const native=service('American Association for the Advancement of Science');
 assert.equal(chooseService([service('Journals@Ovid'),service('OhioLINK Electronic Journals Center'),native],{DOI:'10.1126/example'}),native);
});
test('PMC and generic available-content services yield a publisher DOI fallback',()=>{
 const services=[service('PubMed Central'),service('Publicly Available Content Database')];
 assert.equal(chooseService(services,{DOI:'10.1038/example'}),undefined);
 assert.equal(deliveryEntry({DOI:'10.1038/example'},undefined).route_source,'institutional_doi_fallback');
 assert.ok(deliveryEntry({DOI:'10.1371/journal.pone.example'},undefined).url.startsWith('https://doi.org/'));
});
test('known platform migrations do not require a DOI prefix to match the host',()=>{
 const native={...service('Oxford University Press'),resolution_url:'https://academic.oup.com/article/123'};
 assert.equal(chooseService([native],{DOI:'10.1002/example'}),native);
});
test('protected and public native services carry different delivery policies',()=>{
 const native=service('Nature');
 assert.equal(deliveryEntry({DOI:'10.1038/example'},native).institutional,true);
 assert.equal(deliveryEntry({DOI:'10.1371/example'},service('PLOS')).institutional,false);
});
test('additional access screens and repository delivery are distinct outcomes',()=>{
 assert.equal(accessDestination('https://go.ohiolink.edu/acprod/odb_ejc/r/ohl/go/selection'),'institutional_access_required');
 assert.equal(accessDestination('https://login.ebsco.com/'),'external_authentication_required');
 assert.equal(accessDestination('https://openurl.ebsco.com/srh/detailv2'),'delivery_intermediary');
 assert.equal(accessDestination('https://pmc.ncbi.nlm.nih.gov/articles/PMC123/'),'repository_redirect');
 assert.equal(accessDestination('https://www.nature.com/articles/example'),null);
});
test('connection-loss signals differ from an ordinary loading timeout',()=>{
 for(const message of ['page.goto: net::ERR_INTERNET_DISCONNECTED','net::ERR_PROXY_CONNECTION_FAILED','ECONNRESET','Client network socket disconnected before secure TLS connection was established'])assert.equal(connectionFailure({message}),true);
 assert.equal(connectionFailure({message:'Timeout 45000ms exceeded'}),false);
});
test('routing repair explicitly requeues earlier failed routes and skips success',()=>{
 const pub={'Publication Index':'PUB-0001',DOI:'10.1234/example',Journal:'Example'};
 const history=[{publication_index:'PUB-0001',outcome:'unsupported_platform',mode:'automatic'}];
 assert.equal(eligible(pub,history),false);assert.equal(eligible(pub,history,'automatic',true),true);
 assert.equal(eligible(pub,[...history,{publication_index:'PUB-0001',outcome:'retrieved',mode:'automatic'}],'automatic',true),false);
});
test('native Nature and AAAS packages remain selectable without saved pilot data',()=>{
 const nature=service('Nature');
 const science=service('American Association for the Advancement of Science');
 assert.equal(chooseService([service('OhioLINK'),nature],{DOI:'10.1038/example',Journal:'Nature'}),nature);
 assert.equal(chooseService([service('Journals@Ovid'),science],{DOI:'10.1126/example',Journal:'Science'}),science);
});
test('journal homepage identity failures qualify for routing repair, article conflicts do not',()=>{
 const pub={'Publication Index':'PUB-0001',DOI:'10.1093/nar/example',Journal:'NAR'};
 const home={publication_index:'PUB-0001',outcome:'article_identity_unverified',platform:'OUP',destination:'https://academic-oup-com.proxy.lib.ohio-state.edu/nar'};
 assert.equal(journalLanding(home.destination,'OUP'),true);assert.equal(eligible(pub,[home],'automatic',true),true);
 assert.equal(eligible(pub,[{...home,destination:home.destination+'/article/123'}],'automatic',true),false);
});
test('bad service delivery has bounded platform-appropriate fallbacks',()=>{
 const menu={outcome:'library_route_unavailable',destination:'https://login.proxy.lib.ohio-state.edu/menu'};
 assert.equal(routingFallback({DOI:'10.1002/jcp.27595'},menu).kind,'wiley_root_bootstrap');
 assert.equal(routingFallback({DOI:'10.1038/s41598-example'},menu).kind,'public_doi_after_bad_delivery');
 assert.equal(routingFallback({DOI:'10.15252/example'},menu).kind,'public_doi_after_bad_delivery');
 assert.equal(routingFallback({DOI:'10.1016/example'},menu).kind,'institutional_doi_after_bad_delivery');
 assert.equal(routingFallback({DOI:'10.1093/nar/example'},{outcome:'article_identity_unverified',platform:'OUP',destination:'https://academic.oup.com/nar'}).institutional,true);
 assert.equal(routingFallback({DOI:'10.3389/example'},{outcome:'article_identity_unverified',platform:'Frontiers',destination:'https://www.frontiersin.org/journals/immunology'}).institutional,false);
});
test('alternate delivery never retries an access block, CAPTCHA, outage, or rate limit',()=>{
 for(const outcome of ['challenge','access_block','rate_limited','connection_interrupted','service_unavailable','external_authentication_required']){
  assert.equal(routingFallback({DOI:'10.1038/example'},{outcome,destination:'https://www.nature.com/articles/example'}),null);
 }
});
test('Cell Reports Medicine menu failures use public DOI delivery',()=>{
 const pub={DOI:'10.1016/j.xcrm.2024.101999'};
 const menu={outcome:'library_route_unavailable',destination:'https://login.proxy.lib.ohio-state.edu/menu'};
 const result=routingFallback(pub,menu);
 assert.equal(result.kind,'public_doi_after_bad_delivery');assert.equal(result.institutional,false);
 assert.equal(result.url,'https://doi.org/'+pub.DOI);
 assert.equal(routingFallback(pub,{outcome:'access_block',destination:menu.destination}),null);
});
