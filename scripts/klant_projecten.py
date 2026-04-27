# -*- coding: utf-8 -*-
"""
Project + taken aanmaken per klant op basis van open to-do's uit de dossiers.
Portal-zichtbaar zodat klanten kunnen opvolgen via /my.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'suppliers'))
from odoo_client import OdooClient

pw = sys.argv[1] if len(sys.argv) > 1 else None
odoo = OdooClient(password=pw)

def project(naam, partner_id):
    bestaande = odoo.search_read('project.project',
        [('name', '=', naam)], ['id', 'name'])
    if bestaande:
        print('Project al aanwezig: {}'.format(naam))
        return bestaande[0]['id']
    pid = odoo.create('project.project', {
        'name':       naam,
        'partner_id': partner_id,
        'privacy_visibility': 'portal',  # zichtbaar voor klant
    })
    print('Project aangemaakt: {} (id={})'.format(naam, pid))
    return pid

def taak(naam, project_id, beschrijving=None):
    odoo.create('project.task', {
        'name':        naam,
        'project_id':  project_id,
        'description': beschrijving or '',
    })
    print('  Taak: {}'.format(naam))

# ── Vakantiehuis Muziekbos (partner id=7) ───────────────────────────────────
p = project('Vakantiehuis Muziekbos - Wifi uitbreiding', 7)
taak('2 extra TP-Link Deco X60 antennes plaatsen', p,
    'Onvoldoende dekking op grote slaapkamer bovenaan en verste kamers kelder. '
    'Wandrekjes worden geleverd door kennis van klant — contact opnemen bij levering.')
taak('Telenet Center Ronse bezoeken (Derco Systems)', p,
    'Nagaan wat er op naam van Maarten Lauwers hangt vs. vakantiehuisabonnement. '
    'Alles groeperen onder Vakantiehuis Muziekbos. Modem eventueel bridgen.\n'
    'Derco Systems, Peperstraat 37, 9600 Ronse — 055/21.07.75 — ronse@derco.be')
taak('Evaluatie: overstap naar Unifi in-wall AP', p,
    'Huidige Deco-materiaal heeft nog tweedehandswaarde. '
    'Kleinste Unifi inwall AP lost datapunten-op-tv-hoogte probleem op.')

# ── Ide - Tack (partner id=9) ────────────────────────────────────────────────
p = project('Ide - Tack - Netwerk oplevering', 9)
taak('Telenet modem volledig bridgen', p,
    'Modem staat nu als DHCP-server (192.168.5.226 > 192.168.0.1). '
    'Vaste adressen in 192.168.0.x-range aanpassen voor overgang.')
taak('IoT-band instellen op 20MHz', p,
    'Blijft nu op 40MHz staan. Aiphone kan hierdoor niet verbinden.')
taak('Parental Control instellen', p,
    'Heel belangrijk voor klant. Via Unifi per profiel instellen: IDE - Kids.')
taak('Wifi blackout aanleren via app', p,
    'Tijdschema verschilt in vakantie vs. normale periode. Klant zelf leren instellen.')
taak('Poolhouse wifi-dekking verbeteren', p,
    'Op randje nu, zeker op 5GHz. Extra AP of mesh-unit evalueren.')
taak('HP Multifunctional op wifi aansluiten', p, '')

# ── Werkplaats Walter (partner id=10) ────────────────────────────────────────
p = project('Werkplaats Walter - Netwerk & ICT', 10)
taak('2e internetverbinding activeren + failover configureren', p,
    'EDPnet als failover: 1000/500, 4G failover, vast IP voor 85,95/mnd. '
    'Proximus 2.5Gbit als hoofdverbinding.')
taak('Proximus modem verplaatsen naar hoofdrack (-1)', p, '')
taak('Appartementen netwerk volledig isoleren', p,
    'Verdiep +4: 2 appartementen volledig gescheiden van Werkplaats Walter netwerk.')
taak('AP voorzien in hoofdrack (kelder)', p,
    'Hoofdrack staat nu in kelder zonder wifi-dekking.')
taak('Wifi in privaat verhuurde ateliers voorzien', p, '')
taak('Bekabeling concertruimte valideren', p, '')
taak('Metalen deur hoofdrack ontvangen en plaatsen', p, '')
taak('Patchkabelkleur corrigeren', p,
    'Blauw = interne bekabeling. Rood = uplink/toevoer/modem.')
taak('Kinderdagverblijf gelijkvloers: switch + AP', p,
    'Invulling handelspand vooraan. Eigen switch voorzien.')
taak('Signage vitrine vooraan evalueren', p, '')
taak('A3 printer + lamineerder installeren (gedeeld)', p, '')
taak('Boosters Proximus stopzetten op factuur', p,
    '2 gratis inbegrepen in oud pack, 3e staat betalend. Aanpassen bij Proximus.')

# ── Manu BV (partner id=17) ──────────────────────────────────────────────────
p = project('Manu BV - Project', 17)
taak('Projectinhoud nog in te vullen', p,
    'Klantenfiche aangemaakt. Projectdetails nog toe te voegen.')

print('\nAlle projecten en taken aangemaakt.')
print('Portaallink voor klanten: https://odoo.workinglocal.be/my')
