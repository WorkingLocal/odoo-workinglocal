#!/usr/bin/env python3
"""
Working Local — Odoo CE volledig importscript
=============================================
Importeert categorieën, attributen en alle producten vanuit pv-consulting.com.

Gebruik:
    python3 odoo_import_full.py

Vereisten:
    - Odoo CE online bereikbaar
    - eCommerce-module geactiveerd (vereist voor product.image galerij)
    - curl beschikbaar op het systeem (voor afbeeldingen ophalen)

Werking:
    - Idempotent: producten die al bestaan (op default_code) worden overgeslagen
    - Afbeeldingen: hoofdafbeelding + galerij gescraped van pv-consulting.com
    - Aankoopprijs: automatisch gescraped van pv-consulting.com (incl. → excl. 21% BTW)
    - Omschrijvingen: offerteomschrijving + ecommerce-omschrijving van leverancier
    - Placeholders: SVG-afbeeldingen voor diensten zonder foto
"""

import xmlrpc.client, subprocess, re, base64, time
from html import unescape

# ── Verbinding ────────────────────────────────────────────────────────────────
URL      = 'https://odoo.workinglocal.be'
DB       = 'workinglocal'
USERNAME = 'info@workinglocal.be'
PASSWORD = input("Odoo wachtwoord: ")
BTW      = 1.21   # BTW-factor voor aankoopprijs omrekening
PV_BASE  = 'https://pv-consulting.com/products/'
PV_IMG   = 'https://pv-consulting.com/images/'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid    = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("Login mislukt!")
    exit(1)
