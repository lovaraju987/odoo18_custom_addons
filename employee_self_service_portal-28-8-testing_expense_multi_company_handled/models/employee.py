from odoo import models, fields, api

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    user_id = fields.Many2one('res.users', string="Portal User", help="Portal user linked to this employee")
    portal_access_crm = fields.Boolean("Portal Access CRM", default=False, help="Allow access to CRM functionality in portal")
    portal_access_attendance = fields.Boolean("Portal Access Attendance", default=True, help="Allow access to attendance functionality in portal")
    portal_access_expenses = fields.Boolean("Portal Access Expenses", default=False, help="Allow access to expenses functionality in portal")
    portal_access_payslip = fields.Boolean("Portal Access Payslip", default=False, help="Allow access to payslip functionality in portal")
    
    # @api.onchange('portal_access_crm', 'portal_access_attendance', 'portal_access_expenses', 'portal_access_payslip', 'user_id')
    # def _onchange_portal_access(self):
    #     """When portal access settings change, inform the user about the need to save"""
    #     if self.user_id and any([self.portal_access_crm, self.portal_access_attendance, 
    #                            self.portal_access_expenses, self.portal_access_payslip]):
    #         return {
    #             'warning': {
    #                 'title': 'Portal Access Changed',
    #                 'message': 'Please save the record to update user access rights.'
    #             }
    #         }
    
    def write(self, vals):
        """Override write to update portal user access groups"""
        res = super(HREmployee, self).write(vals)
        
        # Check if any portal access fields were changed or user_id was assigned
        portal_fields = ['portal_access_crm', 'portal_access_attendance', 
                         'portal_access_expenses', 'portal_access_payslip', 'user_id']
        
        if any(field in vals for field in portal_fields):
            self._update_portal_access_groups()
        
        return res
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set portal user access groups"""
        employees = super(HREmployee, self).create(vals_list)
        for employee in employees:
            employee._update_portal_access_groups()
        return employees
    
    def _update_portal_access_groups(self):
        """Update the user's access groups based on portal access settings"""
        for employee in self:
            if not employee.user_id:
                continue
                
            user = employee.user_id
            
            # Dictionary mapping access fields to security groups
            access_groups = {
                'portal_access_crm': self.env.ref('employee_self_service_portal.group_portal_crm'),
                'portal_access_attendance': self.env.ref('employee_self_service_portal.group_portal_attendance'),
                'portal_access_expenses': self.env.ref('employee_self_service_portal.group_portal_expenses'),
                'portal_access_payslip': self.env.ref('employee_self_service_portal.group_portal_payslip'),
            }
            
            # Add or remove user from groups based on settings
            for field_name, group in access_groups.items():
                if employee[field_name]:
                    user.sudo().write({'groups_id': [(4, group.id)]})
                else:
                    user.sudo().write({'groups_id': [(3, group.id)]})
    
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
