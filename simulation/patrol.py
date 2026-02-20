import math
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PatrolState(str, Enum):
    IDLE = "IDLE"
    AVAILABLE = "AVAILABLE"
    PATROLLING = "PATROLLING"
    PREVENTIVE_PATROL = "PREVENTIVE_PATROL"
    RESPONDING = "RESPONDING"
    REFUELING = "REFUELING"
    MAINTENANCE = "MAINTENANCE"
    EMERGENCY_RETURN = "EMERGENCY_RETURN"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


@dataclass
class Patrol:
    patrol_id: int
    x: float
    y: float
    speed: float
    unit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fuel_level: float = 1.0
    mechanical_health: float = 1.0
    state: PatrolState = PatrolState.IDLE
    target_incident_id: Optional[int] = None
    target_x: Optional[float] = None
    target_y: Optional[float] = None
    task_ticks_remaining: int = 0
    home_zone: tuple[int, int] = field(default_factory=lambda: (0, 0))
    coverage_radius: float = 120.0
    operational_radius: float = 120.0
    is_dynamic: bool = False
    engine_temperature: float = 78.0
    tire_pressure: float = 34.0
    current_speed: float = 0.0

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def is_dispatchable(self) -> bool:
        return self.state in {
            PatrolState.IDLE,
            PatrolState.AVAILABLE,
            PatrolState.PATROLLING,
            PatrolState.PREVENTIVE_PATROL,
        }

    def effective_speed(self) -> float:
        if self.state == PatrolState.OUT_OF_SERVICE:
            return 0.0
        fuel_factor = max(0.2, self.fuel_level)
        mech_factor = max(0.2, self.mechanical_health)
        return self.speed * fuel_factor * mech_factor

    def fuel_penalty(self) -> float:
        return 1.0 - max(0.0, min(1.0, self.fuel_level))

    def mechanical_risk(self) -> float:
        return 1.0 - max(0.0, min(1.0, self.mechanical_health))

    def assign_to_incident(self, incident_id: int, target: tuple[float, float]) -> None:
        self.target_incident_id = incident_id
        self.target_x, self.target_y = target
        self.state = PatrolState.RESPONDING

    def set_patrol_target(self, target: tuple[float, float]) -> None:
        self.target_incident_id = None
        self.target_x, self.target_y = target
        self.state = PatrolState.PATROLLING

    def set_preventive_target(self, target: tuple[float, float]) -> None:
        self.target_incident_id = None
        self.target_x, self.target_y = target
        self.state = PatrolState.PREVENTIVE_PATROL

    def set_service_target(self, target: tuple[float, float], emergency: bool = False) -> None:
        self.target_x, self.target_y = target
        self.target_incident_id = None
        self.state = PatrolState.EMERGENCY_RETURN if emergency else self.required_service_state()

    def required_service_state(self) -> PatrolState:
        if self.fuel_level <= self.mechanical_health:
            return PatrolState.REFUELING
        return PatrolState.MAINTENANCE

    def has_target(self) -> bool:
        return self.target_x is not None and self.target_y is not None

    def update_motion(self, dt: float) -> bool:
        if not self.has_target():
            self.current_speed = 0.0
            return False

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)
        step = self.effective_speed() * dt

        if distance <= step or distance == 0.0:
            self.x, self.y = self.target_x, self.target_y
            self.current_speed = 0.0
            self._consume_resources(distance)
            return True

        ux = dx / distance
        uy = dy / distance
        self.x += ux * step
        self.y += uy * step
        self.current_speed = step / max(dt, 1e-6)
        self._consume_resources(step)
        return False

    def on_arrival(self) -> None:
        self.target_x = None
        self.target_y = None

        if self.state == PatrolState.RESPONDING:
            self.task_ticks_remaining = 2
            return

        if self.state in {PatrolState.REFUELING, PatrolState.MAINTENANCE, PatrolState.EMERGENCY_RETURN}:
            self.fuel_level = 1.0
            self.mechanical_health = 1.0
            self.engine_temperature = 76.0
            self.tire_pressure = 34.5
            self.task_ticks_remaining = 0
            self.state = PatrolState.IDLE

    def update_task(self) -> None:
        if self.state == PatrolState.RESPONDING and not self.has_target():
            self.current_speed = 0.0
            self.task_ticks_remaining = max(0, self.task_ticks_remaining - 1)
            if self.task_ticks_remaining == 0:
                self.target_incident_id = None
                self.state = PatrolState.IDLE

    def _consume_resources(self, traveled_distance: float) -> None:
        self.fuel_level = max(0.0, self.fuel_level - traveled_distance * 0.00025)
        self.mechanical_health = max(0.12, self.mechanical_health - traveled_distance * 0.00006)
        self.engine_temperature = min(120.0, self.engine_temperature + traveled_distance * 0.012 + (1.0 - self.mechanical_health) * 0.25)
        self.tire_pressure = max(27.5, self.tire_pressure - traveled_distance * 0.00012)
        if self.fuel_level <= 0.01 or self.mechanical_health <= 0.1:
            self.state = PatrolState.OUT_OF_SERVICE

    def cool_down_idle(self) -> None:
        if self.state in {
            PatrolState.IDLE,
            PatrolState.AVAILABLE,
            PatrolState.PATROLLING,
            PatrolState.PREVENTIVE_PATROL,
            PatrolState.REFUELING,
            PatrolState.MAINTENANCE,
        }:
            self.engine_temperature = max(70.0, self.engine_temperature - 0.8)

    def mechanical_status(self) -> str:
        if self.mechanical_health <= 0.2 or self.engine_temperature >= 108.0 or self.tire_pressure <= 28.0:
            return "CRITICAL"
        if self.mechanical_health <= 0.45 or self.engine_temperature >= 98.0 or self.tire_pressure <= 31.0:
            return "WARN"
        return "OK"
