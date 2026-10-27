"""Generate the Claude Design CSS layer from tokens.json (the single source of values).

Writes tokens/fonts.css, tokens/colors.css, tokens/type.css, tokens/spacing.css.
styles.css (hand-written, @import lines only) links them.

Usage: python3 tools/gen_tokens_css.py   (run from the design-system root)
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
T = json.loads((ROOT / "tokens.json").read_text())
OUT = ROOT / "tokens"
OUT.mkdir(exist_ok=True)
HEAD = "/* Generated from tokens.json by tools/gen_tokens_css.py. Do not edit by hand. */\n"

# Fonts: static Pretendard. One CSS family ("Pretendard", weights 400–700) plus the
# PowerPoint family names ("Pretendard Medium", "Pretendard SemiBold") for parity.
fonts = [HEAD]
for f in T["type"]["fonts"]:
    w = f["weight"]
    fonts.append(
        '@font-face { font-family: "Pretendard"; font-weight: %s; font-style: normal; '
        'font-display: swap; src: url("../%s") format("truetype"); }\n' % (w, f["file"])
    )
    if f["family"] != "Pretendard":
        fonts.append(
            '@font-face { font-family: "%s"; font-weight: %s; font-style: normal; '
            'font-display: swap; src: url("../%s") format("truetype"); }\n' % (f["family"], w, f["file"])
        )
(OUT / "fonts.css").write_text("".join(fonts))

colors = [HEAD, ":root {\n"]
for c in T["color"]["tokens"]:
    colors.append("  --%s: %s; /* %s */\n" % (c["name"], c["value"], c["usage"].split(".")[0]))
colors.append("}\n")
(OUT / "colors.css").write_text("".join(colors))

type_css = [HEAD, ":root {\n", '  --font-sans: "Pretendard", "Malgun Gothic", sans-serif;\n']
for g in T["type"]["groups"]:
    for s in g["styles"]:
        type_css.append("  --text-%s: %s;\n" % (s["name"], s["fontSize"]))
type_css.append("  --weight-regular: 400;\n  --weight-medium: 500;\n  --weight-semibold: 600;\n  --weight-bold: 700;\n}\n")
(OUT / "type.css").write_text("".join(type_css))

sp = [HEAD, ":root {\n"]
for fam in ("spacing", "radius", "stroke"):
    for t in T[fam]["tokens"]:
        sp.append("  --%s: %s;\n" % (t["name"], t["value"]))
sp.append("}\n")
(OUT / "spacing.css").write_text("".join(sp))
print("wrote", ", ".join(p.name for p in sorted(OUT.glob("*.css"))))
