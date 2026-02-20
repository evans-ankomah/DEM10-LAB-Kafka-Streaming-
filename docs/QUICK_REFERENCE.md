# Quick Reference Card

## Project Initialization

```bash
# 1. Setup
cd "Kafka project"
cp .env.example .env

# 2. Start
docker-compose up -d --build

# 3. Verify
docker-compose ps                    # All containers should be healthy
docker-compose logs heartbeat-producer  # Check producer
docker-compose logs heartbeat-consumer  # Check consumer
```

## Common Tasks

### View Data Flow

```bash
# Terminal 1: Watch producer
docker-compose logs -f heartbeat-producer

# Terminal 2: Watch consumer
docker-compose logs -f heartbeat-consumer

# Terminal 3: Send test data
docker-compose exec heartbeat-producer python src/test_data_producer.py
```

### Inspect Database

```bash
# Latest 10 records
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  -c "SELECT * FROM heartbeats ORDER BY ts DESC LIMIT 10;"

# Statistical summary
python scripts/inspect_db.py

# Record count
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  -c "SELECT COUNT(*) FROM heartbeats;"
```

### Monitor Kafka

```bash
# Via Confluent Kafka UI
open http://localhost:8080

# Via script
python scripts/monitor_kafka.py

# Via kafka CLI
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group heartbeat-consumer-group \
  --describe
```

### Access Grafana

```bash
# Open in browser
open http://localhost:3000

# Login: admin / admin
# Check datasource "Postgres-Heartbeats"
# Dashboard: "Heartbeat Monitoring Overview"
```

## Testing

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/heartbeat_pipeline --cov-report=html
coverage report

# Specific test module
pytest tests/test_models.py -v

# Specific test
pytest tests/test_models.py::TestHeartbeatRecord::test_valid_heartbeat -v
```

## Troubleshooting

| Problem | Command | Solution |
|---------|---------|----------|
| No data in DB | `docker-compose logs heartbeat-consumer` | Check for validation errors |
| Kafka connection error | `docker-compose logs kafka` | Restart Kafka service |
| PostgreSQL connection error | `docker-compose logs postgres` | Verify pg_isready |
| Logs not appearing | `ls -la logs/` | Check LOG_FILE_PATH env var |
| Consumer lag high | `monitor_kafka.py` | Increase producer interval |

## Stop & Reset

```bash
# Stop (preserve data)
docker-compose down

# Stop everything (delete data)
docker-compose down -v

# Clean up images
docker-compose down -v --rmi all
```

## Environment Variables

```bash
# .env file locations
KAFKA_BOOTSTRAP_SERVERS=localhost:9092      # Kafka broker (Docker: kafka:29092)
POSTGRES_HOST=localhost                     # DB host (Docker: postgres)
LOG_LEVEL=INFO                              # DEBUG|INFO|WARNING|ERROR
PRODUCER_INTERVAL_SECONDS=1.0               # Delay between readings
CUSTOMER_COUNT=100                          # Simulated customers
LOG_FILE_PATH=logs/heartbeat_pipeline.log   # Optional file logging
```

## File Locations

| Component | File |
|-----------|------|
| Producer code | `src/producer.py` |
| Consumer code | `src/consumer.py` |
| Data generator | `src/heartbeat_pipeline/generator.py` |
| Database schema | `sql/init.sql` |
| Configuration | `src/heartbeat_pipeline/config.py` |
| Logging | `src/heartbeat_pipeline/logging_config.py` |
| Tests | `tests/` |
| Documentation | `docs/` |
| Helper scripts | `scripts/` |

## Important Ports

| Service | Port | URL |
|---------|------|-----|
| Kafka | 9092 | - |
| PostgreSQL | 5432 | - |
| Grafana | 3000 | http://localhost:3000 |
| Confluent Kafka UI | 8080 | http://localhost:8080 |
| Zookeeper | 2181 | - |

## Key Commands

```bash
# View docker-compose services
docker-compose ps

# Stream all logs
docker-compose logs -f

# Execute commands in container
docker-compose exec heartbeat-producer python src/test_data_producer.py
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db

# Stop specific service
docker-compose stop heartbeat-consumer

# Restart specific service
docker-compose restart heartbeat-producer

# View resource usage
docker stats

# Clean up unused images
docker image prune
```

## Data Validation Rules

| Field | Valid Range | Anomaly Range | Action if Invalid |
|-------|-------------|----------------|-------------------|
| customer_id | 1-N | N/A | Skip record |
| timestamp | ISO8601 | N/A | Skip record |
| heart_rate | 30-220 | <45 or >180 | Insert + warn if valid, skip if not |

## Metrics to Monitor

- **Throughput**: Messages/sec (target: 1 msg/sec per config)
- **Latency**: Time from producer to database
- **Database Size**: `SELECT pg_size_pretty(pg_total_relation_size('heartbeats'));`
- **Record Count**: `SELECT COUNT(*) FROM heartbeats;`
- **Consumer Lag**: Via Confluent Kafka UI or CLI
- **Anomaly Rate**: `SELECT COUNT(*) FROM heartbeats WHERE heart_rate < 45 OR heart_rate > 180;`

## Documentation Map

- **Getting Started**: [SETUP.md](SETUP.md)
- **How It Works**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing**: [DEVELOPMENT.md](DEVELOPMENT.md)
- **Solving Problems**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Project Overview**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**Need help?** Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide!
