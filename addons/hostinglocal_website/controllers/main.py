from odoo import http
from odoo.http import request


class HostingLocalWebsite(http.Controller):

    @http.route('/hostinglocal/contact/submit', type='http', auth='public',
                methods=['POST'], website=True, csrf=True)
    def contact_submit(self, **post):
        """Verwerkt het contactformulier en maakt een CRM lead aan."""
        naam      = post.get('naam', '').strip()
        bedrijf   = post.get('bedrijf', '').strip()
        email     = post.get('email', '').strip()
        telefoon  = post.get('telefoon', '').strip()
        interesse = post.get('interesse', '').strip()
        bericht   = post.get('bericht', '').strip()

        if not naam or not email:
            return request.redirect('/contact?error=1')

        beschrijving = f"Interesse: {interesse}\n\n{bericht}" if interesse else bericht

        request.env['crm.lead'].sudo().create({
            'name':          f"Website — {naam}" + (f" ({bedrijf})" if bedrijf else ''),
            'contact_name':  naam,
            'partner_name':  bedrijf or naam,
            'email_from':    email,
            'phone':         telefoon,
            'description':   beschrijving,
            'source_id':     request.env['utm.source'].sudo().search(
                                 [('name', '=', 'Website')], limit=1).id or False,
            'website_id':    request.website.id,
            'tag_ids':       [(6, 0, request.env['crm.tag'].sudo().search(
                                 [('name', '=', 'Hosting Local')], limit=1).ids)],
        })

        return request.redirect('/contact/bedankt')

    @http.route('/contact/bedankt', type='http', auth='public', website=True)
    def contact_bedankt(self, **kw):
        return request.render('hostinglocal_website.hl_page_bedankt')
