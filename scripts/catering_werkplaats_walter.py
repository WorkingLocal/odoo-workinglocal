# -*- coding: utf-8 -*-
"""
Catering als dienst-product — nodig voor de "Business Jam"-pakketoptie van
Werkplaats Walter (optionele add-on, apart te factureren bovenop het pakket).

Prijs is FICTIEF maar realistisch (Belgische cateringmarkt, walking dinner/
receptie-niveau) — bevestig met Working Local/Werkplaats Walter voor je
effectief gaat factureren.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)

diensten_cat = odoo.get_or_create_cat('Diensten')
catering_cat = odoo.get_or_create_cat('Catering', parent_id=diensten_cat)

tmpl_id = odoo.upsert_product('SRV-CATER-01', {
    'name': 'Catering — receptie/walking dinner (per persoon)',
    'categ_id': catering_cat,
    'list_price': 18.0,
    'type': 'service',
    'description_sale': 'Broodjes, hapjes en drank voor events (Business Jam en gelijkaardige '
                         'pakketten) — per persoon, excl. btw. Aantal personen manueel invullen '
                         'op de factuur/offerte.',
})
print(f"\nCatering-product klaar: template id={tmpl_id}")
print("Gebruik: voeg als aparte factuurlijn toe bovenop een Business Jam-reservatie (qty = aantal gasten).")
