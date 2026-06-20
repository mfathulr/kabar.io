from __future__ import annotations

import math

try:
    from .data import esc
except ImportError:  # pragma: no cover - script-style fallback
    from data import esc


def svg_title(*lines: object) -> str:
    text = "\n".join(str(line) for line in lines if line is not None and str(line) != "")
    return f"<title>{esc(text)}</title>" if text else ""


def tr(lang: str, id_text: str, en_text: str) -> str:
    return id_text if lang == "id" else en_text


def mk_donut(sentiment_counts: dict[str, int], total: int, lang: str = "id") -> str:
    total = max(total, 1)
    pos = sentiment_counts.get("positive", 0)
    neg = sentiment_counts.get("negative", 0)
    neu = sentiment_counts.get("neutral", 0)
    c = 2 * math.pi * 32.25
    p_len = pos / total * c
    n_len = neg / total * c
    u_len = neu / total * c
    pos_pct = round((pos / total) * 100)
    neg_pct = round((neg / total) * 100)
    neu_pct = round((neu / total) * 100)
    donut_label = tr(lang, "Distribusi sentimen", "Sentiment distribution")
    return f"""
    <svg viewBox="0 0 100 100" style="width:100%;height:100%">
      {svg_title(donut_label, total, tr(lang, "Positif", "Positive"), f"{pos:,} ({pos_pct}%)", tr(lang, "Negatif", "Negative"), f"{neg:,} ({neg_pct}%)", tr(lang, "Netral", "Neutral"), f"{neu:,} ({neu_pct}%)")}
      <circle cx="50" cy="50" r="32.25" fill="none" stroke="var(--chart-track)" stroke-width="13">
        {svg_title(tr(lang, "Total", "Total"), total)}
      </circle>
      <circle cx="50" cy="50" r="32.25" fill="none" stroke="var(--chart-positive)" stroke-width="13" stroke-dasharray="{p_len} {c}" transform="rotate(-90 50 50)">
        {svg_title(tr(lang, "Positif", "Positive"), f"{pos:,}", f"{pos_pct}%")}
      </circle>
      <circle cx="50" cy="50" r="32.25" fill="none" stroke="var(--chart-negative)" stroke-width="13" stroke-dasharray="{n_len} {c}" stroke-dashoffset="-{p_len}" transform="rotate(-90 50 50)">
        {svg_title(tr(lang, "Negatif", "Negative"), f"{neg:,}", f"{neg_pct}%")}
      </circle>
      <circle cx="50" cy="50" r="32.25" fill="none" stroke="var(--chart-neutral)" stroke-width="13" stroke-dasharray="{u_len} {c}" stroke-dashoffset="-{p_len + n_len}" transform="rotate(-90 50 50)">
        {svg_title(tr(lang, "Netral", "Neutral"), f"{neu:,}", f"{neu_pct}%")}
      </circle>
      <text x="50" y="47" text-anchor="middle" font-size="10" font-weight="700" fill="var(--chart-text)" font-family="system-ui">{total:,}</text>
      <text x="50" y="56" text-anchor="middle" font-size="5.5" fill="var(--chart-muted)" font-family="system-ui">{'artikel' if lang == 'id' else 'articles'}</text>
    </svg>
    """


