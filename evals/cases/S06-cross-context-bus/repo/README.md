# Order Notifications (eval fixture S06)

Two contexts share an event without an explicit contract: billing publishes `InvoicePaid` to its own bus; notifications subscribes and re-sends an email. The contract is implicit in the payload shape used by both sides.
