"""
SQLite DB helper for TestLab AI pipeline logging
location: memory/testlab.db (or configure via DATABASE_PATH env var)
"""

import json
import sqlite3
from typing import Any, Dict


def init_db(db_path: str):
    """Initialize DB and create table if missing."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            ts_created TEXT,
            report_json TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def insert_pipeline_run(db_path: str, run_id: str, report: Dict[str, Any]):
    """Insert or replace a pipeline run record."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO pipeline_runs (run_id, ts_created, report_json)
        VALUES (?, datetime('now'), ?)
        """,
        (run_id, json.dumps(report))
    )
    conn.commit()
    conn.close()


def fetch_pipeline_run(db_path: str, run_id: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT run_id, ts_created, report_json FROM pipeline_runs WHERE run_id = ?", (run_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {"run_id": row[0], "ts_created": row[1], "report": json.loads(row[2])}
