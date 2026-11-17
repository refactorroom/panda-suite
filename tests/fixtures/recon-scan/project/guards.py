def require_owner(db, actor, invoice_id):
    if db.owner(invoice_id) != actor:
        raise PermissionError("not owner")
