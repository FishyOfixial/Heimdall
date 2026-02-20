from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class StochasticUrbanSimulator:
    seed: int | None = None
    base_intensity: float = 120.0
    contagion_weight: float = 0.35
    decay: float = 0.05
    alpha: float = 0.12

    recent_events: dict[tuple[int, int], list[int]] = field(default_factory=lambda: defaultdict(list))

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def generate_incidents(self, world, tick: int) -> list[tuple[float, float, int]]:
        generated: list[tuple[float, float, int]] = []

        # SUE is ground truth and must be independent from dispatcher/predictor mode.
        for zx in range(world.partition.cols):
            for zy in range(world.partition.rows):
                zone = (zx, zy)

                lam = self._zone_lambda(world, zone, tick)

                # Poisson probability for at least one event in interval.
                DT_HOURS = 1.0 / 3600.0
                p = 1 - math.exp(-lam * DT_HOURS)

                if self._rng.random() > p:
                    continue

                x0, y0, x1, y1 = world.partition.zone_bounds(zone)
                x = self._rng.uniform(x0, x1)
                y = self._rng.uniform(y0, y1)
                severity = self._sample_severity(lam)

                generated.append((x, y, severity))
                self.register_incident(zone, tick)

        return generated

    def register_incident(self, zone: tuple[int, int], tick: int) -> None:
        self.recent_events[zone].append(tick)

    # -------------------- λ(z,t) --------------------

    def _zone_lambda(self, world, zone: tuple[int, int], tick: int) -> float:

        spatial = world.crime_field.risk(zone)
        hour_factor = self._hour_factor(tick)
        contagion = self._contagion(world, zone, tick)
        total_zones = world.partition.cols * world.partition.rows
        lam = self.base_intensity / self.base_intensity

        return lam * spatial * hour_factor * (1 + self.contagion_weight * contagion)

    def _contagion(self, world, zone: tuple[int, int], tick: int) -> float:
        influence = 0.0

        for nz in world.partition.neighbor_zones(zone, radius=2):
            for event_tick in self.recent_events.get(nz, []):
                dt = tick - event_tick
                if dt <= 0:
                    continue

                influence += math.exp(-self.decay * dt)

        # NORMALIZACION (la clave)
        influence = 1 - math.exp(-influence * self.alpha)

        return influence


    def _hour_factor(self, tick: int) -> float:
        hour = tick % 24

        if hour >= 20 or hour <= 2:
            return 1.45   # noche
        if 18 <= hour <= 23:
            return 1.25   # tarde
        if 6 <= hour <= 8:
            return 1.15   # mañana pico
        return 0.8        # madrugada tranquila

    def _sample_severity(self, lam: float) -> int:
        if lam > 0.02:
            return self._rng.choices([3, 4, 5], weights=[2, 4, 3])[0]
        if lam > 0.01:
            return self._rng.choices([2, 3, 4], weights=[3, 4, 2])[0]
        return self._rng.choices([1, 2, 3], weights=[5, 3, 1])[0]
