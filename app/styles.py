from __future__ import annotations


BASE_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
  html, body, [class*="stApp"] { background: #f5f2ec; color: #2d2a25; }
  .stApp { font-family: system-ui, -apple-system, "Segoe UI", Helvetica, sans-serif; }
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
    padding: 18px 28px 16px;
    border-bottom: 1px solid #e8e0d4;
    background: rgba(250, 248, 244, 0.98);
    backdrop-filter: blur(8px);
  }
  .topbar-inner { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  .page-title {
    margin: 0; font-family: "Playfair Display", Georgia, serif; font-size: 20px; font-weight: 700; line-height: 1.2;
    color: #2d2a25; letter-spacing: -0.3px;
  }
  .page-subtitle { margin: 3px 0 0; font-size: 12px; color: #786f62; }
  .live-badge, .export-btn {
    display: inline-flex; align-items: center; gap: 6px; border-radius: 6px;
    padding: 5px 12px; font-size: 12px; font-weight: 600; line-height: 1; white-space: nowrap;
  }
  .live-badge { background: #edf7ef; color: #2d7a3a; border: 1px solid #c4e6c9; }
  .export-btn { background: #ffffff; color: #786f62; border: 1px solid #e8e0d4; }
  .panel {
    background: #ffffff; border: 1px solid #e8e0d4; border-radius: 8px; padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(44, 28, 12, 0.06);
  }
  .panel.compact { padding: 16px 18px; }
  .card-title { font-size: 13px; font-weight: 600; color: #2d2a25; margin: 0 0 14px; letter-spacing: -0.2px; }
  .card-subtitle { font-size: 11px; color: #786f62; margin: 0 0 14px; }
  .kpi-label {
    font-size: 10px; font-weight: 700; color: #786f62; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px;
  }
  .kpi-value {
    font-family: "Playfair Display", Georgia, serif; font-size: 32px; font-weight: 700; line-height: 1; color: #2d2a25; margin-bottom: 4px;
  }
  .kpi-note { font-size: 11px; color: #786f62; }
  .metric-positive { color: #2d7a3a; }
  .metric-negative { color: #cc2200; }
  .legend-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 10px; }
  .legend-item { display: flex; align-items: center; gap: 7px; font-size: 12px; color: #786f62; }
  .legend-swatch { width: 9px; height: 9px; border-radius: 2px; display: inline-block; flex: 0 0 auto; }
  .bar-track { height: 8px; background: #e8e0d4; border-radius: 4px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; }
  .subtle-rule { border-top: 1px solid #e8e0d4; margin-top: 10px; padding-top: 10px; }
  .word-cloud { display: flex; flex-wrap: wrap; gap: 5px 10px; line-height: 1.7; }
  .word-cloud span { font-family: Georgia, serif; opacity: 0.6; }
  .table-wrap { overflow-x: auto; }
  table.news-table { width: 100%; border-collapse: collapse; min-width: 580px; }
  .news-table thead tr { border-bottom: 2px solid #e8e0d4; }
  .news-table th {
    padding: 8px 12px; text-align: left; font-size: 10px; font-weight: 700; color: #786f62;
    text-transform: uppercase; letter-spacing: 0.07em; white-space: nowrap;
  }
  .news-table td { padding: 10px 12px; font-size: 12px; vertical-align: top; border-bottom: 1px solid #e8e0d4; }
  .news-pill {
    display: inline-block; padding: 2px 9px; border-radius: 11px; font-size: 11px; font-weight: 600;
  }
  .pill-positive { background: #edf7ef; color: #2d7a3a; }
  .pill-negative { background: #fdf0ee; color: #cc2200; }
  .pill-neutral { background: #f2ede8; color: #786f62; }
  .sidebar-brand { padding: 22px 20px 18px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  .sidebar-logo {
    font-family: "Playfair Display", Georgia, serif; font-size: 22px; font-weight: 700; color: #f0ede8;
    letter-spacing: -0.5px; line-height: 1;
  }
  .sidebar-logo .accent { color: #cc2200; }
  .sidebar-subtitle { font-size: 10px; color: #3d3028; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.07em; }
  .sidebar-section-title {
    font-size: 9px; font-weight: 700; color: #3a2f27; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 14px;
  }
  .sidebar-label { font-size: 10.5px; color: #5c5048; margin-bottom: 7px; font-weight: 500; }
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
  .muted { color: #786f62; }
  .section-pad { padding: 22px 28px 32px; }
  .gauge-wrap { display: flex; align-items: center; justify-content: center; }
  .bar-caption { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 6px; font-size: 12px; }
  .chip {
    display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 10px;
    background: #e8e0d4; color: #786f62; font-size: 11.5px; font-weight: 500;
  }
  .stRadio > div { gap: 4px; }
  .stRadio label { font-size: 13px; }
</style>
"""
