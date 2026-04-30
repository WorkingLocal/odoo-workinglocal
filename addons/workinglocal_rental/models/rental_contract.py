from odoo import models, fields, api, _
from odoo.exceptions import UserError

_MONTHS_NL = {
    1: 'januari', 2: 'februari', 3: 'maart', 4: 'april',
    5: 'mei', 6: 'juni', 7: 'juli', 8: 'augustus',
    9: 'september', 10: 'oktober', 11: 'november', 12: 'december',
}


class RentalContract(models.Model):
    _name = 'rental.contract'
    _description = 'Huurcontract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, name desc'

    name = fields.Char(
        string='Referentie',
        readonly=True,
        copy=False,
        default='Nieuw',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Huurder',
        required=True,
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Concept'),
        ('active', 'Actief'),
        ('ended', 'Beëindigd'),
    ], default='draft', tracking=True, string='Status')

    date_start = fields.Date(string='Startdatum', required=True, tracking=True)
    date_end = fields.Date(string='Einddatum', tracking=True, help='Leeg laten voor open einde.')

    invoice_day = fields.Integer(
        string='Facturatiedag',
        default=1,
        help='Dag van de maand waarop de maandfactuur aangemaakt wordt (1–28).',
    )

    line_ids = fields.One2many('rental.contract.line', 'contract_id', string='Huurregels')

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.EUR'),
    )
    total_monthly = fields.Monetary(
        string='Totaal per maand',
        compute='_compute_total_monthly',
        store=True,
        currency_field='currency_id',
    )

    invoice_ids = fields.One2many('account.move', 'rental_contract_id', string='Facturen')
    invoice_count = fields.Integer(compute='_compute_invoice_count', string='# Facturen')

    note = fields.Text(string='Opmerkingen')

    # ── Computed ──────────────────────────────────────────────────────────────

    @api.depends('line_ids.price_month', 'line_ids.qty')
    def _compute_total_monthly(self):
        for rec in self:
            rec.total_monthly = sum(l.price_month * l.qty for l in rec.line_ids)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nieuw') == 'Nieuw':
                vals['name'] = self.env['ir.sequence'].next_by_code('rental.contract') or 'Nieuw'
        return super().create(vals_list)

    def action_activate(self):
        self.write({'state': 'active'})

    def action_end(self):
        self.write({'state': 'ended'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    # ── Facturatie ────────────────────────────────────────────────────────────

    def action_generate_invoice(self):
        self.ensure_one()
        if self.state != 'active':
            raise UserError(_('Enkel actieve contracten kunnen gefactureerd worden.'))
        if not self.line_ids:
            raise UserError(_('Voeg minstens één huurlijn toe voor je een factuur aanmaakt.'))

        today = fields.Date.today()
        month_label = f"{_MONTHS_NL[today.month]} {today.year}"

        invoice_lines = [(0, 0, {
            'name': f"{line.description} — {month_label}",
            'quantity': line.qty,
            'price_unit': line.price_month,
        }) for line in self.line_ids]

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': today,
            'rental_contract_id': self.id,
            'invoice_line_ids': invoice_lines,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Factuur'),
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Facturen'),
            'res_model': 'account.move',
            'domain': [('rental_contract_id', '=', self.id)],
            'view_mode': 'list,form',
            'context': {'default_rental_contract_id': self.id},
        }
