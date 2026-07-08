from datetime import datetime

from odoo import fields, models, api, _


class CoworkingWorkspace(models.Model):
    _inherit = 'coworking.workspace'

    workspace_type = fields.Selection(
        selection_add=[
            ('atelier', 'Atelier'),
            ('appartement', 'Appartement'),
        ],
        ondelete={
            'atelier': 'cascade',
            'appartement': 'cascade',
        },
    )

    active_rental_count = fields.Integer(
        compute='_compute_active_rental_count',
        string='Actieve huurcontracten',
    )

    @api.depends()
    def _compute_active_rental_count(self):
        for rec in self:
            lines = self.env['rental.contract.line'].search([
                ('workspace_id', '=', rec.id),
                ('contract_id.state', '=', 'active'),
            ])
            rec.active_rental_count = len(lines.mapped('contract_id'))

    def action_view_rental_contracts(self):
        self.ensure_one()
        contract_ids = self.env['rental.contract.line'].search([
            ('workspace_id', '=', self.id),
        ]).mapped('contract_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Huurcontracten'),
            'res_model': 'rental.contract',
            'domain': [('id', 'in', contract_ids)],
            'view_mode': 'list,form',
        }

    def get_floorplan_status(self):
        """Combineert verhuurstatus (rental.contract) en reservatiestatus (vandaag)
        voor het schematisch vloerplan. Aanwezigheid = None zolang er geen
        geconsenteerde toestellen met last_seen-data zijn (fase 3, UniFi-poller)."""
        self.ensure_one()
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59)

        active_line = self.env['rental.contract.line'].search([
            ('workspace_id', '=', self.id),
            ('contract_id.state', '=', 'active'),
        ], limit=1)

        today_res = self.env['coworking.reservation'].search([
            ('state', '=', 'confirmed'),
            ('start_datetime', '<=', today_end),
            ('end_datetime', '>=', today_start),
            '|',
                ('workspace_id', '=', self.id),
                ('package_id.workspace_ids', 'in', [self.id]),
        ], order='start_datetime', limit=1)

        occupied_now = bool(today_res and today_res.start_datetime <= now <= today_res.end_datetime)

        if active_line:
            status = 'verhuurd'
        elif occupied_now:
            status = 'bezet_nu'
        elif today_res:
            status = 'gereserveerd_vandaag'
        else:
            status = 'vrij'

        presence = None
        if active_line:
            devices = self.env['rental.tenant.device'].search([
                ('contract_id', '=', active_line.contract_id.id),
                ('consent_given', '=', True),
            ])
            if devices:
                presence = any(d.is_present for d in devices)

        return {
            'status': status,
            'tenant': active_line.contract_id.partner_id.name if active_line else None,
            'presence': presence,
        }
