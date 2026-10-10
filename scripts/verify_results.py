"""Check completeness, uniqueness and published aggregate means; stdlib only."""
import argparse,csv,json,math,sys
from collections import Counter,defaultdict
from pathlib import Path
KEYS=["seed","floors","lifts","population","traffic","special_share","carrying_share","sensor_noise","controller"]
def main():
 p=argparse.ArgumentParser();p.add_argument("--results",default="data/full/results.csv");p.add_argument("--out",default="results/reproduction_check.json");a=p.parse_args()
 root=Path(__file__).resolve().parents[1]
 expected=list(csv.DictReader((root/"results/full_controller_means.csv").open()))
 metrics=[k for k in expected[0] if k not in {"controller","runs"}]
 sums=defaultdict(Counter); ns=defaultdict(Counter); counts=Counter();seen=set();complete=Counter(); generated=Counter()
 with open(a.results,newline="") as f:
  for r in csv.DictReader(f):
   key=tuple(r[k] for k in KEYS)
   if key in seen: raise SystemExit("Duplicate experiment key")
   seen.add(key);c=r["controller"];counts[c]+=1
   complete[c]+=int(float(r["completed"]));generated[c]+=int(float(r["generated"]))
   for m in metrics:
    v=float(r[m])
    if math.isfinite(v):sums[c][m]+=v;ns[c][m]+=1
 sys.path.insert(0,str(root/"scripts"))
 from run_experiments import iter_jobs
 expected_keys={tuple(str(v) for v in [seed,sc.floors,sc.lifts,sc.population,sc.traffic,sc.special_share,sc.carrying_share,sc.sensor_noise,c]) for sc,c,seed in iter_jobs("full")}
 errors=[]
 if seen!=expected_keys:errors.append("factorial grid keys")
 means={c:{m:sums[c][m]/ns[c][m] for m in metrics} for c in counts}
 for r in expected:
  c=r["controller"]
  if counts[c]!=int(r["runs"]):errors.append(c+" run count")
  for m in metrics:
   if abs(means[c][m]-float(r[m]))>0.000051:errors.append(c+" "+m)
 if sum(counts.values())!=279936 or len(counts)!=8:errors.append("full grid size")
 report={"passed":not errors,"errors":errors,"rows":sum(counts.values()),"runs":dict(counts),"means":means,"completion_fraction":{c:complete[c]/generated[c] for c in counts},"note":"Completion fractions are passenger-weighted; waits in archived outputs describe completed trips only."}
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
 print("PASS" if not errors else "FAIL",sum(counts.values()),"rows; report:",out)
 if errors:raise SystemExit(1)
if __name__=="__main__":main()
