"""
Koppel UniFi Design Center URLs aan projecten.
Voer uit na installatie van workinglocal_interventions.

Gebruik:
    python scripts/setup_interventions.py
"""

from suppliers.odoo_client import OdooClient

odoo = OdooClient()

UNIFI_URLS = {
    3: 'https://design.ui.com/projects/ef1e07e5-f86d-475c-8489-7d017a7b5a9e',  # Werkplaats Walter
}

for project_id, url in UNIFI_URLS.items():
    odoo.write('project.project', [project_id], {'unifi_design_url': url})
    projects = odoo.search_read('project.project', [('id', '=', project_id)], ['name'])
    name = projects[0]['name'] if projects else f'id={project_id}'
    print(f"  OK {name}: UniFi Design Center URL ingesteld")
