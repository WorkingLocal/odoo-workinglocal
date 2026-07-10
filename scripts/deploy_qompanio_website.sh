#!/usr/bin/env bash
# Deploy qompanio_website addon naar VPS en installeer/upgrade via XML-RPC
# Gebruik: ODOO_PASS=... bash scripts/deploy_qompanio_website.sh
# (wachtwoord: Vaultwarden "Odoo CE - odoo.workinglocal.be"; zonder ODOO_PASS wordt
#  interactief gevraagd door upgrade_module.py / set_qompanio_website.py)
set -e

VPS="100.107.226.24"
ADDONS_VOLUME="/var/lib/docker/volumes/wmsa9jotez65ynj0xsb748rq_odoo-addons/_data"
ADDON="qompanio_website"

echo "==> Tar addon..."
cd "$(dirname "$0")/.."
tar czf /tmp/qompanio_website.tar.gz -C addons "$ADDON"

echo "==> SCP naar VPS..."
scp /tmp/qompanio_website.tar.gz "root@${VPS}:/tmp/"

echo "==> Uitpakken + kopiëren naar Docker volume..."
ssh "root@${VPS}" bash <<EOF
  cd /tmp
  tar xzf qompanio_website.tar.gz
  rm -rf "${ADDONS_VOLUME}/${ADDON}"
  cp -r "${ADDON}" "${ADDONS_VOLUME}/"
  echo "  Gekopieerd naar ${ADDONS_VOLUME}/${ADDON}"
EOF

echo "==> Install/upgrade via XML-RPC..."
if [ -n "$ODOO_PASS" ]; then
  python3 scripts/upgrade_module.py "$ADDON" "$ODOO_PASS"
else
  python3 scripts/upgrade_module.py "$ADDON"
fi

echo "==> website_id instellen (vereist dat het Qompanio website-record al manueel is aangemaakt)..."
if [ -n "$ODOO_PASS" ]; then
  python3 scripts/set_qompanio_website.py "$ODOO_PASS"
else
  python3 scripts/set_qompanio_website.py
fi

echo ""
echo "✅ Deploy klaar — controleer via hosts-file entry naar qompanio.be (zie plan/verificatie)"
