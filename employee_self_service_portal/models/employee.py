from odoo import models, fields

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    user_id = fields.Many2one('res.users', string="Portal User", help="Portal user linked to this employee")
    x_experience = fields.Text("Experience")
    x_skills = fields.Char("Skills")
    x_certifications = fields.Text("Certifications")
    x_bank_account = fields.Char("Bank Account Number")
    x_bank_name = fields.Char("Bank Name")
    x_ifsc = fields.Char("IFSC Code")
