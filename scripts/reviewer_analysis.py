"""Paired structural-scenario bootstrap and partial-identification sensitivity."""
import argparse,csv,json,math
from pathlib import Path
import numpy as np
METRICS=['mean_wait','p95_wait','special_mean_wait','general_mean_wait','door_crowding_rate','fairness_disparity','completion_fraction','passenger_weighted_completed_wait']
KEYS=['floors','lifts','population','traffic','special_share','carrying_share']
def main():
 p=argparse.ArgumentParser();p.add_argument('--results',default='data/full/results.csv');p.add_argument('--out',default='results/reviewer_analysis');p.add_argument('--bootstrap',type=int,default=2000);a=p.parse_args();blocks={};rows=0
 with open(a.results,newline='') as f:
  for r in csv.DictReader(f):
   key=tuple(r[k] for k in KEYS);c=r['controller'];rows+=1;z=blocks.setdefault((key,c),np.zeros((8,2)))
   for i,m in enumerate(METRICS[:6]):
    v=float(r[m])
    if math.isfinite(v):z[i]+=[v,1]
   completed=float(r['completed']);generated=float(r['generated']);z[6]+=[completed,generated];z[7]+=[float(r['mean_wait'])*completed,completed]
 keys=sorted({k for k,c in blocks});controllers=sorted({c for k,c in blocks});K=len(keys);assert rows==279936 and K==972
 weights=np.random.default_rng(20261008).multinomial(K,np.full(K,1/K),size=a.bootstrap);estimates={};draws={}
 for c in controllers:
  mat=np.array([blocks[k,c] for k in keys]);base=mat.sum(axis=0);boot=np.einsum('bk,kmn->bmn',weights,mat);v=base[:,0]/base[:,1];draws[c]=boot[:,:,0]/boot[:,:,1];estimates[c]={m:float(v[i]) for i,m in enumerate(METRICS)};estimates[c]['ratio_of_group_mean_waits']=float(v[2]/v[3])
 contrasts=[];ref='collective'
 for c in controllers:
  if c==ref:continue
  for i,m in enumerate(METRICS):
   lo,hi=np.quantile(draws[c][:,i]-draws[ref][:,i],[.025,.975]);rl,rh=np.quantile(100*(draws[ref][:,i]-draws[c][:,i])/draws[ref][:,i],[.025,.975]);contrasts.append(dict(controller=c,reference=ref,metric=m,difference=estimates[c][m]-estimates[ref][m],ci_low=float(lo),ci_high=float(hi),relative_reduction_percent=100*(estimates[ref][m]-estimates[c][m])/estimates[ref][m],reduction_ci_low=float(rl),reduction_ci_high=float(rh)))
 sensitivity=[]
 for c,v in estimates.items():
  f=v['completion_fraction'];known=v['passenger_weighted_completed_wait']*f;sensitivity.append(dict(controller=c,finite_horizon_lower_bound=known,finite_horizon_upper_bound=known+(1-f)*4499,**{f'assumed_incomplete_wait_{u}':known+(1-f)*u for u in [0,500,1000,1500,2000]}))
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 for name,data in [('controller_outcomes',[{'controller':c,**v} for c,v in estimates.items()]),('paired_cluster_intervals',contrasts),('censoring_sensitivity',sensitivity)]:
  with (out/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 meta=dict(rows=rows,structural_clusters=K,bootstrap_replicates=a.bootstrap,seed=20261008,cluster_keys=KEYS,noise_levels_and_seeds_resampled_together=True,method='Paired percentile bootstrap of structural scenarios, retaining all three noise levels and twelve seeds jointly. Arithmetic finite-value run means except passenger-weighted completion and completed wait. Intervals describe design-scenario composition sensitivity, not physical validity or random-building population inference.',missing_wait_note='Raw CSV lacks individual unboarded arrival/end-time records. Bounds and common-value imputation are sensitivity analyses, not recovered censoring-aware estimates. Upper bound applies to waiting accrued by the finite horizon, not eventual waiting beyond it.',estimates=estimates)
 (out/'analysis_metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
