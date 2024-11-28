# RQueue and RThread Library

A dud library implementing a queue and thread subclass meant to make stopping sequential thread chains easier to terminate.

Consider a program that reads frames from a video, extracts x from those frames, extracts y from x, and so on. The threads should all terminate when the video has been consumed. This was an experiment in handling that termination process within the queue object itself. 

The library is a dud because the interface is unintuitive and the problem probably better solved on a case by case basis.

## Overview

- `RQueue`: A queue with methods to add callbacks for predefined messages and send objects directly to downstream queues.
- `RThread`: A thread class with stop and kill methods that relay signals to downstream queues.

## Components

### RQueue

A Queue subclass that adds:
- Signal relay functionality
- Callback registration
- Subscriber management

```python
queue = RQueue(
    max_size=0,
    callbacks={RelaySignal.STOP: my_callback},
    subscribers=[downstream_queue]
)
```

#### `__init__(max_size: int = 0, callbacks: dict[object, Callable] = {}, subscribers: List[PutProtocol] = [])`
- `max_size`: Maximum queue size (0 for unlimited)
- `callbacks`: Map of signals to their callback functions
- `subscribers`: List of downstream queues that implement put()

#### `get(block=True, timeout=None, ignore_empty=False, relay=False) -> Any`
Retrieves item from queue. If item is registered for a callback function, executes the callback.
- `relay`: If True, propagates STOP signals to subscribers if message is STOP signal
- `ignore_empty`: If True, returns None when empty instead of raising Empty

#### `put(item, block=True, timeout=None)`
Adds item to queue
- Standard Queue.put() behavior

#### `relay(signal: Hashable, trigger_callback=True)`
Sends signal to all subscribers
- `trigger_callback`: If True, executes callback for signal if one exists

#### `add_callback(callback: Callable, signal: object)`
Registers callback function for given signal

#### `add_subscriber(subscriber: PutProtocol)`
Adds new subscriber to receive relayed signals


### RThread

A Thread subclass that:
- Integrates with RQueue for signal handling
- Provides abstract `work()` method for processing items
- Implements both graceful and immediate shutdown methods

#### `__init__(queue: RQueue, target: Callable | None = None, name: str | None = None, daemon: bool | None = None)`
- `queue`: RQueue instance for thread
- `target`: Optional work function (alternative to implementing work())
- Standard Thread parameters: name, daemon

#### `run()`
Fetches items from queue and passes them into work() method. Items are processed until STOP signal received

#### `work(item: Any)`
Abstract method to process queue items. Must be implemented by subclasses or provided via target

#### `stop(signal: object | None = RelaySignal.STOP)`
Puts STOP signal in queue

#### `kill()`
Immediate shuts down thread and puts STOP signal in downstream queues

#### `put(item, block=True, timeout=None)`
Adds item to thread's queue

## Example RThread Subclass

```python
class Worker(RThread):
    def __init__(self, next_worker):
        super().__init__(RQueue(subscribers=[next_worker]))
        self.next_worker = next_worker

    def work(self, item):
        processed_item = foo(item) # do something
        self.next_worker.put(processed_item)

# Create a chain of worker threads
final_worker = Worker()
middle_worker = Worker(final_worker) 
first_worker = Worker(middle_worker)

final_worker.start()
middle_worker.start()
first_worker.start()

for item in items_to_process:
    first_worker.put(item)

# Stop will put a STOP signal in the queue, which will pass around the work()
# method, cause the thread to stop, and then be sent to the next thread, stopping
# the entire chain
first_worker.stop()

# OR 

# Kill will immediately stop the thread and put a STOP signal in the queue for 
# the next thread
first_worker.kill()
```
