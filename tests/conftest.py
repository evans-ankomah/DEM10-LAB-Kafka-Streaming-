"""Pytest configuration and fixtures."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest

from heartbeat_pipeline.config import AppConfig
from heartbeat_pipeline.models import HeartbeatRecord


@pytest.fixture
def sample_config() -> AppConfig:
    """Provide a sample configuration for tests."""
    return AppConfig(
        app_name="test-app",
        log_level="DEBUG",
        kafka_bootstrap_servers="localhost:9092",
        kafka_topic="test-heartbeats",
        kafka_group_id="test-consumer-group",
        producer_interval_seconds=0.1,
        customer_count=10,
        pg_host="localhost",
        pg_port=5432,
        pg_db="test_heartbeat_db",
        pg_user="testuser",
        pg_password="testpass",
        producer_client_id="test-producer",
        consumer_client_id="test-consumer",
    )


@pytest.fixture
def sample_heartbeat_record() -> HeartbeatRecord:
    """Provide a sample valid heartbeat record."""
    return HeartbeatRecord(
        customer_id=1,
        timestamp=datetime.now(timezone.utc),
        heart_rate=72,
    )


@pytest.fixture
def sample_heartbeat_payload() -> dict:
    """Provide a sample heartbeat payload as it would arrive from Kafka."""
    return {
        "customer_id": 5,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "heart_rate": 85,
    }


@pytest.fixture
def sample_anomaly_payload() -> dict:
    """Provide a sample heartbeat payload with anomalous heart rate."""
    return {
        "customer_id": 5,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "heart_rate": 195,  # Above alert threshold
    }


@pytest.fixture
def sample_invalid_payload() -> dict:
    """Provide a sample invalid heartbeat payload."""
    return {
        "customer_id": "not_a_number",
        "timestamp": "invalid-date",
        "heart_rate": "not_a_number",
    }


# Markers for test categorization
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (deselect with '-m \"not unit\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (requires external services)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
