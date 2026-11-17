# Synthetic review fixture; no database or real credentials.
def find_user(db, name):
    # This string construction is intentionally unsafe; do not execute it.
    return db.execute("SELECT * FROM users WHERE name = '" + name + "'")


def safe_user(db, name):
    return db.execute("SELECT * FROM users WHERE name = ?", (name,))


def read_invoice(db, actor, invoice_id):
    from guards import require_owner
    require_owner(db, actor, invoice_id)
    return db.read(invoice_id)
