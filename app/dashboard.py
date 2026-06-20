from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    from .data import clear_dashboard_snapshot_cache, filter_articles, build_stats, load_dashboard_snapshot, esc, t
    from .render import page_css, render_page, topbar
except ImportError:  # pragma: no cover - script-style fallback
    from data import clear_dashboard_snapshot_cache, filter_articles, build_stats, load_dashboard_snapshot, esc, t
    from render import page_css, render_page, topbar


def format_refresh_label(refresh_at: str | None) -> str:
    if not refresh_at:
        return "Belum ada"
    try:
        ts = datetime.fromisoformat(refresh_at)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=ZoneInfo("UTC"))
        local_ts = ts.astimezone(ZoneInfo("Asia/Jakarta"))
        return local_ts.strftime("%d %b %Y, %H:%M WIB")
    except ValueError:
        return refresh_at


def localize_source_note(note: str, lang: str) -> str:
    translations = {
        "Neon/Postgres unavailable": ("Neon/Postgres tidak tersedia", "Neon/Postgres unavailable"),
        "Neon/Postgres empty": ("Neon/Postgres kosong", "Neon/Postgres empty"),
        "data/news.csv missing": ("file data/news.csv tidak ditemukan", "data/news.csv missing"),
        "Demo": ("Demo", "Demo"),
    }
    if not note:
        return t(lang, "Belum ada catatan", "No note yet")
    parts = [part.strip() for part in note.split(";") if part.strip()]
    if not parts:
        return note
    localized = [translations.get(part, (part, part))[0 if lang == "id" else 1] for part in parts]
    return "; ".join(localized)


def build_source_options(df) -> list[str]:
    if df.empty:
        return ["all"]
    source_series = (
        df["source_id"].fillna("").replace("", pd.NA).fillna(df["domain"].fillna("unknown")).fillna("unknown").astype(str).str.lower()
    )
    options = ["all"]
    options.extend(sorted({value for value in source_series.tolist() if value}))
    return options


