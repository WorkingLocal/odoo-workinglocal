# -*- coding: utf-8 -*-
"""
Klantendossier: BV Werkplaats Walter - Anderlecht
Bron: Confluence PROJ page 12943390 + alle subpagina's
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)

# 1. Klant aanmaken (bedrijf)
bestaande = odoo.search_read('res.partner', [('name', 'like', 'Werkplaats Walter')], ['id', 'name'])

if bestaande:
    partner_id = bestaande[0]['id']
    print("Klant al aanwezig: id={} - {}".format(partner_id, bestaande[0]['name']))
else:
    partner_id = odoo.create('res.partner', {
        'name':          'Werkplaats Walter',
        'is_company':    True,
        'customer_rank': 1,
        'vat':           'BE0658981475',
        'phone':         '02 356 29 32',
        'street':        'Van Lintstraat 43-45',
        'zip':           '1070',
        'city':          'Anderlecht',
        'country_id':    21,
        'comment':       'Coworking/creatieve werkplaats Anderlecht. Grote Ubiquiti Unifi installatie (29+ AP\'s). Proximus Fiber 1000/500. Contact via Teun & Bart Michels (elektricien).',
    })
    print("Klant aangemaakt: id={}".format(partner_id))

def nota(titel, body):
    odoo.exe('res.partner', 'message_post', [[partner_id]], {
        'body': body, 'message_type': 'comment', 'subtype_xmlid': 'mail.mt_note',
    })
    print("Notitie: {}".format(titel))

# 2. Locatie
nota("Locatie & gebouw", """<h3>Locatie & Gebouw</h3>
<p><strong>Oud gebouw:</strong> Van Lintstraat 43-45, 1070 Anderlecht<br/>
<strong>Nieuw gebouw:</strong> Van Lintstraat 47, 1070 Anderlecht<br/>
(Beide gebouwen worden 1 geheel na verbouwing. Pand links naast het huidige ook verworven in 2024-2025.)</p>
<p><strong>Atypisch:</strong> Kleiner pand met gevel op straat, binnentuin erachter, dan de grotere gebouwen.<br/>
Oude wachtbuis onder binnentuin oud gebouw. Nieuwe ondergrondse kabelgoot onder binnentuin nieuw gebouw.</p>
<p><strong>Indeling verdiepen:</strong></p>
<ul>
  <li>Verdiep -1: Fietsenstalling, stockage, hoofdrack (Proximus modem 2)</li>
  <li>Verdiep 0: Ateliers A-E, inkomhal, handelspand vooraan (kinderdagverblijf)</li>
  <li>Verdiep +1: Bar, Foyer, keuken, ateliers F/G/H (meeting room), overdekte terrassen</li>
  <li>Verdiep +2: Ateliers I-M, opnamestudio (box-in-box), polyvalente zaal</li>
  <li>Verdiep +3: Atelier Ifinitive, foyer polyvalente ruimte, coworking 120m2 + 90m2, groot terras</li>
  <li>Verdiep +4: 2 appartementen (volledig gescheiden netwerk)</li>
