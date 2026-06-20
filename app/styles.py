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
    --chart-text: #2d2a25;
    --chart-muted: #786f62;
    --chart-grid: #e8e0d4;
    --chart-track: #e8e0d4;
    --chart-positive: #2d7a3a;
    --chart-negative: #cc2200;
    --chart-neutral: #b09580;
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
  div[data-testid="stHorizontalBlock"]:has(button[data-testid="stPopoverButton"]):has(div[data-testid="stTextInput"]) {
    gap: 0.45rem !important;
    align-items: flex-start;
    margin-bottom: 2px;
  }
  div[data-testid="stHorizontalBlock"]:has(button[data-testid="stPopoverButton"]):has(div[data-testid="stTextInput"]) > div {
    padding-top: 0 !important;
  }
  section[data-testid="stSidebar"] {
    background: #1e1a14;
    border-right: 1px solid rgba(255,255,255,0.06);
  }
  section[data-testid="stSidebar"] > div { padding-top: 0; }
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
  .news-page-meta { font-size: 11.5px; color: var(--text-soft); }
  .news-table-scroll {
    max-height: min(70vh, 720px);
    overflow: auto;
    border-radius: 8px;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    margin: 0;
  }
  .news-table-empty {
    padding: 2px 0 0;
    font-size: 12.5px;
    line-height: 1.45;
    color: var(--text-soft);
  }
  .news-grid-table {
    width: 100%;
    min-width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    table-layout: auto;
  }
  .news-grid-table thead th {
    position: sticky;
    top: 0;
    z-index: 3;
    padding: 11px 12px 10px;
    border-bottom: 1px solid #d9cfc3;
    background: linear-gradient(180deg, rgba(248,244,239,0.99), rgba(243,238,231,0.99));
    color: #3f372e;
    text-align: left;
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    white-space: nowrap;
    box-shadow: 0 1px 0 rgba(255,255,255,0.6) inset;
  }
  .news-th-label {
    display: inline-block;
    font-weight: 800;
    color: #3f372e;
  }
  .news-grid-table tbody tr {
    transition: background-color 120ms ease, transform 120ms ease;
  }
  .news-grid-table tbody tr:nth-child(odd) td {
    background: rgba(250,247,242,0.62);
  }
  .news-grid-table tbody tr:hover {
    background: rgba(245, 242, 236, 0.72);
  }
  .news-grid-table td {
    padding: 11px 12px;
    border-bottom: 1px solid #e8e0d4;
    color: var(--text-soft);
    font-size: 11px;
    vertical-align: top;
  }
  .news-grid-table tbody tr:last-child td {
    border-bottom: 0;
  }
  .cell-title {
    max-width: 260px;
    color: #2d2a25;
    line-height: 1.34;
    font-weight: 600;
  }
  .cell-meta {
    color: #786f62;
    white-space: nowrap;
  }
  .cell-reason {
    max-width: 220px;
    color: #4f473e;
    line-height: 1.38;
  }
  .cell-error {
    max-width: 170px;
    color: #8c8278;
    line-height: 1.34;
  }
  .news-pill {
    display: inline-block; padding: 2px 9px; border-radius: 11px; font-size: 11px; font-weight: 600;
  }
  .news-sort-level {
    margin: 0 0 8px;
    padding: 3px 5px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8c8278;
    background: rgba(45, 42, 37, 0.05);
    border-radius: 3px;
    display: inline-block;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) div[data-testid="stHorizontalBlock"] {
    gap: 0.3rem !important;
    margin-bottom: 2px !important;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) [data-testid="stButton"] button {
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.34rem 0.5rem;
    min-height: 2.5rem;
    height: 2.5rem;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox [role="combobox"] {
    min-height: 2.5rem;
    height: 2.5rem;
  }
  .pill-positive { background: #edf7ef; color: #2d7a3a; }
  .pill-negative { background: #fdf0ee; color: #cc2200; }
  .pill-neutral { background: #f2ede8; color: #786f62; }
  .pill-unknown { background: #f3efe9; color: #8c8278; border: 1px dashed #d3c8bc; }
  @media (max-width: 900px) {
    .section-pad { padding: 14px 18px 18px; }
    .news-grid-table thead th { padding: 9px 8px 8px; font-size: 10px; }
    .news-grid-table { min-width: 100%; }
    .news-grid-table td { padding: 10px 10px; font-size: 10.5px; }
    .cell-title { max-width: 200px; }
    .cell-reason { max-width: 180px; }
    .cell-error { max-width: 150px; }
  }
  @media (max-width: 640px) {
    .news-grid-table thead th { padding: 8px 8px 7px; }
    .news-grid-table { min-width: 100%; }
    .news-grid-table td { padding: 8px 8px; }
    .news-pill { padding: 2px 7px; font-size: 10.5px; }
    .news-source-link { width: 100%; justify-content: center; }
  }
  @media (max-width: 768px) {
    .stHorizontalBlock {
      padding-left: 16px;
      padding-right: 16px;
    }
    div[data-testid="stHorizontalBlock"]:has(.toolbar-label) {
      flex-direction: column;
      gap: 0.45rem !important;
      align-items: stretch;
    }
    div[data-testid="stHorizontalBlock"]:has(.toolbar-label) > div {
      width: 100% !important;
      padding-top: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.toolbar-label) button[data-testid="stPopoverButton"],
    div[data-testid="stHorizontalBlock"]:has(.toolbar-label) .stTextInput input,
    div[data-testid="stHorizontalBlock"]:has(.toolbar-label) .stSelectbox [data-baseweb="select"],
    div[data-testid="stHorizontalBlock"]:has(.toolbar-label) .stSelectbox [role="combobox"] {
      min-height: 2.8rem;
      height: 2.8rem;
      width: 100%;
    }
    div[data-testid="stPopover"] > div:last-child,
    div[data-testid="stPopover"]:has(.news-columns-popover) > div:last-child,
    div[data-testid="stPopover"]:has(.news-sort-popover) > div:last-child {
      min-width: calc(100vw - 24px) !important;
      width: calc(100vw - 24px) !important;
    }
    div[data-testid="stPopover"]:has(.news-sort-popover) .stColumns {
      gap: 0.55rem;
    }
  }
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
  .sidebar-status-box { margin-bottom: 12px; }
  .status-row { display: flex; align-items: center; gap: 6px; margin-bottom: 3px; }
  .sidebar-status-title { font-size: 11px; color: #9e9589; font-weight: 500; }
  .sidebar-status-line { font-size: 10px; color: #5c5048; line-height: 1.35; }
  .sidebar-status-label { color: #3d3028; }
  .sidebar-status-value { color: #5c5048; }
  .chart-shell {
    color: var(--chart-text);
  }
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
  .stButton button,
  .stPopover button,
  button[data-testid="stPopoverButton"],
  button[kind="secondary"] {
    border-radius: 10px;
    padding: 0.34rem 0.9rem;
    min-height: 2.1rem;
    font-size: 0.82rem;
    line-height: 1;
    border: 1px solid #dcd3c8;
    background: #ffffff;
    color: #4f473e;
    box-shadow: 0 1px 2px rgba(44,28,12,0.03);
    font-weight: 650;
    letter-spacing: 0.01em;
  }
  .stButton button:hover,
  .stPopover button:hover,
  button[data-testid="stPopoverButton"]:hover,
  button[kind="secondary"]:hover {
    background: #ffffff;
    border-color: #cfc5b8;
    color: #2d2a25;
    box-shadow: 0 6px 14px rgba(44,28,12,0.06);
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
  .stPopover button,
  button[data-testid="stPopoverButton"],
  button[kind="secondary"],
  .stTextInput input,
  .stNumberInput input,
  .stSelectbox [role="combobox"],
  .stMultiSelect [role="combobox"],
  .stRadio input,
  .stToggle button {
    transition: box-shadow 120ms ease, border-color 120ms ease, transform 120ms ease, background-color 120ms ease;
  }
  .stButton button:focus-visible,
  .stPopover button:focus-visible,
  button[data-testid="stPopoverButton"]:focus-visible,
  button[kind="secondary"]:focus-visible,
  .stTextInput input:focus-visible,
  .stNumberInput input:focus-visible,
  .stSelectbox [role="combobox"]:focus-visible,
  .stMultiSelect [role="combobox"]:focus-visible,
  .stToggle button:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px var(--focus-ring);
  }
  .stButton button,
  .stPopover button,
  button[data-testid="stPopoverButton"],
  button[kind="secondary"] {
    position: relative;
  }
  .stButton button::after,
  .stPopover button::after,
  button[data-testid="stPopoverButton"]::after,
  button[kind="secondary"]::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 10px;
    pointer-events: none;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.0) 45%, rgba(255,255,255,0.20) 50%, rgba(255,255,255,0.0) 55%, transparent 100%);
    transform: translateX(-120%);
    opacity: 0;
  }
  .stButton button:hover::after,
  .stPopover button:hover::after,
  button[data-testid="stPopoverButton"]:hover::after,
  button[kind="secondary"]:hover::after {
    opacity: 1;
    animation: nav-sheen 900ms ease-out 1;
  }
  button[data-testid="stPopoverButton"] {
    background: #2d2a25;
    border: 1px solid #403930;
    color: #f3efe9;
    box-shadow: 0 1px 2px rgba(17,13,9,0.22);
    width: 100%;
    height: 2.5rem;
    min-width: 0;
    max-width: 100%;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    justify-content: space-between;
    gap: 0.35rem;
  }
  button[data-testid="stPopoverButton"]:hover {
    background: #3a342d;
    border-color: #4d453c;
    color: #ffffff;
    box-shadow: 0 6px 14px rgba(17,13,9,0.24);
    transform: translateY(-1px) translateX(1px);
  }
  button[data-testid="stPopoverButton"] > div {
    width: 100%;
    min-width: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.35rem;
  }
  button[data-testid="stPopoverButton"] p,
  button[data-testid="stPopoverButton"] span,
  button[data-testid="stPopoverButton"] svg {
    color: currentColor;
    fill: currentColor;
    flex-shrink: 0;
  }
  button[data-testid="stPopoverButton"] svg {
    opacity: 0.95;
  }
  button[data-testid="stPopoverButton"] p {
    margin: 0;
    white-space: nowrap;
  }
  div[data-testid="stPopover"] > div:last-child {
    min-width: 520px !important;
    width: min(820px, 88vw) !important;
  }
  div[data-testid="stPopover"]:has(.news-columns-popover) > div:last-child {
    min-width: 520px !important;
    width: min(820px, 88vw) !important;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) > div:last-child {
    min-width: 1000px !important;
    width: min(1400px, 95vw) !important;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox [role="combobox"],
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox,
  div[data-testid="stPopover"]:has(.news-sort-popover) .stButton button {
    width: 100%;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox,
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox [data-baseweb="select"],
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox [data-baseweb="select"] > div {
    min-width: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .stColumns {
    gap: 0.9rem;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .news-sort-level {
    margin-top: 12px;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox [role="combobox"] {
    min-height: 2.55rem;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .stSelectbox [data-baseweb="select"] {
    min-height: 2.55rem;
  }
  div[data-testid="stPopover"]:has(.news-sort-popover) .stCaption,
  div[data-testid="stPopover"]:has(.news-columns-popover) .stCaption {
    white-space: normal;
    line-height: 1.45;
  }
  @media (max-width: 768px) {
  }
  div[data-testid="stTextInput"] {
    margin-top: 0;
  }
  div[data-testid="stTextInput"] input {
    height: 2.5rem;
    min-height: 2.5rem;
    padding-top: 0.34rem;
    padding-bottom: 0.34rem;
    box-sizing: border-box;
  }
  div[data-testid="stTextInput"] input::placeholder {
    color: #8a8075;
    opacity: 1;
  }
  @keyframes nav-sheen {
    from { transform: translateX(-120%); }
    to { transform: translateX(120%); }
  }
</style>
"""
