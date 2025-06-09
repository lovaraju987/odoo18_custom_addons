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
    x_nationality = fields.Char("Nationality")
    x_emirates_id = fields.Char("Emirates Id")
    x_emirates_expiry = fields.Date("Emirates Id Expiry Date")
    x_passport_number = fields.Char("Passport Number")
    x_passport_country = fields.Char("Passport Issuing Country")
    x_passport_issue = fields.Date("Passport Issue Date")
    x_passport_expiry = fields.Date("Passport Expiry Date")
    employee_id = fields.Char("Employee ID")
