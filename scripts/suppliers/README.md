# Leveranciersimportscripts

Eén script per leverancier. Alle scripts delen `odoo_client.py` voor de Odoo XML-RPC verbinding, scraping-hulpfuncties en SVG-placeholders.

## Structuur

```
scripts/suppliers/
├── odoo_client.py      ← gedeelde client (importeer dit in elk leveranciersscript)
├── pv_consulting.py    ← PV Consulting (pv-consulting.com) — webscraping
├── leverancier_2.py    ← toekomstig — API-gebaseerd
└── leverancier_3.py    ← toekomstig — API-gebaseerd
```

## Gebruik

```bash
# Kopieer naar VPS en voer uit:
scp scripts/suppliers/*.py root@23.94.220.181:/tmp/
ssh root@23.94.220.181 "cd /tmp && python3 pv_consulting.py"
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
