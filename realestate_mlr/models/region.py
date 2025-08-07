from odoo import models, fields


class RealEstateRegion(models.Model):
    _name = 'realestate.region'
    _description = 'Region'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(help='Short code for the region')
    description = fields.Text(translate=True)
    location = fields.Char(string='Location', translate=True)
    manager = fields.Char(string='Region Manager', translate=True)
    project_ids = fields.One2many('realestate.project', 'region_id', string='Projects')
