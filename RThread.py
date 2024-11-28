from abc import ABC, abstractmethod
from typing import Callable, Any
from threading import Thread

from RQueue import RQueue, RelaySignal


class RThread(Thread, ABC):
    def __init__(
        self,
        queue: RQueue,
        target: Callable | None = None,
        name: str | None = None,
        daemon: bool | None = None,
    ):
        Thread.__init__(self, name=name, daemon=daemon)
        self.queue = queue
        self.process = False
        if target is not None:
            self.work = target

    def run(self):
        self.process = True
        while self.process:
            item = self.queue.get(relay=True)
            if item is RelaySignal.STOP:
                self.process = False
                break
            self.work(item)

    @abstractmethod
    def work(self, item: Any):
        pass

    def stop(self, signal: object | None = RelaySignal.STOP):
        if signal is not None:
            self.queue.put(signal)

    def kill(self):
        self.process = False
        self.queue.put(RelaySignal.STOP)
        self.queue.relay(RelaySignal.STOP)


    def put(self, item, block=True, timeout=None):
        self.queue.put(item, block=block, timeout=timeout)
