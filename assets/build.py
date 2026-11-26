"""Generates the animated README SVGs in light and dark variants.

Run: python assets/build.py  (writes assets/*-light.svg and assets/*-dark.svg)
Edit the content here, never the generated SVGs.

The animation framework (Anim, svg, window, box, wire, packets, themes) is adapted from
Sebastian Cortez's profile repo, github.com/sxbast1anCZ/sxbast1anCZ. The scenes are mine.
All numbers shown are model or test metrics; the Insecap scene uses no company data.
"""
import random
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
T = 16  # seconds per animation loop

THEMES = {
    "dark": dict(bg="#0d1117", panel="#161b22", border="#30363d", text="#e6edf3", muted="#8b949e",
                 accent="#58a6ff", green="#3fb950", yellow="#d29922", orange="#e8743b", red="#f85149", purple="#bc8cff"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de", text="#1f2328", muted="#59636e",
                  accent="#0969da", green="#1a7f37", yellow="#9a6700", orange="#c2521f", red="#cf222e", purple="#8250df"),
}
MAGMA = ["#3b0f70", "#641a80", "#8c2981", "#b73779", "#de4968", "#f7705c", "#fe9f6d", "#fecf92", "#fcfdbf"]
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
CW = 8.43  # width of one 14px monospace char


def pct(t):
    return f"{t / T * 100:.2f}%"


class Anim:
    """Collects per-element keyframes so every element shares one loop of T seconds."""

    def __init__(self):
        self.css, self.n = [], 0

    def _add(self, frames, timing=""):
        name = f"k{self.n}"
        self.n += 1
        self.css.append(f"@keyframes {name}{{{frames}}}.{name}{{animation:{name} {T}s {timing} infinite}}")
        return name

    def appear(self, t):
        """Hidden until t, then visible until the loop fades out."""
        return self._add(f"0%,{pct(t)}{{opacity:0}}{pct(t + .25)},100%{{opacity:1}}")

    def type(self, t, chars):
        """Cover rect that shrinks toward its right edge one char at a time, revealing typed text."""
        dur = chars * 0.05
        return self._add(f"0%,{pct(t)}{{transform:scaleX(1);animation-timing-function:steps({chars})}}"
                         f"{pct(t + dur)},100%{{transform:scaleX(0)}}"), t + dur

    def move(self, t, dur, dx, dy, period=None):
        """Packet travelling (dx,dy) starting at t; repeats every `period` seconds within the loop."""
        steps, cur = [], t
        while cur + dur <= T - 1:
            steps.append(f"{pct(cur)}{{transform:translate(0,0);opacity:1}}"
                         f"{pct(cur + dur)}{{transform:translate({dx}px,{dy}px);opacity:1}}"
                         f"{pct(cur + dur + .01)}{{opacity:0}}")
            if not period:
                break
            cur += period
        return self._add(f"0%,{pct(t - .01)}{{opacity:0}}" + "".join(steps) + "100%{opacity:0}", "linear")

    def grow(self, t, dur=.6):
        """scaleY from 0 for bars (needs .bar: transform-box fill-box, origin bottom)."""
        return self._add(f"0%,{pct(t)}{{transform:scaleY(0)}}{pct(t + dur)},100%{{transform:scaleY(1)}}", "ease-out")

    def style(self, extra=""):
        return (f"<style>text{{font-family:{MONO}}}.sans{{font-family:{SANS}}}"
                f".loop{{animation:loop {T}s infinite}}@keyframes loop{{0%,95%{{opacity:1}}98%,100%{{opacity:0}}}}"
                f".blink{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}"
                f".pulse{{animation:pulse 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}"
                f"@keyframes pulse{{50%{{transform:scale(1.25);opacity:.6}}}}"
                f".twinkle{{animation:twinkle 3s ease-in-out infinite}}@keyframes twinkle{{50%{{opacity:.35}}}}"
                f".bar{{transform-box:fill-box;transform-origin:bottom}}.cover{{transform-box:fill-box;transform-origin:right}}"
                + "".join(self.css) + extra +
                # Reduced motion: show the finished frame, no movement.
                "@media (prefers-reduced-motion:reduce){*{animation:none!important}.cover,.pkt{display:none}}</style>")


