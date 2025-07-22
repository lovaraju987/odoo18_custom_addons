from odoo import models, fields

class RealEstateFurniture(models.Model):
    _name = 'realestate.furniture'
    _description = 'Furniture Item'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(string='Furniture Code')
    description = fields.Text(translate=True)
    is_active = fields.Boolean(default=True)
    product_id = fields.Many2one('product.product', string='Product', help='Link to Odoo Inventory Product')
    property_ids = fields.Many2many('realestate.property', 'property_furniture_rel', 'furniture_id', 'property_id', string='Properties')
    unit_ids = fields.Many2many('realestate.unit', 'unit_furniture_rel', 'furniture_id', 'unit_id', string='Units')
    qty = fields.Float(string='Quantity', default=1.0)
    location = fields.Selection([
        ('warehouse', 'Company Warehouse'),
        ('property', 'Property'),
        ('unit', 'Unit'),
        ('customer', 'Customer Warehouse'),
    ], string='Current Location', default='warehouse')
    stock_quant_ids = fields.One2many(
        comodel_name='stock.quant',
        inverse_name='product_id',
        string='Stock Quants',
        compute='_compute_stock_quant_ids',
        store=False
    )

    def _compute_stock_quant_ids(self):
        for rec in self:
            if rec.product_id:
                rec.stock_quant_ids = self.env['stock.quant'].search([('product_id', '=', rec.product_id.id)])
            else:
                rec.stock_quant_ids = False
