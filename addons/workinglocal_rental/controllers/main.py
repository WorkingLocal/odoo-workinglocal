from odoo import http
from odoo.http import request

_FLOOR_ORDER = [
    'Verdiep -1', 'Verdiep 0', 'Verdiep +1', 'Verdiep +2', 'Verdiep +3', 'Verdiep +4', 'Verdiep +5',
]

_STATUS_LABELS = {
    'verhuurd': 'Verhuurd',
    'bezet_nu': 'Bezet nu',
    'gereserveerd_vandaag': 'Gereserveerd vandaag',
    'vrij': 'Vrij',
}

# De handmatig ingeschatte zone-posities bleken niet kloppen met de werkelijke
# plattegrond. Terug naar de eenvoudige kaartjeslijst tot er een correcte
# versie is (voorbereid in Claude Design) — de positiedata zelf blijft
# gewoon staan op coworking.workspace, enkel het tonen van het achtergrond-
# beeld + overlays wordt hier tijdelijk uitgeschakeld.
SHOW_INTERACTIVE_MAP = False


class WorkinglocalFloorplan(http.Controller):

    @http.route('/vloerplan', type='http', auth='public', website=True)
    def floorplan(self, **kwargs):
        workspaces = request.env['coworking.workspace'].sudo().search([
            ('is_active', '=', True),
            ('floor', '!=', False),
        ], order='floor, sequence, name')

        floors = {}
        mobile = []
        for ws in workspaces:
            info = ws.get_floorplan_status()
            tile = {
                'workspace': ws,
                'status': info['status'],
                'status_label': _STATUS_LABELS.get(info['status'], info['status']),
                'tenant': info['tenant'],
                'presence': info['presence'],
                'x': ws.floorplan_x,
                'y': ws.floorplan_y,
                'w': ws.floorplan_w or 10.0,
                'h': ws.floorplan_h or 10.0,
            }
            if ws.floor and ws.floor.startswith('Mobiel'):
                mobile.append(tile)
            else:
                floors.setdefault(ws.floor, {'tiles': [], 'image_id': None})
                floors[ws.floor]['tiles'].append(tile)
                if SHOW_INTERACTIVE_MAP and ws.floorplan_attachment_id:
                    floors[ws.floor]['image_id'] = ws.floorplan_attachment_id.id

        def floor_sort_key(floor_name):
            try:
                return _FLOOR_ORDER.index(floor_name)
            except ValueError:
                return len(_FLOOR_ORDER)

        floor_sections = [
            {'name': name, 'tiles': data['tiles'], 'image_id': data['image_id']}
            for name, data in sorted(floors.items(), key=lambda kv: floor_sort_key(kv[0]))
        ]

        return request.render('workinglocal_rental.website_floorplan', {
            'floor_sections': floor_sections,
            'mobile_tiles': mobile,
        })