def svg(w, h, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{escape(label)}"><title>{escape(label)}</title>{body}</svg>')


def window(x, y, w, h, title, c):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{c["panel"]}" stroke="{c["border"]}"/>'
            f'<path d="M{x} {y + 34}h{w}" stroke="{c["border"]}"/>'
            + "".join(f'<circle cx="{x + 20 + i * 18}" cy="{y + 17}" r="5.5" fill="{col}"/>'
                      for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")))
            + f'<text x="{x + w / 2}" y="{y + 22}" text-anchor="middle" font-size="12" fill="{c["muted"]}">{title}</text>')


def box(x, y, w, h, title, sub, c, col):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{c["panel"]}" stroke="{col}" stroke-width="1.5"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 - 3}" text-anchor="middle" font-size="14" font-weight="600" fill="{c["text"]}">{title}</text>'
            f'<text x="{x + w / 2}" y="{y + h / 2 + 16}" text-anchor="middle" font-size="11" fill="{c["muted"]}">{sub}</text>')


def wire(x1, y1, x2, y2, c):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{c["border"]}" stroke-width="1.5" stroke-dasharray="4 5"/>'


def packets(a, x1, y1, x2, y2, col, start, n=3):
    return "".join(f'<circle class="pkt {a.move(start + i * .5, 1.1, x2 - x1, y2 - y1, period=3)}" '
                   f'cx="{x1}" cy="{y1}" r="4" fill="{col}"/>' for i in range(n))


def card(c):
    return f'<rect width="880" height="{{h}}" rx="12" fill="{c["panel"]}" stroke="{c["border"]}"/>'


def t(x, y, s, c, size=11, fill="text", anchor="start", weight=None):
    """Text helper. `s` must already be XML-escaped (use &amp; for an ampersand)."""
    w = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c.get(fill, fill)}"{w}>{s}</text>'


def show(a, when, *parts):
    return f'<g class="{a.appear(when)}">{"".join(parts)}</g>'


