/** Publisher-host detection and institutional DOI delivery for library enrichment.
 * These shared functions preserve the tested routing/file boundaries. There is
 * no pilot CLI, publication-specific repair table, or independent API enrichment.
 * OSU proxy addresses remain part of the current institutional adapter.
 */
/** Check an observed article host against the native/proxied provider allowlist. */
export function providerAllowed(address,publisher){
  const u=new URL(address);
  const native={Elsevier:['www.sciencedirect.com','sciencedirect.com','www.cell.com','cell.com'],AAAS:['www.science.org','science.org'],Wiley:['onlinelibrary.wiley.com','advanced.onlinelibrary.wiley.com'],Nature:['www.nature.com','nature.com'],AACR:['aacrjournals.org','www.aacrjournals.org'],ASM:['journals.asm.org'],PNAS:['www.pnas.org','pnas.org'],PLOS:['journals.plos.org'],OUP:['academic.oup.com'],ASH:['ashpublications.org','www.bloodjournal.org','www.sciencedirect.com','sciencedirect.com'],BMC:['link.springer.com','rd.springer.com','genomebiology.biomedcentral.com'],eLife:['elifesciences.org'],EMBO:['www.embopress.org','embopress.org','www.nature.com','link.springer.com'],CSH:['genesdev.cshlp.org'],RUP:['rupress.org'],MDPI:['www.mdpi.com','mdpi.com'],Springer:['link.springer.com','rd.springer.com'],CompanyBiologists:['journals.biologists.com'],Frontiers:['www.frontiersin.org','frontiersin.org'],JCI:['www.jci.org','jci.org','insight.jci.org'],Haematologica:['haematologica.org','www.haematologica.org'],LSA:['www.life-science-alliance.org','life-science-alliance.org'],BMJ:['gut.bmj.com'],TaylorFrancis:['www.tandfonline.com','tandfonline.com'],Impact:['www.oncotarget.com','oncotarget.com','www.aging-us.com']}[publisher]??[];
  // Compare against explicit encoded host variants; decoding all hyphens would
  // corrupt legitimate native names such as life-science-alliance.org.
  // Known hosting variations retain the requested publisher label.
  if(publisher==='Wiley')native.push('febs.onlinelibrary.wiley.com','journals.lww.com','chemistry-europe.onlinelibrary.wiley.com');
  if(publisher==='ASM')native.push('www.tandfonline.com');
  if(publisher==='ResearchSquare')native.push('www.researchsquare.com','researchsquare.com');
  if(publisher==='BioRxiv')native.push('www.biorxiv.org','biorxiv.org');
  if(publisher==='LWW')native.push('journals.lww.com');
  const matched=native.some(h=>u.hostname===h||u.hostname===h.replaceAll('.','-')+'.proxy.lib.ohio-state.edu');
  return u.protocol==='https:'&&matched&&!/(?:\.pdf|\.zip|\.xlsx?|\.csv|\.gz)$|\/pdf(?:\/|$)|\/doi\/(?:pdf|epdf|suppl)\/|\/suppdata\/|\/attachment\//i.test(u.pathname);
}

/** Infer the supported platform from an observed destination. */
export function deliveryPlatform(address){
  // Prefer the actual shared host to legacy journal/publisher aliases.
  const hosted=['TaylorFrancis','LWW','Springer'].find(p=>providerAllowed(address,p));
  if(hosted)return hosted;
  return ['Nature','Elsevier','AAAS','Wiley','AACR','ASM','PNAS','PLOS','OUP','ASH','BMC','eLife','EMBO','CSH','RUP','MDPI','Springer','CompanyBiologists','Frontiers','JCI','Haematologica','LSA','BMJ','TaylorFrancis','Impact','ResearchSquare','BioRxiv'].find(p=>providerAllowed(address,p))??null;
}

/** Block experimental-file and PDF routes before browser navigation. */
export function collectionFileAddress(address){
  const u=new URL(address),p=u.pathname;
  return /\.(?:pdf|zip|xlsx?|csv|tsv|gz|bz2|tar|fastq|fq|bam|cram|rds|h5|h5ad|fcs|mtx|loom|npy|parquet|docx?|pptx?)(?:\/|$)|\/doi\/(?:pdf|epdf|suppl)\/|\/suppdata\/|\/attachment\/|\/article\/file(?:\/|$)|\/pdf(?:\/|$)/i.test(p)||u.searchParams.get('type')==='supplementary';
}

/** Construct the current institutional DOI entry without guessing file URLs. */
export function doiProxyEntry(doi){
  return 'https://login.proxy.lib.ohio-state.edu/login?url=https://doi.org/'+encodeURI(doi);
}
