# -*- coding: utf-8 -*-
"""
Klantendossier: Paul & Katrien Van Loveren - Vakantiehuis Muziekbos
Aanmaakt: res.partner + interne notities in Odoo CRM

Gebruik:
    python scripts/klant_muziekbos.py WACHTWOORD
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))

from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)

# 1. Klant aanmaken

bestaande = odoo.search_read('res.partner',
    [('name', 'like', 'Van Loveren')],
    ['id', 'name'])

if bestaande:
    partner_id = bestaande[0]['id']
    print("Klant al aanwezig: id={} - {}".format(partner_id, bestaande[0]['name']))
else:
    partner_id = odoo.create('res.partner', {
        'name':         'Paul & Katrien Van Loveren (Vakantiehuis Muziekbos)',
        'is_company':   False,
        'customer_rank': 1,
        'phone':        '+32 473 70 25 46',
        'street':       'Wilgenstraat 56',
        'zip':          '9600',
        'city':         'Ronse',
        'country_id':   21,
        'website':      'https://vakantiehuis-muziekbos.be/contact/',
        'comment':      'Vakantiehuis Muziekbos - TP-Link Deco wifi-installatie + uitbreiding',
    })
    print("Klant aangemaakt: id={}".format(partner_id))

# Helper: interne notitie posten

def nota(titel, body):
    odoo.exe('res.partner', 'message_post', [[partner_id]], {
        'body':          body,
        'message_type':  'comment',
        'subtype_xmlid': 'mail.mt_note',
    })
    print("Notitie gepost: {}".format(titel))

# 2. Installatiedetails (23/01/2026)

nota("Installatie 23/01/2026", """<h3>Installatie 23/01/2026 — 10h tot 14h</h3>
<p><strong>Uitgevoerd:</strong> TP-Link Deco X60 wifi-installatie (3 stuks)</p>
<ul>
  <li>Telenet modem wifi uitgeschakeld</li>
  <li>Telenet modem aangesloten op D-Link Switch</li>
  <li>Onverklaarbare POE adapter aanwezig op locatie</li>
  <li>Volledige herinstallatie via Android Deco App na factory reset van alle 3 units</li>
</ul>
<p><strong>Deco-configuratie:</strong></p>
<ul>
  <li>SSID: <code>Vakantiewoning</code></li>
  <li>Wachtwoord: <code>Wilgenstraat56</code></li>
  <li>Master AP: technische ruimte</li>
  <li>AP 2: gelijkvloers — zithoek</li>
  <li>AP 3: gelijkvloers — keuken</li>
</ul>
<p><strong>Deco Portal-toegang:</strong><br/>
Admin: <code>thomas@hostinglocal.be</code> / <code>Wilgenstr@at56</code></p>
<p><strong>Telenet:</strong> Provider Telenet — abonnement 1000/50 (snelheden gehaald)<br/>
Klantnummer: 1057469142 | Accountnummer: 112764065<br/>
Abonnement staat op naam: <strong>Maarten Lauwers</strong>, Sint-Jozefsplein 2, 8000 Brugge</p>""")

# 3. Openstaande punten

nota("Openstaande punten", """<h3>Openstaande punten</h3>
<p><strong>Probleem 1 — Onvoldoende dekking:</strong><br/>
Grootste kamer bovenaan + verste kamers in de kelder: onvoldoende wifi, telefoon valt terug op 5G.<br/>
Oplossing: 2 extra TP-Link Deco X60 antennes nodig.</p>
<p><strong>Probleem 2 — Datapunten op tv-hoogte:</strong><br/>
Datapunten zitten op ooghoogte (initieel voorzien voor tv).<br/>
Kennis van klant bouwt wandrekjes → levering voorzien midden maart 2026.</p>
<p><strong>Actie Telenet:</strong><br/>
Telenet Center Ronse bezoeken: <strong>Derco Systems</strong>, Peperstraat 37, 9600 Ronse — 055/21.07.75 — ronse@derco.be<br/>
Nagaan wat er aan <strong>Maarten Lauwers</strong> hangt vs. wat bij het vakantiehuisabonnement hoort.<br/>
Alles van Vakantiewoning Muziekbos groeperen onder eigen dossier.<br/>
Mogelijkheid tot bridging van de modem bekijken.</p>
<p><strong>Toekomstig voorstel:</strong><br/>
Unifi in-wall AP overwegen: huidige Deco-materiaal heeft nog tweedehandswaarde,
kleine Unifi inwall AP lost datapunten-probleem op.</p>""")

# 4. Opvolgingsgesprek 26/02/2026

nota("Opvolgingsgesprek 26/02/2026", """<h3>Opvolgingsgesprek 26/02/2026</h3>
<p>Telefoontje voor update: wandrekjes nog niet geleverd.<br/>
Afspraak: klant opnieuw contacteren <strong>midden maart 2026</strong>.<br/>
Reminder in agenda gezet.</p>""")

# 5. Telenet Center info

nota("Telenet Center Ronse", """<h3>Telenet Center Ronse — Derco Systems</h3>
<ul>
  <li>Adres: Peperstraat 37, 9600 Ronse</li>
  <li>Tel: 055/21.07.75</li>
  <li>E-mail: ronse@derco.be</li>
  <li>Openingsuren: ma-za, doorgaans tot 18u</li>
</ul>
<p><strong>Te doen bij bezoek:</strong><br/>
Nagaan wat er precies op naam van Maarten Lauwers staat en of de link verbroken kan worden.<br/>
Modem eventueel laten bridgen voor volledige controle over het netwerk.</p>
<p><strong>Telenet-referenties klant:</strong><br/>
Klantnummer: 1057469142<br/>
Doccle-token: 92424<br/>
Easy Switch ID: 740188913</p>""")

print("")
print("Klantendossier Muziekbos volledig aangemaakt in Odoo.")
print("Link: https://odoo.workinglocal.be/web#id={}&model=res.partner&view_type=form".format(partner_id))
