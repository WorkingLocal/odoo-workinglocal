from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    rental_contract_id = fields.Many2one(
        'rental.contract',
        string='Huurcontract',
        ondelete='set null',
        index=True,
        copy=False,
    )
