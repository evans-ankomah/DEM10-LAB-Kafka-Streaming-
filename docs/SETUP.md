# Setup Instructions

## Prerequisites

- Docker & Docker Compose (or local installations of Kafka, PostgreSQL)
- Python 3.8+
- Git

## Local Development Setup

### 1. Clone and Install

```bash
# Navigate to project directory
cd "Kafka project"

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file and customize
cp .env.example .env

# Edit .env with your settings (if not using Docker)
# Set KAFKA_BOOTSTRAP_SERVERS, POSTGRES_HOST, etc.
```

### 3. Start Services (Docker)

```bash
# Build and start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Optional: View logs
docker-compose logs -f
```

### 4. Verify Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db -c "SELECT * FROM heartbeats LIMIT 5;"
```

## Running the Pipeline

### Start Producer

```bash
# Terminal 1: Run synthetic data generator + producer
python src/producer.py

# Should output:
# INFO | producer | Producer started topic=heartbeats...
# INFO | producer | Published heartbeat payload={...}
```

### Start Consumer

```bash
# Terminal 2: Run consumer (stores data in DB)
python src/consumer.py

# Should output:
# INFO | consumer | Consumer started topic=heartbeats...
# INFO | consumer | Stored heartbeat payload={...}
```

### Test Pipeline

```bash
# Terminal 3: Send test data (valid, invalid, anomalies)
python src/test_data_producer.py

# Check consumer logs for:
# - Accepted records: "Stored heartbeat"
# - Anomalies: "Anomaly detected"
# - Invalid data: "Skipping malformed payload"
```

## Using Grafana Dashboard

1. Open http://localhost:3000
2. Login: `admin` / `admin`
3. Add PostgreSQL data source:
   - Host: `postgres:5432`
   - Database: `heartbeat_db`
   - User: `heartbeat_user`
   - Password: `heartbeat_password`
4. Import dashboard from `grafana/dashboards/heartbeat-overview.json`

## Using Confluent Kafka UI

- Open http://localhost:8080
- Monitor Kafka topics, consumer groups, brokers, and messages in real-time
- View detailed cluster metrics and lag monitoring

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_models.py -v

# Run with coverage
python -m pytest tests/ --cov=src/heartbeat_pipeline --cov-report=html
```

## Troubleshooting

### Kafka Connection Error

```
Failed to connect to Kafka bootstrap servers
```

**Solution:**
- Ensure Kafka is running: `docker-compose ps kafka`
- Check KAFKA_BOOTSTRAP_SERVERS: localhost:9092 (local) or kafka:29092 (Docker)

### PostgreSQL Connection Error

```
psycopg2.OperationalError: could not translate host name
```

**Solution:**
- Ensure PostgreSQL is running: `docker-compose ps postgres`
- Check POSTGRES_HOST env var (localhost for local, postgres for Docker)

### Topic Not Found

```
KafkaError: Topic 'heartbeats' does not exist
```

**Solution:**
- Kafka auto-creates topics (KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true")
- Or manually create: `docker-compose exec kafka kafka-topics --create --topic heartbeats --bootstrap-server localhost:9092`

### No Data in Database

1. Check producer logs for "Published heartbeat"
2. Check consumer logs for "Stored heartbeat"
3. Verify connection: `docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db -c "SELECT COUNT(*) FROM heartbeats;"`

## Stopping Services

```bash
# Stop all running services
docker-compose down

# Stop and remove volumes (DELETE DATA)
docker-compose down -v
```
