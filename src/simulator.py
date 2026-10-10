from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from statistics import mean
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class Passenger:
    pid: int
    origin: int
    dest: int
    arrival_time: int
    special_need: bool
    carrying: bool
    boarded_time: Optional[int] = None
    alighted_time: Optional[int] = None
    failed_pickups: int = 0
    guided_away: int = 0

    @property
    def direction(self) -> int:
        return 1 if self.dest > self.origin else -1


@dataclass
class Lift:
    lid: int
    floor: int = 0
    direction: int = 0
    capacity: int = 13
    passengers: List[Passenger] = field(default_factory=list)
    target_floors: set = field(default_factory=set)
    distance: int = 0
    stops: int = 0
    unnecessary_stops: int = 0
    failed_pickup_events: int = 0
    door_crowding_events: int = 0
    jerk_exposure: float = 0.0
    stability_exposure: float = 0.0
    adaptive_slowdowns: int = 0
    energy_proxy: float = 0.0

    def load_ratio(self) -> float:
        return len(self.passengers) / self.capacity

    def has_space(self) -> bool:
        return len(self.passengers) < self.capacity


@dataclass(frozen=True)
class Scenario:
    floors: int
    lifts: int
    population: int
    traffic: str
    special_share: float
    carrying_share: float
    sensor_noise: float
    duration: int = 3600
    arrival_rate_scale: float = 1.0


@dataclass
class RunMetrics:
    completed: int
    generated: int
    mean_wait: float
    p95_wait: float
    mean_journey: float
    failed_pickup_rate: float
    unnecessary_stop_rate: float
    door_crowding_rate: float
    energy_proxy: float
    utilisation_imbalance: float
    special_mean_wait: float
    general_mean_wait: float
    fairness_disparity: float
    stability_risk: float
    jerk_exposure: float
    adaptive_slowdowns: int
    guidance_events: int
    score: float


def percentile(values: List[float], p: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    k = (len(xs) - 1) * p
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - k) + xs[hi] * (k - lo)


def traffic_weight(t: int, duration: int, traffic: str) -> float:
    x = t / max(duration, 1)
    if traffic == "up_peak":
        return 2.2 * math.exp(-((x - 0.18) / 0.18) ** 2) + 0.35
    if traffic == "down_peak":
        return 2.2 * math.exp(-((x - 0.78) / 0.18) ** 2) + 0.35
    if traffic == "lunch":
        return 1.2 * math.exp(-((x - 0.50) / 0.22) ** 2) + 0.55
    return 0.85 + 0.45 * math.sin(2 * math.pi * x) ** 2


def sample_origin_dest(rng: random.Random, floors: int, traffic: str) -> Tuple[int, int]:
    if traffic == "up_peak":
        origin = 0 if rng.random() < 0.82 else rng.randrange(floors)
        dest = rng.randrange(1, floors) if origin == 0 else rng.randrange(floors)
    elif traffic == "down_peak":
        origin = rng.randrange(1, floors) if rng.random() < 0.82 else rng.randrange(floors)
        dest = 0 if origin != 0 else rng.randrange(1, floors)
    elif traffic == "lunch":
        origin = rng.randrange(floors)
        dest = rng.randrange(floors)
    else:
        if rng.random() < 0.45:
            origin = 0
            dest = rng.randrange(1, floors)
        elif rng.random() < 0.75:
            origin = rng.randrange(1, floors)
            dest = 0
        else:
            origin = rng.randrange(floors)
            dest = rng.randrange(floors)
    while dest == origin:
        dest = rng.randrange(floors)
    return origin, dest


def generate_arrivals(s: Scenario, seed: int) -> Dict[int, List[Passenger]]:
    rng = random.Random(seed)
    arrivals: Dict[int, List[Passenger]] = {}
    base_rate = (s.population / 650.0) * 0.24 * s.arrival_rate_scale
    pid = 0
    for t in range(s.duration):
        lam = base_rate * traffic_weight(t, s.duration, s.traffic)
        n = poisson(rng, lam)
        for _ in range(n):
            origin, dest = sample_origin_dest(rng, s.floors, s.traffic)
            p = Passenger(
                pid=pid,
                origin=origin,
                dest=dest,
                arrival_time=t,
                special_need=rng.random() < s.special_share,
                carrying=rng.random() < s.carrying_share,
            )
            arrivals.setdefault(t, []).append(p)
            pid += 1
    return arrivals


def poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    if lam > 15:
        return max(0, int(rng.gauss(lam, math.sqrt(lam)) + 0.5))
    l = math.exp(-lam)
    k = 0
    p = 1.0
    while p > l:
        k += 1
        p *= rng.random()
    return k - 1


def estimate_stability(lift: Lift, carrying_share: float, rng: random.Random, sensor_noise: float) -> float:
    n = len(lift.passengers)
    if n == 0:
        return 0.0
    carrying = sum(1 for p in lift.passengers if p.carrying)
    special = sum(1 for p in lift.passengers if p.special_need)
    load_component = lift.load_ratio() ** 1.7
    asymmetry = rng.betavariate(2.0, 5.0) * (0.45 + 0.55 * load_component)
    carrying_component = (carrying / n) * 0.35
    special_component = (special / n) * 0.18
    noise = rng.gauss(0.0, sensor_noise)
    return max(0.0, min(1.0, load_component * 0.35 + asymmetry + carrying_component + special_component + noise))


class Controller:
    def __init__(self, name: str):
        self.name = name

    def supports_occupancy(self) -> bool:
        return self.name in {"occupancy_aware", "access_priority", "stability_aware", "human_aware", "layered_access_stability", "oracle_upper"}

    def supports_access(self) -> bool:
        return self.name in {"access_priority", "human_aware", "layered_access_stability", "oracle_upper"}

    def supports_stability(self) -> bool:
        return self.name in {"stability_aware", "human_aware", "layered_access_stability", "oracle_upper"}

    def supports_guidance(self) -> bool:
        return self.name in {"human_aware", "oracle_upper"}

    def choose_lift(
        self,
        lifts: List[Lift],
        floor: int,
        waiting: List[Passenger],
        now: int,
        scenario: Scenario,
        rng: random.Random,
    ) -> Lift:
        direction = majority_direction(waiting)
        best_lift = lifts[0]
        best_score = float("inf")
        special_waiting = any(p.special_need for p in waiting)
        for lift in lifts:
            distance = abs(lift.floor - floor)
            direction_penalty = 0
            if lift.direction and direction and lift.direction != direction:
                direction_penalty = 2.5
            load_penalty = 0.0
            if self.supports_occupancy():
                load_penalty = 10.0 * max(0.0, lift.load_ratio() - 0.78)
            access_bonus = 0.0
            if self.supports_access() and special_waiting:
                access_bonus = -2.8 * (1.0 - lift.load_ratio())
            stability_penalty = 0.0
            if self.supports_stability():
                predicted = lift.load_ratio() + len(waiting) / max(lift.capacity, 1)
                predicted = min(1.0, predicted)
                stability_penalty = 2.2 * predicted * scenario.carrying_share
            oracle_bonus = 0.0
            if self.name == "oracle_upper":
                oracle_bonus = -1.2 if lift.has_space() and lift.direction in {0, direction} else 0.0
            score = distance + direction_penalty + load_penalty + access_bonus + stability_penalty + oracle_bonus
            score += rng.random() * 0.02
            if score < best_score:
                best_score = score
                best_lift = lift
        return best_lift

    def should_stop_for_pickup(self, lift: Lift, waiting: List[Passenger], scenario: Scenario) -> bool:
        if not waiting:
            return False
        if not self.supports_occupancy():
            return True
        special_waiting = any(p.special_need for p in waiting)
        if lift.load_ratio() >= 0.92 and not (self.supports_access() and special_waiting and lift.has_space()):
            return False
        if lift.load_ratio() >= 0.82 and len(waiting) > max(1, lift.capacity - len(lift.passengers)):
            return self.name in {"access_priority", "human_aware", "oracle_upper"} and special_waiting
        return True

    def speed_factor(self, stability: float, carrying_inside: bool) -> float:
        if not self.supports_stability():
            return 1.0
        if stability > 0.72 or carrying_inside:
            return 0.72
        if stability > 0.52:
            return 0.86
        return 1.0


