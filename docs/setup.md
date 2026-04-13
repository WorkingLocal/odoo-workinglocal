# Odoo CE — Working Local Setup

## Overzicht

Odoo CE draait als Docker container op VPS-WORKINGLOCAL, beheerd via Coolify.

- **URL:** `odoo.workinglocal.be`
- **Database:** `workinglocal` (PostgreSQL 15)
- **Custom addons:** `coworking_reservation`, `workinglocal_theme`

---

## Deployment via Coolify

1. In Coolify: **New Resource → Docker Compose**
2. Plak de inhoud van `docker-compose.yml`
3. Stel het domein in: `https://odoo.workinglocal.be`
4. Voeg environment variabelen toe (zie `.env.template`):
   - `ODOO_DB_USER`
   - `ODOO_DB_PASSWORD`
5. Deploy

## Eerste setup na deploy

1. Ga naar `https://odoo.workinglocal.be/web/database/manager`
2. Maak een nieuwe database aan (naam: `workinglocal`)
3. Installeer via **Apps → Lijst bijwerken** de volgende modules:
   - `Website`
   - `eCommerce` (webshop — vereist voor productafbeeldingen via `product.image`)
   - `Invoicing` (Facturatie)
   - `Portal`
   - `coworking_reservation`
   - `workinglocal_theme`

