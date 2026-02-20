from __future__ import annotations

import json
import logging
import os
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError

from heartbeat_pipeline.config import load_config
from heartbeat_pipeline.generator import HeartbeatGenerator
from heartbeat_pipeline.logging_config import setup_logging


logger = logging.getLogger("heartbeat.producer")


def main() -> None:
    config = load_config()
    
    # Set up logging with file rotation
    log_file = os.getenv("LOG_FILE_PATH", None)
    setup_logging(config.log_level, log_file=log_file)
    
    generator = HeartbeatGenerator(customer_count=config.customer_count)

    producer = KafkaProducer(
        bootstrap_servers=config.kafka_bootstrap_servers,
        client_id=config.producer_client_id,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    logger.info(
        "Producer started topic=%s bootstrap_servers=%s",
        config.kafka_topic,
        config.kafka_bootstrap_servers,
    )
    try:
        while True:
            event = generator.generate()
            payload = event.to_dict()
            future = producer.send(config.kafka_topic, value=payload)
            future.get(timeout=10)
            logger.info("Published heartbeat payload=%s", payload)
            time.sleep(config.producer_interval_seconds)
    except KeyboardInterrupt:
        logger.info("Producer interrupted by user")
    except KafkaError as err:
        logger.exception("Kafka producer failure: %s", err)
        raise
    finally:
        producer.flush()
        producer.close()
        logger.info("Producer stopped")


def main() -> None:
    config = load_config()
    setup_logging(config.log_level)
    generator = HeartbeatGenerator(customer_count=config.customer_count)

    producer = KafkaProducer(
        bootstrap_servers=config.kafka_bootstrap_servers,
        client_id=config.producer_client_id,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    logger.info(
        "Producer started topic=%s bootstrap_servers=%s",
        config.kafka_topic,
        config.kafka_bootstrap_servers,
    )
    try:
        while True:
            event = generator.generate()
            payload = event.to_dict()
            future = producer.send(config.kafka_topic, value=payload)
            future.get(timeout=10)
            logger.info("Published heartbeat payload=%s", payload)
            time.sleep(config.producer_interval_seconds)
    except KeyboardInterrupt:
        logger.info("Producer interrupted by user")
    except KafkaError as err:
        logger.exception("Kafka producer failure: %s", err)
        raise
    finally:
        producer.flush()
        producer.close()
        logger.info("Producer stopped")


if __name__ == "__main__":
    main()