print(f"Ingelogd als uid={uid}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def exe(model, method, args=None, kw=None):
    return models.execute_kw(DB, uid, PASSWORD, model, method, args or [], kw or {})

def search_read(model, domain, fields):
    return exe(model, 'search_read', [domain], {'fields': fields})

def create(model, vals):
    return exe(model, 'create', [vals])

def write(model, ids, vals):
    return exe(model, 'write', [ids, vals])

# ── Afbeeldingen helpers ──────────────────────────────────────────────────────
PV_IMG_SKIP = {
    "pvconsultingMainLogo.png", "pvconsultingInvertedColor.png",
    "1946488.png", "1451574.png", "1170678.png", "2590818.png",
    "Digital_Inline_Green.png",
}

def curl_bytes(url):
    r = subprocess.run(["curl", "-sf", "--max-time", "20", url], capture_output=True)
    return r.stdout if r.returncode == 0 else b''

def b64(data):
    return base64.b64encode(data).decode('utf-8')

def scrape_page(slug):
    """Haal naam, offerteomschrijving, ecommerce-omschrijving, prijs en afbeeldingen op."""
    html = curl_bytes(PV_BASE + slug).decode('utf-8', errors='replace')
    if len(html) < 500:
        return {}

    result = {}

    m = re.search(r'<h2[^>]*u-text-1[^>]*>([^<]+)', html)
    if m:
        result['pv_name'] = unescape(m.group(1).strip())

    m = re.search(r'u-product-desc[^>]*>\s*([^<]{5,})', html)
    if m:
        result['description_sale'] = unescape(m.group(1).strip())

    m = re.search(r'u-product-full-desc[^>]*>\s*([^<]{5,})', html)
    if m:
        result['website_description'] = '<p>' + unescape(m.group(1).strip()) + '</p>'

    m = re.search(r'u-price[^>]*>\s*€\s*([\d.,]+)', html)
    if m:
        try:
            price_incl = float(m.group(1).replace(',', '.'))
            result['standard_price'] = round(price_incl / BTW, 2)
        except ValueError:
            pass

    filenames = re.findall(r'<img[^>]+src=["\']\.\.\/images\/([^"\']+)["\']', html)
    seen = set()
    unique = [f for f in filenames if f not in PV_IMG_SKIP and not (f in seen or seen.add(f))]
    result['images'] = unique

    return result

def upload_images(tmpl_id, images):
    """Upload afbeeldingen: eerste als hoofdafbeelding, rest als galerij."""
    for i, fname in enumerate(images):
        data = curl_bytes(PV_IMG + fname)
        if not data:
            continue
        if i == 0:
            write('product.template', [tmpl_id], {'image_1920': b64(data)})
        else:
            create('product.image', {
                'product_tmpl_id': tmpl_id,
                'image_1920': b64(data),
                'name': fname,
            })
        time.sleep(0.15)

# ── SVG placeholder helper ────────────────────────────────────────────────────
SVG_ICONS = {
    'wifi': (
        '<circle cx="200" cy="230" r="20" fill="#F5B800"/>'
        '<path d="M140,180 Q200,130 260,180" stroke="#F5B800" stroke-width="14" fill="none" stroke-linecap="round"/>'
        '<path d="M100,145 Q200,75 300,145" stroke="#F5B800" stroke-width="14" fill="none" stroke-linecap="round" opacity="0.7"/>'
        '<path d="M60,110 Q200,20 340,110" stroke="#F5B800" stroke-width="14" fill="none" stroke-linecap="round" opacity="0.4"/>',
        'WiFi & Internet'
    ),
    'focus': (
        '<circle cx="200" cy="200" r="120" stroke="#F5B800" stroke-width="12" fill="none"/>'
        '<circle cx="200" cy="200" r="80" stroke="#F5B800" stroke-width="12" fill="none" opacity="0.7"/>'
        '<circle cx="200" cy="200" r="40" stroke="#F5B800" stroke-width="12" fill="none" opacity="0.4"/>'
        '<circle cx="200" cy="200" r="12" fill="#F5B800"/>',
        'Focussessies'
    ),
    'av': (
        '<rect x="60" y="130" width="210" height="140" rx="16" fill="none" stroke="#F5B800" stroke-width="14"/>'
        '<polygon points="290,145 340,110 340,290 290,255" fill="#F5B800" opacity="0.85"/>'
        '<circle cx="155" cy="200" r="35" fill="none" stroke="#F5B800" stroke-width="10"/>'
        '<circle cx="155" cy="200" r="14" fill="#F5B800"/>',
        'AV & Studio'
    ),
    'logistiek': (
        '<rect x="40" y="150" width="200" height="120" rx="10" fill="none" stroke="#F5B800" stroke-width="14"/>'
        '<path d="M240,175 L240,270 L340,270 L340,230 L310,175 Z" stroke="#F5B800" stroke-width="14" fill="none" stroke-linejoin="round"/>'
        '<line x1="40" y1="270" x2="340" y2="270" stroke="#F5B800" stroke-width="14"/>'
        '<circle cx="100" cy="280" r="22" fill="#1A2E5A" stroke="#F5B800" stroke-width="10"/>'
        '<circle cx="280" cy="280" r="22" fill="#1A2E5A" stroke="#F5B800" stroke-width="10"/>',
        'Logistiek'
    ),
    'verhuur': (
        '<circle cx="160" cy="190" r="80" stroke="#F5B800" stroke-width="14" fill="none"/>'
        '<circle cx="160" cy="190" r="35" fill="#F5B800" opacity="0.3"/>'
        '<line x1="222" y1="228" x2="330" y2="310" stroke="#F5B800" stroke-width="20" stroke-linecap="round"/>'
        '<line x1="285" y1="275" x2="305" y2="255" stroke="#F5B800" stroke-width="14" stroke-linecap="round"/>'
        '<line x1="310" y1="293" x2="330" y2="273" stroke="#F5B800" stroke-width="14" stroke-linecap="round"/>',
        'Verhuur'
    ),
}

def svg_placeholder(icon_key):
    shapes, label = SVG_ICONS[icon_key]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">'
        '<rect width="400" height="400" fill="#1A2E5A"/>'
        f'{shapes}'
        f'<text x="200" y="360" font-family="Arial,sans-serif" font-size="22" font-weight="bold"'
        f' text-anchor="middle" fill="#F5B800" opacity="0.9">{label}</text>'
        '</svg>'
    )
    return b64(svg.encode('utf-8'))

