# Hoe gebruik ik Odoo? — Working Local

## Wat is dit?

Odoo is het centrale beheersysteem voor Working Local. Het beheert werkplekken, reservaties en lidmaatschappen. Er is ook een publieke boekingspagina voor bezoekers en een koppeling met de digitale schermen (Xibo).

---

## Hoe deploy ik Odoo op de VPS?

### Stap 1 — Deployen via Coolify

1. Ga naar **https://coolify.workinglocal.be**
2. Klik **New Resource → Docker Compose**
3. Plak de inhoud van `docker-compose.yml` uit deze repo
4. Stel de environment variables in:

   | Variabele | Waarde |
   |---|---|
   | `ODOO_DB_USER` | `odoo` |
   | `ODOO_DB_PASSWORD` | gegenereerd wachtwoord |

5. Domein instellen: `https://odoo.workinglocal.be` → poort `8069`
6. Klik **Deploy**

### Stap 2 — Eerste database aanmaken

1. Ga naar **https://odoo.workinglocal.be/web/database/manager**
2. Klik **Create Database**
3. Vul in:
   - **Master Password:** (staat in Coolify environment variables)
   - **Database naam:** `workinglocal`
   - **Taal:** Nederlands
   - **Land:** Belgium
4. Klik **Create** — dit duurt 1-2 minuten

### Stap 3 — Custom addon installeren

1. Ga naar **https://odoo.workinglocal.be/web?debug=1** (activeer developer mode)
2. Klik op het raster-icoon → **Apps**
3. Klik **Update Apps List** (rechtsboven)
4. Zoek op `coworking`
5. Klik **Installeren** bij **Working Local — Coworking Reservaties**

Na installatie verschijnt het **Coworking** menu in de navigatie.

---

## Hoe voeg ik een werkplek toe?

1. Ga naar **Coworking → Werkplekken**
2. Klik **Nieuw**
3. Vul in:
   - **Naam:** bv. "Stille zone bureau 1"
   - **Type:** desk / meeting room / phone booth
   - **Capaciteit:** aantal personen
   - **Voorzieningen:** wifi, scherm, printer, etc.
4. Klik **Opslaan**

---

## Hoe maak ik een reservatie?

### Via de admin interface

1. Ga naar **Coworking → Reservaties → Nieuw**
2. Kies de werkplek, het lid, datum en tijdslot
3. Vul de bijdrage in (vrij bedrag)
4. Klik **Opslaan**

### Via de publieke website

Bezoekers kunnen zelf reserveren via:
**https://odoo.workinglocal.be/werkplekken**

---

## Hoe beheer ik lidmaatschappen?

1. Ga naar **Coworking → Lidmaatschappen → Nieuw**
2. Kies het lid (contactpersoon)
3. Stel het lidmaatschapstype en de geldigheidsperiode in
4. Klik **Opslaan**

---

## Hoe update ik de custom addon?

Als er wijzigingen zijn in de addon code op GitHub:

1. Herstart de `odoo-addons` container in Coolify — die kloont automatisch de laatste versie
2. Herstart de `odoo` container
3. Log in en ga naar **Apps → Geïnstalleerde apps → Working Local Coworking → Upgraden**

---

## Hoe koppel ik Odoo aan Xibo (digitale schermen)?

De API endpoint is beschikbaar op:

```
https://odoo.workinglocal.be/api/workspaces/availability
```

In Xibo:
1. **DataSets → + Add DataSet → Remote DataSet**
2. URL: bovenstaand adres
3. Refresh: 60 seconden
4. Data path: `workspaces`

Zie [xibo-integration.md](xibo-integration.md) voor de volledige configuratie.

---

## Problemen oplossen

| Probleem | Oplossing |
|---|---|
| Addon niet zichtbaar | Herstart `odoo-addons` container, dan `odoo` container |
| Database aanmaken mislukt | Controleer of `odoo-db` container draait |
| Installatie mislukt met XML fout | Controleer de Odoo logs: Coolify → Service → Logs |
| API geeft lege lijst | Controleer of er werkplekken aangemaakt zijn in Odoo |
| Trage login | Eerste request na containerstart is altijd traag (Odoo opwarmen) |
