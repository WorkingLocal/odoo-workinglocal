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
