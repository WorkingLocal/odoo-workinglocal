"""
Wimood leveranciersimportscript — UniFi / Ubiquiti productlijn
Haalt producten op via de Wimood XML-productcatalogus en importeert ze in Odoo.

Filter: alleen producten van merk Ubiquiti waarvan de naam 'UniFi' bevat.
        (sluit AirMAX, EdgeRouter, EdgeSwitch en andere Ubiquiti-lijnen uit)

Prijzen in de Wimood XML zijn excl. BTW (standaard B2B):
  - prijs  → standard_price (inkoopprijs voor Working Local)
  - msrp   → list_price     (aanbevolen verkoopprijs)

Gebruik:
    # Kopieer naar VPS en voer uit:
    scp scripts/suppliers/*.py root@23.94.220.181:/tmp/
    ssh root@23.94.220.181 "cd /tmp && python3 wimood.py"
"""

import sys, os, subprocess, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
from odoo_client import OdooClient, svg_placeholder

# ── Wimood XML API ─────────────────────────────────────────────────────────────
WIMOOD_XML_URL = (
    "https://wimoodshop.nl/api/index.php"
    "?api_key=804pVwKtJULuakng9WQQjsd9NagZSQ&klantnummer=11556"
)


def fetch_wimood_xml():
    """Download en parse de Wimood productcatalogus (iso-8859-1 XML)."""
    r = subprocess.run(
        ["curl", "-sfL", "--max-time", "30", WIMOOD_XML_URL],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError("Wimood XML ophalen mislukt — controleer URL en netwerk")
    return ET.fromstring(r.stdout)


def get_unifi_products(root):
    """
    Filter producten: merk Ubiquiti én 'UniFi' in de productnaam.
    Geeft lijst van dicts terug met genormaliseerde velden.
    """
    products = []
    for p in root.findall('product'):
        brand = (p.findtext('brand') or '').strip()
        name  = (p.findtext('product_name') or '').strip()
        if brand == 'Ubiquiti' and 'UniFi' in name:
            products.append({
                'wimood_id': p.findtext('product_id'),
                'code':      (p.findtext('product_code') or '').strip(),
                'name':      name,
                'stock':     int(p.findtext('stock') or 0),
                'msrp':      float(p.findtext('msrp') or 0),   # aanbevolen vvp excl. BTW
                'prijs':     float(p.findtext('prijs') or 0),  # inkoopprijs excl. BTW
            })
    return products


# ── Categorie-mapping ──────────────────────────────────────────────────────────
_AP_CODES   = ('UAP', 'U6-', 'U7-')
_SW_CODES   = ('USW',)
_GW_CODES   = ('UDM', 'USG', 'UXG', 'UDR')
_CAM_CODES  = ('UVC', 'UNVR', 'UP-F')          # UP-FloodLight e.d.
_CTRL_CODES = ('UCK', 'CKG', 'USP-')


def get_subcategory(name: str, code: str) -> str:
    """Bepaal Odoo-subcategorie op basis van productnaam en -code."""
    n = name.lower()
    c = code.upper()

    # Op productnaam
    if any(x in n for x in ['access point', 'nanohd', 'flexhd', 'in-wall hd',
                              'mesh point', 'u6 ', 'u7 ']):
        return 'Access Points'
    if 'switch' in n:
        return 'Switches'
    if any(x in n for x in ['dream machine', 'dream router', 'gateway',
                              'security gateway']):
        return 'Gateways'
    if any(x in n for x in ['protect', 'doorbell', 'nvr', 'flood light',
                              'viewport', 'camera']):
        return 'Beveiliging'
    if any(x in n for x in ['cloud key', 'redundant power', 'smartpower']):
        return 'Controllers'

    # Fallback op productoncode-prefix
    if c.startswith(_AP_CODES):
        return 'Access Points'
    if c.startswith(_SW_CODES):
        return 'Switches'
    if c.startswith(_GW_CODES):
        return 'Gateways'
    if c.startswith(_CAM_CODES):
        return 'Beveiliging'
    if c.startswith(_CTRL_CODES):
        return 'Controllers'

    return 'Accessoires'


# ── Leverancier ───────────────────────────────────────────────────────────────
def get_or_create_wimood_partner(odoo):
    """Zoek Wimood op als leverancier (res.partner) of maak aan."""
    res = odoo.search_read('res.partner', [('name', '=', 'Wimood')], ['id'])
    if res:
        return res[0]['id']
    partner_id = odoo.create('res.partner', {
        'name':       'Wimood',
        'is_company': True,
        'supplier_rank': 1,
        'website':    'https://wimoodshop.nl',
        'country_id': odoo.search_read('res.country', [('code', '=', 'NL')], ['id'])[0]['id'],
    })
    print(f"  ✓ Leverancier aangemaakt: Wimood (id={partner_id})")
    return partner_id


# ── Main import ────────────────────────────────────────────────────────────────
def main():
    odoo = OdooClient()

    # Leverancier aanmaken / ophalen
    print("\nLeverancier ophalen…")
    wimood_id = get_or_create_wimood_partner(odoo)

    # Categoriehiërarchie aanmaken
    print("\nCategorieën aanmaken…")
    cat_netwerk = odoo.get_or_create_cat('Netwerk & WiFi')
    subcats = {}
    for sub in ('Access Points', 'Switches', 'Gateways',
                 'Beveiliging', 'Controllers', 'Accessoires'):
        subcats[sub] = odoo.get_or_create_cat(sub, parent_id=cat_netwerk)

    placeholder = svg_placeholder('wifi')

    # XML ophalen en filteren
    print("\nWimood XML ophalen…")
    root = fetch_wimood_xml()
    products = get_unifi_products(root)
    print(f"  → {len(products)} UniFi producten gevonden\n")

    created = skipped = 0
    for p in products:
        subcat_name = get_subcategory(p['name'], p['code'])
        categ_id    = subcats[subcat_name]

        vals = {
            'name':           p['name'],
            'default_code':   p['code'],
            'type':           'consu',
            'categ_id':       categ_id,
            'list_price':     round(p['msrp'],  2),
            'standard_price': round(p['prijs'], 2),
            'purchase_ok':    True,
            'sale_ok':        True,
            'is_published':   False,   # niet zichtbaar op webshop
            # Leveranciersinformatie
            'seller_ids': [(0, 0, {
                'partner_id': wimood_id,
                'price':      round(p['prijs'], 2),
                'min_qty':    1,
            })],
        }

        existing = odoo.search_read(
            'product.template',
            [('default_code', '=', p['code'])],
            ['id', 'name'],
        )
        if existing:
            print(f"  ~ Bestaat al: {p['code']:<30} — {existing[0]['name'][:50]}")
            skipped += 1
        else:
            tmpl_id = odoo.create('product.template', vals)
            odoo.write('product.template', [tmpl_id], {'image_1920': placeholder})
            print(f"  ✓ {p['code']:<30}  {p['name'][:55]}")
            created += 1

    print(f"\nKlaar: {created} aangemaakt, {skipped} overgeslagen.")
    print(f"Categorie: 'Netwerk & WiFi' → {', '.join(subcats)}")


if __name__ == '__main__':
    main()
