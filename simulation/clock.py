from dataclasses import dataclass


@dataclass
class SimulationClock:
    tick_seconds: float = 1.0
    current_tick: int = 0

    def tick(self) -> int:
        self.current_tick += 1
        return self.current_tick

    @property
    def current_time(self) -> float:
        return self.current_tick * self.tick_seconds
