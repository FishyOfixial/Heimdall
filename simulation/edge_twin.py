from __future__ import annotations

import math
from dataclasses import dataclass

from simulation.telemetry_packet import TelemetryPacket


@dataclass
class EdgeTwin:
    unit_id: str
    max_speed_error_mps: float = 8.0
    fuel_rate_per_distance: float = 0.0006
    fuel_margin: float = 0.015
    critical_temp_c: float = 105.0
    critical_temp_seconds: int = 5
    max_gap_seconds: int = 3

    last_packet: TelemetryPacket | None = None
    critical_temp_counter: int = 0

    def validate(self, packet: TelemetryPacket) -> list[str]:
        alerts: list[str] = []
        if self.last_packet is not None:
            dt = max(1, packet.timestamp - self.last_packet.timestamp)
            if dt > self.max_gap_seconds:
                alerts.append(f"LOSS_OF_UPDATES gap={dt}s")

            dx = packet.position[0] - self.last_packet.position[0]
            dy = packet.position[1] - self.last_packet.position[1]
            observed_speed = math.hypot(dx, dy) / dt
            if abs(packet.speed - observed_speed) > self.max_speed_error_mps:
                alerts.append(
                    f"IMPOSSIBLE_SPEED declared={packet.speed:.2f} observed={observed_speed:.2f} dt={dt}s"
                )

            fuel_drop = self.last_packet.fuel_level - packet.fuel_level
            max_physical_drop = (math.hypot(dx, dy) * self.fuel_rate_per_distance) + self.fuel_margin
            if fuel_drop > max_physical_drop:
                alerts.append(
                    f"FUEL_DROP_ANOMALY drop={fuel_drop:.4f} max={max_physical_drop:.4f}"
                )

        if packet.engine_temperature > self.critical_temp_c:
            self.critical_temp_counter += 1
        else:
            self.critical_temp_counter = 0

        if self.critical_temp_counter > self.critical_temp_seconds:
            alerts.append(
                f"SUSTAINED_CRITICAL_TEMPERATURE temp={packet.engine_temperature:.1f} duration={self.critical_temp_counter}s"
            )

        self.last_packet = packet
        return alerts
