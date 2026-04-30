# CLAUDE.md — Briefing voor Claude Code
## Project: workinglocal.be — Website herbouw + Odoo CE productcatalogus

> Dit document is de volledige instructiebasis voor Claude Code.
> Lees dit volledig voor je iets uitvoert.
> Vraag bevestiging bij elke destructieve actie.
> Werk altijd op **wordpress.workinglocal.be** (staging) — NOOIT op workinglocal.be (productie).

---

## 1. Infrastructuuroverzicht

```
workinglocal.be           → productiesite op Hostinger (NIET aanraken)
wordpress.workinglocal.be → staging WordPress op Coolify VPS
odoo.workinglocal.be      → Odoo Community Edition op Coolify VPS (leading systeem)

Coolify VPS
├── Docker container: WordPress (website/inhoud)
└── Docker container: Odoo CE (producten, diensten, webshop, CRM)
```

**Odoo CE is het leading systeem voor:**
- Producten en diensten (catalogus, prijzen, voorraad)
- Webshop (e-commerce module)
- CRM en offertes
- Facturatie

**WordPress is het leading systeem voor:**
- Websitecontent (dienstenpagina's, homepage)
- Elementor-opgebouwde pagina's

---

## 2. Verbinding maken

### SSH naar de VPS

```bash
ssh [VPS_USER]@[VPS_IP]

# WordPress container
docker ps | grep -i wordpress
docker exec -it [wp-container] bash
wp --info --allow-root

# Odoo container
docker ps | grep -i odoo
docker exec -it [odoo-container] bash
```

### Odoo XML-RPC verbinding (Python scripts)

```python
import xmlrpc.client

url      = 'https://odoo.workinglocal.be'
db       = 'workinglocal'   # enige database, lege 'odoo' db verwijderd 2026-04-25
username = 'info@workinglocal.be'
password = '[zie Vaultwarden: Odoo CE - odoo.workinglocal.be]'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid    = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def create(model, vals):
    return models.execute_kw(db, uid, password, model, 'create', [vals])

def search_read(model, domain, fields):
    return models.execute_kw(db, uid, password, model, 'search_read', [domain], {'fields': fields})
```

---

## 3. DEEL 1 — WordPress website herbouw

### Pagina's aanmaken of herbouwen:

| # | Pagina | Slug | Actie |
|---|--------|------|-------|
| 1 | Homepage | / | Elementor-inhoud vervangen |
| 2 | Werkplekinrichting | /werkplekinrichting | Nieuw aanmaken |
| 3 | Wifi-installaties | /wifi-installaties | Nieuw aanmaken |
| 4 | Cloudplatform | /cloudplatform | Nieuw aanmaken |
| 5 | Hybride meeting-sets | /meeting-sets | Nieuw aanmaken |
| 6 | Focustraject | /focustraject | Nieuw aanmaken |
| 7 | Webinar & Livestream | /webinar-livestream | Nieuw aanmaken |

### Uitvoeringsplan:

```bash
alias wpcli='docker exec -it [wp-container] wp --allow-root --path=/var/www/html'

# FASE 1 — Audit
wpcli post list --post_type=page --fields=ID,post_title,post_name,post_status
wpcli option get page_on_front
wpcli theme list --status=active

# FASE 2 — Child theme
THEMA=$(wpcli theme list --status=active --field=name | head -1)
mkdir -p /var/www/html/wp-content/themes/${THEMA}-child
# Maak style.css en functions.php aan (zie sectie 4)
wpcli theme activate ${THEMA}-child

# FASE 3 — Pagina's via wpcli eval-file
# FASE 4 — Cache
wpcli elementor flush-css && wpcli cache flush

# FASE 5 — Navigatiemenu bijwerken
wpcli menu list
```

### Child theme style.css:

```css
/*
 Theme Name: [Thema] Child
 Template:   [thema-naam]
 Version:    1.0
*/
:root {
  --wl-navy:       #1A2E5A;
  --wl-yellow:     #F5B800;
  --wl-light-blue: #EEF4FB;
  --wl-footer:     #151E35;
}
.wl-badge-green {
  background: #EAF4EB; border: 1.5px solid #4CAF50;
  border-radius: 20px; color: #2E7D32;
  font-size: 11px; font-weight: 700; padding: 4px 14px;
  display: inline-flex; align-items: center; gap: 6px;
}
.wl-badge-blue {
  background: #F0F4FF; border: 1.5px solid #5B7BE5;
  border-radius: 20px; color: #2A3FA0;
  font-size: 11px; font-weight: 700; padding: 4px 14px;
  display: inline-flex; align-items: center; gap: 6px;
}
```

### Child theme functions.php:

```php
<?php
add_action('wp_enqueue_scripts', function() {
    wp_enqueue_style('parent-style', get_template_directory_uri() . '/style.css');
    wp_enqueue_style('child-style', get_stylesheet_directory_uri() . '/style.css', ['parent-style']);
});
```

---

## 4. Pagina-inhoud (Elementor, copy-paste klaar)

### Homepage

| Sectie | Tekst |
|--------|-------|
| Hero boventitel | COWORKING MET EEN SOCIALE MISSIE |
| Hero hoofdtitel | Laagdrempelige coworkingplekken laten groeien en verbinden |
| Hero knop 1 | Onze diensten » |
| Hero knop 2 | Ken jij een plek? — Tip ons |
| Diensten label | DIENSTEN DIE WIJ AANBIEDEN |
| Diensten titel | Onze diensten |
| Dienst 1 | Werkplekinrichting — Ergonomische werkplekken vanaf €249 — refurbished meubilair, monitoren en hardware. |
| Dienst 2 | Wifi-installaties — 100+ professionele installaties als gecertificeerde Ubiquiti netwerktechnieker. |
| Dienst 3 | Cloudplatform — Reservaties, ledenbeheer en schermbeheer op afstand — gebouwd op Odoo Community Edition. |
| Dienst 4 | Hybride meeting-sets — Plug-and-play audio en video voor vergaderruimtes, compatibel met elke laptop. |
| Dienst 5 | Focustraject — GTD, groeps-Pomodoro's en RescueTime — voor ritme, focus en community. |
| Dienst 6 | Webinar & Livestream — Compacte setups voor online workshops en hybride events, gebaseerd op OBS. |
| Over WL label | WAAROM VOOR ONS KIEZEN |
| Over WL titel | Over Working Local |
| Over WL tekst | Working Local ondersteunt laagdrempelige coworkingplaatsen met een sociale of maatschappelijke missie. We helpen hen groeien, professionaliseren en hun werking uitbreiden met concrete, betaalbare en duurzame oplossingen. Alles wat we bouwen blijft eenvoudig, overdraagbaar en onderhoudsarm. |
| Checklist label | WAT WE VOOR U DOEN |
| Checklist titel | Buurtplekken die écht werken |
| Checklist 1 | Betaalbare werkplekinrichting voor kleine budgetten |
| Checklist 2 | Stabiele en professionele wifi voor elke coworkingplek |
| Checklist 3 | Eenvoudige reservatie- en administratietools |
| Checklist 4 | Professionele vergaderruimtes zonder hoge kosten |
| Checklist 5 | Focustrajecten die community en ritme opbouwen |
| Checklist 6 | Zelfstandig verder groeien na onze begeleiding |
| CTA titel | Ken jij een plek die dit verdient? |
| CTA tekst | We zijn actief op zoek naar laagdrempelige locaties met een sociale missie. Stuur ons een tip — dan nemen wij contact op. |
| CTA knop | Stel een plek voor » |

### Werkplekinrichting

| Sectie | Tekst |
|--------|-------|
| Badge (groen) | Circulaire aanpak — refurbished meubilair & apparatuur |
| Titel | Professionele werkplekken, eerlijk voor mens en planeet |
| Intro | Working Local richt werkplekken in met refurbished kantoormeubilair, hardware en audiovisuele apparatuur. Zo bieden we betaalbare, professionele werkplekken aan buurtplekken en sociale coworkings — zonder afval, zonder buitensporige kosten, met maximale waarde. |
| Groen blok | Waarom refurbished? Kantoormeubilair en hardware worden na gemiddeld 3 tot 5 jaar afgedankt door grote bedrijven, vaak in perfecte staat. Working Local geeft deze spullen een tweede leven bij coworkingplekken met een sociale missie — goed voor het budget, goed voor de planeet. |
| Kaart 1 | Refurbished bureau & stoel — Ergonomisch kantoormeubilair van A-merken, gereinigd en hersteld. |
| Kaart 2 | Refurbished monitoren — Single of dual monitor met verstelbare monitorarm, 24" of groter. |
| Kaart 3 | Refurbished hardware & AV — Laptops, webcams, headsets en speakers, gecertificeerd refurbished. |
| Voordelen | Volledig uitgerust vanaf €249 / Tot 70% goedkoper dan nieuw / A-merken kwaliteit / CO₂-voetafdruk verlaagd / Levering en installatie inbegrepen / Aanpasbaar aan budget |
| Voor wie | Buurtplekken / Vrijwilligerswerkingen / Sociale organisaties / Coworkings met missie |
| Prijs | vanaf €249 excl. btw per werkplek |
| CTA | Interesse of vragen? → Contacteer ons » |

### Wifi-installaties

| Sectie | Tekst |
|--------|-------|
| Titel | Stabiel, snel en schaalbaar netwerk voor elke coworkingplek |
| Intro | Als gecertificeerde Ubiquiti netwerktechnieker hebben we de voorbije 5 jaar meer dan 100 professionele wifi-installaties gerealiseerd. We bouwen netwerken die gewoon werken — voor elke gebruiker, op elk moment, zonder gedoe. |
| Kaart 1 | Ubiquiti UniFi wifi — Access points op strategische plaatsen voor volledige dekking, ook buiten. |
| Kaart 2 | Netwerksegmentatie — Gescheiden netwerken voor medewerkers, gasten en apparaten. |
| Kaart 3 | Beheer & documentatie — Centrale monitoring, helder gedocumenteerd voor zelfstandig beheer. |
| Stap 1 | Plaatsbezoek & meting — We analyseren de ruimte en bepalen de optimale plaatsing. |
| Stap 2 | Voorstel op maat — Concreet plan met materiaallijst, layout en prijs. |
| Stap 3 | Installatie & oplevering — Vakkundige installatie en overdracht met documentatie. |
| CTA | Klaar voor een stabiel netwerk? → Plan een plaatsbezoek » |

### Cloudplatform

| Sectie | Tekst |
|--------|-------|
| Badge (blauw) | Gebouwd op Odoo Community Edition — open source |
| Titel | Eén platform voor je hele coworkingwerking |
| Intro | Working Local biedt een cloudplatform gebouwd op Odoo Community Edition, uitgebreid met modules op maat voor het beheer van een coworkingplek. Van werkplekreservaties en ledenadministratie tot facturatie en het centraal beheren van informatieschermen op al je locaties — alles in één overzichtelijk systeem. |
| Kaart 1 | Werkplekken reserveren — Via web of smartphone, overzichtelijk voor bewoner en beheerder. |
| Kaart 2 | Ledenbeheer & toegang — Profielen, toegangsrechten en aanwezigheid, ook op afstand. |
| Kaart 3 | Informatieschermen op afstand — Centraal beheren wat op de schermen verschijnt, vanop elke locatie. |
| Module 1 | Werkplek- en ruimtereservatie — Bezettingszicht, tijdslots, terugkerende boekingen. |
| Module 2 | Facturatie & betalingen — Automatische facturatie van lidmaatschappen en reservaties. |
| Module 3 | Centraal schermbeheer — Live bijwerken zonder ter plaatse te gaan. |
| Module 4 | Rapportage & inzichten — Bezettingsgraad, populaire tijdslots, groei ledenbestand. |
| Blauw blok | Waarom Odoo Community Edition? Odoo is een volwassen, wereldwijd bewezen open-source platform. De Community Edition is volledig gratis — geen licentiekosten, geen vendor lock-in. |
| CTA | Wil je het platform in actie zien? → Vraag een demo » |

### Hybride meeting-sets

| Sectie | Tekst |
|--------|-------|
| Titel | Professionele vergaderingen, plug-and-play |
| Intro | Universele, plug-and-play oplossingen voor vergaderruimtes. Professioneel audio en video, compatibel met elke laptop of smartphone. Beschikbaar als product én als dienst — inclusief installatie en onderhoud. |
| Kaart 1 | Professionele webcam — Brede hoek, hoge resolutie, automatische belichting. |
| Kaart 2 | 360° speakerphone — Omnidirectionele microfoon en luidspreker voor iedereen aan tafel. |
| Kaart 3 | Scherm of tv-mount — Groot scherm voor presentaties en remote deelnemers. |
| CTA | Klaar voor professionele hybride vergaderingen? → Vraag een offerte » |

### Focustraject

| Sectie | Tekst |
|--------|-------|
| Titel | Meer focus, ritme en vooruitgang — samen met anderen |
| Intro | Een concreet traject om uitstelgedrag en concentratieproblemen aan te pakken. Gebaseerd op drie bewezen methodes in een praktisch, gemeenschappelijk programma binnen jouw coworkingplek. |
| Kaart 1 | GTD + Todoist — Getting Things Done als fundament, Todoist als digitaal werkgeheugen. |
| Kaart 2 | Groeps-Pomodoro's — Focussessies in groep via onze eigen webapp, hybride of online. |
| Kaart 3 | RescueTime + Exist — Automatische tijdsmeting en persoonlijke inzichten. |
| Stap 1 | Introductiesessie — in 2 uur opgestart |
| Stap 2 | Wekelijkse focussessies — via de webapp |
| Stap 3 | Persoonlijke tracking — RescueTime en Exist meten automatisch |
| CTA | Geef jouw bewoners meer focus en ritme → Meer weten of inschrijven » |

### Webinar & Livestream

| Sectie | Tekst |
|--------|-------|
| Titel | Professioneel online of hybride op het podium |
| Intro | Compacte, hoogwaardige setups voor online workshops, hybride events en webinars. Gebaseerd op OBS-technologie en Microsoft Teams. Beschikbaar met of zonder begeleiding. |
| Kaart 1 | OBS-videoproductie — Scènes, overlays, schermopname en live-switching op maat. |
| Kaart 2 | Hybride events — Combineer aanwezigen met online deelnemers via Teams of YouTube. |
| Kaart 3 | Technische begeleiding — Aanwezig of op afstand, zodat jij je focust op de inhoud. |
| CTA | Klaar om professioneel online te gaan? → Bespreek jouw event » |

---

## 5. Volledige productcatalogus voor Odoo CE

### Categoriestructuur

```
Alle producten
├── Circulaire werkplek
│   ├── Bureau's
│   ├── Tafels
│   └── Stoelen
├── Beeldschermen
│   ├── 22"
│   ├── 27"
│   ├── 32"
│   └── 34" Ultrawide
├── Informatieschermen
├── IT-hardware
│   ├── Laptops
│   ├── Desktops & mini-pc's
│   └── Servers & werkstations
├── Accessoires
│   ├── Monitorarmen
│   ├── Docking stations
│   ├── Draadloze desktops
│   └── Conference sets
├── Meubelen
│   ├── Kasten
│   └── Zitmeubelen
└── Diensten
    ├── Wifi
    ├── Focussessies
    ├── AV & Studio
    └── Logistiek
```

### Productattributen (Odoo Configuratie → Attributen)

| Attribuut | Waarden |
|-----------|---------|
| Merk | Dell, HP, Lenovo, LG, Samsung, Philips, NEC, SMART, Huawei, Polycom |
| Schermdiagonaal | 22", 27", 32", 34", 42", 43", 55", 75" |
| Resolutie | Full HD (1080p), QHD (1440p), 4K UHD, WQHD Ultrawide (3440×1440) |
| Staat | Refurbished, Nieuw in doos, Nieuw ongebruikt |

### Productstatus (custom veld `x_status`)

| Waarde | Betekenis | Webshop |
|--------|-----------|---------|
| `beschikbaar` | Normaal te bestellen | Zichtbaar + bestelbaar |
| `uitverkocht` | Niet beschikbaar | Zichtbaar + niet bestelbaar + tekst "Momenteel uitverkocht — binnenkort opnieuw beschikbaar of op aanvraag." |
| `nieuw` | Nieuw product | Zichtbaar + bestelbaar + "Nieuw"-badge |

---

### DIENSTEN

#### Wifi
| Ref | Naam | Type | Prijs |
|-----|------|------|-------|
| SRV-WIFI-01 | Wifi-audit met planning, aankoopadvies en -begeleiding | Forfait | €199 excl. btw |
| SRV-WIFI-02 | Wifi-installatie | Uurprijs | €65/u excl. btw |
| SRV-WIFI-03 | Wifi-configuratie | Uurprijs | €65/u excl. btw |
| SRV-WIFI-04 | Wifi-interventie op afstand | Forfait | €50 excl. btw |
| SRV-WIFI-05 | Wifi-interventie ter plaatse | Forfait | €99 excl. btw |

#### Focussessies
| Ref | Naam | Type | Prijs |
|-----|------|------|-------|
| SRV-FOCUS-01 | Begeleide focussessie — halve dag | Forfait | €149 excl. btw |
| SRV-FOCUS-02 | Begeleide focussessie — volledige dag | Forfait | €249 excl. btw |
| SRV-FOCUS-03 | Huur Focus Kiosk voor zelfbegeleide sessies | Verhuur/dag | €99 excl. btw |

#### AV & Studio
| Ref | Naam | Type | Prijs |
|-----|------|------|-------|
| SRV-AV-01 | OBS-studio operator — halve dag | Forfait | €149 excl. btw |
| SRV-AV-02 | OBS-studio operator — volledige dag | Forfait | €249 excl. btw |
| SRV-AV-03 | OBS-studio operator — in regie | Uurprijs | €65/u excl. btw |

#### Logistiek
| Ref | Naam | Type | Prijs |
|-----|------|------|-------|
| SRV-LOG-01 | Verhuis-, plaatsings- en montageservice | Uurprijs | €50/u excl. btw |

---

### CIRCULAIRE WERKPLEK > BUREAU'S

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| DESK-01 | Refurbished Bureau 180×80 cm — verstelbaar 62–82 cm, asymmetrisch blad, kabelgoot | Beschikbaar | €119 excl. btw |
| DESK-02 | Refurbished Slingerbureau Ahrend 160×80 cm — Trespa-blad, verstelbaar 64–90 cm | Beschikbaar | €179 excl. btw |
| DESK-03 | Refurbished Bureau Kinnarps 160×80 cm — demonteerbare poten, kabelgoot, hoogteverstelbaar | Beschikbaar | €99 excl. btw |
| DESK-04 | Refurbished Zit-sta Bureau 160×80 cm — verstelbaar 64–110 cm | Beschikbaar | €199 excl. btw |

---

### CIRCULAIRE WERKPLEK > TAFELS

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| TABLE-01 | Refurbished Vergadertafel 100×125 cm — vaste hoogte 70 cm, demonteerbare poten | Beschikbaar | €89 excl. btw |
| TABLE-02 | Rechthoekige tafel | Uitverkocht | — |

---

### CIRCULAIRE WERKPLEK > STOELEN

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| CHAIR-01 | Bureaustoel variant 1 | Te bepalen | link nodig |
| CHAIR-02 | Bureaustoel variant 2 | Te bepalen | link nodig |
| CHAIR-03 | Gewone stoel | Te bepalen | link nodig |

---

### BEELDSCHERMEN

*Filterattributen per product: Merk / Schermdiagonaal / Resolutie / Staat*

#### 22"
| Ref | Naam | Merk | Diagonaal | Resolutie | Status | Prijs |
|-----|------|------|-----------|-----------|--------|-------|
| MON-22-01 | Beeldscherm 22" Full HD — Dell P2219H, HDMI/DP/VGA, USB-hub, roterende voet | Dell | 22" | Full HD | Beschikbaar | €89 excl. btw |
| MON-22-02 | Beeldscherm 22" HP | HP | 22" | Te bepalen | Te bepalen | link nodig |

#### 27"
| Ref | Naam | Merk | Diagonaal | Resolutie | Status | Prijs |
|-----|------|------|-----------|-----------|--------|-------|
| MON-27-01 | Beeldscherm 27" Full HD — Dell P2717H, HDMI/DP/VGA, USB-hub, voet apart | Dell | 27" | Full HD | Beschikbaar | €109 excl. btw |
| MON-27-02 | Beeldscherm 27" QHD — HP Z27n, kantelbare HP-voet | HP | 27" | QHD | Beschikbaar | €139 excl. btw |
| MON-27-03 | Beeldscherm 27" 4K — HP S270n, USB-C 60W, hoogteverstelbaar | HP | 27" | 4K | Beschikbaar | €219 excl. btw |
| MON-27-04 | Beeldscherm 27" QHD — Lenovo P27h-10, USB-C PD, op voet | Lenovo | 27" | QHD | Beschikbaar | €189 excl. btw |
| MON-27-05 | Beeldscherm 27" QHD — Lenovo P27h-20, USB-C 90W + Ethernet + luidsprekers, zonder voet | Lenovo | 27" | QHD | Beschikbaar | €169 excl. btw |
| MON-27-06 | Beeldscherm 27" QHD — Dell U2721DE, USB-C docking + Ethernet, Dell-voet | Dell | 27" | QHD | Beschikbaar | €199 excl. btw |
| MON-27-07 | Beeldscherm 27" QHD — Dell P2723DE, USB-C 90W + HDMI + DP + Ethernet, zonder voet | Dell | 27" | QHD | Beschikbaar | €199 excl. btw |
| MON-27-08 | Beeldscherm 27" 4K — LG, design voet, kantelbaar/verstelbaar | LG | 27" | 4K | Beschikbaar | €219 excl. btw |
| MON-27-SET | Set 2× Beeldscherm 27" QHD — Dell U2717D op Ergotron-voet | Dell | 27" | QHD | Beschikbaar | €249 excl. btw (set) |

#### 32"
| Ref | Naam | Merk | Diagonaal | Resolutie | Status | Prijs |
|-----|------|------|-----------|-----------|--------|-------|
| MON-32-01 | Beeldscherm 32" 4K — Lenovo P32p-20, USB-C 90W + Ethernet, IPS, zonder voet | Lenovo | 32" | 4K | Beschikbaar | €249 excl. btw |

#### 34" Ultrawide
| Ref | Naam | Merk | Diagonaal | Resolutie | Status | Prijs |
|-----|------|------|-----------|-----------|--------|-------|
| MON-34-01 | Ultrabreed Beeldscherm 34" QHD — LG 34WK650, IPS, 75Hz, 2×HDMI+DP, op voet | LG | 34" | WQHD Ultrawide | Beschikbaar | €219 excl. btw |
| MON-34-02 | Curved Ultrabreed 34" WQHD — Dell U3419W, USB-C hub, op voet | Dell | 34" | WQHD Ultrawide | Beschikbaar | €409 excl. btw |
| MON-34-03 | Curved Ultrabreed 34" WQHD — Dell P3424WE, USB-C 90W + Ethernet, nieuw ongebruikt | Dell | 34" | WQHD Ultrawide | Nieuw | €439 excl. btw |

---

### INFORMATIESCHERMEN

#### Verkoop
| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| SIGN-01 | Informatiescherm 32" Full HD — NEC MultiSync E328, HDMI/USB, luidsprekers, nieuw in doos | Nieuw | €299 excl. btw |
| SIGN-02 | Smart Display 75" 4K Android — SMART Board NX175, geen aanraking, nieuw in doos | Nieuw | €899 excl. btw |
| SIGN-03 | Informatiescherm 43" 4K — Samsung LH43Q, VESA, refurbished | Beschikbaar | €239 excl. btw |
| SIGN-04 | Informatiescherm 42" HD — Philips BDL4270EL, met afstandsbediening, refurbished | Beschikbaar | €219 excl. btw |
| SIGN-05 | Informatiezuil 43" 4K Dell op statief/trolley | Te bepalen | link nodig |
| SIGN-06 | Interactief whiteboard 75" Philips Android touchscreen op statief | Te bepalen | link nodig |

#### Verhuur (dagprijzen)
| Ref | Naam | Huurprijs/dag |
|-----|------|---------------|
| RENT-01 | Huur Informatiezuil 55" 4K LG 55UH5F op rijdend statief | €99 excl. btw |
| RENT-02 | Huur Hybride Meetingset 55" LG op statief + HP Poly conference bar | €129 excl. btw |
| RENT-03 | Huur Touchscreen Kiosk 32" portrait op statief (Windows PC ingebouwd) | Te bepalen |

---

### IT-HARDWARE > LAPTOPS

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| LAP-01 | Laptop Small 13" — HP EliteBook 830 G8, i7-1185G7, 16GB, 500GB, B&O, USB-C, Win11 Pro | Refurbished | €349 excl. btw |
| LAP-02 | Laptop Small 14" — Lenovo ThinkBook 14 G2, i7-1165G7, 24GB, 512GB, wifi6, USB-C, Win11 Pro | Refurbished | €399 excl. btw |
| LAP-03 | Laptop Normal 15,5" — HP EliteBook 855 G8, Ryzen 5, 16GB, 256GB, B&O, Win11 Pro | Refurbished | €399 excl. btw |
| LAP-04 | Laptop Normal 2-in-1 14" — Lenovo X1 Yoga Gen 6, i7, 16GB, 1TB, 4K touch 360°, Win11 Pro | Refurbished | €699 excl. btw |
| LAP-05 | Laptop High End 14" — Dell Precision 5480, i7-13700H, 16GB, 512GB, RTX A1000 6GB, nieuw | Nieuw in doos | €1.499 excl. btw |

---

### IT-HARDWARE > DESKTOPS & MINI-PC'S

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| PC-01 | Desktop Ultralight — Dell OptiPlex 3050 SFF, i5-6500, 8GB, 256GB NVMe, Win11 Pro | Refurbished | €149 excl. btw |
| PC-02 | Signage Client — Dell OptiPlex 3050 SFF, i5-6500, 8GB, 256GB NVMe, Win11 Pro + Xibo CMS | Refurbished | €149 excl. btw |
| PC-03 | Miniserver Linux — Dell OptiPlex 3050 SFF, i5-6500, 16GB, 256GB NVMe, Linux | Refurbished | €249 excl. btw |

---

### IT-HARDWARE > SERVERS & WERKSTATIONS

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| SRV-01 | Werkstation Basic — Lenovo P520, Xeon W, 16GB, 500GB NVMe, NVIDIA P1000 (4×miniDP), Win11 Pro | Refurbished | €299 excl. btw |
| SRV-02 | Werkstation Pro — Lenovo P520, Xeon W, 32GB, 1TB NVMe (nieuw), NVIDIA P1000, Win11 Pro | Refurbished | €499 excl. btw |
| SRV-03 | Server/Virtualisatiehost — Lenovo P520, Xeon W, 32GB, geen OS/opslag, NVIDIA P1000 | Refurbished | €399 excl. btw |
| SRV-04 | Dual-CPU Werkstation/Server — Lenovo P720, 2× Xeon Gold 6134 (16c/32t), 64GB, 1TB NVMe, P1000, Win11 Pro WS | Refurbished | €899 excl. btw |

---

### ACCESSOIRES > MONITORARMEN

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| ARM-01 | Enkele monitorarm | Uitverkocht | — |
| ARM-02 | Dubbele monitorarm High End — Humanscale M8, nieuw, tafelklem, max 2× 27", kabelgeleiding | Beschikbaar (Nieuw) | €199 excl. btw |
| ARM-03 | Dubbele monitorarm Flex — ACT8312, nieuw, gasveersysteem, VESA | Beschikbaar (Nieuw) | €149 excl. btw |
| ARM-04 | Dubbele monitorarm Basic — refurbished, tafelklem, max 2× 32", instelbaar gewicht, VESA | Beschikbaar | €99 excl. btw |
| ARM-05 | Vierledige monitorarm — Ewent Quad, nieuw, tafelklem, 4× max 32", VESA | Beschikbaar (Nieuw) | €99 excl. btw |

---

### ACCESSOIRES > DOCKING STATIONS

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| DOCK-01 | Dell Thunderbolt Dock TB19 (2019) | Uitverkocht | — |
| DOCK-02 | Dell Thunderbolt Dock TB22 (2022) | Uitverkocht | — |
| DOCK-03 | Refurbished Dell USB-C Docking Station WD19 — 130W, USB-C, inclusief voeding | Beschikbaar | €89 excl. btw |
| DOCK-04 | HP Universele USB-C Multipoort Hub — nieuw, 7 poorten, DP/HDMI/Ethernet/USB | Beschikbaar (Nieuw) | €59 excl. btw |

---

### ACCESSOIRES > DRAADLOZE DESKTOPS

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| KBM-01 | HP draadloze desktop — ingebouwde oplaadbare batterij | Te bepalen | link nodig |
| KBM-02 | HP draadloze desktop — vervangbare batterijen | Te bepalen | link nodig |

---

### ACCESSOIRES > CONFERENCE SETS

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| CONF-01 | Refurbished Audio- en Videobar — HP Poly Studio P009, USB, camera+microfoon+luidspreker | Beschikbaar | €249 excl. btw |
| CONF-02 | Refurbished Draadloze Headset — HP Poly Voyager Focus UC B825, ANC, 10u+, Bluetooth | Beschikbaar | €89 excl. btw |
| CONF-03 | Refurbished IP-Telefoon USB — Polycom CX300 R2, Teams-gecertificeerd, speakerphone | Beschikbaar | €79 excl. btw |
| CONF-04 | IP-Telefoon 2-lijn SIP — Huawei eSpace 7810, nieuw, PoE, encryptie | Beschikbaar (Nieuw) | €89 excl. btw |

---

### MEUBELEN

| Ref | Naam | Status | Prijs |
|-----|------|--------|-------|
| FURN-01 | Refurbished Garderobe / Roomdivider 240×160×64 cm — afwasbaar, kapstokconstructie | Beschikbaar | €249 excl. btw |
| FURN-02 | Refurbished Hoge Roldeurkast MEWAF — metaal, roldeuren, verstelbare leggers | Beschikbaar | €219 excl. btw |
| FURN-03 | Refurbished Zitbank 2-persoons — groen, 128×80×98 cm, hoge zit | Beschikbaar | €199 excl. btw |

---

## 6. Odoo import — stappenplan

### Stap 1 — Categorieën aanmaken (Python script)

```python
# Volgorde: parents eerst, dan children
parents = [
    'Circulaire werkplek', 'Beeldschermen', 'Informatieschermen',
    'IT-hardware', 'Accessoires', 'Meubelen', 'Diensten'
]
children = {
    'Circulaire werkplek': ["Bureau's", 'Tafels', 'Stoelen'],
    'Beeldschermen':       ['22"', '27"', '32"', '34" Ultrawide'],
    'IT-hardware':         ['Laptops', "Desktops & mini-pc's", 'Servers & werkstations'],
    'Accessoires':         ['Monitorarmen', 'Docking stations', 'Draadloze desktops', 'Conference sets'],
    'Meubelen':            ['Kasten', 'Zitmeubelen'],
    'Diensten':            ['Wifi', 'Focussessies', 'AV & Studio', 'Logistiek'],
}
```

### Stap 2 — Attributen aanmaken

Via Odoo backend: Webshop → Configuratie → Attributen
Of via script (attribuuttype = `select`):

```python
for name, values in {
    'Merk': ['Dell','HP','Lenovo','LG','Samsung','Philips','NEC','SMART','Huawei','Polycom'],
    'Schermdiagonaal': ['22"','27"','32"','34"','42"','43"','55"','75"'],
    'Resolutie': ['Full HD (1080p)','QHD (1440p)','4K UHD','WQHD Ultrawide (3440×1440)'],
    'Staat': ['Refurbished','Nieuw in doos','Nieuw ongebruikt'],
}.items():
    attr_id = create('product.attribute', {'name': name, 'create_variant': 'no_variant'})
    for v in values:
        create('product.attribute.value', {'name': v, 'attribute_id': attr_id})
```

### Stap 3 — Producten importeren via XML-RPC

**Uitgevoerd** via `/tmp/odoo_import_full.py`. 66 producten aangemaakt met `xmlrpc.client`.

> Geen CSV-import: speciale tekens (apostrofen, aanhalingstekens in productnamen zoals "Bureau's") breken bash heredocs. Python script via SCP naar VPS is betrouwbaarder.

```python
models.execute_kw(db, uid, password, 'product.template', 'create', [{
    'name': 'Beeldscherm 27" Full HD — Dell P2717H',
    'default_code': 'MON-27-01',
    'categ_id': cat_ids['27"'],
    'list_price': 109.0,
    'type': 'product',          # 'service' voor diensten
    'description_sale': 'HDMI/DP/VGA, USB-hub, voet apart. Refurbished.',
    'x_status': 'beschikbaar',
}])
```

### Stap 4 — Hoofdafbeeldingen uploaden

**Uitgevoerd** via `/tmp/odoo_images.py`. 49 producten kregen een hoofdafbeelding.

pv-consulting.com blokkeert Python urllib (HTTP 403). Gebruik `curl` via subprocess:

```python
result = subprocess.run(["curl", "-sf", "--max-time", "20", url], capture_output=True)
b64 = base64.b64encode(result.stdout).decode('utf-8')
models.execute_kw(db, uid, password, 'product.template', 'write',
                  [[tmpl_id], {'image_1920': b64}])
```

### Stap 5 — Extra galerij-afbeeldingen

**Uitgevoerd** via `/tmp/odoo_scrape_images.py`. ~292 extra afbeeldingen gescraped van pv-consulting.com productpagina's en opgeslagen als `product.image` records.

> Vereist: eCommerce-module geactiveerd (anders bestaat `product.image` niet).

### Stap 6 — Placeholder afbeeldingen voor diensten

**Uitgevoerd** via `/tmp/create_placeholders.py`. 18 dienst-producten zonder foto kregen een SVG-placeholder in de huisstijl (marineblauw + geel). Iconen per categorie: WiFi-antenne, bullseye, camera, vrachtwagen, sleutel.

---

## 7. Afbeeldingsbronnen per product

| Product | Bestanden (pv-consulting.com/images/) |
|---------|---------------------------------------|
| Bureau 180×80 | TEMP_20231025_110928.jpg, 20231025_110257.jpg |
| Slingerbureau Ahrend | 24.png, 14.png, 48.png |
| Bureau Kinnarps | 20240221_133802.jpg, 20240221_133830.jpg |
| Zit-sta bureau | 5.png, 21.png, 31.png |
| Vergadertafel 100×125 | 23.png, 13.png, 33.png |
| Dell OptiPlex 3050 (PC) | dell_optiplex_3050_sff_1.jpeg, 20250510_095458.jpg |
| Dell OptiPlex 3050 (Linux) | dell_optiplex_3050_sff_1.jpeg, 20250510_095640.jpg |
| Lenovo P520 | vooraanzichtlinks.jpg, kastopen.jpg, achterzichtlinks.jpg |
| Lenovo P720 | 13.jpg, 20240704_114816_HDR.jpg |
| HP EliteBook 830 G8 | PXL_20260331_181019263.jpg + 15 meer |
| Lenovo ThinkBook 14 G2 | IMG_20251008_162851_HDR.jpg + 5 meer |
| HP EliteBook 855 G8 | PXL_20260207_113634494.jpg + 9 meer |
| Lenovo X1 Yoga Gen 6 | PXL_20260301_104809492.jpg + 17 meer |
| Dell Precision 5480 | 111.png + 6 meer |
| Humanscale M8 arm | 22.jpg, 12.jpg, 32.jpg |
| ACT8312 dubbele arm | 311.png, 27.png, specs.png + 4 meer |
| Dubbele arm basic | PXL_20260109_183109691.jpg + 9 meer |
| Ewent Quad arm | PXL_20260301_112658571.jpg + 4 meer |
| Dell WD19 | connections1.jpg, specs6.jpg + 9 meer |
| HP USB-C Hub | 24.jpg, 34.jpg, 15.jpg + 3 meer |
| LG 55" | 20250530_180457.jpg + 9 meer |
| NEC 32" signage | 19.jpg + 8 meer |
| SMART Board 75" | 11.jpg + 6 meer |
| Samsung 43" | 20240724_095245_HDR.jpg + 6 meer |
| Philips 42" | 20240723_114937_HDR.jpg + 9 meer |
| HP Poly Studio P009 | IMG_20251015_110102_HDR.jpg + 9 meer |
| HP Poly Voyager headset | headset.jpg, set.jpg, specs13.jpg |
| Polycom CX300 | 2001509219.png + 4 meer |
| Huawei eSpace 7810 | espace-7810-500x500.png + 5 meer |
| Garderobe roomdivider | 15.png + 5 meer |
| Zitbank groen | 3.png, 1.png, 2.png, 4.png |
| Roldeurkast MEWAF | PXL_20260328_124640727.jpg + 4 meer |
| Dell 22" P2219H | 20250518_175753.jpg + 6 meer |
| Dell 27" P2717H | PXL_20260117_134538405.jpg + 5 meer |
| HP 27" Z27n | 20250523_195448.jpg + 6 meer |
| HP 27" S270n 4K | 20250508_134944.jpg + 4 meer |
| Lenovo P27h-10 | PXL_20260301_112041500.jpg + 8 meer |
| Lenovo P27h-20 | Screenshot2025-02-20180850.png + 3 meer |
| Dell U2721DE | 20250315_104016_HDR.jpg + 5 meer |
| Dell P2723DE | PXL_20260117_134116611.jpg + 9 meer |
| LG 27" 4K | 120240715_111619_HDR.jpg + 9 meer |
| Set Dell U2717D | 20241003_170600_HDR.jpg + 3 meer |
| Lenovo P32p-20 | Screenshot2025-02-20182007.png + 3 meer |
| LG 34" Ultrawide | PXL_20260301_110509698.jpg + 5 meer |
| Dell U3419W curved | 19.png + 2 meer |
| Dell P3424WE curved | 18.png + 7 meer |

---

## 8. Git-workflow en addon-deployment

```bash
git pull origin main
git add addons/workinglocal_theme/static/src/scss/workinglocal_theme.scss
git commit -m "fix: omschrijving"
git push origin main
```

> Let op: de addons staan in een **Docker volume op de VPS**, niet als bind-mount. Na een git push moet je de bestanden handmatig kopiëren:

```bash
# Enkel gewijzigd SCSS-bestand:
scp addons/workinglocal_theme/static/src/scss/workinglocal_theme.scss \
    root@23.94.220.181:/var/lib/docker/volumes/wmsa9jotez65ynj0xsb748rq_odoo-addons/_data/workinglocal_theme/static/src/scss/

# Na elke SCSS-wijziging: theme recompileren
docker exec odoo-[container-id] odoo \
    -u workinglocal_theme -d workinglocal --stop-after-init \
    --db_host=odoo-db --db_user=odoo --db_password='[wachtwoord]' --no-http
docker restart odoo-[container-id]
```

Volledig volumepad opzoeken: `docker inspect odoo-[id] --format '{{json .Mounts}}'`

---

## 9. Config deployment

De Coolify server-side docker-compose bevat **geen** bind mount voor `odoo.conf`.
Na elke config wijziging handmatig deployen:

```bash
scp config/odoo.conf root@23.94.220.181:/data/coolify/services/wmsa9jotez65ynj0xsb748rq/config/odoo.conf
ssh root@23.94.220.181 'docker cp /data/coolify/services/wmsa9jotez65ynj0xsb748rq/config/odoo.conf odoo-wmsa9jotez65ynj0xsb748rq:/etc/odoo/odoo.conf && docker restart odoo-wmsa9jotez65ynj0xsb748rq'
```

Master password (database manager): `bptz-dskh-cec4` — staat in `odoo.conf` als `admin_passwd`.
Database: enkel `workinglocal` (lege `odoo` db verwijderd 2026-04-25).

**E-mail: BEWUST UITGESCHAKELD.**
Geen `ir.mail_server` geconfigureerd. `odoo.conf` wijst naar localhost (geen SMTP).
Odoo kan geen mails versturen naar klanten. Activeer pas na expliciete beslissing via Instellingen > Technisch > Uitgaande mailserver.

---

## 10. Klantendossiers (CRM + Project + Portaal)

Scripts staan in `scripts/`. Gebruik `OdooClient` uit `scripts/suppliers/odoo_client.py`.

### Klantenfiches

| id | Klantenfiche | Type | Script |
|----|---|---|---|
| 7 | Vakantiehuis Muziekbos | Bedrijf | `klant_muziekbos.py` |
| 9 | Ide - Tack | Bedrijf | `klant_ide_steven.py` |
| 10 | Werkplaats Walter | Bedrijf | `klant_werkplaats_walter.py` |
| 17 | Manu BV | Bedrijf | `klant_contactpersonen.py` |

### Contactpersonen

| id | Naam | Ouder | Tel | Email | Portaal uid |
|----|---|---|---|---|---|
| 11 | Paul Van Loveren | Vakantiehuis Muziekbos | 0473 70 25 46 | info@vakantiehuis-muziekbos.be | 5 |
| 12 | Katrien Van Loveren | Vakantiehuis Muziekbos | — | info@vakantiehuis-muziekbos.be | 6 |
| 13 | Ilse Tack | Ide - Tack | — | tackilse@hotmail.com | 7 |
| 14 | Teun Verbruggen | Werkplaats Walter | 0476 43 15 63 | teun@werkplaatswalter.be | 8 |
| 15 | Steven Ide | Ide - Tack | 0479 79 36 77 | Stivie02@hotmail.com | 9 |
| 16 | Lien Van Steendam | Werkplaats Walter | 0471 56 20 29 | lien@werkplaatswalter.be | 10 |
| 18 | Manu Mattelin | Manu BV | 0478/702305 | manu.mattelin@telenet.be | 11 |
| 19 | Isabelle Volckaert | Manu BV | — | — | — |

> Katrien Van Loveren (id=12) deelt email met Paul. Aanpassen als eigen adres bekend.
> Nog ontbrekend: tel Katrien, Ilse Tack, Isabelle Volckaert + email Isabelle.

### Projecten (opvolging via klantenportaal)

| id | Project | Klant | Taken | Handleiding taak-id |
|----|---|---|---|---|
| 1 | Vakantiehuis Muziekbos - Wifi uitbreiding | id=7 | 4 | 24 |
| 2 | Ide - Tack - Netwerk oplevering | id=9 | 7 | 25 |
| 3 | Werkplaats Walter - Netwerk & ICT | id=10 | 13 | 26 |
| 4 | Manu BV - Project | id=17 | 1 (placeholder) | — |

Handleidingen aangemaakt via `scripts/klant_handleidingen.py` (2026-04-27):
- Taak 24: "Handleiding: TP-Link Deco wifi" — project 1 (Muziekbos)
- Taak 25: "Handleiding: Parental Control" — project 2 (Ide-Tack)
- Taak 26: "Documentatie: Netwerk & Unifi installatie" — project 3 (Werkplaats Walter)

Klanten volgen op via: **https://odoo.workinglocal.be/my**
**Nog geen uitnodigingsmails verstuurd** — email staat bewust uitgeschakeld.

### Odoo 19 CE veldvalkuilen
- `res.partner`: geen `mobile` veld → gebruik `phone`
- `res.users` aanmaken: gebruik `group_ids` niet `groups_id`

---

## 11. Custom addons

### Overzicht geïnstalleerde addons

| Addon | Versie | Beschrijving |
|---|---|---|
| `coworking_reservation` | 19.0.2.0.0 | Werkplekbeheer, reservaties, pakketten, dagdelen, signage |
| `workinglocal_rental` | 19.0.1.0.0 | Huurcontracten ateliers/appartementen, maandelijkse facturatie |
| `workinglocal_interventions` | 19.0.1.0.0 | Interventieregistratie, checklists, PDF-rapport |

### coworking_reservation — sleutelfunctionaliteit

**Werkplektypes:** hot_desk, fixed_desk, meeting_room, focus_zone, event, hybrid_meeting, muziekzaal, productiestudio, foyer, muziekstudio

**Boekingseenheid per werkplek:** dag (volledige dag) of slot (VM/NM/AV met configureerbare tijdsloten)

**Pakketten (`coworking.package`):** groepeert meerdere ruimten — één reservatie blokkeert alle gekoppelde ruimten. Overlap-check detecteert conflicten via directe én pakket-reservaties.

**Boekingstype op reservaties:** extern / intern / geblokkeerd

**Website routes:**
- `/werkplekken` — werkplekken overzicht + boekingsformulier
- `/beschikbaarheid` — weekoverzicht beschikbaarheid per ruimte (publiek)
- `/signage/reservaties` — fullscreen TV-display voor Xibo CMS (publiek, auto-refresh 60s)
- `/mijn/reservaties` — klantenportaal (auth required)

**JSON endpoint voor Xibo DataSets:**
```
GET /api/workspaces/availability
→ {updated_at, workspaces[], today_schedule[], upcoming[]}
```

**Xibo setup:** Webpage widget → URL `/signage/reservaties` → Duration 60s → Scale Best Fit 1920×1080

### workinglocal_rental — sleutelfunctionaliteit

**Model:** `rental.contract` met referentie HUV/YYYY/NNN

**Cron:** dagelijks 07:00 → draft-facturen voor actieve contracten waar `invoice_day == vandaag` (idempotent)

**Werkplek-koppeling:** `rental.contract.line` kan optioneel linken aan `coworking.workspace` (vult prijs automatisch)

### Addon deployen (VPS)

```bash
# 1. SCP naar volume
scp -r addons/<addon> root@23.94.220.181:/var/lib/docker/volumes/wmsa9jotez65ynj0xsb748rq_odoo-addons/_data/

# 2. Config in container schrijven (& in wachtwoord → nooit via CLI doorgeven)
ssh root@23.94.220.181 'cat > /tmp/odoo_upgrade.conf << "EOF"
[options]
db_host = odoo-db-wmsa9jotez65ynj0xsb748rq
db_user = odoo
db_password = FidonH4fyjfH&9
db_name = workinglocal
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
EOF
docker cp /tmp/odoo_upgrade.conf odoo-wmsa9jotez65ynj0xsb748rq:/tmp/odoo_upgrade.conf'

# 3. Installeren (-i) of upgraden (-u)
ssh root@23.94.220.181 'docker exec odoo-wmsa9jotez65ynj0xsb748rq odoo \
  -c /tmp/odoo_upgrade.conf -u coworking_reservation -d workinglocal --stop-after-init 2>&1 | tail -5'

# 4. Herstarten
ssh root@23.94.220.181 'docker restart odoo-wmsa9jotez65ynj0xsb748rq'
```

### Addon deployen (on-premise klantserver)

```bash
# Via update script (auto-detecteert containers en volumes)
ssh wp-walter 'bash /opt/workinglocal/scripts/update-addons.sh'

# Specifieke modules
ssh wp-walter 'bash /opt/workinglocal/scripts/update-addons.sh --modules "coworking_reservation"'
```

### Odoo 19 CE valkuilen

- `<list>` niet `<tree>` in views
- `invisible="condition"` niet `states=`
- Geen `expand` attribuut op `<group>` in search views
- `ir.cron` heeft geen `numbercall` of `doall` velden meer
- `selection_add` met `ondelete={'value': 'cascade'}` — NIET `'set default'` bij required fields zonder default
- `create()` geeft lijst terug → altijd `result[0]` gebruiken
- `write()` op `account.move` via XML-RPC faalt → gebruik directe SQL
- `seller_ids` partner_id moet integer zijn (niet lijst)
- DB wachtwoord bevat `&` → altijd via config file doorgeven, nooit via CLI args

---

## 12. Veiligheidsgrenzen

### Nooit zonder bevestiging:
- workinglocal.be (productie) aanraken
- Odoo-database op productie wijzigen
- WordPress-pagina's op productie verwijderen
- wp-config.php wijzigen

### Altijd doen voor destructieve acties:
```bash
# WordPress
wpcli db export /tmp/wp-backup-$(date +%Y%m%d-%H%M).sql

# Odoo (binnen container)
odoo --stop-after-init -d [db] --backup /tmp/odoo-backup-$(date +%Y%m%d-%H%M).zip
```

### Zelfstandig toegestaan:
- Pagina's aanmaken op wordpress.workinglocal.be
- Child theme aanmaken en aanpassen
- Odoo-producten importeren op staging
- Git commits en pushes
- Elementor-cache leegmaken

---

## 13. Leveranciersscripts

Scripts staan in `scripts/suppliers/`. Gedeelde module: `odoo_client.py`.

### PV Consulting — pv-consulting.com
- Script: `scripts/suppliers/pv_consulting.py`
- Leverancier: `res.partner` "PV Consulting" (supplier_rank=1, BE)
- Methode: webscraping (curl, HTML-regex) + automatische `seller_ids` koppeling
- SKU-reeks: `MON-22-*`, `MON-27-*`, `MON-32-*`, `MON-34-*`, `MON-43-*`, `DESK-*`, `LAP-*`, `PC-*`, `SRV-*`, `ARM-*`, `DOCK-*`, `CONF-*`, `FURN-*`, `NET-*`, `SIGN-*`, `RENT-*`
- Prijzen: scraped van pagina **incl.** 21% BTW → `round(prijs / 1.21, 2)` voor `standard_price`
- Patch-sectie: voegt PV Consulting als leverancier toe aan reeds bestaande producten (idempotent)

### Wimood — wimoodshop.nl
- Script: `scripts/suppliers/wimood.py`
- Methode: XML-API (`https://wimoodshop.nl/api/index.php?api_key=...&klantnummer=11556`)
- Filter: `brand='Ubiquiti'` én `'UniFi'` in productnaam (sluit AirMAX/EdgeRouter/etc. uit)
- SKU: Wimood `product_code` rechtstreeks als `default_code` (bv. `U6-Pro`, `USW-16-POE`)
- Prijzen in XML zijn **excl.** BTW: `prijs` → `standard_price`, `msrp` → `list_price`
- Categorieën: `Netwerk & WiFi` → Access Points / Switches / Gateways / Beveiliging / Controllers / Accessoires
- Afbeeldingen: SVG WiFi-placeholder (geen afbeeldings-URL in Wimood XML)

### DSIT — patchkabel.be
- Geen script: producten worden manueel aangemaakt per item
- Leverancier: `res.partner` "DSIT" (id=21, supplier_rank=1, BE)
- Website: https://www.patchkabel.be
- SKU-reeks: product code rechtstreeks van patchkabel.be (bv. `DC-6A1-005`)
- Prijsregel: aankoopprijs = website excl. BTW; verkoopprijs manueel instellen
- Categorie: Netwerkhardware → Switches / Accessoires netwerk
- Alle kabels en netwerking buiten Ubiquiti komen van DSIT

### Prijsregel leveranciers (algemeen)
- Handmatig ingestelde `list_price` in het script is altijd leading
- Enkel bij `list_price=0`: PV-website prijs incl. BTW = onze verkoopprijs excl. BTW (21% markup op cost)

### Nieuw leveranciersscript
1. Maak `leverancier_naam.py` in `scripts/suppliers/`
2. Importeer bovenaan: `from odoo_client import OdooClient, svg_placeholder, b64`
3. Voeg de SKU-reeks toe in dit overzicht (sectie 10)

---

## 14. Openstaande producten

| # | Product | Ontbreekt |
|---|---------|-----------|
| 1 | Bureaustoel variant 1 & 2 | Link + prijs |
| 2 | Gewone stoel | Link + prijs |
| 3 | HP draadloze desktops (2 varianten) | Link + prijs |
| 4 | Hybride meeting-set | Omschrijving + prijs |
| 5 | OBS-Studio multicam setup | Omschrijving + prijs |
| 6 | Informatiezuil 43" Dell op statief | Link + prijs |
| 7 | Interactief whiteboard 75" Philips op statief | Link + prijs |
| 8 | Touchscreen Kiosk 32" portrait | Prijs koop + verhuur |
| 9 | Volledig uitgeruste circulaire werkplek (bundel) | Samenstelling + prijs |

---

## 15. Referenties

| | |
|---|---|
| Staging WordPress | https://wordpress.workinglocal.be |
| WordPress admin | https://wordpress.workinglocal.be/wp-admin |
| Odoo CE | https://odoo.workinglocal.be |
| Odoo-repo | https://github.com/WorkingLocal/odoo-workinglocal |
| WordPress-repo | https://github.com/WorkingLocal/wordpress-workinglocal |
| Productiesite | https://workinglocal.be (NIET aanraken) |
| Inhoudsdocument | workinglocal-elementor-inhoud.docx |
| Contact | info@workinglocal.be |

---

| n8n automatisering | https://n8n.workinglocal.be |
| n8n-repo | https://github.com/WorkingLocal/n8n-workinglocal |

---

*Aangemaakt in samenwerking met Claude (Anthropic) — april 2026*
*Dit bestand wordt niet gedeployed naar de server (staat in .gitignore).*
