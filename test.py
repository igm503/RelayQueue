from queue import Queue

import numpy as np

from RQueue import RQueue, RelaySignal
from RThread import RThread

stop = False


def callback_a():
    global stop
    stop = True


def callback_b():
    global stop
    stop = True


print("Testing put and get")

relay_a = RQueue(callbacks={RelaySignal.STOP: callback_a})
relay_b = RQueue(callbacks={RelaySignal.STOP: callback_b})

relay_a.put(RelaySignal.STOP)
message = relay_a.get()
assert stop, "relay a did not trigger"
stop = False

relay_b.put(message)
relay_b.get()
assert stop, "relay b did not trigger"


print("Testing direct")

relay_a = RQueue(callbacks={RelaySignal.STOP: callback_a}, subscribers=[relay_b])

relay_a.put(RelaySignal.STOP)
relay_a.get()
assert stop, "relay a did not trigger"
stop = False
relay_a.relay(RelaySignal.STOP)

relay_b.get()
assert stop, "relay b did not trigger"


class Worker1(RThread):
    def __init__(self, next_worker):
        super().__init__(RQueue(subscribers=[next_worker]))
        self.next_worker = next_worker

    def work(self, item):
        array1, array2 = item
        sum = array1 + array2
        self.next_worker.put(sum)


class Worker2(RThread):
    def __init__(self, next_worker):
        super().__init__(RQueue(subscribers=[next_worker]))
        self.next_worker = next_worker

    def work(self, item):
        squared = item**2
        self.next_worker.put(squared)


class Worker3(RThread):
    def __init__(self):
        super().__init__(RQueue())
        self.output_queue = Queue()

    def work(self, item):
        squared = item**3
        self.output_queue.put(squared)


arrays = [np.random.rand(100) for _ in range(100)]

final_worker = Worker3()
middle_worker = Worker2(final_worker)
first_worker = Worker1(middle_worker)

final_worker.start()
middle_worker.start()
first_worker.start()

for array in arrays:
    first_worker.put((array, array))
first_worker.stop()
final_worker.join()

arrays = [np.random.rand(100) for _ in range(100)]

final_worker = Worker3()
middle_worker = Worker2(final_worker)
first_worker = Worker1(middle_worker)

final_worker.start()
middle_worker.start()
first_worker.start()

for array in arrays:
    first_worker.put((array, array))
first_worker.kill()
final_worker.join()
