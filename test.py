from RQueue import RQueue, RelaySignal

stop = False


def callback_a():
    global stop
    stop = True


def callback_b():
    global stop
    stop = True


print("Testing put and get")

relay_a = RQueue(callback_a)
relay_b = RQueue(callback_b)

relay_a.put(RelaySignal.STOP)
message = relay_a.get()
assert stop, "relay a did not trigger"
stop = False

relay_b.put(message)
relay_b.get()
assert stop, "relay b did not trigger"


print("Testing direct")

relay_a = RQueue(callback_a, subscribers=[relay_b])

relay_a.put(RelaySignal.STOP)
relay_a.get()
assert stop, "relay a did not trigger"
stop = False

relay_b.get()
assert stop, "relay b did not trigger"
