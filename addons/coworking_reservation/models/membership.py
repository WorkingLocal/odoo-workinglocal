from odoo import models, fields, api
from datetime import date, timedelta


class CoworkingMembership(models.Model):
    _name = 'coworking.membership'
    _description = 'Lidmaatschap / Proefperiode'
    _inherit = ['mail.thread']
    _order = 'start_date desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Klant',
        required=True,
        tracking=True,
    )
    state = fields.Selection([
        ('trial', 'Proefperiode'),
        ('active', 'Actief'),
        ('expired', 'Verlopen'),
    ], default='trial', tracking=True, string='Status')

    start_date = fields.Date(string='Startdatum', default=fields.Date.today)
    trial_end_date = fields.Date(
        string='Einde proefperiode',
        compute='_compute_trial_end',
        store=True,
    )
    trial_days = fields.Integer(
        string='Proefperiode (dagen)',
        default=7,
    )
    is_in_trial = fields.Boolean(
        string='In proefperiode',
        compute='_compute_is_in_trial',
    )

    reservation_ids = fields.One2many(
        'coworking.reservation',
        'partner_id',
        string='Reservaties',
    )
    reservation_count = fields.Integer(
        compute='_compute_reservation_count',
    )

    @api.depends('start_date', 'trial_days')
    def _compute_trial_end(self):
        for rec in self:
            if rec.start_date:
                rec.trial_end_date = rec.start_date + timedelta(days=rec.trial_days)

    @api.depends('trial_end_date', 'state')
    def _compute_is_in_trial(self):
        today = date.today()
        for rec in self:
            rec.is_in_trial = (
                rec.state == 'trial' and
                rec.trial_end_date and
                rec.trial_end_date >= today
            )

    @api.depends('reservation_ids')
    def _compute_reservation_count(self):
        for rec in self:
            rec.reservation_count = len(rec.reservation_ids)
