from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CoworkingPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'reservation_count' in counters:
            values['reservation_count'] = request.env['coworking.reservation'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('state', '!=', 'cancelled'),
            ])
        return values

    @http.route('/mijn/reservaties', type='http', auth='user', website=True)
    def portal_reservations(self, **kwargs):
        partner = request.env.user.partner_id
        reservations = request.env['coworking.reservation'].sudo().search([
            ('partner_id', '=', partner.id),
        ], order='start_datetime desc')
        return request.render('coworking_reservation.portal_reservations', {
            'reservations': reservations,
        })

    @http.route('/mijn/reservaties/<int:reservation_id>', type='http', auth='user', website=True)
    def portal_reservation_detail(self, reservation_id, **kwargs):
        reservation = request.env['coworking.reservation'].sudo().browse(reservation_id)
        if not reservation.exists() or reservation.partner_id != request.env.user.partner_id:
            return request.not_found()
        return request.render('coworking_reservation.portal_reservation_detail', {
            'reservation': reservation,
        })
