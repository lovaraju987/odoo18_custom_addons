from odoo import http, fields
from odoo.http import request
import json
from datetime import date

API_KEY_HEADER = "x-api-key"
MODEL_NAME = 'sale.order'  # Model being accessed

class SalesAPI(http.Controller):

    @http.route('/api/sales_orders', auth='none', type='http', methods=['GET'], csrf=False)
    def get_sales_orders(self, **kwargs):
        api_key_value = request.httprequest.headers.get(API_KEY_HEADER)
        ip_address = request.httprequest.remote_addr
        query_string = request.httprequest.query_string.decode('utf-8')

        # 🔒 Validate API key
        api_key = request.env['res.api.key'].sudo().search([
            ('key', '=', api_key_value),
            ('active', '=', True),
            '|', ('expiry_date', '=', False),
                 ('expiry_date', '>=', date.today())
        ], limit=1)

        if not api_key:
            request.env['api.access.log'].sudo().create({
                'api_key_id': False,
                'endpoint': '/api/sales_orders',
                'status': 'unauthorized',
                'ip_address': ip_address,
                'query_string': query_string,
            })
            return request.make_response(
                json.dumps({"error": "Unauthorized"}),
                headers=[('Content-Type', 'application/json')],
                status=401
            )

        # ❌ Model access check
        if not api_key.is_admin and MODEL_NAME not in api_key.allowed_model_ids.mapped('model'):
            request.env['api.access.log'].sudo().create({
                'api_key_id': api_key.id,
                'endpoint': '/api/sales_orders',
                'status': 'forbidden',
                'ip_address': ip_address,
                'query_string': query_string,
            })
            return request.make_response(
                json.dumps({"error": f"Access to model '{MODEL_NAME}' is not allowed for this API key"}),
                headers=[('Content-Type', 'application/json')],
                status=403
            )

        # 🔍 Field selection logic
        requested_fields = request.params.get('fields')
        if requested_fields:
            requested_fields = requested_fields.split(',')
        else:
            requested_fields = ['name', 'date_order', 'customer', 'amount_total']

        # 🔁 Role-based filtering
        domain = []
        if not api_key.is_admin and api_key.user_id:
            domain.append(('user_id', '=', api_key.user_id.id))

        orders = request.env[MODEL_NAME].sudo().search(domain, limit=100)

        result = []
        for o in orders:
            entry = {}
            if 'name' in requested_fields:
                entry['name'] = o.name
            if 'date_order' in requested_fields:
                entry['date_order'] = o.date_order.isoformat()
            if 'customer' in requested_fields:
                entry['customer'] = o.partner_id.name
            if 'amount_total' in requested_fields:
                entry['amount_total'] = o.amount_total
            result.append(entry)

        # ✅ Log access
        request.env['api.access.log'].sudo().create({
            'api_key_id': api_key.id,
            'endpoint': '/api/sales_orders',
            'status': 'success',
            'ip_address': ip_address,
            'query_string': query_string,
        })

        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )
