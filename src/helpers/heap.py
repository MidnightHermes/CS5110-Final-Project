from collections.abc import Iterable
from dataclasses import dataclass
import heapq
from typing import Any

@dataclass(order=True)
class Entry:
    key: Any
    value: Any

    def __eq__(a, b):
        return a.value == b

class Heap:
    def __init__(self, elems: Iterable[Entry | tuple[Any, Any]]):
        if all((isinstance(e, Entry) for e in elems)):
            self._heap = list(elems)
        else:
            self._heap = [Entry(key, value) for key, value in elems]

        heapq.heapify(self._heap)

    def push(self, key, value):
        heapq.heappush(self._heap, Entry(key, value))

    def pop(self):
        return heapq.heappop(self._heap).value

    def decrease_key(self, value, new_key):
        pos = self._heap.index(value)
        self._heap[pos].key = new_key

        heapq._siftdown(self._heap, 0, pos)

    def __repr__(self):
        return self._heap.__repr__()
