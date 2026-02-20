from __future__ import annotations

import pygame

from simulation.patrol import PatrolState


class Renderer:
    BG = (20, 24, 31)
    GRID = (42, 47, 58)
    TEXT = (220, 226, 232)
    SERVICE_ZONE = (80, 170, 250)
    GAS_STATION = (255, 215, 90)

    STATE_COLOR = {
        PatrolState.IDLE: (95, 220, 135),
        PatrolState.AVAILABLE: (80, 210, 120),
        PatrolState.PATROLLING: (120, 220, 170),
        PatrolState.PREVENTIVE_PATROL: (65, 190, 255),
        PatrolState.RESPONDING: (255, 180, 60),
        PatrolState.REFUELING: (100, 180, 255),
        PatrolState.MAINTENANCE: (200, 140, 255),
        PatrolState.EMERGENCY_RETURN: (255, 120, 90),
        PatrolState.OUT_OF_SERVICE: (130, 130, 130),
    }
    INCIDENT = (255, 60, 60)

    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        self.screen = screen
        self.font = font

    def draw(self, world, tick: int, paused: bool) -> None:
        self.screen.fill(self.BG)
        self._draw_zones(world)
        self._draw_service_zone(world)
        self._draw_incidents(world)
        self._draw_patrols(world)
        self._draw_hud(world, tick, paused)

    def _draw_zones(self, world) -> None:
        cell = int(max(6, world.partition.cell_size))

        for zone, risk in world.risk_map.items():
            x0, y0, x1, y1 = world.partition.zone_bounds(zone)
            intensity = min(215, int(risk * 50))
            red = min(255, 40 + intensity)
            color = (red, 30, 30)
            rect = pygame.Rect(int(x0), int(y0), int(x1 - x0), int(y1 - y0))
            pygame.draw.rect(self.screen, color, rect)

        for col in range(world.partition.cols + 1):
            x = int(col * cell)
            pygame.draw.line(self.screen, self.GRID, (x, 0), (x, int(world.height)), 1)
        for row in range(world.partition.rows + 1):
            y = int(row * cell)
            pygame.draw.line(self.screen, self.GRID, (0, y), (int(world.width), y), 1)

    def _draw_service_zone(self, world) -> None:
        mx, my = world.mechanic_base
        pygame.draw.circle(self.screen, self.SERVICE_ZONE, (int(mx), int(my)), 13, width=2)
        label = self.font.render("MECANICO", True, self.SERVICE_ZONE)
        self.screen.blit(label, (int(mx) + 14, int(my) - 8))

        for idx, (gx, gy) in enumerate(world.gas_stations, start=1):
            pygame.draw.rect(self.screen, self.GAS_STATION, pygame.Rect(int(gx) - 7, int(gy) - 7, 14, 14), width=2)
            glabel = self.font.render(f"GAS {idx}", True, self.GAS_STATION)
            self.screen.blit(glabel, (int(gx) + 10, int(gy) - 8))

    def _draw_patrols(self, world) -> None:
        for patrol in world.patrols:
            color = self.STATE_COLOR.get(patrol.state, self.STATE_COLOR[PatrolState.OUT_OF_SERVICE])
            pygame.draw.circle(
                self.screen,
                (80, 120, 165),
                (int(patrol.x), int(patrol.y)),
                int(patrol.coverage_radius),
                width=1,
            )
            pygame.draw.circle(self.screen, color, (int(patrol.x), int(patrol.y)), 7)

    def _draw_incidents(self, world) -> None:
        for incident in world.active_incidents():
            radius = 7 + incident.required_responders
            pygame.draw.circle(self.screen, self.INCIDENT, (int(incident.x), int(incident.y)), radius, width=2)

    def _draw_hud(self, world, tick: int, paused: bool) -> None:
        text = (
            f"Tick: {tick} | Patrols: {len(world.patrols)} | "
            f"Active incidents: {len(world.active_incidents())} | "
            f"Zone cell: {world.partition.cell_size:.1f} | "
            f"{'PAUSED' if paused else 'RUNNING'}"
        )
        surface = self.font.render(text, True, self.TEXT)
        self.screen.blit(surface, (10, 10))

        help_text = "Incidentes: SUE automatico | Space: pausa | R: recalcular zonas"
        help_surface = self.font.render(help_text, True, self.TEXT)
        self.screen.blit(help_surface, (10, 34))
