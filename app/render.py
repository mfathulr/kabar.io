from __future__ import annotations

import math

import pandas as pd
import streamlit as st
from textwrap import dedent

try:
    from .charts import mk_category_chart, mk_donut, mk_source_chart, mk_timeseries
    from .data import category_label, esc, t
except ImportError:  # pragma: no cover - script-style fallback
    from charts import mk_category_chart, mk_donut, mk_source_chart, mk_timeseries
    from data import category_label, esc, t


def nav_titles(nav: str, lang: str) -> tuple[str, str]:
    titles = {
        "analysis": (t(lang, "Analisis", "Analysis"), t(lang, "Ringkasan, sentimen, kategori, dan sumber dalam satu alur", "Summary, sentiment, category, and source in one flow")),
        "news": (t(lang, "Feed Berita", "News Feed"), t(lang, "Jelajahi artikel yang diproses pipeline", "Browse articles processed by the pipeline")),
    }
    return titles[nav]


def dr_map(lang: str, dr: str) -> str:
    return {"7d": t(lang, "7 Hari", "7-Day"), "14d": t(lang, "14 Hari", "14-Day"), "30d": t(lang, "30 Hari", "30-Day"), "90d": t(lang, "90 Hari", "90-Day")}[dr]


def page_css() -> str:
    try:
        from .styles import BASE_CSS
    except ImportError:  # pragma: no cover - script-style fallback
        from styles import BASE_CSS

    return BASE_CSS