</ul>
<p><strong>Fieldwire:</strong> <a href="https://app.fieldwire.com/projects/f5780a73-e677-4631-a377-749c38d991f1/plans">Plans bekijken</a><br/>
<strong>Ubiquiti Design:</strong> <a href="https://design.ui.com/projects/ef1e07e5-f86d-475c-8489-7d017a7b5a9e/plans/default">Wifi planning</a></p>""")

# 3. Telecom
nota("Telecom / ISP", """<h3>Telecom & ISP</h3>
<p><strong>Proximus Fiber (huidig - huisnr 43):</strong><br/>
Klantennummer: 619723409<br/>
Abonnement: Business Flex Fiber 1Gbit/500Mbps<br/>
Referentie: Bizz Internet Fiber 102342694928<br/>
Telefoonnummer (IP): 02 356 29 32<br/>
Modem: hangt achteraan gelijkvloers, wordt verplaatst naar hoofdrack.</p>
<p><strong>Geplande setup:</strong> 2 fiber-verbindingen aggregeren (Proximus 2.5Gbit als hoofd + EDPnet als failover + vast IP).<br/>
EDPnet: 1000/500 voor 85,95/maand incl. 4G failover & vast IP.</p>
<p><strong>Telenet B2B:</strong> Geen fiber beschikbaar op adres. Wel lichte abbo met 4G failover mogelijk.</p>
<p><strong>Boosters Proximus:</strong> 2 inbegrepen in oud pack, intussen betalend maar niet meer nodig. Derde staat ook betalend - aanpassen!</p>""")

# 4. Unifi netwerk
nota("Unifi Netwerkconfiguratie", """<h3>Unifi Netwerkconfiguratie</h3>
<p><strong>Hardware hoofdrack:</strong></p>
<ul>
  <li>UDM-PRO-SE (gateway/router/firewall)</li>
  <li>Unifi Switch Pro Max 24 port non-POE x2</li>
  <li>Unifi Switch Pro Max 24 port POE (667W)</li>
  <li>Aggregatieswitch</li>
</ul>
<p><strong>Secundair rack (per verdiep):</strong></p>
<ul>
  <li>Unifi Switch Pro Max 16 non-POE x2</li>
  <li>Unifi Switch Pro Max 16 POE</li>
</ul>
<p><strong>Access Points:</strong> 29 indoor + 1 outdoor Unifi U6+<br/>
Totaal LAN-verbindingen: 68 (2 per aansluitpunt)</p>

<p><strong>SSID's & Wachtwoorden:</strong></p>
<ul>
  <li>Werkplaats Walter Intern / <code>WerkWalt1070</code></li>
  <li>Werkplaats Walter Guest / <code>walterwerkt</code> (wachtwoord op toog)</li>
  <li>Werkplaats Walter Venue / <code>WeWa1070Venue</code></li>
  <li>Werkplaats Walter Tech / <code>WerkWalt1070iot</code> (verborgen na oplevering)</li>
</ul>

