"""Tests for heartbeat data models and validation."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from heartbeat_pipeline.models import HeartbeatRecord


class TestHeartbeatRecord(unittest.TestCase):
    """Test cases for HeartbeatRecord validation."""

    def test_valid_heartbeat(self) -> None:
        """Test creation and validation of valid heartbeat record."""
        ts = datetime.now(timezone.utc)
        record = HeartbeatRecord(customer_id=1, timestamp=ts, heart_rate=72)

        self.assertEqual(record.customer_id, 1)
        self.assertEqual(record.heart_rate, 72)
        self.assertTrue(record.is_valid())
        self.assertFalse(record.is_anomaly())

    def test_heart_rate_too_low(self) -> None:
        """Test validation of too-low heart rate."""
        ts = datetime.now(timezone.utc)
        record = HeartbeatRecord(customer_id=1, timestamp=ts, heart_rate=20)

        self.assertFalse(record.is_valid())

    def test_heart_rate_too_high(self) -> None:
        """Test validation of too-high heart rate."""
        ts = datetime.now(timezone.utc)
        record = HeartbeatRecord(customer_id=1, timestamp=ts, heart_rate=250)

        self.assertFalse(record.is_valid())

    def test_anomaly_low_detection(self) -> None:
        """Test detection of anomalously low heart rate."""
        ts = datetime.now(timezone.utc)
        record = HeartbeatRecord(customer_id=1, timestamp=ts, heart_rate=40)

        self.assertTrue(record.is_valid())
        self.assertTrue(record.is_anomaly())

    def test_anomaly_high_detection(self) -> None:
        """Test detection of anomalously high heart rate."""
        ts = datetime.now(timezone.utc)
        record = HeartbeatRecord(customer_id=1, timestamp=ts, heart_rate=190)

        self.assertTrue(record.is_valid())
        self.assertTrue(record.is_anomaly())

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        ts = datetime.now(timezone.utc)
        record = HeartbeatRecord(customer_id=5, timestamp=ts, heart_rate=75)
        data = record.to_dict()

        self.assertEqual(data["customer_id"], 5)
        self.assertEqual(data["heart_rate"], 75)
        self.assertIn("timestamp", data)

    def test_from_message(self) -> None:
        """Test creation from message payload."""
        payload = {
            "customer_id": "10",
            "timestamp": "2024-01-01T12:00:00+00:00",
            "heart_rate": "85",
        }
        record = HeartbeatRecord.from_message(payload)

        self.assertEqual(record.customer_id, 10)
        self.assertEqual(record.heart_rate, 85)
        self.assertTrue(record.is_valid())

    def test_from_message_invalid_customer_id(self) -> None:
        """Test error handling for invalid customer_id."""
        payload = {
            "customer_id": "not_a_number",
            "timestamp": "2024-01-01T12:00:00+00:00",
            "heart_rate": "85",
        }
        with self.assertRaises(ValueError):
            HeartbeatRecord.from_message(payload)


if __name__ == "__main__":
    unittest.main()
