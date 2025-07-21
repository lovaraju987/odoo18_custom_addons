from odoo import models, fields

class Sale(models.Model):
    _name = 'real.estate.sale'
    _description = 'Sale'

    property_id = fields.Many2one('real.estate.property', string='Property', required=True)
    buyer_name = fields.Char(string='Buyer Name', required=True)
    sale_date = fields.Date(string='Sale Date', required=True)
    sale_price = fields.Float(string='Sale Price', required=True)
