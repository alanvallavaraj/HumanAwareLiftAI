#!/usr/bin/env python3
"""Rebuild the three manuscript figures from retained analysis tables."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'publishing/figures'; OUT.mkdir(exist_ok=True)
def rows(path):
 with (ROOT/path).open() as f:return list(csv.DictReader(f))
def save(fig,name):
 fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight')
 fig.savefig(OUT/(name+'.png'),dpi=300,bbox_inches='tight');plt.close(fig)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
r=[x for x in rows('results/reviewer_analysis/paired_cluster_intervals.csv') if x['controller']=='layered_access_stability' and x['reference']=='collective']
fig,ax=plt.subplots(1,2,figsize=(9,3.8),gridspec_kw={'width_ratios':[2,1]})
for a,metrics,labels,scale in [(ax[0],['mean_wait','special_mean_wait','general_mean_wait'],['All completed trips','Priority requests','General requests'],1),(ax[1],['completion_fraction'],['Completion'],100)]:
 vals=[];lo=[];hi=[]
 for m in metrics:
  x=next(x for x in r if x['metric']==m);v=float(x['difference'])*scale;vals.append(v);lo.append(v-float(x['ci_low'])*scale);hi.append(float(x['ci_high'])*scale-v)
 a.errorbar(vals,np.arange(len(vals)),xerr=[lo,hi],fmt='o',color='#224e76',capsize=4);a.axvline(0,color='.6',lw=1);a.set_yticks(range(len(vals)),labels);a.invert_yaxis();a.set_xlabel('Difference (model time units)' if scale==1 else 'Difference (percentage points)')
fig.tight_layout();save(fig,'conditional_contrasts')
d=rows('results/censoring_validation/restricted_outcomes.csv'); order=['collective','distance_only_nearest','occupancy_aware','access_priority'];d={x['controller']:x for x in d};labels=['Collective','Distance-only','Occupancy','Priority'];colors=['#3b6c94','#d29a30','#578768']
fig,ax=plt.subplots(figsize=(8,4));x=np.arange(4)
for j,(m,label) in enumerate([('all_restricted_wait_900','All arrivals'),('priority_restricted_wait_900','Priority requests'),('general_restricted_wait_900','General requests')]):
 ax.bar(x+(j-1)*.25,[float(d[c][m]) for c in order],.25,label=label,color=colors[j])
ax.set_xticks(x,labels);ax.set_ylabel('Mean restricted wait (model time units)');ax.set_ylim(0,400);ax.legend(frameon=False,ncols=3,loc='upper center');fig.tight_layout();save(fig,'restricted_waits')
fig,ax=plt.subplots(figsize=(8,4))
for j,(m,label) in enumerate([('completion_fraction','All arrivals'),('priority_completion_fraction','Priority requests'),('general_completion_fraction','General requests')]):
 ax.bar(x+(j-1)*.25,[100*float(d[c][m]) for c in order],.25,label=label,color=colors[j])
ax.set_xticks(x,labels);ax.set_ylabel('Destination completion (%)');ax.set_ylim(0,115);ax.legend(frameon=False,ncols=3,loc='upper center');fig.tight_layout();save(fig,'completion_by_group')
print('Wrote three vector PDF figures and 300 dpi PNG previews.')
