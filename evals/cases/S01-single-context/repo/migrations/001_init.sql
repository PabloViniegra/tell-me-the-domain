CREATE TABLE claims (
    id INTEGER PRIMARY KEY,
    hospital_id INTEGER NOT NULL,
    insurer_ref TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    status TEXT NOT NULL,
    reviewer_id INTEGER,
    submitted_at TEXT,
    CONSTRAINT paid_requires_reviewer CHECK (status <> 'PAID' OR reviewer_id IS NOT NULL)
);
