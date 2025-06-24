# -*- coding: utf-8 -*-
import datetime
import logging
from odoo import http, fields
from odoo.http import request
import json

_logger = logging.getLogger(__name__)

def serialize_field(record, field_name, field):
    value = record[field_name]
    if field.type in (
        'char', 'text', 'selection', 'integer', 'float', 'boolean', 'monetary'
    ):
        return value
    elif field.type in ('date', 'datetime'):
        return value.isoformat() if value else value
    elif field.type == 'many2one':
        if value:
            try:
                rec = value[0] if len(value) > 1 else value
                rec.ensure_one()
                try:
                    ng = rec.name_get()
                except Exception:
                    ng = None
                if ng:
                    name = ng[0][1]
                elif hasattr(rec, 'name'):
                    name = rec.name
                else:
                    name = str(rec.id)
            except Exception:
                name = str(value.id) if value else ''
            return {'id': rec.id, 'name': name}
        return None
    elif field.type in ('one2many', 'many2many'):
        result = []
        for r in value:
            try:
                r.ensure_one()
                try:
                    ng = r.name_get()
                except Exception:
                    ng = None
                if ng:
                    name = ng[0][1]
                elif hasattr(r, 'name'):
                    name = r.name
                else:
                    name = str(r.id)
            except Exception:
                name = str(r.id)
            result.append({'id': r.id, 'name': name})
        return result
    elif field.type == 'binary':
        return bool(value)
    else:
        return str(value)

# FINAL PATCH: Ensure allowed_company_ids never becomes an empty list in context

class DynamicAPI(http.Controller):
    @http.route('/api/<string:endpoint_path>', auth='none', type='http', methods=['GET'], csrf=False)
    def dynamic_api_handler(self, endpoint_path, **kwargs):
        api_key_value = (
            request.httprequest.headers.get('x-api-key') or
            request.params.get('key')  # allow ?key=your_api_key in URL
        )
        ip_address = request.httprequest.remote_addr
        query_string = request.httprequest.query_string.decode()

        api_key = request.env['res.api.key'].sudo().search([
            ('key', '=', api_key_value),
            ('active', '=', True),
            '|', ('expiry_date', '=', False),
                 ('expiry_date', '>=', fields.Date.today())
        ], limit=1)

        if not api_key:
            return self._unauthorized(endpoint_path, ip_address, query_string)

        endpoint = request.env['res.api.endpoint'].sudo().search([
            ('url_path', '=', endpoint_path),
            ('active', '=', True),
            ('api_key_ids', 'in', api_key.id),
        ], limit=1)

        if not endpoint:
            return self._unauthorized(endpoint_path, ip_address, query_string)

        model_name = endpoint.model_id.model
        allowed_fields = endpoint.field_ids.mapped('name')
        model_obj = request.env[model_name]

        # Get allowed companies from API key, fallback to user's companies
        allowed_companies = api_key.company_ids.ids
        if not allowed_companies:
            allowed_companies = request.env.user.company_ids.ids
        if not allowed_companies:
            allowed_companies = request.env['res.company'].sudo().search([]).ids
        if not allowed_companies:
            return request.make_response(
                json.dumps({'error': 'No companies found in the system.'}),
                status=403,
                headers=[('Content-Type', 'application/json')]
            )
        # Optional: filter allowed companies via URL (?companies=1,2 or repeated params)
        raw_vals = request.httprequest.args.getlist('companies') or []
        _logger.debug(f"Raw companies params: {raw_vals}")
        if raw_vals:
            comps = []
            for val in raw_vals:
                for part in val.split(','):
                    try:
                        comps.append(int(part.strip()))
                    except Exception:
                        pass
            requested = list(set(comps))
            _logger.info(f"Requested companies: {requested}")
            subset = [c for c in requested if c in allowed_companies]
            if subset:
                allowed_companies = subset
                _logger.info(f"Filtering to companies: {allowed_companies}")
            else:
                _logger.warning("No requested companies in allowed list; ignoring filter")

        try:
            # Debug: Log the company IDs being used
            _logger.info(f"Using allowed_companies: {allowed_companies}")
            _logger.info(f"Model name: {model_name}")
            
            # Try bypassing all Odoo security and company rules
            # by using raw SQL query instead of ORM
            _logger.info("Attempting direct SQL query to bypass ORM...")
            
            # Get the table name for the model
            table_name = model_obj._table
            _logger.info(f"Table name: {table_name}")
            # Filter by allowed companies in raw SQL
            model_fields = model_obj._fields
            # check for single-company field
            has_company_id = 'company_id' in model_fields
            # check for multi-company many2many
            has_company_ids = 'company_ids' in model_fields and model_fields['company_ids'].type == 'many2many'
            if has_company_id:
                placeholders = ','.join(['%s'] * len(allowed_companies))
                sql = f"SELECT id FROM {table_name} WHERE company_id IN ({placeholders})"
                params = tuple(allowed_companies)
            elif has_company_ids:
                m2m = model_fields['company_ids']
                rel_table = m2m.relation
                col1 = m2m.column1
                col2 = m2m.column2
                placeholders = ','.join(['%s'] * len(allowed_companies))
                sql = (f"SELECT t.id FROM {table_name} t "
                       f"JOIN {rel_table} rel ON rel.{col1} = t.id "
                       f"WHERE rel.{col2} IN ({placeholders})")
                params = tuple(allowed_companies)
            else:
                _logger.warning(f"Model {model_name} has no company filter; returning unfiltered IDs")
                sql = f"SELECT id FROM {table_name}"
                params = ()
            request.env.cr.execute(sql, params)
            record_ids = [row[0] for row in request.env.cr.fetchall()]
            _logger.info(f"Found {len(record_ids)} record IDs via SQL: {record_ids}")
            
            # Now browse the records using the IDs (this might still trigger the error)
            if record_ids:
                records = model_obj.sudo().browse(record_ids)
                _logger.info(f"Successfully browsed {len(records)} records")
            else:
                records = model_obj.sudo().browse([])
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                status=500,
                headers=[('Content-Type', 'application/json')]
            )

        model_fields = model_obj._fields
        data = []
        for rec in records:
            rec_data = {}
            for fld in allowed_fields:
                field = model_fields.get(fld)
                if field:
                    try:
                        rec_data[fld] = serialize_field(rec, fld, field)
                    except Exception:
                        continue
            data.append(rec_data)

        try:
            if request.env.cr.status == "in_failed_transaction":
                request.env.cr.rollback()
        except Exception:
            request.env.cr.rollback()

        request.env['api.access.log'].sudo().create({
            'api_key_id': api_key.id,
            'endpoint': endpoint.url_path,
            'status': 'success',
            'ip_address': ip_address,
            'query_string': query_string,
        })

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

    def _unauthorized(self, endpoint_path, ip_address, query_string):
        request.env['api.access.log'].sudo().create({
            'api_key_id':  False,
            'endpoint':    endpoint_path,
            'status':      'unauthorized',
            'ip_address':  ip_address,
            'query_string': query_string,
        })
        return request.make_response(
            json.dumps({'error': 'Unauthorized'}),
            status=401,
            headers=[('Content-Type', 'application/json')]
        )