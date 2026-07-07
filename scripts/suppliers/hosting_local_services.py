"""
Hosting Local — Volledige diensten- en productcatalogus
scripts/suppliers/hosting_local_services.py

Maakt aan:
  - Diensten > Server & Virtualisatie  (SRV-VIRT-*)
  - Diensten > IT Beheer & Support     (SRV-IT-*)
  - Diensten > Monitoring              (SRV-MON-*)
  - Diensten > Beveiliging & Toegang   (SRV-SEC-*)
  - Diensten > Microsoft 365           (SRV-M365-*)
  - Diensten > Managed Hosting         (SRV-HOST-*)
  - IT-hardware > Turnkey Servers      (HL-SRV-*)  — refurbished PV-consulting hardware,
                                                      klaar met Proxmox / PBS / Grafana

Circulaire focus: Dell OptiPlex en Lenovo P-serie van PV-consulting als basis voor
alle Hosting Local serveroplossingen. Refurbished hardware + lokale software-stack.

Gebruik:
    python scripts/suppliers/hosting_local_services.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from odoo_client import OdooClient, b64


# ── SVG helpers ───────────────────────────────────────────────────────────────

def _svg(shapes, label):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">'
        '<rect width="400" height="400" fill="#1A2E5A"/>'
        f'{shapes}'
        f'<text x="200" y="374" font-family="Arial,sans-serif" font-size="19" font-weight="bold"'
        f' text-anchor="middle" fill="#F5B800" opacity="0.9">{label}</text>'
        '</svg>'
    )
    return b64(svg.encode('utf-8'))


ICONS = {
    'virt': (
        # Rack + virtualisatielagen
        '<rect x="80" y="60" width="240" height="200" rx="12" fill="none" stroke="#F5B800" stroke-width="12"/>'
        '<rect x="100" y="85" width="200" height="32" rx="5" fill="#F5B800" opacity="0.18"/>'
        '<rect x="100" y="85" width="200" height="32" rx="5" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<rect x="100" y="130" width="200" height="32" rx="5" fill="#F5B800" opacity="0.18"/>'
        '<rect x="100" y="130" width="200" height="32" rx="5" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<rect x="100" y="175" width="200" height="32" rx="5" fill="#F5B800" opacity="0.18"/>'
        '<rect x="100" y="175" width="200" height="32" rx="5" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<circle cx="278" cy="101" r="7" fill="#F5B800"/>'
        '<circle cx="278" cy="146" r="7" fill="#F5B800" opacity="0.55"/>'
        '<circle cx="278" cy="191" r="7" fill="#F5B800" opacity="0.3"/>'
        '<path d="M140,295 L200,265 L260,295" stroke="#F5B800" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M140,315 L200,285 L260,315" stroke="#F5B800" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/>',
        'Virtualisatie'
    ),
    'it': (
        # Tandwiel
        '<circle cx="200" cy="185" r="55" fill="none" stroke="#F5B800" stroke-width="12"/>'
        '<circle cx="200" cy="185" r="25" fill="#F5B800" opacity="0.25"/>'
        '<circle cx="200" cy="185" r="25" fill="none" stroke="#F5B800" stroke-width="8"/>'
        '<rect x="191" y="105" width="18" height="32" rx="7" fill="#F5B800"/>'
        '<rect x="191" y="233" width="18" height="32" rx="7" fill="#F5B800"/>'
        '<rect x="105" y="176" width="32" height="18" rx="7" fill="#F5B800"/>'
        '<rect x="233" y="176" width="32" height="18" rx="7" fill="#F5B800"/>'
        '<rect x="134" y="118" width="18" height="32" rx="7" fill="#F5B800" transform="rotate(45 143 134)"/>'
        '<rect x="220" y="207" width="18" height="32" rx="7" fill="#F5B800" transform="rotate(45 229 223)"/>'
        '<rect x="134" y="207" width="32" height="18" rx="7" fill="#F5B800" transform="rotate(45 150 216)"/>'
        '<rect x="220" y="118" width="32" height="18" rx="7" fill="#F5B800" transform="rotate(45 236 127)"/>',
        'IT Beheer'
    ),
    'mon': (
        # Dashboard grafiek
        '<rect x="65" y="85" width="270" height="175" rx="12" fill="none" stroke="#F5B800" stroke-width="11"/>'
        '<polyline points="90,210 135,160 175,180 220,120 265,145 305,105" '
        'stroke="#F5B800" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="90"  cy="210" r="6" fill="#F5B800"/>'
        '<circle cx="135" cy="160" r="6" fill="#F5B800"/>'
        '<circle cx="175" cy="180" r="6" fill="#F5B800"/>'
        '<circle cx="220" cy="120" r="6" fill="#F5B800"/>'
        '<circle cx="265" cy="145" r="6" fill="#F5B800"/>'
        '<circle cx="305" cy="105" r="6" fill="#F5B800"/>'
        '<line x1="90" y1="260" x2="310" y2="260" stroke="#F5B800" stroke-width="7" stroke-linecap="round" opacity="0.4"/>',
        'Monitoring'
    ),
    'sec': (
        # Schild + slot
        '<path d="M200,55 L325,105 L325,230 Q325,318 200,358 Q75,318 75,230 L75,105 Z" '
        'fill="none" stroke="#F5B800" stroke-width="12" stroke-linejoin="round"/>'
        '<rect x="165" y="185" width="70" height="55" rx="8" fill="none" stroke="#F5B800" stroke-width="10"/>'
        '<path d="M175,185 Q175,152 200,152 Q225,152 225,185" '
        'fill="none" stroke="#F5B800" stroke-width="10" stroke-linecap="round"/>'
        '<circle cx="200" cy="212" r="8" fill="#F5B800"/>',
        'Beveiliging'
    ),
    'm365': (
        # M-logo gestileerd
        '<rect x="80" y="80" width="240" height="240" rx="20" fill="none" stroke="#F5B800" stroke-width="11"/>'
        '<path d="M120,290 L120,145 L200,230 L280,145 L280,290" '
        'stroke="#F5B800" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="120" y1="290" x2="280" y2="290" stroke="#F5B800" stroke-width="10" stroke-linecap="round" opacity="0.5"/>',
        'Microsoft 365'
    ),
    'host': (
        # Huis + server
        '<path d="M200,70 L330,165 L310,165 L310,305 L90,305 L90,165 L70,165 Z" '
        'fill="none" stroke="#F5B800" stroke-width="11" stroke-linejoin="round"/>'
        '<rect x="135" y="215" width="130" height="32" rx="5" fill="#F5B800" opacity="0.18"/>'
        '<rect x="135" y="215" width="130" height="32" rx="5" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<rect x="135" y="260" width="130" height="28" rx="5" fill="#F5B800" opacity="0.18"/>'
        '<rect x="135" y="260" width="130" height="28" rx="5" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<circle cx="244" cy="231" r="6" fill="#F5B800"/>'
        '<circle cx="244" cy="274" r="6" fill="#F5B800" opacity="0.5"/>',
        'Managed Hosting'
    ),
    'server': (
        # Enkele server/mini-PC met recycling pijlen
        '<rect x="90" y="100" width="220" height="155" rx="14" fill="none" stroke="#F5B800" stroke-width="12"/>'
        '<rect x="110" y="122" width="180" height="30" rx="5" fill="#F5B800" opacity="0.18"/>'
        '<rect x="110" y="122" width="180" height="30" rx="5" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<rect x="110" y="165" width="180" height="30" rx="5" fill="#F5B800" opacity="0.18"/>'
        '<rect x="110" y="165" width="180" height="30" rx="5" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<circle cx="268" cy="137" r="6" fill="#F5B800"/>'
        '<circle cx="268" cy="180" r="6" fill="#F5B800" opacity="0.5"/>'
        # Circulair pijltje
        '<path d="M155,295 Q200,270 245,295" stroke="#F5B800" stroke-width="8" fill="none" stroke-linecap="round"/>'
        '<polygon points="245,287 245,303 258,295" fill="#F5B800"/>'
        '<path d="M245,295 Q200,320 155,295" stroke="#F5B800" stroke-width="8" fill="none" stroke-linecap="round" opacity="0.6"/>'
        '<polygon points="155,287 155,303 142,295" fill="#F5B800" opacity="0.6"/>',
        'Circulaire Server'
    ),
}

def svg_icon(key):
    shapes, label = ICONS[key]
    return _svg(shapes, label)


# ── Producten ─────────────────────────────────────────────────────────────────

# Refurbished servers klaar met Hosting Local software-stack
# Hardware van PV-consulting, geconfigureerd door Hosting Local
TURNKEY_SERVERS = [
    {
        'ref': 'HL-SRV-01',
        'name': 'Proxmox Virtualisatiehost — Dell OptiPlex 3050 SFF, i5-6500, 16GB, 256GB NVMe, Proxmox VE',
        'list_price': 349.00,
        'standard_price': 249.00,
        'description_sale': (
            'Refurbished Dell OptiPlex 3050 SFF geconfigureerd als volwaardige Proxmox VE virtualisatiehost. '
            'Draait 2–4 VMs of LXC containers gelijktijdig. '
            'Inclusief Proxmox installatie, netwerkconfiguratie en basisbeveiliging. '
            'Uitbreidbaar met extra opslag. '
            'Verbruik: ~35–65W (24/7 ≈ €5–9/mnd). Refurbished — circulair aanbod.'
        ),
    },
    {
        'ref': 'HL-SRV-02',
        'name': 'Proxmox Virtualisatiehost Pro — Lenovo P520, Xeon W, 32GB, 1TB NVMe, Proxmox VE',
        'list_price': 699.00,
        'standard_price': 499.00,
        'description_sale': (
            'Refurbished Lenovo ThinkStation P520 als krachtige Proxmox VE virtualisatiehost. '
            'Geschikt voor 6–10 gelijktijdige VMs of containers, zware workloads, development en staging. '
            'Inclusief Proxmox installatie, cluster-voorbereiding en storage configuratie. '
            'Verbruik: ~80–180W (24/7 ≈ €12–26/mnd). Refurbished — circulair aanbod.'
        ),
    },
    {
        'ref': 'HL-SRV-03',
        'name': 'Proxmox Backup Server — Dell OptiPlex 3050 SFF, i5-6500, 16GB, PBS + extra opslag',
        'list_price': 399.00,
        'standard_price': 280.00,
        'description_sale': (
            'Refurbished Dell OptiPlex 3050 SFF als dedicated Proxmox Backup Server (PBS). '
            'Deduplicated, incrementele backups van VMs, containers en werkstations. '
            'Inclusief PBS installatie, datastore configuratie en backup-jobs voor uw Proxmox-omgeving. '
            'Uitbreidbaar met USB- of interne schijven. '
            'Verbruik: ~35–55W (24/7 ≈ €5–8/mnd). Refurbished — circulair aanbod.'
        ),
    },
    {
        'ref': 'HL-SRV-04',
        'name': 'Monitoring Server — Dell OptiPlex 3050 SFF, i5-6500, 16GB, Grafana + Prometheus',
        'list_price': 349.00,
        'standard_price': 249.00,
        'description_sale': (
            'Refurbished Dell OptiPlex 3050 SFF als dedicated monitoring server. '
            'Draait Grafana (dashboards), Prometheus (metrics) en Uptime Kuma (uptime). '
            'Inclusief installatie, basisdashboards voor netwerk en servers, en alerting via e-mail. '
            'Verbruik: ~30–50W (24/7 ≈ €4–7/mnd). Refurbished — circulair aanbod.'
        ),
    },
    {
        'ref': 'HL-SRV-05',
        'name': 'NAS & Fileserver — Dell OptiPlex 3050 SFF, i5-6500, 16GB, TrueNAS SCALE',
        'list_price': 399.00,
        'standard_price': 280.00,
        'description_sale': (
            'Refurbished Dell OptiPlex 3050 SFF als lokale fileserver op TrueNAS SCALE. '
            'ZFS-opslag, SMB/NFS shares, automatische snapshots en replicatie. '
            'Inclusief installatie, poolconfiguratie en netwerkkoppelingen. '
            'Schijven apart te bestellen. '
            'Verbruik: ~35–60W (24/7 ≈ €5–9/mnd). Refurbished — circulair aanbod.'
        ),
    },
]

DIENSTEN = {
    'Server & Virtualisatie': [
        {
            'ref': 'SRV-VIRT-01',
            'name': 'Proxmox VE installatie & basisconfiguratie',
            'list_price': 149.00,
            'description_sale': (
                'Installatie van Proxmox Virtual Environment op refurbished hardware. '
                'Netwerkconfiguratie, storage setup, basisbeveiliging en eerste VM of container. '
                'Forfaitprijs; complexe omgevingen in regie à €65/u.'
            ),
        },
        {
            'ref': 'SRV-VIRT-02',
            'name': 'VM of container aanmaken & configureren',
            'list_price': 65.00,
            'description_sale': (
                'Aanmaken en configureren van een virtuele machine (VM) of LXC container '
                'op een bestaande Proxmox-omgeving. Inclusief OS-installatie en netwerkkoppeling. '
                'Prijs per uur excl. BTW.'
            ),
        },
        {
            'ref': 'SRV-VIRT-03',
            'name': 'Docker & Coolify setup op refurbished hardware',
            'list_price': 149.00,
            'description_sale': (
                'Installatie van Docker en Coolify (self-hosted PaaS) op refurbished hardware. '
                'Inclusief reverse proxy (Caddy/Traefik), SSL en eerste applicatie-deployment. '
                'Forfaitprijs.'
            ),
        },
        {
            'ref': 'SRV-VIRT-04',
            'name': 'Virtualisatie & serveromgeving — Maandabonnement',
            'list_price': 39.00,
            'description_sale': (
                'Maandelijks beheer van uw Proxmox of Docker omgeving: updates, patching, '
                'controle van VM-gezondheid en opslaggebruik, kwartaalrapport. '
                'Prijs per maand excl. BTW.'
            ),
        },
    ],

    'IT Beheer & Support': [
        {
            'ref': 'SRV-IT-01',
            'name': 'IT audit & inventarisatie — hardware, software en netwerk',
            'list_price': 199.00,
            'description_sale': (
                'Volledige inventarisatie van uw IT-omgeving: hardware (inclusief leeftijd en '
                'vervangingsstrategie), software, netwerk en beveiligingsniveau. '
                'Schriftelijk auditrapport met prioriteitenlijst en circulaire vervangingsopties.'
            ),
        },
        {
            'ref': 'SRV-IT-02',
            'name': 'IT beheer — Maandabonnement',
            'list_price': 49.00,
            'description_sale': (
                'Maandelijks IT-beheer: updates en patches, monitoring van systemen, '
                'proactieve opvolging en maandrapport. '
                'Inclusief remote interventie (tot 30 min/mnd). Prijs per maand excl. BTW.'
            ),
        },
        {
            'ref': 'SRV-IT-03',
            'name': 'Remote interventie — IT support op afstand',
            'list_price': 50.00,
            'description_sale': (
                'Remote probleemoplossing via SSH of remote desktop. '
                'Forfaitprijs per interventie excl. BTW.'
            ),
        },
        {
            'ref': 'SRV-IT-04',
            'name': 'Interventie ter plaatse — IT support on-site',
            'list_price': 99.00,
            'description_sale': (
                'Probleemoplossing en configuratie ter plaatse bij de klant. '
                'Forfaitprijs (tot 1u) excl. BTW; daarna €65/u.'
            ),
        },
        {
            'ref': 'SRV-IT-05',
            'name': 'Hardware advies & selectie — circulair vervangingsplan',
            'list_price': 99.00,
            'description_sale': (
                'Advies over hardware-vervanging met focus op refurbished en circulair aanbod. '
                'Op basis van uw IT-audit (SRV-IT-01) of los aan te vragen. '
                'Forfaitprijs excl. BTW.'
            ),
        },
    ],

    'Monitoring': [
        {
            'ref': 'SRV-MON-01',
            'name': 'Monitoring setup — Grafana + Prometheus + Uptime Kuma',
            'list_price': 149.00,
            'description_sale': (
                'Installatie en configuratie van een lokaal monitoring platform: '
                'Grafana (dashboards), Prometheus (metrics) en Uptime Kuma (uptime). '
                'Inclusief basisdashboards voor servers, netwerk en services. '
                'Op eigen hardware (circulair aanbod HL-SRV-04) of bestaande server.'
            ),
        },
        {
            'ref': 'SRV-MON-02',
            'name': 'Monitoring & alerting — Maandabonnement',
            'list_price': 19.00,
            'description_sale': (
                'Maandelijkse opvolging van uw monitoring: controle van dashboards, '
                'alertingregels bijsturen, kwartaalrapport met trends en aanbevelingen. '
                'Prijs per maand excl. BTW.'
            ),
        },
        {
            'ref': 'SRV-MON-03',
            'name': 'Uptime monitoring — Maandabonnement',
            'list_price': 9.00,
            'description_sale': (
                'Uptime monitoring van uw publieke services (website, mail, VPN) via Uptime Kuma. '
                'Alerting bij downtime via e-mail of notificatie. '
                'Prijs per maand excl. BTW.'
            ),
        },
    ],

    'Beveiliging & Toegang': [
        {
            'ref': 'SRV-SEC-01',
            'name': 'Firewall audit & configuratie — UniFi of pfSense',
            'list_price': 149.00,
            'description_sale': (
                'Audit van bestaande firewallregels en configuratie van een gezonde '
                'netwerksegmentatie: VLAN-indeling, poortrestricties en gastnetwerk. '
                'Op UniFi (UDM/USG) of pfSense/OPNsense. Forfaitprijs.'
            ),
        },
        {
            'ref': 'SRV-SEC-02',
            'name': 'VPN setup — Tailscale of WireGuard',
            'list_price': 99.00,
            'description_sale': (
                'Installatie en configuratie van een zero-config VPN (Tailscale) of '
                'traditionele WireGuard VPN voor veilige remote toegang. '
                'Inclusief toestellen koppelen en documentatie. Forfaitprijs.'
            ),
        },
        {
            'ref': 'SRV-SEC-03',
            'name': 'SSO implementatie — Keycloak of Authentik',
            'list_price': 249.00,
            'description_sale': (
                'Opzet van een centraal Single Sign-On platform (Keycloak of Authentik) '
                'op refurbished hardware of bestaande virtualisatieomgeving. '
                'Koppeling met bestaande applicaties (Grafana, Nextcloud, e.d.). '
                'Forfaitprijs; integraties per applicatie €65/u.'
            ),
        },
        {
            'ref': 'SRV-SEC-04',
            'name': 'Security audit — netwerk, toegang en patching',
            'list_price': 199.00,
            'description_sale': (
                'Grondige beoordeling van uw beveiligingsniveau: open poorten, '
                'patch-achterstand, wachtwoordbeleid, encryptie en toegangsrechten. '
                'Schriftelijk rapport met prioriteitenlijst. Forfaitprijs.'
            ),
        },
    ],

    'Microsoft 365': [
        {
            'ref': 'SRV-M365-01',
            'name': 'Microsoft 365 tenant setup & configuratie',
            'list_price': 249.00,
            'description_sale': (
                'Opzet van een Microsoft 365 tenant: domeinkoppeling, gebruikersbeheer, '
                'Exchange Online, SharePoint basisstructuur en beveiligingsbeleid. '
                'Forfaitprijs voor maximaal 5 gebruikers; daarna €65/u.'
            ),
        },
        {
            'ref': 'SRV-M365-02',
            'name': 'Microsoft 365 migratie — e-mail en data',
            'list_price': 65.00,
            'description_sale': (
                'Migratie van bestaande e-mail (Gmail, IMAP, lokale Exchange) en bestanden '
                'naar Microsoft 365. Prijs per uur excl. BTW.'
            ),
        },
        {
            'ref': 'SRV-M365-03',
            'name': 'Teams Room setup — vergaderruimte configuratie',
            'list_price': 199.00,
            'description_sale': (
                'Configuratie van een Microsoft Teams vergaderruimte: '
                'room account, kalenderintegratie, audio/video hardware koppeling '
                'en testoproep. Forfaitprijs per ruimte.'
            ),
        },
        {
            'ref': 'SRV-M365-04',
            'name': 'Microsoft 365 beheer — Maandabonnement',
            'list_price': 29.00,
            'description_sale': (
                'Maandelijks beheer van uw M365 tenant: gebruikersbeheer, licentieopvolging, '
                'beveiligingswaarschuwingen en maandrapport. '
                'Prijs per maand excl. BTW.'
            ),
        },
    ],

    'Managed Hosting': [
        {
            'ref': 'SRV-HOST-01',
            'name': 'Managed VM — Maandabonnement (op Hosting Local infrastructuur)',
            'list_price': 29.00,
            'description_sale': (
                'Beheerde virtuele machine op de Hosting Local infrastructuur. '
                'Inclusief backups (dagelijks), updates, monitoring en support. '
                'Data blijft in België, op eigen hardware. Prijs per maand excl. BTW.'
            ),
        },
        {
            'ref': 'SRV-HOST-02',
            'name': 'Managed website hosting — Maandabonnement',
            'list_price': 19.00,
            'description_sale': (
                'WordPress of statische website gehost op Hosting Local infrastructuur. '
                'Inclusief SSL, dagelijkse backups, updates en 99,9% uptime garantie. '
                'Data blijft in België. Prijs per maand excl. BTW.'
            ),
        },
        {
            'ref': 'SRV-HOST-03',
            'name': 'Managed Docker service — Maandabonnement',
            'list_price': 39.00,
            'description_sale': (
                'Beheerde Docker-applicatie (Nextcloud, Gitea, n8n, e.d.) '
                'op Hosting Local infrastructuur via Coolify. '
                'Inclusief updates, backups en monitoring. Prijs per maand excl. BTW.'
            ),
        },
    ],
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    odoo = OdooClient()

    print("\n── Categorieën ──────────────────────────────────────────────────")
    diensten_id = odoo.get_or_create_cat('Diensten')
    it_hw_id    = odoo.get_or_create_cat('IT-hardware')

    cat_ids = {}
    for naam in DIENSTEN:
        cat_ids[naam] = odoo.get_or_create_cat(naam, parent_id=diensten_id)

    turnkey_cat_id = odoo.get_or_create_cat('Turnkey Servers', parent_id=it_hw_id)

    print("\n── Turnkey servers (circulaire hardware + HL software) ──────────")
    srv_img = svg_icon('server')
    for p in TURNKEY_SERVERS:
        odoo.upsert_product(p['ref'], {
            'name':             p['name'],
            'categ_id':         turnkey_cat_id,
            'list_price':       p['list_price'],
            'standard_price':   p['standard_price'],
            'type':             'consu',
            'description_sale': p['description_sale'],
            'x_status':         'beschikbaar',
        }, placeholder_b64=srv_img)

    print("\n── Diensten ─────────────────────────────────────────────────────")
    icon_map = {
        'Server & Virtualisatie': 'virt',
        'IT Beheer & Support':    'it',
        'Monitoring':             'mon',
        'Beveiliging & Toegang':  'sec',
        'Microsoft 365':          'm365',
        'Managed Hosting':        'host',
    }

    total = 0
    for categorie, producten in DIENSTEN.items():
        print(f"\n  {categorie}")
        img = svg_icon(icon_map[categorie])
        for s in producten:
            odoo.upsert_product(s['ref'], {
                'name':             s['name'],
                'categ_id':         cat_ids[categorie],
                'list_price':       s['list_price'],
                'type':             'service',
                'invoice_policy':   'order',
                'description_sale': s['description_sale'],
                'x_status':         'beschikbaar',
            }, placeholder_b64=img)
            total += 1

    print(f"\n── Klaar ─────────────────────────────────────────────────────────")
    print(f"{len(TURNKEY_SERVERS)} turnkey servers (IT-hardware > Turnkey Servers)")
    print(f"{total} diensten verdeeld over {len(DIENSTEN)} categorieën")


if __name__ == '__main__':
    main()
