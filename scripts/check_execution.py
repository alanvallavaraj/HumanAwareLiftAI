"""Rerun one archived case per controller and compare every output metric."""
import argparse,csv,json,math,sys
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from simulator import Scenario,simulate

def main():
 p=argparse.ArgumentParser();p.add_argument('--results',default='data/full/results.csv');p.add_argument('--out',default='results/execution_spot_checks.json');a=p.parse_args();rows={}
 with open(a.results) as f:
  for r in csv.DictReader(f):
   rows.setdefault(r['controller'],r)
   if len(rows)==8:break
 if len(rows)!=8:raise SystemExit('Expected eight controllers')
 checks={}
 for c,r in rows.items():
  sc=Scenario(floors=int(r['floors']),lifts=int(r['lifts']),population=int(r['population']),traffic=r['traffic'],special_share=float(r['special_share']),carrying_share=float(r['carrying_share']),sensor_noise=float(r['sensor_noise']),duration=3600)
  v=asdict(simulate(sc,c,int(r['seed'])));bad=[]
  for k,x in v.items():
   y=float(r[k])
   if not(math.isnan(x) and math.isnan(y)) and not math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12):bad.append(k)
  checks[c]={'seed':r['seed'],'matching_all_metrics':not bad,'differences':bad}
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(checks,indent=2)+'\n')
 print('PASS' if all(x['matching_all_metrics'] for x in checks.values()) else 'FAIL',out)
 if not all(x['matching_all_metrics'] for x in checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
