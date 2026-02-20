from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TelemetryPacket:
    unit_id: str
    timestamp: int
    position: tuple[float, float]
    speed: float
    fuel_level: float
    engine_temperature: float
    tire_pressure: float
    mechanical_status: str
    patrol_state: str

    def to_dict(self) -> dict:
        return asdict(self)
