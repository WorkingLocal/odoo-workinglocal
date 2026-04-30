from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


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
        tracking=True,
    )
    workspace_type = fields.Selection(
        related='workspace_id.workspace_type',
        store=True,
        readonly=True,
    )

    # Pakket (blokkeert meerdere ruimten tegelijk)
    package_id = fields.Many2one(
        'coworking.package',
        string='Pakket',
        ondelete='set null',
        tracking=True,
    )

    # Type boeking
    booking_type = fields.Selection([
        ('extern', 'Extern'),
        ('intern', 'Intern'),
        ('geblokkeerd', 'Geblokkeerd'),
    ], string='Type', default='extern', required=True, tracking=True)

    # Dagdeel (VM/NM/AV/dag) — enkel relevant bij slot-gebaseerde werkplekken
    slot = fields.Selection([
        ('vm', 'Voormiddag'),
        ('nm', 'Namiddag'),
        ('av', 'Avond'),
        ('dag', 'Volledige dag'),
    ], string='Dagdeel', tracking=True)

    start_datetime = fields.Datetime(string='Van', required=True, tracking=True)
    end_datetime = fields.Datetime(string='Tot', required=True, tracking=True)
    duration_hours = fields.Float(
        string='Duur (uur)',
        compute='_compute_duration',
        store=True,
    )
    attendees = fields.Integer(string='Aantal personen', default=1)

    state = fields.Selection([
        ('draft', 'Aanvraag'),
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
        ('package', 'Pakketprijs'),
    ], string='Facturatietype', required=True, default='contribution')

    contribution_amount = fields.Monetary(
        string='Bedrag (€)',
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

    # ── Computed ──────────────────────────────────────────────────────────────

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

    # ── Onchange ──────────────────────────────────────────────────────────────

    @api.onchange('package_id')
    def _onchange_package_id(self):
        if self.package_id:
            ws_list = self.package_id.workspace_ids
            if ws_list and (not self.workspace_id or self.workspace_id not in ws_list):
                self.workspace_id = ws_list[0]
            if self.package_id.price and not self.contribution_amount:
                self.contribution_amount = self.package_id.price
                self.billing_type = 'package'

    @api.onchange('slot', 'workspace_id')
    def _onchange_slot(self):
        if not self.slot or not self.workspace_id:
            return
        ws = self.workspace_id
        if ws.booking_granularity != 'slot':
            return
        base_date = self.start_datetime.date() if self.start_datetime else fields.Date.today()
        start_h, end_h = ws.get_slot_times(self.slot)

        def float_to_hm(h):
            hh = int(h)
            mm = int(round((h - hh) * 60))
            return hh, mm

        s_hh, s_mm = float_to_hm(start_h)
        e_hh, e_mm = float_to_hm(end_h)
        self.start_datetime = datetime.combine(base_date, datetime.min.time().replace(hour=s_hh, minute=s_mm))
        self.end_datetime = datetime.combine(base_date, datetime.min.time().replace(hour=e_hh, minute=e_mm))

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nieuw') == 'Nieuw':
                vals['name'] = self.env['ir.sequence'].next_by_code('coworking.reservation') or 'Nieuw'
        return super().create(vals_list)

    # ── Constraints ───────────────────────────────────────────────────────────

    @api.constrains('start_datetime', 'end_datetime')
    def _check_dates(self):
        for rec in self:
            if rec.end_datetime <= rec.start_datetime:
                raise ValidationError(_('Eindtijd moet na starttijd liggen.'))

    @api.constrains('start_datetime', 'end_datetime', 'workspace_id', 'package_id', 'state')
    def _check_overlap(self):
        for rec in self:
            if rec.state == 'cancelled':
                continue

            # Alle ruimten die deze reservatie blokkeert
            blocked_ws_ids = set()
            if rec.workspace_id:
                blocked_ws_ids.add(rec.workspace_id.id)
            if rec.package_id:
                blocked_ws_ids.update(rec.package_id.workspace_ids.ids)
            if not blocked_ws_ids:
                continue

            time_domain = [
                ('id', '!=', rec.id),
                ('state', 'not in', ['cancelled', 'draft']),
                ('start_datetime', '<', rec.end_datetime),
                ('end_datetime', '>', rec.start_datetime),
            ]

            # Check: directe werkplek-overlap (enkel voor capaciteit=1 ruimten)
            direct_blocked = self.search(time_domain + [
                ('workspace_id', 'in', list(blocked_ws_ids)),
            ])
            for conflict in direct_blocked:
                if conflict.workspace_id.capacity == 1:
                    raise ValidationError(_(
                        'Ruimte "%s" is al gereserveerd in deze periode (%s).',
                        conflict.workspace_id.name, conflict.name,
                    ))

            # Check: pakket-reservaties die onze ruimten overlappen
            pkg_reservations = self.search(time_domain + [
                ('package_id', '!=', False),
            ])
            for pkg_res in pkg_reservations:
                pkg_ws_ids = set(pkg_res.package_id.workspace_ids.ids)
                overlap_ids = pkg_ws_ids & blocked_ws_ids
                if overlap_ids:
                    ws_names = ', '.join(
                        self.env['coworking.workspace'].browse(list(overlap_ids)).mapped('name')
                    )
                    raise ValidationError(_(
                        'Ruimte(n) "%s" zijn al gereserveerd via pakket "%s" in deze periode.',
                        ws_names, pkg_res.package_id.name,
                    ))

    # ── Actions ───────────────────────────────────────────────────────────────

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
                'name': f'Reservatie {self.workspace_id.name or self.package_id.name} — {self.name}',
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
