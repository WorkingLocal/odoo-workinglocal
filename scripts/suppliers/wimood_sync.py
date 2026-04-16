#!/usr/bin/env python3
"""
Wimood nachtelijkse synchronisatie — prijzen, voorraad, nieuwe producten.

Vergelijkt de actuele Wimood XML-catalogus met Odoo en voert bij:
  • Prijswijzigingen   → update standard_price, list_price en leveranciersprijs
  • Voorraadwijzigingen → update x_wimood_stock (Wimood-voorraad als indicator)
  • Nieuwe producten   → aanmaken met WiFi-placeholder

Na afloop POST een JSON-samenvatting naar de n8n webhook voor e-mailmeldingen.

─── Gebruik (VPS, interactief) ──────────────────────────────────────────────
    python3 /tmp/wimood_sync.py

─── Crontab (dagelijks 02:00, wachtwoord uit env-variabele) ─────────────────
    Stap 1 — wachtwoord veilig opslaan:
        echo 'JOUW_WACHTWOORD' > /root/.odoo_password && chmod 600 /root/.odoo_password

    Stap 2 — crontab instelling (crontab -e):
        0 2 * * * ODOO_PASSWORD=$(cat /root/.odoo_password) python3 /tmp/wimood_sync.py >> /var/log/wimood_sync.log 2>&1
"""

import sys, os, json, subprocess, datetime, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
from odoo_client import OdooClient, svg_placeholder

# ── Constanten ─────────────────────────────────────────────────────────────────
WIMOOD_XML_URL = (
    "https://wimoodshop.nl/api/index.php"
    "?api_key=804pVwKtJULuakng9WQQjsd9NagZSQ&klantnummer=11556"
)
N8N_WEBHOOK_URL = "http://10.0.1.10:5678/webhook/wimood-sync"  # intern IP — omzeilt SSL

# Minimale prijsdelta om een update te triggeren (voorkomt float-ruis)
PRICE_MIN_DELTA = 0.01  # €0,01


# ── Custom veld — eenmalige setup ──────────────────────────────────────────────
def ensure_wimood_stock_field(odoo):
    """
    Maak het custom veld x_wimood_stock aan op product.template.
    Wordt enkel bij de eerste run uitgevoerd; daarna wordt het veld gevonden.
    """
    model = odoo.search_read('ir.model', [('model', '=', 'product.template')], ['id'])
    if not model:
        raise RuntimeError("ir.model: product.template niet gevonden")
    model_id = model[0]['id']

    existing = odoo.search_read(
        'ir.model.fields',
        [('model_id', '=', model_id), ('name', '=', 'x_wimood_stock')],
        ['id']
    )
    if not existing:
        odoo.create('ir.model.fields', {
            'name':              'x_wimood_stock',
            'field_description': 'Wimood Voorraad',
            'model_id':          model_id,
            'ttype':             'integer',
            'store':             True,
            'copied':            False,
        })
        print("  ✓ Veld x_wimood_stock aangemaakt op product.template")
    else:
        print("  ~ x_wimood_stock bestaat al")