# ---------------------------------------------------------------- hero
def hero(c):
    a, out = Anim(), []
    H = 420
    out.append(window(0, 0, 560, H, "vicente@antofagasta: ~", c))
    prompt = f'<tspan fill="{c["green"]}">~/vicente</tspan><tspan fill="{c["muted"]}"> $ </tspan>'
    award = lambda h, place, col, name: (f'<tspan fill="{c["yellow"]}">{h}</tspan><tspan fill="{col}"> {place}</tspan>'
                                         f'<tspan fill="{c["text"]}"> · {name}</tspan>')
    lines = [
        ("cmd", "whoami"),
        ("out", f'<tspan fill="{c["text"]}">ML &amp; Software Engineer</tspan><tspan fill="{c["muted"]}"> · 4th year @ </tspan>'
                f'<tspan fill="{c["accent"]}">UCN</tspan>'),
        ("cmd", "cat focus.txt"),
        ("out", f'<tspan fill="{c["text"]}">data science + machine learning</tspan><tspan fill="{c["accent"]}"> → </tspan>'
                f'<tspan fill="{c["purple"]}">software that ships it</tspan>'),
        ("cmd", "cat teaching.txt"),
        ("out", f'<tspan fill="{c["text"]}">TA: Software Eng · Web &amp; Mobile · Data Science</tspan>'),
        ("cmd", "git log --awards --oneline"),
        ("out", award("e3c19f0", "1st", c["green"], "NASA Space Apps 2026 (Fireguard)")),
        ("out", award("b74d2a1", "1st", c["green"], "Hackadisc 2026 (Insecap)")),
        ("cmd", "echo $STATUS"),
        ("out", f'<tspan fill="{c["green"]}">open to internships</tspan><tspan fill="{c["muted"]}"> · Antofagasta, Chile</tspan>'),
    ]
    tm, y, px = 0.6, 70, 20 + 16 * CW  # prompt "~/vicente $ " is 12 chars; keep a small gap
    px = 20 + 12 * CW
    for i, (kind, txt) in enumerate(lines):
        if kind == "cmd":
            start = tm + .4
            out.append(f'<text class="{a.appear(start - .3)}" x="20" y="{y}" font-size="14">{prompt}'
                       f'<tspan fill="{c["text"]}">{txt}</tspan></text>')
            k, tm = a.type(start, len(txt))
            out.append(f'<rect class="cover {k}" x="{px - 2:.1f}" y="{y - 15}" width="{len(txt) * CW + 6:.1f}" height="20" fill="{c["panel"]}"/>')
        else:
            tm += .35
            out.append(f'<text class="{a.appear(tm)}" x="20" y="{y}" font-size="14">{txt}</text>')
        y += 26
        if kind == "out" and i + 1 < len(lines) and lines[i + 1][0] == "cmd":
            y += 10
    out.append(f'<text class="{a.appear(tm + .4)}" x="20" y="{y + 10}" font-size="14">{prompt}'
               f'<tspan class="blink" fill="{c["accent"]}">▍</tspan></text>')

    # right column: what I've shipped
    out.append(window(580, 0, 300, H, "shipped.md", c))
    shipped = [("Fireguard model", "harmonized + next-day fire risk", c["red"]),
               ("Insecap forecasts", "close, payments, client risk", c["accent"]),
               ("GameVault API", "layered FastAPI backend", c["green"]),
               ("Book scraper", "Selenium + SQLModel pipeline", c["yellow"]),
               ("Selection algorithms", "Quickselect · BFPRT, benchmarked", c["purple"])]
    for i, (name, sub, col) in enumerate(shipped):
        yy, k = 52 + i * 70, a.appear(1.2 + i * 1.1)
        out.append(f'<g class="{k}"><rect x="598" y="{yy}" width="264" height="56" rx="8" fill="{c["bg"]}" stroke="{c["border"]}"/>'
                   f'<rect x="598" y="{yy}" width="4" height="56" rx="2" fill="{col}"/>'
                   f'<text x="616" y="{yy + 24}" font-size="13" font-weight="600" fill="{c["text"]}">{name}</text>'
                   f'<text x="616" y="{yy + 43}" font-size="11" fill="{c["muted"]}">{sub}</text>'
                   f'<text x="846" y="{yy + 24}" font-size="13" text-anchor="end" fill="{c["green"]}">✓</text></g>')
    return svg(880, H, "Terminal session: Vicente Siglic, machine learning and software engineer, fourth-year computer "
               "engineering student at UCN, teaching assistant in software engineering, web and mobile development and "
               "data science. Awards: 1st at NASA Space Apps 2026 and 1st at Hackadisc 2026. Open to internships. "
               "Beside it, a list of shipped work: the Fireguard model, Insecap forecasts, the GameVault API, a book "
               "scraper and selection algorithms.", a.style() + f'<g class="loop">{"".join(out)}</g>')


