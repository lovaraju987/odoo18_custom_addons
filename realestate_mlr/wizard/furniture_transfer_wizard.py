from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FurnitureTransferWizard(models.TransientModel):
    _name = 'realestate.furniture.transfer.wizard'
    _description = 'Furniture Transfer Wizard'

    furniture_id = fields.Many2one('realestate.furniture', string='Furniture', required=True)
    from_location = fields.Selection([
        ('warehouse', 'Company Warehouse'),
        ('property', 'Property'),
        ('unit', 'Unit'),
        ('customer', 'Customer Warehouse'),
    ], string='From', required=True)
    to_location = fields.Selection([
        ('warehouse', 'Company Warehouse'),
        ('property', 'Property'),
        ('unit', 'Unit'),
        ('customer', 'Customer Warehouse'),
    ], string='To', required=True)
    property_id = fields.Many2one('realestate.property', string='Property')
    unit_id = fields.Many2one('realestate.unit', string='Unit')
    qty = fields.Float(string='Quantity', default=1.0)

    def action_transfer(self):
        if self.from_location == self.to_location:
            raise UserError(_('Source and destination must be different.'))
        if self.qty <= 0:
            raise UserError(_('Quantity must be positive.'))
        # Update location and links
        furniture = self.furniture_id
        furniture.location = self.to_location
        if self.to_location == 'property' and self.property_id:
            furniture.property_ids = [(4, self.property_id.id)]
        if self.to_location == 'unit' and self.unit_id:
            furniture.unit_ids = [(4, self.unit_id.id)]
        # In a real implementation, integrate with stock.move for inventory
        return {'type': 'ir.actions.act_window_close'}
