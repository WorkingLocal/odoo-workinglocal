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
            }
            if ws.floor and ws.floor.startswith('Mobiel'):
                mobile.append(tile)
            else:
                floors.setdefault(ws.floor, []).append(tile)

        def floor_sort_key(floor_name):
            try:
                return _FLOOR_ORDER.index(floor_name)
            except ValueError:
                return len(_FLOOR_ORDER)

        floor_sections = [
            {'name': name, 'tiles': tiles}
            for name, tiles in sorted(floors.items(), key=lambda kv: floor_sort_key(kv[0]))
        ]

        return request.render('workinglocal_rental.website_floorplan', {
            'floor_sections': floor_sections,
            'mobile_tiles': mobile,
        })
