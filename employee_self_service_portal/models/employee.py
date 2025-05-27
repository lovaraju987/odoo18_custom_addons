from odoo import models, fields

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    user_id = fields.Many2one('res.users', string="Portal User", help="Portal user linked to this employee")
