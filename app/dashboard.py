from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

try:
    from .data import load_dashboard_data, filter_articles, build_stats
    from .render import page_css, render_page
except ImportError:  # pragma: no cover - script-style fallback
    from data import load_dashboard_data, filter_articles, build_stats
    from render import page_css, render_page


def sidebar_controls(source_name: str, source_note: str) -> tuple[str, str, str, str, str, bool]:
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
        st.markdown('<div class="sidebar-section-title">Filter</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-label">Rentang Waktu</div>', unsafe_allow_html=True)
        dr = st.radio(
            "Date range",
            ["7d", "14d", "30d", "90d"],
            index=["7d", "14d", "30d", "90d"].index(st.session_state.dr),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.markdown('<div class="sidebar-label" style="margin-top:8px">Sentimen</div>', unsafe_allow_html=True)
        sent_f = st.radio(
            "Sentiment",
            ["all", "positive", "negative", "neutral"],
            index=["all", "positive", "negative", "neutral"].index(st.session_state.sent_f),
            horizontal=True,
            label_visibility="collapsed",
            format_func=lambda value: {"all": "Semua", "positive": "Positif", "negative": "Negatif", "neutral": "Netral"}[value],
        )
        search = st.text_input("Search", value=st.session_state.search, placeholder="Cari judul...")

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
        st.markdown(
            f"""
            <div class="status-box">
              <div class="status-row"><div class="pulse"></div><span style="font-size:11px;color:#9e9589;font-weight:500">Pipeline active</span></div>
              <div style="font-size:10px;color:#3d3028">Data: <span style="color:#5c5048">{source_name}</span></div>
              <div style="font-size:10px;color:#5c5048">Note: {source_note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return nav, lang, "all" if sent_f == "all" else sent_f, dr, search, dark


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

    raw_df, source_name, source_note = load_dashboard_data()
    nav, lang, sent_f, dr, search, dark = sidebar_controls(source_name, source_note)
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
              .page-subtitle, .kpi-note, .muted, .card-subtitle, .news-table th, .news-table td { color: #8c8278 !important; }
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
