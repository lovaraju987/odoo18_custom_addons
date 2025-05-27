from odoo import models, fields, _
from odoo.exceptions import UserError
import secrets

class ResApiKey(models.Model):
    _name = 'res.api.key'
    _description = 'API Key'

    name = fields.Char(string="Name", required=True)
    key = fields.Char(string="API Key", readonly=True, copy=False)
    user_id = fields.Many2one('res.users', string="User")
    active = fields.Boolean(default=True)
    expiry_date = fields.Date()
    is_admin = fields.Boolean(string="Admin Access", default=False)
    allowed_model_ids = fields.Many2many(
        'ir.model',
        'res_api_key_ir_model_rel',
        'api_key_id',
        'model_id',
        string='Allowed Models'
    )
    # Your endpoint_ids field remains defined as before.
    endpoint_ids = fields.Many2many(
        'res.api.endpoint',
        'res_api_key_res_api_endpoint_rel',
        'api_key_id',
        'endpoint_id',
        string='API Endpoints'
    )
    company_ids = fields.Many2many('res.company', string="Allowed Companies")

    def generate_key(self):
        for rec in self:
            rec.key = secrets.token_hex(20)

    def create(self, vals):
        vals['key'] = secrets.token_hex(20)
        return super(ResApiKey, self).create(vals)

    def _compute_endpoint_ids(self):
        # Compute logic to populate endpoint_ids
        for rec in self:
            endpoints = self.env['res.api.endpoint'].search([('api_key_ids', 'in', rec.id)])
            rec.endpoint_ids = endpoints

    def unlink(self):
        for rec in self:
            if rec.endpoint_ids:
                raise UserError(_("You cannot delete an API Key that has associated endpoint URLs."))
        return super(ResApiKey, self).unlink()