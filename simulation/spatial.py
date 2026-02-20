import math
from dataclasses import dataclass


@dataclass
class AdaptiveSpatialPartition:
    width: float
    height: float
    unit_count: int
    density_factor: float = 1.8
    min_zones: int = 16
    max_zones: int = 220
    reference_area: float = 1_000_000.0

    def __post_init__(self) -> None:
        self.recalculate(self.width, self.height, self.unit_count)

    def recalculate(self, width: float | None = None, height: float | None = None, unit_count: int | None = None) -> None:
        if width is not None:
            self.width = max(1.0, width)
        if height is not None:
            self.height = max(1.0, height)
        if unit_count is not None:
            self.unit_count = max(1, unit_count)

        area = self.width * self.height

        # Small maps get more zones and large maps fewer zones.
        scale = math.sqrt(self.reference_area / max(area, 1.0))
        target_zones = int(round(self.unit_count * self.density_factor * scale * 8))
        target_zones = max(self.min_zones, min(self.max_zones, target_zones))

        self.cell_size = max(8.0, math.sqrt(area / target_zones))
        self.cols = max(1, int(math.ceil(self.width / self.cell_size)))
        self.rows = max(1, int(math.ceil(self.height / self.cell_size)))

    def point_to_zone(self, x: float, y: float) -> tuple[int, int]:
        clamped_x = min(max(x, 0.0), self.width - 1e-6)
        clamped_y = min(max(y, 0.0), self.height - 1e-6)
        zone_x = int(clamped_x // self.cell_size)
        zone_y = int(clamped_y // self.cell_size)
        return (zone_x, zone_y)

    def zone_bounds(self, zone: tuple[int, int]) -> tuple[float, float, float, float]:
        zx, zy = zone
        x0 = zx * self.cell_size
        y0 = zy * self.cell_size
        x1 = min(self.width, x0 + self.cell_size)
        y1 = min(self.height, y0 + self.cell_size)
        return (x0, y0, x1, y1)

    def zone_center(self, zone: tuple[int, int]) -> tuple[float, float]:
        x0, y0, x1, y1 = self.zone_bounds(zone)
        return ((x0 + x1) * 0.5, (y0 + y1) * 0.5)

    def valid_zone(self, zone: tuple[int, int]) -> bool:
        zx, zy = zone
        return 0 <= zx < self.cols and 0 <= zy < self.rows

    def neighbor_zones(self, zone: tuple[int, int], radius: int = 1) -> list[tuple[int, int]]:
        zx, zy = zone
        neighbors: list[tuple[int, int]] = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nz = (zx + dx, zy + dy)
                if self.valid_zone(nz):
                    neighbors.append(nz)
        return neighbors
