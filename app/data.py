from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from collections import Counter, defaultdict
from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

try:
    import psycopg
except Exception:  # pragma: no cover - optional at runtime
    psycopg = None  # type: ignore[assignment]
CSV_PATH = ROOT_DIR / "data" / "news.csv"
DASHBOARD_CACHE_TTL_SECONDS = 300

Nav = Literal["overview", "sentiment", "category", "source", "news"]
CANONICAL_COLUMNS = [
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
    "sentiment_status",
    "sentiment_attempts",
    "sentiment_processed_at",
    "sentiment_last_error",
]

CATEGORY_LABELS = {
    "politics": ("Politik", "Politics"),
    "business": ("Bisnis", "Business"),
    "technology": ("Teknologi", "Technology"),
    "health": ("Kesehatan", "Health"),
    "world": ("Dunia", "World"),
    "entertainment": ("Hiburan", "Entertainment"),
    "sports": ("Olahraga", "Sports"),
    "domestic": ("Domestik", "Domestic"),
    "education": ("Pendidikan", "Education"),
    "crime": ("Kriminal", "Crime"),
    "environment": ("Lingkungan", "Environment"),
    "science": ("Sains", "Science"),
    "food": ("Kuliner", "Food"),
    "lifestyle": ("Gaya Hidup", "Lifestyle"),
    "tourism": ("Pariwisata", "Tourism"),
    "other": ("Lainnya", "Other"),
}

STOPWORDS = {
    "dan",
    "yang",
    "di",
    "ke",
    "dari",
    "untuk",
    "pada",
    "dengan",
    "atau",
    "the",
    "and",
    "to",
    "of",
    "in",
    "for",
    "on",
    "is",
    "a",
    "an",
    "rt",
    "ini",
    "itu",
    "para",
    "akan",
    "dalam",
    "jadi",
    "agar",
    "lebih",
    "telah",
    "sebagai",
}


def esc(value: object) -> str:
    import html

    return html.escape("" if value is None else str(value))


def t(lang: str, id_text: str, en_text: str) -> str:
    return id_text if lang == "id" else en_text


def extract_domain(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    match = re.search(r"^[a-z]+://([^/]+)/?", value.strip(), flags=re.I)
    if match:
        return match.group(1).lower()
    if "." in value:
        return value.strip().lower().split("/")[0]
    return ""


def choose_date_col(df: pd.DataFrame) -> str:
    for candidate in ("published_at_wib", "published_at", "fetched_at"):
        if candidate in df.columns and not df[candidate].isna().all():
            return candidate
    return "fetched_at"


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)

    df = df.copy()
    rename_map = {}
    if "pubDate" in df.columns and "published_at" not in df.columns:
        rename_map["pubDate"] = "published_at"
    if "pub_date_wib" in df.columns and "published_at_wib" not in df.columns:
        rename_map["pub_date_wib"] = "published_at_wib"
    if rename_map:
        df = df.rename(columns=rename_map)

    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    if "article_id" not in df.columns or df["article_id"].isna().all():
        df["article_id"] = [
            f"row-{i}-{abs(hash((str(row.get('title', '')), str(row.get('source_url', ''))))) % 10**10}"
            for i, row in df.iterrows()
        ]

    text_cols = [
        "title",
        "description",
        "source_id",
        "source_url",
        "country",
        "category",
        "language",
        "domain",
        "sentiment",
        "sentiment_reason",
        "sentiment_status",
        "sentiment_last_error",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str)

    df["country"] = df["country"].replace("", "id")
    df["category"] = df["category"].replace("", "other").str.lower()
    df["language"] = df["language"].replace("", "id")
    df["sentiment"] = df["sentiment"].replace("", "unknown").str.lower()
    df["sentiment_status"] = df["sentiment_status"].replace("", "pending").str.lower()
    df["sentiment_reason"] = df["sentiment_reason"].fillna("")
    df["sentiment_last_error"] = df["sentiment_last_error"].fillna("")

    if "source_id" in df.columns:
        df["source_id"] = df["source_id"].replace("", pd.NA)
    if "source_url" in df.columns:
        df["source_url"] = df["source_url"].replace("", pd.NA)

    if "domain" in df.columns:
        df["domain"] = df["domain"].fillna("").astype(str)
    else:
        df["domain"] = ""
    domain_from_url = df["source_url"].fillna("").map(extract_domain)
    df["domain"] = df["domain"].where(df["domain"].astype(str).str.strip() != "", domain_from_url)
    df["source_id"] = df["source_id"].fillna(df["domain"]).replace("", "unknown")

    for col in ("published_at", "fetched_at", "published_at_wib", "sentiment_processed_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    if df["published_at"].isna().all() and "published_at_wib" in df.columns:
        df["published_at"] = df["published_at_wib"]
    if df["published_at_wib"].isna().all() and "published_at" in df.columns:
        df["published_at_wib"] = df["published_at"].dt.tz_convert("Asia/Jakarta")

    if df["fetched_at"].isna().all():
        df["fetched_at"] = pd.Timestamp.now(tz="UTC")

    df["sentiment_confidence"] = pd.to_numeric(df.get("sentiment_confidence", 0.0), errors="coerce").fillna(0.0).clip(0.0, 1.0)
    df["sentiment_attempts"] = pd.to_numeric(df.get("sentiment_attempts", 0), errors="coerce").fillna(0).astype(int)
    return df.reset_index(drop=True)


def load_neon_articles() -> tuple[pd.DataFrame, str]:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url or psycopg is None:
        return pd.DataFrame(), "Neon/Postgres unavailable"

    query = """
        SELECT
            article_id,
            title,
            description,
            source_id,
            source_url,
            country,
            category,
            language,
            published_at,
            fetched_at,
            published_at_wib,
            domain,
            sentiment,
            sentiment_confidence,
            sentiment_reason,
            sentiment_status,
            sentiment_attempts,
            sentiment_processed_at,
            sentiment_last_error
        FROM news_articles
        ORDER BY COALESCE(published_at_wib, published_at, fetched_at) DESC NULLS LAST, article_id DESC
    """

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description or []]

    if not rows:
        return pd.DataFrame(columns=CANONICAL_COLUMNS), "Neon/Postgres empty"
    return normalize_dataframe(pd.DataFrame.from_records(rows, columns=columns)), "Neon/Postgres"


