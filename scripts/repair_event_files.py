"""Single, manifest-driven recovery of event files; aggregate rows never change."""
import json,math,sys
from pathlib import Path
from run_censoring_validation import run
out=Path(sys.argv[1] if len(sys.argv)>1 else 'results/censoring_validation')
errors=json.loads((out/'event_file_errors.json').read_text());records=[]
for e in errors:
 r=e['row'];params={k:int(r[k]) for k in ['floors','lifts','population','duration']};params.update({k:float(r[k]) for k in ['special_share','carrying_share','sensor_noise']});params['traffic']=r['traffic']
 new=run((int(r['case_index']),params,r['controller'],int(r['seed']),str(out)))
 for k,x in new.items():
  if isinstance(x,(int,float)):
   y=float(r[k]);assert (math.isnan(x) and math.isnan(y)) or math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12),(k,x,y)
  else:assert str(x)==r[k],k
 records.append({'case_index':r['case_index'],'controller':r['controller'],'seed':r['seed'],'reason':'Event file row-count mismatch','all_aggregate_metrics_identical':True})
(out/'event_recovery.json').write_text(json.dumps(records,indent=2)+'\n');print('Recovered',len(records),'files; aggregates unchanged')
