# Development Guide

## Project Layout

```
Kafka project/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── docker-compose.yml        # Multi-container orchestration
├── Dockerfile                # Container image definition
├── README.md                 # Project overview & quick start
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata & build config
│
├── src/                      # Source code
│   ├── producer.py           # Main producer script
│   ├── consumer.py           # Main consumer script  
│   ├── test_data_producer.py # Data generator for testing
│   │
│   └── heartbeat_pipeline/   # Core pipeline package
│       ├── __init__.py
│       ├── config.py         # Configuration loader
│       ├── constants.py      # App-wide constants
│       ├── exceptions.py     # Custom exceptions
│       ├── generator.py      # Synthetic data generator
│       ├── models.py         # Data models & validation
│       ├── db.py             # Database operations
│       ├── logging_utils.py  # Legacy logging (deprecated)
│       ├── logging_config.py # Enhanced logging with rotation
│       └── __pycache__/      # Python bytecode cache
│
├── tests/                    # Unit & integration tests
│   ├── __init__.py
│   ├── test_models.py        # HeartbeatRecord validation tests
│   ├── test_config.py        # Configuration loading tests
│   ├── test_generator.py     # Data generation tests
│   └── conftest.py           # Pytest configuration & fixtures
│
├── docs/                     # Documentation
│   ├── SETUP.md              # Setup & installation guide
│   ├── ARCHITECTURE.md       # System design & components
│   ├── DEVELOPMENT.md        # Development guidelines
│   └── TROUBLESHOOTING.md    # Common issues & solutions
│
├── scripts/                  # Helper scripts
│   ├── run_tests.sh          # Run test suite
│   ├── setup_local.sh        # Local development setup
│   ├── query_db.py           # Database inspection tool
│   └── monitor_kafka.py      # Kafka topic monitor
│
├── grafana/                  # Grafana configuration
│   ├── dashboards/
│   │   └── heartbeat-overview.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yml
│       └── datasources/
│           └── postgres.yml
│
├── sql/                      # Database scripts
│   └── init.sql              # Schema creation
│
└── logs/                     # Application logs (created at runtime)
    └── heartbeat_pipeline.log
```

## Code Style & Standards

### Python Style
- **Standard**: PEP 8
- **Type Hints**: Required for all functions and class attributes
- **Docstrings**: Google-style docstrings for public functions

### Example Function
```python
def insert_heartbeat(conn: Connection, customer_id: int, timestamp: datetime, heart_rate: int) -> None:
    """
    Insert a validated heartbeat record into the database.

    Args:
        conn: PostgreSQL database connection.
        customer_id: ID of the customer.
        timestamp: When the reading was taken.
        heart_rate: Beats per minute (should be validated before calling).

    Raises:
        psycopg2.Error: If database insertion fails.
    """
    # Implementation...
```

### Import Organization
```python
# Standard library
from __future__ import annotations
import json
import logging
from pathlib import Path

# Third-party
import psycopg2
from kafka import KafkaProducer

# Local
from heartbeat_pipeline.config import load_config
from heartbeat_pipeline.models import HeartbeatRecord
```

## Adding New Features

### 1. Add a New Validation Rule

Example: Alert if customer hasn't sent data in 5 minutes

```python
# In models.py
@dataclass
class HeartbeatRecord:
    # ... existing fields ...
    
    def is_stale(self, current_time: datetime, threshold_seconds: int = 300) -> bool:
        """Check if reading is older than threshold."""
        age = (current_time - self.timestamp).total_seconds()
        return age > threshold_seconds

# In consumer.py
if record.is_stale(datetime.now(timezone.utc)):
    logger.warning("Stale record detected: %s", record.customer_id)
```

### 2. Add a Custom Metric/Log

```python
# In logging_config.py - add ContextFilter usage
filter_ = ContextFilter({"request_id": "12345", "service": "consumer"})
logger.addFilter(filter_)
# Now all logs will include: request_id=12345 service=consumer
```

### 3. Add a Database Query Helper

```python
# In db.py
def get_customer_heart_rate_stats(
    conn: Connection, 
    customer_id: int, 
    hours: int = 24
) -> dict[str, float]:
    """Calculate statistics for a customer's recent readings."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                AVG(heart_rate) as avg_hr,
                MIN(heart_rate) as min_hr,
                MAX(heart_rate) as max_hr,
                STDDEV(heart_rate) as stddev_hr
            FROM public.heartbeats
            WHERE customer_id = %s 
              AND ts > NOW() - INTERVAL '%s hours'
        """, (customer_id, hours))
        row = cur.fetchone()
    return {
        "avg_heart_rate": row[0],
        "min_heart_rate": row[1],
        "max_heart_rate": row[2],
        "stddev_heart_rate": row[3],
    }
```

## Testing

### Running Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific test
python -m pytest tests/test_models.py::TestHeartbeatRecord::test_valid_heartbeat -v

# With coverage
python -m pytest tests/ --cov=src/heartbeat_pipeline --cov-report=term-missing
```

### Writing New Tests
```python
# tests/test_new_feature.py
import unittest
from heartbeat_pipeline.new_module import MyClass

class TestMyClass(unittest.TestCase):
    def setUp(self) -> None:
        """Initialize test fixtures."""
        self.obj = MyClass()
    
    def test_happy_path(self) -> None:
        """Test normal operation."""
        result = self.obj.do_something()
        self.assertIsNotNone(result)
    
    def test_error_case(self) -> None:
        """Test error handling."""
        with self.assertRaises(ValueError):
            self.obj.do_something_invalid()
```

## Debugging

### Enable Debug Logging
```bash
# Launch with debug level
LOG_LEVEL=DEBUG python src/producer.py
```

### Check Consumer Group Status
```bash
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group heartbeat-consumer-group \
  --describe
```

### Query Database Directly
```bash
docker-compose exec postgres psql \
  -U heartbeat_user \
  -d heartbeat_db \
  -c "SELECT * FROM heartbeats ORDER BY ts DESC LIMIT 10;"
```

## Deployment Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] No lint issues: `pylint src/`
- [ ] Type hints verified: `mypy src/`
- [ ] Docker image builds: `docker build -t heartbeat:latest .`
- [ ] Docker-compose stack starts: `docker-compose up --no-start`
- [ ] Environment variables set in production `.env`
- [ ] Database backups configured
- [ ] Log rotation tested
- [ ] Monitoring/alerting configured
- [ ] Grafana dashboards imported
