import argparse
import random
from pathlib import Path

from simulation.clock import SimulationClock
from simulation.dispatcher import IntelligentDispatcher, ReactiveDispatcher
from simulation.patrol import Patrol
from simulation.predictor import RiskPredictor
from simulation.spatial import AdaptiveSpatialPartition
from simulation.sue import StochasticUrbanSimulator
from simulation.world import World


def build_world(width: int, height: int, patrol_count: int) -> World:
    partition = AdaptiveSpatialPartition(width=float(width), height=float(height), unit_count=patrol_count)
    world = World(width=float(width), height=float(height), partition=partition)
    world.set_mechanic_base(
        random.uniform(width * 0.42, width * 0.58),
        random.uniform(height * 0.42, height * 0.58),
    )
    world.set_gas_stations(
        [
            (random.uniform(width * 0.08, width * 0.25), random.uniform(height * 0.10, height * 0.25)),
            (random.uniform(width * 0.75, width * 0.92), random.uniform(height * 0.10, height * 0.25)),
            (random.uniform(width * 0.08, width * 0.25), random.uniform(height * 0.75, height * 0.90)),
            (random.uniform(width * 0.75, width * 0.92), random.uniform(height * 0.75, height * 0.90)),
        ]
    )

    for patrol_id in range(1, patrol_count + 1):
        x = random.uniform(30, width - 30)
        y = random.uniform(50, height - 30)
        speed = random.uniform(45.0, 70.0)
        world.add_patrol(Patrol(patrol_id=patrol_id, x=x, y=y, speed=speed))

    return world


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador de Gemelo Digital Urbano")
    parser.add_argument("--mode", choices=["reactive", "intelligent"], default="intelligent")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--metrics-file", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--ticks", type=int, default=3600)
    args = parser.parse_args()

    random.seed(args.seed)

    width, height = 1100, 700

    # ---------- HEADLESS MODE ----------
    if args.headless:
        sim_clock = SimulationClock(tick_seconds=1.0)
        world = build_world(width, height, patrol_count=16)
        world.operating_mode = args.mode

        predictor = RiskPredictor()
        world.risk_high_threshold = predictor.high_risk_threshold
        dispatcher = ReactiveDispatcher() if args.mode == "reactive" else IntelligentDispatcher()
        sue = StochasticUrbanSimulator(seed=args.seed)

        while sim_clock.current_tick < args.ticks:
            current_tick = sim_clock.tick()
            world.step(current_tick, sim_clock.tick_seconds, predictor, dispatcher, sue=sue)

        # imprimir SOLO csv limpio
        header, row = world.metrics_engine.to_csv_row()
        print(header)
        print(row)
        return

    # ---------- VISUAL MODE ----------
    import pygame
    from ui.controls import ControlState, Controls
    from ui.renderer import Renderer

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Simulador de Gemelo Digital Urbano [{args.mode}] seed={args.seed}")

    font = pygame.font.SysFont("consolas", 18)
    renderer = Renderer(screen, font)
    controls = Controls()
    control_state = ControlState()

    sim_clock = SimulationClock(tick_seconds=1.0)
    world = build_world(width, height, patrol_count=16)
    world.operating_mode = args.mode

    predictor = RiskPredictor()
    world.risk_high_threshold = predictor.high_risk_threshold
    dispatcher = ReactiveDispatcher() if args.mode == "reactive" else IntelligentDispatcher()
    sue = StochasticUrbanSimulator(seed=args.seed)

    real_clock = pygame.time.Clock()
    accumulator = 0.0
    real_step = 0.1

    running = True
    while running:
        frame_dt = real_clock.tick(60) / 1000.0
        accumulator += frame_dt

        running = controls.process_events(world, sim_clock, control_state)

        while accumulator >= real_step:
            accumulator -= real_step
            if not control_state.paused:
                current_tick = sim_clock.tick()
                world.step(current_tick, sim_clock.tick_seconds, predictor, dispatcher, sue=sue)
                if sim_clock.current_tick >= args.ticks:
                    running = False
                    break

        renderer.draw(world, sim_clock.current_tick, control_state.paused)
        pygame.display.flip()

    pygame.quit()



if __name__ == "__main__":
    main()
