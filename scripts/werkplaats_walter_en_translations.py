# -*- coding: utf-8 -*-
"""
Engelse vertalingen voor de dynamisch aangemaakte werkplek- en pakketrecords
(die niet via module-data/.po-bestanden lopen, dus apart via de lang-context
weggeschreven moeten worden). Ateliers hebben geen omschrijving en de naam
"Atelier X" is een internationaal begrepen term — bewust niet vertaald.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)


def set_en(model, name_nl, vals_en):
    res = odoo.search_read(model, [('name', '=', name_nl)], ['id'])
    if not res:
        print(f"  ! Niet gevonden: {name_nl}")
        return
    odoo.exe(model, 'write', [[res[0]['id']], vals_en], {'context': {'lang': 'en_US'}})
    print(f"  ~ EN: {name_nl} -> {vals_en.get('name', name_nl)}")


print("== Generieke werkplekken (gedeeld, alle Working Local-klanten) ==")
set_en('coworking.workspace', 'Vaste Plek', {'name': 'Fixed Desk'})
set_en('coworking.workspace', 'Vergaderzaal', {'name': 'Meeting Room'})
set_en('coworking.workspace', 'Evenementenruimte', {'name': 'Event Space'})
set_en('coworking.workspace', 'Hybride Meetingroom', {'name': 'Hybrid Meeting Room'})

print("\n== Werkplaats Walter — specifieke ruimtes ==")
set_en('coworking.workspace', 'Opnamestudio (box-in-box)', {
    'name': 'Recording Studio (box-in-box)',
    'description': '<p>Soundproofed recording studio (box-in-box construction) with recording '
                   'equipment, rentable per half-day or per day.</p>',
})
set_en('coworking.workspace', 'Concertzaal / Polyvalente zaal', {
    'name': 'Concert Hall / Multipurpose Hall',
    'description': '<p>Multipurpose hall, suitable for concerts, corporate presentations and '
                   'events. Rentable per day.</p>',
})
set_en('coworking.workspace', 'Muziekzaal', {
    'name': 'Music Hall',
    'description': '<p>Rehearsal and recording space, rentable per full day only.</p>',
})
set_en('coworking.workspace', 'Vergaderruimte', {
    'name': 'Meeting Room',
    'description': '<p>Meeting room, rentable per half-day (morning/afternoon/evening).</p>',
})
set_en('coworking.workspace', 'Foyer', {
    'description': '<p>Foyer next to the bar, reception space for events — either as part of '
                   'packages or rentable separately.</p>',
})
set_en('coworking.workspace', 'Mobiele hybride meeting room', {
    'name': 'Mobile Hybrid Meeting Room',
    'description': '<p>Portable hybrid meeting set (screen + video conferencing) — usable '
                   'anywhere within the coworking space.</p>',
})
set_en('coworking.workspace', 'Mobiele Podcast-installatie', {
    'name': 'Mobile Podcast Setup',
    'description': '<p>Mobile podcast setup with video streaming.</p>',
})
set_en('coworking.workspace', 'Mobiel Whiteboard', {
    'name': 'Mobile Whiteboard',
    'description': '<p>Mobile whiteboard for brainstorming sessions.</p>',
})
set_en('coworking.workspace', 'Appartement 1', {
    'name': 'Apartment 1',
    'description': '<p>High-end fully furnished apartment, aimed at expats and companies '
                   '(corporate housing / relocation). Fully separated network from the '
                   'coworking space/studios.</p>',
})
set_en('coworking.workspace', 'Appartement 2', {
    'name': 'Apartment 2',
    'description': '<p>High-end fully furnished apartment, aimed at expats and companies '
                   '(corporate housing / relocation). Fully separated network from the '
                   'coworking space/studios.</p>',
})
set_en('coworking.workspace', 'Coworking Zone 120m2', {
    'description': '<p>Open coworking zone, 120m², floor +3. Loose rental — final layout '
                   'of this floor still to be determined.</p>',
})
set_en('coworking.workspace', 'Coworking Zone 90m2', {
    'description': '<p>Open coworking zone, 90m², floor +3. Loose rental — final layout '
                   'of this floor still to be determined.</p>',
})

print("\n== Pakketten ==")
set_en('coworking.package', 'TBS Opnamedag', {
    'name': 'Recording Day',
    'description': 'Music hall + production studio + sound engineer for the day. '
                    'Mon-Fri only. Extras (instruments, catering) on request, '
                    'billed separately on the invoice.',
})
set_en('coworking.package', 'TBS Productiestudio', {
    'name': 'Production Studio',
    'description': 'Production studio per half-day — customer-friendly name for a direct '
                    'half-day booking of the recording studio.',
})
set_en('coworking.package', 'Repetitie / Residentie', {
    'name': 'Rehearsal / Residency',
    'description': 'Music hall per day for rehearsals or a residency.',
})
set_en('coworking.package', 'Meeting Room', {
    'description': 'Meeting room per half-day — customer-friendly name for a direct '
                    'half-day booking of the meeting room.',
})
set_en('coworking.package', 'Business Jam', {
    'description': 'Music hall + foyer for corporate events. Meeting room and catering '
                    'optional add-ons, billed separately on the invoice.',
})
set_en('coworking.package', 'Verdiep +3 volledig (Event)', {
    'name': 'Floor +3 Full (Event)',
    'description': 'Entire floor +3 (120m² + 90m² combined) for an event — instead of '
                    'renting the two zones separately by half. Loose rental, final layout '
                    'of this floor still to be determined.',
})

print("\nEngelse vertalingen weggeschreven.")
