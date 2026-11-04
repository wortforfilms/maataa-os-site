#!/bin/bash
# Builds, checks and deploys https://maataa-os.allb.xyz (same steps as CI).
cd "$(dirname "$0")" || exit 1
KFLAG=""; for k in ../maataa-os "$HOME/revenue/live/maataa-os"; do [ -f "$k/docs/size.md" ] && KFLAG="--kernel $k" && break; done
echo "== Build"; python3 tools/build.py || { read -r -p "Build failed. Press Enter"; exit 1; }
echo "== Check"; python3 tools/check.py $KFLAG || { read -r -p "Check failed: fix the lines above. Press Enter"; exit 1; }
echo "== Cloudflare account"
npx --yes wrangler@latest whoami >/dev/null || { echo "Not logged in: run  npx wrangler login  and try again"; read -r -p "Press Enter to close"; exit 1; }
echo "== Deploy"; npx --yes wrangler@latest deploy
echo "== Live check"; sleep 5
for p in / /vision.html /portfolio.html /privacy.html /.well-known/security.txt /sitemap.xml; do
  printf "%-28s %s\n" "$p" "$(curl -s -o /dev/null -w '%{http_code}' "https://maataa-os.allb.xyz$p")"
done
curl -sSI https://maataa-os.allb.xyz/ | grep -iE "^(strict-transport|content-security)" | cut -c1-80
read -r -p "Done. Press Enter to close"
