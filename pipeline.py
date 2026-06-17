"""Main orchestration for the media_pulse pipeline."""

from __future__ import annotations

import argparse
from collections import Counter

from config import OUTPUT_CSV
from collectors.newsdata_client import NewsDataClient
from processors.cleaner import clean_articles
from processors.sentiment import analyze_sentiment
from storage.neon_handler import save_with_fallback


def main() -> None:
    """Run the media_pulse ingestion pipeline."""
    parser = argparse.ArgumentParser(description="Run the media_pulse pipeline")
    parser.add_argument(
        "--skip-sentiment",
        action="store_true",
        help="Skip Gemini sentiment analysis for faster testing",
    )
    args = parser.parse_args()

    client = NewsDataClient()
    print("Fetching latest articles...", flush=True)
    raw_articles = client.fetch_all_categories()
    fetched_count = len(raw_articles)

    print(f"Fetched {fetched_count} rows. Cleaning articles...", flush=True)
    cleaned_df = clean_articles(raw_articles)

    if args.skip_sentiment:
        print("Skipping sentiment analysis by request.", flush=True)
        final_df = cleaned_df.copy()
        if "sentiment" not in final_df.columns:
            final_df["sentiment"] = "unknown"
        if "sentiment_confidence" not in final_df.columns:
            final_df["sentiment_confidence"] = 0.0
        if "sentiment_reason" not in final_df.columns:
            final_df["sentiment_reason"] = ""
    else:
        print("Running sentiment analysis...", flush=True)
        final_df = analyze_sentiment(cleaned_df)

    print("Saving results...", flush=True)
    save_with_fallback(final_df, OUTPUT_CSV)

    if "sentiment" in final_df.columns and not final_df.empty:
        sentiment_distribution = dict(Counter(final_df["sentiment"].fillna("unknown")))
    else:
        sentiment_distribution = {}

    print(f"Total fetched: {fetched_count}")
    print(f"Total saved: {len(final_df)}")
    print(f"Sentiment distribution: {sentiment_distribution}")
    print("Pipeline finished.", flush=True)


def run() -> None:
    """Backward-compatible alias for older callers."""
    main()


if __name__ == "__main__":
    main()
