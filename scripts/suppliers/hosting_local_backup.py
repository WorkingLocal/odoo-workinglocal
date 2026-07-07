"""
Hosting Local — Backup & Opslag productcatalogus
scripts/suppliers/hosting_local_backup.py

Maakt aan:
  - Categorieën: IT-hardware > Backup & Opslag / Diensten > Backup
  - Hardware: refurbished backup server (eigen stock via PV-consulting)
  - Diensten: audit, installatie, monitoring (maandabonnement), data recovery

NAS-apparaten worden NIET verkocht — Hosting Local configureert de NAS van de klant.

Gebruik:
    python scripts/suppliers/hosting_local_backup.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from odoo_client import OdooClient, b64


# ── SVG placeholders ──────────────────────────────────────────────────────────

def _svg(shapes, label):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">'
        '<rect width="400" height="400" fill="#1A2E5A"/>'
        f'{shapes}'
        f'<text x="200" y="370" font-family="Arial,sans-serif" font-size="20" font-weight="bold"'
        f' text-anchor="middle" fill="#F5B800" opacity="0.9">{label}</text>'
        '</svg>'
    )
    return b64(svg.encode('utf-8'))


def svg_nas():
    shapes = (
        '<rect x="90" y="70" width="220" height="220" rx="14" fill="none" stroke="#F5B800" stroke-width="13"/>'
        '<rect x="110" y="100" width="180" height="38" rx="6" fill="#F5B800" opacity="0.15"/>'
        '<rect x="110" y="100" width="180" height="38" rx="6" fill="none" stroke="#F5B800" stroke-width="8"/>'
        '<rect x="110" y="154" width="180" height="38" rx="6" fill="#F5B800" opacity="0.15"/>'
        '<rect x="110" y="154" width="180" height="38" rx="6" fill="none" stroke="#F5B800" stroke-width="8"/>'
        '<rect x="110" y="208" width="180" height="38" rx="6" fill="#F5B800" opacity="0.15"/>'
        '<rect x="110" y="208" width="180" height="38" rx="6" fill="none" stroke="#F5B800" stroke-width="8"/>'
        '<circle cx="272" cy="119" r="8" fill="#F5B800"/>'
        '<circle cx="272" cy="173" r="8" fill="#F5B800" opacity="0.55"/>'
        '<circle cx="272" cy="227" r="8" fill="#F5B800" opacity="0.3"/>'
    )
    return _svg(shapes, 'Backup &amp; Opslag')


def svg_backup_service():
    shapes = (
        '<path d="M200,55 L330,105 L330,235 Q330,320 200,360 Q70,320 70,235 L70,105 Z" '
        'fill="none" stroke="#F5B800" stroke-width="13" stroke-linejoin="round"/>'
        '<path d="M148,198 L188,240 L258,158" stroke="#F5B800" stroke-width="15" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return _svg(shapes, 'Backup Dienst')


# ── Productdefinities ─────────────────────────────────────────────────────────

HARDWARE = [
    {
        'ref': 'BKP-PC-01',
        'name': 'Refurbished Backup Server — Dell OptiPlex 3050 SFF, i5-6500, 16GB, Proxmox Backup Server',
        'list_price': 299.00,
        'standard_price': 180.00,
        'description_sale': (
            'Kant-en-klare backup target op basis van Proxmox Backup Server (PBS). '
            'Uitbreidbaar met extra schijven via USB of interne bay. '
            'Ondersteunt incrementele en deduplicated backups van VMs, containers en werkstations. '
            'Refurbished hardware, inclusief basisinstallatie en configuratie.'
        ),
    },
]

DIENSTEN = [
    {
        'ref': 'SRV-BKP-01',
        'name': 'Backup audit & advies — analyse + aanbevelingsrapport',
        'list_price': 149.00,
        'description_sale': (
            'Analyse van de huidige backup-situatie: welke data wordt bewaard, '
            'hoe, hoe frequent en waar. Risicobeoordeling (RTO/RPO) en schriftelijk '
            'aanbevelingsrapport met concrete, budgetbewuste oplossingen.'
        ),
    },
    {
        'ref': 'SRV-BKP-02',
        'name': 'Backup installatie & configuratie',
        'list_price': 65.00,
        'description_sale': (
            'Installatie en configuratie van NAS, backup software (Synology DSM, '
            'Proxmox Backup Server, Veeam Agent of rclone) en automatische taken. '
            'Prijs per uur excl. BTW.'
        ),
    },
    {
        'ref': 'SRV-BKP-03',
        'name': 'Backup monitoring — Maandabonnement',
        'list_price': 19.00,
        'description_sale': (
            'Maandelijkse monitoring van alle geconfigureerde backup-jobs. '
            'Alerting bij fouten of gemiste backups, kwartaalrapport met overzicht '
            'en aanbevelingen. Prijs per maand excl. BTW.'
        ),
    },
    {
        'ref': 'SRV-BKP-04',
        'name': 'Data recovery — noodinterventie en herstel',
        'list_price': 199.00,
        'description_sale': (
            'Noodinterventie bij dataverlies: analyse van de situatie, '
            'herstel van bestanden of volledige systemen vanuit bestaande backup. '
            'Forfaitprijs; complexe gevallen in regie à €65/u excl. BTW.'
        ),
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    odoo = OdooClient()

    print("\n── Categorieën ──────────────────────────────────────────────────")
    it_id       = odoo.get_or_create_cat('IT-hardware')
    bkp_hw_id   = odoo.get_or_create_cat('Backup & Opslag', parent_id=it_id)
    diensten_id = odoo.get_or_create_cat('Diensten')
    bkp_svc_id  = odoo.get_or_create_cat('Backup', parent_id=diensten_id)

    nas_img = svg_nas()
    svc_img = svg_backup_service()

    print("\n── Hardware ─────────────────────────────────────────────────────")
    for p in HARDWARE:
        odoo.upsert_product(p['ref'], {
            'name':             p['name'],
            'categ_id':         bkp_hw_id,
            'list_price':       p['list_price'],
            'standard_price':   p['standard_price'],
            'type':             'consu',
            'description_sale': p['description_sale'],
            'x_status':         'beschikbaar',
        }, placeholder_b64=nas_img)

    print("\n── Diensten ─────────────────────────────────────────────────────")
    for s in DIENSTEN:
        odoo.upsert_product(s['ref'], {
            'name':             s['name'],
            'categ_id':         bkp_svc_id,
            'list_price':       s['list_price'],
            'type':             'service',
            'invoice_policy':   'order',
            'description_sale': s['description_sale'],
            'x_status':         'beschikbaar',
        }, placeholder_b64=svc_img)

    print("\n── Klaar ─────────────────────────────────────────────────────────")
    print("5 producten aangemaakt: 1 hardware (IT-hardware > Backup & Opslag)")
    print("                        4 diensten (Diensten > Backup)")


if __name__ == '__main__':
    main()
