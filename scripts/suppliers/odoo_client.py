"""
Gedeelde Odoo XML-RPC client voor leveranciersimportscripts.

Gebruik:
    from odoo_client import OdooClient, PV_BTW, curl_bytes, b64, svg_placeholder

    odoo = OdooClient()
    cat_id = odoo.get_or_create_cat('Beeldschermen')
    tmpl_id = odoo.create('product.template', {...})
"""

import xmlrpc.client
import subprocess
import base64
import re
import time
from html import unescape
from getpass import getpass

# ── Constanten ────────────────────────────────────────────────────────────────
PV_BTW   = 1.21   # Belgisch BTW-tarief standaard goederen
PV_BASE  = 'https://pv-consulting.com/products/'
PV_IMG   = 'https://pv-consulting.com/images/'

PV_IMG_SKIP = {
    "pvconsultingMainLogo.png", "pvconsultingInvertedColor.png",
    "1946488.png", "1451574.png", "1170678.png", "2590818.png",
    "Digital_Inline_Green.png",
}

# ── Odoo client ───────────────────────────────────────────────────────────────
class OdooClient:
    def __init__(self,
                 url='https://odoo.workinglocal.be',
                 db='workinglocal',
                 username='info@workinglocal.be',
                 password=None):
        self.url      = url
        self.db       = db
        self.username = username
        self.password = password or input("Odoo wachtwoord: ")

        common  = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = common.authenticate(db, username, self.password, {})
        if not self.uid:
            raise RuntimeError("Odoo login mislukt")
        print(f"Ingelogd als uid={self.uid} op {url}")
        self._models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    def exe(self, model, method, args=None, kw=None):
        return self._models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args or [], kw or {}
        )

    def search_read(self, model, domain, fields):
        return self.exe(model, 'search_read', [domain], {'fields': fields})

    def create(self, model, vals):
        return self.exe(model, 'create', [vals])

    def write(self, model, ids, vals):
        return self.exe(model, 'write', [ids, vals])

    def get_or_create_cat(self, name, parent_id=None):
        domain = [('name', '=', name)]
        if parent_id:
            domain.append(('parent_id', '=', parent_id))
        res = self.search_read('product.category', domain, ['id'])
        if res:
            return res[0]['id']
        vals = {'name': name}
        if parent_id:
            vals['parent_id'] = parent_id
        cid = self.create('product.category', vals)
        print(f"  ✓ Categorie: {name}")
        return cid

    def get_or_create_attribute(self, name, values):
        """Haal attribuut op of maak aan, voeg ontbrekende waarden toe."""
        res = self.search_read('product.attribute', [('name', '=', name)], ['id'])
        attr_id = res[0]['id'] if res else self.create('product.attribute',
            {'name': name, 'create_variant': 'no_variant'})
        for v in values:
            vres = self.search_read('product.attribute.value',
                [('name', '=', v), ('attribute_id', '=', attr_id)], ['id'])
            if not vres:
                self.create('product.attribute.value',
                    {'name': v, 'attribute_id': attr_id})
                print(f"  ✓ {name}: {v}")
        return attr_id

    def upsert_product(self, ref, vals, images=None, placeholder_b64=None):
        """
        Maak product aan als het nog niet bestaat (op default_code).
        Geeft altijd het template-id terug.

        - vals: dict met alle product-velden (name, categ_id, list_price, ...)
        - images: lijst van (filename_or_url, bytes) tuples voor galerij
        - placeholder_b64: base64-string voor placeholder-afbeelding
        """
        existing = self.search_read('product.template',
            [('default_code', '=', ref)], ['id', 'name'])
        if existing:
            print(f"  ~ Bestaat al: {ref} — {existing[0]['name'][:50]}")
            return existing[0]['id']

        vals.setdefault('default_code', ref)
        vals.setdefault('sale_ok', True)
        tmpl_id = self.create('product.template', vals)
        print(f"  ✓ {ref}: {vals.get('name', '')[:60]}")

        if images:
            upload_images(self, tmpl_id, images)
        elif placeholder_b64:
            self.write('product.template', [tmpl_id], {'image_1920': placeholder_b64})

        return tmpl_id


# ── HTTP helpers ──────────────────────────────────────────────────────────────
def curl_bytes(url):
    r = subprocess.run(["curl", "-sf", "--max-time", "20", url], capture_output=True)
    return r.stdout if r.returncode == 0 else b''

def b64(data):
    return base64.b64encode(data).decode('utf-8')


