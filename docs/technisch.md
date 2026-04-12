# Technische documentatie — Odoo Working Local

## Concept

Odoo 19 Community Edition draait als Docker container op de VPS. Twee custom addons voegen Working Local-specifieke functionaliteit toe:

- `coworking_reservation` — werkplekbeheer, reservaties, lidmaatschappen, publieke boekingswebsite
- `workinglocal_theme` — huisstijl voor backend én webshop

---

## Architectuur

```
Internet
    │
    ▼
Traefik (Coolify) → odoo.workinglocal.be
    │
    ▼
odoo container (Odoo 19 CE)
    │   ├── /web              → Gebruikersinterface (backend)
    │   ├── /shop             → Webshop (eCommerce)
    │   ├── /werkplekken      → Publieke werkplekpagina
    │   └── /api/workspaces   → JSON API voor Xibo integratie
    │
    ▼
odoo-db container (PostgreSQL 15)
    │
    └── database: workinglocal

Volumes:
    odoo-data     → /var/lib/odoo   (filestore, uploads)
    odoo-addons   → /mnt/extra-addons (custom addons, bijgewerkt via scp)
```

## docker-compose.yml (vereenvoudigd)

```yaml
services:
  odoo:
    image: odoo:19
    volumes:
      - odoo-data:/var/lib/odoo
      - odoo-addons:/mnt/extra-addons
      - ./config/odoo.conf:/etc/odoo/odoo.conf:ro
    depends_on:
      - odoo-db

  odoo-db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=workinglocal
      - POSTGRES_USER=${ODOO_DB_USER}
      - POSTGRES_PASSWORD=${ODOO_DB_PASSWORD}
```

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

---

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

### Odoo 19 — bekende beperkingen

Odoo 19 heeft strikte XML-validatieregels, reeds gefixte problemen:
- Geen `active_id` in publieke contexten (portal/website)
- Geen `<group>` in search views
- Geen niet-opgeslagen computed fields in domain filters
- `is_in_trial` filter verwijderd (non-stored computed veld)

---

## Addon: workinglocal_theme

### Doel

Overschrijft de Odoo-standaardstijl met de Working Local huisstijl:

| Kleur | Hex | Gebruik |
|---|---|---|
| Marineblauw | `#1A2E5A` | Achtergrond knoppen, primaire elementen |
| Geel | `#F5B800` | Accenten, hover, highlights |

### Bestanden

```
addons/workinglocal_theme/
├── __manifest__.py
├── __init__.py
├── static/src/scss/
│   ├── variables.scss          ← kleurvariabelen (prepend in assets_backend)
│   └── workinglocal_theme.scss ← alle CSS-overschrijvingen
```

### variables.scss

Ingeladen via `('prepend', ...)` zodat de variabelen beschikbaar zijn vóór Odoo's eigen SCSS compileert:

```scss
$primary:   #1A2E5A;
$secondary: #F5B800;
```

### workinglocal_theme.scss — overzicht

| Sectie | Wat het doet |
|---|---|
| `.o_main_navbar` | Gele border-bottom, app-naam in geel |
| `.btn-primary` | Navy achtergrond, geel bij hover |
| `a:not(.btn)` | Links in navy, hover geel |
| `.o_statusbar_status` | Statusbalk-knoppen in geel |
| `.o_priority .fa-star` | Sterren in geel |
| `.progress-bar` | Voortgangsbalk in navy |
| `.oe_website_sale .oe_product_image img` | `object-fit: contain` — producten niet bijgesneden |
| `::after` pseudo-elementen | Witte overlay op shop-thumbnails verwijderd |
| `.o_field_image img` | Backend product-afbeeldingen ook contain |

### Productafbeeldingen — CSS-fix

**Probleem:** Odoo 19's `website_sale` gebruikt `%o-wsale-shop-thumb { object-fit: cover }` als basis voor alle shop-thumbnails. Hierdoor worden niet-vierkante productfoto's bijgesneden en lijken ze "ingezoomd".

**Oplossing** in `workinglocal_theme.scss`:

```scss
.oe_website_sale .oe_product_image img,
.oe_website_sale .oe_product_image_link img,
.oe_product .oe_product_image img {
    object-fit: contain !important;
    object-position: center !important;
    background-color: #f8f8f8 !important;
}

// Witte transparante overlay verwijderen
.oe_product_image_link::after,
.oe_product_image::after,
.o_product_detail_img_wrapper::after {
    display: none !important;
    background: none !important;
}
```

### Theme assets recompileren

Na elke SCSS-aanpassing:

