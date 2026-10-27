/* ============================================================
   IGIS 제안서 디자인가이드-KAMCO — PowerPoint template generator.
   PPT presentation + A4 print only (no web).

   Every color and zone line comes from ../../tokens.json.
   Geometry is in the 1280×720 canvas unit (96 px = 1 in, so the
   13.333×7.5 in LAYOUT_WIDE canvas maps 1:1). Font sizes: px × 0.75 = pt.

   Fonts are the STATIC Pretendard TTFs (fonts/), addressed by the
   family names Office shows: "Pretendard" (Regular / Bold via bold),
   "Pretendard Medium", "Pretendard SemiBold". Never set bold on the
   Medium / SemiBold families (PowerPoint would fake a heavier weight).

   Usage:  node build-template.js <out.pptx> [--layouts-only]
   Then:   python3 postprocess.py <out.pptx> [--potx out.potx]
   ============================================================ */

const path = require("path");
const pptxgen = require("pptxgenjs");

const OUT = process.argv[2] || "IGIS-KAMCO-sample-deck.pptx";
const LAYOUTS_ONLY = process.argv.includes("--layouts-only");
const ROOT = path.join(__dirname, "..", "..");
const LOGOS = path.join(ROOT, "assets", "Logos");
const TOKENS = require(path.join(ROOT, "tokens.json"));

// ---- Tokens ----
const C = Object.fromEntries(TOKENS.color.tokens.map((t) => [t.name, t.value.replace("#", "").toUpperCase()]));
const SP = Object.fromEntries(TOKENS.spacing.tokens.map((t) => [t.name, parseFloat(t.value)]));
const { navy: NAVY, gray: GRAY, blue: BLUE, sky: SKY, white: WHITE } = C;

const F = { R: "Pretendard", M: "Pretendard Medium", SB: "Pretendard SemiBold" };
const REG = { fontFace: F.R, bold: false };
const MED = { fontFace: F.M, bold: false };
const SEMI = { fontFace: F.SB, bold: false };
const BOLD = { fontFace: F.R, bold: true };

const THEME = {
  name: "IGIS KAMCO",
  headFontFace: F.SB,
  bodyFontFace: F.R,
  colors: {
    dk1: "000000", lt1: WHITE, dk2: NAVY, lt2: C["gray-200"],
    accent1: BLUE, accent2: NAVY, accent3: SKY, accent4: GRAY, accent5: C["gray-400"], accent6: C["gray-300"],
    hlink: BLUE, folHlink: NAVY,
  },
};

const px = (n) => n / 96; // canvas px → inches
const pt = (n) => +(n * 0.75).toFixed(2); // canvas px → points
const W = 1280, H = 720;
const MX = SP["margin-x"], CONTENT_W = W - 2 * MX;
const TOP = SP["inset-top"], TITLE_Y = SP["header-title-y"];
const CT = SP["content-top"], CT_COMPACT = SP["content-top-compact"], CB = SP["content-bottom"];
const FOOTER_Y = SP["footer-y"];
const HAIR = 0.75; // stroke-hair, pt

const LOGO_PRIMARY = { w: 1170, h: 273 }, LOGO_WORDMARK = { w: 602, h: 145 };
const img = (file, x, y, h, dims) => ({
  image: { path: path.join(LOGOS, file), x: px(x), y: px(y), h: px(h), w: px((h * dims.w) / dims.h) },
});
// Solid fills only: no transparency, gradient or shadow (they print differently from the screen)
const rect = (x, y, w, h, color) => ({
  rect: { x: px(x), y: px(y), w: px(w), h: px(h), fill: { color }, line: { type: "none" } },
});
const text = (t, x, y, w, h, o) => ({
  text: { text: t, options: { x: px(x), y: px(y), w: px(w), h: px(h), margin: 0, ...REG, valign: "middle", ...o } },
});
const ph = (name, type, prompt, x, y, w, h, o) => ({
  placeholder: {
    options: { name, objectName: name, type, x: px(x), y: px(y), w: px(w), h: px(h), margin: 0, ...REG, align: "left", valign: "top", ...o },
    text: prompt,
  },
});