def sidebar_controls(source_name: str, source_note: str, refresh_at: str | None) -> tuple[str, bool]:
    lang = st.session_state.lang
    display_note = localize_source_note(source_note, lang)
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand">
              <div class="sidebar-logo">kabar<span class="accent">.io</span></div>
              <div class="sidebar-subtitle">{esc(t(lang, "Pantau Berita Indonesia", "Indonesian News Monitor"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="status-box" style="margin-bottom:12px">
              <div class="status-row"><div class="pulse"></div><span style="font-size:11px;color:#9e9589;font-weight:500">{esc(t(lang, "Alur pemrosesan aktif", "Pipeline active"))}</span></div>
              <div style="font-size:10px;color:#3d3028">{esc(t(lang, "Data", "Data"))}: <span style="color:#5c5048">{esc(source_name)}</span></div>
              <div style="font-size:10px;color:#5c5048">{esc(t(lang, "Catatan", "Note"))}: {esc(display_note)}</div>
              <div style="font-size:10px;color:#5c5048">{esc(t(lang, "Terakhir diperbarui", "Last refreshed"))}: {esc(format_refresh_label(refresh_at))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        lang = st.radio(
            t(lang, "Bahasa", "Language"),
            ["id", "en"],
            index=["id", "en"].index(st.session_state.lang),
            horizontal=True,
            label_visibility="collapsed",
            format_func=lambda value: value.upper(),
        )
        dark = st.toggle(t(lang, "Gelap", "Dark"), value=st.session_state.dark)

    return lang, dark


def refresh_strip(refresh_at: str | None) -> None:
    left, right = st.columns([1, 0.12], gap="small")
    with left:
        st.markdown(
            f'<div class="refresh-strip"><p class="refresh-meta">{esc(t(st.session_state.lang, "Terakhir diperbarui", "Last refreshed"))}: {esc(format_refresh_label(refresh_at))}</p></div>',
            unsafe_allow_html=True,
        )
    with right:
        if st.button(t(st.session_state.lang, "Segarkan", "Refresh"), use_container_width=True):
            clear_dashboard_snapshot_cache()
            st.session_state.latest_refresh_at = None
            st.rerun()


def main_filters(show_search: bool, source_options: list[str]) -> tuple[str, str, str, str, str]:
    cols = st.columns(4, gap="small")
    dr_options = ["7d", "14d", "30d", "90d"]
    sent_options = ["all", "positive", "negative", "neutral"]
    category_options = ["all", "breaking", "top", "business", "education", "politics", "sports", "technology", "world", "health", "entertainment", "domestic", "crime", "environment", "science", "food", "lifestyle", "tourism", "other"]
    lang = st.session_state.lang

    category_fmt = lambda value: {
        "all": t(lang, "Semua", "All"),
        "breaking": t(lang, "Berita Terkini", "Breaking News"),
        "top": t(lang, "Teratas", "Top"),
        "business": t(lang, "Bisnis", "Business"),
        "education": t(lang, "Pendidikan", "Education"),
        "politics": t(lang, "Politik", "Politics"),
        "sports": t(lang, "Olahraga", "Sports"),
        "technology": t(lang, "Teknologi", "Technology"),
        "world": t(lang, "Dunia", "World"),
        "health": t(lang, "Kesehatan", "Health"),
        "entertainment": t(lang, "Hiburan", "Entertainment"),
        "domestic": t(lang, "Domestik", "Domestic"),
        "crime": t(lang, "Kriminal", "Crime"),
        "environment": t(lang, "Lingkungan", "Environment"),
        "science": t(lang, "Sains", "Science"),
        "food": t(lang, "Kuliner", "Food"),
        "lifestyle": t(lang, "Gaya Hidup", "Lifestyle"),
        "tourism": t(lang, "Pariwisata", "Tourism"),
        "other": t(lang, "Lainnya", "Other"),
    }[value]

    source_fmt = lambda value: t(lang, "Semua", "All") if value == "all" else value

    if show_search:
        with cols[0]:
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Sumber", "Source"))}</div>', unsafe_allow_html=True)
            source_f = st.selectbox(
                "",
                source_options,
                index=source_options.index(st.session_state.source_f) if st.session_state.source_f in source_options else 0,
                label_visibility="collapsed",
                key="main_source",
                format_func=source_fmt,
            )
        with cols[1]:
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Kategori", "Category"))}</div>', unsafe_allow_html=True)
            cat_f = st.selectbox(
                "",
                category_options,
                index=category_options.index(st.session_state.cat_f),
                label_visibility="collapsed",
                key="main_category",
                format_func=category_fmt,
            )
        with cols[2]:
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Sentimen", "Sentiment"))}</div>', unsafe_allow_html=True)
            sent_f = st.selectbox(
                "",
                sent_options,
                index=sent_options.index(st.session_state.sent_f),
                label_visibility="collapsed",
                key="main_sentiment",
                format_func=lambda value: {
                    "all": t(lang, "Semua", "All"),
                    "positive": t(lang, "Positif", "Positive"),
                    "negative": t(lang, "Negatif", "Negative"),
                    "neutral": t(lang, "Netral", "Neutral"),
                }[value],
            )
        with cols[3]:
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Pencarian", "Search"))}</div>', unsafe_allow_html=True)
            search = st.text_input(
                "",
                value=st.session_state.search,
                placeholder=t(lang, "Cari judul atau sumber...", "Search by title or source..."),
                label_visibility="collapsed",
                key="main_search",
            )
        dr = st.session_state.dr
    else:
        with cols[0]:
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Rentang Waktu", "Time Range"))}</div>', unsafe_allow_html=True)
            dr = st.selectbox("", dr_options, index=dr_options.index(st.session_state.dr), label_visibility="collapsed", key="main_dr")
        with cols[1]:
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Sumber", "Source"))}</div>', unsafe_allow_html=True)
            source_f = st.selectbox(
                "",
                source_options,
                index=source_options.index(st.session_state.source_f) if st.session_state.source_f in source_options else 0,
                label_visibility="collapsed",
                key="main_source",
                format_func=source_fmt,
            )
        with cols[2]:
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Kategori", "Category"))}</div>', unsafe_allow_html=True)
            cat_f = st.selectbox(
                "",
                category_options,
                index=category_options.index(st.session_state.cat_f),
                label_visibility="collapsed",
                key="main_category",
                format_func=category_fmt,
            )
        with cols[3]:
            st.markdown(f'<div class="toolbar-label">{esc(t(lang, "Sentimen", "Sentiment"))}</div>', unsafe_allow_html=True)
            sent_f = st.selectbox(
                "",
                sent_options,
                index=sent_options.index(st.session_state.sent_f),
                label_visibility="collapsed",
                key="main_sentiment",
                format_func=lambda value: {
                    "all": t(lang, "Semua", "All"),
                    "positive": t(lang, "Positif", "Positive"),
                    "negative": t(lang, "Negatif", "Negative"),
                    "neutral": t(lang, "Netral", "Neutral"),
                }[value],
            )
        search = st.session_state.search

    return dr, "all" if sent_f == "all" else sent_f, "all" if cat_f == "all" else cat_f, "all" if source_f == "all" else source_f, search


def page_navigation(nav: str) -> None:
    lang = st.session_state.lang
    st.markdown('<div class="nav-footer"></div>', unsafe_allow_html=True)
    if nav == "analysis":
        left, right = st.columns([1, 0.28], gap="small")
        with right:
            if st.button(t(lang, "Lihat Detail →", "See Detail →"), use_container_width=True):
                st.session_state.nav = "news"
                st.session_state.scroll_to_top = True
                st.rerun()
    else:
        left, right = st.columns([0.28, 1], gap="small")
        with left:
            if st.button(t(lang, "← Kembali", "← Back"), use_container_width=True):
                st.session_state.nav = "analysis"
                st.session_state.scroll_to_top = True
                st.rerun()


def scroll_to_top() -> None:
    components.html(
        """
        <script>
        (function () {
          const run = () => {
            try {
              const target = window.parent || window;
              target.scrollTo({ top: 0, left: 0, behavior: 'instant' });
            } catch (err) {
              try {
                (window.parent || window).scrollTo(0, 0);
              } catch (_) {}
            }
          };
          if (document.readyState === 'complete') {
            setTimeout(run, 50);
          } else {
            window.addEventListener('load', () => setTimeout(run, 50), { once: true });
          }
        })();
        </script>
        """,
        height=0,
    )


def recover_sidebar() -> None:
    components.html(
        """
        <script>
        (function () {
          const tryOpen = () => {
            try {
              const root = window.parent && window.parent.document;
              if (!root) return false;
              const sidebar = root.querySelector('section.stSidebar, section[data-testid="stSidebar"]');
              const control = root.querySelector('header [data-testid="collapsedControl"], [data-testid="collapsedControl"]');
              if (!sidebar || !control) return false;
              const expanded = sidebar.getAttribute('aria-expanded');
              if (expanded === 'false') {
                control.click();
                return true;
              }
              return false;
            } catch (err) {
              return false;
            }
          };

          const run = () => {
            let tries = 0;
            const timer = setInterval(() => {
              tries += 1;
              if (tryOpen() || tries >= 12) clearInterval(timer);
            }, 150);
          };

          if (document.readyState === 'complete') {
            run();
          } else {
            window.addEventListener('load', run, { once: true });
          }
        })();
        </script>
        """,
        height=0,
    )


def main() -> None:
    st.set_page_config(page_title="kabar.io Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.session_state.setdefault("nav", "analysis")
    st.session_state.setdefault("lang", "id")
    st.session_state.setdefault("dark", False)
    st.session_state.setdefault("sent_f", "all")
    st.session_state.setdefault("cat_f", "all")
    st.session_state.setdefault("source_f", "all")
    st.session_state.setdefault("dr", "14d")
    st.session_state.setdefault("search", "")

    st.markdown(page_css(), unsafe_allow_html=True)

    if st.session_state.nav not in {"analysis", "news"}:
        st.session_state.nav = "analysis"

    raw_df, source_name, source_note, refresh_at = load_dashboard_snapshot()
    st.session_state.latest_refresh_at = refresh_at
    source_options = build_source_options(raw_df)

    lang, dark = sidebar_controls(source_name, source_note, refresh_at)
    nav = st.session_state.nav
    topbar(nav, lang)
    refresh_strip(refresh_at)
    st.markdown('<div class="topbar-divider"></div>', unsafe_allow_html=True)
    dr, sent_f, cat_f, source_f, search = main_filters(False, source_options)
    recover_sidebar()

    st.session_state.nav = nav
    st.session_state.lang = lang
    st.session_state.sent_f = sent_f
    st.session_state.cat_f = cat_f
    st.session_state.source_f = source_f
    st.session_state.dr = dr
    st.session_state.dark = dark

    if dark:
        st.markdown(
            """
            <style>
              html, body, [class*="stApp"] { background: #0f0d0b; color: #f0ede8; }
              .topbar { background: rgba(18,16,14,0.98); border-bottom-color: #2a2622; }
              .page-title, .panel .kpi-value, .panel .card-title { color: #f0ede8; }
              .refresh-meta, .kpi-note, .muted, .card-subtitle, .news-table th, .news-table td { color: #8c8278 !important; }
              .panel, .export-btn { background: #1a1714; border-color: #2a2622; }
              .bar-track, .subtle-rule, .news-table thead tr, .news-table td { border-color: #2a2622; }
              .news-table td { border-bottom-color: #2a2622; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    chart_df, table_df = filter_articles(raw_df, dr, source_f, sent_f, cat_f, search if nav == "news" else "")
    stats = build_stats(chart_df, lang)
    render_page(nav, lang, stats, dr, table_df)
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    page_navigation(nav)
    if st.session_state.pop("scroll_to_top", False):
        scroll_to_top()


if __name__ == "__main__":
    main()
