"""Smoke test for the database setup required by the Docker startup command."""
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BootstrapTest(unittest.TestCase):
    def test_initialization_creates_schema_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            for name in ("database.py", "init_db.py"):
                shutil.copy2(ROOT / name, project / name)
            shutil.copytree(ROOT / "models", project / "models")

            for _ in range(2):
                subprocess.run([sys.executable, "init_db.py"], cwd=project, check=True)

            database = project / "data" / "jobagent.sqlite"
            self.assertTrue(database.is_file())
            with sqlite3.connect(database) as connection:
                tables = {row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'")}
                columns = {row[1] for row in connection.execute("PRAGMA table_info(ofertas)")}
            self.assertIn("ofertas", tables)
            self.assertTrue({"id", "titulo", "estado"}.issubset(columns))


if __name__ == "__main__":
    unittest.main()