def topbar(nav: str, lang: str) -> None:
    title, _subtitle = nav_titles(nav, lang)
    st.markdown(
        dedent(
            f"""
        <div class="topbar">
          <div class="topbar-inner">
            <div class="topbar-copy">
              <h1 class="page-title">{esc(title)}</h1>
            </div>
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )


def metric_card(title: str, value: str, note: str, accent: str = "muted") -> str:
    color_class = f"metric-{accent}" if accent in {"positive", "negative"} else "muted"
    return (
        f'<div class="panel compact">'
        f'<div class="kpi-label {color_class}">{esc(title)}</div>'
        f'<div class="kpi-value {color_class}">{esc(value)}</div>'
        f'<div class="kpi-note">{esc(note)}</div>'
        f'</div>'
    )


def analysis_section(title: str, subtitle: str) -> str:
    return (
        f'<div class="analysis-section">'
        f'<div class="analysis-section-title">{esc(title)}</div>'
        f'<div class="analysis-section-subtitle">{esc(subtitle)}</div>'
        f'</div>'
    )


def render_overview(stats: dict[str, object], lang: str, dr: str) -> None:
    total = int(stats["total"])
    pos = int(stats["sentiment_counts"].get("positive", 0))
    neg = int(stats["sentiment_counts"].get("negative", 0))
    neu = int(stats["sentiment_counts"].get("neutral", 0))
    pos_pct = round((pos / total) * 100) if total else 0
    neg_pct = round((neg / total) * 100) if total else 0
    avg_conf = float(stats["avg_conf"])

    st.markdown(
        dedent(
            f"""
        <div class="section-pad" id="overview">
          <div class="grid-4">
            {metric_card(t(lang, "Total Artikel", "Total Articles"), f"{total:,}".replace(",", "."), t(lang, "14 hari terakhir", "Last 14 days"))}
            {metric_card(t(lang, "Sentimen Positif", "Positive Sentiment"), f"{pos_pct}%", t(lang, "Porsi artikel positif", "Share of positive articles"), "positive")}
            {metric_card(t(lang, "Sentimen Negatif", "Negative Sentiment"), f"{neg_pct}%", t(lang, "Porsi artikel negatif", "Share of negative articles"), "negative")}
            {metric_card("Avg. Confidence", f"{round(avg_conf * 100)}%", t(lang, "Gemini AI score", "Gemini AI score"))}
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        dedent(
            f"""
        <div class="section-pad section-tight">
          {analysis_section(t(lang, "Apa yang Terjadi", "What is Happening"), t(lang, "Sentimen menunjukkan arah umum percakapan hari ini", "Sentiment shows the overall direction of today's conversation"))}
          <div class="grid-2-1">
            <div class="panel">
              <div class="card-title">{esc(t(lang, "Distribusi Sentimen", "Sentiment Distribution"))}</div>
              <div style="height:175px">{mk_donut(stats["sentiment_counts"], total)}</div>
              <div class="subtle-rule">
                <div class="bar-caption"><span class="legend-item"><span class="legend-swatch" style="background:#2d7a3a"></span>{esc(t(lang, "Positif", "Positive"))}</span><strong>{pos:,} ({pos_pct}%)</strong></div>
                <div class="bar-caption"><span class="legend-item"><span class="legend-swatch" style="background:#cc2200"></span>{esc(t(lang, "Negatif", "Negative"))}</span><strong>{neg:,} ({neg_pct}%)</strong></div>
                <div class="bar-caption"><span class="legend-item"><span class="legend-swatch" style="background:#b09580"></span>{esc(t(lang, "Netral", "Neutral"))}</span><strong>{neu:,} ({round((neu / total) * 100) if total else 0}%)</strong></div>
              </div>
            </div>
            <div class="panel">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
                <div class="card-title" style="margin-bottom:0">{esc(t(lang, f"Tren Sentimen {dr_map(lang, dr)}", f"{dr_map(lang, dr)} Sentiment Trend"))}</div>
                <div style="display:flex;align-items:center;gap:14px">
                  <div class="legend-item"><span class="legend-swatch" style="width:18px;height:2px;background:#2d7a3a;border-radius:1px"></span>{esc(t(lang, "Positif", "Positive"))}</div>
                  <div class="legend-item"><span class="legend-swatch" style="width:18px;height:2px;background:#cc2200;border-radius:1px"></span>{esc(t(lang, "Negatif", "Negative"))}</div>
                  <div class="legend-item"><span class="legend-swatch" style="width:18px;height:1px;background:#786f62;border-radius:1px;opacity:0.4"></span>Total</div>
                </div>
              </div>
              <div style="height:230px">{mk_timeseries(stats["time_series"])}</div>
            </div>
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        dedent(
            f"""
        <div class="section-pad section-tight">
          {analysis_section(t(lang, "Apa yang Dibicarakan", "What People Talk About"), t(lang, "Kata kunci dan kategori menjelaskan tema utama di balik sentimen", "Keywords and categories explain the main themes behind the sentiment"))}
          <div class="grid-2">
            <div class="panel">
              <div class="card-title" style="margin-bottom:2px">{esc(t(lang, "Kata Kunci Dominan", "Dominant Keywords"))}</div>
              <div class="card-subtitle">{esc(t(lang, "Ukuran = frekuensi · warna = sentimen dominan", "Size = frequency · color = dominant sentiment"))}</div>
              <div style="min-height:130px">{mk_word_cloud(stats["word_cloud"])}</div>
              <div class="subtle-rule">
                <div class="legend-row">
                  <div class="legend-item"><span class="legend-swatch" style="background:#2d7a3a;border-radius:50%"></span>{esc(t(lang, "Positif", "Positive"))}</div>
                  <div class="legend-item"><span class="legend-swatch" style="background:#cc2200;border-radius:50%"></span>{esc(t(lang, "Negatif", "Negative"))}</div>
                  <div class="legend-item"><span class="legend-swatch" style="background:#b09580;border-radius:50%"></span>{esc(t(lang, "Netral", "Neutral"))}</div>
                </div>
              </div>
            </div>
            <div class="panel">
              <div class="card-title">{esc(t(lang, "Distribusi per Kategori", "Distribution by Category"))}</div>
              <div class="card-subtitle">{esc(t(lang, "Komposisi kategori yang paling banyak muncul", "Category composition by volume"))}</div>
              <div style="height:255px">{mk_category_chart(stats["categories"], lang)}</div>
              <div class="subtle-rule">
                <div class="legend-row">
                  <div class="legend-item"><span class="legend-swatch" style="width:14px;height:7px;background:#2d7a3a;border-radius:1px"></span>{esc(t(lang, "Positif", "Positive"))}</div>
                  <div class="legend-item"><span class="legend-swatch" style="width:14px;height:7px;background:#cc2200;border-radius:1px"></span>{esc(t(lang, "Negatif", "Negative"))}</div>
                  <div class="legend-item"><span class="legend-swatch" style="width:14px;height:7px;background:#b09580;border-radius:1px"></span>{esc(t(lang, "Netral", "Neutral"))}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        dedent(
            f"""
        <div class="section-pad section-tight">
          {analysis_section(t(lang, "Siapa yang Membentuk Narasi", "Who Shapes the Narrative"), t(lang, "Sumber menjelaskan media mana yang paling banyak berkontribusi ke percakapan", "Sources show which media contribute most to the conversation"))}
          <div class="panel" style="margin-bottom:10px">
            <div class="card-title" style="margin-bottom:2px">{esc(t(lang, "Top Sumber Berita", "Top News Sources"))}</div>
            <div class="card-subtitle">{esc(t(lang, "Distribusi sentimen lintas media — n = total artikel, % = porsi positif", "Sentiment distribution across media — n = total articles, % = positive share"))}</div>
            <div style="height:265px">{mk_source_chart(stats["sources"])}</div>
            <div class="subtle-rule">
              <div class="legend-row">
                <div class="legend-item"><span class="legend-swatch" style="width:14px;height:7px;background:#2d7a3a;border-radius:1px"></span>{esc(t(lang, "Positif", "Positive"))}</div>
                <div class="legend-item"><span class="legend-swatch" style="width:14px;height:7px;background:#cc2200;border-radius:1px"></span>{esc(t(lang, "Negatif", "Negative"))}</div>
                <div class="legend-item"><span class="legend-swatch" style="width:14px;height:7px;background:#b09580;border-radius:1px"></span>{esc(t(lang, "Netral", "Neutral"))}</div>
              </div>
            </div>
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )


def format_article_date(article: pd.Series) -> str:
    for col in ("published_at_wib", "published_at", "fetched_at"):
        value = article.get(col)
        if pd.notna(value):
            ts = pd.to_datetime(value, utc=True, errors="coerce")
            if pd.isna(ts):
                continue
            return ts.tz_convert("Asia/Jakarta").strftime("%d %b")
    return ""


def mk_article_table(df: pd.DataFrame, lang: str) -> str:
    labels = ["Judul", "Kategori", "Sentimen", "Confidence", "Sumber", "Tanggal"] if lang == "id" else ["Title", "Category", "Sentiment", "Confidence", "Source", "Date"]
    sent_label = {
        "positive": ("Positif", "Positive"),
        "negative": ("Negatif", "Negative"),
        "neutral": ("Netral", "Neutral"),
        "unknown": ("Tak Diketahui", "Unknown"),
    }
    rows = []
    for _, article in df.iterrows():
        title = article.get("title", "")
        category = category_label(article.get("category", ""), lang)
        sent = str(article.get("sentiment", "unknown")).lower()
        rows.append(
            "<tr class='news-row'>"
            f'<td style="max-width:300px;color:#2d2a25;line-height:1.35">{esc(title)}</td>'
            f'<td style="color:#786f62;white-space:nowrap">{esc(category)}</td>'
            f'<td><span class="news-pill pill-{sent if sent in {"positive","negative","neutral"} else "neutral"}">{esc(sent_label.get(sent, sent_label["unknown"])[0 if lang == "id" else 1])}</span></td>'
            f'<td style="color:#786f62;white-space:nowrap">{round(float(article.get("sentiment_confidence", 0)) * 100)}%</td>'
            f'<td style="color:#786f62;white-space:nowrap">{esc(article.get("source_id") or article.get("domain") or "unknown")}</td>'
            f'<td style="color:#786f62;white-space:nowrap">{esc(format_article_date(article))}</td>'
            "</tr>"
        )
    return f"""
    <div class="table-wrap">
      <table class="news-table">
        <thead><tr>{"".join(f"<th>{esc(label)}</th>" for label in labels)}</tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>
    """


def render_news(table_df: pd.DataFrame, lang: str) -> None:
    st.markdown(
        dedent(
            f"""
        <div class="section-pad">
          <div class="panel">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;gap:12px">
              <div>
                <div class="card-title" style="margin-bottom:1px">{esc(t(lang, "Artikel Berita Terkini", "Latest News Articles"))}</div>
                <div class="card-subtitle" style="margin-bottom:0">{esc(t(lang, "Diproses oleh pipeline kabar.io", "Processed by the kabar.io pipeline"))}</div>
              </div>
              <div class="chip">{len(table_df)} {esc(t(lang, "artikel", "articles"))}</div>
            </div>
            {mk_article_table(table_df, lang)}
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )


def render_page(nav: str, lang: str, stats: dict[str, object], dr: str, table_df: pd.DataFrame) -> None:
    if nav == "analysis":
        render_overview(stats, lang, dr)
    else:
        render_news(table_df, lang)


def mk_word_cloud(words: list[dict[str, object]]) -> str:
    colors = {"positive": "#2d7a3a", "negative": "#cc2200", "neutral": "#b09580"}
    if not words:
        words = [{"w": "kabar", "sz": 22, "s": "neutral"}]
    ranked = sorted(words, key=lambda row: float(row.get("sz", 0)), reverse=True)
    if len(ranked) == 1:
        ranked = ranked * 1

    parts = []
    size_scale = [float(row.get("sz", 18)) for row in ranked]
    max_size = max(size_scale) if size_scale else 18.0
    min_size = min(size_scale) if size_scale else 18.0
    def scaled_size(raw_size: float) -> float:
        if max_size == min_size:
            return 18.0
        spread = (raw_size - min_size) / (max_size - min_size)
        return 14.0 + spread * 20.0

    layout: list[tuple[dict[str, object], float, float]] = []
    center = ranked[0]
    layout.append((center, 50.0, 50.0))

    remaining = ranked[1:]
    if remaining:
        ring_plan = [6, 10, 14, 18]
        idx = 0
        ring_index = 0
        while idx < len(remaining):
            ring_count = ring_plan[ring_index] if ring_index < len(ring_plan) else ring_plan[-1] + (ring_index - len(ring_plan) + 1) * 6
            ring_items = remaining[idx : idx + ring_count]
            radius = 14 + ring_index * 12
            for i, row in enumerate(ring_items):
                angle = (2 * math.pi * i / max(len(ring_items), 1)) - math.pi / 2
                jitter = (ring_index % 2) * (math.pi / max(len(ring_items), 1))
                x = 50.0 + math.cos(angle + jitter) * radius
                y = 50.0 + math.sin(angle + jitter) * radius
                layout.append((row, x, y))
            idx += ring_count
            ring_index += 1

    for row, x, y in layout:
        size = float(row["sz"])
        color = colors.get(str(row["s"]), "#b09580")
        font_size = scaled_size(size)
        left = max(6.0, min(94.0, x))
        top = max(6.0, min(94.0, y))
        weight = 700 if size == max_size else 600 if size > (max_size + min_size) / 2 else 500
        word_key = str(row["w"])
        seed = sum(ord(ch) for ch in word_key)
        delay = round(-((seed % 7000) / 7000) * 6, 2)
        duration = 9 + ((seed % 5) * 1.5)
        parts.append(
            f'<span class="word-cloud-item" style="left:{left}%;top:{top}%;transform:translate(-50%,-50%);">'
            f'<span class="word-cloud-chip" style="font-size:{font_size}px;color:{color};font-weight:{weight};'
            f'animation-duration:{duration:.1f}s;animation-delay:{delay}s;'
            f'--chip-opacity:{0.78 + (font_size / 34.0) * 0.22};">{esc(row["w"])}</span>'
            f"</span>"
        )
    return f'<div class="word-cloud-circle">{"".join(parts)}</div>'
