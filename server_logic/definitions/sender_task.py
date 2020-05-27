from collections import namedtuple

SenderTask = namedtuple("SenderTask", ["user", "context"])
ExecutionTask = namedtuple("ExecutionTask", ["func", "args", "kwargs"])
