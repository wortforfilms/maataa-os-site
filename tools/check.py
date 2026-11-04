#!/usr/bin/env python3
"""Checks the built site before deploy. Exit 1 on any problem.

- every internal link and image resolves to a file in public/
- no banned claims (sovereign, world first, production-ready, AI-native ...)
- every page carries the company name, the CIN and the concept-render notice
- with --kernel DIR (a checkout of wortforfilms/os): the release matches the kernel README,
  and the kernel size in facts.json is within 2 KiB of docs/size.md (the kernel's own check uses the same margin)
- without it: the release is compared with the README on GitHub (online only)
"""
import argparse, json, re, sys, urllib.request
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument("--kernel"); ARGS = ap.parse_args()
ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
F = json.loads((ROOT / "content/facts.json").read_text())
BANNED = [r"\bsovereign\b", r"world'?s first", r"india'?s first", r"production[- ]ready(?! operating system: )",
          r"\bai[- ]native\b", r"\bTBD\b", r"lorem ipsum", r"\bguarantee"]
ALLOW_PRODUCTION_READY = ["not yet a production operating system", "Not positioned as a production-ready",
                          "Is it production-ready?", "No production readiness", "\"production-ready\""]
bad = []
pages = sorted(PUB.glob("*.html"))
for p in pages:
    s = p.read_text()
    text = re.sub(r"<[^>]+>", " ", s)
    for pat in BANNED:
        for m in re.finditer(pat, text, re.I):
            ctx = text[max(0, m.start() - 60): m.end() + 60]
            if any(a.lower() in ctx.lower() for a in ALLOW_PRODUCTION_READY):
                continue
            bad.append(f"{p.name}: banned phrase '{m.group(0)}' … {' '.join(ctx.split())}")
    for ref in re.findall(r'(?:href|src)="(/[^"#?]*)', s):
        path = ref.lstrip("/") or "index.html"
        if path.endswith("/"):
            path += "index.html"
        if not (PUB / path).exists():
            bad.append(f"{p.name}: missing target {ref}")
    for need in (F["company"], F["cin"], "concept renders"):
        if need not in s:
            bad.append(f"{p.name}: footer lacks '{need}'")

def kernel_checks(readme, size_md):
    m = re.search(r"Release: `v([^`]+)`", readme)
    if m and m.group(1) != F["release"]:
        bad.append(f"facts.json says {F['release']} but the kernel README says {m.group(1)}: update the site")
    if size_md:
        s = re.search(r"\| F411 release \| ([\d,]+) \|", size_md)
        if s:
            doc = int(s.group(1).replace(",", ""))
            if abs(doc - F["kernel_bytes"]) > 2048:
                bad.append(f"kernel_bytes {F['kernel_bytes']} is more than 2 KiB from docs/size.md ({doc})")
            elif doc != F["kernel_bytes"]:
                print(f"note: kernel_bytes {F['kernel_bytes']} vs docs/size.md {doc} (within 2 KiB)")
    if F["release"] not in (PUB / "index.html").read_text():
        bad.append(f"index.html: release {F['release']} not shown")

if ARGS.kernel:
    k = Path(ARGS.kernel)
    kernel_checks((k / "README.md").read_text(), (k / "docs/size.md").read_text() if (k / "docs/size.md").exists() else "")
else:
    try:
        readme = urllib.request.urlopen(urllib.request.Request(
            f"https://raw.githubusercontent.com/{F['repo']}/main/README.md",
            headers={"User-Agent": "maataa-os-site-check"}), timeout=20).read().decode()
        kernel_checks(readme, "")
    except Exception as ex:
        print(f"note: release not compared ({ex})")

if bad:
    print("\n".join(bad)); sys.exit(1)
print(f"site check: {len(pages)} pages OK")