// Navy is allowed on the cover and section dividers only; every other slide is white.
// One deck serves both presenting and print: no separate print variants.
const TONES = {
  navy: {
    bg: NAVY, logo: "logo-primary-white.png", wordmark: "logo-wordmark-white.png",
    title: WHITE, kicker: SKY, meta: C["on-navy-72"], sub: C["on-navy-60"],
    foot: C["on-navy-55"], sep: C["on-navy-45"],
  },
  white: {
    bg: WHITE, logo: "logo-primary.png", wordmark: "logo-wordmark.png",
    title: NAVY, kicker: BLUE, meta: GRAY, sub: C["gray-500"],
    foot: C["gray-500"], sep: C["gray-400"], fine: C["gray-500"], value: GRAY,
  },
};

// ---- Footer: left = Source · Unit · As-of placeholder, right = {wordmark} _ {page} ----
function footer(tone, defaultLeft, x = MX, w = 900) {
  const t = TONES[tone];
  const y = FOOTER_Y;
  return {
    objects: [
      ph("footer", "body", defaultLeft || "Source: 출처 · 단위: — · 'YY.MM.DD 기준", x, y, w, 18,
        { fontSize: 9, color: t.foot, valign: "middle" }),
      img(t.wordmark, W - MX - 28 - 20 - 54, y + 2.5, 13, LOGO_WORDMARK),
      text("_", W - MX - 28 - 20, y, 20, 18, { fontSize: 9, color: t.sep, align: "center" }),
    ],
    slideNumber: { x: px(W - MX - 28), y: px(y), w: px(28), h: px(18), fontFace: F.R, fontSize: 9, color: t.foot, align: "right", valign: "middle", margin: 0 },
  };
}

// Standard-body header: eyebrow + action title (+ lead), all on the left rail.
// No decorative dash before the eyebrow and no accent lines.
function header({ lead }) {
  const o = [
    ph("eyebrow", "body", "섹션명 · EYEBROW", MX, TOP, 900, 17,
      { fontSize: pt(13), ...SEMI, color: NAVY, charSpacing: 1.6, valign: "middle" }),
    ph("title", "title", "결론을 한 문장으로 쓰는 액션 타이틀", MX, TITLE_Y, CONTENT_W, 50,
      { fontSize: 28, ...SEMI, color: NAVY, valign: "middle" }),
  ];
  if (lead) o.push(ph("lead", "body", "제목을 보충하는 리드 문장 한 줄 (선택)", MX, 96, 1060, 28,
    { fontSize: pt(19), color: GRAY, valign: "middle" }));
  return o;
}
const cornerMark = () => [rect(0, 0, 30, 3, BLUE), rect(0, 0, 3, 30, BLUE)];

function defineCover(pres, title) {
  const t = TONES.navy, f = footer("navy", "본 자료는 정보제공 목적이며 투자권유를 구성하지 않습니다.");
  pres.defineSlideMaster({
    title,
    background: { color: t.bg },
    objects: [
      img(t.logo, MX, 36, 30, LOGO_PRIMARY),
      text("Investing in\nLasting Values", W - MX - 300, 36, 300, 46,
        { fontSize: pt(15), color: t.meta, align: "right", valign: "top", charSpacing: 0.4, lineSpacingMultiple: 1.2 }),
      ph("eyebrow", "body", "사업명 · 제안 발표", MX, 377, 900, 20,
        { fontSize: pt(14), ...SEMI, color: t.kicker, charSpacing: 2, valign: "middle" }),
      ph("title", "title", "표지 제목\n두 줄까지", MX, 405, 1100, 140,
        { fontSize: pt(62), ...BOLD, color: t.title, lineSpacingMultiple: 0.95 }),
      ph("meta", "body", "2025. 06  ·  제안사  ·  IGIS Asset Management", MX, 566, 1000, 22,
        { fontSize: pt(15), color: t.meta, valign: "middle" }),
      ...f.objects,
    ],
    slideNumber: f.slideNumber,
  });
}

function defineSection(pres, title) {
  const t = TONES.navy, f = footer("navy", "Investing in Lasting Values");
  // No translucent band or ghost numeral: both print differently from the screen.
  pres.defineSlideMaster({
    title,
    background: { color: t.bg },
    objects: [
      ph("number", "body", "SECTION 01", MX, 300, 600, 22,
        { fontSize: pt(16), ...SEMI, color: t.kicker, charSpacing: 1.2, valign: "middle" }),
      ph("title", "title", "섹션 타이틀", MX, 326, 1100, 64,
        { fontSize: pt(52), ...BOLD, color: t.title, valign: "middle" }),
      ph("subtitle", "body", "Section title in English", MX, 394, 1100, 28,
        { fontSize: pt(18), color: t.sub, valign: "middle" }),
      ...f.objects,
    ],
    slideNumber: f.slideNumber,
  });
}

