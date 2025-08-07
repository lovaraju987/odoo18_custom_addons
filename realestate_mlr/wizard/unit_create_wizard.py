from odoo import models, fields, api, _
from odoo.exceptions import UserError

class UnitAutoCreateWizard(models.TransientModel):
    _name = 'realestate.unit.create.wizard'
    _description = 'Auto Create Units Wizard'

    property_id = fields.Many2one('realestate.property', string='Property', required=True)
    number_of_units = fields.Integer(string='Number of Units', required=True, default=1)
    base_name = fields.Char(string='Base Unit Name', required=True)
    floor = fields.Char(string='Floor/Number')
    area = fields.Float(string='Area (sqm)')
    num_bedrooms = fields.Integer(string='Bedrooms')
    num_bathrooms = fields.Integer(string='Bathrooms')
    price = fields.Float(string='Unit Price')

    def action_create_units(self):
        if self.number_of_units < 1:
            raise UserError(_('Number of units must be at least 1.'))
        for i in range(1, self.number_of_units + 1):
            self.env['realestate.unit'].create({
                'name': f"{self.base_name} {i}",
                'property_id': self.property_id.id,
                'floor': self.floor,
                'area': self.area,
                'num_bedrooms': self.num_bedrooms,
                'num_bathrooms': self.num_bathrooms,
                'price': self.price,
            })
