#!/usr/bin/env python3
"""Build the generated parts of maataa-os.allb.xyz from content/.

  updates.json -> updates.html list, home "Latest" (2 newest), feed.xml
  GitHub API   -> "Latest commits on main" on updates.html (kept as is if offline)
  facts.json   -> sitemap.xml lastmod and the release shown on the site

Run from sites/maataa-os:  python3 tools/build.py
"""
import json, re, html, sys, urllib.request, datetime
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
U = json.loads((ROOT / "content/updates.json").read_text())
F = json.loads((ROOT / "content/facts.json").read_text())
U.sort(key=lambda u: u["date"], reverse=True)

def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]

def uid(u):
    return f"u-{u['date']}-{slug(u['title'])}"

def nice(d):
    return datetime.date.fromisoformat(d).strftime("%-d %b %Y")

def entry(u, kind=True):
    e = html.escape
    body = "".join(f"<p>{e(p)}</p>" for p in u["body"])
    if u.get("points"):
        body += "<ul>" + "".join(f"<li>{e(p)}</li>" for p in u["points"]) + "</ul>"
    k = f'<span class="kind">{e(u["kind"])}</span>' if kind else ""
    return (f'<li class="entry" id="{uid(u)}">{k}<time datetime="{u["date"]}">{nice(u["date"])}</time>'
            f'<h3>{e(u["title"])}</h3>{body}</li>')

def short(u):
    e = html.escape
    first = u["body"][0] if u["body"] else ""
    return (f'<li class="entry"><time datetime="{u["date"]}">{nice(u["date"])}</time>'
            f'<h3><a href="/updates#{uid(u)}" style="color:inherit;text-decoration:none">{e(u["title"])}</a></h3><p>{e(first)}</p></li>')

def put(path, name, content):
    p = PUB / path
    s = p.read_text()
    pat = re.compile(rf"(<!--BUILD:{name}-->).*?(<!--/BUILD:{name}-->)", re.S)
    if not pat.search(s):
        sys.exit(f"{path}: marker BUILD:{name} missing")
    p.write_text(pat.sub(lambda m: m.group(1) + "\n" + content + "\n" + m.group(2), s))

def commits():
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{F['repo']}/commits?per_page=6",
                                     headers={"User-Agent": "maataa-os-site-build", "Accept": "application/vnd.github+json"})
        data = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as ex:
        print(f"note: commits not refreshed ({ex}); keeping the last list")
        return None
    e = html.escape
    rows = []
    for c in data:
        msg = c["commit"]["message"].splitlines()[0]
        rows.append(f'<li><a href="{e(c["html_url"])}"><code>{c["sha"][:7]}</code></a> '
                    f'<strong style="font-weight:400">{e(msg)}</strong> <span>{c["commit"]["author"]["date"][:10]}</span></li>')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return "\n".join(rows) + f'\n<li><span>Read from GitHub at {stamp}.</span></li>'

put("updates.html", "updates", "\n".join(entry(u) for u in U))
put("index.html", "latest", "\n".join(short(u) for u in U[:2]))
c = commits()
if c:
    put("updates.html", "commits", c)

items = []
for u in U:
    desc = " ".join(u["body"] + u.get("points", []))
    dt = format_datetime(datetime.datetime.fromisoformat(u["date"] + "T12:00:00+05:30"))
    items.append(f"<item><title>{html.escape(u['title'])}</title><link>{F['site']}/updates#{uid(u)}</link>"
                 f"<guid isPermaLink=\"false\">maataa-os-{uid(u)[2:]}</guid><pubDate>{dt}</pubDate>"
                 f"<category>{html.escape(u['kind'])}</category><description>{html.escape(desc)}</description></item>")
(PUB / "feed.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
    f"<title>MAATAA OS updates</title><link>{F['site']}/updates</link>\n"
    "<description>Releases, board runs and decisions for MAATAA OS.</description><language>en</language>\n"
    + "\n".join(items) + "\n</channel></rss>\n")

today = datetime.date.today().isoformat()
sm = PUB / "sitemap.xml"
sm.write_text(re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{today}</lastmod>", sm.read_text()))
print(f"built: {len(U)} updates, feed, home latest, sitemap ({today})" + ("" if c else ", commits unchanged"))
