#!/usr/bin/env python
"""Kafka topic monitor and message inspector."""

from __future__ import annotations

import json
import sys
from datetime import datetime

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from heartbeat_pipeline.config import load_config


def monitor_topic(max_messages: int = 20) -> None:
    """Monitor Kafka topic for messages."""
    config = load_config()

    try:
        consumer = KafkaConsumer(
            config.kafka_topic,
            bootstrap_servers=config.kafka_bootstrap_servers,
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            consumer_timeout_ms=5000,  # Exit after 5 seconds of no messages
        )

        print("\n" + "=" * 60)
        print(f"MONITORING KAFKA TOPIC: {config.kafka_topic}")
        print("=" * 60 + "\n")

        message_count = 0
        for message in consumer:
            message_count += 1

            payload = message.value
            print(
                f"Message #{message_count} (Partition {message.partition}, "
                f"Offset {message.offset})"
            )
            print(f"  Timestamp: {datetime.now()}")
            print(f"  Payload: {json.dumps(payload, indent=2)}")
            print()

            if message_count >= max_messages:
                break

        print(f"Received {message_count} message(s)")
        consumer.close()

    except KafkaError as e:
        print(f"Kafka Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        consumer.close()
        sys.exit(0)


if __name__ == "__main__":
    monitor_topic(max_messages=20)