# ── Categorieën ───────────────────────────────────────────────────────────────
print("\n=== 1. Categorieën ===")

def get_or_create_cat(name, parent_id=None):
    domain = [('name', '=', name)]
    if parent_id:
        domain.append(('parent_id', '=', parent_id))
    res = search_read('product.category', domain, ['id'])
    if res:
        return res[0]['id']
    vals = {'name': name}
    if parent_id:
        vals['parent_id'] = parent_id
    cid = create('product.category', vals)
    print(f"  ✓ Categorie: {name}")
    return cid

parents = {
    'Circulaire werkplek': get_or_create_cat('Circulaire werkplek'),
    'Beeldschermen':       get_or_create_cat('Beeldschermen'),
    'Informatieschermen':  get_or_create_cat('Informatieschermen'),
    'IT-hardware':         get_or_create_cat('IT-hardware'),
    'Accessoires':         get_or_create_cat('Accessoires'),
    'Meubelen':            get_or_create_cat('Meubelen'),
    'Diensten':            get_or_create_cat('Diensten'),
}
children_map = {
    'Circulaire werkplek': ["Bureau's", 'Tafels', 'Stoelen'],
    'Beeldschermen':       ['22"', '27"', '32"', '34" Ultrawide'],
    'IT-hardware':         ['Laptops', "Desktops & mini-pc's", 'Servers & werkstations'],
    'Accessoires':         ['Monitorarmen', 'Docking stations', 'Draadloze desktops', 'Conference sets'],
    'Meubelen':            ['Kasten', 'Zitmeubelen'],
    'Diensten':            ['Wifi', 'Focussessies', 'AV & Studio', 'Logistiek'],
}
cat_ids = dict(parents)
for parent_name, child_names in children_map.items():
    for child_name in child_names:
        cat_ids[child_name] = get_or_create_cat(child_name, parent_id=parents[parent_name])
print(f"✓ {len(cat_ids)} categorieën klaar")

# ── Attributen ────────────────────────────────────────────────────────────────
print("\n=== 2. Attributen ===")
attrs_def = {
    'Merk':            ['Dell','HP','Lenovo','LG','Samsung','Philips','NEC','SMART','Huawei','Polycom'],
    'Schermdiagonaal': ['22"','23"','27"','32"','34"','42"','43"','55"','75"'],
    'Resolutie':       ['Full HD (1080p)','QHD (1440p)','4K UHD','WQHD Ultrawide (3440×1440)'],
    'Staat':           ['Refurbished','Nieuw in doos','Nieuw ongebruikt'],
}
attr_ids = {}
for attr_name, values in attrs_def.items():
    res = search_read('product.attribute', [('name', '=', attr_name)], ['id'])
    attr_id = res[0]['id'] if res else create('product.attribute',
        {'name': attr_name, 'create_variant': 'no_variant'})
    attr_ids[attr_name] = attr_id
    for v in values:
        vres = search_read('product.attribute.value',
            [('name', '=', v), ('attribute_id', '=', attr_id)], ['id'])
        if not vres:
            create('product.attribute.value', {'name': v, 'attribute_id': attr_id})
            print(f"  ✓ {attr_name}: {v}")
print(f"✓ {len(attr_ids)} attributen klaar")

