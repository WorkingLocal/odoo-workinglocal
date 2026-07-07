# -*- coding: utf-8 -*-
"""
Verhuurlocaties Werkplaats Walter — ateliers, opnamestudio, concertzaal, mobiele kits.
Draait tegen de klant-instantie (niet odoo.workinglocal.be).
Bron: klant_werkplaats_walter.py (klantendossier) — verdiepingsindeling en AV-materiaal.

Prijzen zijn PLACEHOLDERS (# TODO) — er bestaat nog geen prijslijst voor deze
ruimtes/materiaal, in tegenstelling tot de refurbished-hardwarecatalogus.
Bevestig met Working Local voor er echt gefactureerd wordt.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(
    url='https://wpwalter-odoo.workinglocal.be',
    db='wpwalter',
    username='admin',
    password=pw,
)


def get_or_create_amenity(name, icon='bi-tools'):
    res = odoo.search_read('coworking.amenity', [('name', '=', name)], ['id'])
    if res:
        return res[0]['id']
    aid = odoo.create('coworking.amenity', {'name': name, 'icon': icon})
    print(f"  + Voorziening aangemaakt: {name}")
    return aid


def get_or_create_workspace(name, vals):
    existing = odoo.search_read('coworking.workspace', [('name', '=', name)], ['id'])
    if existing:
        print(f"  ~ Bestaat al: {name}")
        return existing[0]['id']
    vals = dict(vals, name=name)
    wid = odoo.create('coworking.workspace', vals)
    print(f"  + Aangemaakt: {name} ({vals.get('workspace_type')})")
    return wid


# ── Voorzieningen (nieuw, specifiek voor deze ruimtes) ──────────────────────
amenity_recording   = get_or_create_amenity('Opnameapparatuur', 'bi-mic')
amenity_pa          = get_or_create_amenity('PA-geluidsinstallatie', 'bi-volume-up')
amenity_stage_light = get_or_create_amenity('Podiumverlichting', 'bi-lightbulb')

# Voorzieningen die al bestaan uit de generieke demo-data (workspace_data.xml)
amenity_video_conf = odoo.search_read('coworking.amenity', [('name', '=', 'Videoconferentie')], ['id'])
amenity_video_conf = amenity_video_conf[0]['id'] if amenity_video_conf else get_or_create_amenity('Videoconferentie', 'bi-camera-video')
amenity_interactive = odoo.search_read('coworking.amenity', [('name', '=', 'Interactief scherm')], ['id'])
amenity_interactive = amenity_interactive[0]['id'] if amenity_interactive else get_or_create_amenity('Interactief scherm', 'bi-display-fill')
amenity_whiteboard = odoo.search_read('coworking.amenity', [('name', '=', 'Whiteboard')], ['id'])
amenity_whiteboard = amenity_whiteboard[0]['id'] if amenity_whiteboard else get_or_create_amenity('Whiteboard', 'bi-easel')

print("\n== Ateliers ==")
ATELIER_DEFAULTS = {
    'workspace_type': 'atelier',
    'capacity': 1,
    'monthly_rate': 0,  # TODO: prijs bevestigen met Working Local (per atelier kan verschillen qua grootte)
    'booking_granularity': 'day',
    'show_on_signage': False,
}
for letter, floor in [('A', 'Verdiep 0'), ('B', 'Verdiep 0'), ('C', 'Verdiep 0'),
                       ('D', 'Verdiep 0'), ('E', 'Verdiep 0'),
                       ('F', 'Verdiep +1'), ('G', 'Verdiep +1'), ('H', 'Verdiep +1'),
                       ('I', 'Verdiep +2'), ('J', 'Verdiep +2'), ('K', 'Verdiep +2'),
                       ('L', 'Verdiep +2'), ('M', 'Verdiep +2')]:
    get_or_create_workspace(f'Atelier {letter}', dict(ATELIER_DEFAULTS, floor=floor))
get_or_create_workspace('Atelier Ifinitive', dict(ATELIER_DEFAULTS, floor='Verdiep +3'))

print("\n== Opnamestudio ==")
get_or_create_workspace('Opnamestudio (box-in-box)', {
    'workspace_type': 'productiestudio',
    'floor': 'Verdiep +2',
    'capacity': 4,
    'hourly_rate': 0,  # TODO: prijs bevestigen
    'daily_rate': 0,   # TODO: prijs bevestigen
    'booking_granularity': 'slot',
    'show_on_signage': True,
    'description': '<p>Geïsoleerde opnamestudio (box-in-box constructie) met opnameapparatuur, '
                   'verhuurbaar per dagdeel of per dag.</p>',
    'amenity_ids': [(4, amenity_recording)],
})

print("\n== Concertzaal / Polyvalente zaal ==")
get_or_create_workspace('Concertzaal / Polyvalente zaal', {
    'workspace_type': 'concertzaal',
    'floor': 'Verdiep +2',
    'capacity': 0,  # TODO: capaciteit bevestigen met Working Local
    'daily_rate': 0,  # TODO: prijs bevestigen (dagtarief bedrijfsevent)
    'booking_granularity': 'day',
    'show_on_signage': True,
    'description': '<p>Polyvalente zaal, geschikt voor concerten, bedrijfspresentaties en events. '
                   'Verhuurbaar per dag.</p>',
    'amenity_ids': [(4, amenity_pa), (4, amenity_stage_light)],
})

print("\n== Mobiele kits ==")
get_or_create_workspace('Mobiele hybride meeting room', {
    'workspace_type': 'mobiele_teamsstudio',
    'floor': 'Mobiel — overal binnen coworking inzetbaar',
    'capacity': 1,
    'hourly_rate': 0,  # TODO: prijs bevestigen
    'booking_granularity': 'slot',
    'has_interactive_display': True,
    'show_on_signage': False,
    'description': '<p>Verplaatsbare hybride meetingset (scherm + videoconferentie) — te gebruiken '
                   'op elke gewenste plek binnen de coworking.</p>',
    'amenity_ids': [(4, amenity_video_conf), (4, amenity_interactive)],
})
get_or_create_workspace('Mobiele Podcast-installatie', {
    'workspace_type': 'presentatieset',
    'floor': 'Mobiel — overal binnen coworking inzetbaar',
    'capacity': 1,
    'hourly_rate': 0,  # TODO: prijs bevestigen
    'booking_granularity': 'slot',
    'show_on_signage': False,
    'description': '<p>Mobiele podcast-installatie met videostreaming.</p>',
})
get_or_create_workspace('Mobiel Whiteboard', {
    'workspace_type': 'presentatieset',
    'floor': 'Mobiel — overal binnen coworking inzetbaar',
    'capacity': 1,
    'hourly_rate': 0,  # TODO: prijs bevestigen
    'booking_granularity': 'slot',
    'show_on_signage': False,
    'description': '<p>Mobiel whiteboard voor brainstormsessies.</p>',
    'amenity_ids': [(4, amenity_whiteboard)],
})

print("\nVerhuurlocaties Werkplaats Walter geconfigureerd.")
print("Prijzen staan op 0 waar nog TODO — bevestig deze met Working Local voor je gaat factureren.")