def mk_timeseries(rows: list[dict[str, object]], lang: str = "id") -> str:
    if not rows:
        rows = [{"d": "n/a", "t": 0, "p": 0, "n": 0}]
    w, h = 440, 160
    p_l, p_r, p_t, p_b = 28, 8, 8, 26
    c_w, c_h = w - p_l - p_r, h - p_t - p_b
    max_v = max(max(int(r["t"]), int(r["p"]), int(r["n"])) for r in rows) or 1

    def x(i: int) -> float:
        return p_l + (i / max(len(rows) - 1, 1)) * c_w

    def y(v: float) -> float:
        return p_t + c_h - (v / max_v) * c_h

    def path(key: str) -> str:
        return " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(int(row[key])):.1f}" for i, row in enumerate(rows))

    p_path = path("p")
    n_path = path("n")
    t_path = path("t")
    area = f"{p_path} L{x(len(rows)-1):.1f},{y(0):.1f} L{x(0):.1f},{y(0):.1f} Z"
    grid = []
    for v in [0, 25, 50, 75, 100]:
        grid.append(
            f'<g><line x1="{p_l}" y1="{y(v):.1f}" x2="{w-p_r}" y2="{y(v):.1f}" stroke="var(--chart-grid)" stroke-width="0.65"></line>'
            f'<text x="{p_l-4}" y="{y(v)+3:.1f}" text-anchor="end" font-size="5.8" fill="var(--chart-muted)">{v}</text></g>'
        )
    labels = []
    step = max(1, math.ceil(len(rows) / 7))
    for i, row in enumerate(rows):
        if i % step == 0:
            labels.append(
                f'<g>{svg_title(tr(lang, "Tanggal", "Date"), row["d"], tr(lang, "Positif", "Positive"), row["p"], tr(lang, "Negatif", "Negative"), row["n"], tr(lang, "Total", "Total"), row["t"])}'
                f'<text x="{x(i):.1f}" y="{h-p_b+13}" text-anchor="middle" font-size="5.8" fill="var(--chart-muted)">{esc(row["d"])}</text></g>'
            )
    return f"""
    <svg viewBox="0 0 {w} {h}" style="width:100%;height:100%">
      {"".join(grid)}
      <path d="{area}" fill="var(--chart-positive)" fill-opacity="0.07">
        {svg_title(tr(lang, "Area sentimen positif", "Positive sentiment area"))}
      </path>
      <path d="{p_path}" fill="none" stroke="var(--chart-positive)" stroke-width="1.65">
        {svg_title(tr(lang, "Garis positif", "Positive line"))}
      </path>
      <path d="{n_path}" fill="none" stroke="var(--chart-negative)" stroke-width="1.65">
        {svg_title(tr(lang, "Garis negatif", "Negative line"))}
      </path>
      <path d="{t_path}" fill="none" stroke="var(--chart-neutral)" stroke-width="0.75" stroke-dasharray="3 2" opacity="0.48">
        {svg_title(tr(lang, "Garis total", "Total line"))}
      </path>
      {"".join(labels)}
    </svg>
    """


def mk_category_chart(categories: list[dict[str, object]], lang: str) -> str:
    data = sorted(categories, key=lambda row: int(row["n"]), reverse=True)
    w, b_h, gap, p_l, p_r = 280, 20, 10, 70, 30
    c_w = w - p_l - p_r
    h = len(data) * (b_h + gap) + 12
    max_n = max(int(row["n"]) for row in data) or 1
    rows = []
    for i, row in enumerate(data):
        y = 6 + i * (b_h + gap)
        n_val = max(1, int(row["n"]))
        b_w = (n_val / max_n) * c_w
        p_w = (int(row["p"]) / n_val) * b_w
        n_w = (int(row["ne"]) / n_val) * b_w
        label = row["id"] if lang == "id" else row["en"]
        rows.append(
            f'<g>{svg_title(label, tr(lang, "Total", "Total"), n_val, tr(lang, "Positif", "Positive"), int(row["p"]), tr(lang, "Negatif", "Negative"), int(row["ne"]))}'
            f'<text x="{p_l-6}" y="{y+b_h/2+3.6}" text-anchor="end" font-size="8.8" fill="var(--chart-text)">{esc(label)}</text>'
            f'<rect x="{p_l}" y="{y}" width="{p_w}" height="{b_h}" fill="var(--chart-positive)">{svg_title(label, tr(lang, "Positif", "Positive"), int(row["p"]), f"{round((int(row["p"]) / n_val) * 100)}%")}</rect>'
            f'<rect x="{p_l+p_w}" y="{y}" width="{n_w}" height="{b_h}" fill="var(--chart-negative)">{svg_title(label, tr(lang, "Negatif", "Negative"), int(row["ne"]), f"{round((int(row["ne"]) / n_val) * 100)}%")}</rect>'
            f'<rect x="{p_l+p_w+n_w}" y="{y}" width="{b_w-p_w-n_w}" height="{b_h}" fill="var(--chart-neutral)">{svg_title(label, tr(lang, "Netral", "Neutral"), int(row["n"]) - int(row["p"]) - int(row["ne"]))}</rect>'
            f'<text x="{p_l+b_w+5}" y="{y+b_h/2+3.6}" font-size="7.9" fill="var(--chart-muted)">{n_val}</text></g>'
        )
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:100%">{"".join(rows)}</svg>'


