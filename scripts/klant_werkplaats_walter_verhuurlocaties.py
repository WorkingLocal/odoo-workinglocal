# -*- coding: utf-8 -*-
"""
Verhuurlocaties Werkplaats Walter — ateliers, opnamestudio, concertzaal, mobiele kits,
appartementen, coworking-zones.
Bron: klant_werkplaats_walter.py (klantendossier) — verdiepingsindeling en AV-materiaal.

Draait standaard tegen de VPS-instantie (odoo.workinglocal.be / db workinglocal) —
de dedicated on-premise server van Werkplaats Walter was offline op het moment dat dit
opgezet werd. Overschrijfbaar via ODOO_TARGET_URL / ODOO_TARGET_DB / ODOO_TARGET_USER
zodra die server terug bereikbaar is.

Prijzen zijn FICTIEF maar realistisch (Anderlecht-regio) — bedoeld om het systeem
bruikbaar te demonstreren. Bevestig de echte tarieven met Working Local voor je
effectief gaat factureren.

Idempotent: bestaande records worden bijgewerkt (upsert), niet overgeslagen —
zo kun je dit script opnieuw draaien na een prijscorrectie.
"""
import sys, os, io
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


def get_or_create_amenity(name, icon='bi-tools'):
    res = odoo.search_read('coworking.amenity', [('name', '=', name)], ['id'])
    if res:
        return res[0]['id']
    aid = odoo.create('coworking.amenity', {'name': name, 'icon': icon})
    print(f"  + Voorziening aangemaakt: {name}")
    return aid


def upsert_workspace(name, vals):
    """Maak aan of werk bij (prijzen/velden), altijd op naam."""
    existing = odoo.search_read('coworking.workspace', [('name', '=', name)], ['id'])
    vals = dict(vals, name=name)
    if existing:
        odoo.write('coworking.workspace', [existing[0]['id']], vals)
        print(f"  ~ Bijgewerkt: {name}")
        return existing[0]['id']
    wid = odoo.create('coworking.workspace', vals)
    print(f"  + Aangemaakt: {name} ({vals.get('workspace_type')})")
    return wid


# ── Voorzieningen (nieuw, specifiek voor deze ruimtes) ──────────────────────
amenity_recording   = get_or_create_amenity('Opnameapparatuur', 'bi-mic')
amenity_pa          = get_or_create_amenity('PA-geluidsinstallatie', 'bi-volume-up')
amenity_stage_light = get_or_create_amenity('Podiumverlichting', 'bi-lightbulb')

# Voorzieningen die al bestaan uit de generieke demo-data (workspace_data.xml)
def existing_amenity(name, icon):
    res = odoo.search_read('coworking.amenity', [('name', '=', name)], ['id'])
    return res[0]['id'] if res else get_or_create_amenity(name, icon)

amenity_video_conf  = existing_amenity('Videoconferentie', 'bi-camera-video')
amenity_interactive = existing_amenity('Interactief scherm', 'bi-display-fill')
amenity_whiteboard  = existing_amenity('Whiteboard', 'bi-easel')
amenity_wifi        = existing_amenity('WiFi', 'bi-wifi')
amenity_locker      = existing_amenity('Locker', 'bi-lock')

print("\n== Ateliers (fictieve huurprijs: 185 EUR/maand, Ifinitive groter: 320 EUR/maand) ==")
ATELIER_DEFAULTS = {
    'workspace_type': 'atelier',
    'capacity': 1,
    'monthly_rate': 185,
    'booking_granularity': 'day',
    'show_on_signage': False,
}
for letter, floor in [('A', 'Verdiep 0'), ('B', 'Verdiep 0'), ('C', 'Verdiep 0'),
                       ('D', 'Verdiep 0'), ('E', 'Verdiep 0'),
                       ('F', 'Verdiep +1'), ('G', 'Verdiep +1'), ('H', 'Verdiep +1'),
                       ('I', 'Verdiep +2'), ('J', 'Verdiep +2'), ('K', 'Verdiep +2'),
                       ('L', 'Verdiep +2'), ('M', 'Verdiep +2')]:
    upsert_workspace(f'Atelier {letter}', dict(ATELIER_DEFAULTS, floor=floor))
upsert_workspace('Atelier Ifinitive', dict(ATELIER_DEFAULTS, floor='Verdiep +3', monthly_rate=320, capacity=2))

