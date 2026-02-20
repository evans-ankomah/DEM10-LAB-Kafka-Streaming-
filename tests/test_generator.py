"""Tests for data generator."""

from __future__ import annotations

import unittest

from heartbeat_pipeline.generator import HeartbeatGenerator


class TestHeartbeatGenerator(unittest.TestCase):
    """Test cases for heartbeat data generation."""

    def test_generator_initialization(self) -> None:
        """Test generator initialization with customer count."""
        generator = HeartbeatGenerator(customer_count=10)
        self.assertEqual(generator.customer_count, 10)

    def test_generate_valid_heartbeat(self) -> None:
        """Test that generated heartbeats have valid values."""
        generator = HeartbeatGenerator(customer_count=100)

        for _ in range(100):
            record = generator.generate()

            # Check all fields are present
            self.assertIsNotNone(record.customer_id)
            self.assertIsNotNone(record.timestamp)
            self.assertIsNotNone(record.heart_rate)

            # Check value ranges
            self.assertGreaterEqual(record.customer_id, 1)
            self.assertLessEqual(record.customer_id, 100)
            self.assertGreater(record.heart_rate, 0)
            self.assertLess(record.heart_rate, 250)

    def test_customer_id_distribution(self) -> None:
        """Test that customer IDs are distributed across range."""
        generator = HeartbeatGenerator(customer_count=50)
        customer_ids = set()

        for _ in range(200):
            record = generator.generate()
            customer_ids.add(record.customer_id)

        # Should have multiple different customer IDs
        self.assertGreater(len(customer_ids), 1)
        self.assertLessEqual(max(customer_ids), 50)

    def test_reproducible_with_seed(self) -> None:
        """Test that generator with seed produces reproducible results."""
        gen1 = HeartbeatGenerator(customer_count=10, seed=42)
        gen2 = HeartbeatGenerator(customer_count=10, seed=42)

        records1 = [gen1.generate() for _ in range(10)]
        records2 = [gen2.generate() for _ in range(10)]

        for r1, r2 in zip(records1, records2):
            self.assertEqual(r1.customer_id, r2.customer_id)
            self.assertEqual(r1.heart_rate, r2.heart_rate)


if __name__ == "__main__":
    unittest.main()
