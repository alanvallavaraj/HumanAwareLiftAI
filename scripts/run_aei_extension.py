"""Execute the immutable bounded priority/dwell campaign; resume only missing cases."""
import argparse,csv,gzip,json,sys,hashlib,platform,os,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from dataclasses import asdict
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from aei_extension import POLICIES,simulate
from simulator import Scenario

def execute(payload):
    i,parameters,policy,seed,out=payload;root=Path(out);stem=f'{i:03d}-{policy.name}-{seed:02d}';done=root/'cases'/f'{stem}.json'
    if done.exists():
        row=json.loads(done.read_text())
        if (root/'passengers'/f'{stem}.csv.gz').exists():return row
        raise RuntimeError('Case result exists without passenger events: '+stem)
    row,ps=simulate(Scenario(**parameters),policy,seed)
    row={'case_index':i,'configuration':policy.name,'seed':seed,**parameters,**asdict(policy),**row};row.pop('name')
    event=root/'passengers'/f'{stem}.csv.gz';event.parent.mkdir(parents=True,exist_ok=True);tmp=event.with_suffix('.tmp')
    with gzip.open(tmp,'wt',newline='') as f:
        w=csv.writer(f);w.writerow(['pid','origin','destination','arrival_time','priority_requested','carrying','boarded_time','alighted_time','observation_end','observed_wait'])
        for p in ps:w.writerow([p.pid,p.origin,p.dest,p.arrival_time,int(p.special_need),int(p.carrying),p.boarded_time if p.boarded_time is not None else '',p.alighted_time if p.alighted_time is not None else '',row['observation_end'],(p.boarded_time if p.boarded_time is not None else row['observation_end'])-p.arrival_time])
    os.replace(tmp,event);done.parent.mkdir(parents=True,exist_ok=True);tmp=done.with_suffix('.tmp');tmp.write_text(json.dumps(row)+'\n');os.replace(tmp,done);return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=8);p.add_argument('--smoke',action='store_true');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    cases=[]
    for i,((floors,lifts),pop,traffic,share) in enumerate(product([(8,2),(16,4),(32,8)],[200,800,2000],['up_peak','down_peak','lunch','mixed'],[.02,.08,.15])):
        params=dict(floors=floors,lifts=lifts,population=pop,traffic=traffic,special_share=share,carrying_share=.20,sensor_noise=.08,duration=3600)
        for policy,seed in product(POLICIES,range(12)):cases.append((i,params,policy,seed,str(out)))
    if a.smoke:cases=[x for x in cases if x[0] in [0,107] and x[3]==0]
    protocol={'expected_runs':len(cases),'scenario_count':2 if a.smoke else 108,'seeds':1 if a.smoke else 12,'configurations':[asdict(p) for p in POLICIES],'execution_environment':os.environ.get('LIFT_EXECUTION_ENVIRONMENT','Local'),'source_commit':(Path(__file__).resolve().parents[1]/'RUN_SOURCE_COMMIT').read_text().strip() if (Path(__file__).resolve().parents[1]/'RUN_SOURCE_COMMIT').exists() else None,'python':platform.python_version(),'source_sha256':{str(q.relative_to(Path(__file__).resolve().parents[1])):hashlib.sha256(q.read_bytes()).hexdigest() for q in [Path(__file__),Path(__file__).resolve().parents[1]/'src/aei_extension.py',Path(__file__).resolve().parents[1]/'src/simulator.py']},'model_revision':'served targets cleared; common counter-based dispatch jitter; explicit transfer completion times; no synthetic comfort accounting','stopping_rule':'Fixed grid only. Resume missing cases only. No performance-driven reruns.'}
    target=out/'protocol.json'
    if target.exists():
        old=json.loads(target.read_text());assert old['source_sha256']==protocol['source_sha256'] and old['expected_runs']==protocol['expected_runs']
    else:target.write_text(json.dumps(protocol,indent=2)+'\n')
    manifest=[{'case_index':i,'parameters':params,'configuration':pol.name,'seed':seed} for i,params,pol,seed,_ in cases]
    (out/'manifest.json').write_text(json.dumps(manifest,separators=(',',':'))+'\n')
    rows=[];started=time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for n,row in enumerate(pool.map(execute,cases,chunksize=1),1):
            rows.append(row)
            if n%100==0:print(f'{n}/{len(cases)} completed; elapsed {time.time()-started:.1f}s',flush=True)
    tmp=out/'results.csv.tmp'
    with tmp.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    os.replace(tmp,out/'results.csv');print('COMPLETE',len(rows),'cases',flush=True)
if __name__=='__main__':main()
