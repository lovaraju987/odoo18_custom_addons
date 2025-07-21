from odoo import models, fields


class RealEstateProject(models.Model):
    _name = 'realestate.project'
    _description = 'Real Estate Project'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    region_id = fields.Many2one('realestate.region', string='Region')
    description = fields.Text(translate=True)
    location = fields.Char(string='Location', translate=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    property_ids = fields.One2many('realestate.property', 'project_id', string='Properties')
