# -*- coding: utf-8 -*-
"""
Handleidingen toevoegen als vaste taak in de klantenportaalprojecten.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)

def handleiding(naam, project_id, html):
    tid = odoo.create('project.task', {
        'name':        naam,
        'project_id':  project_id,
        'description': html,
        'sequence':    0,  # bovenaan in lijst
    })
    print('Handleiding aangemaakt: {} (id={})'.format(naam, tid))

# ══════════════════════════════════════════════════════════════════════════════
# VAKANTIEHUIS MUZIEKBOS — TP-Link Deco X50 (5 stuks)
# Project id=1
# ══════════════════════════════════════════════════════════════════════════════
handleiding('Handleiding: TP-Link Deco wifi', 1, """
<h2>Uw wifi-installatie — Vakantiehuis Muziekbos</h2>
<p>Uw vakantiewoning is uitgerust met <strong>5 TP-Link Deco X50 mesh-antennes</strong>.
Deze werken samen als één netwerk dat de volledige woning en bijgebouwen dekt.
U hoeft niets handmatig te schakelen: uw toestellen verbinden automatisch met de sterkste antenne.</p>

<hr/>

<h3>Verbinden met het wifi</h3>
<table>
  <tr><td><strong>Netwerknaam (SSID)</strong></td><td>Vakantiewoning</td></tr>
  <tr><td><strong>Wachtwoord</strong></td><td>Wilgenstraat56</td></tr>
</table>
<p>Dit geldt voor zowel uw gsm, laptop als smart-tv. Er is geen apart netwerk voor 2,4 GHz of 5 GHz —
het systeem kiest automatisch de beste verbinding.</p>

<hr/>

<h3>De Deco-app (optioneel)</h3>
<p>Via de gratis <strong>TP-Link Deco-app</strong> (iOS of Android) kunt u:</p>
<ul>
  <li>Zien welke apparaten verbonden zijn</li>
  <li>Het wifi-wachtwoord aanpassen</li>
  <li>Gastnetwerken aanmaken voor huurders</li>
  <li>Apparaten tijdelijk de internettoegang ontnemen (Parental Controls)</li>
</ul>
<p>Inloggen in de app:<br/>
<strong>Account:</strong> thomas@hostinglocal.be<br/>
Neem contact op met uw installateur voor het wachtwoord van de beheerapp.</p>

<hr/>

<h3>Wat te doen als het wifi niet werkt?</h3>
<ol>
  <li><strong>Controleer of de Deco-antenne een blauw lampje heeft.</strong>
      Oranje of rood lampje = probleem met die antenne.</li>
  <li><strong>Herstart de master-antenne</strong> (staat in de technische ruimte):
      stekker eruit, 10 seconden wachten, terug insteken. Wacht 2 minuten.</li>
  <li><strong>Controleer het modem</strong> van Telenet: ook dit kan u herstarten
      door de stekker eruit te halen en terug in te steken.</li>
  <li>Werkt het nog steeds niet? Neem contact op via de gegevens hieronder.</li>
</ol>

<hr/>

<h3>Locatie van de antennes</h3>
<ul>
  <li>Master-antenne: technische ruimte</li>
  <li>Antenne 2: gelijkvloers — zithoek</li>
  <li>Antenne 3: gelijkvloers — keuken</li>
  <li>Antenne 4 &amp; 5: zie plaatsingsplan</li>
</ul>

<hr/>

<h3>Contact bij problemen</h3>
<p><strong>Working Local</strong><br/>
thomas@hostinglocal.be</p>
""")

# ══════════════════════════════════════════════════════════════════════════════
# IDE - TACK — Parental Control handleiding
# Project id=2
# ══════════════════════════════════════════════════════════════════════════════
handleiding('Handleiding: Parental Control', 2, """
<h2>Parental Control — Hoe werkt het?</h2>
<p>Uw netwerk is opgesplitst in <strong>drie profielen</strong>. Elk profiel heeft een eigen
wifi-wachtwoord en eigen instellingen voor internettoegang en tijdsbeperkingen.</p>

<hr/>

<h3>De drie wifi-profielen</h3>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><th>Profiel</th><th>Wifi-naam</th><th>Wachtwoord</th><th>Voor wie</th></tr>
  <tr><td><strong>Ouders</strong></td><td>Ide Wifi</td><td>Idewifi55</td><td>Ouders, thuiswerken, vaste toestellen</td></tr>
  <tr><td><strong>Kids</strong></td><td>Ide Wifi</td><td>141011300614</td><td>Kinderen — met tijdsbeperkingen</td></tr>
  <tr><td><strong>Gasten</strong></td><td>Ide Wifi Guest</td><td>Open (geen wachtwoord)</td><td>Bezoekers</td></tr>