> **Belangrijk:** installeer de eCommerce module vóór het importeren van productafbeeldingen. Het model `product.image` (voor meerdere foto's per product) bestaat niet zonder deze module.

---

## Addons bijwerken na een git push

De addons staan **in een Docker volume**, niet als bindmount. Na een git push in de repo moet je de bestanden handmatig kopiëren naar het volume:

```bash
# Geef het volume-pad op via:
docker inspect odoo-[container-id] --format '{{json .Mounts}}'
# Voorbeeld volumepad: /var/lib/docker/volumes/wmsa9jotez65ynj0xsb748rq_odoo-addons/_data

# Kopieer enkel de gewijzigde addon:
scp -r addons/workinglocal_theme/ root@23.94.220.181:/var/lib/docker/volumes/wmsa9jotez65ynj0xsb748rq_odoo-addons/_data/

# Of een enkel bestand:
scp addons/workinglocal_theme/static/src/scss/workinglocal_theme.scss \
    root@23.94.220.181:/var/lib/docker/volumes/wmsa9jotez65ynj0xsb748rq_odoo-addons/_data/workinglocal_theme/static/src/scss/
```

### Theme recompileren na SCSS-wijziging

Na elke aanpassing aan `workinglocal_theme.scss` of `variables.scss` moet het theme opnieuw worden gecompileerd:

```bash
# 1. SCSS kopiëren naar volume (zie hierboven)

# 2. Assets recompileren (--stop-after-init zorgt dat Odoo nadien afsluit):
docker exec odoo-[container-id] odoo \
    -u workinglocal_theme \
    -d workinglocal \
    --stop-after-init \
    --db_host=odoo-db \
    --db_user=odoo \
    --db_password='[ODOO_DB_PASSWORD]' \
    --no-http

# 3. Odoo-container herstarten:
docker restart odoo-[container-id]
```

---

## Productcatalogus importeren (verse installatie)

De volledige productcatalogus (66 producten, 7 categoriegroepen, 4 attributen) wordt geïmporteerd via een Python XML-RPC script.

### Vereisten

- Python 3 op de lokale machine of de VPS
- Odoo online bereikbaar op `https://odoo.workinglocal.be`
- eCommerce module geactiveerd (voor `product.image`)

### Stap 1 t/m 5 — Volledig importscript

Alles in één script: categorieën, attributen, producten, omschrijvingen (gescrapet van pv-consulting.com), aankoopprijzen (incl. → excl. 21% BTW) en afbeeldingen.

```bash
# Script staat in de repo: scripts/odoo_import_full.py
# Kopieer naar VPS en voer uit:
scp scripts/odoo_import_full.py root@23.94.220.181:/tmp/
ssh root@23.94.220.181 "python3 /tmp/odoo_import_full.py"
```

Het script is **idempotent**: producten die al bestaan (op `default_code`) worden overgeslagen. Alleen nieuw toegevoegde producten worden aangemaakt met afbeeldingen en omschrijvingen.

**Nieuw product toevoegen:**
1. Voeg een `make_product(...)` aanroep toe onderaan de juiste sectie
2. Geef de `slug` mee van de pv-consulting productpagina
3. Script haalt automatisch naam, omschrijvingen, aankoopprijs en foto's op

---

### Stap 1 — Categorieën en attributen (legacy, vervangen door bovenstaand script)

```bash
# Script staat in: /tmp/odoo_categories.py (of zie sectie 6 in CLAUDE.md)
python3 /tmp/odoo_categories.py
```

Maakt aan:
- 7 hoofdcategorieën: Circulaire werkplek, Beeldschermen, Informatieschermen, IT-hardware, Accessoires, Meubelen, Diensten
- 21 subcategorieën (Bureau's, Tafels, Stoelen, 22", 27", enz.)
- 4 attributen: Merk, Schermdiagonaal, Resolutie, Staat

### Stap 2 — Producten importeren

```bash
# Volledig import script (66 producten):
python3 /tmp/odoo_import_full.py
```

Het script maakt elk product aan met:
- `default_code` (SKU zoals `MON-27-01`, `DESK-02`, `SRV-WIFI-01`, enz.)
- Correcte categorie
- Prijs, type (`product` of `service`), omschrijving
- Custom veld `x_status` (beschikbaar / uitverkocht / nieuw)

### Stap 3 — Hoofdafbeeldingen uploaden

Afbeeldingen worden gedownload van `https://pv-consulting.com/images/` via `curl` (pv-consulting.com blokkeert Python urllib met een 403, curl werkt wel) en als base64 opgeslagen in het veld `image_1920` van `product.template`.

```bash
python3 /tmp/odoo_images.py
```

49 producten krijgen een of meerdere hoofdafbeeldingen.

### Stap 4 — Extra productafbeeldingen (galerij)

Aanvullende afbeeldingen worden gescraped van de respectievelijke productpagina's op pv-consulting.com en opgeslagen als `product.image` records (linked aan `product_tmpl_id`).

```bash
python3 /tmp/odoo_scrape_images.py
```

~292 extra afbeeldingen verdeeld over 49 producten.

### Stap 5 — Placeholder afbeeldingen voor diensten

Service-producten (Wifi, Focus, AV & Studio, Logistiek, Verhuur) hebben geen foto's. Ze krijgen SVG-placeholders in de huisstijl (marineblauw + geel):

```bash
python3 /tmp/create_placeholders.py
```

18 dienst-producten krijgen een herkenbare placeholder (WiFi-icoon, bullseye, camera, vrachtwagen, sleutel).

---

## DNS (Cloudflare)

```
Type:  A
Name:  odoo
Value: 23.94.220.181
TTL:   Auto
Proxy: DNS only (grijs wolkje — NIET proxied)
```

Odoo vereist directe verbinding voor Let's Encrypt. Zet de Cloudflare proxy UIT (grijs wolkje).

---

## Custom addons

### coworking_reservation

Zie [technisch.md](technisch.md) voor volledige documentatie.

Biedt:
- **6 werkplektypes:** hot desk, vaste plek, vergaderzaal, focus zone, event, hybride meeting
- **Online reservaties** via de Odoo website (`/werkplekken`)
- **Klantenzone** voor reservatieopvolging (`/mijn/reservaties`)
- **Vrije bijdrage** facturatie model
- **Gratis proefperiode** voor nieuwe leden
- **Xibo integratie** via JSON endpoint (`/api/workspaces/availability`)

### workinglocal_theme

Huisstijl-addon voor de Odoo backend én webshop. Zie [technisch.md](technisch.md#addon-workinglocal_theme).

Bevat:
- SCSS-variabelen (marineblauw `#1A2E5A`, geel `#F5B800`)
- Backend huisstijl (navbar, knoppen, links, statusbalk)
- Webshop product-imagecorrectie (`object-fit: contain`)
- Verwijdering witte overlay op shop-thumbnails

---

## Xibo integratie

Zie [xibo-integration.md](xibo-integration.md) voor de koppeling met Xibo CMS.
