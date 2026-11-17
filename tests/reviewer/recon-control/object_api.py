"""Reviewer-only correct control. Do not copy to task workspaces."""


def read_object(actor, object_id, records):
    record = records.get(object_id)
    return record if record and record["owner"] == actor else None
