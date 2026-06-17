"""Sentiment analysis helpers using OpenAI."""

from __future__ import annotations

import json
import os
import time
from typing import Any

import pandas as pd
from openai import OpenAI


SYSTEM_PROMPT = (
    "Kamu adalah analis media Indonesia. Klasifikasikan sentimen "
    "berita berikut. Jawab HANYA dengan JSON format: "
    '{sentiment: positif|negatif|netral, confidence: 0.0-1.0, reason: string max 10 kata}'
)
MODEL = "gpt-4o-mini"
BATCH_SIZE = 10


def _safe_parse_json(content: str) -> dict[str, Any]:
    """Parse JSON response from the model as safely as possible."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def _extract_message_content(response: Any) -> str:
    """Extract text content from OpenAI chat response objects."""
    try:
        choice = response.choices[0]
        message = choice.message
        content = getattr(message, "content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                text = getattr(item, "text", None)
                if text:
                    parts.append(text)
            return "".join(parts)
    except Exception:
        pass
    return ""


def analyze_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Add sentiment columns to a DataFrame using the OpenAI API."""
    result = df.copy()
    result["sentiment"] = "unknown"
    result["sentiment_confidence"] = 0.0
    result["sentiment_reason"] = ""

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or result.empty:
        return result

    client = OpenAI(api_key=api_key)

    for start in range(0, len(result), BATCH_SIZE):
        batch = result.iloc[start : start + BATCH_SIZE]

        for idx, row in batch.iterrows():
            user_prompt = f"Judul: {row.get('title', '')}\nDeskripsi: {row.get('description', '')}"
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0,
                )
                content = _extract_message_content(response)
                parsed = _safe_parse_json(content)

                sentiment = str(parsed.get("sentiment", "unknown")).strip().lower()
                if sentiment not in {"positif", "negatif", "netral"}:
                    sentiment = "unknown"

                confidence_raw = parsed.get("confidence", 0.0)
                try:
                    confidence = float(confidence_raw)
                except (TypeError, ValueError):
                    confidence = 0.0
                confidence = max(0.0, min(1.0, confidence))

                reason = str(parsed.get("reason", "")).strip()
                reason = " ".join(reason.split()[:10])
                result.at[idx, "sentiment"] = sentiment
                result.at[idx, "sentiment_confidence"] = confidence
                result.at[idx, "sentiment_reason"] = reason
            except Exception:
                result.at[idx, "sentiment"] = "unknown"
                result.at[idx, "sentiment_confidence"] = 0.0
                result.at[idx, "sentiment_reason"] = ""

        if start + BATCH_SIZE < len(result):
            time.sleep(1)

    return result


def enrich_sentiment(text: str) -> str:
    """Backward-compatible wrapper for older callers."""
    frame = pd.DataFrame([{"title": text, "description": ""}])
    analyzed = analyze_sentiment(frame)
    return str(analyzed.loc[0, "sentiment"])
