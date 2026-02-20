from __future__ import annotations
import random
import math


class CrimeField:
    def __init__(self, partition, seed: int = 42):
        self.partition = partition
        self._rng = random.Random(seed)
        self.base_risk: dict[tuple[int, int], float] = {}

        self._generate_hotspots()

    def _generate_hotspots(self) -> None:
        hotspot_count = max(3, (self.partition.cols * self.partition.rows) // 35)

        centers = []
        for _ in range(hotspot_count):
            zx = self._rng.randint(0, self.partition.cols - 1)
            zy = self._rng.randint(0, self.partition.rows - 1)
            intensity = self._rng.uniform(2.0, 4.5)
            radius = self._rng.uniform(2.0, 5.5)
            centers.append((zx, zy, intensity, radius))

        for zx in range(self.partition.cols):
            for zy in range(self.partition.rows):
                risk = 0.05

                for cx, cy, intensity, radius in centers:
                    dist = math.dist((zx, zy), (cx, cy))
                    risk += intensity * math.exp(-(dist**2) / (2 * radius**2))

                self.base_risk[(zx, zy)] = risk

    def risk(self, zone: tuple[int, int]) -> float:
        return self.base_risk.get(zone, 0.05)