def mk_heatmap(categories: list[dict[str, object]], lang: str) -> str:
    sents = [
        {"k": "p", "li": "Positif", "le": "Positive", "c": "#2d7a3a"},
        {"k": "ne", "li": "Negatif", "le": "Negative", "c": "#cc2200"},
        {"k": "nu", "li": "Netral", "le": "Neutral", "c": "#b09580"},
    ]
    c_w, c_h = 70, 36
    p_l, p_t = 80, 30
    w = p_l + len(sents) * c_w + 6
    h = p_t + len(categories) * c_h + 6
    max_v = max(max(int(row["p"]), int(row["ne"]), int(row["nu"])) for row in categories) or 1
    cells = []
    for ci, cat in enumerate(categories):
        for si, sent in enumerate(sents):
            v = int(cat[sent["k"]])
            a = v / max_v
            hex_alpha = format(round(a * 195 + 35), "02x")
            x = p_l + si * c_w
            y = p_t + ci * c_h
            tc = "#ffffff" if a > 0.48 else "#2d2a25"
            label = cat["id"] if lang == "id" else cat["en"]
            if si == 0:
                cells.append(f'<text x="{p_l-7}" y="{p_t+ci*c_h+(c_h-3)/2+3.6}" text-anchor="end" font-size="8.6" fill="var(--chart-text)">{esc(label)}</text>')
            cells.append(
            f'<g>{svg_title(label, sent["li"] if lang == "id" else sent["le"], v, tr(lang, "Skala intensitas warna", "Color intensity scale"))}'
            f'<rect x="{x}" y="{y}" width="{c_w-3}" height="{c_h-3}" fill="{sent["c"]}{hex_alpha}" rx="3"></rect>'
            f'<text x="{x+(c_w-3)/2}" y="{y+(c_h-3)/2+3.6}" text-anchor="middle" font-size="9.5" font-weight="600" fill="{tc}">{v}</text></g>'
        )
    headers = []
    for i, sent in enumerate(sents):
        label = sent["li"] if lang == "id" else sent["le"]
        headers.append(f'<text x="{p_l+i*c_w+(c_w-3)/2}" y="{p_t-9}" text-anchor="middle" font-size="7.5" fill="var(--chart-muted)">{esc(label)}</text>')
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:100%">{"".join(cells)}{"".join(headers)}</svg>'


