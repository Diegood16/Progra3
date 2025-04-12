# cola.py
from collections import deque

class ColaDeMisiones:
    def __init__(self):
        self.items = deque()

    def enqueue(self, mission):
        self.items.append(mission)

    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        return None

    def first(self):
        return self.items[0] if not self.is_empty() else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        return list(self.items)