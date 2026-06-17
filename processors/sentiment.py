"""Sentiment analysis helpers using Gemini."""

from __future__ import annotations

import json
import os
import time
from typing import Any

import pandas as pd
import requests

from config import GEMINI_API_KEYS, GEMINI_MODEL


SYSTEM_PROMPT = (
    "Kamu adalah analis media Indonesia. Klasifikasikan sentimen "
    "berita berikut. Jawab HANYA dengan JSON format: "
    "{sentiment: positif|negatif|netral, confidence: 0.0-1.0, reason: string max 10 kata}"
)
MODEL = GEMINI_MODEL
GEMINI_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
)
BATCH_SIZE = 10
GEMINI_KEYS_ENV = "GEMINI_API_KEYS"


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
    """Extract text content from Gemini response objects."""
    try:
        candidates = response.get("candidates", [])
        if not candidates:
            return ""
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        texts: list[str] = []
        for part in parts:
            text = part.get("text")
            if text:
                texts.append(str(text))
        return "".join(texts)
    except Exception:
        pass
    return ""


def _load_gemini_keys() -> list[str]:
    """Load one or more Gemini API keys from env/config."""
    raw_keys = os.getenv(GEMINI_KEYS_ENV, GEMINI_API_KEYS)
    keys: list[str] = []

    if raw_keys:
        keys.extend([key.strip() for key in raw_keys.split(",") if key.strip()])

    return keys


def analyze_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Add sentiment columns to a DataFrame using the Gemini API."""
    result = df.copy()
    result["sentiment"] = "unknown"
    result["sentiment_confidence"] = 0.0
    result["sentiment_reason"] = ""

    api_keys = _load_gemini_keys()
    if not api_keys or result.empty:
        return result

    total_batches = (len(result) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Starting sentiment analysis for {len(result)} rows across {total_batches} batches.", flush=True)

    for start in range(0, len(result), BATCH_SIZE):
        batch = result.iloc[start : start + BATCH_SIZE]
        batch_no = start // BATCH_SIZE + 1
        print(
            f"Analyzing sentiment batch {batch_no}/{total_batches} "
            f"({start + 1}-{min(start + BATCH_SIZE, len(result))}/{len(result)})",
            flush=True,
        )

        for idx, row in batch.iterrows():
            user_prompt = f"Judul: {row.get('title', '')}\nDeskripsi: {row.get('description', '')}"
            row_done = False
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
                            }
                        ],
                    }
                ],
                "generationConfig": {
                    "temperature": 0,
                    "responseMimeType": "application/json",
                },
            }

            for api_key in api_keys:
                try:
                    response = requests.post(
                        GEMINI_ENDPOINT,
                        params={"key": api_key},
                        json=payload,
                        timeout=60,
                    )
                    if response.status_code == 429:
                        print(f"Gemini rate limit hit for row {idx}. Trying next key.", flush=True)
                        continue

                    response.raise_for_status()
                    content = _extract_message_content(response.json())
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
                    row_done = True
                    break
                except requests.exceptions.ConnectionError:
                    time.sleep(1)
                    continue
                except Exception:
                    continue

            if not row_done:
                result.at[idx, "sentiment"] = "unknown"
                result.at[idx, "sentiment_confidence"] = 0.0
                result.at[idx, "sentiment_reason"] = ""

        if start + BATCH_SIZE < len(result):
            time.sleep(1)

    print("Sentiment analysis finished.", flush=True)
    return result


def enrich_sentiment(text: str) -> str:
    """Backward-compatible wrapper for older callers."""
    frame = pd.DataFrame([{"title": text, "description": ""}])
    analyzed = analyze_sentiment(frame)
    return str(analyzed.loc[0, "sentiment"])
