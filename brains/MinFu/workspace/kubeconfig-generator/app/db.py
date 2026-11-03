"""Kết nối PostgreSQL (psycopg 3) và chạy migration."""
from __future__ import annotations

import contextlib
import logging
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

log = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

# Khoá advisory (số tuỳ ý nhưng cố định)
LOCK_MIGRATE = 7_310_001
LOCK_CLEANUP = 7_310_002


class Database:
    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 8):
        self.dsn = dsn
        self.pool = ConnectionPool(
            dsn,
            min_size=min_size,
            max_size=max_size,
            kwargs={"row_factory": dict_row, "autocommit": False},
            open=True,
        )

    def close(self) -> None:
        self.pool.close()

    @contextlib.contextmanager
    def tx(self):
        """Một transaction: commit khi xong, rollback khi lỗi."""
        with self.pool.connection() as conn:
            with conn.transaction():
                yield conn

    def ping(self) -> bool:
        try:
            with self.tx() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:  # noqa: BLE001
            return False

    @contextlib.contextmanager
    def try_advisory_lock(self, key: int):
        """Giữ khoá ở mức session trên một kết nối riêng. Yield True nếu lấy được."""
        with self.pool.connection() as conn:
            conn.autocommit = True
            got = conn.execute("SELECT pg_try_advisory_lock(%s) AS ok", (key,)).fetchone()["ok"]
            try:
                yield got
            finally:
                if got:
                    conn.execute("SELECT pg_advisory_unlock(%s)", (key,))
                conn.autocommit = False

    def migrate(self) -> list[str]:
        applied: list[str] = []
        with psycopg.connect(self.dsn, autocommit=True, row_factory=dict_row) as conn:
            conn.execute("SELECT pg_advisory_lock(%s)", (LOCK_MIGRATE,))
            try:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS schema_migrations ("
                    " version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
                )
                done = {r["version"] for r in conn.execute("SELECT version FROM schema_migrations")}
                for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
                    if path.name in done:
                        continue
                    sql = path.read_text(encoding="utf-8")
                    with conn.transaction():
                        conn.execute(sql)
                        conn.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (path.name,))
                    applied.append(path.name)
                    log.info("Đã chạy migration %s", path.name)
            finally:
                conn.execute("SELECT pg_advisory_unlock(%s)", (LOCK_MIGRATE,))
        return applied
