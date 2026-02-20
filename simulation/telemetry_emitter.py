from __future__ import annotations

from dataclasses import dataclass

from simulation.telemetry_packet import TelemetryPacket


@dataclass
class TelemetryEmitter:
    last_emitted_timestamp: int = -1
    interval_seconds: int = 1

    def due(self, unix_timestamp: int) -> bool:
        if self.last_emitted_timestamp >= 0 and unix_timestamp - self.last_emitted_timestamp < self.interval_seconds:
            return False
        return True

    def build_packet(self, patrol, unix_timestamp: int) -> TelemetryPacket:
        return TelemetryPacket(
            unit_id=patrol.unit_id,
            timestamp=unix_timestamp,
            position=(patrol.x, patrol.y),
            speed=patrol.current_speed,
            fuel_level=patrol.fuel_level,
            engine_temperature=patrol.engine_temperature,
            tire_pressure=patrol.tire_pressure,
            mechanical_status=patrol.mechanical_status(),
            patrol_state=patrol.state.value,
        )

    def emit(self, packet: TelemetryPacket, bus) -> None:
        bus.publish(packet)
        self.last_emitted_timestamp = packet.timestamp
