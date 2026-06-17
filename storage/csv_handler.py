"""CSV storage helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


EXPECTED_COLUMNS = [
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
    "pub_date_wib",
    "domain",
    "sentiment",
    "sentiment_confidence",
    "sentiment_reason",
]


def load_existing(filepath: str) -> pd.DataFrame:
    """Load an existing CSV file or return an empty frame with expected columns."""
    path = Path(filepath)
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=EXPECTED_COLUMNS)


def save_to_csv(df: pd.DataFrame, filepath: str) -> None:
    """Append data to CSV, deduplicate by article_id, and save back in place."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing = load_existing(filepath)
    before_rows = len(existing)

    if existing.empty:
        combined = df.copy()
    else:
        combined = pd.concat([existing, df], ignore_index=True)

    if "article_id" in combined.columns:
        combined = combined.drop_duplicates(subset=["article_id"], keep="first")

    added_rows = len(combined) - before_rows
    combined.to_csv(path, index=False)
    print(f"Added {max(added_rows, 0)} new rows.")


def append_csv(df: pd.DataFrame, output_path: str) -> None:
    """Backward-compatible alias for older callers."""
    save_to_csv(df, output_path)
