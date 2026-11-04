# maataa-os-site

Source of https://maataa-os.allb.xyz, the public home of MAATAA OS.

Static files only, served by the Cloudflare Worker `maataa-os-site`; no scripts, no cookies, no third-party requests.

| Path | What it holds |
| --- | --- |
| `public/*.html` | Home, Vision, Portfolio, Updates, Roadmap, Team, FAQ, Support, Privacy, 404 |
| `public/feed.xml` | RSS feed, generated |
| `public/_headers` | Security headers (HSTS, CSP, frame, referrer, permissions) |
| `public/.well-known/security.txt` | Where to report vulnerabilities |
| `public/assets/` | Board photo, concept renders, self-hosted fonts |
| `content/updates.json` | The one source for updates: page, home "Latest" and feed |
| `content/facts.json` | Release, sizes, company and CIN that the check holds the site to |
| `tools/build.py` | Writes the generated parts between `<!--BUILD:…-->` markers |
| `tools/check.py` | Fails on broken links, banned claims, a missing footer or a stale release |

## Posting an update

1. Add an entry at the top of `content/updates.json` (date, kind, title, body, points).
2. Commit and push to `main`. GitHub Actions builds, checks against the kernel repository, and deploys (`.github/workflows/site.yml`).
   Without CI: double-click `Deploy site.command`, which runs the same build and check first.

After a kernel release, update `release` and the sizes in `content/facts.json`; the check fails until you do.

## One-time setup for CI

In GitHub, `wortforfilms/maataa-os-site` → Settings → Environments → New environment `production`, and add these environment secrets:

- `CLOUDFLARE_API_TOKEN`: a Cloudflare token limited to this account's Workers Scripts (edit) and the allb.xyz zone (Workers Routes edit, DNS edit for the custom domain)
- `CLOUDFLARE_ACCOUNT_ID`: the account ID shown by `npx wrangler whoami`

`uptime.yml` checks the site every hour; GitHub emails you when it fails.

Rules: say what was run and where; no user counts, uptime figures, "first", "sovereign" or "production-ready"; device images stay labelled as AI-generated concepts.

## Licence

All rights reserved. See LICENSE. The MAATAA OS kernel has its own licence in its own repository.