# ---------------------------------------------------------------- Fireguard: harmonization + next-day model
def fireguard_model(c):
    a, o, rnd = Anim(), [], random.Random(11)
    H = 360
    o.append(card(c).format(h=H))
    o.append(t(40, 40, "1 · one scale for 26 years", c, 12, "muted"))
    o.append(t(316, 40, "2 · next-day model", c, 12, "muted"))
    o.append(t(640, 40, "3 · risk map for tomorrow", c, 12, "muted"))
    o.append(f'<path d="M30 284H850" stroke="{c["border"]}"/>')

    # stage 1: yearly hotspots, MODIS-only years lifted to the VIIRS scale
    base, x0, step, bw = 240, 40, 9.4, 7.6
    raw = [rnd.uniform(18, 32) if i < 12 else rnd.uniform(66, 100) for i in range(26)]
    o.append(f'<text x="40" y="64" font-size="10"><tspan fill="{c["yellow"]}">■ MODIS 1 km</tspan>'
             f'<tspan fill="{c["accent"]}">  ■ VIIRS 375 m</tspan><tspan fill="{c["orange"]}">  ■ harmonized</tspan></text>')
    for i in range(12):  # harmonized MODIS years, drawn first so the raw bar sits on top
        h = raw[i] * 3.0
        o.append(f'<rect class="bar {a.grow(3.6 + i * .06, .5)}" x="{x0 + i * step:.1f}" y="{base - h:.0f}" width="{bw}" '
                 f'height="{h:.0f}" rx="1.5" fill="{c["orange"]}" fill-opacity=".8"/>')
    for i, h in enumerate(raw):
        col = c["yellow"] if i < 12 else c["accent"]
        o.append(f'<rect class="bar {a.grow(.4 + i * .06, .5)}" x="{x0 + i * step:.1f}" y="{base - h:.0f}" width="{bw}" '
                 f'height="{h:.0f}" rx="1.5" fill="{col}"/>')
    jx = x0 + 12 * step - 1.4
    o.append(show(a, 1.9, f'<path d="M{jx:.1f} 96V{base}" stroke="{c["red"]}" stroke-dasharray="3 3"/>',
                  t(f"{jx:.1f}", 92, "2012: new sensor", c, 10, "red", "middle")))
    o.append(f'<path d="M40 {base}H284" stroke="{c["border"]}"/>')
    o.append(t(40, 256, "2000", c, 9, "muted") + t(284, 256, "2025", c, 9, "muted", "end"))
    o.append(show(a, 3.4, t(40, 274, "factor per region · month · satellite pass", c, 10, "orange")))

    # stage 2: features -> LightGBM
    feats = ["fire, last 7 days", "8 neighbour cells", "history of the cell", "FRP · night detect"]
    for i, name in enumerate(feats):
        y = 62 + i * 36
        o.append(show(a, 5.2 + i * .35,
                      f'<rect x="316" y="{y}" width="146" height="28" rx="7" fill="{c["bg"]}" stroke="{c["border"]}"/>'
                      f'<circle cx="331" cy="{y + 14}" r="3.5" fill="{c["purple"]}"/>' + t(341, y + 18, name, c, 10)))
        o.append(wire(462, y + 14, 486, 136, c))
    o.append(show(a, 6.8, t(316, 218, "+ 19 more features", c, 10, "muted")))
    o.append(show(a, 6.6, box(486, 98, 130, 76, "LightGBM", "1 per country", c, c["purple"])))
    o.append(packets(a, 462, 98, 486, 136, c["purple"], 7.2, 2) + packets(a, 462, 170, 486, 136, c["purple"], 7.6, 2))
    o.append(wire(616, 136, 640, 136, c) + packets(a, 616, 136, 640, 136, c["orange"], 8.0, 2))
    o.append(show(a, 7.4, t(551, 196, "SHAP: a reason", c, 10, "muted", "middle") + t(551, 210, "for every alert", c, 10, "muted", "middle")))

    # stage 3: risk grid around a hotspot seen today
    cols, rows, s, gx, gy = 7, 5, 30, 640, 62
    hot = (2, 2)
    cells = []
    for r in range(rows):
        for q in range(cols):
            d = ((q - hot[0]) ** 2 + (r - hot[1]) ** 2) ** .5
            v = max(0, min(8, int(8 - d * 2.3 + rnd.uniform(-.8, .8))))
            cells.append(f'<rect x="{gx + q * s}" y="{gy + r * s}" width="{s - 2}" height="{s - 2}" rx="3" '
                         f'fill="{MAGMA[v]}" fill-opacity=".85"/>')
    o.append(show(a, 9.0, *cells))
    hx, hy = gx + hot[0] * s + (s - 2) / 2, gy + hot[1] * s + (s - 2) / 2
    o.append(show(a, 9.8, f'<circle cx="{hx}" cy="{hy}" r="4" fill="#fff" stroke="{c["border"]}"/>'))
    ax, ay = gx + 3 * s, gy + 2 * s
    o.append(show(a, 10.8, f'<rect class="pulse" x="{ax - 1}" y="{ay - 1}" width="{s}" height="{s}" rx="4" fill="none" '
                           f'stroke="{c["orange"]}" stroke-width="2.4"/>'))
    o.append(show(a, 11.4, f'<rect x="640" y="222" width="210" height="48" rx="8" fill="{c["orange"]}" fill-opacity=".1" stroke="{c["orange"]}"/>'
                           + t(652, 241, "alert: fire next door today,", c, 10, "text")
                           + t(652, 257, "and it is the burning season", c, 10, "muted")))

    # results
    o.append(show(a, 12.4, t(40, 306, "held-out years: the yearly total is off by 2.1% (Argentina) · 5.3% (Chile)", c, 11)))
    o.append(show(a, 13.0, t(40, 326, "2023–2025, never seen in training: 78.0% (AR) · 79.1% (CL) of fire cell-days caught", c, 11)))
    o.append(show(a, 13.6, t(40, 346, "same alert budget as the “fire nearby” rule: 79% vs 64% (AR) · 68% vs 49% (CL)", c, 11, "green")))
    return svg(880, H, "Diagram of the Fireguard modelling work. One: yearly hotspot counts jump in 2012 when VIIRS replaces "
               "MODIS, and harmonization factors lift the MODIS years to one continuous scale, with a yearly-total error of "
               "2.1 percent in Argentina and 5.3 percent in Chile on held-out years. Two: 23 features per cell-day feed one "
               "LightGBM model per country, with a SHAP reason for every alert. Three: a risk map for the next day. On "
               "2023 to 2025, unseen in training, it catches 78.0 percent of fire cell-days in Argentina and 79.1 percent "
               "in Chile, against 64 and 49 percent for the neighbour rule at the same alert budget.",
               a.style() + "".join(o))


