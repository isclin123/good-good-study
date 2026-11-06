import hashlib
import importlib.util
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'probe_memory.py'
spec = importlib.util.spec_from_file_location('memory_probe', SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / '中文 # 课程 %?.sqlite3'
        with sqlite3.connect(str(self.db)) as connection:
            connection.execute('PRAGMA user_version=7')
            connection.execute('CREATE TABLE attempts (id INTEGER PRIMARY KEY, answer TEXT)')
            connection.execute('INSERT INTO attempts VALUES (1, ?)', ('PRIVATE ANSWER',))

    def invoke(self, path):
        return subprocess.run([sys.executable, str(SCRIPT), '--db', str(path)],
                              capture_output=True, text=True)

    def test_snapshot_has_counts_version_and_no_answers(self):
        result = probe.inspect_database(self.db)
        self.assertEqual(result['schema_version'], 7)
        self.assertEqual(result['row_counts']['attempts'], 1)
        self.assertEqual(result['quick_check'], ['ok'])
        self.assertNotIn('PRIVATE ANSWER', json.dumps(result))
        self.assertFalse(result['role_context_loaded'])

    def test_does_not_change_database(self):
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        probe.inspect_database(self.db)
        after = hashlib.sha256(self.db.read_bytes()).hexdigest()
        self.assertEqual(before, after)

    def test_missing_file_is_not_created(self):
        path = self.db.parent / 'absent.sqlite3'
        result = self.invoke(path)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(path.exists())
        self.assertIn('error', json.loads(result.stderr))

    def test_invalid_database_fails_cleanly(self):
        path = self.db.parent / 'invalid.sqlite3'
        path.write_text('not a sqlite database')
        result = self.invoke(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn('error', json.loads(result.stderr))

    def test_special_table_names_are_quoted(self):
        with sqlite3.connect(str(self.db)) as connection:
            connection.execute('CREATE TABLE "table""; odd name" (id INTEGER)')
        self.assertEqual(probe.inspect_database(self.db)['row_counts']['table"; odd name'], 0)

    def test_foreign_key_errors_are_reported(self):
        with sqlite3.connect(str(self.db)) as connection:
            connection.execute('CREATE TABLE parent (id INTEGER PRIMARY KEY)')
            connection.execute('CREATE TABLE child (id INTEGER REFERENCES parent(id))')
            connection.execute('INSERT INTO child VALUES (999)')
        result = self.invoke(self.db)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(json.loads(result.stdout)['foreign_key_errors'])

    def test_wal_database_reads_committed_state(self):
        connection = sqlite3.connect(str(self.db))
        self.addCleanup(connection.close)
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('INSERT INTO attempts VALUES (2, ?)', ('SECOND PRIVATE ANSWER',))
        connection.commit()
        self.assertEqual(probe.inspect_database(self.db)['row_counts']['attempts'], 2)

    def test_fts_shadow_tables_are_not_counted(self):
        with sqlite3.connect(str(self.db)) as connection:
            connection.execute('CREATE VIRTUAL TABLE knowledge_fts USING fts5(term)')
            connection.execute("INSERT INTO knowledge_fts VALUES ('example')")
        result = probe.inspect_database(self.db)
        self.assertEqual(result['row_counts']['knowledge_fts'], 1)
        self.assertNotIn('knowledge_fts_data', result['row_counts'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
