"""Synthetic fail-closed checks; these are not model or GPU tests."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from materialize_data import select_payload, verify_archive


class MaterializationTests(unittest.TestCase):
    def fixture(self):
        rows = [{"input": "", "context": "synthetic", "answers": ["test"], "dataset": "qasper", "_id": str(i)} for i in range(200)]
        raw = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode()
        selected = sorted(rows, key=lambda row: hashlib.sha256(("qasper\0" + row["_id"]).encode()).hexdigest())[:32]
        payload = ("\n".join(json.dumps(row, ensure_ascii=False) for row in selected) + "\n").encode()
        entry = {"source_rows": 200, "selected_rows": 32, "source_sha256": hashlib.sha256(raw).hexdigest(), "ids": [row["_id"] for row in selected], "selected_file_sha256": hashlib.sha256(payload).hexdigest()}
        return raw, entry, payload

    def test_exact_serialization(self):
        raw, entry, payload = self.fixture()
        self.assertEqual(select_payload("qasper", raw, entry), payload)

    def test_corrupt_source_rejected(self):
        raw, entry, _ = self.fixture()
        with self.assertRaisesRegex(ValueError, "source member SHA256"):
            select_payload("qasper", raw + b" ", entry)

    def test_duplicate_id_rejected_even_with_correct_source_hash(self):
        raw, entry, _ = self.fixture()
        rows = [json.loads(line) for line in raw.splitlines()]
        rows[-1]["_id"] = rows[0]["_id"]
        raw = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
        entry["source_sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, "duplicate source IDs"):
            select_payload("qasper", raw, entry)

    def test_wrong_selection_order_rejected(self):
        raw, entry, _ = self.fixture()
        entry["ids"] = list(reversed(entry["ids"]))
        with self.assertRaisesRegex(ValueError, "selection order"):
            select_payload("qasper", raw, entry)

    def test_wrong_output_hash_rejected(self):
        raw, entry, _ = self.fixture()
        entry["selected_file_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "selected file SHA256"):
            select_payload("qasper", raw, entry)

    def test_incomplete_archive_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "incomplete.zip"
            archive.write_bytes(b"not the archive")
            with self.assertRaisesRegex(ValueError, "archive byte count"):
                verify_archive(archive)


if __name__ == "__main__":
    unittest.main()
