CREATE TABLE IF NOT EXISTS public.heartbeats (
    id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    heart_rate INT NOT NULL CHECK (heart_rate BETWEEN 30 AND 220),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_heartbeats_ts ON public.heartbeats (ts DESC);
CREATE INDEX IF NOT EXISTS idx_heartbeats_customer_ts ON public.heartbeats (customer_id, ts DESC);

