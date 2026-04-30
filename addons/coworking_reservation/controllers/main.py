from odoo import http
from odoo.http import request
from datetime import datetime, date, timedelta


# Weekday labels Dutch (Monday=0)
_WEEKDAY_NL = ['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo']

_WS_TYPE_LABELS = [
    ('hot_desk', 'Hot Desk'), ('fixed_desk', 'Vaste Plek'),
    ('meeting_room', 'Vergaderzaal'), ('focus_zone', 'Focus Zone'),
    ('event', 'Eventdeelname'), ('hybrid_meeting', 'Hybride Meetingroom'),
    ('muziekzaal', 'Muziekzaal'), ('productiestudio', 'Productiestudio'),
    ('foyer', 'Foyer'), ('muziekstudio', 'Muziekstudio'),
]

_SLOT_LABELS = {'vm': 'VM', 'nm': 'NM', 'av': 'AV'}


def _float_to_time(h):
    hh = int(h)
    mm = int(round((h - hh) * 60))
    from datetime import time
    return time(hh, mm)


class CoworkingWebsite(http.Controller):

    @http.route('/werkplekken', type='http', auth='public', website=True)
    def workspace_overview(self, **kwargs):
        workspaces = request.env['coworking.workspace'].sudo().search([
            ('is_active', '=', True),
        ], order='sequence, name')
        return request.render('coworking_reservation.website_workspaces', {
            'workspaces': workspaces,
        })

    @http.route('/werkplekken/<int:workspace_id>/reserveer', type='http', auth='user', website=True)
    def workspace_booking(self, workspace_id, **kwargs):
        workspace = request.env['coworking.workspace'].sudo().browse(workspace_id)
        if not workspace.exists() or not workspace.is_active:
            return request.not_found()
        return request.render('coworking_reservation.website_booking_form', {
            'workspace': workspace,
            'suggestions': workspace.contribution_suggestions.split(',') if workspace.contribution_suggestions else [],
        })

    @http.route('/werkplekken/reserveer/bevestig', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def booking_confirm(self, **post):
        workspace = request.env['coworking.workspace'].sudo().browse(int(post.get('workspace_id')))
        partner = request.env.user.partner_id

        billing_type = post.get('billing_type', 'contribution')
        contribution = float(post.get('contribution_amount', 0)) if billing_type == 'contribution' else 0

        reservation = request.env['coworking.reservation'].sudo().create({
            'partner_id': partner.id,
            'workspace_id': workspace.id,
            'start_datetime': post.get('start_datetime'),
            'end_datetime': post.get('end_datetime'),
            'attendees': int(post.get('attendees', 1)),
            'billing_type': billing_type,
            'contribution_amount': contribution,
            'booking_type': 'extern',
        })
        # Externe aanvragen blijven als 'draft' voor admin-bevestiging

        return request.redirect(f'/mijn/reservaties/{reservation.id}')

    # ── Beschikbaarheidskalender ──────────────────────────────────────────

    @http.route('/beschikbaarheid', type='http', auth='public', website=True)
    def availability_calendar(self, week=0, **kwargs):
        try:
            week_offset = int(week)
        except (ValueError, TypeError):
            week_offset = 0

        today = date.today()
        # Monday of the target week
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        week_end = week_start + timedelta(days=6)

        workspaces = request.env['coworking.workspace'].sudo().search([
            ('is_active', '=', True),
        ], order='sequence, name')

        packages = request.env['coworking.package'].sudo().search([
            ('active', '=', True),
        ], order='sequence, name')

        # Build day headers
        days = []
        for i in range(7):
            d = week_start + timedelta(days=i)
            days.append({
                'date': d,
                'date_str': d.strftime('%d/%m'),
                'label': _WEEKDAY_NL[d.weekday()],
                'weekday': d.weekday(),
            })

        # Fetch all relevant reservations for the week
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(week_end, datetime.max.time())

        reservations = request.env['coworking.reservation'].sudo().search([
            ('state', 'not in', ['cancelled', 'draft']),
            ('start_datetime', '<=', week_end_dt),
            ('end_datetime', '>=', week_start_dt),
        ])

        # Index reservations per workspace per date
        # ws_reservations[ws_id][date] = list of reservations
        ws_reservations = {}
        for res in reservations:
            ws_ids = set()
            if res.workspace_id:
                ws_ids.add(res.workspace_id.id)
            if res.package_id:
                ws_ids.update(res.package_id.workspace_ids.ids)
            for ws_id in ws_ids:
                if ws_id not in ws_reservations:
                    ws_reservations[ws_id] = {}
                # Mark each day this reservation spans
                r_start = res.start_datetime.date()
                r_end = res.end_datetime.date()
                cur = r_start
                while cur <= r_end:
                    if cur not in ws_reservations[ws_id]:
                        ws_reservations[ws_id][cur] = []
                    ws_reservations[ws_id][cur].append(res)
                    cur += timedelta(days=1)

        # Build rows
        rows = []
        for ws in workspaces:
            cells = []
            for day in days:
                d = day['date']
                avail_day = ws.is_available_on_weekday(d.weekday())
                day_res = ws_reservations.get(ws.id, {}).get(d, [])

                if ws.booking_granularity == 'slot':
                    slots = []
                    for slot_key, slot_label in [('vm', 'VM'), ('nm', 'NM'), ('av', 'AV')]:
                        start_h, end_h = ws.get_slot_times(slot_key)
                        slot_start = datetime.combine(d, _float_to_time(start_h))
                        slot_end = datetime.combine(d, _float_to_time(end_h))
                        taken_res = [
                            r for r in day_res
                            if r.start_datetime < slot_end and r.end_datetime > slot_start
                        ]
                        partner_name = taken_res[0].partner_id.name if taken_res else ''
                        slots.append({
                            'key': slot_key,
                            'label': slot_label,
                            'avail_day': avail_day,
                            'taken': bool(taken_res),
                            'partner': partner_name if taken_res else '',
                        })
                    cells.append({'slots': slots, 'avail_day': avail_day, 'taken': bool(day_res)})
                else:
                    partner_name = day_res[0].partner_id.name if day_res else ''
                    cells.append({
                        'avail_day': avail_day,
                        'taken': bool(day_res),
                        'partner': partner_name,
                        'slots': [],
                    })

            rows.append({'workspace': ws, 'cells': cells})

        return request.render('coworking_reservation.website_availability', {
            'week_start': week_start,
            'week_end': week_end,
            'week_offset': week_offset,
            'days': days,
            'rows': rows,
            'packages': packages,
            'ws_type_labels': _WS_TYPE_LABELS,
        })
