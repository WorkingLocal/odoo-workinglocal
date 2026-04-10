# Odoo — Working Local

Odoo 19 CE met een custom addon voor werkplekbeheer, online reservaties en digitale schermintegratie.

## Wat het doet

- **Werkplekbeheer** — 6 types: hot desk, vaste plek, vergaderzaal, focus zone, event, hybride meeting
- **Online reservaties** via de Odoo website (`/werkplekken`)
- **Klantenzone** voor reservatieopvolging (`/mijn/reservaties`)
- **Vrije bijdrage** facturatiemodel voor coworking leden
- **Gratis proefperiode** voor nieuwe leden
- **Xibo integratie** — live bezettingsdata via JSON endpoint (`/api/workspaces/availability`)

## Deployment

Draait op `odoo.workinglocal.be` via Coolify op VPS-WORKINGLOCAL.

### Vereisten

- Coolify op de VPS (zie [vps-workinglocal](https://github.com/WorkingLocal/vps-workinglocal))
- DNS A-record: `odoo.workinglocal.be` → `23.94.220.181` (Cloudflare proxy UIT)

### Stappen

1. In Coolify: **New Resource → Docker Compose**
2. Plak de inhoud van `docker-compose.yml`
3. Domein instellen: `https://odoo.workinglocal.be`
4. Environment variabelen toevoegen:
   - `ODOO_DB_USER`
   - `ODOO_DB_PASSWORD`
5. Deploy

De `odoo-addons` container kloont automatisch de addon van GitHub naar het gedeelde volume.

### Eerste setup na deploy

1. Ga naar `https://odoo.workinglocal.be/web/database/manager`
2. Maak een nieuwe database aan
3. Installeer via **Apps → Lijst bijwerken** de module `Working Local — Coworking Reservaties`

## Stack

| Onderdeel | Technologie |
|---|---|
| Applicatie | Odoo 19 CE |
| Database | PostgreSQL 15 |
| Addon sync | alpine/git (eenmalige container via Docker volume) |
| Reverse proxy | Caddy (via Coolify) |

## Documentatie

- [docs/setup.md](docs/setup.md) — volledige deployment handleiding
- [docs/xibo-integration.md](docs/xibo-integration.md) — Xibo CMS koppeling via JSON endpoint

## Gerelateerde repositories

| Repo | Inhoud |
|---|---|
| [vps-workinglocal](https://github.com/WorkingLocal/vps-workinglocal) | Server setup & infrastructuur |
| [signage-workinglocal](https://github.com/WorkingLocal/signage-workinglocal) | Xibo CMS voor digitale schermen |
| [focus-workinglocal](https://github.com/WorkingLocal/focus-workinglocal) | Focus Kiosk app |
| [metrics-workinglocal](https://github.com/WorkingLocal/metrics-workinglocal) | Netdata monitoring |
