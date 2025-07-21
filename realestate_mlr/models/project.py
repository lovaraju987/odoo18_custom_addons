from odoo import models, fields


class RealEstateProject(models.Model):
    _name = 'realestate.project'
    _description = 'Real Estate Project'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    region_id = fields.Many2one('realestate.region', string='Region')
    description = fields.Text(translate=True)
    property_ids = fields.One2many('realestate.property', 'project_id', string='Properties')
