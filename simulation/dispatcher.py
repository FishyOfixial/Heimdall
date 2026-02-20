from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field

from simulation.patrol import PatrolState


@dataclass
class DispatchWeights:
    w1_eta: float = 1.0
    w2_fuel_penalty: float = 2.0
    w3_mechanical_risk: float = 2.0
    w4_coverage_loss: float = 1.5
    w5_severity: float = 1.2
    w6_zone_risk: float = 0.8


class BaseDispatcher:
    def select_patrol(self, world, incident, excluded_patrol_ids: set[int] | None = None) -> int | None:
        raise NotImplementedError

    def score_patrol(self, world, patrol_id: int, incident) -> float:
        raise NotImplementedError

    def _candidate_ids(self, world, excluded_patrol_ids: set[int] | None = None) -> list[int]:
        return world.central_coordinator.dispatchable_patrol_ids(excluded_patrol_ids)

    def _eta_seconds(self, position: tuple[float, float], speed: float, incident) -> float:
        dx = position[0] - incident.x
        dy = position[1] - incident.y
        distance = math.hypot(dx, dy)
        return distance / max(0.1, speed)

    def _planning_speed(self, world, patrol_id: int, observed_speed: float) -> float:
        if observed_speed > 0.1:
            return observed_speed
        patrol = world._patrol_by_id(patrol_id)
        if patrol is not None:
            return max(0.1, patrol.effective_speed())
        return 0.1

    def _coverage_loss(self, world, selected_patrol_id: int) -> float:
        selected_state = world.central_coordinator.get_state_by_patrol_id(selected_patrol_id)
        if selected_state is None:
            return 2.0

        selected_zone = world.zone_for_point(selected_state.position[0], selected_state.position[1])
        selected_center = world.partition.zone_center(selected_zone)

        others = [
            state
            for state in world.central_coordinator.global_state.values()
            if state.patrol_id != selected_patrol_id and state.connected and state.patrol_state in {"AVAILABLE", "PATROLLING"}
        ]
        if not others:
            return 2.0

        nearest = float("inf")
        sx, sy = selected_center
        for state in others:
            zone = world.zone_for_point(state.position[0], state.position[1])
            cx, cy = world.partition.zone_center(zone)
            nearest = min(nearest, math.hypot(cx - sx, cy - sy))

        return min(2.0, nearest / max(1.0, world.partition.cell_size * 4.0))

    def _risk_after_dispatch(self, world, patrol_id: int, incident) -> float:
        state = world.central_coordinator.get_state_by_patrol_id(patrol_id)
        if state is None:
            return 2.5

        zone = world.zone_for_point(state.position[0], state.position[1])

        current_risk = world.risk_map.get(zone, 0.0)

        remaining_units = 0
        for other in world.central_coordinator.global_state.values():
            if other.patrol_id == patrol_id:
                continue
            if not other.connected:
                continue
            if other.patrol_state not in {"AVAILABLE", "PATROLLING"}:
                continue

            other_zone = world.zone_for_point(other.position[0], other.position[1])
            if other_zone == zone:
                remaining_units += 1

        if remaining_units == 0:
            return current_risk * 1.2

        if remaining_units == 1:
            return current_risk * 1.2

        return current_risk * 0.4


