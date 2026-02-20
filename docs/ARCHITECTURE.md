# Architecture & Design

## System Overview

The Heartbeat Monitoring Pipeline is a real-time stream processing system that:

1. **Generates** synthetic customer heartbeat data
2. **Streams** it through Kafka topics  
3. **Validates** and filters anomalies
4. **Stores** in PostgreSQL for analysis
5. **Monitors** via Grafana dashboards

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   DATA SIMULATION LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  HeartbeatGenerator                                          │
│  - Generates random readings per customer                    │
│  - Realistic baseline + variation + rare spikes              │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  KAFKA PRODUCER       │
         │  (src/producer.py)    │
         │  - Serializes to JSON │
         │  - Publishes to topic │
         └───────────┬───────────┘
                     │
    ┌────────────────▼────────────────┐
    │   KAFKA TOPIC: heartbeats        │
    │   (Distributed message queue)    │
    └────────────────┬────────────────┘
                     │
         ┌───────────▼────────────┐
         │  KAFKA CONSUMER        │
         │  (src/consumer.py)     │
         │  - Deserializes JSON   │
         │  - Validates ranges    │
         │  - Detects anomalies   │
         └───────────┬────────────┘
                     │
    ┌────────────────▼──────────────────────┐
    │     POSTGRESQL DATABASE               │
    │     Table: heartbeats                 │
    │     - customer_id (indexed)           │
    │     - ts (timestamptz, indexed)       │
    │     - heart_rate (range validated)    │
    │     - created_at (automatic)          │
    └────────────────┬──────────────────────┘
                     │
     ┌───────────────┴────────────────┐
     │                                │
  ┌──▼──────┐                  ┌─────▼────────┐
  │ GRAFANA │                  │ KAFKA UI │
  │Dashboard│                  │ Kafka Monitor│
  └─────────┘                  └──────────────┘
```

## Data Flow

### Valid Record Path
```
HeartbeatGenerator 
  → JSON (customer_id: int, timestamp: ISO8601, heart_rate: int)
  → Kafka Topic
  → Consumer: Parse & Validate
  → Check: 30 ≤ heart_rate ≤ 220?
  → YES: Insert into DB
  → Log: "Stored heartbeat"
```

### Invalid Record Path
```
Kafka Topic
  → Consumer: Parse & Validate
  → Check: Valid JSON & required fields?
  → NO: Skip & Log warning
  → "Skipping malformed payload"
```

### Anomaly Record Path
```
Kafka Topic
  → Consumer: Parse & Validate
  → Check: 45 ≤ heart_rate ≤ 180?
  → NO: Still insert but flag
  → Log: "Anomaly detected - heart_rate=195"
```

## Component Details

### 1. HeartbeatGenerator
- **File**: `src/heartbeat_pipeline/generator.py`
- **Responsibility**: Generate synthetic heart rate data
- **Algorithm**:
  - Each customer has a baseline (60-90 BPM)
  - Add daily variation (-15 to +15 BPM)
  - 4% chance of spike (-40 to +40 BPM)
  - Clamp to [25, 230]
- **Output**: `HeartbeatRecord(customer_id, timestamp, heart_rate)`

### 2. Kafka Producer
- **File**: `src/producer.py`
- **Responsibility**: Read from generator, publish to Kafka
- **Features**:
  - Configurable interval between messages
  - JSON serialization
  - Error handling for Kafka failures
  - Graceful shutdown on interrupt

### 3. Kafka Consumer
- **File**: `src/consumer.py`
- **Responsibility**: Listen to Kafka, validate, store in DB
- **Features**:
  - JSON deserialization
  - Input validation (range checks)
  - Anomaly detection (flags unusual values)
  - Transaction handling (commit after DB insert)
  - Graceful error handling

### 4. PostgreSQL Schema
- **File**: `sql/init.sql`
- **Table**: `public.heartbeats`
  - `id`: BIGSERIAL PRIMARY KEY (auto-increment)
  - `customer_id`: INT NOT NULL (customer identifier)
  - `ts`: TIMESTAMPTZ NOT NULL (measurement timestamp)
  - `heart_rate`: INT NOT NULL CHECK (30-220 range)
  - `created_at`: TIMESTAMPTZ DEFAULT NOW() (insertion time)
- **Indexes**:
  - `idx_heartbeats_ts`: For time-range queries
  - `idx_heartbeats_customer_ts`: For per-customer time-series

### 5. Validation Rules

| Field | Rule | Action on Failure |
|-------|------|------------------|
| customer_id | Must be integer 1-N | Skip record (malformed) |
| timestamp | Valid ISO8601 | Skip record (malformed) |
| heart_rate | Must be 30-220 | Reject record (invalid) |
| heart_rate | Alert if <45 or >180 | Insert + log anomaly |

## Configuration Management

- **Source**: Environment variables (`.env` file)
- **Loading**: `src/heartbeat_pipeline/config.py`
- **Type**: Dataclass with validation
- **Defaults**: Provided in `.env.example`

Key configurations:
```python
KAFKA_BOOTSTRAP_SERVERS  # Kafka broker addresses
KAFKA_TOPIC              # Topic to publish/subscribe
POSTGRES_*               # Database connection details
PRODUCER_INTERVAL_SECONDS # Delay between data points
CUSTOMER_COUNT           # Number of simulated customers
LOG_LEVEL                # Logging verbosity
```

## Error Handling Strategy

### Producer Errors
- **Kafka unavailable**: Log error, retry with exponential backoff
- **Serialization failure**: Log and skip record
- **Keyboard interrupt**: Gracefully flush and close

### Consumer Errors
- **Kafka unavailable**: Attempt reconnect
- **Malformed JSON**: Log warning, skip record
- **Database connection lost**: Attempt reconnect, queue messages
- **Validation failure**: Log and reject, do not store
- **Keyboard interrupt**: Close connection gracefully

## Monitoring & Observability

### Logging
- **Pattern**: `TIMESTAMP | LEVEL | LOGGER | FUNCTION:LINE | MESSAGE`
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Output**: Console + rotating file (`logs/heartbeat_pipeline.log`)
- **Rotation**: 10MB max size, 5 backup files

### Confluent Kafka UI
- Monitor Kafka partitions, offsets, and brokers
- View message contents in real-time
- Track consumer lag and lag trending
- Full-featured cluster management interface

### Grafana Dashboard
- Time-series visualization of heart rate data
- Customer-specific trends
- Anomaly spotting via alerts

## Scalability Considerations

### Current Limitations
- Single Kafka broker (no replication)
- Single consumer (would process partitions sequentially)
- No sharding of data

### Future Improvements
- Multi-partition Kafka topic (for parallel processing)
- Consumer groups with multiple instances
- Database partitioning by time
- Caching layer (Redis) for frequent queries