# ---------------------------------------------------------------- Insecap: the models and how they plug into the KPI API
def insecap_models(c):
    a, o = Anim(), []
    H = 400
    o.append(card(c).format(h=H))
    o.append(t(30, 40, "data", c, 12, "muted") + t(190, 40, "my models · offline batch", c, 12, "muted")
             + t(596, 40, "integration", c, 12, "muted"))

    # inputs
    for i, name in enumerate(("sales", "quotes")):
        y = 100 + i * 60
        o.append(show(a, .4 + i * .5, f'<rect x="30" y="{y}" width="110" height="36" rx="7" fill="{c["bg"]}" stroke="{c["border"]}"/>'
                      f'<circle cx="48" cy="{y + 18}" r="4" fill="{c["accent"]}"/>' + t(60, y + 22, name, c, 12)))
        o.append(f'<path d="M140 {y + 18}H165" stroke="{c["border"]}" stroke-dasharray="4 5" stroke-width="1.5"/>')
    o.append(f'<path d="M165 92V284" stroke="{c["border"]}" stroke-dasharray="4 5" stroke-width="1.5"/>')
    o.append(packets(a, 140, 118, 165, 118, c["accent"], 1.6, 2) + packets(a, 140, 178, 165, 178, c["accent"], 2.0, 2))

    # model cards
    cards = [
        (56, "02 · Sales close forecast", "mm3_drift · time series, not ML", "MAPE 11.8% vs 12.6% baseline · 8/8 in band", c["accent"], 2.0),
        (152, "03 · Payments", "Random Forest · invoice days + late pay", "late-pay AUC-PR 0.46 · 15.7× chance", c["green"], 3.4),
        (248, "04 · Client risk", "4 risk axes, never merged", "churn LightGBM · AUC-PR 0.89 vs 0.78", c["purple"], 4.8),
    ]
    for y, title, sub, metric, col, when in cards:
        parts = [f'<rect x="190" y="{y}" width="310" height="72" rx="10" fill="{c["panel"]}" stroke="{col}" stroke-width="1.5"/>',
                 t(206, y + 24, title, c, 13, "text", weight=600), t(206, y + 41, sub, c, 11, "muted"),
                 t(206, y + 61, metric, c, 11, col)]
        o.append(show(a, when, *parts))
        o.append(f'<path d="M165 {y + 36}H190" stroke="{c["border"]}" stroke-dasharray="4 5" stroke-width="1.5"/>')
        o.append(packets(a, 165, y + 36, 190, y + 36, col, when + .6, 1))
        o.append(f'<path d="M500 {y + 36}H532" stroke="{c["border"]}" stroke-dasharray="4 5" stroke-width="1.5"/>')
    # per-card mini visuals
    o.append(show(a, 2.8,
                  f'<path d="M432 {56 + 44}L444 {56 + 38}L456 {56 + 40}L468 {56 + 30}L486 {56 + 22}V{56 + 40}L468 {56 + 42}'
                  f'L456 {56 + 46}L444 {56 + 44}L432 {56 + 50}Z" fill="{c["accent"]}" fill-opacity=".18"/>'
                  f'<path d="M432 {56 + 47}L444 {56 + 41}L456 {56 + 43}L468 {56 + 36}L486 {56 + 31}" fill="none" stroke="{c["accent"]}" stroke-width="2"/>'))
    o.append(show(a, 4.2, "".join(f'<circle cx="480" cy="{152 + 16 + i * 17}" r="5" fill="{col}"/>'
                                  for i, col in enumerate((c["red"], c["yellow"], c["green"])))))
    o.append(f'<rect class="bar {a.grow(5.6)}" x="464" y="{248 + 14}" width="12" height="38" rx="2" fill="{c["purple"]}"/>'
             f'<rect class="bar {a.grow(5.8)}" x="480" y="{248 + 14 + 5}" width="12" height="33" rx="2" fill="{c["muted"]}" fill-opacity=".6"/>')
    # model 03 score is reused by model 04
    o.append(show(a, 5.8, f'<path d="M250 224V248" stroke="{c["green"]}" stroke-width="1.5" stroke-dasharray="3 3"/>'
                          f'<path d="M246 243l4 6l4 -6" fill="none" stroke="{c["green"]}" stroke-width="1.5"/>'
                          + t(262, 240, "payment score reused", c, 10, "green")))

    # output bus into the integration column
    o.append(f'<path d="M532 92V284M532 75H596" stroke="{c["border"]}" stroke-dasharray="4 5" stroke-width="1.5" fill="none"/>')
    o.append(packets(a, 532, 75, 596, 75, c["accent"], 6.6, 2))

    # integration column: tables -> KPI API (Sebastian) -> dashboard
    o.append(show(a, 7.0, f'<rect x="596" y="56" width="254" height="38" rx="8" fill="{c["bg"]}" stroke="{c["border"]}"/>'
                  + t(723, 79, "outputs/*.csv · json", c, 12, "text", "middle")))
    o.append(wire(723, 94, 723, 120, c) + packets(a, 723, 94, 723, 120, c["green"], 7.8, 2))
    o.append(show(a, 8.0, box(596, 120, 254, 58, "KPI API", "FastAPI · built by Sebastián Cortez", c, c["green"])))
    o.append(wire(723, 178, 723, 204, c) + packets(a, 723, 178, 723, 204, c["green"], 8.8, 2))
    dash = [f'<rect x="596" y="204" width="254" height="116" rx="10" fill="{c["bg"]}" stroke="{c["border"]}"/>',
            f'<rect x="606" y="212" width="86" height="22" rx="6" fill="{c["green"]}" fill-opacity=".15"/>',
            t(649, 227, "management", c, 10, "green", "middle"), t(736, 227, "sales exec", c, 10, "muted", "middle")]
    o.append(show(a, 9.6, *dash))
    o.append(show(a, 10.6,
                  f'<path d="M608 300L624 288L640 291L656 278L676 270V288L656 292L640 297L624 296L608 306Z" fill="{c["accent"]}" fill-opacity=".18"/>'
                  f'<path d="M608 303L624 292L640 294L656 284L676 274" fill="none" stroke="{c["accent"]}" stroke-width="2"/>'
                  + t(608, 314, "close forecast + band", c, 9, "muted")))
    o.append(show(a, 11.4, t(700, 252, "client risk", c, 10, "text")
                  + "".join(f'<circle cx="706" cy="{266 + i * 15}" r="4" fill="{col}"/>' + t(716, 270 + i * 15, f"client {n}", c, 10, "text")
                            for i, (col, n) in enumerate(((c["green"], "A"), (c["yellow"], "B"), (c["red"], "C"))))))

    o.append(show(a, 12.4, t(30, 354, "each model beat the alternatives in a rolling-origin backtest: simple won, and was kept", c, 11, "text")))
    o.append(show(a, 13.2, t(30, 374, "batch, not live inference: the API only reads tables that were computed offline", c, 11, "muted")))
    o.append(t(850, 392, "sample values", c, 9, "muted", "end"))
    return svg(880, H, "Diagram: sales and quotes feed three offline models. A sales close forecast using mm3_drift, with a MAPE "
               "of 11.8 percent against 12.6 percent for the best baseline. A payments model, a Random Forest, with a late "
               "payment AUC-PR of 0.46, 15.7 times chance. A client risk model with four axes, with a churn AUC-PR of 0.89 "
               "against 0.78 for the existing rule. The payment score is reused by the client risk model. The outputs are "
               "CSV and JSON tables that the KPI API reads and serves to a dashboard with management and sales executive views.",
               a.style() + "".join(o))


