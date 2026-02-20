from dataclasses import dataclass
import pygame


@dataclass
class ControlState:
    paused: bool = False


class Controls:
    def process_events(self, world, clock, control_state: ControlState) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    control_state.paused = not control_state.paused
                elif event.key == pygame.K_r:
                    world.recalculate_zones()

        return True
