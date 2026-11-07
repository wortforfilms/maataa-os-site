#!/usr/bin/env python3
"""Writes the product concept pages (public/products/<slug>.html) and the
products index from content/products.json, using portfolio.html as the page
shell (head, header, footer). Also links the six cards on the portfolio page.

Run after tools/models.py (which makes the 3D files) and before tools/check.py.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
D = json.loads((ROOT / "content/products.json").read_text())
FACTS = json.loads((ROOT / "content/facts.json").read_text())
e = html.escape
shell = (PUB / "portfolio.html").read_text()
HEAD, rest = shell.split('<main id="main">', 1)
FOOT = rest.split("</main>", 1)[1]

CSS = """
/* product concept pages */
.phero{position:relative;overflow:hidden;background:radial-gradient(1200px 500px at 85% 20%,rgba(255,154,31,.16),transparent 60%),linear-gradient(160deg,#1F2A5C 0%,#10151F 70%);color:#E8EDF8;border-bottom:1px solid var(--line)}
.phero .wrap{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:32px;align-items:center;padding-top:56px;padding-bottom:48px}
.phero h1{font-size:clamp(32px,4.6vw,54px);line-height:1.05;color:#fff}
.phero .hook{font-size:20px;color:#C9D2EA;margin:18px 0 0;max-width:640px}
.phero .eyebrow{color:#FFB255}
.phero .art{position:relative;border-radius:20px;background:#F7F7F7;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.phero .art img{display:block;width:100%;height:auto;border-radius:20px}
.phero .art::after{content:"";position:absolute;inset:auto 18px -10px 18px;height:8px;border-radius:0 0 12px 12px;background:#FF9A1F;opacity:.9}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}
.chip{font:600 13px 'JetBrains Mono',monospace;letter-spacing:.04em;border:1px solid rgba(232,237,248,.35);border-radius:999px;padding:6px 12px;color:#E8EDF8}
.chip.warn{border-color:#FF9A1F;color:#FFB255}
.phero .jump{margin:26px 0 0;padding:0}.phero .jump a{color:#E8EDF8;border-color:rgba(232,237,248,.35)}
@media (max-width:860px){.phero .wrap{grid-template-columns:minmax(0,1fr)}}
.cards3{margin-top:22px;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:18px}
.card{background:var(--bg2);border:1px solid var(--line);border-radius:14px;padding:20px 22px}
.card h3{font-size:19px;margin:0 0 6px}.card p{margin:0;color:var(--soft);font-size:16px}
.card .k{font:600 12px 'JetBrains Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--acc);margin:0 0 8px}
.glance{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:28px;align-items:start}
.glance dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:10px 16px;background:var(--bg2);border:1px solid var(--line);border-radius:14px;padding:20px 22px}
.glance dt{font:600 12px 'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);padding-top:3px}.glance dd{margin:0;color:var(--soft)}
@media (max-width:860px){.glance{grid-template-columns:minmax(0,1fr)}}
.viewer{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:28px;align-items:start}
@media (max-width:860px){.viewer{grid-template-columns:minmax(0,1fr)}}
.stage{border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#F7F7F7}
.tt{aspect-ratio:4/3;background-repeat:no-repeat;background-size:2400% 100%;background-position:0 0;animation:tt 8s steps(23) infinite}
.tt:hover{animation-play-state:paused}
@keyframes tt{to{background-position:100% 0}}
.stage{display:flex;flex-wrap:wrap;gap:6px;padding:0 0 10px;background:#fff}.stage>.tt{order:-1;flex-basis:100%;border-bottom:1px solid #DDD;margin-bottom:4px;background-color:#F7F7F7}.stage label:first-of-type{margin-left:10px}
.stage input{position:absolute;opacity:0;width:1px;height:1px}
.stage label{cursor:pointer;min-height:44px;min-width:44px;display:inline-flex;align-items:center;justify-content:center;padding:0 12px;border:1px solid #C9CDD8;border-radius:10px;font:600 13px 'JetBrains Mono',monospace;color:#14182E}
.stage input:checked+label{background:#1F2A5C;color:#fff;border-color:#1F2A5C}
.stage input:focus-visible+label{outline:3px solid var(--acc-fill);outline-offset:2px}
.files{width:100%;min-width:0;table-layout:fixed;border-collapse:collapse;font-size:15px}.files td:first-child{overflow-wrap:anywhere}.files col.c1{width:46%}.files col.c3{width:76px}.files td,.files th{padding:10px 8px;border-bottom:1px solid var(--line);text-align:left}.files th{background:transparent;font:600 12px 'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.files td:last-child{white-space:nowrap;color:var(--mut)}
.bp{border-radius:14px;overflow:hidden;border:1px solid var(--line);background:#1F2A5C}.bp img{display:block;width:100%;height:auto}
.scrollx{overflow-x:auto}.scrollx .bp{min-width:640px}
.feat{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:16px}
.feat .card h3{font-size:18px}.feat .card .note{margin-top:10px;font-size:15px;color:var(--ink);border-left:3px solid var(--acc-fill);padding-left:10px}
ul.ny{margin:8px 0 0;padding-left:20px;color:var(--soft)}ul.ny li{margin:4px 0}
.safety{border:2px solid #FF9A1F;border-radius:14px;padding:18px 22px;background:rgba(255,154,31,.08);margin-top:22px}.safety b{color:var(--acc)}
.guides{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(320px,100%),1fr));gap:18px}
.guide{background:var(--bg2);border:1px solid var(--line);border-radius:16px;padding:22px 24px}
.guide h3{font-size:22px;margin:0}.guide .who{font:600 12px 'JetBrains Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--acc);margin:0 0 6px}
.guide ol,.guide ul{padding-left:20px;margin:10px 0 0;color:var(--soft)}.guide li{margin:6px 0}
.guide .flag{font-size:13px;color:var(--mut);margin:12px 0 0}
.prodnav{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:12px}
.prodnav a{display:flex;gap:12px;align-items:center;border:1px solid var(--line);border-radius:12px;padding:10px;text-decoration:none;color:var(--ink);min-height:44px}
.prodnav a:hover{border-color:var(--acc)}.prodnav img{width:72px;height:54px;object-fit:cover;border-radius:8px;background:#F7F7F7}
.pi .more{margin-top:4px;font-size:14px;font-weight:600}
.band.light a:not(.btn){color:#A65200}
"""

def page(title, desc, body, path):
    h = HEAD.replace("<title>Portfolio · MAATAA OS</title>", f"<title>{e(title)} · MAATAA OS</title>")
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', h)
    h = h.replace("</style>", CSS + "</style>", 1)
    (PUB / path).parent.mkdir(parents=True, exist_ok=True)
    (PUB / path).write_text(h + '<main id="main">\n' + body + "\n</main>" + FOOT)

def kib(p): return f"{p.stat().st_size / 1024:.0f} KiB"

ANG = [(0, "Spin"), (0, "0°"), (4, "60°"), (8, "120°"), (12, "180°"), (16, "240°"), (20, "300°")]

def viewer(p):
    base = f'/products/files/{p["slug"]}'
    css = []
    radios = []
    for i, (f, lab) in enumerate(ANG):
        rid = f'v{i}'
        radios.append(f'<input type="radio" name="ang" id="{rid}"{" checked" if i == 0 else ""}><label for="{rid}">{lab}</label>')
        if i:
            css.append(f'#{rid}:checked~.tt{{animation:none;background-position:{f*100/23:.4f}% 0}}')
    # the stage sits after the radios so the ~ selector reaches it
    return (f'<style>{"".join(css)}</style>'
            f'<div class="stage" role="group" aria-label="View angle">{"".join(radios)}'
            f'<div class="tt" role="img" aria-label="Turntable view of the {e(p["name"])} concept enclosure" '
            f'style="background-image:url({base}/turntable.webp)"></div></div>')

def product(p):
    F = D["features"]; s = p["slug"]; base = f"/products/files/{s}"; out = PUB / "products/files" / s
    tier = {"A": "A · today's MCU class", "A+C": "A + C · MAATAA inside", "B": "B · bigger MCU"}.get(p["tier"], p["tier"])
    jump = [("uses", "Use cases"), ("view", "3D view"), ("blueprint", "Blueprint"), ("os", "MAATAA OS"), ("guides", "Guides"), ("print", "3D print")]
    b = []
    b.append(f'<section class="phero"><div class="wrap"><div><p class="eyebrow">Product concept · {e(p["category"])}</p>'
             f'<h1>{e(p["name"])}</h1><p class="hook">{e(p["hook"])}</p>'
             f'<div class="chips"><span class="chip warn">Concept · not a product</span><span class="chip">Tier {e(tier)}</span><span class="chip">Open 3D files</span></div>'
             f'<nav class="jump" aria-label="On this page">{"".join(f"<a href=#{a}>{t}</a>" for a, t in jump)}</nav></div>'
             f'<div class="art"><img src="{base}/hero.webp" alt="Exploded CAD view of the {e(p["name"])} concept enclosure, lid lifted" width="1400" height="1000"></div></div></section>')
    b.append(f'<section class="band"><div class="wrap glance"><div><p class="eyebrow">At a glance</p><h2>What it is</h2><p class="intro">{e(p["summary"])}</p></div>'
             f'<dl><dt>Status</dt><dd>Concept. No hardware has been built or tested.</dd><dt>Tier</dt><dd>{e(tier)}</dd>'
             f'<dt>Enclosure</dt><dd>{e(p["form"])}</dd><dt>Portfolio</dt><dd><a href="/portfolio">{e(p["portfolio"])}</a></dd></dl></div></section>')
    b.append('<section class="band light" id="uses"><div class="wrap"><p class="eyebrow">Use cases</p><h2>Where it would work</h2><div class="cards3">'
             + "".join(f'<div class="role"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in p["uses"]) + '</div></div></section>')
    files = [(f"{s}.3mf", "Both parts on one plate (3MF)"), (f"{s}-base.stl", "Base (STL, print orientation)"),
             (f"{s}-lid.stl", "Lid (STL, print orientation)"), (f'{p["model"]}.scad', "Parametric source (OpenSCAD)"),
             ("maataa-lib.scad", "Shared library the source includes"), ("blueprint.svg", "Blueprint (SVG)")]
    rows = "".join(f'<tr><td><a href="{base}/{f}" download>{e(f)}</a></td><td>{e(t)}</td><td>{kib(out / f)}</td></tr>' for f, t in files)
    b.append(f'<section class="band" id="view"><div class="wrap viewer"><div>{viewer(p)}</div>'
             f'<div><p class="eyebrow">3D view</p><h2>Turn it around</h2><p class="intro">A turntable of 24 CAD renders of the printable enclosure, with a placeholder board inside. Pick an angle to stop it; hover pauses it. With reduced motion turned on, it stays still.</p>'
             f'<table class="files"><colgroup><col class="c1"><col><col class="c3"></colgroup><thead><tr><th>File</th><th>What</th><th>Size</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>')
    b.append(f'<section class="band light" id="blueprint"><div class="wrap"><p class="eyebrow">Blueprint</p><h2>Enclosure drawing</h2>'
             f'<p class="intro" style="color:var(--pmut)">Top view of the lid, front and side views of the closed enclosure, and a section through the base. Dimensions in millimetres, taken from the same model as the print files.</p>'
             f'<div class="scrollx" tabindex="0" role="region" aria-label="Blueprint, scrolls sideways on small screens"><div class="bp"><a href="{base}/blueprint.svg"><img src="{base}/blueprint.svg" alt="Blueprint of the {e(p["name"])} concept enclosure with top, front and side views, a section and a title block" width="1200" height="820" loading="lazy"></a></div></div></div></section>')
    feats = []
    for k in p["features"]:
        t, x = F[k]; n = p.get("feature_notes", {}).get(k)
        feats.append(f'<div class="card"><p class="k">Works today</p><h3>{e(t)}</h3><p>{e(x)}</p>' + (f'<p class="note">Here: {e(n)}</p>' if n else "") + "</div>")
    saf = f'<div class="safety"><b>Safety.</b> {e(p["safety"])}</div>' if p.get("safety") else ""
    b.append(f'<section class="band" id="os"><div class="wrap"><p class="eyebrow">MAATAA OS</p><h2>What the OS brings, and what is missing</h2>'
             f'<p class="intro">{e(D["today"])} Release {e(FACTS["release"])}.</p><div class="feat">{"".join(feats)}</div>'
             f'<div class="card" style="margin-top:18px"><p class="k">Not yet</p><h3>Work before this concept can run</h3><ul class="ny">'
             + "".join(f"<li>{e(x)}</li>" for x in p["notyet"]) + f'</ul></div>{saf}</div></section>')
    user = [p["mount"], p["wire"],
            "Commission it from a laptop over the service port: the host channel reports status and accepts signed setting changes.",
            "Leave it running. It keeps its settings and logs through a power cut.",
            "After any reset it reports why it reset. Send that report to the device maker."]
    maker = ["Pick the hardware from the class list below; the MCU must run MAATAA OS (the F411 today, the production board later).",
             "Bring up the board support: clocks, pins and the service UART.",
             "Add the missing drivers listed under Not yet as walled-off tasks, each with only the capabilities it needs in its signed manifest.",
             "Write the device logic as a signed capsule or a task; keep settings in the power-loss-safe store.",
             "Run the kernel's QEMU checks, then a power-cut test on your board, before any field unit.",
             "Print the enclosure from the files below, then change the parametric source to your real board."]
    partner = ["Tell us the device and the volume: partners@allb.xyz.",
               "We agree a pilot: one board, the missing drivers, and the tests that decide pass or fail.",
               "Licensing and support are priced per device and per year; porting to a new board is priced per project. The FAQ lists today's starting points.",
               "Before any field pilot: the production security profile on a second board and an outside review.",
               "You build and sell the hardware; we license and support the OS."]
    b.append('<section class="band light" id="guides"><div class="wrap"><p class="eyebrow">Guides</p><h2>For users, makers and partners</h2>'
             '<p class="intro" style="color:var(--pmut)">Concept briefs. They describe the intended use; none of the steps below is a tested procedure.</p><div class="guides">'
             f'<div class="role"><p class="meta">User guide</p><h3>Using it</h3><ol>{"".join(f"<li>{e(x)}</li>" for x in user)}</ol></div>'
             f'<div class="role"><p class="meta">Manufacturer guide</p><h3>Building it</h3><ol>{"".join(f"<li>{e(x)}</li>" for x in maker)}</ol>'
             f'<p style="margin-top:12px"><b style="color:var(--pink)">Hardware classes</b></p><ul>{"".join(f"<li>{e(x)}</li>" for x in p["bom"])}</ul>'
             '<p class="meta" style="margin-top:10px">Classes, not part numbers or prices: these depend on the maker.</p></div>'
             f'<div class="role"><p class="meta">Partner guide</p><h3>Working with us</h3><ol>{"".join(f"<li>{e(x)}</li>" for x in partner)}</ol>'
             '<p><a href="/faq#business">Business FAQ</a> · <a href="mailto:partners@allb.xyz?subject=MAATAA%20OS%20design%20partner">partners@allb.xyz</a></p></div>'
             '</div></div></section>')
    b.append(f'<section class="band" id="print"><div class="wrap glance"><div><p class="eyebrow">3D print</p><h2>Print the enclosure</h2>'
             f'<p class="intro">Two parts, exported in print orientation and checked to be closed solids. The board inside is a placeholder: change the sizes in <code>{e(p["model"])}.scad</code> when a real board exists.</p>'
             f'<ul class="ny">{"".join(f"<li>{e(x)}</li>" for x in p["print"])}</ul></div>'
             f'<dl><dt>Material</dt><dd>{e(p["material"])}</dd><dt>Layers</dt><dd>{e(p["layer"])} mm</dd><dt>Infill</dt><dd>{e(p["infill"])}</dd>'
             f'<dt>Walls</dt><dd>3 perimeters</dd><dt>Fasteners</dt><dd>{e(p["fasteners"])}</dd><dt>Files</dt><dd><a href="{base}/{s}.3mf" download>{s}.3mf</a></dd>'
             '<dt>Licence</dt><dd>CC BY 4.0</dd></dl></div></section>')
    others = [q for q in D["products"] if q["slug"] != s]
    b.append('<section class="band light"><div class="wrap"><p class="eyebrow">More concepts</p><h2>The other five pilot concepts</h2><div class="prodnav">'
             + "".join(f'<a href="/products/{q["slug"]}"><img src="/products/files/{q["slug"]}/poster.webp" alt="" width="72" height="54" loading="lazy"><span style="color:var(--pink)">{e(q["name"])}</span></a>' for q in others)
             + '</div><p class="note" style="margin-top:18px"><a href="/products/">All six</a> · <a href="/portfolio">All 112 concepts</a></p></div></section>')
    page(p["name"], f'{p["name"]}: a MAATAA OS product concept with use cases, blueprint, 3D view, guides and printable enclosure files.', "\n".join(b), f"products/{s}.html")

def index():
    cards = "".join(
        f'<article class="pi"><a href="/products/{p["slug"]}" style="text-decoration:none;color:inherit"><div class="im" style="background:#F7F7F7"><img src="/products/files/{p["slug"]}/poster.webp" alt="CAD render of the {e(p["name"])} concept enclosure" width="480" height="360" loading="lazy" style="object-fit:contain"></div>'
        f'<div class="bd"><h3>{e(p["name"])}</h3><p>{e(p["hook"])}</p><p class="nd">Tier {e(p["tier"])} · concept</p></div></a></article>' for p in D["products"])
    body = ('<section class="page-hero"><div class="wrap"><p class="eyebrow">Products · concepts</p><h1>Six concepts, worked out in detail.</h1>'
            '<p>Picked from the 112 in the portfolio because they match the first pilot conversations we want to have. Our focus is three families: Field I/O (the CAN / RS-485 module), Gateway (the solar gateway) and Motion (the motor controller and the drone spray-payload controller). The vibration and soil sensors are later concepts. Each has use cases, a blueprint, a 3D view, guides for users, makers and partners, and enclosure files you can print. None is a product yet.</p></div></section>'
            f'<section class="band" style="border-top:0;padding-top:8px"><div class="wrap"><h2 class="vh">The six concepts</h2><div class="pgrid">{cards}</div></div></section>')
    page("Product concepts", "Six MAATAA OS product concepts with blueprints, 3D views, guides and printable enclosure files.", body, "products/index.html")

def portfolio():
    p = PUB / "portfolio.html"; s = p.read_text()
    s = s.replace('<span class="cr">AI-generated concept</span>', "")
    s = re.sub(r"\.pi \.cr\{[^}]*\}\n?", "", s)
    if ".pi .more{" not in s:
        s = s.replace("</style>", ".pi .more{margin-top:4px;font-size:14px;font-weight:600}\n</style>", 1)
    s = s.replace("<p>Inspection and defence drones</p>", "<p>Agricultural spraying and inspection drones</p>")
    s = s.replace("MAATAA on the flight controller; payload computer on Linux",
                  "MAATAA on the spray-payload controller; flight control stays on the autopilot; payload computer on Linux")
    for q in D["products"]:
        h3 = f'<h3>{e(q["portfolio"])}</h3>'
        i = s.find(h3)
        assert i > 0, q["portfolio"]
        j = s.find("</div></article>", i)
        seg = s[i:j]
        if "class=\"more\"" not in seg:
            s = s[:j] + f'<p class="more"><a href="/products/{q["slug"]}">Concept details, 3D files →</a></p>' + s[j:]
    if 'href="/products/">' not in s:
        s = s.replace('<div class="jump has-toc">', '<p style="margin:18px 0 0"><a class="btn" href="/products/">Six concepts in detail, with printable enclosures →</a></p><div class="jump has-toc">', 1)
    p.write_text(s)
    c = PUB / "portfolio.csv"; t = c.read_text()
    t = t.replace("Robots (systems),Drone / UAV,Inspection and defence drones,A+C,MAATAA on the flight controller; payload computer on Linux,",
                  "Robots (systems),Drone / UAV,Agricultural spraying and inspection drones,A+C,MAATAA on the spray-payload controller; flight control stays on the autopilot; payload computer on Linux,")
    c.write_text(t)

for p in D["products"]: product(p)
index(); portfolio()
sm = PUB / "sitemap.xml"; t = sm.read_text()
for u in ["/products"] + [f'/products/{p["slug"]}' for p in D["products"]]:
    loc = f'{FACTS["site"]}{u}'
    if f"<loc>{loc}</loc>" not in t:
        t = t.replace("</urlset>", f'<url><loc>{loc}</loc><lastmod>2026-11-06</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>\n</urlset>')
sm.write_text(t)
print(f"products: {len(D['products'])} pages + index, portfolio linked")
