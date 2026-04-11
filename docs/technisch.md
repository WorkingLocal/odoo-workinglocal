# Technische documentatie — Odoo Working Local

## Concept

Odoo 19 Community Edition draait als Docker container op de VPS. De custom `coworking_reservation` addon voegt coworking-specifieke functionaliteit toe: werkplekbeheer, reservaties, lidmaatschappen en een publieke boekingswebsite.

## Architectuur

```
Internet
    │
    ▼
Traefik → odoo.workinglocal.be
    │
    ▼
odoo container (Odoo 19 CE)
    │   ├── /web              → Gebruikersinterface
    │   ├── /werkplekken      → Publieke werkplekpagina
    │   └── /api/workspaces   → JSON API voor Xibo integratie
    │
    ▼
odoo-db container (PostgreSQL 15)
    │
    └── database: workinglocal

odoo-addons container (alpine/git)
    → kloont addons van GitHub bij elke deploy
    → kopieert naar /mnt/extra-addons volume
```

## docker-compose.yml

```yaml
services:
  odoo:
    image: odoo:19
    ports:
      - "8069:8069"
    volumes:
      - odoo-data:/var/lib/odoo
      - odoo-addons:/mnt/extra-addons
      - ./config/odoo.conf:/etc/odoo/odoo.conf:ro

  odoo-db:
    image: postgres:15-alpine

  odoo-addons:
    image: alpine/git
    restart: "no"              # draait eenmalig bij deploy
    entrypoint: >
      sh -c "git clone ... && cp -r /tmp/repo/addons/* /addons/"
```

## Addon: coworking_reservation

### Modellen

| Model | Beschrijving |
|---|---|
| `coworking.workspace` | Werkplek (naam, type, capaciteit, amenities) |
| `coworking.reservation` | Reservatie (werkplek, lid, datum, tijdslot, bijdrage) |
| `coworking.membership` | Lidmaatschap (lid, type, geldigheid, gebruik) |
| `coworking.amenity` | Voorziening (wifi, printer, etc.) |

### Views

| View | Pad | Beschrijving |
|---|---|---|
| Backend werkplekken | `/web` → Coworking menu | Beheer van werkplekken en reservaties |
| Publieke werkplekpagina | `/werkplekken` | Overzicht voor bezoekers |
| Publiek boekingsformulier | `/werkplekken/<id>/reserveer` | Reservatie met vrije bijdrage |
| Portaal reservaties | `/mijn/reservaties` | Overzicht voor ingelogde leden |

### API endpoint

```
GET /api/workspaces/availability
```

Respons (JSON):
```json
{
  "workspaces": [
    {
      "id": 1,
      "name": "Stille zone",
      "type": "desk",
      "available": true,
      "capacity": 4,
      "is_occupied": false
    }
  ]
}
```

Gebruikt door Xibo CMS voor digitale schermen.

## config/odoo.conf

```ini
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
db_host = odoo-db
db_port = 5432
db_user = ${ODOO_DB_USER}
db_password = ${ODOO_DB_PASSWORD}
```

## Environment variables

| Variabele | Beschrijving |
|---|---|
| `ODOO_DB_USER` | PostgreSQL gebruikersnaam |
| `ODOO_DB_PASSWORD` | PostgreSQL wachtwoord |

## Addon installatie (Odoo 19 specifiek)

Odoo 19 heeft strikte XML-validatieregels:
- Geen `active_id` in publieke contexten
- Geen `<group>` in search views
- Geen niet-opgeslagen computed fields in domain filters
- Calendar views vereisen specifieke configuratie

Alle views zijn gevalideerd voor Odoo 19.

## Persistentie

| Volume | Inhoud |
|---|---|
| `odoo-data` | Filestore (bijlagen, uploads, rapporten) |
| `odoo-db` | PostgreSQL database |
| `odoo-addons` | Custom addons (worden bij elke deploy opnieuw gekloned) |

## Odoo database manager

Bereikbaar via: `https://odoo.workinglocal.be/web/database/manager`

Vereist het master password uit de Coolify environment variables.
