"""Controlled priority-rule ablations and an explicit passenger-transfer dwell model."""
from dataclasses import dataclass
import hashlib,json,math
from statistics import mean
from simulator import Lift,Scenario,generate_arrivals,majority_direction,move_lift

@dataclass(frozen=True)
class Policy:
    name:str
    occupancy:bool=True
    dispatch:bool=False
    boarding:bool=False
    exception:bool=False
    bonus:float=2.8
    nearest:bool=False
    fixed_dwell:int=0
    transfer_dwell:int=0

POLICIES=[Policy('occupancy_reference'),Policy('dispatch_only',dispatch=True),
 Policy('boarding_only',boarding=True),Policy('pickup_exception_only',exception=True),
 Policy('full_priority',dispatch=True,boarding=True,exception=True),
 Policy('priority_weight_1.4',dispatch=True,boarding=True,exception=True,bonus=1.4),
 Policy('priority_weight_4.2',dispatch=True,boarding=True,exception=True,bonus=4.2),
 Policy('collective',occupancy=False),Policy('distance_only_nearest',occupancy=False,nearest=True)]
POLICIES += [Policy('dwell_'+p.name,p.occupancy,p.dispatch,p.boarding,p.exception,p.bonus,p.nearest,5,1)
             for p in POLICIES if p.name in ['occupancy_reference','full_priority','collective','distance_only_nearest']]

def jitter(seed,t,floor,lid):
    # Counter-based common random numbers, independent of service/exposure draws.
    x=(seed*7919+t*104729+floor*1009+lid*37+101)&((1<<64)-1)
    x=(x+0x9e3779b97f4a7c15)&((1<<64)-1)
    x=((x^(x>>30))*0xbf58476d1ce4e5b9)&((1<<64)-1)
    x=((x^(x>>27))*0x94d049bb133111eb)&((1<<64)-1)
    return ((x^(x>>31))/2**64)*.02

def choose(lifts,floor,queue,policy,seed,t):
    if policy.nearest:return min(lifts,key=lambda l:(abs(l.floor-floor),l.lid))
    direction=majority_direction(queue);priority=any(p.special_need for p in queue)
    def score(l):
        return abs(l.floor-floor)+(2.5 if l.direction and direction and l.direction!=direction else 0) + (10*max(0,l.load_ratio()-.78) if policy.occupancy else 0) - (policy.bonus*(1-l.load_ratio()) if policy.dispatch and priority else 0)+jitter(seed,t,floor,l.lid)
    return min(lifts,key=score)

def pickup(load,queue,policy):
    if not queue:return False
    if not policy.occupancy:return True
    priority=any(p.special_need for p in queue);space=len(load)<13;ratio=len(load)/13
    if ratio>=.92 and not(policy.exception and priority and space):return False
    if ratio>=.82 and len(queue)>max(1,13-len(load)):return policy.exception and priority
    return True

def selection(lift,post_alighting,queue,policy):
    ordered=sorted(queue,key=lambda p:(not p.special_need,p.arrival_time,p.pid) if policy.boarding else (p.arrival_time,p.pid))
    direction=lift.direction or majority_direction(ordered);post=list(post_alighting);selected=[]
    for p in ordered:
        if len(post)>=lift.capacity:break
        if direction and p.direction!=direction and post:continue
        selected.append(p);post.append(p)
    return selected

def simulate(scenario,policy,seed,arrivals=None):
    arrivals=generate_arrivals(scenario,seed) if arrivals is None else arrivals
    passengers=[p for t in sorted(arrivals) for p in arrivals[t]]
    waiting={f:[] for f in range(scenario.floors)};lifts=[Lift(lid=i) for i in range(scenario.lifts)]
    pending={l.lid:[] for l in lifts};busy_until={l.lid:-1 for l in lifts}
    stops=dwell_ticks=0;end=scenario.duration+900;max_load=0
    for t in range(end):
        for p in arrivals.get(t,[]):waiting[p.origin].append(p)
        if t%8==0:
            for floor,queue in waiting.items():
                if queue:choose(lifts,floor,queue,policy,seed,t).target_floors.add(floor)
        for lift in lifts:
            actions=pending[lift.lid]
            while actions and actions[0][0]<=t:
                when,kind,p=actions.pop(0)
                if kind=='alight':
                    lift.passengers.remove(p);p.alighted_time=when
                else:
                    assert len(lift.passengers)<lift.capacity
                    lift.passengers.append(p);p.boarded_time=when;lift.target_floors.add(p.dest)
            max_load=max(max_load,len(lift.passengers))
            if t<busy_until[lift.lid]:
                dwell_ticks+=1;continue
            if busy_until[lift.lid]==t:
                move_lift(lift,scenario.floors);continue
            queue=waiting[lift.floor];alight=[p for p in lift.passengers if p.dest==lift.floor]
            post=[p for p in lift.passengers if p.dest!=lift.floor]
            requested=lift.floor in lift.target_floors
            take=selection(lift,post,queue,policy) if requested and pickup(post,queue,policy) else []
            # Corrected target lifecycle shared across all extension arms.
            lift.target_floors.discard(lift.floor)
            if alight or take or (requested and queue and pickup(post,queue,policy)):
                stops+=1
                for p in take:queue.remove(p)
                delay=policy.fixed_dwell
                for kind,group in [('alight',alight),('board',take)]:
                    for p in group:
                        delay+=policy.transfer_dwell;pending[lift.lid].append((t+delay,kind,p))
                if policy.fixed_dwell or policy.transfer_dwell:
                    busy_until[lift.lid]=t+delay
                    dwell_ticks+=1
                    continue
                # Zero-delay actions take place before movement, as in the legacy loop.
                for when,kind,p in pending[lift.lid]:
                    if kind=='alight':lift.passengers.remove(p);p.alighted_time=t
                    else:
                        assert len(lift.passengers)<lift.capacity
                        lift.passengers.append(p);p.boarded_time=t;lift.target_floors.add(p.dest)
                pending[lift.lid]=[]
            max_load=max(max_load,len(lift.passengers));assert max_load<=13
            move_lift(lift,scenario.floors)
    row={'generated':len(passengers),'completed':sum(p.alighted_time is not None for p in passengers),'physical_stops':stops,'distance':sum(l.distance for l in lifts),'dwell_car_ticks':dwell_ticks,'max_car_load':max_load,'observation_end':end}
    for name,group in [('all',passengers),('priority',[p for p in passengers if p.special_need]),('general',[p for p in passengers if not p.special_need])]:
        waits=[(p.boarded_time if p.boarded_time is not None else end)-p.arrival_time for p in group]
        row[name+'_generated']=len(group);row[name+'_completed']=sum(p.alighted_time is not None for p in group)
        row[name+'_boarded']=sum(p.boarded_time is not None for p in group)
        row[name+'_restricted_wait_900']=mean([min(w,900) for w in waits]) if group else math.nan
        row[name+'_horizon_wait']=mean(waits) if group else math.nan
        row[name+'_boarded_by_900']=mean([p.boarded_time is not None and p.boarded_time-p.arrival_time<=900 for p in group]) if group else math.nan
        row[name+'_completion_fraction']=row[name+'_completed']/len(group) if group else math.nan
    row['arrival_sha256']=hashlib.sha256(json.dumps([(p.pid,p.origin,p.dest,p.arrival_time,p.special_need,p.carrying) for p in passengers],separators=(',',':')).encode()).hexdigest()
    return row,passengers
