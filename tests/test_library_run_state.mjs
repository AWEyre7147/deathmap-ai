/** Offline recovery cases for the maintained library run controller. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {binding,eligible,cooldown,cooling,mergeContent} from '../scripts/library_run_state.mjs';
import {options} from '../scripts/library_enrichment.mjs';
import {platformFor,blockedAddress,chooseService} from '../scripts/library_browser.mjs';

const pub={'Publication Index':'PUB-0001',DOI:'10.1234/example',Journal:'Example'};
const attempt=(outcome,mode='automatic')=>({publication_index:'PUB-0001',outcome,mode});
test('restart skips retrieved work and leaves failures available to assistance',()=>{
 assert.equal(eligible(pub,[]),true);
 assert.equal(eligible(pub,[attempt('retrieved')]),false);
 assert.equal(eligible(pub,[attempt('access_block')]),false);
 assert.equal(eligible(pub,[attempt('access_block')],'assisted'),true);
 assert.equal(eligible(pub,[attempt('authentication_expired')]),true);
});
test('429 permits one later automatic retry without abandoning the publication',()=>{
 assert.equal(eligible(pub,[attempt('rate_limited')]),true);
 assert.equal(eligible(pub,[attempt('rate_limited'),attempt('rate_limited')]),false);
 assert.equal(eligible(pub,[attempt('rate_limited'),attempt('rate_limited')],'assisted'),true);
});
test('cooldown survives JSON checkpoint and uses both server header forms',()=>{
 const now=Date.parse('2026-11-11T12:00:00Z');
 const state=JSON.parse(JSON.stringify({cooldown:cooldown({'retry-after':'120'},'Elsevier',now)}));
 assert.equal(cooling(state,now+119000),true);assert.equal(cooling(state,now+120000),false);
 assert.equal(cooldown({'retry-after':'Wed, 11 Nov 2026 12:03:00 GMT'},'Elsevier',now).not_before_utc,'2026-11-11T12:03:00.000Z');
 assert.equal(cooldown({},'Alma',now).not_before_utc,'2026-11-11T12:15:00.000Z');
});
test('manifest binding changes when input identity changes',()=>{
 assert.notEqual(binding({publications:[pub]}),binding({publications:[{...pub,DOI:'10.1234/other'}]}));
});
test('content merge deduplicates source text and retains size guard',()=>{
 const a={doi_verified:true,context:[{text:'Text',heading:'Methods'}],materials:[],notes:[]};
 const b={doi_verified:true,context:[{text:'Text',heading:'Methods'},{text:'x'.repeat(60000),heading:'Methods'}],materials:[],notes:[]};
 const merged=mergeContent(a,b);assert.equal(merged.context.length,1);assert.ok(merged.notes.some(n=>n.includes('size guard')));
});
test('actual platform and experimental-file boundaries are explicit',()=>{
 assert.equal(platformFor('https://faseb.onlinelibrary.wiley.com/doi/full/10.1/a'),'Wiley');
 assert.equal(platformFor('https://www.tandfonline.com/doi/full/10.1/a'),'TaylorFrancis');
 assert.equal(blockedAddress('https://example.org/data.fastq.gz'),true);
 assert.equal(blockedAddress('https://www.oncotarget.com/article/1/text/'),true);
 assert.equal(blockedAddress('https://www.nature.com/articles/example'),false);
});
test('Alma service ranking prefers native publishers over aggregators',()=>{
 const a={resolution_url:'https://aggregator.example/a',fields:{package_display_name:['Aggregator']}};
 const b={resolution_url:'https://library.example/article',fields:{package_display_name:['ScienceDirect']}};
 assert.equal(chooseService([a,b]),b);
});
test('CLI rejects unknown controls and invalid delays',()=>{
 assert.equal(options([])['--paper-delay-seconds'],15);
 assert.throws(()=>options(['--request-delay-seconds','0']));
 assert.throws(()=>options(['--request-delay-seconds','Infinity']));
 assert.throws(()=>options(['--surprise']));
});