</table>
<p><em>Tip: verbind de toestellen van uw kinderen eenmalig met het Kids-wachtwoord.
Daarna hoeft u niets meer te doen — de tijdsbeperkingen gelden automatisch.</em></p>

<hr/>

<h3>Wifi uitschakelen op vaste tijden (Blackout)</h3>
<p>Via de <strong>UniFi-app</strong> kunt u instellen dat het Kids-profiel
automatisch uitvalt op bepaalde uren — bijvoorbeeld 's avonds of tijdens schooltijd.</p>
<ol>
  <li>Open de UniFi-app op uw smartphone.</li>
  <li>Ga naar <strong>Profiles</strong> &gt; <strong>IDE - Kids</strong>.</li>
  <li>Tik op <strong>Schedule</strong> of <strong>Wifi Blackout</strong>.</li>
  <li>Stel de gewenste tijden in per dag van de week.</li>
  <li>Tik op <strong>Save</strong>.</li>
</ol>
<p><strong>Let op:</strong> u kunt twee schema's instellen — één voor schooldagen
en één voor weekends of vakantie. Zo hoeft u niets manueel aan te passen.</p>

<hr/>

<h3>Internet volledig uitschakelen voor een toestel</h3>
<p>Wilt u een specifiek toestel (bv. de tablet van uw kind) tijdelijk blokkeren?</p>
<ol>
  <li>Open de UniFi-app.</li>
  <li>Ga naar <strong>Clients</strong> (lijst van verbonden toestellen).</li>
  <li>Tik op het toestel dat u wilt blokkeren.</li>
  <li>Tik op <strong>Block</strong>. Het toestel heeft geen internet meer
      totdat u het terug deblokkeren via dezelfde knop (<strong>Unblock</strong>).</li>
</ol>

<hr/>

<h3>Websites blokkeren</h3>
<p>Via het Kids-profiel kunt u categorieën van websites blokkeren
(bv. social media, gaming, volwasseneninhoud).</p>
<ol>
  <li>Open de UniFi-app &gt; <strong>Profiles</strong> &gt; <strong>IDE - Kids</strong>.</li>
  <li>Ga naar <strong>Content Filtering</strong>.</li>
  <li>Activeer de categorieën die u wilt blokkeren.</li>
  <li>Tik op <strong>Apply</strong>.</li>
</ol>

<hr/>

<h3>Inloggegevens UniFi-app</h3>
<p>Vraag uw installateur naar de inloggegevens voor de UniFi-app.<br/>
<strong>Working Local</strong> — thomas@hostinglocal.be</p>
""")

# ══════════════════════════════════════════════════════════════════════════════
# WERKPLAATS WALTER — Volledige Unifi installatie documentatie
# Project id=3
# ══════════════════════════════════════════════════════════════════════════════
handleiding('Documentatie: Netwerk & Unifi installatie', 3, """
<h2>Netwerkinstallatie Werkplaats Walter</h2>
<p>Werkplaats Walter beschikt over een volledig professioneel netwerk op basis van
<strong>Ubiquiti UniFi</strong>. Dit document bevat alles wat u nodig hebt om
het netwerk te beheren en te begrijpen.</p>

<hr/>

