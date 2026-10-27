"""Build the six body-pattern cards (BP-1..BP-6) in body/ as static HTML.

Charts are inline SVG computed from the data here, so bar lengths, label positions
and the waterfall arithmetic are exact. ALL DATA BELOW IS FICTIONAL (illustrative
only) and every card says so on the slide.

Usage: python3 tools/build_body_cards.py   (run from the design-system root)
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "body"
NAVY, BLUE, G300, G200, G500, WHITE = "var(--navy)", "var(--blue)", "var(--gray-300)", "var(--gray-200)", "var(--gray-500)", "var(--white)"
CW, GAP = 1164, 40  # content width, gap-block


def span(n, gap=GAP, total=CW):
    """Width of an n/12 block when a row is split into blocks separated by `gap`."""
    return (total - gap) * n / 12


def fmt(v, nd=1, sign=False):
    s = f"{abs(v):,.{nd}f}"
    if v < 0:
        return "−" + s
    return ("+" if sign and v > 0 else "") + s


# ---------------------------------------------------------------- SVG helpers
def bar_chart(w, h, cats, vals, colors, ymax, labels=None, deltas=None, label_cls=None, nd=1, ymin=0, gap_ratio=0.45, callouts=()):
    """Vertical bars from a zero baseline. deltas: {index: (text, ref_text, emphasis)}."""
    top, bottom = 52, 26                       # room for value + delta labels / category labels
    plot_h = h - top - bottom
    scale = plot_h / (ymax - ymin)
    base_y = top + ymax * scale
    n = len(cats)
    slot = w / n
    bw = slot * (1 - gap_ratio)
    out = [f'<svg class="chart" width="{w:.1f}" height="{h}" viewBox="0 0 {w:.1f} {h}">']
    for i, (c, v, col) in enumerate(zip(cats, vals, colors)):
        x = i * slot + (slot - bw) / 2
        y = base_y - max(v, 0) * scale
        bh = abs(v) * scale
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}"/>')
        lab = labels[i] if labels else fmt(v, nd)
        cls = (label_cls[i] if label_cls else "c-val")
        ly = (y - 6) if v >= 0 else (base_y + bh + 16)
        out.append(f'<text class="{cls}" x="{x + bw / 2:.1f}" y="{ly:.1f}" text-anchor="middle">{lab}</text>')
        if deltas and i in deltas:
            t, ref, em = deltas[i]
            out.append(f'<text class="c-delta{" em" if em else ""}" x="{x + bw / 2:.1f}" y="{ly - 22:.1f}" text-anchor="middle">{t}</text>')
            if ref:
                out.append(f'<text class="c-delta-ref" x="{x + bw / 2:.1f}" y="{ly - 40:.1f}" text-anchor="middle">{ref}</text>')
        out.append(f'<text class="c-axis" x="{i * slot + slot / 2:.1f}" y="{h - 6}" text-anchor="middle">{c}</text>')
    out.append(f'<rect x="0" y="{base_y:.1f}" width="{w:.1f}" height="1" fill="{G300}"/>')
    for (cx, cy, lines) in callouts:
        for k, line in enumerate(lines):
            out.append(f'<text class="c-callout" x="{cx}" y="{cy + k * 19}">{line}</text>')
    out.append("</svg>")
    return "".join(out), dict(slot=slot, bw=bw)


def grouped_bars(w, h, cats, s1, s2, c2, ymax, s_names, nd=1):
    """Two bars per category: s1 (earlier, gray-300) and s2 (later, colors c2)."""
    top, bottom = 30, 26
    plot_h = h - top - bottom
    scale = plot_h / ymax
    base_y = top + plot_h
    slot = w / len(cats)
    bw = slot * 0.26
    out = [f'<svg class="chart" width="{w:.1f}" height="{h}" viewBox="0 0 {w:.1f} {h}">']
    centers = []
    for i, c in enumerate(cats):
        cx = i * slot + slot / 2
        centers.append(cx)
        for j, (v, col, cls) in enumerate(((s1[i], G300, "c-val"), (s2[i], c2[i], "c-val em" if c2[i] == BLUE else "c-val"))):
            x = cx - bw - 2 + j * (bw + 4)
            y = base_y - v * scale
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{v * scale:.1f}" fill="{col}"/>')
            out.append(f'<text class="{cls}" x="{x + bw / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle">{fmt(v, nd)}</text>')
        out.append(f'<text class="c-axis" x="{cx:.1f}" y="{h - 6}" text-anchor="middle">{c}</text>')
    out.append(f'<rect x="0" y="{base_y:.1f}" width="{w:.1f}" height="1" fill="{G300}"/>')
    out.append("</svg>")
    return "".join(out), centers


def waterfall(w, h, steps, ymax):
    """steps: [(label, value, kind)] kind in start|up|down|end; emphasis via kind 'up*'."""
    top, bottom = 30, 26
    plot_h = h - top - bottom
    scale = plot_h / ymax
    base_y = top + plot_h
    slot = w / len(steps)
    bw = slot * 0.56
    run = 0
    out = [f'<svg class="chart" width="{w:.1f}" height="{h}" viewBox="0 0 {w:.1f} {h}">']
    for i, (lab, v, kind) in enumerate(steps):
        x = i * slot + (slot - bw) / 2
        if kind in ("start", "end"):
            lo, hi = 0, v
            run = v
            col = G300 if kind == "start" else NAVY
            txt, cls = fmt(v, 1), "c-val"
        else:
            lo, hi = (run, run + v) if v >= 0 else (run + v, run)
            run += v
            em = kind.endswith("*")
            col = BLUE if em else (G300 if v >= 0 else G200)
            txt, cls = fmt(v, 1, sign=True), ("c-val em" if em else "c-val")
        y = base_y - hi * scale
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{(hi - lo) * scale:.1f}" fill="{col}"/>')
        out.append(f'<text class="{cls}" x="{x + bw / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle">{txt}</text>')
        out.append(f'<text class="c-axis" x="{i * slot + slot / 2:.1f}" y="{h - 6}" text-anchor="middle">{lab}</text>')
    out.append(f'<rect x="0" y="{base_y:.1f}" width="{w:.1f}" height="1" fill="{G300}"/>')
    out.append("</svg>")
    return "".join(out), dict(slot=slot, bw=bw, scale=scale, base_y=base_y)


# ---------------------------------------------------------------- page shell
def page(card, eyebrow, title_html, body, footer, pagenum, lead=None, corner=True):
    head = card
    return f"""{head}
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{eyebrow}</title>
<link rel="stylesheet" href="../styles.css">
<link rel="stylesheet" href="body.css">
</head>
<body>
<div class="slide">
  {'<div class="corner-h"></div><div class="corner-v"></div>' if corner else ''}
  <div class="eyebrow">{eyebrow}</div>
  <h2 class="title">{title_html}</h2>
  {f'<p class="lead">{lead}</p>' if lead else ''}
  <div class="content {'with-lead' if lead else 'compact'}">
{body}
  </div>
  <div class="footer-left">{footer}</div>
  <img class="footer-mark" src="../assets/Logos/logo-wordmark.png" alt="IGIS">
  <div class="footer-sep">_</div>
  <div class="footer-page">{pagenum}</div>
