"""Three vector figures of the fixed corrected-campaign contrasts; no controller selection."""
import argparse,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--directory',default='results/aei_extension');a=p.parse_args();root=Path(__file__).resolve().parents[1];data=root/a.directory;out=root/'publishing/figures';out.mkdir(exist_ok=True)
with (data/'paired_intervals.csv').open() as f:rows=list(csv.DictReader(f))
def contrast(label,metric):return next(x for x in rows if x['contrast']==label and x['metric']==metric)
def vals(labels,metric):
 r=[contrast(l,metric) for l in labels];v=np.array([float(x['difference']) for x in r]);return v,np.array([v-[float(x['ci_low']) for x in r],[float(x['ci_high']) for x in r]-v])
def save(fig,name):
 fig.savefig(out/(name+'.pdf'),bbox_inches='tight');fig.savefig(out/(name+'.png'),dpi=300,bbox_inches='tight');plt.close(fig)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
groups=[('all_restricted_wait_900','All arrivals'),('priority_restricted_wait_900','Priority requests'),('general_restricted_wait_900','General requests')]
fig,axes=plt.subplots(1,3,figsize=(11,4))
labels=[x+' vs occupancy_reference' for x in ['dispatch_only','boarding_only','pickup_exception_only','full_priority']]
for ax,(metric,name) in zip(axes,groups):
 v,e=vals(labels,metric);ax.errorbar(v,np.arange(4),xerr=e,fmt='o',capsize=3,color='#32658b');ax.set_yticks(range(4),['Dispatch','Boarding','Exception','Full']);ax.invert_yaxis();ax.axvline(0,color='.6',lw=1);ax.set_title(name);ax.set_xlabel('Difference in restricted wait\n(model time units)')
fig.tight_layout();save(fig,'aei_ablation')
fig,ax=plt.subplots(figsize=(8,4));x=np.arange(3)
for shift,label,color in [(-.12,'No dwell','#32658b'),(.12,'Dwell: 5 + 1 per transfer','#b77a23')]:
 labels=['full_priority vs collective' if shift<0 else 'dwell full_priority vs collective']*3
 v=[];lo=[];hi=[]
 for lab,(metric,_) in zip(labels,groups):
  z=contrast(lab,metric);q=float(z['difference']);v.append(q);lo.append(q-float(z['ci_low']));hi.append(float(z['ci_high'])-q)
 ax.errorbar(x+shift,v,yerr=[lo,hi],fmt='o',capsize=4,label=label,color=color)
ax.set_xticks(x,[n for _,n in groups]);ax.set_ylabel('Full priority minus collective\n(restricted wait, model time units)');ax.axhline(0,color='.6',lw=1);ax.legend(frameon=False);fig.tight_layout();save(fig,'aei_dwell')
fig,axes=plt.subplots(1,3,figsize=(11,3.8));labels=['priority_weight_1.4 vs occupancy_reference','full_priority vs occupancy_reference','priority_weight_4.2 vs occupancy_reference']
for ax,(metric,name) in zip(axes,groups):
 v,e=vals(labels,metric);ax.errorbar([1.4,2.8,4.2],v,yerr=e,fmt='o-',capsize=3,color='#32658b');ax.axhline(0,color='.6',lw=1);ax.set_title(name);ax.set_xlabel('Priority bonus magnitude');ax.set_xticks([1.4,2.8,4.2]);ax.set_ylabel('Restricted-wait difference\n(model time units)')
fig.tight_layout();save(fig,'aei_weights')
print('Wrote three corrected-campaign figures; intervals from all fixed scenario contrasts.')
