from __future__ import annotations

from queue import Queue

from simulation.telemetry_packet import TelemetryPacket


class TelemetryBus:
    def __init__(self) -> None:
        self._queue: Queue[TelemetryPacket] = Queue()

    def publish(self, packet: TelemetryPacket) -> None:
        self._queue.put(packet)

    def consume_all(self) -> list[TelemetryPacket]:
        packets: list[TelemetryPacket] = []
        while not self._queue.empty():
            packets.append(self._queue.get_nowait())
        return packets