def mk_source_chart(sources: list[dict[str, object]], lang: str = "id") -> str:
    data = sorted(sources, key=lambda row: int(row["n"]), reverse=True)[:7]
    w, b_h, gap, p_l, p_r = 380, 22, 10, 118, 72
    c_w = w - p_l - p_r
    h = len(data) * (b_h + gap) + 12
    max_n = max(int(row["n"]) for row in data) or 1
    rows = []
    for i, row in enumerate(data):
        y = 6 + i * (b_h + gap)
        n_val = max(1, int(row["n"]))
        b_w = (n_val / max_n) * c_w
        p_w = (int(row["p"]) / n_val) * b_w
        n_w = (int(row["ne"]) / n_val) * b_w
        rows.append(
            f'<g>{svg_title(row["name"], tr(lang, "Positif", "Positive"), int(row["p"]), tr(lang, "Negatif", "Negative"), int(row["ne"]), tr(lang, "Netral", "Neutral"), int(row["n"]) - int(row["p"]) - int(row["ne"]))}'
            f'<text x="{p_l-7}" y="{y+b_h/2+3.6}" text-anchor="end" font-size="8.6" fill="var(--chart-text)">{esc(row["name"])}</text>'
            f'<rect x="{p_l}" y="{y}" width="{p_w}" height="{b_h}" fill="var(--chart-positive)">{svg_title(row["name"], tr(lang, "Positif", "Positive"), int(row["p"]))}</rect>'
            f'<rect x="{p_l+p_w}" y="{y}" width="{n_w}" height="{b_h}" fill="var(--chart-negative)">{svg_title(row["name"], tr(lang, "Negatif", "Negative"), int(row["ne"]))}</rect>'
            f'<rect x="{p_l+p_w+n_w}" y="{y}" width="{b_w-p_w-n_w}" height="{b_h}" fill="var(--chart-neutral)">{svg_title(row["name"], tr(lang, "Netral", "Neutral"), int(row["n"]) - int(row["p"]) - int(row["ne"]))}</rect>'
            f'<text x="{p_l+b_w+7}" y="{y+b_h/2+3.6}" font-size="8" fill="var(--chart-muted)">{n_val} · {int(row["pp"])}%+</text></g>'
        )
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:100%">{"".join(rows)}</svg>'


def mk_gauge(avg_conf: float, lang: str = "id") -> str:
    val = max(0.0, min(1.0, avg_conf))
    r = 36
    cx = 50
    cy = 58

    def to_r(d: float) -> float:
        return d * math.pi / 180

    def ax(rad: float, deg: float) -> float:
        return cx + rad * math.cos(to_r(deg))

    def ay(rad: float, deg: float) -> float:
        return cy + rad * math.sin(to_r(deg))

    end_d = -180 + val * 180
    bg = f"M{ax(r, -180):.2f},{ay(r, -180):.2f} A{r},{r} 0 0 1 {ax(r, 0):.2f},{ay(r, 0):.2f}"
    vp = f"M{ax(r, -180):.2f},{ay(r, -180):.2f} A{r},{r} 0 0 1 {ax(r, end_d):.2f},{ay(r, end_d):.2f}"
    nx = cx + 28 * math.cos(to_r(end_d))
    ny = cy + 28 * math.sin(to_r(end_d))
    return f"""
    <svg viewBox="0 0 100 68" style="width:100%;height:100%">
      {svg_title(tr(lang, "Rata-rata keyakinan", "Average confidence"), f"{round(val * 100):.0f}%")}
      <path d="{bg}" fill="none" stroke="var(--chart-track)" stroke-width="9" stroke-linecap="round">
        {svg_title(tr(lang, "Latar gauge", "Gauge background"))}
      </path>
      <path d="{vp}" fill="none" stroke="var(--chart-positive)" stroke-width="9" stroke-linecap="round">
        {svg_title(tr(lang, "Skor confidence", "Confidence score"), f"{round(val * 100):.0f}%")}
      </path>
      <line x1="{cx}" y1="{cy}" x2="{nx:.2f}" y2="{ny:.2f}" stroke="var(--chart-text)" stroke-width="1.5" stroke-linecap="round"></line>
      <circle cx="{cx}" cy="{cy}" r="3" fill="var(--chart-text)"></circle>
      <text x="{cx}" y="{cy-8.5}" text-anchor="middle" font-size="14.5" font-weight="700" fill="var(--chart-text)" font-family="system-ui">{round(val * 100):.0f}%</text>
      <text x="{cx}" y="{cy-1}" text-anchor="middle" font-size="5.5" fill="var(--chart-muted)" font-family="system-ui">{'rata-rata keyakinan' if lang == 'id' else 'avg confidence'}</text>
    </svg>
    """
