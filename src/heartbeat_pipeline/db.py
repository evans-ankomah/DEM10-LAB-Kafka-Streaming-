from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extensions import connection as Connection


logger = logging.getLogger(__name__)


@contextmanager
def postgres_connection(dsn: str) -> Iterator[Connection]:
    conn = psycopg2.connect(dsn)
    try:
        yield conn
    finally:
        conn.close()


def insert_heartbeat(conn: Connection, customer_id: int, timestamp, heart_rate: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.heartbeats (customer_id, ts, heart_rate)
            VALUES (%s, %s, %s)
            """,
            (customer_id, timestamp, heart_rate),
        )
    conn.commit()

