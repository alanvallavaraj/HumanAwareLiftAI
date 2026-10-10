"""Verify every event file; report paired scenario intervals for all fixed contrasts."""
import argparse,csv,gzip,hashlib,json,math,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
METRICS=['all_restricted_wait_900','priority_restricted_wait_900','general_restricted_wait_900','all_horizon_wait','all_boarded_by_900','all_completion_fraction','priority_completion_fraction','general_completion_fraction','physical_stops','distance','dwell_car_ticks']

def main():
 p=argparse.ArgumentParser();p.add_argument('--directory',required=True);p.add_argument('--smoke',action='store_true');a=p.parse_args();out=Path(a.directory)
 rows=list(csv.DictReader((out/'results.csv').open()));protocol=json.loads((out/'protocol.json').read_text());assert len(rows)==protocol['expected_runs']
 cohorts=defaultdict(set);seen=set();blocks={};events=0
 for r in rows:
  key=(int(r['case_index']),r['configuration'],int(r['seed']));assert key not in seen;seen.add(key);cohorts[key[0],key[2]].add(r['arrival_sha256'])
  file=out/'passengers'/f'{key[0]:03d}-{key[1]}-{key[2]:02d}.csv.gz';sums=defaultdict(float);counts=defaultdict(int);boarded=defaultdict(int);complete=defaultdict(int);arrival=[]
  with gzip.open(file,'rt') as stream:
   for q in csv.DictReader(stream):
    at=int(q['arrival_time']);end=int(q['observation_end']);assert end-at>=900
    b=int(q['boarded_time']) if q['boarded_time'] else None;z=int(q['alighted_time']) if q['alighted_time'] else None
    assert b is None or at<=b<end;assert z is None or (b is not None and b<=z<end)
    w=(b if b is not None else end)-at;assert w==int(q['observed_wait'])
    group='priority' if q['priority_requested']=='1' else 'general'
    for g in ['all',group]:
     counts[g]+=1;sums[g]+=min(w,900);boarded[g]+=b is not None;complete[g]+=z is not None
    events+=1;arrival.append((int(q['pid']),int(q['origin']),int(q['destination']),at,q['priority_requested']=='1',q['carrying']=='1'))
  assert hashlib.sha256(json.dumps(arrival,separators=(',',':')).encode()).hexdigest()==r['arrival_sha256']
  for g in ['all','priority','general']:
   assert counts[g]==int(r[g+'_generated']) and boarded[g]==int(r[g+'_boarded']) and complete[g]==int(r[g+'_completed'])
   if counts[g]:assert math.isclose(sums[g]/counts[g],float(r[g+'_restricted_wait_900']),rel_tol=1e-12,abs_tol=1e-12)
  mat=blocks.setdefault((key[0],key[1]),np.zeros((len(METRICS),2)))
  for i,m in enumerate(METRICS):
   v=float(r[m])
   if math.isfinite(v):mat[i]+=[v,1]
 if not a.smoke:assert len(cohorts)==1296
 assert all(len(x)==1 for x in cohorts.values())
 configs=sorted({c for k,c in blocks});keys=sorted({k for k,c in blocks});K=len(keys);weights=np.random.default_rng(20261008).multinomial(K,np.full(K,1/K),size=2000)
 means={};samples={};nvalues={}
 for c in configs:
  mat=np.array([blocks[k,c] for k in keys]);z=mat.sum(axis=0);boot=np.einsum('bk,kmn->bmn',weights,mat);means[c]=z[:,0]/z[:,1];samples[c]=boot[:,:,0]/boot[:,:,1];nvalues[c]=z[:,1]
 # Linear contrasts retain common scenario resamples and all twelve seeds jointly.
 specs=[]
 for c in ['dispatch_only','boarding_only','pickup_exception_only','full_priority','priority_weight_1.4','priority_weight_4.2']:
  specs.append(('ablation_or_weight',c+' vs occupancy_reference',{c:1,'occupancy_reference':-1}))
 for ref in ['collective','distance_only_nearest']:
  specs.append(('reference_comparison','full_priority vs '+ref,{'full_priority':1,ref:-1}))
 for c in ['occupancy_reference','full_priority','collective','distance_only_nearest']:
  specs.append(('dwell_effect','dwell minus zero: '+c,{'dwell_'+c:1,c:-1}))
 for ref in ['occupancy_reference','collective','distance_only_nearest']:
  specs.append(('dwell_priority_effect','dwell full_priority vs '+ref,{'dwell_full_priority':1,'dwell_'+ref:-1}))
  specs.append(('dwell_interaction','change in priority contrast vs '+ref,{'dwell_full_priority':1,'dwell_'+ref:-1,'full_priority':-1,ref:1}))
 for c in ['priority_weight_1.4','priority_weight_4.2']:specs.append(('weight_change',c+' vs -2.8',{c:1,'full_priority':-1}))
 specs.append(('nonadditivity','full effect minus sum of singleton effects',{'full_priority':1,'dispatch_only':-1,'boarding_only':-1,'pickup_exception_only':-1,'occupancy_reference':2}))
 contrast=[]
 for kind,label,terms in specs:
  point=sum(means[c]*w for c,w in terms.items());draw=sum(samples[c]*w for c,w in terms.items());low,high=np.quantile(draw,[.025,.975],axis=0)
  for i,m in enumerate(METRICS):contrast.append({'family':kind,'contrast':label,'metric':m,'difference':float(point[i]),'ci_low':float(low[i]),'ci_high':float(high[i])})
 summary=[{'configuration':c,**{m:float(means[c][i]) for i,m in enumerate(METRICS)},'priority_group_nonempty_runs':int(nvalues[c][1])} for c in configs]
 for name,records in [('controller_outcomes',summary),('paired_intervals',contrast)]:
  with (out/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 report={'runs':len(rows),'passenger_records':events,'matched_arrival_blocks':len(cohorts),'structural_clusters':K,'bootstrap_replicates':2000,'bootstrap_seed':20261008,'source_sha256':protocol['source_sha256'],**({'execution_environment':protocol['execution_environment']} if 'execution_environment' in protocol else {}),'result_sha256':hashlib.sha256((out/'results.csv').read_bytes()).hexdigest(),'checks':'All case event rows reconstructed; arrival hashes, group counts, boarding/alighting order, observation horizons and restricted waits verified. Physical transfer capacity asserted during execution.','interval_note':'Paired fixed-design scenario bootstrap, not building-population or calibration uncertainty. No performance exclusions.'}
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