def load_csv_articles() -> tuple[pd.DataFrame, str]:
    if not CSV_PATH.exists():
        return pd.DataFrame(columns=CANONICAL_COLUMNS), "data/news.csv missing"
    return normalize_dataframe(pd.read_csv(CSV_PATH)), "data/news.csv"


def load_dashboard_data() -> tuple[pd.DataFrame, str, str]:
    neon_df, neon_note = load_neon_articles()
    if not neon_df.empty:
        return neon_df, "Neon/Postgres", neon_note
    csv_df, csv_note = load_csv_articles()
    if not csv_df.empty:
        return csv_df, "CSV", csv_note
    return pd.DataFrame(columns=CANONICAL_COLUMNS), "Demo", f"{neon_note}; {csv_note}"


@st.cache_data(ttl=DASHBOARD_CACHE_TTL_SECONDS, show_spinner=False)
def load_dashboard_snapshot() -> tuple[pd.DataFrame, str, str, str]:
    """Load the dashboard data once and cache it briefly for Streamlit reruns."""
    df, source_name, source_note = load_dashboard_data()
    refresh_at = datetime.now(timezone.utc).isoformat()
    return df, source_name, source_note, refresh_at


def clear_dashboard_snapshot_cache() -> None:
    """Clear the cached dashboard snapshot so the next rerun hits Neon again."""
    load_dashboard_snapshot.clear()


def category_label(value: object, lang: str) -> str:
    key = str(value or "").strip().lower()
    if not key:
        return t(lang, "Lainnya", "Other")
    if key in CATEGORY_LABELS:
        return CATEGORY_LABELS[key][0 if lang == "id" else 1]
    return key.replace("_", " ").title()


def build_word_cloud_rows(df: pd.DataFrame) -> list[dict[str, object]]:
    tokens = Counter()
    sentiment_votes: dict[str, Counter[str]] = defaultdict(Counter)
    for _, row in df.iterrows():
        text = f"{row.get('title', '')} {row.get('description', '')}"
        words = re.findall(r"[A-Za-zÀ-ÿ0-9]{3,}", str(text).lower())
        sentiment = str(row.get("sentiment", "unknown")).lower() or "unknown"
        for word in words:
            if word in STOPWORDS or word.isdigit():
                continue
            tokens[word] += 1
            sentiment_votes[word][sentiment] += 1

    rows = []
    for word, count in tokens.most_common(24):
        dominant = sentiment_votes[word].most_common(1)[0][0] if sentiment_votes[word] else "neutral"
        rows.append({"w": word, "sz": min(32, 8 + count * 2), "s": dominant if dominant in {"positive", "negative", "neutral"} else "neutral"})
    return rows or [{"w": "kabar", "sz": 22, "s": "neutral"}]


