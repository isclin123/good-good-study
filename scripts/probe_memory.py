#!/usr/bin/env python3
"""Inspect a local learning SQLite database without application writes or migration."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def inspect_database(database_path):
    path = Path(database_path).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError("Database path must be an existing regular file.")
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )]
        fts_tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND lower(sql) LIKE '%using fts%'"
        )]
        counts = {}
        for name in tables:
            if name.startswith("sqlite_") or any(
                name.startswith(fts_name + "_") for fts_name in fts_tables
            ):
                continue
            quoted_name = '"' + name.replace('"', '""') + '"'
            counts[name] = connection.execute(
                "SELECT COUNT(*) FROM " + quoted_name
            ).fetchone()[0]
        integrity = [row[0] for row in connection.execute("PRAGMA quick_check")]
        foreign_key_errors = [list(row) for row in connection.execute(
            "PRAGMA foreign_key_check"
        )]
        return {
            "inspection_only": True,
            "database_path": str(path),
            "schema_version": connection.execute("PRAGMA user_version").fetchone()[0],
            "tables": tables,
            "row_counts": counts,
            "quick_check": integrity,
            "foreign_key_errors": foreign_key_errors,
            "role_context_loaded": False,
        }
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="Existing SQLite database path")
    arguments = parser.parse_args()
    try:
        result = inspect_database(arguments.db)
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(json.dumps({"error": str(exc), "inspection_only": True},
                         ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["quick_check"] == ["ok"] and not result["foreign_key_errors"] else 2


if __name__ == "__main__":
    sys.exit(main())
