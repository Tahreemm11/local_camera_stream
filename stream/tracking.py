import time, numpy as np
from numpy.linalg import norm

class FaceRegistry:
    def __init__(self, sim_threshold=0.45, ttl_seconds=10):
        self.sim_threshold = sim_threshold
        self.ttl = ttl_seconds
        self._items = {}      # pid -> {"emb": np.array, "last_seen": ts}
        self._next_id = 1

    @staticmethod
    def cos(a, b):
        d = (norm(a) * norm(b)) or 1e-9
        return float(np.dot(a, b) / d)

    def match_or_create(self, emb: np.ndarray):
        now = time.time()
        for pid in list(self._items.keys()):
            if now - self._items[pid]["last_seen"] > self.ttl:
                del self._items[pid]

        best_pid, best_sim = None, -1.0
        for pid, row in self._items.items():
            s = self.cos(row["emb"], emb)
            if s > best_sim:
                best_sim, best_pid = s, pid

        if best_sim >= self.sim_threshold and best_pid:
            self._items[best_pid].update(emb=emb, last_seen=now)
            return best_pid, best_sim

        pid = self._next_id; self._next_id += 1
        self._items[pid] = {"emb": emb, "last_seen": now}
        return pid, None

registry = FaceRegistry(sim_threshold=0.45, ttl_seconds=10)
