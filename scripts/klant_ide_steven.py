# -*- coding: utf-8 -*-
"""
Klantendossier: Steven Ide & Ilse Tack - Waregem
Bron: Confluence PROJ pages 245858305 + 274759681
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)

# 1. Klant aanmaken
bestaande = odoo.search_read('res.partner', [('name', 'like', 'Ide')], ['id', 'name'])
bestaande = [x for x in bestaande if 'Steven' in x['name'] or 'Ide' in x['name']]

if bestaande:
    partner_id = bestaande[0]['id']
    print("Klant al aanwezig: id={} - {}".format(partner_id, bestaande[0]['name']))
else:
    partner_id = odoo.create('res.partner', {
        'name':          'Steven Ide & Ilse Tack',
        'is_company':    False,
        'customer_rank': 1,
        'email':         'Stivie02@hotmail.com',
        'street':        'Kievitstraat 55',
        'zip':           '8970',
        'city':          'Waregem',
        'country_id':    21,
        'comment':       'Particuliere verbouwing: uitbreiding woning met bijgebouwen. Ubiquiti Unifi wifi-installatie. Parental Control is prioriteit.',
    })
    print("Klant aangemaakt: id={}".format(partner_id))

def nota(titel, body):
    odoo.exe('res.partner', 'message_post', [[partner_id]], {
        'body': body, 'message_type': 'comment', 'subtype_xmlid': 'mail.mt_note',
    })
    print("Notitie: {}".format(titel))

# 2. Projectomschrijving
nota("Project", """<h3>Project - Waregem</h3>
<p><strong>Type:</strong> Particuliere verbouwing - uitbreiding woning met bijgebouwen (poolhouse, schuur, ...)</p>
<p><strong>Scope:</strong> Volledige nieuwe Ubiquiti Unifi wifi-installatie die alles omvat.<br/>
Parental Control is <strong>heel belangrijk</strong> voor hen.</p>
<p><strong>Fieldwire:</strong> <a href="https://app.fieldwire.com/projects/b6dc4c53-e42e-4b16-a9ce-f1088f35e9ec/plans">Plans bekijken</a></p>
<p><strong>Betaling:</strong> Contant</p>
<p><strong>Contactpersoon bestelling:</strong> Michels Electro (Bart) + Steven Ide<br/>
Doormailen vanuit thomas@hostinglocal.be</p>""")

# 3. Unifi netwerkconfiguratie
nota("Unifi Netwerkconfiguratie", """<h3>Unifi Netwerkconfiguratie</h3>
<p><strong>Controller naam:</strong> Ide Cloud Gateway Ultra</p>
<p><strong>MAC WAN gateway:</strong> 6c:63:f8:49:06:40<br/>
<strong>MAC WAN (bridge-verbinding Telenet):</strong> 6C:63:F8:49:06:44</p>

<p><strong>VLAN / Subnetten:</strong></p>
<ul>
  <li>Ide LAN: 192.168.55.0/24 (255.255.255.0)</li>
  <li>Ide IoT: 192.168.56.0/24</li>
  <li>Ide Gasten: 192.168.57.0/24 (geisoleerd)</li>
</ul>

<p><strong>Wifi SSID's:</strong></p>
<ul>
  <li>Ide Wifi / <code>Idewifi55</code></li>
  <li>Ide Wifi Guest / Open</li>
  <li>Ide Wifi IoT / <code>-Idewifiiot</code></li>
</ul>

<p><strong>Wachtwoorden per profiel:</strong></p>
<ul>
  <li>IDE - Kids: <code>141011300614</code></li>
  <li>IDE - Ouders: <code>$5Rzjn$g8$</code></li>
  <li>IDE - Gasten: Open</li>
</ul>

<p><strong>Let op:</strong> Wifi-settings zijn ingesteld op AP-niveau, niet op controller-niveau.</p>""")

# 4. Telenet
nota("Telenet", """<h3>Telenet</h3>
<p><strong>Abonnement:</strong> Whoppa<br/>
<strong>Accountnummer:</strong> 112067286</p>
<p><strong>Login:</strong> tackilse@hotmail.com / <code>We099d7m@</code></p>
<p><strong>Oud wifi (verwijderd):</strong> SSID 'Living' - HP Aruba AP weggenomen<br/>
<strong>Oud wachtwoord:</strong> 0938858899</p>
<p><strong>10/03/2026:</strong> Telenet modem aangepast naar SSID Telenet_oud / telenetoud<br/>
<strong>10/03/2026:</strong> Nieuwe modem gebridged naar Unifi Gateway</p>
<p><strong>Telenet modem:</strong> CH7465LG-TN<br/>
MAC LAN: ac:22:05:ad:50:55<br/>
MAC WAN: AC:22:05:9E:43:F3</p>
<p><em>Niet werkend:</em> Telenet User aa099d7m@ / 7b0i67$o</p>""")

# 5. Teletask
nota("Teletask domotica", """<h3>Teletask Domotica</h3>
<p><strong>IP Centrale:</strong> 192.168.1.200<br/>
<strong>Poorten open te zetten:</strong> 55955 tot en met 55959</p>""")

# 6. Hardware voorstel
nota("Hardware voorstel", """<h3>Hardware Voorstel - Ubiquiti Unifi</h3>
<ul>
  <li>Cloud Gateway Ultra</li>
  <li>Switch POE 52W 8 port</li>
  <li>Wifi 7 Lite</li>
  <li>Wifi 6 of 7 Mesh (aantal nog te bepalen op basis van plaatsing)</li>
</ul>
<p><strong>Vragen nog open:</strong></p>
<ul>
  <li>Inverters zonnepanelen: internet via kabel of wifi? (Wifi voorzien)</li>
  <li>Bekabelde aansluitingen nodig in de schuur?</li>
  <li>Huidige Telenet abonnement? Nieuwe modem vragen? Bridgeable?</li>
  <li>Bestaan er digitale grondplannen?</li>
</ul>""")

# 7. Openstaande to-do's
nota("Open to-do's", """<h3>Open To-do's</h3>
<ul>
  <li>Modem Telenet volledig bridgen (nu DHCP-server naar gateway 192.168.5.226 > 192.168.0.1, range 192.168.0.x/24 wegens vaste adressen)</li>
  <li>IoT-band naar 20MHz zetten (blijft nu op 40MHz - Aiphone kan niet verbinden)</li>
  <li>Parental Control instellen</li>
  <li>Wifi blackout aanleren via app (anders in vakantie dan normaal)</li>
  <li>Poolhouse dekking verbeteren: op randje nu, zeker op 5GHz</li>
  <li>HP Multifunctional op wifi zetten</li>
</ul>""")

# 8. Tijdslijn
nota("Tijdslijn", """<h3>Tijdslijn</h3>
<ul>
  <li><strong>22/11/2025:</strong> Pakket van Wimood week vast in UPS-postpuntje, afgehaald door Jeroen.</li>
  <li><strong>10/03/2026:</strong> Telenet modem gebridged, nieuwe Unifi-setup actief.</li>
</ul>""")

print("\nKlantendossier Steven Ide volledig aangemaakt.")
print("Link: https://odoo.workinglocal.be/web#id={}&model=res.partner&view_type=form".format(partner_id))
