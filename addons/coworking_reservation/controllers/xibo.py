import json
from datetime import datetime
from odoo import http
from odoo.http import request, Response


class XiboAvailabilityController(http.Controller):
    """
    Publiek JSON endpoint voor Xibo CMS DataSets.
    Xibo haalt dit op via een Dataset URL connector op interval.

    Endpoint: GET /api/workspaces/availability
    Auth: optionele API key via query parameter ?key=...
    """

    @http.route('/api/workspaces/availability', type='http', auth='public', methods=['GET'], csrf=False)
    def workspace_availability(self, **kwargs):
        # Optionele API key bescherming
        api_key = request.env['ir.config_parameter'].sudo().get_param('coworking.xibo_api_key', '')
        if api_key:
            provided_key = kwargs.get('key', '')
            if provided_key != api_key:
                return Response(
                    json.dumps({'error': 'Unauthorized'}),
                    status=401,
                    content_type='application/json',
                )

        workspaces = request.env['coworking.workspace'].sudo().search([
            ('is_active', '=', True),
            ('show_on_signage', '=', True),
        ], order='sequence, name')

        data = {
            'updated_at': datetime.now().isoformat(),
            'workspaces': [ws.get_availability_for_xibo() for ws in workspaces],
        }

        response = Response(
            json.dumps(data, default=str),
            content_type='application/json',
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Cache-Control'] = 'no-cache, max-age=60'
        return response
