from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import re

_MAC_RE = re.compile(r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$')
_PRESENCE_WINDOW_MINUTES = 5


class RentalTenantDevice(models.Model):
    _name = 'rental.tenant.device'
    _description = 'Toestel huurder (aanwezigheidsdetectie, opt-in)'
    _order = 'contract_id, device_label'

    contract_id = fields.Many2one(
        'rental.contract',
        string='Huurcontract',
        required=True,
        ondelete='cascade',
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Huurder',
        related='contract_id.partner_id',
        store=True,
    )
    device_label = fields.Char(string='Omschrijving', help='Bv. "iPhone Jan"')
    device_mac = fields.Char(string='MAC-adres', required=True)

    consent_given = fields.Boolean(string='Toestemming gegeven', default=False)
    consent_date = fields.Date(string='Datum toestemming')
    consent_text = fields.Text(
        string='Toestemmingstekst',
        help='Kopie van de tekst die de huurder te zien kreeg bij het geven van toestemming — '
             'voor juridische traceerbaarheid.',
    )

    last_seen = fields.Datetime(
        string='Laatst gezien',
        readonly=True,
        help='Wordt bijgewerkt door de UniFi-aanwezigheidspoller (fase 3 — nog niet actief).',
    )
    is_present = fields.Boolean(
        string='Aanwezig',
        compute='_compute_is_present',
    )

    @api.depends('last_seen')
    def _compute_is_present(self):
        cutoff = fields.Datetime.now() - timedelta(minutes=_PRESENCE_WINDOW_MINUTES)
        for rec in self:
            rec.is_present = bool(rec.last_seen and rec.last_seen >= cutoff)

    @api.onchange('device_mac')
    def _onchange_device_mac(self):
        if self.device_mac:
            self.device_mac = self.device_mac.strip().upper().replace('-', ':')

    @api.constrains('device_mac')
    def _check_device_mac(self):
        for rec in self:
            if rec.device_mac and not _MAC_RE.match(rec.device_mac):
                raise ValidationError(_(
                    'Ongeldig MAC-adres formaat: "%s" (verwacht bv. AA:BB:CC:DD:EE:FF).',
                    rec.device_mac,
                ))

    @api.onchange('consent_given')
    def _onchange_consent_given(self):
        if self.consent_given and not self.consent_date:
            self.consent_date = fields.Date.today()
