from odoo import models, fields, api


class CoworkingWorkspaceEquipment(models.Model):
    _name = 'coworking.workspace.equipment'
    _description = 'Geïnstalleerde uitrusting per werkplek'
    _order = 'workspace_id, sequence, id'

    workspace_id = fields.Many2one(
        'coworking.workspace',
        string='Werkplek',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        'product.product',
        string='Item',
        help='Bv. bureau, bureaustoel, monitorarm, monitor, cordless desktop uit de catalogus.',
    )
    description = fields.Char(
        string='Omschrijving',
        required=True,
        help='Vrije tekst, bv. "Dubbele monitorarm" — wordt automatisch ingevuld vanuit het item.',
    )
    quantity = fields.Integer(string='Aantal', default=1)
    installed_date = fields.Date(string='Geïnstalleerd op')
    note = fields.Char(string='Notitie')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.description:
            self.description = self.product_id.name
