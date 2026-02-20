#!/usr/bin/env python
"""Database inspection and query tool."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import RealDictCursor

from heartbeat_pipeline.config import load_config


def get_latest_records(cursor, limit: int = 10) -> list[dict]:
    """Fetch the latest heartbeat records."""
    cursor.execute(
        "SELECT * FROM heartbeats ORDER BY ts DESC LIMIT %s",
        (limit,),
    )
    return cursor.fetchall()


def get_stats(cursor) -> dict:
    """Get database statistics."""
    cursor.execute(
        """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT customer_id) as unique_customers,
            MIN(ts) as oldest_record,
            MAX(ts) as newest_record,
            AVG(heart_rate) as avg_heart_rate,
            STDDEV(heart_rate) as stddev_heart_rate
        FROM heartbeats
        """
    )
    result = cursor.fetchone()
    return {
        "total_records": result[0],
        "unique_customers": result[1],
        "oldest_record": result[2],
        "newest_record": result[3],
        "avg_heart_rate": round(float(result[4]) if result[4] else 0, 2),
        "stddev_heart_rate": round(float(result[5]) if result[5] else 0, 2),
    }


def get_anomalies(cursor, hours: int = 1) -> list[dict]:
    """Find records with anomalous heart rates."""
    cursor.execute(
        """
        SELECT * FROM heartbeats
        WHERE (heart_rate < 45 OR heart_rate > 180)
          AND ts > NOW() - INTERVAL '%s hours'
        ORDER BY ts DESC
        LIMIT 20
        """,
        (hours,),
    )
    return cursor.fetchall()


def main() -> None:
    """Main entry point."""
    try:
        config = load_config()
        conn = psycopg2.connect(config.postgres_dsn)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("\n" + "=" * 60)
        print("HEARTBEAT DATABASE INSPECTION")
        print("=" * 60 + "\n")

        # Statistics
        print("DATABASE STATISTICS")
        print("-" * 60)
        stats = get_stats(cursor)
        for key, value in stats.items():
            print(f"  {key:.<40} {value}")

        # Latest records
        print("\n\nLATEST RECORDS (last 10)")
        print("-" * 60)
        records = get_latest_records(cursor, limit=10)
        for i, record in enumerate(records, 1):
            print(
                f"  {i}. Customer {record['customer_id']}: "
                f"{record['heart_rate']} BPM @ {record['ts']}"
            )

        # Anomalies
        print("\n\nRECENT ANOMALIES (last 1 hour)")
        print("-" * 60)
        anomalies = get_anomalies(cursor, hours=1)
        if anomalies:
            for i, record in enumerate(anomalies, 1):
                status = "TOO LOW" if record["heart_rate"] < 45 else "TOO HIGH"
                print(
                    f"  {i}. Customer {record['customer_id']}: "
                    f"{record['heart_rate']} BPM ({status}) @ {record['ts']}"
                )
        else:
            print("  No anomalies detected in the last hour.")

        print("\n" + "=" * 60 + "\n")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