<p><strong>WAN:</strong> 2 fiber-verbindingen gebalanceerd (Proximus Fiber 2.5Gbit + failover)</p>""")

# 5. Hardware & leveranciers
nota("Hardware & Leveranciers", """<h3>Hardware & Leveranciers</h3>
<p><strong>Wimood (account Bart Michels):</strong><br/>
Klantnummer: 11556 | bart@hostinglocal.be | BE0898555045<br/>
Bauterstraat 11, 9870 Olsene<br/>
Volgende staffel bereikt 20/06/2025 - grotere korting actief.</p>
<p><strong>Patchkast.be / DSIT:</strong> Partneraccount aangevraagd en goedgekeurd.<br/>
<strong>Netwerkkabel.eu:</strong> Account Bart Michels: bart@hostinglocal.be / <code>6bK0cAJ3K#D0z^</code></p>
<p><strong>Patchkast bestelling betaald:</strong> EUR 844,73 via Multisafepay<br/>
IBAN: NL34 DEUT 7351 1150 95 | SWIFT: DEUTNL2A</p>
<p><strong>Kabelkleurcode:</strong><br/>
Blauw = interne bekabeling netwerkapparatuur<br/>
Rood = toevoer/uplink/modem</p>""")

# 6. ICT-infrastructuur
nota("ICT Infrastructuur", """<h3>ICT Infrastructuur - Hosting Local</h3>
<p><strong>Server:</strong> Lenovo P520, 16GB RAM, Xeon (359EUR) + HDD/SSD + NIC 10Gbe SFP+ ~ 650EUR totaal<br/>
Wordt in rack geplaatst. Bevat: Odoo CE, TrueNAS (backup/opslag), Xibo (schermbeheer), Tailscale.</p>
<p><strong>Printer (gedeeld over huurders):</strong><br/>
Laserprinter hoge volumes (Lexar ~69EUR + toners)<br/>
Kleuren A3 deskjet over netwerk beschikbaar</p>
<p><strong>Appartementen:</strong> Volledig gescheiden netwerk van Werkplaats Walter.</p>""")

# 7. AV
nota("AV & Media", """<h3>Audio-Visueel & Media</h3>
<p><strong>Aanbod:</strong></p>
<ul>
  <li>Mobiele podcast-installatie met videostreaming</li>
  <li>Mobiele hybride meeting room</li>
  <li>Mobiel whiteboard voor brainstorming</li>
  <li>OBS Studio training setup (Lenovo 14" i7 laptop)</li>
</ul>
<p><strong>Camera's:</strong> 3x Logitech Brio + hoofdcamera nog aan te kopen (Canon HF G70 ~950EUR gebruikt of Zoom Q8n-4K)</p>
<p><strong>Schermen aanwezig:</strong><br/>
1x Philips 75" touchscreen nieuw<br/>
1x 43" Dell (afgerekend)<br/>
1x 55" LG (niet afgerekend)<br/>
1x HP Poly Studio voor onder 55" LG</p>
<p><strong>Polyvalente zaal:</strong> 2x 75" schermen + 1 kleine monitor voor spreker + evt. 2x 55" voor grotere groepen</p>""")

# 8. Planning & uren
nota("Planning & Uren", """<h3>Planning & Uren (samenvatting)</h3>
<ul>
  <li>1e Plaatsbezoek: 08/2024 (2u + verplaatsing)</li>
  <li>2e Plaatsbezoek: 07/01/2025</li>
  <li>18/03/2025: Ophaling materiaal Zulte, configuratie fase 1 (4u)</li>
  <li>Installatie AP's & racks: 16u (30 x 65EUR = 1950EUR excl)</li>
  <li>06/05/2025: Bespreking bij Bart Michels Zulte (1u + 2u opvolging)</li>
  <li>20/06/2025: Werfbezoek met Bart - rack check, ophaling materiaal</li>
  <li>23/06/2025: Carte blanche ISP-onderzoek</li>
  <li>30/06/2025: Bezoek Business Centers Proximus & Telenet, offertes in mailbox</li>
  <li>30/01/2026: Verdere opvolging (vele verplaatsingen)</li>
  <li>25/01/2026: Verhuis bureaus & monitoren naar WP Walter (verhuiswagen + laadklep via Benny)</li>
</ul>
<p><strong>Contact elektricien:</strong> Bart Michels, Bauterstraat 11, 9870 Olsene - Tel: 09/388.84.27<br/>
<strong>Contact klant:</strong> Teun (hoofdcontact)</p>""")

# 9. Open to-do's
nota("Open to-do's", """<h3>Open To-do's</h3>
<ul>
  <li>Wifi in privaat verhuurde ateliers voorzien</li>
  <li>2 datapunten naar meeting room & hybride meeting room (atelier)</li>
  <li>ISP 2e verbinding activeren + failover configureren</li>
  <li>Modem Proximus verplaatsen naar hoofdrack (-1)</li>
  <li>AP voorzien in hoofdrack zelf (staat nu in kelder)</li>
  <li>Appartementen volledig gescheiden configureren</li>
  <li>Ikea Symfonisk of Sonos One: bureau, bar & foyer</li>
  <li>A3 printer + lamineerder gedeeld over huurders</li>
  <li>Signage in vitrine vooraan</li>
  <li>Binnentuin: buitenantenne + invulling</li>
  <li>Handelspand gelijkvloers: switch + AP + kinderdagverblijf</li>
  <li>Bekabeling concertruimte valideren</li>
  <li>Metalen deur hoofdrack nog te ontvangen & te vervangen</li>
  <li>Patchkabelkleurcorrectie (blauw intern / rood uplink)</li>
  <li>Greenscreen / foto- en videostudio evalueren</li>
  <li>Veilingen screenen voor interessant materiaal</li>
</ul>""")

print("\nKlantendossier Werkplaats Walter volledig aangemaakt.")
print("Link: https://odoo.workinglocal.be/web#id={}&model=res.partner&view_type=form".format(partner_id))
