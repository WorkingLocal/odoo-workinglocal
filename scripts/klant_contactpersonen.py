# -*- coding: utf-8 -*-
"""
Contactpersonen toevoegen onder bestaande klantenfiches.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)

def contact(parent_id, name, email=None, phone=None, mobile=None, function=None):
    existing = odoo.search_read('res.partner',
        [('name', '=', name), ('parent_id', '=', parent_id)], ['id', 'name'])
    if existing:
        print("Al aanwezig: {} (id={})".format(name, existing[0]['id']))
        return existing[0]['id']
    vals = {
        'name':       name,
        'parent_id':  parent_id,
        'type':       'contact',
        'is_company': False,
    }
    if email:    vals['email']    = email
    if phone:    vals['phone']    = phone
    if mobile:   vals['mobile']   = mobile
    if function: vals['function'] = function
    cid = odoo.create('res.partner', vals)
    print("Aangemaakt: {} (id={}) onder parent {}".format(name, cid, parent_id))
    return cid

# ── Vakantiehuis Muziekbos (id=7) ───────────────────────────────────────────
# Hoofdrecord omzetten naar bedrijf zodat contactpersonen eronder passen
odoo.exe('res.partner', 'write', [[7], {
    'name':       'Vakantiehuis Muziekbos',
    'is_company': True,
}])
print("Muziekbos: hoofdrecord hernoemd naar 'Vakantiehuis Muziekbos' (bedrijf)")

contact(7, 'Paul Van Loveren',   phone='+32 473 70 25 46')
contact(7, 'Katrien Van Loveren', phone='+32 473 70 25 46')

# ── Steven Ide (id=9) ────────────────────────────────────────────────────────
# Hoofdrecord bijwerken naar Steven Ide alleen
odoo.exe('res.partner', 'write', [[9], {
    'name':  'Steven Ide',
    'email': 'Stivie02@hotmail.com',
}])
print("Steven Ide: hoofdrecord bijgewerkt")

contact(9, 'Ilse Tack', email='tackilse@hotmail.com')

# ── Werkplaats Walter (id=10) ────────────────────────────────────────────────
# Teun is de hoofdcontact (geen achternaam bekend uit documentatie)
contact(10, 'Teun', function='Hoofdcontact / Zaakvoerder', phone='02 356 29 32')

print("\nAlle contactpersonen aangemaakt.")
