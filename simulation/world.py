from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import TYPE_CHECKING

from simulation.incident import Incident
from simulation.patrol import Patrol, PatrolState
from simulation.spatial import AdaptiveSpatialPartition
from simulation.central_coordinator import CentralCoordinator
from simulation.audit_logger import AuditLogger
from simulation.metrics_engine import MetricsEngine
from simulation.edge_twin import EdgeTwin
from simulation.telemetry_bus import TelemetryBus
from simulation.telemetry_emitter import TelemetryEmitter
from simulation.telemetry_packet import TelemetryPacket
from simulation.crime_field import CrimeField

if TYPE_CHECKING:
    from simulation.dispatcher import BaseDispatcher
    from simulation.predictor import RiskPredictor
    from simulation.sue import StochasticUrbanSimulator


@dataclass
class World:
    width: float
    height: float
    partition: AdaptiveSpatialPartition
    patrols: list[Patrol] = field(default_factory=list)
    incidents: dict[int, Incident] = field(default_factory=dict)
    risk_map: dict[tuple[int, int], float] = field(default_factory=dict)
    zone_incident_counts: dict[tuple[int, int], int] = field(default_factory=dict)
    next_incident_id: int = 1
    next_patrol_id: int = 1
    mechanic_base: tuple[float, float] = (0.0, 0.0)
    gas_stations: list[tuple[float, float]] = field(default_factory=list)
    max_patrols: int = 12
    enable_dynamic_patrols: bool = False
    operating_mode: str = "intelligent"
    audit_logger: AuditLogger = field(default_factory=AuditLogger)
    metrics_engine: MetricsEngine = field(default_factory=MetricsEngine)
    risk_high_threshold: float = 1.6

    telemetry_bus: TelemetryBus = field(default_factory=TelemetryBus)
    central_coordinator: CentralCoordinator = field(default_factory=CentralCoordinator)
    telemetry_emitters: dict[str, TelemetryEmitter] = field(default_factory=dict)
    edge_twins: dict[str, EdgeTwin] = field(default_factory=dict)
    edge_alerts: list[dict] = field(default_factory=list)

    fuel_low_threshold: float = 0.14
    fuel_critical_threshold: float = 0.04
    mech_low_threshold: float = 0.18
    mech_critical_threshold: float = 0.08
    fuel_consumption_per_unit: float = 0.00025
    mech_wear_per_unit: float = 0.00006
    predictive_margin_factor: float = 1.2
    predictive_fuel_reserve: float = 0.03
    predictive_mech_reserve: float = 0.03
    patrol_retarget_interval_ticks: int = 4

    def __post_init__(self) -> None:
        self.crime_field = CrimeField(self.partition)

    def recalculate_zones(self) -> None:
        self.partition.recalculate(self.width, self.height, max(1, len(self.patrols)))
        coverage = self.service_radius()
        operational = self.operational_radius()
        for patrol in self.patrols:
            patrol.coverage_radius = coverage
            patrol.operational_radius = operational

    def service_radius(self) -> float:
        return 2.5 * self.partition.cell_size

    def operational_radius(self) -> float:
        return 3.0 * self.partition.cell_size

    def set_mechanic_base(self, x: float, y: float) -> None:
        bx = min(max(0.0, x), self.width)
        by = min(max(0.0, y), self.height)
        self.mechanic_base = (bx, by)

    def set_gas_stations(self, stations: list[tuple[float, float]]) -> None:
        normalized: list[tuple[float, float]] = []
        for x, y in stations:
            sx = min(max(0.0, x), self.width)
            sy = min(max(0.0, y), self.height)
            normalized.append((sx, sy))
        self.gas_stations = normalized[:4]

    # Backward compatibility helper for old calls.
    def set_service_bases(self, bases: list[tuple[float, float]]) -> None:
        if bases:
            self.set_mechanic_base(*bases[0])
            self.set_gas_stations(bases[1:5])
        else:
            self.set_mechanic_base(self.width * 0.5, self.height * 0.5)
            self.set_gas_stations(
                [
                    (self.width * 0.2, self.height * 0.2),
                    (self.width * 0.8, self.height * 0.2),
                    (self.width * 0.2, self.height * 0.8),
                    (self.width * 0.8, self.height * 0.8),
                ]
            )

    def add_patrol(self, patrol: Patrol) -> None:
        patrol.home_zone = self.zone_for_point(patrol.x, patrol.y)
        patrol.coverage_radius = self.service_radius()
        patrol.operational_radius = self.operational_radius()
        self.patrols.append(patrol)
        self.next_patrol_id = max(self.next_patrol_id, patrol.patrol_id + 1)
        self.telemetry_emitters[patrol.unit_id] = TelemetryEmitter()
        self.edge_twins[patrol.unit_id] = EdgeTwin(unit_id=patrol.unit_id)
        self.central_coordinator.register_unit(patrol.patrol_id, patrol.unit_id)
        self.recalculate_zones()

    def zone_for_point(self, x: float, y: float) -> tuple[int, int]:
        return self.partition.point_to_zone(x, y)

    def create_incident(self, x: float, y: float, severity: int, tick: int) -> Incident:
        x = min(max(0.0, x), self.width)
        y = min(max(0.0, y), self.height)
        severity = max(1, min(5, severity))
        zone = self.zone_for_point(x, y)
        required_responders = self._required_responders(zone, severity)
        incident = Incident(
            incident_id=self.next_incident_id,
            x=x,
            y=y,
            severity=severity,
            created_tick=tick,
            required_responders=required_responders,
        )
        self.incidents[incident.incident_id] = incident
        self.zone_incident_counts[zone] = self.zone_incident_counts.get(zone, 0) + 1
        anticipated = self.risk_map.get(zone, 0.0) >= self.risk_high_threshold
        self.metrics_engine.record_incident_created(tick, zone, anticipated)
        self.next_incident_id += 1
        return incident

    def active_incidents(self) -> list[Incident]:
        return [incident for incident in self.incidents.values() if incident.active]

    def step(
        self,
        tick: int,
        dt: float,
        predictor: RiskPredictor,
        dispatcher: BaseDispatcher,
        sue: StochasticUrbanSimulator | None = None,
    ) -> None:
        if sue is not None:
            self._generate_stochastic_incidents(sue, tick)
        self._update_patrols(dt, tick, predictor)
        self._resolve_stalled_incidents(tick, predictor)
        self._emit_telemetry(tick)
        self._consume_telemetry(tick)
        self._manage_dynamic_patrol_capacity()
        self._dispatch_incidents(dispatcher, tick)
        if self.operating_mode == "intelligent":
            predictor.update_risk_map(self, tick)
            predicted_high_risk = predictor.high_risk_zones(self)
            if hasattr(dispatcher, "filter_high_risk_zones"):
                predicted_high_risk = dispatcher.filter_high_risk_zones(self, predicted_high_risk)
            if hasattr(dispatcher, "rebalance_preventive"):
                dispatcher.rebalance_preventive(self, predicted_high_risk)
            high_risk_zones = set(predicted_high_risk)
        else:
            self.risk_map = {}
            high_risk_zones = set()
        self.metrics_engine.update_tick(self, tick, high_risk_zones)

    def _resolve_stalled_incidents(self, tick: int, predictor: RiskPredictor) -> None:
        # Prevent incidents from staying active forever when quorum cannot be completed.
        for incident in self.active_incidents():
            age = tick - incident.created_tick
            arrived = len(incident.arrived_patrol_ids)
            assigned = len(incident.assigned_patrol_ids)

            # After sustained waiting, relax required responders to current feasible level.
            if age >= 70 and incident.required_responders > 1:
                feasible = max(1, max(arrived, assigned))
                incident.required_responders = min(incident.required_responders, feasible)

            # If at least one unit is already on-scene and incident is old, close by degraded protocol.
            close_age = 25 if self.operating_mode == "intelligent" else 110
            if age >= close_age and arrived > 0 and incident.active:
                self._resolve_incident(incident, tick, predictor)
                continue

            # Hard timeout safeguard: never let incidents remain forever.
            if age >= 180 and incident.active:
                self._resolve_incident(incident, tick, predictor)

    def _generate_stochastic_incidents(self, sue: StochasticUrbanSimulator, tick: int) -> None:
        for x, y, severity in sue.generate_incidents(self, tick):
            self.create_incident(x, y, severity, tick)

    def _emit_telemetry(self, tick: int) -> None:
        unix_timestamp = 1_700_000_000 + tick
        for patrol in self.patrols:
            emitter = self.telemetry_emitters.get(patrol.unit_id)
            if emitter is None:
                emitter = TelemetryEmitter()
                self.telemetry_emitters[patrol.unit_id] = emitter
            twin = self.edge_twins.get(patrol.unit_id)
            if twin is None:
                twin = EdgeTwin(unit_id=patrol.unit_id)
                self.edge_twins[patrol.unit_id] = twin

            if not emitter.due(unix_timestamp):
                continue

            packet = emitter.build_packet(patrol, unix_timestamp)
            alerts = twin.validate(packet)
            if alerts:
                self._register_edge_alerts(patrol, packet.timestamp, alerts)

            emitter.emit(packet, self.telemetry_bus)

    def _consume_telemetry(self, tick: int) -> None:
        unix_timestamp = 1_700_000_000 + tick
        self.central_coordinator.consume_telemetry_bus(self.telemetry_bus, unix_timestamp)
        self._apply_disconnect_states()

    def _register_edge_alerts(self, patrol: Patrol, timestamp: int, alerts: list[str]) -> None:
        for message in alerts:
            self.edge_alerts.append(
                {
                    "timestamp": timestamp,
                    "unit_id": patrol.unit_id,
                    "patrol_id": patrol.patrol_id,
                    "alert": message,
                    "action": "ALERT_ONLY",
                }
            )

    def telemetry_for_patrol(self, patrol_id: int) -> TelemetryPacket | None:
        state = self.central_coordinator.get_state_by_patrol_id(patrol_id)
        if state is None:
            return None
        return TelemetryPacket(
            unit_id=state.unit_id,
            timestamp=state.timestamp,
            position=state.position,
            speed=state.speed,
            fuel_level=state.fuel_level,
            engine_temperature=state.engine_temperature,
            tire_pressure=state.tire_pressure,
            mechanical_status=state.mechanical_status,
            patrol_state=state.patrol_state,
        )

    def _apply_disconnect_states(self) -> None:
        # Disconnects remain as central alerts/flags only; no forced local shutdown.
        return

    def _dispatch_incidents(self, dispatcher: BaseDispatcher, tick: int) -> None:
        unix_timestamp = 1_700_000_000 + tick
        for incident in self._prioritized_incidents():
            while incident.needs_more_units():
                previous_state = self._audit_state_snapshot(incident, None)
                event_received = self._audit_event_payload(incident)
                patrol_id = dispatcher.select_patrol(self, incident, excluded_patrol_ids=incident.assigned_patrol_ids)
                if patrol_id is None:
                    posterior_state = self._audit_state_snapshot(incident, None)
                    self.audit_logger.log_entry(
                        timestamp=unix_timestamp,
                        event_received=event_received,
                        decision_taken="NO_AVAILABLE_PATROL",
                        patrol_assigned=None,
                        previous_state=previous_state,
                        posterior_state=posterior_state,
                        score_calculated=None,
                    )
                    break
                patrol = self._patrol_by_id(patrol_id)
                if patrol is None:
                    break
                score = dispatcher.score_patrol(self, patrol_id, incident)
                if patrol.state == PatrolState.PREVENTIVE_PATROL:
                    patrol.target_x = None
                    patrol.target_y = None
                incident.assign_patrol(patrol_id)
                patrol.assign_to_incident(incident.incident_id, incident.pos)
                posterior_state = self._audit_state_snapshot(incident, patrol_id)
                self.audit_logger.log_entry(
                    timestamp=unix_timestamp,
                    event_received=event_received,
                    decision_taken="ASSIGN_PATROL",
                    patrol_assigned=patrol_id,
                    previous_state=previous_state,
                    posterior_state=posterior_state,
                    score_calculated=score,
                )

    def _patrol_by_id(self, patrol_id: int) -> Patrol | None:
        for patrol in self.patrols:
            if patrol.patrol_id == patrol_id:
                return patrol
        return None

    def _audit_event_payload(self, incident: Incident) -> dict:
        zone = self.zone_for_point(incident.x, incident.y)
        return {
            "event_type": "INCIDENT_DISPATCH_REQUEST",
            "incident_id": incident.incident_id,
            "severity": incident.severity,
            "zone": zone,
            "required_responders": incident.required_responders,
            "assigned_count": len(incident.assigned_patrol_ids),
        }

    def _audit_state_snapshot(self, incident: Incident, patrol_id: int | None) -> dict:
        patrol_state = None
        if patrol_id is not None:
            state = self.central_coordinator.get_state_by_patrol_id(patrol_id)
            patrol_state = {
                "patrol_id": patrol_id,
                "connected": state.connected if state is not None else False,
                "patrol_state": state.patrol_state if state is not None else None,
                "position": state.position if state is not None else None,
                "speed": state.speed if state is not None else None,
                "fuel_level": state.fuel_level if state is not None else None,
                "mechanical_status": state.mechanical_status if state is not None else None,
            }

        return {
            "incident": {
                "incident_id": incident.incident_id,
                "active": incident.active,
                "required_responders": incident.required_responders,
                "assigned_patrol_ids": sorted(list(incident.assigned_patrol_ids)),
                "arrived_patrol_ids": sorted(list(incident.arrived_patrol_ids)),
            },
            "patrol": patrol_state,
        }

    def _prioritized_incidents(self) -> list[Incident]:
        prioritized = list(self.active_incidents())
        # Keep incident servicing fair and stable in both modes to avoid starvation and inflated response times.
        prioritized.sort(key=lambda incident: (-incident.severity, incident.created_tick))
        return prioritized

    def _incident_priority(self, incident: Incident) -> float:
        zone = self.zone_for_point(incident.x, incident.y)
        zone_risk = self.risk_map.get(zone, 0.0)
        zone_history = self.zone_incident_counts.get(zone, 0)
        unmet = max(0, incident.required_responders - len(incident.assigned_patrol_ids))
        return (4.0 * incident.severity) + (1.8 * zone_risk) + (0.45 * zone_history) + (2.0 * unmet)

    def _update_patrols(self, dt: float, tick: int, predictor: RiskPredictor) -> None:
        for patrol in self.patrols:
            if patrol.state == PatrolState.OUT_OF_SERVICE:
                continue

            self._ensure_service_policy(patrol)

            if patrol.has_target():
                arrived = patrol.update_motion(dt)
                if arrived:
                    self._handle_arrival(patrol, tick, predictor)

            patrol.update_task()
            patrol.cool_down_idle()
            self._ensure_patrolling_behavior(patrol, tick)

    def _ensure_service_policy(self, patrol: Patrol) -> None:
        in_service_flow = patrol.state in {
            PatrolState.REFUELING,
            PatrolState.MAINTENANCE,
            PatrolState.EMERGENCY_RETURN,
        }
        if in_service_flow:
            return

        telemetry = self.telemetry_for_patrol(patrol.patrol_id)
        if telemetry is None:
            return

        need_kind = self._service_need_kind(patrol, telemetry)
        if need_kind is None:
            return
        critical = telemetry.fuel_level <= self.fuel_critical_threshold or telemetry.mechanical_status == "CRITICAL"

        objective = self._patrol_objective_point(patrol)
        service_target = self._service_target_for(patrol, need_kind, objective)

        if patrol.state == PatrolState.RESPONDING and patrol.target_incident_id is not None:
            incident = self.incidents.get(patrol.target_incident_id)
            if incident and incident.active:
                incident.unassign_patrol(patrol.patrol_id)
            patrol.target_incident_id = None

        patrol.set_service_target(service_target, emergency=critical)

    def _patrol_objective_point(self, patrol: Patrol) -> tuple[float, float] | None:
        if patrol.state == PatrolState.RESPONDING and patrol.target_incident_id is not None:
            incident = self.incidents.get(patrol.target_incident_id)
            if incident and incident.active:
                return incident.pos
        if patrol.has_target():
            return (patrol.target_x, patrol.target_y)
        return None

    def _service_need_kind(self, patrol: Patrol, telemetry: TelemetryPacket) -> str | None:
        if telemetry.fuel_level <= self.fuel_low_threshold:
            return "fuel"
        if telemetry.mechanical_status == "CRITICAL":
            return "mechanical"

        if self._predictive_fuel_needed(patrol, telemetry):
            return "fuel"
        if self._predictive_mech_needed(patrol, telemetry):
            return "mechanical"
        return None

    def _service_target_for(self, patrol: Patrol, need_kind: str, objective: tuple[float, float] | None = None) -> tuple[float, float]:
        if need_kind == "fuel":
            return self._best_gas_station_for(patrol, objective)
        return self.mechanic_base

    def _best_gas_station_for(self, patrol: Patrol, objective: tuple[float, float] | None = None) -> tuple[float, float]:
        stations = self.gas_stations or [self.mechanic_base]
        px, py = self._patrol_position_for_planning(patrol)
        best = stations[0]
        best_cost = float("inf")
        for station in stations:
            cost = math.hypot(px - station[0], py - station[1])
            if objective is not None:
                cost += 0.2 * math.hypot(station[0] - objective[0], station[1] - objective[1])
            if cost < best_cost:
                best_cost = cost
                best = station
        return best

    def _predictive_fuel_needed(self, patrol: Patrol, telemetry: TelemetryPacket) -> bool:
        target = self._best_gas_station_for(patrol, self._patrol_objective_point(patrol))
        distance = math.hypot(telemetry.position[0] - target[0], telemetry.position[1] - target[1])
        fuel_needed = distance * self.fuel_consumption_per_unit
        fuel_after_arrival = telemetry.fuel_level - (fuel_needed * self.predictive_margin_factor + self.predictive_fuel_reserve)
        return fuel_after_arrival <= self.fuel_critical_threshold

    def _predictive_mech_needed(self, patrol: Patrol, telemetry: TelemetryPacket) -> bool:
        target = self.mechanic_base
        distance = math.hypot(telemetry.position[0] - target[0], telemetry.position[1] - target[1])
        mech_needed = distance * self.mech_wear_per_unit
        mech_health = 1.0 if telemetry.mechanical_status == "OK" else (0.45 if telemetry.mechanical_status == "WARN" else 0.15)
        mech_after_arrival = mech_health - (mech_needed * self.predictive_margin_factor + self.predictive_mech_reserve)
        return mech_after_arrival <= self.mech_critical_threshold

    def _handle_arrival(self, patrol: Patrol, tick: int, predictor: RiskPredictor) -> None:
        if patrol.state == PatrolState.RESPONDING and patrol.target_incident_id is not None:
            incident = self.incidents.get(patrol.target_incident_id)
            if incident and incident.active:
                should_resolve = incident.register_arrival(patrol.patrol_id)
                if should_resolve:
                    self._resolve_incident(incident, tick, predictor)

        patrol.on_arrival()

    def _resolve_incident(self, incident: Incident, tick: int, predictor: RiskPredictor) -> None:
        incident.active = False
        incident.resolved_tick = tick
        zone = self.zone_for_point(incident.x, incident.y)
        predictor.record_incident(zone, incident.severity, tick)
        self.metrics_engine.record_incident_resolved(incident.created_tick, tick)

        for patrol in self.patrols:
            if patrol.target_incident_id != incident.incident_id:
                continue
            patrol.target_incident_id = None
            patrol.target_x = None
            patrol.target_y = None
            if patrol.state == PatrolState.RESPONDING:
                patrol.state = PatrolState.IDLE

    def _manage_dynamic_patrol_capacity(self) -> None:
        if not self.enable_dynamic_patrols:
            return
        if len(self.patrols) >= self.max_patrols:
            self._send_dynamic_reserve_to_base()
            return

        pending_demand = sum(
            max(0, incident.required_responders - len(incident.assigned_patrol_ids))
            for incident in self.active_incidents()
        )
        dispatchable_now = 0
        for patrol_id in self.central_coordinator.dispatchable_patrol_ids():
            patrol = self._patrol_by_id(patrol_id)
            if patrol is not None and patrol.target_incident_id is None:
                dispatchable_now += 1
        shortfall = max(0, pending_demand - dispatchable_now)
        creatable = max(0, self.max_patrols - len(self.patrols))
        for _ in range(min(shortfall, creatable)):
            self._spawn_dynamic_patrol()

        self._send_dynamic_reserve_to_base()

    def _spawn_dynamic_patrol(self) -> None:
        if self.mechanic_base == (0.0, 0.0):
            self.set_service_bases([])
        base = self.mechanic_base
        patrol = Patrol(
            patrol_id=self.next_patrol_id,
            x=base[0],
            y=base[1],
            speed=random.uniform(47.0, 72.0),
            fuel_level=1.0,
            mechanical_health=1.0,
            state=PatrolState.IDLE,
            coverage_radius=120.0,
            is_dynamic=True,
        )
        self.next_patrol_id += 1
        self.add_patrol(patrol)

    def _send_dynamic_reserve_to_base(self) -> None:
        for patrol in self.patrols:
            if not patrol.is_dynamic:
                continue
            if patrol.state in {
                PatrolState.RESPONDING,
                PatrolState.REFUELING,
                PatrolState.MAINTENANCE,
                PatrolState.EMERGENCY_RETURN,
                PatrolState.OUT_OF_SERVICE,
            }:
                continue
            if patrol.target_incident_id is not None:
                continue

            base = self.mechanic_base
            px, py = self._patrol_position_for_planning(patrol)
            distance_to_base = math.hypot(px - base[0], py - base[1])
            if distance_to_base > 6.0 and not patrol.has_target():
                patrol.set_patrol_target(base)
            elif distance_to_base <= 6.0:
                patrol.target_x = None
                patrol.target_y = None
                patrol.state = PatrolState.IDLE

    def _ensure_patrolling_behavior(self, patrol: Patrol, tick: int) -> None:
        if patrol.is_dynamic:
            return
        if patrol.state not in {PatrolState.IDLE, PatrolState.AVAILABLE, PatrolState.PATROLLING, PatrolState.PREVENTIVE_PATROL}:
            return
        if patrol.has_target():
            return
        if tick % self.patrol_retarget_interval_ticks != 0 and patrol.state in {PatrolState.PATROLLING, PatrolState.PREVENTIVE_PATROL}:
            return

        target_zone = self._select_patrol_target_zone(patrol)
        target = self.partition.zone_center(target_zone)
        patrol.set_patrol_target(target)

    def _patrol_position_for_planning(self, patrol: Patrol) -> tuple[float, float]:
        telemetry = self.telemetry_for_patrol(patrol.patrol_id)
        if telemetry is not None:
            return telemetry.position
        return (patrol.x, patrol.y)

    def _select_patrol_target_zone(self, patrol: Patrol) -> tuple[int, int]:
        patrol_positions = [
            self._patrol_position_for_planning(p)
            for p in self.patrols
            if p.patrol_id != patrol.patrol_id and p.state not in {PatrolState.OUT_OF_SERVICE, PatrolState.EMERGENCY_RETURN}
        ]
        px, py = self._patrol_position_for_planning(patrol)
        best_zone = self.zone_for_point(px, py)
        best_score = -10e9

        for zx in range(self.partition.cols):
            for zy in range(self.partition.rows):
                zone = (zx, zy)
                cx, cy = self.partition.zone_center(zone)
                cover_count = 0
                for ox, oy in patrol_positions:
                    if math.hypot(ox - cx, oy - cy) <= patrol.coverage_radius:
                        cover_count += 1

                uncovered_bonus = 5.0 if cover_count == 0 else (1.2 if cover_count == 1 else 0.0)
                overcrowded_penalty = max(0, cover_count - 1) * 2.6
                proximity_penalty = math.hypot(px - cx, py - cy) / max(1.0, self.partition.cell_size * 8.0)
                # Base coverage behavior. Intelligent mode adds predictive rebalancing separately in dispatcher.
                score = (2.2 * uncovered_bonus) - (1.8 * overcrowded_penalty) - proximity_penalty
                if score > best_score:
                    best_score = score
                    best_zone = zone

        return best_zone

    def _required_responders(self, zone: tuple[int, int], severity: int) -> int:
        zone_history = self.zone_incident_counts.get(zone, 0)
        responders = 1
        if severity >= 4:
            responders += 1
        if severity >= 5 or zone_history >= 4:
            responders += 1
        if zone_history >= 7:
            responders += 1
        return min(max(1, responders), max(1, len(self.patrols)))

    def all_relevant_zones(self) -> set[tuple[int, int]]:
        zones = set(self.risk_map.keys())
        for patrol in self.patrols:
            px, py = self._patrol_position_for_planning(patrol)
            zones.add(self.zone_for_point(px, py))
        for incident in self.active_incidents():
            zones.add(self.zone_for_point(incident.x, incident.y))
        zones.add(self.zone_for_point(self.mechanic_base[0], self.mechanic_base[1]))
        for gx, gy in self.gas_stations:
            zones.add(self.zone_for_point(gx, gy))
        return zones

    def random_zone(self) -> tuple[int, int]:
        return (
            random.randint(0, max(0, self.partition.cols - 1)),
            random.randint(0, max(0, self.partition.rows - 1)),
        )