# ── Product helpers ───────────────────────────────────────────────────────────
def make_product(ref, name, cat_key, list_price, ptype='consu',
                 description='', slug=None, placeholder=None):
    """
    Maak product aan of update bestaand product.
    - ref: SKU / default_code
    - name: Working Local productnaam
    - cat_key: sleutel in cat_ids dict
    - list_price: verkoopprijs excl. BTW
    - ptype: 'consu' (fysiek) of 'service'
    - description: fallback offerteomschrijving (wordt overschreven door pv-scrape)
    - slug: pv-consulting.com productpagina slug (voor omschrijvingen, prijs, foto's)
    - placeholder: SVG icon-key voor diensten zonder foto ('wifi','focus','av','logistiek','verhuur')
    """
    existing = search_read('product.template', [('default_code', '=', ref)], ['id', 'name'])
    if existing:
        tmpl_id = existing[0]['id']
        is_new = False
    else:
        vals = {
            'name':          name,
            'default_code':  ref,
            'categ_id':      cat_ids.get(cat_key, cat_ids['Diensten']),
            'list_price':    list_price,
            'type':          ptype,
            'sale_ok':       True,
            'purchase_ok':   ptype == 'consu',
        }
        if description:
            vals['description_sale'] = description
        tmpl_id = create('product.template', vals)
        is_new = True
        print(f"  ✓ {ref}: {name}")

    # Scrape van pv-consulting indien slug opgegeven
    if slug:
        pv = scrape_page(slug)
        update_vals = {}
        if pv.get('description_sale'):
            update_vals['description_sale'] = pv['description_sale']
        if pv.get('website_description'):
            update_vals['website_description'] = pv['website_description']
        if pv.get('standard_price'):
            update_vals['standard_price'] = pv['standard_price']
        if update_vals:
            write('product.template', [tmpl_id], update_vals)
        if pv.get('images') and is_new:
            upload_images(tmpl_id, pv['images'])
        elif not pv.get('images') and placeholder and is_new:
            write('product.template', [tmpl_id], {'image_1920': svg_placeholder(placeholder)})
        time.sleep(0.3)

    # Placeholder voor diensten zonder pv-slug
    if not slug and placeholder and is_new:
        write('product.template', [tmpl_id], {'image_1920': svg_placeholder(placeholder)})

    return tmpl_id

# ── 3. Diensten ───────────────────────────────────────────────────────────────
print("\n=== 3. Diensten ===")

# Wifi
make_product('SRV-WIFI-01', 'Wifi-audit met planning, aankoopadvies en -begeleiding',
    'Wifi', 199, 'service', 'Forfait', placeholder='wifi')
make_product('SRV-WIFI-02', 'Wifi-installatie',
    'Wifi', 65, 'service', 'Uurprijs', placeholder='wifi')
make_product('SRV-WIFI-03', 'Wifi-configuratie',
    'Wifi', 65, 'service', 'Uurprijs', placeholder='wifi')
make_product('SRV-WIFI-04', 'Wifi-interventie op afstand',
    'Wifi', 50, 'service', 'Forfait', placeholder='wifi')
make_product('SRV-WIFI-05', 'Wifi-interventie ter plaatse',
    'Wifi', 99, 'service', 'Forfait', placeholder='wifi')

# Focussessies
make_product('SRV-FOCUS-01', 'Begeleide focussessie — halve dag',
    'Focussessies', 149, 'service', 'Forfait', placeholder='focus')
make_product('SRV-FOCUS-02', 'Begeleide focussessie — volledige dag',
    'Focussessies', 249, 'service', 'Forfait', placeholder='focus')
make_product('SRV-FOCUS-03', 'Huur Focus Kiosk voor zelfbegeleide sessies',
    'Focussessies', 99, 'service', 'Verhuur/dag', placeholder='focus')

# AV & Studio
make_product('SRV-AV-01', 'OBS-studio operator — halve dag',
    'AV & Studio', 149, 'service', 'Forfait', placeholder='av')
make_product('SRV-AV-02', 'OBS-studio operator — volledige dag',
    'AV & Studio', 249, 'service', 'Forfait', placeholder='av')
make_product('SRV-AV-03', 'OBS-studio operator — in regie',
    'AV & Studio', 65, 'service', 'Uurprijs', placeholder='av')

