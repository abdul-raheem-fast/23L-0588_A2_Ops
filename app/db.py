import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class HistoryStore:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.is_postgres = database_url.startswith(("postgresql://", "postgres://"))
        if self.is_postgres:
            self.path = None
        elif database_url.startswith("sqlite:///"):
            self.path = Path(database_url.removeprefix("sqlite:///"))
            self.path.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise ValueError("DATABASE_URL must use sqlite:/// or postgresql://.")
        self.initialize()

    def connect(self):
        if self.is_postgres:
            import psycopg

            connection = psycopg.connect(self.database_url)
            connection.row_factory = psycopg.rows.dict_row
            return connection
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    model_name TEXT NOT NULL,
                    model_version TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def add_prediction(self, filename, label, confidence, model_name, model_version):
        created_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO predictions
                    (created_at, filename, label, confidence, model_name, model_version)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (created_at, filename, label, confidence, model_name, model_version),
            )

    def recent(self, limit=50):
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT created_at, filename, label, confidence, model_name, model_version
                FROM predictions ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