```bash
# 1. Bestand kopiëren naar volume op de VPS:
scp addons/workinglocal_theme/static/src/scss/workinglocal_theme.scss \
    root@23.94.220.181:/var/lib/docker/volumes/wmsa9jotez65ynj0xsb748rq_odoo-addons/_data/workinglocal_theme/static/src/scss/

# 2. Assets recompileren (herstart Odoo automatisch via --stop-after-init):
docker exec odoo-[container-id] odoo \
    -u workinglocal_theme -d workinglocal \
    --stop-after-init \
    --db_host=odoo-db --db_user=odoo --db_password='[wachtwoord]' \
    --no-http

# 3. Container opnieuw starten:
docker restart odoo-[container-id]
```

---

## Productcatalogus — technische details

### XML-RPC verbindingspatroon

Alle import-scripts gebruiken Odoo's standaard XML-RPC API (geen directe DB-toegang):

```python
import xmlrpc.client, base64

url      = 'https://odoo.workinglocal.be'
db       = 'workinglocal'
username = 'info@workinglocal.be'
password = '[wachtwoord]'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid    = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def exe(model, method, args=None, kwargs=None):
    return models.execute_kw(db, uid, password, model, method,
                             args or [], kwargs or {})
```

> **Waarom XML-RPC en niet binnen de container?** De Odoo-container verbindt met een externe PostgreSQL-container. Er is geen lokale Unix socket (`/var/run/postgresql/...`). Scripts die direct Odoo Python API-aanroepen (via `odoo.api.Environment`) falen daardoor met `psycopg2.OperationalError`. XML-RPC via het HTTP-endpoint werkt altijd.

### Productafbeeldingen ophalen van pv-consulting.com

pv-consulting.com blokkeert Python's `urllib` met HTTP 403. `curl` werkt wel:

```python
import subprocess, base64

def download_image(url):
    result = subprocess.run(
        ["curl", "-sf", "--max-time", "20", url],
        capture_output=True
    )
    if result.returncode != 0 or not result.stdout:
        return None
    return base64.b64encode(result.stdout).decode('utf-8')
```

Afbeeldingen worden als base64-string opgeslagen in `image_1920` (hoofdafbeelding) of in `product.image` records (extra galerij-afbeeldingen).

### product.image model (extra galerij)

Het model `product.image` bestaat alleen als de **eCommerce-module** geactiveerd is. Velden:

| Veld | Type | Beschrijving |
|---|---|---|
| `product_tmpl_id` | Many2one | Koppeling aan `product.template` |
| `image_1920` | Binary (base64) | Afbeeldingsdata |
| `name` | Char | Optionele naam/label |

```python
exe('product.image', 'create', [{
    'product_tmpl_id': template_id,
    'image_1920': base64_string,
    'name': 'Zijkant',
}])
```

### Scraping van extra productafbeeldingen

Extra afbeeldingen worden gescraped van `https://pv-consulting.com/products/[product-slug].html`:

```python
import re, subprocess

def scrape_images(page_url):
    html = subprocess.run(
        ["curl", "-sf", "--max-time", "20", page_url],
        capture_output=True
    ).stdout.decode('utf-8', errors='replace')
    filenames = re.findall(r'<img[^>]+src=["\']\.\.\/images\/([^"\']+)["\']', html)
    # Sla UI-afbeeldingen over:
    skip = {"pvconsultingMainLogo.png", "pvconsultingInvertedColor.png",
            "1946488.png", "1451574.png", "1170678.png", "2590818.png",
            "Digital_Inline_Green.png"}
    return [f for f in filenames if f not in skip]
```

Resultaat: ~292 extra afbeeldingen over 49 producten.

### Placeholder SVG-afbeeldingen voor diensten

Service-producten (Wifi, Focus, AV, Logistiek, Verhuur) hebben geen productfoto's. Ze krijgen programmatisch gegenereerde SVG-placeholders in de huisstijl:

```python
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="#1A2E5A"/>
  {icon_shapes}
  <text x="200" y="360" font-family="Arial,sans-serif" font-size="22"
        font-weight="bold" text-anchor="middle" fill="#F5B800">{label}</text>
</svg>'''
b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
exe('product.template', 'write', [[product_id], {'image_1920': b64}])
```

Geïmplementeerde iconen: WiFi-antenne, bullseye (Focus), camera (AV & Studio), vrachtwagen (Logistiek), sleutel (Verhuur).

---

## Persistentie

| Volume | Inhoud |
|---|---|
| `odoo-data` | Filestore (bijlagen, uploads, PDF-rapporten) |
| `odoo-db` | PostgreSQL database `workinglocal` |
| `odoo-addons` | Custom addons — bij elke update handmatig gekopieerd via `scp` |

> De addons worden **niet** automatisch bij elke Coolify-redeploy ververst vanuit git. Ze worden beheerd via handmatige `scp`. De `odoo-addons` init-container (alpine/git) uit de oorspronkelijke setup is vervangen door dit workflow.

## Odoo database manager

Bereikbaar via: `https://odoo.workinglocal.be/web/database/manager`

Vereist het master password uit de Coolify environment variables.
