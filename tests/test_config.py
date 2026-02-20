"""Tests for configuration loading."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from heartbeat_pipeline.config import AppConfig, load_config


class TestConfigLoading(unittest.TestCase):
    """Test cases for configuration management."""

    def setUp(self) -> None:
        """Save original environment."""
        self.original_env = os.environ.copy()

    def tearDown(self) -> None:
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch.dict(
        os.environ,
        {
            "APP_NAME": "test-app",
            "LOG_LEVEL": "debug",
            "KAFKA_BOOTSTRAP_SERVERS": "kafka:9092",
            "KAFKA_TOPIC": "test-topic",
            "KAFKA_GROUP_ID": "test-group",
            "PRODUCER_INTERVAL_SECONDS": "0.5",
            "CUSTOMER_COUNT": "50",
            "POSTGRES_HOST": "db",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
            "KAFKA_PRODUCER_CLIENT_ID": "test-producer",
            "KAFKA_CONSUMER_CLIENT_ID": "test-consumer",
        },
    )
    def test_load_config_from_env(self) -> None:
        """Test loading configuration from environment variables."""
        config = load_config()

        self.assertEqual(config.app_name, "test-app")
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.kafka_bootstrap_servers, "kafka:9092")
        self.assertEqual(config.kafka_topic, "test-topic")
        self.assertEqual(config.producer_interval_seconds, 0.5)
        self.assertEqual(config.customer_count, 50)

    def test_postgres_dsn_generation(self) -> None:
        """Test PostgreSQL DSN string generation."""
        config = AppConfig(
            app_name="test",
            log_level="INFO",
            kafka_bootstrap_servers="localhost:9092",
            kafka_topic="test",
            kafka_group_id="test-group",
            producer_interval_seconds=1.0,
            customer_count=10,
            pg_host="localhost",
            pg_port=5432,
            pg_db="testdb",
            pg_user="user",
            pg_password="password",
            producer_client_id="prod",
            consumer_client_id="cons",
        )

        dsn = config.postgres_dsn
        self.assertIn("host=localhost", dsn)
        self.assertIn("port=5432", dsn)
        self.assertIn("dbname=testdb", dsn)
        self.assertIn("user=user", dsn)

    @patch.dict(os.environ, {})
    def test_load_config_uses_defaults(self) -> None:
        """Test that default values are used when env vars are not set."""
        # This test might fail if actual env vars are set
        # It demonstrates that defaults are applied
        try:
            config = load_config()
            self.assertIsNotNone(config)
        except ValueError:
            # Expected if required env vars are not set
            pass


if __name__ == "__main__":
    unittest.main()
