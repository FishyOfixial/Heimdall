from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Incident:
    incident_id: int
    x: float
    y: float
    severity: int
    created_tick: int
    required_responders: int = 1
    active: bool = True
    assigned_patrol_ids: set[int] = field(default_factory=set)
    arrived_patrol_ids: set[int] = field(default_factory=set)
    resolved_tick: Optional[int] = None

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def needs_more_units(self) -> bool:
        return len(self.assigned_patrol_ids) < self.required_responders

    def assign_patrol(self, patrol_id: int) -> None:
        self.assigned_patrol_ids.add(patrol_id)

    def unassign_patrol(self, patrol_id: int) -> None:
        self.assigned_patrol_ids.discard(patrol_id)
        self.arrived_patrol_ids.discard(patrol_id)

    def register_arrival(self, patrol_id: int) -> bool:
        self.arrived_patrol_ids.add(patrol_id)
        return len(self.arrived_patrol_ids) >= self.required_responders
