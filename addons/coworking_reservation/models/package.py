from odoo import models, fields, api


class CoworkingPackage(models.Model):
    _name = 'coworking.package'
    _description = 'Reservatiepakket'
    _order = 'sequence, name'

    name = fields.Char(string='Naam', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Omschrijving')

    workspace_ids = fields.Many2many(
        'coworking.workspace',
        string='Ruimten',
        help='Alle ruimten die gelijktijdig geblokkeerd worden bij een pakket-reservatie.',
    )

    price = fields.Monetary(string='Prijs')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.EUR'),
    )

    # Weekdag restricties (welke dagen is dit pakket boekbaar)
    avail_mon = fields.Boolean(string='Maandag', default=True)
    avail_tue = fields.Boolean(string='Dinsdag', default=True)
    avail_wed = fields.Boolean(string='Woensdag', default=True)
    avail_thu = fields.Boolean(string='Donderdag', default=True)
    avail_fri = fields.Boolean(string='Vrijdag', default=True)
    avail_sat = fields.Boolean(string='Zaterdag', default=False)
    avail_sun = fields.Boolean(string='Zondag', default=False)

    reservation_ids = fields.One2many(
        'coworking.reservation',
        'package_id',
        string='Reservaties',
    )
    reservation_count = fields.Integer(
        compute='_compute_reservation_count',
        string='# Reservaties',
    )

    @api.depends('reservation_ids')
    def _compute_reservation_count(self):
        for rec in self:
            rec.reservation_count = len(rec.reservation_ids)

    def is_available_on_weekday(self, weekday_num):
        """weekday_num: 0=Monday ... 6=Sunday"""
        day_map = {
            0: self.avail_mon, 1: self.avail_tue, 2: self.avail_wed,
            3: self.avail_thu, 4: self.avail_fri,
            5: self.avail_sat, 6: self.avail_sun,
        }
        return day_map.get(weekday_num, False)