@dataclass
class IntelligentDispatcher(BaseDispatcher):
    weights: DispatchWeights = field(default_factory=DispatchWeights)

    def select_patrol(self, world, incident, excluded_patrol_ids: set[int] | None = None) -> int | None:
        # Regla de dos niveles: el despacho de incidentes reales se comporta como baseline reactivo (ETA minimo).
        return self._nearest_patrol(world, incident, excluded_patrol_ids)

    def score_patrol(self, world, patrol_id: int, incident) -> float:
        state = world.central_coordinator.get_state_by_patrol_id(patrol_id)
        if state is None or not state.connected:
            return float("inf")
        # Para asignacion de incidente se usa ETA puro para no penalizar tiempos de respuesta.
        return self._eta_seconds(state.position, self._planning_speed(world, patrol_id, state.speed), incident)

    def rebalance_preventive(self, world, high_risk_zones: list[tuple[int, int]]) -> None:
        if not high_risk_zones:
            return

        filtered_zones = self.filter_high_risk_zones(world, high_risk_zones)
        if not filtered_zones:
            return

        total_units = max(1, len(world.patrols))
        cap = max(1, int(total_units * 0.25))
        pending_demand = sum(
            max(0, incident.required_responders - len(incident.assigned_patrol_ids))
            for incident in world.active_incidents()
        )
        dispatchable_ids = world.central_coordinator.dispatchable_patrol_ids()
        surplus = len(dispatchable_ids) - pending_demand
        if surplus <= 1:
            return
        cap = min(cap, max(1, surplus - 1))
        preventive_ids = self._preventive_patrol_ids(world)
        available_slots = max(0, cap - len(preventive_ids))
        if available_slots <= 0:
            return

        eligible_ids = self._eligible_idle_ids(world)
        if not eligible_ids:
            return

        protected_ids = self._critical_for_active_incidents(world, eligible_ids)
        assigned_in_call: set[int] = set()

        for zone in filtered_zones:
            if available_slots <= 0:
                break

            unit_id = self._closest_eligible_to_zone(world, zone, eligible_ids, protected_ids, assigned_in_call)
            if unit_id is None:
                continue

            if self._would_leave_large_empty_area(world, unit_id):
                continue

            patrol = world._patrol_by_id(unit_id)
            if patrol is None:
                continue

            zone_center = world.partition.zone_center(zone)
            patrol.set_preventive_target(zone_center)
            assigned_in_call.add(unit_id)
            available_slots -= 1

    def filter_high_risk_zones(self, world, predicted_zones: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not world.risk_map:
            return []

        risks = list(world.risk_map.values())
        mu = statistics.fmean(risks)
        sigma = statistics.pstdev(risks) if len(risks) > 1 else 0.0
        dynamic_threshold = mu + (1.2 * sigma)

        selected = [zone for zone in predicted_zones if world.risk_map.get(zone, 0.0) >= dynamic_threshold]
        selected.sort(key=lambda zone: world.risk_map.get(zone, 0.0), reverse=True)
        return selected

    def _nearest_patrol(self, world, incident, excluded_patrol_ids: set[int] | None = None) -> int | None:
        candidates = self._candidate_ids(world, excluded_patrol_ids)
        if not candidates:
            return None
        best_id = None
        best_eta = float("inf")
        for patrol_id in candidates:
            state = world.central_coordinator.get_state_by_patrol_id(patrol_id)
            if state is None or not state.connected:
                continue
            eta = self._eta_seconds(state.position, self._planning_speed(world, patrol_id, state.speed), incident)
            if eta < best_eta:
                best_eta = eta
                best_id = patrol_id
        return best_id

    def _preventive_patrol_ids(self, world) -> set[int]:
        ids: set[int] = set()
        for state in world.central_coordinator.global_state.values():
            if not state.connected:
                continue
            if state.patrol_state == "PREVENTIVE_PATROL":
                ids.add(state.patrol_id)
        return ids

    def _eligible_idle_ids(self, world) -> list[int]:
        eligible: list[int] = []
        for state in world.central_coordinator.global_state.values():
            if not state.connected:
                continue
            if state.patrol_state not in {"IDLE", "AVAILABLE", "PATROLLING", "PREVENTIVE_PATROL"}:
                continue
            patrol = world._patrol_by_id(state.patrol_id)
            if patrol is None:
                continue
            if patrol.target_incident_id is not None:
                continue
            if patrol.state in {
                PatrolState.REFUELING,
                PatrolState.MAINTENANCE,
                PatrolState.EMERGENCY_RETURN,
                PatrolState.OUT_OF_SERVICE,
            }:
                continue
            eligible.append(state.patrol_id)
        return eligible

    def _critical_for_active_incidents(self, world, candidate_ids: list[int]) -> set[int]:
        protected: set[int] = set()
        active_incidents = [i for i in world.active_incidents() if i.needs_more_units()]
        if not active_incidents:
            return protected

        active_incidents.sort(key=lambda i: (-i.severity, i.created_tick))
        for incident in active_incidents[:3]:
            nearest_id = self._nearest_patrol(world, incident)
            if nearest_id is not None and nearest_id in candidate_ids:
                protected.add(nearest_id)
        return protected

    def _closest_eligible_to_zone(
        self,
        world,
        zone: tuple[int, int],
        eligible_ids: list[int],
        protected_ids: set[int],
        already_selected: set[int],
    ) -> int | None:
        cx, cy = world.partition.zone_center(zone)
        best_id = None
        best_dist = float("inf")
        for patrol_id in eligible_ids:
            if patrol_id in protected_ids or patrol_id in already_selected:
                continue
            state = world.central_coordinator.get_state_by_patrol_id(patrol_id)
            if state is None or not state.connected:
                continue
            patrol = world._patrol_by_id(patrol_id)
            if patrol is None:
                continue
            dist = math.hypot(state.position[0] - cx, state.position[1] - cy)
            home_zone = patrol.home_zone
            if not world.partition.valid_zone(home_zone):
                home_zone = world.zone_for_point(state.position[0], state.position[1])
            hx, hy = world.partition.zone_center(home_zone)
            operational_radius = patrol.operational_radius if patrol.operational_radius > 0 else world.operational_radius()
            # Regla operativa real: patrullaje predictivo solo dentro del sector operativo.
            if math.hypot(cx - hx, cy - hy) > operational_radius:
                continue
            if dist < best_dist:
                best_dist = dist
                best_id = patrol_id
        return best_id

    def _would_leave_large_empty_area(self, world, patrol_id: int) -> bool:
        selected_state = world.central_coordinator.get_state_by_patrol_id(patrol_id)
        if selected_state is None:
            return True

        nearest = float("inf")
        sx, sy = selected_state.position
        for state in world.central_coordinator.global_state.values():
            if state.patrol_id == patrol_id or not state.connected:
                continue
            if state.patrol_state in {"OUT_OF_SERVICE", "RESPONDING", "MAINTENANCE", "REFUELING", "EMERGENCY_RETURN"}:
                continue
            nearest = min(nearest, math.hypot(state.position[0] - sx, state.position[1] - sy))

        if math.isinf(nearest):
            return True

        gap_threshold = max(300.0, world.partition.cell_size * 4.8)
        return nearest > gap_threshold


class ReactiveDispatcher(BaseDispatcher):
    def select_patrol(self, world, incident, excluded_patrol_ids: set[int] | None = None) -> int | None:
        candidates = self._candidate_ids(world, excluded_patrol_ids)
        if not candidates:
            return None
        scored = [(self.score_patrol(world, patrol_id, incident), patrol_id) for patrol_id in candidates]
        scored = [item for item in scored if not math.isinf(item[0])]
        if not scored:
            return None
        scored.sort(key=lambda item: item[0])
        return scored[0][1]

    def score_patrol(self, world, patrol_id: int, incident) -> float:
        state = world.central_coordinator.get_state_by_patrol_id(patrol_id)
        if state is None or not state.connected:
            return float("inf")
        # Baseline reactivo: solo cercanía/ETA.
        return self._eta_seconds(state.position, self._planning_speed(world, patrol_id, state.speed), incident)
