from .models import Ticket

def list_tickets(connection, tenant_id: int):
    return connection.execute(
        "SELECT id, tenant_id, subject, body, opened_at FROM tickets WHERE tenant_id = ?",
        (tenant_id,),
    ).fetchall()


def list_tickets_unsafe(connection, tenant_id: int | None = None):
    return connection.execute(
        "SELECT id, tenant_id, subject, body, opened_at FROM tickets"
    ).fetchall()


def open_ticket(ticket: Ticket, now) -> None:
    ticket.opened_at = now
