from __future__ import annotations


BASE_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
  :root {
    --font-body: system-ui, -apple-system, "Segoe UI", Helvetica, sans-serif;
    --font-display: "Playfair Display", Georgia, serif;
    --text-main: #2d2a25;
    --text-muted: #665d52;
    --text-soft: #75695d;
    --focus-ring: rgba(204,34,0,0.28);
  }
  html, body, [class*="stApp"] { background: #f5f2ec; color: var(--text-main); }
  .stApp { font-family: var(--font-body); }
  #MainMenu, footer { display: none; }
  header {
    visibility: visible;
    height: auto;
    min-height: 0;
    background: transparent;
    border: 0;
  }
  header [data-testid="stToolbar"] { display: block; }
  header [data-testid="collapsedControl"] {
    top: 14px;
    left: 14px;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 1;
    pointer-events: auto;
  }
  [data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 0;
    padding-left: 0;
    padding-right: 0;
    max-width: none;
  }
  .stHorizontalBlock {
    padding-left: 28px;
    padding-right: 28px;
    box-sizing: border-box;
  }
  section[data-testid="stSidebar"] {
    background: #1e1a14;
    border-right: 1px solid rgba(255,255,255,0.06);
  }
  section[data-testid="stSidebar"] > div { padding-top: 0; }
  section[data-testid="stSidebar"] * { color: #9e9589; }
  section[data-testid="stSidebar"] [data-testid="stRadio"] { margin-top: 2px; }
  section[data-testid="stSidebar"] [role="radiogroup"] { gap: 2px; }
  section[data-testid="stSidebar"] [role="radiogroup"] label {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1px 10px;
    padding: 9px 16px;
    border-radius: 5px;
    border: 1px solid transparent;
    background: transparent;
    transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease, transform 120ms ease;
  }
  section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.03);
    border-color: rgba(255,255,255,0.05);
  }
  section[data-testid="stSidebar"] [role="radiogroup"] label:has(input[type="radio"]:checked) {
    background: rgba(204,34,0,0.18);
    border-color: rgba(204,34,0,0.28);
    color: #f0ede8;
    box-shadow: inset 0 0 0 1px rgba(204,34,0,0.08);
    transform: translateX(0.5px);
  }
  section[data-testid="stSidebar"] [role="radiogroup"] label:has(input[type="radio"]:checked) span {
    color: #f0ede8 !important;
    font-weight: 600 !important;
  }
  section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
    margin-right: 2px;
  }
  .topbar {
    position: sticky; top: 0; z-index: 10;
    padding: 8px 28px 0;
    background: rgba(245,242,236,0.96);
    backdrop-filter: blur(8px);
  }
  .topbar-inner { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding: 0 0 4px; }
  .topbar-copy { display: flex; flex-direction: column; gap: 2px; }
  .page-title {
    margin: 0; font-family: var(--font-display); font-size: 22px; font-weight: 700; line-height: 1.08;
    color: #2d2a25; letter-spacing: -0.3px;
  }
  .topbar-divider {
    height: 1px;
    background: linear-gradient(90deg, #e8e0d4 0%, rgba(232,224,212,0.2) 100%);
    margin: 0 0 2px;
  }
  .refresh-strip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 0;
    margin: 0 0 2px;
  }
  .refresh-meta {
    margin: 0;
    font-size: 11px;
    color: var(--text-soft);
    line-height: 1.25;
    letter-spacing: 0.01em;
  }
  .panel {
    background: #ffffff; border: 1px solid #e8e0d4; border-radius: 8px; padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(44, 28, 12, 0.06);
    transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease, background-color 140ms ease;
  }
  .panel.compact { padding: 16px 18px; }
  .panel:hover {
    transform: translateY(-2px);
    border-color: #dbcdbc;
    box-shadow: 0 8px 22px rgba(44, 28, 12, 0.10);
  }
  .panel:focus-within {
    border-color: rgba(204,34,0,0.24);
    box-shadow: 0 0 0 3px rgba(204,34,0,0.08), 0 6px 18px rgba(44, 28, 12, 0.08);
  }
  .panel.compact:hover {
    transform: translateY(-1px);
  }
  .card-title { font-size: 13px; font-weight: 600; color: #2d2a25; margin: 0 0 12px; letter-spacing: -0.2px; }
  .card-subtitle { font-size: 12.5px; color: var(--text-soft); margin: 0 0 12px; line-height: 1.45; }
  .kpi-label {
    font-size: 11px; font-weight: 700; color: #5f564d; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px;
  }
  .kpi-value {
    font-family: var(--font-display); font-size: 32px; font-weight: 700; line-height: 1; color: #2d2a25; margin-bottom: 4px;
  }
  .kpi-note { font-size: 12px; color: var(--text-soft); line-height: 1.45; }
  .metric-positive { color: #2d7a3a; }
  .metric-negative { color: #cc2200; }
  .legend-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 8px; }
  .legend-item { display: flex; align-items: center; gap: 7px; font-size: 12.3px; color: var(--text-soft); }
  .legend-swatch { width: 9px; height: 9px; border-radius: 2px; display: inline-block; flex: 0 0 auto; }
  .bar-track { height: 8px; background: #e8e0d4; border-radius: 4px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; }
  .subtle-rule { border-top: 1px solid #e8e0d4; margin-top: 12px; padding-top: 12px; }
  .word-cloud-circle {
    position: relative;
    width: 100%;
    min-height: 300px;
    max-height: 340px;
    aspect-ratio: 1 / 1;
    overflow: hidden;
    border-radius: 50%;
    background:
      radial-gradient(circle at center, rgba(255,255,255,0.92) 0%, rgba(255,255,255,0.86) 42%, rgba(245,242,236,0.65) 72%, rgba(245,242,236,0.25) 100%);
  }
  .word-cloud-item {
    position: absolute;
  }
  .word-cloud-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    white-space: nowrap;
    font-family: var(--font-display);
    line-height: 1;
    letter-spacing: -0.01em;
    transform-origin: center;
    border-radius: 999px;
    padding: 3px 10px;
    background: rgba(255,255,255,0.7);
    border: 1px solid rgba(0,0,0,0.04);
    box-shadow: 0 1px 2px rgba(44,28,12,0.05);
    opacity: var(--chip-opacity, 0.9);
    animation-name: word-cloud-float;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
    will-change: transform;
    transition: filter 140ms ease, box-shadow 140ms ease, border-color 140ms ease, background-color 140ms ease;
    cursor: default;
  }
  .word-cloud-chip:hover {
    animation-play-state: paused;
    border-color: rgba(204,34,0,0.20);
    box-shadow: 0 8px 18px rgba(44,28,12,0.12);
    background: rgba(255,255,255,0.92);
    filter: saturate(1.05);
  }
  @keyframes word-cloud-float {
    0%, 100% { transform: translateY(0) rotate(-1.5deg); }
    50% { transform: translateY(-4px) rotate(1.5deg); }
  }
  .table-wrap { overflow-x: auto; }
  table.news-table { width: 100%; border-collapse: collapse; min-width: 580px; }
  .news-table thead tr { border-bottom: 2px solid #e8e0d4; }
  .news-table tbody tr { transition: background-color 120ms ease, transform 120ms ease; }
  .news-table tbody tr:hover { background: rgba(245, 242, 236, 0.8); }
  .news-table tbody tr:hover td { color: #2d2a25; }
  .news-table th {
    padding: 10px 12px 9px; text-align: left; font-size: 10px; font-weight: 700; color: var(--text-soft);
    text-transform: uppercase; letter-spacing: 0.07em; white-space: nowrap;
  }
  .news-table td { padding: 10px 12px; font-size: 12px; vertical-align: top; border-bottom: 1px solid #e8e0d4; color: var(--text-soft); }
  .news-table td .news-line { line-height: 1.35; }
  .news-table td .news-reason { color: #4f473e; }
  .news-table td .news-note { color: #786f62; font-size: 11px; margin-top: 3px; }
  .news-toolbar { display: grid; grid-template-columns: 1.4fr 0.62fr 0.62fr 0.45fr; gap: 10px; margin: 0 0 12px; align-items: end; }
  .news-toolbar .toolbar-block { display: flex; flex-direction: column; gap: 6px; }
  .news-toolbar .toolbar-label { margin: 0; }
  .news-pagination {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-top: 10px;
  }
  .news-page-meta { font-size: 11.5px; color: var(--text-soft); }
  .news-page-controls { display: flex; align-items: center; gap: 8px; }
  .news-page-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    background: #f2ede8;
    color: #786f62;
    font-size: 11.5px;
    font-weight: 600;
  }
  .news-pill {
    display: inline-block; padding: 2px 9px; border-radius: 11px; font-size: 11px; font-weight: 600;
  }
  .pill-positive { background: #edf7ef; color: #2d7a3a; }
  .pill-negative { background: #fdf0ee; color: #cc2200; }
  .pill-neutral { background: #f2ede8; color: #786f62; }
  .pill-unknown { background: #f3efe9; color: #8c8278; border: 1px dashed #d3c8bc; }
  .sidebar-brand { padding: 22px 20px 18px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  .sidebar-logo {
    font-family: var(--font-display); font-size: 22px; font-weight: 700; color: #f0ede8;
    letter-spacing: -0.5px; line-height: 1;
  }
  .sidebar-logo .accent { color: #cc2200; }
  .sidebar-subtitle { font-size: 10.5px; color: #3d3028; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.07em; }
  .sidebar-section-title {
    font-size: 10px; font-weight: 700; color: #3a2f27; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 14px;
  }
  .sidebar-label { font-size: 11px; color: #5c5048; margin-bottom: 7px; font-weight: 500; }
  .status-box {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 9px 11px;
  }
  .status-row { display: flex; align-items: center; gap: 6px; margin-bottom: 3px; }
  .pulse { width: 6px; height: 6px; border-radius: 50%; background: #2d7a3a; animation: pulse 2.5s infinite; flex-shrink: 0; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
  .grid-2-1 { display: grid; grid-template-columns: 295px minmax(0, 1fr); gap: 14px; }
  .grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
  .grid-4-small { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
  .muted { color: var(--text-soft); }
  .section-pad { padding: 16px 28px 20px; }
  .section-tight { padding-top: 4px; }
  .analysis-section {
    margin: 0 0 12px;
  }
  .analysis-section-title {
    font-family: var(--font-display);
    font-size: 17px;
    font-weight: 700;
    line-height: 1.1;
    color: #2d2a25;
    letter-spacing: -0.25px;
    margin: 0 0 4px;
  }
  .analysis-section-subtitle {
    font-size: 12.5px;
    line-height: 1.45;
    color: var(--text-soft);
    margin: 0;
  }
  .toolbar-label {
    font-size: 11px;
    font-weight: 700;
    color: #5f564d;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 6px;
  }
  .stButton button {
    border-radius: 10px;
    padding: 0.34rem 0.9rem;
    min-height: 2.1rem;
    font-size: 0.82rem;
    line-height: 1;
    border: 1px solid #e4dbd0;
    background: linear-gradient(180deg, #fbf8f3 0%, #f6f1e9 100%);
    color: #5f564d;
    box-shadow: 0 1px 2px rgba(44,28,12,0.04);
    font-weight: 650;
    letter-spacing: 0.01em;
  }
  .stButton button:hover {
    background: linear-gradient(180deg, #f8f3ec 0%, #f2ece3 100%);
    border-color: #d8cdc1;
    color: #4f473e;
    box-shadow: 0 6px 14px rgba(44,28,12,0.08);
    transform: translateY(-1px) translateX(1px);
  }
  .nav-footer { height: 14px; }
  .gauge-wrap { display: flex; align-items: center; justify-content: center; }
  .bar-caption { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 6px; font-size: 12.5px; }
  .chip {
    display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 10px;
    background: #e8e0d4; color: var(--text-muted); font-size: 12px; font-weight: 500;
    transition: transform 120ms ease, background-color 120ms ease, color 120ms ease, box-shadow 120ms ease;
    cursor: default;
  }
  .chip:hover {
    transform: translateY(-1px);
    background: #ddd3c4;
    color: #514a41;
    box-shadow: 0 4px 12px rgba(44, 28, 12, 0.08);
  }
  .live-badge, .export-btn {
    transition: transform 120ms ease, box-shadow 120ms ease, background-color 120ms ease, border-color 120ms ease, color 120ms ease;
  }
  .live-badge:hover, .export-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(44, 28, 12, 0.08);
  }
  .export-btn:hover {
    background: #faf7f2;
    border-color: #d8cdc1;
    color: #5f564d;
  }
  .stRadio > div { gap: 4px; }
  .stRadio label { font-size: 13px; }
  section[data-testid="stSidebar"] [role="radiogroup"] label:focus-within {
    outline: 2px solid rgba(204,34,0,0.22);
    outline-offset: 1px;
  }
  .stButton button,
  .stTextInput input,
  .stNumberInput input,
  .stSelectbox [role="combobox"],
  .stMultiSelect [role="combobox"],
  .stRadio input,
  .stToggle button {
    transition: box-shadow 120ms ease, border-color 120ms ease, transform 120ms ease, background-color 120ms ease;
  }
  .stButton button:focus-visible,
  .stTextInput input:focus-visible,
  .stNumberInput input:focus-visible,
  .stSelectbox [role="combobox"]:focus-visible,
  .stMultiSelect [role="combobox"]:focus-visible,
  .stToggle button:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px var(--focus-ring);
  }
  .stButton button {
    position: relative;
  }
  .stButton button::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 10px;
    pointer-events: none;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.0) 45%, rgba(255,255,255,0.20) 50%, rgba(255,255,255,0.0) 55%, transparent 100%);
    transform: translateX(-120%);
    opacity: 0;
  }
  .stButton button:hover::after {
    opacity: 1;
    animation: nav-sheen 900ms ease-out 1;
  }
  @keyframes nav-sheen {
    from { transform: translateX(-120%); }
    to { transform: translateX(120%); }
  }
</style>
"""