def majority_direction(waiting: Iterable[Passenger]) -> int:
    dirs = [p.direction for p in waiting]
    if not dirs:
        return 0
    return 1 if sum(dirs) >= 0 else -1


def simulate(scenario: Scenario, controller_name: str, seed: int) -> RunMetrics:
    controller_offsets = {
        "collective": 11,
        "nearest_car": 23,
        "occupancy_aware": 37,
        "access_priority": 43,
        "stability_aware": 59,
        "human_aware": 71,
        "layered_access_stability": 83,
        "oracle_upper": 89,
    }
    rng = random.Random(seed * 7919 + controller_offsets.get(controller_name, 101))
    controller = Controller(controller_name)
    arrivals = generate_arrivals(scenario, seed)
    lifts = [Lift(lid=i, floor=0, capacity=13) for i in range(scenario.lifts)]
    waiting: Dict[int, List[Passenger]] = {f: [] for f in range(scenario.floors)}
    all_passengers: List[Passenger] = []
    completed: List[Passenger] = []
    guidance_events = 0

    assign_period = 8 if controller_name != "oracle_upper" else 5
    for t in range(scenario.duration + 900):
        for p in arrivals.get(t, []):
            waiting[p.origin].append(p)
            all_passengers.append(p)

        if t % assign_period == 0:
            for floor, queue in waiting.items():
                if not queue:
                    continue
                lift = controller.choose_lift(lifts, floor, queue, t, scenario, rng)
                if controller.supports_guidance() and lift.load_ratio() >= 0.9:
                    for p in queue:
                        p.guided_away += 1
                    guidance_events += len(queue)
                lift.target_floors.add(floor)

        for lift in lifts:
            current_waiting = waiting[lift.floor]
            alighting = [p for p in lift.passengers if p.dest == lift.floor]
            if alighting:
                lift.stops += 1
                for p in alighting:
                    p.alighted_time = t
                    completed.append(p)
                lift.passengers = [p for p in lift.passengers if p.dest != lift.floor]

            stop_for_pickup = lift.floor in lift.target_floors and controller.should_stop_for_pickup(lift, current_waiting, scenario)
            if stop_for_pickup:
                lift.stops += 1
                boarded_any = board_passengers(lift, current_waiting, controller, t)
                if not boarded_any:
                    lift.unnecessary_stops += 1
                if current_waiting and not lift.has_space():
                    lift.failed_pickup_events += len(current_waiting)
                    lift.door_crowding_events += max(0, len(current_waiting) - 2)
                    for p in current_waiting:
                        p.failed_pickups += 1
                lift.target_floors.discard(lift.floor)
            elif lift.floor in lift.target_floors and current_waiting:
                lift.failed_pickup_events += len(current_waiting)
                for p in current_waiting:
                    p.failed_pickups += 1
                lift.target_floors.discard(lift.floor)

            for p in lift.passengers:
                lift.target_floors.add(p.dest)

            stability = estimate_stability(lift, scenario.carrying_share, rng, scenario.sensor_noise)
            carrying_inside = any(p.carrying for p in lift.passengers)
            speed = controller.speed_factor(stability, carrying_inside)
            if speed < 1.0:
                lift.adaptive_slowdowns += 1
            lift.stability_exposure += stability * len(lift.passengers)
            lift.jerk_exposure += (1.0 + 1.3 * stability) * speed * len(lift.passengers)
            lift.energy_proxy += (0.08 + lift.load_ratio() * 0.18) * (1.0 / max(speed, 0.25))

            move_lift(lift, scenario.floors)

        if t > scenario.duration and not any(waiting.values()) and not any(l.passengers for l in lifts):
            break

    return summarise(all_passengers, completed, lifts, guidance_events)


