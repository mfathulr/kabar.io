"""Cleaning helpers for NewsData articles."""

from __future__ import annotations

from urllib.parse import urlparse

import pandas as pd


def clean_articles(raw_list) -> pd.DataFrame:
    """Clean and normalize a list of article dictionaries."""
    df = pd.DataFrame(list(raw_list))
    if df.empty:
        return df

    keep_columns = [
        "article_id",
        "title",
        "description",
        "source_id",
        "source_url",
        "country",
        "category",
        "language",
        "pubDate",
        "fetched_at",
    ]
    df = df.reindex(columns=keep_columns)

    df = df.dropna(subset=["title"])

    if "article_id" in df.columns:
        df = df.drop_duplicates(subset=["article_id"], keep="first")

    df["pubDate"] = pd.to_datetime(df["pubDate"], errors="coerce", utc=True)
    df["pub_date_wib"] = df["pubDate"].dt.tz_convert("Asia/Jakarta")

    def _extract_domain(value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            return ""
        parsed = urlparse(value)
        return parsed.netloc or ""

    df["domain"] = df["source_url"].map(_extract_domain)
    return df.reset_index(drop=True)


def normalize_articles(raw_list) -> pd.DataFrame:
    """Backward-compatible alias for older callers."""
    return clean_articles(raw_list)
