from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components

try:
    from .data import clear_dashboard_snapshot_cache, filter_articles, build_stats, load_dashboard_snapshot, esc
    from .render import page_css, render_page, topbar
except ImportError:  # pragma: no cover - script-style fallback
    from data import clear_dashboard_snapshot_cache, filter_articles, build_stats, load_dashboard_snapshot, esc
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


def sidebar_controls(source_name: str, source_note: str, refresh_at: str | None) -> tuple[str, str, bool]:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
              <div class="sidebar-logo">kabar<span class="accent">.io</span></div>
              <div class="sidebar-subtitle">Indonesian News Monitor</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="status-box" style="margin-bottom:12px">
              <div class="status-row"><div class="pulse"></div><span style="font-size:11px;color:#9e9589;font-weight:500">Pipeline active</span></div>
              <div style="font-size:10px;color:#3d3028">Data: <span style="color:#5c5048">{esc(source_name)}</span></div>
              <div style="font-size:10px;color:#5c5048">Note: {esc(source_note)}</div>
              <div style="font-size:10px;color:#5c5048">Latest refresh: {esc(format_refresh_label(refresh_at))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav = st.radio(
            "Navigation",
            ["overview", "sentiment", "category", "source", "news"],
            index=["overview", "sentiment", "category", "source", "news"].index(st.session_state.nav),
            format_func=lambda value: {
                "overview": "Ringkasan",
                "sentiment": "Sentimen",
                "category": "Kategori",
                "source": "Sumber",
                "news": "Berita",
            }[value],
            label_visibility="collapsed",
        )

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        lang = st.radio(
            "Language",
            ["id", "en"],
            index=["id", "en"].index(st.session_state.lang),
            horizontal=True,
            label_visibility="collapsed",
            format_func=lambda value: value.upper(),
        )
        dark = st.toggle("Dark", value=st.session_state.dark)

    return nav, lang, dark


def refresh_strip(refresh_at: str | None) -> None:
    left, right = st.columns([1, 0.12], gap="small")
    with left:
        st.markdown(
            f'<div class="refresh-strip"><p class="refresh-meta">Last refresh: {esc(format_refresh_label(refresh_at))}</p></div>',
            unsafe_allow_html=True,
        )
    with right:
        if st.button("Refresh", use_container_width=True):
            clear_dashboard_snapshot_cache()
            st.session_state.latest_refresh_at = None
            st.rerun()


def main_filters() -> tuple[str, str, str]:
    cols = st.columns(3, gap="small")
    dr_options = ["7d", "14d", "30d", "90d"]
    sent_options = ["all", "positive", "negative", "neutral"]

    with cols[0]:
        st.markdown('<div class="toolbar-label">Rentang Waktu</div>', unsafe_allow_html=True)
        dr = st.selectbox("", dr_options, index=dr_options.index(st.session_state.dr), label_visibility="collapsed", key="main_dr")
    with cols[1]:
        st.markdown('<div class="toolbar-label">Sentimen</div>', unsafe_allow_html=True)
        sent_f = st.selectbox(
            "",
            sent_options,
            index=sent_options.index(st.session_state.sent_f),
            label_visibility="collapsed",
            key="main_sentiment",
            format_func=lambda value: {"all": "Semua", "positive": "Positif", "negative": "Negatif", "neutral": "Netral"}[value],
        )
    with cols[2]:
        st.markdown('<div class="toolbar-label">Pencarian</div>', unsafe_allow_html=True)
        search = st.text_input("", value=st.session_state.search, placeholder="Cari judul atau sumber...", label_visibility="collapsed", key="main_search")

    return dr, "all" if sent_f == "all" else sent_f, search


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
    st.session_state.setdefault("nav", "overview")
    st.session_state.setdefault("lang", "id")
    st.session_state.setdefault("dark", False)
    st.session_state.setdefault("sent_f", "all")
    st.session_state.setdefault("dr", "14d")
    st.session_state.setdefault("search", "")

    st.markdown(page_css(), unsafe_allow_html=True)

    raw_df, source_name, source_note, refresh_at = load_dashboard_snapshot()
    st.session_state.latest_refresh_at = refresh_at

    nav, lang, dark = sidebar_controls(source_name, source_note, refresh_at)
    topbar(nav, lang)
    refresh_strip(refresh_at)
    st.markdown('<div class="topbar-divider"></div>', unsafe_allow_html=True)
    dr, sent_f, search = main_filters()
    recover_sidebar()

    st.session_state.nav = nav
    st.session_state.lang = lang
    st.session_state.sent_f = sent_f
    st.session_state.dr = dr
    st.session_state.search = search
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

    chart_df, table_df = filter_articles(raw_df, dr, sent_f, search)
    stats = build_stats(chart_df, lang)
    render_page(nav, lang, stats, dr, table_df)


if __name__ == "__main__":
    main()
