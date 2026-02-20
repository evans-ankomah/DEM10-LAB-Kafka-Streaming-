from __future__ import annotations

import json
import logging
import os

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from heartbeat_pipeline.config import load_config
from heartbeat_pipeline.db import insert_heartbeat, postgres_connection
from heartbeat_pipeline.logging_config import setup_logging
from heartbeat_pipeline.models import HeartbeatRecord


logger = logging.getLogger("heartbeat.consumer")


def main() -> None:
    config = load_config()
    
    # Set up logging with file rotation
    log_file = os.getenv("LOG_FILE_PATH", None)
    setup_logging(config.log_level, log_file=log_file)


def main() -> None:
    config = load_config()
    setup_logging(config.log_level)

    consumer = KafkaConsumer(
        config.kafka_topic,
        bootstrap_servers=config.kafka_bootstrap_servers,
        client_id=config.consumer_client_id,
        group_id=config.kafka_group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    logger.info(
        "Consumer started topic=%s bootstrap_servers=%s group_id=%s",
        config.kafka_topic,
        config.kafka_bootstrap_servers,
        config.kafka_group_id,
    )

    try:
        with postgres_connection(config.postgres_dsn) as conn:
            for message in consumer:
                try:
                    record = HeartbeatRecord.from_message(message.value)
                except (KeyError, TypeError, ValueError) as err:
                    logger.warning("Skipping malformed payload=%s err=%s", message.value, err)
                    continue

                if not record.is_valid():
                    logger.warning("Rejected out-of-range record payload=%s", record.to_dict())
                    continue

                if record.is_anomaly():
                    logger.warning("Anomaly detected payload=%s", record.to_dict())

                insert_heartbeat(
                    conn=conn,
                    customer_id=record.customer_id,
                    timestamp=record.timestamp,
                    heart_rate=record.heart_rate,
                )
                logger.info("Stored heartbeat payload=%s", record.to_dict())
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user")
    except KafkaError as err:
        logger.exception("Kafka consumer failure: %s", err)
        raise
    finally:
        consumer.close()
        logger.info("Consumer stopped")


if __name__ == "__main__":
    main()

