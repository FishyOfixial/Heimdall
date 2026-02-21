from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field


@dataclass(frozen=True)
class IncidentPoint:
    x: float
    y: float
    timestamp: int


class TrafficMemory:
    def __init__(self) -> None:
        self._incidents: deque[IncidentPoint] = deque()
        self._current_time: int = 0

    def set_current_time(self, t: int) -> None:
        self._current_time = t

    def record_incident(self, x: float, y: float, t: int) -> None:
        self._incidents.append(IncidentPoint(x=float(x), y=float(y), timestamp=int(t)))

    def get_recent_incidents(self, window: int) -> list[IncidentPoint]:
        if window <= 0:
            return []
        limit = self._current_time - window
        recent = [incident for incident in self._incidents if incident.timestamp >= limit]
        while self._incidents and self._incidents[0].timestamp < limit:
            self._incidents.popleft()
        return recent


@dataclass
class RiskPredictor:
    tau: float = 40.0
    alpha: float = 0.08
    alpha_min: float = 0.02
    alpha_max: float = 0.2
    spatial_radius: int = 2
    memory_window: int = 160
    high_risk_threshold: float = 0.55
    memory: TrafficMemory = field(default_factory=TrafficMemory)

    def __post_init__(self) -> None:
        self._bound_world = None
        self._last_predicted_zones: set[tuple[int, int]] = set()

    def record_incident(self, x: float, y: float, t: int) -> None:
        self.memory.record_incident(x, y, t)

    def update_risk_map(self, world, tick: int) -> None:
        self._bound_world = world
        self.memory.set_current_time(tick)
        self._online_update_alpha(world, tick)

        updated: dict[tuple[int, int], float] = {}
        candidate_zones = world.all_relevant_zones() | self._zones_from_recent_incidents(world)
        for zone in candidate_zones:
            cx, cy = world.partition.zone_center(zone)
            prob = self.predict_risk(cx, cy, tick)
            if prob > 0.0:
                updated[zone] = prob
        world.risk_map = updated

    def high_risk_zones(self, world) -> list[tuple[int, int]]:
        prioritized = [zone for zone, prob in world.risk_map.items() if prob >= self.high_risk_threshold]
        self._last_predicted_zones = set(prioritized)
        return prioritized

    def predict_risk(self, x: float, y: float, t: int) -> float:
        if self._bound_world is None:
            return 0.0
        world = self._bound_world
        zone = world.zone_for_point(x, y)
        score = self._score_zone(world, zone, t)
        prob = 1.0 - math.exp(-self.alpha * score)
        return max(0.0, min(1.0, prob))

    def _score_zone(self, world, zone: tuple[int, int], current_time: int) -> float:
        self.memory.set_current_time(current_time)
        score = 0.0
        for incident in self.memory.get_recent_incidents(self.memory_window):
            incident_zone = world.zone_for_point(incident.x, incident.y)
            dist = abs(incident_zone[0] - zone[0]) + abs(incident_zone[1] - zone[1])
            if dist > self.spatial_radius:
                continue
            temporal_weight = math.exp(-(max(0, current_time - incident.timestamp)) / max(1e-6, self.tau))
            spatial_weight = 1.0 / (1.0 + dist)
            score += temporal_weight * spatial_weight
        return score

    def _zones_from_recent_incidents(self, world) -> set[tuple[int, int]]:
        zones: set[tuple[int, int]] = set()
        for incident in self.memory.get_recent_incidents(self.memory_window):
            zones.add(world.zone_for_point(incident.x, incident.y))
        return zones

    def _online_update_alpha(self, world, tick: int) -> None:
        if not self._last_predicted_zones:
            return
        actual_zones = {
            world.zone_for_point(incident.x, incident.y)
            for incident in world.incidents.values()
            if incident.created_tick == tick
        }
        for zone in self._last_predicted_zones:
            if zone in actual_zones:
                self.alpha *= 1.02
            else:
                self.alpha *= 0.98
        self.alpha = min(self.alpha_max, max(self.alpha_min, self.alpha))
