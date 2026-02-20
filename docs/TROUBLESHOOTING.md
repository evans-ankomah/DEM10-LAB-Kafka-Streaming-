# Troubleshooting Guide

## Common Issues and Solutions

### 1. Kafka Connection Issues

#### Error: `Failed to connect to bootstrap servers`

**Symptoms:**
```
KafkaError: NoBrokersAvailable: Unable to connect to Kafka brokers
```

**Causes:**
- Kafka container not running
- Wrong bootstrap server address
- Kafka not fully initialized

**Solutions:**
```bash
# Check if Kafka is running
docker-compose ps kafka

# Restart Kafka
docker-compose restart kafka

# Verify Kafka is listening
docker-compose exec kafka nc -zv localhost 9092

# Check firewall/network
docker-compose logs kafka | tail -50
```

---

### 2. PostgreSQL Connection Issues

#### Error: `could not translate host name "postgres" to address`

**Symptoms:**
```
psycopg2.operational_error: could not translate host name "postgres" to address
```

**Causes:**
- PostgreSQL container not running
- Wrong host name (use "postgres" in Docker, "localhost" locally)
- PostgreSQL initialization incomplete

**Solutions:**
```bash
# Check if Postgres is running
docker-compose ps postgres

# Check Postgres health
docker-compose exec postgres pg_isready -U heartbeat_user

# Check Postgres logs
docker-compose logs postgres | tail -50

# Verify database exists
docker-compose exec postgres psql -U heartbeat_user -l
```

---

### 3. No Data Flowing Through Pipeline

#### Symptom: Consumer running but no data inserted

**Debugging Steps:**

```bash
# 1. Check producer is sending data
docker-compose logs heartbeat-producer | tail -20

# 2. Check Kafka topic has messages (using Confluent Kafka UI)
# Visit http://localhost:8080

# 3. Check consumer is processing messages
docker-compose logs heartbeat-consumer | tail -20

# 4. Check database directly
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  -c "SELECT COUNT(*) FROM heartbeats;"

# 5. Check consumer group offset
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group heartbeat-consumer-group \
  --describe
```

**Common Causes:**
- Consumer group lag (reading from old offset)
  - Solution: Delete consumer group and restart
    ```bash
    docker-compose exec kafka kafka-consumer-groups \
      --bootstrap-server localhost:9092 \
      --group heartbeat-consumer-group \
      --delete
    ```
- Topic auto-creation disabled
  - Solution: Create topic manually
    ```bash
    docker-compose exec kafka kafka-topics \
      --create \
      --topic heartbeats \
      --bootstrap-server localhost:9092
    ```

---

### 4. Validation Rejection

#### Symptom: Consumer logs show "Rejected out-of-range record"

**What it means:** Heart rate value is outside 30-220 BPM range

**Debugging:**
```bash
# View rejected records
docker-compose logs heartbeat-consumer | grep "Rejected"

# Check anomalies
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  -c "SELECT * FROM heartbeats WHERE heart_rate < 30 OR heart_rate > 220 LIMIT 10;"
```

**Note:** This is expected behavior. Test data includes intentionally invalid values.

---

### 5. Logging Not Appearing

#### Symptom: No logs in `logs/` directory

**Causes:**
- LOG_FILE_PATH not set
- Logs directory doesn't exist or no write permission
- Container log driver not configured

**Solutions:**
```bash
# Verify environment variable
docker-compose exec heartbeat-consumer env | grep LOG_FILE

# Check logs directory exists
ls -la logs/

# Check container logs instead
docker-compose logs heartbeat-consumer

# Enable file logging in docker-compose.yml
# Add LOG_FILE_PATH: logs/consumer.log to environment section
```

---

### 6. Database Schema Not Initialized

#### Error: `relation "public.heartbeats" does not exist`

**Causes:**
- init.sql not executed during container startup
- Container restarted after initial creation

**Solutions:**
```bash
# Verify schema exists
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  -c "\dt public.*"

# Manually initialize if missing
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  < sql/init.sql

# Or rebuild from scratch
docker-compose down -v
docker-compose up -d
```

---

### 7. Grafana Connection to PostgreSQL

#### Error: "Test connection failed" in Grafana

**Steps:**
1. Go to Grafana: http://localhost:3000
2. Connections → Data Sources
3. Add PostgreSQL with:
   - Host: `postgres:5432` (not localhost!)
   - Database: `heartbeat_db`
   - User: `heartbeat_user`
   - Password: `heartbeat_password`
   - SSL Mode: `disable`

4. Click "Test and save"

---

### 8. Tests Failing

#### Error: Tests can't find modules

**Solution:**
```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/project/src:$PYTHONPATH

# Or run from project root
python -m pytest tests/ -v
```

#### Error: Tests require Kafka/Postgres running

**Solutions:**
```bash
# Start services first
docker-compose up -d

# Run tests with integration markers only
pytest tests/ -m integration

# Or run unit tests only
pytest tests/test_models.py tests/test_config.py -v
```

---

### 9. High Memory Usage

#### Symptom: Docker containers consuming excessive memory

**Solutions:**
```bash
# Check memory usage
docker stats

# Reduce producer interval (send less frequently)
# Edit docker-compose.yml: PRODUCER_INTERVAL_SECONDS: 5.0

# Limit container memory
# Add to docker-compose.yml service:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

---

### 10. Consumer Lag Increasing

#### Symptom: Confluent Kafka UI shows large offset lag

**Causes:**
- Consumer processing slower than producer sending
- Database inserts are slow
- Network bottleneck

**Solutions:**
```bash
# Increase producer interval (slower generation)
PRODUCER_INTERVAL_SECONDS=2.0

# Add multiple consumer instances (requires topic partitions)
# Launch second consumer with different KAFKA_CONSUMER_CLIENT_ID

# Check database performance
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  -c "SELECT COUNT(*) FROM heartbeats;"
```

---

## Performance Diagnostics

### Check System Resource Usage
```bash
# Docker container stats
docker stats

# Log file sizes
du -sh logs/

# Database table size
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  -c "SELECT pg_size_pretty(pg_total_relation_size('heartbeats'));"
```

### Monitor Message Rate
```bash
# Count messages in Kafka topic
docker-compose exec kafka kafka-run-class kafka.tools.JmxTool \
  --object-name kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec
```

### Check Consumer Lag Over Time
```bash
watch -n 5 "docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group heartbeat-consumer-group \
  --describe"
```

---

## Getting Help

### Collect Diagnostics
```bash
# Export logs for analysis
docker-compose logs > logs/docker-compose.log

# Export consumer group info
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group heartbeat-consumer-group \
  --describe > logs/consumer-group.txt

# Export database schema
docker-compose exec postgres pg_dump -U heartbeat_user heartbeat_db \
  --schema-only > logs/schema.sql
```

### Reset Everything
```bash
# Complete system reset
docker-compose down -v
docker-compose up -d
docker-compose exec postgres psql -U heartbeat_user -d heartbeat_db \
  -c "\dt public.*"  # Verify schema
```
