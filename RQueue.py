from queue import Queue, Empty
from typing import List, Protocol, Callable, Hashable


class RelaySignal:
    STOP = object()


class PutProtocol(Protocol):
    def put(self, item) -> None: ...


class RQueue:
    def __init__(
        self,
        max_size: int = 0,
        callbacks: dict[object, Callable] = {},
        subscribers: List[PutProtocol] = [],
    ):
        self.queue = Queue(maxsize=max_size)
        self.callbacks = callbacks
        self.subscribers = subscribers

    def get(self, block=True, timeout=None, ignore_empty=False, relay=False):
        try:
            item = self.queue.get(block=block, timeout=timeout)
        except Empty:
            if ignore_empty:
                return None
            raise

        self.try_callback(item)

        if relay and item is RelaySignal.STOP:
            self.relay(item, trigger_callback=False)

        return item

    def put(self, item, block=True, timeout=None):
        self.queue.put(item, block=block, timeout=timeout)

    def relay(self, signal: Hashable, trigger_callback=True):
        for sub in self.subscribers:
            sub.put(signal)
        if trigger_callback:
            self.try_callback(signal)

    def try_callback(self, signal: Hashable):
        try:
            in_callbacks = signal in self.callbacks
        except TypeError:
            in_callbacks = False
        if in_callbacks:
            self.callbacks[signal]()

    def add_callback(self, callback: Callable, signal: object):
        self.callbacks[signal] = callback

    def add_subscriber(self, subscriber: PutProtocol):
        self.subscribers.append(subscriber)

    def __getattr__(self, name):
        return getattr(self.queue, name)
