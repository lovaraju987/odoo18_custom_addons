from odoo import models, fields

class Amenity(models.Model):
    _name = 'real.estate.amenity'
    _description = 'Property Amenity'

    name = fields.Char('Amenity Name', required=True)
    description = fields.Text('Description')
