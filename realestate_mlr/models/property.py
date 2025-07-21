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
    ], string='Property Type', default='building')
    address = fields.Char()
    description = fields.Text(translate=True)
    unit_ids = fields.One2many('realestate.unit', 'property_id', string='Units')
