from __future__ import annotations

import math

import pandas as pd
import streamlit as st
from textwrap import dedent

try:
    from .charts import mk_category_chart, mk_donut, mk_source_chart, mk_timeseries
    from .data import category_label, choose_date_col, esc, search_articles, t
except ImportError:  # pragma: no cover - script-style fallback
    from charts import mk_category_chart, mk_donut, mk_source_chart, mk_timeseries
    from data import category_label, choose_date_col, esc, search_articles, t


def nav_titles(nav: str, lang: str) -> tuple[str, str]:
    titles = {
        "analysis": (t(lang, "Analisis", "Analysis"), t(lang, "Ringkasan, sentimen, kategori, dan sumber dalam satu alur", "Summary, sentiment, category, and source in one flow")),
        "news": (t(lang, "Berita", "News"), t(lang, "Jelajahi artikel hasil pemrosesan", "Browse articles processed by the pipeline")),
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
    labeled_total = int(stats.get("labeled_total", 0))
    unknown_total = int(stats["sentiment_counts"].get("unknown", 0))
    pos = int(stats["sentiment_counts"].get("positive", 0))
    neg = int(stats["sentiment_counts"].get("negative", 0))
    neu = int(stats["sentiment_counts"].get("neutral", 0))
    labeled_pct = round((labeled_total / total) * 100) if total else 0
    pos_pct = round((pos / labeled_total) * 100) if labeled_total else 0
    neg_pct = round((neg / labeled_total) * 100) if labeled_total else 0
    neu_pct = round((neu / labeled_total) * 100) if labeled_total else 0
    avg_conf = float(stats["avg_conf"])

    st.markdown(
        dedent(
            f"""
        <div class="section-pad" id="overview">
          <div class="grid-4">
            {metric_card(t(lang, "Total Artikel", "Total Articles"), f"{total:,}".replace(",", "."), t(lang, f"{labeled_total} ({labeled_pct}%) artikel berlabel", f"{labeled_total} ({labeled_pct}%) labeled articles"))}
            {metric_card(t(lang, "Sentimen Positif", "Positive Sentiment"), f"{pos_pct}%", t(lang, "Porsi artikel positif", "Share of positive articles"), "positive")}
            {metric_card(t(lang, "Sentimen Negatif", "Negative Sentiment"), f"{neg_pct}%", t(lang, "Porsi artikel negatif", "Share of negative articles"), "negative")}
            {metric_card(t(lang, "Rata-rata keyakinan", "Avg. Confidence"), f"{round(avg_conf * 100)}%", t(lang, "Skor model Gemini", "Gemini model score"))}
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
              <div style="height:175px">{mk_donut(stats["sentiment_counts"], labeled_total or total, lang)}</div>
              <div class="subtle-rule">
                <div class="bar-caption"><span class="legend-item"><span class="legend-swatch" style="background:#2d7a3a"></span>{esc(t(lang, "Positif", "Positive"))}</span><strong>{pos:,} ({pos_pct}%)</strong></div>
                <div class="bar-caption"><span class="legend-item"><span class="legend-swatch" style="background:#cc2200"></span>{esc(t(lang, "Negatif", "Negative"))}</span><strong>{neg:,} ({neg_pct}%)</strong></div>
                <div class="bar-caption"><span class="legend-item"><span class="legend-swatch" style="background:#b09580"></span>{esc(t(lang, "Netral", "Neutral"))}</span><strong>{neu:,} ({neu_pct}%)</strong></div>
                <div class="news-page-meta" style="margin-top:8px">
                  {esc(t(lang, f"Belum dilabel: {unknown_total:,} artikel. Distribusi di atas hanya menghitung artikel berlabel.", f"Unlabeled: {unknown_total:,} articles. The chart only counts labeled articles."))}
                </div>
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
            <div class="card-title" style="margin-bottom:2px">{esc(t(lang, "Sumber Teratas", "Top Sources"))}</div>
            <div class="card-subtitle">{esc(t(lang, "Distribusi sentimen lintas sumber — n = total artikel, % = porsi positif", "Sentiment distribution across sources — n = total articles, % = positive share"))}</div>
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


def format_processed_at(article: pd.Series) -> str:
    value = article.get("sentiment_processed_at")
    if pd.notna(value):
        ts = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.notna(ts):
            return ts.tz_convert("Asia/Jakarta").strftime("%d %b %H:%M")
    return ""


def format_sort_label(lang: str, key: str) -> str:
    labels = {
        "published_at": t(lang, "Terbaru", "Newest"),
        "confidence": t(lang, "Confidence", "Confidence"),
        "title": t(lang, "Judul", "Title"),
        "source": t(lang, "Sumber", "Source"),
        "category": t(lang, "Kategori", "Category"),
        "sentiment": t(lang, "Sentimen", "Sentiment"),
        "status": t(lang, "Status AI", "AI Status"),
        "attempts": t(lang, "Percobaan", "Attempts"),
    }
    return labels.get(key, key)


def render_news_controls(df: pd.DataFrame, lang: str) -> tuple[pd.DataFrame, int, int, int, str]:
    sort_options = {
        "published_at": "published_at",
        "confidence": "sentiment_confidence",
        "title": "title",
        "source": "source_id",
        "category": "category",
        "sentiment": "sentiment",
        "status": "sentiment_status",
        "attempts": "sentiment_attempts",
    }
    cols = st.columns([1.55, 0.62, 0.62, 0.36], gap="small")
    with cols[0]:
        search = st.text_input(
            t(lang, "Cari di detail...", "Search in detail..."),
            value=st.session_state.get("news_table_search", ""),
            placeholder=t(lang, "Cari judul, reason, sumber, atau status...", "Search title, reason, source, or status..."),
            label_visibility="collapsed",
            key="news_table_search",
        )
    with cols[1]:
        sort_key = st.selectbox(
            t(lang, "Urutkan", "Sort by"),
            list(sort_options.keys()),
            format_func=lambda value: format_sort_label(lang, value),
            index=list(sort_options.keys()).index(st.session_state.get("news_table_sort", "published_at"))
            if st.session_state.get("news_table_sort", "published_at") in sort_options
            else 0,
            key="news_table_sort",
            label_visibility="collapsed",
        )
    with cols[2]:
        sort_dir = st.selectbox(
            t(lang, "Arah", "Direction"),
            ["desc", "asc"],
            index=0 if st.session_state.get("news_table_dir", "desc") == "desc" else 1,
            format_func=lambda value: t(lang, "Terbaru", "Newest") if value == "desc" else t(lang, "Terlama", "Oldest"),
            key="news_table_dir",
            label_visibility="collapsed",
        )
    with cols[3]:
        page_size = st.selectbox(
            t(lang, "Baris", "Rows"),
            [10, 20, 30, 50],
            index=[10, 20, 30, 50].index(st.session_state.get("news_table_size", 10))
            if st.session_state.get("news_table_size", 10) in [10, 20, 30, 50]
            else 0,
            key="news_table_size",
            label_visibility="collapsed",
        )

    state_sig = (search.strip(), sort_key, sort_dir, page_size)
    if st.session_state.get("news_table_sig") != state_sig:
        st.session_state.news_table_page = 1
        st.session_state.news_table_sig = state_sig

    filtered = search_articles(df, search)
    if filtered.empty:
        return filtered, page_size, 1, 0, search

    sort_col = sort_options.get(sort_key, "published_at")
    sort_df = filtered.copy()
    date_col = choose_date_col(sort_df)
    sort_df[date_col] = pd.to_datetime(sort_df[date_col], errors="coerce", utc=True)
    sort_df["__sent_rank"] = sort_df["sentiment"].fillna("unknown").str.lower().map({"positive": 0, "neutral": 1, "negative": 2, "unknown": 3}).fillna(3)
    sort_df["__status_rank"] = sort_df["sentiment_status"].fillna("pending").str.lower().map({"done": 0, "processing": 1, "pending": 2}).fillna(3)

    if sort_col == "published_at":
        sort_value = date_col
        sort_kwargs = {"na_position": "last"}
    elif sort_col == "sentiment_confidence":
        sort_value = sort_col
        sort_kwargs = {"na_position": "last"}
    elif sort_col == "sentiment_attempts":
        sort_value = sort_col
        sort_kwargs = {"na_position": "last"}
    elif sort_col == "title":
        sort_df["__title"] = sort_df["title"].fillna("").astype(str).str.lower()
        sort_value = "__title"
        sort_kwargs = {"na_position": "last"}
    elif sort_col == "source_id":
        sort_df["__source"] = sort_df["source_id"].fillna("").replace("", pd.NA).fillna(sort_df["domain"].fillna("unknown")).fillna("unknown").astype(str).str.lower()
        sort_value = "__source"
        sort_kwargs = {"na_position": "last"}
    elif sort_col == "category":
        sort_df["__category"] = sort_df["category"].fillna("").astype(str).str.lower()
        sort_value = "__category"
        sort_kwargs = {"na_position": "last"}
    elif sort_col == "sentiment":
        sort_value = "__sent_rank"
        sort_kwargs = {"na_position": "last"}
    else:
        sort_value = "__status_rank"
        sort_kwargs = {"na_position": "last"}

    ascending = sort_dir == "asc"
    sort_df = sort_df.sort_values(sort_value, ascending=ascending, **sort_kwargs).reset_index(drop=True)

    total_pages = max(1, math.ceil(len(sort_df) / page_size))
    current_page = int(st.session_state.get("news_table_page", 1))
    current_page = min(max(current_page, 1), total_pages)
    st.session_state.news_table_page = current_page
    start = (current_page - 1) * page_size
    page_df = sort_df.iloc[start : start + page_size].reset_index(drop=True)

    return page_df, page_size, total_pages, len(filtered), search


def mk_article_table(df: pd.DataFrame, lang: str) -> str:
    labels = [
        t(lang, "Judul", "Title"),
        t(lang, "Kategori", "Category"),
        t(lang, "Sentimen", "Sentiment"),
        t(lang, "Confidence", "Confidence"),
        t(lang, "Status AI", "AI Status"),
        t(lang, "Reason AI", "AI Reason"),
        t(lang, "Sumber", "Source"),
        t(lang, "Tanggal", "Date"),
        t(lang, "Attempts", "Attempts"),
        t(lang, "Diproses", "Processed"),
        t(lang, "Error", "Error"),
    ]
    sent_label = {
        "positive": ("Positif", "Positive"),
        "negative": ("Negatif", "Negative"),
        "neutral": ("Netral", "Neutral"),
        "unknown": ("Belum Dilabel", "Unlabeled"),
    }
    rows = []
    for _, article in df.iterrows():
        title = article.get("title", "")
        category = category_label(article.get("category", ""), lang)
        sent = str(article.get("sentiment", "unknown")).lower()
        reason = str(article.get("sentiment_reason", "")).strip() or "—"
        status = str(article.get("sentiment_status", "pending")).strip().lower() or "pending"
        attempts = int(article.get("sentiment_attempts", 0) or 0)
        processed_at = format_processed_at(article) or "—"
        last_error = str(article.get("sentiment_last_error", "")).strip() or "—"
        rows.append(
            "<tr class='news-row'>"
            f'<td style="max-width:280px;color:#2d2a25;line-height:1.35"><div class="news-line">{esc(title)}</div></td>'
            f'<td style="color:#786f62;white-space:nowrap">{esc(category)}</td>'
            f'<td><span class="news-pill pill-{sent if sent in {"positive","negative","neutral"} else "unknown"}">{esc(sent_label.get(sent, sent_label["unknown"])[0 if lang == "id" else 1])}</span></td>'
            f'<td style="color:#786f62;white-space:nowrap">{round(float(article.get("sentiment_confidence", 0)) * 100)}%</td>'
            f'<td style="white-space:nowrap"><span class="news-pill pill-{"positive" if status == "done" else "neutral" if status == "processing" else "unknown"}">{esc(status)}</span></td>'
            f'<td style="max-width:260px;color:#4f473e;line-height:1.4"><div class="news-line news-reason">{esc(reason)}</div></td>'
            f'<td style="color:#786f62;white-space:nowrap">{esc(article.get("source_id") or article.get("domain") or "unknown")}</td>'
            f'<td style="color:#786f62;white-space:nowrap">{esc(format_article_date(article))}</td>'
            f'<td style="color:#786f62;white-space:nowrap">{attempts}</td>'
            f'<td style="color:#786f62;white-space:nowrap">{esc(processed_at)}</td>'
            f'<td style="max-width:220px;color:#8c8278;line-height:1.35"><div class="news-note">{esc(last_error)}</div></td>'
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
    page_df, page_size, total_pages, filtered_count, _search = render_news_controls(table_df, lang)
    current_page = int(st.session_state.get("news_table_page", 1))
    if page_df.empty:
        table_html = f"""
        <div class="panel" style="border-style:dashed;background:#fbf9f5">
          <div class="news-page-meta">{esc(t(lang, "Tidak ada artikel yang cocok dengan filter ini.", "No articles match this filter."))}</div>
        </div>
        """
    else:
        table_html = mk_article_table(page_df, lang)
    page_summary = t(lang, f"Halaman {current_page}/{total_pages}", f"Page {current_page}/{total_pages}")
    st.markdown(
        dedent(
            f"""
        <div class="section-pad">
          <div class="panel">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;gap:12px">
              <div>
            <div class="card-title" style="margin-bottom:1px">{esc(t(lang, "Detail Artikel", "Article Detail"))}</div>
                <div class="card-subtitle" style="margin-bottom:0">{esc(t(lang, "Hasil pemrosesan kabar.io", "Processed by the kabar.io pipeline"))}</div>
              </div>
            </div>
            <div class="news-page-meta" style="margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap">
              <span>{esc(t(lang, f"{filtered_count} artikel cocok dengan filter dan pencarian ini.", f"{filtered_count} articles match this filter and search."))}</span>
              <span class="news-page-pill">{esc(page_summary)}</span>
            </div>
            {table_html}
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )
    if total_pages > 1:
        prev_col, meta_col, next_col = st.columns([0.28, 0.44, 0.28], gap="small")
        with prev_col:
            if st.button(t(lang, "← Kembali", "← Back"), use_container_width=True, disabled=current_page <= 1, key="news_prev_page"):
                st.session_state.news_table_page = max(1, current_page - 1)
                st.rerun()
        with meta_col:
            st.markdown(
                f'<div class="news-page-pill" style="justify-content:center;width:100%">{esc(t(lang, f"Halaman {current_page}/{total_pages}", f"Page {current_page}/{total_pages}"))}</div>',
                unsafe_allow_html=True,
            )
        with next_col:
            if st.button(t(lang, "Lanjut →", "Next →"), use_container_width=True, disabled=current_page >= total_pages, key="news_next_page"):
                st.session_state.news_table_page = min(total_pages, current_page + 1)
                st.rerun()


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
