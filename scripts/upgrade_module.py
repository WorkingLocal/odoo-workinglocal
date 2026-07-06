#!/usr/bin/env python3
"""
Odoo module upgraden via XML-RPC.

Gebruik: python3 scripts/upgrade_module.py <module_naam>
Voorbeeld: python3 scripts/upgrade_module.py workinglocal_theme

Waarom XML-RPC en niet `docker exec odoo ... -u module`?
- DB-wachtwoord bevat '&' → breekt shell-argument parsing
- XML-RPC triggert de upgrade asynchroon via de Odoo worker (geen container-herstart nodig)
"""
import xmlrpc.client
import sys

url = "https://odoo.workinglocal.be"
db = "workinglocal"
username = "info@workinglocal.be"
# Wachtwoord: zie Vaultwarden "Odoo CE - odoo.workinglocal.be"
password = input("Odoo wachtwoord: ") if len(sys.argv) < 3 else sys.argv[2]

module = sys.argv[1] if len(sys.argv) > 1 else "workinglocal_theme"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
if not uid:
    print("Authenticatie mislukt")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

mods = models.execute_kw(
    db, uid, password,
    "ir.module.module", "search_read",
    [[["name", "=", module]]],
    {"fields": ["id", "state", "latest_version"]},
)
if not mods:
    print(f"Module '{module}' niet gevonden in database")
    sys.exit(1)

m = mods[0]
print(f"Module: {module} | State: {m['state']} | Versie DB: {m['latest_version']}")

if m["state"] == "installed":
    models.execute_kw(db, uid, password, "ir.module.module", "button_immediate_upgrade", [[m["id"]]])
    print("Upgrade gestart! Controleer na ~30s de versie in de DB.")
elif m["state"] == "uninstalled":
    models.execute_kw(db, uid, password, "ir.module.module", "button_immediate_install", [[m["id"]]])
    print("Installatie gestart!")
else:
    print(f"Onverwachte state '{m['state']}' — check manueel in Odoo backend")