# Logistiek
make_product('SRV-LOG-01', 'Verhuis-, plaatsings- en montageservice',
    'Logistiek', 50, 'service', 'Uurprijs', placeholder='logistiek')

# ── 4. Bureau's ───────────────────────────────────────────────────────────────
print("\n=== 4. Bureau's ===")
make_product('DESK-01',
    "Refurbished Bureau 180×80 cm — verstelbaar 62–82 cm, asymmetrisch blad, kabelgoot",
    "Bureau's", 119,
    slug='bureau-180-x-80---62-82cm-hoog.html')
make_product('DESK-02',
    'Refurbished Slingerbureau Ahrend 160×80 cm — Trespa-blad, verstelbaar 64–90 cm',
    "Bureau's", 179,
    slug='slingerbureau-ahrend-160x80-64-90cm-hoog.html')
make_product('DESK-03',
    'Refurbished Bureau Kinnarps 160×80 cm — demonteerbare poten, kabelgoot, hoogteverstelbaar',
    "Bureau's", 99,
    slug='tafel-kinnarps---160-x-80.html')
make_product('DESK-04',
    'Refurbished Zit-sta Bureau 160×80 cm — verstelbaar 64–110 cm',
    "Bureau's", 199,
    slug='zit-sta-bureau-160x80-64-110cm-hoog.html')

# ── 5. Tafels ─────────────────────────────────────────────────────────────────
print("\n=== 5. Tafels ===")
make_product('TABLE-01',
    'Refurbished Vergadertafel 100×125 cm — vaste hoogte 70 cm, demonteerbare poten',
    'Tafels', 89,
    slug='tafel-tds-100x125cm.html')
make_product('TABLE-02',
    'Rechthoekige tafel',
    'Tafels', 0,
    description='Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag.',
    placeholder='verhuur')

# ── 6. Beeldschermen ──────────────────────────────────────────────────────────
print('\n=== 6. Beeldschermen 22"/23" ===')
make_product('MON-22-01',
    'Beeldscherm 22" Full HD — Dell P2219H, HDMI/DP/VGA, USB-hub, roterende voet',
    '22"', 89,
    slug='dell-22--p2219h-hd.html')
make_product('MON-22-02',
    'Beeldscherm 23" Full HD — HP EliteDisplay E232, zonder voet',
    '22"', 39,
    slug='hp-elitedisplay-e232---hd.html')

print('\n=== 6. Beeldschermen 27" ===')
make_product('MON-27-01',
    'Beeldscherm 27" Full HD — Dell P2717H, HDMI/DP/VGA, USB-hub, voet apart',
    '27"', 109,
    slug='dell-27--p2717h-hd-monitor.html')
make_product('MON-27-02',
    'Beeldscherm 27" QHD — HP Z27n, kantelbare HP-voet',
    '27"', 139,
    slug='hp-27--z27n-qhd.html')
make_product('MON-27-03',
    'Beeldscherm 27" 4K — HP S270n, USB-C 60W, hoogteverstelbaar',
    '27"', 219,
    slug='hp-s270n-27inch-4k.html')
make_product('MON-27-04',
    'Beeldscherm 27" QHD — Lenovo P27h-10, USB-C PD, op voet',
    '27"', 189,
    slug='lenovo-thinkvision-27--qhd-p27h-10-monitor-op-voet.html')
make_product('MON-27-05',
    'Beeldscherm 27" QHD — Lenovo P27h-20, USB-C 90W + Ethernet + luidsprekers, zonder voet',
    '27"', 169,
    slug='lenovo-thinkvision-p27h-20-qhd-ips-panel.html')
make_product('MON-27-06',
    'Beeldscherm 27" QHD — Dell U2721DE, USB-C docking + Ethernet, Dell-voet',
    '27"', 199,
    slug='dell-27--u2721de-qhd-met-ingebouwde-docking-station.html')
