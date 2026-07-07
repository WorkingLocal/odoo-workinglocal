"""
Koppelt alle Hosting Local website.page records aan website_id=2.
Uitvoeren NA installatie van de hostinglocal_website addon.

Gebruik: python scripts/set_hl_website.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = os.environ.get('ODOO_PASS') or (sys.argv[1] if len(sys.argv) > 1 else None)
odoo = OdooClient(password=pw)

# Zoek website id=2 (Hosting Local)
websites = odoo.search_read('website', [['id', '=', 2]], ['id', 'name'])
if not websites:
    print("ERROR: website met id=2 niet gevonden.")
    sys.exit(1)
print(f"Website gevonden: {websites[0]['name']} (id={websites[0]['id']})")

# Zoek alle HL pagina's (aangemaakt door addon)
hl_urls = ['/', '/diensten', '/contact', '/contact/bedankt']
pages = odoo.search_read(
    'website.page',
    [['url', 'in', hl_urls]],
    ['id', 'name', 'url', 'website_id']
)
print(f"\n{len(pages)} pagina's gevonden:")
for p in pages:
    print(f"  [{p['id']}] {p['url']} — website_id={p['website_id']}")

page_ids = [p['id'] for p in pages]
if page_ids:
    odoo.models.execute_kw(
        odoo.db, odoo.uid, odoo.password,
        'website.page', 'write',
        [page_ids, {'website_id': 2}]
    )
    print(f"\n✅ {len(page_ids)} pagina's gekoppeld aan website_id=2 (Hosting Local)")
else:
    print("Geen pagina's gevonden om bij te werken.")
