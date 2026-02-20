from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    app_name: str
    log_level: str
    kafka_bootstrap_servers: str
    kafka_topic: str
    kafka_group_id: str
    producer_interval_seconds: float
    customer_count: int
    pg_host: str
    pg_port: int
    pg_db: str
    pg_user: str
    pg_password: str
    producer_client_id: str
    consumer_client_id: str

    @property
    def postgres_dsn(self) -> str:
        return (
            f"host={self.pg_host} "
            f"port={self.pg_port} "
            f"dbname={self.pg_db} "
            f"user={self.pg_user} "
            f"password={self.pg_password}"
        )


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    if not value:
        raise ValueError(f"Environment variable {name} is empty.")
    return value


def load_config() -> AppConfig:
    return AppConfig(
        app_name=_get_env("APP_NAME", "heartbeat-pipeline"),
        log_level=_get_env("LOG_LEVEL", "INFO").upper(),
        kafka_bootstrap_servers=_get_env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        kafka_topic=_get_env("KAFKA_TOPIC", "heartbeats"),
        kafka_group_id=_get_env("KAFKA_GROUP_ID", "heartbeat-consumer-group"),
        producer_interval_seconds=float(_get_env("PRODUCER_INTERVAL_SECONDS", "1.0")),
        customer_count=int(_get_env("CUSTOMER_COUNT", "100")),
        pg_host=_get_env("POSTGRES_HOST", "localhost"),
        pg_port=int(_get_env("POSTGRES_PORT", "5432")),
        pg_db=_get_env("POSTGRES_DB", "heartbeat_db"),
        pg_user=_get_env("POSTGRES_USER", "heartbeat_user"),
        pg_password=_get_env("POSTGRES_PASSWORD", "heartbeat_password"),
        producer_client_id=_get_env("KAFKA_PRODUCER_CLIENT_ID", "heartbeat-producer"),
        consumer_client_id=_get_env("KAFKA_CONSUMER_CLIENT_ID", "heartbeat-consumer"),
    )

