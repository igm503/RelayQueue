from queue import Queue
from typing import List, Protocol, Callable


class RelaySignal:
    STOP = object()
    EXCEPT = object()
    KILL = object()


class PutProtocol(Protocol):
    def put(self, item) -> None: ...


class RQueue:
    def __init__(
        self,
        callback: Callable,
        max_size: int = 0,
        subscribers: List[PutProtocol] = [],
    ):
        self.queue = Queue(maxsize=max_size)
        self.callback = callback
        self.subscribers = subscribers

    def get(self, block=True, timeout=None):
        item = self.queue.get(block=block, timeout=timeout)
        if item is RelaySignal.STOP:
            self.signal(signal=item, put=False)
            self.callback()
        return item

    def size(self):
        return self.queue.qsize()

    def signal(self, signal=RelaySignal.STOP, put=True):
        for sub in self.subscribers:
            sub.put(signal)
        if put:
            self.queue.put(signal)

    def put(self, item, block=True, timeout=None):
        self.queue.put(item, block=block, timeout=timeout)

    def __getattr__(self, name):
        return getattr(self.queue, name)
