"""
Koppelt de Qompanio website.page-record aan het juiste website_id.
Uitvoeren NA installatie van de qompanio_website addon EN nadat het
Qompanio website-record manueel is aangemaakt in de Odoo-backend
(Website-app -> Instellingen -> nieuwe website "Qompanio").

Gebruik: python scripts/set_qompanio_website.py
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = os.environ.get('ODOO_PASS') or (sys.argv[1] if len(sys.argv) > 1 else None)
odoo = OdooClient(password=pw)

# Zoek website "Qompanio" op naam (numeriek ID is nog niet gekend vóór aanmaak)
websites = odoo.search_read('website', [['name', '=', 'Qompanio']], ['id', 'name'])
if not websites:
    print("ERROR: website 'Qompanio' niet gevonden. Maak eerst manueel aan via "
          "Website-app -> Instellingen -> nieuwe website.")
    sys.exit(1)
website_id = websites[0]['id']
print(f"Website gevonden: {websites[0]['name']} (id={website_id})")
print("LET OP: zorg dat dit ID overeenkomt met de 'website.id == N' check in "
      "views/website_layout.xml — pas anders die template aan en herinstalleer.")

# Zoek de Qompanio homepage via haar XML-ID (betrouwbaarder dan filteren op
# url='/', want elke website heeft een eigen pagina op '/').
xml_id = odoo.search_read(
    'ir.model.data',
    [['module', '=', 'qompanio_website'], ['name', '=', 'qom_page_homepage_record']],
    ['res_id']
)
if not xml_id:
    print("ERROR: qom_page_homepage_record niet gevonden — is de addon geïnstalleerd?")
    sys.exit(1)

page_id = xml_id[0]['res_id']
page = odoo.search_read('website.page', [['id', '=', page_id]], ['id', 'name', 'url', 'website_id'])[0]
print(f"\nPagina gevonden: [{page['id']}] {page['url']} — website_id={page['website_id']}")

odoo.write('website.page', [page_id], {'website_id': website_id})
print(f"\n✅ Pagina gekoppeld aan website_id={website_id} (Qompanio)")