# ── Wimood XML ─────────────────────────────────────────────────────────────────
def fetch_wimood_xml():
    r = subprocess.run(
        ["curl", "-sfL", "--max-time", "30", WIMOOD_XML_URL],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Wimood XML ophalen mislukt (curl exit {r.returncode})")
    return ET.fromstring(r.stdout)


def get_unifi_from_xml(root):
    """Haal alle UniFi/Ubiquiti producten op uit de XML. Geeft dict {code: product}."""
    products = {}
    for p in root.findall('product'):
        if (p.findtext('brand') or '').strip() != 'Ubiquiti':
            continue
        name = (p.findtext('product_name') or '').strip()
        if 'UniFi' not in name:
            continue
        code = (p.findtext('product_code') or '').strip()
        if not code:
            continue
        products[code] = {
            'code':  code,
            'name':  name,
            'msrp':  round(float(p.findtext('msrp')  or 0), 2),
            'prijs': round(float(p.findtext('prijs') or 0), 2),
            'stock': int(p.findtext('stock') or 0),
        }
    return products


# ── Odoo helpers ───────────────────────────────────────────────────────────────
def get_odoo_wimood_products(odoo, wimood_partner_id):
    """Haal alle producten op waarbij Wimood de leverancier is."""
    records = odoo.search_read(
        'product.template',
        [('seller_ids.partner_id', '=', wimood_partner_id)],
        ['id', 'name', 'default_code', 'list_price', 'standard_price',
         'x_wimood_stock', 'categ_id']
    )
    return {r['default_code']: r for r in records if r.get('default_code')}


def sync_seller_price(odoo, tmpl_id, wimood_partner_id, new_price):
    """Update leveranciersprijs in het Inkoop-tabblad, of voeg toe als ontbrekend."""
    sellers = odoo.search_read(
        'product.supplierinfo',
        [('product_tmpl_id', '=', tmpl_id),
         ('partner_id', '=', wimood_partner_id)],
        ['id']
    )
    if sellers:
        odoo.write('product.supplierinfo', [sellers[0]['id']], {'price': new_price})
    else:
        odoo.create('product.supplierinfo', {
            'product_tmpl_id': tmpl_id,
            'partner_id':      wimood_partner_id,
            'price':           new_price,
            'min_qty':         1,
        })


# ── Categorie-mapping (zelfde logica als wimood.py) ────────────────────────────
def get_subcategory(name, code):
    n = name.lower()
    c = code.upper()
    if any(x in n for x in ['access point', 'nanohd', 'flexhd', 'in-wall hd',
                              'mesh point', 'u6 ', 'u7 ']):
        return 'Access Points'
    if 'switch' in n:
        return 'Switches'
    if any(x in n for x in ['dream machine', 'dream router', 'gateway',
                              'security gateway', 'cloud gateway']):
        return 'Gateways'
    if any(x in n for x in ['protect', 'doorbell', 'nvr', 'flood light', 'viewport']):
        return 'Beveiliging'
    if any(x in n for x in ['cloud key', 'redundant power', 'smartpower']):
        return 'Controllers'
    if c.startswith(('UAP', 'U6-', 'U7-')):
        return 'Access Points'
    if c.startswith('USW'):
        return 'Switches'
    if c.startswith(('UDM', 'USG', 'UXG', 'UDR', 'UCG')):
        return 'Gateways'
    if c.startswith(('UVC', 'UNVR', 'ENVR')):
        return 'Beveiliging'
    if c.startswith(('UCK', 'CKG', 'USP-')):
        return 'Controllers'
    return 'Accessoires'


# ── Hoofd sync ─────────────────────────────────────────────────────────────────
def main():
    ts_start = datetime.datetime.now()
    print(f"=== Wimood sync gestart: {ts_start.strftime('%Y-%m-%d %H:%M')} ===\n")

    # Wachtwoord: env-variabele ODOO_PASSWORD of interactief via stdin
    password = os.environ.get('ODOO_PASSWORD') or None
    odoo = OdooClient(password=password)

    # Veld aanmaken indien nodig
    print("Custom veld controleren…")
    ensure_wimood_stock_field(odoo)

    # Wimood leverancier ophalen
    partners = odoo.search_read('res.partner', [('name', '=', 'Wimood')], ['id'])
    if not partners:
        raise RuntimeError("Leverancier 'Wimood' niet gevonden — eerst wimood.py draaien")
    wimood_partner_id = partners[0]['id']

    # Categorie-cache voor nieuwe producten
    cat_netwerk = odoo.search_read(
        'product.category', [('name', '=', 'Netwerk & WiFi')], ['id'])
    subcats_cache = {}
    if cat_netwerk:
        subs = odoo.search_read(
            'product.category',
            [('parent_id', '=', cat_netwerk[0]['id'])],
            ['id', 'name']
        )
        subcats_cache = {s['name']: s['id'] for s in subs}

    placeholder = svg_placeholder('wifi')

    # Data ophalen
    print("\nWimood XML ophalen…")
    xml_products = get_unifi_from_xml(fetch_wimood_xml())
    print(f"  → {len(xml_products)} UniFi producten in XML")

    print("\nOdoo-producten ophalen…")
    odoo_products = get_odoo_wimood_products(odoo, wimood_partner_id)
    print(f"  → {len(odoo_products)} Wimood-producten in Odoo\n")

    # Resultaten
    price_changes = []
    stock_changes = []
    new_products  = []
    errors        = []

    print("Synchroniseren…")
    for code, xml_p in xml_products.items():
        try:
            if code in odoo_products:
                odoo_p  = odoo_products[code]
                tmpl_id = odoo_p['id']
                updates = {}

                # ── Prijs ──────────────────────────────────────────────────────
                old_cost = round(float(odoo_p.get('standard_price') or 0), 2)
                old_list = round(float(odoo_p.get('list_price')     or 0), 2)
                new_cost = xml_p['prijs']
                new_list = xml_p['msrp']

                cost_changed = abs(new_cost - old_cost) >= PRICE_MIN_DELTA
                list_changed = abs(new_list - old_list) >= PRICE_MIN_DELTA

                if cost_changed or list_changed:
                    if cost_changed:
                        updates['standard_price'] = new_cost
                    if list_changed:
                        updates['list_price'] = new_list
                    sync_seller_price(odoo, tmpl_id, wimood_partner_id, new_cost)

                    pct = round((new_cost - old_cost) / old_cost * 100, 1) if old_cost else 0
                    cat_name = odoo_p['categ_id'][1] if odoo_p.get('categ_id') else ''
                    price_changes.append({
                        'code':               code,
                        'name':               odoo_p['name'],
                        'category':           cat_name,
                        'old_standard_price': old_cost,
                        'new_standard_price': new_cost,
                        'old_list_price':     old_list,
                        'new_list_price':     new_list,
                        'pct_change':         pct,
                    })

                # ── Voorraad ───────────────────────────────────────────────────
                old_stock = int(odoo_p.get('x_wimood_stock') or 0)
                new_stock = xml_p['stock']
                if old_stock != new_stock:
                    updates['x_wimood_stock'] = new_stock
                    cat_name = odoo_p['categ_id'][1] if odoo_p.get('categ_id') else ''
                    stock_changes.append({
                        'code':      code,
                        'name':      odoo_p['name'],
                        'category':  cat_name,
                        'old_stock': old_stock,
                        'new_stock': new_stock,
                    })

                if updates:
                    odoo.write('product.template', [tmpl_id], updates)

            else:
                # ── Nieuw product ──────────────────────────────────────────────
                subcat   = get_subcategory(xml_p['name'], code)
                categ_id = subcats_cache.get(subcat) or subcats_cache.get('Accessoires')
                vals = {
                    'name':            xml_p['name'],
                    'default_code':    code,
                    'type':            'consu',
                    'categ_id':        categ_id,
                    'list_price':      xml_p['msrp'],
                    'standard_price':  xml_p['prijs'],
                    'purchase_ok':     True,
                    'sale_ok':         True,
                    'is_published':    False,
                    'x_wimood_stock':  xml_p['stock'],
                    'seller_ids': [(0, 0, {
                        'partner_id': wimood_partner_id,
                        'price':      xml_p['prijs'],
                        'min_qty':    1,
                    })],
                }
                tmpl_id = odoo.create('product.template', vals)
                odoo.write('product.template', [tmpl_id], {'image_1920': placeholder})
                new_products.append({'code': code, 'name': xml_p['name']})
                print(f"  + Nieuw: {code} — {xml_p['name'][:50]}")

        except Exception as e:
            errors.append({'code': code, 'error': str(e)})
            print(f"  ✗ Fout {code}: {e}", file=sys.stderr)

    # ── Samenvatting ───────────────────────────────────────────────────────────
    duration = int((datetime.datetime.now() - ts_start).total_seconds())
    payload = {
        'timestamp':    ts_start.isoformat(),
        'duration_sec': duration,
        'sync_stats': {
            'total_xml':      len(xml_products),
            'total_odoo':     len(odoo_products),
            'prices_updated': len(price_changes),
            'stock_updated':  len(stock_changes),
            'new_products':   len(new_products),
            'errors':         len(errors),
        },
        'price_changes': price_changes,
        'stock_changes': stock_changes,
        'new_products':  new_products,
        'errors':        errors,
    }

    print(f"\n{'─' * 52}")
    print(f"Prijswijzigingen:     {len(price_changes)}")
    print(f"Voorraadwijzigingen:  {len(stock_changes)}")
    print(f"Nieuwe producten:     {len(new_products)}")
    if errors:
        print(f"Fouten:              {len(errors)}")
    print(f"Duur:                 {duration}s")

    # ── POST naar n8n webhook ──────────────────────────────────────────────────
    json_str = json.dumps(payload, ensure_ascii=False)
    r = subprocess.run(
        ["curl", "-sfX", "POST", N8N_WEBHOOK_URL,
         "-H", "Content-Type: application/json",
         "--max-time", "15",
         "-d", json_str],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print(f"\n✓ n8n webhook verstuurd ({N8N_WEBHOOK_URL})")
    else:
        print(f"\n✗ n8n webhook mislukt — resultaten opgeslagen als fallback-bestand",
              file=sys.stderr)
        fallback = f"/tmp/wimood_sync_{ts_start.strftime('%Y%m%d_%H%M')}.json"
        with open(fallback, 'w') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"  → {fallback}", file=sys.stderr)

    print(f"\n=== Sync voltooid: {datetime.datetime.now().strftime('%H:%M:%S')} ===")


if __name__ == '__main__':
    main()
