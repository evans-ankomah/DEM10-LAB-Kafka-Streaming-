from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

from kafka import KafkaProducer

from heartbeat_pipeline.config import load_config
from heartbeat_pipeline.logging_config import setup_logging


logger = logging.getLogger("heartbeat.test_producer")


def main() -> None:
    config = load_config()
    
    # Set up logging with file rotation
    log_file = os.getenv("LOG_FILE_PATH", None)
    setup_logging(config.log_level, log_file=log_file)


def main() -> None:
    config = load_config()
    setup_logging(config.log_level)

    samples = [
        {"customer_id": 10, "timestamp": datetime.now(timezone.utc).isoformat(), "heart_rate": 72},
        {"customer_id": 11, "timestamp": datetime.now(timezone.utc).isoformat(), "heart_rate": 38},
        {"customer_id": 12, "timestamp": datetime.now(timezone.utc).isoformat(), "heart_rate": 195},
        {"customer_id": 13, "timestamp": datetime.now(timezone.utc).isoformat(), "heart_rate": 250},
        {"customer_id": "invalid", "timestamp": "bad-ts", "heart_rate": "abc"},
    ]

    producer = KafkaProducer(
        bootstrap_servers=config.kafka_bootstrap_servers,
        client_id=f"{config.producer_client_id}-tests",
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    for payload in samples:
        producer.send(config.kafka_topic, value=payload).get(timeout=10)
        logger.info("Published test payload=%s", payload)

    producer.flush()
    producer.close()
    logger.info("Published %s test payloads", len(samples))


if __name__ == "__main__":
    main()

