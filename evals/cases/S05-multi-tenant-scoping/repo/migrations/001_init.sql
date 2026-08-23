CREATE TABLE tickets (
    id INTEGER PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    opened_at TEXT
);

CREATE INDEX idx_tickets_tenant ON tickets(tenant_id);
