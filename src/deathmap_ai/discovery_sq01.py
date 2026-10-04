"""Standalone SQ01 prepare/preflight/run/resume/export/verify command.

This entry point needs only Python and the repository. It never sends records to
Codex or a language model. Live execution requires an offline preflight tied to
the exact source/tests and accepted plan. All writers share a crash-safe OS lock.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from deathmap_ai import sq01_omicsdi as omics
from deathmap_ai import sq01_orcs as orcs
from deathmap_ai.sq01_export import export
from deathmap_ai.sq01_plan import VERSION, RUN_ID, build_plan, digest, load_plan, validate_plan
from deathmap_ai.sq01_io import (read, write, encoded, atomic_bytes, sha, now, folders,
                                writer_lock, preservation, verify_freeze)

OUTPUT_NAMES = {'resume_state.json','source_records.json','candidates.json','query_hits.json',
                'candidate_summary.json','issues.json','search_manifest.json','freeze_manifest.json'}


def code_digest(root):
    """Bind preflight to implementation/tests without reading scientific inputs."""
    paths=sorted(list((root/'src').rglob('*.py'))+list((root/'tests').rglob('*.py')))
    return digest({p.relative_to(root).as_posix():sha(p) for p in paths})


def check_directories(root, plan_digest):
    """Accept only new or matching SQ01 directories; stop on uncommitted writes."""
    paths=folders(root)
    for name in ('omicsdi','orcs'):
        folder=paths[name]
        if not folder.exists() or not list(folder.iterdir()):
            continue
        state_path=folder/'resume_state.json'
        if not state_path.is_file():
            raise ValueError('Nonempty resource directory lacks matching resumable state')
        state=read(state_path)
        if state['plan_digest']!=plan_digest or state['run_id']!=RUN_ID:
            raise ValueError('Foreign resource run state')
        allowed=OUTPUT_NAMES.copy()
        if name=='omicsdi':
            omics.check_state(state,plan_digest)
            for event in state['attempts']:
                allowed.update([event['raw_file'],event['receipt_file']])
        for file in folder.rglob('*'):
            if file.is_file() and file.relative_to(folder).as_posix() not in allowed:
                raise ValueError('Unexpected/uncommitted resource file: '+str(file))
        if (folder/'freeze_manifest.json').exists():
            verify_freeze(folder,plan_digest)
    return paths


def prepare(root):
    """Install accepted SQ01 plan and new ledgers; archive only the superseded draft."""
    plan=build_plan(); plan_digest=validate_plan(plan)
    paths=check_directories(root,plan_digest)
    baseline_source=root/'docs/sq01-preservation.json'
    preservation(root,baseline_source)
    shared=paths['shared']; target=shared/'query_plan.json'
    if target.exists():
        existing=read(target)
        if existing!=plan:
            if existing.get('plan_version')!='immune-crispr-coculture-v03.1' or existing.get('status')!='proposed_for_owner_review':
                raise ValueError('Refusing to overwrite a different accepted plan')
            archive=shared/'planning-history/query_plan-proposed-v03.1.json'
            original=target.read_bytes()
            if archive.exists() and archive.read_bytes()!=original:
                raise ValueError('Conflicting historical planning artifact')
            if not archive.exists():
                atomic_bytes(archive,original)
            write(target,plan)
    else:
        write(target,plan)
    baseline=shared/'preservation_baseline.json'
    if not baseline.exists():
        source=read(baseline_source)
        write(baseline,{'recorded_at':source['recorded_at'],'before':source['before']})
    preservation(root,baseline)
    for name,adapter in [('omicsdi',omics),('orcs',orcs)]:
        file=paths[name]/'resume_state.json'
        if not file.exists():
            write(file,adapter.initial(plan_digest))
    return {'prepared':True,'plan_digest':plan_digest,'queries':plan['resources'][0]['queries'],
            'policy':plan['resources'][0]['request_policy']}


def preflight(root):
    """Run all offline tests and concrete preservation/cache/path gates; no requests."""
    plan=load_plan(root); plan_digest=digest(plan)
    paths=check_directories(root,plan_digest)
    preserved=preservation(root,paths['shared']/'preservation_baseline.json')
    rows,metadata=orcs.load_index(root)
    env=dict(os.environ); env['PYTHONPATH']=str(root/'src'); env['PYTHONDONTWRITEBYTECODE']='1'
    command=[sys.executable,'-B','-m','unittest','discover','-s',str(root/'tests')]
    result=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=300)
    if result.returncode:
        raise RuntimeError('Offline test gate failed:\n'+result.stderr[-6000:])
    stamp={'passed_at':now(),'plan_digest':plan_digest,'code_digest':code_digest(root),
        'preservation':preserved,'orcs_cache_records':len(rows),'cache_retrieved_at':metadata['retrieved_at'],
        'tests':{'command':command,'returncode':result.returncode,'summary':result.stderr[-2000:]},
        'network_requests':0,'candidate_page_runtime_caps':None,'detail_requests_enabled':False,
        'request_policy':plan['resources'][0]['request_policy'],
        'exact_query_family':[{k:q[k] for k in ('query_id','submitted_query')} for q in plan['resources'][0]['queries']]}
    write(paths['shared']/'preflight.json',stamp)
    return stamp


def require_preflight(root, plan_digest):
    paths=check_directories(root,plan_digest)
    stamp=read(paths['shared']/'preflight.json')
    if stamp['plan_digest']!=plan_digest or stamp['code_digest']!=code_digest(root) or stamp['tests']['returncode']!=0:
        raise ValueError('Preflight missing/stale for this code and plan')
    preservation(root,paths['shared']/'preservation_baseline.json')
    return paths


def run_summary(root, verify=False):
    """Write/verify compact cross-resource counts without constructing entity tables."""
    plan=load_plan(root); paths=folders(root)
    summaries={}
    for name,adapter in [('omicsdi',omics),('orcs',orcs)]:
        summaries[name]=adapter.summary(read(paths[name]/'resume_state.json'))
    value={'run_id':RUN_ID,'plan_digest':digest(plan),'scientific_questions':plan['scientific_questions'],
        'status':'complete' if all(s['status']=='complete' for s in summaries.values()) else 'partial',
        'resources':summaries,'detail_requests':0,'enrichment_requests':0,'entity_projection_performed':False,
        'evaluation_performed':False,'review_status':'unreviewed; stop for project-owner review'}
    file=paths['shared']/'run_summary.json'
    frozen=paths['shared']/'run_freeze.json'
    if verify or frozen.exists():
        if file.read_bytes()!=encoded(value):
            raise ValueError('Shared summary regeneration mismatch')
    else:
        write(file,value)
    if value['status']=='complete':
        hashes={str(p.relative_to(paths['shared'])):sha(p) for p in [paths['shared']/'query_plan.json', paths['shared']/'preservation_baseline.json',file]}
        package_hashes={name:sha(paths[name]/'freeze_manifest.json') for name in ('omicsdi','orcs')}
        content={'plan_digest':digest(plan),'shared_files':hashes,'resource_freeze_hashes':package_hashes}
        if frozen.exists():
            if read(frozen)!=content:
                raise ValueError('Shared freeze integrity mismatch')
        elif not verify:
            write(frozen,content)
        else:
            raise ValueError('Complete run is not frozen')
    return value


def execute(root, action, resource):
    """Execute or resume one logical run; frozen packages are only verified."""
    plan=load_plan(root); plan_digest=digest(plan)
    paths=require_preflight(root,plan_digest)
    names=['orcs','omicsdi'] if resource=='all' else [resource]
    for name in names:
        folder=paths[name]; state=read(folder/'resume_state.json')
        if state['status']!='complete':
            if action=='run' and state['status']!='prepared':
                raise ValueError('Existing progress requires explicit resume, not a new run')
            if name=='orcs':
                orcs.run(root,folder,state,plan_digest)
            else:
                omics.run(folder,state,plan_digest)
        export(root,folder,state)
        if state['status']=='failed':
            break
    value=run_summary(root)
    selected=[value['resources'][name]['status'] for name in names]
    return value, 3 if 'failed' in selected else 0 if all(x=='complete' for x in selected) else 2


def compact(value):
    """Keep terminal output bounded by query count, not result/page count."""
    result=copy.deepcopy(value)
    for resource in result.get('resources',{}).values():
        for query in resource.get('queries',{}).values():
            totals=query.pop('reported_totals',[])
            if totals:
                query['last_reported_total']=totals[-1]['count']
    return result


def main(argv=None):
    """Independent CLI; 0 complete/success, 2 partial/usage, 3 failure/preflight gate."""
    parser=argparse.ArgumentParser(description='SQ01 blind native discovery; no details, evaluation, enrichment or entity projection')
    parser.add_argument('action',choices=['prepare','preflight','run','resume','export','verify'])
    parser.add_argument('--resource',choices=['all','orcs','omicsdi'],default='all')
    parser.add_argument('--root',type=Path,default=Path.cwd())
    args=parser.parse_args(argv); root=args.root.resolve()
    try:
        if args.action=='verify':
            plan=load_plan(root); paths=check_directories(root,digest(plan))
            preserved=preservation(root,paths['shared']/'preservation_baseline.json')
            for name in (['orcs','omicsdi'] if args.resource=='all' else [args.resource]):
                state=read(paths[name]/'resume_state.json')
                export(root,paths[name],state,verify=True)
            value=run_summary(root,verify=True)
            print(json.dumps({'verification':'passed','preservation':preserved,'summary':compact(value)},indent=2))
            return 0
        with writer_lock(root):
            if args.action=='prepare':
                value=prepare(root); code=0
            elif args.action=='preflight':
                value=preflight(root); code=0
            elif args.action in ('run','resume'):
                value,code=execute(root,args.action,args.resource)
            else:
                plan=load_plan(root); paths=check_directories(root,digest(plan))
                for name in (['orcs','omicsdi'] if args.resource=='all' else [args.resource]):
                    state=read(paths[name]/'resume_state.json')
                    if name=='omicsdi' and state['status']!='complete':
                        omics.reconcile(paths[name],state)
                        omics.checkpoint(paths[name],state)
                    export(root,paths[name],state)
                value=run_summary(root);code=0
            print(json.dumps(compact(value),indent=2))
            return code
    except (Exception,KeyboardInterrupt) as error:
        print(json.dumps({'status':'failed_or_interrupted','error_type':type(error).__name__,'error':str(error),
            'instruction':'Preserved checkpoints/receipts remain authoritative. Do not reset accounting; inspect the failure before explicit resume.'}),file=sys.stderr)
        return 3


if __name__=='__main__':
    raise SystemExit(main())