make_product('MON-27-07',
    'Beeldscherm 27" QHD — Dell P2723DE, USB-C 90W + HDMI + DP + Ethernet, zonder voet',
    '27"', 199,
    slug='dell-27--p2723de-qhd-usb-c-hub-monitor.html')
make_product('MON-27-08',
    'Beeldscherm 27" 4K — LG, design voet, kantelbaar/verstelbaar',
    '27"', 219,
    slug='lg-27--4k-schermen.html')
make_product('MON-27-SET',
    'Set 2× Beeldscherm 27" QHD — Dell U2717D op Ergotron-voet',
    '27"', 249,
    slug='set-dell-27--u2717d-qhd.html')

print('\n=== 6. Beeldschermen 32" ===')
make_product('MON-32-01',
    'Beeldscherm 32" 4K — Lenovo P32p-20, USB-C 90W + Ethernet, IPS, zonder voet',
    '32"', 249,
    slug='lenovo-thinkvision-p32p-20-4k-ips-panel.html')

print('\n=== 6. Beeldschermen 34" Ultrawide ===')
make_product('MON-34-01',
    'Ultrabreed Beeldscherm 34" QHD — LG 34WK650, IPS, 75Hz, 2×HDMI+DP, op voet',
    '34" Ultrawide', 219,
    slug='lg-34--34wk650-w-qhd-monitor.html')
make_product('MON-34-02',
    'Curved Ultrabreed 34" WQHD — Dell U3419W, USB-C hub, op voet',
    '34" Ultrawide', 409,
    slug='dell-34--u3419w-curved-wqhd-monitor---zeer-goede-staat.html')
make_product('MON-34-03',
    'Curved Ultrabreed 34" WQHD — Dell P3424WE, USB-C 90W + Ethernet, nieuw ongebruikt',
    '34" Ultrawide', 439,
    slug='dell-34--p3424we-curved-wqhd-monitor---nieuw.html')

# ── 7. Informatieschermen ────────────────────────────────────────────────────
print("\n=== 7. Informatieschermen ===")
make_product('SIGN-01',
    'Informatiescherm 32" Full HD — NEC MultiSync E328, HDMI/USB, luidsprekers, nieuw in doos',
    'Informatieschermen', 299,
    slug='nec-multisync-e328-2-32--signage-screen---nieuw-in-doos.html')
make_product('SIGN-02',
    'Smart Display 75" 4K Android — SMART Board NX175, geen aanraking, nieuw in doos',
    'Informatieschermen', 899,
    slug='smart-board-nx175---75----4k--no-touch----nieuw.html')
make_product('SIGN-03',
    'Informatiescherm 43" 4K — Samsung LH43Q, VESA, refurbished',
    'Informatieschermen', 239,
    slug='samsung-4k-lh43q-signage-display.html')
make_product('SIGN-04',
    'Informatiescherm 42" HD — Philips BDL4270EL, met afstandsbediening, refurbished',
    'Informatieschermen', 219,
    slug='philips-hd-bdl4270el-signage-display.html')

# Verhuur informatieschermen
make_product('RENT-01',
    'Huur Informatiezuil 55" 4K LG 55UH5F op rijdend statief',
    'Informatieschermen', 99, 'service',
    slug='lg-55uh5f-h-55inch-signage-screen.html',
    placeholder='verhuur')
make_product('RENT-02',
    'Huur Hybride Meetingset 55" LG op statief + HP Poly conference bar',
    'Informatieschermen', 129, 'service',
    description='Dagprijs verhuur.',
    placeholder='verhuur')

# ── 8. Laptops ───────────────────────────────────────────────────────────────
print("\n=== 8. Laptops ===")
make_product('LAP-01',
    'Laptop Small 13" — HP EliteBook 830 G8, i7-1185G7, 16GB, 500GB, B&O, USB-C, Win11 Pro',
    'Laptops', 349,
    slug='hp-elitebook-830-g8-intel-i7-16gb-ram-500gb-m2.html')
