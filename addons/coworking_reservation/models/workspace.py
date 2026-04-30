from odoo import models, fields, api

WORKSPACE_TYPES = [
    ('hot_desk', 'Hot Desk'),
    ('fixed_desk', 'Vaste Plek'),
    ('meeting_room', 'Vergaderzaal'),
    ('focus_zone', 'Focus Zone'),
    ('event', 'Eventdeelname'),
    ('hybrid_meeting', 'Hybride Meetingroom'),
    ('muziekzaal', 'Muziekzaal'),
    ('productiestudio', 'Productiestudio'),
    ('foyer', 'Foyer'),
    ('muziekstudio', 'Muziekstudio'),
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

    # Boekingseenheid en dagdelen
    booking_granularity = fields.Selection([
        ('day', 'Volledige dag'),
        ('slot', 'Dagdelen (VM / NM / AV)'),
    ], string='Boekingseenheid', default='day')

    slot_vm_start = fields.Float(string='VM start (u)', default=8.0, digits=(4, 2))
    slot_vm_end = fields.Float(string='VM einde (u)', default=13.0, digits=(4, 2))
    slot_nm_start = fields.Float(string='NM start (u)', default=13.0, digits=(4, 2))
    slot_nm_end = fields.Float(string='NM einde (u)', default=18.0, digits=(4, 2))
    slot_av_start = fields.Float(string='AV start (u)', default=18.0, digits=(4, 2))
    slot_av_end = fields.Float(string='AV einde (u)', default=23.0, digits=(4, 2))

    # Beschikbare weekdagen
    avail_mon = fields.Boolean(string='Maandag', default=True)
    avail_tue = fields.Boolean(string='Dinsdag', default=True)
    avail_wed = fields.Boolean(string='Woensdag', default=True)
    avail_thu = fields.Boolean(string='Donderdag', default=True)
    avail_fri = fields.Boolean(string='Vrijdag', default=True)
    avail_sat = fields.Boolean(string='Zaterdag', default=False)
    avail_sun = fields.Boolean(string='Zondag', default=False)

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

    def is_available_on_weekday(self, weekday_num):
        """weekday_num: 0=Monday ... 6=Sunday"""
        day_map = {
            0: self.avail_mon, 1: self.avail_tue, 2: self.avail_wed,
            3: self.avail_thu, 4: self.avail_fri,
            5: self.avail_sat, 6: self.avail_sun,
        }
        return day_map.get(weekday_num, False)

    def get_slot_times(self, slot):
        """Returns (start_hour_float, end_hour_float) for a given slot key."""
        if slot == 'vm':
            return self.slot_vm_start, self.slot_vm_end
        if slot == 'nm':
            return self.slot_nm_start, self.slot_nm_end
        if slot == 'av':
            return self.slot_av_start, self.slot_av_end
        if slot == 'dag':
            return self.slot_vm_start, self.slot_av_end
        return 0.0, 24.0

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
