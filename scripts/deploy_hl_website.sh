#!/usr/bin/env bash
# Deploy hostinglocal_website addon naar VPS en installeer/upgrade via XML-RPC
# Gebruik: bash scripts/deploy_hl_website.sh [install|upgrade]
set -e

ACTION="${1:-upgrade}"
VPS="100.107.226.24"
ADDONS_VOLUME="/var/lib/docker/volumes/wmsa9jotez65ynj0xsb748rq_odoo-addons/_data"
ADDON="hostinglocal_website"

echo "==> Tar addon..."
cd "$(dirname "$0")/.."
tar czf /tmp/hl_website.tar.gz -C addons "$ADDON"

echo "==> SCP naar VPS..."
scp /tmp/hl_website.tar.gz "root@${VPS}:/tmp/"

echo "==> Uitpakken + kopiëren naar Docker volume..."
ssh "root@${VPS}" bash <<EOF
  cd /tmp
  tar xzf hl_website.tar.gz
  rm -rf "${ADDONS_VOLUME}/${ADDON}"
  cp -r "${ADDON}" "${ADDONS_VOLUME}/"
  echo "  Gekopieerd naar ${ADDONS_VOLUME}/${ADDON}"
EOF

echo "==> ${ACTION} via XML-RPC..."
python3 scripts/upgrade_module.py "$ADDON" "$ACTION"

echo "==> website_id instellen..."
python3 scripts/set_hl_website.py

echo ""
echo "✅ Deploy klaar — https://odoo.workinglocal.be"
