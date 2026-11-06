#!/usr/bin/env python3
"""Builds the 3D files for the product concept pages (run in a container with
OpenSCAD 2021+, xvfb-run, and pip packages trimesh, shapely, lxml, networkx, pillow).

content/models/<model>.scad  ->  public/products/files/<slug>/
  <slug>-base.stl, <slug>-lid.stl   binary STL, print orientation
  <slug>.3mf                        both parts on one plate
  <slug>.scad, maataa-lib.scad      parametric source (CC BY 4.0)
  turntable.webp                    24-frame sprite for the CSS-only 3D view
  hero.webp                         exploded render for the page hero
  blueprint.svg                     orthographic views, section and title block

Not run in CI: the outputs are committed. Re-run after changing a model.
"""
import json, math, shutil, subprocess, sys, tempfile, datetime
from pathlib import Path
import numpy as np, trimesh
from PIL import Image
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "content/models"
P = json.loads((ROOT / "content/products.json").read_text())
only = set(sys.argv[1:])

def scad(src, out, part, explode=0, extra=()):
    subprocess.run(["openscad", "-q", "-o", str(out), "-D", f'part="{part}"', "-D", f"explode={explode}", *extra, str(src)],
                   check=True, cwd=MOD)

def png(src, out, part, explode, cam, size):
    subprocess.run(["xvfb-run", "-a", "openscad", "-q", "-o", str(out), f"--imgsize={size[0]},{size[1]}",
                    "--colorscheme=Tomorrow", "--projection=p", f"--camera={cam}",
                    "-D", f'part="{part}"', "-D", f"explode={explode}", str(src)], check=True, cwd=MOD)

def polys(g):
    if g.is_empty: return []
    return list(g.geoms) if isinstance(g, MultiPolygon) else [g]

def silhouette(mesh, axis):
    # project triangles onto the plane normal to axis and union them
    keep = [i for i in range(3) if i != axis]
    tri = mesh.triangles[:, :, keep]
    ps = [Polygon(t) for t in tri if abs(Polygon(t).area) > 1e-6]
    return unary_union([p.buffer(0.01) for p in ps]).buffer(-0.01)

def section(mesh, z):
    s = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None: return Polygon()
    g = Polygon()
    for loop in s.discrete:
        if len(loop) >= 3: g = g.symmetric_difference(Polygon(loop[:, :2]).buffer(0))
    return g

def svg_path(geom, ox, oy, k, flipy=True):
    d = []
    for p in polys(geom):
        for ring in [p.exterior, *p.interiors]:
            pts = [(ox + x * k, oy - y * k if flipy else oy + y * k) for x, y in ring.coords]
            d.append("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z")
    return " ".join(d)

def dim(x1, y1, x2, y2, label, off, horiz=True):
    if horiz:
        y = y1 + off
        return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" y2="{y:.1f}" class="e"/><line x1="{x2:.1f}" y1="{y2:.1f}" x2="{x2:.1f}" y2="{y:.1f}" class="e"/>'
                f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" class="d" marker-start="url(#a)" marker-end="url(#a)"/>'
                f'<text x="{(x1+x2)/2:.1f}" y="{y-5:.1f}" text-anchor="middle">{label}</text>')
    x = x1 + off
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y1:.1f}" class="e"/><line x1="{x2:.1f}" y1="{y2:.1f}" x2="{x:.1f}" y2="{y2:.1f}" class="e"/>'
            f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" class="d" marker-start="url(#a)" marker-end="url(#a)"/>'
            f'<text x="{x+6:.1f}" y="{(y1+y2)/2+4:.1f}" transform="rotate(-90 {x+6:.1f} {(y1+y2)/2+4:.1f})" text-anchor="middle">{label}</text>')

