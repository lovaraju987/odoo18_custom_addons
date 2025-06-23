# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ApiEndpoint(models.Model):
    _name = 'res.api.endpoint'
    _description = 'Dynamic API Endpoint'

    name = fields.Char(
        string="Name",
        required=True,
        help="Descriptive name (e.g. Sales Orders for BI)"
    )
    url_path = fields.Char(
        string="URL Path",
        required=True,
        help="Endpoint exposed at /api/<url_path>"
    )
    model_id = fields.Many2one(
        'ir.model',
        string="Model",
        required=True,
        ondelete='cascade',
        help="Odoo model to expose"
    )
    field_ids = fields.Many2many(
        'ir.model.fields',
        string="Allowed Fields",
        domain="[('model_id','=',model_id)]",
        help="Which fields of the model will be returned"
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to disable this endpoint"
    )
    api_key_ids = fields.Many2many(
        'res.api.key',
        'res_api_key_res_api_endpoint_rel',
        'endpoint_id',
        'api_key_id',
        string='Allowed API Keys',
        help="Only these API keys can call this endpoint"
    )

    _sql_constraints = [
        ('unique_url_path', 'unique(url_path)', "The URL Path must be unique across all API Endpoints.")
    ]

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            base_url = self.model_id.model.replace('.', '_')
            # Check if base_url already exists in other endpoints
            existing = self.search([('url_path', '=', base_url)])
            if existing:
                # If exists, find a suffix that makes it unique.
                suffix = 1
                new_url = f"{base_url}_{suffix}"
                while self.search([('url_path', '=', new_url)]):
                    suffix += 1
                    new_url = f"{base_url}_{suffix}"
                self.url_path = new_url
            else:
                self.url_path = base_url
