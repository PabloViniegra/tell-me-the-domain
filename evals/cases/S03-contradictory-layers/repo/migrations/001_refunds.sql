CREATE TABLE refunds (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    refunded_at TEXT NOT NULL,
    CONSTRAINT refund_window CHECK (julianday(refunded_at) - julianday(created_at) <= 14)
);
