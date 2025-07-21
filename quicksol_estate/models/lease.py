from odoo import models, fields

class Lease(models.Model):
    _name = 'real.estate.lease'
    _description = 'Lease Agreement'

    property_id = fields.Many2one('real.estate.property', string='Property', required=True)
    tenant_id = fields.Many2one('real.estate.tenant', string='Tenant', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    rent_amount = fields.Float(string='Rent', required=True)
