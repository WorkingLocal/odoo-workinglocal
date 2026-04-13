#!/usr/bin/env python3
"""
Leveranciersimport: PV Consulting (pv-consulting.com)
=====================================================
Importeert alle Working Local-producten van PV Consulting in Odoo CE.

Gebruik:
    python3 pv_consulting.py

Werking:
    - Idempotent: producten die al bestaan (op default_code) worden overgeslagen
    - Scrapet automatisch van pv-consulting.com:
        * Offerteomschrijving (u-product-desc)
        * Ecommerce-omschrijving (u-product-full-desc)
        * Aankoopprijs incl. 21% BTW → omgerekend naar excl.
        * Productafbeeldingen (hoofdfoto + galerij)
    - SVG-placeholders voor diensten zonder foto

Nieuwe producten toevoegen:
    Voeg een make_product() aanroep toe in de juiste sectie.
    Geef de slug van de pv-consulting productpagina mee.
    Alles (omschrijving, prijs, foto's) wordt automatisch opgehaald.
"""

import sys
import os
import time

# Zorg dat odoo_client.py vindbaar is (zelfde map)
sys.path.insert(0, os.path.dirname(__file__))
from odoo_client import (
    OdooClient, scrape_pv_page, upload_images,
    svg_placeholder, b64, PV_BTW
)

# ── Verbinding ────────────────────────────────────────────────────────────────
odoo = OdooClient()

# ── 1. Categorieën ───────────────────────────────────────────────────────────
print("\n=== 1. Categorieën ===")

