"""Application constants and configuration values."""

# Logger names
LOGGER_PRODUCER = "heartbeat.producer"
LOGGER_CONSUMER = "heartbeat.consumer"
LOGGER_DB = "heartbeat.db"
LOGGER_GENERATOR = "heartbeat.generator"

# Heartbeat validation ranges
MIN_HEART_RATE = 30
MAX_HEART_RATE = 220

# Anomaly detection thresholds
ALERT_LOW_HEART_RATE = 45
ALERT_HIGH_HEART_RATE = 180

# Kafka defaults
DEFAULT_KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
DEFAULT_KAFKA_TOPIC = "heartbeats"
DEFAULT_KAFKA_GROUP_ID = "heartbeat-consumer-group"

# Database defaults
DEFAULT_PG_HOST = "localhost"
DEFAULT_PG_PORT = 5432
DEFAULT_PG_DB = "heartbeat_db"
DEFAULT_PG_USER = "heartbeat_user"
DEFAULT_PG_PASSWORD = "heartbeat_password"

# Producer configuration
DEFAULT_INTERVAL_SECONDS = 1.0
DEFAULT_CUSTOMER_COUNT = 100

# Retry configuration
KAFKA_SEND_TIMEOUT_SEC = 10
DB_RETRY_MAX_ATTEMPTS = 3
DB_RETRY_WAIT_SEC = 2