def board_passengers(lift: Lift, queue: List[Passenger], controller: Controller, now: int) -> bool:
    if not queue or not lift.has_space():
        return False
    if controller.supports_access():
        queue.sort(key=lambda p: (not p.special_need, p.arrival_time))
    else:
        queue.sort(key=lambda p: p.arrival_time)
    boarded = []
    direction = lift.direction or majority_direction(queue)
    for p in list(queue):
        if not lift.has_space():
            break
        if direction and p.direction != direction and lift.passengers:
            continue
        p.boarded_time = now
        lift.passengers.append(p)
        lift.target_floors.add(p.dest)
        boarded.append(p)
    for p in boarded:
        queue.remove(p)
    return bool(boarded)


def move_lift(lift: Lift, floors: int) -> None:
    if not lift.target_floors:
        lift.direction = 0
        return
    above = [f for f in lift.target_floors if f > lift.floor]
    below = [f for f in lift.target_floors if f < lift.floor]
    if lift.direction == 0:
        nearest = min(lift.target_floors, key=lambda f: abs(f - lift.floor))
        lift.direction = 1 if nearest > lift.floor else -1 if nearest < lift.floor else 0
    if lift.direction > 0 and not above:
        lift.direction = -1 if below else 0
    elif lift.direction < 0 and not below:
        lift.direction = 1 if above else 0
    if lift.direction:
        lift.floor = max(0, min(floors - 1, lift.floor + lift.direction))
        lift.distance += 1


def summarise(all_passengers: List[Passenger], completed: List[Passenger], lifts: List[Lift], guidance_events: int) -> RunMetrics:
    waits = [p.boarded_time - p.arrival_time for p in completed if p.boarded_time is not None]
    journeys = [p.alighted_time - p.boarded_time for p in completed if p.boarded_time is not None and p.alighted_time is not None]
    special_waits = [p.boarded_time - p.arrival_time for p in completed if p.special_need and p.boarded_time is not None]
    general_waits = [p.boarded_time - p.arrival_time for p in completed if not p.special_need and p.boarded_time is not None]
    stops = sum(l.stops for l in lifts)
    failed = sum(l.failed_pickup_events for l in lifts)
    unnecessary = sum(l.unnecessary_stops for l in lifts)
    crowding = sum(l.door_crowding_events for l in lifts)
    energy = sum(l.energy_proxy for l in lifts)
    distances = [l.distance for l in lifts]
    avg_dist = mean(distances) if distances else 0.0
    imbalance = (max(distances) - min(distances)) / max(avg_dist, 1.0) if distances else 0.0
    stability = sum(l.stability_exposure for l in lifts) / max(len(completed), 1)
    jerk = sum(l.jerk_exposure for l in lifts) / max(len(completed), 1)
    special_mean = mean(special_waits) if special_waits else float("nan")
    general_mean = mean(general_waits) if general_waits else float("nan")
    fairness = special_mean / max(general_mean, 1.0) if special_waits and general_waits else float("nan")
    failed_rate = failed / max(len(all_passengers), 1)
    unnecessary_rate = unnecessary / max(stops, 1)
    crowding_rate = crowding / max(len(all_passengers), 1)
    score = (
        (mean(waits) if waits else 999.0)
        + 0.35 * (percentile(waits, 0.95) if waits else 999.0)
        + 65.0 * failed_rate
        + 18.0 * unnecessary_rate
        + 18.0 * crowding_rate
        + 3.0 * max(0.0, (fairness if not math.isnan(fairness) else 1.0) - 1.0)
        + 0.8 * stability
        + 0.5 * jerk
    )
    return RunMetrics(
        completed=len(completed),
        generated=len(all_passengers),
        mean_wait=mean(waits) if waits else float("nan"),
        p95_wait=percentile(waits, 0.95),
        mean_journey=mean(journeys) if journeys else float("nan"),
        failed_pickup_rate=failed_rate,
        unnecessary_stop_rate=unnecessary_rate,
        door_crowding_rate=crowding_rate,
        energy_proxy=energy / max(len(completed), 1),
        utilisation_imbalance=imbalance,
        special_mean_wait=special_mean,
        general_mean_wait=general_mean,
        fairness_disparity=fairness,
        stability_risk=stability,
        jerk_exposure=jerk,
        adaptive_slowdowns=sum(l.adaptive_slowdowns for l in lifts),
        guidance_events=guidance_events,
        score=score,
    )

