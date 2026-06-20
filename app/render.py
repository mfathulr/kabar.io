from __future__ import annotations

import math
import uuid

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
                  <div class="legend-item"><span class="legend-swatch" style="width:18px;height:1px;background:#786f62;border-radius:1px;opacity:0.4"></span>{esc(t(lang, "Total", "Total"))}</div>
                </div>
              </div>
              <div style="height:230px">{mk_timeseries(stats["time_series"], lang)}</div>
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
            <div style="height:265px">{mk_source_chart(stats["sources"], lang)}</div>
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


def build_news_table_df(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    if df.empty:
        return df

    table_df = df.copy()
    date_col = choose_date_col(table_df)
    published_at = pd.to_datetime(table_df[date_col], errors="coerce", utc=True)
    if getattr(published_at.dt, "tz", None) is not None:
        published_at = published_at.dt.tz_convert("Asia/Jakarta")

    processed_at = pd.to_datetime(table_df["sentiment_processed_at"], errors="coerce", utc=True)
    if getattr(processed_at.dt, "tz", None) is not None:
        processed_at = processed_at.dt.tz_convert("Asia/Jakarta")

    source = table_df["source_id"].fillna("").replace("", pd.NA).fillna(table_df["domain"].fillna("unknown")).fillna("unknown").astype(str)
    sentiment = table_df["sentiment"].fillna("unknown").astype(str).str.lower()
    status = table_df["sentiment_status"].fillna("pending").astype(str).str.lower()

    sent_label = {
        "positive": t(lang, "Positif", "Positive"),
        "negative": t(lang, "Negatif", "Negative"),
        "neutral": t(lang, "Netral", "Neutral"),
        "unknown": t(lang, "Belum Dilabel", "Unlabeled"),
    }
    status_label = {
        "done": t(lang, "Selesai", "Done"),
        "processing": t(lang, "Memproses", "Processing"),
        "pending": t(lang, "Menunggu", "Pending"),
    }

    table_df["title_display"] = table_df["title"].fillna("").astype(str)
    table_df["category_display"] = table_df["category"].fillna("").map(lambda value: category_label(value, lang)).astype(str)
    table_df["sentiment_display"] = sentiment.map(sent_label).fillna(sentiment)
    table_df["confidence_display"] = (pd.to_numeric(table_df["sentiment_confidence"], errors="coerce").fillna(0) * 100).round(0).astype("Int64")
    table_df["status_display"] = status.map(status_label).fillna(status)
    table_df["reason_display"] = table_df["sentiment_reason"].fillna("").astype(str)
    table_df["source_display"] = source.astype(str)
    table_df["published_at_display"] = published_at
    table_df["attempts_display"] = pd.to_numeric(table_df["sentiment_attempts"], errors="coerce").fillna(0).astype("Int64")
    table_df["processed_display"] = processed_at
    table_df["error_display"] = table_df["sentiment_last_error"].fillna("").astype(str)
    return table_df


def news_header_label(lang: str, key: str) -> str:
    labels = {
        "published_at": t(lang, "Tanggal", "Date"),
        "confidence": t(lang, "Confidence", "Confidence"),
        "title": t(lang, "Judul", "Title"),
        "source": t(lang, "Sumber", "Source"),
        "category": t(lang, "Kategori", "Category"),
        "sentiment": t(lang, "Sentimen", "Sentiment"),
        "status": t(lang, "Status model", "Model status"),
        "reason": t(lang, "Alasan model", "Model rationale"),
        "attempts": t(lang, "Attempts", "Attempts"),
        "processed": t(lang, "Diproses", "Processed"),
        "error": t(lang, "Error", "Error"),
    }
    return labels.get(key, key)


def render_news_toolbar(lang: str) -> None:
    news_column_keys = [
        "published_at",
        "title",
        "source",
        "category",
        "sentiment",
        "confidence",
        "status",
        "reason",
        "attempts",
        "processed",
        "error",
    ]
    column_labels = {
        "published_at": news_header_label(lang, "published_at"),
        "title": news_header_label(lang, "title"),
        "source": news_header_label(lang, "source"),
        "category": news_header_label(lang, "category"),
        "sentiment": news_header_label(lang, "sentiment"),
        "confidence": news_header_label(lang, "confidence"),
        "status": news_header_label(lang, "status"),
        "reason": news_header_label(lang, "reason"),
        "attempts": news_header_label(lang, "attempts"),
        "processed": news_header_label(lang, "processed"),
        "error": news_header_label(lang, "error"),
    }
    compact_labels = {
        "published_at": t(lang, "Tgl", "Date"),
        "title": t(lang, "Judul", "Title"),
        "source": t(lang, "Sumber", "Source"),
        "category": t(lang, "Kat", "Cat"),
        "sentiment": t(lang, "Sent", "Sent"),
        "confidence": t(lang, "Key", "Conf"),
        "status": t(lang, "Status", "Status"),
        "reason": t(lang, "Alasan", "Reason"),
        "attempts": t(lang, "Attempts", "Attempts"),
        "processed": t(lang, "Proc", "Proc"),
        "error": t(lang, "Error", "Error"),
    }

    sort_mode_options = {
        "newest": t(lang, "Terbaru", "Newest"),
        "oldest": t(lang, "Terlama", "Oldest"),
        "confidence_desc": t(lang, "Keyakinan tinggi", "High confidence"),
        "confidence_asc": t(lang, "Keyakinan rendah", "Low confidence"),
        "attempts_desc": t(lang, "Attempts tinggi", "High attempts"),
        "custom": t(lang, "Kustom", "Custom"),
    }
    sort_field_options = [
        ("published_at", t(lang, "Tanggal", "Date")),
        ("title", t(lang, "Judul", "Title")),
        ("source", t(lang, "Sumber", "Source")),
        ("category", t(lang, "Kategori", "Category")),
        ("sentiment", t(lang, "Sentimen", "Sentiment")),
        ("confidence", t(lang, "Keyakinan", "Confidence")),
        ("status", t(lang, "Status model", "Model status")),
        ("reason", t(lang, "Alasan model", "Model rationale")),
        ("attempts", t(lang, "Attempts", "Attempts")),
        ("processed", t(lang, "Diproses", "Processed")),
        ("error", t(lang, "Error", "Error")),
    ]

    if "news_visible_columns" not in st.session_state:
        st.session_state.news_visible_columns = list(news_column_keys)
    if "news_sort_mode" not in st.session_state:
        st.session_state.news_sort_mode = "custom"
    if "news_sort_levels" not in st.session_state:
        st.session_state.news_sort_levels = [
            {"id": uuid.uuid4().hex, "field": "published_at", "direction": "desc"},
        ]
    if st.session_state.news_sort_mode != "custom":
        st.session_state.news_sort_mode = "custom"

    toolbar_cols = st.columns([0.14, 0.14, 0.72], gap="small")
    with toolbar_cols[0]:
        visible_columns = news_visible_columns()
        with st.popover(t(lang, "Kolom terpilih", "Selected columns")):
            st.markdown('<div class="news-columns-popover"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Kolom terpilih", "Selected columns"))}</div>', unsafe_allow_html=True)
            st.caption(t(lang, "Pilih kolom yang ingin ditampilkan.", "Choose which columns to display."))
            selected_columns = []
            checkbox_cols = st.columns(2, gap="small")
            for idx, column_key in enumerate(news_column_keys):
                col = checkbox_cols[idx % 2]
                with col:
                    checked = st.checkbox(
                        column_labels[column_key],
                        value=st.session_state.get(
                            f"news_col_{column_key}",
                            column_key in (st.session_state.news_visible_columns or news_column_keys),
                        ),
                        key=f"news_col_{column_key}",
                    )
                if checked:
                    selected_columns.append(column_key)
            st.session_state.news_visible_columns = selected_columns or list(news_column_keys)
    with toolbar_cols[1]:
        with st.popover(t(lang, "Urutkan", "Sort")):
            st.markdown('<div class="news-sort-popover"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Urutkan", "Sort"))}</div>', unsafe_allow_html=True)
            st.caption(t(lang, "Pilih kolom dan arah untuk tiap level.", "Choose the column and direction for each level."))
            if st.button(t(lang, "+ Tambah level", "+ Add level"), use_container_width=True):
                st.session_state.news_sort_levels.append({"id": uuid.uuid4().hex, "field": "", "direction": "desc"})
                st.rerun()

            sort_field_map = dict(sort_field_options)
            levels = list(st.session_state.news_sort_levels)
            updated_levels = []

            for idx, level in enumerate(levels):
                level_id = str(level.get("id") or idx)
                st.markdown(f'<div class="news-sort-level">L{idx + 1}</div>', unsafe_allow_html=True)

                field_value = st.selectbox(
                    t(lang, "Kolom", "Column"),
                    options=[""] + [item[0] for item in sort_field_options],
                    format_func=lambda key: t(lang, "Pilih kolom", "Choose column") if key == "" else sort_field_map[key],
                    key=f"news_sort_field_{level_id}",
                    index=([""] + [item[0] for item in sort_field_options]).index(str(level.get("field", ""))) if str(level.get("field", "")) in ([""] + [item[0] for item in sort_field_options]) else 0,
                    label_visibility="collapsed",
                )

                dir_cols = st.columns([1, 0.12], gap="xxsmall")
                with dir_cols[0]:
                    dir_value = st.selectbox(
                        t(lang, "Arah", "Direction"),
                        options=["desc", "asc"],
                        format_func=lambda key: t(lang, "Turun", "Desc") if key == "desc" else t(lang, "Naik", "Asc"),
                        key=f"news_sort_dir_{level_id}",
                        index=0 if str(level.get("direction", "desc")).lower() == "desc" else 1,
                        label_visibility="collapsed",
                    )
                with dir_cols[1]:
                    if len(levels) > 1 and st.button("×", key=f"news_sort_remove_{level_id}", use_container_width=True):
                        st.session_state.news_sort_levels = [item for item in st.session_state.news_sort_levels if str(item.get("id")) != level_id]
                        st.rerun()

                updated_levels.append({"id": level_id, "field": field_value, "direction": dir_value})

            st.session_state.news_sort_levels = updated_levels
    with toolbar_cols[2]:
        st.text_input(
            "",
            value=st.session_state.get("news_table_search", ""),
            placeholder=t(lang, "Cari judul artikel...", "Search article titles..."),
            key="news_table_search",
            label_visibility="collapsed",
        )


def news_column_order() -> list[str]:
    return [
        "published_at",
        "title",
        "source",
        "category",
        "sentiment",
        "confidence",
        "status",
        "reason",
        "attempts",
        "processed",
        "error",
    ]


def news_visible_columns() -> list[str]:
    all_columns = news_column_order()
    selected = [column for column in st.session_state.get("news_visible_columns", all_columns) if column in all_columns]
    return selected or all_columns


def news_sort_key_map() -> dict[str, str]:
    return {
        "published_at": "__sort_published",
        "title": "__sort_title",
        "source": "__sort_source",
        "category": "__sort_category",
        "sentiment": "__sort_sentiment",
        "confidence": "__sort_confidence",
        "status": "__sort_status_rank",
        "reason": "__sort_reason",
        "attempts": "__sort_attempts",
        "processed": "__sort_processed",
        "error": "__sort_error",
    }


def apply_news_sort(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    mode = str(st.session_state.get("news_sort_mode", "newest"))
    preset = {
        "newest": [("__sort_published", False), ("__sort_processed", False)],
        "oldest": [("__sort_published", True), ("__sort_processed", True)],
        "confidence_desc": [("__sort_confidence", False), ("__sort_published", False)],
        "confidence_asc": [("__sort_confidence", True), ("__sort_published", False)],
        "attempts_desc": [("__sort_attempts", False), ("__sort_published", False)],
    }
    specs: list[tuple[str, bool]] = list(preset.get(mode, []))
    if mode == "custom":
        for level in st.session_state.get("news_sort_levels", []):
            field = str(level.get("field", "")).strip()
            direction = str(level.get("direction", "desc")).strip().lower()
            if not field:
                continue
            mapped = news_sort_key_map().get(field)
            if mapped:
                specs.append((mapped, direction != "desc"))
    if not specs:
        specs = preset["newest"]

    sort_columns = [column for column, _ in specs if column in df.columns]
    if not sort_columns:
        return df
    ascending = [ascending for column, ascending in specs if column in df.columns]
    return df.sort_values(sort_columns, ascending=ascending, na_position="last").reset_index(drop=True)


def render_news_header(lang: str, visible_columns: list[str] | None = None) -> str:
    headers = visible_columns or news_column_order()
    labels = []
    for key in headers:
        labels.append(f'<th class="news-th"><span class="news-th-label">{esc(news_header_label(lang, key))}</span></th>')
    return "".join(labels)


def render_news_rows(df: pd.DataFrame, lang: str, visible_columns: list[str] | None = None) -> str:
    sent_label = {
        "positive": ("Positif", "Positive"),
        "negative": ("Negatif", "Negative"),
        "neutral": ("Netral", "Neutral"),
        "unknown": ("Belum Dilabel", "Unlabeled"),
    }
    status_label = {
        "done": ("Selesai", "Done"),
        "processing": ("Memproses", "Processing"),
        "pending": ("Menunggu", "Pending"),
    }
    columns = visible_columns or news_column_order()

    def safe_text(value: object, fallback: str = "—") -> str:
        if value is None or pd.isna(value):
            return fallback
        text = str(value).strip()
        return text if text and text != "NaT" else fallback

    rows = []
    for _, article in df.iterrows():
        title = safe_text(article.get("title_display", article.get("title", "")))
        category = safe_text(article.get("category_display", category_label(article.get("category", ""), lang)))
        sent = str(article.get("sentiment", "unknown")).lower()
        reason = safe_text(article.get("reason_display", article.get("sentiment_reason", "")))
        status = str(article.get("sentiment_status", "pending")).strip().lower() or "pending"
        source = safe_text(article.get("source_display", article.get("source_id") or article.get("domain") or "unknown"), "unknown")
        published = safe_text(article.get("published_at_display", ""))
        attempts_raw = article.get("attempts_display", article.get("sentiment_attempts", 0))
        attempts = int(0 if attempts_raw is None or pd.isna(attempts_raw) else attempts_raw)
        processed = safe_text(article.get("processed_display", article.get("sentiment_processed_at", "")))
        error = safe_text(article.get("error_display", article.get("sentiment_last_error", "")))
        confidence_raw = article.get("confidence_display", article.get("sentiment_confidence", 0))
        confidence = 0 if confidence_raw is None or pd.isna(confidence_raw) else confidence_raw
        cells: list[str] = []
        for column in columns:
            if column == "published_at":
                cells.append(f'<td class="cell-meta">{esc(published)}</td>')
            elif column == "title":
                cells.append(f'<td class="cell-title">{esc(title)}</td>')
            elif column == "source":
                cells.append(f'<td class="cell-meta">{esc(source)}</td>')
            elif column == "category":
                cells.append(f'<td class="cell-meta">{esc(category)}</td>')
            elif column == "sentiment":
                cells.append(f'<td><span class="news-pill pill-{sent if sent in {"positive","negative","neutral"} else "unknown"}">{esc(sent_label.get(sent, sent_label["unknown"])[0 if lang == "id" else 1])}</span></td>')
            elif column == "confidence":
                cells.append(f'<td class="cell-meta">{int(round(float(confidence)))}%</td>')
            elif column == "status":
                cells.append(f'<td><span class="news-pill pill-{"positive" if status == "done" else "neutral" if status == "processing" else "unknown"}">{esc(status_label.get(status, status_label["pending"])[0 if lang == "id" else 1])}</span></td>')
            elif column == "reason":
                cells.append(f'<td class="cell-reason">{esc(reason)}</td>')
            elif column == "attempts":
                cells.append(f'<td class="cell-meta">{attempts}</td>')
            elif column == "processed":
                cells.append(f'<td class="cell-meta">{esc(processed)}</td>')
            elif column == "error":
                cells.append(f'<td class="cell-error">{esc(error)}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "".join(rows)


def render_news(table_df: pd.DataFrame, lang: str) -> None:
    search = st.session_state.get("news_table_search", "")
    render_news_toolbar(lang)

    filtered = search_articles(table_df, search)
    sorted_df = filtered.copy()
    date_col = choose_date_col(sorted_df)
    sorted_df[date_col] = pd.to_datetime(sorted_df[date_col], errors="coerce", utc=True)
    sorted_df = sorted_df.sort_values(date_col, ascending=False, na_position="last").reset_index(drop=True)
    sorted_df["sentiment_confidence"] = pd.to_numeric(sorted_df["sentiment_confidence"], errors="coerce")
    sorted_df["sentiment_attempts"] = pd.to_numeric(sorted_df["sentiment_attempts"], errors="coerce")
    sorted_df["__published"] = pd.to_datetime(sorted_df[date_col], errors="coerce", utc=True)
    sorted_df["__processed"] = pd.to_datetime(sorted_df["sentiment_processed_at"], errors="coerce", utc=True)
    display_df = build_news_table_df(sorted_df, lang)
    if not display_df.empty:
        display_df["published_at_display"] = sorted_df["__published"].dt.tz_convert("Asia/Jakarta").dt.strftime("%d %b %Y %H:%M").fillna("—").to_list() if "__published" in sorted_df.columns else ["—"] * len(display_df)
        display_df["sentiment_processed_display"] = sorted_df["__processed"].dt.tz_convert("Asia/Jakarta").dt.strftime("%d %b %H:%M").fillna("—").to_list() if "__processed" in sorted_df.columns else ["—"] * len(display_df)
        display_df["__sort_published"] = pd.to_datetime(sorted_df["__published"], errors="coerce", utc=True)
        display_df["__sort_processed"] = pd.to_datetime(sorted_df["__processed"], errors="coerce", utc=True)
        display_df["__sort_title"] = display_df["title_display"].fillna("").astype(str).str.lower()
        display_df["__sort_source"] = display_df["source_display"].fillna("").astype(str).str.lower()
        display_df["__sort_category"] = display_df["category_display"].fillna("").astype(str).str.lower()
        display_df["__sort_sentiment"] = display_df["sentiment_display"].fillna("").astype(str).str.lower()
        display_df["__sort_confidence"] = pd.to_numeric(display_df["confidence_display"], errors="coerce")
        display_df["__sort_attempts"] = pd.to_numeric(display_df["attempts_display"], errors="coerce")
        status_rank = {"done": 0, "processing": 1, "pending": 2}
        display_df["__sort_status_rank"] = display_df["status_display"].fillna("").astype(str).str.lower().map(status_rank).fillna(99)
        display_df["__sort_reason"] = display_df["reason_display"].fillna("").astype(str).str.lower()
        display_df["__sort_error"] = display_df["error_display"].fillna("").astype(str).str.lower()
        display_df = apply_news_sort(display_df)

    if display_df.empty:
        st.markdown(
            f'<div class="news-table-empty">{esc(t(lang, "Tidak ada artikel yang cocok dengan filter ini.", "No articles match this filter."))}</div>',
            unsafe_allow_html=True,
        )
    else:
        visible_columns = news_visible_columns()
        st.markdown(
            f"""
            <div class="news-table-scroll">
              <table class="news-grid-table">
                <thead><tr>{render_news_header(lang, visible_columns)}</tr></thead>
                <tbody>
                  {render_news_rows(display_df, lang, visible_columns)}
                </tbody>
              </table>
            </div>
            """,
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
