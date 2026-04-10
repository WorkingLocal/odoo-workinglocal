from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class CoworkingReservation(models.Model):
    _name = 'coworking.reservation'
    _description = 'Werkplekreservatie'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc'

    name = fields.Char(
        string='Referentie',
        readonly=True,
        copy=False,
        default='Nieuw',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Klant',
        required=True,
        tracking=True,
    )
    workspace_id = fields.Many2one(
        'coworking.workspace',
        string='Werkplek',
        required=True,
        tracking=True,
    )
    workspace_type = fields.Selection(
        related='workspace_id.workspace_type',
        store=True,
        readonly=True,
    )

    start_datetime = fields.Datetime(string='Van', required=True, tracking=True)
    end_datetime = fields.Datetime(string='Tot', required=True, tracking=True)
    duration_hours = fields.Float(
        string='Duur (uur)',
        compute='_compute_duration',
        store=True,
    )
    attendees = fields.Integer(string='Aantal personen', default=1)

    state = fields.Selection([
        ('draft', 'Concept'),
        ('confirmed', 'Bevestigd'),
        ('done', 'Afgerond'),
        ('cancelled', 'Geannuleerd'),
    ], default='draft', tracking=True, string='Status')

    # Bijdrage / facturatie
    billing_type = fields.Selection([
        ('free_trial', 'Gratis proefperiode'),
        ('contribution', 'Vrije bijdrage'),
        ('fixed_hourly', 'Uurtarief'),
        ('fixed_daily', 'Dagtarief'),
        ('fixed_monthly', 'Maandtarief'),
    ], string='Facturatietype', required=True, default='contribution')

    contribution_amount = fields.Monetary(
        string='Bijdrage (€)',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.EUR'),
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Factuur',
        readonly=True,
        copy=False,
    )
    invoice_state = fields.Selection(
        related='invoice_id.payment_state',
        string='Betaalstatus',
        readonly=True,
    )

    notes = fields.Text(string='Notities')
    is_trial = fields.Boolean(
        string='Proefperiode',
        compute='_compute_is_trial',
        store=True,
    )

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime:
                delta = rec.end_datetime - rec.start_datetime
                rec.duration_hours = delta.total_seconds() / 3600
            else:
                rec.duration_hours = 0

    @api.depends('billing_type')
    def _compute_is_trial(self):
        for rec in self:
            rec.is_trial = rec.billing_type == 'free_trial'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nieuw') == 'Nieuw':
                vals['name'] = self.env['ir.sequence'].next_by_code('coworking.reservation') or 'Nieuw'
        return super().create(vals_list)

    @api.constrains('start_datetime', 'end_datetime')
    def _check_dates(self):
        for rec in self:
            if rec.end_datetime <= rec.start_datetime:
                raise ValidationError(_('Eindtijd moet na starttijd liggen.'))

    @api.constrains('start_datetime', 'end_datetime', 'workspace_id', 'state')
    def _check_overlap(self):
        for rec in self:
            if rec.state == 'cancelled':
                continue
            overlapping = self.search([
                ('id', '!=', rec.id),
                ('workspace_id', '=', rec.workspace_id.id),
                ('state', 'not in', ['cancelled', 'draft']),
                ('start_datetime', '<', rec.end_datetime),
                ('end_datetime', '>', rec.start_datetime),
            ])
            if overlapping and rec.workspace_id.capacity == 1:
                raise ValidationError(_(
                    'Werkplek "%s" is al gereserveerd in deze periode.',
                    rec.workspace_id.name,
                ))

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            return
        if self.billing_type == 'free_trial' or self.contribution_amount == 0:
            return

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': f'Reservatie {self.workspace_id.name} — {self.name}',
                'quantity': 1,
                'price_unit': self.contribution_amount,
            })],
        })
        self.invoice_id = invoice
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
        }