<h3>Wifi-netwerken (SSID's)</h3>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><th>Netwerknaam</th><th>Wachtwoord</th><th>Gebruik</th></tr>
  <tr><td><strong>Werkplaats Walter Intern</strong></td><td>WerkWalt1070</td><td>Medewerkers en vaste huurders</td></tr>
  <tr><td><strong>Werkplaats Walter Guest</strong></td><td>walterwerkt</td><td>Bezoekers en publiek — wachtwoord op toog</td></tr>
  <tr><td><strong>Werkplaats Walter Venue</strong></td><td>WeWa1070Venue</td><td>Events, optredens, polyvalente zaal</td></tr>
  <tr><td><strong>Werkplaats Walter Tech</strong></td><td>WerkWalt1070iot</td><td>Technische apparaten — verborgen netwerk</td></tr>
</table>
<p><em>Het Tech-netwerk is verborgen en niet zichtbaar in de lijst van beschikbare wifi-netwerken.
Alleen technische apparaten (printers, schermen, sensoren) worden hierop aangesloten.</em></p>

<hr/>

<h3>Hardware-overzicht</h3>
<p><strong>Hoofdrack (kelder, verdiep -1):</strong></p>
<ul>
  <li>UniFi Dream Machine Pro SE — gateway, firewall en controller</li>
  <li>UniFi Switch Pro Max 24 (non-POE) × 2</li>
  <li>UniFi Switch Pro Max 24 POE — voeding voor access points</li>
  <li>Aggregatieswitch — verbinding tussen hoofd- en verdiepracks</li>
  <li>Proximus Fiber modem (te verplaatsen naar dit rack)</li>
</ul>
<p><strong>Verdiepracks:</strong></p>
<ul>
  <li>Per verdiep: UniFi Switch Pro Max 16 (× 2 non-POE + × 1 POE)</li>
</ul>
<p><strong>Access Points:</strong> 29 UniFi U6+ (indoor) + 1 outdoor<br/>
Verspreid over alle verdiepen en ruimtes. Elk access point dekt 1 ruimte.</p>

<hr/>

<h3>Netwerksegmentatie</h3>
<p>Het netwerk is opgesplitst in aparte segmenten (VLAN's) zodat apparaten van
verschillende huurders of zones elkaar niet kunnen bereiken:</p>
<ul>
  <li><strong>Intern</strong> — huurders en medewerkers, toegang tot gedeelde printers</li>
  <li><strong>Gasten</strong> — internetverbinding, geen toegang tot intern netwerk</li>
  <li><strong>Venue</strong> — geïsoleerd netwerk voor events</li>
  <li><strong>Tech/IoT</strong> — technische apparaten gescheiden van de rest</li>
  <li><strong>Appartementen</strong> — volledig gescheiden van Werkplaats Walter</li>
</ul>
<p>Per access point kunnen maximaal 4 aparte wifi-netwerken actief zijn.
Dit maakt het mogelijk om per ruimte of per huurder een eigen netwerk aan te bieden.</p>

<hr/>

<h3>Internetverbinding</h3>
<ul>
  <li><strong>Hoofdverbinding:</strong> Proximus Fiber 1 Gbit/s down — 500 Mbit/s up</li>
  <li><strong>Klantennummer Proximus:</strong> 619723409</li>
  <li><strong>Telefoonnummer (IP):</strong> 02 356 29 32</li>
  <li><strong>Geplande 2e verbinding:</strong> failover via EDPnet (in uitvoering)</li>
</ul>

<hr/>

<h3>UniFi beheren</h3>
<p>Het netwerk wordt centraal beheerd via de <strong>UniFi Network-app</strong>
of via de webinterface op de Dream Machine Pro SE.</p>
<p>Wat u zelf kunt doen via de app:</p>
<ul>
  <li>Zien welke toestellen verbonden zijn en op welk access point</li>
  <li>Wifi-wachtwoord aanpassen</li>
  <li>Een toestel tijdelijk blokkeren</li>
  <li>Bandbreedte per netwerk beperken</li>
  <li>Statistieken bekijken (hoeveel data, snelheid per gebruiker)</li>
</ul>
<p>Vraag uw installateur naar de inloggegevens voor de beheerinterface.</p>

<hr/>

<h3>Nieuwe huurder aansluiten</h3>
<ol>
  <li>Geef de huurder het wachtwoord van <strong>Werkplaats Walter Intern</strong>
      voor het gedeelde interne netwerk.</li>
  <li>Wil de huurder een <strong>eigen, volledig afgeschermd netwerk</strong>?
      Contacteer dan uw installateur — dit kan worden ingesteld via een
      apart SSID dat enkel zichtbaar is op de access points in zijn ruimte.</li>
</ol>

<hr/>

<h3>Wat te doen bij problemen</h3>
<ol>
  <li><strong>Geen internet?</strong> Controleer of de lampjes op de Dream Machine Pro SE (hoofdrack, kelder) normaal branden. Groen = OK.</li>
  <li><strong>Eén ruimte zonder wifi?</strong> Controleer het access point in die ruimte — het lampje onderaan knippert blauw als het normaal werkt.</li>
  <li><strong>Herstart:</strong> trek de stekker van het betreffende access point of de switch eruit, wacht 10 seconden en steek terug in.</li>
  <li><strong>Probleem aanmelden:</strong> maak een taak aan in dit portaal of neem contact op via thomas@hostinglocal.be</li>
</ol>

<hr/>

<h3>Contact &amp; Installateur</h3>
<p><strong>Working Local</strong><br/>
thomas@hostinglocal.be<br/>
Telefonisch via Teun Verbruggen of Lien Van Steendam</p>
""")

print("\nAlle handleidingen aangemaakt.")
