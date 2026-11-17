import unittest
from object_api import read_object


class ObjectTest(unittest.TestCase):
    def test_owner_reads_object(self):
        row = {"owner": "synthetic-alice", "value": "synthetic-document"}
        self.assertEqual(row, read_object("synthetic-alice", "doc1", {"doc1": row}))

    def test_missing_object(self):
        self.assertIsNone(read_object("synthetic-alice", "missing", {}))