function defineClosing(pres, title) {
  const t = TONES.white, f = footer("white", "© 2025 IGIS Asset Management");
  const contact = (i, k, v) => [
    text(k, MX + i * 300, 548, 280, 16, { fontSize: pt(12), ...SEMI, color: t.kicker, charSpacing: 1.3 }),
    ph(`contact ${i + 1}`, "body", v, MX + i * 300, 570, 280, 24, { fontSize: pt(17), color: t.value, valign: "middle" }),
  ];
  pres.defineSlideMaster({
    title,
    background: { color: t.bg },
    objects: [
      img(t.logo, MX, 36, 28, LOGO_PRIMARY),
      ph("eyebrow", "body", "Q&A · THANK YOU", MX, 230, 600, 20,
        { fontSize: pt(14), ...SEMI, color: t.kicker, charSpacing: 2, valign: "middle" }),
      ph("title", "title", "Investing in\nLasting Values", MX, 262, 1100, 130,
        { fontSize: pt(56), ...BOLD, color: t.title, lineSpacingMultiple: 0.95 }),
      ...contact(0, "INVESTOR RELATIONS", "ir@igisam.com"),
      ...contact(1, "TEL", "+82 2 0000 0000"),
      ...contact(2, "ADDRESS", "서울특별시 영등포구 국제금융로"),
      ph("disclaimer", "body", "면책 문구", MX, 636, 900, 30,
        { fontSize: pt(12), color: t.fine, lineSpacingMultiple: 1.15 }),
      ...f.objects,
    ],
    slideNumber: f.slideNumber,
  });
}

function defineLayouts(pres) {
  defineCover(pres, "IGIS 01 표지");

  // 2 — Contents (TOC): left panel with logo + heading, right = numbered list
  const fToc = footer("white", "IGIS Asset Management", 48, 290);
  pres.defineSlideMaster({
    title: "IGIS 02 목차",
    background: { color: WHITE },
    objects: [
      rect(359, 0, 1, H, C["gray-300"]),
      img("logo-primary.png", 48, 36, 26, LOGO_PRIMARY),
      text("CONTENTS", 48, 290, 280, 18, { fontSize: pt(13), ...SEMI, color: C["gray-500"], charSpacing: 1.6 }),
      text("목차", 48, 314, 280, 46, { fontSize: pt(40), ...BOLD, color: NAVY }),
      text("Agenda", 48, 360, 280, 46, { fontSize: pt(40), ...BOLD, color: BLUE }),
      ...fToc.objects,
    ],
    slideNumber: fToc.slideNumber,
  });

  defineSection(pres, "IGIS 03 섹션 간지");

  // 4 — Standard body: corner mark + header + free body placeholder
  const fStd = footer("white");
  pres.defineSlideMaster({
    title: "IGIS 04 표준 본문",
    background: { color: WHITE },
    objects: [
      ...cornerMark(), ...header({ lead: true }),
      ph("body", "body", "본문 — Pretendard 13pt, 좌측 정렬 (하한 12pt)", MX, CT, CONTENT_W, CB - CT,
        { fontSize: pt(17), color: GRAY, lineSpacingMultiple: 1.3, paraSpaceAfter: 6 }),
      ...fStd.objects,
    ],
    slideNumber: fStd.slideNumber,
  });

  // 4b — Header + lead only, content composed on the slide (KPI rows, tables, cards)
  const fLead = footer("white");
  pres.defineSlideMaster({
    title: "IGIS 04b 제목+리드",
    background: { color: WHITE },
    objects: [...cornerMark(), ...header({ lead: true }), ...fLead.objects],
    slideNumber: fLead.slideNumber,
  });

  // 5 — Two panel: matching panel headers on one baseline, separation by whitespace
  const fTwo = footer("white");
  const GAP = SP["gap-panel"], PANEL_W = (CONTENT_W - GAP) / 2;
  const panel = (key, x, chip, chipColor, heading, tagline) => [
    rect(x, CT_COMPACT, 26, 26, chipColor),
    text(chip, x, CT_COMPACT, 26, 26, { fontSize: pt(14), ...SEMI, color: WHITE, align: "center" }),
    ph(`${key} heading`, "body", heading, x + 38, CT_COMPACT, PANEL_W - 38, 26,
      { fontSize: pt(22), ...SEMI, color: NAVY, valign: "middle" }),
    rect(x, CT_COMPACT + 38, PANEL_W, 1.67, NAVY),
    ph(`${key} body`, "body", "핵심 항목. 설명 문장", x, CT_COMPACT + 58, PANEL_W, CB - 52 - (CT_COMPACT + 58),
      { fontSize: pt(17), color: GRAY, lineSpacingMultiple: 1.25 }),
    rect(x, CB - 40, PANEL_W, 1, C["gray-300"]),
    ph(`${key} tag`, "body", tagline, x, CB - 26, PANEL_W, 24,
      { fontSize: pt(14), ...MED, color: C["gray-500"], valign: "middle" }),
  ];
  pres.defineSlideMaster({
    title: "IGIS 05 2-패널",
    background: { color: WHITE },
    objects: [
      ...header({ lead: false }),
      ...panel("panel A", MX, "A", NAVY, "패널 A 제목", "요약 지표 · 조건"),
      ...panel("panel B", MX + PANEL_W + GAP, "B", BLUE, "패널 B 제목", "요약 지표 · 조건"),
      ...fTwo.objects,
    ],
    slideNumber: fTwo.slideNumber,
  });

  // 6 — Data / table: header + full-width chart placeholder; Source·Unit·As-of footer
  const fData = footer("white");
  pres.defineSlideMaster({
    title: "IGIS 06 데이터·표",
    background: { color: WHITE },
    objects: [
      ...cornerMark(), ...header({ lead: false }),
      ph("chart", "chart", "차트 삽입 — 강조 1색(BLUE), 나머지 회색", MX, CT_COMPACT, CONTENT_W, CB - CT_COMPACT,
        { fontSize: 12, color: C["gray-500"] }),
      ...fData.objects,
    ],
    slideNumber: fData.slideNumber,
  });

  defineClosing(pres, "IGIS 07 클로징");
}