# ---------------------------------------------------------------- GameVault: layered architecture
def gamevault(c):
    a, o = Anim(), []
    H = 400
    o.append(card(c).format(h=H))
    layers = [("Client", "Swagger UI", c["muted"], ("any HTTP client", "or a front end")),
              ("Router", "app/routers", c["accent"], ("HTTP and validation", "never touches the DB")),
              ("Service", "app/services", c["purple"], ("business rules", "never writes a query")),
              ("Repository", "app/repositories", c["green"], ("the only layer that", "calls select()")),
              ("Model", "app/models", c["orange"], ("SQLModel · SQLite", "Alembic migrations"))]
    bw, gap, x0, y0, bh = 120, 50, 40, 84, 72
    o.append(show(a, .2, f'<rect x="40" y="30" width="190" height="26" rx="13" fill="{c["accent"]}" fill-opacity=".14"/>'
                  + t(135, 47, "POST /orders/checkout", c, 11, "accent", "middle")))
    o.append(show(a, .2, t(850, 47, "→ request", c, 10, "accent", "end") + t(770, 47, "← response", c, 10, "green", "end")))
    for i, (name, sub, col, rule) in enumerate(layers):
        x = x0 + i * (bw + gap)
        o.append(show(a, .5 + i * .5, box(x, y0, bw, bh, name, sub, c, col)))
        o.append(show(a, 1.4 + i * .6, t(x + bw / 2, y0 + bh + 26, rule[0], c, 10.5, "text", "middle")
                      + t(x + bw / 2, y0 + bh + 42, rule[1], c, 10.5, "muted", "middle")))
        if i < 4:
            xa, xb = x + bw, x + bw + gap
            o.append(f'<path d="M{xa} {y0 + 26}H{xb}M{xa} {y0 + 46}H{xb}" stroke="{c["border"]}" stroke-width="1.5" stroke-dasharray="4 5"/>')
            o.append(packets(a, xa, y0 + 26, xb, y0 + 26, c["accent"], 3.0 + i * .8, 2))
            o.append(packets(a, xb, y0 + 46, xa, y0 + 46, c["green"], 6.6 + (3 - i) * .8, 2))

    # cross-cutting concerns and integrations
    groups = [(40, "app/core", ("JWT + token blacklist", "rate limit on /auth", "JSON logs · request_id", "one error format"), c["accent"], 8.6),
              (450, "app/integrations + jobs", ("Resend · email codes", "Cloudinary · images", "PDF receipts", "APScheduler · cleanup"), c["orange"], 10.0)]
    for gx, title, chips, col, when in groups:
        parts = [f'<rect x="{gx}" y="238" width="390" height="116" rx="10" fill="{c["bg"]}" stroke="{c["border"]}"/>',
                 t(gx + 16, 262, title, c, 12, col, weight=600)]
        for i, chip in enumerate(chips):
            cx, cy = gx + 16 + (i % 2) * 186, 276 + (i // 2) * 36
            parts.append(f'<rect x="{cx}" y="{cy}" width="172" height="28" rx="7" fill="{c["panel"]}" stroke="{c["border"]}"/>'
                         f'<circle cx="{cx + 14}" cy="{cy + 14}" r="3.5" fill="{col}"/>' + t(cx + 26, cy + 18, chip, c, 10.5))
        o.append(show(a, when, *parts))
    o.append(show(a, 12.2, t(40, 380, "idempotent checkout · soft deletes · reviews only for games you own", c, 11, "muted")))
    return svg(880, H, "Diagram of the GameVault UCN layered architecture: a request such as POST orders checkout travels "
               "from the client to the router, the service, the repository and the model, and the response travels back. "
               "Routers never touch the database, services never write a query, and only repositories call select. "
               "Below, the core layer with JWT and a token blacklist, rate limiting, JSON logs with a request id and one "
               "error format, and the integrations: Resend email, Cloudinary images, PDF receipts and APScheduler jobs.",
               a.style() + "".join(o))


if __name__ == "__main__":
    for name, fn in (("hero", hero), ("work-fireguard-model", fireguard_model),
                     ("work-insecap-models", insecap_models), ("work-gamevault-layers", gamevault)):
        for theme, c in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(fn(c), encoding="utf-8")
            print("wrote", f"{name}-{theme}.svg")
