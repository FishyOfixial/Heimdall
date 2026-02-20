from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricsEngine:
    incidents_total: int = 0
    incidents_prevented: int = 0
    resolved_incidents: int = 0
    total_response_time: float = 0.0

    tp: int = 0
    fp: int = 0
    fn: int = 0

    coverage_sum: float = 0.0
    coverage_samples: int = 0

    incidents_by_tick: dict[int, set[tuple[int, int]]] = field(default_factory=lambda: defaultdict(set))

    def record_incident_created(self, tick: int, zone: tuple[int, int], anticipated: bool) -> None:
        self.incidents_total += 1
        if anticipated:
            self.incidents_prevented += 1
        self.incidents_by_tick[tick].add(zone)

    def record_incident_resolved(self, created_tick: int, resolved_tick: int) -> None:
        if resolved_tick < created_tick:
            return
        self.resolved_incidents += 1
        self.total_response_time += float(resolved_tick - created_tick)

    def update_tick(self, world, tick: int, high_risk_zones: set[tuple[int, int]]) -> None:
        self._update_prediction_confusion(tick, high_risk_zones)
        self._update_coverage(world)

    def _update_prediction_confusion(self, tick: int, high_risk_zones: set[tuple[int, int]]) -> None:
        actual_zones = self.incidents_by_tick.pop(tick, set())
        tp = len(high_risk_zones & actual_zones)
        fp = len(high_risk_zones - actual_zones)
        fn = len(actual_zones - high_risk_zones)
        self.tp += tp
        self.fp += fp
        self.fn += fn

    def _update_coverage(self, world) -> None:
        patrol_positions: list[tuple[float, float, float]] = []
        if world.central_coordinator.global_state:
            for state in world.central_coordinator.global_state.values():
                patrol = world._patrol_by_id(state.patrol_id)
                radius = patrol.coverage_radius if patrol is not None else 120.0
                patrol_positions.append((state.position[0], state.position[1], radius))
        else:
            for patrol in world.patrols:
                patrol_positions.append((patrol.x, patrol.y, patrol.coverage_radius))

        total_zones = max(1, world.partition.cols * world.partition.rows)
        covered = 0
        for zx in range(world.partition.cols):
            for zy in range(world.partition.rows):
                cx, cy = world.partition.zone_center((zx, zy))
                if any(math.hypot(px - cx, py - cy) <= radius for px, py, radius in patrol_positions):
                    covered += 1

        coverage = (covered / total_zones) * 100.0
        self.coverage_sum += coverage
        self.coverage_samples += 1

    def snapshot(self) -> dict[str, float]:
        avg_response = (self.total_response_time / self.resolved_incidents) if self.resolved_incidents else 0.0
        avg_coverage = (self.coverage_sum / self.coverage_samples) if self.coverage_samples else 0.0
        prediction_rate = (self.incidents_prevented / self.incidents_total) if self.incidents_total else 0.0
        precision = (self.tp / (self.tp + self.fp)) if (self.tp + self.fp) else 0.0
        recall = (self.tp / (self.tp + self.fn)) if (self.tp + self.fn) else 0.0
        return {
            "avg_response_time": avg_response,
            "coverage_percent": avg_coverage,
            "incidents_prevented": float(self.incidents_prevented),
            "prediction_rate": prediction_rate,
            "prediction_precision": precision,
            "prediction_recall": recall,
            "incidents_total": float(self.incidents_total),
            "resolved_incidents": float(self.resolved_incidents),
        }

    def to_csv_row(self):
        header = "avg_response_time,coverage_percent,incidents_prevented,prediction_rate,prediction_precision,prediction_recall,incidents_total,resolved_incidents"
        row = f"{self.avg_response_time},{self.coverage_percent},{self.incidents_prevented},{self.prediction_rate},{self.prediction_precision},{self.prediction_recall},{self.incidents_total},{self.resolved_incidents}"
        return header, row


    def export_csv(self, file_path: str) -> None:
        metrics = self.snapshot()
        fieldnames = [
            "avg_response_time",
            "coverage_percent",
            "incidents_prevented",
            "prediction_rate",
            "prediction_precision",
            "prediction_recall",
            "incidents_total",
            "resolved_incidents",
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(metrics)