// ---------------- Sample slides ----------------
function addSamples(pres) {
  const SECTION = "IGIS 아키타입";
  pres.addSection({ title: SECTION });
  const add = (masterName) => pres.addSlide({ masterName, sectionTitle: SECTION });

  // 01 Cover
  {
    const s = add("IGIS 01 표지");
    s.addText("한국자산관리공사 · 제안 발표", { placeholder: "eyebrow" });
    s.addText("국내 최대 부동산\n자산운용 플랫폼", { placeholder: "title" });
    s.addText("2025. 06  ·  제안사 IGIS Asset Management", { placeholder: "meta" });
    s.addText("본 자료는 정보제공 목적이며 투자권유를 구성하지 않습니다.", { placeholder: "footer" });
  }

  // 02 Contents — numbered list between rules (table: num / name / English)
  let s = add("IGIS 02 목차");
  const items = [
    ["01", "운용 전략 및 차별화", "Investment Strategy"],
    ["02", "운용자산 현황", "Assets Under Management"],
    ["03", "트랙 레코드 및 성과", "Track Record"],
    ["04", "리스크 관리 체계", "Risk Management"],
    ["05", "ESG 및 향후 계획", "ESG & Outlook"],
  ];
  const rowLine = { type: "solid", pt: HAIR, color: C["gray-300"] };
  const none = { type: "none" };
  const rows = items.map((r, i) => {
    const border = [i === 0 ? { type: "solid", pt: 1.25, color: NAVY } : none, none, rowLine, none];
    return [
      { text: r[0], options: { fontSize: pt(20), ...SEMI, color: BLUE, border } },
      { text: r[1], options: { fontSize: pt(22), ...MED, color: NAVY, border } },
      { text: r[2], options: { fontSize: pt(13), color: C["gray-500"], align: "right", border } },
    ];
  });
  s.addTable(rows, {
    x: px(424), y: px(176), w: px(792), colW: [px(84), px(440), px(268)], rowH: px(74),
    fontFace: F.R, valign: "middle", margin: 0, objectName: "TOC list",
  });
  s.addText("IGIS Asset Management", { placeholder: "footer" });

  // 03 Section divider
  {
    s = add("IGIS 03 섹션 간지");
    s.addText("SECTION 01", { placeholder: "number" });
    s.addText("운용 전략 및 차별화", { placeholder: "title" });
    s.addText("Investment Strategy & Differentiation", { placeholder: "subtitle" });
    s.addText("Investing in Lasting Values", { placeholder: "footer" });
  }

  // 04 Standard body — KPI row + two-column copy
  s = add("IGIS 04b 제목+리드");
  s.addText("운용자산 현황 · AUM", { placeholder: "eyebrow" });
  s.addText([
    { text: "부동산 전 섹터에 걸친 " },
    { text: "68조원 규모", options: { color: BLUE } },
    { text: "의 운용 플랫폼" },
  ], { placeholder: "title" });
  s.addText("오피스·물류·리테일·주거 및 대체자산까지, 핵심 입지 중심의 분산된 포트폴리오를 운용합니다.", { placeholder: "lead" });
  const kpis = [
    ["68.2", "조원", "운용자산(AUM)", "'24.12.31 기준", BLUE],
    ["142", "개", "운용 펀드 수", "실물·재간접 합산", NAVY],
    ["2.3", "x", "평균 투자 멀티플", "청산 펀드 기준", NAVY],
  ];
  const kw = CONTENT_W / 3;
  s.addShape(pres.ShapeType.rect, { x: px(MX), y: px(CT), w: px(CONTENT_W), h: px(1.67), fill: { color: NAVY }, line: { type: "none" }, objectName: "KPI rule" });
  kpis.forEach(([v, u, l, c, col], i) => {
    const x = MX + i * kw + 28;
    if (i > 0) s.addShape(pres.ShapeType.rect, { x: px(MX + i * kw), y: px(CT + 2), w: px(1), h: px(170), fill: { color: C["gray-300"] }, line: { type: "none" }, objectName: `KPI divider ${i}` });
    s.addText([
      { text: v, options: { fontSize: pt(52), ...SEMI, color: col } },
      { text: " " + u, options: { fontSize: pt(22), ...MED, color: GRAY } },
    ], { x: px(x), y: px(CT + 26), w: px(kw - 56), h: px(56), margin: 0, valign: "bottom", isTextBox: true, objectName: `KPI ${i + 1} value` });
    s.addText(l, { x: px(x), y: px(CT + 96), w: px(kw - 56), h: px(24), margin: 0, fontSize: pt(17), ...MED, color: NAVY, isTextBox: true, objectName: `KPI ${i + 1} label` });
    s.addText(c, { x: px(x), y: px(CT + 124), w: px(kw - 56), h: px(20), margin: 0, fontSize: pt(13), ...REG, color: C["gray-500"], isTextBox: true, objectName: `KPI ${i + 1} note` });
  });
  const colW = (CONTENT_W - SP["gap-block"]) / 2;
  const copy = (runs, x, name) => s.addText(runs, { x: px(x), y: px(CT + 204), w: px(colW), h: px(90), margin: 0, valign: "top", fontSize: pt(17), ...REG, color: GRAY, lineSpacingMultiple: 1.3, isTextBox: true, objectName: name });
  copy([
    { text: "코어·코어플러스 전략", options: { ...SEMI, color: NAVY } },
    { text: "을 중심으로 안정적 현금흐름을 확보하고, 선별적 " },
    { text: "밸류애드", options: { ...SEMI, color: BLUE } },
    { text: " 기회를 통해 초과수익을 추구합니다." },
  ], MX, "Body copy left");
  copy([
    { text: "전 과정에 걸친 " },
    { text: "리스크 관리 체계", options: { ...SEMI, color: NAVY } },
    { text: "와 내재화된 운용 역량으로 시장 사이클 전반에서 일관된 성과를 지향합니다." },
  ], MX + colW + SP["gap-block"], "Body copy right");
  s.addText("Source: IGIS Research · 단위: 조원 · '24.12.31 기준", { placeholder: "footer" });

  // 05 Two panel
  s = add("IGIS 05 2-패널");
  s.addText("운용 전략 · 비교", { placeholder: "eyebrow" });
  s.addText([
    { text: "전략별 역할 분담으로 " },
    { text: "위험·수익", options: { color: BLUE } },
    { text: "의 균형 추구" },
  ], { placeholder: "title" });
  const bullets = (list) => list.flatMap(([b, rest], i) => [
    { text: b + " ", options: { ...SEMI, color: NAVY } },
    { text: rest, options: { breakLine: i < list.length - 1 } },
  ]);
  s.addText("코어 · 코어플러스", { placeholder: "panel A heading" });
  s.addText(bullets([
    ["안정적 배당.", "우량 임차인 중심 장기 계약으로 예측 가능한 현금흐름 확보"],
    ["핵심 입지.", "권역 내 상위 자산에 집중, 공실 리스크 최소화"],
    ["낮은 변동성.", "시장 사이클 전반에서 방어적 포지션 유지"],
  ]), { placeholder: "panel A body" });
  s.addText("목표 IRR 6–8% · 보유기간 7년+", { placeholder: "panel A tag" });
  s.addText("밸류애드", { placeholder: "panel B heading" });
  s.addText(bullets([
    ["가치 제고.", "리모델링·임차 구조 개선으로 자산 가치 상승 견인"],
    ["선별적 진입.", "명확한 출구 전략이 확보된 기회에 한정"],
    ["초과수익.", "운용 역량 기반의 적극적 자산관리로 알파 창출"],
  ]), { placeholder: "panel B body" });
  s.addText("목표 IRR 10–13% · 보유기간 3–5년", { placeholder: "panel B tag" });
  s.addText("Source: IGIS Research · 목표 수익률은 예시이며 실현을 보장하지 않습니다 (E)", { placeholder: "footer" });

  // 06 Data — native waterfall (stacked column with an invisible base series).
  // postprocess.py hides the base series, recolors and relabels the bars.
  s = add("IGIS 06 데이터·표");
  s.addText("성과 분석 · Waterfall", { placeholder: "eyebrow" });
  s.addText([
    { text: "기말 가치 증가는 " },
    { text: "단가 상승", options: { color: BLUE } },
    { text: "이 주도" },
  ], { placeholder: "title" });
  const labels = ["기초", "신규", "이탈", "단가", "기말"];
  s.addChart(pres.ChartType.bar, [
    { name: "base", labels, values: [0, 100, 116, 116, 0] },
    { name: "기초", labels, values: [100, 0, 0, 0, 0] },
    { name: "증가", labels, values: [0, 38, 0, 0, 0] },
    { name: "감소", labels, values: [0, 0, 22, 0, 0] },
    { name: "강조", labels, values: [0, 0, 0, 30, 0] },
    { name: "기말", labels, values: [0, 0, 0, 0, 146] },
  ], {
    objectName: "Waterfall chart",
    x: px(MX), y: px(CT_COMPACT), w: px(CONTENT_W), h: px(CB - CT_COMPACT - 40),
    barDir: "col", barGrouping: "stacked", barGapWidthPct: 120,
    chartColors: [WHITE, C["gray-300"], C["gray-300"], C["gray-200"], BLUE, NAVY],
    showLegend: false, showValue: true, dataLabelPosition: "inEnd",
    dataLabelFontFace: F.SB, dataLabelFontSize: 12, dataLabelColor: GRAY,
    catAxisLabelFontFace: F.R, catAxisLabelFontSize: pt(15), catAxisLabelColor: GRAY,
    catAxisLineShow: true, catAxisLineColor: C["gray-300"],
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    valAxisMinVal: 0, valAxisMaxVal: 160,
  });
  s.addText([
    { text: "■ ", options: { color: BLUE } },
    { text: "강조 1색: '단가' 기여만 BLUE, 나머지는 회색으로 배경화(gray-out)" },
  ], { x: px(MX), y: px(CB - 24), w: px(800), h: px(22), margin: 0, fontSize: pt(15), ...REG, color: GRAY, isTextBox: true, objectName: "Chart note" });
  s.addText("Source: 예시 데이터 (Illustrative) · 단위: 지수(기초=100) · '24.12.31 기준", { placeholder: "footer" });

  // 07 Closing
  {
    s = add("IGIS 07 클로징");
    s.addText("Q&A · THANK YOU", { placeholder: "eyebrow" });
    s.addText("Investing in\nLasting Values", { placeholder: "title" });
    s.addText("ir@igisam.com", { placeholder: "contact 1" });
    s.addText("+82 2 0000 0000", { placeholder: "contact 2" });
    s.addText("서울특별시 영등포구 국제금융로", { placeholder: "contact 3" });
    s.addText("본 자료는 정보제공을 목적으로 작성되었으며 투자권유 또는 청약의 권유를 구성하지 않습니다. 과거의 운용실적이 미래의 수익을 보장하지 않으며, 투자원금의 손실이 발생할 수 있습니다. 무단 복제·배포를 금합니다.", { placeholder: "disclaimer" });
    s.addText("© 2025 IGIS Asset Management", { placeholder: "footer" });
  }
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 × 7.5 in = 33.87 × 19.05 cm
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = "IGIS Asset Management";
  pres.company = "IGIS Asset Management";
  pres.title = "IGIS 제안서 디자인가이드-KAMCO";
  defineLayouts(pres);
  if (!LAYOUTS_ONLY) addSamples(pres);
  await pres.writeFile({ fileName: OUT });
  const { applyTheme } = require(process.env.APPLY_THEME || "./apply_theme.js");
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