print("\n== Opnamestudio ==")
upsert_workspace('Opnamestudio (box-in-box)', {
    'workspace_type': 'productiestudio',
    'floor': 'Verdiep +2',
    'capacity': 4,
    'hourly_rate': 35,
    'daily_rate': 220,
    'booking_granularity': 'slot',
    'show_on_signage': True,
    'description': '<p>Geïsoleerde opnamestudio (box-in-box constructie) met opnameapparatuur, '
                   'verhuurbaar per dagdeel of per dag.</p>',
    'amenity_ids': [(4, amenity_recording)],
})

print("\n== Concertzaal / Polyvalente zaal ==")
upsert_workspace('Concertzaal / Polyvalente zaal', {
    'workspace_type': 'concertzaal',
    'floor': 'Verdiep +2',
    'capacity': 150,
    'daily_rate': 450,
    'booking_granularity': 'day',
    'show_on_signage': True,
    'description': '<p>Polyvalente zaal, geschikt voor concerten, bedrijfspresentaties en events. '
                   'Verhuurbaar per dag.</p>',
    'amenity_ids': [(4, amenity_pa), (4, amenity_stage_light)],
})

print("\n== Mobiele kits ==")
upsert_workspace('Mobiele hybride meeting room', {
    'workspace_type': 'mobiele_teamsstudio',
    'floor': 'Mobiel — overal binnen coworking inzetbaar',
    'capacity': 1,
    'hourly_rate': 25,
    'booking_granularity': 'slot',
    'has_interactive_display': True,
    'show_on_signage': False,
    'description': '<p>Verplaatsbare hybride meetingset (scherm + videoconferentie) — te gebruiken '
                   'op elke gewenste plek binnen de coworking.</p>',
    'amenity_ids': [(4, amenity_video_conf), (4, amenity_interactive)],
})
upsert_workspace('Mobiele Podcast-installatie', {
    'workspace_type': 'presentatieset',
    'floor': 'Mobiel — overal binnen coworking inzetbaar',
    'capacity': 1,
    'hourly_rate': 30,
    'booking_granularity': 'slot',
    'show_on_signage': False,
    'description': '<p>Mobiele podcast-installatie met videostreaming.</p>',
})
upsert_workspace('Mobiel Whiteboard', {
    'workspace_type': 'presentatieset',
    'floor': 'Mobiel — overal binnen coworking inzetbaar',
    'capacity': 1,
    'hourly_rate': 10,
    'booking_granularity': 'slot',
    'show_on_signage': False,
    'description': '<p>Mobiel whiteboard voor brainstormsessies.</p>',
    'amenity_ids': [(4, amenity_whiteboard)],
})

print("\n== Appartementen (Verdiep +4, apart netwerk) ==")
upsert_workspace('Appartement 1', {
    'workspace_type': 'appartement',
    'floor': 'Verdiep +4',
    'capacity': 2,
    'monthly_rate': 750,
    'booking_granularity': 'day',
    'show_on_signage': False,
    'description': '<p>Volledig gescheiden netwerk van de coworking/ateliers.</p>',
    'amenity_ids': [(4, amenity_wifi)],
})
upsert_workspace('Appartement 2', {
    'workspace_type': 'appartement',
    'floor': 'Verdiep +4',
    'capacity': 2,
    'monthly_rate': 750,
    'booking_granularity': 'day',
    'show_on_signage': False,
    'description': '<p>Volledig gescheiden netwerk van de coworking/ateliers.</p>',
    'amenity_ids': [(4, amenity_wifi)],
})

print("\n== Coworking-zones (Verdiep +3) ==")
upsert_workspace('Coworking Zone 120m2', {
    'workspace_type': 'hot_desk',
    'floor': 'Verdiep +3',
    'capacity': 20,
    'contribution_enabled': True,
    'contribution_suggestions': '5,10,15',
    'show_on_signage': True,
    'description': '<p>Open coworking-zone, 120m², verdiep +3.</p>',
    'amenity_ids': [(4, amenity_wifi), (4, amenity_locker)],
})
upsert_workspace('Coworking Zone 90m2', {
    'workspace_type': 'hot_desk',
    'floor': 'Verdiep +3',
    'capacity': 14,
    'contribution_enabled': True,
    'contribution_suggestions': '5,10,15',
    'show_on_signage': True,
    'description': '<p>Open coworking-zone, 90m², verdiep +3.</p>',
    'amenity_ids': [(4, amenity_wifi), (4, amenity_locker)],
})

print("\nVerhuurlocaties Werkplaats Walter volledig geconfigureerd (fictieve maar realistische prijzen).")
