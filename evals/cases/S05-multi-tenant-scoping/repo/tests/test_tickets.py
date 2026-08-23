from src.tickets.service import list_tickets, list_tickets_unsafe


def test_scoped_query_filters_by_tenant():
    def fake_connection(rows):
        class C:
            def execute(self, sql, params=()):
                self.sql = sql
                self.params = params
                return self

            def fetchall(self):
                return [r for r in rows if r["tenant_id"] == self.params[0]]
        return C()

    rows = [
        {"id": 1, "tenant_id": 1, "subject": "a", "body": "x", "opened_at": None},
        {"id": 2, "tenant_id": 2, "subject": "b", "body": "y", "opened_at": None},
    ]
    out = list_tickets(fake_connection(rows), tenant_id=1)
    assert all(r["tenant_id"] == 1 for r in out)


def test_unsafe_query_returns_all_tenants():
    rows = [
        {"id": 1, "tenant_id": 1, "subject": "a", "body": "x", "opened_at": None},
        {"id": 2, "tenant_id": 2, "subject": "b", "body": "y", "opened_at": None},
    ]
    out = list_tickets_unsafe(object())
    assert len(out) == 2
