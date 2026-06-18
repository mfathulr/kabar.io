"""Incremental sentiment worker for pending news articles."""

from __future__ import annotations

import argparse

from processors.sentiment import classify_sentiment
from storage.neon_handler import claim_sentiment_batch, update_sentiment_result, reset_processing_to_pending

DEFAULT_BATCH_SIZE = 5


def main() -> None:
    """Process a small batch of pending articles by publication time."""
    parser = argparse.ArgumentParser(description="Run the sentiment worker")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Number of pending articles to process per run",
    )
    parser.add_argument(
        "--reset-processing",
        action="store_true",
        help="Reset stale processing rows back to pending before claiming work",
    )
    args = parser.parse_args()

    if args.reset_processing:
        print("Resetting stale processing rows...", flush=True)
        reset_processing_to_pending()

    print(f"Claiming up to {args.batch_size} pending articles...", flush=True)
    batch = claim_sentiment_batch(args.batch_size)
    if batch.empty:
        print("No pending articles found.", flush=True)
        return

    print(f"Claimed {len(batch)} articles for sentiment processing.", flush=True)

    for _, row in batch.iterrows():
        article_id = str(row.get("article_id", ""))
        title = str(row.get("title", ""))
        description = str(row.get("description", ""))

        print(f"Processing {article_id}...", flush=True)
        sentiment, confidence, reason, ok, error = classify_sentiment(title, description)

        if ok:
            update_sentiment_result(
                article_id=article_id,
                sentiment=sentiment,
                confidence=confidence,
                reason=reason,
                status="done",
                last_error="",
            )
            print(f"Updated {article_id} as done.", flush=True)
            continue

        update_sentiment_result(
            article_id=article_id,
            sentiment="unknown",
            confidence=0.0,
            reason="",
            status="pending",
            last_error=error,
        )
        print(f"Kept {article_id} pending due to: {error}", flush=True)

    print("Sentiment worker finished.", flush=True)


if __name__ == "__main__":
    main()