make_product('LAP-02',
    'Laptop Small 14" — Lenovo ThinkBook 14 G2, i7-1165G7, 24GB, 512GB, wifi6, USB-C, Win11 Pro',
    'Laptops', 399,
    slug='lenovo-thinkbook-14-g2-itl-14--i7-24gb-ram.html')
make_product('LAP-03',
    'Laptop Normal 15,5" — HP EliteBook 855 G8, Ryzen 5, 16GB, 256GB, B&O, Win11 Pro',
    'Laptops', 399,
    slug='hp-elitebook-855-g8-15-5-.html')
make_product('LAP-04',
    'Laptop Normal 2-in-1 14" — Lenovo X1 Yoga Gen 6, i7, 16GB, 1TB, 4K touch 360°, Win11 Pro',
    'Laptops', 699,
    slug='lenovo-thinkpad-x1-yoga-gen-6-14--2-in-1-laptop-tablet.html')
make_product('LAP-05',
    'Laptop High End 14" — Dell Precision 5480, i7-13700H, 16GB, 512GB, RTX A1000 6GB, nieuw',
    'Laptops', 1499,
    slug='dell-precision-5480-i7-16gb-gpu-rtx-a1000-6gb---nieuw-in-doos.html')

# ── 9. Desktops & mini-pc's ──────────────────────────────────────────────────
print("\n=== 9. Desktops & mini-pc's ===")
make_product('PC-01',
    'Desktop Ultralight — Dell OptiPlex 3050 SFF, i5-6500, 8GB, 256GB NVMe, Win11 Pro',
    "Desktops & mini-pc's", 149,
    slug='dell-optiplex-3050-sff---pc.html')
make_product('PC-02',
    'Signage Client — Dell OptiPlex 3050 SFF, i5-6500, 8GB, 256GB NVMe, Win11 Pro + Xibo CMS',
    "Desktops & mini-pc's", 149,
    slug='dell-optiplex-3050-sff---pc.html')
make_product('PC-03',
    'Miniserver Linux — Dell OptiPlex 3050 SFF, i5-6500, 16GB, 256GB NVMe, Linux',
    "Desktops & mini-pc's", 249,
    slug='dell-optiplex-3050-sff---server.html')

# ── 10. Servers & werkstations ───────────────────────────────────────────────
print("\n=== 10. Servers & werkstations ===")
make_product('SRV-01',
    'Werkstation Basic — Lenovo P520, Xeon W, 16GB, 500GB NVMe, NVIDIA P1000 (4×miniDP), Win11 Pro',
    'Servers & werkstations', 299,
    slug='lenovo-p520---basic.html')
make_product('SRV-02',
    'Werkstation Pro — Lenovo P520, Xeon W, 32GB, 1TB NVMe (nieuw), NVIDIA P1000, Win11 Pro',
    'Servers & werkstations', 499,
    slug='lenovo-p520---pro.html')
make_product('SRV-03',
    'Server/Virtualisatiehost — Lenovo P520, Xeon W, 32GB, geen OS/opslag, NVIDIA P1000',
    'Servers & werkstations', 399,
    slug='lenovo-p520---server.html')
make_product('SRV-04',
    'Dual-CPU Werkstation/Server — Lenovo P720, 2× Xeon Gold 6134 (16c/32t), 64GB, 1TB NVMe, P1000, Win11 Pro WS',
    'Servers & werkstations', 899,
    slug='lenovo-p720---dual-cpu---gold.html')

# ── 11. Monitorarmen ─────────────────────────────────────────────────────────
print("\n=== 11. Monitorarmen ===")
make_product('ARM-01',
    'Enkele monitorarm',
    'Monitorarmen', 0,
    description='Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag.',
    placeholder='verhuur')
make_product('ARM-02',
    'Dubbele monitorarm High End — Humanscale M8, nieuw, tafelklem, max 2× 27", kabelgeleiding',
    'Monitorarmen', 199,
    slug='nieuw---humanscale-m8-monitorarm-voor-2-schermen.html')
