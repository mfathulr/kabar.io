"""Neon Postgres storage helpers with pooled connections."""

from __future__ import annotations

import os
from typing import Any

import pandas as pd

try:
    from psycopg_pool import ConnectionPool
except Exception:  # pragma: no cover - optional dependency for Neon usage
    ConnectionPool = None  # type: ignore[assignment]

from storage.csv_handler import EXPECTED_COLUMNS, save_to_csv

TABLE_NAME = "news_articles"
POOL_MIN_SIZE = 1
POOL_MAX_SIZE = 5
_POOL: ConnectionPool | None = None


def _get_database_url() -> str:
    """Return the Neon/Postgres URL from env."""
    return os.getenv("DATABASE_URL", "").strip()


def _get_pool() -> ConnectionPool:
    """Create a pooled Postgres client on demand."""
    global _POOL

    if _POOL is not None:
        return _POOL

    if ConnectionPool is None:
        raise RuntimeError("psycopg-pool is not installed")

    database_url = _get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL is not configured")

    _POOL = ConnectionPool(
        conninfo=database_url,
        min_size=POOL_MIN_SIZE,
        max_size=POOL_MAX_SIZE,
        kwargs={"autocommit": True},
    )
    return _POOL


def _normalize_value(value: Any) -> Any:
    """Convert pandas values to psycopg-friendly Python values."""
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if hasattr(value, "to_pydatetime"):
        try:
            return value.to_pydatetime()
        except Exception:
            return value
    return value


def _row_payload(row: pd.Series) -> dict[str, Any]:
    """Map a DataFrame row to the database schema."""
    payload = {column: _normalize_value(row.get(column)) for column in EXPECTED_COLUMNS}
    return payload


def _ensure_table(conn) -> None:
    """Create the target table if it does not exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            article_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            source_id TEXT,
            source_url TEXT,
            country TEXT,
            category TEXT,
            language TEXT,
            pubDate TIMESTAMPTZ,
            fetched_at TIMESTAMPTZ,
            pub_date_wib TIMESTAMPTZ,
            domain TEXT,
            sentiment TEXT,
            sentiment_confidence DOUBLE PRECISION,
            sentiment_reason TEXT
        )
        """
    )


def save_to_neon(df: pd.DataFrame) -> None:
    """Insert or update rows in Neon Postgres using a pooled connection."""
    if df.empty:
        print("No rows to save to Neon.")
        return

    pool = _get_pool()
    rows = [_row_payload(row) for _, row in df.iterrows()]

    with pool.connection() as conn:
        _ensure_table(conn)
        with conn.cursor() as cur:
            cur.executemany(
                f"""
                INSERT INTO {TABLE_NAME} (
                    article_id,
                    title,
                    description,
                    source_id,
                    source_url,
                    country,
                    category,
                    language,
                    pubDate,
                    fetched_at,
                    pub_date_wib,
                    domain,
                    sentiment,
                    sentiment_confidence,
                    sentiment_reason
                ) VALUES (
                    %(article_id)s,
                    %(title)s,
                    %(description)s,
                    %(source_id)s,
                    %(source_url)s,
                    %(country)s,
                    %(category)s,
                    %(language)s,
                    %(pubDate)s,
                    %(fetched_at)s,
                    %(pub_date_wib)s,
                    %(domain)s,
                    %(sentiment)s,
                    %(sentiment_confidence)s,
                    %(sentiment_reason)s
                )
                ON CONFLICT (article_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    source_id = EXCLUDED.source_id,
                    source_url = EXCLUDED.source_url,
                    country = EXCLUDED.country,
                    category = EXCLUDED.category,
                    language = EXCLUDED.language,
                    pubDate = EXCLUDED.pubDate,
                    fetched_at = EXCLUDED.fetched_at,
                    pub_date_wib = EXCLUDED.pub_date_wib,
                    domain = EXCLUDED.domain,
                    sentiment = EXCLUDED.sentiment,
                    sentiment_confidence = EXCLUDED.sentiment_confidence,
                    sentiment_reason = EXCLUDED.sentiment_reason
                """,
                rows,
            )

    print(f"Saved {len(rows)} rows to Neon table '{TABLE_NAME}'.")


def save_with_fallback(df: pd.DataFrame, fallback_csv_path: str) -> None:
    """Prefer Neon Postgres and fall back to CSV if DB is unavailable."""
    database_url = _get_database_url()
    if database_url:
        try:
            save_to_neon(df)
            return
        except Exception as exc:
            print(f"Neon save failed, falling back to CSV: {exc}")

    save_to_csv(df, fallback_csv_path)
