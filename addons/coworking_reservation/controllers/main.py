from odoo import http
from odoo.http import request
from datetime import datetime, date


class CoworkingWebsite(http.Controller):

    @http.route('/werkplekken', type='http', auth='public', website=True)
    def workspace_overview(self, **kwargs):
        workspaces = request.env['coworking.workspace'].sudo().search([
            ('is_active', '=', True),
        ], order='sequence, name')
        return request.render('coworking_reservation.website_workspaces', {
            'workspaces': workspaces,
        })

    @http.route('/werkplekken/<int:workspace_id>/reserveer', type='http', auth='user', website=True)
    def workspace_booking(self, workspace_id, **kwargs):
        workspace = request.env['coworking.workspace'].sudo().browse(workspace_id)
        if not workspace.exists() or not workspace.is_active:
            return request.not_found()
        return request.render('coworking_reservation.website_booking_form', {
            'workspace': workspace,
            'suggestions': workspace.contribution_suggestions.split(',') if workspace.contribution_suggestions else [],
        })

    @http.route('/werkplekken/reserveer/bevestig', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def booking_confirm(self, **post):
        workspace = request.env['coworking.workspace'].sudo().browse(int(post.get('workspace_id')))
        partner = request.env.user.partner_id

        billing_type = post.get('billing_type', 'contribution')
        contribution = float(post.get('contribution_amount', 0)) if billing_type == 'contribution' else 0

        reservation = request.env['coworking.reservation'].sudo().create({
            'partner_id': partner.id,
            'workspace_id': workspace.id,
            'start_datetime': post.get('start_datetime'),
            'end_datetime': post.get('end_datetime'),
            'attendees': int(post.get('attendees', 1)),
            'billing_type': billing_type,
            'contribution_amount': contribution,
        })
        reservation.action_confirm()

        return request.redirect(f'/mijn/reservaties/{reservation.id}')
