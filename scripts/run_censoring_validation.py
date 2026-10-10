"""Bounded event-recording replication; archived simulator calculation is unchanged."""
import argparse,csv,gzip,hashlib,json,sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from itertools import product
from pathlib import Path
from statistics import mean
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import simulator as legacy
BASE_CONTROLLER=legacy.Controller
BASE_SUMMARISE=legacy.summarise
CONTROLLERS=['collective','occupancy_aware','access_priority','distance_only_nearest']
class DistinctNearest(BASE_CONTROLLER):
 def choose_lift(self,lifts,floor,waiting,now,scenario,rng):
  if self.name=='distance_only_nearest':return min(lifts,key=lambda l:(abs(l.floor-floor),l.lid))
  return super().choose_lift(lifts,floor,waiting,now,scenario,rng)
def run(payload):
 index,parameters,c,seed,out=payload;sc=legacy.Scenario(**parameters);capture={}
 def collect(passengers,completed,lifts,guidance):
  original=BASE_SUMMARISE(passengers,completed,lifts,guidance);groups={'all':passengers,'priority':[p for p in passengers if p.special_need],'general':[p for p in passengers if not p.special_need]}
  row={'case_index':index,'controller':c,'seed':seed,**parameters,**asdict(original)}
  for name,ps in groups.items():
   row[name+'_generated']=len(ps);row[name+'_completed']=sum(p.alighted_time is not None for p in ps);row[name+'_boarded']=sum(p.boarded_time is not None for p in ps)
   observed=[(p.boarded_time if p.boarded_time is not None else 4500)-p.arrival_time for p in ps]
   row[name+'_restricted_wait_900']=mean([min(w,900) for w in observed]) if ps else float('nan')
   row[name+'_horizon_wait']=mean(observed) if ps else float('nan')
   row[name+'_boarded_by_900']=mean([p.boarded_time is not None and p.boarded_time-p.arrival_time<=900 for p in ps]) if ps else float('nan')
  arrival=[(p.pid,p.origin,p.dest,p.arrival_time,p.special_need,p.carrying) for p in passengers]
  row['arrival_sha256']=hashlib.sha256(json.dumps(arrival,separators=(',',':')).encode()).hexdigest()
  target=Path(out)/'passengers'/f'{index:05d}-{c}-{seed}.csv.gz';target.parent.mkdir(parents=True,exist_ok=True)
  with gzip.open(target,'wt',newline='') as f:
   w=csv.writer(f);w.writerow(['pid','origin','destination','arrival_time','priority_requested','carrying','boarded_time','alighted_time','observation_end','observed_wait','boarding_observed'])
   for p in passengers:w.writerow([p.pid,p.origin,p.dest,p.arrival_time,int(p.special_need),int(p.carrying),p.boarded_time if p.boarded_time is not None else '',p.alighted_time if p.alighted_time is not None else '',4500,(p.boarded_time if p.boarded_time is not None else 4500)-p.arrival_time,int(p.boarded_time is not None)])
  capture.update(row);return original
 legacy.Controller=DistinctNearest;legacy.summarise=collect
 try:legacy.simulate(sc,c,seed)
 finally:legacy.Controller=BASE_CONTROLLER;legacy.summarise=BASE_SUMMARISE
 return capture
def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=8);p.add_argument('--seeds',type=int,default=12);p.add_argument('--out',default='results/censoring_validation');p.add_argument('--limit',type=int,default=0);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 cases=[]
 for index,((floors,lifts),population,traffic,share) in enumerate(product([(8,2),(16,4),(32,8)],[200,800,2000],['up_peak','down_peak','lunch','mixed'],[.02,.08,.15])):
  parameters=dict(floors=floors,lifts=lifts,population=population,traffic=traffic,special_share=share,carrying_share=.20,sensor_noise=.08,duration=3600)
  for seed,c in product(range(a.seeds),CONTROLLERS):cases.append((index,parameters,c,seed,str(out)))
 if a.limit:cases=cases[:a.limit]
 protocol={'case_count':len(cases),'structural_scenarios':108,'seeds':a.seeds,'controllers':CONTROLLERS,'arrival_horizon':3600,'observation_horizon':4500,'restricted_wait_horizon':900,'stopping_rule':'One execution of the declared grid; no tuning or reruns based on performance. Smoke checks are separate.','design_note':'Matched arrival streams. Same archived movement, no door dwell or physical dynamics. Distinct distance-only nearest-car baseline is a transparent reference rule, not a reproduction of an entire published system. Fixed carrying/noise levels; diagonal floor/lift combinations restrict generality. Original accessibility/stability accounting is retained only to reproduce archived code; no comfort claims or disability-instability inference is made.'}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 with (out/'results.csv').open('w',newline='') as f:
  writer=None
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for n,row in enumerate(pool.map(run,cases,chunksize=1),1):
    if writer is None:writer=csv.DictWriter(f,fieldnames=list(row));writer.writeheader()
    writer.writerow(row)
    if n%100==0:print(n,'/',len(cases),flush=True)
 print('Completed',len(cases),'cases',flush=True)
if __name__=='__main__':main()
