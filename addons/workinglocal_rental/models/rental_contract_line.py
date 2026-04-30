from odoo import models, fields, api


class RentalContractLine(models.Model):
    _name = 'rental.contract.line'
    _description = 'Huurcontract regel'
    _order = 'sequence, id'

    contract_id = fields.Many2one(
        'rental.contract',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)

    workspace_id = fields.Many2one(
        'coworking.workspace',
        string='Ruimte / Locatie',
        help='Koppel aan een werkplek of locatie. Vul manueel in voor materialen.',
    )
    description = fields.Char(string='Omschrijving', required=True)
    qty = fields.Float(string='Aantal', default=1.0)
    price_month = fields.Monetary(string='Prijs / maand', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        related='contract_id.currency_id',
        store=True,
    )

    # ── Onchange ──────────────────────────────────────────────────────────────

    @api.onchange('workspace_id')
    def _onchange_workspace(self):
        if self.workspace_id:
            self.description = self.workspace_id.name
            if self.workspace_id.monthly_rate:
                self.price_month = self.workspace_id.monthly_rate
