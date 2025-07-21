from odoo import models, fields, api

class RealEstateDashboard(models.TransientModel):
    _name = 'realestate.dashboard'
    _description = 'Real Estate Dashboard Wizard'

    total_units = fields.Integer(string='Total Units', readonly=True)
    available_units = fields.Integer(string='Available Units', readonly=True)
    sold_units = fields.Integer(string='Sold Units', readonly=True)
    rented_units = fields.Integer(string='Rented Units', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        Unit = self.env['realestate.unit']
        res['total_units'] = Unit.search_count([])
        res['available_units'] = Unit.search_count([('status', '=', 'available')])
        res['sold_units'] = Unit.search_count([('status', '=', 'sold')])
        res['rented_units'] = Unit.search_count([('status', '=', 'rented')])
        return res