# ── pv-consulting scraper ─────────────────────────────────────────────────────
def scrape_pv_page(slug):
    """
    Scrape een pv-consulting.com productpagina.
    Geeft dict terug met: pv_name, description_sale, website_description,
                          standard_price (excl. BTW), images (lijst filenames)
    """
    html = curl_bytes(PV_BASE + slug).decode('utf-8', errors='replace')
    if len(html) < 500:
        return {}

    result = {}

    m = re.search(r'<h2[^>]*u-text-1[^>]*>([^<]+)', html)
    if m:
        result['pv_name'] = unescape(m.group(1).strip())

    m = re.search(r'u-product-desc[^>]*>\s*([^<]{5,})', html)
    if m:
        result['description_sale'] = unescape(m.group(1).strip())

    m = re.search(r'u-product-full-desc[^>]*>\s*([^<]{5,})', html)
    if m:
        result['website_description'] = '<p>' + unescape(m.group(1).strip()) + '</p>'

    m = re.search(r'u-price[^>]*>\s*€\s*([\d.,]+)', html)
    if m:
        try:
            price_incl = float(m.group(1).replace(',', '.'))
            result['standard_price'] = round(price_incl / PV_BTW, 2)
        except ValueError:
            pass

    filenames = re.findall(r'<img[^>]+src=["\']\.\.\/images\/([^"\']+)["\']', html)
    seen = set()
    result['images'] = [
        f for f in filenames
        if f not in PV_IMG_SKIP and not (f in seen or seen.add(f))
    ]

    return result


def upload_images(odoo, tmpl_id, images):
    """Upload lijst van bestandsnamen als product-afbeeldingen via pv-consulting CDN."""
    for i, fname in enumerate(images):
        data = curl_bytes(PV_IMG + fname)
        if not data:
            continue
        if i == 0:
            odoo.write('product.template', [tmpl_id], {'image_1920': b64(data)})
        else:
            odoo.create('product.image', {
                'product_tmpl_id': tmpl_id,
                'image_1920': b64(data),
                'name': fname,
            })
        time.sleep(0.15)


# ── SVG placeholders ──────────────────────────────────────────────────────────
_SVG_ICONS = {
    'wifi': (
        '<circle cx="200" cy="230" r="20" fill="#F5B800"/>'
        '<path d="M140,180 Q200,130 260,180" stroke="#F5B800" stroke-width="14" fill="none" stroke-linecap="round"/>'
        '<path d="M100,145 Q200,75 300,145" stroke="#F5B800" stroke-width="14" fill="none" stroke-linecap="round" opacity="0.7"/>'
        '<path d="M60,110 Q200,20 340,110" stroke="#F5B800" stroke-width="14" fill="none" stroke-linecap="round" opacity="0.4"/>',
        'WiFi & Internet'
    ),
    'focus': (
        '<circle cx="200" cy="200" r="120" stroke="#F5B800" stroke-width="12" fill="none"/>'
        '<circle cx="200" cy="200" r="80" stroke="#F5B800" stroke-width="12" fill="none" opacity="0.7"/>'
        '<circle cx="200" cy="200" r="40" stroke="#F5B800" stroke-width="12" fill="none" opacity="0.4"/>'
        '<circle cx="200" cy="200" r="12" fill="#F5B800"/>',
        'Focussessies'
    ),
    'av': (
        '<rect x="60" y="130" width="210" height="140" rx="16" fill="none" stroke="#F5B800" stroke-width="14"/>'
        '<polygon points="290,145 340,110 340,290 290,255" fill="#F5B800" opacity="0.85"/>'
        '<circle cx="155" cy="200" r="35" fill="none" stroke="#F5B800" stroke-width="10"/>'
        '<circle cx="155" cy="200" r="14" fill="#F5B800"/>',
        'AV & Studio'
    ),
    'logistiek': (
        '<rect x="40" y="150" width="200" height="120" rx="10" fill="none" stroke="#F5B800" stroke-width="14"/>'
        '<path d="M240,175 L240,270 L340,270 L340,230 L310,175 Z" stroke="#F5B800" stroke-width="14" fill="none" stroke-linejoin="round"/>'
        '<line x1="40" y1="270" x2="340" y2="270" stroke="#F5B800" stroke-width="14"/>'
        '<circle cx="100" cy="280" r="22" fill="#1A2E5A" stroke="#F5B800" stroke-width="10"/>'
        '<circle cx="280" cy="280" r="22" fill="#1A2E5A" stroke="#F5B800" stroke-width="10"/>',
        'Logistiek'
    ),
    'verhuur': (
        '<circle cx="160" cy="190" r="80" stroke="#F5B800" stroke-width="14" fill="none"/>'
        '<circle cx="160" cy="190" r="35" fill="#F5B800" opacity="0.3"/>'
        '<line x1="222" y1="228" x2="330" y2="310" stroke="#F5B800" stroke-width="20" stroke-linecap="round"/>'
        '<line x1="285" y1="275" x2="305" y2="255" stroke="#F5B800" stroke-width="14" stroke-linecap="round"/>'
        '<line x1="310" y1="293" x2="330" y2="273" stroke="#F5B800" stroke-width="14" stroke-linecap="round"/>',
        'Verhuur'
    ),
}

def svg_placeholder(icon_key):
    """Genereer base64-gecodeerde SVG-placeholder in Working Local huisstijl."""
    shapes, label = _SVG_ICONS[icon_key]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">'
        '<rect width="400" height="400" fill="#1A2E5A"/>'
        f'{shapes}'
        f'<text x="200" y="360" font-family="Arial,sans-serif" font-size="22" font-weight="bold"'
        f' text-anchor="middle" fill="#F5B800" opacity="0.9">{label}</text>'
        '</svg>'
    )
    return b64(svg.encode('utf-8'))
