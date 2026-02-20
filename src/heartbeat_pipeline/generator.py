from __future__ import annotations

import random
from datetime import datetime, timezone

from heartbeat_pipeline.models import HeartbeatRecord


class HeartbeatGenerator:
    def __init__(self, customer_count: int, seed: int | None = None) -> None:
        self.customer_count = customer_count
        self._random = random.Random(seed)
        self._baselines = {
            customer_id: self._random.randint(60, 90)
            for customer_id in range(1, customer_count + 1)
        }

    def generate(self) -> HeartbeatRecord:
        customer_id = self._random.randint(1, self.customer_count)
        baseline = self._baselines[customer_id]
        swing = self._random.randint(-15, 15)
        rare_spike = self._random.choice([0] * 96 + [self._random.randint(-40, 40)] * 4)
        heart_rate = max(25, min(230, baseline + swing + rare_spike))
        return HeartbeatRecord(
            customer_id=customer_id,
            timestamp=datetime.now(timezone.utc),
            heart_rate=heart_rate,
        )

