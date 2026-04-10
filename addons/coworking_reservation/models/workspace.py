from odoo import models, fields, api

WORKSPACE_TYPES = [
    ('hot_desk', 'Hot Desk'),
    ('fixed_desk', 'Vaste Plek'),
    ('meeting_room', 'Vergaderzaal'),
    ('focus_zone', 'Focus Zone'),
    ('event', 'Eventdeelname'),
    ('hybrid_meeting', 'Hybride Meetingroom'),
]


class CoworkingWorkspace(models.Model):
    _name = 'coworking.workspace'
    _description = 'Werkplek'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(string='Naam', required=True, tracking=True)
    sequence = fields.Integer(default=10)
    workspace_type = fields.Selection(
        WORKSPACE_TYPES,
        string='Type',
        required=True,
        tracking=True,
    )
    description = fields.Html(string='Omschrijving')
    capacity = fields.Integer(string='Capaciteit (personen)', default=1)
    is_active = fields.Boolean(string='Actief', default=True)
    image = fields.Image(string='Foto')

    # Locatie
    floor = fields.Char(string='Verdieping / Zone')
    amenity_ids = fields.Many2many(
        'coworking.amenity',
        string='Voorzieningen',
    )

    # Tarieven
    hourly_rate = fields.Monetary(string='Uurtarief', currency_field='currency_id')
    daily_rate = fields.Monetary(string='Dagtarief', currency_field='currency_id')
    monthly_rate = fields.Monetary(string='Maandtarief', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.EUR'),
    )

    # Vrije bijdrage instellingen
    contribution_enabled = fields.Boolean(
        string='Vrije bijdrage',
        default=False,
        help='Laat klanten zelf een bijdrage kiezen.',
    )
    contribution_suggestions = fields.Char(
        string='Voorgestelde bedragen (€)',
        default='5,10,15',
        help='Kommagescheiden lijst van voorgestelde bijdragen.',
    )
    contribution_min = fields.Monetary(
        string='Minimale bijdrage',
        currency_field='currency_id',
        default=0,
    )

    # Xibo display instellingen
    show_on_signage = fields.Boolean(
        string='Tonen op schermen (Xibo)',
        default=True,
    )
    signage_label = fields.Char(
        string='Schermtekst',
        help='Korte naam voor op de Xibo displays. Laat leeg om standaardnaam te gebruiken.',
    )

    # Hybride meetingroom specifiek
    has_interactive_display = fields.Boolean(string='Interactief scherm aanwezig')
    display_brand = fields.Char(string='Scherm / Type')

    reservation_ids = fields.One2many(
        'coworking.reservation',
        'workspace_id',
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

    def get_availability_for_xibo(self):
        """Geeft bezettingsstatus terug voor Xibo JSON endpoint."""
        from datetime import datetime, timedelta
        now = datetime.now()
        today_end = now.replace(hour=23, minute=59, second=59)

        active_reservations = self.env['coworking.reservation'].search([
            ('workspace_id', '=', self.id),
            ('state', 'in', ['confirmed']),
            ('start_datetime', '<=', today_end),
            ('end_datetime', '>=', now),
        ])

        booked_capacity = sum(r.attendees for r in active_reservations) if active_reservations else 0
        is_occupied = bool(active_reservations)

        next_res = self.env['coworking.reservation'].search([
            ('workspace_id', '=', self.id),
            ('state', '=', 'confirmed'),
            ('start_datetime', '>', now),
        ], order='start_datetime asc', limit=1)

        return {
            'id': self.id,
            'name': self.signage_label or self.name,
            'type': self.workspace_type,
            'capacity': self.capacity,
            'is_occupied': is_occupied,
            'booked': min(booked_capacity, self.capacity),
            'available': max(self.capacity - booked_capacity, 0),
            'next_reservation': next_res.start_datetime.isoformat() if next_res else None,
        }


class CoworkingAmenity(models.Model):
    _name = 'coworking.amenity'
    _description = 'Voorziening'

    name = fields.Char(string='Naam', required=True)
    icon = fields.Char(string='Icoon (Bootstrap)', help='bv. bi-wifi, bi-projector')