make_product('ARM-03',
    'Dubbele monitorarm Flex — ACT8312, nieuw, gasveersysteem, VESA',
    'Monitorarmen', 149,
    slug='act8312-dubbele-monitorarm---nieuw.html')
make_product('ARM-04',
    'Dubbele monitorarm Basic — refurbished, tafelklem, max 2× 32", instelbaar gewicht, VESA',
    'Monitorarmen', 99,
    slug='dubbele-monitorarm-met-tafelklem.html')
make_product('ARM-05',
    'Vierledige monitorarm — Ewent Quad, nieuw, tafelklem, 4× max 32", VESA',
    'Monitorarmen', 99,
    slug='ewent-quad-monitor-voet---nieuw.html')

# ── 12. Docking stations ─────────────────────────────────────────────────────
print("\n=== 12. Docking stations ===")
make_product('DOCK-01',
    'Dell Thunderbolt Dock TB19 (2019)',
    'Docking stations', 0,
    description='Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag.',
    placeholder='verhuur')
make_product('DOCK-02',
    'Dell Thunderbolt Dock TB22 (2022)',
    'Docking stations', 0,
    description='Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag.',
    placeholder='verhuur')
make_product('DOCK-03',
    'Refurbished Dell USB-C Docking Station WD19 — 130W, USB-C, inclusief voeding',
    'Docking stations', 89,
    slug='dell-usb-c-docking-station-wd19-wd19s---130w.html')
make_product('DOCK-04',
    'HP Universele USB-C Multipoort Hub — nieuw, 7 poorten, DP/HDMI/Ethernet/USB',
    'Docking stations', 59,
    slug='hp-universal-usb-c-multiport-hub---nieuw-in-doos.html')

# ── 13. Conference sets ──────────────────────────────────────────────────────
print("\n=== 13. Conference sets ===")
make_product('CONF-01',
    'Refurbished Audio- en Videobar — HP Poly Studio P009, USB, camera+microfoon+luidspreker',
    'Conference sets', 249,
    slug='hp-poly-studio-p009.html')
make_product('CONF-02',
    'Refurbished Draadloze Headset — HP Poly Voyager Focus UC B825, ANC, 10u+, Bluetooth',
    'Conference sets', 89,
    slug='hp-poly-plantronics-voyager-focus-uc-b825-draadloze-headset.html')
make_product('CONF-03',
    'Refurbished IP-Telefoon USB — Polycom CX300 R2, Teams-gecertificeerd, speakerphone',
    'Conference sets', 79,
    slug='polycom-cx300-r2-ip-phone.html')
make_product('CONF-04',
    'IP-Telefoon 2-lijn SIP — Huawei eSpace 7810, nieuw, PoE, encryptie',
    'Conference sets', 89,
    slug='huawei-espace-7810-ip-phone-nieuw.html')

# ── 14. Meubelen ─────────────────────────────────────────────────────────────
print("\n=== 14. Meubelen ===")
make_product('FURN-01',
    'Refurbished Garderobe / Roomdivider 240×160×64 cm — afwasbaar, kapstokconstructie',
    'Kasten', 249,
    slug='garderobe-kast---room-divider---240b-x-160h-x-64d.html')
make_product('FURN-02',
    'Refurbished Hoge Roldeurkast MEWAF — metaal, roldeuren, verstelbare leggers',
    'Kasten', 219,
    slug='hoge-roldeurkast-mewaf.html')
make_product('FURN-03',
    'Refurbished Zitbank 2-persoons — groen, 128×80×98 cm, hoge zit',
    'Zitmeubelen', 199,
    slug='zitbank-groen.html')

# ── Klaar ─────────────────────────────────────────────────────────────────────
print("\n=== IMPORT VOLTOOID ===")
total = exe('product.template', 'search_count', [[]])
print(f"Totaal producten in Odoo: {total}")
