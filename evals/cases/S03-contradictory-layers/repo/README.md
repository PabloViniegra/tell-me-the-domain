# Refund service (eval fixture S03)

Each refund request is checked against a refund window. The service, the database, and the tests disagree on how long that window is. The skill must record both variants as a conflict, not pick one.
