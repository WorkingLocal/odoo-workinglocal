# -*- coding: utf-8 -*-
"""
Upload originele grondplannen (LHOAS & LHOAS architecten, PDF, schaal 1/50) als
bijlage bij de klantfiche "Werkplaats Walter" in Odoo.

Bron: OneDrive "1 HOSTING LOCAL/Klanten/Werkplaats Walter Voorbeeld-20260321/
Werkplaats Walter Voorbeeld/Laatste Schema_s Werkplaats Walter"
"""
import sys, os, io, base64, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(
    url=os.environ.get('ODOO_TARGET_URL', 'https://odoo.workinglocal.be'),
    db=os.environ.get('ODOO_TARGET_DB', 'workinglocal'),
    username=os.environ.get('ODOO_TARGET_USER', 'info@workinglocal.be'),
    password=pw,
)

SOURCE_DIR = (
    r"C:\Users\Lenovo\OneDrive\1 HOSTING LOCAL\Klanten"
    r"\Werkplaats Walter Voorbeeld-20260321\Werkplaats Walter Voorbeeld"
    r"\Laatste Schema_s Werkplaats Walter"
)

partner = odoo.search_read('res.partner', [('name', 'like', 'Werkplaats Walter')], ['id', 'name'], )
partner = [p for p in partner if p['name'] == 'Werkplaats Walter'] or partner
partner_id = partner[0]['id']
print(f"Klant: {partner[0]}")

files = sorted(glob.glob(os.path.join(SOURCE_DIR, '*')))
uploaded = 0
for path in files:
    fname = os.path.basename(path)
    if fname.lower().endswith('.drawio'):
        mimetype = 'application/xml'
    elif fname.lower().endswith('.pdf'):
        mimetype = 'application/pdf'
    else:
        continue

    existing = odoo.search_read('ir.attachment', [
        ('res_model', '=', 'res.partner'),
        ('res_id', '=', partner_id),
        ('name', '=', fname),
    ], ['id'])
    if existing:
        print(f"  ~ Bestaat al: {fname}")
        continue

    with open(path, 'rb') as f:
        data = f.read()

    odoo.create('ir.attachment', {
        'name': fname,
        'res_model': 'res.partner',
        'res_id': partner_id,
        'type': 'binary',
        'datas': base64.b64encode(data).decode('utf-8'),
        'mimetype': mimetype,
        'description': 'Origineel grondplan — LHOAS & LHOAS architecten, schaal 1/50 (2024-03-07)',
    })
    print(f"  + Geüpload: {fname} ({len(data)//1024} KB)")
    uploaded += 1

print(f"\n{uploaded} bestand(en) geüpload naar de klantfiche 'Werkplaats Walter' (partner id={partner_id}).")
print(f"Bekijken: https://odoo.workinglocal.be/odoo/contacts/{partner_id}")
