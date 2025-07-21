from odoo import models, fields


class RealEstateUnit(models.Model):
    _name = 'realestate.unit'
    _description = 'Property Unit'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    property_id = fields.Many2one('realestate.property', string='Property', required=True)
    floor = fields.Char(string='Floor/Number')
    area = fields.Float(string='Area (sqm)')
    status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ], default='available')
    description = fields.Text(translate=True)
