---
name: igis-kamco-proposal-design
description: Use this skill to build IGIS Asset Management (이지스자산운용) proposal presentation decks for public-enterprise audiences such as KAMCO (한국자산관리공사) — PowerPoint 16:9 for presenting and A4 landscape print. Contains the brand rules, tokens, static Pretendard fonts, logos, a PowerPoint template with 8 layouts, body-slide components and patterns, and a separate authoring guide for messages, evidence and number checks.
user-invocable: true
---

Read `README.md` first (in Korean). It lists every hard rule and points to the other files.

This system is for **PowerPoint and print only**. The HTML in `body/` and the CSS in `tokens/`
exist so Claude Design can read the system; the deliverable is still a 16:9 deck.

Key files:
- `templates/IGIS-KAMCO-template.potx` — start every deck from this template's layouts.
  One deck serves both presenting and print; there are no separate print layouts.
- `IGIS_Deck_Authoring_Guide_v2.md` — what to say on each body slide and which slide type /
  pattern / component to use (§6 has 10 content types with exact references). Read it before
  writing body slides.
- `body-components.md` — visual rules for body components BC-01..BC-09 and patterns BP-1..BP-6.
- `slide-types.md` — body slide-type catalog (S, N, C, R, P, K, D IDs) with usage conditions.
- `body/bp*.html` — six rendered body-pattern examples (all numbers are fictional).
- `tokens.json` — colors, type sizes, zone lines (1280×720 px canvas; pt = px × 0.75).
- `change-policy.md` — locked rules vs. extendable body types, and the body-only exception procedure.
- `CHANGELOG_v2.md` — what v2 changed and why.
- `fonts/` — static Pretendard TTFs (Regular, Medium, SemiBold, Bold). `assets/Logos/` — logos.

Non-negotiables:
- Cover, TOC, section divider and closing (IGIS 01/02/03/07) are fixed: do not restyle them, and do
  not apply body components or patterns to them.
- Pretendard only; hierarchy by weight ("Pretendard", "Pretendard Medium", "Pretendard SemiBold",
  Bold via the bold flag on "Pretendard"). Never bold the Medium/SemiBold families.
- Palette HEX only; 1–2 accent colors per slide, the rest grayed out.
- Navy full-bleed backgrounds on the cover and section dividers only; every other slide is white.
- No decorative horizontal lines (no dash before eyebrows, no short accent lines, no brackets or
  arrows on change labels).
- Action titles (conclusion sentences). Source · Unit · As-of on every chart and table; longer
  conditions (definitions, sample, FX, rounding) go in the BC-05 notes block.
- Bars start at zero; no axis breaks; no bubble charts or color-scale heatmaps.
- Nothing that prints differently from the screen: no shadows, transparency, gradients,
  glow, 3-D, fills lighter than gray-200 (#E2E2E2), lines under 0.75pt, text under 9pt, Light weight.
- Only use IDs that exist in these files; never invent component names or numbers. Mark
  illustrative data as such.

If invoked without guidance, ask what the deck is for (the call for proposals, its evaluation
criteria and page limit, the audience) before building.
