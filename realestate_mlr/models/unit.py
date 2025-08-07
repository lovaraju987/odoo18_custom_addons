from odoo import models, fields


class RealEstateUnit(models.Model):
    _name = 'realestate.unit'
    _description = 'Property Unit'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    property_id = fields.Many2one('realestate.property', string='Property', required=True)
    floor = fields.Char(string='Floor/Number', translate=True)
    area = fields.Float(string='Area (sqm)')
    num_bedrooms = fields.Integer(string='Bedrooms')
    num_bathrooms = fields.Integer(string='Bathrooms')
    price = fields.Float(string='Unit Price')
    status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ], default='available')
    image = fields.Binary(string='Image')
    description = fields.Text(translate=True)
    notes = fields.Text(string='Notes', translate=True)
