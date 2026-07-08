# -*- coding: utf-8 -*-
"""
Zone-posities voor het interactieve vloerplan (/vloerplan) — gebaseerd op
visuele inspectie van de gerasteriseerde originele grondplannen (LHOAS &
LHOAS architecten). GEEN pixel-exacte CAD-vectortrace: de kamerlabels waren
niet betrouwbaar te ontcijferen uit de PDF-tekstlaag, enkel via de
gerasteriseerde afbeelding zelf herkend. Posities zijn dus een goede
benadering, geen architecturale garantie — vooral de volgende zijn
LAGE ZEKERHEID en verdienen bevestiging met Werkplaats Walter:
  - Muziekzaal (verdiep +1): geen duidelijk aparte ruimte gevonden op het plan
  - Concertzaal (verdiep +2): geen "polyvalente zaal"-label gevonden
  - Coworking Zone 120m2/90m2 (verdiep +3): het plan toont hier een
    appartement-achtige indeling (Séjour+Cuisine, Chambre, Buanderie/
    Cellier), niet een open coworking-zone — zie projectmemory.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)

ATTACHMENTS = {
    'R+0': 6074, 'R+1': 6075, 'R+2': 6076, 'R+3': 6077, 'R+4': 6078,
}

# (naam, verdieping, x, y, w, h) — alle waarden % van het beeld
POSITIONS = [
    ('Atelier A', 'R+0', 25, 36, 17, 22),
    ('Atelier B', 'R+0', 25, 58, 17, 16),
    ('Atelier C', 'R+0', 25, 75, 17, 17),
    ('Atelier D', 'R+0', 42, 75, 13, 17),
    ('Atelier E', 'R+0', 70, 56, 18, 18),

    ('Atelier F', 'R+1', 25, 36, 17, 22),
    ('Atelier G', 'R+1', 25, 58, 17, 16),
    ('Vergaderruimte', 'R+1', 42, 75, 13, 17),
    ('Foyer', 'R+1', 70, 56, 13, 11),
    ('Muziekzaal', 'R+1', 54, 36, 15, 20),

    ('Opnamestudio (box-in-box)', 'R+2', 25, 36, 17, 22),
    ('Atelier I', 'R+2', 25, 58, 17, 16),
    ('Atelier J', 'R+2', 25, 75, 17, 17),
    ('Atelier K', 'R+2', 42, 75, 13, 17),
    ('Atelier L', 'R+2', 54, 36, 15, 20),
    ('Atelier M', 'R+2', 70, 56, 18, 18),
    ('Concertzaal / Polyvalente zaal', 'R+2', 42, 36, 12, 35),

    ('Atelier Ifinitive', 'R+3', 25, 36, 17, 22),
    ('Coworking Zone 120m2', 'R+3', 42, 56, 28, 20),
    ('Coworking Zone 90m2', 'R+3', 70, 56, 18, 18),

    ('Appartement 1', 'R+4', 25, 40, 30, 45),
    ('Appartement 2', 'R+4', 60, 40, 30, 45),
]

for name, floor_key, x, y, w, h in POSITIONS:
    ws = odoo.search_read('coworking.workspace', [('name', '=', name)], ['id'])
    if not ws:
        print(f"  ! Niet gevonden: {name}")
        continue
    odoo.write('coworking.workspace', [ws[0]['id']], {
        'floorplan_attachment_id': ATTACHMENTS[floor_key],
        'floorplan_x': x,
        'floorplan_y': y,
        'floorplan_w': w,
        'floorplan_h': h,
    })
    print(f"  ~ {name} -> {floor_key} ({x},{y},{w}x{h})")

print(f"\n{len(POSITIONS)} zones gepositioneerd op /vloerplan.")
