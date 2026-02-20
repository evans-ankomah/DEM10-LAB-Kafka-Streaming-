from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


MIN_HEART_RATE = 30
MAX_HEART_RATE = 220
ALERT_LOW = 45
ALERT_HIGH = 180


@dataclass(frozen=True)
class HeartbeatRecord:
    customer_id: int
    timestamp: datetime
    heart_rate: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "timestamp": self.timestamp.isoformat(),
            "heart_rate": self.heart_rate,
        }

    @staticmethod
    def from_message(payload: dict[str, Any]) -> "HeartbeatRecord":
        return HeartbeatRecord(
            customer_id=int(payload["customer_id"]),
            timestamp=_parse_timestamp(payload["timestamp"]),
            heart_rate=int(payload["heart_rate"]),
        )

    def is_valid(self) -> bool:
        return MIN_HEART_RATE <= self.heart_rate <= MAX_HEART_RATE

    def is_anomaly(self) -> bool:
        return self.heart_rate < ALERT_LOW or self.heart_rate > ALERT_HIGH


def _parse_timestamp(raw_value: str) -> datetime:
    dt = datetime.fromisoformat(raw_value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

