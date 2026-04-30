import json
from datetime import datetime, date
from odoo import http
from odoo.http import request, Response


_WS_TYPE_LABELS = {
    'hot_desk': 'Hot Desk', 'fixed_desk': 'Vaste Plek',
    'meeting_room': 'Vergaderzaal', 'focus_zone': 'Focus Zone',
    'event': 'Eventdeelname', 'hybrid_meeting': 'Hybride Meetingroom',
    'muziekzaal': 'Muziekzaal', 'productiestudio': 'Productiestudio',
    'foyer': 'Foyer', 'muziekstudio': 'Muziekstudio',
}

_SLOT_LABELS = {'vm': 'Voormiddag', 'nm': 'Namiddag', 'av': 'Avond', 'dag': 'Volledige dag'}


def _fmt_time(dt):
    return dt.strftime('%H:%M') if dt else ''


def _build_today_data(workspaces):
    """Bouwt signage-data voor vandaag. Returns (workspace_cards, upcoming_agenda)."""
    now = datetime.now()
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    all_res = request.env['coworking.reservation'].sudo().search([
        ('state', 'not in', ['cancelled', 'draft']),
        ('start_datetime', '<=', today_end),
        ('end_datetime', '>=', today_start),
    ], order='start_datetime asc')

    ws_res_index = {}
    for res in all_res:
        ws_ids = set()
        if res.workspace_id:
            ws_ids.add(res.workspace_id.id)
        if res.package_id:
            ws_ids.update(res.package_id.workspace_ids.ids)
        for ws_id in ws_ids:
            ws_res_index.setdefault(ws_id, []).append(res)

    workspace_cards = []
    for ws in workspaces:
        day_res = ws_res_index.get(ws.id, [])
        current_res = next((r for r in day_res if r.start_datetime <= now <= r.end_datetime), None)
        next_res = next((r for r in day_res if r.start_datetime > now), None)

        workspace_cards.append({
            'id': ws.id,
            'name': ws.signage_label or ws.name,
            'type_label': _WS_TYPE_LABELS.get(ws.workspace_type, ws.workspace_type),
            'is_occupied': bool(current_res) and current_res.booking_type != 'geblokkeerd',
            'blocked': bool(current_res) and current_res.booking_type == 'geblokkeerd',
            'current': {
                'partner': current_res.partner_id.name,
                'start': _fmt_time(current_res.start_datetime),
                'end': _fmt_time(current_res.end_datetime),
                'slot_label': _SLOT_LABELS.get(current_res.slot, '') if current_res.slot else '',
            } if current_res else None,
            'next': {
                'partner': next_res.partner_id.name,
                'start': _fmt_time(next_res.start_datetime),
                'end': _fmt_time(next_res.end_datetime),
            } if next_res else None,
            'capacity': ws.capacity,
        })

    seen_ids = set()
    upcoming = []
    for res in all_res:
        if res.id in seen_ids or res.end_datetime <= now:
            continue
        seen_ids.add(res.id)
        ws_name = (res.workspace_id.signage_label or res.workspace_id.name) if res.workspace_id \
                  else (res.package_id.name if res.package_id else '?')
        upcoming.append({
            'start': _fmt_time(res.start_datetime),
            'end': _fmt_time(res.end_datetime),
            'room': ws_name,
            'partner': res.partner_id.name,
            'booking_type': res.booking_type,
        })

    return workspace_cards, upcoming[:8]


class XiboAvailabilityController(http.Controller):

    @http.route('/api/workspaces/availability', type='http', auth='public', methods=['GET'], csrf=False)
    def workspace_availability(self, **kwargs):
        workspaces = request.env['coworking.workspace'].sudo().search([
            ('is_active', '=', True),
            ('show_on_signage', '=', True),
        ], order='sequence, name')

        workspace_cards, upcoming = _build_today_data(workspaces)

        response = Response(
            json.dumps({
                'updated_at': datetime.now().isoformat(),
                'workspaces': [ws.get_availability_for_xibo() for ws in workspaces],
                'today_schedule': workspace_cards,
                'upcoming': upcoming,
            }, default=str),
            content_type='application/json',
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Cache-Control'] = 'no-cache, max-age=60'
        return response

    @http.route('/signage/reservaties', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def signage_reservaties(self, **kwargs):
        workspaces = request.env['coworking.workspace'].sudo().search([
            ('is_active', '=', True),
            ('show_on_signage', '=', True),
        ], order='sequence, name')

        workspace_cards, upcoming = _build_today_data(workspaces)

        response = request.render('coworking_reservation.signage_reservaties', {
            'workspaces': workspace_cards,
            'upcoming': upcoming,
        })
        response.headers['Cache-Control'] = 'no-cache, no-store'
        return response