def filter_articles(
    df: pd.DataFrame,
    dr: str,
    sentiment_filter: str,
    search: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return df, df

    chart_df = df.copy()
    date_col = choose_date_col(chart_df)
    chart_df[date_col] = pd.to_datetime(chart_df[date_col], errors="coerce", utc=True)
    now = pd.Timestamp.now(tz="UTC")
    days = {"7d": 7, "14d": 14, "30d": 30, "90d": 90}.get(dr, 14)
    cutoff = now - pd.Timedelta(days=days)
    chart_df = chart_df[chart_df[date_col].isna() | (chart_df[date_col] >= cutoff)]
    if sentiment_filter != "all":
        chart_df = chart_df[chart_df["sentiment"].str.lower() == sentiment_filter]

    table_df = chart_df.copy()
    if search:
        q = search.lower().strip()
        haystack = (
            table_df["title"].fillna("").astype(str)
            + " "
            + table_df["description"].fillna("").astype(str)
            + " "
            + table_df["category"].fillna("").astype(str)
            + " "
            + table_df["source_id"].fillna("").astype(str)
        ).str.lower()
        table_df = table_df[haystack.str.contains(q, na=False)]

    return chart_df.reset_index(drop=True), table_df.reset_index(drop=True)


def build_stats(df: pd.DataFrame, lang: str) -> dict[str, object]:
    total = len(df)
    sentiment_counts = (
        df["sentiment"].fillna("unknown").str.lower().value_counts().reindex(["positive", "negative", "neutral", "unknown"], fill_value=0).to_dict()
    )
    avg_conf = float(df["sentiment_confidence"].mean() or 0.0) if total else 0.0

    category_df = (
        df.assign(_cat=df["category"].fillna("other").str.lower())
        .groupby("_cat", dropna=False)
        .agg(n=("article_id", "count"), p=("sentiment", lambda s: int((s.str.lower() == "positive").sum())), ne=("sentiment", lambda s: int((s.str.lower() == "negative").sum())), nu=("sentiment", lambda s: int((s.str.lower() == "neutral").sum())))
        .reset_index()
        .sort_values("n", ascending=False)
    )
    categories = [
        {
            "id": category_label(row["_cat"], "id"),
            "en": category_label(row["_cat"], "en"),
            "n": int(row["n"]),
            "p": int(row["p"]),
            "ne": int(row["ne"]),
            "nu": int(row["nu"]),
        }
        for _, row in category_df.iterrows()
    ] or [{"id": t(lang, "Lainnya", "Other"), "en": "Other", "n": 0, "p": 0, "ne": 0, "nu": 0}]

    source_series = df.assign(_source=df["source_id"].fillna("").replace("", pd.NA).fillna(df["domain"].fillna("unknown")).fillna("unknown"))
    source_df = (
        source_series.groupby("_source", dropna=False)
        .agg(n=("article_id", "count"), p=("sentiment", lambda s: int((s.str.lower() == "positive").sum())), ne=("sentiment", lambda s: int((s.str.lower() == "negative").sum())), nu=("sentiment", lambda s: int((s.str.lower() == "neutral").sum())))
        .reset_index()
        .sort_values("n", ascending=False)
    )
    sources = [
        {
            "name": str(row["_source"] or "unknown"),
            "n": int(row["n"]),
            "p": int(row["p"]),
            "ne": int(row["ne"]),
            "nu": int(row["nu"]),
            "pp": int(round((row["p"] / row["n"]) * 100)) if row["n"] else 0,
        }
        for _, row in source_df.iterrows()
    ] or [{"name": "unknown", "n": 0, "p": 0, "ne": 0, "nu": 0, "pp": 0}]

    date_col = choose_date_col(df)
    ts = df.copy()
    ts[date_col] = pd.to_datetime(ts[date_col], errors="coerce", utc=True)
    ts = ts.dropna(subset=[date_col])
    if ts.empty:
        time_series = []
    else:
        ts["_day"] = ts[date_col].dt.tz_convert("Asia/Jakarta").dt.floor("D")
        grouped = (
            ts.groupby("_day")
            .agg(total=("article_id", "count"), p=("sentiment", lambda s: int((s.str.lower() == "positive").sum())), n=("sentiment", lambda s: int((s.str.lower() == "negative").sum())))
            .reset_index()
            .sort_values("_day")
        )
        time_series = [{"d": row["_day"].strftime("%d/%-m"), "t": int(row["total"]), "p": int(row["p"]), "n": int(row["n"])} for _, row in grouped.iterrows()]

    return {
        "total": total,
        "sentiment_counts": sentiment_counts,
        "avg_conf": avg_conf,
        "categories": categories,
        "sources": sources,
        "time_series": time_series,
        "word_cloud": build_word_cloud_rows(df),
    }