def blueprint(p, allm, base, lid, out):
    W, H = 1200, 820
    lt = lid.copy(); lt.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    views = {"TOP": silhouette(lt, 2), "FRONT": silhouette(allm, 1), "SIDE": silhouette(allm, 0)}
    zmid = (base.bounds[0][2] + base.bounds[1][2]) / 2
    zmid = max(zmid, 6)
    sec = section(base, zmid)
    b = allm.bounds; ext = b[1] - b[0]
    k = min(330 / max(ext[0], ext[1]), 230 / max(ext[2], 1), 330 / max(ext[0], 1), 4.0)
    out_s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Blueprint of the {p["name"]} concept enclosure">',
             '<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,2 L10,5 L0,8 z" fill="#E8EDF8"/></marker>'
             '<pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#2C3A78" stroke-width="1"/></pattern>'
             '<pattern id="h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#FF9A1F" stroke-width="1.2"/></pattern></defs>',
             '<style>text{font:13px "JetBrains Mono",monospace;fill:#E8EDF8}.t{font:600 15px "JetBrains Mono",monospace;letter-spacing:.08em}.o{fill:none;stroke:#E8EDF8;stroke-width:1.6}.s{fill:url(#h);stroke:#FF9A1F;stroke-width:1.4;fill-rule:evenodd}.e{stroke:#9FB0D8;stroke-width:.8}.d{stroke:#E8EDF8;stroke-width:1}.f{fill:none;stroke:#E8EDF8;stroke-width:2}.tb{fill:#18224A;stroke:#E8EDF8;stroke-width:1.2}.big{font:700 22px Mukta,sans-serif}.w{fill:#FF9A1F;font-weight:700}</style>',
             f'<rect width="{W}" height="{H}" fill="#1F2A5C"/><rect width="{W}" height="{H}" fill="url(#g)"/><rect x="14" y="14" width="{W-28}" height="{H-28}" class="f"/>']
    out_s.append('<text class="t" x="80" y="400" fill-opacity=".7">TOP: LID, OUTSIDE FACE</text>') if False else None
    cells = {"TOP": (60, 60, 0, 1), "FRONT": (60, 440, 0, 2), "SIDE": (470, 440, 1, 2)}
    for name, (cx, cy, ax, ay) in cells.items():
        g = views[name]
        if g.is_empty: continue
        x0, y0, x1, y1 = g.bounds
        ox = cx + 20 - x0 * k; oy = cy + 30 + (y1 - y0) * k + y0 * k
        out_s.append(f'<text class="t" x="{cx+20}" y="{cy+16}">{name}</text>')
        out_s.append(f'<path class="o" fill-rule="evenodd" d="{svg_path(g, ox, oy, k)}"/>')
        X0, X1 = ox + x0 * k, ox + x1 * k; Y0, Y1 = oy - y1 * k, oy - y0 * k
        out_s.append(dim(X0, Y1, X1, Y1, f"{x1-x0:.0f}", 26))
        out_s.append(dim(X1, Y0, X1, Y1, f"{y1-y0:.0f}", 26, horiz=False))
    if not sec.is_empty:
        x0, y0, x1, y1 = sec.bounds
        cx, cy = 470, 60
        ox = cx + 20 - x0 * k; oy = cy + 30 + (y1 - y0) * k + y0 * k
        out_s.append(f'<text class="t" x="{cx+20}" y="{cy+16}">SECTION A–A (BASE AT Z = {zmid:.0f})</text>')
        out_s.append(f'<path class="s" d="{svg_path(sec, ox, oy, k)}"/>')
    tx = 880
    out_s.append(f'<rect class="tb" x="{tx}" y="60" width="290" height="{H-120}"/>')
    rows = [("PRODUCT", p["name"]), ("STATUS", "CONCEPT · NOT A PRODUCT"), ("PART", "ENCLOSURE: BASE + LID"),
            ("UNITS", "mm"), ("MATERIAL", p["material"]), ("PRINT", f'{p["layer"]} mm layers, {p["infill"]} infill'),
            ("FASTENERS", p["fasteners"]), ("PCB", "placeholder until a real board"),
            ("SOURCE", f'{p["model"]}.scad'), ("LICENCE", "CC BY 4.0"), ("DRAWN", datetime.date.today().isoformat()),
            ("BY", "ALL B Vegan Pvt Ltd")]
    y = 92
    out_s.append(f'<text class="big" x="{tx+16}" y="{y}">MAATAA OS</text>'); y += 26
    for kk, v in rows:
        out_s.append(f'<text x="{tx+16}" y="{y}" fill-opacity=".7">{kk}</text>'); y += 18
        for line in wrap(v, 30):
            out_s.append(f'<text x="{tx+16}" y="{y}"{" class=\"w\"" if kk=="STATUS" else ""}>{esc(line)}</text>'); y += 18
        y += 8
    out_s.append("</svg>")
    out.write_text("\n".join(out_s))

def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return lines + ([cur] if cur else [])

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

for p in P["products"]:
    if only and p["slug"] not in only: continue
    src = MOD / f'{p["model"]}.scad'
    out = ROOT / "public/products/files" / p["slug"]; out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    for part in ("base", "lid"):
        scad(src, tmp / f"{part}.stl", part)
        m = trimesh.load(tmp / f"{part}.stl")
        assert m.is_watertight, f'{p["slug"]} {part} not watertight'
        m.apply_translation([0, 0, -m.bounds[0][2]])
        m.export(out / f'{p["slug"]}-{part}.stl')
    base = trimesh.load(out / f'{p["slug"]}-base.stl'); lid = trimesh.load(out / f'{p["slug"]}-lid.stl')
    l2 = lid.copy(); l2.apply_translation([0, base.bounds[1][1] - lid.bounds[0][1] + 8, 0])
    trimesh.Scene({"base": base, "lid": l2}).export(out / f'{p["slug"]}.3mf')
    shutil.copy(src, out / src.name); shutil.copy(MOD / "maataa-lib.scad", out / "maataa-lib.scad")
    scad(src, tmp / "all.stl", "all")
    allm = trimesh.load(tmp / "all.stl")
    if isinstance(allm, trimesh.Scene): allm = allm.dump(concatenate=True)
    c = (allm.bounds[0] + allm.bounds[1]) / 2; r = np.linalg.norm(allm.bounds[1] - allm.bounds[0])
    blueprint(p, allm, trimesh.load(tmp / "base.stl"), lid, out / "blueprint.svg")
    frames = []
    for i in range(24):
        f = tmp / f"f{i:02d}.png"
        png(src, f, "all", 0, f"{c[0]:.1f},{c[1]:.1f},{c[2]:.1f},62,0,{i*15+20},{r*2.7:.1f}", (480, 360))
        frames.append(Image.open(f).convert("RGB"))
    sheet = Image.new("RGB", (480 * 24, 360))
    for i, fr in enumerate(frames): sheet.paste(fr, (480 * i, 0))
    sheet.save(out / "turntable.webp", quality=72, method=6)
    frames[0].save(out / "poster.webp", quality=80, method=6)
    ex = p.get("explode", 22)
    png(src, tmp / "hero.png", "all", ex, f"{c[0]:.1f},{c[1]:.1f},{c[2]+ex/2:.1f},58,0,32,{r*2.9:.1f}", (1400, 1000))
    Image.open(tmp / "hero.png").convert("RGB").save(out / "hero.webp", quality=80, method=6)
    shutil.rmtree(tmp)
    sz = sum(f.stat().st_size for f in out.iterdir())
    print(f'{p["slug"]}: {len(list(out.iterdir()))} files, {sz/1024:.0f} KiB')
