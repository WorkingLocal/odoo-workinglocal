"""
Hosting Local — Lokale AI Processing
scripts/suppliers/hosting_local_ai.py

Maakt aan:
  - IT-hardware > Lokale AI Servers  (HL-AI-*)
  - Diensten > Lokale AI             (SRV-AI-*)

Verkoopverhaal: uw AI draait lokaal op eigen hardware. Geen data naar
OpenAI, Google of Azure. GDPR-compliant, werkt zonder internet, goedkoper
op termijn dan cloud-API's. Gebouwd op energiezuinige refurbished hardware.

Bijwerkt ook de beschrijvingen van bestaande HL-SRV-* en SRV-BKP-* / SRV-VIRT-*
naar mensentaal.

Gebruik:
    python scripts/suppliers/hosting_local_ai.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from odoo_client import OdooClient, b64


# ── SVG helpers ───────────────────────────────────────────────────────────────

def _svg(shapes, label):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">'
        '<rect width="400" height="400" fill="#1A2E5A"/>'
        f'{shapes}'
        f'<text x="200" y="374" font-family="Arial,sans-serif" font-size="19" font-weight="bold"'
        f' text-anchor="middle" fill="#F5B800" opacity="0.9">{label}</text>'
        '</svg>'
    )
    return b64(svg.encode('utf-8'))


def svg_ai_server():
    """Chip + neurale verbindingen."""
    shapes = (
        '<rect x="130" y="120" width="140" height="140" rx="14" fill="none" stroke="#F5B800" stroke-width="11"/>'
        '<rect x="155" y="145" width="90" height="90" rx="8" fill="#F5B800" opacity="0.15"/>'
        '<rect x="155" y="145" width="90" height="90" rx="8" fill="none" stroke="#F5B800" stroke-width="7"/>'
        # CPU pinnen links
        '<line x1="90" y1="155" x2="130" y2="155" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="90" y1="180" x2="130" y2="180" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="90" y1="205" x2="130" y2="205" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="90" y1="230" x2="130" y2="230" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        # CPU pinnen rechts
        '<line x1="270" y1="155" x2="310" y2="155" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="270" y1="180" x2="310" y2="180" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="270" y1="205" x2="310" y2="205" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="270" y1="230" x2="310" y2="230" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        # CPU pinnen boven/onder
        '<line x1="160" y1="80" x2="160" y2="120" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="200" y1="80" x2="200" y2="120" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="240" y1="80" x2="240" y2="120" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="160" y1="260" x2="160" y2="300" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="200" y1="260" x2="200" y2="300" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="240" y1="260" x2="240" y2="300" stroke="#F5B800" stroke-width="7" stroke-linecap="round"/>'
        # Centraalpunt
        '<circle cx="200" cy="190" r="18" fill="#F5B800" opacity="0.9"/>'
    )
    return _svg(shapes, 'Lokale AI')


def svg_ai_service():
    """Hersennetwerk / neuraal patroon."""
    shapes = (
        # Knooppunten
        '<circle cx="200" cy="140" r="18" fill="none" stroke="#F5B800" stroke-width="9"/>'
        '<circle cx="120" cy="220" r="14" fill="none" stroke="#F5B800" stroke-width="8"/>'
        '<circle cx="280" cy="220" r="14" fill="none" stroke="#F5B800" stroke-width="8"/>'
        '<circle cx="155" cy="300" r="12" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<circle cx="245" cy="300" r="12" fill="none" stroke="#F5B800" stroke-width="7"/>'
        '<circle cx="200" cy="140" r="7" fill="#F5B800"/>'
        # Verbindingen
        '<line x1="200" y1="158" x2="126" y2="207" stroke="#F5B800" stroke-width="6" stroke-linecap="round" opacity="0.8"/>'
        '<line x1="200" y1="158" x2="274" y2="207" stroke="#F5B800" stroke-width="6" stroke-linecap="round" opacity="0.8"/>'
        '<line x1="126" y1="233" x2="155" y2="288" stroke="#F5B800" stroke-width="5" stroke-linecap="round" opacity="0.6"/>'
        '<line x1="126" y1="233" x2="245" y2="288" stroke="#F5B800" stroke-width="5" stroke-linecap="round" opacity="0.4"/>'
        '<line x1="274" y1="233" x2="155" y2="288" stroke="#F5B800" stroke-width="5" stroke-linecap="round" opacity="0.4"/>'
        '<line x1="274" y1="233" x2="245" y2="288" stroke="#F5B800" stroke-width="5" stroke-linecap="round" opacity="0.6"/>'
        # Kleine bolletjes op knooppunten
        '<circle cx="120" cy="220" r="5" fill="#F5B800" opacity="0.7"/>'
        '<circle cx="280" cy="220" r="5" fill="#F5B800" opacity="0.7"/>'
        '<circle cx="155" cy="300" r="4" fill="#F5B800" opacity="0.5"/>'
        '<circle cx="245" cy="300" r="4" fill="#F5B800" opacity="0.5"/>'
    )
    return _svg(shapes, 'AI Dienst')


# ── Turnkey AI Servers ────────────────────────────────────────────────────────

AI_SERVERS = [
    {
        'ref': 'HL-AI-01',
        'name': 'Lokale AI Server Starter — Lenovo P520, Xeon W, 32GB, NVIDIA P1000 4GB, Ollama',
        'list_price': 649.00,
        'standard_price': 450.00,
        'description_sale': (
            'Stel u voor: een AI-assistent die uw e-mails samenvat, vergaderingen noteert en '
            'vragen over uw documenten beantwoordt — volledig op uw eigen netwerk, zonder '
            'dat er ook maar één zin uw kantoor verlaat.\n\n'
            'Deze refurbished Lenovo ThinkStation P520 draait Ollama met taalmodellen tot 7 miljard '
            'parameters (Llama 3, Mistral, Phi-3). Dat is krachtig genoeg voor tekstverwerking, '
            'samenvatten, vertalen en eenvoudige code-assistentie — voor een onbeperkt aantal '
            'gebruikers in uw organisatie, zonder maandelijkse API-kosten.\n\n'
            'Wat u krijgt: hardware klaar voor gebruik, Ollama geïnstalleerd, twee modellen naar '
            'keuze geladen, en een Open WebUI zodat iedereen meteen aan de slag kan.\n\n'
            'Energieverbruik: ~80–120W onder belasting (24/7 ≈ €12–17/mnd bij €0,28/kWh). '
            'Refurbished — circulair aanbod van PV-consulting.'
        ),
    },
    {
        'ref': 'HL-AI-02',
        'name': 'Lokale AI Server Pro — Lenovo P720, dual Xeon, 64GB, NVIDIA Quadro 16GB+, Ollama',
        'list_price': 1349.00,
        'standard_price': 950.00,
        'description_sale': (
            'Voor organisaties die serieuze AI-taken lokaal willen uitvoeren: documenten analyseren, '
            'complexe teksten genereren, RAG-systemen (vraag-antwoord over uw eigen kennisbank), '
            'of meerdere gebruikers tegelijk bedienen.\n\n'
            'Deze krachtige refurbished Lenovo ThinkStation P720 draait modellen tot 32 miljard '
            'parameters — de klasse die normaal €20–30 per maand aan cloudkosten kost per gebruiker. '
            'Hier draait het onbeperkt, offline, op uw eigen locatie.\n\n'
            'Wat u krijgt: hardware klaar voor gebruik, Ollama geïnstalleerd, modellen naar keuze '
            'geladen (inclusief een Nederlands-sterk model), Open WebUI met gebruikersaccounts, '
            'en documentatie voor uw team.\n\n'
            'Energieverbruik: ~120–200W onder belasting (24/7 ≈ €17–28/mnd bij €0,28/kWh). '
            'Refurbished — circulair aanbod van PV-consulting.'
        ),
    },
    {
        'ref': 'HL-AI-03',
        'name': 'Lokale AI Server Ultimate — Lenovo P720, dual Xeon, 128GB, NVIDIA RTX 3090 24GB, Ollama',
        'list_price': 2499.00,
        'standard_price': 1800.00,
        'description_sale': (
            'De meest krachtige lokale AI-server in ons aanbod. Met 24GB VRAM draait deze machine '
            'modellen tot 70 miljard parameters — dezelfde schaalklasse als GPT-3.5, maar volledig '
            'in uw eigen beheer, op uw eigen netwerk, met uw eigen data.\n\n'
            'Ideaal voor organisaties met gevoelige data (juridisch, medisch, financieel) die de '
            'voordelen van AI willen zonder ook maar één byte naar een externe server te sturen. '
            'Ook geschikt als gedeelde AI-infrastructuur voor meerdere teams of bedrijven op '
            'dezelfde locatie.\n\n'
            'Wat u krijgt: hardware klaar voor gebruik, Ollama met meerdere modellen, Open WebUI '
            'met team-accounts en gebruikersbeheer, LiteLLM proxy voor API-integraties, en '
            'een installatierapport met aanbevelingen voor uw specifieke use case.\n\n'
            'Energieverbruik: ~200–350W onder belasting (24/7 ≈ €28–49/mnd bij €0,28/kWh). '
            'Refurbished — circulair aanbod van PV-consulting.'
        ),
    },
]


# ── AI Diensten ───────────────────────────────────────────────────────────────

AI_DIENSTEN = [
    {
        'ref': 'SRV-AI-01',
        'name': 'Lokale AI setup — Ollama + modellen installeren op uw hardware',
        'list_price': 149.00,
        'description_sale': (
            'U heeft de hardware, wij zorgen dat uw AI draait.\n\n'
            'We installeren Ollama op uw server of werkstation, laden de taalmodellen '
            'die passen bij uw gebruik (tekst, code, Nederlands, meertalig), en zetten '
            'Open WebUI op zodat iedereen in uw team meteen kan chatten met de AI — '
            'zonder technische kennis.\n\n'
            'Inclusief: Ollama installatie, twee modellen naar keuze, Open WebUI, '
            'basistest en korte handleiding. Forfait excl. BTW.'
        ),
    },
    {
        'ref': 'SRV-AI-02',
        'name': 'Privé AI assistent — Open WebUI met gebruikersaccounts en SSO',
        'list_price': 249.00,
        'description_sale': (
            'Een privé ChatGPT voor uw organisatie, volledig onder uw controle.\n\n'
            'We bouwen een gebruiksvriendelijke AI-omgeving op uw eigen netwerk: '
            'iedereen logt in met zijn eigen account (gekoppeld aan uw bestaande logins '
            'via SSO), heeft een eigen gespreksgeschiedenis, en de beheerder ziet '
            'welke modellen gebruikt worden.\n\n'
            'Uw medewerkers gebruiken AI voor hun dagelijkse taken — samenvatten, '
            'schrijven, vertalen, brainstormen — zonder dat er data naar externe '
            'servers gaat. Inclusief: Open WebUI setup, gebruikersbeheer, '
            'SSO-koppeling (optioneel), en handleiding voor eindgebruikers. '
            'Forfait excl. BTW.'
        ),
    },
    {
        'ref': 'SRV-AI-03',
        'name': 'AI in uw workflow — n8n + Ollama automatisering',
        'list_price': 299.00,
        'description_sale': (
            'Laat AI uw herhalende taken overnemen — volledig lokaal en automatisch.\n\n'
            'We koppelen uw lokale AI-server aan n8n (workflow-automatisering) zodat u '
            'taken kunt automatiseren zoals: inkomende e-mails categoriseren en '
            'samenvatten, documenten analyseren en doorsturen, klantberichten beantwoorden '
            'op basis van uw eigen kennisbank, of rapporten genereren vanuit uw data.\n\n'
            'Alles draait op uw eigen netwerk — geen data naar externe diensten. '
            'Inclusief: n8n installatie (indien nog niet aanwezig), drie AI-workflows '
            'naar keuze, en documentatie. Forfait excl. BTW.'
        ),
    },
    {
        'ref': 'SRV-AI-04',
        'name': 'Documentenanalyse met AI — RAG kennisbank op uw eigen data',
        'list_price': 399.00,
        'description_sale': (
            'Stel vragen aan uw eigen documenten — en krijg antwoorden met bronvermelding.\n\n'
            'RAG (Retrieval-Augmented Generation) laat u een AI-systeem bouwen dat uw '
            'bedrijfsdocumenten, handleidingen, contracten of kennisbanken "begrijpt". '
            'Medewerkers stellen vragen in gewone taal en krijgen precieze antwoorden '
            'met verwijzing naar het juiste document.\n\n'
            'Praktische toepassingen: onboarding van nieuwe medewerkers, technische '
            'support op basis van uw handleidingen, juridische of HR-vragen beantwoorden '
            'op basis van uw eigen beleidsdocumenten.\n\n'
            'Inclusief: vectordatabase setup (Qdrant of Chroma), documentenverwerking, '
            'AI-koppeling en een eenvoudige zoekinterface. Uw data verlaat uw netwerk nooit. '
            'Forfait excl. BTW; uitbreiding met extra documenttypen of integraties à €65/u.'
        ),
    },
    {
        'ref': 'SRV-AI-05',
        'name': 'Lokale AI beheer — Maandabonnement',
        'list_price': 29.00,
        'description_sale': (
            'Uw AI blijft up-to-date en goed afgesteld — zonder dat u er naar om hoeft te kijken.\n\n'
            'We houden uw Ollama-installatie bij: nieuwe en betere modellen beschikbaar stellen, '
            'performantieproblemen oplossen, schijfruimte bewaken en bij vragen bereikbaar zijn. '
            'Maandelijks een kort rapport over gebruik en eventuele aanbevelingen.\n\n'
            'Prijs per maand excl. BTW.'
        ),
    },
]


# ── Bijgewerkte beschrijvingen bestaande producten ────────────────────────────
# Mensentaal voor turnkey servers en backup-diensten

UPDATES = [
    ('HL-SRV-01', {
        'description_sale': (
            'Een volledige serveromgeving in een kast zo groot als een brooddoos.\n\n'
            'Deze refurbished Dell OptiPlex SFF draait Proxmox — software waarmee u '
            '2 tot 4 virtuele computers op één machine kunt laten draaien. Ideaal als '
            'u een eigen mailserver, fileserver of webapplicatie wilt hosten zonder '
            'te betalen voor cloudopslag.\n\n'
            'Wat u krijgt: hardware klaar voor gebruik, Proxmox geïnstalleerd, '
            'netwerkconfiguratie en basisbeveiliging. Uitbreidbaar met extra opslag.\n\n'
            'Verbruik: ~35–65W — minder dan een gloeilamp (24/7 ≈ €5–9/mnd bij €0,28/kWh). '
            'Refurbished Dell hardware — circulair aanbod via PV-consulting.'
        ),
    }),
    ('HL-SRV-02', {
        'description_sale': (
            'Krachtige virtualisatiehost voor wie serieus aan de slag wil met eigen servers.\n\n'
            'De Lenovo ThinkStation P520 is een werkpaardmachine: Xeon-processor, 32GB RAM '
            'en 1TB snelle opslag. Op Proxmox draait u gemakkelijk 6 tot 10 virtuele machines '
            'gelijktijdig — een testomgeving, een productieserver, een backup-target en meer, '
            'allemaal op één apparaat.\n\n'
            'Wat u krijgt: hardware klaar voor gebruik, Proxmox geïnstalleerd met cluster-'
            'voorbereiding en storage configuratie, zodat u meteen kunt beginnen.\n\n'
            'Verbruik: ~80–180W (24/7 ≈ €12–26/mnd bij €0,28/kWh). '
            'Refurbished Lenovo hardware — circulair aanbod via PV-consulting.'
        ),
    }),
    ('HL-SRV-03', {
        'description_sale': (
            'Uw backups zijn zo goed als uw backup-server.\n\n'
            'Deze dedicated backup-machine draait Proxmox Backup Server: software die '
            'automatisch dagelijkse backups maakt van al uw servers en virtuele machines, '
            'met slimme deduplicatie (alleen gewijzigde data wordt opgeslagen, zodat u '
            'veel meer backups kwijt kunt op dezelfde schijf).\n\n'
            'Wat u krijgt: hardware klaar voor gebruik, PBS geïnstalleerd, backup-jobs '
            'ingesteld voor uw Proxmox-omgeving, en een eerste testbackup uitgevoerd.\n\n'
            'Verbruik: ~35–55W (24/7 ≈ €5–8/mnd bij €0,28/kWh). '
            'Refurbished Dell hardware — circulair aanbod via PV-consulting.'
        ),
    }),
    ('HL-SRV-04', {
        'description_sale': (
            'Weten wat er gaande is in uw netwerk en op uw servers — zonder naar elke '
            'machine afzonderlijk te kijken.\n\n'
            'Deze dedicated monitoring-server draait Grafana (mooie dashboards), '
            'Prometheus (meet alles op uw netwerk) en Uptime Kuma (waarschuwt u als '
            'een dienst uitvalt). U ziet in één oogopslag CPU-gebruik, schijfruimte, '
            'netwerkverkeer en uptime — en ontvangt een melding als er iets misgaat.\n\n'
            'Wat u krijgt: hardware klaar voor gebruik, monitoring stack geïnstalleerd, '
            'basisdashboards voor netwerk en servers, en alerting ingesteld via e-mail.\n\n'
            'Verbruik: ~30–50W (24/7 ≈ €4–7/mnd bij €0,28/kWh). '
            'Refurbished Dell hardware — circulair aanbod via PV-consulting.'
        ),
    }),
    ('HL-SRV-05', {
        'description_sale': (
            'Uw eigen Dropbox of OneDrive — maar dan in uw eigen kantoor.\n\n'
            'TrueNAS SCALE zet een gewone computer om in een professionele fileserver: '
            'bestanden delen via Windows (SMB) of Mac (NFS), automatische snapshots '
            'zodat u per ongeluk gewiste bestanden kunt herstellen, en optionele '
            'replicatie naar een tweede locatie als extra veiligheid.\n\n'
            'Wat u krijgt: hardware klaar voor gebruik, TrueNAS geïnstalleerd, '
            'opslag geconfigureerd en netwerkkoppelingen ingesteld. Schijven apart '
            'te bestellen (BKP-DRIVE-01 of -02).\n\n'
            'Verbruik: ~35–60W (24/7 ≈ €5–9/mnd bij €0,28/kWh). '
            'Refurbished Dell hardware — circulair aanbod via PV-consulting.'
        ),
    }),
    ('SRV-BKP-01', {
        'description_sale': (
            'Weet u zeker dat uw data veilig is als uw computer morgen stopt?\n\n'
            'We analyseren uw huidige backup-situatie van a tot z: welke data wordt '
            'bewaard, hoe vaak, waar, en wat er verloren zou gaan bij een incident. '
            'Daarna krijgt u een helder rapport met concrete aanbevelingen — niet '
            'meer dan u nodig heeft, maar ook niet minder.\n\n'
            'Forfait excl. BTW. Inclusief schriftelijk rapport.'
        ),
    }),
    ('SRV-BKP-02', {
        'description_sale': (
            'We richten uw backup-oplossing in van begin tot eind.\n\n'
            'Of het nu gaat om een Synology NAS van de klant, een Proxmox Backup '
            'Server op refurbished hardware, of rclone-scripts voor automatische '
            'synchronisatie — we installeren de software, configureren de automatische '
            'taken en testen of de herstelstap effectief werkt. Want een backup die '
            'je niet kunt terugzetten is geen backup.\n\n'
            'Prijs per uur excl. BTW.'
        ),
    }),
    ('SRV-BKP-03', {
        'description_sale': (
            'Backups zijn zoals rookmelders: je denkt er niet aan tot het te laat is.\n\n'
            'We bewaken uw backup-jobs elke maand: zijn alle backups geslaagd? '
            'Is er voldoende schijfruimte? Worden de backups niet stilletjes ouder? '
            'Bij een probleem krijgt u meteen een melding — niet pas als u het nodig heeft.\n\n'
            'Inclusief kwartaalrapport met overzicht en aanbevelingen. '
            'Prijs per maand excl. BTW.'
        ),
    }),
    ('SRV-BKP-04', {
        'description_sale': (
            'Het ergste is al gebeurd — maar er is nog hoop.\n\n'
            'Bij dataverlies door een crash, ransomware of menselijke fout '
            'analyseren we de situatie en herstellen we uw bestanden of systemen '
            'vanuit de beschikbare backup. Snel, grondig en met zo weinig mogelijk verlies.\n\n'
            'Forfait voor standaard herstel; complexe gevallen worden afgerekend '
            'in regie à €65/u excl. BTW.'
        ),
    }),
    ('SRV-VIRT-01', {
        'description_sale': (
            'Eén server, meerdere computers — en u betaalt maar één keer stroom.\n\n'
            'Proxmox is de software die grote cloudproviders gebruiken om servers '
            'op te splitsen in virtuele machines. Wij installeren het op uw '
            'refurbished hardware zodat u hetzelfde kunt doen in uw eigen kantoor: '
            'een testomgeving naast een productieserver, of een mailserver naast '
            'uw boekhoudapplicatie — alles op één apparaat, netjes gescheiden.\n\n'
            'Inclusief netwerkconfiguratie, storage setup, basisbeveiliging en '
            'uw eerste VM of container. Forfait excl. BTW.'
        ),
    }),
    ('SRV-VIRT-03', {
        'description_sale': (
            'Applicaties deployen zoals de grote spelers — maar op uw eigen hardware.\n\n'
            'Docker laat u applicaties draaien in geïsoleerde containers: sneller, '
            'veiliger en makkelijker te beheren dan traditionele installaties. '
            'Coolify is de gebruiksvriendelijke laag erbovenop: via een web-interface '
            'deployt u applicaties met een paar klikken, met automatisch SSL en '
            'een reverse proxy.\n\n'
            'Inclusief Docker installatie, Coolify setup, SSL-configuratie '
            'en uw eerste applicatie-deployment. Forfait excl. BTW.'
        ),
    }),
    ('SRV-IT-01', {
        'description_sale': (
            'Voordat u investeert, moet u weten wat u al heeft — en wat het waard is.\n\n'
            'We maken een volledige inventaris van uw IT-omgeving: welke hardware '
            'er staat (inclusief leeftijd en wanneer vervanging zinvol is), welke '
            'software draait, hoe uw netwerk is ingericht en hoe het staat met '
            'uw beveiliging. Het resultaat is een helder rapport met een '
            'prioriteitenlijst — inclusief concrete circulaire vervangingsopties '
            'die goedkoper zijn dan nieuw en minder belastend voor het milieu.\n\n'
            'Forfait excl. BTW. Inclusief schriftelijk rapport.'
        ),
    }),
    ('SRV-IT-02', {
        'description_sale': (
            'Uw IT loopt gewoon — ook als u er niet aan denkt.\n\n'
            'We houden uw systemen bij: updates en patches installeren voor '
            'ze een probleem worden, servers en services monitoren op fouten, '
            'en proactief ingrijpen als er iets dreigt mis te gaan. '
            'Elke maand krijgt u een kort rapport met wat er is gedaan en '
            'of er actie nodig is.\n\n'
            'Inclusief tot 30 minuten remote interventie per maand. '
            'Prijs per maand excl. BTW.'
        ),
    }),
    ('SRV-MON-01', {
        'description_sale': (
            'Weten wat er gaande is in uw netwerk — voordat uw gebruikers '
            'u komen vertellen dat iets niet werkt.\n\n'
            'We bouwen een lokaal monitoring platform op uw eigen netwerk: '
            'Grafana toont overzichtelijke dashboards, Prometheus meet alles '
            'automatisch (CPU, geheugen, schijf, netwerk), en Uptime Kuma '
            'stuurt u een melding als een website of dienst uitvalt.\n\n'
            'Werkt op uw eigen hardware (onze HL-SRV-04 monitoring server '
            'of een bestaande machine). Uw monitoringdata verlaat uw netwerk nooit.\n\n'
            'Inclusief installatie, basisdashboards voor servers en netwerk, '
            'en alerting via e-mail. Forfait excl. BTW.'
        ),
    }),
    ('SRV-SEC-01', {
        'description_sale': (
            'Een netwerk zonder goede firewall is als een voordeur die op een '
            'kier blijft staan.\n\n'
            'We analyseren uw huidige firewallregels en configureren een '
            'gezonde netwerksegmentatie: gasten op een apart netwerk, '
            'servers afgeschermd van werkstations, alleen de poorten open '
            'die echt nodig zijn. Op uw UniFi-omgeving (UDM/USG) of '
            'pfSense/OPNsense.\n\n'
            'Forfait excl. BTW. Inclusief documentatie van de configuratie.'
        ),
    }),
    ('SRV-SEC-02', {
        'description_sale': (
            'Veilig inloggen op uw thuisnetwerk of kantoor, van waar u ook bent.\n\n'
            'We installeren Tailscale (zero-config, werkt overal) of WireGuard '
            '(traditioneel, volledig open source) als VPN-oplossing. Uw laptop '
            'of smartphone verbindt beveiligd met uw thuisnetwerk — '
            'of u nu op café bent, op hotel of bij een klant.\n\n'
            'Inclusief installatie op de server, koppeling van uw toestellen '
            'en een korte handleiding. Forfait excl. BTW.'
        ),
    }),
    ('SRV-HOST-01', {
        'description_sale': (
            'Uw eigen server, zonder de zorgen van een eigen server.\n\n'
            'We hosten een virtuele machine op de Hosting Local infrastructuur: '
            'u beslist wat erop draait, wij zorgen voor updates, dagelijkse backups, '
            'monitoring en ondersteuning. Uw data staat in België, op hardware '
            'die u kunt komen bekijken.\n\n'
            'Geen verborgen kosten, geen lock-in — u kunt uw VM op elk moment '
            'meenemen naar eigen hardware. Prijs per maand excl. BTW.'
        ),
    }),
    ('SRV-HOST-02', {
        'description_sale': (
            'Uw website snel, betrouwbaar en in Belgisch beheer.\n\n'
            'We hosten uw WordPress of statische website op de Hosting Local '
            'infrastructuur. SSL-certificaat automatisch vernieuwd, dagelijkse '
            'backups, updates beheerd, en 99,9% uptime gegarandeerd. '
            'Als er iets is, bent u niet afhankelijk van een buitenlandse '
            'helpdesk in een andere tijdzone.\n\n'
            'Uw data staat in België. Prijs per maand excl. BTW.'
        ),
    }),
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    odoo = OdooClient()

    print("\n── Categorieën ──────────────────────────────────────────────────")
    diensten_id = odoo.get_or_create_cat('Diensten')
    it_hw_id    = odoo.get_or_create_cat('IT-hardware')
    ai_svc_id   = odoo.get_or_create_cat('Lokale AI', parent_id=diensten_id)
    ai_hw_id    = odoo.get_or_create_cat('Lokale AI Servers', parent_id=it_hw_id)

    ai_srv_img = svg_ai_server()
    ai_svc_img = svg_ai_service()

    print("\n── Turnkey AI Servers ───────────────────────────────────────────")
    for p in AI_SERVERS:
        odoo.upsert_product(p['ref'], {
            'name':             p['name'],
            'categ_id':         ai_hw_id,
            'list_price':       p['list_price'],
            'standard_price':   p['standard_price'],
            'type':             'consu',
            'description_sale': p['description_sale'],
            'x_status':         'beschikbaar',
        }, placeholder_b64=ai_srv_img)

    print("\n── AI Diensten ──────────────────────────────────────────────────")
    for s in AI_DIENSTEN:
        odoo.upsert_product(s['ref'], {
            'name':             s['name'],
            'categ_id':         ai_svc_id,
            'list_price':       s['list_price'],
            'type':             'service',
            'invoice_policy':   'order',
            'description_sale': s['description_sale'],
            'x_status':         'beschikbaar',
        }, placeholder_b64=ai_svc_img)

    print("\n── Beschrijvingen bijwerken (mensentaal) ────────────────────────")
    for ref, vals in UPDATES:
        recs = odoo.search_read('product.template',
                                [('default_code', '=', ref)], ['id', 'name'])
        if recs:
            odoo.write('product.template', [recs[0]['id']], vals)
            print(f"  ✓ {ref}: beschrijving bijgewerkt")
        else:
            print(f"  ~ {ref}: niet gevonden, overgeslagen")

    print("\n── Klaar ─────────────────────────────────────────────────────────")
    print(f"{len(AI_SERVERS)} AI-servers (IT-hardware > Lokale AI Servers)")
    print(f"{len(AI_DIENSTEN)} AI-diensten (Diensten > Lokale AI)")
    print(f"{len(UPDATES)} bestaande beschrijvingen bijgewerkt naar mensentaal")


if __name__ == '__main__':
    main()
