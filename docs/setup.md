# Odoo CE — Working Local Setup

## Overzicht

Odoo CE draait als Docker container op VPS-WORKINGLOCAL, beheerd via Coolify.

- **URL:** `odoo.workinglocal.be`
- **Database:** PostgreSQL 15
- **Custom addon:** `coworking_reservation`

## Deployment via Coolify

1. In Coolify: **New Resource → Docker Compose**
2. Plak de inhoud van `docker-compose.yml`
3. Stel het domein in: `https://odoo.workinglocal.be`
4. Voeg environment variabelen toe (zie `.env.template`):
   - `ODOO_DB_USER`
   - `ODOO_DB_PASSWORD`
5. Deploy

## Eerste setup

Na de eerste deploy:
1. Ga naar `https://odoo.workinglocal.be/web/database/manager`
2. Maak een nieuwe database aan (gebruik de master password uit `.env`)
3. Installeer de volgende modules:
   - `Website`
   - `Invoicing` (Facturatie)
   - `Portal`
   - `coworking_reservation` (onze custom addon — staat in `/mnt/extra-addons`)

## Custom addon — coworking_reservation

De addon bevindt zich in `addons/coworking_reservation/` en biedt:

- **6 werkplektypes:** hot desk, vaste plek, vergaderzaal, focus zone, event, hybride meeting
- **Online reservaties** via de Odoo website (`/werkplekken`)
- **Klantenzone** voor reservatieopvolging (`/mijn/reservaties`)
- **Vrije bijdrage** facturatie model
- **Gratis proefperiode** voor nieuwe leden
- **Xibo integratie** via JSON endpoint (`/api/workspaces/availability`)

## DNS (Cloudflare)

```
Type:  A
Name:  odoo
Value: 23.94.220.181
TTL:   Auto
Proxy: DNS only (grijs wolkje)
```

## Xibo integratie

Zie [xibo-integration.md](xibo-integration.md) voor de koppeling met Xibo CMS.
