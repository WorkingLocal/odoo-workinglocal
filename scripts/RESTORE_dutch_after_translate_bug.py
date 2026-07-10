# -*- coding: utf-8 -*-
"""
NOODHERSTEL: write() met context={'lang': 'en_US'} bleek de Nederlandse
brontekst zelf te overschrijven i.p.v. een aparte Engelse variant op te
slaan (translate=True velden op coworking.workspace/package waren blijkbaar
niet correct naar jsonb-opslag gemigreerd na de module-upgrade). Dit script
zet alles terug naar de originele Nederlandse waarden.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)


def restore(model, current_name, vals):
    res = odoo.search_read(model, [('name', '=', current_name)], ['id'])
    if not res:
        print(f"  ! Niet gevonden: {current_name}")
        return
    odoo.write(model, [res[0]['id']], vals)
    print(f"  ~ Hersteld: {current_name} -> {vals.get('name', current_name)}")


print("== Generieke werkplekken ==")
restore('coworking.workspace', 'Fixed Desk', {'name': 'Vaste Plek'})
restore('coworking.workspace', 'Meeting Room', {'name': 'Vergaderzaal'})  # generieke demo (id=3)
restore('coworking.workspace', 'Event Space', {'name': 'Evenementenruimte'})
restore('coworking.workspace', 'Hybrid Meeting Room', {'name': 'Hybride Meetingroom'})

print("\n== Werkplaats Walter — specifieke ruimtes ==")
restore('coworking.workspace', 'Recording Studio (box-in-box)', {
    'name': 'Opnamestudio (box-in-box)',
    'description': '<p>Geïsoleerde opnamestudio (box-in-box constructie) met opnameapparatuur, '
                   'verhuurbaar per dagdeel of per dag.</p>',
})
restore('coworking.workspace', 'Concert Hall / Multipurpose Hall', {
    'name': 'Concertzaal / Polyvalente zaal',
    'description': '<p>Polyvalente zaal, geschikt voor concerten, bedrijfspresentaties en events. '
                   'Verhuurbaar per dag.</p>',
})
restore('coworking.workspace', 'Music Hall', {
    'name': 'Muziekzaal',
    'description': '<p>Repetitie- en opnameruimte, enkel per volledige dag verhuurbaar.</p>',
})
restore('coworking.workspace', 'Meeting Room', {
    'name': 'Vergaderruimte',
    'description': '<p>Vergaderruimte, per dagdeel (VM/NM/evt. avond) verhuurbaar.</p>',
})
restore('coworking.workspace', 'Foyer', {
    'description': '<p>Foyer naast de bar, receptieruimte voor events — enkel als onderdeel van pakketten of apart te huren.</p>',
})
restore('coworking.workspace', 'Mobile Hybrid Meeting Room', {
    'name': 'Mobiele hybride meeting room',
    'description': '<p>Verplaatsbare hybride meetingset (scherm + videoconferentie) — te gebruiken '
                   'op elke gewenste plek binnen de coworking.</p>',
})
restore('coworking.workspace', 'Mobile Podcast Setup', {
    'name': 'Mobiele Podcast-installatie',
    'description': '<p>Mobiele podcast-installatie met videostreaming.</p>',
})
restore('coworking.workspace', 'Mobile Whiteboard', {
    'name': 'Mobiel Whiteboard',
    'description': '<p>Mobiel whiteboard voor brainstormsessies.</p>',
})
restore('coworking.workspace', 'Apartment 1', {
    'name': 'Appartement 1',
    'description': '<p>High-end volledig ingericht appartement, gericht op expats en bedrijven '
                   '(corporate housing / relocatie). Volledig gescheiden netwerk van de '
                   'coworking/ateliers.</p>',
})
restore('coworking.workspace', 'Apartment 2', {
    'name': 'Appartement 2',
    'description': '<p>High-end volledig ingericht appartement, gericht op expats en bedrijven '
                   '(corporate housing / relocatie). Volledig gescheiden netwerk van de '
                   'coworking/ateliers.</p>',
})
restore('coworking.workspace', 'Coworking Zone 120m2', {
    'description': '<p>Open coworking-zone, 120m², verdiep +3. Losse verhuur — definitieve '
                   'invulling van deze verdieping volgt nog.</p>',
})
restore('coworking.workspace', 'Coworking Zone 90m2', {
    'description': '<p>Open coworking-zone, 90m², verdiep +3. Losse verhuur — definitieve '
                   'invulling van deze verdieping volgt nog.</p>',
})

print("\n== Pakketten ==")
restore('coworking.package', 'Recording Day', {
    'name': 'TBS Opnamedag',
    'description': 'Muziekzaal + productiestudio + sound engineer voor de dag. '
                    'Enkel ma-vr. Eventuele extra\'s (instrumenten, catering) in overleg, '
                    'apart te verrekenen op de factuur.',
})
restore('coworking.package', 'Production Studio', {
    'name': 'TBS Productiestudio',
    'description': 'Productiestudio per dagdeel — klantvriendelijke naam voor een directe '
                    'dagdeel-boeking van de opnamestudio.',
})
restore('coworking.package', 'Rehearsal / Residency', {
    'name': 'Repetitie / Residentie',
    'description': 'Muziekzaal per dag voor repetities of een residentie.',
})
restore('coworking.package', 'Meeting Room', {
    'description': 'Vergaderruimte per dagdeel — klantvriendelijke naam voor een directe '
                    'dagdeel-boeking van de vergaderruimte.',
})
restore('coworking.package', 'Business Jam', {
    'description': 'Muziekzaal + foyer voor bedrijfsevents. Vergaderruimte en catering '
                    'optioneel bij te boeken, apart te verrekenen op de factuur.',
})
restore('coworking.package', 'Floor +3 Full (Event)', {
    'name': 'Verdiep +3 volledig (Event)',
    'description': 'Volledige verdieping +3 (120m² + 90m² samen) voor een event — '
                    'i.p.v. de twee zones apart per helft te huren. Losse verhuur, '
                    'definitieve invulling van deze verdieping volgt nog.',
})

print("\n== Mailsjabloon (corrupted testwaarde) ==")
res = odoo.search_read('mail.template', [('name', '=', 'Reservatie — aanvraag ontvangen')], ['id'])
if res:
    odoo.write('mail.template', [res[0]['id']], {
        'subject': 'Je aanvraag {{ object.name }} is ontvangen',
        'body_html': (
            '<div style="margin: 0; padding: 0;">\n'
            '                <p>Beste {{ object.partner_id.name }},</p>\n'
            '                <p>\n'
            '                    We hebben je aanvraag <strong>{{ object.name }}</strong> voor\n'
            '                    <strong t-out="object.package_id.name or object.workspace_id.name"/>\n'
            '                    ontvangen, van\n'
            '                    <t t-out="format_datetime(object.start_datetime, tz=object.partner_id.tz, dt_format=\'short\')"/>\n'
            '                    tot\n'
            '                    <t t-out="format_datetime(object.end_datetime, tz=object.partner_id.tz, dt_format=\'short\')"/>.\n'
            '                </p>\n'
            '                <p>\n'
            '                    Dit is nog geen bevestiging — we nemen je aanvraag zo snel mogelijk door\n'
            '                    en laten je weten zodra de plek definitief voor jou gereserveerd is.\n'
            '                </p>\n'
            '                <p>Je kan de status van je aanvraag altijd opvolgen via je\n'
            '                    <a t-attf-href="/mijn/reservaties/{{ object.id }}">klantenportaal</a>.\n'
            '                </p>\n'
            '                <p>Met vriendelijke groeten,<br/>Working Local</p>\n'
            '            </div>\n'
            '        '
        ),
    })
    print("  ~ Hersteld: Reservatie — aanvraag ontvangen")

print("\nHerstel voltooid.")