</div>
</body>
</html>
"""


def card_tag(name, sub):
    return f'<!-- @dsCard group="Body patterns" viewport="1280x720" name="{name}" subtitle="{sub}" -->'


cards = {}

# ---------------------------------------------------------------- BP-1 단일 근거형 (시장 추세, N1)
years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]
deal = [10.4, 11.2, 12.4, 16.1, 13.5, 9.8, 11.6]
chg = deal[-1] / deal[-2] - 1                      # +18.4%
two_yr = deal[-2] / deal[3] - 1                    # 2021→2023: −39.1%
w8, w4 = span(8), span(4)
svg, _ = bar_chart(w8, 430, years, deal, [G300] * 6 + [BLUE], 18,
                   label_cls=["c-val"] * 6 + ["c-val em"],
                   deltas={6: (f"+{chg * 100:.0f}%", "전년 대비", True), 5: (f"−{abs(two_yr) * 100:.0f}%", "2021년 대비", False)})
body = f"""
    <div class="block" style="left:0;top:0;width:{w8:.1f}px">
      <div class="exh-head">오피스 거래금액<span class="unit">, 서울, 조원</span><span class="sub">2018–2024, 연간</span></div>
      <div style="margin-top:8px">{svg}</div>
    </div>
    <div class="block insight side" style="left:{w8 + GAP:.1f}px;top:0;width:{w4:.1f}px">
      <div class="item"><span class="key">2024년 증가는 대형 거래 재개가 주도</span>1,000억원 이상 거래가 전년 6건에서 11건으로 늘었습니다.</div>
      <div class="item"><span class="key">고점(2021년) 대비 {deal[-1] / deal[3] * 100:.0f}% 수준</span>2년 감소분({fmt(deal[-2] - deal[3])}조원) 중 {(deal[-1] - deal[-2]) / (deal[3] - deal[-2]) * 100:.0f}%를 회복했습니다.</div>
      <div class="item"><span class="key"><span class="tag">해석</span> 금리 인하 기대가 배경으로 추정</span>거래 재개 시점과 금리 전망 변화가 겹치지만, 인과관계는 확인되지 않았습니다.</div>
    </div>
    <div class="notes">
      <p>주: 연면적 3,300㎡ 이상 오피스 매매 기준, 지분 거래 포함·부분 매각 제외. 전년 대비 증감률은 반올림 전 값으로 계산.</p>
      <p>자료: 가상 예시 데이터(Illustrative). 실제 시장 통계가 아닙니다.</p>
    </div>"""
cards["bp1-single.html"] = page(
    card_tag("BP-1 단일 근거형", "시장 추세 · N1 추이 + BC-01·02·04·05 (가상 예시)"),
    "시장 추세 · 가상 예시",
    f'서울 오피스 거래금액은 2년 감소 후 2024년 <span class="pt">{chg * 100:.0f}% 증가</span>',
    body, "Source: 가상 예시 데이터 (Illustrative) · 단위: 조원 · '24.12.31 기준", "05")

# ---------------------------------------------------------------- BP-2 대조형 (지역 비교, C1 + N1, 같은 척도)
qs = ["'23.4Q", "'24.1Q", "2Q", "3Q", "4Q"]
gbd = [6.8, 6.1, 5.5, 5.0, 4.7]
cbd = [7.9, 8.4, 9.6, 10.8, 11.3]
w6 = (CW - 56) / 2
def vac(vals, em_delta):
    d = vals[-1] - vals[0]
    return bar_chart(w6, 360, qs, vals, [G300] * 4 + [BLUE], 14,
                     label_cls=["c-val"] * 4 + ["c-val em"],
                     deltas={4: (f"{fmt(d, 1, sign=True)}%p", "4개 분기 전 대비", em_delta)})[0]
body = f"""
    <div class="block" style="left:0;top:0;width:{w6:.1f}px">
      <div class="exh-head">공실률<span class="unit">, 강남권(GBD), %</span><span class="sub">두 도표 같은 척도(0–14%)</span></div>
      <div style="margin-top:8px">{vac(gbd, True)}</div>
      <div class="insight bottom" style="grid-template-columns:1fr;margin-top:14px"><div><span class="key">임차 수요가 신규 공급 없이 기존 공실을 흡수</span>4개 분기 연속 하락했습니다.</div></div>
    </div>
    <div class="block" style="left:{w6 + 56:.1f}px;top:0;width:{w6:.1f}px">
      <div class="exh-head">공실률<span class="unit">, 도심권(CBD), %</span><span class="sub">두 도표 같은 척도(0–14%)</span></div>
      <div style="margin-top:8px">{vac(cbd, True)}</div>
      <div class="insight bottom" style="grid-template-columns:1fr;margin-top:14px"><div><span class="key">신규 공급 2개 동 준공이 상승 요인</span>준공분을 빼면 공실률은 {cbd[0]:.1f}%에서 8.2%로 0.3%p 오르는 데 그칩니다.</div></div>
    </div>
    <div class="notes">
      <p>주: 공실률은 임대 가능 면적 기준, 분기 말 시점. 도심권 2024년 준공 2개 동(연면적 합계 18만㎡) 포함.</p>
      <p>자료: 가상 예시 데이터(Illustrative). 실제 시장 통계가 아닙니다.</p>
    </div>"""
cards["bp2-contrast.html"] = page(
    card_tag("BP-2 대조형", "지역 비교 · C1 + N1, 같은 척도 두 도표 (가상 예시)"),
    "권역 비교 · 가상 예시",
    f'강남권 공실률은 <span class="pt">2.1%p 하락</span>, 도심권은 신규 공급으로 3.4%p 상승',
    body, "Source: 가상 예시 데이터 (Illustrative) · 단위: % · '24.12.31 기준", "06")

# ---------------------------------------------------------------- BP-3 복수 지표형 (펀드 현황, BC-07)
yrs = ["2020", "2021", "2022", "2023", "2024"]
series = [("투자 집행", [4200, 5100, 3900, 3100, 4250]),
          ("회수", [2600, 3000, 2400, 1900, 2550]),
          ("신규 모집", [3200, 3800, 4100, 5200, 4000])]
pw = (CW - 2 * GAP) / 3
panels = []
for i, (name, vals) in enumerate(series):
    d = vals[-1] / vals[-2] - 1
    svg, _ = bar_chart(pw, 330, yrs, vals, [G300] * 4 + [BLUE], 6000,
                       labels=[f"{v:,}" for v in vals], label_cls=["c-val"] * 4 + ["c-val em"],
                       deltas={4: (f"{'+' if d > 0 else '−'}{abs(d) * 100:.0f}%", "전년 대비", True)})
    panels.append(f"""
    <div class="block" style="left:{i * (pw + GAP):.1f}px;top:0;width:{pw:.1f}px">
      <div class="exh-head">{name}<span class="unit">, 억원</span><span class="sub">세 패널 같은 척도(0–6,000억원)</span></div>
      <div style="margin-top:8px">{svg}</div>
    </div>""")
inv, ex, fr = (s[1] for s in series)
body = "".join(panels) + f"""
    <div class="block insight bottom" style="left:0;top:418px;width:{CW}px;grid-template-columns:repeat(3,1fr)">
      <div><span class="key">집행은 2년 감소 뒤 {inv[-1] / inv[-2] * 100 - 100:.0f}% 반등</span>다만 2021년 고점의 {inv[-1] / inv[1] * 100:.0f}% 수준입니다.</div>
      <div><span class="key">회수도 같은 방향으로 회복</span>회수/집행 비율은 {ex[-1] / inv[-1] * 100:.0f}%로 전년({ex[-2] / inv[-2] * 100:.0f}%)과 비슷합니다.</div>
      <div><span class="key">모집만 반대로 {abs(fr[-1] / fr[-2] - 1) * 100:.0f}% 감소</span>2023년 대형 펀드 1건의 기저 효과가 큽니다(추정).</div>
    </div>
    <div class="notes">
      <p>주: 집행·회수는 해당 연도 현금흐름 기준, 모집은 최종 결성액 기준(약정). 2024년 수치는 '24.12.31 잠정.</p>
      <p>자료: 가상 예시 데이터(Illustrative). 실제 펀드 실적이 아닙니다.</p>
    </div>"""
cards["bp3-multi.html"] = page(
    card_tag("BP-3 복수 지표형", "펀드 현황 · BC-07 복수 패널, 공통 축·척도 (가상 예시)"),
    "운용 현황 · 가상 예시",
    f'집행·회수는 2년 감소 뒤 반등했으나 <span class="pt">신규 모집은 23% 감소</span>',
    body, "Source: 가상 예시 데이터 (Illustrative) · 단위: 억원 · '24.12.31 기준", "07")

# ---------------------------------------------------------------- BP-4 패턴+상세형 (지역·자산 비교, N5b + BC-03 + BC-06a)
regions = ["도심", "강남", "여의도", "분당·판교", "기타"]
r23 = [2.1, 3.4, 2.8, 3.0, 1.2]
r24 = [0.3, 5.2, 4.6, 2.2, 0.8]
stock = [520, 460, 310, 180, 230]           # 만㎡
rent = [108500, 112300, 97800, 74600, 61200]  # 원/3.3㎡, 월
vacr = [11.3, 4.7, 6.2, 3.1, 8.9]           # %
deals = [3.2, 4.1, 2.6, 1.2, 0.5]           # 조원
S = sum(stock)
wavg = lambda xs: sum(a * b for a, b in zip(xs, stock)) / S
c2 = [G500, BLUE, BLUE, G500, G500]
gsvg, centers = grouped_bars(CW, 200, regions, r23, r24, c2, 6, ("2023", "2024"))
aux = "".join(f'<span class="v{" em" if c2[i] == BLUE else ""}" style="left:{centers[i]:.1f}px">{vacr[i]:.1f}%</span>' for i in range(5))
rows = "".join(
    f'<tr><td class="rh">{regions[i]}</td><td>{stock[i]:,}</td><td>{rent[i]:,}</td><td{" class=em" if c2[i] == BLUE else ""}>{r24[i]:.1f}</td><td>{vacr[i]:.1f}</td><td>{deals[i]:.1f}</td></tr>'
    for i in range(5))
rows += (f'<tr class="total"><td class="l">전체</td><td>{S:,}</td><td>{wavg(rent):,.0f}</td><td>{wavg(r24):.1f}</td>'
         f'<td>{wavg(vacr):.1f}</td><td>{sum(deals):.1f}</td></tr>')
body = f"""
    <div class="block" style="left:0;top:0;width:{CW}px">
      <div class="exh-head">임대료 상승률<span class="unit">, 권역별, 전년 대비 %</span><span class="sub">회색 2023년 · 진한 막대 2024년 (강조: 강남·여의도)</span></div>
      <div style="margin-top:6px">{gsvg}</div>
      <div class="aux-row" style="left:0;top:252px;width:{CW}px;height:28px"><span class="name">공실률 '24.4Q</span>{aux}</div>
    </div>
    <div class="block" style="left:0;top:296px;width:{CW}px">
      <table class="igis">
        <tr><th class="l">권역</th><th>재고 연면적<br>(만㎡)</th><th>평균 임대료<br>(원/3.3㎡·월)</th><th>임대료 상승률<br>2024 (%)</th><th>공실률<br>'24.4Q (%)</th><th>거래금액<br>2024 (조원)</th></tr>
        {rows}
      </table>
    </div>
    <div class="notes">
      <p>주: 전체 행의 임대료·상승률·공실률은 재고 연면적 가중평균, 거래금액은 합계. 임대료는 전용면적 환산 전 명목 임대료.</p>
      <p>자료: 가상 예시 데이터(Illustrative). 실제 시장 통계가 아닙니다.</p>
    </div>"""
cards["bp4-pattern-detail.html"] = page(
    card_tag("BP-4 패턴+상세형", "지역 비교 · N5b + BC-03 보조 지표 행 + BC-06a 표 (가상 예시)"),
    "권역 비교 · 가상 예시",
    f'임대료 상승은 <span class="pt">강남·여의도에 집중</span>되고 도심은 0.3%로 정체',
    body, "Source: 가상 예시 데이터 (Illustrative) · 단위: 표 머리글 참조 · '24.12.31 기준", "08")

# ---------------------------------------------------------------- BP-5 증감 분해형 (N6 + BC-06c + BC-08)
start, end = 120.0, 126.0
factors = [("임대료 인상", 9.0, "계약 갱신 12건, 평균 4% 인상", True),
           ("공실 축소", 5.0, "공실률 9% → 5%", False),
           ("운영비 증가", -6.0, "관리 용역 단가 인상", False),
           ("재산세 증가", -2.0, "공시가격 상승", False)]
assert abs(start + sum(f[1] for f in factors) - end) < 1e-9
steps = [("2023 NOI", start, "start")] + [(f[0], f[1], "up*" if f[3] else ("up" if f[1] > 0 else "down")) for f in factors] + [("2024 NOI", end, "end")]
w7, w5 = span(7), span(5)
wsvg, geo = waterfall(w7, 380, steps, 140)
contrib = [f[1] / start * 100 for f in factors]
up = sum(f[1] for f in factors if f[1] > 0)
dn = -sum(f[1] for f in factors if f[1] < 0)
callout_x = geo["slot"] * 3 - 10
wsvg = wsvg.replace("</svg>", f'<text class="c-callout" x="{callout_x:.1f}" y="{geo["base_y"] - 60:.1f}">비용 증가 {dn:.1f}억원이</text>'
                    f'<text class="c-callout" x="{callout_x:.1f}" y="{geo["base_y"] - 41:.1f}">증가 요인의 {dn / up * 100:.0f}%를 상쇄</text></svg>')
trs = "".join(
    f'<tr><td class="rh">{f[0]}</td><td{" class=em" if f[3] else ""}>{fmt(f[1], 1, True)}</td><td{" class=em" if f[3] else ""}>{fmt(c, 1, True)}</td><td class="txt">{f[2]}</td></tr>'
    for f, c in zip(factors, contrib))
body = f"""
    <div class="block" style="left:0;top:0;width:{w7:.1f}px">
      <div class="exh-head">NOI 증감 요인<span class="unit">, A빌딩, 억원</span><span class="sub">2023 → 2024</span></div>
      <div style="margin-top:8px">{wsvg}</div>
    </div>
    <div class="block" style="left:{w7 + GAP:.1f}px;top:0;width:{w5:.1f}px">
      <div class="exh-head">증감 분해<span class="unit">, 억원·%p</span><span class="sub">기여도 = 요인별 증감 ÷ 2023 NOI</span></div>
      <table class="igis" style="margin-top:8px">
        <tr><th class="l">요인</th><th>금액</th><th>기여도</th><th class="l">근거</th></tr>
        <tr><td class="rh">2023 NOI</td><td>{start:.1f}</td><td>–</td><td class="txt">실적</td></tr>
        {trs}
        <tr class="total"><td class="l">2024 NOI</td><td>{end:.1f}</td><td>{fmt(sum(contrib), 1, True)}</td><td class="txt" style="font-weight:400">실적</td></tr>
      </table>
    </div>
    <div class="block insight bottom" style="left:0;top:452px;width:{CW}px;grid-template-columns:repeat(2,1fr)">
      <div><span class="key">증가 요인 {up:.1f}억원 중 임대료 인상이 {9.0 / up * 100:.0f}%</span>나머지는 공실 축소({fmt(5.0, 1, True)}억원)입니다.</div>
      <div><span class="key">비용 증가는 일회성이 아님</span>용역 단가는 3년 계약으로 2025년에도 유지됩니다.</div>
    </div>
    <div class="notes">
      <p>주: 반올림으로 기여도 합계가 총 증감률과 다를 수 있음(본 예시는 일치). 시작값 + 요인 합계 = 종료값 대사 완료.</p>
      <p>자료: 가상 예시 데이터(Illustrative). 실제 자산 실적이 아닙니다.</p>
    </div>"""
cards["bp5-decomposition.html"] = page(
    card_tag("BP-5 증감 분해형", "증감 원인 · N6 폭포 + BC-06c 증감 분해 표 + BC-08 (가상 예시)"),
    "자산 성과 · 가상 예시",
    f'NOI {(end / start - 1) * 100:.1f}% 증가는 <span class="pt">임대료 인상이 주도</span>했고 비용 증가가 일부 상쇄',
    body, "Source: 가상 예시 데이터 (Illustrative) · 단위: 억원 · '24.12.31 기준", "09")

# ---------------------------------------------------------------- BP-6 교차 비교형 (외부 통계, N12 / BC-09)
assets = ["오피스", "물류", "주거", "데이터센터", "리테일", "호텔"]
groups = [("연기금", 24), ("보험", 31), ("공제회", 18), ("해외", 27)]
vals = {"오피스": [38, 29, 33, 41], "물류": [58, 52, 61, 49], "주거": [54, 45, 50, 63],
        "데이터센터": [46, 35, 28, 52], "리테일": [13, 10, 11, 15], "호텔": [21, 16, 22, 30]}
N = sum(n for _, n in groups)
total = {a: sum(v * n for v, (_, n) in zip(vals[a], groups)) / N for a in assets}
colmax = [max(vals[a][j] for a in assets) for j in range(4)]
totmax = max(total.values())
th = "".join(f"<th>{g}<br>(n={n})</th>" for g, n in groups)
trs = ""
for a in assets:
    tds = "".join(f'<td{" class=em" if vals[a][j] == colmax[j] else ""}>{vals[a][j]}</td>' for j in range(4))
    trs += f'<tr><td class="rh">{a}</td><td class="all{" em" if total[a] == totmax else ""}">{total[a]:.0f}</td>{tds}</tr>'
w8b, w4b = span(8), span(4)
lo = min(total, key=total.get)
body = f"""
    <div class="block" style="left:0;top:0;width:{w8b:.1f}px">
      <div class="exh-head">향후 12개월 비중 확대 계획 응답 비율<span class="unit">, 자산 유형 × 투자자 유형, %</span><span class="sub">강조: 열별 최댓값</span></div>
      <table class="igis cross" style="margin-top:8px">
        <tr><th class="l rh">자산 유형</th><th>전체<br>(n={N})</th>{th}</tr>
        {trs}
      </table>
    </div>
    <div class="block insight side" style="left:{w8b + GAP:.1f}px;top:0;width:{w4b:.1f}px">
      <div class="item"><span class="key">물류가 국내 기관 3개 군 모두에서 1위</span>해외 투자자만 주거({vals["주거"][3]}%)가 가장 높습니다.</div>
      <div class="item"><span class="key">{lo}은 모든 군에서 최하위</span>전체 {total[lo]:.0f}%로, 확대 계획 응답이 가장 적습니다.</div>
      <div class="item"><span class="key"><span class="tag">한계</span> 응답 의향이며 실제 집행이 아님</span>군별 표본이 18~31곳이라 군 간 차이는 참고 수준입니다.</div>
    </div>
    <div class="notes">
      <p>표본: 국내외 기관투자자 {N}곳(연기금 24·보험 31·공제회 18·해외 27). 조사기간 2024.11.4–11.22. 질문: "향후 12개월 내 해당 자산 비중을 늘릴 계획인가"(복수 응답).</p>
      <p>주: 전체 = 응답 수 가중평균. 자료: 가상 예시 설문(Illustrative). 실제 조사 결과가 아닙니다.</p>
    </div>"""
cards["bp6-cross.html"] = page(
    card_tag("BP-6 교차 비교형", "외부 통계 · N12 / BC-09 교차 비교 표 (가상 예시)"),
    "투자자 설문 · 가상 예시",
    f'비중 확대 의향은 <span class="pt">물류·주거에 집중</span>되고 리테일은 전 투자자군에서 최하위',
    body, "Source: 가상 예시 설문 (Illustrative) · 단위: % · 조사기간 '24.11", "10")

OUT.mkdir(exist_ok=True)
for name, html in cards.items():
    (OUT / name).write_text(html)
print("wrote", ", ".join(cards))
print(f"BP-1 chg {chg * 100:.1f}%  two-yr {two_yr * 100:.1f}%")
print("BP-4 wavg rent/r24/vac:", round(wavg(rent)), round(wavg(r24), 2), round(wavg(vacr), 2), "deals", sum(deals))
print("BP-5 contrib:", [round(c, 2) for c in contrib], "sum", round(sum(contrib), 2))
print("BP-6 totals:", {a: round(t, 1) for a, t in total.items()})
