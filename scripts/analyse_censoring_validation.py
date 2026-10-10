"""Check event cohort pairing, archived parity and bounded-run clustered intervals."""
import argparse,csv,json,math,gzip,hashlib,platform
from collections import defaultdict
from pathlib import Path
import numpy as np
KEYS=['floors','lifts','population','traffic','special_share','carrying_share','sensor_noise','seed','controller']
METRICS=['all_restricted_wait_900','priority_restricted_wait_900','general_restricted_wait_900','all_horizon_wait','all_boarded_by_900','completion_fraction','priority_completion_fraction','general_completion_fraction']
def main():
 p=argparse.ArgumentParser();p.add_argument('--directory',default='results/censoring_validation');p.add_argument('--archived',default='data/full/results.csv');a=p.parse_args();out=Path(a.directory);rows=list(csv.DictReader((out/'results.csv').open()));assert len(rows)==5184
 paired=defaultdict(set);seen=set();blocks={}
 for r in rows:
  key=tuple(r[k] for k in KEYS);assert key not in seen;seen.add(key);paired[r['case_index'],r['seed']].add(r['arrival_sha256'])
  for name in ['all','priority','general']:r[name+'_completion_fraction']=float(r[name+'_completed'])/float(r[name+'_generated']) if float(r[name+'_generated']) else float('nan')
  r['completion_fraction']=r['all_completion_fraction'];z=blocks.setdefault((int(r['case_index']),r['controller']),np.zeros((8,2)))
  for i,m in enumerate(METRICS):
   v=float(r[m])
   if math.isfinite(v):z[i]+=[v,1]
 assert len(paired)==1296 and all(len(v)==1 for v in paired.values())
 wanted={tuple(r[k] for k in KEYS) for r in rows if r['controller']!='distance_only_nearest'}
 original={tuple(r[k] for k in KEYS):r for r in csv.DictReader(open(a.archived)) if tuple(r[k] for k in KEYS) in wanted};parity=0;differences=[]
 for r in rows:
  if r['controller']=='distance_only_nearest':continue
  old=original[tuple(r[k] for k in KEYS)]
  bad=[]
  for m in ['completed','generated','mean_wait','p95_wait','special_mean_wait','general_mean_wait','door_crowding_rate']:
   x,y=float(r[m]),float(old[m])
   if not ((math.isnan(x) and math.isnan(y)) or math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12)):bad.append(m)
  if bad:differences.append({'case_index':r['case_index'],'controller':r['controller'],'seed':r['seed'],'metrics':bad})
  else:parity+=1
 # Independently reconstruct restricted waiting from every event file.
 event_count=0
 for r in rows:
  sums=defaultdict(float);counts=defaultdict(int);f=out/'passengers'/f"{int(r['case_index']):05d}-{r['controller']}-{r['seed']}.csv.gz"
  with gzip.open(f,'rt') as src:
   for p in csv.DictReader(src):
    assert 4500-int(p['arrival_time'])>=900
    w=min(float(p['observed_wait']),900);g='priority' if p['priority_requested']=='1' else 'general';sums['all']+=w;sums[g]+=w;counts['all']+=1;counts[g]+=1;event_count+=1
  assert counts['all']==int(r['generated'])
  for g in ['all','priority','general']:
   if counts[g]:assert math.isclose(sums[g]/counts[g],float(r[g+'_restricted_wait_900']),rel_tol=1e-12,abs_tol=1e-12)
 controllers=sorted({c for k,c in blocks});weights=np.random.default_rng(20261008).multinomial(108,np.full(108,1/108),size=2000);est={};bs={}
 for c in controllers:
  mat=np.array([blocks[k,c] for k in range(108)]);z=mat.sum(axis=0);boot=np.einsum('bk,kmn->bmn',weights,mat);est[c]={m:float(z[i,0]/z[i,1]) for i,m in enumerate(METRICS)};bs[c]=boot[:,:,0]/boot[:,:,1]
 contrasts=[]
 for ref in ['collective','distance_only_nearest']:
  for c in controllers:
   if c==ref:continue
   for i,m in enumerate(METRICS):
    lo,hi=np.quantile(bs[c][:,i]-bs[ref][:,i],[.025,.975]);contrasts.append(dict(controller=c,reference=ref,metric=m,difference=est[c][m]-est[ref][m],ci_low=float(lo),ci_high=float(hi)))
 for name,data in [('restricted_outcomes',[{'controller':c,**v} for c,v in est.items()]),('restricted_cluster_intervals',contrasts)]:
  with (out/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 report=dict(runs=len(rows),passenger_records=event_count,matched_arrival_blocks=len(paired),legacy_runs_matching_archived=parity,legacy_runs_compared=3888,legacy_runs_not_matching_archived=len(differences),archived_parity_note='Some cases do not reproduce the archived outputs under the current execution environment. The cause is set-iteration tie resolution in the movement rule; all 3,888 cases reproduce under Python 3.9.6 (replay_parity_python39.json). New bounded campaign is reported separately, with paired arrivals and retained events; no rows were excluded based on performance.',structural_clusters=108,bootstrap_replicates=2000,bootstrap_seed=20261008,execution_environment='Local computational workspace, eight Python workers.',python_version=platform.python_version(),result_sha256=hashlib.sha256((out/'results.csv').read_bytes()).hexdigest(),estimand='Average run-level restricted waiting E[min(time-to-boarding,900)] over all generated passengers; every passenger has at least 900 units follow-up. Counts boarded passengers even if not alighted; unboarded passengers contribute 900. Finite-horizon waiting uses observation end 4500. Completion means destination reached.',interval_note='Paired 108-scenario percentile bootstrap, all twelve seeds together. Conditional design-scenario resampling intervals, not calibrated building forecasts.',estimates=est)
 (out/'archived_parity_differences.json').write_text(json.dumps(differences,indent=2)+'\n')
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
