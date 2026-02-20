from __future__ import annotations

from dataclasses import dataclass

from simulation.telemetry_packet import TelemetryPacket


@dataclass
class UnitOperationalState:
    patrol_id: int
    unit_id: str
    timestamp: int
    position: tuple[float, float]
    speed: float
    fuel_level: float
    engine_temperature: float
    tire_pressure: float
    mechanical_status: str
    patrol_state: str
    connected: bool = True


class CentralCoordinator:
    def __init__(self, disconnect_timeout_seconds: int = 3) -> None:
        self.disconnect_timeout_seconds = disconnect_timeout_seconds
        self.patrol_to_unit: dict[int, str] = {}
        self.unit_to_patrol: dict[str, int] = {}
        self.global_state: dict[str, UnitOperationalState] = {}
        self.disconnect_alerts: list[dict] = []

    def register_unit(self, patrol_id: int, unit_id: str) -> None:
        self.patrol_to_unit[patrol_id] = unit_id
        self.unit_to_patrol[unit_id] = patrol_id

    def consume_telemetry_bus(self, telemetry_bus, current_timestamp: int) -> None:
        for packet in telemetry_bus.consume_all():
            self._ingest_packet(packet)
        self._mark_disconnected_units(current_timestamp)

    def _ingest_packet(self, packet: TelemetryPacket) -> None:
        patrol_id = self.unit_to_patrol.get(packet.unit_id)
        if patrol_id is None:
            return

        self.global_state[packet.unit_id] = UnitOperationalState(
            patrol_id=patrol_id,
            unit_id=packet.unit_id,
            timestamp=packet.timestamp,
            position=packet.position,
            speed=packet.speed,
            fuel_level=packet.fuel_level,
            engine_temperature=packet.engine_temperature,
            tire_pressure=packet.tire_pressure,
            mechanical_status=packet.mechanical_status,
            patrol_state=packet.patrol_state,
            connected=True,
        )

    def _mark_disconnected_units(self, current_timestamp: int) -> None:
        for unit_id, state in self.global_state.items():
            if current_timestamp - state.timestamp > self.disconnect_timeout_seconds:
                if state.connected:
                    self.disconnect_alerts.append(
                        {
                            "timestamp": current_timestamp,
                            "unit_id": unit_id,
                            "patrol_id": state.patrol_id,
                            "alert": f"DISCONNECTED gap={current_timestamp - state.timestamp}s",
                            "action": "MARK_NOT_AVAILABLE",
                        }
                    )
                state.connected = False
                state.patrol_state = "OUT_OF_SERVICE"

    def get_state_by_patrol_id(self, patrol_id: int) -> UnitOperationalState | None:
        unit_id = self.patrol_to_unit.get(patrol_id)
        if unit_id is None:
            return None
        return self.global_state.get(unit_id)

    def dispatchable_patrol_ids(self, excluded_patrol_ids: set[int] | None = None) -> list[int]:
        excluded = excluded_patrol_ids or set()
        dispatchable: list[int] = []
        for state in self.global_state.values():
            if state.patrol_id in excluded:
                continue
            if not state.connected:
                continue
            if state.patrol_state not in {"IDLE", "AVAILABLE", "PATROLLING", "PREVENTIVE_PATROL"}:
                continue
            dispatchable.append(state.patrol_id)
        return dispatchable
