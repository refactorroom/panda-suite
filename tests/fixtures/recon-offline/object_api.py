"""Synthetic in-memory object service; no actual API, network or real user data."""


def read_object(actor, object_id, records):
    return records.get(object_id)
