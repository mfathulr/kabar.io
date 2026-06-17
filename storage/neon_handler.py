"""Neon Postgres storage helpers with pooled connections."""

from __future__ import annotations

import os
from typing import Any

import pandas as pd

try:
    from psycopg_pool import ConnectionPool as _ConnectionPool
    HAS_CONNECTION_POOL = True
except Exception:  # pragma: no cover - optional dependency for Neon usage
    _ConnectionPool = Any  # type: ignore[assignment]
    HAS_CONNECTION_POOL = False

from storage.csv_handler import save_to_csv

TABLE_NAME = "news_articles"
DB_COLUMNS = [
    "article_id",
    "title",
    "description",
    "source_id",
    "source_url",
    "country",
    "category",
    "language",
    "published_at",
    "fetched_at",
    "published_at_wib",
    "domain",
    "sentiment",
    "sentiment_confidence",
    "sentiment_reason",
]
POOL_MIN_SIZE = 1
POOL_MAX_SIZE = 5
_POOL: Any = None


def _get_database_url() -> str:
    """Return the Neon/Postgres URL from env."""
    return os.getenv("DATABASE_URL", "").strip()


def _get_pool() -> Any:
    """Create a pooled Postgres client on demand."""
    global _POOL

    if _POOL is not None:
        return _POOL

    if not HAS_CONNECTION_POOL:
        raise RuntimeError("psycopg-pool is not installed")

    database_url = _get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL is not configured")

    _POOL = _ConnectionPool(
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
    payload = {
        "article_id": _normalize_value(row.get("article_id")),
        "title": _normalize_value(row.get("title")),
        "description": _normalize_value(row.get("description")),
        "source_id": _normalize_value(row.get("source_id")),
        "source_url": _normalize_value(row.get("source_url")),
        "country": _normalize_value(row.get("country")),
        "category": _normalize_value(row.get("category")),
        "language": _normalize_value(row.get("language")),
        "published_at": _normalize_value(row.get("pubDate")),
        "fetched_at": _normalize_value(row.get("fetched_at")),
        "published_at_wib": _normalize_value(row.get("pub_date_wib")),
        "domain": _normalize_value(row.get("domain")),
        "sentiment": _normalize_value(row.get("sentiment")),
        "sentiment_confidence": _normalize_value(row.get("sentiment_confidence")),
        "sentiment_reason": _normalize_value(row.get("sentiment_reason")),
    }
    return payload


def _ensure_table(conn) -> None:
    """Create the target table if it does not exist."""
    statements = [
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            article_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            source_id TEXT,
            source_url TEXT,
            country TEXT NOT NULL DEFAULT 'id',
            category TEXT NOT NULL,
            language TEXT,
            published_at TIMESTAMPTZ,
            fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            published_at_wib TIMESTAMPTZ,
            domain TEXT,
            sentiment TEXT NOT NULL DEFAULT 'unknown',
            sentiment_confidence DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (sentiment_confidence >= 0 AND sentiment_confidence <= 1),
            sentiment_reason TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_news_articles_category_published_at
            ON {TABLE_NAME} (category, published_at DESC)
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_news_articles_fetched_at
            ON {TABLE_NAME} (fetched_at DESC)
        """,
        f"""
        CREATE INDEX IF NOT EXISTS idx_news_articles_source_id
            ON {TABLE_NAME} (source_id)
        """,
        """
        CREATE OR REPLACE FUNCTION set_news_articles_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """,
        f"""
        DROP TRIGGER IF EXISTS trg_news_articles_updated_at ON {TABLE_NAME}
        """,
        f"""
        CREATE TRIGGER trg_news_articles_updated_at
        BEFORE UPDATE ON {TABLE_NAME}
        FOR EACH ROW
        EXECUTE FUNCTION set_news_articles_updated_at()
        """,
    ]

    for statement in statements:
        conn.execute(statement)


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
                    {", ".join(DB_COLUMNS)}
                ) VALUES (
                    %(article_id)s,
                    %(title)s,
                    %(description)s,
                    %(source_id)s,
                    %(source_url)s,
                    %(country)s,
                    %(category)s,
                    %(language)s,
                    %(published_at)s,
                    %(fetched_at)s,
                    %(published_at_wib)s,
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
                    published_at = EXCLUDED.published_at,
                    fetched_at = EXCLUDED.fetched_at,
                    published_at_wib = EXCLUDED.published_at_wib,
                    domain = EXCLUDED.domain,
                    sentiment = EXCLUDED.sentiment,
                    sentiment_confidence = EXCLUDED.sentiment_confidence,
                    sentiment_reason = EXCLUDED.sentiment_reason,
                    updated_at = NOW()
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
