from odoo import models, fields


class RealEstateProperty(models.Model):
    _name = 'realestate.property'
    _description = 'Property'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    project_id = fields.Many2one('realestate.project', string='Project')
    property_type = fields.Selection([
        ('building', 'Building'),
        ('villa', 'Villa'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
        ('office', 'Office'),
    ], string='Property Type', default='building')
    address = fields.Char(translate=True)
    price = fields.Float(string='Price')
    num_rooms = fields.Integer(string='Number of Rooms')
    amenities = fields.Char(string='Amenities', translate=True)
    image = fields.Binary(string='Image')
    description = fields.Text(translate=True)
    notes = fields.Text(string='Notes', translate=True)
    unit_ids = fields.One2many('realestate.unit', 'property_id', string='Units')
