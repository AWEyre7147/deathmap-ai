/** Offline checks for the maintained library helpers after retiring pilot CLIs. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {atomicJson,chromiumFromModule,safeAddress,requestPacer,authenticationExpired,libraryMenuDestination} from '../scripts/library_access.mjs';
import {providerAllowed,deliveryPlatform,collectionFileAddress,doiProxyEntry} from '../scripts/library_delivery.mjs';

test('browser loading supports named and CommonJS exports without launching',()=>{
 const chromium={launch(){throw Error('No live browser in this fixture');}};
 assert.equal(chromiumFromModule({chromium}),chromium);
 assert.equal(chromiumFromModule({default:{chromium}}),chromium);
 assert.throws(()=>chromiumFromModule({}),TypeError);
});

test('recorded addresses omit authentication queries and fragments',()=>{
 assert.equal(safeAddress('https://example.org/article?ticket=private#session'),'https://example.org/article');
});

test('native host detection and file boundaries survive removal of probe scripts',()=>{
 assert.equal(deliveryPlatform('https://www-nature-com.proxy.lib.ohio-state.edu/articles/example'),'Nature');
 assert.equal(deliveryPlatform('https://www.sciencedirect.com/science/article/pii/S123'),'Elsevier');
 assert(providerAllowed('https://www.life-science-alliance.org/content/1/1/example','LSA'));
 assert(!providerAllowed('https://unrelated.example/article','Nature'));
 assert(collectionFileAddress('https://publisher.example/files/results.xlsx'));
 assert(collectionFileAddress('https://publisher.example/doi/pdf/10.1234/example'));
 assert(!collectionFileAddress('https://www.nature.com/articles/example'));
 assert.equal(doiProxyEntry('10.1234/example'),'https://login.proxy.lib.ohio-state.edu/login?url=https://doi.org/10.1234/example');
});

test('authentication and menus remain distinct; pacing needs no real sleep',async()=>{
 assert(authenticationExpired('https://webauth.service.ohio-state.edu/idp/profile'));
 assert(libraryMenuDestination('https://proxy.lib.ohio-state.edu/menu'));
 assert(!authenticationExpired('https://proxy.lib.ohio-state.edu/menu'));
 let clock=0;const delays=[];
 const pace=requestPacer(3000,{now:()=>clock,pause:async ms=>{delays.push(ms);clock+=ms;}});
 await pace();clock=1000;await pace();
 assert.deepEqual(delays,[2000]);
});

test('atomic checkpoints replace prior derived JSON and leave no temporary file',async t=>{
 const folder=await fs.mkdtemp(fileURLToPath(new URL('../outputs/library-support-test-',import.meta.url)));
 t.after(()=>fs.rm(folder,{recursive:true,force:true}));
 const path=folder+'/state.json';
 await atomicJson(path,{attempts:1});await atomicJson(path,{attempts:2});
 assert.deepEqual(JSON.parse(await fs.readFile(path,'utf8')),{attempts:2});
 await assert.rejects(fs.access(path+'.tmp'));
});
