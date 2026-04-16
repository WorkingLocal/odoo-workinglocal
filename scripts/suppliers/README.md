# Leveranciersimportscripts

Eén script per leverancier. Alle scripts delen `odoo_client.py` voor de Odoo XML-RPC verbinding, scraping-hulpfuncties en SVG-placeholders.

## Structuur

```
scripts/suppliers/
├── odoo_client.py      ← gedeelde client (importeer dit in elk leveranciersscript)
├── pv_consulting.py    ← PV Consulting (pv-consulting.com) — initiële import, webscraping
├── wimood.py           ← Wimood — initiële import (eenmalig, 380 producten aangemaakt)
├── wimood_sync.py      ← Wimood — nachtelijkse sync: prijzen, voorraad, nieuwe producten
└── leverancier_3.py    ← toekomstig
```

## Gebruik

```bash
# Kopieer naar VPS en voer uit:
scp scripts/suppliers/*.py root@23.94.220.181:/tmp/

# Initiële import (eenmalig):
ssh root@23.94.220.181 "cd /tmp && python3 pv_consulting.py"
ssh root@23.94.220.181 "cd /tmp && python3 wimood.py"

# Nachtelijkse sync (normaal via cron — zie n8n-workinglocal/README.md):
ssh root@23.94.220.181 "ODOO_PASSWORD=$(cat /root/.odoo_password) python3 /tmp/wimood_sync.py"
```

Elk script vraagt bij opstart om het Odoo-wachtwoord.

## Idempotentie

Alle scripts zijn idempotent: producten die al bestaan op `default_code` worden overgeslagen. Veilig om meerdere keren te draaien.

## Nieuw product toevoegen aan PV Consulting

1. Zoek de productpagina op pv-consulting.com
2. Kopieer de slug uit de URL (bv. `dell-27--p2723de-qhd-usb-c-hub-monitor.html`)
3. Voeg een `make_product()` aanroep toe in `pv_consulting.py`
4. Het script haalt automatisch omschrijving, aankoopprijs en foto's op

```python
make_product('MON-27-NEW',
    'Beeldscherm 27" — Nieuw model',
    '27"', 199,
    slug='nieuw-model-slug.html')
```

## Wimood — UniFi productlijn

Wimood levert producten via een XML-API. Authenticatie via `api_key` + `klantnummer` als queryparameter.

```
URL: https://wimoodshop.nl/api/index.php?api_key=...&klantnummer=11556
```

De XML bevat alle producten van Wimood. `wimood.py` filtert alleen:
- `brand = 'Ubiquiti'`
- `'UniFi'` aanwezig in de productnaam

Hiermee worden AirMAX, EdgeRouter, EdgeSwitch en andere Ubiquiti-lijnen automatisch uitgesloten.

**Prijsvelden (beide excl. BTW — B2B):**

| XML-veld | Odoo-veld        | Betekenis                   |
|----------|------------------|-----------------------------|
| `prijs`  | `standard_price` | Wimood inkoopprijs           |
| `msrp`   | `list_price`     | Aanbevolen verkoopprijs      |

**Categorieën** aangemaakt onder `Netwerk & WiFi`:
Access Points, Switches, Gateways, Beveiliging, Controllers, Accessoires

**Custom veld** `x_wimood_stock` op `product.template`:
Slaat de actuele Wimood-voorraad op. Aangemaakt automatisch bij eerste sync-run.

**Nachtelijkse sync** via `wimood_sync.py`:
- Werkt prijzen en `x_wimood_stock` bij voor alle 380 producten
- Maakt nieuwe producten aan die in de XML verschijnen
- POSt JSON-samenvatting naar n8n webhook (`/wimood-sync`)
- n8n verstuurt e-mailmelding als drempels overschreden worden

Zie **n8n-workinglocal/README.md** voor volledige setup-instructies (cron + n8n workflow importeren).

## Nieuw leveranciersscript aanmaken

1. Maak `leverancier_naam.py` aan in deze map
2. Importeer de gedeelde client bovenaan:
   ```python
   import sys, os
   sys.path.insert(0, os.path.dirname(__file__))
   from odoo_client import OdooClient, svg_placeholder, b64
   ```
3. Gebruik `OdooClient()` voor alle Odoo-operaties
4. Voeg de SKU-reeks toe aan `CLAUDE.md` sectie 10

## odoo_client.py — beschikbare functies

| Functie / klasse | Beschrijving |
|---|---|
| `OdooClient()` | Verbinding + authenticatie, herbruikbaar object |
| `odoo.get_or_create_cat(name, parent_id)` | Categorie opzoeken of aanmaken |
| `odoo.get_or_create_attribute(name, values)` | Attribuut + waarden opzoeken of aanmaken |
| `odoo.upsert_product(ref, vals, images, placeholder_b64)` | Product aanmaken als het nog niet bestaat |
| `odoo.search_read(model, domain, fields)` | XML-RPC search_read |
| `odoo.create(model, vals)` | XML-RPC create |
| `odoo.write(model, ids, vals)` | XML-RPC write |
| `scrape_pv_page(slug)` | Scrape pv-consulting productpagina → dict |
| `upload_images(odoo, tmpl_id, images)` | Upload afbeeldingen van pv-consulting CDN |
| `svg_placeholder(icon_key)` | Genereer base64 SVG-placeholder |
| `curl_bytes(url)` | HTTP GET via curl (werkt rond hotlink-bescherming) |
| `b64(data)` | bytes → base64 string |