parents = {
    'Circulaire werkplek': odoo.get_or_create_cat('Circulaire werkplek'),
    'Beeldschermen':       odoo.get_or_create_cat('Beeldschermen'),
    'Informatieschermen':  odoo.get_or_create_cat('Informatieschermen'),
    'IT-hardware':         odoo.get_or_create_cat('IT-hardware'),
    'Accessoires':         odoo.get_or_create_cat('Accessoires'),
    'Meubelen':            odoo.get_or_create_cat('Meubelen'),
    'Diensten':            odoo.get_or_create_cat('Diensten'),
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
        cat_ids[child_name] = odoo.get_or_create_cat(child_name,
            parent_id=parents[parent_name])
print(f"✓ {len(cat_ids)} categorieën klaar")

# ── 2. Attributen ────────────────────────────────────────────────────────────
print("\n=== 2. Attributen ===")
odoo.get_or_create_attribute('Merk',
    ['Dell','HP','Lenovo','LG','Samsung','Philips','NEC','SMART','Huawei','Polycom'])
odoo.get_or_create_attribute('Schermdiagonaal',
    ['22"','23"','27"','32"','34"','42"','43"','55"','75"'])
odoo.get_or_create_attribute('Resolutie',
    ['Full HD (1080p)','QHD (1440p)','4K UHD','WQHD Ultrawide (3440×1440)'])
odoo.get_or_create_attribute('Staat',
    ['Refurbished','Nieuw in doos','Nieuw ongebruikt'])
print("✓ Attributen klaar")

# ── Product helper ────────────────────────────────────────────────────────────
def make_product(ref, name, cat_key, list_price, ptype='consu',
                 description='', slug=None, placeholder=None,
                 standard_price=None):
    """
    Maak product aan (of sla over als het al bestaat).

    Parameters:
        ref           — SKU / default_code (unieke sleutel)
        name          — Working Local productnaam
        cat_key       — sleutel in cat_ids (bv. '27"', 'Laptops', 'Wifi')
        list_price    — verkoopprijs excl. BTW
        ptype         — 'consu' (fysiek product) of 'service'
        description   — fallback offerteomschrijving (overschreven door pv-scrape)
        slug          — pv-consulting.com pagina-slug; scrapet naam/omschrijving/prijs/foto's
        placeholder   — SVG icon voor producten zonder foto: 'wifi','focus','av','logistiek','verhuur'
        standard_price — handmatige aankoopprijs excl. BTW (overschrijft scrape-prijs)
    """
    vals = {
        'name':         name,
        'categ_id':     cat_ids.get(cat_key, cat_ids['Diensten']),
        'list_price':   list_price,
        'type':         ptype,
        'sale_ok':      True,
        'purchase_ok':  ptype == 'consu',
    }
    if description:
        vals['description_sale'] = description

    existing = odoo.search_read('product.template',
        [('default_code', '=', ref)], ['id', 'name'])
    if existing:
        print(f"  ~ Bestaat al: {ref} — {existing[0]['name'][:50]}")
        return existing[0]['id']

    # Scrape pv-consulting indien slug opgegeven
    pv = scrape_pv_page(slug) if slug else {}

    if pv.get('description_sale'):
        vals['description_sale'] = pv['description_sale']
    if pv.get('website_description'):
        vals['website_description'] = pv['website_description']
    if pv.get('standard_price'):
        vals['standard_price'] = pv['standard_price']

    # Handmatige aankoopprijs heeft voorrang op gescrapete prijs
    if standard_price is not None:
        vals['standard_price'] = standard_price

    vals['default_code'] = ref
    tmpl_id = odoo.create('product.template', vals)
    print(f"  ✓ {ref}: {name[:60]}")

    # Afbeeldingen
    if pv.get('images'):
        upload_images(odoo, tmpl_id, pv['images'])
    elif placeholder:
        odoo.write('product.template', [tmpl_id],
            {'image_1920': svg_placeholder(placeholder)})

    time.sleep(0.3)
    return tmpl_id


# ── 3. Diensten ───────────────────────────────────────────────────────────────
print("\n=== 3. Diensten ===")

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

make_product('SRV-FOCUS-01', 'Begeleide focussessie — halve dag',
    'Focussessies', 149, 'service', 'Forfait', placeholder='focus')
make_product('SRV-FOCUS-02', 'Begeleide focussessie — volledige dag',
    'Focussessies', 249, 'service', 'Forfait', placeholder='focus')
make_product('SRV-FOCUS-03', 'Huur Focus Kiosk voor zelfbegeleide sessies',
    'Focussessies', 99, 'service', 'Verhuur/dag', placeholder='focus')

make_product('SRV-AV-01', 'OBS-studio operator — halve dag',
    'AV & Studio', 149, 'service', 'Forfait', placeholder='av')
make_product('SRV-AV-02', 'OBS-studio operator — volledige dag',
    'AV & Studio', 249, 'service', 'Forfait', placeholder='av')
make_product('SRV-AV-03', 'OBS-studio operator — in regie',
    'AV & Studio', 65, 'service', 'Uurprijs', placeholder='av')

make_product('SRV-LOG-01', 'Verhuis-, plaatsings- en montageservice',
    'Logistiek', 50, 'service', 'Uurprijs', placeholder='logistiek')

# ── 4. Bureau's ───────────────────────────────────────────────────────────────
print("\n=== 4. Bureau's ===")
make_product('DESK-01',
    "Refurbished Bureau 180×80 cm — verstelbaar 62–82 cm, asymmetrisch blad, kabelgoot",
    "Bureau's", 119, slug='bureau-180-x-80---62-82cm-hoog.html')
make_product('DESK-02',
    'Refurbished Slingerbureau Ahrend 160×80 cm — Trespa-blad, verstelbaar 64–90 cm',
    "Bureau's", 179, slug='slingerbureau-ahrend-160x80-64-90cm-hoog.html')
make_product('DESK-03',
    'Refurbished Bureau Kinnarps 160×80 cm — demonteerbare poten, kabelgoot, hoogteverstelbaar',
    "Bureau's", 99, slug='tafel-kinnarps---160-x-80.html')
make_product('DESK-04',
    'Refurbished Zit-sta Bureau 160×80 cm — verstelbaar 64–110 cm',
    "Bureau's", 199, slug='zit-sta-bureau-160x80-64-110cm-hoog.html')

# ── 5. Tafels ─────────────────────────────────────────────────────────────────
print("\n=== 5. Tafels ===")
make_product('TABLE-01',
    'Refurbished Vergadertafel 100×125 cm — vaste hoogte 70 cm, demonteerbare poten',
    'Tafels', 89, slug='tafel-tds-100x125cm.html')
make_product('TABLE-02',
    'Rechthoekige tafel', 'Tafels', 0,
    description='Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag.',
    placeholder='verhuur')

# ── 6. Beeldschermen 22"/23" ─────────────────────────────────────────────────
print('\n=== 6. Beeldschermen 22"/23" ===')
make_product('MON-22-01',
    'Beeldscherm 22" Full HD — Dell P2219H, HDMI/DP/VGA, USB-hub, roterende voet',
    '22"', 89, slug='dell-22--p2219h-hd.html')
make_product('MON-22-02',
    'Beeldscherm 23" Full HD — HP EliteDisplay E232, zonder voet',
    '22"', 39, slug='hp-elitedisplay-e232---hd.html')

# ── 6. Beeldschermen 27" ─────────────────────────────────────────────────────
print('\n=== 6. Beeldschermen 27" ===')
make_product('MON-27-01',
    'Beeldscherm 27" Full HD — Dell P2717H, HDMI/DP/VGA, USB-hub, voet apart',
    '27"', 109, slug='dell-27--p2717h-hd-monitor.html')
make_product('MON-27-02',
    'Beeldscherm 27" QHD — HP Z27n, kantelbare HP-voet',
    '27"', 139, slug='hp-27--z27n-qhd.html')
make_product('MON-27-03',
    'Beeldscherm 27" 4K — HP S270n, USB-C 60W, hoogteverstelbaar',
    '27"', 219, slug='hp-s270n-27inch-4k.html')
make_product('MON-27-04',
    'Beeldscherm 27" QHD — Lenovo P27h-10, USB-C PD, op voet',
    '27"', 189, slug='lenovo-thinkvision-27--qhd-p27h-10-monitor-op-voet.html')
make_product('MON-27-05',
    'Beeldscherm 27" QHD — Lenovo P27h-20, USB-C 90W + Ethernet + luidsprekers, zonder voet',
    '27"', 169, slug='lenovo-thinkvision-p27h-20-qhd-ips-panel.html')
make_product('MON-27-06',
    'Beeldscherm 27" QHD — Dell U2721DE, USB-C docking + Ethernet, Dell-voet',
    '27"', 199, slug='dell-27--u2721de-qhd-met-ingebouwde-docking-station.html')
make_product('MON-27-07',
    'Beeldscherm 27" QHD — Dell P2723DE, USB-C 90W + HDMI + DP + Ethernet, zonder voet',
    '27"', 199, slug='dell-27--p2723de-qhd-usb-c-hub-monitor.html')
make_product('MON-27-08',
    'Beeldscherm 27" 4K — LG, design voet, kantelbaar/verstelbaar',
    '27"', 219, slug='lg-27--4k-schermen.html')
make_product('MON-27-SET',
    'Set 2× Beeldscherm 27" QHD — Dell U2717D op Ergotron-voet',
    '27"', 249, slug='set-dell-27--u2717d-qhd.html')

# ── 6. Beeldschermen 32" ─────────────────────────────────────────────────────
print('\n=== 6. Beeldschermen 32" ===')
make_product('MON-32-01',
    'Beeldscherm 32" 4K — Lenovo P32p-20, USB-C 90W + Ethernet, IPS, zonder voet',
    '32"', 249, slug='lenovo-thinkvision-p32p-20-4k-ips-panel.html')

# ── 6. Beeldschermen 34" Ultrawide ───────────────────────────────────────────
print('\n=== 6. Beeldschermen 34" Ultrawide ===')
make_product('MON-34-01',
    'Ultrabreed Beeldscherm 34" QHD — LG 34WK650, IPS, 75Hz, 2×HDMI+DP, op voet',
    '34" Ultrawide', 219, slug='lg-34--34wk650-w-qhd-monitor.html')
make_product('MON-34-02',
    'Curved Ultrabreed 34" WQHD — Dell U3419W, USB-C hub, op voet',
    '34" Ultrawide', 409, slug='dell-34--u3419w-curved-wqhd-monitor---zeer-goede-staat.html')
make_product('MON-34-03',
    'Curved Ultrabreed 34" WQHD — Dell P3424WE, USB-C 90W + Ethernet, nieuw ongebruikt',
    '34" Ultrawide', 439, slug='dell-34--p3424we-curved-wqhd-monitor---nieuw.html')

# ── 7. Informatieschermen ────────────────────────────────────────────────────
print("\n=== 7. Informatieschermen ===")
make_product('SIGN-01',
    'Informatiescherm 32" Full HD — NEC MultiSync E328, HDMI/USB, luidsprekers, nieuw in doos',
    'Informatieschermen', 299, slug='nec-multisync-e328-2-32--signage-screen---nieuw-in-doos.html')
make_product('SIGN-02',
    'Smart Display 75" 4K Android — SMART Board NX175, geen aanraking, nieuw in doos',
    'Informatieschermen', 899, slug='smart-board-nx175---75----4k--no-touch----nieuw.html')
make_product('SIGN-03',
    'Informatiescherm 43" 4K — Samsung LH43Q, VESA, refurbished',
    'Informatieschermen', 239, slug='samsung-4k-lh43q-signage-display.html')
make_product('SIGN-04',
    'Informatiescherm 42" HD — Philips BDL4270EL, met afstandsbediening, refurbished',
    'Informatieschermen', 219, slug='philips-hd-bdl4270el-signage-display.html')
make_product('RENT-01',
    'Huur Informatiezuil 55" 4K LG 55UH5F op rijdend statief',
    'Informatieschermen', 99, 'service',
    slug='lg-55uh5f-h-55inch-signage-screen.html', placeholder='verhuur')
make_product('RENT-02',
    'Huur Hybride Meetingset 55" LG op statief + HP Poly conference bar',
    'Informatieschermen', 129, 'service',
    description='Dagprijs verhuur.', placeholder='verhuur')

# ── 8. Laptops ───────────────────────────────────────────────────────────────
print("\n=== 8. Laptops ===")
make_product('LAP-01',
    'Laptop Small 13" — HP EliteBook 830 G8, i7-1185G7, 16GB, 500GB, B&O, USB-C, Win11 Pro',
    'Laptops', 349, slug='hp-elitebook-830-g8-intel-i7-16gb-ram-500gb-m2.html')
make_product('LAP-02',
    'Laptop Small 14" — Lenovo ThinkBook 14 G2, i7-1165G7, 24GB, 512GB, wifi6, USB-C, Win11 Pro',
    'Laptops', 399, slug='lenovo-thinkbook-14-g2-itl-14--i7-24gb-ram.html')
make_product('LAP-03',
    'Laptop Normal 15,5" — HP EliteBook 855 G8, Ryzen 5, 16GB, 256GB, B&O, Win11 Pro',
    'Laptops', 399, slug='hp-elitebook-855-g8-15-5-.html')
make_product('LAP-04',
    'Laptop Normal 2-in-1 14" — Lenovo X1 Yoga Gen 6, i7, 16GB, 1TB, 4K touch 360°, Win11 Pro',
    'Laptops', 699, slug='lenovo-thinkpad-x1-yoga-gen-6-14--2-in-1-laptop-tablet.html')
make_product('LAP-05',
    'Laptop High End 14" — Dell Precision 5480, i7-13700H, 16GB, 512GB, RTX A1000 6GB, nieuw',
    'Laptops', 1499,
    slug='dell-precision-5480-i7-16gb-gpu-rtx-a1000-6gb---nieuw-in-doos.html',
    standard_price=round(1499 / PV_BTW, 2))  # pv-consulting toont geen prijs online

# ── 9. Desktops & mini-pc's ──────────────────────────────────────────────────
print("\n=== 9. Desktops & mini-pc's ===")
make_product('PC-01',
    'Desktop Ultralight — Dell OptiPlex 3050 SFF, i5-6500, 8GB, 256GB NVMe, Win11 Pro',
    "Desktops & mini-pc's", 149, slug='dell-optiplex-3050-sff---pc.html')
make_product('PC-02',
    'Signage Client — Dell OptiPlex 3050 SFF, i5-6500, 8GB, 256GB NVMe, Win11 Pro + Xibo CMS',
    "Desktops & mini-pc's", 149, slug='dell-optiplex-3050-sff---pc.html')
make_product('PC-03',
    'Miniserver Linux — Dell OptiPlex 3050 SFF, i5-6500, 16GB, 256GB NVMe, Linux',
    "Desktops & mini-pc's", 249, slug='dell-optiplex-3050-sff---server.html')

# ── 10. Servers & werkstations ───────────────────────────────────────────────
print("\n=== 10. Servers & werkstations ===")
make_product('SRV-01',
    'Werkstation Basic — Lenovo P520, Xeon W, 16GB, 500GB NVMe, NVIDIA P1000 (4×miniDP), Win11 Pro',
    'Servers & werkstations', 299, slug='lenovo-p520---basic.html')
make_product('SRV-02',
    'Werkstation Pro — Lenovo P520, Xeon W, 32GB, 1TB NVMe (nieuw), NVIDIA P1000, Win11 Pro',
    'Servers & werkstations', 499, slug='lenovo-p520---pro.html')
make_product('SRV-03',
    'Server/Virtualisatiehost — Lenovo P520, Xeon W, 32GB, geen OS/opslag, NVIDIA P1000',
    'Servers & werkstations', 399, slug='lenovo-p520---server.html')
make_product('SRV-04',
    'Dual-CPU Werkstation/Server — Lenovo P720, 2× Xeon Gold 6134 (16c/32t), 64GB, 1TB NVMe, P1000, Win11 Pro WS',
    'Servers & werkstations', 899, slug='lenovo-p720---dual-cpu---gold.html')

# ── 11. Monitorarmen ─────────────────────────────────────────────────────────
print("\n=== 11. Monitorarmen ===")
make_product('ARM-01',
    'Enkele monitorarm', 'Monitorarmen', 0,
    description='Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag.',
    placeholder='verhuur')
make_product('ARM-02',
    'Dubbele monitorarm High End — Humanscale M8, nieuw, tafelklem, max 2× 27", kabelgeleiding',
    'Monitorarmen', 199, slug='nieuw---humanscale-m8-monitorarm-voor-2-schermen.html')
make_product('ARM-03',
    'Dubbele monitorarm Flex — ACT8312, nieuw, gasveersysteem, VESA',
    'Monitorarmen', 149, slug='act8312-dubbele-monitorarm---nieuw.html')
make_product('ARM-04',
    'Dubbele monitorarm Basic — refurbished, tafelklem, max 2× 32", instelbaar gewicht, VESA',
    'Monitorarmen', 99, slug='dubbele-monitorarm-met-tafelklem.html')
make_product('ARM-05',
    'Vierledige monitorarm — Ewent Quad, nieuw, tafelklem, 4× max 32", VESA',
    'Monitorarmen', 99, slug='ewent-quad-monitor-voet---nieuw.html')

# ── 12. Docking stations ─────────────────────────────────────────────────────
print("\n=== 12. Docking stations ===")
make_product('DOCK-01',
    'Dell Thunderbolt Dock TB19 (2019)', 'Docking stations', 0,
    description='Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag.',
    placeholder='verhuur')
make_product('DOCK-02',
    'Dell Thunderbolt Dock TB22 (2022)', 'Docking stations', 0,
    description='Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag.',
    placeholder='verhuur')
make_product('DOCK-03',
    'Refurbished Dell USB-C Docking Station WD19 — 130W, USB-C, inclusief voeding',
    'Docking stations', 89, slug='dell-usb-c-docking-station-wd19-wd19s---130w.html')
make_product('DOCK-04',
    'HP Universele USB-C Multipoort Hub — nieuw, 7 poorten, DP/HDMI/Ethernet/USB',
    'Docking stations', 59, slug='hp-universal-usb-c-multiport-hub---nieuw-in-doos.html')

# ── 13. Conference sets ──────────────────────────────────────────────────────
print("\n=== 13. Conference sets ===")
make_product('CONF-01',
    'Refurbished Audio- en Videobar — HP Poly Studio P009, USB, camera+microfoon+luidspreker',
    'Conference sets', 249, slug='hp-poly-studio-p009.html')
make_product('CONF-02',
    'Refurbished Draadloze Headset — HP Poly Voyager Focus UC B825, ANC, 10u+, Bluetooth',
    'Conference sets', 89, slug='hp-poly-plantronics-voyager-focus-uc-b825-draadloze-headset.html')
make_product('CONF-03',
    'Refurbished IP-Telefoon USB — Polycom CX300 R2, Teams-gecertificeerd, speakerphone',
    'Conference sets', 79, slug='polycom-cx300-r2-ip-phone.html')
make_product('CONF-04',
    'IP-Telefoon 2-lijn SIP — Huawei eSpace 7810, nieuw, PoE, encryptie',
    'Conference sets', 89, slug='huawei-espace-7810-ip-phone-nieuw.html')

# ── 14. Meubelen ─────────────────────────────────────────────────────────────
print("\n=== 14. Meubelen ===")
make_product('FURN-01',
    'Refurbished Garderobe / Roomdivider 240×160×64 cm — afwasbaar, kapstokconstructie',
    'Kasten', 249, slug='garderobe-kast---room-divider---240b-x-160h-x-64d.html')
make_product('FURN-02',
    'Refurbished Hoge Roldeurkast MEWAF — metaal, roldeuren, verstelbare leggers',
    'Kasten', 219, slug='hoge-roldeurkast-mewaf.html')
make_product('FURN-03',
    'Refurbished Zitbank 2-persoons — groen, 128×80×98 cm, hoge zit',
    'Zitmeubelen', 199, slug='zitbank-groen.html')

# ── Klaar ─────────────────────────────────────────────────────────────────────
print("\n=== IMPORT VOLTOOID ===")
total = odoo.exe('product.template', 'search_count', [[]])
print(f"Totaal producten in Odoo: {total}")
