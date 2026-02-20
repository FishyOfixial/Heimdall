from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class RiskPredictor:
    decay_lambda: float = 0.08
    weight_hour: float = 0.45
    weight_traffic: float = 0.35
    weight_day: float = 0.20
    high_risk_threshold: float = 1.25
    persistence_floor: float = 0.12

    def __post_init__(self) -> None:
        total = self.weight_hour + self.weight_traffic + self.weight_day
        self.weight_hour /= total
        self.weight_traffic /= total
        self.weight_day /= total
        self.zone_events: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)

    def record_incident(self, zone: tuple[int, int], severity: int, tick: int) -> None:
        self.zone_events[zone].append((tick, severity))

    def update_risk_map(self, world, tick: int) -> None:
        updated: dict[tuple[int, int], float] = {}
        traffic_factor = self._traffic_factor(world)
        hour_factor = self._hour_factor(tick)
        day_factor = self._day_factor(tick)

        for zone in world.all_relevant_zones() | set(self.zone_events.keys()):
            hist = self._historical_risk(zone, tick)
            bayes_like = (
                self.weight_hour * hour_factor
                + self.weight_traffic * traffic_factor.get(zone, 1.0)
                + self.weight_day * day_factor
            )
            prior = self.persistence_floor * math.log1p(world.zone_incident_counts.get(zone, 0))
            risk = (hist * bayes_like) + prior
            if risk > 0.01:
                updated[zone] = risk

        world.risk_map = updated

    def high_risk_zones(self, world) -> list[tuple[int, int]]:
        return [zone for zone, risk in world.risk_map.items() if risk >= self.high_risk_threshold]

    def _historical_risk(self, zone: tuple[int, int], tick: int) -> float:
        risk = 0.0
        for event_tick, severity in self.zone_events.get(zone, []):
            dt = max(0, tick - event_tick)
            risk += severity * math.exp(-self.decay_lambda * dt)
        return risk

    def _hour_factor(self, tick: int) -> float:
        hour = tick % 24
        if 18 <= hour <= 23:
            return 1.25
        if 0 <= hour <= 5:
            return 1.1
        return 0.95

    def _day_factor(self, tick: int) -> float:
        day = (tick // 24) % 7
        return 1.15 if day in (4, 5) else 1.0

    def _traffic_factor(self, world) -> dict[tuple[int, int], float]:
        density: dict[tuple[int, int], int] = defaultdict(int)
        for patrol in world.patrols:
            zone = world.zone_for_point(patrol.x, patrol.y)
            density[zone] += 1

        factors: dict[tuple[int, int], float] = {}
        for zone in world.all_relevant_zones() | set(density.keys()):
            factors[zone] = 1.0 + 0.05 * density.get(zone, 0)
        return factors
